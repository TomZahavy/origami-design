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

import collections
import time as time_mod

from absl.testing import absltest
from bp_pipeline import rectangle as shaping_utils
from bp_pipeline.crease_pattern import symmetry
from bp_pipeline.crease_pattern.parser import svg as svg_parser
from bp_pipeline.packing import river as river_lib
from bp_pipeline.packing import utils_packing_flaps
from bp_pipeline.packing import utils_packing_svg
from bp_pipeline.packing import utils_tracker
import numpy as np


class RiverTest(absltest.TestCase):

  def test_compute_unoccupied_areas_on_river_sides_vertical(self):
    river = river_lib.River(
        width=1,
        offset=2,
        orientation=river_lib.RiverOrientation.VERTICAL,
        grid_size=5,
    )
    grid = np.zeros((5, 5), dtype=bool)
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (10, 10)
    )

    grid[0, 0] = True
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (9, 10)
    )

    grid[4, 4] = True
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (9, 9)
    )

  def test_compute_unoccupied_areas_on_river_sides_horizontal(self):
    river = river_lib.River(
        width=2,
        offset=1,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=5,
    )
    grid = np.zeros((5, 5), dtype=bool)
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (5, 10)
    )

    grid[0, 0] = True
    grid[4, 0] = True
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (4, 9)
    )

  def test_compute_unoccupied_areas_on_river_sides_no_gap_on_one_side(self):
    river_top = river_lib.River(
        width=2,
        offset=0,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=5,
    )
    grid = np.zeros((5, 5), dtype=bool)
    self.assertEqual(
        river_top.compute_unoccupied_areas_on_river_sides(grid), (0, 15)
    )

    river_bottom = river_lib.River(
        width=2,
        offset=3,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=5,
    )
    grid = np.zeros((5, 5), dtype=bool)
    self.assertEqual(
        river_bottom.compute_unoccupied_areas_on_river_sides(grid), (15, 0)
    )

  def test_compute_unoccupied_areas_on_river_sides_with_blocking_river(self):
    grid = np.zeros((5, 5), dtype=bool)
    grid[2, :] = True  # horizontal river is blocking
    river_v = river_lib.River(
        width=1,
        offset=2,
        orientation=river_lib.RiverOrientation.VERTICAL,
        grid_size=5,
    )
    self.assertEqual(
        river_v.compute_unoccupied_areas_on_river_sides(grid), (8, 8)
    )


class CCWDistTest(absltest.TestCase):

  def test_ccw_dist(self):
    self.assertEqual(
        river_lib.get_border_cell_counter_clockwise_index((0, 0), 3), 0
    )
    self.assertEqual(
        river_lib.get_border_cell_counter_clockwise_index((1, 0), 3), 1
    )
    self.assertEqual(
        river_lib.get_border_cell_counter_clockwise_index((2, 0), 3), 2
    )
    self.assertEqual(
        river_lib.get_border_cell_counter_clockwise_index((2, 1), 3), 3
    )
    self.assertEqual(
        river_lib.get_border_cell_counter_clockwise_index((2, 2), 3), 4
    )
    self.assertEqual(
        river_lib.get_border_cell_counter_clockwise_index((1, 2), 3), 5
    )
    self.assertEqual(
        river_lib.get_border_cell_counter_clockwise_index((0, 2), 3), 6
    )
    self.assertEqual(
        river_lib.get_border_cell_counter_clockwise_index((0, 1), 3), 7
    )
    self.assertEqual(
        river_lib.calculate_counter_clockwise_distance((1, 0), (0, 0), 3), 1
    )
    self.assertEqual(
        river_lib.calculate_counter_clockwise_distance((0, 1), (0, 0), 3), 7
    )
    self.assertEqual(
        river_lib.calculate_counter_clockwise_distance((0, 0), (0, 1), 3), 1
    )
    self.assertEqual(
        river_lib.calculate_counter_clockwise_distance((0, 1), (1, 0), 3), 6
    )

  def test_start_cell_straight_river(self):
    river_h = river_lib.River(
        width=1,
        offset=1,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=5,
    )
    self.assertEqual(river_h.start_cell, (1, 0))
    river_v = river_lib.River(
        width=1,
        offset=2,
        orientation=river_lib.RiverOrientation.VERTICAL,
        grid_size=5,
    )
    self.assertEqual(river_v.start_cell, (0, 2))

  def test_start_cell_lshape_river(self):
    river_bl = river_lib.LShapedRiver(
        width=1,
        grid_size=5,
        l_shape_type=river_lib.LShapeType.BOTTOM_LEFT,
        turn_x=2,
        turn_y=2,
    )
    self.assertEqual(river_bl.start_cell, (2, 0))
    river_tr = river_lib.LShapedRiver(
        width=1,
        grid_size=5,
        l_shape_type=river_lib.LShapeType.TOP_RIGHT,
        turn_x=2,
        turn_y=2,
    )
    self.assertEqual(river_tr.start_cell, (0, 2))

  def test_start_cell_hugging_river(self):
    river_hug = river_lib.HuggingRiver(
        grid_size=3,
        width=1,
        subriver_paths=[[(0, 1), (1, 1), (1, 0)]],
        hug_side=river_lib.HugSide.RIGHT,
    )
    self.assertEqual(river_hug.start_cell, (0, 1))

  def test_hugging_river_variant_type(self):
    river = river_lib.HuggingRiver(
        grid_size=3,
        width=1,
        subriver_paths=[[(0, 1), (1, 1), (1, 0)]],
        hug_side=river_lib.HugSide.RIGHT,
        variant_type=river_lib.PathVariantType.STRAIGHT,
    )
    self.assertEqual(river.variant_type, river_lib.PathVariantType.STRAIGHT)


