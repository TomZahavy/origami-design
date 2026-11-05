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

import copy

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline import rectangle as shaping_utils
from bp_pipeline.packing import compute_ridges
from bp_pipeline.packing import config as config_lib
from bp_pipeline.packing import river as river_lib
from bp_pipeline.packing import types
from bp_pipeline.packing import utils_solver
from bp_pipeline.packing import utils_tracker
from bp_pipeline.stick_figures import stick as stick_lib
from bp_pipeline.stick_figures.examples import example_trees
import numpy as np


class RidgeGenerationTest(parameterized.TestCase):

  @parameterized.named_parameters(
      dict(
          testcase_name="square_ridge",
          rect_x=0,
          rect_y=0,
          width=10,
          height=10,
          grid_size=30,
          y_ridge_at_border=False,
          expected_lines=[
              ((0, 0), (10, 10)),
              ((10, 0), (0, 10)),
          ],
      ),
      dict(
          testcase_name="wide_rectangle_ridge",
          rect_x=5,
          rect_y=5,
          width=20,
          height=10,
          grid_size=30,
          y_ridge_at_border=False,
          expected_lines=[
              ((5, 5), (10, 10)),  # Top-left to merge
              ((25, 5), (20, 10)),  # Top-right to merge
              ((25, 15), (20, 10)),  # Bottom-right to merge
              ((5, 15), (10, 10)),  # Bottom-left to merge
              ((10, 10), (20, 10)),  # Central horizontal line
          ],
      ),
      dict(
          testcase_name="tall_rectangle_ridge",
          rect_x=5,
          rect_y=5,
          width=10,
          height=20,
          grid_size=30,
          y_ridge_at_border=False,
          expected_lines=[
              ((5, 5), (10, 10)),  # Top-left to merge
              ((15, 5), (10, 10)),  # Top-right to merge
              ((15, 25), (10, 20)),  # Bottom-right to merge
              ((5, 25), (10, 20)),  # Bottom-left to merge
              ((10, 10), (10, 20)),  # Central vertical line
          ],
      ),
      dict(
          testcase_name="wide_rect_touch_left_border",
          rect_x=0,
          rect_y=0,
          width=20,
          height=10,
          grid_size=30,
          y_ridge_at_border=True,
          expected_lines=[
              ((0, 5), (5, 5)),  # Y-shape on left
              ((20, 0), (15, 5)),  # Top-right to merge
              ((20, 10), (15, 5)),  # Bottom-right to merge
              ((5, 5), (15, 5)),  # Central horizontal line
          ],
      ),
      dict(
          testcase_name="wide_rect_touch_right_border",
          rect_x=10,
          rect_y=0,
          width=20,
          height=10,
          grid_size=30,
          y_ridge_at_border=True,
          expected_lines=[
              ((10, 0), (15, 5)),  # Top-left to merge
              ((10, 10), (15, 5)),  # Bottom-left to merge
              ((30, 5), (25, 5)),  # Y-shape on right
              ((15, 5), (25, 5)),  # Central horizontal line
          ],
      ),
      dict(
          testcase_name="tall_rect_touch_top_border",
          rect_x=0,
          rect_y=0,
          width=10,
          height=20,
          grid_size=30,
          y_ridge_at_border=True,
          expected_lines=[
              ((5, 0), (5, 5)),  # Y-shape on top
              ((0, 20), (5, 15)),  # Bottom-left to merge
              ((10, 20), (5, 15)),  # Bottom-right to merge
              ((5, 5), (5, 15)),  # Central vertical line
          ],
      ),
      dict(
          testcase_name="tall_rect_touch_bottom_border",
          rect_x=0,
          rect_y=10,
          width=10,
          height=20,
          grid_size=30,
          y_ridge_at_border=True,
          expected_lines=[
              ((0, 10), (5, 15)),  # Top-left to merge
              ((10, 10), (5, 15)),  # Top-right to merge
              ((5, 30), (5, 25)),  # Y-shape on bottom
              ((5, 15), (5, 25)),  # Central vertical line
          ],
      ),
      dict(
          testcase_name="tall_rect_crossing_top_left_border_y_ridge",
          rect_x=-1,
          rect_y=-1,
          width=4,
          height=6,
          grid_size=10,
          y_ridge_at_border=True,
          expected_lines=[
              ((1.0, -1.0), (1.0, 1.0)),
              ((-1.0, 5.0), (1.0, 3.0)),
              ((3.0, 5.0), (1.0, 3.0)),
              ((1.0, 1.0), (1.0, 3.0)),
          ],
      ),
      dict(
          testcase_name="wide_rect_crossing_top_left_border_y_ridge",
          rect_x=-1,
          rect_y=-1,
          width=6,
          height=4,
          grid_size=10,
          y_ridge_at_border=True,
          expected_lines=[
              ((-1.0, 1.0), (1.0, 1.0)),
              ((5.0, -1.0), (3.0, 1.0)),
              ((5.0, 3.0), (3.0, 1.0)),
              ((1.0, 1.0), (3.0, 1.0)),
          ],
      ),
      dict(
          testcase_name="wide_rect_crossing_top_border_no_y_ridge",
          rect_x=1,
          rect_y=-1,
          width=6,
          height=4,
          grid_size=10,
          y_ridge_at_border=True,
          expected_lines=[
              ((1.0, -1.0), (3.0, 1.0)),
              ((1.0, 3.0), (3.0, 1.0)),
              ((7.0, -1.0), (5.0, 1.0)),
              ((7.0, 3.0), (5.0, 1.0)),
              ((3.0, 1.0), (5.0, 1.0)),
          ],
      ),
      dict(
          testcase_name="wide_rect_touching_top_border_no_y_ridge",
          rect_x=1,
          rect_y=0,
          width=6,
          height=4,
          grid_size=10,
          y_ridge_at_border=True,
          expected_lines=[
              ((1.0, 0.0), (3.0, 2.0)),
              ((1.0, 4.0), (3.0, 2.0)),
              ((7.0, 0.0), (5.0, 2.0)),
              ((7.0, 4.0), (5.0, 2.0)),
              ((3.0, 2.0), (5.0, 2.0)),
          ],
      ),
      dict(
          testcase_name="square_not_touch_border_y_ridge_true",
          rect_x=10,
          rect_y=10,
          width=10,
          height=10,
          grid_size=40,
          y_ridge_at_border=True,
          expected_lines=[
              ((10, 10), (20, 20)),
              ((20, 10), (10, 20)),
          ],
      ),
      dict(
          testcase_name="square_touch_top_border_y_ridge",
          rect_x=10,
          rect_y=0,
          width=10,
          height=10,
          grid_size=30,
          y_ridge_at_border=True,
          expected_lines=[
              ((15, 0), (15, 5)),
              ((10, 10), (15, 5)),
              ((20, 10), (15, 5)),
          ],
      ),
      dict(
          testcase_name="square_touch_left_border_y_ridge",
          rect_x=0,
          rect_y=10,
          width=10,
          height=10,
          grid_size=30,
          y_ridge_at_border=True,
          expected_lines=[
              ((0, 15), (5, 15)),
              ((10, 10), (5, 15)),
              ((10, 20), (5, 15)),
          ],
      ),
      dict(
          testcase_name="square_touch_top_left_corner_y_ridge",
          rect_x=0,
          rect_y=0,
          width=10,
          height=10,
          grid_size=30,
          y_ridge_at_border=True,
          expected_lines=[
              ((0, 5), (5, 5)),
              ((10, 0), (5, 5)),
              ((10, 10), (5, 5)),
          ],
      ),
      dict(
          testcase_name="square_overlap_top_border_y_ridge",
          rect_x=10,
          rect_y=-2,
          width=10,
          height=10,
          grid_size=30,
          y_ridge_at_border=True,
          expected_lines=[
              ((15, -2), (15, 3)),
              ((10, 8), (15, 3)),
              ((20, 8), (15, 3)),
          ],
      ),
      dict(
          testcase_name="square_overlap_top_left_corner_y_ridge",
          rect_x=-2,
          rect_y=-2,
          width=10,
          height=10,
          grid_size=30,
          y_ridge_at_border=True,
          expected_lines=[
              ((-2, 3), (3, 3)),
              ((8, -2), (3, 3)),
              ((8, 8), (3, 3)),
          ],
      ),
      dict(
          testcase_name="center_on_left_border_y_ridge",
          rect_x=-2,
          rect_y=-1,
          width=4,
          height=4,
          grid_size=8,
          y_ridge_at_border=True,
          expected_lines=[
              ((-2, 3), (0, 1)),
              ((2, 3), (0, 1)),
              ((0, -1), (0, 1)),
          ],
      ),
      dict(
          testcase_name="center_on_top_left_corner_y_ridge",
          rect_x=-2,
          rect_y=-2,
          width=4,
          height=4,
          grid_size=8,
          y_ridge_at_border=True,
          expected_lines=[
              ((-2, -2), (2, 2)),
              ((2, -2), (-2, 2)),
          ],
      ),
      dict(
          testcase_name="center_on_top_border_y_ridge",
          rect_x=-1,
          rect_y=-2,
          width=4,
          height=4,
          grid_size=8,
          y_ridge_at_border=True,
          expected_lines=[
              ((3, -2), (1, 0)),
              ((3, 2), (1, 0)),
              ((-1, 0), (1, 0)),
          ],
      ),
  )
  def test_get_rectangle_ridge_lines(
      self,
      rect_x,
      rect_y,
      width,
      height,
      grid_size,
      y_ridge_at_border,
      expected_lines,
  ):
    """Tests the ridge crease calculation for different rectangle types."""
    rect = shaping_utils.Rectangle(
        name="test",
        x_start=float(rect_x),
        y_start=float(rect_y),
        x_len=float(width),
        y_len=float(height),
    )
    result = compute_ridges.get_ridge_lines(
        rect, grid_size=grid_size, y_ridge_at_border=y_ridge_at_border
    )
    self.assertLen(result, len(expected_lines))
    result_set = {tuple(sorted(line)) for line in result}
    expected_set = {tuple(sorted(line)) for line in expected_lines}
    self.assertSetEqual(result_set, expected_set)

  def test_square_touching_border_is_y_ridge(self):
    """Explicitly tests that a square touching a border gets a Y-ridge."""
    rect = shaping_utils.Rectangle(
        name="test_square", x_start=10, y_start=0, x_len=10, y_len=10
    )
    grid_size = 30
    result = compute_ridges.get_ridge_lines(rect, grid_size=grid_size)

    expected_y_shape = {
        tuple(sorted(((15.0, 0.0), (15.0, 5.0)))),
        tuple(sorted(((10.0, 10.0), (15.0, 5.0)))),
        tuple(sorted(((20.0, 10.0), (15.0, 5.0)))),
    }

    expected_x_shape = {
        tuple(sorted(((10.0, 0.0), (20.0, 10.0)))),
        tuple(sorted(((20.0, 0.0), (10.0, 10.0)))),
    }

    result_set = {tuple(sorted(line)) for line in result}

    self.assertSetEqual(result_set, expected_y_shape)
    self.assertNotEqual(result_set, expected_x_shape)

  def test_compute_ridges_for_rectangles(self):
    """Tests the main function that computes ridges for a tracker object."""
    tracker = utils_tracker.CreasePatternTracker(20)
    tracker.add_polygon(
        "p1_square",
        types.PolygonPlacement.from_grid_coords(
            offset=(0, 0), size=(10, 10), grid_size=20
        ),
    )
    tracker.add_polygon(
        "p2_wide",
        types.PolygonPlacement.from_grid_coords(
            offset=(10, 10), size=(8, 4), grid_size=20
        ),
    )

    result = compute_ridges.compute_ridges_for_rectangles(tracker)

    self.assertIn("p1_square", result)
    self.assertIn("p2_wide", result)

    expected_square_ridge = {
        tuple(sorted(((0.0, 5.0), (5.0, 5.0)))),
        tuple(sorted(((10.0, 0.0), (5.0, 5.0)))),
        tuple(sorted(((10.0, 10.0), (5.0, 5.0)))),
    }
    result_square_ridge = {tuple(sorted(line)) for line in result["p1_square"]}
    self.assertSetEqual(result_square_ridge, expected_square_ridge)

    expected_wide_ridge = {
        tuple(sorted(((10, 10), (12, 12)))),
        tuple(sorted(((18, 10), (16, 12)))),
        tuple(sorted(((18, 14), (16, 12)))),
        tuple(sorted(((10, 14), (12, 12)))),
        tuple(sorted(((12, 12), (16, 12)))),
    }
    result_wide_ridge = {tuple(sorted(line)) for line in result["p2_wide"]}
    self.assertSetEqual(result_wide_ridge, expected_wide_ridge)

  def test_compute_ridges_for_rectangles_no_y_ridge(self):
    """Tests compute_ridges_for_rectangles with y_ridge_at_border=False."""
    tracker = utils_tracker.CreasePatternTracker(20)
    tracker.add_polygon(
        "p1_square",
        types.PolygonPlacement.from_grid_coords(
            offset=(0, 0), size=(10, 10), grid_size=20
        ),
    )
    tracker.add_polygon(
        "p2_wide",
        types.PolygonPlacement.from_grid_coords(
            offset=(0, 10), size=(10, 6), grid_size=20
        ),
    )

    result = compute_ridges.compute_ridges_for_rectangles(
        tracker, y_ridge_at_border=False
    )

    self.assertIn("p1_square", result)
    self.assertIn("p2_wide", result)

    expected_square_ridge = {
        tuple(sorted(((0.0, 0.0), (10.0, 10.0)))),
        tuple(sorted(((10.0, 0.0), (0.0, 10.0)))),
    }
    result_square_ridge = {tuple(sorted(line)) for line in result["p1_square"]}
    self.assertSetEqual(result_square_ridge, expected_square_ridge)

    expected_wide_ridge = {
        tuple(sorted(((0.0, 13.0), (3.0, 13.0)))),
        tuple(sorted(((3.0, 13.0), (7.0, 13.0)))),
        tuple(sorted(((10.0, 10.0), (7.0, 13.0)))),
        tuple(sorted(((10.0, 16.0), (7.0, 13.0)))),
    }
    result_wide_ridge = {tuple(sorted(line)) for line in result["p2_wide"]}
    self.assertSetEqual(result_wide_ridge, expected_wide_ridge)

  def test_compute_ridges_for_empty_placement(self):
    """Ensures the function handles None or empty trackers gracefully."""
    self.assertEmpty(compute_ridges.compute_ridges_for_rectangles(None))

    empty_tracker = utils_tracker.CreasePatternTracker(10)
    self.assertEmpty(
        compute_ridges.compute_ridges_for_rectangles(empty_tracker)
    )


