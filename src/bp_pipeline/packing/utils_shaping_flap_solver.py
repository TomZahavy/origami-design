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

"""Solver that applies heuristics for stick figures with shaping flaps."""

from collections.abc import Sequence
import dataclasses
import itertools
import logging
import typing

import numpy as np

from .. import rectangle as shaping_utils
from ..stick_figures import stick as stick_lib
from ..stick_figures import stick_figure as stick_figure_lib
from . import config as config_lib
from . import river as river_lib
from . import scoring
from . import types
from . import utils_packing_flaps
from . import utils_packing_svg
from . import utils_river_solver
from . import utils_tracker
from .debug import debug_types

Orientations = typing.Literal['Wide', 'Tall']
Corner = typing.Literal['BottomLeft', 'BottomRight', 'TopLeft', 'TopRight']
Edge = typing.Literal['Bottom', 'Top', 'Left', 'Right']


def _get_coordinate(
    grid_size: int, polygon_size: int, align_right_or_top: bool
) -> int:
  """Computes the coordinate for packing a polygon in the corner of the paper, using its size.

  Args:
    grid_size: The grid size of the paper.
    polygon_size: The size of the polygon to be packed.
    align_right_or_top: If True, align to the right or top, by returning
      grid_size - polygon_size. If False, returns 0 for left or bottom
      alignment.

  Returns:
    The coordinate for the polygon.
  """
  return grid_size - polygon_size if align_right_or_top else 0


def _get_hugging_side(
    corner_def: Corner, orientation: Orientations
) -> river_lib.HugSide:
  """Returns the hugging side for river placement based on corner and orientation.

  Args:
    corner_def: The corner where the pattern is placed.
    orientation: The orientation of the pattern ('Wide' or 'Tall').

  Returns:
    The hugging side for the river.
  """
  if orientation == 'Wide':
    return (
        river_lib.HugSide.LEFT
        if corner_def in ['BottomLeft', 'TopRight']
        else river_lib.HugSide.RIGHT
    )
  else:  # tall
    return (
        river_lib.HugSide.LEFT
        if corner_def in ['BottomLeft', 'TopLeft']
        else river_lib.HugSide.RIGHT
    )


