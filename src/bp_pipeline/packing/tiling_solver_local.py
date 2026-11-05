# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Library that solves the issue of perfectly tiling a crease pattern through local perturbations."""

import abc
from collections.abc import Iterator, Sequence, Set as AbstractSet
import dataclasses
import enum
import functools
import itertools
import math
import typing
from typing import Self

from absl import logging
import numpy as np

from .. import timeout
from . import config as config_lib
from . import grid
from . import types
from . import utils_packing_flaps
from . import utils_tracker

TrackerID = str


class ImpossibleTilingError(Exception):
  """Raised when a perfect tiling based on the given packing is impossible."""


class GridArea(abc.ABC):
  """Represents a 2D area on a grid."""

  @abc.abstractmethod
  def walk(self) -> Iterator[grid.Cell]:
    """Yields all cells affected by the delta."""
    raise NotImplementedError()

  @functools.cached_property
  def cells(self) -> frozenset[grid.Cell]:
    """The set of all cells affected by the delta."""
    return frozenset(self.walk())

  def __hash__(self) -> int:
    return hash(self.cells)

  def __eq__(self, other: Self) -> bool:  # pyrefly: ignore[bad-override]
    if not isinstance(other, GridArea):
      return NotImplemented
    return self.cells == other.cells

  @functools.cached_property
  def grid_indices(self) -> tuple[np.ndarray, np.ndarray]:
    """The row and column indices of the cells affected by the delta.

    The indices are returned as a tuple of two numpy arrays, suitable for
    indexing a 2D numpy array.
    """
    ys, xs = zip(*((cell.i, cell.j) for cell in self.cells))
    return np.array(ys), np.array(xs)

  def grid_has_space(self, occupancy_grid: np.ndarray) -> bool:
    """Check that area of this RectDelta doesn't overlap with any occupied cells."""
    return not occupancy_grid[self.grid_indices].any()

  def add_to_grid(self, occupancy_grid: np.ndarray) -> None:
    occupancy_grid[self.grid_indices] = True


@dataclasses.dataclass(frozen=True, eq=True)
class RectDelta(GridArea):
  """Represents a potential change to a flap's size and its affected grid cells.

  Attributes:
    delta: The grid Delta representing the change in the flap's dimensions.
    edge_walk: A grid Walk along the edge of the flap that is being extended.
  """

  delta: grid.Delta
  edge_walk: grid.Walk

  def __post_init__(self):
    if self.delta == grid.Delta(di=0, dj=0):
      raise ValueError('Delta must not be zero.')
    if self.delta.direction.axis == self.edge_walk.direction.axis:
      raise ValueError('Delta direction must be perpendicular to edge walk.')

  def walk(self) -> Iterator[grid.Cell]:
    """Yields all cells affected by the delta."""
    for subdelta in grid.all_subdeltas(self.delta):
      if subdelta == grid.Delta(di=0, dj=0):
        continue
      try:
        delta_walk = dataclasses.replace(
            self.edge_walk, start_cell=self.edge_walk.start_cell.shift(subdelta)
        )
      except ValueError:
        # This happens if no part of the walk is on the grid.
        return
      yield from delta_walk


# Utils for finding all possible flap expansions that will cover an empty cell.


@dataclasses.dataclass(frozen=True, eq=True)
class _RiverRange:
  source_id: TrackerID
  start: grid.Cell
  end: grid.Cell


@dataclasses.dataclass(frozen=True)
class _OpenRiverRange:
  source_id: TrackerID
  start: grid.Cell

  def close(self, cell: grid.Cell) -> _RiverRange:
    return _RiverRange(self.source_id, self.start, cell)


@dataclasses.dataclass(frozen=True, eq=True)
class FlapOption(GridArea):
  """Represents a potential change to a flap and its affected grid cells."""

  flap_id: TrackerID
  rect_deltas: Sequence[RectDelta]

  def __post_init__(self):
    if not self.rect_deltas:
      raise ValueError('FlapOption must have at least one rect_delta.')

    if len(self.rect_deltas) > 1:
      cells = list(self.walk())
      if len(cells) > len(set(cells)):
        raise ValueError('Deltas must not overlap.')

      # Flap-delta specific checks
      if (
          len({
              rect_delta.edge_walk.direction for rect_delta in self.rect_deltas
          })
          > 1
      ):
        raise ValueError('All edge walks must be in the same direction.')

      for prev_rect_delta, current_rect_delta in itertools.pairwise(
          self.rect_deltas
      ):
        prev_walk = prev_rect_delta.edge_walk
        current_walk = current_rect_delta.edge_walk
        assert prev_walk.steps is not None
        assert current_walk.steps is not None
        if prev_walk.steps >= current_walk.steps:
          raise ValueError('edge_walks must be strictly increasing in length.')

  @property
  def delta(self) -> grid.Delta:
    return sum(
        (rect_delta.delta for rect_delta in self.rect_deltas),
        start=grid.Delta(di=0, dj=0),
    )

  def walk(self) -> Iterator[grid.Cell]:
    for rect_delta in self.rect_deltas:
      yield from rect_delta.walk()


@dataclasses.dataclass(frozen=True)
class PolygonExpansion:
  """Represents a polygon expansion option."""

  source_id: TrackerID
  placement: types.PolygonPlacement
  polygon_cell: grid.Cell
  start_cell: grid.Cell
  rivers: Sequence[_RiverRange] = ()

  @functools.cached_property
  def polygon_to_cell(self) -> grid.Delta:
    """Returns the delta from the polygon's center to the start cell."""
    return self.polygon_cell.delta_to(self.start_cell)

  @functools.cached_property
  def cell_to_riverstart(self) -> Sequence[grid.Delta]:
    """Returns the deltas from the start cell to each river start."""
    return [self.start_cell.delta_to(river.start) for river in self.rivers]


# Utils for finding all possible flap expansions that will cover an empty cell.


class _MissingRiverError(RuntimeError):
  """Raised when a river is required but not found."""