class RiverRidgeGenerationTest(parameterized.TestCase):

  @parameterized.named_parameters(
      dict(
          testcase_name="bottom_left",
          l_shape_type=river_lib.LShapeType.BOTTOM_LEFT,
          expected_lines=[((2.0, 2.0), (3.0, 3.0))],
      ),
      dict(
          testcase_name="bottom_right",
          l_shape_type=river_lib.LShapeType.BOTTOM_RIGHT,
          expected_lines=[((3.0, 2.0), (2.0, 3.0))],
      ),
      dict(
          testcase_name="top_left",
          l_shape_type=river_lib.LShapeType.TOP_LEFT,
          expected_lines=[((2.0, 3.0), (3.0, 2.0))],
      ),
      dict(
          testcase_name="top_right",
          l_shape_type=river_lib.LShapeType.TOP_RIGHT,
          expected_lines=[((3.0, 3.0), (2.0, 2.0))],
      ),
  )
  def test_get_l_shaped_river_ridge_lines(self, l_shape_type, expected_lines):
    river = river_lib.LShapedRiver(
        width=1, grid_size=5, l_shape_type=l_shape_type, turn_x=2, turn_y=2
    )
    result = compute_ridges.get_river_ridge_lines(river)
    self.assertLen(result, len(expected_lines))
    result_set = {tuple(sorted(line)) for line in result}
    expected_set = {tuple(sorted(line)) for line in expected_lines}
    self.assertSetEqual(result_set, expected_set)

  def test_get_straight_river_ridge_lines(self):
    river = river_lib.River(
        width=1,
        offset=0,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=5,
    )
    result = compute_ridges.get_river_ridge_lines(river)
    self.assertEmpty(result)

  def test_get_hugging_river_ridge_lines_l_shape(self):
    grid_size = 6
    occupancy_grid = np.zeros((6, 6), dtype=bool)
    occupancy_grid[0, 1:4] = True
    occupancy_grid[1:4, 3] = True
    start_cell = (0, 0)
    hug_side = river_lib.HugSide.LEFT
    width = 1
    river = river_lib.HuggingRiver.from_contour(
        grid_size=grid_size,
        width=width,
        occupancy_grid=occupancy_grid,
        start_cell=start_cell,
        hug_side=hug_side,
    )
    result = compute_ridges.get_river_ridge_lines(river)
    expected_lines = [
        ((0.0, 2.0), (1.0, 1.0)),
        ((2.0, 2.0), (3.0, 1.0)),
        ((2.0, 5.0), (3.0, 4.0)),
        ((4.0, 4.0), (5.0, 5.0)),
    ]
    self.assertLen(result, len(expected_lines))
    result_set = {tuple(sorted(line)) for line in result}
    expected_set = {tuple(sorted(line)) for line in expected_lines}
    self.assertSetEqual(result_set, expected_set)

  def test_get_hugging_river_ridge_lines_right_turn(self):
    river = river_lib.HuggingRiver(
        grid_size=3,
        width=1,
        subriver_paths=[[(0, 1), (1, 1), (1, 0)]],
        hug_side=river_lib.HugSide.RIGHT,
    )
    result = compute_ridges.get_river_ridge_lines(river)
    expected_lines = [((1.0, 1.0), (2.0, 2.0))]
    self.assertLen(result, len(expected_lines))
    result_set = {tuple(sorted(line)) for line in result}
    expected_set = {tuple(sorted(line)) for line in expected_lines}
    self.assertSetEqual(result_set, expected_set)

  def test_get_hugging_river_ridge_lines_left_turn(self):
    river = river_lib.HuggingRiver(
        grid_size=3,
        width=1,
        subriver_paths=[[(1, 0), (1, 1), (0, 1)]],
        hug_side=river_lib.HugSide.LEFT,
    )
    result = compute_ridges.get_river_ridge_lines(river)
    expected_lines = [((1.0, 1.0), (2.0, 2.0))]
    self.assertLen(result, len(expected_lines))
    result_set = {tuple(sorted(line)) for line in result}
    expected_set = {tuple(sorted(line)) for line in expected_lines}
    self.assertSetEqual(result_set, expected_set)

  def test_get_hugging_river_internal_turn_ridges(self):
    path = [(0, 1), (1, 1), (1, 0)]
    result = compute_ridges._get_hugging_river_internal_turn_ridges(path)
    expected_set = {((1.0, 1.0), (2.0, 2.0))}
    self.assertLen(result, len(expected_set))
    result_set = {tuple(sorted(line)) for line in result}
    self.assertSetEqual(result_set, expected_set)

  def test_closed_path_gets_wrap_ridges_and_skips_endpoints(self):
    river = river_lib.HuggingRiver(
        grid_size=3,
        width=1,
        subriver_paths=[
            [(0, 0), (0, 1), (0, 2), (1, 2), (1, 1), (1, 0)],
        ],
        hug_side=river_lib.HugSide.LEFT,
    )
    result = compute_ridges.get_river_ridge_lines(river)
    expected_lines = [
        ((2.0, 1.0), (3.0, 0.0)),
        ((2.0, 1.0), (3.0, 2.0)),
        ((0.0, 0.0), (1.0, 1.0)),
        ((0.0, 2.0), (1.0, 1.0)),
    ]
    self.assertLen(result, len(expected_lines))
    result_set = {tuple(sorted(line)) for line in result}
    expected_set = {tuple(sorted(line)) for line in expected_lines}
    self.assertSetEqual(result_set, expected_set)

  def test_hugging_river_border_example_1(self):
    grid_size = 5
    occupancy_grid = np.zeros((grid_size, grid_size), dtype=bool)
    occupancy_grid[1, 0] = True
    occupancy_grid[0, 0] = True
    occupancy_grid[1, 1] = True
    river = river_lib.HuggingRiver.from_contour(
        grid_size=grid_size,
        width=1,
        occupancy_grid=occupancy_grid,
        start_cell=(2, 0),
        hug_side=river_lib.HugSide.LEFT,
    )
    expected_path = [(2, 0), (2, 1), (2, 2), (1, 2), (0, 2), (0, 1)]
    self.assertEqual(river.subriver_paths[0], expected_path)
    result = compute_ridges.get_river_ridge_lines(river)
    expected_lines = [
        ((1.0, 1.0), (2.0, 0.0)),
        ((2.0, 2.0), (3.0, 3.0)),
        ((2.0, 1.0), (3.0, 0.0)),
    ]
    self.assertLen(result, len(expected_lines))
    result_set = {tuple(sorted(line)) for line in result}
    expected_set = {tuple(sorted(line)) for line in expected_lines}
    self.assertSetEqual(result_set, expected_set)

  def test_hugging_river_border_example_2(self):
    grid_size = 5
    occupancy_grid = np.zeros((grid_size, grid_size), dtype=bool)
    occupancy_grid[1, 0] = True
    occupancy_grid[0, 0] = True
    occupancy_grid[2, 1] = True
    occupancy_grid[3, 1] = True
    occupancy_grid[1, 1] = True
    river = river_lib.HuggingRiver.from_contour(
        grid_size=grid_size,
        width=1,
        occupancy_grid=occupancy_grid,
        start_cell=(2, 0),
        hug_side=river_lib.HugSide.LEFT,
    )
    expected_path = [
        (2, 0),
        (3, 0),
        (4, 0),
        (4, 1),
        (4, 2),
        (3, 2),
        (2, 2),
        (1, 2),
        (0, 2),
        (0, 1),
    ]
    self.assertEqual(river.subriver_paths[0], expected_path)
    result = compute_ridges.get_river_ridge_lines(river)
    expected_lines = [
        ((0.0, 3.0), (1.0, 2.0)),
        ((1.0, 1.0), (2.0, 0.0)),
        ((0.0, 5.0), (1.0, 4.0)),
        ((2.0, 4.0), (3.0, 5.0)),
        ((2.0, 1.0), (3.0, 0.0)),
    ]
    self.assertLen(result, len(expected_lines))
    result_set = {tuple(sorted(line)) for line in result}
    expected_set = {tuple(sorted(line)) for line in expected_lines}
    self.assertSetEqual(result_set, expected_set)

  def test_hugging_river_border_example_3(self):
    grid_size = 5
    occupancy_grid = np.zeros((grid_size, grid_size), dtype=bool)
    occupancy_grid[1, 0] = True
    occupancy_grid[0, 0] = True
    occupancy_grid[2, 1] = True
    occupancy_grid[3, 1] = True
    occupancy_grid[1, 1] = True
    occupancy_grid[4, 2] = True
    river = river_lib.HuggingRiver.from_contour(
        grid_size=grid_size,
        width=1,
        occupancy_grid=occupancy_grid,
        start_cell=(2, 0),
        hug_side=river_lib.HugSide.LEFT,
    )
    expected_path = [(2, 0), (3, 0), (4, 0), (4, 1)]
    self.assertEqual(river.subriver_paths[0], expected_path)
    result = compute_ridges.get_river_ridge_lines(river)
    expected_lines = [
        ((0.0, 3.0), (1.0, 2.0)),
        ((1.0, 5.0), (2.0, 4.0)),
        ((0.0, 5.0), (1.0, 4.0)),
    ]
    self.assertLen(result, len(expected_lines))
    result_set = {tuple(sorted(line)) for line in result}
    expected_set = {tuple(sorted(line)) for line in expected_lines}
    self.assertSetEqual(result_set, expected_set)

  def test_hugging_river_border_example_4(self):
    grid_size = 5
    occupancy_grid = np.zeros((grid_size, grid_size), dtype=bool)
    occupancy_grid[3, 3] = True
    occupancy_grid[3, 4] = True
    occupancy_grid[2, 3] = True
    occupancy_grid[1, 3] = True
    occupancy_grid[1, 2] = True
    occupancy_grid[1, 1] = True
    occupancy_grid[0, 1] = True
    river = river_lib.HuggingRiver.from_contour(
        grid_size=grid_size,
        width=1,
        occupancy_grid=occupancy_grid,
        start_cell=(2, 4),
        hug_side=river_lib.HugSide.LEFT,
    )
    expected_path = [(2, 4), (1, 4), (0, 4), (0, 3), (0, 2)]
    self.assertEqual(river.subriver_paths[0], expected_path)
    result = compute_ridges.get_river_ridge_lines(river)
    expected_lines = [
        ((4.0, 3.0), (5.0, 2.0)),
        ((2.0, 1.0), (3.0, 0.0)),
        ((4.0, 1.0), (5.0, 0.0)),
    ]
    self.assertLen(result, len(expected_lines))
    result_set = {tuple(sorted(line)) for line in result}
    expected_set = {tuple(sorted(line)) for line in expected_lines}
    self.assertSetEqual(result_set, expected_set)


