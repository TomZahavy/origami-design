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

"""Utilities for drawing hinge and ridge creases in packing svg."""

import collections
import dataclasses
import enum
import itertools
import logging
import math

import lxml.etree as ET

from .. import rectangle as shaping_utils
from .. import utils_tree as utils
from ..crease_pattern import crease as crease_lib
from ..crease_pattern import crease_pattern as crease_pattern_lib
from ..crease_pattern import point as point_lib
from ..crease_pattern.parser import svg as svg_parser
from ..stick_figures import stick_figure as stick_figure_lib
from . import compute_hinges
from . import compute_ridges
from . import river as river_lib
from . import types
from . import utils_tracker

_BUCKET_MULTIPLIER = 100_000_000


@dataclasses.dataclass(frozen=True)
class _ParentEntry:
  x_lo: float
  x_hi: float
  y_lo: float
  y_hi: float
  segment_key: tuple[tuple[float, float], tuple[float, float]]


class PolygonIDSuffix(enum.Enum):
  COPY = types.COPY_SUFFIX


def _split_overlapping_creases(
    crease_to_split: crease_lib.Crease,
    other_creases: list[crease_lib.Crease],
) -> list[crease_lib.Crease]:
  """Splits crease by intersections and overlapping collinear creases.

  Args:
    crease_to_split: The crease to split.
    other_creases: The other creases to split by.

  Returns:
    A list of split creases.
  """
  split_points = [crease_to_split.p1, crease_to_split.p2]
  for c in other_creases:
    if c.isclose(crease_to_split):
      continue
    # Add intersection points
    v = crease_to_split.vertex_with_crease(c)
    if v is not None:
      if not any(v.isclose(p) for p in split_points):
        split_points.append(v)
    # Add endpoints of overlapping collinear creases
    if crease_to_split.is_collinear(c) and crease_to_split.is_overlapping(c):
      if crease_to_split.point_status(c.p1) == crease_lib.PointStatus.INTERNAL:
        if not any(c.p1.isclose(p) for p in split_points):
          split_points.append(c.p1)
      if crease_to_split.point_status(c.p2) == crease_lib.PointStatus.INTERNAL:
        if not any(c.p2.isclose(p) for p in split_points):
          split_points.append(c.p2)

  if crease_to_split.is_vertical:
    split_points.sort(key=lambda p: (p.y, p.x))
  else:
    split_points.sort(key=lambda p: (p.x, p.y))

  segments = []
  for p1, p2 in itertools.pairwise(split_points):
    segments.append(
        crease_lib.Crease(
            p1,
            p2,
            fold=crease_to_split.fold,
            fold_percent=crease_to_split.fold_percent,
        )
    )
  return segments


def _add_element_edges(
    lines: list[tuple[tuple[float, float], tuple[float, float]]],
    element_name: str,
    grid_size: int,
    clip_box: tuple[float, float, float, float],
    edge_to_elements: dict[
        tuple[tuple[float, float], tuple[float, float]], list[str]
    ],
) -> None:
  """Clips lines, filters border lines, and adds them to edge_to_elements map.

  Args:
    lines: A list of line segments, each represented as a tuple of (start, end)
      coordinates.
    element_name: The name of the element (polygon or river) the lines belong
      to.
    grid_size: The size of the grid.
    clip_box: The clipping box (xmin, ymin, xmax, ymax).
    edge_to_elements: A dictionary mapping canonical line segments to a list of
      element names.

  Returns:
    None.
  """
  for p1, p2 in lines:
    clipped_points = _clip_and_filter_line(p1, p2, clip_box)
    if not clipped_points:
      continue
    p1_clipped, p2_clipped = clipped_points
    if _filter_border_line(p1_clipped, p2_clipped, grid_size):
      continue

    canonical_line = tuple(sorted((p1_clipped, p2_clipped)))
    edge_to_elements[canonical_line].append(element_name)  # pyrefly: ignore[bad-index]
  return None