@dataclasses.dataclass
class KneePattern:
  """Handles a specific stick figure pattern of 3 sticks.

  This pattern consists of one river, one shaping flap, and one normal flap.

  Attributes:
    shaping_flap: Shaping flap.
    normal_flap: A flap that is not a shaping flap.
    other: The third stick connected to the joint, which is a river.
    joint_name: The name of the joint connecting the three sticks.
  """

  shaping_flap: stick_lib.Stick
  normal_flap: stick_lib.Stick
  other: stick_lib.Stick
  joint_name: str

  def get_total_size(self, orientation: Orientations) -> tuple[int, int]:
    """Returns the required packing size of the pattern.

    Args:
      orientation: The orientation of the pattern.

    Returns:
      A tuple (width, height) of the required packing size.
    """
    short_side = self.normal_flap.length + 2 * self.other.length
    long_side = short_side + 2 * self.shaping_flap.length
    if orientation == 'Wide':
      return (long_side, short_side)
    else:
      return (short_side, long_side)

  def get_shaping_flap_size(self, orientation: Orientations) -> tuple[int, int]:
    """Returns the size of the shaping flap.

    Args:
      orientation: The orientation of the pattern.

    Returns:
      A tuple (width, height) for the shaping flap.
    """
    short_side = self.normal_flap.length
    long_side = 2 * self.shaping_flap.length
    if orientation == 'Wide':
      return (long_side, short_side)
    else:  # tall
      return (short_side, long_side)

  def get_normal_flap_size(self) -> tuple[int, int]:
    """Returns the size of the normal flap.

    Returns:
      A tuple (width, height) for the normal flap.
    """
    return (self.normal_flap.length, self.normal_flap.length)

  def compute_placement_and_pack_polygons(
      self,
      orientation: typing.Literal['Wide', 'Tall'],
      corner_def: Corner,
      grid_size: int,
  ) -> tuple[dict[str, types.PolygonPlacement], river_lib.HuggingRiver]:
    """Computes individual placements for sticks in a shaping pattern.

    Args:
      orientation: The orientation of the pattern.
      corner_def: The corner where the pattern is placed.
      grid_size: The size of the grid.

    Returns:
      A tuple containing a dictionary of polygon placements and the hugging
      river.
    """
    corner_w, corner_h = self.get_total_size(orientation)
    normal_flap_size = self.get_normal_flap_size()
    shaping_flap_size = self.get_shaping_flap_size(orientation)
    return self.pack_polygons(
        orientation,
        corner_def,
        grid_size,
        corner_w,
        corner_h,
        normal_flap_size,
        shaping_flap_size,
    )

  def pack_polygons(
      self,
      orientation: typing.Literal['Wide', 'Tall'],
      corner_def: Corner,
      grid_size: int,
      corner_w: int,
      corner_h: int,
      normal_flap_size: tuple[int, int],
      shaping_flap_size: tuple[int, int],
  ) -> tuple[dict[str, types.PolygonPlacement], river_lib.HuggingRiver]:
    """Places flaps and river in the grid.

    Args:
      orientation: The orientation of the pattern.
      corner_def: The corner where the pattern is placed.
      grid_size: The size of the grid.
      corner_w: The width of the corner block.
      corner_h: The height of the corner block.
      normal_flap_size: The size of the non-shaping flap.
      shaping_flap_size: The size of the shaping flap.

    Returns:
      A tuple containing a dictionary of polygon placements and the hugging
      river.
    """

    normal_flap_width, normal_flap_height = normal_flap_size
    shaping_flap_width, shaping_flap_height = shaping_flap_size

    pack_on_right = corner_def in ['BottomRight', 'TopRight']
    pack_on_top = corner_def in ['TopLeft', 'TopRight']

    block_offset_x = _get_coordinate(grid_size, corner_w, pack_on_right)
    block_offset_y = _get_coordinate(grid_size, corner_h, pack_on_top)

    placements = {}

    # Normal flap placement
    normal_flap_x = _get_coordinate(corner_w, normal_flap_width, pack_on_right)
    normal_flap_y = _get_coordinate(corner_h, normal_flap_height, pack_on_top)
    placements[self.normal_flap.name] = types.PolygonPlacement.from_grid_coords(
        size=(normal_flap_width, normal_flap_height),
        offset=(block_offset_x + normal_flap_x, block_offset_y + normal_flap_y),
        grid_size=grid_size,
    )

    # Shaping flap placement
    if orientation == 'Wide':
      shaping_flap_x = (
          normal_flap_x - shaping_flap_width
          if pack_on_right
          else normal_flap_x + normal_flap_width
      )
      shaping_flap_y = normal_flap_y
    else:  # tall
      shaping_flap_x = normal_flap_x
      shaping_flap_y = (
          normal_flap_y - shaping_flap_height
          if pack_on_top
          else normal_flap_y + normal_flap_height
      )
    placements[self.shaping_flap.name] = (
        types.PolygonPlacement.from_grid_coords(
            size=(shaping_flap_width, shaping_flap_height),
            offset=(
                block_offset_x + shaping_flap_x,
                block_offset_y + shaping_flap_y,
            ),
            grid_size=grid_size,
        )
    )

    # Compute occupancy grid for river placement
    occupancy_grid = np.zeros((grid_size, grid_size), dtype=bool)
    for flap_name in [self.normal_flap.name, self.shaping_flap.name]:
      placement = placements[flap_name]
      rect = shaping_utils.Rectangle(
          name=flap_name,
          x_start=placement.offset[0],
          y_start=placement.offset[1],
          x_len=placement.size[0],
          y_len=placement.size[1],
      )
      utils_packing_flaps.set_grid_occupation(occupancy_grid, rect, True)

    # Place river
    if orientation == 'Wide':
      if corner_def == 'BottomLeft':
        start_cell = (
            block_offset_y + normal_flap_y + normal_flap_height,
            block_offset_x + normal_flap_x,
        )
      elif corner_def == 'BottomRight':
        start_cell = (
            block_offset_y + shaping_flap_y,
            block_offset_x + shaping_flap_x - 1,
        )
      elif corner_def == 'TopLeft':
        start_cell = (
            block_offset_y + normal_flap_y - 1,
            block_offset_x + normal_flap_x,
        )
      else:  # TopRight
        start_cell = (
            block_offset_y + shaping_flap_y + shaping_flap_height - 1,
            block_offset_x + shaping_flap_x - 1,
        )
    else:  # tall
      if corner_def == 'BottomLeft':
        start_cell = (
            block_offset_y + normal_flap_y,
            block_offset_x + normal_flap_x + normal_flap_width,
        )
      elif corner_def == 'BottomRight':
        start_cell = (
            block_offset_y + normal_flap_y,
            block_offset_x + normal_flap_x - 1,
        )
      elif corner_def == 'TopLeft':
        start_cell = (
            block_offset_y + shaping_flap_y - 1,
            block_offset_x + shaping_flap_x,
        )
      else:  # TopRight
        start_cell = (
            block_offset_y + shaping_flap_y - 1,
            block_offset_x + shaping_flap_x + shaping_flap_width - 1,
        )
    hug_side = _get_hugging_side(corner_def, orientation)

    river = river_lib.HuggingRiver.from_contour(
        grid_size=grid_size,
        width=2 * self.other.length,
        occupancy_grid=occupancy_grid,
        start_cell=start_cell,
        hug_side=hug_side,
    )
    return placements, river


