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

"""Geometric folding heuristics for 3D shaping."""

import collections
from collections.abc import Sequence
import dataclasses
import logging
import math
import typing
from typing import TypedDict, cast

import matplotlib.pyplot as plt
import numpy as np

from ..crease_pattern import crease as crease_utils
from ..crease_pattern import crease_pattern as cp_utils
from ..crease_pattern import point as point_utils
from ..packing import packing_output as packing_output_utils
from ..packing import types as packing_types
from ..solving import hinges as hinge_utils
from ..stick_figures import angle_utils
from ..stick_figures import stick_figure as sf_utils
from . import geometric_fold_3d_heuristics_utils
from . import geometric_simple_fold
from . import geometric_utils
from . import heuristics
from . import heuristics_3d
from . import heuristics_utils
from . import shaping_elements
from . import shaping_utils
from . import types as shaping_types

_NINETY_DEG_SLOPE_TOLERANCE = 0.1


class ElementShapingResult(TypedDict):
  """Result of shaping a single element."""

  simple_fold_info: heuristics_3d.SimpleFoldInfo
  shaping_element: shaping_elements.ShapingElement
  shaping_creases: Sequence[crease_utils.Crease]


class Heuristics3DShapingResult(TypedDict):
  """Result of heuristics 3D shaping."""

  shaping_creases: Sequence[crease_utils.Crease]
  # Mapping from element name to a list of element shaping results.
  detailed_shaping_info: dict[str, list[ElementShapingResult]]


@dataclasses.dataclass(frozen=True)
class InscribeHParams:
  """Parameters for inscribing a simple fold plus some other hparams.

  Attributes:
    avoid_hinges: Whether to attempt to avoid hinges by inscribing deeper.
    inscribe_depth: The depth (in grid units) to inscribe the simple fold
      unrelated to avoid_hinges.
    hinge_inscribe_depth: The depth to additionally inscribe when avoiding
      hinges.
    ninety_deg_slope_tolerance: The tolerance for ninety degree angles. Angles
      close (under this tolerance) to ninety degrees are treated as ninety
      degrees.
    max_slope_thresh: The maximum slope for a simple fold. Anything above this
      threshold is removed.
    clip_slope_thresh: The threshold to clip the slope of a simple fold to if
      it's not above max_slope_thresh.
  """

  avoid_hinges: bool = False
  inscribe_depth: float = 0.0
  hinge_inscribe_depth: float = (
      geometric_fold_3d_heuristics_utils.INSCRIBE_FRACTION
  )
  ninety_deg_slope_tolerance: float = _NINETY_DEG_SLOPE_TOLERANCE
  max_slope_thresh: float = heuristics_3d.MAX_SLOPE
  clip_slope_thresh: float = 5.0


@dataclasses.dataclass(frozen=True)
class GeometricFolding3DHParams:
  """Parameters for geometric folding 3D shaping.

  Attributes:
    shape_subset: The subset of elements to shape.
    default_inscribe_hparams: The default inscribe hparams for all elements.
    check_ff_violations: Whether to check for flap folding violations.
    strategy: The 3D folding strategy to use.
    per_flap_strategy: Per-flap overrides for the folding strategy.
    per_flap_hinge_inscribe_depth: Per-flap overrides for hinge inscribe depth.
  """

  shape_subset: Sequence[str] | None = None
  default_inscribe_hparams: InscribeHParams = InscribeHParams()
  check_ff_violations: bool = False
  strategy: heuristics_3d.FoldStrategy3D = heuristics_3d.FoldStrategy3D.DEFAULT
  per_flap_strategy: dict[str, heuristics_3d.FoldStrategy3D] = (
      dataclasses.field(default_factory=dict)
  )
  per_flap_hinge_inscribe_depth: dict[str, float] = dataclasses.field(
      default_factory=dict
  )


def _get_rotation_axis_slope(
    simple_fold_direction: np.ndarray,
) -> float | None:
  """Returns the slope of the simple fold direction."""
  if math.isclose(simple_fold_direction[0], 0.0):
    return None
  return simple_fold_direction[1] / simple_fold_direction[0]


def _clip_to_slope_one(simple_fold_direction: np.ndarray) -> np.ndarray:
  """Returns a vector with slope 1 or -1.

  The sign of the returned vector matches the sign of the input vector.

  Args:
      simple_fold_direction: The simple fold direction to clip.

  Returns:
      A vector with slope 1 or -1.
  """
  return np.array([
      float(np.sign(simple_fold_direction[0])),
      float(np.sign(simple_fold_direction[1])),
      0.0,
  ])


def _clip_slope_to_max(
    simple_fold_direction: np.ndarray, max_slope: float
) -> np.ndarray:
  """Returns a vector with slope at most max_slope."""
  # Normalize so that first component is 1.
  simple_fold_direction = simple_fold_direction / simple_fold_direction[0]
  return np.array([
      1.0,
      np.clip(simple_fold_direction[1], -max_slope, max_slope),
      0.0,
  ])


