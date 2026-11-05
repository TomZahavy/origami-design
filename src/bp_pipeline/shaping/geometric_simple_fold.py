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

"""Utility functions for applying geometric simple folds to crease patterns."""

import collections
import itertools
import logging
from typing import Sequence, TypeAlias, TypedDict

from .. import timeout as timeout_lib
from ..crease_pattern import crease as crease_utils
from ..crease_pattern import crease_pattern as cp_utils
from ..crease_pattern import point as point_utils
from ..third_party.flat_folder import folded_state
from ..third_party.flat_folder import graph_creation
from ..third_party.flat_folder import graph_topology
from ..third_party.flat_folder import math_utils
from . import shaping_elements
from . import shaping_utils

Point = math_utils.Point
Edge = math_utils.Edge

LimitingPolygon: TypeAlias = (
    shaping_utils.Rectangle
    | shaping_elements.ShapingFlap
    | shaping_elements.ShapingRiver
    | list[shaping_utils.Rectangle]
)


def interpolate(*, point1: Point, point2: Point, t: float) -> Point:
  """Linearly interpolates between two points."""
  return (
      point1[0] + t * (point2[0] - point1[0]),
      point1[1] + t * (point2[1] - point1[1]),
  )


class GraphData(TypedDict):
  """Graph data for folding simulations.

  Attributes:
      vertices_coords: Unfolded coordinates of vertices.
      face_vertices: list of vertex indices per face.
      edge_vertices: list of vertex index pairs per edge.
      edge_assignments: Fold assignment (M/V/B/U) for each edge.
      edge_key_to_faces: Map from edge tuple to list of adjacent face indices.
      folded_vertices: Folded coordinates of vertices.
      face_orientations: List of face orientations (flipped or not).
  """

  vertices_coords: list[Point]
  face_vertices: list[list[int]]
  edge_vertices: list[list[int]]
  edge_assignments: list[str]
  edge_key_to_faces: dict[tuple[int, int], list[int]]
  folded_vertices: list[Point | None]
  face_orientations: list[bool | None]


def prepare_graph_data(crease_pattern: cp_utils.CreasePattern) -> GraphData:
  """Prepares graph data from a crease pattern for folding simulations."""
  lines = []
  assignments = []
  for c in crease_pattern.creases:
    timeout_lib.maybe_timeout_cooperatively()
    lines.append(((c.p1.x, c.p1.y), (c.p2.x, c.p2.y)))
    if c.fold == crease_utils.Fold.MOUNTAIN:
      assignments.append('M')
    elif c.fold == crease_utils.Fold.VALLEY:
      assignments.append('V')
    elif c.fold == crease_utils.Fold.BORDER:
      assignments.append('B')
    else:
      assignments.append('U')

  vertices_coords, edge_vertices, edge_lines, _ = (
      graph_creation.create_graph_from_lines(lines)
  )
  edge_assignments = []
  for indices in edge_lines:
    timeout_lib.maybe_timeout_cooperatively()
    if not indices:
      edge_assignments.append('U')
    else:
      edge_assignments.append(assignments[indices[0]])

  _, face_vertices = graph_topology.graph_to_adjacency_and_faces(
      vertices_coords, edge_vertices
  )
  edge_key_to_faces = collections.defaultdict(list)
  for face_index, vertices in enumerate(face_vertices):
    timeout_lib.maybe_timeout_cooperatively()
    for i, vertex1 in enumerate(vertices):
      vertex2 = vertices[(i + 1) % len(vertices)]
      edge_key = tuple(sorted((vertex1, vertex2)))
      edge_key_to_faces[edge_key].append(face_index)

  folded_vertices, face_orientations = folded_state.compute_folded_state(
      vertices_coords, face_vertices, edge_vertices, edge_assignments
  )

  return {
      'vertices_coords': vertices_coords,
      'face_vertices': face_vertices,
      'edge_vertices': edge_vertices,
      'edge_assignments': edge_assignments,
      'edge_key_to_faces': dict(edge_key_to_faces),
      'folded_vertices': folded_vertices,
      'face_orientations': face_orientations,
  }


def _check_inside_limiting_polygon(
    point: Point, limiting_polygon: LimitingPolygon | None
) -> bool:
  """Checks if a point is inside a limiting polygon."""
  if limiting_polygon is None:
    return True
  pt = point_utils.Point(x=point[0], y=point[1], require_on_paper=False)
  if isinstance(limiting_polygon, list):
    return any(polygon.is_internal_point(pt) for polygon in limiting_polygon)
  elif isinstance(
      limiting_polygon,
      (
          shaping_elements.ShapingRiver,
          shaping_utils.Rectangle,
          shaping_elements.ShapingFlap,
      ),
  ):
    return limiting_polygon.is_internal_point(pt)
  else:
    raise ValueError(
        'limiting_polygon must be a list of Rectangles, a Rectangle, a '
        f'ShapingFlap or a ShapingRiver. Got: {type(limiting_polygon)}.'
    )


