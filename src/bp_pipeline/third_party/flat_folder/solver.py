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

"""Solver for flat-folding crease patterns."""

from . import constraints
from . import face_constraints
from . import logging
from . import math_utils

FacePair = tuple[int, int]
FacePairKey = tuple[int, int]
Assignment = int  # 0: undecided, 1: order1, 2: order2
Implication = tuple[int, Assignment]  # face_pair_index, assignment
ConstraintFaceIndices = list[int]

# Global flip table for reverse face pair ordering (when y < x).
_FLIP_REV = (0, 2, 1)


def infer_implications(
    constraint_type_id: int,
    faces: ConstraintFaceIndices,
    face_pair_to_index: dict[FacePairKey, int],
    assignments: list[Assignment],
) -> list[Implication] | int | None:
  """Infers implied assignments from a single constraint.

  Args:
    constraint_type_id: The type of constraint being checked.
    faces: A list of face indices involved in the constraint.
    face_pair_to_index: A map from face pairs to variable indices.
    assignments: The current list of variable assignments.

  Returns:
    Constraints.State.conflict if assignments conflict with the constraint,
    Constraints.State.dead or Constraints.State.alive if no implications
    can be drawn, or a list of implied assignments [face_pair_idx,
    assignment],
    or None if face pair not found.
  """
  int_tables = constraints.Constraints.IMPLIED_STATES_INT
  if not int_tables:
    constraints.Constraints.build_implication_tables()
    int_tables = constraints.Constraints.IMPLIED_STATES_INT

  if constraint_type_id == 3:
    f0, f1, f2 = faces[0], faces[1], faces[2]
    if f1 < f0:
      idx0 = face_pair_to_index[(f1, f0)]
      a0 = _FLIP_REV[assignments[idx0]]
      flip0 = True
    else:
      idx0 = face_pair_to_index[(f0, f1)]
      a0 = assignments[idx0]
      flip0 = False
    if f2 < f1:
      idx1 = face_pair_to_index[(f2, f1)]
      a1 = _FLIP_REV[assignments[idx1]]
      flip1 = True
    else:
      idx1 = face_pair_to_index[(f1, f2)]
      a1 = assignments[idx1]
      flip1 = False
    if f0 < f2:
      idx2 = face_pair_to_index[(f0, f2)]
      a2 = _FLIP_REV[assignments[idx2]]
      flip2 = True
    else:
      idx2 = face_pair_to_index[(f2, f0)]
      a2 = assignments[idx2]
      flip2 = False
    implications = int_tables[3][a0 + 3 * a1 + 9 * a2]
    if not isinstance(implications, list):
      return implications
    idxs = (idx0, idx1, idx2)
    flips = (flip0, flip1, flip2)
    return [
        (idxs[i], _FLIP_REV[val] if flips[i] else val)
        for i, val in implications
    ]

  if constraint_type_id == 1:
    f0, f1, f2 = faces[0], faces[1], faces[2]
    if f2 < f0:
      idx0 = face_pair_to_index[(f2, f0)]
      a0 = _FLIP_REV[assignments[idx0]]
      flip0 = True
    else:
      idx0 = face_pair_to_index[(f0, f2)]
      a0 = assignments[idx0]
      flip0 = False
    if f1 < f2:
      idx1 = face_pair_to_index[(f1, f2)]
      a1 = _FLIP_REV[assignments[idx1]]
      flip1 = True
    else:
      idx1 = face_pair_to_index[(f2, f1)]
      a1 = assignments[idx1]
      flip1 = False
    implications = int_tables[1][a0 + 3 * a1]
    if not isinstance(implications, list):
      return implications
    idxs = (idx0, idx1)
    flips = (flip0, flip1)
    return [
        (idxs[i], _FLIP_REV[val] if flips[i] else val)
        for i, val in implications
    ]

  if constraint_type_id == 2:
    f0, f1, f2, f3 = faces[0], faces[1], faces[2], faces[3]
    if f2 < f0:
      idx0 = face_pair_to_index[(f2, f0)]
      a0 = _FLIP_REV[assignments[idx0]]
      flip0 = True
    else:
      idx0 = face_pair_to_index[(f0, f2)]
      a0 = assignments[idx0]
      flip0 = False
    if f3 < f1:
      idx1 = face_pair_to_index[(f3, f1)]
      a1 = _FLIP_REV[assignments[idx1]]
      flip1 = True
    else:
      idx1 = face_pair_to_index[(f1, f3)]
      a1 = assignments[idx1]
      flip1 = False
    implications = int_tables[2][a0 + 3 * a1]
    if not isinstance(implications, list):
      return implications
    idxs = (idx0, idx1)
    flips = (flip0, flip1)
    return [
        (idxs[i], _FLIP_REV[val] if flips[i] else val)
        for i, val in implications
    ]

  pairs = constraints.Constraints.get_pairs_for_type(constraint_type_id, faces)
  state_idx = 0
  mul = 1
  for x, y in pairs:
    if y < x:
      face_pair_idx = face_pair_to_index[(y, x)]
      val = _FLIP_REV[assignments[face_pair_idx]]
    else:
      face_pair_idx = face_pair_to_index[(x, y)]
      val = assignments[face_pair_idx]
    state_idx += val * mul
    mul *= 3

  implications = int_tables[constraint_type_id][state_idx]
  if not isinstance(implications, list):
    return implications

  res = []
  for i, assignment_value in implications:
    x, y = pairs[i]
    face_pair_idx = face_pair_to_index.get((y, x) if y < x else (x, y))
    if face_pair_idx is not None:
      res.append((
          face_pair_idx,
          _FLIP_REV[assignment_value] if y < x else assignment_value,
      ))
  return res


