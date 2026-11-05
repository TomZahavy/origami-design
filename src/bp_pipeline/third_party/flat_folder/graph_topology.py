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

"""Graph topology utilities for flat-folder."""

from . import math_utils

Point = math_utils.Point
Edge = math_utils.Edge


def graph_to_adjacency_and_faces(
    vertices: list[Point], edge_vertices: list[Edge]
) -> tuple[list[list[int]], list[list[int]]]:
  """Computes vertex adjacencies and faces from graph vertices and edges.

  Adjacency lists are sorted by angle around each vertex. Faces are
  calculated by traversing edges, and the outermost face is removed.

  Args:
      vertices: List of vertex coordinates.
      edge_vertices: List of edges defined by vertex indices.

  Returns:
      A tuple containing:
      - vertex_adjacencies: List of adjacency lists for each vertex,
        sorted by angle.
      - face_vertices: List of faces, where each face is a list of
        vertex indices.
  """
  adjacency_list = [[] for _ in range(len(vertices))]
  for vertex1_index, vertex2_index in edge_vertices:
    adjacency_list[vertex1_index].append(vertex2_index)
    adjacency_list[vertex2_index].append(vertex1_index)

  vertex_adjacencies = []
  for vertex_index, vertex in enumerate(vertices):
    angles = []
    for neighbor_index in adjacency_list[vertex_index]:
      diff = math_utils.subtract(vertices[neighbor_index], vertex)
      angles.append([neighbor_index, math_utils.angle(diff)])
    angles.sort(key=lambda x: x[1])
    vertex_adjacencies.append([x[0] for x in angles])

  face_vertices = []
  seen = set()
  for vertex1, neighbors in enumerate(vertex_adjacencies):
    for vertex2 in neighbors:
      key = math_utils.list_to_tuple([vertex1, vertex2])
      if key not in seen:
        seen.add(key)
        face = [vertex1]
        current_vertex_index, next_vertex_index = vertex1, vertex2
        while next_vertex_index != vertex1:
          face.append(next_vertex_index)  # pyrefly: ignore[bad-argument-type]
          prev_neighbor_index = math_utils.previous_in_list(
              vertex_adjacencies[next_vertex_index], current_vertex_index  # pyrefly: ignore[bad-index]
          )
          seen.add(
              math_utils.list_to_tuple([next_vertex_index, prev_neighbor_index])
          )
          current_vertex_index, next_vertex_index = (
              next_vertex_index,
              prev_neighbor_index,
          )
        if len(face) > 2:
          face_vertices.append(face)

  math_utils.sort_faces(face_vertices, vertices)
  if face_vertices:
    face_vertices.pop()  # remove outer face
  return vertex_adjacencies, face_vertices


def faces_to_adjacency(
    vertices: list[Point], face_vertices: list[list[int]]
) -> list[list[int]]:
  """Computes angularly sorted vertex adjacencies from faces.

  Args:
      vertices: List of vertex coordinates.
      face_vertices: List of faces, where each face is a list of vertex indices
        in order.

  Returns:
      List of adjacency lists for each vertex, sorted by angle.
  """
  next_neighbor = [dict() for _ in range(len(vertices))]
  prev_neighbor = [dict() for _ in range(len(vertices))]
  for _, face in enumerate(face_vertices):
    v_prev_on_face, v_curr_on_face = face[-2], face[-1]
    for v_next_on_face in face:
      next_neighbor[v_curr_on_face][v_prev_on_face] = v_next_on_face
      prev_neighbor[v_curr_on_face][v_next_on_face] = v_prev_on_face
      v_prev_on_face, v_curr_on_face = v_curr_on_face, v_next_on_face

  vertex_adjacencies: list[list[int]] = [[] for _ in range(len(vertices))]
  for vertex_index, adjacency in enumerate(vertex_adjacencies):
    if not next_neighbor[vertex_index]:
      continue

    # Find first neighbor in angular order to start iteration
    start_neighbor_candidate = next(iter(next_neighbor[vertex_index]))
    current_neighbor = start_neighbor_candidate
    prev_neighbor_candidate = prev_neighbor[vertex_index].get(
        start_neighbor_candidate
    )
    while (
        prev_neighbor_candidate is not None
        and prev_neighbor_candidate != start_neighbor_candidate
    ):
      current_neighbor = prev_neighbor_candidate
      prev_neighbor_candidate = prev_neighbor[vertex_index].get(
          current_neighbor
      )

    start_neighbor = current_neighbor
    adjacency.append(start_neighbor)
    current_neighbor = next_neighbor[vertex_index].get(current_neighbor)
    while current_neighbor is not None and current_neighbor != start_neighbor:
      adjacency.append(current_neighbor)
      current_neighbor = next_neighbor[vertex_index].get(current_neighbor)
  return vertex_adjacencies


def build_edge_face_maps(
    edge_vertices: list[Edge], face_vertices: list[list[int]]
) -> tuple[list[list[int]], list[list[int | None]]]:
  """Builds edge-to-face and face-to-edge mappings.

  Args:
      edge_vertices: List of edges defined by vertex indices.
      face_vertices: List of faces, where each face is a list of vertex indices.

  Returns:
      A tuple containing:
      - edge_faces: A list where edge_faces[i] is a list of faces
        incident to edge i. Edges on boundary have one face.
      - face_edges: A list where face_edges[i] is a list of edge
        indices that make up face i.
  """
  edge_index_map = {
      math_utils.encode_order_pair(edge): i
      for i, edge in enumerate(edge_vertices)
  }
  edge_faces_pairs: list[list[int | None]] = [
      [None, None] for _ in edge_vertices
  ]

  for face_index, face in enumerate(face_vertices):
    for vertex_index_in_face, vertex1 in enumerate(face):
      vertex2 = face[(vertex_index_in_face + 1) % len(face)]
      edge_index = edge_index_map.get(
          math_utils.encode_order_pair([vertex1, vertex2])
      )
      if edge_index is not None:
        slot = 0 if vertex2 < vertex1 else 1
        edge_faces_pairs[edge_index][slot] = face_index

  edge_faces: list[list[int]] = []
  for face_pair in edge_faces_pairs:
    faces = [face_index for face_index in face_pair if face_index is not None]
    edge_faces.append(faces)

  face_edges: list[list[int | None]] = []
  for face in face_vertices:
    edges: list[int | None] = []
    vertex1 = face[-1]
    for vertex2 in face:
      edges.append(
          edge_index_map.get(math_utils.encode_order_pair([vertex1, vertex2]))
      )
      vertex1 = vertex2
    face_edges.append(edges)

  return edge_faces, face_edges
