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
from bp_pipeline import rectangle as shaping_utils
from bp_pipeline.packing import compute_hinges
from bp_pipeline.packing import river as river_lib
from bp_pipeline.packing import utils_tracker
import numpy as np


class GetRiverHingesTest(parameterized.TestCase):

  def test_hugging_river_hinges_1(self):
    grid_size = 8
    grid = np.zeros((grid_size, grid_size), dtype=bool)

    grid[0, 2] = True
    grid[0, 3] = True
    grid[0, 4] = True
    grid[0, 5] = True

    tracker = utils_tracker.CreasePatternTracker(grid_size)
    river = river_lib.HuggingRiver.from_contour(
        grid_size=grid_size,
        width=2,
        occupancy_grid=grid,
        start_cell=(0, 1),
        hug_side=river_lib.HugSide.LEFT,
    )
    tracker.add_river("river", river)

    result = compute_hinges.get_river_hinges(tracker, grid_size)
    expected_lines = [
        ((0.0, 0.0), (2.0, 0.0)),
        ((0.0, 0.0), (0.0, 3.0)),
        ((2.0, 0.0), (2.0, 1.0)),
        ((6.0, 0.0), (8.0, 0.0)),
        ((6.0, 0.0), (6.0, 1.0)),
        ((8.0, 0.0), (8.0, 3.0)),
        ((2.0, 1.0), (6.0, 1.0)),
        ((0.0, 3.0), (8.0, 3.0)),
        ((1.0, 0.0), (1.0, 1.0)),
        ((2.0, 2.0), (3.0, 2.0)),
        ((5.0, 2.0), (6.0, 2.0)),
        ((1.0, 2.0), (2.0, 2.0)),
        ((1.0, 1.0), (1.0, 2.0)),
        ((4.0, 2.0), (5.0, 2.0)),
        ((7.0, 0.0), (7.0, 1.0)),
        ((7.0, 1.0), (7.0, 2.0)),
        ((6.0, 2.0), (7.0, 2.0)),
        ((3.0, 2.0), (4.0, 2.0)),
    ]
    self.assertCountEqual(
        [tuple(sorted(s)) for s in result],
        [tuple(sorted(s)) for s in expected_lines],
    )

  def test_hugging_river_hinges_2(self):
    grid_size = 6
    grid = np.zeros((grid_size, grid_size), dtype=bool)

    grid[0, 1] = True
    grid[0, 2] = True
    grid[0, 3] = True
    grid[1, 3] = True
    grid[2, 3] = True
    grid[3, 3] = True
    tracker = utils_tracker.CreasePatternTracker(6)
    river = river_lib.HuggingRiver.from_contour(
        grid_size=6,
        width=1,
        occupancy_grid=grid,
        start_cell=(0, 0),
        hug_side=river_lib.HugSide.LEFT,
    )
    tracker.add_river("river", river)
    result = compute_hinges.get_river_hinges(tracker, grid_size)
    expected_lines = [
        ((0.0, 0.0), (1.0, 0.0)),
        ((0.0, 0.0), (0.0, 2.0)),
        ((1.0, 0.0), (1.0, 1.0)),
        ((4.0, 0.0), (5.0, 0.0)),
        ((4.0, 0.0), (4.0, 4.0)),
        ((5.0, 0.0), (5.0, 5.0)),
        ((0.0, 2.0), (2.0, 2.0)),
        ((1.0, 1.0), (3.0, 1.0)),
        ((3.0, 1.0), (3.0, 4.0)),
        ((2.0, 2.0), (2.0, 5.0)),
        ((2.0, 5.0), (5.0, 5.0)),
        ((3.0, 4.0), (4.0, 4.0)),
    ]
    self.assertCountEqual(
        [tuple(sorted(s)) for s in result],
        [tuple(sorted(s)) for s in expected_lines],
    )


class GetHingesBetweenLayersTest(parameterized.TestCase):

  def test_get_hinges_between_layers(self):
    river_width1 = river_lib.HuggingRiver(
        grid_size=1,
        width=1,
        subriver_paths=[[(0, 0)]],
        hug_side=river_lib.HugSide.LEFT,
    )

    grid_size = 8
    grid = np.zeros((grid_size, grid_size), dtype=bool)
    grid[0, 2] = True
    grid[0, 3] = True
    grid[0, 4] = True
    grid[0, 5] = True
    river_width2 = river_lib.HuggingRiver.from_contour(
        grid_size=grid_size,
        width=2,
        occupancy_grid=grid,
        start_cell=(0, 1),
        hug_side=river_lib.HugSide.LEFT,
    )

    river_width3 = river_lib.HuggingRiver(
        grid_size=2,
        width=3,
        subriver_paths=[
            [(0, 0)],
            [(0, 1)],
            [(1, 1)],
        ],
        hug_side=river_lib.HugSide.LEFT,
    )

    with self.subTest("width1"):
      result = compute_hinges._get_hinges_between_layers(river_width1)
      self.assertEmpty(result)

    with self.subTest("width2"):
      result = compute_hinges._get_hinges_between_layers(river_width2)
      expected = [
          ((1.0, 0.0), (1.0, 1.0)),
          ((2.0, 2.0), (3.0, 2.0)),
          ((5.0, 2.0), (6.0, 2.0)),
          ((1.0, 2.0), (2.0, 2.0)),
          ((1.0, 1.0), (1.0, 2.0)),
          ((4.0, 2.0), (5.0, 2.0)),
          ((7.0, 0.0), (7.0, 1.0)),
          ((7.0, 1.0), (7.0, 2.0)),
          ((6.0, 2.0), (7.0, 2.0)),
          ((3.0, 2.0), (4.0, 2.0)),
      ]
      self.assertCountEqual(
          [tuple(sorted(s)) for s in result],
          [tuple(sorted(s)) for s in expected],
      )

    with self.subTest("width3"):
      result = compute_hinges._get_hinges_between_layers(river_width3)
      expected = [
          ((1.0, 0.0), (1.0, 1.0)),  # layer 0->1: (0,0) adj (0,1) right
          ((1.0, 1.0), (2.0, 1.0)),  # layer 1->2: (0,1) adj (1,1) bottom
      ]
      self.assertCountEqual(
          [tuple(sorted(s)) for s in result],
          [tuple(sorted(s)) for s in expected],
      )