def _create_flap_pattern_from_sticks_and_joint_name(
    sticks: Sequence[stick_lib.Stick], joint_name: str
) -> KneePattern | None:
  """Creates a FlapPattern if sticks match the pattern, else returns None.

  Args:
    sticks: A sequence of sticks connected at a joint.
    joint_name: The name of the joint.

  Returns:
    A ThreeFlapPattern if the sticks match the pattern, otherwise None.
  """
  if len(sticks) == 3:
    shaping_sticks = [s for s in sticks if s.shaping_flap]
    normal_flaps = [s for s in sticks if not s.shaping_flap and not s.is_river]
    if len(shaping_sticks) == 1 and len(normal_flaps) == 1:
      found_names = {shaping_sticks[0].name, normal_flaps[0].name}
      other_stick = next(s for s in sticks if s.name not in found_names)
      return KneePattern(
          shaping_flap=shaping_sticks[0],
          normal_flap=normal_flaps[0],
          other=other_stick,
          joint_name=joint_name,
      )
  return None


@dataclasses.dataclass
class TailPattern:
  """Handles tail patterns (see TAIL_SIMPLE in example_trees.py).

  The tail starts with a shaping flap on a stick (that is neither a flap nor a
  river).
  This second stick is treated as a river.
  This is followed by a sequence of shaping flaps with a river between them.

  Attributes:
    n_flaps: Number of flaps on the tail.
    flap_length: Length of the flap.
    flap_width: Width of the flap.
    river_length: Length of the rivers between flaps.  By construction, the
      flaps and rivers must have the same width so that the tail has one width.
      Therefore, width is set by the flap width.
    shaping_flaps: List of shaping flap sticks in order.
    connecting_rivers: List of river sticks in order.
  """

  n_flaps: int
  flap_length: int = 1
  flap_width: int = 2
  river_length: int = 1
  shaping_flaps: list[stick_lib.Stick] = dataclasses.field(default_factory=list)
  connecting_rivers: list[stick_lib.Stick] = dataclasses.field(
      default_factory=list
  )

  def __post_init__(self):
    if self.n_flaps < 1:
      raise ValueError(f'n_flaps must be >= 1, got {self.n_flaps}')
    if self.flap_length < 1:
      raise ValueError(f'flap_length must be >= 1, got {self.flap_length}')
    if self.flap_width < 1:
      raise ValueError(f'flap_width must be >= 1, got {self.flap_width}')
    if self.river_length < 1:
      raise ValueError(f'river_length must be >= 1, got {self.river_length}')

  def get_polygon_sizes(self) -> tuple[list[tuple[int, int]], list[int]]:
    """Returns the required packing size of the tail.

    Returns:
      A tuple containing:
        - A list of dimensions for each step of packing (flaps and rivers).
        - A list of widths for each flap.
    """

    # Hugging rivers add 2*self.river_width to the width, and self.river_width
    # to the height.
    def add_river(dims):
      return (
          dims[-1][0] + 2 * self.river_length,
          dims[-1][1] + self.river_length,
      )

    # Rule: flaps are packed on top of the previous polygons.
    # Therefore a flaps adds 2*self.flap_length to the height but not the width.
    def add_flap(dims):
      return (dims[-1][0], dims[-1][1] + 2 * self.flap_length)

    # one flap
    dims = [(self.flap_width, self.flap_length)]
    flap_widths = [self.flap_width]
    dims.append(add_river(dims))
    for _ in range(1, self.n_flaps):
      flap_dim = add_flap(dims)
      dims.append(flap_dim)
      flap_widths.append(flap_widths[-1] + 2 * self.river_length)
      river_dim = add_river(dims)
      dims.append(river_dim)

    return dims, flap_widths

  def pack_polygons(
      self,
      tracker: utils_tracker.CreasePatternTracker,
      grid_size: int,
      debug: debug_types.DebugConfig,
  ) -> tuple[
      dict[str, types.PolygonPlacement],
      utils_tracker.CreasePatternTracker,
      river_lib.HuggingRiver,
  ]:
    """Places flaps and river in the grid.

    Args:
      tracker: The crease pattern tracker.
      grid_size: The size of the grid.
      debug: Packing debug config.

    Returns:
      A tuple containing:
        - A dictionary of polygon placements for the flaps.
        - The updated crease pattern tracker.
        - The main river of the tail pattern.
    """
    placements = {}
    main_river = None

    # initiate variable to middle of the grid
    center_x = grid_size // 2
    top_right_y = 0
    # initial river position
    river_y = 0
    _, widths = self.get_polygon_sizes()

    for i in range(self.n_flaps):
      # place flap as polygon
      flap_w, flap_h = widths[i], 2 * self.flap_length
      top_left_x = center_x - flap_w // 2

      if i != 0:
        top_right_y += 2 * self.flap_length + self.river_length

      placement = types.PolygonPlacement.from_grid_coords(
          size=(flap_w, flap_h),
          offset=(top_left_x, top_right_y),
          grid_size=grid_size,
      )
      flap_name = self.shaping_flaps[i].name
      placements[flap_name] = placement
      tracker.add_polygon(flap_name, placement)
      if debug.is_active():
        debug.record_step(
            tracker, 'INFO', f'Heuristic: Placed tail polygon {flap_name}'
        )
      # place hugging river around polygon.
      river_x = top_left_x - 1
      hug_side = river_lib.HugSide.LEFT
      river = river_lib.HuggingRiver.from_contour(
          grid_size=grid_size,
          width=self.river_length,
          occupancy_grid=tracker.occupancy_grid,
          start_cell=(river_y, river_x),  # (y,x)
          hug_side=hug_side,
      )
      if i == 0:
        main_river = river
      tracker.add_river(self.connecting_rivers[i].name, river)
      if debug.is_active():
        debug.record_step(
            tracker,
            'INFO',
            f'Heuristic: Placed tail river {self.connecting_rivers[i].name}',
        )

    if main_river is None:
      raise ValueError('No river placed.')
    return placements, tracker, main_river


