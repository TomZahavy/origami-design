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

"""Tests for Box Pleating ridges."""

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import crease_pattern
from bp_pipeline.solving import ridges as ridge_utils
from bp_pipeline.solving import utils
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

  def test_ridge_assignment(self):
    for example in [examples.SPIDER, examples.SCORPION]:
      assigned_pleats_cp = example.assigned_pleats_cp
      assert assigned_pleats_cp
      borders = [
          c for c in assigned_pleats_cp.creases if c.fold == crease.Fold.BORDER
      ]
      ridges = [
          c
          for c in example.packing_cp.creases
          if c.fold == crease.Fold.MOUNTAIN
      ]
      assigned_pleats = [
          c for c in assigned_pleats_cp.creases if c.fold != crease.Fold.BORDER
      ]
      unassigned_ridges, _ = utils.split_unassigned_and_central_ridges(ridges)
      assigned_ridges = ridge_utils.assign_ridges(
          unassigned_ridges, assigned_pleats, grid_size=32
      )
      assigned_ridges_cp = crease_pattern.CreasePattern(
          assigned_ridges + assigned_pleats + borders
      )
      self.assertEqual(
          _min_subset_score(
              assigned_ridges_cp, example.assigned_ridges_cp, True
          ),
          1.0,
      )


if __name__ == '__main__':
  absltest.main()