class IsSegmentOnBorderEdgeTest(absltest.TestCase):

  def test_border_edge_horizontal(self):
    self.assertTrue(
        compute_ridges._is_segment_on_border_edge(
            cell_to_check=(0, 1), segment_neighbor=(0, 2), grid_size=4
        )
    )
    self.assertTrue(
        compute_ridges._is_segment_on_border_edge(
            cell_to_check=(3, 1), segment_neighbor=(3, 2), grid_size=4
        )
    )

  def test_border_edge_vertical(self):
    self.assertTrue(
        compute_ridges._is_segment_on_border_edge(
            cell_to_check=(1, 0), segment_neighbor=(2, 0), grid_size=4
        )
    )
    self.assertTrue(
        compute_ridges._is_segment_on_border_edge(
            cell_to_check=(1, 3), segment_neighbor=(2, 3), grid_size=4
        )
    )

  def test_corner_cell1(self):
    self.assertFalse(
        compute_ridges._is_segment_on_border_edge(
            cell_to_check=(0, 0), segment_neighbor=(0, 1), grid_size=4
        )
    )
    self.assertFalse(
        compute_ridges._is_segment_on_border_edge(
            cell_to_check=(0, 3), segment_neighbor=(0, 2), grid_size=4
        )
    )
    self.assertFalse(
        compute_ridges._is_segment_on_border_edge(
            cell_to_check=(3, 0), segment_neighbor=(3, 1), grid_size=4
        )
    )
    self.assertFalse(
        compute_ridges._is_segment_on_border_edge(
            cell_to_check=(3, 3), segment_neighbor=(3, 2), grid_size=4
        )
    )

  def test_cell1_not_on_border(self):
    self.assertFalse(
        compute_ridges._is_segment_on_border_edge(
            cell_to_check=(1, 1), segment_neighbor=(1, 2), grid_size=4
        )
    )

  def test_segment_not_on_border(self):
    self.assertFalse(
        compute_ridges._is_segment_on_border_edge(
            cell_to_check=(0, 1), segment_neighbor=(1, 1), grid_size=4
        )
    )