def get_face_intersections_in_unfolded_plane(
    face_vertex_indices: list[int],
    folded_vertices: list[Point | None],
    unfolded_vertices: list[Point],
    *,
    cut_line_start: Point,
    cut_line_end: Point,
) -> list[Point]:
  """Computes intersections of a single face with the cut line."""
  intersections = []
  line_crease: crease_utils.Crease | None = None
  for i, vertex1_index in enumerate(face_vertex_indices):
    vertex2_index = face_vertex_indices[(i + 1) % len(face_vertex_indices)]

    point1_folded = folded_vertices[vertex1_index]
    point2_folded = folded_vertices[vertex2_index]

    if point1_folded is None or point2_folded is None:
      continue

    segment_p1 = point_utils.Point(
        x=point1_folded[0], y=point1_folded[1], require_on_paper=False
    )
    segment_p2 = point_utils.Point(
        x=point2_folded[0], y=point2_folded[1], require_on_paper=False
    )
    # Narrowing can emit folded sub-faces with corners closer than Point's
    # default tolerance even when graph_creation kept them distinct.
    if segment_p1.isclose(segment_p2):
      continue
    segment_crease = crease_utils.Crease(
        segment_p1, segment_p2, fold=crease_utils.Fold.BORDER
    )
    if line_crease is None:
      line_p1 = point_utils.Point(
          x=cut_line_start[0], y=cut_line_start[1], require_on_paper=False
      )
      line_p2 = point_utils.Point(
          x=cut_line_end[0], y=cut_line_end[1], require_on_paper=False
      )
      line_crease = crease_utils.Crease(
          line_p1, line_p2, fold=crease_utils.Fold.BORDER
      )
    intersection = segment_crease.vertex_with_crease(
        line_crease,
        extend_lines=True,
        include_external=True,
    )
    if intersection is not None:
      if intersection.isclose(segment_p1, atol=point_utils.DEFAULT_TOLERANCE):
        intersection = segment_p1
      elif intersection.isclose(segment_p2, atol=point_utils.DEFAULT_TOLERANCE):
        intersection = segment_p2

    if (
        intersection
        and segment_crease.point_status(intersection)
        == crease_utils.PointStatus.EXTERNAL
    ):
      intersection = None

    if intersection is not None:
      dx_folded = point2_folded[0] - point1_folded[0]
      dy_folded = point2_folded[1] - point1_folded[1]

      if abs(dx_folded) > abs(dy_folded):
        t = (
            (intersection.x - point1_folded[0]) / dx_folded
            if abs(dx_folded) > point_utils.DEFAULT_TOLERANCE
            else 0.0
        )
      else:
        t = (
            (intersection.y - point1_folded[1]) / dy_folded
            if abs(dy_folded) > point_utils.DEFAULT_TOLERANCE
            else 0.0
        )
      t = max(0.0, min(1.0, t))

      point1_unfolded = unfolded_vertices[vertex1_index]
      point2_unfolded = unfolded_vertices[vertex2_index]
      point_unfolded = interpolate(
          point1=point1_unfolded, point2=point2_unfolded, t=t
      )
      if not any(
          math_utils.distance(existing_point, point_unfolded)
          < point_utils.DEFAULT_TOLERANCE
          for existing_point in intersections
      ):
        intersections.append(point_unfolded)
  return intersections


def compute_intersections_and_selected_face_indices(
    *,
    vertices_coords: list[Point],
    face_vertices: list[list[int]],
    folded_vertices: list[Point | None],
    face_orientations: list[bool | None],
    cut_line_start: Point,
    cut_line_end: Point,
    limiting_polygon: LimitingPolygon | None,
) -> tuple[dict[int, tuple[Point, Point]], list[int]]:
  """Calculates face-cut intersections and identifies selected face indices."""
  face_cuts = {}  # face_idx -> (p1_unfolded, p2_unfolded)
  selected_face_indices = []
  for face_index, face in enumerate(face_vertices):
    timeout_lib.maybe_timeout_cooperatively()
    if face_orientations[face_index] is None:
      continue

    intersections = get_face_intersections_in_unfolded_plane(
        face,
        folded_vertices,
        vertices_coords,
        cut_line_start=cut_line_start,
        cut_line_end=cut_line_end,
    )

    if len(intersections) >= 3:
      intersections = [
          intersection
          for intersection in intersections
          if _check_inside_limiting_polygon(intersection, limiting_polygon)
      ]

    if len(intersections) >= 2:
      best_pair = max(
          (
              (intersection_1, intersection_2)
              for intersection_1, intersection_2 in itertools.combinations(
                  intersections, 2
              )
          ),
          key=lambda pair: math_utils.distance(pair[0], pair[1]),
      )
      face_cuts[face_index] = best_pair
      selected_face_indices.append(face_index)

  return face_cuts, selected_face_indices


