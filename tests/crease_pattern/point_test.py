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

"""Tests for Point object."""

import dataclasses
import math

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline import rectangle as vector
from bp_pipeline.crease_pattern import point


@dataclasses.dataclass(frozen=True)
class PointTestExample:
  """Contains a single variant of a problem."""

  x: float
  y: float
  viewbox: tuple[float, float, float, float]


VALID_POINT_EXAMPLES = [
    PointTestExample(
        x=0.5,
        y=0.5,
        viewbox=(0, 0, 1, 1),
    ),
    PointTestExample(
        x=0.5,
        y=0.5 + 1.1e-3,
        viewbox=(0, 0, 1, 1),
    ),
    PointTestExample(
        x=0.5,
        y=0.5 + 1e-5,
        viewbox=(0, 0, 1, 1),
    ),
    PointTestExample(
        x=0.5,
        y=1.0 + 1e-5,
        viewbox=(0, 0, 1, 1),
    ),
]

INVALID_POINT_EXAMPLES = [
    PointTestExample(
        x=2.5,
        y=0.5,
        viewbox=(0, 0, 1, 1),
    ),
    PointTestExample(
        x=0.5,
        y=1.0 + 1.1e-3,
        viewbox=(0, 0, 1, 1),
    ),
]

POINT_TARGET_EXAMPLES = [
    (
        PointTestExample(
            x=0,
            y=0,
            viewbox=(-1, -1, 2, 2),
        ),
        (0.5, 0.5),
    ),
    (
        PointTestExample(
            x=4,
            y=4,
            viewbox=(-1, -1, 10, 10),
        ),
        (0.5, 0.5),
    ),
    (
        PointTestExample(
            x=2,
            y=2,
            viewbox=(0, 0, 2, 4),
        ),
        (0.5, 0.5),
    ),
    (
        PointTestExample(
            x=-1,
            y=1,
            viewbox=(-5, 0, 10, 5),
        ),
        (0.4, 0.1),
    ),
]