def _find_tail_pattern_from_leaf_stick(
    leaf_stick: stick_lib.Stick,
    leaf_joint_name: str,
    stick_figure: stick_figure_lib.StickFigure,
    processed_stick_names: set[str],
) -> tuple[TailPattern, list[stick_lib.Stick], list[stick_lib.Stick]] | None:
  """Finds the tail pattern from a leaf stick.

  Args:
    leaf_stick: Candidate stick for the end of the tail pattern.
    leaf_joint_name: The name of the degree-2 joint.
    stick_figure: The stick figure to process.
    processed_stick_names: A set of names of sticks that have already been
      processed as part of other patterns.

  Returns:
    A tuple of (TailPattern, list of sticks in the tail) if a tail pattern is
    found, otherwise None.
  """
  if not leaf_stick.shaping_flap:
    return None
  if not leaf_stick.width.is_integer():
    return None

  flap_path = [leaf_stick]
  curr_stick = leaf_stick
  prev_joint_name = leaf_joint_name

  shaping_flap_length = leaf_stick.length
  shaping_flap_width = int(leaf_stick.width)
  river_length = -1

  # find next stick in path
  river_path = []
  next_joint_name = (
      curr_stick.start if curr_stick.end == prev_joint_name else curr_stick.end
  )
  joint_sticks = stick_figure.joints[next_joint_name].sticks
  next_stick = [s for s in joint_sticks if s.name != curr_stick.name][0]
  if not (next_stick.is_river) and not (next_stick.is_flap):
    river_path.append(next_stick)
    curr_stick = next_stick
    prev_joint_name = next_joint_name
  else:
    return None

  while True:
    next_joint_name = (
        curr_stick.start
        if curr_stick.end == prev_joint_name
        else curr_stick.end
    )
    next_joint = stick_figure.joints[next_joint_name]
    if next_joint.degree != 3:
      break

    other_sticks = [s for s in next_joint.sticks if s.name != curr_stick.name]
    s1, s2 = other_sticks
    if s1.name in processed_stick_names or s2.name in processed_stick_names:
      break
    # Check for river-shaping flap pattern.
    if s1.is_river and s2.shaping_flap:
      river, shaping = s1, s2
    elif s2.is_river and s1.shaping_flap:
      river, shaping = s2, s1
    else:
      break

    if not shaping.width.is_integer():
      break
    # Check for consistent lengths and widths.
    if (
        shaping.length != shaping_flap_length
        or int(shaping.width) != shaping_flap_width
    ):
      break
    if river_length == -1:
      river_length = river.length
    elif river.length != river_length:
      break

    flap_path.append(shaping)
    river_path.append(river)

    curr_stick = river
    prev_joint_name = next_joint_name

  if len(flap_path) >= 2 and river_path:
    pattern = TailPattern(
        n_flaps=len(flap_path),
        flap_length=shaping_flap_length,
        flap_width=shaping_flap_width,
        river_length=river_length,
        shaping_flaps=flap_path,
        connecting_rivers=river_path,
    )
    # require polygon sizes to be even
    dims, _ = pattern.get_polygon_sizes()
    if dims[-1][0] % 2 == 0 and dims[-1][1] % 2 == 0:
      return pattern, flap_path, river_path
  return None


