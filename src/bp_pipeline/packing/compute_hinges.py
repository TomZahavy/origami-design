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

"""Utilities for computing hinge creases in packing."""

from typing import Sequence

import numpy as np

from .. import rectangle as shaping_utils
from ..crease_pattern import crease as crease_lib
from ..crease_pattern import point as point_lib
from . import river as river_lib
from . import utils_tracker


def _add_grid_hinge_crease(
    *,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    grid_size: int,
    creases: list[crease_lib.Crease],
) -> None:
  """Creates a hinge crease from grid coordinates and adds it to creases list.

  Args:
    x1: x-coordinate of first point in grid units.
    y1: y-coordinate of first point in grid units.
    x2: x-coordinate of second point in grid units.
    y2: y-coordinate of second point in grid units.
    grid_size: The size of grid.
    creases: The list of creases to append to.
  """
  creases.append(
      crease_lib.Crease(
          point_lib.Point(x=float(x1) / grid_size, y=float(y1) / grid_size),
          point_lib.Point(x=float(x2) / grid_size, y=float(y2) / grid_size),
          fold=crease_lib.Fold.HINGE,
      )
  )


def get_river_border(
    rectangles: Sequence[shaping_utils.Rectangle], grid_size: int
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
  """Get border of union of rectangles.

  Args:
    rectangles: Sequence of rectangles to get border of.
    grid_size: The size of the grid.

  Returns:
    A list of tuples representing the border of the union of the rectangles.
    Each tuple is a line segment represented as a pair of (x, y) coordinates.
  """
  if not rectangles:
    return []
  h, w = grid_size, grid_size
  occupancy = np.zeros((h, w), dtype=bool)
  for rect in rectangles:
    x_start = max(0, int(rect.x_start))
    y_start = max(0, int(rect.y_start))
    x_end = min(w, int(rect.x_start + rect.x_len))
    y_end = min(h, int(rect.y_start + rect.y_len))
    if x_start < x_end and y_start < y_end:
      occupancy[y_start:y_end, x_start:x_end] = True
  creases = []
  for row in range(h):
    for col in range(w):
      if occupancy[row, col]:
        # top
        if row == 0 or not occupancy[row - 1, col]:
          _add_grid_hinge_crease(
              x1=col,
              y1=row,
              x2=col + 1,
              y2=row,
              grid_size=grid_size,
              creases=creases,
          )
        # bottom
        if row == h - 1 or not occupancy[row + 1, col]:
          _add_grid_hinge_crease(
              x1=col,
              y1=row + 1,
              x2=col + 1,
              y2=row + 1,
              grid_size=grid_size,
              creases=creases,
          )
        # left
        if col == 0 or not occupancy[row, col - 1]:
          _add_grid_hinge_crease(
              x1=col,
              y1=row,
              x2=col,
              y2=row + 1,
              grid_size=grid_size,
              creases=creases,
          )
        # right
        if col == w - 1 or not occupancy[row, col + 1]:
          _add_grid_hinge_crease(
              x1=col + 1,
              y1=row,
              x2=col + 1,
              y2=row + 1,
              grid_size=grid_size,
              creases=creases,
          )

  merged_creases = crease_lib.merge_creases(creases, only_trivial=False)
  border_segments = []
  for crease in merged_creases:
    p1 = (
        int(round(crease.p1.x * grid_size)),
        int(round(crease.p1.y * grid_size)),
    )
    p2 = (
        int(round(crease.p2.x * grid_size)),
        int(round(crease.p2.y * grid_size)),
    )
    border_segments.append((p1, p2))
  return border_segments


def _get_hinges_between_layers(
    river: river_lib.HuggingRiver,
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
  """Computes hinges between adjacent layers of a hugging river.

  These hinges separate cells of layer i from cells of layer i+1 when river
  width > 1.

  Args:
    river: The hugging river to compute hinges for.

  Returns:
    A list of hinge lines between layers.
  """
  hinges = []
  if river.width <= 1:
    return hinges
  for i in range(river.width - 1):
    path_i_cells = set(river.subriver_paths[i])
    path_i1_cells = set(river.subriver_paths[i + 1])
    for row, col in path_i_cells:
      if (row, col + 1) in path_i1_cells:
        hinges.append(((col + 1, row), (col + 1, row + 1)))
      if (row + 1, col) in path_i1_cells:
        hinges.append(((col, row + 1), (col + 1, row + 1)))
      if (row, col - 1) in path_i1_cells:
        hinges.append(((col, row), (col, row + 1)))
      if (row - 1, col) in path_i1_cells:
        hinges.append(((col, row), (col + 1, row)))
  return hinges


def _is_consecutive_in_path(
    path: Sequence[tuple[int, int]],
    index: int,
    cell: tuple[int, int],
) -> bool:
  """Checks if a cell is consecutive to a given index in a path.

  Args:
    path: A sequence of (row, col) cells forming the path.
    index: The index of the current cell in the path.
    cell: The cell to check for consecutiveness.

  Returns:
    True if the cell is path[index-1] or path[index+1].
  """
  is_prev = index > 0 and path[index - 1] == cell
  is_next = index < len(path) - 1 and path[index + 1] == cell
  return is_prev or is_next


def _get_hinges_for_180_turns(
    river: river_lib.HuggingRiver,
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
  """Computes hinges for 180-degree turns within each layer of a hugging river.

  These hinges occur when two cells in the same layer path are adjacent but
  not consecutive in the path, indicating the path folds back on itself.

  Args:
    river: The hugging river to compute hinges for.

  Returns:
    A list of hinge lines for 180-degree turns.
  """

  hinges = []
  for i in range(river.width):
    path = river.subriver_paths[i]
    path_cells = set(path)
    is_closed = len(path) > 1 and _are_adjacent(path[0], path[-1])
    for j, (row, col) in enumerate(path):
      # check right neighbor
      right_neighbor = (row, col + 1)
      if right_neighbor in path_cells and not _is_consecutive_in_path(
          path, j, right_neighbor
      ):
        if (
            is_closed
            and _is_wrap_pair(j, len(path))
            and right_neighbor in (path[0], path[-1])
        ):
          continue
        hinges.append(((col + 1, row), (col + 1, row + 1)))
      # check bottom neighbor
      bottom_neighbor = (row + 1, col)
      if bottom_neighbor in path_cells and not _is_consecutive_in_path(
          path, j, bottom_neighbor
      ):
        if (
            is_closed
            and _is_wrap_pair(j, len(path))
            and bottom_neighbor in (path[0], path[-1])
        ):
          continue
        hinges.append(((col, row + 1), (col + 1, row + 1)))
  return hinges


def _are_adjacent(c1: tuple[int, int], c2: tuple[int, int]) -> bool:
  return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) == 1


def _is_wrap_pair(index: int, path_len: int) -> bool:
  return index == 0 or index == path_len - 1


def get_river_hinges(
    final_placement: utils_tracker.CreasePatternTracker,
    grid_size: int,
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
  """Computes hinge creases for all rivers in the placement.

  Args:
    final_placement: The CreasePatternTracker containing the placement.
    grid_size: The size of the grid.

  Returns:
    A list of river hinge lines.
  """
  river_hinges_list = []
  for river in final_placement.packed_rivers.values():
    if isinstance(river, river_lib.River):
      rects = [river.rectangle]
    elif hasattr(river, 'rectangles'):
      rects = river.rectangles
    else:
      continue
    river_hinges_list.extend(get_river_border(rects, grid_size))
    if isinstance(river, river_lib.HuggingRiver):
      river_hinges_list.extend(_get_hinges_between_layers(river))
      river_hinges_list.extend(_get_hinges_for_180_turns(river))
  return river_hinges_list
