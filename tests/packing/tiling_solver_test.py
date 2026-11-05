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

import math
from typing import Any, TypedDict
from unittest import mock

from absl.testing import absltest
from bp_pipeline import utils_tree
from bp_pipeline.packing import config as config_lib
from bp_pipeline.packing import tiling_solver
from bp_pipeline.packing import types
from bp_pipeline.packing import utils_packing_svg
from bp_pipeline.packing import utils_tracker
from bp_pipeline.packing.debug import debug_types
from bp_pipeline.stick_figures import stick as stick_lib
from bp_pipeline.stick_figures import stick_figure
import numpy as np


class PolygonData(TypedDict):
  """Describes the raw data for a polygon in test parameters.

  Attributes:
      offset: The (x, y) coordinate of the top-left corner of the polygon.
      size: The (width, height) of the polygon.
  """

  offset: tuple[int, int]
  size: tuple[int, int]


def _make_stick(name: str, length: int = 1) -> stick_lib.Stick:
  return stick_lib.Stick(
      name=name, start='a', end='b', azimuth_angle=0, length=length
  )


def _bps_to_stick_figure(bps: dict[str, Any]) -> stick_figure.StickFigure:
  data = bps['design']
  tree = data['tree']
  nodes = {node['id']: node for node in tree['nodes']}
  children = []
  root_edge = tree['edges'][0]
  root_name = f"{nodes[root_edge['n1']]['id']}_{nodes[root_edge['n2']]['id']}"
  for edge in tree['edges']:
    start = nodes[edge['n1']]
    end = nodes[edge['n2']]
    dy = end['y'] - start['y']
    dx = end['x'] - start['x']
    angle = (math.degrees(math.atan2(dy, dx)) - 90) % 360
    length = round(edge['length'] or 1)
    children.append(
        stick_lib.Stick(
            start=str(start['id']),
            end=str(end['id']),
            name=f"{start['id']}_{end['id']}",
            length=length,
            azimuth_angle=angle,
        )
    )
  return stick_figure.StickFigure(
      name=data['title'],
      category='',
      complexity=1,
      root=root_name,
      children=children,
  )