def _find_next_occupied_cell(
    tracker: utils_tracker.CreasePatternTracker,
    start_cell: grid.Cell,
    direction: grid.Direction,
    allowed_rivers: Sequence[TrackerID] = (),
    require_rivers: bool = False,
) -> tuple[grid.Cell, list[_RiverRange], bool]:
  """Returns the closest occupied cell in the given direction.

  Args:
    tracker: The CreasePatternTracker containing the occupancy grid.
    start_cell: The cell from which to start the search.
    direction: The direction in which to search for an occupied cell.
    allowed_rivers: A sequence of river IDs that are allowed to be crossed. If
      the search encounters a cell occupied by a river in this list, it will
      continue searching beyond it. Rivers must be encountered in the order
      specified in this list.
    require_rivers: If True, all rivers in `allowed_rivers` must be crossed or
      else this function will raise a _MissingRiverError.

  Returns:
    A tuple containing a `grid.Cell`, a list of encountered rivers as
    `_RiverRange` objects, and a boolean. If an occupied cell is
    found, returns that cell, seen_rivers and True. If no occupied cell is
    found, returns the last cell on the grid in the given direction, seen_rivers
    and False.

  Raises:
    _MissingRiverError: If `require_rivers` is True and not all
      `allowed_rivers` were encountered before finding another occupied cell.
  """
  grid_size = tracker.grid_size
  si, sj = start_cell.i, start_cell.j

  if not allowed_rivers and (0 <= si < grid_size) and (0 <= sj < grid_size):
    occ = tracker.occupancy_grid
    if direction is grid.Direction.NORTH:
      col_slice = occ[: si + 1, sj]
      rev = col_slice[::-1]
      if rev.any():
        return grid.Cell(i=si - int(np.argmax(rev)), j=sj), [], True
      return grid.Cell(i=0, j=sj), [], False
    elif direction is grid.Direction.SOUTH:
      col_slice = occ[si:, sj]
      if col_slice.any():
        return grid.Cell(i=si + int(np.argmax(col_slice)), j=sj), [], True
      return grid.Cell(i=grid_size - 1, j=sj), [], False
    elif direction is grid.Direction.WEST:
      row_slice = occ[si, : sj + 1]
      rev = row_slice[::-1]
      if rev.any():
        return grid.Cell(i=si, j=sj - int(np.argmax(rev))), [], True
      return grid.Cell(i=si, j=0), [], False
    elif direction is grid.Direction.EAST:
      row_slice = occ[si, sj:]
      if row_slice.any():
        return grid.Cell(i=si, j=sj + int(np.argmax(row_slice))), [], True
      return grid.Cell(i=si, j=grid_size - 1), [], False

  seen_rivers: list[_RiverRange] = []
  current_river: _OpenRiverRange | None = None
  walk = grid.Walk(start_cell, direction, tracker.grid_size)
  cell: grid.Cell = start_cell
  found = True
  prev_cell: grid.Cell | None = None  # Necessary typing for itertools.chain
  for prev_cell, cell in itertools.pairwise(itertools.chain([prev_cell], walk)):  # pyrefly: ignore[bad-assignment]
    assert cell is not None
    if tracker.occupancy_grid[cell.i, cell.j]:
      grid_state = tracker.grid[cell.i, cell.j]
      if grid_state.type is utils_packing_flaps.GridCellType.RIVER:
        # If we are in a river, check if we are already crossing it.
        if current_river is not None:
          if grid_state.source_id == current_river.source_id:
            continue
          else:
            assert prev_cell is not None
            seen_rivers.append(current_river.close(prev_cell))
            current_river = None
        else:
          # This is a new river, so we need to start a new range.
          river_i = len(seen_rivers)
          if (
              river_i < len(allowed_rivers)
              and grid_state.source_id == allowed_rivers[river_i]
          ):
            current_river = _OpenRiverRange(grid_state.source_id, cell)
          else:
            break
      else:  # Terminate the search if we find a non-river obstacle.
        break
    elif current_river is not None:
      # If we are in an unoccupied cell, close the current river.
      assert prev_cell is not None
      seen_rivers.append(current_river.close(prev_cell))
      current_river = None
  else:
    # Finished walk without finding an occupied cell.
    found = False

  if current_river is not None:
    assert prev_cell is not None
    seen_rivers.append(current_river.close(prev_cell))

  if require_rivers and len(seen_rivers) < len(allowed_rivers):
    raise _MissingRiverError(
        'Some required rivers were not encountered:'
        f' {allowed_rivers[len(seen_rivers):]}'
    )
  return cell, seen_rivers, found


def _get_polygon_boundary(
    placement: types.PolygonPlacement,
    direction: grid.Direction,
    grid_size: int = -1,
) -> grid.Walk:
  """Returns a grid.Walk along the boundary of a polygon (rectangle).

  The side of the polygon to walk along is specified by the direction. The walk
  is always east or south (positive deltas) e.g., if we are walking along the
  north edge of the polygon, the walk will be eastward from the north-west
  corner.

  Args:
    placement: The PolygonPlacement of the polygon.
    direction: The direction of the boundary to walk along (e.g., NORTH for the
      top edge).
    grid_size: The size of the grid. Used to bound the walk.

  Returns:
    A grid.Walk covering the specified boundary of the polygon.
  """
  offset_x, offset_y = placement.offset
  width, height = placement.size

  match direction:
    case grid.Direction.NORTH:
      # Along the north face we should walk east from the north-west corner.
      return grid.Walk(
          grid.Cell(i=offset_y, j=offset_x),
          grid.Direction.EAST,
          grid_size,
          steps=width,
      )
    case grid.Direction.EAST:
      # Along the east face we should walk south from the north-east corner.
      return grid.Walk(
          grid.Cell(i=offset_y, j=offset_x + width - 1),
          grid.Direction.SOUTH,
          grid_size,
          steps=height,
      )
    case grid.Direction.SOUTH:
      # Along the south face we should walk east from the south-west corner.
      return grid.Walk(
          grid.Cell(i=offset_y + height - 1, j=offset_x),
          grid.Direction.EAST,
          grid_size,
          steps=width,
      )
    case grid.Direction.WEST:
      # Along the west face we should walk south from the north-west corner.
      return grid.Walk(
          grid.Cell(i=offset_y, j=offset_x),
          grid.Direction.SOUTH,
          grid_size,
          steps=height,
      )
    case _:
      raise ValueError(f'Unknown grid direction: {direction}')