def _get_opposite_hinge_points_no_elevation(
    boundary: shaping_elements.ShapingBoundary,
    grid_size: int,
) -> tuple[point_utils.Point, point_utils.Point]:
  """Returns two points on the boundary that are on paper."""
  cur_p, edge_index = boundary.creases[0].p1_init, 0
  assert shaping_utils.check_point_on_grid(
      cur_p, grid_size
  ), f'Point {cur_p} is not on the grid with size {grid_size}.'
  for _ in range(boundary.num_walk_steps_upper_bound(grid_size)):
    next_p, edge_index = boundary.walk(cur_p, edge_index, grid_size)
    assert shaping_utils.check_point_on_grid(
        next_p, grid_size
    ), f'Point {next_p} is not on the grid with size {grid_size}.'

    if cur_p.on_paper and next_p.on_paper:
      return cur_p, next_p
    else:
      cur_p = next_p

  raise ValueError(
      'No opposite hinge points found on boundary: {boundary} with grid size:'
      f' {grid_size}.'
  )


def get_opposite_hinge_points(
    boundary: shaping_elements.ShapingBoundary,
    grid_size: int,
    elevation_diff: int,
    creases: list[crease_utils.Crease],
) -> tuple[point_utils.Point, point_utils.Point]:
  """Returns two points on the boundary with opposite elevations."""
  if elevation_diff <= 0:
    raise ValueError('Elevation difference must be positive.')
  if elevation_diff == 1:
    # Use basic method that ignores elevation
    return _get_opposite_hinge_points_no_elevation(boundary, grid_size)

  def boundary_iter():
    """Walks around the boundary."""
    cur_p, edge_index = boundary.creases[0].p1_init, 0
    cur_elevation = geometric_fold_3d_heuristics_utils.check_point_elevation(
        cur_p, creases
    )
    for _ in range(boundary.num_walk_steps_upper_bound(grid_size)):
      yield cur_p, cur_elevation
      cur_p, edge_index, cur_elevation = (
          geometric_fold_3d_heuristics_utils.get_next_point_edge_index_and_elevation(
              cur_p, edge_index, creases, boundary, grid_size
          )
      )

  window = collections.deque()
  for p2, p2_el in boundary_iter():
    window.append((p2, p2_el))
    if len(window) <= elevation_diff:
      continue

    p1, p1_el = window.popleft()
    if p1_el is None or p2_el is None:
      continue
    if not p1.on_paper or not p2.on_paper:
      continue
    if abs(p1_el - p2_el) == elevation_diff:
      return p1, p2

  raise ValueError(f'No opposite hinge points found on boundary: {boundary}')


def _get_cut_line_from_anchor_and_direction(
    anchor: point_utils.Point,
    simple_fold_direction: np.ndarray,
    graph_data: geometric_simple_fold.GraphData,
    folded_verts: list[tuple[float, float] | None],
) -> tuple[tuple[float, float], tuple[float, float]]:
  """Returns the cut line from an anchor point and fold direction.

  The cut line starting point is determined by mapping the anchor point
  on the unfolded crease pattern to a point on the folded crease pattern.
  The cut line ending point is determined by adding the simple fold direction
  vector to the starting point.

  Args:
      anchor: The anchor point on the unfolded crease pattern lying on the
        boundary of the target shaping element.
      simple_fold_direction: A vector indicating the direction of the fold.
      graph_data: The graph data for the crease pattern.
      folded_verts: The folded vertices of the crease pattern.

  Returns:
      A tuple containing the start and end points of the cut line in folded
      space.
  """
  assert all(v is not None for v in folded_verts), folded_verts
  cut_line_start = geometric_utils.get_folded_pos(
      point=anchor,
      unfolded_coords=graph_data['vertices_coords'],
      folded_coords=folded_verts,  # pyrefly: ignore[bad-argument-type]
      edge_vertices=graph_data['edge_vertices'],
      face_vertices=graph_data['face_vertices'],
  )
  assert (
      cut_line_start is not None
  ), f'Cut line start is None for anchor: {anchor}.'
  cut_line_end = (
      cut_line_start[0] + simple_fold_direction[0],
      cut_line_start[1] + simple_fold_direction[1],
  )
  return cut_line_start, cut_line_end


def _get_root_element_orientation(
    root_element: shaping_elements.ShapingElement,
    stick_figure: sf_utils.StickFigure,
    graph_data: geometric_simple_fold.GraphData,
    folded_verts: list[tuple[float, float] | None],
) -> np.ndarray:
  """Returns a 3d vector from the root element's start to end joint.

  This vector points from the root element's start joint to its end joint in 3D.
  It is computed by finding the direction of the boundary depth vector
  corresponding to the element's start joint.

  Args:
      root_element: The root element of the shaping element tree.
      stick_figure: The stick figure.
      graph_data: The graph data for the crease pattern.
      folded_verts: The folded vertices of the crease pattern.

  Returns:
      A unit vector in 3d pointing from a point on the root start joint with
      elevation 0 to a point on the root end joint with elevation 0.
  """
  start, end = shaping_elements.get_unfolded_root_vector(
      root_element, stick_figure
  )

  # Get folded positions of start and end points.
  start_folded = geometric_utils.get_folded_pos(
      point=start,
      unfolded_coords=graph_data['vertices_coords'],
      folded_coords=folded_verts,  # pyrefly: ignore[bad-argument-type]
      edge_vertices=graph_data['edge_vertices'],
      face_vertices=graph_data['face_vertices'],
  )
  end_folded = geometric_utils.get_folded_pos(
      point=end,
      unfolded_coords=graph_data['vertices_coords'],
      folded_coords=folded_verts,  # pyrefly: ignore[bad-argument-type]
      edge_vertices=graph_data['edge_vertices'],
      face_vertices=graph_data['face_vertices'],
  )

  return np.array([
      end_folded[0] - start_folded[0],
      end_folded[1] - start_folded[1],
      0.0,
  ])


