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

"""Tests for .cp crease pattern parser."""

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import crease_pattern
from bp_pipeline.crease_pattern import point
from bp_pipeline.crease_pattern.parser import cp_format as parser

# Create a square base crease pattern at any scale by formatting the coordinates
SQUARE_BASE = """3 0 {half} {half} {half}
2 {half} 0 {half} {half}
2 {half} {half} {half} {full}
2 {half} {half} {full} {half}"""


class CpFormatTest(parameterized.TestCase):

  @parameterized.parameters([
      ("1", crease.Fold.BORDER),
      ("2", crease.Fold.MOUNTAIN),
      ("3", crease.Fold.VALLEY),
      ("4", crease.Fold.TRIANGLE),
      ("5", crease.Fold.MOUNTAIN_ZEBRA),
      ("6", crease.Fold.VALLEY_ZEBRA),
  ])
  def test_get_fold_valid(self, linetype: str, expected_fold: crease.Fold):
    fold = parser.get_fold(linetype)
    self.assertEqual(fold, expected_fold)

  @parameterized.parameters(["0", "7", "abc", ""])
  def test_get_fold_invalid(self, linetype: str):
    with self.assertRaises(ValueError):
      parser.get_fold(linetype)

  def test_parse_cp_valid(self):
    cp_file = """3 0 0.5 1 0.5
2 0.5 0 0.5 1
1 0 0 1 0
1 1 0 1 1
1 1 1 0 1
1 0 1 0 0"""
    pattern = parser.parse_cp(cp_file)
    self.assertIsInstance(pattern, crease_pattern.CreasePattern)
    self.assertLen(pattern.creases, 12)
    self.assertLen(pattern.vertices, 9)

  def test_parse_cp_empty(self):
    cp_file = ""
    with self.assertRaises(ValueError):
      parser.parse_cp(cp_file)

  @parameterized.parameters([
      "1 0 0 1",
      "1 0 0 1 1 extra",
      "1 a b c d",
  ])
  def test_parse_cp_invalid(self, cp_file: str):
    with self.assertRaises(ValueError):
      parser.parse_cp(cp_file)

  def test_to_cp_valid(self):
    pattern = crease_pattern.CreasePattern(
        creases=[
            crease.Crease(
                point.Point(x=0, y=1),
                point.Point(x=1, y=0),
                fold=crease.Fold.VALLEY,
            ),
            crease.Crease(
                point.Point(x=0, y=0),
                point.Point(x=1, y=1),
                fold=crease.Fold.BORDER,
            ),
        ]
    )
    cp_string = parser.to_cp(pattern)
    expected_cp_string = """1 0 0 500 500
3 500 500 0 1000
3 500 500 1000 0
1 500 500 1000 1000"""
    self.assertEqual(cp_string, expected_cp_string)

  @parameterized.parameters([1000, 100, 10])
  def test_to_cp_scale(self, scale: float):
    cp_target_string = SQUARE_BASE.format(full=scale, half=scale // 2)
    pattern = crease_pattern.CreasePattern(
        creases=[
            crease.Crease(
                point.Point(x=0, y=0.5),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.VALLEY,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=0.5, y=1),
                fold=crease.Fold.MOUNTAIN,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=1, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
        ],
    )
    cp_string = parser.to_cp(pattern, scale=scale)
    self.assertEqual(cp_string, cp_target_string)

  def test_to_cp_empty(self):
    with self.assertRaises(ValueError):
      crease_pattern.CreasePattern(creases=[])

  def test_cp_roundtrip(self):
    cp_file = """3 0 5 5 5
2 5 5 10 0
3 5 5 10 10"""
    pattern = parser.parse_cp(cp_file)
    cp_string = parser.to_cp(pattern, scale=10)
    self.assertEqual(cp_string, cp_file)


if __name__ == "__main__":
  absltest.main()
