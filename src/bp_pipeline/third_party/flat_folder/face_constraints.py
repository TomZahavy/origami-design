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

"""Face constraints utilities for flat-folder."""

import collections
import graphlib
from . import constraints
from . import logging
from . import math_utils

Point = math_utils.Point
Line = math_utils.Line
Edge = math_utils.Edge


def get_faces_in_contact_through_cells(
    face_index: int, face_cells: list[list[int]], cell_faces: list[list[int]]
) -> set[int]:
  """Returns faces that share any cell with the given face.

  Args:
    face_index: The index of the face to check.
    face_cells: A list where face_cells[i] contains cell indices for face i.
    cell_faces: A list where cell_faces[i] contains face indices for cell i.

  Returns:
    A set of face indices that share any cell with the given face.
  """
  faces_in_contact = set()
  for cell_index in face_cells[face_index]:
    for face in cell_faces[cell_index]:
      faces_in_contact.add(face)
  return faces_in_contact


def compute_cell_face_mappings(
    edge_faces: list[list[int | None]],
    face_vertices: list[list[int]],
    segment_vertices: list[Edge],
    segment_edges: list[list[int]],
    cell_vertices: list[list[int]],
    segment_cells: list[list[int]],
) -> tuple[list[list[int]], list[list[int]]]:
  """Computes mappings between cells and faces.

  Args:
    edge_faces: For each edge, list of faces it borders.
    face_vertices: For each face, list of vertex indices.
    segment_vertices: For each segment, list of vertex indices.
    segment_edges: For each segment, list of edges it contains.
    cell_vertices: For each cell, list of vertex indices.
    segment_cells: For each segment, list of cells it borders.

  Returns:
    A tuple containing:
    - cell_faces: A list where cell_faces[i] contains face indices for cell i.
    - face_cells: A list where face_cells[i] contains cell indices for face i.
  """
  segment_face_map = {}
  for segment_index, vertices in enumerate(segment_vertices):
    faces = []
    for edge_index in segment_edges[segment_index]:
      for face_index in edge_faces[edge_index]:
        if face_index is not None:
          faces.append(face_index)
    segment_face_map[math_utils.encode_order_pair(vertices)] = faces

  segment_cell_map = {}
  for cell_index, cell in enumerate(cell_vertices):
    vertex1 = cell[-1]
    for vertex2 in cell:
      segment_cell_map[math_utils.list_to_tuple([vertex2, vertex1])] = (
          cell_index
      )
      vertex1 = vertex2

  cell_faces: list[list[int]] = [[] for _ in cell_vertices]
  seen_cells = set()
  queue = []

  for segment_index, cells in enumerate(segment_cells):
    if len(cells) == 1:
      cell_index = cells[0]
      cell_faces[cell_index] = segment_face_map.get(
          math_utils.encode_order_pair(segment_vertices[segment_index]),
          [],
      )
      queue.append(cell_index)
      seen_cells.add(cell_index)
      break

  queue_index = 0
  while queue_index < len(queue):
    cell_index = queue[queue_index]
    queue_index += 1
    if cell_index >= len(cell_vertices):
      continue

    cell = cell_vertices[cell_index]
    vertex1 = cell[-1]
    for vertex2 in cell:
      neighbor_cell_index = segment_cell_map.get(
          math_utils.list_to_tuple([vertex1, vertex2])
      )
      if (
          neighbor_cell_index is not None
          and neighbor_cell_index not in seen_cells
      ):
        queue.append(neighbor_cell_index)
        seen_cells.add(neighbor_cell_index)
        faces_set = set(cell_faces[cell_index])
        key = math_utils.encode_order_pair([vertex1, vertex2])
        for face_index in segment_face_map.get(key, []):
          if face_index in faces_set:
            faces_set.remove(face_index)
          else:
            faces_set.add(face_index)
        cell_faces[neighbor_cell_index] = list(faces_set)
      vertex1 = vertex2

  face_cells_map: list[list[int]] = [[] for _ in face_vertices]
  for cell_index, faces in enumerate(cell_faces):
    faces.sort()
    for face_index in faces:
      face_cells_map[face_index].append(cell_index)

  return cell_faces, face_cells_map


