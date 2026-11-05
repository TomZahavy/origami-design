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

"""Tests for flap placement and validation functions."""

from typing import TypedDict
from unittest import mock

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.crease_pattern import point as point_lib
from bp_pipeline.packing import config as config_lib
from bp_pipeline.packing import flap_placement as flap_placement_lib
from bp_pipeline.packing import types
from bp_pipeline.packing import utils_tracker
from bp_pipeline.stick_figures import stick as stick_lib


class PolygonData(TypedDict):
  """Describes the raw data for a polygon in test parameters.

  Attributes:
      offset: The (x, y) coordinate of the top-left corner of the polygon.
      size: The (width, height) of the polygon.
  """

  offset: tuple[int, int]
  size: tuple[int, int]


class ValidateCandidateTest(parameterized.TestCase):

  @parameterized.named_parameters(
      # --- SUCCESS CASES ---
      dict(
          testcase_name='valid_placement_on_empty_grid',
          grid_size=10,
          existing_polygons={},
          candidate_offset=(4, 4),
          candidate_size=(2, 2),
          is_valid=True,
      ),
      dict(
          testcase_name='valid_placement_touching_another_polygon',
          grid_size=10,
          existing_polygons={'p1': {'offset': (2, 2), 'size': (4, 4)}},
          candidate_offset=(6, 2),
          candidate_size=(2, 4),
          is_valid=True,
      ),
      dict(
          testcase_name='valid_placement_with_center_on_border',
          grid_size=10,
          existing_polygons={},
          candidate_offset=(-2, 8),
          candidate_size=(4, 4),
          is_valid=True,
      ),
      dict(
          testcase_name='valid_placement_ignores_prev_id_for_collision',
          grid_size=10,
          existing_polygons={'p1': {'offset': (2, 2), 'size': (4, 4)}},
          candidate_offset=(6, 2),
          candidate_size=(2, 4),
          is_valid=True,
      ),
      # --- FAILURE CASES ---
      dict(
          testcase_name='fail_if_candidate_has_odd_width',
          grid_size=10,
          existing_polygons={},
          candidate_offset=(4, 4),
          candidate_size=(3, 2),  # Odd width -> non-integer center_x
          is_valid=False,
      ),
      dict(
          testcase_name='fail_if_candidate_has_odd_height',
          grid_size=10,
          existing_polygons={},
          candidate_offset=(4, 4),
          candidate_size=(2, 5),  # Odd height -> non-integer center_y
          is_valid=False,
      ),
      dict(
          testcase_name='fail_if_center_is_outside_grid_bounds',
          grid_size=10,
          existing_polygons={},
          candidate_offset=(10, 10),
          candidate_size=(2, 2),  # Center (11, 11) is > 10
          is_valid=False,
      ),
      dict(
          testcase_name='fail_on_direct_collision',
          grid_size=10,
          existing_polygons={'p1': {'offset': (2, 2), 'size': (4, 4)}},
          candidate_offset=(3, 3),
          candidate_size=(2, 2),
          is_valid=False,
      ),
      dict(
          testcase_name='fail_on_partial_collision',
          grid_size=10,
          existing_polygons={'p1': {'offset': (2, 2), 'size': (4, 4)}},
          candidate_offset=(5, 3),
          candidate_size=(2, 2),
          is_valid=False,
      ),
      dict(
          testcase_name='fail_on_collision_with_polygon_other_than_prev_id',
          grid_size=10,
          existing_polygons={
              'p1': {'offset': (0, 2), 'size': (2, 2)},
              'p2': {'offset': (4, 2), 'size': (2, 2)},
          },
          candidate_offset=(2, 2),
          candidate_size=(4, 2),
          is_valid=False,
      ),
      # --- SYMMETRY TESTS ---
      dict(
          testcase_name='symmetry_on_axis_center_valid',
          grid_size=10,
          existing_polygons={},
          candidate_offset=(4, 4),
          candidate_size=(2, 2),
          is_valid=True,
          is_symmetric=True,
          symmetry_axes={'999': True},
      ),
      dict(
          testcase_name='symmetry_on_axis_off_center_invalid',
          grid_size=10,
          existing_polygons={},
          candidate_offset=(3, 4),
          candidate_size=(2, 2),
          is_valid=False,
          is_symmetric=True,
          symmetry_axes={'999': True},
      ),
      dict(
          testcase_name='symmetry_off_axis_off_center_valid',
          grid_size=10,
          existing_polygons={},
          candidate_offset=(3, 4),
          candidate_size=(2, 2),
          is_valid=True,
          is_symmetric=True,
          symmetry_axes={'999': False},
      ),
      dict(
          testcase_name='symmetry_off_axis_rhs_invalid',
          grid_size=10,
          existing_polygons={},
          candidate_offset=(6, 4),
          candidate_size=(2, 2),
          is_valid=False,
          is_symmetric=True,
          symmetry_axes={'999': False},
      ),
      dict(
          testcase_name='symmetry_off_axis_crossing_center_invalid',
          grid_size=10,
          existing_polygons={},
          candidate_offset=(4, 4),
          candidate_size=(2, 2),
          is_valid=False,
          is_symmetric=True,
          symmetry_axes={'999': False},
      ),
      dict(
          testcase_name='symmetry_disabled_on_axis_off_center_valid',
          grid_size=10,
          existing_polygons={},
          candidate_offset=(3, 4),
          candidate_size=(2, 2),
          is_valid=True,
          is_symmetric=False,
          symmetry_axes={'999': True},
      ),
      dict(
          testcase_name='symmetry_axes_none_is_valid',
          grid_size=10,
          existing_polygons={},
          candidate_offset=(6, 4),
          candidate_size=(2, 2),
          is_valid=True,
          is_symmetric=True,
          symmetry_axes=None,
      ),
  )
  def test_validate_candidate(
      self,
      grid_size: int,
      existing_polygons: dict[str, PolygonData],
      candidate_offset: tuple[int, int],
      candidate_size: tuple[int, int],
      is_valid: bool,
      is_symmetric: bool = False,
      symmetry_axes: dict[str, bool] | None = None,
  ):
    """Tests the validate_candidate function with various scenarios."""
    tracker = utils_tracker.CreasePatternTracker(grid_size)
    for poly_id, p_data in existing_polygons.items():
      placement = types.PolygonPlacement.from_grid_coords(
          offset=p_data['offset'], size=p_data['size'], grid_size=grid_size
      )
      tracker.add_polygon(poly_id, placement)

    result = flap_placement_lib.validate_candidate(
        tracker=tracker,
        current_stick_name='999',
        offset=candidate_offset,
        size=candidate_size,
        is_symmetric=is_symmetric,
        symmetry_axes=symmetry_axes,
    )

    if is_valid:
      self.assertIsNotNone(result, 'Expected a valid candidate, but got None.')
      self.assertEqual(result['placement'].offset, candidate_offset)
      self.assertEqual(result['placement'].size, candidate_size)
    else:
      self.assertIsNone(result, 'Expected None, but got a valid candidate.')