def propagate_assignment(
    face_pair_idx: int,
    assignment_value: Assignment,
    face_pair_to_index: dict[FacePairKey, int],
    face_pairs: list[FacePair],
    constraint_table: list[list[list[tuple[int, ...]]]],
    assignments: list[Assignment],
    face_cells: list[list[int]],
    cell_faces: list[list[int]],
    face_components: list[dict[int, int]],
) -> list[int]:
  """Propagates an assignment through constraints.

  Args:
    face_pair_idx: The index of the face pair being assigned.
    assignment_value: The assignment value (1 or 2).
    face_pair_to_index: Map from face pair to index in assignments array.
    face_pairs: List of face pairs corresponding to assignments.
    constraint_table: Table of constraints for each face pair.
    assignments: Array of current assignments.
    face_cells: For each face, list of cells it belongs to.
    cell_faces: For each cell, list of faces it contains.
    face_components: Face connectivity components for transitivity.

  Returns:
    A list of face pair indices that were assigned during propagation, or
    an empty list if a conflict was detected.
  """
  propagation_queue = [face_pair_idx]
  assignments[face_pair_idx] = assignment_value
  idx = 0
  while idx < len(propagation_queue):
    current_face_pair_idx = propagation_queue[idx]
    f1, f2 = face_pairs[current_face_pair_idx]
    constraints_for_pair = constraint_table[current_face_pair_idx]
    for type_id in constraints.Constraints.types:
      constraint_face_list = unpack_constraints(
          constraints_for_pair,
          type_id,
          f1,
          f2,
          face_cells,
          cell_faces,
          face_components,
      )
      for faces in constraint_face_list:
        implications = infer_implications(
            type_id, faces, face_pair_to_index, assignments
        )
        if implications == constraints.Constraints.State.conflict:
          for i in propagation_queue:
            assignments[i] = 0
          return []

        if not isinstance(implications, list):
          continue

        for implied_idx, implied_assignment in implications:
          if assignments[implied_idx] == 0:
            propagation_queue.append(implied_idx)
            assignments[implied_idx] = implied_assignment
          elif assignments[implied_idx] != implied_assignment:
            for i in propagation_queue:
              assignments[i] = 0
            return []
      if type_id == constraints.Constraints.Type.transitivity:
        break
    idx += 1
  return propagation_queue