def get_face_pairs_sharing_cells(
    cell_faces: list[list[int]],
) -> list[tuple[int, ...]]:
  """Returns pairs of faces that share cells.

  Args:
    cell_faces: A list where cell_faces[i] contains face indices for cell i.

  Returns:
    A list of face pairs that share cells.
  """
  face_pairs = set()
  logging.NOTE.start_check("cell", cell_faces)  # pyrefly: ignore[bad-argument-type]
  for cell_index, faces in enumerate(cell_faces):
    logging.NOTE.check(cell_index)
    for face1_idx, face1 in enumerate(faces):
      for face2_idx in range(face1_idx + 1, len(faces)):
        face2 = faces[face2_idx]
        face_pairs.add(math_utils.list_to_tuple([face1, face2]))
  return sorted(list(face_pairs))


def compute_transitive_face_pairs(
    edge_faces: list[list[int | None]],
    segment_vertices: list[Edge],
    segment_edges: list[list[int]],
    cell_vertices: list[list[int]],
    cell_faces: list[list[int]],
) -> list[tuple[int, int]]:
  """Computes transitive face pairs.

  Args:
    edge_faces: For each edge, list of faces it borders.
    segment_vertices: For each segment, list of vertex indices.
    segment_edges: For each segment, list of edges it contains.
    cell_vertices: For each cell, list of vertex indices.
    cell_faces: A list where cell_faces[i] contains face indices for cell i.

  Returns:
    A list of face pairs that are transitive.
  """
  segment_face_map = {}
  for segment_index, vertices in enumerate(segment_vertices):
    faces = []
    for edge_index in segment_edges[segment_index]:
      for face_index in edge_faces[edge_index]:
        if face_index is not None:
          faces.append(face_index)
    segment_face_map[math_utils.encode_order_pair(vertices)] = faces

  segment_cell_map = {}
  for cell_index, cell in enumerate(cell_vertices):
    vertex1 = cell[-1]
    for vertex2 in cell:
      segment_cell_map[math_utils.list_to_tuple([vertex2, vertex1])] = (
          cell_index
      )
      vertex1 = vertex2

  face_pairs = set()
  seen_cells = set()
  queue = [0]

  if cell_faces and cell_faces[0]:
    faces0 = cell_faces[0]
    for j_idx in range(1, len(faces0)):
      for i_idx in range(j_idx):
        face_pairs.add(
            math_utils.encode_order_pair([faces0[i_idx], faces0[j_idx]])
        )

  queue_index = 0
  cell_face_sets = [set(faces) for faces in cell_faces]

  while queue_index < len(queue):
    cell_index_i = queue[queue_index]
    queue_index += 1
    if cell_index_i >= len(cell_vertices):
      continue

    cell = cell_vertices[cell_index_i]
    vertex1 = cell[-1]
    for vertex2 in cell:
      cell_index_j = segment_cell_map.get(
          math_utils.list_to_tuple([vertex1, vertex2])
      )
      if cell_index_j is not None and cell_index_j not in seen_cells:
        queue.append(cell_index_j)
        seen_cells.add(cell_index_j)
        faces_i_set = cell_face_sets[cell_index_i]
        faces_j_set = cell_face_sets[cell_index_j]
        key = math_utils.encode_order_pair([vertex1, vertex2])

        for face_i in segment_face_map.get(key, []):
          if (face_i in faces_i_set) or (face_i not in faces_j_set):
            continue
          for face_j in faces_j_set:
            if face_i == face_j:
              continue
            face_pairs.add(math_utils.encode_order_pair([face_i, face_j]))
      vertex1 = vertex2

  return sorted(list(face_pairs))


def is_face_pair_overlapping(
    pair: list[int], face_pair_indices: dict[tuple[int, int], int]
) -> int:
  """Checks if a face pair is in the overlapping set.

  Args:
    pair: A list of two face indices.
    face_pair_indices: A dictionary mapping face pairs to indices.

  Returns:
    1 if the face pair is in the overlapping set, 0 otherwise.
  """
  return 1 if math_utils.encode_order_pair(pair) in face_pair_indices else 0


def add_constraint_to_table(
    constraint: tuple[int, list[int]] | None,
    face_pair_indices: dict[tuple[int, int], int],
    constraint_table: list[list[list[tuple[int, ...]]]],
) -> None:
  """Adds a constraint to constraint table.

  Args:
    constraint: A tuple of constraint type and faces, or None.
    face_pair_indices: A dictionary mapping face pairs to indices.
    constraint_table: The constraint table to add the constraint to.
  """
  if constraint is None:
    return
  type_id, faces = constraint
  pairs = constraints.Constraints.get_pairs_for_type(type_id, faces)
  for pair in pairs:
    pair_index = face_pair_indices.get(math_utils.encode_order_pair(pair))
    if pair_index is None:
      raise ValueError("Constraint variable missing")
    constraint_table[pair_index][type_id].append(
        math_utils.list_to_tuple(faces)
    )