class FindAllUnoccupiedPlacementsTest(parameterized.TestCase):

  @parameterized.named_parameters(
      dict(
          testcase_name=(
              'finds_all_slots_for_2x2_in_4x4_grid_including_overhang'
          ),
          is_symmetric=False,
          symmetry_axes=None,
          grid_size=4,
          existing_polygons={},
          candidate_size=(2, 2),
          expected_offsets=[
              (-1, -1),
              (-1, 0),
              (-1, 1),
              (-1, 2),
              (-1, 3),
              (0, -1),
              (0, 0),
              (0, 1),
              (0, 2),
              (0, 3),
              (1, -1),
              (1, 0),
              (1, 1),
              (1, 2),
              (1, 3),
              (2, -1),
              (2, 0),
              (2, 1),
              (2, 2),
              (2, 3),
              (3, -1),
              (3, 0),
              (3, 1),
              (3, 2),
              (3, 3),
          ],
      ),
      dict(
          testcase_name='finds_all_slots_in_a_crowded_grid_including_overhang',
          is_symmetric=False,
          symmetry_axes=None,
          grid_size=4,
          existing_polygons={
              'left_wall': {'offset': (0, 0), 'size': (2, 4)},
              'right_wall': {'offset': (2, 2), 'size': (2, 2)},
          },
          candidate_size=(2, 2),
          expected_offsets=[(2, 0), (2, -1), (3, 0), (3, -1)],
      ),
      dict(
          testcase_name='returns_empty_if_grid_is_full',
          is_symmetric=False,
          symmetry_axes=None,
          grid_size=4,
          existing_polygons={'full': {'offset': (0, 0), 'size': (4, 4)}},
          candidate_size=(2, 2),
          expected_offsets=[],
      ),
      dict(
          testcase_name=(
              'finds_correct_overhanging_placements_for_large_candidate'
          ),
          is_symmetric=False,
          symmetry_axes=None,
          grid_size=4,
          existing_polygons={},
          candidate_size=(6, 6),
          expected_offsets=[
              (-3, -3),
              (-2, -3),
              (-3, -2),
              (-2, -2),
              (1, -3),
              (0, -3),
              (1, -2),
              (0, -2),
              (-3, 1),
              (-2, 1),
              (-3, 0),
              (-2, 0),
              (1, 1),
              (0, 1),
              (1, 0),
              (0, 0),
          ],
      ),
      dict(
          testcase_name='symmetry_on_axis_returns_only_center_line',
          grid_size=4,
          existing_polygons={},
          candidate_size=(2, 2),
          is_symmetric=True,
          symmetry_axes={'999': True},
          expected_offsets=[(1, -1), (1, 0), (1, 1), (1, 2), (1, 3)],
      ),
  )
  def test_find_all_unoccupied_placements(
      self,
      grid_size,
      existing_polygons,
      candidate_size,
      expected_offsets,
      is_symmetric,
      symmetry_axes,
  ):
    """Tests the brute-force placement generation via integration."""
    tracker = utils_tracker.CreasePatternTracker(grid_size)
    for poly_id, p_data in existing_polygons.items():
      placement = types.PolygonPlacement.from_grid_coords(
          offset=p_data['offset'], size=p_data['size'], grid_size=grid_size
      )
      tracker.add_polygon(poly_id, placement)

    stick_name_to_dims = {'999': candidate_size}
    result = flap_placement_lib.find_all_unoccupied_placements(
        tracker,
        '999',
        stick_name_to_dims,
        is_symmetric=is_symmetric,
        symmetry_axes=symmetry_axes,
    )
    result_offsets = {p['placement'].offset for p in result}
    self.assertCountEqual(result_offsets, expected_offsets)


