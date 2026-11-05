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

"""Flat foldable solver."""

import collections
from collections.abc import Sequence
import dataclasses
import heapq
import math

from bp_pipeline import rectangle as rectangle_lib
from bp_pipeline import timeout as timeout_lib
from bp_pipeline.crease_pattern import crease as crease_utils
from bp_pipeline.crease_pattern import crease_pattern as cp_utils
from bp_pipeline.crease_pattern import point as point_utils
from bp_pipeline.crease_pattern import rotation
from bp_pipeline.crease_pattern import vertex


@dataclasses.dataclass(kw_only=True)
class CandidateCreasePattern:
  """A candidate crease Pattern that is being modified to fix flat foldability."""

  cp: cp_utils.CreasePattern
  non_foldable_vertices: list[vertex.Vertex]
  unmodifiable_crease_hashes: frozenset[int]
  crease_hash_to_vertex_mapping: dict[int, list[vertex.Vertex]]
  score: float
  border_distance: float
  num_crease_modifications: int
  candidate_num: int

  @classmethod
  def from_cp(
      cls,
      cp: cp_utils.CreasePattern,
      *,
      unmodifiable_crease_hashes: frozenset[int],
      num_crease_modifications: int,
      candidate_num: int,
  ) -> 'CandidateCreasePattern':
    """Initializes a CandidateCreasePattern from a Crease Pattern."""
    score, _, non_foldable_vertices = cp.vertex_flat_foldability_percentage()

    crease_hash_to_vertex_mapping: dict[int, list[vertex.Vertex]] = (
        collections.defaultdict(list)
    )
    for v in cp.vertices:
      timeout_lib.maybe_timeout_cooperatively()
      for c in v.creases:
        crease_hash_to_vertex_mapping[c.hash_value].append(v)

    border_distance = sum(
        min(v.point.x, 1.0 - v.point.x, v.point.y, 1.0 - v.point.y)
        for v in non_foldable_vertices
    )

    return cls(
        cp=cp,
        non_foldable_vertices=non_foldable_vertices,
        unmodifiable_crease_hashes=unmodifiable_crease_hashes,
        crease_hash_to_vertex_mapping=crease_hash_to_vertex_mapping,
        score=score,
        border_distance=border_distance,
        num_crease_modifications=num_crease_modifications,
        candidate_num=candidate_num,
    )

  def to_tuple(self) -> tuple[float, float, int, int, 'CandidateCreasePattern']:
    return (
        -self.score,
        self.border_distance,
        self.num_crease_modifications,
        self.candidate_num,
        self,
    )


def _get_other_connecting_vertex(
    connected_vertex: vertex.Vertex,
    connecting_crease: crease_utils.Crease,
    crease_hash_to_vertex_mapping: dict[int, list[vertex.Vertex]],
) -> vertex.Vertex:
  """Returns the other vertex connected to the given vertex and crease."""
  connected_vertices = crease_hash_to_vertex_mapping[
      connecting_crease.hash_value
  ]
  if len(connected_vertices) != 2:
    raise ValueError(
        'Crease must be connected to exactly two vertices (got'
        f' {len(connected_vertices)}).'
    )
  if connected_vertices[0].point.isclose(connected_vertex.point):
    return connected_vertices[1]
  elif connected_vertices[1].point.isclose(connected_vertex.point):
    return connected_vertices[0]
  else:
    raise ValueError(
        'Crease to be modified must be connected exactly to the violating'
        ' vertex and one other vertex.'
    )


