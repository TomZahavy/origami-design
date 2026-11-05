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

"""Tests for flat foldability solver."""

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.crease_pattern import flat_foldable
from bp_pipeline.crease_pattern.parser import svg
import cp_test_fixtures as shaping_examples


class FlatFoldableTest(parameterized.TestCase):

  @parameterized.named_parameters(
      dict(
          testcase_name='one_kawasaki_violation',
          example=shaping_examples.ONE_KAWASAKI_VIOLATION,
      ),
      dict(
          testcase_name='four_kawasaki_violations',
          example=shaping_examples.FOUR_KAWASAKI_VIOLATIONS,
      ),
  )
  def test_get_flat_foldable(
      self, example: shaping_examples.BoxPleatingCreasePatternExample
  ):
    base_cp = svg.parse_svg(example.base_svg, grid_size=example.grid_size)
    self.assertFalse(base_cp.local_flat_foldability())
    fixed_cp = flat_foldable.get_flat_foldable(base_cp)
    self.assertIsNotNone(fixed_cp)
    self.assertTrue(fixed_cp.local_flat_foldability())

  def test_max_candidates_limits_search(self):
    example = shaping_examples.FOUR_KAWASAKI_VIOLATIONS
    base_cp = svg.parse_svg(example.base_svg, grid_size=example.grid_size)
    self.assertFalse(base_cp.local_flat_foldability())
    result = flat_foldable.get_flat_foldable(base_cp, max_candidates=1)
    self.assertIsNone(result)

  def test_max_crease_modifications_limits_search(self):
    example = shaping_examples.FOUR_KAWASAKI_VIOLATIONS
    base_cp = svg.parse_svg(example.base_svg, grid_size=example.grid_size)
    self.assertFalse(base_cp.local_flat_foldability())
    result = flat_foldable.get_flat_foldable(
        base_cp, max_crease_modifications=0
    )
    self.assertIsNone(result)


if __name__ == '__main__':
  absltest.main()