def extract_hinges_info(
    tracker: utils_tracker.CreasePatternTracker, grid_size: int
) -> list[types.HingeInfo]:
  """Extracts hinge information from packed polygons.

  Hinges are shared edges between packed polygons, clipped to grid boundaries
  and not on paper border. Intersecting hinges are split into smaller segments.
  The 'assigned' property of each HingeInfo object will be set to False by
  default and updated after the crease pattern is solved.

  Args:
    tracker: The CreasePatternTracker containing packed polygons.
    grid_size: The size of the grid.

  Returns:
    A list of HingeInfo objects.
  """
  edge_to_elements = collections.defaultdict(list)
  clip_box = (0, 0, grid_size, grid_size)

  for name, placement in tracker.packed_polygons.items():
    if name.startswith(types.AXIS_FILLER_PREFIX):
      continue
    _add_element_edges(
        lines=_get_rectangle_lines(placement),
        element_name=name,
        grid_size=grid_size,
        clip_box=clip_box,
        edge_to_elements=edge_to_elements,
    )

  for river_id, river in tracker.packed_rivers.items():
    if hasattr(river, 'rectangles') and not isinstance(
        river, (river_lib.River, river_lib.LShapedRiver, river_lib.HuggingRiver)
    ):
      # For reconstructed or ring rivers decomposed into multiple rectangles,
      # only add outer/inner bank boundaries (never internal rectangle seams).
      bank_lines = [
          ((float(p1[0]), float(p1[1])), (float(p2[0]), float(p2[1])))
          for p1, p2 in compute_hinges.get_river_border(
              river.rectangles, grid_size
          )
      ]
      _add_element_edges(
          lines=bank_lines,
          element_name=river_id,
          grid_size=grid_size,
          clip_box=clip_box,
          edge_to_elements=edge_to_elements,
      )
      continue
    if isinstance(river, river_lib.River):
      rects_to_process = [river.rectangle]
    elif isinstance(
        river,
        (
            river_lib.LShapedRiver,
            river_lib.HuggingRiver,
        ),
    ):
      rects_to_process = river.rectangles
    else:
      raise TypeError(f'Unknown river type: {type(river)}')

    for rect in rects_to_process:
      _add_element_edges(
          lines=_get_rectangle_lines(rect),
          element_name=river_id,
          grid_size=grid_size,
          clip_box=clip_box,
          edge_to_elements=edge_to_elements,
      )

  unsplit_creases = []
  crease_to_seg = {}
  for seg in edge_to_elements:
    p1 = point_lib.Point(x=seg[0][0] / grid_size, y=seg[0][1] / grid_size)
    p2 = point_lib.Point(x=seg[1][0] / grid_size, y=seg[1][1] / grid_size)
    c = crease_lib.Crease(p1, p2, fold=crease_lib.Fold.HINGE)
    unsplit_creases.append(c)
    crease_to_seg[id(c)] = seg

  split_creases = crease_pattern_lib.split_creases(
      unsplit_creases, unsplit_creases
  )

  unique_segments = {}
  for s in split_creases:
    unique_segments[crease_lib.CreaseWithExactMatch(s)] = s

  tol = point_lib.DEFAULT_TOLERANCE

  horizontal_parents = collections.defaultdict(list)
  vertical_parents = collections.defaultdict(list)
  for parent in unsplit_creases:
    p1x, p1y = parent.p1.x, parent.p1.y
    p2x, p2y = parent.p2.x, parent.p2.y
    segment_key = crease_to_seg[id(parent)]
    entry = _ParentEntry(
        x_lo=min(p1x, p2x),
        x_hi=max(p1x, p2x),
        y_lo=min(p1y, p2y),
        y_hi=max(p1y, p2y),
        segment_key=segment_key,
    )
    if parent.is_vertical:
      vertical_parents[round(p1x * _BUCKET_MULTIPLIER)].append(entry)
    else:
      horizontal_parents[round(p1y * _BUCKET_MULTIPLIER)].append(entry)

  hinges = []
  for segment in unique_segments.values():
    adjacent_elements = set()
    seg_p1x, seg_p1y = segment.p1.x, segment.p1.y
    seg_p2x, seg_p2y = segment.p2.x, segment.p2.y
    if segment.is_vertical:
      candidates = vertical_parents.get(round(seg_p1x * _BUCKET_MULTIPLIER), [])
    else:
      candidates = horizontal_parents.get(
          round(seg_p1y * _BUCKET_MULTIPLIER), []
      )
    for parent in candidates:
      if (
          parent.x_lo - tol <= seg_p1x <= parent.x_hi + tol
          and parent.y_lo - tol <= seg_p1y <= parent.y_hi + tol
          and parent.x_lo - tol <= seg_p2x <= parent.x_hi + tol
          and parent.y_lo - tol <= seg_p2y <= parent.y_hi + tol
      ):
        for name in edge_to_elements[parent.segment_key]:
          adjacent_elements.add(name)

    sorted_elements = sorted(adjacent_elements)
    assert sorted_elements

    hinges.append(
        types.HingeInfo(
            coordinate=segment,
            assigned=False,
            flap_names=tuple(sorted_elements),
        )
    )
  return hinges