def _rotate_simple_fold_direction_by_model_orientation(
    simple_fold_direction: np.ndarray,
    root_element: shaping_elements.ShapingElement,
    stick_figure: sf_utils.StickFigure,
    graph_data: geometric_simple_fold.GraphData,
    folded_verts: list[tuple[float, float] | None],
) -> np.ndarray:
  """Rotates the simple fold direction to match the fold orientation."""
  root_element_orientation = _get_root_element_orientation(
      root_element, stick_figure, graph_data, folded_verts
  )
  logging.info('root_element_orientation: %s', root_element_orientation)
  # Rotate root_element_orientation to align it with positive y-axis.
  rotation_matrix = angle_utils.get_rotation_matrix_to_align(
      vec_start=root_element_orientation, vec_target=np.array([0, 1, 0])
  )
  # Apply the inverse rotation to the simple fold direction.
  new_simple_fold_direction = rotation_matrix @ simple_fold_direction
  logging.info('new_simple_fold_direction: %s', new_simple_fold_direction)
  return new_simple_fold_direction


def _get_shaping_creases(
    base_cp: cp_utils.CreasePattern,
    anchor: point_utils.Point,
    simple_fold_direction: np.ndarray,
    fold_assignment: crease_utils.Fold,
    limiting_polygon: (
        shaping_elements.ShapingFlap | shaping_elements.ShapingRiver
    ),
    graph_data: geometric_simple_fold.GraphData,
    folded_verts: list[tuple[float, float] | None],
    rotation_angle: float,
    visualize: bool = False,
    extra_limiting_rectangles: Sequence[shaping_utils.Rectangle] = (),
) -> Sequence[crease_utils.Crease]:
  """Returns creases from a geometric simple fold.

  The creases are generated for a given anchor point and fold direction.

  Args:
      base_cp: The base crease pattern.
      anchor: The anchor point for the simple fold.
      simple_fold_direction: The simple fold direction for the simple fold.
      fold_assignment: The fold assignment for the simple fold.
      limiting_polygon: The limiting polygon for the simple fold.
      graph_data: The graph data for the base crease pattern.
      folded_verts: The folded vertices for the base crease pattern.
      rotation_angle: The rotation angle for the simple fold.
      visualize: Whether to visualize the cut line on the folded crease pattern.
      extra_limiting_rectangles: Other rectangles that the creases can propagate
        to.

  Returns:
      The shaping creases for the element.
  """
  logging.info('anchor: %s', anchor)
  logging.info('simple_fold_direction: %s', simple_fold_direction)

  cut_line_start, cut_line_end = _get_cut_line_from_anchor_and_direction(
      anchor=anchor,
      simple_fold_direction=simple_fold_direction,
      graph_data=graph_data,
      folded_verts=folded_verts,
  )

  if (
      geometric_fold_3d_heuristics_utils.tuple_dist(
          cut_line_start, cut_line_end
      )
      < crease_utils.DEFAULT_TOLERANCE
  ):
    logging.warning(
        'Cut line start and end points are too close for element: %s. '
        'Cut line start: %s, cut line end: %s. '
        'Skipping.',
        limiting_polygon.name,
        cut_line_start,
        cut_line_end,
    )
    return []

  if visualize:
    fig = geometric_fold_3d_heuristics_utils.visualize_cut_line_on_folded_cp(
        base_cp,
        cut_line_start,
        cut_line_end,
        limiting_polygon,
    )
    plt.close(fig)

  if not extra_limiting_rectangles:
    limiting_rectangles = limiting_polygon
  else:
    if isinstance(limiting_polygon, shaping_elements.ShapingFlap):
      limiting_rectangles = [limiting_polygon.to_legacy_rectangle()]
    else:
      limiting_rectangles = list(limiting_polygon.covering_legacy_rectangles)
    limiting_rectangles.extend(extra_limiting_rectangles)

  shaping_creases = geometric_simple_fold.get_geometric_fold_creases(
      crease_pattern=base_cp,
      cut_line_start=cut_line_start,
      cut_line_end=cut_line_end,
      fold_assignment=fold_assignment,
      limiting_polygon=limiting_rectangles,
      graph_data=graph_data,
  )

  # Adjust fold percent to match the rotation angle.
  fold_percent = abs(rotation_angle / 180)
  shaping_creases = [
      dataclasses.replace(crease, fold_percent=fold_percent)
      for crease in shaping_creases
  ]

  return shaping_creases


