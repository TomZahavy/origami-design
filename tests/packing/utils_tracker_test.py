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

"""Unit tests for the CreasePatternTracker class."""

import copy
from unittest import mock

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.crease_pattern import point
from bp_pipeline.packing import grid
from bp_pipeline.packing import river as river_lib
from bp_pipeline.packing import types
from bp_pipeline.packing import utils_packing_flaps
from bp_pipeline.packing import utils_tracker
import numpy as np


class PlotTrackerTest(absltest.TestCase):

  @mock.patch("matplotlib.pyplot.show")
  @mock.patch("matplotlib.pyplot.subplots")
  def test_plot_tracker_on_empty_tracker(self, mock_subplots, mock_show):
    mock_subplots.return_value = (mock.MagicMock(), mock.MagicMock())
    tracker = utils_tracker.CreasePatternTracker(grid_size=4)
    utils_tracker.plot_tracker(tracker)
    mock_subplots.assert_called_once()
    mock_show.assert_called_once()


class CreasePatternTrackerTest(parameterized.TestCase):
  """Tests the CreasePatternTracker class."""

  def test_initialization_succeeds(self):
    """Tests that the grids are created correctly with a valid size."""
    grid_size = 10
    tracker = utils_tracker.CreasePatternTracker(grid_size)

    self.assertLen(tracker.grid, grid_size)
    self.assertLen(tracker.occupancy_grid, grid_size)

    for y in range(grid_size):
      for x in range(grid_size):
        self.assertEqual(
            tracker.grid[y][x], utils_packing_flaps.EmptyGridCellState
        )
        self.assertFalse(tracker.occupancy_grid[y][x])

    self.assertEmpty(tracker.packed_polygons)

  def test_initialization_fails_with_zero_size(self):
    """Tests that initializing with a grid size of 0 raises a ValueError."""
    with self.assertRaises(ValueError):
      utils_tracker.CreasePatternTracker(0)

  def test_initialization_fails_with_negative_size(self):
    """Tests that initializing with a negative grid size raises a ValueError."""
    with self.assertRaises(ValueError):
      utils_tracker.CreasePatternTracker(-5)

  def test_add_polygon_succeeds(self):
    """Tests adding one polygon that fits completely within the grid."""
    tracker = utils_tracker.CreasePatternTracker(grid_size=5)
    leaf_id = "leaf_A"
    placement = types.PolygonPlacement.from_grid_coords(
        offset=(1, 1), size=(2, 2), grid_size=5
    )
    expected_state = utils_packing_flaps.GridCellState(
        type=utils_packing_flaps.GridCellType.POLYGON, source_id=leaf_id
    )

    tracker.add_polygon(leaf_id, placement)

    for y in range(1, 3):
      for x in range(1, 3):
        self.assertEqual(tracker.grid[y][x], expected_state)
        self.assertTrue(tracker.occupancy_grid[y][x])

  def test_add_multiple_separate_polygons_succeeds(self):
    """Tests adding multiple, non-overlapping polygons sequentially."""
    tracker = utils_tracker.CreasePatternTracker(grid_size=8)
    placement1 = types.PolygonPlacement.from_grid_coords(
        offset=(1, 1), size=(2, 2), grid_size=8
    )
    placement2 = types.PolygonPlacement.from_grid_coords(
        offset=(4, 4), size=(2, 2), grid_size=8
    )

    tracker.add_polygon("leaf_B1", placement1)
    tracker.add_polygon("leaf_B2", placement2)

    self.assertEqual(tracker.grid[2][2].source_id, "leaf_B1")
    self.assertTrue(tracker.occupancy_grid[2][2])
    self.assertEqual(tracker.grid[5][5].source_id, "leaf_B2")
    self.assertTrue(tracker.occupancy_grid[5][5])

  def test_add_polygon_partially_outside_grid(self):
    """Tests that adding a polygon partially off-grid only marks visible cells."""
    tracker = utils_tracker.CreasePatternTracker(grid_size=4)
    placement = types.PolygonPlacement.from_grid_coords(
        offset=(2, 2), size=(2, 2), grid_size=4
    )
    tracker.add_polygon("leaf_C", placement)

    for y in range(4):
      for x in range(4):
        if x >= 2 and y >= 2:
          self.assertEqual(
              tracker.grid[y][x].type, utils_packing_flaps.GridCellType.POLYGON
          )
          self.assertTrue(tracker.occupancy_grid[y][x])
        else:
          self.assertEqual(
              tracker.grid[y][x], utils_packing_flaps.EmptyGridCellState
          )
          self.assertFalse(tracker.occupancy_grid[y][x])

  def test_add_and_remove_by_id_cycle_restores_state(self):
    """Tests that removing a polygon by ID reverses the adding operation."""
    tracker = utils_tracker.CreasePatternTracker(grid_size=5)
    placement = types.PolygonPlacement.from_grid_coords(
        offset=(1, 1), size=(2, 2), grid_size=5
    )
    empty_state_grid = np.full(
        (5, 5), fill_value=utils_packing_flaps.EmptyGridCellState, dtype=object
    )
    empty_occupancy_grid = np.full((5, 5), fill_value=False, dtype=bool)

    tracker.add_polygon("leaf_E", placement)
    self.assertFalse(np.array_equal(tracker.grid, empty_state_grid))

    tracker.remove_by_id("leaf_E")
    self.assertTrue(np.array_equal(tracker.grid, empty_state_grid))
    self.assertTrue(
        np.array_equal(tracker.occupancy_grid, empty_occupancy_grid)
    )

  def test_add_polygon_raises_error_on_overlap(self):
    """Tests that add_polygon fails if a cell is already occupied."""
    tracker = utils_tracker.CreasePatternTracker(5)
    placement_a = types.PolygonPlacement.from_grid_coords(
        offset=(1, 1), size=(2, 2), grid_size=5
    )
    tracker.add_polygon("leaf_A", placement_a)
    grid_before_fail = tracker.grid.copy()

    placement_b = types.PolygonPlacement.from_grid_coords(
        offset=(2, 2), size=(2, 2), grid_size=5
    )
    with self.assertRaisesRegex(ValueError, "Overlap detected"):
      tracker.add_polygon("leaf_B", placement_b)

    self.assertTrue(np.array_equal(tracker.grid, grid_before_fail))
    self.assertNotIn("leaf_B", tracker.packed_polygons)

  def test_add_polygon_raises_error_on_duplicate_id(self):
    """Tests that adding a polygon with an existing ID fails."""
    tracker = utils_tracker.CreasePatternTracker(5)
    placement_a = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=5
    )
    tracker.add_polygon("leaf_A", placement_a)

    placement_b = types.PolygonPlacement.from_grid_coords(
        offset=(2, 2), size=(2, 2), grid_size=5
    )
    with self.assertRaisesRegex(ValueError, "already exists"):
      tracker.add_polygon("leaf_A", placement_b)

  def test_remove_by_id_raises_error_for_nonexistent_id(self):
    """Tests that removing a non-existent ID raises a KeyError."""
    tracker = utils_tracker.CreasePatternTracker(5)
    with self.assertRaisesRegex(KeyError, "not found"):
      tracker.remove_by_id("nonexistent_id")

  def test_remove_by_id_does_not_affect_other_polygons(self):
    """Tests that removing one polygon does not disturb another."""
    tracker = utils_tracker.CreasePatternTracker(5)
    placement_a = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=5
    )
    placement_b = types.PolygonPlacement.from_grid_coords(
        offset=(3, 3), size=(2, 2), grid_size=5
    )
    tracker.add_polygon("leaf_A", placement_a)
    tracker.add_polygon("leaf_B", placement_b)

    tracker.remove_by_id("leaf_A")

    self.assertEqual(tracker.grid[0][0], utils_packing_flaps.EmptyGridCellState)
    self.assertFalse(tracker.occupancy_grid[0][0])
    self.assertNotIn("leaf_A", tracker.packed_polygons)

    self.assertIsNotNone(tracker.grid[3][3])
    self.assertTrue(tracker.occupancy_grid[3][3])
    self.assertIn("leaf_B", tracker.packed_polygons)

  @parameterized.named_parameters(
      dict(
          testcase_name="north",
          direction=grid.Direction.NORTH,
          amount=2,
          expected_offset=(4, 2),
          expected_size=(2, 4),
      ),
      dict(
          testcase_name="south",
          direction=grid.Direction.SOUTH,
          amount=2,
          expected_offset=(4, 4),
          expected_size=(2, 4),
      ),
      dict(
          testcase_name="west",
          direction=grid.Direction.WEST,
          amount=2,
          expected_offset=(2, 4),
          expected_size=(4, 2),
      ),
      dict(
          testcase_name="east",
          direction=grid.Direction.EAST,
          amount=2,
          expected_offset=(4, 4),
          expected_size=(4, 2),
      ),
  )
  def test_expand_polygon_direction_succeeds(
      self, direction, amount, expected_offset, expected_size
  ):
    tracker = utils_tracker.CreasePatternTracker(grid_size=10)
    p = types.PolygonPlacement.from_grid_coords(
        offset=(4, 4), size=(2, 2), grid_size=10
    )
    tracker.add_polygon("p1", p)
    tracker.expand_polygon("p1", direction, amount)
    new_p = tracker.packed_polygons["p1"]
    self.assertEqual(new_p.offset, expected_offset)
    self.assertEqual(new_p.size, expected_size)

  @parameterized.named_parameters(
      dict(
          testcase_name="vertical",
          axis=grid.Axis.VERTICAL,
          amount=2,
          expected_offset=(4, 2),
          expected_size=(2, 6),
      ),
      dict(
          testcase_name="horizontal",
          axis=grid.Axis.HORIZONTAL,
          amount=2,
          expected_offset=(2, 4),
          expected_size=(6, 2),
      ),
  )
  def test_expand_polygon_axis_succeeds(
      self, axis, amount, expected_offset, expected_size
  ):
    tracker = utils_tracker.CreasePatternTracker(grid_size=10)
    p = types.PolygonPlacement.from_grid_coords(
        offset=(4, 4), size=(2, 2), grid_size=10
    )
    tracker.add_polygon("p1", p)
    tracker.expand_polygon("p1", axis, amount)
    new_p = tracker.packed_polygons["p1"]
    self.assertEqual(new_p.offset, expected_offset)
    self.assertEqual(new_p.size, expected_size)

  def test_expand_polygon_bad_amount_fails(self):
    tracker = utils_tracker.CreasePatternTracker(grid_size=10)
    p = types.PolygonPlacement.from_grid_coords(
        offset=(4, 4), size=(2, 2), grid_size=10
    )
    tracker.add_polygon("p1", p)
    with self.assertRaisesRegex(ValueError, "Amount must be positive"):
      tracker.expand_polygon("p1", grid.Direction.NORTH, 0)
    with self.assertRaisesRegex(ValueError, "Amount must be positive"):
      tracker.expand_polygon("p1", grid.Direction.NORTH, -1)

  def test_expand_polygon_nonexistent_leaf_id_fails(self):
    tracker = utils_tracker.CreasePatternTracker(grid_size=10)
    with self.assertRaisesRegex(ValueError, "Polygon not found"):
      tracker.expand_polygon("p1", grid.Direction.NORTH, 1)

  def test_expand_polygon_odd_amount_non_border_fails(self):
    tracker = utils_tracker.CreasePatternTracker(grid_size=10)
    p = types.PolygonPlacement.from_grid_coords(
        offset=(4, 4), size=(2, 2), grid_size=10
    )
    tracker.add_polygon("p1", p)
    with self.assertRaisesRegex(
        ValueError, "Odd deltas are only allowed for axis expansion"
    ):
      tracker.expand_polygon("p1", grid.Direction.NORTH, 1)

  def test_expand_polygon_odd_amount_axis_succeeds(self):
    tracker = utils_tracker.CreasePatternTracker(grid_size=10)
    p = types.PolygonPlacement.from_grid_coords(
        offset=(4, 4), size=(2, 2), grid_size=10
    )
    tracker.add_polygon("p1", p)
    tracker.expand_polygon("p1", grid.Axis.HORIZONTAL, 1)
    new_p = tracker.packed_polygons["p1"]
    self.assertEqual(new_p.offset, (3, 4))
    self.assertEqual(new_p.size, (4, 2))

  def test_expand_polygon_odd_amount_border_direction_fails(self):
    tracker = utils_tracker.CreasePatternTracker(grid_size=10)
    p = types.PolygonPlacement.from_grid_coords(
        offset=(0, 4), size=(2, 2), grid_size=10
    )
    tracker.add_polygon("p1", p)
    with self.assertRaisesRegex(
        ValueError, "Odd deltas are only allowed for axis expansion"
    ):
      tracker.expand_polygon("p1", grid.Direction.EAST, 1)

  @parameterized.parameters(
      utils_packing_flaps.EmptyGridCellState.source_id,
      utils_packing_flaps.BlockedGridCellState.source_id,
  )
  def test_add_polygon_invalid_id_fails(self, reserved_id):
    """Tests that adding a polygon with an invalid ID fails."""
    tracker = utils_tracker.CreasePatternTracker(5)
    with self.assertRaisesRegex(
        ValueError,
        "source_id must not be the source_id of EMPTY or BLOCKED cells.",
    ):
      tracker.add_polygon(reserved_id, mock.Mock())

  @parameterized.parameters(
      utils_packing_flaps.EmptyGridCellState.source_id,
      utils_packing_flaps.BlockedGridCellState.source_id,
  )
  def test_add_river_invalid_id_fails(self, reserved_id):
    """Tests that adding a river with an invalid ID fails."""
    tracker = utils_tracker.CreasePatternTracker(5)
    with self.assertRaisesRegex(
        ValueError,
        "source_id must not be the source_id of EMPTY or BLOCKED cells.",
    ):
      tracker.add_river(reserved_id, mock.Mock(grid_size=5))

  def test_id_grid_on_empty_tracker(self):
    """Tests that id_grid returns an empty grid for an empty tracker."""
    tracker = utils_tracker.CreasePatternTracker(grid_size=2)
    expected_id_grid = np.array([["", ""], ["", ""]])
    np.testing.assert_array_equal(tracker.id_grid, expected_id_grid)

  def test_id_grid_with_polygons_and_rivers(self):
    """Tests that id_grid returns correct IDs for polygons and rivers."""
    tracker = utils_tracker.CreasePatternTracker(grid_size=3)
    placement = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=3
    )
    tracker.add_polygon("poly1", placement)
    river = river_lib.River(
        width=1,
        offset=2,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=3,
    )
    tracker.add_river("river1", river)

    expected_id_grid = np.array([
        ["poly1", "poly1", ""],
        ["poly1", "poly1", ""],
        ["river1", "river1", "river1"],
    ])
    np.testing.assert_array_equal(tracker.id_grid, expected_id_grid)