class HuggingRiverTest(absltest.TestCase):

  def test_hugging_river_1x1_right(self):
    grid = np.zeros((3, 3), dtype=bool)
    grid[0, 0] = True
    river = river_lib.HuggingRiver.from_contour(
        grid_size=3,
        width=1,
        occupancy_grid=grid,
        start_cell=(0, 1),
        hug_side=river_lib.HugSide.RIGHT,
    )
    expected_path = [(0, 1), (1, 1), (1, 0)]
    self.assertEqual(river.path, expected_path)

  def test_hugging_river_1x1_right_width2(self):
    grid = np.zeros((3, 3), dtype=bool)
    grid[0, 0] = True
    grid[2, 2] = True
    with self.assertRaisesRegex(
        river_lib.HuggingError,
        'Hugging river layer 2 collides with obstacle at \\(2, 2\\)',
    ):
      river_lib.HuggingRiver.from_contour(
          grid_size=3,
          width=2,
          occupancy_grid=grid,
          start_cell=(0, 1),
          hug_side=river_lib.HugSide.RIGHT,
      )

  def test_hugging_river_1x1_left(self):
    grid = np.zeros((3, 3), dtype=bool)
    grid[0, 0] = True
    river = river_lib.HuggingRiver.from_contour(
        grid_size=3,
        width=1,
        occupancy_grid=grid,
        start_cell=(1, 0),
        hug_side=river_lib.HugSide.LEFT,
    )
    expected_path = [(1, 0), (1, 1), (0, 1)]
    self.assertEqual(river.path, expected_path)

  def test_hugging_river_2sq_left(self):
    grid = np.zeros((3, 3), dtype=bool)
    grid[0, 0] = True
    grid[1, 1] = True
    river = river_lib.HuggingRiver.from_contour(
        grid_size=3,
        width=1,
        occupancy_grid=grid,
        start_cell=(0, 1),
        hug_side=river_lib.HugSide.RIGHT,
    )
    expected_path = [(0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0)]
    self.assertEqual(river.path, expected_path)

  def test_hugging_river_3sq_right(self):
    grid = np.zeros((3, 3), dtype=bool)
    grid[0, 0] = True
    grid[0, 1] = True
    grid[1, 1] = True
    river = river_lib.HuggingRiver.from_contour(
        grid_size=3,
        width=1,
        occupancy_grid=grid,
        start_cell=(0, 2),
        hug_side=river_lib.HugSide.RIGHT,
    )
    expected_path = [(0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0)]
    self.assertEqual(river.path, expected_path)

  def test_hugging_river_lshape_right(self):
    grid = np.zeros((6, 6), dtype=bool)
    grid[0, 1] = True
    grid[0, 2] = True
    grid[0, 3] = True
    grid[1, 3] = True
    grid[2, 3] = True
    grid[3, 3] = True
    river = river_lib.HuggingRiver.from_contour(
        grid_size=6,
        width=1,
        occupancy_grid=grid,
        start_cell=(0, 0),
        hug_side=river_lib.HugSide.LEFT,
    )
    expected_path = [
        (0, 0),
        (1, 0),
        (1, 1),
        (1, 2),
        (2, 2),
        (3, 2),
        (4, 2),
        (4, 3),
        (4, 4),
        (3, 4),
        (2, 4),
        (1, 4),
        (0, 4),
    ]
    self.assertEqual(river.path, expected_path)

  def test_hugging_river_dead_end(self):
    grid = np.array(
        [
            [True, True, True],
            [True, False, True],
            [False, False, False],
        ],
        dtype=bool,
    )
    with self.assertRaisesRegex(
        river_lib.HuggingError,
        'Hugging path generation failed at cell \\(1, 1\\). The set of polygons'
        ' could not be strictly hugged',
    ):
      river_lib.HuggingRiver.from_contour(
          grid_size=3,
          width=1,
          occupancy_grid=grid,
          start_cell=(2, 0),
          hug_side=river_lib.HugSide.LEFT,
      )

  def test_hugging_river_subpattern_4x4(self):
    grid = np.array(
        [
            [True, True, True, True],
            [True, False, False, True],
            [False, False, False, True],
            [False, False, False, False],
        ],
        dtype=bool,
    )
    river = river_lib.HuggingRiver.from_contour(
        grid_size=4,
        width=1,
        occupancy_grid=grid,
        start_cell=(2, 0),
        hug_side=river_lib.HugSide.LEFT,
    )
    expected_path = [(2, 0), (2, 1), (1, 1), (1, 2), (2, 2), (3, 2), (3, 3)]
    self.assertEqual(river.path, expected_path)

  def test_hugging_river_notebook_issue(self):
    grid_size = 8
    grid_r30 = np.zeros((grid_size, grid_size), dtype=bool)
    rect_0_1 = shaping_utils.Rectangle(
        name='0_1', x_start=0, y_start=0, x_len=2, y_len=2
    )
    utils_packing_flaps.set_grid_occupation(grid_r30, rect_0_1, True)
    river30 = river_lib.HuggingRiver.from_contour(
        grid_size, 1, grid_r30, (2, 0), river_lib.HugSide.LEFT
    )
    expected_river30_path = [(2, 0), (2, 1), (2, 2), (1, 2), (0, 2)]
    self.assertEqual(river30.path, expected_river30_path)

    grid_r63 = np.zeros((grid_size, grid_size), dtype=bool)
    utils_packing_flaps.set_grid_occupation(grid_r63, rect_0_1, True)
    for r, c in river30.path:
      grid_r63[r, c] = True
    rect_3_4 = shaping_utils.Rectangle(
        name='3_4', x_start=0, y_start=3, x_len=2, y_len=4
    )
    utils_packing_flaps.set_grid_occupation(grid_r63, rect_3_4, True)
    river63 = river_lib.HuggingRiver.from_contour(
        grid_size, 1, grid_r63, (7, 0), river_lib.HugSide.LEFT
    )
    expected_river63_path = [
        (7, 0),
        (7, 1),
        (7, 2),
        (6, 2),
        (5, 2),
        (4, 2),
        (3, 2),
        (3, 3),
        (2, 3),
        (1, 3),
        (0, 3),
    ]
    self.assertEqual(river63.path, expected_river63_path)

  def test_compute_unoccupied_areas_on_river_sides_width1(self):
    grid = np.zeros((4, 4), dtype=bool)
    grid[0, 0] = True
    river = river_lib.HuggingRiver.from_contour(
        grid_size=4,
        width=1,
        occupancy_grid=grid,
        start_cell=(0, 1),
        hug_side=river_lib.HugSide.RIGHT,
    )
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (0, 12)
    )

  def test_compute_unoccupied_areas_on_river_sides_width2(self):
    grid = np.zeros((4, 4), dtype=bool)
    grid[0, 0] = True
    river = river_lib.HuggingRiver.from_contour(
        grid_size=4,
        width=2,
        occupancy_grid=grid,
        start_cell=(0, 1),
        hug_side=river_lib.HugSide.RIGHT,
    )
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (0, 7)
    )

  def test_get_river_mask_and_forbidden_grid(self):
    occupancy_grid = np.array([[1, 0, 0], [0, 0, 0], [0, 0, 0]], dtype=bool)
    river = river_lib.HuggingRiver(
        grid_size=3,
        width=1,
        subriver_paths=[[(0, 1), (1, 1), (1, 0)]],
        hug_side=river_lib.HugSide.RIGHT,
    )
    river_mask, forbidden_grid = river.get_river_mask_and_forbidden_grid(
        occupancy_grid
    )
    expected_river_mask = np.array(
        [[0, 1, 0], [1, 1, 0], [0, 0, 0]], dtype=bool
    )
    expected_forbidden_grid = np.array(
        [[1, 1, 0], [1, 1, 0], [0, 0, 0]], dtype=bool
    )
    np.testing.assert_array_equal(river_mask, expected_river_mask)
    np.testing.assert_array_equal(forbidden_grid, expected_forbidden_grid)

  def test_get_adjacent_cells_by_side(self):
    grid_size = 3
    occupancy_grid = np.zeros((grid_size, grid_size), dtype=bool)
    river = river_lib.HuggingRiver(
        grid_size=grid_size,
        width=1,
        subriver_paths=[[(0, 1), (1, 1), (2, 1)]],
        hug_side=river_lib.HugSide.LEFT,
    )
    hugging_adj, opposite_adj = river.get_adjacent_cells_by_side(occupancy_grid)
    self.assertSetEqual(hugging_adj, set([(0, 2), (1, 2), (2, 2)]))
    self.assertSetEqual(opposite_adj, set([(0, 0), (1, 0), (2, 0)]))