def _clip_by_min_inscribe_depth(inscribe_depth: float, grid_size: int) -> float:
  """Returns the minimum inscribe depth for a given grid size."""
  return max(inscribe_depth, point_utils.DEFAULT_TOLERANCE * grid_size + 1e-5)


def _get_shaping_creases_with_heuristics(
    *,
    base_cp: cp_utils.CreasePattern,
    anchor: point_utils.Point,
    simple_fold_direction: np.ndarray,
    fold_assignment: crease_utils.Fold,
    limiting_polygon: (
        shaping_elements.ShapingFlap | shaping_elements.ShapingRiver
    ),
    graph_data: geometric_simple_fold.GraphData,
    folded_verts: list[tuple[float, float] | None],
    hinge_info_list: Sequence[packing_types.HingeInfo],
    rotation_angle: float,
    root_element: shaping_elements.ShapingElement,
    stick_figure: sf_utils.StickFigure,
    visualize: bool = False,
    inscribe_hparams: InscribeHParams = InscribeHParams(),
    extra_limiting_rectangles: Sequence[shaping_utils.Rectangle] = (),
) -> tuple[
    Sequence[crease_utils.Crease], shaping_elements.ShapingElement, bool
]:
  """Returns the shaping creases for a given anchor point and fold direction.

  Some heuristics are included to improve visual quality and reduce
  flat-foldability violations.

  Args:
      base_cp: The base crease pattern.
      anchor: The anchor point for the simple fold.
      simple_fold_direction: The simple fold direction for the simple fold.
      fold_assignment: The fold assignment for the simple fold.
      limiting_polygon: The limiting polygon for the simple fold.
      graph_data: The graph data for the base crease pattern.
      folded_verts: The folded vertices for the base crease pattern.
      hinge_info_list: The list of hinge info.
      rotation_angle: The rotation angle for the simple fold.
      root_element: The root element of the shaping element tree.
      stick_figure: The stick figure.
      visualize: Whether to visualize the cut line on the folded crease pattern.
      inscribe_hparams: Parameters controlling cut line inscription depth.
      extra_limiting_rectangles: Other rectangles to propagate creases to.

  Returns:
      A tuple containing:
        - The shaping creases for the element.
        - The shaping element used (after shrinking/inscribing).
  """
  # Filter out vertical simple fold directions.
  simple_fold_slope = _get_rotation_axis_slope(simple_fold_direction)
  if simple_fold_slope is None:
    logging.warning(
        'Simple fold direction is vertical for element: %s. Skipping.',
        limiting_polygon.name,
    )
    return [], limiting_polygon, False

  # Filter out nearly vertical simple fold directions.
  if (
      abs(_get_rotation_axis_slope(simple_fold_direction))  # pyrefly: ignore[bad-argument-type]
      > inscribe_hparams.max_slope_thresh
  ):
    logging.warning(
        'Slope of simple fold direction is too large for element: %s. '
        'Slope: %s. Skipping.',
        limiting_polygon.name,
        _get_rotation_axis_slope(simple_fold_direction),
    )
    return [], limiting_polygon, False
  # Otherwise, clip slope if still too large.
  elif (
      abs(_get_rotation_axis_slope(simple_fold_direction))  # pyrefly: ignore[bad-argument-type]
      > inscribe_hparams.clip_slope_thresh
  ):
    logging.warning(
        'Slope of simple fold direction is too large for element: %s. '
        'Slope: %s. Clipping.',
        limiting_polygon.name,
        _get_rotation_axis_slope(simple_fold_direction),
    )
    simple_fold_direction = _clip_slope_to_max(
        simple_fold_direction, inscribe_hparams.clip_slope_thresh
    )

  # Filter out creases with rotation angle 0.
  if math.isclose(rotation_angle, 0.0):
    logging.warning(
        'Rotation angle is close to 0 for element: %s. Skipping.',
        limiting_polygon.name,
    )
    return [], limiting_polygon, False

  # Clip angles near 90o to 90o
  if (
      abs(abs(simple_fold_slope) - 1.0)
      < inscribe_hparams.ninety_deg_slope_tolerance
  ):
    logging.info(
        'Clipping simple fold direction to slope 1 for element: %s',
        limiting_polygon.name,
    )
    simple_fold_direction = _clip_to_slope_one(simple_fold_direction)

  # Rotate simple_fold_direction to match how the flap is folded in 3D.
  simple_fold_direction = _rotate_simple_fold_direction_by_model_orientation(
      simple_fold_direction,
      root_element,
      stick_figure,
      graph_data,
      folded_verts,
  )

  bank_index = (
      limiting_polygon.get_outer_bank_index()
      if isinstance(limiting_polygon, shaping_elements.ShapingRiver)
      else None
  )

  # Increase inscribe depth if element has hinge.
  # NOTE: we inscribe with a hinge even if inscribe_depth > 0.0
  # because a close by fold is assumed to already be inscribed
  # due to the hinge.
  if inscribe_hparams.avoid_hinges and shaping_elements.has_assigned_hinge(
      limiting_polygon, hinge_info_list, bank_index=bank_index
  ):
    inscribe_depth = (
        inscribe_hparams.inscribe_depth + inscribe_hparams.hinge_inscribe_depth
    )
  else:
    inscribe_depth = inscribe_hparams.inscribe_depth

  # Inscribe cut line if inscribe depth is specified.
  inscribe_success = True
  if inscribe_depth > 0.0:
    # Get min inscribe depth depending on grid size and point tolerance.
    # Otherwise the inscribed point will be snapped back to the grid.
    inscribe_depth = _clip_by_min_inscribe_depth(
        inscribe_depth, grid_size=base_cp.grid_size
    )
    logging.info(
        'Inscribing cut line for element: %s with depth: %s',
        limiting_polygon.name,
        inscribe_depth,
    )
    anchor, limiting_polygon, inscribe_success = (
        geometric_fold_3d_heuristics_utils.inscribe_cut_line(
            anchor, limiting_polygon, inscribe_depth=inscribe_depth
        )
    )
    logging.info(
        'Inscribed cut line for element: %s. New anchor: %s, new limiting'
        ' polygon: %s',
        limiting_polygon.name,
        anchor,
        limiting_polygon,
    )

  creases = _get_shaping_creases(
      base_cp=base_cp,
      anchor=anchor,
      simple_fold_direction=simple_fold_direction,
      fold_assignment=fold_assignment,
      limiting_polygon=limiting_polygon,
      graph_data=graph_data,
      folded_verts=folded_verts,
      visualize=visualize,
      rotation_angle=rotation_angle,
      extra_limiting_rectangles=extra_limiting_rectangles,
  )
  return creases, limiting_polygon, inscribe_success