def get_assignment_components(
    face_pair_to_index: dict[FacePairKey, int],
    face_pairs: list[FacePair],
    constraint_table: list[list[list[tuple[int, ...]]]],
    assignments: list[Assignment],
    face_cells: list[list[int]],
    cell_faces: list[list[int]],
    face_components: list[dict[int, int]],
    trans_count: dict[str, int],
) -> list[list[int]]:
  """Gets connected components of unassigned variables.

  Args:
    face_pair_to_index: Map from face pair to index in assignments array.
    face_pairs: List of face pairs corresponding to assignments.
    constraint_table: Table of constraints for each face pair.
    assignments: Array of current assignments.
    face_cells: For each face, list of cells it belongs to.
    cell_faces: For each cell, list of faces it contains.
    face_components: Face connectivity components for transitivity.
    trans_count: Dictionary to count transitivity checks.

  Returns:
    A list of components, where each component is a list of face pair indices.
  """
  initially_assigned_pairs = [
      i for i, assignment in enumerate(assignments) if assignment != 0
  ]
  components = []
  seen = set()

  logging.NOTE.start_check("variable", face_pairs)  # pyrefly: ignore[bad-argument-type]
  for face_pair_idx, assignment in enumerate(assignments):
    if (face_pair_idx not in seen) and (assignment == 0):
      stack = [face_pair_idx]
      seen.add(face_pair_idx)
      stack_idx = 0
      while stack_idx < len(stack):
        current_face_pair_idx = stack[stack_idx]
        constraints_for_pair = constraint_table[current_face_pair_idx]
        f1, f2 = face_pairs[current_face_pair_idx]
        for type_id in constraints.Constraints.types:
          constraint_face_list = unpack_constraints(
              constraints_for_pair,
              type_id,
              f1,
              f2,
              face_cells,
              cell_faces,
              face_components,
              trans_count,
          )
          for faces in constraint_face_list:
            implications = infer_implications(
                type_id, faces, face_pair_to_index, assignments
            )
            if implications == constraints.Constraints.State.dead:
              continue

            pairs_in_constraint = [
                math_utils.encode_order_pair(p)
                for p in constraints.Constraints.get_pairs_for_type(
                    type_id, faces
                )
            ]
            for key in pairs_in_constraint:
              idx = face_pair_to_index.get(key)
              if idx is not None and idx not in seen and assignments[idx] == 0:
                stack.append(idx)
                seen.add(idx)
              logging.NOTE.check(len(seen))
          if type_id == constraints.Constraints.Type.transitivity:
            break
        stack_idx += 1
      components.append(stack)

  components.sort(key=len)
  components.insert(0, initially_assigned_pairs)
  return components


def unpack_constraints(
    constraints_for_pair: list[list[tuple[int, ...]]],
    constraint_type_id: int,
    f1: int,
    f2: int,
    face_cells: list[list[int]],
    cell_faces: list[list[int]],
    face_components: list[dict[int, int]],
    trans_count: dict[str, int] | None = None,
) -> list[ConstraintFaceIndices]:
  """Unpacks constraints of a given type for a face pair.

  Args:
    constraints_for_pair: Constraints associated with a face pair.
    constraint_type_id: The type of constraint to unpack.
    f1: First face in pair.
    f2: Second face in pair.
    face_cells: For each face, list of cells it belongs to.
    cell_faces: For each cell, list of faces it contains.
    face_components: Face connectivity components for transitivity.
    trans_count: Optional dictionary to count transitivity checks.

  Returns:
    A list of face lists, each defining an instance of the constraint.
  """
  if constraint_type_id == constraints.Constraints.Type.transitivity:
    if trans_count is None and constraints_for_pair[3]:
      return constraints_for_pair[3]  # pyrefly: ignore[bad-return]
    res = [
        [f1, f2, f3]
        for f3 in face_constraints.get_transitive_face_triplets(
            face_cells, cell_faces, face_components, [f1, f2], trans_count
        )
    ]
    constraints_for_pair[3] = res  # pyrefly: ignore[bad-assignment]
    return res
  return [
      math_utils.tuple_to_list(k)
      for k in constraints_for_pair[constraint_type_id]
  ]


