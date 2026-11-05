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
#
# Ported from Flat-Folder (https://github.com/origamimagiro/flat-folder),
# Copyright (c) 2022 Jason S. Ku (origamimagiro), licensed under the MIT
# License; see LICENSE in this directory.
# ==============================================================================

"""Folded state utilities for flat-folder."""

import math
from . import math_utils

Point = math_utils.Point
Edge = math_utils.Edge


def check_vertex_foldability(
    vertices: list[Point],
    vertex_adjacencies: list[list[int]],
    edge_vertices: list[Edge],
    edge_assignments: list[str],
    log: list[str] | None,
    kawasaki_epsilon: float,
) -> list[dict[str, str | float | int]]:
  """Checks Maekawa's and Kawasaki's theorems for each vertex.

  Args:
      vertices: List of vertex coordinates.
      vertex_adjacencies: List of adjacency lists for each vertex.
      edge_vertices: List of edges defined by vertex indices.
      edge_assignments: List of assignments ('M', 'V', 'B', 'U') for each edge.
      log: An optional list to append logging messages to.
      kawasaki_epsilon: Tolerance for Kawasaki's theorem check.

  Returns:
      A list of dictionaries, one for each vertex, indicating foldability
      status ('ok', 'maekawa', 'kawasaki') and deviation if any.
  """
  if log is None:
    log = []
  assignment_map = {}
  for edge_index, pair in enumerate(edge_vertices):
    vertex1, vertex2 = pair
    assignment = edge_assignments[edge_index]
    assignment_map[math_utils.list_to_tuple([vertex1, vertex2])] = assignment
    assignment_map[math_utils.list_to_tuple([vertex2, vertex1])] = assignment

  vertex_kawasaki_results = []
  for vertex_index, neighbors in enumerate(vertex_adjacencies):
    log.append(f"--- Checking Vertex v{vertex_index} ---")
    internal_neighbors = []
    is_boundary = False
    mountain_count, valley_count, unassigned_count = 0, 0, 0
    for neighbor_index in neighbors:
      assignment = assignment_map.get(
          math_utils.list_to_tuple([vertex_index, neighbor_index])
      )
      if assignment == "B":
        is_boundary = True
        break
      if assignment in ["V", "M", "U"]:
        internal_neighbors.append(neighbor_index)
      if assignment == "M":
        mountain_count += 1
      if assignment == "V":
        valley_count += 1
      if assignment == "U":
        unassigned_count += 1

    log.append(
        f"[v{vertex_index}] Crease counts: M={mountain_count},"
        f" V={valley_count}, U={unassigned_count}. Internal:"
        f" {len(internal_neighbors)}"
    )

    if is_boundary or not internal_neighbors:
      log.append(f"[v{vertex_index}] STATUS: OK")
      vertex_kawasaki_results.append({"type": "ok", "deviation": 0})
    elif (
        (unassigned_count == 0) and (abs(mountain_count - valley_count) != 2)
    ) or (len(internal_neighbors) % 2 != 0):
      deviation = abs(mountain_count - valley_count)
      log.append(f"[v{vertex_index}] FAILED Maekawa")
      vertex_kawasaki_results.append({
          "type": "maekawa",
          "deviation": deviation,
          "M": mountain_count,
          "V": valley_count,
      })
    else:
      angles = [
          math_utils.angle(
              math_utils.subtract(vertices[j], vertices[vertex_index])
          )
          for j in internal_neighbors
      ]
      angles.sort()
      kawasaki_sum = 0
      for j in range(0, len(angles), 2):
        kawasaki_sum += angles[j + 1] - angles[j]

      deviation = abs(kawasaki_sum - math.pi)
      if deviation > kawasaki_epsilon:
        log.append(f"[v{vertex_index}] FAILED Kawasaki deviation={deviation}")
      else:
        log.append(f"[v{vertex_index}] OK Kawasaki")
      vertex_kawasaki_results.append(
          {"type": "kawasaki", "deviation": deviation}
      )
  return vertex_kawasaki_results


