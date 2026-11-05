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

"""Tests utilities for packing in box pleating with flaps."""

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline import rectangle as shaping_utils
from bp_pipeline.packing import utils_packing_flaps
from bp_pipeline.stick_figures import stick as stick_lib
import numpy as np


class PackingFlapsUtilsTest(parameterized.TestCase):

  @parameterized.named_parameters(
      dict(
          testcase_name="perfectly_filled_single_rect",
          width=10,
          height=10,
          placement=[((10, 10), 0, 0)],
          assertion_method="assertEqual",
          expected_value=0,
      ),
      dict(
          testcase_name="unused_area_single_rect",
          width=10,
          height=10,
          placement=[((5, 5), 0, 0)],
          assertion_method="assertEqual",
          expected_value=75,
      ),
      dict(
          testcase_name="perfectly_filled_multiple_rects",
          width=4,
          height=4,
          placement=[((2, 4), 0, 0), ((2, 4), 2, 0)],
          assertion_method="assertEqual",
          expected_value=0,
      ),
      dict(
          testcase_name="perfectly_filled_complex",
          width=6,
          height=6,
          placement=[
              ((3, 3), 0, 0),
              ((3, 3), 3, 0),
              ((3, 3), 0, 3),
              ((3, 3), 3, 3),
          ],
          assertion_method="assertEqual",
          expected_value=0,
      ),
      dict(
          testcase_name="gap_in_container",
          width=4,
          height=4,
          placement=[((2, 2), 0, 0)],
          assertion_method="assertNotEqual",
          expected_value=0,
      ),
      dict(
          testcase_name="complex_gap_in_container",
          width=3,
          height=3,
          placement=[((3, 2), 0, 0), ((2, 1), 0, 2)],
          assertion_method="assertNotEqual",
          expected_value=0,
      ),
      dict(
          testcase_name="rect_partially_outside_fills_container",
          width=5,
          height=5,
          placement=[((7, 7), -1, -1)],
          assertion_method="assertEqual",
          expected_value=0,
      ),
      dict(
          testcase_name="rect_partially_outside_leaves_gap",
          width=5,
          height=5,
          placement=[((3, 3), -1, -1)],
          assertion_method="assertNotEqual",
          expected_value=0,
      ),
      dict(
          testcase_name="rect_entirely_outside",
          width=5,
          height=5,
          placement=[((2, 2), 10, 10)],
          assertion_method="assertNotEqual",
          expected_value=0,
      ),
      dict(
          testcase_name="empty_packing_placement",
          width=5,
          height=5,
          placement=[],
          assertion_method="assertNotEqual",
          expected_value=0,
      ),
      dict(
          testcase_name="empty_container_empty_packing",
          width=0,
          height=0,
          placement=[],
          assertion_method="assertEqual",
          expected_value=0,
      ),
      dict(
          testcase_name="empty_container_with_rects",
          width=0,
          height=0,
          placement=[((1, 1), 0, 0)],
          assertion_method="assertEqual",
          expected_value=0,
      ),
      dict(
          testcase_name="full_mask_no_placement",
          width=2,
          height=2,
          mask=np.array([[True, True], [True, True]]),
          assertion_method="assertEqual",
          expected_value=0,
      ),
      dict(
          testcase_name="partial_mask_no_placement",
          width=2,
          height=2,
          mask=np.array([[False, True], [False, False]]),
          assertion_method="assertEqual",
          expected_value=3,
      ),
      dict(
          testcase_name="mask_with_partial_placement",
          width=4,
          height=4,
          placement=[((2, 2), 2, 2)],
          mask=np.array([
              [True, True, False, False],
              [False] * 4,
              [False] * 4,
              [False] * 4,
          ]),
          assertion_method="assertEqual",
          expected_value=10,
      ),
      dict(
          testcase_name="mask_with_perfect_placement",
          width=2,
          height=2,
          placement=[((1, 2), 0, 1), ((1, 1), 1, 0)],
          mask=np.array([[True, False], [False, False]]),
          assertion_method="assertEqual",
          expected_value=1,
      ),
      dict(
          testcase_name="overlapping_rects",
          width=4,
          height=4,
          placement=[((3, 3), 0, 0), ((3, 3), 1, 1)],
          assertion_method="assertEqual",
          expected_value=2,
      ),
      dict(
          testcase_name="mask_larger_than_container",
          width=2,
          height=2,
          placement=[],
          mask=np.array([
              [True, True, True],
              [True, True, True],
              [True, True, True],
          ]),
          assertion_method="assertEqual",
          expected_value=0,
      ),
      dict(
          testcase_name="mask_smaller_than_container",
          width=4,
          height=4,
          placement=[],
          mask=np.array([[True]]),
          assertion_method="assertEqual",
          expected_value=15,
      ),
      dict(
          testcase_name="perfect_overlap",
          width=2,
          height=2,
          placement=[((2, 2), 0, 0), ((2, 2), 0, 0)],
          assertion_method="assertEqual",
          expected_value=0,
      ),
  )
  def test_compute_unfilled_area(
      self,
      width,
      height,
      assertion_method,
      expected_value,
      placement=None,
      mask=None,
  ):
    if placement is None:
      placement = []

    actual_area = utils_packing_flaps.compute_unfilled_area(
        width, height, placement, mask
    )

    if assertion_method == "assertEqual":
      self.assertEqual(actual_area, expected_value)
    elif assertion_method == "assertNotEqual":
      self.assertNotEqual(actual_area, expected_value)

  def test_set_grid_occupation(self):
    """Tests setting the occupation of a grid."""
    grid = np.full((4, 4), fill_value=False, dtype=bool)
    rect = shaping_utils.Rectangle(
        name="", x_start=0, y_start=0, x_len=2, y_len=2
    )
    utils_packing_flaps.set_grid_occupation(grid, rect, True)
    expected_grid = np.array(
        [
            [True, True, False, False],
            [True, True, False, False],
            [False, False, False, False],
            [False, False, False, False],
        ],
        dtype=bool,
    )
    self.assertTrue(np.array_equal(grid, expected_grid))

  def test_is_unoccupied(self):
    """Tests checking if a rectangle area is unoccupied."""
    grid = np.full((4, 4), fill_value=False, dtype=bool)
    rect = shaping_utils.Rectangle(
        name="", x_start=0, y_start=0, x_len=2, y_len=2
    )
    self.assertTrue(utils_packing_flaps.is_unoccupied(grid, rect))
    grid[0][0] = True
    self.assertFalse(utils_packing_flaps.is_unoccupied(grid, rect))


class GetFlapDimTest(parameterized.TestCase):

  @parameterized.named_parameters(
      dict(
          testcase_name="width_1",
          length=2,
          width=1,
          is_flap=True,
          expected=4,
      ),
      dict(
          testcase_name="width_2",
          length=2,
          width=2,
          is_flap=True,
          expected=4,
      ),
      dict(
          testcase_name="width_3",
          length=2,
          width=3,
          is_flap=True,
          expected=4,
      ),
  )
  def test_get_flap_dim(self, length, width, is_flap, expected):
    stick = stick_lib.Stick(
        name="test_stick",
        start="a",
        end="b",
        azimuth_angle=0,
        length=length,
        width=width,
    )
    stick.is_flap = is_flap
    dim = utils_packing_flaps.get_flap_dim(stick)
    self.assertEqual(dim, expected)


if __name__ == "__main__":
  absltest.main()