def _is_touching_specific_border(
    placement: types.PolygonPlacement, side: grid.Direction, grid_size: int
) -> bool:
  """Returns whether polygon touches/overlaps a particular border of the grid.

  The side of interest is specified as a grid.Direction.

  Args:
    placement: The polygon to check.
    side: Which border of the grid to check
    grid_size: The size of the grid.

  Returns:
    Whether the polygon touches or overlaps that grid border.
  """
  offset_x, offset_y = placement.offset
  width, height = placement.size
  match side:
    case grid.Direction.NORTH:
      return offset_y <= 0
    case grid.Direction.EAST:
      return offset_x + width >= grid_size
    case grid.Direction.SOUTH:
      return offset_y + height >= grid_size
    case grid.Direction.WEST:
      return offset_x <= 0
    case _:
      raise ValueError(f'Unknown grid direction: {side}')


def _is_disallowed_central_flap(
    placement: types.PolygonPlacement,
    towards_polygon: grid.Direction,
    grid_size: int,
    is_symmetric: bool,
) -> bool:
  """Returns whether the proposed flap expansion is a wide central flap.

  A wide central flap is a flap that is not touching any border, is not on the
  symmetry line, and is not expanding into a cell on the border.

  Args:
    placement: The placement of the polygon.
    towards_polygon: The direction from the empty cell to the polygon.
    grid_size: The size of the grid.
    is_symmetric: Whether the packing is symmetric.
  """
  is_horizontal_symmetric_flap = (
      is_symmetric
      and math.isclose(placement.center.x, 0.5)
      and towards_polygon.is_horizontal
  )
  return (
      not placement.center.is_border
      and not _is_touching_specific_border(
          placement, towards_polygon, grid_size
      )
      and not is_horizontal_symmetric_flap
  )


def _allow_odd_delta(
    placement: types.PolygonPlacement,
    towards_polygon: grid.Direction,
    grid_size: int,
    is_symmetric: bool,
) -> bool:
  """Returns whether an odd delta is allowed for the given placement.

  Odd deltas are not allowed in general, but can be made even by expanding the
  opposite side by the same amount.
  There are two cases where we allow an odd delta:
  1. The other side of the polygon is the border of the CP.
  2. The polygon is on the line of symmetry and the delta is horizontal.

  Args:
    placement: The placement of the polygon.
    towards_polygon: The direction from the empty cell to the polygon.
    grid_size: The size of the grid.
    is_symmetric: Whether the packing is symmetric.

  Returns:
    Whether an odd delta is allowed for the given placement.
  """
  center = placement.center
  if _is_touching_specific_border(placement, towards_polygon, grid_size):
    return True
  if (
      is_symmetric
      and math.isclose(center.x, 0.5)
      and towards_polygon.is_horizontal
  ):
    return True
  return False