def _fill_constraint_table_for_edge_edge_overlaps(
    constraint_table: list[list[list[tuple[int, ...]]]],
    face_pair_indices: dict[tuple[int, int], int],
    edge_faces: list[list[int | None]],
    segment_edges: list[list[int]],
) -> None:
  """Fills constraint table based on Edge-Edge overlaps.

  Args:
    constraint_table: The constraint table to fill.
    face_pair_indices: A dictionary mapping face pairs to indices.
    edge_faces: For each edge, list of faces it borders.
    segment_edges: For each segment, list of edges it contains.
  """
  edge_edge_segments = [set() for _ in edge_faces]
  for edges in segment_edges:
    for j_idx, edge1_index in enumerate(edges):
      for k_idx in range(j_idx + 1, len(edges)):
        edge2_index = edges[k_idx]
        index1, index2 = (
            (edge1_index, edge2_index)
            if edge1_index < edge2_index
            else (edge2_index, edge1_index)
        )
        edge_edge_segments[index1].add(index2)

  for edge1_index, mates in enumerate(edge_edge_segments):
    for edge2_index in mates:
      if len(edge_faces[edge1_index]) != 2 or len(edge_faces[edge2_index]) != 2:
        continue
      if (
          edge_faces[edge1_index][0] is None
          or edge_faces[edge1_index][1] is None
          or edge_faces[edge2_index][0] is None
          or edge_faces[edge2_index][1] is None
      ):
        continue
      face1, face2 = edge_faces[edge1_index]
      face3, face4 = edge_faces[edge2_index]
      is_face1_face2_overlapping = is_face_pair_overlapping(
          [face1, face2], face_pair_indices  # pyrefly: ignore[bad-argument-type]
      )
      is_face1_face3_overlapping = is_face_pair_overlapping(
          [face1, face3], face_pair_indices  # pyrefly: ignore[bad-argument-type]
      )
      is_face1_face4_overlapping = is_face_pair_overlapping(
          [face1, face4], face_pair_indices  # pyrefly: ignore[bad-argument-type]
      )

      choice = (
          (is_face1_face2_overlapping << 2)
          | (is_face1_face3_overlapping << 1)
          | is_face1_face4_overlapping
      )
      if choice == 4:
        continue

      constraint = None
      if choice == 0:
        constraint = (
            constraints.Constraints.Type.taco_tortilla,
            [face3, face4, face2],
        )
      elif choice == 1:
        constraint = (
            constraints.Constraints.Type.tortilla_tortilla,
            [face1, face2, face4, face3],
        )
      elif choice == 2:
        constraint = (
            constraints.Constraints.Type.tortilla_tortilla,
            [face1, face2, face3, face4],
        )
      elif choice == 3:
        constraint = (
            constraints.Constraints.Type.taco_tortilla,
            [face3, face4, face1],
        )
      elif choice == 5:
        constraint = (
            constraints.Constraints.Type.taco_tortilla,
            [face1, face2, face4],
        )
      elif choice == 6:
        constraint = (
            constraints.Constraints.Type.taco_tortilla,
            [face1, face2, face3],
        )
      elif choice == 7:
        constraint = (
            constraints.Constraints.Type.taco_taco,
            [face1, face2, face3, face4],
        )

      add_constraint_to_table(
          constraint, face_pair_indices, constraint_table  # pyrefly: ignore[bad-argument-type]
      )
    mates.clear()