class HuggingRiverSpliceTest(absltest.TestCase):

  def test_hugging_river_splice_start_index_le_end_index(self):
    river1 = river_lib.HuggingRiver(
        grid_size=5,
        width=1,
        subriver_paths=[[(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]],
        hug_side=river_lib.HugSide.LEFT,
    )
    river2 = river_lib.HuggingRiver(
        grid_size=5,
        width=1,
        subriver_paths=[[(1, 0), (1, 1), (2, 1), (2, 0), (3, 0)]],
        hug_side=river_lib.HugSide.LEFT,
    )
    spliced_river = river1.splice(river2)
    expected_path = [(0, 0), (1, 0), (1, 1), (2, 1), (2, 0), (3, 0), (4, 0)]
    self.assertEqual(spliced_river.subriver_paths[0], expected_path)
    self.assertEqual(spliced_river.width, 1)
    self.assertEqual(spliced_river.grid_size, 5)

  def test_hugging_river_splice_with_opposing_direction_segment(
      self,
  ):
    river1 = river_lib.HuggingRiver(
        grid_size=5,
        width=1,
        subriver_paths=[
            [(0, 0), (1, 0), (1, 1), (2, 1), (3, 1), (3, 0), (4, 0)]
        ],
        hug_side=river_lib.HugSide.LEFT,
    )
    river2 = river_lib.HuggingRiver(
        grid_size=5,
        width=1,
        subriver_paths=[[(3, 1), (3, 2), (2, 2), (1, 2), (1, 1)]],
        hug_side=river_lib.HugSide.LEFT,
    )
    spliced_river = river1.splice(river2)
    expected_path = [
        (0, 0),
        (1, 0),
        (1, 1),
        (1, 2),
        (2, 2),
        (3, 2),
        (3, 1),
        (3, 0),
        (4, 0),
    ]
    self.assertEqual(spliced_river.subriver_paths[0], expected_path)

  def test_hugging_river_splice_width2(self):
    river1 = river_lib.HuggingRiver(
        grid_size=5,
        width=2,
        subriver_paths=[
            [(0, 0), (1, 0), (2, 0), (3, 0)],
            [(0, 1), (1, 1), (2, 1), (3, 1)],
        ],
        hug_side=river_lib.HugSide.LEFT,
    )
    river2 = river_lib.HuggingRiver(
        grid_size=5,
        width=2,
        subriver_paths=[
            [(1, 0), (2, 0)],
            [(1, 1), (1, 2), (2, 2), (2, 1)],
        ],
        hug_side=river_lib.HugSide.LEFT,
    )
    spliced_river = river1.splice(river2)
    expected_path0 = [(0, 0), (1, 0), (2, 0), (3, 0)]
    expected_path1 = [(0, 1), (1, 1), (1, 2), (2, 2), (2, 1), (3, 1)]
    self.assertEqual(spliced_river.subriver_paths[0], expected_path0)
    self.assertEqual(spliced_river.subriver_paths[1], expected_path1)

  def test_hugging_river_splice_width2_with_reverse_subrivers_true(self):
    p0 = [(0, 0), (1, 0), (2, 0), (3, 0)]
    p1 = [(0, 1), (1, 1), (2, 1), (3, 1)]
    river1 = river_lib.HuggingRiver(
        grid_size=5,
        width=2,
        subriver_paths=[p0, p1],
        hug_side=river_lib.HugSide.LEFT,
    )
    river2 = river_lib.HuggingRiver(
        grid_size=5,
        width=2,
        subriver_paths=[
            [(1, 1), (1, 2), (2, 2), (2, 1)],
            [(1, 0), (2, 0)],
        ],
        hug_side=river_lib.HugSide.RIGHT,
    )
    spliced_river = river1.splice(river2, reverse_subrivers=True)
    expected_path0 = [(0, 0), (1, 0), (2, 0), (3, 0)]
    expected_path1 = [(0, 1), (1, 1), (1, 2), (2, 2), (2, 1), (3, 1)]
    self.assertEqual(spliced_river.subriver_paths[0], expected_path0)
    self.assertEqual(spliced_river.subriver_paths[1], expected_path1)

  def test_hugging_river_splice_width2_one_path_reversed(self):
    river1 = river_lib.HuggingRiver(
        grid_size=5,
        width=2,
        subriver_paths=[
            [(0, 0), (1, 0), (2, 0), (3, 0)],
            [(0, 1), (1, 1), (2, 1), (3, 1)],
        ],
        hug_side=river_lib.HugSide.LEFT,
    )
    river2 = river_lib.HuggingRiver(
        grid_size=5,
        width=2,
        subriver_paths=[
            [(1, 0), (2, 0)],
            [(2, 1), (2, 2), (1, 2), (1, 1)],
        ],
        hug_side=river_lib.HugSide.LEFT,
    )
    spliced_river = river1.splice(river2)
    expected_path0 = [(0, 0), (1, 0), (2, 0), (3, 0)]
    expected_path1 = [(0, 1), (1, 1), (1, 2), (2, 2), (2, 1), (3, 1)]
    self.assertEqual(spliced_river.subriver_paths[0], expected_path0)
    self.assertEqual(spliced_river.subriver_paths[1], expected_path1)

  def test_hugging_river_splice_different_widths_raises_error(self):
    river1 = river_lib.HuggingRiver(
        grid_size=5,
        width=1,
        subriver_paths=[[(0, 0), (1, 0), (2, 0)]],
        hug_side=river_lib.HugSide.LEFT,
    )
    river2 = river_lib.HuggingRiver(
        grid_size=5,
        width=2,
        subriver_paths=[[(1, 0), (2, 0)], [(1, 1), (2, 1)]],
        hug_side=river_lib.HugSide.LEFT,
    )
    with self.assertRaisesRegex(
        ValueError, 'Spliced river must have same width'
    ):
      river1.splice(river2)

  def test_hugging_river_splice_points_not_found_raises_error(self):
    river1 = river_lib.HuggingRiver(
        grid_size=5,
        width=1,
        subriver_paths=[[(0, 0), (1, 0), (2, 0)]],
        hug_side=river_lib.HugSide.LEFT,
    )
    river2 = river_lib.HuggingRiver(
        grid_size=5,
        width=1,
        subriver_paths=[[(1, 1), (2, 1)]],
        hug_side=river_lib.HugSide.LEFT,
    )
    with self.assertRaisesRegex(
        ValueError, 'Start or end point of subriver not found in base river.'
    ):
      river1.splice(river2)


class SymmetricHuggingRiverTest(absltest.TestCase):

  def test_hugging_river_symmetric_boundary_hug(self):
    grid = np.zeros((4, 4), dtype=bool)
    river = river_lib.HuggingRiver.from_contour(
        grid_size=4,
        width=1,
        occupancy_grid=grid,
        start_cell=(0, 0),
        hug_side=river_lib.HugSide.LEFT,
        hug_boundaries=True,
    )
    expected_path = [(0, 0), (0, 1), (0, 2), (0, 3)]
    self.assertCountEqual(river.path, expected_path)
    self.assertTrue(river.is_vertically_symmetric())

  def test_hugging_river_symmetric_boundary_hug_with_obstacle(self):
    grid = np.zeros((4, 4), dtype=bool)
    grid[1, 0] = True
    river = river_lib.HuggingRiver.from_contour(
        grid_size=4,
        width=1,
        occupancy_grid=grid,
        start_cell=(0, 0),
        hug_side=river_lib.HugSide.LEFT,
        hug_boundaries=True,
    )

    expected_path = [(0, 0), (0, 1), (0, 2), (0, 3)]
    self.assertCountEqual(river.path, expected_path)
    self.assertTrue(river.is_vertically_symmetric())

  def test_case2_8x8_corner_obstacle(self):
    grid_size = 8
    grid = np.zeros((grid_size, grid_size), dtype=bool)
    grid[0:2, 0:2] = True
    start_cell = (2, 0)
    hug_side = river_lib.HugSide.LEFT
    river = river_lib.HuggingRiver.from_contour(
        grid_size=grid_size,
        width=1,
        occupancy_grid=grid,
        start_cell=start_cell,
        hug_side=hug_side,
        hug_boundaries=True,
    )
    expected_path = [
        (2, 0),
        (2, 1),
        (2, 2),
        (1, 2),
        (0, 2),
        (0, 3),
        (2, 7),
        (2, 6),
        (2, 5),
        (1, 5),
        (0, 5),
        (0, 4),
    ]
    self.assertCountEqual(river.path, expected_path)
    self.assertTrue(river.is_vertically_symmetric())

  def test_case3_8x8_obstacle_on_sym_axis(self):
    grid_size = 8
    grid = np.zeros((grid_size, grid_size), dtype=bool)
    grid[0:2, 3:5] = True
    start_cell = (0, 2)
    hug_side = river_lib.HugSide.LEFT
    river = river_lib.HuggingRiver.from_contour(
        grid_size=grid_size,
        width=1,
        occupancy_grid=grid,
        start_cell=start_cell,
        hug_side=hug_side,
        hug_boundaries=True,
    )
    expected_path = [
        (0, 2),
        (1, 2),
        (2, 2),
        (2, 3),
        (0, 5),
        (1, 5),
        (2, 5),
        (2, 4),
    ]
    self.assertCountEqual(river.path, expected_path)
    self.assertTrue(river.is_vertically_symmetric())

  def test_case4_12x12_corner_and_sym_axis_obstacles(self):
    grid_size = 12
    grid = np.zeros((grid_size, grid_size), dtype=bool)
    grid[0:2, 0:2] = True
    grid[0:2, 5:7] = True
    start_cell = (2, 0)
    hug_side = river_lib.HugSide.LEFT
    river = river_lib.HuggingRiver.from_contour(
        grid_size=grid_size,
        width=1,
        occupancy_grid=grid,
        start_cell=start_cell,
        hug_side=hug_side,
        hug_boundaries=True,
    )
    expected_path = [
        (2, 0),
        (2, 1),
        (2, 2),
        (1, 2),
        (0, 2),
        (0, 3),
        (0, 4),
        (1, 4),
        (2, 4),
        (2, 5),
        (2, 11),
        (2, 10),
        (2, 9),
        (1, 9),
        (0, 9),
        (0, 8),
        (0, 7),
        (1, 7),
        (2, 7),
        (2, 6),
    ]
    self.assertCountEqual(river.path, expected_path)
    self.assertTrue(river.is_vertically_symmetric())


class MirrorPathSymmetryTest(absltest.TestCase):

  def test_empty_path(self):
    path = []
    new_path = river_lib.get_mirrored_path_for_symmetry(path, 4)
    self.assertEmpty(new_path)

  def test_already_symmetric_path(self):
    path = [(0, 0), (0, 1)]
    new_path = river_lib.get_mirrored_path_for_symmetry(path, 4)
    self.assertEqual(new_path, [(0, 0), (0, 1), (0, 2), (0, 3)])

  def test_mirror_simple_path(self):
    path = [(0, 0), (0, 1)]
    new_path = river_lib.get_mirrored_path_for_symmetry(path, 4)
    self.assertEqual(new_path, [(0, 0), (0, 1), (0, 2), (0, 3)])

  def test_mirror_path_with_shared_cell_on_axis(self):
    path = [(0, 1), (0, 2)]
    new_path = river_lib.get_mirrored_path_for_symmetry(path, 5)
    self.assertCountEqual(new_path, [(0, 1), (0, 2), (0, 3)])

  def test_cross_symmetry_axis_error(self):
    path = [(0, 2)]
    with self.assertRaisesRegex(
        river_lib.HuggingError,
        'Symmetric hugging river generation crossed symmetry axis.',
    ):
      river_lib.get_mirrored_path_for_symmetry(path, 3)


class LShapedRiverTest(absltest.TestCase):

  def test_lshape_bottom_left(self):
    river = river_lib.LShapedRiver(
        width=1,
        grid_size=5,
        l_shape_type=river_lib.LShapeType.BOTTOM_LEFT,
        turn_x=2,
        turn_y=2,
    )
    rects = river.rectangles
    self.assertLen(rects, 2)
    self.assertEqual(rects[0].x_start, 0)
    self.assertEqual(rects[0].y_start, 2)
    self.assertEqual(rects[0].x_len, 3)
    self.assertEqual(rects[0].y_len, 1)
    self.assertEqual(rects[1].x_start, 2)
    self.assertEqual(rects[1].y_start, 0)
    self.assertEqual(rects[1].x_len, 1)
    self.assertEqual(rects[1].y_len, 3)

  def test_lshape_top_right(self):
    river = river_lib.LShapedRiver(
        width=2,
        grid_size=10,
        l_shape_type=river_lib.LShapeType.TOP_RIGHT,
        turn_x=4,
        turn_y=5,
    )
    rects = river.rectangles
    self.assertLen(rects, 2)
    self.assertEqual(rects[0].x_start, 4)
    self.assertEqual(rects[0].y_start, 5)
    self.assertEqual(rects[0].x_len, 6)
    self.assertEqual(rects[0].y_len, 2)
    self.assertEqual(rects[1].x_start, 4)
    self.assertEqual(rects[1].y_start, 5)
    self.assertEqual(rects[1].x_len, 2)
    self.assertEqual(rects[1].y_len, 5)

  def test_compute_unoccupied_areas_on_river_sides_lshape(self):
    river = river_lib.LShapedRiver(
        width=1,
        grid_size=5,
        l_shape_type=river_lib.LShapeType.BOTTOM_LEFT,
        turn_x=2,
        turn_y=2,
    )
    grid = np.zeros((5, 5), dtype=bool)
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (4, 16)
    )
    grid[0, 0] = True
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (3, 16)
    )
    grid[3, 3] = True
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (3, 15)
    )

  def test_compute_unoccupied_areas_on_river_sides_lshape_bottom_right(self):
    river = river_lib.LShapedRiver(
        width=1,
        grid_size=5,
        l_shape_type=river_lib.LShapeType.BOTTOM_RIGHT,
        turn_x=2,
        turn_y=2,
    )
    grid = np.zeros((5, 5), dtype=bool)
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (4, 16)
    )
    grid[0, 3] = True
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (3, 16)
    )
    grid[3, 0] = True
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (3, 15)
    )

  def test_compute_unoccupied_areas_on_river_sides_lshape_top_left(self):
    river = river_lib.LShapedRiver(
        width=1,
        grid_size=5,
        l_shape_type=river_lib.LShapeType.TOP_LEFT,
        turn_x=2,
        turn_y=2,
    )
    grid = np.zeros((5, 5), dtype=bool)
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (4, 16)
    )
    grid[3, 0] = True
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (3, 16)
    )
    grid[0, 0] = True
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (3, 15)
    )

  def test_compute_unoccupied_areas_on_river_sides_lshape_top_right(self):
    river = river_lib.LShapedRiver(
        width=1,
        grid_size=5,
        l_shape_type=river_lib.LShapeType.TOP_RIGHT,
        turn_x=2,
        turn_y=2,
    )
    grid = np.zeros((5, 5), dtype=bool)
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (4, 16)
    )
    grid[3, 3] = True
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (3, 16)
    )
    grid[0, 0] = True
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (3, 15)
    )

  def test_compute_unoccupied_areas_on_river_sides_lshape_with_blocking(self):
    river = river_lib.LShapedRiver(
        width=1,
        grid_size=5,
        l_shape_type=river_lib.LShapeType.BOTTOM_LEFT,
        turn_x=2,
        turn_y=2,
    )
    grid = np.zeros((5, 5), dtype=bool)
    grid[0, 1] = True
    grid[1, 0] = True
    self.assertEqual(
        river.compute_unoccupied_areas_on_river_sides(grid), (1, 16)
    )