class AddRidgesForSquareTest(parameterized.TestCase):

  @parameterized.named_parameters(
      dict(
          testcase_name="no_border_contact",
          x_start=5,
          y_start=5,
          size=10,
          apply_y_ridge=True,
          expected_lines=[((5, 5), (15, 15)), ((15, 5), (5, 15))],
      ),
      dict(
          testcase_name="no_border_contact_y_ridge_false",
          x_start=5,
          y_start=5,
          size=10,
          apply_y_ridge=False,
          expected_lines=[((5, 5), (15, 15)), ((15, 5), (5, 15))],
      ),
      dict(
          testcase_name="touch_left_border",
          x_start=0,
          y_start=5,
          size=10,
          apply_y_ridge=True,
          expected_lines=[
              ((0, 10), (5, 10)),
              ((10, 5), (5, 10)),
              ((10, 15), (5, 10)),
          ],
      ),
      dict(
          testcase_name="touch_right_border",
          x_start=10,
          y_start=5,
          size=10,
          apply_y_ridge=True,
          expected_lines=[
              ((10, 5), (15, 10)),
              ((10, 15), (15, 10)),
              ((20, 10), (15, 10)),
          ],
      ),
      dict(
          testcase_name="touch_top_border",
          x_start=5,
          y_start=0,
          size=10,
          apply_y_ridge=True,
          expected_lines=[
              ((10, 0), (10, 5)),
              ((5, 10), (10, 5)),
              ((15, 10), (10, 5)),
          ],
      ),
      dict(
          testcase_name="touch_bottom_border",
          x_start=5,
          y_start=10,
          size=10,
          apply_y_ridge=True,
          expected_lines=[
              ((5, 10), (10, 15)),
              ((15, 10), (10, 15)),
              ((10, 20), (10, 15)),
          ],
      ),
      dict(
          testcase_name="touch_top_left_corner",
          x_start=0,
          y_start=0,
          size=10,
          apply_y_ridge=True,
          expected_lines=[
              ((0, 5), (5, 5)),
              ((10, 0), (5, 5)),
              ((10, 10), (5, 5)),
          ],
      ),
      dict(
          testcase_name="touch_bottom_right_corner",
          x_start=10,
          y_start=10,
          size=10,
          apply_y_ridge=True,
          expected_lines=[
              ((10, 10), (15, 15)),
              ((10, 20), (15, 15)),
              ((20, 15), (15, 15)),
          ],
      ),
      dict(
          testcase_name="touch_left_border_y_ridge_false",
          x_start=0,
          y_start=5,
          size=10,
          apply_y_ridge=False,
          expected_lines=[((0, 5), (10, 15)), ((10, 5), (0, 15))],
      ),
  )
  def test_add_ridges_for_square(
      self, x_start, y_start, size, apply_y_ridge, expected_lines
  ):
    lines = []
    rect = shaping_utils.Rectangle(
        name="square",
        x_start=float(x_start),
        y_start=float(y_start),
        x_len=float(size),
        y_len=float(size),
    )

    touch_left = x_start == 0
    touch_right = x_start + size == 20
    touch_top = y_start == 0
    touch_bottom = y_start + size == 20

    center_x, center_y = rect.center
    (
        top_left_p,
        top_right_p,
        bottom_right_p,
        bottom_left_p,
    ) = rect.corners
    top_left = (top_left_p.x, top_left_p.y)
    top_right = (top_right_p.x, top_right_p.y)
    bottom_right = (bottom_right_p.x, bottom_right_p.y)
    bottom_left = (bottom_left_p.x, bottom_left_p.y)
    compute_ridges._add_ridges_for_square(
        lines=lines,
        rectangle=rect,
        touch_left=touch_left,
        touch_right=touch_right,
        touch_top=touch_top,
        touch_bottom=touch_bottom,
        apply_y_ridge=apply_y_ridge,
        center_x=center_x,
        center_y=center_y,
        top_left=top_left,
        top_right=top_right,
        bottom_right=bottom_right,
        bottom_left=bottom_left,
        grid_size=20,
    )
    result_set = {tuple(sorted(line)) for line in lines}
    expected_set = {tuple(sorted(line)) for line in expected_lines}
    self.assertSetEqual(result_set, expected_set)

  def test_hugging_river_ridges_border(self):
    grid_size = 5
    tracker_ex = utils_tracker.CreasePatternTracker(grid_size)
    sq1_placement = types.PolygonPlacement.from_grid_coords(
        offset=(4, -1), size=(2, 2), grid_size=grid_size
    )
    tracker_ex.add_polygon("sq1", sq1_placement)
    sq2_placement = types.PolygonPlacement.from_grid_coords(
        offset=(2, 1), size=(6, 6), grid_size=grid_size
    )
    tracker_ex.add_polygon("sq2", sq2_placement)
    hugging_river = river_lib.HuggingRiver.from_contour(
        grid_size=grid_size,
        width=1,
        occupancy_grid=tracker_ex.occupancy_grid,
        start_cell=(0, 3),
        hug_side=river_lib.HugSide.LEFT,
    )
    river_ridges = compute_ridges.get_river_ridge_lines(hugging_river)
    expected_ridges = [
        ((3.0, 0.0), (4.0, 1.0)),
        ((1.0, 0.0), (2.0, 1.0)),
    ]
    self.assertLen(river_ridges, 2)
    result_set = {tuple(sorted(line)) for line in river_ridges}
    expected_set = {tuple(sorted(line)) for line in expected_ridges}
    self.assertSetEqual(result_set, expected_set)