def shape_element_with_3d_geometric_folding_heuristics(
    *,
    element: shaping_elements.ShapingElement,
    base_cp: cp_utils.CreasePattern,
    simple_fold_info: heuristics_3d.SimpleFoldInfo,
    hinge_info_list: Sequence[packing_types.HingeInfo],
    root_element: shaping_elements.ShapingElement,
    stick_figure: sf_utils.StickFigure,
    inscribe_hparams: InscribeHParams = InscribeHParams(),
    visualize: bool = False,
    graph_data: geometric_simple_fold.GraphData | None = None,
    extra_limiting_rectangles: Sequence[shaping_utils.Rectangle] = (),
) -> ElementShapingResult:
  """Shapes a single element with 3D geometric folding heuristics.

  The heuristic proceeds in several steps:
  1. The folded state of the base crease pattern is computed.
  2. The boundary of the shaping element is determined.
  3. Two points on the boundary with opposite elevations are found.
  4. Apply a two geometric simple folds with each point as the anchor.
    Only one of the folds will typically succeed (i.e. produce creases
    that intersect the target element).

  Args:
      element: The shaping element to shape.
      base_cp: The base crease pattern.
      simple_fold_info: The simple fold info for the element. Computed by
        heuristics_3d.get_flap_post_dict().
      hinge_info_list: The list of hinge info.
      root_element: The root element of the shaping element tree.
      stick_figure: The stick figure.
      inscribe_hparams: Parameters controlling cut line inscription depth.
      visualize: Whether to visualize the cut line on the folded crease pattern.
      graph_data: Precomputed graph data for the crease pattern. If None, it
        will be computed from base_cp.
      extra_limiting_rectangles: Other rectangles to propagate creases to.

  Returns:
      A list of ElementShapingResult objects, one for each successful fold
      attempt.
  """
  # Skip elements with no fold.
  if math.isclose(simple_fold_info.rotation_angle, 0.0):
    logging.info(
        'No fold for element: %s. Rotation angle: %s. Skipping.',
        element.name,
        simple_fold_info.rotation_angle,
    )
    return ElementShapingResult(
        simple_fold_info=simple_fold_info,
        shaping_element=element,
        shaping_creases=[],
    )

  # 1. Compute Folded State
  # NOTE: optimize runtime by caching graph data.
  if graph_data is None:
    graph_data = geometric_simple_fold.prepare_graph_data(base_cp)
  folded_verts = graph_data['folded_vertices']

  # 2. Get Shaping Boundary
  match element:
    case shaping_elements.ShapingFlap():
      shaping_boundary = shaping_elements.get_flap_boundary(
          element, element.grid_size
      )
    case shaping_elements.ShapingRiver():
      shaping_boundary = element.get_boundary_from_index(
          element.get_outer_bank_index()
      )
    case _ as unreachable:
      typing.assert_never(unreachable)

  # Compute points on the boundary of the flap on opposite elevations.
  elevations = element.elevations
  if len(elevations) < 2:
    elevation_diff = 1
  else:
    elevation_diff = max(elevations) - min(elevations)
  p1, p2 = get_opposite_hinge_points(
      shaping_boundary, element.grid_size, elevation_diff, element.creases
  )

  # 3. Try geometric folding with both hinge points as the anchor.
  # NOTE: Check this assignment.
  fold_assignment = (
      crease_utils.Fold.MOUNTAIN
      if simple_fold_info.rotation_angle > 0
      else crease_utils.Fold.VALLEY
  )

  simple_fold_direction = simple_fold_info.rotation_axis_local
  logging.info('simple_fold_direction: %s', simple_fold_direction)
  logging.info('slope: %s', _get_rotation_axis_slope(simple_fold_direction))

  # If close to 180o, round to 180o.
  if abs(simple_fold_direction[1]) < 0.1:
    simple_fold_direction = np.array([1.0, 0.0, 0.0])

  shaping_creases: Sequence[crease_utils.Crease] = []
  shaped_element = element
  inscribe_success = False
  for anchor in (p1, p2):
    shaping_creases, shaped_element, inscribe_success = (
        _get_shaping_creases_with_heuristics(
            base_cp=base_cp,
            anchor=anchor,
            simple_fold_direction=simple_fold_direction,
            fold_assignment=fold_assignment,
            limiting_polygon=element,
            hinge_info_list=hinge_info_list,
            graph_data=graph_data,
            folded_verts=folded_verts,
            root_element=root_element,
            stick_figure=stick_figure,
            visualize=visualize,
            inscribe_hparams=inscribe_hparams,
            rotation_angle=simple_fold_info.rotation_angle,
            extra_limiting_rectangles=extra_limiting_rectangles,
        )
    )
    if shaping_creases:
      break

  if not inscribe_success:
    return ElementShapingResult(
        simple_fold_info=simple_fold_info,
        shaping_element=element,
        shaping_creases=[],
    )
  return ElementShapingResult(
      simple_fold_info=simple_fold_info,
      shaping_element=shaped_element,
      shaping_creases=shaping_creases,
  )