def _fill_constraint_table_for_edge_face_overlaps(
    constraint_table: list[list[list[tuple[int, ...]]]],
    face_pair_indices: dict[tuple[int, int], int],
    edge_faces: list[list[int | None]],
    segment_edges: list[list[int]],
    cell_faces: list[list[int]],
    segment_cells: list[list[int]],
) -> None:
  """Fills constraint table based on Edge-Face overlaps.

  Args:
    constraint_table: The constraint table to fill.
    face_pair_indices: A dictionary mapping face pairs to indices.
    edge_faces: For each edge, list of faces it borders.
    segment_edges: For each segment, list of edges it contains.
    cell_faces: A list where cell_faces[i] contains face indices for cell i.
    segment_cells: For each segment, list of cells it borders.
  """
  edge_face_segments: list[set[int]] = [set() for _ in edge_faces]
  for segment_index, cells in enumerate(segment_cells):
    if len(cells) == 2:
      edges = segment_edges[segment_index]
      cell1_index, cell2_index = cells
      faces = []
      faces1 = set(cell_faces[cell1_index])
      for face_index in cell_faces[cell2_index]:
        if face_index in faces1:
          faces.append(face_index)
      for edge_index in edges:
        for face_index in faces:
          edge_face_segments[edge_index].add(face_index)

  for edge_index, faces in enumerate(edge_face_segments):
    for face3 in faces:
      if len(edge_faces[edge_index]) != 2:
        continue
      if edge_faces[edge_index][0] is None or edge_faces[edge_index][1] is None:
        continue
      face1, face2 = edge_faces[edge_index]
      if face1 == face3 or face2 == face3:
        continue
      is_face1_face2_overlapping = is_face_pair_overlapping(
          [face1, face2], face_pair_indices  # pyrefly: ignore[bad-argument-type]
      )
      if is_face1_face2_overlapping == 1:
        constraint = (
            constraints.Constraints.Type.taco_tortilla,
            [face1, face2, face3],
        )
      else:
        constraint = (
            constraints.Constraints.Type.tortilla_tortilla,
            [face1, face2, face3, face3],
        )
      add_constraint_to_table(
          constraint, face_pair_indices, constraint_table  # pyrefly: ignore[bad-argument-type]
      )
    faces.clear()


def build_face_pair_constraint_table(
    face_pairs: list[tuple[int, int]],
    face_pair_indices: dict[tuple[int, int], int],
    edge_faces: list[list[int | None]],
    segment_edges: list[list[int]],
    cell_faces: list[list[int]],
    segment_cells: list[list[int]],
) -> list[list[list[tuple[int, ...]]]]:
  """Builds face pair constraint table.

  Args:
    face_pairs: A list of face pairs.
    face_pair_indices: A dictionary mapping face pairs to indices.
    edge_faces: For each edge, list of faces it borders.
    segment_edges: For each segment, list of edges it contains.
    cell_faces: A list where cell_faces[i] contains face indices for cell i.
    segment_cells: For each segment, list of cells it borders.

  Returns:
    A constraint table for face pairs.
  """
  # Initialize with 4 slots to safely handle taco_taco (index 3)
  constraint_table: list[list[list[tuple[int, ...]]]] = [
      [[], [], [], []] for _ in face_pairs
  ]
  _fill_constraint_table_for_edge_edge_overlaps(
      constraint_table, face_pair_indices, edge_faces, segment_edges
  )
  _fill_constraint_table_for_edge_face_overlaps(
      constraint_table,
      face_pair_indices,
      edge_faces,
      segment_edges,
      cell_faces,
      segment_cells,
  )
  return constraint_table


def build_face_graph_components(
    face_cells: list[list[int]],
    face_pair_constraints: list[list[list[tuple[int, ...]]]],
) -> list[dict[int, int]]:
  """Builds face connectivity components based on taco-tortilla constraints.

  Args:
      face_cells: A list where face_cells[i] contains cell indices for face i.
      face_pair_constraints: A table where face_pair_constraints[i] lists
        constraints for face pair i.

  Returns:
      A list of dictionaries, where each dictionary maps face indices to
      a component ID for a given face graph.
  """
  face_graphs = [collections.defaultdict(set) for _ in face_cells]

  for _, constraint_list in enumerate(face_pair_constraints):
    for encoded_faces in constraint_list[
        constraints.Constraints.Type.taco_tortilla
    ]:
      face1, face2, face3 = math_utils.tuple_to_list(encoded_faces)
      face_graphs[face3][face1].add(face2)
      face_graphs[face3][face2].add(face1)

  components_list = []
  for _, graph in enumerate(face_graphs):
    components: dict[int, int] = {}
    component_id = 0
    for face_index in graph:
      if face_index in components:
        continue
      queue = [face_index]
      components[face_index] = component_id
      head = 0
      while head < len(queue):
        current_face_index = queue[head]
        head += 1
        if current_face_index in graph:
          for neighbor in graph[current_face_index]:
            if neighbor not in components:
              queue.append(neighbor)
              components[neighbor] = component_id
      component_id += 1
    components_list.append(components)
  return components_list