def _get_rectangle_lines(
    rect_like_obj,
) -> list[tuple[tuple[float, float], tuple[float, float]]]:
  """Returns the four line segments forming the rectangle of an object.

  Args:
    rect_like_obj: An object with either offset and size attrs
      (PolygonPlacement) or x_start, y_start, x_len, y_len attrs
      (shaping_utils.Rectangle).

  Returns:
    A list of four line segments, each represented as a tuple of (start, end)
    coordinates.
  """
  if hasattr(rect_like_obj, 'offset'):
    x, y = rect_like_obj.offset
    w, h = rect_like_obj.size
  else:
    x, y = rect_like_obj.x_start, rect_like_obj.y_start
    w, h = rect_like_obj.x_len, rect_like_obj.y_len
  return [
      ((x, y), (x + w, y)),  # Top
      ((x + w, y), (x + w, y + h)),  # Right
      ((x + w, y + h), (x, y + h)),  # Bottom
      ((x, y + h), (x, y)),  # Left
  ]


def _filter_border_line(p1, p2, grid_size):
  """Returns true if the line segment should be filtered out.

  This function checks if the line segment lies on the grid's border. It does
  so by converting the coordinates to a unit square using the grid size,
  creating a temporary Crease object, and checking if it is overlapping the
  border.

  Args:
    p1: A tuple of (x, y) coordinates.
    p2: A tuple of (x, y) coordinates.
    grid_size: The size of the grid.

  Returns:
    True if the line segment should be filtered out, False otherwise.
  """
  # Normalize to unit square for Crease/Point
  p1_unit = point_lib.Point(x=p1[0] / grid_size, y=p1[1] / grid_size)
  p2_unit = point_lib.Point(x=p2[0] / grid_size, y=p2[1] / grid_size)
  # Hinge here has no meaning, we just need a crease type.
  temp_crease = crease_lib.Crease(p1_unit, p2_unit, fold=crease_lib.Fold.HINGE)
  return temp_crease.is_overlapping_border


def _clip_and_filter_line(
    p1: tuple[float, float],
    p2: tuple[float, float],
    clip_box: tuple[float, float, float, float],
) -> tuple[tuple[float, float], tuple[float, float]] | None:
  """Clips line to clip_box and filters if too short.

  Args:
    p1: Start point of the line segment.
    p2: End point of the line segment.
    clip_box: The clipping box (xmin, ymin, xmax, ymax).

  Returns:
    A tuple containing the clipped coordinates (p1, p2) of the line segment if
    it is valid, or None if it should be filtered out.
  """
  clipped = shaping_utils.restrict_crease_to_rectangle(
      shaping_utils.Rectangle.from_clip_box(
          name='clip_box',
          clip_box=clip_box,
      ),
      crease_lib.Crease(
          point_lib.Point(x=p1[0], y=p1[1], require_on_paper=False),
          point_lib.Point(x=p2[0], y=p2[1], require_on_paper=False),
          fold=crease_lib.Fold.HINGE,
      ),
  )
  if not clipped:
    return None
  p1_clipped = (clipped.p1_init.x, clipped.p1_init.y)
  p2_clipped = (clipped.p2_init.x, clipped.p2_init.y)
  if math.dist(p1_clipped, p2_clipped) < point_lib.DEFAULT_TOLERANCE:
    return None
  return p1_clipped, p2_clipped