class GetHingesFor180TurnsTest(parameterized.TestCase):

  def test_closed_path_skips_wrap_but_keeps_real_hinge(self):
    river = river_lib.HuggingRiver(
        grid_size=3,
        width=1,
        subriver_paths=[
            [(0, 0), (0, 1), (0, 2), (1, 2), (1, 1), (1, 0)],
        ],
        hug_side=river_lib.HugSide.LEFT,
    )
    result = compute_hinges._get_hinges_for_180_turns(river)
    expected = [
        ((1, 1), (2, 1)),
    ]
    self.assertCountEqual(
        [tuple(sorted(s)) for s in result],
        [tuple(sorted(s)) for s in expected],
    )


class IsConsecutiveInPathTest(parameterized.TestCase):

  def test_is_consecutive_in_path(self):
    path = [(0, 0), (0, 1), (1, 1)]
    self.assertTrue(compute_hinges._is_consecutive_in_path(path, 0, (0, 1)))
    self.assertFalse(compute_hinges._is_consecutive_in_path(path, 0, (1, 1)))
    self.assertTrue(compute_hinges._is_consecutive_in_path(path, 1, (0, 0)))
    self.assertTrue(compute_hinges._is_consecutive_in_path(path, 1, (1, 1)))
    self.assertTrue(compute_hinges._is_consecutive_in_path(path, 2, (0, 1)))
    self.assertFalse(compute_hinges._is_consecutive_in_path(path, 2, (0, 0)))

  def test_is_consecutive_in_path_single_element(self):
    path = [(0, 0)]
    self.assertFalse(compute_hinges._is_consecutive_in_path(path, 0, (0, 1)))


class UnionBorderTest(parameterized.TestCase):

  def test_get_river_border(self):
    r1 = shaping_utils.Rectangle(
        name="r1", x_start=0.0, y_start=0.0, x_len=2.0, y_len=2.0
    )
    r2 = shaping_utils.Rectangle(
        name="r2", x_start=1.0, y_start=1.0, x_len=2.0, y_len=2.0
    )
    r3 = shaping_utils.Rectangle(
        name="r3", x_start=0.0, y_start=0.0, x_len=1.0, y_len=1.0
    )
    r4 = shaping_utils.Rectangle(
        name="r4", x_start=2.0, y_start=2.0, x_len=1.0, y_len=1.0
    )
    r5 = shaping_utils.Rectangle(
        name="r5", x_start=0.0, y_start=0.0, x_len=1.0, y_len=2.0
    )
    r6 = shaping_utils.Rectangle(
        name="r6", x_start=1.0, y_start=0.0, x_len=1.0, y_len=1.0
    )

    test_cases = [
        dict(
            testcase_name="empty",
            rects=[],
            grid_size=4,
            expected=[],
        ),
        dict(
            testcase_name="single",
            rects=[r1],
            grid_size=4,
            expected=[
                ((0.0, 0.0), (2.0, 0.0)),
                ((2.0, 0.0), (2.0, 2.0)),
                ((0.0, 2.0), (2.0, 2.0)),
                ((0.0, 0.0), (0.0, 2.0)),
            ],
        ),
        dict(
            testcase_name="disjoint",
            rects=[r3, r4],
            grid_size=4,
            expected=[
                ((0.0, 0.0), (1.0, 0.0)),
                ((1.0, 0.0), (1.0, 1.0)),
                ((0.0, 1.0), (1.0, 1.0)),
                ((0.0, 0.0), (0.0, 1.0)),
                ((2.0, 2.0), (3.0, 2.0)),
                ((3.0, 2.0), (3.0, 3.0)),
                ((2.0, 3.0), (3.0, 3.0)),
                ((2.0, 2.0), (2.0, 3.0)),
            ],
        ),
        dict(
            testcase_name="overlapping",
            rects=[r1, r2],
            grid_size=4,
            expected=[
                ((0.0, 0.0), (2.0, 0.0)),
                ((0.0, 0.0), (0.0, 2.0)),
                ((2.0, 0.0), (2.0, 1.0)),
                ((0.0, 2.0), (1.0, 2.0)),
                ((2.0, 1.0), (3.0, 1.0)),
                ((1.0, 2.0), (1.0, 3.0)),
                ((3.0, 1.0), (3.0, 3.0)),
                ((1.0, 3.0), (3.0, 3.0)),
            ],
        ),
        dict(
            testcase_name="L-shape",
            rects=[r5, r6],
            grid_size=3,
            expected=[
                ((0.0, 0.0), (2.0, 0.0)),
                ((0.0, 0.0), (0.0, 2.0)),
                ((2.0, 0.0), (2.0, 1.0)),
                ((1.0, 1.0), (2.0, 1.0)),
                ((1.0, 1.0), (1.0, 2.0)),
                ((0.0, 2.0), (1.0, 2.0)),
            ],
        ),
    ]

    for params in test_cases:
      with self.subTest(params["testcase_name"]):
        result = compute_hinges.get_river_border(
            params["rects"], params["grid_size"]
        )
        self.assertCountEqual(
            [tuple(sorted(s)) for s in result],
            [tuple(sorted(s)) for s in params["expected"]],
        )


if __name__ == "__main__":
  absltest.main()