class RiverMirrorTest(absltest.TestCase):

  def _check_symmetry_with_creases(self, river, grid_size):
    tracker = utils_tracker.CreasePatternTracker(grid_size)
    tracker.add_river('r1', river)
    svg1 = utils_packing_svg.convert_packing_to_svg(grid_size, tracker)[0]
    cp1 = svg_parser.parse_svg(svg1, grid_size=grid_size)

    mirrored_river = river.mirror(grid_size)
    tracker_m = utils_tracker.CreasePatternTracker(grid_size)
    tracker_m.add_river('r1m', mirrored_river)
    svg_m = utils_packing_svg.convert_packing_to_svg(grid_size, tracker_m)[0]
    cp_m = svg_parser.parse_svg(svg_m, grid_size=grid_size)

    cp1_flipped = symmetry.Transform.VERTICAL_FLIP(cp1)
    self.assertEqual(len(cp1_flipped.creases), len(cp_m.creases))
    for c1 in cp1_flipped.creases:
      self.assertTrue(any(c1.isclose(c2) for c2 in cp_m.creases))
    for c2 in cp_m.creases:
      self.assertTrue(any(c2.isclose(c1) for c1 in cp1_flipped.creases))

  def test_mirror_vertical_river(self):
    river = river_lib.River(
        width=2,
        offset=1,
        orientation=river_lib.RiverOrientation.VERTICAL,
        grid_size=10,
    )
    self.assertTrue(river_lib.is_mirror_correct(river, 10))
    self._check_symmetry_with_creases(river, 10)

  def test_mirror_horizontal_river(self):
    river = river_lib.River(
        width=2,
        offset=1,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=10,
    )
    mirrored = river.mirror(10)
    self.assertEqual(mirrored, river)
    self.assertTrue(river_lib.is_mirror_correct(river, 10))
    self._check_symmetry_with_creases(river, 10)

  def test_mirror_lshape_river_bl(self):
    river = river_lib.LShapedRiver(
        width=1,
        grid_size=6,
        l_shape_type=river_lib.LShapeType.BOTTOM_LEFT,
        turn_x=1,
        turn_y=1,
    )
    self.assertTrue(river_lib.is_mirror_correct(river, 6))
    self._check_symmetry_with_creases(river, 6)

  def test_mirror_lshape_river_tr(self):
    river = river_lib.LShapedRiver(
        width=1,
        grid_size=6,
        l_shape_type=river_lib.LShapeType.TOP_RIGHT,
        turn_x=3,
        turn_y=1,
    )
    self.assertTrue(river_lib.is_mirror_correct(river, 6))
    self._check_symmetry_with_creases(river, 6)

  def test_mirror_hugging_river(self):
    grid_size_hug = 10
    occupancy_grid_hug = np.zeros((10, 10), dtype=bool)
    occupancy_grid_hug[0, 1:3] = True
    occupancy_grid_hug[1:4, 2] = True
    river = river_lib.HuggingRiver.from_contour(
        grid_size=grid_size_hug,
        width=1,
        occupancy_grid=occupancy_grid_hug,
        start_cell=(0, 0),
        hug_side=river_lib.HugSide.LEFT,
    )
    mirrored = river.mirror(grid_size_hug)
    self.assertEqual(mirrored.hug_side, river_lib.HugSide.RIGHT)
    self.assertTrue(river_lib.is_mirror_correct(river, grid_size_hug))
    self._check_symmetry_with_creases(river, grid_size_hug)