def _add_crease_if_valid(
    p1: tuple[float, float],
    p2: tuple[float, float],
    fold: crease_lib.Fold,
    deduplicate: bool,
    grid_size: int,
    clip_box: tuple[float, float, float, float],
    creases: list[crease_lib.Crease],
    drawn_lines: set[tuple[tuple[float, float], tuple[float, float]]],
):
  """Clips, filters, and adds a crease if valid.

  Helper function to clip a line segment to the grid boundaries, filter it if
  it's too short or lies on the border, and add it as a crease if it's
  valid. Optionally deduplicates lines based on canonical representation.

  Args:
    p1: Start point of the line segment.
    p2: End point of the line segment.
    fold: The type of fold (e.g., HINGE, MOUNTAIN).
    deduplicate: If True, check for duplicates in drawn_lines before adding.
    grid_size: The size of the grid.
    clip_box: The clipping box (xmin, ymin, xmax, ymax).
    creases: The list of creases to append to if the line is valid.
    drawn_lines: The set of drawn lines for deduplication.
  """
  clipped_points = _clip_and_filter_line(p1, p2, clip_box)
  if not clipped_points:
    return
  p1_clipped, p2_clipped = clipped_points
  if _filter_border_line(p1_clipped, p2_clipped, grid_size):
    return
  if deduplicate:
    canonical_line = tuple(sorted((p1_clipped, p2_clipped)))
    if canonical_line in drawn_lines:
      return
    drawn_lines.add(canonical_line)  # pyrefly: ignore[bad-argument-type]
  creases.append(
      crease_lib.Crease(
          point_lib.Point(
              x=p1_clipped[0] / grid_size, y=p1_clipped[1] / grid_size
          ),
          point_lib.Point(
              x=p2_clipped[0] / grid_size, y=p2_clipped[1] / grid_size
          ),
          fold=fold,
      )
  )


def _get_adjusted_flap_rectangle(
    name: str,
    polygon: types.PolygonPlacement,
    grid_size: int,
    y_ridge_at_border: bool = True,
) -> shaping_utils.Rectangle:
  """Gets an adjusted flap rectangle from a polygon placement.

  If the polygon is a square touching the border, it may be extended
  to be treated as wide or tall.

  Args:
    name: The name of the polygon.
    polygon: The polygon placement.
    grid_size: The grid size.
    y_ridge_at_border: If True, apply Y-ridge on border contact for squares.

  Returns:
    A shaping_utils.Rectangle representing the flap.
  """
  x_start = float(polygon.offset[0])
  y_start = float(polygon.offset[1])
  x_len = float(polygon.size[0])
  y_len = float(polygon.size[1])

  rect_for_check = shaping_utils.Rectangle(
      name=name, x_start=x_start, y_start=y_start, x_len=x_len, y_len=y_len
  )
  touch_left, touch_right, touch_top, touch_bottom = (
      rect_for_check.get_borders_touched(grid_size)
  )
  is_touching = touch_left or touch_right or touch_top or touch_bottom

  if (
      y_ridge_at_border
      and rect_for_check.is_square
      and is_touching
      and not rect_for_check.is_center_on_corner(grid_size)
  ):
    side_len = x_len
    treat_as_wide = rect_for_check.treat_as_wide_on_border(grid_size)
    if treat_as_wide:
      x_len += side_len
      if touch_left:
        x_start -= side_len
    else:  # treat as tall
      y_len += side_len
      if touch_top:
        y_start -= side_len

  rect = shaping_utils.Rectangle(
      name=name,
      x_start=x_start,
      y_start=y_start,
      x_len=x_len,
      y_len=y_len,
  )
  centers = rect.get_circle_centers(grid_size=grid_size)
  rect_with_centers = dataclasses.replace(rect, circle_centers=centers)
  return rect_with_centers


def _flap_length_from_polygon(polygon: types.PolygonPlacement) -> int:
  """Returns integer length of the flap corresponding to the given polygon."""
  return min(polygon.size) // 2