def find_tail_patterns(
    stick_figure: stick_figure_lib.StickFigure,
) -> tuple[list[TailPattern], set[str]]:
  """Finds tail patterns in stick figure.

  A tail pattern is defined as sequence of SF-R-SF-... sticks starting
  with a SF stick connected to a degree-1 joint, where internal joints
  are degree-2, and all SFs and Rivers have consistent lengths respectively.

  Args:
    stick_figure: The stick figure to process.

  Returns:
    A tuple of (list of TailPatterns found, list of sticks in tail patterns).
  """
  tail_patterns = []
  tail_sticks_list = set()

  for stick in stick_figure.children:
    if stick.shaping_flap and (stick.name not in tail_sticks_list):
      for joint_name in [stick.start, stick.end]:
        if stick_figure.joints[joint_name].degree == 1:
          result = _find_tail_pattern_from_leaf_stick(
              stick, joint_name, stick_figure, tail_sticks_list
          )
          if result:
            pattern, flap_path, river_path = result
            tail_patterns.append(pattern)
            curr_sticks = [f.name for f in flap_path] + [
                f.name for f in river_path
            ]
            tail_sticks_list.update(curr_sticks)
            break
  return tail_patterns, tail_sticks_list


def find_shaping_patterns(
    stick_figure: stick_figure_lib.StickFigure,
) -> list[KneePattern]:
  """Finds 3-stick joints with 1 shaping flap and 1 normal flap.

  Args:
    stick_figure: The stick figure to process.

  Returns:
    A list of ThreeFlapPattern objects found in the stick figure.
  """
  patterns = []
  processed_joints = set()
  for joint_name, joint in stick_figure.joints.items():
    if joint_name in processed_joints:
      continue
    sticks = joint.sticks
    # Heuristic: 3 sticks sharing a joint, one is shaping, one is normal flap.
    pattern = _create_flap_pattern_from_sticks_and_joint_name(
        sticks, joint_name
    )
    if pattern:
      patterns.append(pattern)
      # Mark all joints of included sticks as processed to avoid overlap
      for s in sticks:
        processed_joints.add(s.start)
        processed_joints.add(s.end)
  return patterns