def get_shaping_creases_with_3d_geometric_folding_heuristics(
    *,
    base_cp: cp_utils.CreasePattern,
    stick_figure: sf_utils.StickFigure,
    shaping_flaps: Sequence[shaping_elements.ShapingFlap],
    shaping_rivers: Sequence[shaping_elements.ShapingRiver],
    hinge_info_list: Sequence[packing_types.HingeInfo],
    central_crease_removed: bool,
    shape_with_unmerged_tree: bool,
    merge_converter: dict[str, str] | None = None,
    visualize: bool = False,
    hparams: GeometricFolding3DHParams = GeometricFolding3DHParams(),
    graph_data: geometric_simple_fold.GraphData | None = None,
    shaping_data: heuristics_utils.ShapingData | None = None,
    sacrificial_flaps: Sequence[packing_types.SacrificialFlap] = (),
) -> Heuristics3DShapingResult:
  """Returns shaping creases using 3D geometric folding heuristics.

  The heuristic proceeds in several steps:
  1. Find a good stick figure root and rotate the stick figure so that the root
    has 0 elevation and 0 azimuth.
  2. Compute flap info dict for each shaping element. This determines element
    orientation in the base crease pattern.
  3. Compute each element's local cooridnate shaping rotation using 3D
    folding heuristics.
  4. Combine each element's local coordinate rotation with geometric simple
    folds to obtain the final shaping creases.

  Args:
      base_cp: The base crease pattern.
      stick_figure: The stick figure.
      shaping_flaps: The shaping flaps.
      shaping_rivers: The shaping rivers.
      hinge_info_list: The list of hinge info.
      central_crease_removed: Whether the central crease has been removed.
      shape_with_unmerged_tree: Whether to shape with unmerged tree.
      merge_converter: The merge converter.
      visualize: Whether to visualize the cut line on the folded CP.
      hparams: Hyperparameters controlling heuristic behavior.
      graph_data: Precomputed graph data for the crease pattern.
      shaping_data: Precomputed shaping data for the crease pattern.
      sacrificial_flaps: All sacrificial flaps in the crease pattern.

  Returns:
      A Heuristics3DShapingResult containing:
        - shaping_creases: The shaping creases for the crease pattern.
        - detailed_shaping_info: A dictionary mapping element names to a list of
          element shaping results.
  """
  logging.info(
      'Getting shaping creases for %s with 3D geometric folding heuristics.',
      stick_figure.name,
  )

  is_input_symmetric = stick_figure.is_symmetric_tree
  symmetric_partners: dict[str, str] = {}
  if is_input_symmetric:
    for s in stick_figure.children:
      if (
          s.symmetric_stick_name is not None
          and s.symmetric_stick_name != s.name
      ):
        symmetric_partners[s.name] = s.symmetric_stick_name
    if not shape_with_unmerged_tree:
      merged_sf, _ = stick_figure.merge_linear_chains()
      if merged_sf.is_symmetric_tree:
        for s in merged_sf.children:
          if (
              s.symmetric_stick_name is not None
              and s.symmetric_stick_name != s.name
          ):
            symmetric_partners[s.name] = s.symmetric_stick_name

  # 0. Compute a good stick_figure root and assign it.
  root = heuristics.get_first_stick_for_shaping(stick_figure)
  stick_figure = dataclasses.replace(stick_figure, root=root.name)
  stick_figure = stick_figure.align_root_stick_to_target_azimuth_elevation()

  # 1. Compute flap info dict.
  if shaping_data is None:
    shaping_data = heuristics_utils.get_heuristics_shaping_data(
        stick_figure=stick_figure,
        shaping_flaps=list(shaping_flaps),
        shaping_rivers=list(shaping_rivers),
        hinge_info_list=list(hinge_info_list),
        central_crease_removed=central_crease_removed,
        shape_with_unmerged_tree=shape_with_unmerged_tree,
        merge_converter=merge_converter,
        sacrificial_flaps=sacrificial_flaps,
    )
  shaping_flaps = shaping_data['shaping_flaps']
  shaping_rivers = shaping_data['shaping_rivers']
  flap_info_dict = shaping_data['flap_info']
  outer_bank_indices = shaping_data['outer_bank_indices']
  logging.debug('flap_info_dict: %s', flap_info_dict)

  # 2. Update shaping rivers outer_bank_indices.
  shaping_rivers = [
      shaping_river.update_outer_bank_index(
          cast(shaping_types.BankIndex, outer_bank_indices[shaping_river.name])
      )
      for shaping_river in shaping_rivers
  ]

  flap_strategies = {flap.name: hparams.strategy for flap in shaping_flaps}
  flap_strategies.update(hparams.per_flap_strategy)
  simple_fold_info_dict = heuristics_3d.get_flap_post_dict(
      stick_figure,
      flap_info_dict,
      make_post_hinge_top=True,
      default_strategy=hparams.strategy,
      flap_strategies=flap_strategies,
      max_slope_thresh=hparams.default_inscribe_hparams.max_slope_thresh,
  )

  # 4. Compute shaping creases for each element.
  elements = shaping_flaps + shaping_rivers
  root_element = shaping_elements.get_element_by_name(
      stick_figure.root, shaping_flaps, shaping_rivers
  )
  if hparams.shape_subset is not None:
    elements = [
        element for element in elements if element.name in hparams.shape_subset
    ]
  shaping_flaps_by_name = {flap.name: flap for flap in shaping_flaps}
  elements_by_name = {element.name: element for element in elements}
  if is_input_symmetric:
    for elem_name in elements_by_name:
      if elem_name.endswith(packing_types.COPY_SUFFIX):
        base_name = elem_name[: -len(packing_types.COPY_SUFFIX)]
        if (
            base_name in elements_by_name
            and base_name not in symmetric_partners
            and elem_name not in symmetric_partners
        ):
          symmetric_partners[base_name] = elem_name
          symmetric_partners[elem_name] = base_name
    symmetric_partners = {
        k: v
        for k, v in symmetric_partners.items()
        if k in elements_by_name and v in elements_by_name
    }
  if graph_data is None:
    graph_data = geometric_simple_fold.prepare_graph_data(base_cp)
  accepted_creases_by_element: dict[str, list[crease_utils.Crease]] = {}
  discarded_partners: dict[str, str] = {}
  detailed_shaping_info = {}
  current_cp = base_cp

  def _rollback_partner(partner_name: str, failed_name: str) -> None:
    nonlocal current_cp, accepted_creases_by_element
    if partner_name in accepted_creases_by_element:
      accepted_creases_by_element.pop(partner_name, None)
      detailed_shaping_info.pop(partner_name, None)
      logging.warning(
          'Flat foldability violation detected after shaping element: %s. '
          'Discarding creases for this element (symmetric partner %s failed).',
          partner_name,
          failed_name,
      )
      rebuilt_cp = base_cp
      if hparams.check_ff_violations:
        surviving: dict[str, list[crease_utils.Crease]] = {}
        for kept_name, kept_creases in accepted_creases_by_element.items():
          if not kept_creases:
            surviving[kept_name] = kept_creases
            continue
          cand_cp = rebuilt_cp.update_with_shaping_creases(kept_creases)
          if cand_cp.local_flat_foldability():
            rebuilt_cp = cand_cp
            surviving[kept_name] = kept_creases
          else:
            detailed_shaping_info.pop(kept_name, None)
        accepted_creases_by_element = surviving
      current_cp = rebuilt_cp
    else:
      discarded_partners[partner_name] = failed_name

  for element in elements:
    logging.info(
        'Shaping element: %s with 3D geometric folding heuristics.',
        element.name,
    )
    if element.name in discarded_partners:
      failed_partner = discarded_partners[element.name]
      logging.warning(
          'Flat foldability violation detected after shaping element: %s. '
          'Discarding creases for this element (symmetric partner %s failed).',
          element.name,
          failed_partner,
      )
      continue
    if element.name not in simple_fold_info_dict:
      logging.warning(
          'No simple fold info found for element: %s. Skipping.', element.name
      )
      continue
    simple_fold_infos = simple_fold_info_dict[element.name]
    element_creases = []
    element_had_assertion_failure = False
    extra_limiting_rectangles = [
        shaping_flaps_by_name[sac_flap].to_legacy_rectangle()
        for sac_flap in flap_info_dict[element.name].sacrificial_flaps
    ]
    for simple_fold_info in simple_fold_infos:
      logging.info('simple_fold_info: %s', simple_fold_info)
      # NOTE: consider increasing min angle tolerance.
      if math.isclose(simple_fold_info.rotation_angle, 0.0, abs_tol=1e-3):
        logging.info(
            'Skipping element: %s with 0 rotation angle.',
            element.name,
        )
        continue
      try:
        element_output = shape_element_with_3d_geometric_folding_heuristics(
            element=element,
            base_cp=base_cp,
            simple_fold_info=simple_fold_info,
            hinge_info_list=hinge_info_list,
            root_element=root_element,
            stick_figure=stick_figure,
            visualize=visualize,
            inscribe_hparams=dataclasses.replace(
                hparams.default_inscribe_hparams,
                inscribe_depth=simple_fold_info.inscribe_depth,
                hinge_inscribe_depth=hparams.per_flap_hinge_inscribe_depth.get(
                    element.name,
                    hparams.default_inscribe_hparams.hinge_inscribe_depth,
                ),
            ),
            graph_data=graph_data,
            extra_limiting_rectangles=extra_limiting_rectangles,
        )
        element_creases.extend(element_output['shaping_creases'])
        if element.name not in detailed_shaping_info:
          detailed_shaping_info[element.name] = []
        detailed_shaping_info[element.name].append(element_output)
      except AssertionError as e:
        element_had_assertion_failure = True
        logging.warning(
            'Failed to shape element: %s with 3D geometric folding heuristics. '
            'Simple fold info: %s. '
            'Skipping. Error: %s',
            element.name,
            simple_fold_info.rotation_axis_local,
            e,
        )
    if element_had_assertion_failure and element.name in symmetric_partners:
      detailed_shaping_info.pop(element.name, None)
      logging.warning(
          'Flat foldability violation detected after shaping element: %s. '
          'Discarding creases for this element (symmetric failure).',
          element.name,
      )
      _rollback_partner(symmetric_partners[element.name], element.name)
      continue
    if hparams.check_ff_violations and element_creases:
      updated_cp = current_cp.update_with_shaping_creases(element_creases)
      if not updated_cp.local_flat_foldability():
        logging.warning(
            'Flat foldability violation detected after shaping element: %s. '
            'Discarding creases for this element.',
            element.name,
        )
        detailed_shaping_info.pop(element.name, None)
        if element.name in symmetric_partners:
          _rollback_partner(symmetric_partners[element.name], element.name)
        continue
      current_cp = updated_cp
    accepted_creases_by_element[element.name] = element_creases

  shaping_creases: list[crease_utils.Crease] = []
  for creases in accepted_creases_by_element.values():
    shaping_creases.extend(creases)
  return Heuristics3DShapingResult(
      shaping_creases=shaping_creases,
      detailed_shaping_info=detailed_shaping_info,
  )


