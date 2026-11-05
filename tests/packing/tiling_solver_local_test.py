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

import time
from unittest import mock

from absl import logging
from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.packing import config as config_lib
from bp_pipeline.packing import grid
from bp_pipeline.packing import river as river_lib
from bp_pipeline.packing import tiling_solver_local
from bp_pipeline.packing import types
from bp_pipeline.packing import utils_tracker
import numpy as np

RectDelta = tiling_solver_local.RectDelta
FlapModification = tiling_solver_local.FlapOption


class RectDeltaTest(parameterized.TestCase):

  @parameterized.named_parameters(
      dict(
          testcase_name='north_expansion',
          delta=grid.Delta(di=-2, dj=0),
          edge_walk=grid.Walk(
              start_cell=grid.Cell(i=2, j=0),
              direction=grid.Direction.EAST,
              grid_size=4,
              steps=2,
          ),
          expected_cells=[
              grid.Cell(i=1, j=0),
              grid.Cell(i=1, j=1),
              grid.Cell(i=0, j=0),
              grid.Cell(i=0, j=1),
          ],
      ),
      dict(
          testcase_name='east_expansion',
          delta=grid.Delta(di=0, dj=2),
          edge_walk=grid.Walk(
              start_cell=grid.Cell(i=0, j=1),
              direction=grid.Direction.SOUTH,
              grid_size=4,
              steps=2,
          ),
          expected_cells=[
              grid.Cell(i=0, j=2),
              grid.Cell(i=1, j=2),
              grid.Cell(i=0, j=3),
              grid.Cell(i=1, j=3),
          ],
      ),
  )
  def test_walk(self, delta, edge_walk, expected_cells):
    rect_delta = RectDelta(delta=delta, edge_walk=edge_walk)
    self.assertCountEqual(list(rect_delta.walk()), expected_cells)

  def test_walk_off_grid(self):
    rect_delta = RectDelta(
        # This delta is long enough to go off the grid.
        delta=grid.Delta(di=3, dj=0),
        edge_walk=grid.Walk(
            start_cell=grid.Cell(i=0, j=0),
            direction=grid.Direction.EAST,
            grid_size=2,
            steps=2,
        ),
    )
    self.assertLen(list(rect_delta.walk()), 2)

  def test_where(self):
    rect_delta = RectDelta(
        delta=grid.Delta(di=-1, dj=0),
        edge_walk=grid.Walk(
            start_cell=grid.Cell(i=1, j=0),
            direction=grid.Direction.EAST,
            grid_size=2,
            steps=1,
        ),
    )
    # walk should yield grid.Cell(0,0)
    where_ys, where_xs = rect_delta.grid_indices
    np.testing.assert_array_equal(where_ys, np.array([0]))
    np.testing.assert_array_equal(where_xs, np.array([0]))

  def test_is_all_empty_and_add_to_grid(self):
    rect_delta = RectDelta(
        delta=grid.Delta(di=0, dj=1),
        edge_walk=grid.Walk(
            start_cell=grid.Cell(i=0, j=0),
            direction=grid.Direction.SOUTH,
            grid_size=2,
            steps=1,
        ),
    )
    # walk should yield grid.Cell(0,1)
    occupancy_grid = np.zeros((2, 2), dtype=bool)
    self.assertTrue(rect_delta.grid_has_space(occupancy_grid))
    rect_delta.add_to_grid(occupancy_grid)
    self.assertTrue(occupancy_grid[0, 1])
    self.assertFalse(rect_delta.grid_has_space(occupancy_grid))


class FindNextOccupiedCellTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self.tracker = utils_tracker.CreasePatternTracker(4)
    self.placement = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=4
    )
    self.tracker.add_polygon('p1', self.placement)
    self.river_tracker = utils_tracker.CreasePatternTracker(4)
    self.river_tracker.add_polygon('p1', self.placement)
    r1 = river_lib.HuggingRiver.from_contour(
        grid_size=self.river_tracker.grid_size,
        width=1,
        occupancy_grid=self.river_tracker.occupancy_grid,
        start_cell=(0, 2),
        hug_side=river_lib.HugSide.RIGHT,
    )
    self.river_tracker.add_river('r1', r1)

  def test_found(self):
    cell, rivers, found = tiling_solver_local._find_next_occupied_cell(
        self.tracker, grid.Cell(i=3, j=0), grid.Direction.NORTH
    )
    self.assertEqual(cell, grid.Cell(i=1, j=0))
    self.assertTrue(found)
    self.assertEmpty(rivers)

  def test_found_with_rivers(self):
    expected_river = tiling_solver_local._RiverRange(
        source_id='r1', start=grid.Cell(i=2, j=0), end=grid.Cell(i=2, j=0)
    )
    cell, rivers, found = tiling_solver_local._find_next_occupied_cell(
        self.river_tracker, grid.Cell(i=3, j=0), grid.Direction.NORTH, ['r1']
    )
    self.assertTrue(found)
    self.assertEqual(cell, grid.Cell(i=1, j=0))
    self.assertEqual(rivers, [expected_river])

  def test_wrong_allowed_river(self):
    cell, rivers, found = tiling_solver_local._find_next_occupied_cell(
        self.river_tracker, grid.Cell(i=3, j=0), grid.Direction.NORTH, ['r2']
    )
    self.assertTrue(found)
    self.assertEqual(cell, grid.Cell(i=2, j=0))
    self.assertEmpty(rivers)

  def test_wrong_order(self):
    cell, rivers, found = tiling_solver_local._find_next_occupied_cell(
        self.river_tracker,
        grid.Cell(i=3, j=0),
        grid.Direction.NORTH,
        ['r2', 'r1'],
    )
    self.assertTrue(found)
    self.assertEqual(cell, grid.Cell(i=2, j=0))
    self.assertEmpty(rivers)

  def test_river_required_success(self):
    expected_river = tiling_solver_local._RiverRange(
        source_id='r1', start=grid.Cell(i=2, j=0), end=grid.Cell(i=2, j=0)
    )
    cell, rivers, found = tiling_solver_local._find_next_occupied_cell(
        self.river_tracker,
        grid.Cell(i=3, j=0),
        grid.Direction.NORTH,
        ('r1',),
        require_rivers=True,
    )
    self.assertTrue(found)
    self.assertEqual(cell, grid.Cell(i=1, j=0))
    self.assertEqual(rivers, [expected_river])

  def test_remaining_river_required(self):
    with self.assertRaises(tiling_solver_local._MissingRiverError):
      tiling_solver_local._find_next_occupied_cell(
          self.river_tracker,
          grid.Cell(i=3, j=0),
          grid.Direction.NORTH,
          ('r1', 'r2'),
          require_rivers=True,
      )

  def test_not_found(self):
    cell, rivers, found = tiling_solver_local._find_next_occupied_cell(
        self.tracker, grid.Cell(i=0, j=3), grid.Direction.SOUTH
    )
    self.assertEqual(cell, grid.Cell(i=3, j=3))
    self.assertFalse(found)
    self.assertEmpty(rivers)


class GetFeasiblePolygonExpansionsTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self.grid_size = 6
    self.tracker = utils_tracker.CreasePatternTracker(self.grid_size)
    self.placement = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=self.grid_size
    )
    self.tracker.add_polygon('p1', self.placement)

  @parameterized.parameters(True, False)
  def test_found(self, search_rivers: bool):
    [expansion] = tiling_solver_local._get_feasible_polygon_expansions(
        self.tracker,
        grid.Cell(i=2, j=0),
        grid.Direction.NORTH,
        search_rivers=search_rivers,
    )
    self.assertEqual(expansion.source_id, 'p1')
    self.assertEqual(expansion.placement, self.placement)
    self.assertEqual(expansion.polygon_to_cell, grid.Delta(di=1, dj=0))
    self.assertEmpty(expansion.rivers)

  @parameterized.parameters(True, False)
  def test_not_found(self, search_rivers: bool):
    result = tiling_solver_local._get_feasible_polygon_expansions(
        self.tracker,
        grid.Cell(i=0, j=2),
        grid.Direction.EAST,
        search_rivers=search_rivers,
    )
    self.assertEmpty(result)

  @parameterized.parameters(grid.Cell(i=0, j=3), grid.Cell(i=2, j=3))
  def test_found_with_river_crossing(self, start_cell: grid.Cell):
    r1 = river_lib.HuggingRiver.from_contour(
        grid_size=self.grid_size,
        width=1,
        occupancy_grid=self.tracker.occupancy_grid,
        start_cell=(0, 2),
        hug_side=river_lib.HugSide.RIGHT,
    )
    self.tracker.add_river('r1', r1)
    expansions = tiling_solver_local._get_feasible_polygon_expansions(
        self.tracker, start_cell, grid.Direction.WEST, search_rivers=True
    )
    self.assertNotEmpty(expansions)
    expansion = expansions[0]
    self.assertEqual(expansion.source_id, 'p1')
    self.assertEqual(expansion.polygon_to_cell, grid.Delta(di=0, dj=2))
    self.assertLen(expansion.rivers, 1)
    self.assertEqual(expansion.rivers[0].source_id, 'r1')
    self.assertEqual(expansion.cell_to_riverstart[0], grid.Delta(di=0, dj=-1))

  @parameterized.parameters(grid.Cell(i=0, j=3), grid.Cell(i=2, j=3))
  def test_does_not_widen_when_no_more_river(self, start_cell: grid.Cell):
    r1 = river_lib.HuggingRiver.from_contour(
        grid_size=self.grid_size,
        width=1,
        occupancy_grid=self.tracker.occupancy_grid,
        start_cell=(0, 2),
        hug_side=river_lib.HugSide.RIGHT,
    )
    self.tracker.add_river('r1', r1)
    p2 = types.PolygonPlacement.from_grid_coords(
        offset=(0, 3), size=(2, 2), grid_size=self.grid_size
    )
    self.tracker.add_polygon('p2', p2)

    expansions = tiling_solver_local._get_feasible_polygon_expansions(
        self.tracker, start_cell, grid.Direction.WEST, search_rivers=True
    )
    self.assertLen(expansions, 1, msg='Polygon 2 should not be found.')
    expansion = expansions[0]
    self.assertEqual(expansion.source_id, 'p1')
    self.assertEqual(expansion.polygon_to_cell, grid.Delta(di=0, dj=2))
    self.assertLen(expansion.rivers, 1)
    self.assertEqual(expansion.rivers[0].source_id, 'r1')
    self.assertEqual(expansion.cell_to_riverstart[0], grid.Delta(di=0, dj=-1))

  @parameterized.parameters(
      grid.Cell(i=0, j=5), grid.Cell(i=2, j=5), grid.Cell(i=3, j=5)
  )
  def test_two_rivers(self, start_cell: grid.Cell):
    r1 = river_lib.HuggingRiver.from_contour(
        grid_size=self.grid_size,
        width=1,
        occupancy_grid=self.tracker.occupancy_grid,
        start_cell=(0, 2),
        hug_side=river_lib.HugSide.RIGHT,
    )
    self.tracker.add_river('r1', r1)
    r2 = river_lib.River(
        grid_size=self.grid_size,
        width=1,
        orientation=river_lib.RiverOrientation.VERTICAL,
        offset=4,
    )
    self.tracker.add_river('r2', r2)

    expansions = tiling_solver_local._get_feasible_polygon_expansions(
        self.tracker, start_cell, grid.Direction.WEST, search_rivers=True
    )
    self.assertLen(expansions, 1)
    [expansion] = expansions
    self.assertEqual(expansion.source_id, 'p1')
    self.assertEqual(expansion.polygon_to_cell, grid.Delta(di=0, dj=4))
    self.assertLen(expansion.rivers, 2)
    first_river, second_river = expansion.rivers
    self.assertEqual(first_river.source_id, 'r2')
    self.assertEqual(second_river.source_id, 'r1')
    first_delta, second_delta = expansion.cell_to_riverstart
    self.assertEqual(first_delta, grid.Delta(di=0, dj=-1))
    self.assertEqual(second_delta, grid.Delta(di=0, dj=-3))

  @parameterized.parameters(grid.Cell(i=0, j=3), grid.Cell(i=2, j=3))
  def test_found_with_river_crossing_no_search_rivers(
      self, start_cell: grid.Cell
  ):
    r1 = river_lib.HuggingRiver.from_contour(
        grid_size=self.grid_size,
        width=1,
        occupancy_grid=self.tracker.occupancy_grid,
        start_cell=(0, 2),
        hug_side=river_lib.HugSide.RIGHT,
    )
    self.tracker.add_river('r1', r1)
    expansions = tiling_solver_local._get_feasible_polygon_expansions(
        self.tracker, start_cell, grid.Direction.WEST, search_rivers=False
    )
    self.assertEmpty(expansions)

  @parameterized.named_parameters(
      dict(
          testcase_name='block',
          river_action=tiling_solver_local._RiverAction.BLOCK,
          expected_expansions=0,
      ),
      dict(
          testcase_name='allow',
          river_action=tiling_solver_local._RiverAction.ALLOW,
          expected_expansions=1,
      ),
      dict(
          testcase_name='widen_left',
          river_action=tiling_solver_local._RiverAction.WIDEN_LEFT,
          expected_expansions=1,
      ),
      dict(
          testcase_name='widen_right',
          river_action=tiling_solver_local._RiverAction.WIDEN_RIGHT,
          expected_expansions=2,
      ),
      dict(
          testcase_name='widen_both',
          river_action=tiling_solver_local._RiverAction.WIDEN_BOTH,
          expected_expansions=2,
      ),
  )
  def test_feasible_polygon_expansions_generator_river_action(
      self, river_action, expected_expansions
  ):
    r1 = river_lib.HuggingRiver.from_contour(
        grid_size=self.grid_size,
        width=1,
        occupancy_grid=self.tracker.occupancy_grid,
        start_cell=(0, 2),
        hug_side=river_lib.HugSide.RIGHT,
    )
    self.tracker.add_river('r1', r1)
    start_cell = grid.Cell(i=1, j=3)
    expansions = list(
        tiling_solver_local._feasible_polygon_expansions_generator(
            self.tracker,
            start_cell,
            grid.Direction.WEST,
            found_rivers=(),
            river_action=river_action,
        )
    )
    self.assertLen(expansions, expected_expansions)


class HelperFunctionsTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self.tracker = utils_tracker.CreasePatternTracker(4)
    self.placement = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=4
    )
    self.tracker.add_polygon('p1', self.placement)

  @parameterized.parameters(
      (
          grid.Direction.NORTH,
          grid.Walk(grid.Cell(i=0, j=0), grid.Direction.EAST, 4, steps=2),
      ),
      (
          grid.Direction.EAST,
          grid.Walk(grid.Cell(i=0, j=1), grid.Direction.SOUTH, 4, steps=2),
      ),
      (
          grid.Direction.SOUTH,
          grid.Walk(grid.Cell(i=1, j=0), grid.Direction.EAST, 4, steps=2),
      ),
      (
          grid.Direction.WEST,
          grid.Walk(grid.Cell(i=0, j=0), grid.Direction.SOUTH, 4, steps=2),
      ),
  )
  def test_get_polygon_boundary(self, direction, expected_walk):
    walk = tiling_solver_local._get_polygon_boundary(
        self.placement, direction, 4
    )
    self.assertEqual(walk.start_cell, expected_walk.start_cell)
    self.assertEqual(walk.direction, expected_walk.direction)
    self.assertEqual(walk.steps, expected_walk.steps)

  @parameterized.parameters(
      (grid.Direction.NORTH, True),
      (grid.Direction.EAST, False),
      (grid.Direction.SOUTH, False),
      (grid.Direction.WEST, True),
  )
  def test_is_touching_directional_border(self, direction, expected):
    self.assertEqual(
        tiling_solver_local._is_touching_specific_border(
            self.placement, direction, 4
        ),
        expected,
    )

  def test_allow_odd_delta_touching_border(self):
    self.assertTrue(
        tiling_solver_local._allow_odd_delta(
            self.placement, grid.Direction.WEST, 4, is_symmetric=False
        )
    )

  def test_allow_odd_delta_symmetric(self):
    p_sym = types.PolygonPlacement.from_grid_coords(
        offset=(1, 1), size=(2, 2), grid_size=4
    )
    self.assertTrue(
        tiling_solver_local._allow_odd_delta(
            p_sym, grid.Direction.WEST, 4, is_symmetric=True
        )
    )
    self.assertFalse(
        tiling_solver_local._allow_odd_delta(
            p_sym, grid.Direction.NORTH, 4, is_symmetric=True
        )
    )

  def test_is_placement_expansion_valid_valid(self):
    self.assertTrue(
        tiling_solver_local._is_placement_expansion_valid(
            self.tracker,
            self.placement,
            grid.Direction.EAST,
            grid.Delta(di=0, dj=1),
            is_symmetric=False,
        )
    )

  def test_is_placement_expansion_valid_invalid(self):
    self.assertFalse(
        tiling_solver_local._is_placement_expansion_valid(
            self.tracker,
            self.placement,
            grid.Direction.EAST,
            grid.Delta(di=0, dj=-1),
            is_symmetric=False,
        )
    )

  def test_is_placement_expansion_valid_symmetric_invalid(self):
    self.assertFalse(
        tiling_solver_local._is_placement_expansion_valid(
            self.tracker,
            self.placement,
            grid.Direction.EAST,
            grid.Delta(di=0, dj=1),
            is_symmetric=True,
        )
    )

  def test_get_empty_cells(self):
    tracker = utils_tracker.CreasePatternTracker(4)
    placement = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=4
    )
    tracker.add_polygon('p1', placement)
    empty_cells = set(
        tiling_solver_local._get_empty_cells(
            tracker.occupancy_grid, is_symmetric=False
        )
    )
    self.assertLen(empty_cells, 12)
    self.assertNotIn(grid.Cell(i=0, j=0), empty_cells)
    self.assertIn(grid.Cell(i=0, j=2), empty_cells)
    self.assertIn(grid.Cell(i=3, j=3), empty_cells)

  def test_get_empty_cells_symmetric(self):
    tracker = utils_tracker.CreasePatternTracker(4)
    placement = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=4
    )
    tracker.add_polygon('p1', placement)
    empty_cells = set(
        tiling_solver_local._get_empty_cells(
            tracker.occupancy_grid, is_symmetric=True
        )
    )
    self.assertLen(empty_cells, 4)
    self.assertNotIn(grid.Cell(i=0, j=0), empty_cells)
    self.assertNotIn(grid.Cell(i=0, j=2), empty_cells)
    self.assertIn(grid.Cell(i=2, j=0), empty_cells)
    self.assertIn(grid.Cell(i=3, j=1), empty_cells)


class GetEmptyCellOptionsTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self.tracker = utils_tracker.CreasePatternTracker(4)
    self.placement = types.PolygonPlacement.from_grid_coords(
        offset=(-2, 0), size=(4, 4), grid_size=4
    )
    self.tracker.add_polygon('p1', self.placement)
    self.config = config_lib.LocalTilingConfig(disable_wide_central_flaps=False)

  def test_get_flap_modification_for_cell_for_direction(self):
    modifications = (
        tiling_solver_local._get_flap_modifications_for_cell_for_direction(
            self.config,
            self.tracker,
            grid.Cell(i=0, j=2),
            grid.Direction.WEST,
            is_symmetric=False,
        )
    )
    self.assertLen(modifications, 1)
    [flap_modification] = modifications
    self.assertEqual(
        FlapModification(
            flap_id='p1',
            rect_deltas=(
                RectDelta(
                    delta=grid.Delta(di=0, dj=1),
                    edge_walk=grid.Walk(
                        start_cell=grid.Cell(i=0, j=1),
                        direction=grid.Direction.SOUTH,
                        grid_size=4,
                        steps=4,
                    ),
                ),
            ),
        ),
        flap_modification,
    )

  def test_get_flap_modification_for_cell_for_direction_odd_delta(self):
    tracker = utils_tracker.CreasePatternTracker(5)
    placement = types.PolygonPlacement.from_grid_coords(
        offset=(1, 1), size=(2, 2), grid_size=5
    )
    tracker.add_polygon('p1', placement)
    modifications = (
        tiling_solver_local._get_flap_modifications_for_cell_for_direction(
            self.config,
            tracker,
            grid.Cell(i=1, j=3),
            grid.Direction.WEST,
            is_symmetric=False,
        )
    )
    self.assertLen(modifications, 1)
    [flap_modification] = modifications
    self.assertEqual(
        FlapModification(
            flap_id='p1',
            rect_deltas=(
                RectDelta(
                    delta=grid.Delta(di=0, dj=2),
                    edge_walk=grid.Walk(
                        start_cell=grid.Cell(i=1, j=2),
                        direction=grid.Direction.SOUTH,
                        grid_size=5,
                        steps=2,
                    ),
                ),
            ),
        ),
        flap_modification,
    )

  def test_get_empty_cell_options_simple(self):
    cell_options = tiling_solver_local._get_empty_cell_options(
        self.config, self.tracker, is_symmetric=False
    )
    self.assertIn(grid.Cell(i=0, j=2), cell_options)
    [flap_modification] = cell_options[grid.Cell(i=0, j=2)]
    self.assertEqual(
        FlapModification(
            flap_id='p1',
            rect_deltas=(
                RectDelta(
                    delta=grid.Delta(di=0, dj=1),
                    edge_walk=grid.Walk(
                        start_cell=grid.Cell(i=0, j=1),
                        direction=grid.Direction.SOUTH,
                        grid_size=4,
                        steps=4,
                    ),
                ),
            ),
        ),
        flap_modification,
    )
    self.assertLen(cell_options, 8)

  def test_get_empty_cell_options_impossible(self):
    tracker = utils_tracker.CreasePatternTracker(4)
    placement = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=4
    )
    tracker.add_polygon('p1', placement)
    with self.assertRaisesRegex(
        tiling_solver_local.ImpossibleTilingError, 'No valid options'
    ):
      tiling_solver_local._get_empty_cell_options(
          self.config, tracker, is_symmetric=False
      )


class DisableWideCentralFlapsTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self.grid_size = 6
    self.tracker = utils_tracker.CreasePatternTracker(self.grid_size)
    self.p1_placement = types.PolygonPlacement.from_grid_coords(
        offset=(2, 2), size=(2, 2), grid_size=self.grid_size
    )
    self.tracker.add_polygon('p1', self.p1_placement)
    self.config = config_lib.LocalTilingConfig(disable_wide_central_flaps=True)

  def test_unblocked_vertical_success(self):
    modifications = (
        tiling_solver_local._get_flap_modifications_for_cell_for_direction(
            self.config,
            self.tracker,
            grid.Cell(i=1, j=2),
            grid.Direction.SOUTH,
            is_symmetric=False,
        )
    )
    self.assertNotEmpty(modifications)

  def test_horizontal_blocked_failure(self):
    p2 = types.PolygonPlacement.from_grid_coords(
        offset=(-1, 2), size=(2, 2), grid_size=self.grid_size
    )
    self.tracker.add_polygon('p2', p2)
    modifications = (
        tiling_solver_local._get_flap_modifications_for_cell_for_direction(
            self.config,
            self.tracker,
            grid.Cell(i=2, j=1),
            grid.Direction.EAST,
            is_symmetric=False,
        )
    )
    self.assertEmpty(modifications)

  def test_vertical_blocked_failure(self):
    p2 = types.PolygonPlacement.from_grid_coords(
        offset=(2, -1), size=(2, 2), grid_size=self.grid_size
    )
    self.tracker.add_polygon('p2', p2)
    modifications = (
        tiling_solver_local._get_flap_modifications_for_cell_for_direction(
            self.config,
            self.tracker,
            grid.Cell(i=1, j=2),
            grid.Direction.SOUTH,
            is_symmetric=False,
        )
    )
    self.assertEmpty(modifications)

  def test_symmetric_blocked_horizontal_success(self):
    p2 = types.PolygonPlacement.from_grid_coords(
        offset=(-1, 2), size=(2, 2), grid_size=self.grid_size
    )
    self.tracker.add_polygon('p2', p2)
    modifications = (
        tiling_solver_local._get_flap_modifications_for_cell_for_direction(
            self.config,
            self.tracker,
            grid.Cell(i=2, j=1),
            grid.Direction.EAST,
            is_symmetric=True,
        )
    )
    self.assertNotEmpty(modifications)

  def test_symmetric_blocked_vertical_failure(self):
    p2 = types.PolygonPlacement.from_grid_coords(
        offset=(2, -1), size=(2, 2), grid_size=self.grid_size
    )
    self.tracker.add_polygon('p2', p2)
    modifications = (
        tiling_solver_local._get_flap_modifications_for_cell_for_direction(
            self.config,
            self.tracker,
            grid.Cell(i=1, j=2),
            grid.Direction.SOUTH,
            is_symmetric=True,
        )
    )
    self.assertEmpty(modifications)