def get_new_cp_with_rotated_crease(
    current_cp: cp_utils.CreasePattern,
    crease_to_be_rotated: crease_utils.Crease,
    violating_vertex: vertex.Vertex,
    crease_hash_to_vertex_mapping: dict[int, list[vertex.Vertex]],
) -> tuple[cp_utils.CreasePattern | None, frozenset[int]]:
  """Returns a new CP with a rotated crease and the hashes of the modified creases.

  Args:
    current_cp: The current CP.
    crease_to_be_rotated: The crease to be rotated.
    violating_vertex: The vertex that the crease to be rotated violates.
    crease_hash_to_vertex_mapping: A mapping of crease hashes to the vertices
      that they connect to.

  Returns:
    rotated_cp: The new CP with the rotated crease. If the rotation is invalid,
      this is None instead.
    modified_crease_hashes: The hashes of the creases that were modified in the
      new CP. If the rotation is invalid, this is an empty set instead.
  """
  new_creases: dict[int, crease_utils.Crease] = {
      c.hash_value: c for c in current_cp.creases
  }
  modified_creases: list[crease_utils.Crease] = []

  # Determine which alternating sum each angle belongs to.
  # sum_odd_angle is the sum of the angle made in the clockwise direction
  # of the crease to be modified and every other angle afterwards in the
  # clockwise direction.
  # sum_even_angle is the sum of the angle made in the
  # counter-clockwise direction of the crease to be modified and every other
  # angle afterwards in the counter-clockwise direction.
  crease_to_be_rotated_index = violating_vertex.creases.index(
      crease_to_be_rotated
  )
  sector_angles = [angle for angle, _, _ in violating_vertex.sector_angles()]
  if crease_to_be_rotated_index % 2 == 0:
    sum_odd_angles = sum(sector_angles[::2])
    sum_even_angles = sum(sector_angles[1::2])
  else:
    sum_odd_angles = sum(sector_angles[1::2])
    sum_even_angles = sum(sector_angles[::2])

  angle_delta = sum_odd_angles - sum_even_angles
  if math.isclose(angle_delta, 0):
    # Kawasaki is satisfied but this current CP is not flat foldable, meaning
    # that some other flat foldable criteria is being violated.
    return None, frozenset()

  # Rotate by half the angle delta since every n degrees we rotate will increase
  # sum_odd_angle by n/2 and decrease sum_even_angle by
  # n/2. So in order to reduce the angle_delta from n to 0, we rotate clockwise
  # by n/2 degrees.
  rotation_delta = angle_delta / 2
  # The angle made from the crease to be modified, to the adjacent creases in
  # both the clockwise and counter-clockwise directions.
  clockwise_angle = sector_angles[crease_to_be_rotated_index]
  counter_clockwise_angle = sector_angles[
      (crease_to_be_rotated_index - 1) % len(sector_angles)
  ]
  if (rotation_delta >= clockwise_angle) or (
      -rotation_delta >= counter_clockwise_angle
  ):
    # rotation_delta is clockwise degrees to satisfy Kawasaki (negative=CCW). If
    # rotation overlaps/passes adjacent crease, violation is unfixable.
    return None, frozenset()

  rotated_crease = rotation.rotate_crease_clockwise(
      crease_to_rotate=crease_to_be_rotated,
      rotation_angle_degrees=rotation_delta,
      rotation_origin_tip=violating_vertex.point,
      require_on_paper=False,
  )

  # The rotated crease connects the violating vertex and one other (adjacent)
  # vertex. Find this other adjacent vertex. We will have to update this vertex
  # as well, with the newly rotated crease.
  adjacent_vertex = _get_other_connecting_vertex(
      violating_vertex, crease_to_be_rotated, crease_hash_to_vertex_mapping
  )

  # adjacent_creases are the creases in the adjacent_vertex that are
  # adjacent to the rotated crease.
  adjacent_creases: list[crease_utils.Crease] = []
  crease_modified_index = adjacent_vertex.creases.index(crease_to_be_rotated)
  for i in [1, -1]:
    adjacent_crease = adjacent_vertex.creases[
        (crease_modified_index + i) % len(adjacent_vertex.creases)
    ]
    if adjacent_crease not in adjacent_creases:
      adjacent_creases.append(adjacent_crease)

  # The rotated crease should intersect with exactly one of the adjacent_creases
  # of the adjacent_vertex.
  new_adjacent_vertex_point = None
  closest_distance = float('inf')
  for adjacent_crease in adjacent_creases:
    timeout_lib.maybe_timeout_cooperatively()
    intersection_point = rotated_crease.vertex_with_crease(
        adjacent_crease, extend_lines=True
    )
    if (not intersection_point) or adjacent_crease.point_status(
        intersection_point
    ) not in (crease_utils.PointStatus.INTERNAL, crease_utils.PointStatus.TIP):
      continue

    distance = point_utils.distance(violating_vertex.point, intersection_point)
    if distance < closest_distance:
      # The closest intersection point to the rotation origin
      # (violating_vertex.point) is where the rotated crease will end up
      # connecting to, on the adjacent crease.
      closest_distance = distance
      new_adjacent_vertex_point = intersection_point
  if not new_adjacent_vertex_point:
    # This means the intersection point lies outside the range of the adjacent
    # creases, meaning it's not possible to rotate this crease without
    # intersecting with another crease (this crease is connected to the tip of
    # the adjacent crease).
    return None, frozenset()

  # Create the new adjacent vertex with the new vertex point, and all creases
  # updated to the new vertex point.
  for adjacent_crease in adjacent_vertex.creases:
    timeout_lib.maybe_timeout_cooperatively()
    if adjacent_crease.fold == crease_utils.Fold.BORDER:
      continue

    # All original non-border creases attached to the adjacent vertex must be
    # removed, since all of them will be replaced by a new corresponding crease
    # that connects to the new_adjacent_vertex_point.
    del new_creases[adjacent_crease.hash_value]

    if adjacent_crease.p1.isclose(adjacent_vertex.point):
      unmodified_point = adjacent_crease.p2
    elif adjacent_crease.p2.isclose(adjacent_vertex.point):
      unmodified_point = adjacent_crease.p1
    else:
      raise ValueError(
          "Crease in adjacent vertex is not connected to the adjacent vertex's"
          ' point.'
      )

    if unmodified_point.isclose(new_adjacent_vertex_point):
      # we moved the vertex close enough to another vertex so this adjacent
      # crease should be eliminated.
      continue
    new_adjacent_crease = crease_utils.Crease(
        unmodified_point, new_adjacent_vertex_point, fold=adjacent_crease.fold
    )
    modified_creases.append(new_adjacent_crease)

  new_cp = cp_utils.CreasePattern(
      creases=list(new_creases.values()) + modified_creases,
  )

  return (
      new_cp,
      frozenset({c.hash_value for c in modified_creases}),
  )


