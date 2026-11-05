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

"""Utilities for computing ridge creases for rectangles."""

from collections.abc import Callable
import math
from typing import Any

from .. import rectangle as shaping_utils
from ..crease_pattern import point as point_utils
from ..stick_figures import stick as stick_lib
from ..stick_figures import stick_figure as stick_figure_lib
from . import river as river_lib
from . import types as packing_types
from . import utils_tracker


def _create_line_if_valid(
    p1: tuple[float, float],
    p2: tuple[float, float],
) -> list[tuple[tuple[float, float], tuple[float, float]]]:
  """Creates a line segment if its length is above a tolerance threshold."""
  if math.dist(p1, p2) > point_utils.DEFAULT_TOLERANCE:
    return [(p1, p2)]
  return []


def _is_corner(cell: tuple[int, int], grid_size: int) -> bool:
  """Checks if a cell is a corner cell."""
  y, x = cell
  g = grid_size - 1
  return (y == 0 or y == g) and (x == 0 or x == g)


def _segment_shares_border_edge(
    cell1: tuple[int, int], cell2: tuple[int, int], grid_size: int
) -> bool:
  """Checks if cell1 and cell2 lie on the same border edge."""
  y1, x1 = cell1
  y2, x2 = cell2
  g = grid_size - 1
  return (
      (y1 == 0 and y2 == 0)
      or (y1 == g and y2 == g)
      or (x1 == 0 and x2 == 0)
      or (x1 == g and x2 == g)
  )


def _is_segment_on_border_edge(
    cell_to_check: tuple[int, int],
    segment_neighbor: tuple[int, int],
    grid_size: int,
) -> bool:
  """Checks if cell_to_check is on border edge and segment to neighbor lies on it."""
  if _is_corner(cell_to_check, grid_size):
    return False
  return _segment_shares_border_edge(cell_to_check, segment_neighbor, grid_size)