class TilingSolutionTest(parameterized.TestCase):

  def test_add_delta_simple(self):
    solution = tiling_solver_local.TilingSolution(
        occupancy_grid=np.zeros((4, 4), dtype=bool)
    )
    delta = RectDelta(
        delta=grid.Delta(di=0, dj=1),
        edge_walk=grid.Walk(
            grid.Cell(i=0, j=0), grid.Direction.SOUTH, grid_size=4, steps=1
        ),
    )
    solution.add_flap_option(tiling_solver_local.FlapOption('flap1', (delta,)))
    self.assertEqual(solution.grid_deltas, {'flap1': grid.Delta(di=0, dj=1)})
    self.assertTrue(solution.occupancy_grid[0, 1])

  def test_add_delta_subdelta(self):
    solution = tiling_solver_local.TilingSolution(
        occupancy_grid=np.zeros((4, 4), dtype=bool)
    )
    delta1 = RectDelta(
        delta=grid.Delta(di=0, dj=2),
        edge_walk=grid.Walk(
            grid.Cell(i=0, j=0), grid.Direction.SOUTH, grid_size=4, steps=1
        ),
    )
    solution.add_flap_option(tiling_solver_local.FlapOption('flap1', (delta1,)))
    self.assertEqual(solution.grid_deltas, {'flap1': grid.Delta(di=0, dj=2)})
    self.assertTrue(solution.occupancy_grid[0, 1])
    self.assertTrue(solution.occupancy_grid[0, 2])

    delta2 = RectDelta(
        delta=grid.Delta(di=0, dj=1),
        edge_walk=grid.Walk(
            grid.Cell(i=0, j=0), grid.Direction.SOUTH, grid_size=4, steps=1
        ),
    )
    solution.add_flap_option(tiling_solver_local.FlapOption('flap1', (delta2,)))
    self.assertEqual(solution.grid_deltas, {'flap1': grid.Delta(di=0, dj=2)})

  def test_add_delta_superdelta(self):
    solution = tiling_solver_local.TilingSolution(
        occupancy_grid=np.zeros((4, 4), dtype=bool)
    )
    delta1 = RectDelta(
        delta=grid.Delta(di=0, dj=1),
        edge_walk=grid.Walk(
            grid.Cell(i=0, j=0), grid.Direction.SOUTH, grid_size=4, steps=1
        ),
    )
    solution.add_flap_option(tiling_solver_local.FlapOption('flap1', (delta1,)))
    self.assertTrue(solution.occupancy_grid[0, 1])
    self.assertFalse(solution.occupancy_grid[0, 2])

    delta2 = RectDelta(
        delta=grid.Delta(di=0, dj=2),
        edge_walk=grid.Walk(
            grid.Cell(i=0, j=0), grid.Direction.SOUTH, grid_size=4, steps=1
        ),
    )
    solution.add_flap_option(tiling_solver_local.FlapOption('flap1', (delta2,)))
    self.assertEqual(solution.grid_deltas, {'flap1': grid.Delta(di=0, dj=2)})
    self.assertTrue(solution.occupancy_grid[0, 1])
    self.assertTrue(solution.occupancy_grid[0, 2])

  def test_add_delta_different_direction_raises_error(self):
    solution = tiling_solver_local.TilingSolution(
        occupancy_grid=np.zeros((4, 4), dtype=bool)
    )
    delta1 = RectDelta(
        delta=grid.Delta(di=0, dj=1),
        edge_walk=grid.Walk(
            grid.Cell(i=0, j=0), grid.Direction.SOUTH, grid_size=4, steps=1
        ),
    )
    solution.add_flap_option(tiling_solver_local.FlapOption('flap1', (delta1,)))
    delta2 = RectDelta(
        delta=grid.Delta(di=1, dj=0),
        edge_walk=grid.Walk(
            grid.Cell(i=0, j=0), grid.Direction.EAST, grid_size=4, steps=1
        ),
    )
    with self.assertRaisesRegex(
        tiling_solver_local.ImpossibleTilingError, 'different axis'
    ):
      solution.add_flap_option(
          tiling_solver_local.FlapOption('flap1', (delta2,))
      )

  def test_add_delta_overlap_raises_error(self):
    occupancy_grid = np.zeros((4, 4), dtype=bool)
    occupancy_grid[0, 1] = True
    solution = tiling_solver_local.TilingSolution(occupancy_grid=occupancy_grid)
    delta = RectDelta(
        delta=grid.Delta(di=0, dj=1),
        edge_walk=grid.Walk(
            grid.Cell(i=0, j=0), grid.Direction.SOUTH, grid_size=4, steps=1
        ),
    )
    with self.assertRaisesRegex(
        tiling_solver_local.ImpossibleTilingError, 'overlaps'
    ):
      solution.add_flap_option(
          tiling_solver_local.FlapOption('flap1', (delta,))
      )


class FindPerfectTilingTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self.mock_plot_tracker = self.enter_context(
        mock.patch.object(utils_tracker, 'plot_tracker', autospec=True)
    )

  def test_tiling_impossible_conflicting_deltas(self):
    tracker = utils_tracker.CreasePatternTracker(4)
    placement = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=4
    )
    tracker.add_polygon('p1', placement)
    new_tracker = tiling_solver_local.find_perfect_tiling_from_local_expansions(
        tracker,
        is_symmetric=False,
        config=config_lib.LocalTilingConfig(
            search_type=config_lib.LocalTilingSearchType.SKIP
        ),
    )
    self.assertIsNone(new_tracker)
    self.mock_plot_tracker.assert_not_called()

  def test_tiling_possible(self):
    tracker = utils_tracker.CreasePatternTracker(4)
    p1 = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=4
    )
    tracker.add_polygon('p1', p1)
    p2 = types.PolygonPlacement.from_grid_coords(
        offset=(0, 2), size=(2, 2), grid_size=4
    )
    tracker.add_polygon('p2', p2)

    new_tracker = tiling_solver_local.find_perfect_tiling_from_local_expansions(
        tracker,
        is_symmetric=False,
        config=config_lib.LocalTilingConfig(
            search_type=config_lib.LocalTilingSearchType.SKIP
        ),
    )
    self.assertIsNotNone(new_tracker)
    self.assertEqual(new_tracker.packed_polygons['p1'].size, (4, 2))
    self.assertEqual(new_tracker.packed_polygons['p2'].size, (4, 2))

  def test_tiling_possible_symmetric(self):
    tracker = utils_tracker.CreasePatternTracker(4)
    p1 = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=4
    )
    tracker.add_polygon('p1', p1)

    new_tracker = tiling_solver_local.find_perfect_tiling_from_local_expansions(
        tracker,
        is_symmetric=True,
        config=config_lib.LocalTilingConfig(
            search_type=config_lib.LocalTilingSearchType.SKIP
        ),
    )
    self.assertIsNotNone(new_tracker)
    self.assertEqual(new_tracker.packed_polygons['p1'].size, (2, 4))