def solve_component_by_guessing(
    component: list[int],
    face_pair_to_index: dict[FacePairKey, int],
    face_pairs: list[FacePair],
    constraint_table: list[list[list[tuple[int, ...]]]],
    assignments: list[Assignment],
    face_cells: list[list[int]],
    cell_faces: list[list[int]],
    face_components: list[dict[int, int]],
    solution_limit: int,
) -> list[tuple[int, ...]]:
  """Solves for assignments in a component using guessing and backtracking.

  Args:
    component: List of face pair indices in this component to solve.
    face_pair_to_index: Map from face pair to index in assignments array.
    face_pairs: List of face pairs corresponding to assignments.
    constraint_table: Table of constraints for each face pair.
    assignments: Array of current assignments (mutable).
    face_cells: For each face, list of cells it belongs to.
    cell_faces: For each cell, list of faces it contains.
    face_components: Face connectivity components for transitivity.
    solution_limit: Maximum number of solutions to find.

  Returns:
    A list of solutions, each encoded via MathUtils.bit_encode.
  """
  guesses_stack = []
  solutions = []
  solution = [0] * len(component)
  idx = 0
  backtracking = False

  logging.NOTE.start_check("state")
  while True:
    logging.NOTE.check(len(solutions))
    if backtracking:
      if not guesses_stack:
        break
      last_guess_propagations = guesses_stack.pop()
      assignment_at_guess = assignments[last_guess_propagations[0]]

      while component[idx] != last_guess_propagations[0]:
        idx -= 1

      for i in last_guess_propagations:
        assignments[i] = 0

      if assignment_at_guess == 1:
        propagated_indices = propagate_assignment(
            component[idx],
            2,
            face_pair_to_index,
            face_pairs,
            constraint_table,
            assignments,
            face_cells,
            cell_faces,
            face_components,
        )
        if propagated_indices:
          guesses_stack.append(propagated_indices)
          backtracking = False
          idx += 1
        else:
          guesses_stack.append([component[idx]])
          assignments[component[idx]] = 2
    else:
      if idx == len(component):
        for i, comp_idx in enumerate(component):
          solution[i] = assignments[comp_idx]
        solutions.append(math_utils.list_to_tuple(solution))
        if len(solutions) >= solution_limit:
          return solutions
        backtracking = True
      else:
        if assignments[component[idx]] == 0:
          propagated_indices = propagate_assignment(
              component[idx],
              1,
              face_pair_to_index,
              face_pairs,
              constraint_table,
              assignments,
              face_cells,
              cell_faces,
              face_components,
          )
          if propagated_indices:
            guesses_stack.append(propagated_indices)
          else:
            guesses_stack.append([component[idx]])
            assignments[component[idx]] = 1
            backtracking = True
        idx += 1
  return solutions


def get_initial_assignments_from_creases(
    edge_faces: list[list[int]],
    edge_assignments: list[str],
    face_orientations: list[bool],
    face_pairs: list[FacePair],
    face_pair_to_index: dict[FacePairKey, int],
) -> list[Assignment]:
  """Computes initial face pair assignments from crease pattern M/V assignments.

  Args:
    edge_faces: For each edge, list of incident faces.
    edge_assignments: Assignment for each edge ('M', 'V', 'B', etc.).
    face_orientations: Orientation for each face (True if flipped).
    face_pairs: List of face pairs whose order needs to be determined.
    face_pair_to_index: Map from face pair to its index in assignments array.

  Returns:
    An initial list of assignments based on M/V creases.
  """
  initial_assignments = [0] * len(face_pairs)
  for i, assignment in enumerate(edge_assignments):
    if assignment == "M" or assignment == "V":
      face_pair_key = math_utils.encode_order_pair(edge_faces[i])
      f1, _ = math_utils.tuple_to_list(face_pair_key)
      # Assignment 1 means f1 < f2, 2 means f2 < f1 in stacking order.
      # If face f1 is oriented upwards (!Ff[f1]) and crease is 'M',
      # or face f1 is oriented downwards (Ff[f1]) and crease is 'V',
      # then f2 is below f1.
      if (not face_orientations[f1] and assignment == "M") or (
          face_orientations[f1] and assignment == "V"
      ):
        order = 2
      else:
        order = 1
      idx = face_pair_to_index.get(face_pair_key)
      if idx is not None:
        initial_assignments[idx] = order
  return initial_assignments