def _compute_ridge_at_border_turn(
    endpoint: tuple[int, int],
    adjacent_path_cell: tuple[int, int],
    is_start_of_path: bool,
    grid_size: int,
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
  """Computes the ridge for a path endpoint on the grid border."""
  y, x = endpoint
  if is_start_of_path:
    dy_out, dx_out = adjacent_path_cell[0] - y, adjacent_path_cell[1] - x
    dy_in, dx_in = 0, 0
    if y == 0 and dx_out != 0:
      dy_in = 1  # Coming from North
    elif y == grid_size - 1 and dx_out != 0:
      dy_in = -1  # Coming from South
    if x == 0 and dy_out != 0:
      dx_in = 1  # Coming from West
    elif x == grid_size - 1 and dy_out != 0:
      dx_in = -1  # Coming from East
  else:  # End of path
    dy_in, dx_in = y - adjacent_path_cell[0], x - adjacent_path_cell[1]
    dy_out, dx_out = 0, 0
    if y == 0 and dx_in != 0:
      dy_out = -1  # Exiting to North
    elif y == grid_size - 1 and dx_in != 0:
      dy_out = 1  # Exiting to South
    if x == 0 and dy_in != 0:
      dx_out = -1  # Exiting to West
    elif x == grid_size - 1 and dy_in != 0:
      dx_out = 1  # Exiting to East

  crossprod = dx_in * dy_out - dy_in * dx_out
  if crossprod == 0:
    return []

  if crossprod > 0:  # Right turn
    if dy_in != 0:  # Vertical in
      ridge = ((x, y), (x + 1, y + 1))
    else:
      ridge = ((x, y + 1), (x + 1, y))
  else:  # Left turn
    if dy_in != 0:  # Vertical in
      ridge = ((x, y + 1), (x + 1, y))
    else:
      ridge = ((x, y), (x + 1, y + 1))
  return [ridge]


def _add_ridges_for_rectangle(
    lines: list[tuple[tuple[float, float], tuple[float, float]]],
    corners1: list[tuple[float, float]],
    corners2: list[tuple[float, float]],
    border_point1: tuple[float, float],
    border_point2: tuple[float, float],
    apply_y_ridge: bool,
    touch1: bool,
    touch2: bool,
    x_start: float,
    y_start: float,
    x_len: float,
    y_len: float,
    is_wide_rectangle: bool,
) -> None:
  """Helper to add ridge lines for wide or tall rectangles."""
  half_width, half_height = x_len / 2.0, y_len / 2.0
  center_x, center_y = x_start + half_width, y_start + half_height
  if is_wide_rectangle:
    merge_point1 = (x_start + half_height, center_y)
    merge_point2 = (x_start + x_len - half_height, center_y)
  else:  # Tall rectangle.
    merge_point1 = (center_x, y_start + half_width)
    merge_point2 = (center_x, y_start + y_len - half_width)
  _add_y_ridge_or_corner_ridges(
      lines,
      corners1,
      border_point1,
      merge_point1,
      apply_y_ridge,
      touch1,
  )
  _add_y_ridge_or_corner_ridges(
      lines,
      corners2,
      border_point2,
      merge_point2,
      apply_y_ridge,
      touch2,
  )
  lines.extend(_create_line_if_valid(merge_point1, merge_point2))


def _get_hugging_river_endpoint_ridges(
    path: list[tuple[int, int]], river: river_lib.HuggingRiver
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
  """Computes ridges for start/end cells of a hugging river path if parallel to border."""
  lines = []
  grid_size = river.grid_size
  if len(path) < 2:
    return []

  if _is_segment_on_border_edge(path[0], path[1], grid_size):
    lines.extend(
        _compute_ridge_at_border_turn(
            endpoint=path[0],
            adjacent_path_cell=path[1],
            is_start_of_path=True,
            grid_size=grid_size,
        )
    )

  if _is_segment_on_border_edge(path[-1], path[-2], grid_size):
    lines.extend(
        _compute_ridge_at_border_turn(
            endpoint=path[-1],
            adjacent_path_cell=path[-2],
            is_start_of_path=False,
            grid_size=grid_size,
        )
    )
  return lines


def _get_hugging_river_internal_turn_ridges(
    path: list[tuple[int, int]],
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
  """Computes ridges for internal turns in a hugging river path."""
  lines = []
  if len(path) < 3:
    return lines

  def _add_turn_ridge(prev_cell, cell, next_cell):
    dy_in, dx_in = cell[0] - prev_cell[0], cell[1] - prev_cell[1]
    dy_out, dx_out = next_cell[0] - cell[0], next_cell[1] - cell[1]
    if (dy_in, dx_in) == (dy_out, dx_out):
      return
    y, x = cell[0], cell[1]
    crossprod = dx_in * dy_out - dy_in * dx_out
    if crossprod > 0:
      if dy_in != 0:
        lines.append(((x, y), (x + 1, y + 1)))
      else:
        lines.append(((x, y + 1), (x + 1, y)))
    elif crossprod < 0:
      if dy_in != 0:
        lines.append(((x, y + 1), (x + 1, y)))
      else:
        lines.append(((x, y), (x + 1, y + 1)))

  for i in range(1, len(path) - 1):
    _add_turn_ridge(path[i - 1], path[i], path[i + 1])

  is_closed = abs(path[0][0] - path[-1][0]) + abs(path[0][1] - path[-1][1]) == 1
  if is_closed:
    _add_turn_ridge(path[-1], path[0], path[1])
    _add_turn_ridge(path[-2], path[-1], path[0])

  return lines


_RIVER_RIDGE_HANDLERS: dict[
    type[Any],
    Callable[..., list[tuple[tuple[float, float], tuple[float, float]]]],
] = {}


def register_river_ridge_handler(
    river_cls: type[Any],
    handler: Callable[
        ..., list[tuple[tuple[float, float], tuple[float, float]]]
    ],
) -> None:
  """Registers a custom ridge line generator for an extended river type."""
  _RIVER_RIDGE_HANDLERS[river_cls] = handler


def get_river_ridge_lines(
    river: river_lib.PackingRiver,
    recovery: bool = False,
    grid_size: int | None = None,
) -> list[tuple[tuple[float, float], tuple[float, float]]]:
  """Calculates ridge creases for rivers."""
  for registered_cls, handler in _RIVER_RIDGE_HANDLERS.items():
    if isinstance(river, registered_cls):
      return handler(river, recovery=recovery, grid_size=grid_size)
  if isinstance(river, river_lib.LShapedRiver):
    w = float(river.width)
    tx, ty = float(river.turn_x), float(river.turn_y)
    if river.l_shape_type == river_lib.LShapeType.BOTTOM_LEFT:
      return [((tx, ty), (tx + w, ty + w))]
    elif river.l_shape_type == river_lib.LShapeType.BOTTOM_RIGHT:
      return [((tx + w, ty), (tx, ty + w))]
    elif river.l_shape_type == river_lib.LShapeType.TOP_LEFT:
      return [((tx, ty + w), (tx + w, ty))]
    elif river.l_shape_type == river_lib.LShapeType.TOP_RIGHT:
      return [((tx + w, ty + w), (tx, ty))]
  elif isinstance(river, river_lib.HuggingRiver):
    int_lines = []
    for path in river.subriver_paths:
      # len(path) > 2 is the approved bugfix preventing 2-cell open subrivers
      # from being misclassified as closed loops.
      is_closed = (
          len(path) > 2
          and abs(path[0][0] - path[-1][0]) + abs(path[0][1] - path[-1][1]) == 1
      )
      if not is_closed:
        int_lines.extend(_get_hugging_river_endpoint_ridges(path, river))
      int_lines.extend(_get_hugging_river_internal_turn_ridges(path))
    float_lines = []
    for p1, p2 in int_lines:
      float_lines.append(
          ((float(p1[0]), float(p1[1])), (float(p2[0]), float(p2[1])))
      )
    return float_lines
  return []


def _add_y_ridge_or_corner_ridges(
    lines_list: list[tuple[tuple[float, float], tuple[float, float]]],
    corners: list[tuple[float, float]],
    y_ridge_border_point: tuple[float, float],
    merge_point: tuple[float, float],
    apply_y_ridge: bool,
    touch_border: bool,
) -> None:
  """Adds Y-ridge or corner ridges to lines_list."""
  if apply_y_ridge and touch_border:
    lines_list.extend(_create_line_if_valid(y_ridge_border_point, merge_point))
  else:
    for corner in corners:
      lines_list.extend(_create_line_if_valid(corner, merge_point))


def _add_ridges_for_square(
    lines: list[tuple[tuple[float, float], tuple[float, float]]],
    *,
    rectangle: shaping_utils.Rectangle,
    touch_left: bool,
    touch_right: bool,
    touch_top: bool,
    touch_bottom: bool,
    center_x: float,
    center_y: float,
    top_left: tuple[float, float],
    top_right: tuple[float, float],
    bottom_right: tuple[float, float],
    bottom_left: tuple[float, float],
    grid_size: int,
    apply_y_ridge: bool = True,
) -> None:
  """Adds the appropriate ridge lines ('X' or 'Y' shape) for a square."""
  is_center_on_corner = rectangle.is_center_on_corner(grid_size)
  should_apply_y = (
      apply_y_ridge
      and not is_center_on_corner
      and (touch_left or touch_right or touch_top or touch_bottom)
  )

  if not should_apply_y:
    lines.extend(_create_line_if_valid(top_left, bottom_right))
    lines.extend(_create_line_if_valid(top_right, bottom_left))
    return

  if rectangle.treat_as_wide_on_border(grid_size):
    _add_ridges_for_rectangle(
        lines=lines,
        corners1=[top_left, bottom_left],
        corners2=[top_right, bottom_right],
        border_point1=(rectangle.x_start, center_y),
        border_point2=(rectangle.x_start + rectangle.x_len, center_y),
        apply_y_ridge=apply_y_ridge,
        touch1=touch_left,
        touch2=touch_right,
        x_start=rectangle.x_start,
        y_start=rectangle.y_start,
        x_len=rectangle.x_len,
        y_len=rectangle.y_len,
        is_wide_rectangle=True,
    )
  else:
    _add_ridges_for_rectangle(
        lines=lines,
        corners1=[top_left, top_right],
        corners2=[bottom_left, bottom_right],
        border_point1=(center_x, rectangle.y_start),
        border_point2=(center_x, rectangle.y_start + rectangle.y_len),
        apply_y_ridge=apply_y_ridge,
        touch1=touch_top,
        touch2=touch_bottom,
        x_start=rectangle.x_start,
        y_start=rectangle.y_start,
        x_len=rectangle.x_len,
        y_len=rectangle.y_len,
        is_wide_rectangle=False,
    )


def get_ridge_lines(
    rectangle: shaping_utils.Rectangle,
    grid_size: int,
    y_ridge_at_border: bool = True,
) -> list[tuple[tuple[float, float], tuple[float, float]]]:
  """Calculates the line segments for the ridge creases of a rectangle."""
  lines = []
  center_x, center_y = rectangle.center
  top_left = rectangle.top_left
  top_right = rectangle.top_right
  bottom_right = rectangle.bottom_right
  bottom_left = rectangle.bottom_left

  touch_left, touch_right, touch_top, touch_bottom = (
      rectangle.get_borders_touched(grid_size)
  )

  if rectangle.is_square:
    _add_ridges_for_square(
        lines=lines,
        rectangle=rectangle,
        touch_left=touch_left,
        touch_right=touch_right,
        touch_top=touch_top,
        touch_bottom=touch_bottom,
        apply_y_ridge=y_ridge_at_border,
        center_x=center_x,
        center_y=center_y,
        top_left=top_left,
        top_right=top_right,
        bottom_right=bottom_right,
        bottom_left=bottom_left,
        grid_size=grid_size,
    )
  elif rectangle.is_wide:
    _add_ridges_for_rectangle(
        lines=lines,
        corners1=[top_left, bottom_left],
        corners2=[top_right, bottom_right],
        border_point1=(rectangle.x_start, center_y),
        border_point2=(rectangle.x_start + rectangle.x_len, center_y),
        apply_y_ridge=True,
        touch1=touch_left,
        touch2=touch_right,
        x_start=rectangle.x_start,
        y_start=rectangle.y_start,
        x_len=rectangle.x_len,
        y_len=rectangle.y_len,
        is_wide_rectangle=True,
    )
  else:  # Tall rectangle case
    _add_ridges_for_rectangle(
        lines=lines,
        corners1=[top_left, top_right],
        corners2=[bottom_left, bottom_right],
        border_point1=(center_x, rectangle.y_start),
        border_point2=(center_x, rectangle.y_start + rectangle.y_len),
        apply_y_ridge=True,
        touch1=touch_top,
        touch2=touch_bottom,
        x_start=rectangle.x_start,
        y_start=rectangle.y_start,
        x_len=rectangle.x_len,
        y_len=rectangle.y_len,
        is_wide_rectangle=False,
    )
  return lines


def compute_ridges_for_rectangles(
    final_placement: utils_tracker.CreasePatternTracker | None,
    y_ridge_at_border: bool = True,
) -> dict[str, list[tuple[tuple[float, float], tuple[float, float]]]]:
  """Computes the ridge creases for each rectangle in a final placement."""
  ridges = {}
  if not final_placement:
    return ridges

  for poly_id, placement in final_placement.packed_polygons.items():
    x, y = placement.offset
    width, height = placement.size
    rect = shaping_utils.Rectangle(
        name=poly_id,
        x_start=float(x),
        y_start=float(y),
        x_len=float(width),
        y_len=float(height),
    )
    ridges[poly_id] = get_ridge_lines(
        rect,
        grid_size=final_placement.grid_size,
        y_ridge_at_border=y_ridge_at_border,
    )

  return ridges


def compute_flap_shapes(
    final_placement: utils_tracker.CreasePatternTracker | None,
    y_ridge_at_border: bool = True,
) -> dict[str, stick_lib.FlapTipShape]:
  """Computes the flap tip shape for each packed polygon."""
  shapes = {}
  if not final_placement:
    return shapes

  for poly_id, placement in final_placement.packed_polygons.items():
    x, y = placement.offset
    width, height = placement.size
    rect = shaping_utils.Rectangle(
        name=poly_id,
        x_start=float(x),
        y_start=float(y),
        x_len=float(width),
        y_len=float(height),
    )
    if not rect.is_square:
      shapes[poly_id] = stick_lib.FlapTipShape.RECTANGULAR
    else:
      is_center_on_corner = rect.is_center_on_corner(final_placement.grid_size)
      center_on_border = rect.is_center_on_border(final_placement.grid_size)
      is_center_on_border = any(center_on_border)
      touch_left, touch_right, touch_top, touch_bottom = (
          rect.get_borders_touched(final_placement.grid_size)
      )
      touches_paper_corner = (
          (touch_left and touch_top)
          or (touch_left and touch_bottom)
          or (touch_right and touch_top)
          or (touch_right and touch_bottom)
      )
      has_y_ridge = (
          y_ridge_at_border
          and not is_center_on_corner
          and (not is_center_on_border or touches_paper_corner)
          and (touch_left or touch_right or touch_top or touch_bottom)
      )
      if has_y_ridge:
        shapes[poly_id] = stick_lib.FlapTipShape.RECTANGULAR
      else:
        shapes[poly_id] = stick_lib.FlapTipShape.TRIANGULAR

  return shapes


def assign_flap_shapes_to_unmerged_tree(
    unmerged_tree: stick_figure_lib.StickFigure,
    flap_shapes: dict[str, stick_lib.FlapTipShape],
) -> None:
  """Assigns flap tip shapes to extremal sticks in an unmerged tree."""
  _, merged_mapping = unmerged_tree.merge_linear_chains()
  original_to_merged = {}
  for merged_name, originals in merged_mapping.items():
    for orig in originals:
      original_to_merged[orig] = merged_name

  extremal_sticks = set()
  for joint in unmerged_tree.joints.values():
    if joint.degree == 1:
      extremal_sticks.add(joint.sticks[0].name)

  for stick in unmerged_tree.children:
    lookup_name = original_to_merged.get(stick.name, stick.name)
    if stick.name in extremal_sticks and lookup_name in flap_shapes:
      stick.flap_tip_shape = flap_shapes[lookup_name]
    else:
      stick.flap_tip_shape = stick_lib.FlapTipShape.NOT_APPLICABLE


def assign_flap_shapes_from_packing_output(
    unmerged_tree: stick_figure_lib.StickFigure,
    packing_output: Any,
) -> None:
  """Computes and assigns flap tip shapes from a packing output."""
  if not packing_output.flap_rectangles or not packing_output.details:
    return
  grid_size = int(packing_output.details['grid_size'])
  tracker = utils_tracker.CreasePatternTracker(grid_size)
  for rect in packing_output.flap_rectangles:
    tracker.packed_polygons[rect.name] = packing_types.PolygonPlacement(
        offset=(int(rect.x_start), int(rect.y_start)),
        size=(int(rect.x_len), int(rect.y_len)),
        center=packing_types.point.Point(x=0, y=0, require_on_paper=False),
    )
  y_ridge_at_border = (
      packing_output.config.y_ridge_at_border
      if packing_output.config is not None
      else True
  )
  flap_shapes = compute_flap_shapes(
      tracker, y_ridge_at_border=y_ridge_at_border
  )
  assign_flap_shapes_to_unmerged_tree(unmerged_tree, flap_shapes)