@mock.patch('bp_pipeline.packing.flap_placement.find_possible_flap_placements')
class SolverAlgorithmTest(absltest.TestCase):
  """Tests the logic of the iterative backtracking solver."""

  def setUp(self):
    super().setUp()
    self.tracker = utils_tracker.CreasePatternTracker(grid_size=10)
    self.stick_name_to_dims = {
        'polygon_0': (2, 2),
        'polygon_1': (2, 2),
        'polygon_2': (2, 2),
        'polygon_999': (2, 2),
    }
    self.polygon_a = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=10
    )
    self.polygon_b = types.PolygonPlacement.from_grid_coords(
        offset=(2, 2), size=(2, 2), grid_size=10
    )
    self.polygon_c = types.PolygonPlacement.from_grid_coords(
        offset=(4, 4), size=(2, 2), grid_size=10
    )
    self.polygon_d = types.PolygonPlacement.from_grid_coords(
        offset=(6, 6), size=(2, 2), grid_size=10
    )
    self.polygon_e = types.PolygonPlacement.from_grid_coords(
        offset=(8, 8), size=(2, 2), grid_size=10
    )

  def _create_candidate(self, placement, stick_name: str):
    """Helper to create the candidate dictionary structure."""
    return {
        'type': 'POLYGON',
        'placement': placement,
        'stick_name': stick_name,
    }

  def _get_one_level_backtracking_logic(self):
    """Returns the side_effect function for the one-level backtrack test."""

    def find_placements_logic(tracker, current_stick_name, *args, **kwargs):
      del args, kwargs
      if current_stick_name == 'polygon_0':
        return iter([
            self._create_candidate(self.polygon_a, 'polygon_0'),
            self._create_candidate(self.polygon_b, 'polygon_0'),
        ])
      if current_stick_name == 'polygon_1':
        if (
            'polygon_0' in tracker.packed_polygons
            and tracker.packed_polygons['polygon_0'] == self.polygon_b
        ):
          return iter([self._create_candidate(self.polygon_c, 'polygon_1')])
      return iter([])

    return find_placements_logic

  def _get_deep_backtracking_logic(self):
    """Returns the side_effect function for the deep backtrack tests."""

    def deep_backtracking_logic(tracker, current_stick_name, *args, **kwargs):
      del args, kwargs
      packed = tracker.packed_polygons
      if current_stick_name == 'polygon_0':
        return iter([
            self._create_candidate(self.polygon_a, stick_name='polygon_0'),
            self._create_candidate(self.polygon_b, stick_name='polygon_0'),
        ])
      if current_stick_name == 'polygon_1':
        if 'polygon_0' in packed and packed['polygon_0'] == self.polygon_a:
          return iter(
              [self._create_candidate(self.polygon_c, stick_name='polygon_1')]
          )
        if 'polygon_0' in packed and packed['polygon_0'] == self.polygon_b:
          return iter(
              [self._create_candidate(self.polygon_d, stick_name='polygon_1')]
          )
      if current_stick_name == 'polygon_2':
        if (
            'polygon_0' in packed
            and packed['polygon_0'] == self.polygon_b
            and 'polygon_1' in packed
            and packed['polygon_1'] == self.polygon_d
        ):
          return iter(
              [self._create_candidate(self.polygon_e, stick_name='polygon_2')]
          )
      return iter([])

    return deep_backtracking_logic

  def test_simple_success_path(self, mock_find_placements):
    """Tests a scenario where a solution is found on the first try for each step."""
    traversal_plan = [
        {'stick': _make_stick('polygon_0'), 'constraints': {}},
        {'stick': _make_stick('polygon_1'), 'constraints': {}},
    ]
    mock_find_placements.side_effect = [
        iter([self._create_candidate(self.polygon_a, stick_name='polygon_0')]),
        iter([self._create_candidate(self.polygon_b, stick_name='polygon_1')]),
    ]
    iterator = tiling_solver.solve_packing_iteratively(
        traversal_plan,  # pyrefly: ignore[bad-argument-type]
        self.tracker,
        self.stick_name_to_dims,
        grid_width=10,
        grid_height=10,
        debug=debug_types.DebugConfig(),
    )
    result = next(iterator, None)
    self.assertIsNotNone(result)
    self.assertIn('polygon_0', self.tracker.packed_polygons)

  def test_failure_due_to_no_candidates(self, mock_find_placements):
    """Tests a scenario where a step has no possible placements, leading to failure."""
    traversal_plan = [
        {'stick': _make_stick('polygon_0'), 'constraints': {}},
        {'stick': _make_stick('polygon_1'), 'constraints': {}},
    ]
    mock_find_placements.side_effect = [
        iter([self._create_candidate(self.polygon_a, stick_name='polygon_0')]),
        iter([]),
    ]
    iterator = tiling_solver.solve_packing_iteratively(
        traversal_plan,  # pyrefly: ignore[bad-argument-type]
        self.tracker,
        self.stick_name_to_dims,
        grid_width=10,
        grid_height=10,
        debug=debug_types.DebugConfig(),
    )
    result = next(iterator, None)
    self.assertIsNone(result)
    self.assertEmpty(self.tracker.packed_polygons)

  def test_backtracking_success_one_level(self, mock_find_placements):
    """Tests a scenario forcing the solver to backtrack and try a second choice."""
    traversal_plan = [
        {'stick': _make_stick('polygon_0'), 'constraints': {}},
        {'stick': _make_stick('polygon_1'), 'constraints': {}},
    ]
    mock_find_placements.side_effect = self._get_one_level_backtracking_logic()
    iterator = tiling_solver.solve_packing_iteratively(
        traversal_plan,  # pyrefly: ignore[bad-argument-type]
        self.tracker,
        self.stick_name_to_dims,
        grid_width=10,
        grid_height=10,
        debug=debug_types.DebugConfig(),
        is_symmetric=False,
        symmetry_axes=None,
    )
    result = next(iterator, None)
    self.assertIsNotNone(result)
    self.assertEqual(self.tracker.packed_polygons['polygon_0'], self.polygon_b)
    self.assertEqual(self.tracker.packed_polygons['polygon_1'], self.polygon_c)

  def test_deep_backtracking_success(self, mock_find_placements):
    """Tests backtracking over multiple levels to find a valid solution path."""
    traversal_plan = [
        {'stick': _make_stick('polygon_0'), 'constraints': {}},
        {'stick': _make_stick('polygon_1'), 'constraints': {}},
        {'stick': _make_stick('polygon_2'), 'constraints': {}},
    ]
    mock_find_placements.side_effect = self._get_deep_backtracking_logic()
    iterator = tiling_solver.solve_packing_iteratively(
        traversal_plan,  # pyrefly: ignore[bad-argument-type]
        self.tracker,
        self.stick_name_to_dims,
        grid_width=10,
        grid_height=10,
        debug=debug_types.DebugConfig(),
        is_symmetric=False,
        symmetry_axes=None,
    )
    result = next(iterator, None)
    self.assertIsNotNone(result)
    self.assertEqual(self.tracker.packed_polygons['polygon_0'], self.polygon_b)
    self.assertEqual(self.tracker.packed_polygons['polygon_1'], self.polygon_d)
    self.assertEqual(self.tracker.packed_polygons['polygon_2'], self.polygon_e)

  def test_deep_backtracking_path_is_correct(self, mock_find_placements):
    """Verifies the exact sequence of adds/removes during deep backtracking."""
    traversal_plan = [
        {'stick': _make_stick('polygon_0'), 'constraints': {}},
        {'stick': _make_stick('polygon_1'), 'constraints': {}},
        {'stick': _make_stick('polygon_2'), 'constraints': {}},
    ]
    packed_polygons = {}
    mock_tracker = mock.Mock()
    mock_tracker.packed_polygons = packed_polygons
    mock_tracker.remove_by_id.side_effect = packed_polygons.pop
    mock_tracker.add_polygon.side_effect = packed_polygons.__setitem__

    mock_find_placements.side_effect = self._get_deep_backtracking_logic()

    iterator = tiling_solver.solve_packing_iteratively(
        traversal_plan,  # pyrefly: ignore[bad-argument-type]
        mock_tracker,
        self.stick_name_to_dims,
        grid_width=10,
        grid_height=10,
        debug=debug_types.DebugConfig(),
        is_symmetric=False,
        symmetry_axes=None,
    )
    result = next(iterator, None)

    self.assertIsNotNone(result)
    expected_calls = [
        mock.call.add_polygon('polygon_0', self.polygon_a),
        mock.call.add_polygon('polygon_1', self.polygon_c),
        mock.call.remove_by_id('polygon_1'),
        mock.call.remove_by_id('polygon_0'),
        mock.call.add_polygon('polygon_0', self.polygon_b),
        mock.call.add_polygon('polygon_1', self.polygon_d),
        mock.call.add_polygon('polygon_2', self.polygon_e),
    ]
    self.assertEqual(mock_tracker.method_calls, expected_calls)

  def test_paired_placement_success(self, mock_find_placements):
    """Tests a scenario where a paired placement is found and applied."""
    traversal_plan = [
        {'stick': _make_stick('polygon_0'), 'constraints': {}},
    ]
    paired_candidate = {
        'type': 'PAIRED_ON_AXIS',
        'stick_name': 'polygon_0',
        'placement': self.polygon_a,
        'partner_placement': self.polygon_b,
    }
    mock_find_placements.side_effect = [
        iter([paired_candidate]),
    ]
    iterator = tiling_solver.solve_packing_iteratively(
        traversal_plan,  # pyrefly: ignore[bad-argument-type]
        self.tracker,
        self.stick_name_to_dims,
        grid_width=10,
        grid_height=10,
        debug=debug_types.DebugConfig(),
        is_symmetric=True,
        symmetry_axes={'polygon_0': False},
        allow_paired_axis_placement=True,
    )
    result = next(iterator, None)
    self.assertIsNotNone(result)
    self.assertIn('polygon_0', self.tracker.packed_polygons)
    self.assertIn(
        f'polygon_0{utils_packing_svg.PolygonIDSuffix.COPY.value}',
        self.tracker.packed_polygons,
    )
    self.assertEqual(self.tracker.packed_polygons['polygon_0'], self.polygon_a)
    self.assertEqual(
        self.tracker.packed_polygons[
            f'polygon_0{utils_packing_svg.PolygonIDSuffix.COPY.value}'
        ],
        self.polygon_b,
    )

  def test_solve_packing_require_perfect_tiling_backtrack(
      self, mock_find_placements
  ):
    """Tests that require_perfect_tiling=True forces backtracking."""
    grid_size = 2
    tracker = utils_tracker.CreasePatternTracker(grid_size)
    stick_name_to_dims = {'polygon_0': (2, 2)}
    traversal_plan = [{'stick': _make_stick('0'), 'constraints': {}}]

    imperfect_placement = types.PolygonPlacement.from_grid_coords(
        offset=(-1, -1), size=(2, 2), grid_size=grid_size
    )
    perfect_placement = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=grid_size
    )

    mock_find_placements.return_value = iter([
        self._create_candidate(imperfect_placement, 'polygon_0'),
        self._create_candidate(perfect_placement, 'polygon_0'),
    ])

    iterator = tiling_solver.solve_packing_iteratively(
        traversal_plan,  # pyrefly: ignore[bad-argument-type]
        tracker,
        stick_name_to_dims,
        grid_width=grid_size,
        grid_height=grid_size,
        debug=debug_types.DebugConfig(),
        require_perfect_tiling=True,
    )
    result = next(iterator, None)

    self.assertIsNotNone(result)
    self.assertIn('polygon_0', tracker.packed_polygons)
    self.assertEqual(tracker.packed_polygons['polygon_0'], perfect_placement)