def propagate_initial_assignments(
    assignments: list[Assignment],
    face_pairs: list[FacePair],
    constraint_table: list[list[list[tuple[int, ...]]]],
    face_pair_to_index: dict[FacePairKey, int],
    face_cells: list[list[int]],
    cell_faces: list[list[int]],
    face_components: list[dict[int, int]],
    trans_count: dict[str, int],
) -> list[Assignment] | list[int | ConstraintFaceIndices]:
  """Propagates initial assignments and detects conflicts.

  Args:
    assignments: Initial assignments array (mutable).
    face_pairs: List of face pairs corresponding to assignments.
    constraint_table: Table of constraints for each face pair.
    face_pair_to_index: Map from face pair to index in assignments array.
    face_cells: For each face, list of cells it belongs to.
    cell_faces: For each cell, list of faces it contains.
    face_components: Face connectivity components for transitivity.
    trans_count: Dictionary to count transitivity checks.

  Returns:
    The array of assignments after propagation, or if a conflict is found,
    a list [constraint_type_id, faces, error_faces_list] describing
    the conflict.
  """
  assignment_provenance: list[list[int] | None] = [None] * len(assignments)
  level: dict[int, Assignment] = {}
  new_level: dict[int, Assignment] = {}

  for i, assignment in enumerate(assignments):
    if assignment != 0:
      level[i] = assignment
      assignment_provenance[i] = []

  count = 0
  depth = 0

  logging.NOTE.start_check("variable", assignments)  # pyrefly: ignore[bad-argument-type]
  while level:
    logging.NOTE.log(f"   - {len(level)} orders assigned at depth {depth}")
    for i, assignment in level.items():
      assignments[i] = assignment
    new_level.clear()

    for i, _ in level.items():
      logging.NOTE.check(count)
      count += 1
      f1, f2 = face_pairs[i]
      constraints_for_pair = constraint_table[i]
      for type_id in constraints.Constraints.types:
        constraint_face_list = unpack_constraints(
            constraints_for_pair,
            type_id,
            f1,
            f2,
            face_cells,
            cell_faces,
            face_components,
            trans_count,
        )
        for ci, faces in enumerate(constraint_face_list):
          implications = infer_implications(
              type_id, faces, face_pair_to_index, assignments
          )
          if implications == constraints.Constraints.State.conflict:
            error_faces_list = get_conflict_faces(
                type_id,
                faces,
                face_pairs,
                constraint_table,
                face_pair_to_index,
                assignments,
                assignment_provenance,
                face_cells,
                cell_faces,
                face_components,
            )
            return [type_id, faces, error_faces_list]

          if implications in [
              constraints.Constraints.State.alive,
              constraints.Constraints.State.dead,
          ]:
            continue

          for i_, a_ in implications:  # pyrefly: ignore[not-iterable]
            a__ = new_level.get(i_)
            if a__ is None:
              assignment_provenance[i_] = [type_id, i, ci]
              new_level[i_] = a_
            elif a_ != a__:
              # Conflict detected in current level propagation
              error_faces_list = get_conflict_faces(
                  type_id,
                  faces,
                  face_pairs,
                  constraint_table,
                  face_pair_to_index,
                  assignments,
                  assignment_provenance,
                  face_cells,
                  cell_faces,
                  face_components,
              )
              return [type_id, faces, error_faces_list]

        if type_id == constraints.Constraints.Type.transitivity:
          break

    level = new_level
    new_level = {}
    depth += 1

  return assignments