class SaveLoadTest(absltest.TestCase):

  def test_save_load(self):
    tracker = utils_tracker.CreasePatternTracker(10)
    poly_placement = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=10
    )
    tracker.add_polygon("poly1", poly_placement)
    river = river_lib.River(
        width=1,
        offset=5,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=10,
    )
    tracker.add_river("river1", river)
    tracker.grid[4, 5] = utils_packing_flaps.GridCellState(
        utils_packing_flaps.GridCellType.RIVER_ADJACENT, "joint1"
    )
    tracker.river_banks["river1"] = [(4, 5)]

    tracker_copy = copy.deepcopy(tracker)
    state = tracker.get_state()
    loaded_tracker = utils_tracker.CreasePatternTracker.from_state(state)

    self.assertEqual(tracker_copy.grid_size, loaded_tracker.grid_size)
    self.assertIsInstance(state, utils_tracker.TrackerState)
    self.assertEqual(
        tracker_copy.packed_polygons, loaded_tracker.packed_polygons
    )
    self.assertEqual(tracker_copy.packed_rivers, loaded_tracker.packed_rivers)
    self.assertEqual(tracker_copy.river_banks, loaded_tracker.river_banks)
    np.testing.assert_array_equal(
        tracker_copy.occupancy_grid, loaded_tracker.occupancy_grid
    )
    for r in range(tracker.grid_size):
      for c in range(tracker.grid_size):
        self.assertEqual(
            tracker_copy.grid[r, c],
            loaded_tracker.grid[r, c],
            msg=f"Grid differs at ({r},{c})",
        )

  def test_save_load_with_mask(self):
    mask = np.zeros((10, 10), dtype=bool)
    mask[9, 9] = True
    tracker = utils_tracker.CreasePatternTracker(10, occupancy_mask=mask)
    poly_placement = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=10
    )
    tracker.add_polygon("poly1", poly_placement)
    river = river_lib.River(
        width=1,
        offset=5,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=10,
    )
    tracker.add_river("river1", river)
    tracker.grid[4, 5] = utils_packing_flaps.GridCellState(
        utils_packing_flaps.GridCellType.RIVER_ADJACENT, "joint1"
    )
    tracker.river_banks["river1"] = [(4, 5)]

    tracker_copy = copy.deepcopy(tracker)
    state = tracker.get_state()
    loaded_tracker = utils_tracker.CreasePatternTracker.from_state(state)

    self.assertEqual(tracker_copy.grid_size, loaded_tracker.grid_size)
    self.assertIsInstance(state, utils_tracker.TrackerState)
    self.assertEqual(
        tracker_copy.packed_polygons, loaded_tracker.packed_polygons
    )
    self.assertEqual(tracker_copy.packed_rivers, loaded_tracker.packed_rivers)
    self.assertEqual(tracker_copy.river_banks, loaded_tracker.river_banks)
    np.testing.assert_array_equal(
        tracker_copy.occupancy_grid, loaded_tracker.occupancy_grid
    )
    for r in range(tracker.grid_size):
      for c in range(tracker.grid_size):
        self.assertEqual(
            tracker_copy.grid[r, c],
            loaded_tracker.grid[r, c],
            msg=f"Grid differs at ({r},{c})",
        )

  def test_json_serialization(self):
    mask = np.zeros((10, 10), dtype=bool)
    mask[9, 9] = True
    tracker = utils_tracker.CreasePatternTracker(10, occupancy_mask=mask)
    poly_placement = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=10
    )
    tracker.add_polygon("poly1", poly_placement)
    river = river_lib.River(
        width=1,
        offset=5,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=10,
    )
    tracker.add_river("river1", river)
    lriver = river_lib.LShapedRiver(
        width=1,
        grid_size=10,
        l_shape_type=river_lib.LShapeType.BOTTOM_LEFT,
        turn_x=2,
        turn_y=2,
    )
    tracker.add_river("lriver1", lriver)
    poly2_placement = types.PolygonPlacement.from_grid_coords(
        offset=(8, 0), size=(2, 2), grid_size=10
    )
    tracker.add_polygon("poly2", poly2_placement)
    hr_occupancy_grid = np.zeros((10, 10), dtype=bool)
    hr_occupancy_grid[0:2, 8:10] = True
    hriver = river_lib.HuggingRiver.from_contour(
        grid_size=10,
        width=1,
        occupancy_grid=hr_occupancy_grid,
        start_cell=(0, 7),
        hug_side=river_lib.HugSide.RIGHT,
    )
    tracker.add_river("hriver1", hriver)

    state = tracker.get_state()
    json_state = state.to_json()
    new_state = utils_tracker.TrackerState.from_json(json_state)
    loaded_tracker = utils_tracker.CreasePatternTracker.from_state(new_state)

    self.assertEqual(tracker.grid_size, loaded_tracker.grid_size)
    self.assertEqual(tracker.packed_polygons, loaded_tracker.packed_polygons)
    self.assertEqual(tracker.packed_rivers, loaded_tracker.packed_rivers)
    self.assertEqual(tracker.river_banks, loaded_tracker.river_banks)
    np.testing.assert_array_equal(
        tracker.occupancy_grid, loaded_tracker.occupancy_grid
    )


