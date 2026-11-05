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

"""Tests for Box Pleating pleats."""

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import crease_pattern
from bp_pipeline.crease_pattern import point
from bp_pipeline.solving import pleats as pleat_utils
import cp_test_fixtures as examples


def _subset_score(
    pattern: crease_pattern.CreasePattern,
    reference: crease_pattern.CreasePattern,
    *,
    match_fold: bool = False,
) -> float:
  if not pattern.creases:
    return 1.0 if not reference.creases else 0.0
  matched = sum(
      any(
          c.is_within(other_c, match_fold=match_fold)
          for other_c in reference.creases
          if not c.not_in_encompassing_rectangles(other_c)
      )
      for c in pattern.creases
  )
  return matched / len(pattern.creases)


def _min_subset_score(
    pattern1: crease_pattern.CreasePattern,
    pattern2: crease_pattern.CreasePattern,
    match_fold: bool = False,
) -> float:
  return min(
      _subset_score(pattern1, pattern2, match_fold=match_fold),
      _subset_score(pattern2, pattern1, match_fold=match_fold),
  )


class UtilsTest(parameterized.TestCase):

  @parameterized.parameters([
      examples.SPIDER,
      examples.SCORPION,
      examples.THREEFLAPSETSTWORIVERS,
      examples.RIVERONEFLAP,
      examples.GENERATED1,
      examples.GENERATED2,
      examples.GENERATED3,
      examples.GENERATED6,
      examples.CENTRALFLAP4HINGE,
      examples.CENTRALFOLDONLYPLEATS,
  ])
  def test_valid_pleats(
      self, example: examples.BoxPleatingCreasePatternExample
  ):
    packing_cp = example.packing_cp
    pleats = pleat_utils.create_pleats(packing_cp, grid_size=example.grid_size)
    ridges = [c for c in packing_cp.creases if c.fold == crease.Fold.MOUNTAIN]
    self.assertTrue(
        pleat_utils.valid_pleats(pleats, ridges, grid_size=example.grid_size)
    )

  @parameterized.parameters([
      examples.SPIDER,
      examples.SCORPION,
  ])
  def test_pleats(self, example: examples.BoxPleatingCreasePatternExample):
    packing_cp = example.packing_cp
    borders = [c for c in packing_cp.creases if c.fold == crease.Fold.BORDER]
    ridges = [c for c in packing_cp.creases if c.fold == crease.Fold.MOUNTAIN]
    pleats = pleat_utils.create_pleats(packing_cp, grid_size=example.grid_size)
    pleats_cp = crease_pattern.CreasePattern(
        pleats + borders, merge_trivial=True
    )
    self.assertTrue(pleat_utils.valid_pleats(pleats, ridges, example.grid_size))
    self.assertEqual(
        _min_subset_score(pleats_cp, example.assigned_pleats_cp), 1.0
    )

  @parameterized.parameters([
      examples.SPIDER,
      examples.SCORPION,
  ])
  def test_pleat_assignment(
      self, example: examples.BoxPleatingCreasePatternExample
  ):
    packing_cp = example.packing_cp
    borders = [c for c in packing_cp.creases if c.fold == crease.Fold.BORDER]
    pleats = pleat_utils.create_pleats(packing_cp, grid_size=example.grid_size)
    assigned_pleats = pleat_utils.assign_pleats(pleats, example.grid_size)
    assigned_pleats_cp = crease_pattern.CreasePattern(
        assigned_pleats + borders, merge_trivial=True
    )
    self.assertEqual(
        _min_subset_score(assigned_pleats_cp, example.assigned_pleats_cp, True),
        1.0,
    )

  @parameterized.parameters([
      (
          point.Point(x=0.5, y=0.5),
          crease.Crease(
              point.Point(x=0.0, y=0.5),
              point.Point(x=1.0, y=0.5),
              fold=crease.Fold.MOUNTAIN,
          ),
          True,
      ),
      (
          point.Point(x=0.5, y=0.5),
          crease.Crease(
              point.Point(x=0.5, y=0.0),
              point.Point(x=0.5, y=1.0),
              fold=crease.Fold.MOUNTAIN,
          ),
          True,
      ),
      (
          point.Point(x=0.0, y=0.5),
          crease.Crease(
              point.Point(x=0.0, y=0.5),
              point.Point(x=1.0, y=0.5),
              fold=crease.Fold.MOUNTAIN,
          ),
          True,
      ),
      (
          point.Point(x=0.5, y=0.0),
          crease.Crease(
              point.Point(x=0.5, y=0.0),
              point.Point(x=0.5, y=1.0),
              fold=crease.Fold.MOUNTAIN,
          ),
          True,
      ),
      (
          point.Point(x=0.6, y=0.5),
          crease.Crease(
              point.Point(x=0.0, y=0.5),
              point.Point(x=1.0, y=0.5),
              fold=crease.Fold.MOUNTAIN,
          ),
          True,
      ),
      (
          point.Point(x=0.5, y=0.6),
          crease.Crease(
              point.Point(x=0.5, y=0.0),
              point.Point(x=0.5, y=1.0),
              fold=crease.Fold.MOUNTAIN,
          ),
          True,
      ),
      (
          point.Point(x=0.6, y=0.6),
          crease.Crease(
              point.Point(x=0.0, y=0.5),
              point.Point(x=1.0, y=0.5),
              fold=crease.Fold.MOUNTAIN,
          ),
          False,
      ),
      (
          point.Point(x=0.6, y=0.6),
          crease.Crease(
              point.Point(x=0.5, y=0.0),
              point.Point(x=0.5, y=1.0),
              fold=crease.Fold.MOUNTAIN,
          ),
          False,
      ),
  ])
  def test_grid_point_intermediate_pleat(self, grid_point, pleat, expected):
    self.assertEqual(
        pleat_utils.grid_point_intermediate_pleat(grid_point, pleat),
        expected,
        msg=f'Grid point: {grid_point}, pleat: {pleat}',
    )


if __name__ == '__main__':
  absltest.main()