def solve_all_components(
    face_pair_to_index: dict[FacePairKey, int],
    face_pairs: list[FacePair],
    constraint_table: list[list[list[tuple[int, ...]]]],
    assignments: list[Assignment],
    components: list[list[int]],
    face_cells: list[list[int]],
    cell_faces: list[list[int]],
    face_components: list[dict[int, int]],
    solution_limit: int,
) -> list[list[tuple[int, ...]]] | int:
  """Solves for flat-folding states by iterating through components.

  Args:
    face_pair_to_index: Map from face pair to index in assignments array.
    face_pairs: List of face pairs corresponding to assignments.
    constraint_table: Table of constraints for each face pair.
    assignments: Array of current assignments.
    components: List of components, each a list of face pair indices.
    face_cells: For each face, list of cells it belongs to.
    cell_faces: For each cell, list of faces it contains.
    face_components: Face connectivity components for transitivity.
    solution_limit: Max number of solutions to find for each component.

  Returns:
    A list where each element contains solutions for a component, or an
    integer indicating index of component that failed to solve.
  """
  initially_assigned_pairs = [i for i, v in enumerate(assignments) if v != 0]
  all_solutions = [[
      math_utils.list_to_tuple(
          [assignments[i] for i in initially_assigned_pairs]
      )
  ]]

  for i, component in enumerate(components):
    if i == 0:
      continue
    logging.NOTE.time(
        f"Solving component {i}/{len(components)-1} with size {len(component)}"
    )
    component_solutions = solve_component_by_guessing(
        component,
        face_pair_to_index,
        face_pairs,
        constraint_table,
        assignments,
        face_cells,
        cell_faces,
        face_components,
        solution_limit,
    )
    logging.NOTE.count(len(component_solutions), "assignments")
    if not component_solutions:
      return i  # Return index of failing component
    all_solutions.append(component_solutions)
  return all_solutions


def get_conflict_faces(
    constraint_type_id: int,
    faces: ConstraintFaceIndices,
    face_pairs: list[FacePair],
    constraint_table: list[list[list[tuple[int, ...]]]],
    face_pair_to_index: dict[FacePairKey, int],
    assignments: list[Assignment],
    assignment_provenance: list[list[int] | None],
    face_cells: list[list[int]],
    cell_faces: list[list[int]],
    face_components: list[dict[int, int]],
) -> list[int]:
  """Traces back assignments to find faces involved in a conflict.

  Args:
    constraint_type_id: The type of constraint that caused conflict.
    faces: Faces involved in conflicting constraint.
    face_pairs: List of face pairs corresponding to assignments.
    constraint_table: Table of constraints for each face pair.
    face_pair_to_index: Map from face pair to index in assignments array.
    assignments: Array of current assignments.
    assignment_provenance: For each assignment, stores which constraint caused
      it.
    face_cells: For each face, list of cells it belongs to.
    cell_faces: For each cell, list of faces it contains.
    face_components: Face connectivity components for transitivity.

  Returns:
    A sorted list of face indices involved in the conflict.
  """
  vars_to_check = []
  for pair in constraints.Constraints.get_pairs_for_type(
      constraint_type_id, faces
  ):
    vars_to_check.append(
        face_pair_to_index.get(math_utils.encode_order_pair(pair))
    )

  seen = set()
  while vars_to_check:
    idx = vars_to_check.pop()
    if idx is None:
      continue
    seen.add(idx)
    assignment = assignments[idx]
    if assignment != 0:
      provenance_info = assignment_provenance[idx]
      if provenance_info and provenance_info:
        p_type, p_idx, p_ci = provenance_info
        f1, f2 = math_utils.tuple_to_list(face_pairs[p_idx])
        # Recurse to find constraint that caused this assignment
        parent_constraint_faces = unpack_constraints(
            constraint_table[p_idx],
            p_type,
            f1,
            f2,
            face_cells,
            cell_faces,
            face_components,
        )[p_ci]

        for pair in constraints.Constraints.get_pairs_for_type(
            p_type, parent_constraint_faces
        ):
          i_ = face_pair_to_index.get(math_utils.encode_order_pair(pair))
          if (i_ is not None) and (i_ not in seen):
            vars_to_check.append(i_)

  error_faces_set = set()
  for i in seen:
    for f in math_utils.tuple_to_list(face_pairs[i]):
      error_faces_set.add(f)

  error_faces_list = list(error_faces_set)
  error_faces_list.sort()
  return error_faces_list