class RiverInTrackerTest(absltest.TestCase):

  def test_add_horizontal_river_succeeds(self):
    tracker = utils_tracker.CreasePatternTracker(grid_size=5)
    river = river_lib.River(
        width=2,
        offset=1,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=5,
    )
    tracker.add_river("river1", river)
    self.assertIn("river1", tracker.packed_rivers)
    self.assertTrue(np.all(tracker.occupancy_grid[1:3, :]))
    self.assertFalse(np.any(tracker.occupancy_grid[0, :]))
    self.assertFalse(np.any(tracker.occupancy_grid[3:, :]))
    self.assertEqual(
        tracker.grid[1, 0].type, utils_packing_flaps.GridCellType.RIVER
    )

  def test_add_vertical_river_succeeds(self):
    tracker = utils_tracker.CreasePatternTracker(grid_size=5)
    river = river_lib.River(
        width=1,
        offset=2,
        orientation=river_lib.RiverOrientation.VERTICAL,
        grid_size=5,
    )
    tracker.add_river("river1", river)
    self.assertIn("river1", tracker.packed_rivers)
    self.assertTrue(np.all(tracker.occupancy_grid[:, 2]))
    self.assertFalse(np.any(tracker.occupancy_grid[:, :2]))
    self.assertFalse(np.any(tracker.occupancy_grid[:, 3:]))
    self.assertEqual(
        tracker.grid[0, 2].type, utils_packing_flaps.GridCellType.RIVER
    )

  def test_add_river_raises_error_on_overlap_with_polygon(self):
    tracker = utils_tracker.CreasePatternTracker(5)
    placement_a = types.PolygonPlacement.from_grid_coords(
        offset=(1, 1), size=(2, 2), grid_size=5
    )
    tracker.add_polygon("leaf_A", placement_a)
    river = river_lib.River(
        width=2,
        offset=1,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=5,
    )
    with self.assertRaisesRegex(ValueError, "Overlap detected"):
      tracker.add_river("river1", river)
    self.assertNotIn("river1", tracker.packed_rivers)

  def test_add_polygon_raises_error_on_overlap_with_river(self):
    tracker = utils_tracker.CreasePatternTracker(5)
    river = river_lib.River(
        width=2,
        offset=1,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=5,
    )
    tracker.add_river("river1", river)
    placement_a = types.PolygonPlacement.from_grid_coords(
        offset=(1, 1), size=(2, 2), grid_size=5
    )
    with self.assertRaisesRegex(ValueError, "Overlap detected"):
      tracker.add_polygon("leaf_A", placement_a)
    self.assertNotIn("leaf_A", tracker.packed_polygons)

  def test_remove_river_succeeds(self):
    tracker = utils_tracker.CreasePatternTracker(grid_size=5)
    river = river_lib.River(
        width=2,
        offset=1,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=5,
    )
    tracker.add_river("river1", river)
    tracker.remove_by_id("river1")
    self.assertNotIn("river1", tracker.packed_rivers)
    self.assertFalse(np.any(tracker.occupancy_grid))

  def test_add_river_duplicate_id_fails(self):
    tracker = utils_tracker.CreasePatternTracker(5)
    river1 = river_lib.River(
        width=1,
        offset=0,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=5,
    )
    tracker.add_river("river1", river1)
    river2 = river_lib.River(
        width=1,
        offset=2,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=5,
    )
    with self.assertRaisesRegex(ValueError, "already exists"):
      tracker.add_river("river1", river2)

  def test_add_lshaped_river_succeeds(self):
    tracker = utils_tracker.CreasePatternTracker(grid_size=5)
    river = river_lib.LShapedRiver(
        width=1,
        grid_size=5,
        l_shape_type=river_lib.LShapeType.BOTTOM_LEFT,
        turn_x=2,
        turn_y=2,
    )
    tracker.add_river("lriver1", river)
    self.assertIn("lriver1", tracker.packed_rivers)
    self.assertTrue(tracker.occupancy_grid[2, 0])
    self.assertTrue(tracker.occupancy_grid[2, 1])
    self.assertTrue(tracker.occupancy_grid[2, 2])
    self.assertTrue(tracker.occupancy_grid[0, 2])
    self.assertTrue(tracker.occupancy_grid[1, 2])
    self.assertEqual(
        tracker.grid[2, 2].type, utils_packing_flaps.GridCellType.RIVER
    )
    self.assertEqual(
        tracker.grid[0, 2].type, utils_packing_flaps.GridCellType.RIVER
    )

  def test_remove_lshaped_river_succeeds(self):
    tracker = utils_tracker.CreasePatternTracker(grid_size=5)
    river = river_lib.LShapedRiver(
        width=1,
        grid_size=5,
        l_shape_type=river_lib.LShapeType.BOTTOM_LEFT,
        turn_x=2,
        turn_y=2,
    )
    tracker.add_river("lriver1", river)
    tracker.remove_by_id("lriver1")
    self.assertNotIn("lriver1", tracker.packed_rivers)
    self.assertFalse(np.any(tracker.occupancy_grid))

  def test_add_and_remove_hugging_river_width2(self):
    tracker = utils_tracker.CreasePatternTracker(grid_size=3)
    occupancy_grid = np.zeros((3, 3), dtype=bool)
    occupancy_grid[0, 0] = True
    placement = types.PolygonPlacement(
        offset=(0, 0), size=(1, 1), center=point.Point(x=0.5 / 3, y=0.5 / 3)
    )
    tracker.add_polygon("poly00", placement)
    river = river_lib.HuggingRiver.from_contour(
        grid_size=3,
        width=2,
        occupancy_grid=occupancy_grid,
        start_cell=(0, 1),
        hug_side=river_lib.HugSide.RIGHT,
    )
    self.assertLen(river.subriver_paths, 2)
    self.assertLen(river.rectangles, 8)
    self.assertLen(river.path, 8)

    tracker.add_river("hugging1", river)
    self.assertIn("hugging1", tracker.packed_rivers)
    self.assertTrue(np.all(tracker.occupancy_grid))
    self.assertEqual(tracker.grid[0, 0].source_id, "poly00")
    self.assertEqual(tracker.grid[0, 1].source_id, "hugging1")
    self.assertEqual(tracker.grid[0, 2].source_id, "hugging1")
    self.assertEqual(tracker.grid[1, 0].source_id, "hugging1")
    self.assertEqual(tracker.grid[1, 1].source_id, "hugging1")
    self.assertEqual(tracker.grid[1, 2].source_id, "hugging1")
    self.assertEqual(tracker.grid[2, 0].source_id, "hugging1")
    self.assertEqual(tracker.grid[2, 1].source_id, "hugging1")
    self.assertEqual(tracker.grid[2, 2].source_id, "hugging1")

    tracker.remove_by_id("hugging1")
    self.assertNotIn("hugging1", tracker.packed_rivers)
    self.assertTrue(tracker.occupancy_grid[0, 0])
    self.assertEqual(tracker.grid[0, 0].source_id, "poly00")
    for r in range(3):
      for c in range(3):
        if r == 0 and c == 0:
          continue
        self.assertFalse(
            tracker.occupancy_grid[r, c], msg=f"Cell ({r},{c}) should be empty."
        )
        self.assertEqual(
            tracker.grid[r, c],
            utils_packing_flaps.EmptyGridCellState,
            msg=f"Cell ({r},{c}) should be EmptyGridCellState.",
        )


if __name__ == "__main__":
  absltest.main()