class FindAnalyticallyValidPlacementsTest(parameterized.TestCase):

  @parameterized.named_parameters(
      dict(
          testcase_name='finds_all_sliding_placements_on_empty_background',
          is_symmetric=False,
          symmetry_axes=None,
          grid_size=20,
          existing_polygons={
              'p1': {'offset': (8, 8), 'size': (4, 4)},
          },
          candidate_size=(2, 2),
          constraints={'1': {'type': types.ConstraintType.EQUAL, 'value': 0}},
          expected_offsets=[
              (7, 12),
              (8, 12),
              (9, 12),
              (10, 12),
              (11, 12),
              (7, 6),
              (8, 6),
              (9, 6),
              (10, 6),
              (11, 6),
              (12, 7),
              (12, 8),
              (12, 9),
              (12, 10),
              (12, 11),
              (6, 7),
              (6, 8),
              (6, 9),
              (6, 10),
              (6, 11),
          ],
      ),
      dict(
          testcase_name='sliding_is_blocked_by_another_polygon',
          is_symmetric=False,
          symmetry_axes=None,
          grid_size=20,
          existing_polygons={
              'p1': {'offset': (8, 8), 'size': (4, 4)},
              'blocker': {'offset': (6, 10), 'size': (2, 2)},
          },
          candidate_size=(2, 2),
          constraints={'1': {'type': types.ConstraintType.EQUAL, 'value': 0}},
          expected_offsets=[
              (7, 12),
              (8, 12),
              (9, 12),
              (10, 12),
              (11, 12),
              (7, 6),
              (8, 6),
              (9, 6),
              (10, 6),
              (11, 6),
              (12, 7),
              (12, 8),
              (12, 9),
              (12, 10),
              (12, 11),
              (6, 7),
              (6, 8),
          ],
      ),
      dict(
          testcase_name='finds_placements_around_multiple_constrained_polygons',
          is_symmetric=False,
          symmetry_axes=None,
          grid_size=30,
          existing_polygons={
              'p1': {'offset': (2, 2), 'size': (2, 2)},
              'p2': {'offset': (22, 22), 'size': (2, 2)},
          },
          candidate_size=(2, 2),
          constraints={
              '1': {'type': types.ConstraintType.EQUAL, 'value': 0},
              '2': {'type': types.ConstraintType.EQUAL, 'value': 0},
          },
          expected_offsets=[
              (1, 4),
              (2, 4),
              (3, 4),
              (1, 0),
              (2, 0),
              (3, 0),
              (4, 1),
              (4, 2),
              (4, 3),
              (0, 1),
              (0, 2),
              (0, 3),
              (21, 24),
              (22, 24),
              (23, 24),
              (21, 20),
              (22, 20),
              (23, 20),
              (24, 21),
              (24, 22),
              (24, 23),
              (20, 21),
              (20, 22),
              (20, 23),
          ],
      ),
      dict(
          testcase_name='symmetry_with_adjacency',
          grid_size=10,
          existing_polygons={'p1': {'offset': (4, 0), 'size': (2, 8)}},
          candidate_size=(2, 2),
          constraints={'1': {'type': types.ConstraintType.EQUAL, 'value': 0}},
          is_symmetric=True,
          symmetry_axes={'1': True, '999': True},
          expected_offsets=[(4, 8)],
      ),
  )
  def test_find_analytically_valid_placements(
      self,
      grid_size,
      existing_polygons,
      candidate_size,
      constraints,
      expected_offsets,
      is_symmetric,
      symmetry_axes,
  ):
    """Tests analytical placement generation via integration."""
    tracker = utils_tracker.CreasePatternTracker(grid_size)
    for poly_id, p_data in existing_polygons.items():
      placement = types.PolygonPlacement.from_grid_coords(
          offset=p_data['offset'], size=p_data['size'], grid_size=grid_size
      )
      if poly_id.startswith('p'):
        poly_stick_name = poly_id.replace('p', '')
        tracker.add_polygon(poly_stick_name, placement)
      else:
        tracker.add_polygon(poly_id, placement)

    stick_name_to_dims = {'999': candidate_size}

    result = flap_placement_lib.find_analytically_valid_placements(
        tracker=tracker,
        current_stick_name='999',
        constraints=constraints,
        stick_name_to_dims=stick_name_to_dims,
        is_symmetric=is_symmetric,
        symmetry_axes=symmetry_axes,
    )

    result_offsets = {p['placement'].offset for p in result}
    self.assertCountEqual(result_offsets, expected_offsets)