def compute_folded_state(
    vertices: list[Point],
    face_vertices: list[list[int]],
    edge_vertices: list[Edge],
    edge_assignments: list[str],
) -> tuple[list[Point | None], list[bool | None]]:
  """Computes folded vertex coordinates and face orientations.

  Assumes face 0 is face-up and computes folded coordinates and
  orientations for all other faces via BFS starting from face 0.

  Args:
      vertices: List of vertex coordinates in unfolded state.
      face_vertices: List of faces, each defined by vertex indices.
      edge_vertices: List of edges defined by vertex indices.
      edge_assignments: List of assignments ('M', 'V', 'B', 'U') for each edge.

  Returns:
      A tuple containing:
      - folded_vertices: New coordinates of vertices in folded state.
      - face_orientations: Boolean list where True indicates a face is
        flipped relative to face 0.
  """
  if not face_vertices:
    return [None] * len(vertices), []
  if len(face_vertices[0]) < 2:
    return [None] * len(vertices), [None] * len(face_vertices)

  assignment_map = {}
  for edge_index, edge in enumerate(edge_vertices):
    assignment_map[math_utils.encode_order_pair(edge)] = edge_assignments[
        edge_index
    ]

  edge_to_face_map: dict[tuple[int, ...], int] = {}
  for face_index, face in enumerate(face_vertices):
    for i, vertex1 in enumerate(face):
      vertex2 = face[(i + 1) % len(face)]
      edge_to_face_map[math_utils.list_to_tuple([vertex2, vertex1])] = (
          face_index
      )

  folded_vertices: list[Point | None] = [None] * len(vertices)
  seen_faces = {0}

  vertex1_on_face0, vertex2_on_face0 = (
      face_vertices[0][0],
      face_vertices[0][1],
  )
  folded_vertices[vertex1_on_face0] = vertices[vertex1_on_face0]
  folded_vertices[vertex2_on_face0] = vertices[vertex2_on_face0]

  face_orientations: list[bool | None] = [None] * len(face_vertices)

  queue: list[tuple[int, int, int, float, bool]] = [
      (0, vertex1_on_face0, vertex2_on_face0, float("inf"), True)
  ]
  queue_index = 0

  while queue_index < len(queue):
    face_index, point1_index, point2_index, _, is_face_up = queue[queue_index]
    face_orientations[face_index] = not is_face_up
    queue_index += 1

    face = face_vertices[face_index]
    point1, point2 = vertices[point1_index], vertices[point2_index]
    point1_folded, point2_folded = (
        folded_vertices[point1_index],
        folded_vertices[point2_index],
    )

    if point1_folded is None or point2_folded is None:
      raise ValueError("Folded vertex for face cannot be None.")

    x_axis = math_utils.unit_vector(math_utils.subtract(point2, point1))
    y_axis = math_utils.perpendicular_vector(x_axis)
    x_axis_folded = math_utils.unit_vector(
        math_utils.subtract(point2_folded, point1_folded)
    )
    y_axis_folded = math_utils.perpendicular_vector(x_axis_folded)

    vertex_prev = face[-1]
    for vertex_curr in face:
      if folded_vertices[vertex_curr] is None:
        vector = math_utils.subtract(vertices[vertex_curr], point1)
        dx = math_utils.multiply(
            x_axis_folded, math_utils.dot_product(vector, x_axis)
        )
        dy = math_utils.multiply(
            y_axis_folded,
            math_utils.dot_product(vector, y_axis) * (1 if is_face_up else -1),
        )
        folded_vertices[vertex_curr] = math_utils.add(
            math_utils.add(dx, dy), point1_folded
        )

      edge_length_squared = math_utils.distance_squared(
          vertices[vertex_prev], vertices[vertex_curr]
      )
      neighbor_face_index = edge_to_face_map.get(
          math_utils.list_to_tuple([vertex_prev, vertex_curr])
      )
      assignment = assignment_map.get(
          math_utils.encode_order_pair([vertex_prev, vertex_curr])
      )

      # Flip orientation if crossing a crease
      next_is_face_up = (
          not is_face_up if assignment in ["M", "V", "U"] else is_face_up
      )

      if (
          neighbor_face_index is not None
          and neighbor_face_index not in seen_faces
      ):
        queue.append((
            neighbor_face_index,
            vertex_curr,
            vertex_prev,
            edge_length_squared,
            next_is_face_up,
        ))
        seen_faces.add(neighbor_face_index)

      vertex_prev = vertex_curr

  return folded_vertices, face_orientations