def shape_cp_with_3d_geometric_folding_heuristics_pipeline_wrapper(
    *,
    base_cp: cp_utils.CreasePattern,
    stick_figure: sf_utils.StickFigure,
    packing_output: packing_output_utils.PackingOutput,
    solving_output: hinge_utils.SolverResult,
    solving_grid_size: int,
    central_crease_removed: bool,
    shape_with_unmerged_tree: bool = True,
    merge_converter: dict[str, str] | None = None,
    visualize: bool = False,
    hparams: GeometricFolding3DHParams = GeometricFolding3DHParams(),
    light_mode: bool = False,
    shaping_flaps: Sequence[shaping_elements.ShapingFlap] | None = None,
    shaping_rivers: Sequence[shaping_elements.ShapingRiver] | None = None,
    graph_data: geometric_simple_fold.GraphData | None = None,
    shaping_data: heuristics_utils.ShapingData | None = None,
) -> cp_utils.CreasePattern:
  """Shapes a crease pattern using 3D geometric folding heuristics."""
  if shaping_flaps is None or shaping_rivers is None:
    packing_cp = packing_output.packing_cp
    assert packing_cp is not None, 'Packing CP is None.'
    shaping_flaps, shaping_rivers = (
        shaping_elements.convert_packing_elements_to_shaping_elements(
            packing_rectangles=packing_output.flap_rectangles,  # pyrefly: ignore[bad-argument-type]
            packing_rivers=packing_output.packing_rivers,  # pyrefly: ignore[bad-argument-type]
            packing_grid_size=packing_cp.grid_size,
            solving_grid_size=solving_grid_size,
            base_cp=base_cp,
        )
    )

  hinge_info_list = heuristics.copy_hinge_info_list(packing_output.hinges)
  hinge_info_list = heuristics.update_hinge_info_from_solver_result(
      hinge_info_list, solving_output  # pyrefly: ignore[bad-argument-type]
  )

  shaping_result = get_shaping_creases_with_3d_geometric_folding_heuristics(
      base_cp=base_cp,
      stick_figure=stick_figure,
      shaping_flaps=shaping_flaps,
      shaping_rivers=shaping_rivers,
      hinge_info_list=hinge_info_list,
      central_crease_removed=central_crease_removed,
      shape_with_unmerged_tree=shape_with_unmerged_tree,
      merge_converter=merge_converter,
      visualize=visualize,
      hparams=hparams,
      graph_data=graph_data,
      shaping_data=shaping_data,
      sacrificial_flaps=packing_output.sacrificial_flaps or [],
  )

  return base_cp.update_with_shaping_creases(
      shaping_result['shaping_creases'],
      split_shaping_by_shaping=not light_mode,
  )