class CountCornersInMaskTest(absltest.TestCase):

  def test_count_corners_in_mask_1x1_true(self):
    mask = np.array([[True]])
    self.assertEqual(river_lib.count_corners_in_mask(mask), 1)

  def test_count_corners_in_mask_1x1_false(self):
    mask = np.array([[False]])
    self.assertEqual(river_lib.count_corners_in_mask(mask), 0)

  def test_count_corners_in_mask_2x2_all_false(self):
    mask = np.zeros((2, 2), dtype=bool)
    self.assertEqual(river_lib.count_corners_in_mask(mask), 0)

  def test_count_corners_in_mask_2x2_one_corner(self):
    mask = np.zeros((2, 2), dtype=bool)
    mask[0, 0] = True
    self.assertEqual(river_lib.count_corners_in_mask(mask), 1)

  def test_count_corners_in_mask_2x2_two_corners(self):
    mask = np.zeros((2, 2), dtype=bool)
    mask[0, 0] = True
    mask[1, 1] = True
    self.assertEqual(river_lib.count_corners_in_mask(mask), 2)

  def test_count_corners_in_mask_2x2_three_corners(self):
    mask = np.zeros((2, 2), dtype=bool)
    mask[0, 0] = True
    mask[0, 1] = True
    mask[1, 1] = True
    self.assertEqual(river_lib.count_corners_in_mask(mask), 3)

  def test_count_corners_in_mask_2x2_four_corners(self):
    mask = np.ones((2, 2), dtype=bool)
    self.assertEqual(river_lib.count_corners_in_mask(mask), 4)

  def test_count_corners_in_mask_3x3_two_corners(self):
    mask = np.zeros((3, 3), dtype=bool)
    mask[0, 0] = True
    mask[2, 2] = True
    self.assertEqual(river_lib.count_corners_in_mask(mask), 2)

  def test_count_corners_in_mask_3x3_no_corners_center_true(self):
    mask = np.zeros((3, 3), dtype=bool)
    mask[1, 1] = True
    self.assertEqual(river_lib.count_corners_in_mask(mask), 0)