def _build_merged_packing_pattern(
    grid_size: int,
    final_placement: utils_tracker.CreasePatternTracker,
    y_ridge_at_border: bool = True,
    recovery: bool = False,
) -> tuple[crease_pattern_lib.CreasePattern, list[shaping_utils.Rectangle]]:
  """Builds the light-mode merged interior CreasePattern and flap rectangles."""
  creases = []
  clip_box = (0, 0, grid_size, grid_size)
  drawn_lines = set()

  # 1. Packed Polygon Outlines (Green) - Clipped, Deduplicated, and Filtered
  if final_placement:
    for placement in final_placement.packed_polygons.values():
      for p1, p2 in _get_rectangle_lines(placement):
        _add_crease_if_valid(
            p1,
            p2,
            crease_lib.Fold.HINGE,
            deduplicate=True,
            grid_size=grid_size,
            clip_box=clip_box,
            creases=creases,
            drawn_lines=drawn_lines,
        )
    river_hinges = compute_hinges.get_river_hinges(final_placement, grid_size)
    for p1, p2 in river_hinges:
      _add_crease_if_valid(
          p1,
          p2,
          crease_lib.Fold.HINGE,
          deduplicate=True,
          grid_size=grid_size,
          clip_box=clip_box,
          creases=creases,
          drawn_lines=drawn_lines,
      )

  # 2. Packed Polygon Ridges (Red) - Clipped and Filtered
  ridges = compute_ridges.compute_ridges_for_rectangles(
      final_placement, y_ridge_at_border=y_ridge_at_border
  )
  if ridges:
    for ridge_lines in ridges.values():
      for p1_orig, p2_orig in ridge_lines:
        _add_crease_if_valid(
            p1_orig,
            p2_orig,
            crease_lib.Fold.MOUNTAIN,
            deduplicate=True,
            grid_size=grid_size,
            clip_box=clip_box,
            creases=creases,
            drawn_lines=drawn_lines,
        )
  # update rectangles with ridge data
  ridge_creases = {
      name: [
          crease_lib.Crease(
              point_lib.Point(x=p1[0], y=p1[1], require_on_paper=False),
              point_lib.Point(x=p2[0], y=p2[1], require_on_paper=False),
              fold=crease_lib.Fold.MOUNTAIN,
          )
          for p1, p2 in points
      ]
      for name, points in ridges.items()
  }
  try:
    rectangles = [
        shaping_utils.Rectangle.from_ridges_and_radius(
            name,
            ridges,
            _flap_length_from_polygon(final_placement.packed_polygons[name])
            * math.sqrt(2),
        )
        for name, ridges in ridge_creases.items()
    ]
  # fallback on previous conversion method
  # if reading rectangle from ridge fails
  except ValueError:
    rectangles = [
        _get_adjusted_flap_rectangle(
            name,
            polygon,
            grid_size,
            y_ridge_at_border=y_ridge_at_border,
        )
        for name, polygon in final_placement.packed_polygons.items()
    ]

  # 3. Packed River Ridges (Red) - Clipped and Filtered
  if final_placement:
    for river in final_placement.packed_rivers.values():
      river_ridges = compute_ridges.get_river_ridge_lines(
          river, recovery=recovery, grid_size=grid_size
      )
      for p1_orig, p2_orig in river_ridges:
        _add_crease_if_valid(
            p1_orig,
            p2_orig,
            crease_lib.Fold.MOUNTAIN,
            deduplicate=True,
            grid_size=grid_size,
            clip_box=clip_box,
            creases=creases,
            drawn_lines=drawn_lines,
        )

  # Split creases by intersections and overlaps, then merge
  all_segments = []
  for c in creases:
    all_segments.extend(_split_overlapping_creases(c, creases))

  unique_segments = utils.deduplicate(all_segments)

  merged_segments = crease_lib.merge_creases(
      unique_segments, only_trivial=False
  )

  pattern = crease_pattern_lib.CreasePattern(
      merged_segments, grid_size=grid_size, light_mode=True
  )
  return pattern, rectangles


def build_packing_crease_pattern(
    grid_size: int,
    final_placement: utils_tracker.CreasePatternTracker,
    y_ridge_at_border: bool = True,
    recovery: bool = False,
) -> tuple[crease_pattern_lib.CreasePattern, list[shaping_utils.Rectangle]]:
  """Builds the packed CreasePattern and flap rectangles directly without SVG round-tripping."""
  pattern, rectangles = _build_merged_packing_pattern(
      grid_size,
      final_placement,
      y_ridge_at_border=y_ridge_at_border,
      recovery=recovery,
  )
  # Round scaled grid coordinates to 1 decimal place (matching legacy
  # svg_parser.to_element_tree(..., ndigits=1) + parse_svg quantization) so
  # 45-degree ridge/hinge intersection coordinates have identical float
  # representations without serializing to XML.
  interior_creases = [
      crease_lib.Crease(
          point_lib.Point(
              x=round(c.p1.x * grid_size, 1) / grid_size,
              y=round(c.p1.y * grid_size, 1) / grid_size,
          ),
          point_lib.Point(
              x=round(c.p2.x * grid_size, 1) / grid_size,
              y=round(c.p2.y * grid_size, 1) / grid_size,
          ),
          fold=c.fold,
          fold_percent=c.fold_percent,
          fold_step=c.fold_step,
          elevation=c.elevation,
      )
      for c in pattern.creases
      if c.fold != crease_lib.Fold.BORDER
  ]
  if not interior_creases:
    raise svg_parser.SVGParseError('No interior creases in packing pattern.')
  p1 = point_lib.Point(x=0.0, y=0.0)
  p2 = point_lib.Point(x=0.0, y=1.0)
  p3 = point_lib.Point(x=1.0, y=1.0)
  p4 = point_lib.Point(x=1.0, y=0.0)
  border_creases = [
      crease_lib.Crease(p1, p2, fold=crease_lib.Fold.BORDER),
      crease_lib.Crease(p2, p3, fold=crease_lib.Fold.BORDER),
      crease_lib.Crease(p3, p4, fold=crease_lib.Fold.BORDER),
      crease_lib.Crease(p4, p1, fold=crease_lib.Fold.BORDER),
  ]
  cp = crease_pattern_lib.CreasePattern(
      [*interior_creases, *border_creases],
      grid_size=grid_size,
  )
  return cp, rectangles