class ComputeFlapShapesTest(parameterized.TestCase):

  def test_square_not_touching_border_is_triangular(self):
    tracker = utils_tracker.CreasePatternTracker(20)
    tracker.add_polygon(
        "sq_interior",
        types.PolygonPlacement.from_grid_coords(
            offset=(5, 5), size=(10, 10), grid_size=20
        ),
    )
    result = compute_ridges.compute_flap_shapes(tracker)
    self.assertEqual(result["sq_interior"], stick_lib.FlapTipShape.TRIANGULAR)

  def test_square_touching_border_is_rectangular(self):
    tracker = utils_tracker.CreasePatternTracker(30)
    tracker.add_polygon(
        "sq_border",
        types.PolygonPlacement.from_grid_coords(
            offset=(10, 0), size=(10, 10), grid_size=30
        ),
    )
    result = compute_ridges.compute_flap_shapes(tracker)
    self.assertEqual(result["sq_border"], stick_lib.FlapTipShape.RECTANGULAR)

  def test_square_center_on_corner_is_triangular(self):
    tracker = utils_tracker.CreasePatternTracker(5)
    tracker.add_polygon(
        "sq_corner",
        types.PolygonPlacement.from_grid_coords(
            offset=(0, 0), size=(10, 10), grid_size=5
        ),
    )
    rect = shaping_utils.Rectangle(
        name="sq_corner", x_start=0.0, y_start=0.0, x_len=10.0, y_len=10.0
    )
    self.assertTrue(rect.is_center_on_corner(5))
    result = compute_ridges.compute_flap_shapes(tracker)
    self.assertEqual(result["sq_corner"], stick_lib.FlapTipShape.TRIANGULAR)

  def test_wide_rectangle_is_rectangular(self):
    tracker = utils_tracker.CreasePatternTracker(20)
    tracker.add_polygon(
        "wide_rect",
        types.PolygonPlacement.from_grid_coords(
            offset=(0, 5), size=(20, 10), grid_size=20
        ),
    )
    result = compute_ridges.compute_flap_shapes(tracker)
    self.assertEqual(result["wide_rect"], stick_lib.FlapTipShape.RECTANGULAR)

  def test_tall_rectangle_is_rectangular(self):
    tracker = utils_tracker.CreasePatternTracker(20)
    tracker.add_polygon(
        "tall_rect",
        types.PolygonPlacement.from_grid_coords(
            offset=(5, 0), size=(10, 20), grid_size=20
        ),
    )
    result = compute_ridges.compute_flap_shapes(tracker)
    self.assertEqual(result["tall_rect"], stick_lib.FlapTipShape.RECTANGULAR)

  def test_none_tracker_returns_empty(self):
    result = compute_ridges.compute_flap_shapes(None)
    self.assertEmpty(result)