def _create_checkerboard_tracker(
    grid_size: int,
) -> utils_tracker.CreasePatternTracker:
  """Creates a checkerboard pattern of polygons."""
  if grid_size % 2 != 0:
    raise ValueError('Grid size must be even.')
  checkerboard = utils_tracker.CreasePatternTracker(grid_size)
  for i in range(-1, grid_size, 2):
    for j in range(-1, grid_size, 2):
      if (i // 2) % 2 != (j // 2) % 2:
        continue
      checkerboard.add_polygon(
          f'p{i}{j}',
          types.PolygonPlacement.from_grid_coords(
              offset=(i, j), size=(2, 2), grid_size=grid_size
          ),
      )
  return checkerboard


class OptionSearchTest(parameterized.TestCase):

  @parameterized.parameters(
      config_lib.LocalTilingSearchType.BRUTE_FORCE,
      config_lib.LocalTilingSearchType.BACKTRACK,
  )
  def test_tiling_search(self, search_type):
    tracker = utils_tracker.CreasePatternTracker(4)
    p1 = types.PolygonPlacement.from_grid_coords(
        offset=(0, -1), size=(2, 2), grid_size=4
    )
    tracker.add_polygon('p1', p1)
    p2 = types.PolygonPlacement.from_grid_coords(
        offset=(0, 3), size=(2, 2), grid_size=4
    )
    tracker.add_polygon('p2', p2)

    new_tracker = tiling_solver_local.find_perfect_tiling_from_local_expansions(
        tracker,
        is_symmetric=True,
        config=config_lib.LocalTilingConfig(
            search_type=search_type, disable_wide_central_flaps=False
        ),
    )

    self.assertIsNotNone(new_tracker)

    p1_width, p1_height = new_tracker.packed_polygons['p1'].size
    p2_width, p2_height = new_tracker.packed_polygons['p2'].size
    self.assertEqual(p1_width, 2)
    self.assertEqual(p2_width, 2)
    self.assertIn(p1_height + p2_height, (6, 8))

  @parameterized.parameters((config_lib.LocalTilingSearchType.BACKTRACK,))
  def test_tiling_search_checkerboard(self, search_type):
    checkerboard = _create_checkerboard_tracker(grid_size=8)

    start_time = time.perf_counter()

    new_tracker = tiling_solver_local.find_perfect_tiling_from_local_expansions(
        checkerboard,
        is_symmetric=False,
        config=config_lib.LocalTilingConfig(
            search_type=search_type, disable_wide_central_flaps=False
        ),
    )
    logging.info('Time: %s', time.perf_counter() - start_time)

    self.assertIsNotNone(new_tracker)
    self.assertTrue(new_tracker.occupancy_grid.all())

  @parameterized.product(
      search_type=(config_lib.LocalTilingSearchType.BACKTRACK,),
      grid_size=tuple(range(4, 12, 2)),
  )
  def test_tiling_search_checkerboard_impossible(self, search_type, grid_size):
    checkerboard = _create_checkerboard_tracker(grid_size=grid_size)
    checkerboard.remove_by_id('p-1-1')
    checkerboard.remove_by_id(f'p{grid_size-1}{grid_size-1}')

    start_time = time.perf_counter()

    new_tracker = tiling_solver_local.find_perfect_tiling_from_local_expansions(
        checkerboard,
        is_symmetric=False,
        config=config_lib.LocalTilingConfig(
            search_type=search_type, disable_wide_central_flaps=False
        ),
    )
    logging.info('Time: %s', time.perf_counter() - start_time)
    self.assertIsNone(new_tracker)


class HumanBigBellyTilingTest(absltest.TestCase):

  def test_tiling_human_big_belly_step90_succeeds(self):
    tracker = utils_tracker.CreasePatternTracker(16)
    river = river_lib.River(
        width=4,
        offset=5,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=16,
    )
    tracker.add_river('torso', river)
    placements = {
        'torso__ls_river_sf1': types.PolygonPlacement.from_grid_coords(
            offset=(4, 3), size=(4, 2), grid_size=16, require_on_paper=False
        ),
        'torso__ls_river_sf2': types.PolygonPlacement.from_grid_coords(
            offset=(4, 9), size=(4, 2), grid_size=16, require_on_paper=False
        ),
        'head': types.PolygonPlacement.from_grid_coords(
            offset=(2, 3), size=(2, 2), grid_size=16
        ),
        'left_arm': types.PolygonPlacement.from_grid_coords(
            offset=(2, -3), size=(6, 6), grid_size=16
        ),
        'left_leg': types.PolygonPlacement.from_grid_coords(
            offset=(-4, 11), size=(8, 8), grid_size=16
        ),
    }
    for name, placement in placements.items():
      tracker.add_polygon(name, placement)

    solution = tiling_solver_local.find_perfect_tiling_from_local_expansions(
        tracker,
        is_symmetric=True,
        config=config_lib.LocalTilingConfig(disable_wide_central_flaps=False),
    )
    self.assertIsNotNone(solution)

  def test_sacrificial_flap_expansion_only_on_large_side(self):
    tracker = utils_tracker.CreasePatternTracker(8)
    sf = types.PolygonPlacement.from_grid_coords(
        offset=(2, 0), size=(4, 2), grid_size=8
    )
    tracker.add_polygon('sf1', sf)
    config = config_lib.LocalTilingConfig(disable_wide_central_flaps=False)

    mods_east = (
        tiling_solver_local._get_flap_modifications_for_cell_for_direction(
            config,
            tracker,
            grid.Cell(i=0, j=6),
            grid.Direction.WEST,
            is_symmetric=False,
        )
    )
    self.assertNotEmpty(mods_east)

    mods_south = (
        tiling_solver_local._get_flap_modifications_for_cell_for_direction(
            config,
            tracker,
            grid.Cell(i=2, j=2),
            grid.Direction.NORTH,
            is_symmetric=False,
        )
    )
    self.assertEmpty(mods_south)


if __name__ == '__main__':
  absltest.main()