def convert_packing_to_svg(
    grid_size: int,
    final_placement: utils_tracker.CreasePatternTracker,
    y_ridge_at_border: bool = True,
    recovery: bool = False,
) -> tuple[str, list[shaping_utils.Rectangle]]:
  """Transforms the packing results into an SVG string."""
  pattern, rectangles = _build_merged_packing_pattern(
      grid_size,
      final_placement,
      y_ridge_at_border=y_ridge_at_border,
      recovery=recovery,
  )

  root = svg_parser.to_element_tree(
      pattern, scale=1, ndigits=1, grid=grid_size, replace_border=True
  )

  svg_string = ET.tostring(
      root, encoding='unicode', method='xml', pretty_print=True
  )
  return svg_string, rectangles


def add_highlight_overlays(
    svg_string: str,
    grid_size: int,
    tracker: utils_tracker.CreasePatternTracker,
) -> str:
  """Adds purple overlays on sacrificial flaps in an existing packing SVG.

  Args:
      svg_string: The SVG string to overlay on.
      grid_size: The grid size of the packing.
      tracker: The CreasePatternTracker with polygon placements.

  Returns:
      A new SVG string with purple rectangles on sacrificial flaps.
  """
  root = ET.fromstring(svg_string.encode('utf-8'))

  sacrificial_suffixes = (
      types.RIVER_SF1_SUFFIX,
      types.RIVER_SF2_SUFFIX,
      '__sacrificial_vertical',
      '__sacrificial_horizontal',
      '__corner',
  )

  for name, placement in tracker.packed_polygons.items():
    if any(suffix in name for suffix in sacrificial_suffixes):
      ox, oy = placement.offset
      w, h = placement.size
      rx = max(0, ox)
      ry = max(0, oy)
      rw = min(ox + w, grid_size) - rx
      rh = min(oy + h, grid_size) - ry
      if rw > 0 and rh > 0:
        ET.SubElement(
            root,
            'rect',
            x=str(rx),
            y=str(ry),
            width=str(rw),
            height=str(rh),
            fill='purple',
            stroke='purple',
            opacity='0.3',
        )

  return ET.tostring(root, encoding='unicode', method='xml', pretty_print=True)


def get_mirrored_polygon_placement(
    placement: types.PolygonPlacement, grid_size: int
) -> types.PolygonPlacement:
  """Returns a mirrored placement of the given placement.

  Args:
    placement: The placement to mirror.
    grid_size: The grid size to use for mirroring.

  Returns:
    A new PolygonPlacement object that is mirrored across the y-axis.
  """
  x, y = placement.offset
  w, h = placement.size
  mirrored_x = grid_size - w - x
  mirrored_y = y
  mirrored_coords = None
  if placement.coords is not None:
    mirrored_coords = [(1.0 - x, y) for x, y in placement.coords]
  return types.PolygonPlacement(
      offset=(mirrored_x, mirrored_y),
      size=(w, h),
      center=point_lib.Point(x=1.0 - placement.center.x, y=placement.center.y),
      coords=mirrored_coords,
      river_sf_info=placement.river_sf_info,
  )