class PointTest(parameterized.TestCase):

  @parameterized.parameters(VALID_POINT_EXAMPLES)
  def test_valid_points(self, point_example: PointTestExample):
    pt = point.Point.from_viewbox(
        point_example.x,
        point_example.y,
        point_example.viewbox,
    )
    self.assertIsInstance(pt, point.Point)

  @parameterized.parameters(INVALID_POINT_EXAMPLES)
  def test_invalid_points(self, point_example: PointTestExample):
    with self.assertRaises(ValueError):
      point.Point.from_viewbox(
          point_example.x,
          point_example.y,
          point_example.viewbox,
      )

  def test_close_points(self):
    pe1, pe2, pe3 = VALID_POINT_EXAMPLES[:3]
    p1 = point.Point.from_viewbox(pe1.x, pe1.y, pe1.viewbox)
    p2 = point.Point.from_viewbox(pe2.x, pe2.y, pe2.viewbox)
    p3 = point.Point.from_viewbox(pe3.x, pe3.y, pe3.viewbox)
    self.assertFalse(p1.isclose(p2))
    self.assertTrue(p1.isclose(p3))

  def test_subtract_points(self):
    p1 = point.Point(x=1.0, y=0.5)
    p2 = point.Point(x=0.5, y=0.5)
    self.assertTrue((p1 - p2).isclose(point.Point(x=0.5, y=0.0)))
    self.assertTrue(p1.isclose(point.Point(x=1.0, y=0.5)))
    self.assertTrue(p2.isclose(point.Point(x=0.5, y=0.5)))

  @parameterized.parameters(POINT_TARGET_EXAMPLES)
  def test_point_target_examples(
      self, point_example: PointTestExample, target: tuple[float, float]
  ):
    p = point.Point.from_viewbox(
        point_example.x,
        point_example.y,
        point_example.viewbox,
    )
    x1, x2 = target
    self.assertTrue(p.isclose(point.Point(x=x1, y=x2)))

  def test_collinear_points(self):
    p1 = point.Point(x=0.25, y=0.25)
    p2 = point.Point(x=0.5, y=0.5)
    p3 = point.Point(x=0.75, y=0.75)
    p4 = point.Point(x=0.0, y=0.25)
    p5 = point.Point(x=0.0, y=0.5)
    p6 = point.Point(x=0.0, y=0.75)
    p7 = point.Point(x=0.25, y=0.0)
    p8 = point.Point(x=0.5, y=0.0)
    p9 = point.Point(x=0.75, y=0.0)
    with self.subTest(name='Collinear_points'):
      self.assertTrue(point.is_collinear(p1, p2, p3))
    with self.subTest(name='Collinear_same_x'):
      self.assertTrue(point.is_collinear(p4, p5, p6))
    with self.subTest(name='Collinear_same_y'):
      self.assertTrue(point.is_collinear(p7, p8, p9))
    with self.subTest(name='Collinear_identical_points'):
      self.assertTrue(point.is_collinear(p2, p2, p6))
      self.assertTrue(point.is_collinear(p2, p2, p2))
    with self.subTest(name='Not_collinear_points'):
      self.assertFalse(point.is_collinear(p1, p5, p3))
      self.assertFalse(point.is_collinear(p2, p4, p6))
      self.assertFalse(point.is_collinear(p8, p2, p3))

  def test_is_border(self):
    p1 = point.Point(x=0.25, y=0.25)
    p2 = point.Point(x=0.5, y=0.5)
    p3 = point.Point(x=0.75, y=0.75)
    p4 = point.Point(x=0.0, y=0.0)
    p5 = point.Point(x=0.0, y=0.5)
    p6 = point.Point(x=1.0, y=0.75)
    p7 = point.Point(x=0.5, y=0.99999)

    with self.subTest(name='Internal_points'):
      self.assertFalse(p1.is_border)
      self.assertFalse(p2.is_border)
      self.assertFalse(p3.is_border)
    with self.subTest(name='Border_points'):
      self.assertTrue(p4.is_border)
      self.assertTrue(p5.is_border)
      self.assertTrue(p6.is_border)
    with self.subTest(name='Tolerance'):
      self.assertTrue(p7.is_border)

  def test_is_paper_corner(self):
    p1 = point.Point(x=0.0, y=0.0)
    p2 = point.Point(x=1.0, y=0.0)
    p3 = point.Point(x=0.0, y=1.0)
    p4 = point.Point(x=1.0, y=1.0)
    p5 = point.Point(x=0.5, y=0.5)
    self.assertTrue(p1.is_paper_corner)
    self.assertTrue(p2.is_paper_corner)
    self.assertTrue(p3.is_paper_corner)
    self.assertTrue(p4.is_paper_corner)
    self.assertFalse(p5.is_paper_corner)

  @parameterized.named_parameters(
      dict(
          testcase_name='identity',
          p_in=(0.3, 0.6),
          w=((1.0, 0.0), (0.0, 1.0)),
          b=(0.0, 0.0),
          expected=(0.3, 0.6),
      ),
      dict(
          testcase_name='shift',
          p_in=(0.3, 0.6),
          w=((1.0, 0.0), (0.0, 1.0)),
          b=(0.1, -0.2),
          expected=(0.4, 0.4),
      ),
      dict(
          testcase_name='scale_center',
          p_in=(0.2, 0.8),
          w=((0.5, 0.0), (0.0, 0.5)),
          b=(0.25, 0.25),
          expected=(0.35, 0.65),
      ),
      dict(
          testcase_name='rotate_90_ccw_around (0.5, 0.5)',
          p_in=(0.2, 0.4),
          w=((0.0, -1.0), (1.0, 0.0)),
          b=(1.0, 0.0),
          expected=(0.6, 0.2),
      ),
      dict(
          testcase_name='rotate_90_cw_around (0.5, 0.5)',
          p_in=(0.2, 0.4),
          w=((0.0, 1.0), (-1.0, 0.0)),
          b=(0.0, 1.0),
          expected=(0.4, 0.8),
      ),
      dict(
          testcase_name='rotate (0.5, 0.5) 90 around (0.5, 0.5) is noop',
          p_in=(0.5, 0.5),
          w=((0.0, -1.0), (1.0, 0.0)),
          b=(1.0, 0.0),
          expected=(0.5, 0.5),
      ),
      dict(
          testcase_name='flip_y_eq_x',
          p_in=(0.2, 0.7),
          w=((0.0, 1.0), (1.0, 0.0)),
          b=(0.0, 0.0),
          expected=(0.7, 0.2),
      ),
  )
  def test_transform(self, p_in, w, b, expected):
    p = point.Point(x=p_in[0], y=p_in[1])
    expected_p = point.Point(x=expected[0], y=expected[1])
    transformed_p = p.transform(w, b)
    self.assertTrue(transformed_p.isclose(expected_p))

  def test_in_zero_one_range(self):
    # positives
    tips = [-1e-4, -1e-5, 1e-5, 1e-4, 1 - 1e-4, 1 - 1e-5, 1 + 1e-5, 1 + 1e-4]
    for num in tips:
      self.assertTrue(point.in_zero_one_range(num))
    grid = [i / 100 for i in range(0, 101)]
    for num in grid:
      self.assertTrue(point.in_zero_one_range(num))
    # negatives
    negatives = [-100, -5, -1, -1e-1, -1e-2, 1 + 1e-2, 1 + 1e-1, 5, 100]
    for num in negatives:
      self.assertFalse(point.in_zero_one_range(num))

  def test_strict_in_zero_one_range(self):
    # positives
    grid = [i / 1000 for i in range(2, 999)]
    for num in grid:
      self.assertTrue(point.in_zero_one_range(num, strict=True))
    # negatives
    tips = [
        -1e-4,
        -1e-5,
        0,
        1e-5,
        1e-4,
        1 - 1e-4,
        1 - 1e-5,
        1,
        1 + 1e-5,
        1 + 1e-4,
    ]
    for num in tips:
      self.assertFalse(point.in_zero_one_range(num, strict=True))

  def test_add_point(self):
    p1 = point.Point(x=0.1, y=0.2)
    v1 = vector.Vector(x=0.3, y=0.4)
    p3 = p1 + v1
    self.assertTrue(p3.isclose(point.Point(x=0.4, y=0.6)))

  @parameterized.named_parameters(
      dict(
          testcase_name='close_to_nothing',
          x=0.5,
          y=0.5,
          expected_left=False,
          expected_right=False,
          expected_top=False,
          expected_bottom=False,
      ),
      dict(
          testcase_name='close_to_left',
          x=1e-4,
          y=0.5,
          expected_left=True,
          expected_right=False,
          expected_top=False,
          expected_bottom=False,
      ),
      dict(
          testcase_name='close_to_right',
          x=1 - 1e-4,
          y=0.5,
          expected_left=False,
          expected_right=True,
          expected_top=False,
          expected_bottom=False,
      ),
      dict(
          testcase_name='close_to_top',
          x=0.5,
          y=1e-4,
          expected_left=False,
          expected_right=False,
          expected_top=True,
          expected_bottom=False,
      ),
      dict(
          testcase_name='close_to_bottom',
          x=0.5,
          y=1 - 1e-4,
          expected_left=False,
          expected_right=False,
          expected_top=False,
          expected_bottom=True,
      ),
      dict(
          testcase_name='close_to_top_left',
          x=1e-4,
          y=1e-4,
          expected_left=True,
          expected_right=False,
          expected_top=True,
          expected_bottom=False,
      ),
  )
  def test_close_to_border(
      self, x, y, expected_left, expected_right, expected_top, expected_bottom
  ):
    p = point.Point(x=x, y=y)
    self.assertEqual(p.close_to_left_border, expected_left)
    self.assertEqual(p.close_to_right_border, expected_right)
    self.assertEqual(p.close_to_top_border, expected_top)
    self.assertEqual(p.close_to_bottom_border, expected_bottom)

  @parameterized.named_parameters(
      dict(
          testcase_name='inside_line',
          x=0.25,
          y=0.25,
          p1=(0.0, 0.0),
          p2=(0.5, 0.5),
      ),
      dict(
          testcase_name='at_tip_of_line',
          x=0.5,
          y=0.5,
          p1=(0.0, 0.0),
          p2=(0.5, 0.5),
      ),
      dict(
          testcase_name='outside_line',
          x=0.75,
          y=0.75,
          p1=(0.0, 0.0),
          p2=(0.5, 0.5),
      ),
      dict(
          testcase_name='outside_line_off_paper',
          x=0.0 - 0.1,
          y=0.0 - 0.1,
          p1=(0.0, 0.0),
          p2=(0.5, 0.5),
      ),
      dict(
          testcase_name='fraction_line_inside',
          x=0.2 + 3 / 7 * 0.3,
          y=0.4,
          p1=(0.2, 0.1),
          p2=(0.5, 0.8),
      ),
      dict(
          testcase_name='fraction_line_outside',
          x=0.1,
          y=0.1 - 7 / 3 * 0.1,
          p1=(0.2, 0.1),
          p2=(0.5, 0.8),
      ),
  )
  def test_find_xy_on_line(
      self, x: float, y: float, p1: tuple[float, float], p2: tuple[float, float]
  ):
    p1 = point.Point(x=p1[0], y=p1[1], require_on_paper=False)
    p2 = point.Point(x=p2[0], y=p2[1], require_on_paper=False)
    self.assertTrue(math.isclose(point.find_y_on_line(x, p1, p2), y))
    self.assertTrue(math.isclose(point.find_x_on_line(y, p1, p2), x))

  def test_find_xy_on_line_error(self):
    p1 = point.Point(x=0.5, y=0.5, require_on_paper=False)
    p2 = point.Point(x=0.5, y=0.75, require_on_paper=False)
    with self.assertRaisesRegex(ValueError, 'Cannot find y on line'):
      point.find_y_on_line(0.5, p1, p2)
    p1 = point.Point(x=0.5, y=0.5, require_on_paper=False)
    p2 = point.Point(x=0.75, y=0.5, require_on_paper=False)
    with self.assertRaisesRegex(ValueError, 'Cannot find x on line'):
      point.find_x_on_line(0.5, p1, p2)


if __name__ == '__main__':
  absltest.main()