def get_flat_foldable(
    cp: cp_utils.CreasePattern,
    *,
    rectangles: Sequence[rectangle_lib.Rectangle] | None = None,
    unmodifiable_creases: list[crease_utils.Crease] | None = None,
    max_candidates: int | None = None,
    max_crease_modifications: int | None = None,
) -> cp_utils.CreasePattern | None:
  """Attempts to modify the crease angles of vertices that violate flat foldability criteria and return a flat foldable Crease Pattern.

  Currently, this function only supports fixing Kawasaki violations and not
  Maekawa violations.

  This algorithm uses a priority queue of CP candidates (initially starting
  with only the current CP), prioritizing CP's with high vertex flat
  foldability percentage (i.e. the less non-foldable vertices, the "closer"
  the CP is to being flat foldable). For a given CP candidate, for each
  non-foldable vertex, a new CP candidate is generated by rotating a crease
  attached to that vertex, such that it fixes the Kawasaki violation. These
  new CP's are added to the priority queue. The process is repeated until a CP
  with 100% flat foldable vertices is found, or until the priority queue is
  empty.

  Args:
    cp: The crease pattern to be modified.
    rectangles: Only creases within these rectangles are considered for
      rotation. If None, then all creases are considered.
    unmodifiable_creases: A set of crease hashes that should not be modified.
    max_candidates: Maximum number of unique candidate CPs that can be added to
      the priority queue. If None, no limit is applied.
    max_crease_modifications: Maximum number of crease modifications (rotations)
      allowed in a single candidate chain. Candidates exceeding this depth are
      not added to the priority queue. If None, no limit is applied.

  Returns:
    A flat foldable Crease Pattern or None if no solution is found.
  """
  if rectangles is None:
    rectangles = [
        rectangle_lib.Rectangle(
            name='paper', x_start=0.0, y_start=0.0, x_len=1.0, y_len=1.0
        )
    ]

  if unmodifiable_creases is not None:
    unmodifiable_crease_hashes = frozenset(
        {c.hash_value for c in unmodifiable_creases}
    )
  else:
    unmodifiable_crease_hashes = frozenset()

  # Priority queue stores:
  # (-score, modifications, cp_num, cp, non_foldable_vertices).
  # Using negative score because heapq is a min-heap. The number of
  # modifications is used as a tie-breaker, with the cp_num (denoting the
  # `cp_num`-th CP generated by this method so far) as a final tie-breaker,
  # since the crease pattern itself cannot be compared (since there's no
  # inherent ordering for `CreasePattern`).
  candidate_cp = CandidateCreasePattern.from_cp(
      cp,
      unmodifiable_crease_hashes=unmodifiable_crease_hashes,
      num_crease_modifications=0,
      candidate_num=0,
  )
  if candidate_cp.score == 1.0:
    return cp

  min_heap: list[tuple[float, float, int, int, CandidateCreasePattern]] = [
      candidate_cp.to_tuple()
  ]
  # Visited set to store hashes of crease configurations.
  cp_hashes_seen: set[int] = {cp.hash_value}
  cp_num = 1

  while min_heap:
    timeout_lib.maybe_timeout_cooperatively()
    _, _, _, _, candidate_cp = heapq.heappop(min_heap)

    for non_foldable_vertex in candidate_cp.non_foldable_vertices:
      timeout_lib.maybe_timeout_cooperatively()
      for crease_to_be_rotated in non_foldable_vertex.creases:
        crease_is_within_rectangle = any(
            rect.crease_is_within(crease_to_be_rotated) for rect in rectangles
        )
        if not crease_to_be_rotated.mountain_or_valley():
          continue
        if (
            crease_to_be_rotated.hash_value
            in candidate_cp.unmodifiable_crease_hashes
        ):
          continue
        if not crease_is_within_rectangle:
          continue

        new_cp, modified_crease_hashes = get_new_cp_with_rotated_crease(
            candidate_cp.cp,
            crease_to_be_rotated,
            non_foldable_vertex,
            candidate_cp.crease_hash_to_vertex_mapping,
        )
        if new_cp is None:
          continue

        new_cp_hash = new_cp.hash_value
        if new_cp_hash in cp_hashes_seen:
          continue
        cp_hashes_seen.add(new_cp_hash)

        new_num_modifications = candidate_cp.num_crease_modifications + 1
        if (
            max_crease_modifications is not None
            and new_num_modifications > max_crease_modifications
        ):
          continue

        new_candidate_cp = CandidateCreasePattern.from_cp(
            new_cp,
            unmodifiable_crease_hashes=candidate_cp.unmodifiable_crease_hashes.union(
                modified_crease_hashes
            ),
            num_crease_modifications=new_num_modifications,
            candidate_num=cp_num,
        )

        if new_candidate_cp.score == 1.0:
          return new_cp

        heapq.heappush(min_heap, new_candidate_cp.to_tuple())
        cp_num += 1
        if max_candidates is not None and cp_num > max_candidates:
          return None
  return None