class MockFindPossibleFlapPlacementsTest(parameterized.TestCase):
  """Tests the dispatching logic of find_possible_flap_placements."""

  def setUp(self):
    super().setUp()
    self.tracker = utils_tracker.CreasePatternTracker(grid_size=10)
    self.stick_name_to_dims = {'999': (2, 2)}
    self.current_stick_name = '999'
    self.stick = stick_lib.Stick(
        name=self.current_stick_name,
        start='a',
        end='b',
        azimuth_angle=0,
        length=1,
    )

    self.mock_origin = self.enter_context(
        mock.patch.object(
            flap_placement_lib,
            '_place_first_polygon_at_origin',
            return_value='origin',
        )
    )
    self.mock_analytical = self.enter_context(
        mock.patch.object(
            flap_placement_lib,
            'find_analytically_valid_placements',
            return_value=['analytical'],
        )
    )
    self.mock_unoccupied = self.enter_context(
        mock.patch.object(
            flap_placement_lib,
            'find_all_unoccupied_placements',
            return_value=['unoccupied'],
        )
    )
    self.mock_sort_candidates = self.enter_context(
        mock.patch(
            'bp_pipeline.packing.scoring.ScoringConfig.sort_candidates',
            side_effect=lambda tracker, candidates: candidates,
        )
    )
    self.mock_prune_candidates = self.enter_context(
        mock.patch(
            'bp_pipeline.packing.scoring.ScoringConfig.prune_candidates',
            side_effect=lambda tracker, candidates: candidates,
        )
    )

  def test_dispatches_to_place_on_corner_for_first_polygon(self):
    """Verifies it calls the corner placement logic for the first piece."""
    result = list(
        flap_placement_lib.find_possible_flap_placements(
            tracker=self.tracker,
            stick=self.stick,
            current_stick_name=self.current_stick_name,
            constraints={},
            stick_name_to_dims=self.stick_name_to_dims,
        )
    )
    self.mock_origin.assert_called_once_with(
        self.current_stick_name, self.stick_name_to_dims
    )
    self.mock_analytical.assert_not_called()
    self.mock_unoccupied.assert_not_called()
    self.assertEqual(result, ['origin'])

  def test_skips_place_on_corner_for_first_polygon_if_symmetric_and_on_axis(
      self,
  ):
    """Verifies it skips corner placement for on-axis piece in symmetric packing."""
    self.tracker.packed_polygons.clear()
    result = list(
        flap_placement_lib.find_possible_flap_placements(
            tracker=self.tracker,
            stick=self.stick,
            current_stick_name=self.current_stick_name,
            constraints={},
            stick_name_to_dims=self.stick_name_to_dims,
            is_symmetric=True,
            symmetry_axes={self.current_stick_name: True},
        )
    )
    self.mock_origin.assert_not_called()
    self.mock_analytical.assert_not_called()
    self.mock_unoccupied.assert_called_once_with(
        self.tracker,
        self.current_stick_name,
        self.stick_name_to_dims,
        is_symmetric=True,
        symmetry_axes={self.current_stick_name: True},
        remove_central_crease=False,
    )
    self.assertEqual(result, ['unoccupied'])

  def test_dispatches_to_unoccupied_when_not_constrained(self):
    """Verifies it calls the brute-force solver when no constraints exist."""
    self.tracker.add_polygon(
        '1',
        types.PolygonPlacement.from_grid_coords(
            offset=(0, 0), size=(2, 2), grid_size=self.tracker.grid_size
        ),
    )
    constraints = {'1': {'type': types.ConstraintType.UNSPECIFIED, 'value': 5}}

    result = list(
        flap_placement_lib.find_possible_flap_placements(
            tracker=self.tracker,
            stick=self.stick,
            current_stick_name=self.current_stick_name,
            constraints=constraints,  # pyrefly: ignore[bad-argument-type]
            stick_name_to_dims=self.stick_name_to_dims,
        )
    )
    self.mock_origin.assert_not_called()
    self.mock_analytical.assert_not_called()
    self.mock_unoccupied.assert_called_once_with(
        self.tracker,
        self.current_stick_name,
        self.stick_name_to_dims,
        is_symmetric=False,
        symmetry_axes=None,
        remove_central_crease=False,
    )
    self.assertEqual(result, ['unoccupied'])

  def test_dispatches_to_unoccupied_when_proximity_constraints_not_enforced(
      self,
  ):
    """Verifies it calls the brute-force solver when proximity constraints are not enforced."""
    self.mock_unoccupied.return_value = ['unoccupied']
    self.tracker.add_polygon(
        '1',
        types.PolygonPlacement.from_grid_coords(
            offset=(0, 0), size=(2, 2), grid_size=self.tracker.grid_size
        ),
    )
    constraints = {'1': {'type': types.ConstraintType.EQUAL, 'value': 0}}

    result = list(
        flap_placement_lib.find_possible_flap_placements(
            tracker=self.tracker,
            stick=self.stick,
            current_stick_name=self.current_stick_name,
            constraints=constraints,  # pyrefly: ignore[bad-argument-type]
            stick_name_to_dims=self.stick_name_to_dims,
            enforce_proximity_constraints=False,
        )
    )
    self.mock_origin.assert_not_called()
    self.mock_analytical.assert_not_called()
    self.mock_unoccupied.assert_called_once_with(
        self.tracker,
        self.current_stick_name,
        self.stick_name_to_dims,
        is_symmetric=False,
        symmetry_axes=None,
        remove_central_crease=False,
    )
    self.assertEqual(result, ['unoccupied'])

  def test_paired_axis_placements_are_generated(self):
    """Verifies generation of PAIRED_ON_AXIS candidates."""
    self.mock_unoccupied.return_value = []
    self.tracker.packed_polygons.clear()
    self.tracker.grid_size = 6
    stick_name_to_dims = {'888': (2, 2)}
    result = list(
        flap_placement_lib.find_possible_flap_placements(
            tracker=self.tracker,
            stick=stick_lib.Stick(
                name='888', start='a', end='b', azimuth_angle=0, length=1
            ),
            current_stick_name='888',
            constraints={},
            stick_name_to_dims=stick_name_to_dims,
            is_symmetric=True,
            symmetry_axes={'888': False},
            allow_paired_axis_placement=True,
            start_on_corner=False,
        )
    )

    self.mock_origin.assert_not_called()
    self.mock_analytical.assert_not_called()
    self.mock_unoccupied.assert_called_once()

    paired_candidates = [c for c in result if c['type'] == 'PAIRED_ON_AXIS']
    self.assertLen(paired_candidates, 30)


class FindPossibleFlapPlacementsTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.tracker = utils_tracker.CreasePatternTracker(grid_size=10)
    self.stick_name_to_dims = {'999': (2, 2)}
    self.current_stick_name = '999'
    self.stick = stick_lib.Stick(
        name=self.current_stick_name,
        start='a',
        end='b',
        azimuth_angle=0,
        length=1,
    )

  def test_constrained_placement_from_possible_flaps(self):
    self.tracker.add_polygon(
        '1',
        types.PolygonPlacement.from_grid_coords(
            offset=(0, 0), size=(2, 2), grid_size=self.tracker.grid_size
        ),
    )
    constraints = {'1': {'type': types.ConstraintType.EQUAL, 'value': 0}}
    expected_centers = [
        point_lib.Point(x=0, y=0.3),
        point_lib.Point(x=0.1, y=0.3),
        point_lib.Point(x=0.2, y=0.3),
        point_lib.Point(x=0.3, y=0),
        point_lib.Point(x=0.3, y=0.1),
        point_lib.Point(x=0.3, y=0.2),
    ]
    result = list(
        flap_placement_lib.find_possible_flap_placements(
            tracker=self.tracker,
            stick=self.stick,
            current_stick_name=self.current_stick_name,
            constraints=constraints,  # pyrefly: ignore[bad-argument-type]
            stick_name_to_dims=self.stick_name_to_dims,
        )
    )
    self.assertLen(result, 6)
    for candidate in result:
      placement = candidate['placement']
      self.assertEqual(candidate['type'], 'FLAP')
      self.assertEqual(placement.size, (2, 2))
      self.assertTrue(
          any(
              placement.center.isclose(expected_center)
              for expected_center in expected_centers
          )
      )

  def test_river_adjacent_cells_applied_when_not_easy_mode(self):
    tracker = utils_tracker.CreasePatternTracker(grid_size=30)
    stick_name_to_dims = {'head': (4, 4)}
    stick = stick_lib.Stick(
        name='head',
        start='a',
        end='b',
        azimuth_angle=0,
        length=2,
    )
    config = config_lib.PackingConfig()
    river_adjacent_cells = [(14, 14), (14, 15), (15, 14), (15, 15)]

    result = list(
        flap_placement_lib.find_possible_flap_placements(
            tracker=tracker,
            stick=stick,
            current_stick_name='head',
            constraints={},
            stick_name_to_dims=stick_name_to_dims,
            is_symmetric=True,
            symmetry_axes={'head': True},
            start_on_corner=False,
            config=config,
            river_adjacent_cells=river_adjacent_cells,
        )
    )
    for candidate in result:
      placement = candidate['placement']
      self.assertTrue(
          flap_placement_lib._placement_touches_cells(
              placement, river_adjacent_cells
          )
      )