def mirror_symmetric_placements(
    tracker: utils_tracker.CreasePatternTracker,
    grid_size: int,
    stick_figure: stick_figure_lib.StickFigure | None = None,
):
  """Mirror the placements on one side of a symmetric packing.

  This iterates through all packed polygons on one side of a symmetric packing
  and adds their mirrored counterparts to fill the other side. Polygons
  whose centers lie on the symmetry axis (grid_size / 2) are skipped.

  Args:
      tracker: The CreasePatternTracker containing one side of the packing.
      grid_size: The grid size to use for mirroring.
      stick_figure: If provided, use stick names to name mirrored polygons.
  """
  if not stick_figure:
    return
  for stick_name, placement in list(tracker.packed_polygons.items()):
    if stick_name.endswith(PolygonIDSuffix.COPY.value):
      continue
    # Check if center x-coordinate is on the symmetry axis
    if math.isclose(placement.center.x * grid_size, grid_size / 2.0):
      continue

    matched_suffix = None
    river_stick = None
    sym_river_name = None
    try:
      stick = stick_figure[stick_name]
      if stick.is_on_symmetry_axis:
        continue
      symmetric_stick_name = stick.symmetric_stick_name
      if not symmetric_stick_name or symmetric_stick_name == stick_name:
        continue
    except KeyError as e:
      matched_suffix = next(
          (
              suffix
              for suffix in (types.RIVER_SF1_SUFFIX, types.RIVER_SF2_SUFFIX)
              if stick_name.endswith(suffix)
          ),
          None,
      )
      if placement.river_sf_info is not None and matched_suffix is not None:
        river_stick = stick_figure[placement.river_sf_info.river_name]
        sym_river_name = river_stick.symmetric_stick_name
        if sym_river_name is None:
          sym_river_name = placement.river_sf_info.river_name
          symmetric_stick_name = (
              placement.river_sf_info.river_name
              + matched_suffix
              + PolygonIDSuffix.COPY.value
          )
        else:
          symmetric_stick_name = sym_river_name + matched_suffix
      else:
        raise ValueError(
            f'Stick name {stick_name} not found in stick figure, cannot mirror.'
        ) from e

    # If mirrored polygon already exists (e.g. from paired placement) or
    # was added by mirroring another polygon, skip.
    if symmetric_stick_name in tracker.packed_polygons:
      continue

    logging.info('Mirroring polygon %s to %s', stick_name, symmetric_stick_name)
    try:
      mirrored_placement = get_mirrored_polygon_placement(placement, grid_size)
      if mirrored_placement.river_sf_info and matched_suffix is not None:
        if sym_river_name in stick_figure and river_stick is not None:  # pyrefly: ignore[unsupported-operation]
          assert placement.river_sf_info is not None
          # Heuristically identify parent joint
          sym_river_stick = stick_figure[sym_river_name]  # pyrefly: ignore[bad-index]
          if placement.river_sf_info.parent_joint == river_stick.start:
            sym_parent_joint = sym_river_stick.start
          else:
            sym_parent_joint = sym_river_stick.end

          # Invert vertical river side
          sym_river_side = placement.river_sf_info.river_side
          if sym_river_side == 'left':
            sym_river_side = 'right'
          elif sym_river_side == 'right':
            sym_river_side = 'left'

          mirrored_sf_info = types.RiverSfInfo(
              river_name=sym_river_name,  # pyrefly: ignore[bad-argument-type]
              river_side=sym_river_side,
              parent_joint=sym_parent_joint,
          )
          mirrored_placement = dataclasses.replace(
              mirrored_placement, river_sf_info=mirrored_sf_info
          )
      tracker.add_polygon(symmetric_stick_name, mirrored_placement)
    except ValueError as e:
      logging.warning(
          'Failed to create mirrored placement for polygon %s: %s',
          stick_name,
          e,
      )
      continue

  for stick_name, river in list(tracker.packed_rivers.items()):
    try:
      stick = stick_figure[stick_name]
      if stick.is_on_symmetry_axis:
        continue
      symmetric_stick_name = stick.symmetric_stick_name
      if not symmetric_stick_name or symmetric_stick_name == stick_name:
        continue
    except KeyError as e:
      raise ValueError(
          f'Stick name {stick_name} not found in stick figure, cannot mirror'
          ' river.'
      ) from e

    if symmetric_stick_name in tracker.packed_rivers:
      continue

    logging.info('Mirroring river %s to %s', stick_name, symmetric_stick_name)
    try:
      mirrored_river = river.mirror(grid_size)
      tracker.add_river(symmetric_stick_name, mirrored_river)
    except ValueError as e:
      logging.warning(
          'Failed to create mirrored river for river %s: %s', stick_name, e
      )
      continue
