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

"""Tests for Box Pleating partitioning."""

import itertools

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import crease_pattern
from bp_pipeline.crease_pattern import point as point_lib
from bp_pipeline.crease_pattern import vertex as vertex_lib
from bp_pipeline.solving import partition
import cp_test_fixtures as examples

EXAMPLES = (
    examples.SPIDER,
    examples.SCORPION,
    examples.THREEFLAPSETSTWORIVERS,
    examples.RIVERONEFLAP,
    examples.GENERATED1,
    # examples.GENERATED2,
    examples.GENERATED3,
    examples.GENERATED6,
    examples.CENTRALFLAP4HINGE,
    examples.CENTRALFOLDONLYPLEATS,
    examples.HUMAN,
    examples.GEMINI,
)


class PartitionTest(parameterized.TestCase):

  @parameterized.parameters(
      (examples.SPIDER, 1),
      (examples.SCORPION, 3),
      (examples.NINE_TAIL, 11),
  )
  def test_num_partitions(
      self, example: examples.BoxPleatingCreasePatternExample, n_partitions: int
  ):
    packing_cp = example.packing_cp
    partitions = partition.partition_cp(packing_cp)

    self.assertLen(partitions, n_partitions)

  @parameterized.parameters(*EXAMPLES)
  def test_partitions_are_disjoint(
      self, example: examples.BoxPleatingCreasePatternExample
  ):
    packing_cp = example.packing_cp
    partitions = partition.partition_cp(packing_cp)

    # Test that partitions are disjoint by creases.
    for (i, p_i), (j, p_j) in itertools.combinations(enumerate(partitions), 2):
      self.assertTrue(
          p_i.vertices.keys().isdisjoint(p_j.vertices.keys()),
          f'Partitions {i} and {j} have overlapping vertices.',
      )

  @parameterized.parameters(*EXAMPLES)
  def test_partitions_are_comprehensive(
      self, example: examples.BoxPleatingCreasePatternExample
  ):
    packing_cp = example.packing_cp
    partitions = partition.partition_cp(packing_cp)

    combined = partitions[0]
    for p in partitions[1:]:
      combined = combined.union(p)

    # We construct the CP to sort the vertices
    combined_cp = crease_pattern.CreasePattern(
        [
            *(c.crease for c in combined.hinges.creases),
            *(c.crease for c in combined.ridges.creases),
        ],
        light_mode=True,
    )
    combined_cp.vertices = list(combined.vertices.values())
    combined_cp.sort_vertices()

    self.assertEqual(
        combined_cp.vertices,
        packing_cp.vertices,
    )

  @parameterized.parameters(*EXAMPLES)
  def test_hinges_and_ridges_have_correct_folds(
      self, example: examples.BoxPleatingCreasePatternExample
  ):
    packing_cp = example.packing_cp
    partitions = partition.partition_cp(packing_cp)

    for i, p in enumerate(partitions):
      self.assertTrue(
          all(c.crease.fold == crease.Fold.HINGE for c in p.hinges.creases),
          f'partition[{i}].hinges has non-hinge creases.',
      )
      self.assertTrue(
          all(c.crease.fold == crease.Fold.MOUNTAIN for c in p.ridges.creases),
          f'partition[{i}].ridges has non-ridge creases.',
      )

  @parameterized.parameters(*EXAMPLES)
  def test_no_empty_partitions(
      self, example: examples.BoxPleatingCreasePatternExample
  ):
    packing_cp = example.packing_cp
    partitions = partition.partition_cp(packing_cp)

    for i, p in enumerate(partitions):
      self.assertNotEmpty(p.hinges.creases, f'partition[{i}] has no hinges.')

  def test_has_hinges(self):
    p1 = point_lib.Point(x=0, y=0)
    p2 = point_lib.Point(x=1, y=0)
    p3 = point_lib.Point(x=0, y=1)

    # Vertex with a hinge crease.
    vertex_with_hinge = vertex_lib.Vertex(
        [
            crease.Crease(p1, p2, fold=crease.Fold.HINGE),
            crease.Crease(p1, p3, fold=crease.Fold.MOUNTAIN),
        ],
        vertex_point=p1,
    )
    self.assertTrue(partition._has_hinges(vertex_with_hinge))

    # Vertex without any hinge creases.
    vertex_without_hinge = vertex_lib.Vertex(
        [
            crease.Crease(p1, p2, fold=crease.Fold.MOUNTAIN),
            crease.Crease(p1, p3, fold=crease.Fold.BORDER),
        ],
        vertex_point=p1,
    )
    self.assertFalse(partition._has_hinges(vertex_without_hinge))


class OrderedPartitionsTest(absltest.TestCase):
  """Tests for the OrderedPartitions class."""

  def setUp(self):
    super().setUp()
    self.example = examples.SCORPION
    self.partitions = tuple(partition.partition_cp(self.example.packing_cp))

  def test_ordered_by_num_vertices(self):
    partitions = sorted(
        self.partitions, key=lambda p: len(p.vertices), reverse=True
    )
    ordered_partitions = partition.OrderedPartitions(self.partitions)
    self.assertEqual(ordered_partitions.partitions, tuple(partitions))

  def test_get_partition_id_finds_point_on_crease(self):
    """Tests that get_partition_id can find points on creases via search."""
    ordered_partitions = partition.OrderedPartitions(self.partitions)
    point = point_lib.Point(x=0.5, y=0.1)  # On a crease in partition 0.

    self.assertIsNotNone(ordered_partitions.search_partition_creases(point))

    # Verify the point is not an existing vertex in any partition.
    self.assertNotIn(point, ordered_partitions._point_to_partition_id)

    # get_partition_id should use the search fallback to find the partition.
    self.assertEqual(ordered_partitions.get_partition_id(point), 0)
    self.assertIn(point, ordered_partitions._point_to_partition_id)


if __name__ == '__main__':
  absltest.main()