class PlaceFirstPolygonAtOriginTest(parameterized.TestCase):
  """Tests the helper function for placing the first polygon."""

  def test_places_polygon_centered_at_origin(self):
    """Verifies the function calculates the correct offset."""
    stick_name_to_dims = {'10': (4, 6)}
    candidate = flap_placement_lib._place_first_polygon_at_origin(
        '10', stick_name_to_dims
    )

    self.assertEqual(candidate['stick_name'], '10')
    self.assertEqual(candidate['type'], 'FLAP')

    placement = candidate['placement']
    self.assertEqual(placement.offset, (-2, -3))
    self.assertEqual(placement.size, (4, 6))


class PlacementTouchesCellsTest(parameterized.TestCase):

  @parameterized.named_parameters(
      dict(
          testcase_name='touches',
          offset=(1, 1),
          size=(2, 2),
          cells=[(1, 1), (5, 5)],
          expected=True,
      ),
      dict(
          testcase_name='does_not_touch',
          offset=(1, 1),
          size=(2, 2),
          cells=[(0, 0), (3, 3)],
          expected=False,
      ),
      dict(
          testcase_name='empty_cells',
          offset=(1, 1),
          size=(2, 2),
          cells=[],
          expected=False,
      ),
  )
  def test_placement_touches_cells(self, offset, size, cells, expected):
    placement = types.PolygonPlacement.from_grid_coords(
        offset=offset, size=size, grid_size=10
    )
    self.assertEqual(
        flap_placement_lib._placement_touches_cells(placement, cells), expected
    )


