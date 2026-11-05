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

"""Constraints for flat-folding."""


class Constraints:
  """Contains information about flat-folding constraints."""

  class Type:
    taco_taco = 0
    taco_tortilla = 1
    tortilla_tortilla = 2
    transitivity = 3

  names = ["taco-taco", "taco-tortilla", "tortilla-tortilla", "transitivity"]
  types = [0, 1, 2, 3]

  PAIR_MAPS = [
      # 0: taco-taco ([A,B,C,D]) -> [[A,B],[C,D],[C,B],[A,D],[A,C],[B,D]]
      lambda faces: [
          [faces[0], faces[1]],
          [faces[2], faces[3]],
          [faces[2], faces[1]],
          [faces[0], faces[3]],
          [faces[0], faces[2]],
          [faces[1], faces[3]],
      ],
      # 1: taco-tortilla ([A,B,C]) -> [[A,C],[C,B]]
      lambda faces: [[faces[0], faces[2]], [faces[2], faces[1]]],
      # 2: tortilla-tortilla ([A,B,C,D]) -> [[A,C],[B,D]]
      lambda faces: [[faces[0], faces[2]], [faces[1], faces[3]]],
      # 3: transitivity ([A,B,C]) -> [[A,B],[B,C],[C,A]]
      lambda faces: [
          [faces[0], faces[1]],
          [faces[1], faces[2]],
          [faces[2], faces[0]],
      ],
  ]

  @classmethod
  def get_pairs_for_type(
      cls, type_id: int, faces: list[int]
  ) -> list[list[int]]:
    """Returns the pairs of faces for a given constraint type.

    Args:
      type_id: The type of constraint.
      faces: A list of face indices.

    Returns:
      A list of pairs of face indices.
    """
    return cls.PAIR_MAPS[type_id](faces)

  VALID_STATES = [
      [
          "111112",
          "111121",
          "111222",
          "112111",  # 0: taco-taco
          "121112",
          "121222",
          "122111",
          "122212",
          "211121",
          "211222",
          "212111",
          "212221",
          "221222",
          "222111",
          "222212",
          "222221",
      ],
      ["12", "21"],  # 1: taco-tortilla
      ["11", "22"],  # 2: tortilla-tortilla
      ["112", "121", "122", "211", "212", "221"],  # 3: transitivity
  ]

  IMPLIED_STATES = {}
  IMPLIED_STATES_INT: dict[int, list[list[list[int]] | int]] = {}

  class State:
    conflict = 0
    alive = 1
    dead = 2

  @classmethod
  def build_implication_tables(cls):
    """Generates implication tables by checking all 3^n assignments."""
    if cls.IMPLIED_STATES and cls.IMPLIED_STATES_INT:
      return
    for type_id in cls.types:
      valid_strings = cls.VALID_STATES[type_id]
      n = len(valid_strings[0])
      implications = [dict() for _ in range(n + 1)]
      index_to_key = [""] * (3**n)

      for i in range(3**n):
        k = i
        num_zeros = 0
        assignment = []
        for j in range(n):
          val = k % 3
          num_zeros += 1 if val == 0 else 0
          assignment.append(str(val))
          k = (k - int(assignment[j])) // 3
        key_str = "".join(assignment)
        index_to_key[i] = key_str
        implications[num_zeros][key_str] = cls.State.conflict

      for k in valid_strings:
        implications[0][k] = cls.State.dead

      for i in range(1, n + 1):
        for k, _ in implications[i].items():
          assignment = list(k)
          implied_list = []
          conflict = True
          dead = True

          for j in range(n):
            if assignment[j] != "0":
              continue
            possible = 0
            for c in ["1", "2"]:
              assignment[j] = c
              st = implications[i - 1].get("".join(assignment))
              if st != cls.State.dead:
                dead = False
              if st != cls.State.conflict:
                possible |= int(c)
            assignment[j] = "0"

            if possible:
              conflict = False
              if possible < 3:
                implied_list.append([j, possible])

          if conflict:
            st = cls.State.conflict
          elif implied_list:
            st = implied_list
          elif dead:
            st = cls.State.dead
          else:
            st = cls.State.alive

          implications[i][k] = st

      cls.IMPLIED_STATES[type_id] = {}
      for i in range(n, -1, -1):
        for k, v in implications[i].items():
          cls.IMPLIED_STATES[type_id][k] = v
      cls.IMPLIED_STATES_INT[type_id] = [
          cls.IMPLIED_STATES[type_id][index_to_key[i]] for i in range(3**n)
      ]