def get_transitive_face_triplets(
    face_cells: list[list[int]],
    cell_faces: list[list[int]],
    face_components: list[dict[int, int]],
    pair: list[int],
    trans_count: dict[str, int] | None = None,
) -> list[int]:
  """Gets transitive face triplets.

  Args:
    face_cells: A list where face_cells[i] contains cell indices for face i.
    cell_faces: A list where cell_faces[i] contains face indices for cell i.
    face_components: A list of dictionaries, where each dictionary maps face
      indices to a component ID for a given face graph.
    pair: A list of two face indices.
    trans_count: An optional dictionary to count transitivity checks.

  Returns:
    A list of face indices that form transitive triplets with the given pair.
  """
  face1, face2 = pair
  cells1 = face_cells[face1]
  cells2 = face_cells[face2]
  if len(cells1) < len(cells2):
    cells_set = set(cells1)
    iter_cells = cells2
  else:
    cells_set = set(cells2)
    iter_cells = cells1
  triplets = set()
  for cell_index in iter_cells:
    if cell_index in cells_set:
      triplets.update(cell_faces[cell_index])
  triplets.discard(face1)
  triplets.discard(face2)

  if trans_count:
    trans_count["all"] += len(triplets)

  components_face1 = face_components[face1]
  components_face2 = face_components[face2]
  face2_comp_in_face1_graph = components_face1.get(face2)
  face1_comp_in_face2_graph = components_face2.get(face1)

  output = []
  for face3 in triplets:
    if (
        face2_comp_in_face1_graph is not None
        and face2_comp_in_face1_graph == components_face1.get(face3)
    ):
      continue
    if (
        face1_comp_in_face2_graph is not None
        and face1_comp_in_face2_graph == components_face2.get(face3)
    ):
      continue
    components_face3 = face_components[face3]
    face1_comp_in_face3_graph = components_face3.get(face1)
    if (
        face1_comp_in_face3_graph is not None
        and face1_comp_in_face3_graph == components_face3.get(face2)
    ):
      continue
    output.append(face3)

  if trans_count:
    trans_count["reduced"] += len(output)
  return output


def get_ordered_face_pairs_from_assignments(
    face_pairs: list[tuple[int, int]],
    grouped_assignments: list[list[int]],
    assignment_groups: list[list[tuple[int, ...]]],
    group_indices: list[int],
) -> list[tuple[int, ...]]:
  """Gets ordered face pairs from assignments.

  Args:
    face_pairs: A list of face pairs.
    grouped_assignments: A list of grouped assignments.
    assignment_groups: A list of assignment groups.
    group_indices: A list of group indices.

  Returns:
    A list of ordered face pairs.
  """
  edges = []
  for group_index, group in enumerate(grouped_assignments):
    if group_index >= len(assignment_groups) or group_indices[
        group_index
    ] >= len(assignment_groups[group_index]):
      continue
    orders = math_utils.tuple_to_list(
        assignment_groups[group_index][group_indices[group_index]]
    )
    for pair_list_index, face_pair_index in enumerate(group):
      face1, face2 = math_utils.tuple_to_list(face_pairs[face_pair_index])
      order = orders[pair_list_index]
      edges.append(
          math_utils.list_to_tuple(
              [face1, face2] if order == 1 else [face2, face1]
          )
      )
  return edges


def sort_faces_in_cells_by_order(
    cell_faces: list[list[int]], order_edges: list[tuple[int, ...]]
) -> list[list[int]]:
  """Sorts faces in cells by order.

  Args:
    cell_faces: A list where cell_faces[i] contains face indices for cell i.
    order_edges: A list of face pairs (top, bottom).

  Returns:
    A list of lists of face indices, where each inner list is sorted by
    stacking order.
  """
  edge_set = set(order_edges)
  cell_faces_ordered = []

  for faces in cell_faces:
    ts = graphlib.TopologicalSorter()
    for face in faces:
      ts.add(face)

    n = len(faces)
    for i in range(n):
      for j in range(i + 1, n):
        face1 = faces[i]
        face2 = faces[j]
        if (face1, face2) in edge_set:
          ts.add(face1, face2)
        elif (face2, face1) in edge_set:
          ts.add(face2, face1)

    try:
      cell_faces_ordered.append(list(ts.static_order()))
    except graphlib.CycleError:
      cell_faces_ordered.append(sorted(faces))

  return cell_faces_ordered