class FlapTipShapeIntegrationTest(parameterized.TestCase):

  def _run_packing(self, stickfigure, grid_size, is_symmetric=False):
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        stickfigure,
        grid_size=grid_size,
        is_symmetric=is_symmetric,
        config=config_lib.PackingConfig(
            enforce_proximity_constraints=False,
        ),
    )
    self.assertTrue(packing_outputs)
    self.assertTrue(packing_outputs[0].success)
    return packing_outputs[0]

  def _get_flap_shapes(self, packing):
    tree = packing.stick_figure
    self.assertIsNotNone(tree)
    return {s.name: s.flap_tip_shape for s in tree.children if s.is_flap}

  def test_human_simple_asymmetric_grid_11(self):
    tree = copy.deepcopy(example_trees.HUMAN_SIMPLE)
    packing = self._run_packing(tree, grid_size=11, is_symmetric=False)
    shapes = self._get_flap_shapes(packing)
    self.assertEqual(shapes["head"], stick_lib.FlapTipShape.RECTANGULAR)
    self.assertEqual(shapes["right_arm"], stick_lib.FlapTipShape.TRIANGULAR)
    self.assertEqual(shapes["left_arm"], stick_lib.FlapTipShape.TRIANGULAR)
    self.assertEqual(shapes["right_leg"], stick_lib.FlapTipShape.RECTANGULAR)
    self.assertEqual(shapes["left_leg"], stick_lib.FlapTipShape.TRIANGULAR)

  def test_human_simple_symmetric_grid_12(self):
    tree = copy.deepcopy(example_trees.HUMAN_SIMPLE)
    packing = self._run_packing(tree, grid_size=12, is_symmetric=True)
    shapes = self._get_flap_shapes(packing)
    self.assertEqual(shapes["head"], stick_lib.FlapTipShape.RECTANGULAR)
    self.assertEqual(shapes["right_arm"], stick_lib.FlapTipShape.RECTANGULAR)
    self.assertEqual(shapes["left_arm"], stick_lib.FlapTipShape.RECTANGULAR)
    self.assertEqual(shapes["right_leg"], stick_lib.FlapTipShape.RECTANGULAR)
    self.assertEqual(shapes["left_leg"], stick_lib.FlapTipShape.RECTANGULAR)

  def test_c2_greyhound_asymmetric_grid_9(self):
    stickfigure = example_trees.get_example_by_name("C-2 Greyhound")
    packing = self._run_packing(stickfigure, grid_size=9, is_symmetric=False)
    shapes = self._get_flap_shapes(packing)
    self.assertEqual(
        shapes["fuselage_front"], stick_lib.FlapTipShape.RECTANGULAR
    )
    self.assertEqual(shapes["main_wing"], stick_lib.FlapTipShape.RECTANGULAR)
    self.assertEqual(
        shapes["vertical_stabilizer"], stick_lib.FlapTipShape.TRIANGULAR
    )
    self.assertEqual(
        shapes["horizontal_stabilizer"], stick_lib.FlapTipShape.RECTANGULAR
    )
    self.assertEqual(
        shapes["engine_nacelle"], stick_lib.FlapTipShape.RECTANGULAR
    )