class PackFlapsWithAdjacencyTest(absltest.TestCase):

  @mock.patch.object(tiling_solver, 'solve_packing_iteratively')
  def test_pack_flaps_with_adjacency_no_solution(
      self, mock_solve_packing_iteratively
  ):
    mock_solve_packing_iteratively.return_value = iter([])
    traversal_plan = [{'stick': _make_stick('p1'), 'constraints': {}}]
    base_square_dims = {'p1': (2, 2)}
    with self.assertLogs(level='ERROR') as log_output:
      results = list(
          tiling_solver.pack_flaps_with_adjacency(
              traversal_plan=traversal_plan,  # pyrefly: ignore[bad-argument-type]
              base_square_dims=base_square_dims,
              grid_size_for_tracker=10,
              grid_width=10,
              grid_height=10,
              debug=debug_types.DebugConfig(),
          )
      )
    self.assertEmpty(results)
    self.assertNotEmpty(log_output.records)
    self.assertIn(
        'Initial packing of squares FAILED', log_output.records[0].getMessage()
    )


class FindConstrainedTilingTest(absltest.TestCase):

  def test_find_constrained_tiling_rectangular_throws_error(self):
    tree = {
        'version': 'None',
        'design': {
            'title': 'None',
            'mode': 'tree',
            'description': '',
            'layout': {
                'sheet': {'type': 'rect', 'height': 16, 'width': 16},
                'flaps': [
                    {'id': 1, 'x': 8, 'y': 10, 'width': 0, 'height': 0},
                    {'id': 2, 'x': 8, 'y': 6, 'width': 0, 'height': 0},
                ],
                'stretches': [],
            },
            'tree': {
                'sheet': {'type': 'rect', 'height': 20, 'width': 20},
                'nodes': [
                    {'id': 0, 'name': '', 'x': 10, 'y': 10},
                    {'id': 1, 'name': '', 'x': 10, 'y': 13},
                    {'id': 2, 'name': '', 'x': 10, 'y': 7},
                ],
                'edges': [
                    {'n1': 0, 'n2': 1, 'length': 4},
                    {'n1': 0, 'n2': 2, 'length': 4},
                ],
            },
        },
    }
    grid_width = 8
    grid_height = 16
    stick_figure_val = _bps_to_stick_figure(tree)
    default_traversal_plan = utils_tree.compute_constraints_along_traversal(
        stick_figure_val,
        config=config_lib.PackingConfig(
            traversal_mode=types.TraversalMode.RIVER_PRIORITY
        ),
    )
    base_square_dims = {
        step['stick'].name: (
            step['stick'].length * 2,
            step['stick'].length * 2,
        )
        for step in default_traversal_plan
    }

    with self.assertRaisesRegex(
        ValueError,
        'Grid width and height must be the same for local tiling.',
    ):
      tiling_solver.find_constrained_tiling(
          default_traversal_plan,
          base_square_dims,
          grid_size=grid_width,
          debug=debug_types.DebugConfig(),
          grid_height=grid_height,
          config=config_lib.PackingConfig(
              local_tiling_config=config_lib.LocalTilingConfig()
          ),
      )

  def test_find_constrained_tiling_with_mask(self):
    tree = {
        'version': 'None',
        'design': {
            'title': 'None',
            'mode': 'tree',
            'description': '',
            'layout': {
                'sheet': {'type': 'rect', 'height': 16, 'width': 16},
                'flaps': [
                    {'id': 1, 'x': 8, 'y': 10, 'width': 0, 'height': 0},
                    {'id': 2, 'x': 8, 'y': 6, 'width': 0, 'height': 0},
                ],
                'stretches': [],
            },
            'tree': {
                'sheet': {'type': 'rect', 'height': 20, 'width': 20},
                'nodes': [
                    {'id': 0, 'name': '', 'x': 10, 'y': 10},
                    {'id': 1, 'name': '', 'x': 10, 'y': 13},
                    {'id': 2, 'name': '', 'x': 10, 'y': 7},
                ],
                'edges': [
                    {'n1': 0, 'n2': 1, 'length': 4},
                    {'n1': 0, 'n2': 2, 'length': 4},
                ],
            },
        },
    }
    grid_size = 18
    stick_figure_val = _bps_to_stick_figure(tree)
    default_traversal_plan = utils_tree.compute_constraints_along_traversal(
        stick_figure_val,
        config=config_lib.PackingConfig(
            traversal_mode=types.TraversalMode.RIVER_PRIORITY
        ),
    )
    base_square_dims = {
        step['stick'].name: (
            step['stick'].length * 2,
            step['stick'].length * 2,
        )
        for step in default_traversal_plan
    }
    mask = np.zeros((grid_size, grid_size), dtype=bool)
    mask[:, 8:] = True
    mask[16:18, 0:8] = True
    _, details = tiling_solver.find_constrained_tiling(
        default_traversal_plan,
        base_square_dims,
        grid_size=grid_size,
        debug=debug_types.DebugConfig(),
        grid_height=grid_size,
        occupancy_mask=mask,
    )
    self.assertTrue(details['perfect_tiling_found'])
    self.assertEqual(details['unused_area'], 0)


class CreateTraversalPlanForFlapsTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.s1 = stick_lib.Stick(
        name='s1', start='j1', end='j2', length=1, azimuth_angle=0
    )
    self.s2 = stick_lib.Stick(
        name='s2', start='j2', end='j3', length=2, azimuth_angle=0
    )
    self.s3 = stick_lib.Stick(
        name='s3', start='j3', end='j4', length=3, azimuth_angle=0
    )
    self.traversal_plan = [
        {'stick': self.s1, 'constraints': {}},
        {'stick': self.s2, 'constraints': {}},
        {'stick': self.s3, 'constraints': {}},
    ]

  def test_filter_flaps_and_sort_by_length(self):
    flaps_to_pack = [self.s1, self.s2]
    config = config_lib.PackingConfig(enforce_proximity_constraints=False)
    flaps_traversal_plan = tiling_solver._create_traversal_plan_for_flaps(
        self.traversal_plan,  # pyrefly: ignore[bad-argument-type]
        flaps_to_pack,
        config=config,
    )
    self.assertLen(flaps_traversal_plan, 2)
    self.assertEqual(flaps_traversal_plan[0]['stick'].name, 's2')
    self.assertEqual(flaps_traversal_plan[1]['stick'].name, 's1')

  def test_filter_flaps_and_add_proximity_constraints(self):
    flaps_to_pack = [self.s1, self.s2]
    config = config_lib.PackingConfig(enforce_proximity_constraints=True)
    flaps_traversal_plan = tiling_solver._create_traversal_plan_for_flaps(
        self.traversal_plan,  # pyrefly: ignore[bad-argument-type]
        flaps_to_pack,
        config=config,
    )
    self.assertLen(flaps_traversal_plan, 2)
    self.assertEqual(flaps_traversal_plan[0]['stick'].name, 's1')
    self.assertEqual(flaps_traversal_plan[1]['stick'].name, 's2')
    self.assertIn('s1', flaps_traversal_plan[1]['constraints'])
    self.assertEqual(
        flaps_traversal_plan[1]['constraints']['s1'],
        {'type': types.ConstraintType.EQUAL, 'value': 0},
    )


if __name__ == '__main__':
  absltest.main()