# pack larger polygon
def _place_corner_blocks_for_orientation(
    patterns: list[KneePattern],
    orientation_choices: tuple[Orientations, ...],
    grid_size: int,
    is_symmetric: bool,
    corner_assignment: list[Corner],
) -> (
    tuple[
        utils_tracker.CreasePatternTracker,
        dict[str, dict[str, stick_lib.Stick]],
        dict[str, dict[str, str | None]],
    ]
    | None
):
  """Tries to place corner blocks for a given orientation.

  Args:
    patterns: List of ThreeFlapPattern to place.
    orientation_choices: Tuple of orientations for each pattern.
    grid_size: The size of the grid.
    is_symmetric: Whether to place symmetric counterparts.
    corner_assignment: List of corners to assign to patterns.

  Returns:
    A tuple containing the tracker, info about placed sticks, and info about
    symmetric placed sticks, or None if placement fails.
  """
  initial_tracker = utils_tracker.CreasePatternTracker(grid_size)
  placed_sticks_info = {}
  symmetric_placed_sticks_info = {}

  for pattern_idx, pattern in enumerate(patterns):
    # non-shaping flap (packed in corner)
    normal_flap = pattern.normal_flap
    # shaping flap
    shaping_flap = pattern.shaping_flap
    # other stick, packed as river.
    other = pattern.other

    corner_w, corner_h = pattern.get_total_size(
        orientation_choices[pattern_idx]
    )

    corner = corner_assignment[pattern_idx]
    offset_x = (
        grid_size - corner_w if corner in ['BottomRight', 'TopRight'] else 0
    )
    offset_y = grid_size - corner_h if corner in ['TopLeft', 'TopRight'] else 0
    offset = (offset_x, offset_y)

    if not (
        0 <= offset_x
        and 0 <= offset_y
        and offset_x + corner_w <= grid_size
        and offset_y + corner_h <= grid_size
    ):
      logging.warning(
          "Corner heuristic block W=%d, H=%d doesn't fit in grid %d for"
          ' pattern %d.',
          corner_w,
          corner_h,
          grid_size,
          pattern_idx,
      )
      return None
    block_name = f'corner_block_{pattern_idx}'
    placement = types.PolygonPlacement.from_grid_coords(
        size=(corner_w, corner_h),
        offset=offset,
        grid_size=grid_size,
    )
    try:
      logging.info(
          'Placing corner block %s at %s with size %s for sticks %s,%s,%s',
          block_name,
          offset,
          (corner_w, corner_h),
          shaping_flap.name,
          normal_flap.name,
          other.name,
      )
      stick_placements, river = pattern.compute_placement_and_pack_polygons(
          orientation_choices[pattern_idx],
          corner_assignment[pattern_idx],
          grid_size,
      )
      for stick in [normal_flap, shaping_flap]:
        initial_tracker.add_polygon(stick.name, stick_placements[stick.name])
      initial_tracker.add_river(other.name, river)
      other_joint_name = other.other_joint_name(pattern.joint_name)
      joint_to_side = {
          pattern.joint_name: 'hugging',
          other_joint_name: 'opposite',
      }
      utils_river_solver.add_river_adjacent_cells(
          initial_tracker,
          other.name,
          river,
          joint_to_side,
      )
      placed_sticks_info[block_name] = {
          'shaping_flap': shaping_flap,
          'normal_flap': normal_flap,
          'other': other,
      }

      if is_symmetric:
        mirrored_placement = utils_packing_svg.get_mirrored_polygon_placement(
            placement, grid_size
        )
        mirrored_block_name = f'{block_name}_symmetric'
        symmetric_placed_sticks_info[mirrored_block_name] = {
            'shaping_flap': shaping_flap.symmetric_stick_name,
            'normal_flap': normal_flap.symmetric_stick_name,
            'other': other.symmetric_stick_name,
        }
        logging.info(
            'Placing symmetric corner block %s at %s with size %s for'
            ' sticks %s,%s,%s',
            mirrored_block_name,
            mirrored_placement.offset,
            mirrored_placement.size,
            shaping_flap.symmetric_stick_name,
            normal_flap.symmetric_stick_name,
            other.symmetric_stick_name,
        )
        mirrored_stick_placements = {
            stick_name: utils_packing_svg.get_mirrored_polygon_placement(
                pl, grid_size
            )
            for stick_name, pl in stick_placements.items()
        }
        if normal_flap.symmetric_stick_name:
          initial_tracker.add_polygon(
              normal_flap.symmetric_stick_name,
              mirrored_stick_placements[normal_flap.name],
          )
        if shaping_flap.symmetric_stick_name:
          initial_tracker.add_polygon(
              shaping_flap.symmetric_stick_name,
              mirrored_stick_placements[shaping_flap.name],
          )
        if other.symmetric_stick_name:
          initial_tracker.add_river(
              other.symmetric_stick_name,
              river.mirror(grid_size),
          )
    except ValueError as e:
      logging.warning(
          'Could not place corner block %d or its symmetric counterpart '
          'due to overlap: %s',
          pattern_idx,
          e,
      )
      return None
  return initial_tracker, placed_sticks_info, symmetric_placed_sticks_info