class HelperFunctionsTest(absltest.TestCase):

  def test_count_corners_from_seeds_no_seeds(self):
    self.assertEqual(
        river_lib._count_corners_from_seeds(
            seeds=set(), grid_size=3, forbidden=np.zeros((3, 3), dtype=bool)
        ),
        0,
    )

  def test_count_corners_from_seeds_one_corner(self):
    seeds = {(0, 0)}
    forbidden = np.zeros((3, 3), dtype=bool)
    self.assertEqual(
        river_lib._count_corners_from_seeds(seeds, 3, forbidden), 4
    )
    forbidden[0, 1] = True
    forbidden[1, 0] = True
    forbidden[1, 1] = True
    self.assertEqual(
        river_lib._count_corners_from_seeds(seeds, 3, forbidden), 1
    )

  def test_get_seeds_from_river_mask(self):
    river_mask = np.array(
        [
            [0, 1, 0],
            [0, 1, 0],
            [0, 1, 0],
        ],
        dtype=bool,
    )
    side1_mask = np.array(
        [
            [1, 0, 0],
            [1, 0, 0],
            [1, 0, 0],
        ],
        dtype=bool,
    )
    forbidden_grid = river_mask.copy()
    side1_seeds, side2_seeds = river_lib._get_seeds_from_river_mask(
        grid_size=3,
        river_mask=river_mask,
        side1_mask=side1_mask,
        forbidden_grid=forbidden_grid,
    )
    self.assertEqual(side1_seeds, {(0, 0), (1, 0), (2, 0)})
    self.assertEqual(side2_seeds, {(0, 2), (1, 2), (2, 2)})