class IsCenterAxisOnPaperTest(parameterized.TestCase):

  @parameterized.named_parameters(
      dict(
          testcase_name='center_on_paper',
          offset=(2, 0),
          size=(4, 6),
          grid_size=10,
          expected=True,
      ),
      dict(
          testcase_name='center_on_left_boundary',
          offset=(0, 0),
          size=(4, 6),
          grid_size=10,
          expected=True,
      ),
      dict(
          testcase_name='center_on_right_boundary',
          offset=(8, 0),
          size=(4, 6),
          grid_size=10,
          expected=True,
      ),
      dict(
          testcase_name='center_off_paper_left',
          offset=(-4, 0),
          size=(4, 6),
          grid_size=10,
          expected=False,
      ),
      dict(
          testcase_name='center_off_paper_right',
          offset=(10, 0),
          size=(4, 6),
          grid_size=10,
          expected=False,
      ),
      dict(
          testcase_name='height_exactly_fits',
          offset=(2, 0),
          size=(4, 10),
          grid_size=10,
          expected=True,
      ),
      dict(
          testcase_name='height_overflows_bottom',
          offset=(2, 2),
          size=(4, 10),
          grid_size=10,
          expected=True,
      ),
      dict(
          testcase_name='height_overflows_top',
          offset=(2, -1),
          size=(4, 6),
          grid_size=10,
          expected=True,
      ),
      dict(
          testcase_name='36x52_in_40_grid_negative_offset',
          offset=(-18, 12),
          size=(36, 52),
          grid_size=40,
          expected=True,
      ),
      dict(
          testcase_name='36x52_in_68_grid_fits',
          offset=(16, 8),
          size=(36, 52),
          grid_size=68,
          expected=True,
      ),
  )
  def test_is_center_axis_on_paper(self, offset, size, grid_size, expected):
    placement = types.PolygonPlacement.from_grid_coords(
        offset=offset, size=size, grid_size=grid_size, require_on_paper=False
    )
    self.assertEqual(
        flap_placement_lib.is_center_axis_on_paper(placement, grid_size),
        expected,
    )


if __name__ == '__main__':
  absltest.main()