def compute_segment_display_properties(
    cell_top_face: list[int | None],
    segment_cells: list[list[int]],
    segment_edges: list[list[int]],
    edge_faces: list[list[int | None]],
    face_orientations: list[bool],
) -> list[str]:
  """Computes segment display properties.

  Args:
    cell_top_face: For each cell, the index of the face that is on top.
    segment_cells: For each segment, list of cells it borders.
    segment_edges: For each segment, list of edges it contains.
    edge_faces: For each edge, list of faces it borders.
    face_orientations: For each face, its orientation.

  Returns:
    A list of display properties for each segment ('N', 'B', 'C', 'BL', 'BR').
  """
  edge_face_set = set()
  for faces in edge_faces:
    if len(faces) == 2:
      edge_face_set.add(math_utils.encode_order_pair(faces))

  segment_display_props = []
  for segment_index, cells in enumerate(segment_cells):
    faces = [cell_top_face[cell_index] for cell_index in cells]

    if len(faces) > 1 and faces[0] == faces[1]:
      segment_display_props.append("N")  # None
      continue

    if len(faces) < 2 or faces[0] is None or faces[1] is None:
      segment_display_props.append("B")  # Boundary
      continue

    flips = [face_orientations[face_index] for face_index in faces]  # pyrefly: ignore[bad-index]
    if (flips[0] == flips[1]) and (
        math_utils.encode_order_pair(faces) in edge_face_set
    ):
      segment_display_props.append("C")  # Crease
      continue

    left, right = False, False
    for edge_index in segment_edges[segment_index]:
      edge_face_list = edge_faces[edge_index]
      if len(edge_face_list) < 2:
        face1 = edge_face_list[0]
        face2 = None
      else:
        face1, face2 = edge_face_list

      orientation1 = face_orientations[face1] if face1 is not None else None
      orientation2 = face_orientations[face2] if face2 is not None else None

      if orientation1 == orientation2:
        continue

      if face1 == faces[0] or face2 == faces[0]:
        left = True
      if face1 == faces[1] or face2 == faces[1]:
        right = True

    if left == right:
      segment_display_props.append("B")
    else:
      segment_display_props.append("BL" if left else "BR")
  return segment_display_props


def compute_folded_regions(
    cell_top_face: list[int | None],
    cell_vertices: list[list[int]],
    segment_cells: list[list[int]],
    segment_display_props: list[str],
    face_orientations: list[bool],
    points: list[Point],
) -> tuple[list[list[int]], list[bool]]:
  """Computes folded regions for display.

  Regions are groups of cells that are connected and have the same top face.

  Args:
    cell_top_face: For each cell, the index of the face that is on top.
    cell_vertices: For each cell, list of vertex indices.
    segment_cells: For each segment, list of cells it borders.
    segment_display_props: Display properties for each segment.
    face_orientations: For each face, its orientation.
    points: List of vertex coordinates.

  Returns:
    A tuple containing:
    - region_polygons: A list of polygons, where each polygon is a list of
      vertex indices.
    - region_face_orientations: A list of face orientations for each region.
  """
  cell_count = len(cell_top_face)
  cell_connectivity = [[] for _ in range(cell_count)]
  for segment_index, cells in enumerate(segment_cells):
    if len(cells) != 2:
      continue
    display_prop = segment_display_props[segment_index]
    if display_prop and display_prop.startswith("B"):
      continue
    cell_index_i, cell_index_j = cells
    cell_connectivity[cell_index_i].append(cell_index_j)
    cell_connectivity[cell_index_j].append(cell_index_i)

  region_polygons = []
  region_face_orientations = []
  seen = [False] * cell_count

  for cell_index in range(cell_count):
    face_index = cell_top_face[cell_index]
    if face_index is None or seen[cell_index]:
      continue
    seen[cell_index] = True
    cell_group = [cell_index]
    cell_group_idx = 0
    while cell_group_idx < len(cell_group):
      current_cell = cell_group[cell_group_idx]
      cell_group_idx += 1
      for neighbor_cell in cell_connectivity[current_cell]:
        if not seen[neighbor_cell]:
          seen[neighbor_cell] = True
          cell_group.append(neighbor_cell)

    adjacency_sets = [set() for _ in points]
    for group_cell_index in cell_group:
      cell_points = cell_vertices[group_cell_index]
      prev_point_idx = cell_points[-1]
      for curr_point_idx in cell_points:
        adj_set = adjacency_sets[curr_point_idx]
        if prev_point_idx in adj_set:
          adj_set.remove(prev_point_idx)
        else:
          adjacency_sets[prev_point_idx].add(curr_point_idx)
        prev_point_idx = curr_point_idx

    start_node = -1
    for point_idx, adj_set in enumerate(adjacency_sets):
      if len(adj_set) == 1:
        start_node = point_idx
        break

    if start_node != -1:
      polygon_queue = []
      curr_path_node = start_node
      while True:
        polygon_queue.append(curr_path_node)
        if not adjacency_sets[curr_path_node]:
          break
        next_path_node = next(iter(adjacency_sets[curr_path_node]))
        adjacency_sets[curr_path_node].remove(next_path_node)
        curr_path_node = next_path_node
        if curr_path_node == start_node:
          break
      region_polygons.append(polygon_queue)
      region_face_orientations.append(face_orientations[face_index])

  return region_polygons, region_face_orientations