class RiverGetCornerCountsTest(absltest.TestCase):

  def test_straight_river_corners(self):
    river_h = river_lib.River(1, 1, river_lib.RiverOrientation.HORIZONTAL, 3)
    grid = np.zeros((3, 3), dtype=bool)
    self.assertEqual(
        river_h.get_corner_counts_on_river_sides(grid), {'top': 2, 'bottom': 2}
    )

    grid[0, 0] = True
    self.assertEqual(
        river_h.get_corner_counts_on_river_sides(grid), {'top': 1, 'bottom': 2}
    )

  def test_lshape_river_corners(self):
    river_bl = river_lib.LShapedRiver(
        1, 3, river_lib.LShapeType.BOTTOM_LEFT, 1, 1
    )
    grid = np.zeros((3, 3), dtype=bool)
    self.assertEqual(
        river_bl.get_corner_counts_on_river_sides(grid),
        {'inner': 1, 'outer': 3},
    )

  def test_hugging_river_corners(self):
    grid = np.zeros((3, 3), dtype=bool)
    grid[0, 0] = True
    river = river_lib.HuggingRiver(
        grid_size=3,
        width=1,
        subriver_paths=[[(0, 1), (1, 1), (1, 0)]],
        hug_side=river_lib.HugSide.RIGHT,
    )
    self.assertEqual(
        river.get_corner_counts_on_river_sides(grid),
        {'hugging': 0, 'opposite': 3},
    )

  def test_hugging_river_center_obstacle_0_hug_4_opp_corners(self):
    grid = np.zeros((5, 5), dtype=bool)
    obstacle_grid = np.zeros((5, 5), dtype=bool)
    obstacle_grid[0, 2] = True
    river = river_lib.HuggingRiver.from_contour(
        5, 1, obstacle_grid, (0, 1), river_lib.HugSide.LEFT
    )
    self.assertEqual(
        river.get_corner_counts_on_river_sides(grid),
        {'hugging': 0, 'opposite': 4},
    )

  def test_scipy_ndimage_river_flood_fill_equivalence_and_speedup(self):

    def _naive_bfs_mask(seeds, grid_size, forbidden):
      visited = np.zeros((grid_size, grid_size), dtype=bool)
      queue = collections.deque()
      for r, c in seeds:
        if 0 <= r < grid_size and 0 <= c < grid_size and not forbidden[r, c]:
          if not visited[r, c]:
            visited[r, c] = True
            queue.append((r, c))
      while queue:
        r, c = queue.popleft()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
          nr, nc = r + dr, c + dc
          if (
              0 <= nr < grid_size
              and 0 <= nc < grid_size
              and not visited[nr, nc]
              and not forbidden[nr, nc]
          ):
            visited[nr, nc] = True
            queue.append((nr, nc))
      return visited

    rng = np.random.default_rng(42)
    grid_size = 24
    grids = [rng.random((grid_size, grid_size)) < 0.25 for _ in range(40)]
    rivers = []
    for lt in (
        river_lib.LShapeType.BOTTOM_LEFT,
        river_lib.LShapeType.TOP_RIGHT,
    ):
      for tx, ty in ((6, 6), (10, 8), (12, 12)):
        rivers.append(
            river_lib.LShapedRiver(
                width=2,
                grid_size=grid_size,
                l_shape_type=lt,
                turn_x=tx,
                turn_y=ty,
            )
        )

    for g in grids[:15]:
      seeds = {
          (int(r), int(c))
          for r, c in zip(
              rng.integers(0, grid_size, size=8),
              rng.integers(0, grid_size, size=8),
          )
          if not g[r, c]
      }
      ref_mask = _naive_bfs_mask(seeds, grid_size, g)
      np.testing.assert_array_equal(
          river_lib._get_reachable_mask_from_seeds(seeds, grid_size, g),
          ref_mask,
      )

    def _run_naive():
      t0 = time_mod.perf_counter()
      results = []
      for r in rivers:
        for g in grids:
          river_mask = np.zeros((grid_size, grid_size), dtype=bool)
          for rect in r.rectangles:
            river_lib.utils_packing_flaps.set_grid_occupation(
                river_mask, rect, True
            )
          inner_mask_area, _ = r.get_area_masks(grid_size)
          forbidden = g | river_mask
          inner_seeds = set()
          outer_seeds = set()
          for rx, ry in np.argwhere(river_mask):
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
              nx, ny = int(rx + dx), int(ry + dy)
              if (
                  0 <= nx < grid_size
                  and 0 <= ny < grid_size
                  and not forbidden[nx, ny]
              ):
                if inner_mask_area[nx, ny]:
                  inner_seeds.add((nx, ny))
                else:
                  outer_seeds.add((nx, ny))
          im = _naive_bfs_mask(inner_seeds, grid_size, forbidden)
          om = _naive_bfs_mask(outer_seeds, grid_size, forbidden)
          corners = [
              (0, 0),
              (0, grid_size - 1),
              (grid_size - 1, 0),
              (grid_size - 1, grid_size - 1),
          ]
          results.append((
              (int(np.sum(im)), int(np.sum(om))),
              {
                  'inner': sum(1 for cx, cy in corners if im[cx, cy]),
                  'outer': sum(1 for cx, cy in corners if om[cx, cy]),
              },
          ))
      return time_mod.perf_counter() - t0, results

    def _run_fast():
      t0 = time_mod.perf_counter()
      results = []
      for r in rivers:
        for g in grids:
          results.append((
              r.compute_unoccupied_areas_on_river_sides(g),
              r.get_corner_counts_on_river_sides(g),
          ))
      return time_mod.perf_counter() - t0, results

    _run_fast()
    fast_sec, fast_res = _run_fast()
    naive_sec, naive_res = _run_naive()
    self.assertEqual(fast_res, naive_res)
    speedup = naive_sec / max(fast_sec, 1e-9)
    print(
        f'SCIPY_RIVER_BENCHMARK: fast_sec={fast_sec:.4f}s '
        f'naive_sec={naive_sec:.4f}s speedup={speedup:.2f}x'
    )


if __name__ == '__main__':
  absltest.main()
