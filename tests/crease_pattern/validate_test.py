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

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import crease_pattern
from bp_pipeline.crease_pattern import point
from bp_pipeline.crease_pattern import validate
from bp_pipeline.crease_pattern.parser import svg as parser


class ValidateTest(parameterized.TestCase):

  @parameterized.named_parameters(
      dict(
          testcase_name="hinge_crease",
          cp=crease_pattern.CreasePattern(
              creases=[
                  crease.Crease(
                      point.Point(x=0.0, y=0.0),
                      point.Point(x=1.0, y=1.0),
                      fold=crease.Fold.HINGE,
                  )
              ]
          ),
      ),
      dict(
          testcase_name="only_one_border",
          cp=crease_pattern.CreasePattern(
              creases=[
                  crease.Crease(
                      point.Point(x=0.0, y=0.0),
                      point.Point(x=1.0, y=1.0),
                      fold=crease.Fold.BORDER,
                  )
              ]
          ),
      ),
      dict(
          testcase_name="rect_border",
          cp=crease_pattern.CreasePattern(
              creases=[
                  crease.Crease(
                      point.Point(x=0.0, y=0.0),
                      point.Point(x=0.0, y=0.5),
                      fold=crease.Fold.BORDER,
                  ),
                  crease.Crease(
                      point.Point(x=0.0, y=0.5),
                      point.Point(x=1.0, y=0.5),
                      fold=crease.Fold.BORDER,
                  ),
                  crease.Crease(
                      point.Point(x=1.0, y=0.0),
                      point.Point(x=1.0, y=0.5),
                      fold=crease.Fold.BORDER,
                  ),
                  crease.Crease(
                      point.Point(x=1.0, y=0.0),
                      point.Point(x=0.0, y=0.0),
                      fold=crease.Fold.BORDER,
                  ),
              ]
          ),
      ),
      dict(
          testcase_name="collinear_borders",
          cp=crease_pattern.CreasePattern(
              creases=[
                  crease.Crease(
                      point.Point(x=0.0, y=0.0),
                      point.Point(x=0.0, y=1.0),
                      fold=crease.Fold.BORDER,
                  ),
                  crease.Crease(
                      point.Point(x=0.1, y=0.0),
                      point.Point(x=0.1, y=1.0),
                      fold=crease.Fold.BORDER,
                  ),
                  crease.Crease(
                      point.Point(x=0.2, y=0.0),
                      point.Point(x=0.2, y=1.0),
                      fold=crease.Fold.BORDER,
                  ),
                  crease.Crease(
                      point.Point(x=0.3, y=0.0),
                      point.Point(x=0.3, y=1.0),
                      fold=crease.Fold.BORDER,
                  ),
              ]
          ),
      ),
  )
  def test_is_valid_returns_false(self, cp: crease_pattern.CreasePattern):
    self.assertFalse(validate.valid_pattern(cp))

  def test_valid_pattern_is_valid(self):
    pattern = parser.parse_svg(
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
            <rect stroke="black" x="0" y="0" width="100" height="100"/>
            <line stroke="blue" x1="0" y1="50" x2="100" y2="50"/>
          </svg>"""
    )
    self.assertTrue(validate.valid_pattern(pattern))


if __name__ == "__main__":
  absltest.main()