def create_new_creases_from_cuts(
    *,
    selected_face_indices: list[int],
    face_cuts: dict[int, tuple[Point, Point]],
    face_orientations: list[bool | None],
    fold_assignment: crease_utils.Fold,
) -> dict[int, crease_utils.Crease]:
  """Creates new creases from face cuts, selected_face_indices, and orientations."""
  faces_to_process = set(selected_face_indices)

  new_creases_dict = {}
  for face_idx in faces_to_process:
    timeout_lib.maybe_timeout_cooperatively()
    intersections = face_cuts[face_idx]
    is_flipped = face_orientations[face_idx]

    current_assignment = fold_assignment
    if is_flipped:
      current_assignment = (
          crease_utils.Fold.VALLEY
          if fold_assignment == crease_utils.Fold.MOUNTAIN
          else crease_utils.Fold.MOUNTAIN
      )

    try:
      new_creases_dict[face_idx] = crease_utils.Crease(
          point_utils.Point(x=intersections[0][0], y=intersections[0][1]),
          point_utils.Point(x=intersections[1][0], y=intersections[1][1]),
          fold=current_assignment,
      )
    except ValueError as e:
      logging.exception('Failed to create crease for face %d: %s', face_idx, e)
      continue

  return new_creases_dict


def _restrict_creases_to_limiting_polygon(
    creases: Sequence[crease_utils.Crease],
    limiting_polygon: LimitingPolygon,
) -> Sequence[crease_utils.Crease]:
  """Restricts creases to the given limiting polygon."""
  if isinstance(limiting_polygon, list):
    rects = limiting_polygon
  elif isinstance(limiting_polygon, shaping_elements.ShapingRiver):
    rects = [
        shaping_utils.Rectangle.from_shaping_rect(r)
        for r in limiting_polygon.covering_rectangles
    ]
  elif isinstance(limiting_polygon, shaping_elements.ShapingFlap):
    rects = [limiting_polygon.to_legacy_rectangle()]
  elif isinstance(limiting_polygon, shaping_utils.Rectangle):
    rects = [limiting_polygon]
  else:
    raise ValueError(
        'limiting_polygon must be a list of Rectangles, a Rectangle, a '
        f'ShapingFlap or a ShapingRiver. Got: {type(limiting_polygon)}.'
    )
  restricted_crease_lists = shaping_utils.restrict_creases_to_rectangles(
      rects, creases
  )
  restricted_creases = []
  for crease_list in restricted_crease_lists:
    assert len(crease_list) <= 1
    restricted_creases.extend(crease_list)
  return restricted_creases


def get_geometric_fold_creases(
    *,
    crease_pattern: cp_utils.CreasePattern,
    cut_line_start: Point,
    cut_line_end: Point,
    fold_assignment: crease_utils.Fold = crease_utils.Fold.MOUNTAIN,
    limiting_polygon: LimitingPolygon | None = None,
    graph_data: GraphData | None = None,
) -> Sequence[crease_utils.Crease]:
  """Returns the creases resulting from a geometric simple fold."""
  if graph_data is None:
    graph_data = prepare_graph_data(crease_pattern)
  vertices_coords = graph_data['vertices_coords']
  face_vertices = graph_data['face_vertices']
  folded_vertices = graph_data['folded_vertices']
  face_orientations = graph_data['face_orientations']

  face_cuts, selected_face_indices = (
      compute_intersections_and_selected_face_indices(
          vertices_coords=vertices_coords,
          face_vertices=face_vertices,
          folded_vertices=folded_vertices,
          face_orientations=face_orientations,
          cut_line_start=cut_line_start,
          cut_line_end=cut_line_end,
          limiting_polygon=limiting_polygon,
      )
  )

  new_creases_dict = create_new_creases_from_cuts(
      selected_face_indices=selected_face_indices,
      face_cuts=face_cuts,
      face_orientations=face_orientations,
      fold_assignment=fold_assignment,
  )
  creases = list(new_creases_dict.values())

  if limiting_polygon is not None:
    creases = _restrict_creases_to_limiting_polygon(creases, limiting_polygon)

  return creases


def shape_cp_geometric(
    crease_pattern: cp_utils.CreasePattern,
    *,
    cut_line_start: Point,
    cut_line_end: Point,
    fold_assignment: crease_utils.Fold = crease_utils.Fold.MOUNTAIN,
    limiting_polygon: LimitingPolygon | None = None,
    graph_data: GraphData | None = None,
) -> cp_utils.CreasePattern:
  """Applies a simple fold defined by a cut line in the folded state."""
  new_creases = get_geometric_fold_creases(
      crease_pattern=crease_pattern,
      cut_line_start=cut_line_start,
      cut_line_end=cut_line_end,
      fold_assignment=fold_assignment,
      limiting_polygon=limiting_polygon,
      graph_data=graph_data,
  )
  return crease_pattern.update_with_shaping_creases(new_creases)