class AssignFlapShapesToUnmergedTreeTest(parameterized.TestCase):

  def test_coat_rack(self):
    tree = copy.deepcopy(example_trees.COAT_RACK)
    flap_shapes = {
        "leg_front_left": stick_lib.FlapTipShape.RECTANGULAR,
        "leg_back_left": stick_lib.FlapTipShape.RECTANGULAR,
        "bar_left_outer_hook1_shank_hook1_curve": (
            stick_lib.FlapTipShape.RECTANGULAR
        ),
        "hook4_shank_hook4_curve": stick_lib.FlapTipShape.RECTANGULAR,
        "hook2_shank_hook2_curve": stick_lib.FlapTipShape.RECTANGULAR,
        "leg_front_right": stick_lib.FlapTipShape.RECTANGULAR,
        "leg_back_right": stick_lib.FlapTipShape.RECTANGULAR,
        "bar_right_outer_hook3_shank_hook3_curve": (
            stick_lib.FlapTipShape.RECTANGULAR
        ),
        "hook5_shank_hook5_curve": stick_lib.FlapTipShape.RECTANGULAR,
    }
    compute_ridges.assign_flap_shapes_to_unmerged_tree(tree, flap_shapes)

    expected = {
        "main_pole": stick_lib.FlapTipShape.NOT_APPLICABLE,
        "leg_front_left": stick_lib.FlapTipShape.RECTANGULAR,
        "leg_front_right": stick_lib.FlapTipShape.RECTANGULAR,
        "leg_back_left": stick_lib.FlapTipShape.RECTANGULAR,
        "leg_back_right": stick_lib.FlapTipShape.RECTANGULAR,
        "bar_left_inner": stick_lib.FlapTipShape.NOT_APPLICABLE,
        "bar_left_outer": stick_lib.FlapTipShape.NOT_APPLICABLE,
        "bar_right_inner": stick_lib.FlapTipShape.NOT_APPLICABLE,
        "bar_right_outer": stick_lib.FlapTipShape.NOT_APPLICABLE,
        "hook1_shank": stick_lib.FlapTipShape.NOT_APPLICABLE,
        "hook1_curve": stick_lib.FlapTipShape.RECTANGULAR,
        "hook2_shank": stick_lib.FlapTipShape.NOT_APPLICABLE,
        "hook2_curve": stick_lib.FlapTipShape.RECTANGULAR,
        "hook3_shank": stick_lib.FlapTipShape.NOT_APPLICABLE,
        "hook3_curve": stick_lib.FlapTipShape.RECTANGULAR,
        "hook4_shank": stick_lib.FlapTipShape.NOT_APPLICABLE,
        "hook4_curve": stick_lib.FlapTipShape.RECTANGULAR,
        "hook5_shank": stick_lib.FlapTipShape.NOT_APPLICABLE,
        "hook5_curve": stick_lib.FlapTipShape.RECTANGULAR,
    }
    for stick in tree.children:
      self.assertEqual(
          stick.flap_tip_shape,
          expected[stick.name],
          msg=f"{stick.name} expected {expected[stick.name]}",
      )

  def test_pull_up_bar(self):
    tree = copy.deepcopy(example_trees.PULL_UP_BAR)
    flap_shapes = {
        "door_right_post_up": stick_lib.FlapTipShape.RECTANGULAR,
        "door_right_post_down": stick_lib.FlapTipShape.RECTANGULAR,
        "right_angled_grip": stick_lib.FlapTipShape.RECTANGULAR,
        "right_short_grip": stick_lib.FlapTipShape.TRIANGULAR,
        "left_short_grip": stick_lib.FlapTipShape.RECTANGULAR,
        "door_left_post_down": stick_lib.FlapTipShape.TRIANGULAR,
        "door_left_post_up": stick_lib.FlapTipShape.RECTANGULAR,
        "left_angled_grip": stick_lib.FlapTipShape.RECTANGULAR,
    }
    compute_ridges.assign_flap_shapes_to_unmerged_tree(tree, flap_shapes)

    expected = {
        "bar_center": stick_lib.FlapTipShape.NOT_APPLICABLE,
        "bar_left_section": stick_lib.FlapTipShape.NOT_APPLICABLE,
        "bar_right_section": stick_lib.FlapTipShape.NOT_APPLICABLE,
        "left_angled_grip": stick_lib.FlapTipShape.RECTANGULAR,
        "right_angled_grip": stick_lib.FlapTipShape.RECTANGULAR,
        "left_short_grip": stick_lib.FlapTipShape.RECTANGULAR,
        "right_short_grip": stick_lib.FlapTipShape.TRIANGULAR,
        "left_mount": stick_lib.FlapTipShape.NOT_APPLICABLE,
        "right_mount": stick_lib.FlapTipShape.NOT_APPLICABLE,
        "door_left_post_up": stick_lib.FlapTipShape.RECTANGULAR,
        "door_left_post_down": stick_lib.FlapTipShape.TRIANGULAR,
        "door_right_post_up": stick_lib.FlapTipShape.RECTANGULAR,
        "door_right_post_down": stick_lib.FlapTipShape.RECTANGULAR,
    }
    for stick in tree.children:
      self.assertEqual(
          stick.flap_tip_shape,
          expected[stick.name],
          msg=f"{stick.name} expected {expected[stick.name]}",
      )


if __name__ == "__main__":
  absltest.main()
