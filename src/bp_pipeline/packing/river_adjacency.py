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

"""Utilities for checking river adjacency and alignment."""

import enum
import math

from .. import rectangle as shaping_utils
from ..stick_figures import stick as stick_lib
from ..stick_figures import stick_figure as stick_figure_lib
from . import river as river_lib
from . import types
from . import utils_tracker


class Side(enum.Enum):
  """Enum for sides of a river."""

  TOP = 'top'
  BOTTOM = 'bottom'
  LEFT = 'left'
  RIGHT = 'right'
  INNER = 'inner'
  OUTER = 'outer'


def rects_adjacent(
    rect1: shaping_utils.Rectangle,
    rect2: shaping_utils.Rectangle,
    tol: float = shaping_utils.EPS,
) -> bool:
  """Checks if two rectangles are adjacent."""
  rect1_x_end = rect1.x_start + rect1.x_len
  rect1_y_end = rect1.y_start + rect1.y_len
  rect2_x_end = rect2.x_start + rect2.x_len
  rect2_y_end = rect2.y_start + rect2.y_len

  x_overlap = max(
      0, min(rect1_x_end, rect2_x_end) - max(rect1.x_start, rect2.x_start)
  )
  y_overlap = max(
      0, min(rect1_y_end, rect2_y_end) - max(rect1.y_start, rect2.y_start)
  )

  if math.isclose(rect1_x_end, rect2.x_start, abs_tol=tol) and y_overlap > tol:
    return True
  if math.isclose(rect2_x_end, rect1.x_start, abs_tol=tol) and y_overlap > tol:
    return True
  if math.isclose(rect1_y_end, rect2.y_start, abs_tol=tol) and x_overlap > tol:
    return True
  if math.isclose(rect2_y_end, rect1.y_start, abs_tol=tol) and x_overlap > tol:
    return True
  return False


def are_rivers_geometrically_adjacent(
    river1: types.RiverPlacementAlias,
    river2: types.RiverPlacementAlias,
    tol: float = shaping_utils.EPS,
) -> bool:
  """Checks if two rivers are geometrically adjacent."""
  for r1 in river1.rectangles:
    for r2 in river2.rectangles:
      if rects_adjacent(r1, r2, tol):
        return True
  return False


def are_angularly_adjacent_at_joint(
    stick_figure: stick_figure_lib.StickFigure,
    stick1: stick_lib.Stick,
    stick2: stick_lib.Stick,
    joint_name: str,
) -> bool:
  """Checks if stick1 and stick2 are angularly adjacent at joint_name."""
  joint = stick_figure.joints[joint_name]
  num_sticks = len(joint.sticks)
  if num_sticks <= 1:
    return False
  try:
    idx1 = joint.sticks.index(stick1)
    idx2 = joint.sticks.index(stick2)
  except ValueError:
    return False
  return (idx1 + 1) % num_sticks == idx2 or (idx2 + 1) % num_sticks == idx1


def share_joint_with_no_sticks_between(
    stick1: stick_lib.Stick,
    stick2: stick_lib.Stick,
    stick_figure: stick_figure_lib.StickFigure,
) -> bool:
  """True if sticks share a joint and are angularly adjacent at one of them."""
  s1_joints = {stick1.start, stick1.end}
  s2_joints = {stick2.start, stick2.end}
  shared_joints = s1_joints.intersection(s2_joints)
  if not shared_joints:
    return False
  for j in shared_joints:
    if are_angularly_adjacent_at_joint(stick_figure, stick1, stick2, j):
      return True
  return False


def get_adjacent_river_constraints(
    river: types.RiverPlacementAlias,
    stick: stick_lib.Stick,
    tracker: utils_tracker.CreasePatternTracker,
    stick_figure: stick_figure_lib.StickFigure,
) -> dict[str, Side]:
  """Computes constraints on side assignment due to adjacent rivers."""
  constraints = {}
  for placed_river_name, placed_river in tracker.packed_rivers.items():
    if placed_river_name not in stick_figure:
      continue
    placed_stick = stick_figure[placed_river_name]
    if share_joint_with_no_sticks_between(
        stick, placed_stick, stick_figure
    ) and are_rivers_geometrically_adjacent(river, placed_river):
      common_joints = {stick.start, stick.end} & {
          placed_stick.start,
          placed_stick.end,
      }
      if isinstance(river, river_lib.River):
        for common_joint in common_joints:
          if river.orientation == river_lib.RiverOrientation.HORIZONTAL:
            is_placed_above = any(
                math.isclose(
                    placed_river_rectangle.y_start
                    + placed_river_rectangle.y_len,
                    river.offset,
                    abs_tol=shaping_utils.EPS,
                )
                for placed_river_rectangle in placed_river.rectangles
            )
            is_placed_below = any(
                math.isclose(
                    placed_river_rectangle.y_start,
                    river.offset + river.width,
                    abs_tol=shaping_utils.EPS,
                )
                for placed_river_rectangle in placed_river.rectangles
            )
            if is_placed_above:
              constraints[common_joint] = Side.BOTTOM  # cj cannot be top
            elif is_placed_below:
              constraints[common_joint] = Side.TOP  # cj cannot be bottom
          else:  # VERTICAL
            is_placed_left = any(
                math.isclose(
                    placed_river_rectangle.x_start
                    + placed_river_rectangle.x_len,
                    river.offset,
                    abs_tol=shaping_utils.EPS,
                )
                for placed_river_rectangle in placed_river.rectangles
            )
            is_placed_right = any(
                math.isclose(
                    placed_river_rectangle.x_start,
                    river.offset + river.width,
                    abs_tol=shaping_utils.EPS,
                )
                for placed_river_rectangle in placed_river.rectangles
            )
            if is_placed_left:
              constraints[common_joint] = Side.RIGHT  # cj cannot be left
            elif is_placed_right:
              constraints[common_joint] = Side.LEFT  # cj cannot be right
      elif isinstance(river, river_lib.LShapedRiver):
        inner_mask, outer_mask = river.get_area_masks(river.grid_size)
        placed_river_cells = set()
        for rect in placed_river.rectangles:
          for y in range(int(rect.y_start), int(rect.y_start + rect.y_len)):
            for x in range(int(rect.x_start), int(rect.x_start + rect.x_len)):
              placed_river_cells.add((y, x))
        touches_inner = False
        for y, x in placed_river_cells:
          if inner_mask[y, x]:
            touches_inner = True
            break
        touches_outer = False
        for y, x in placed_river_cells:
          if outer_mask[y, x]:
            touches_outer = True
            break
        for common_joint in common_joints:
          if touches_inner:
            constraints[common_joint] = Side.OUTER  # cj cannot be inner
          elif touches_outer:
            constraints[common_joint] = Side.INNER  # cj cannot be outer
  return constraints