def solve_with_shaping_heuristic(
    tree: stick_figure_lib.StickFigure,
    *,
    debug: debug_types.DebugConfig,
    grid_size: int,
    is_symmetric: bool,
    symmetry_axes: dict[str, bool] | None,
    scoring_config: scoring.ScoringConfig,
    max_solutions: int,
    config: config_lib.PackingConfig = config_lib.PackingConfig(),
) -> list[utils_tracker.CreasePatternTracker] | None:
  """Applies corner heuristic for shaping flaps and solves for the rest.

  If a 3-stick joint pattern (1 shaping flap, 1 normal flap, 1 other)
  is found, it is placed in a corner for this pattern and
  then calls the river solver to pack the remaining sticks in the
  unoccupied space.

  Args:
    tree: The stick figure to process.
    debug: Debug configuration object.
    grid_size: The size of the grid.
    is_symmetric: If True, symmetry constraints are applied.
    symmetry_axes: A dict indicating which stick names are on a symmetry axis.
    scoring_config: Function used to score potential flap placements.
    max_solutions: The maximum number of solutions to return.
    config: Packing configuration.

  Returns:
    A list of trackers with all rivers and flaps packed if solution is found,
    otherwise None if heuristic doesn't apply or fails.
  """
  tail_patterns, placed_stick_names = find_tail_patterns(tree)
  if tail_patterns:
    logging.info('Tail patterns found. Applying tail heuristic.')
    tracker = utils_tracker.CreasePatternTracker(grid_size)
    for pattern in tail_patterns:
      try:
        _, tracker, _ = pattern.pack_polygons(tracker, grid_size, debug=debug)
      except ValueError as e:
        logging.warning('Could not place tail pattern due to overlap: %s', e)
        return None

    logging.info(
        'Tail patterns placed. Calling river solver for remaining sticks...'
    )
    river_solutions = utils_river_solver.solve_rivers_iteratively(
        tree,
        debug=debug,
        grid_size=grid_size,
        is_symmetric=is_symmetric,
        symmetry_axes=symmetry_axes,
        scoring_config=scoring_config,
        max_solutions=max_solutions,
        initial_tracker=tracker,
        ignore_sticks=placed_stick_names,
        config=config,
    )
    if not river_solutions:
      raise ValueError('River solver failed after placing tail patterns.')
    return river_solutions

  three_flap_patterns = find_shaping_patterns(tree)
  if not three_flap_patterns:
    logging.info('No shaping flap patterns found for heuristic.')
    return None

  all_solutions = []
  num_patterns = len(three_flap_patterns)
  corner_defs = typing.get_args(Corner)
  orientation = list(itertools.product(('Wide', 'Tall'), repeat=num_patterns))
  for corner_assignment in itertools.permutations(corner_defs, num_patterns):
    for orientation_choices in orientation:
      placement_result = _place_corner_blocks_for_orientation(
          three_flap_patterns,
          typing.cast(tuple[Orientations, ...], orientation_choices),
          grid_size,
          is_symmetric,
          list(corner_assignment),
      )
      if placement_result is None:
        continue
      tracker, placed_sticks_info, symmetric_placed_sticks_info = (
          placement_result
      )

      placed_stick_names: set[str] = set()
      for info in placed_sticks_info.values():
        placed_stick_names.add(info['shaping_flap'].name)
        placed_stick_names.add(info['normal_flap'].name)
        placed_stick_names.add(info['other'].name)
      for info in symmetric_placed_sticks_info.values():
        if info['shaping_flap']:
          placed_stick_names.add(info['shaping_flap'])
        if info['normal_flap']:
          placed_stick_names.add(info['normal_flap'])
        if info['other']:
          placed_stick_names.add(info['other'])

      logging.info(
          'Corner blocks placed. Calling river solver for remaining sticks...'
      )
      river_solutions = utils_river_solver.solve_rivers_iteratively(
          tree,
          debug=debug,
          grid_size=grid_size,
          is_symmetric=is_symmetric,
          symmetry_axes=symmetry_axes,
          scoring_config=scoring_config,
          max_solutions=max_solutions - len(all_solutions),
          initial_tracker=tracker,
          ignore_sticks=placed_stick_names,
          config=config,
      )

      if not river_solutions:
        logging.warning(
            'River solver failed after placing corner blocks for this'
            ' combination.'
        )
        continue
      all_solutions.extend(river_solutions)
      if len(all_solutions) >= max_solutions:
        all_solutions = all_solutions[:max_solutions]
        break
    if len(all_solutions) >= max_solutions:
      break

  if not all_solutions and three_flap_patterns:
    raise ValueError(
        'No solution found after trying all corner block placements.'
    )
  return all_solutions