def _get_empty_cells(
    occupancy_grid: np.ndarray, is_symmetric: bool
) -> Iterator[grid.Cell]:
  """Yields all empty cells in the grid, considering symmetry.

  Args:
    occupancy_grid: The grid showing which cells are occupied.
    is_symmetric: Whether the packing is symmetric about the vertical
      centerline.

  Yields:
    A grid.Cell for each empty position in the occupancy_grid
  """
  symmetry_mask = np.zeros_like(occupancy_grid)
  if is_symmetric:
    # Cells on the RHS of the grid will be filled by mirroring so they can be
    # masked
    symmetry_mask[:, occupancy_grid.shape[1] // 2 :] = True

  for i, j in zip(*np.where(~(occupancy_grid | symmetry_mask))):
    yield grid.Cell(i=int(i), j=int(j))


class _RiverAction(enum.Enum):
  """The action to take when a river is found."""

  BLOCK = 'block'
  ALLOW = 'allow'
  WIDEN_LEFT = 'widen_left'
  WIDEN_RIGHT = 'widen_right'
  WIDEN_BOTH = 'widen_both'


def _feasible_polygon_expansions_generator(
    tracker: utils_tracker.CreasePatternTracker,
    start_cell: grid.Cell,
    towards_polygon_dir: grid.Direction,
    found_rivers: tuple[TrackerID, ...],
    river_action: _RiverAction,
) -> Iterator[PolygonExpansion]:
  """Recursively finds polygons that can expand to cover start_cell.

  This generator function searches in direction `towards_polygon_dir` from
  `start_cell` for polygons. The search can cross rivers based on
  `allowed_rivers`, and branch off to search from adjacent cells if rivers
  are encountered, depending on `river_action`.

  If the nearest occupied cell in `towards_polygon_dir` is a polygon, a
  `PolygonExpansion` is yielded with the polygon's ID, placement, distance
  delta, and rivers crossed to reach it.

  If the nearest occupied cell is a river, and `river_action` is not `BLOCK`,
  the function may do several things:
  1. It recursively calls itself to search *through* the river, adding the
     current river to `allowed_rivers` and setting `river_action` to `ALLOW`
     (to prevent further widening in this branch).
  2. If `river_action` is `WIDEN_LEFT`, `WIDEN_RIGHT`, or `WIDEN_BOTH`, it
     also recursively calls itself from cells perpendicular to
     `towards_polygon_dir`, because expanding a polygon behind this river will
     be able to cover the start cell.

  Args:
    tracker: The CreasePatternTracker containing the occupancy grid and polygon
      placements.
    start_cell: The starting cell for the search.
    towards_polygon_dir: The direction in which to search for a polygon.
    found_rivers: The rivers that have been found so far in this search.
    river_action: The action to take when a river is encountered. `BLOCK` stops
      searching in this branch, `ALLOW` continues searching through the river,
      and `WIDEN_LEFT`, `WIDEN_RIGHT`, or `WIDEN_BOTH` allow searching through
      the river and branching off to widen it.

  Yields:
    PolygonExpansion objects representing possible expansions.
  """
  try:
    occupied_cell, river_ranges, success = _find_next_occupied_cell(
        tracker,
        start_cell,
        towards_polygon_dir,
        found_rivers,
        require_rivers=True,
    )
  except _MissingRiverError:
    return
  if not success:
    # This happens if there is only empty cells until the border is reached.
    return
  grid_state: utils_packing_flaps.GridCellState = tracker.grid[
      occupied_cell.i, occupied_cell.j
  ]
  source_id = grid_state.source_id
  cell_delta = occupied_cell.delta_to(start_cell)

  if grid_state.type is utils_packing_flaps.GridCellType.POLYGON:
    if logging.level_debug():
      logging.debug(
          '%s is %d steps away from polygon %s in direction %s',
          start_cell,
          cell_delta.l1_norm,
          source_id,
          towards_polygon_dir,
      )
    placement = tracker.packed_polygons.get(source_id)
    if placement is not None:
      yield PolygonExpansion(
          source_id=source_id,
          placement=placement,
          start_cell=start_cell,
          polygon_cell=occupied_cell,
          rivers=river_ranges,
      )
    elif source_id != 'mask':
      logging.warning('No placement found for %s', source_id)
  elif grid_state.type is utils_packing_flaps.GridCellType.RIVER:
    if river_action is _RiverAction.BLOCK:
      return
    # If a river is found, add it a list of allowed rivers.
    # and search again from the start cell for each column in the river width.
    river = tracker.packed_rivers[grid_state.source_id]
    new_found_rivers = found_rivers + (grid_state.source_id,)
    yield from _feasible_polygon_expansions_generator(
        tracker,
        start_cell,
        towards_polygon_dir,
        new_found_rivers,
        _RiverAction.ALLOW,
    )
    # Initiate new searchs by widening based on the river width.
    inner_start_cells = []
    if river_action in (_RiverAction.WIDEN_LEFT, _RiverAction.WIDEN_BOTH):
      # Drop the first cell which == start_cell
      _, *left_start_cells = grid.Walk(
          start_cell=start_cell,
          direction=towards_polygon_dir.rotate_left(),
          grid_size=tracker.grid_size,
          steps=river.width + 1,
      )
      if left_start_cells:
        inner_start_cells.extend(left_start_cells[:-1])
        # Only widen from the leftmost cell of the river walk.
        yield from _feasible_polygon_expansions_generator(
            tracker,
            left_start_cells[-1],
            towards_polygon_dir,
            new_found_rivers,
            _RiverAction.WIDEN_LEFT,
        )
    if river_action in (_RiverAction.WIDEN_RIGHT, _RiverAction.WIDEN_BOTH):
      # Drop the first cell which == start_cell
      _, *right_start_cells = grid.Walk(
          start_cell=start_cell,
          direction=towards_polygon_dir.rotate_right(),
          grid_size=tracker.grid_size,
          steps=river.width + 1,
      )
      if right_start_cells:
        inner_start_cells.extend(right_start_cells[:-1])
        # Only widen from the rightmost cell of the river walk.
        yield from _feasible_polygon_expansions_generator(
            tracker,
            right_start_cells[-1],
            towards_polygon_dir,
            new_found_rivers,
            _RiverAction.WIDEN_RIGHT,
        )
    for cell in inner_start_cells:
      yield from _feasible_polygon_expansions_generator(
          tracker,
          cell,
          towards_polygon_dir,
          new_found_rivers,
          _RiverAction.ALLOW,
      )
  elif grid_state.type is utils_packing_flaps.GridCellType.BLOCKED:
    # If we hit a blocked cell, there is nothing to do
    pass
  else:
    raise ValueError(f'Unknown grid cell type: {grid_state.type}')


def _get_feasible_polygon_expansions(
    tracker: utils_tracker.CreasePatternTracker,
    start_cell: grid.Cell,
    towards_polygon_dir: grid.Direction,
    search_rivers: bool = False,
) -> list[PolygonExpansion]:
  """Finds the nearest polygon in a given direction from a start cell.

  Args:
    tracker: The CreasePatternTracker containing the occupancy grid and polygon
      placements.
    start_cell: The starting cell for the search.
    towards_polygon_dir: The direction in which to search for a polygon.
    search_rivers: Whether to widen the search when rivers are found.

  Returns:
    A list of PolygonExpansion objects representing possible expansions.
  """
  river_action = (
      _RiverAction.WIDEN_BOTH if search_rivers else _RiverAction.BLOCK
  )
  deduplicated_expansions = {}
  for expansion in _feasible_polygon_expansions_generator(
      tracker, start_cell, towards_polygon_dir, (), river_action
  ):
    deduplicated_expansions[expansion.source_id] = expansion
  return list(deduplicated_expansions.values())


def _is_placement_expansion_valid(
    tracker: utils_tracker.CreasePatternTracker,
    placement: types.PolygonPlacement,
    from_polygon_dir: grid.Direction,
    polygon_delta: grid.Delta,
    is_symmetric: bool,
) -> bool:
  """Checks if a polygon expansion is valid directly from placement geometry.

  Avoids allocating `grid.Walk` and `grid.Cell` objects for invalid expansion
  candidates.

  Args:
    tracker: The CreasePatternTracker containing the occupancy grid.
    placement: The PolygonPlacement of the polygon.
    from_polygon_dir: The direction from the polygon towards the expansion.
    polygon_delta: The grid Delta representing the change in dimensions.
    is_symmetric: Whether the packing is symmetric about the vertical
      centerline.

  Returns:
    Whether the expansion is valid.
  """
  offset_x, offset_y = placement.offset
  width, height = placement.size

  match from_polygon_dir:
    case grid.Direction.NORTH:
      start_i = offset_y
      start_j = offset_x
      walk_dir = grid.Direction.EAST
      steps = width
    case grid.Direction.EAST:
      start_i = offset_y
      start_j = offset_x + width - 1
      walk_dir = grid.Direction.SOUTH
      steps = height
    case grid.Direction.SOUTH:
      start_i = offset_y + height - 1
      start_j = offset_x
      walk_dir = grid.Direction.EAST
      steps = width
    case grid.Direction.WEST:
      start_i = offset_y
      start_j = offset_x
      walk_dir = grid.Direction.SOUTH
      steps = height
    case _:
      raise ValueError(f'Unknown grid direction: {from_polygon_dir}')

  si = start_i + polygon_delta.di
  sj = start_j + polygon_delta.dj
  grid_size = tracker.grid_size
  if is_symmetric and sj >= grid_size // 2:
    return False

  axis = polygon_delta.direction.axis
  if axis is grid.Axis.VERTICAL:
    within_axis = 0 <= si < grid_size
  elif axis is grid.Axis.HORIZONTAL:
    within_axis = 0 <= sj < grid_size
  else:
    within_axis = (0 <= si < grid_size) and (0 <= sj < grid_size)

  if not within_axis:
    return True

  if walk_dir is grid.Direction.EAST:
    if si < 0 or si >= grid_size:
      return True
    c0 = max(0, sj)
    c1 = min(grid_size - 1, sj + steps - 1)
    if c0 > c1:
      return True
    return not tracker.occupancy_grid[si, c0 : c1 + 1].any()
  else:  # walk_dir is grid.Direction.SOUTH
    if sj < 0 or sj >= grid_size:
      return True
    r0 = max(0, si)
    r1 = min(grid_size - 1, si + steps - 1)
    if r0 > r1:
      return True
    return not tracker.occupancy_grid[r0 : r1 + 1, sj].any()


def _is_rectangular_expansion_allowed(
    placement: types.PolygonPlacement,
    towards_polygon_dir: grid.Direction,
) -> bool:
  """Checks whether a sacrificial polygon is allowed to expand in a direction.

  Sacrificial flaps should only expand along their long axis. For example, a
  4x2 SF (wider than tall) may only expand EAST or WEST.

  Args:
    placement: The current placement of the sacrificial polygon.
    towards_polygon_dir: The direction from the empty cell towards the polygon.

  Returns:
    True if the expansion is allowed, False otherwise.
  """

  w, h = placement.size
  if w > h:
    return towards_polygon_dir in (grid.Direction.EAST, grid.Direction.WEST)
  elif h > w:
    return towards_polygon_dir in (grid.Direction.NORTH, grid.Direction.SOUTH)
  return True


def _get_flap_modifications_for_cell_for_direction(
    config: config_lib.LocalTilingConfig,
    tracker: utils_tracker.CreasePatternTracker,
    empty_cell: grid.Cell,
    towards_polygon_dir: grid.Direction,
    *,
    is_symmetric: bool,
    locked_long_side_flaps: set[str] | None = None,
) -> list[FlapOption]:
  """Returns a flap modification to cover empty_cell from towards_polygon_dir.

  If an occupied cell belongs to a polygon, it calculates the minimum change
  required for that polygon to expand and cover the empty cell. The delta must
  be an even number of grid units, unless the expansion is against the grid
  border or a symmetry line.

  Args:
    config: The configuration options for local tiling.
    tracker: The CreasePatternTracker containing the current packing state.
    empty_cell: The empty cell to cover.
    towards_polygon_dir: The direction in which to look for a polygon to expand.
    is_symmetric: Whether the packing is symmetric about the vertical
      centerline.
    locked_long_side_flaps: If provided, prevents these flaps from expanding
      along their long side.

  Returns:
    A tuple of (FlapID, RectDelta) if a valid modification is found, else None.
  """

  from_polygon_dir = towards_polygon_dir.flip()

  polygon_expansions = _get_feasible_polygon_expansions(
      tracker, empty_cell, towards_polygon_dir
  )

  flap_options = []
  for expansion in polygon_expansions:
    source_id = expansion.source_id
    placement = expansion.placement
    polygon_to_cell = expansion.polygon_to_cell

    if not _is_rectangular_expansion_allowed(placement, towards_polygon_dir):
      continue

    if locked_long_side_flaps and source_id in locked_long_side_flaps:
      w, h = placement.size
      long_side_is_height = h >= w
      if long_side_is_height and towards_polygon_dir in (
          grid.Direction.NORTH,
          grid.Direction.SOUTH,
      ):
        continue
      if not long_side_is_height and towards_polygon_dir in (
          grid.Direction.EAST,
          grid.Direction.WEST,
      ):
        continue

    if config.disable_wide_central_flaps and _is_disallowed_central_flap(
        placement, towards_polygon_dir, tracker.grid_size, is_symmetric
    ):
      # The flap is a central flap but we need to check if it can be stretched
      # all the way to the border by walking in the opposite direction.
      border_cell, _, is_occupied = _find_next_occupied_cell(
          tracker, empty_cell, towards_polygon_dir.flip()
      )
      if is_occupied:
        # If it is blocked, the modification is invalid
        continue

      cell_to_border = empty_cell.delta_to(border_cell)
      polygon_to_cell = polygon_to_cell + cell_to_border
      assert isinstance(polygon_to_cell, grid.Delta)  # type hint

    distance = polygon_to_cell.l1_norm
    if distance % 2 != 0 and not _allow_odd_delta(
        placement, towards_polygon_dir, tracker.grid_size, is_symmetric
    ):
      logging.debug('Polygon %s is odd distance away, overshooting.', source_id)
      # Shift the polygon delta to be even by overshooting the cell by one.
      # This is necessary because central ridges must be even-length.
      polygon_to_cell = polygon_to_cell + from_polygon_dir.step_delta

    if not _is_placement_expansion_valid(
        tracker, placement, from_polygon_dir, polygon_to_cell, is_symmetric
    ):
      continue

    boundary_walk = _get_polygon_boundary(
        placement, from_polygon_dir, tracker.grid_size
    )

    logging.debug(
        'Found option for flap %s to cover cell %s: %s',
        source_id,
        empty_cell,
        polygon_to_cell,
    )
    flap_options.append(
        FlapOption(
            source_id,
            (RectDelta(delta=polygon_to_cell, edge_walk=boundary_walk),),
        )
    )

  return flap_options


def _get_empty_cell_options(
    config: config_lib.LocalTilingConfig,
    tracker: utils_tracker.CreasePatternTracker,
    *,
    is_symmetric: bool,
    locked_long_side_flaps: set[str] | None = None,
    legacy_iteration_order: bool = False,
) -> dict[grid.Cell, list[FlapOption] | set[FlapOption]]:
  """Returns a mapping from empty cells to possible flap perturbations that will cover them.

  This function iterates through all empty cells in the grid. For each empty
  cell, it looks for the nearest occupied cells in all four directions (NORTH,
  EAST, SOUTH, WEST).

  If an occupied cell belongs to a polygon, it calculates the minimum change
  required for that polygon to expand and cover the empty cell. The delta must
  be an even number of grid units, unless the expansion is against the grid
  border or a symmetry line.

  Args:
    config: The configuration options for local tiling.
    tracker: The CreasePatternTracker containing the current packing state.
    is_symmetric: Whether the packing is symmetric about the vertical
      centerline.
    locked_long_side_flaps: If provided, prevents these flaps from expanding
      along their long side.
    legacy_iteration_order: If True, preserves legacy set-based option
      deduplication and iteration order.

  Returns:
    A dictionary where keys are empty `grid.Cell`s. Each value is set of
    FlapModifications that will cover the cell.
  Raises:
    ImpossibleTilingError: If any empty cell cannot be covered by any
      adjacent polygon through a valid perturbation.
    NotImplementedError: If the tracker contains rivers, as this is not
      yet supported.
  """

  options_by_cell = {}
  use_legacy_order = legacy_iteration_order or getattr(
      config, 'legacy_iteration_order', False
  )
  for empty_cell in _get_empty_cells(tracker.occupancy_grid, is_symmetric):
    possible_modifications: list[FlapOption] | set[FlapOption] = (
        set() if use_legacy_order else []
    )
    for towards_polygon_dir in grid.Direction:
      mods = _get_flap_modifications_for_cell_for_direction(
          config,
          tracker,
          empty_cell,
          towards_polygon_dir,
          is_symmetric=is_symmetric,
          locked_long_side_flaps=locked_long_side_flaps,
      )
      if isinstance(possible_modifications, set):
        possible_modifications.update(mods)
      else:
        for mod in mods:
          if mod not in possible_modifications:
            possible_modifications.append(mod)

    if not possible_modifications:
      raise ImpossibleTilingError(f'No valid options for cell {empty_cell}.')
    options_by_cell[empty_cell] = possible_modifications

  return options_by_cell


# Utils for finding a non-overlapping delta set


@dataclasses.dataclass(frozen=True)
class TilingSolution:
  """Represents a potential solution for tiling the crease pattern.

  Attributes:
    occupancy_grid: A boolean numpy array indicating occupied grid.Cells.
    grid_deltas: A dictionary mapping FlapIDs to the grid.Delta applied to them.
  """

  occupancy_grid: np.ndarray
  grid_deltas: dict[TrackerID, grid.Delta] = dataclasses.field(
      default_factory=dict
  )

  def clone(self) -> 'TilingSolution':
    # grid.Delta is an immutable frozen dataclass, so shallow copying dict
    # values is safe.
    return TilingSolution(
        occupancy_grid=self.occupancy_grid.copy(),
        grid_deltas=self.grid_deltas.copy(),
    )

  def add_flap_option(self, flap_option: FlapOption) -> RectDelta | None:
    """Adds a flap delta to the tiling solution.

    This method attempts to apply a given `FlapDelta` to a specific flap. It
    checks for overlaps with the existing occupancy grid and ensures that
    any previous deltas for the same flap are compatible.

    Args:
      flap_option: The `FlapModification` object representing the proposed
        change.

    Returns:
      The RectDelta that was added to the grid, or None if the delta was
      already covered by a previous delta.

    Raises:
      ImpossibleTilingError: If the proposed delta:
        - Is in a different direction than a previously added delta for the same
          flap.
        - Overlaps with an already occupied cell in the grid.
    """
    if len(flap_option.rect_deltas) > 1:
      raise NotImplementedError('Only basic flap_options are supported.')

    flap_id = flap_option.flap_id
    [flap_delta] = flap_option.rect_deltas
    grid_delta = self.grid_deltas.get(flap_id)
    # If there is no existing delta for this flap, then "relative_delta" to
    # check for emptiness will be the input flap_delta.
    relative_delta = flap_delta
    if grid_delta is not None:
      # This means that we have already added a delta for this flap, so we need
      # to check that the new delta is compatible with the existing one and if
      # it is, then we need to shift the RectDelta to be relative to the
      # existing one.
      if grid_delta.direction != flap_delta.delta.direction:
        raise ImpossibleTilingError(
            'Flap already has a perturbation in a different axis:'
            f' {grid_delta}.'
        )
      if flap_delta.delta.is_subdelta_of(grid_delta):
        # If flap being added is a subdelta of an already added delta, then we
        # don't need to add it and can just return.
        return None
      logging.debug(
          'Flap %s perturbed by %s, checking extension for delta %s',
          flap_id,
          grid_delta,
          flap_delta.delta,
      )
      # We calculate a new RectDelta relative to the existing grid delta.
      # (by shifting the start cell and subtracting the grid deltas)
      relative_delta = dataclasses.replace(
          flap_delta,
          delta=flap_delta.delta - grid_delta,
          edge_walk=dataclasses.replace(
              flap_delta.edge_walk,
              start_cell=flap_delta.edge_walk.start_cell.shift(grid_delta),
          ),
      )

    if relative_delta.grid_has_space(self.occupancy_grid):
      relative_delta.add_to_grid(self.occupancy_grid)
      self.grid_deltas[flap_id] = flap_delta.delta
    else:
      raise ImpossibleTilingError(
          f'Delta {relative_delta} overlaps with occupancy grid.'
      )
    logging.info('Successfully added delta %s for flap %s', flap_delta, flap_id)
    return relative_delta

  def add_necessary_options(
      self: Self, options_by_cell: dict[grid.Cell, set[FlapOption]]
  ) -> dict[grid.Cell, set[FlapOption]]:
    """Adds cell options which are the only one viable option for a given cell.

    After adding an option, the cell option set is filtered to remove any that
    are precluded by the new delta and the function continues iterating until
    no more necessary options remain.

    Args:
      options_by_cell: A dictionary mapping empty cells to possible flap
        perturbations that will cover them.

    Returns:
      A new dictionary with the invalid options removed.

    Raises:
      ImpossibleTilingError: If any cell has no remaining valid options.
    """
    filled_cells = True
    while filled_cells:
      filled_cells = set()
      for options in options_by_cell.values():
        match len(options):
          case 0:
            raise ImpossibleTilingError(
                'Some cells are empty and have no filling options.'
            )
          case 1:
            added_delta = self.add_flap_option(next(iter(options)))
            if added_delta is not None:
              filled_cells.update(added_delta.cells)

      options_by_cell = _filter_invalid_options(
          options_by_cell, self.grid_deltas, filled_cells
      )
    return options_by_cell


def _filter_invalid_options(
    options_by_cell: dict[grid.Cell, Sequence[FlapOption] | set[FlapOption]],
    added_deltas: dict[TrackerID, grid.Delta],
    filled_cells: AbstractSet[grid.Cell],
) -> dict[grid.Cell, list[FlapOption]]:
  """Removes options that are no longer valid given the deltas already applied.

  An option is no longer valid if:
  1. The option is for a flap that has already been modified, but the option's
     delta is not in the same direction as the existing delta.
  2. The option's delta is a subdelta of an already applied delta (meaning
     the cell is already covered).

  Args:
    options_by_cell: A dictionary mapping empty cells to possible flap
      perturbations that will cover them.
    added_deltas: A dictionary mapping FlapIDs to the grid.Delta applied to
      them.
    filled_cells: A set of cells that have been newly filled by added options.

  Returns:
    A new dictionary with the invalid options removed.

  Raises:
    ImpossibleTilingError: If any cell has no remaining valid options.
  """
  filtered_options = {}
  for cell, cell_options in options_by_cell.items():
    if cell in filled_cells:
      continue

    use_set = isinstance(cell_options, set)
    remaining_options: list[FlapOption] | set[FlapOption] = (
        set() if use_set else []
    )
    for flap_modification in cell_options:
      if len(flap_modification.rect_deltas) > 1:
        raise NotImplementedError('Only basic flap_options are supported.')
      flap_id = flap_modification.flap_id
      [flap_delta] = flap_modification.rect_deltas

      if flap_modification.flap_id in added_deltas:
        added_delta = added_deltas[flap_id]
        # Check if the option is precluded by an added delta. This is the case
        # if the option does not share an axis with the added delta.
        if added_delta.direction != flap_delta.delta.direction:
          continue

        # Check if an option is a subdelta of an added delta. If so,
        # it has already been added.
        if flap_delta.delta.is_subdelta_of(added_delta):
          continue

      if isinstance(remaining_options, set):
        remaining_options.add(flap_modification)
      elif flap_modification not in remaining_options:
        remaining_options.append(flap_modification)
    if not remaining_options:
      raise ImpossibleTilingError(
          f'No valid options for cell {cell}. Added deltas: {added_deltas}'
      )
    filtered_options[cell] = remaining_options

  return filtered_options


def _find_solution_by_brute_force(
    options_by_cell: dict[grid.Cell, Sequence[FlapOption] | set[FlapOption]],
    tiling_solution: TilingSolution,
) -> dict[TrackerID, grid.Delta]:
  """Finds a valid tiling solution using brute force.

  This function tries every possible combination of options for each cell and
  returns the first valid solution. If all combinations are tried and no
  solution is found, it raises an ImpossibleTilingError.

  Args:
    options_by_cell: A dictionary mapping empty cells to possible flap
      perturbations that will cover them.
    tiling_solution: The current tiling solution.

  Returns:
    A valid tiling solution mapping FlapIDs to the grid.Delta applied to them.

  Raises:
    ImpossibleTilingError: If no valid tiling solution is found.
  """
  logging.info(
      'There are remaining cell options that must be searched: %s',
      options_by_cell,
  )
  logging.info(
      'Estimated number of solutions to test: %d',
      math.prod(map(len, options_by_cell.values())),
  )
  for idx, solution_set in enumerate(
      itertools.product(*options_by_cell.values())
  ):
    if (idx & 63) == 0:
      timeout.maybe_timeout_cooperatively()
    try:
      solution_copy = tiling_solution.clone()
      for flap_option in solution_set:
        solution_copy.add_flap_option(flap_option)
      return solution_copy.grid_deltas
    except ImpossibleTilingError:
      continue

  # After trying all possible combinations, no solution was found.
  raise ImpossibleTilingError('Exhausted all possible cell combinations.')


def _find_solution_by_search(
    options_by_cell: dict[grid.Cell, Sequence[FlapOption] | set[FlapOption]],
    tiling_solution: TilingSolution,
) -> dict[TrackerID, grid.Delta]:
  """Finds a valid tiling solution using a backtracking search.

  For each remaining cell, try adding it. If successful, add it to the solution
  and remove all options that are precluded by the new delta.
  If no options remain for a cell, raise an error.

  When all cells are covered, return the solution.

  Args:
    options_by_cell: A dictionary mapping empty cells to possible flap
      perturbations that will cover them.
    tiling_solution: The current tiling solution.

  Returns:
    A valid tiling solution mapping FlapIDs to the grid.Delta applied to them.

  Raises:
    ImpossibleTilingError: If no valid tiling solution is found.
  """
  timeout.maybe_timeout_cooperatively()
  if not options_by_cell:
    return tiling_solution.grid_deltas

  # Select cell with fewest options to improve search performance.
  cell = min(options_by_cell, key=lambda cell: len(options_by_cell[cell]))
  for flap_modification in options_by_cell[cell]:
    solution_copy = tiling_solution.clone()
    try:
      added_delta = solution_copy.add_flap_option(flap_modification)
      logging.debug('SEARCH Added delta: %s', added_delta)
      logging.debug('SEARCH Current solution: %s', tiling_solution.grid_deltas)
      assert (
          added_delta is not None
      ), 'Null deltas should have been filtered out.'
      remaining_options = _filter_invalid_options(
          options_by_cell, solution_copy.grid_deltas, added_delta.cells
      )
      remaining_options = solution_copy.add_necessary_options(remaining_options)
      return _find_solution_by_search(remaining_options, solution_copy)
    except ImpossibleTilingError:
      continue
  # If all possible options were tried the tiling is impossible
  raise ImpossibleTilingError('Exhausted all possible cell combinations.')


def _find_valid_delta_set(
    options_by_cell: dict[grid.Cell, set[FlapOption]],
    tiling_solution: TilingSolution,
    search_type: config_lib.LocalTilingSearchType,
) -> dict[TrackerID, grid.Delta]:
  """Finds a valid tiling solution from the given cell options."""
  options_by_cell = tiling_solution.add_necessary_options(options_by_cell)
  logging.info('Necessary deltas applied: %s', tiling_solution.grid_deltas)
  if not options_by_cell:
    logging.info('Tiling solution found through necessary deltas.')
    return tiling_solution.grid_deltas

  match search_type:
    case config_lib.LocalTilingSearchType.BRUTE_FORCE:
      return _find_solution_by_brute_force(options_by_cell, tiling_solution)
    case config_lib.LocalTilingSearchType.BACKTRACK:
      return _find_solution_by_search(options_by_cell, tiling_solution)
    case config_lib.LocalTilingSearchType.SKIP:
      raise ImpossibleTilingError(
          f'Skipping search over {len(options_by_cell)} cell options.'
      )
    case _:
      typing.assert_never(search_type)


# Solution post-processing


def _update_tracker_with_deltas(
    tracker: utils_tracker.CreasePatternTracker,
    deltas: dict[TrackerID, grid.Delta],
    is_symmetric: bool,
) -> utils_tracker.CreasePatternTracker:
  """Applies the given deltas to the tracker.

  Modyfing the tracker in place, this function expands the polygons in the
  tracker according to the deltas found in the tiling solution.

  If a flap is on the line of symmetry, it is expanded symmetrically.

  If a delta has an odd magnitude, it means the flap is on the border of the
  crease pattern. In this case, the flap is expanded in both directions along
  the axis of the delta to keep the total expansion even.

  Args:
    tracker: The CreasePatternTracker to update.
    deltas: A dictionary mapping FlapIDs to the grid.Delta to apply.
    is_symmetric: Whether the packing is symmetric.

  Returns:
    The updated CreasePatternTracker.
  """
  for flap_id, delta in deltas.items():
    amount = delta.l1_norm
    if (
        is_symmetric
        and math.isclose(tracker.packed_polygons[flap_id].center.x, 0.5)
        and delta.direction.is_horizontal
    ):
      # expand symmetrically
      dir_or_axis = delta.direction.axis
    elif amount % 2 == 1:
      dir_or_axis = delta.direction.axis
    else:
      dir_or_axis = delta.direction
    tracker.expand_polygon(flap_id, dir_or_axis, amount)
  return tracker


# Main entry point
def find_perfect_tiling_from_local_expansions(
    initial_tracker: utils_tracker.CreasePatternTracker,
    is_symmetric: bool,
    config: config_lib.LocalTilingConfig,
    locked_long_side_flaps: set[str] | None = None,
    legacy_iteration_order: bool = False,
) -> utils_tracker.CreasePatternTracker | None:
  """Given an initial packing, modifies the flaps in the tracker to tile the unfilled space.

  The algorithm is summarized below:
  1. For each empty cell, search each direction to construct a list of possible
     flap expansions that would cover that cell (at most this will be 4 per
     cell, 1 per direction). This is the search space of the tiling problem.
  2. Given this search space, choose one of the options for each empty cell
     such that there are no overlapping expansions.
  3. For each chosen expansion, modify the tracker to apply it.

  If at any point during this process, an empty cell has no valid options, the
  problem is infeasible and we raise an ImpossibleTilingError. This allows us to
  catch it in this function and return early.

  Args:
    initial_tracker: Tracker with the base packing solution.
    is_symmetric: Whether the packing is symmetric.
    config: Settings that control the tiling process.
    locked_long_side_flaps: If provided, prevents these flaps from expanding
      along their long side.
    legacy_iteration_order: If True, preserves legacy set-based option
      deduplication and iteration order.

  Returns:
    The original `CreasePatternTracker` with modified flaps to form a perfect
    tiling. If no local solution is possible, returns None.
  """

  logging.info('Finding tiling solution using local flap perturbations.')
  try:
    cell_options = _get_empty_cell_options(
        config,
        initial_tracker,
        is_symmetric=is_symmetric,
        locked_long_side_flaps=locked_long_side_flaps,
        legacy_iteration_order=legacy_iteration_order,
    )
    tiling_solution = TilingSolution(
        occupancy_grid=initial_tracker.occupancy_grid.copy()
    )
    deltas = _find_valid_delta_set(
        cell_options, tiling_solution, config.search_type
    )
    logging.info('Found the following deltas: %s', deltas)
  except ImpossibleTilingError as e:
    logging.info('Tiling is impossible: %s', e)
    return None

  # Use the deltas from the discovered solution to fill in the tracker.
  return _update_tracker_with_deltas(initial_tracker, deltas, is_symmetric)
