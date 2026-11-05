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
import math
import typing
from typing import Any
from unittest import mock

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline import utils_tree
from bp_pipeline.crease_pattern import crease as crease_lib
from bp_pipeline.crease_pattern import point
from bp_pipeline.packing import config as config_lib
from bp_pipeline.packing import scoring
from bp_pipeline.packing import tiling_solver_local
from bp_pipeline.packing import types
from bp_pipeline.packing import utils_solver
from bp_pipeline.packing import utils_tracker
from bp_pipeline.packing.debug import debug_types
from bp_pipeline.solving import hinges
from bp_pipeline.stick_figures import stick as stick_lib
from bp_pipeline.stick_figures import stick_figure
from bp_pipeline.stick_figures.examples import example_trees
import cp_test_fixtures as examples


def _bps_to_stick_figure(
    bps: dict[str, Any],
) -> stick_figure.StickFigure:
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


class FindTilingAndGenerateCreasePatternTest(parameterized.TestCase):

  def test_c2_greyhound(self):
    stickfigure = example_trees.get_example_by_name('C-2 Greyhound')
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        stickfigure,
        grid_size=9,
        is_symmetric=False,
        config=config_lib.PackingConfig(enforce_proximity_constraints=False),
    )
    self.assertNotEmpty(packing_outputs)
    self.assertTrue(packing_outputs[0].success)

  def test_c2_greyhound_hugging(self):
    stickfigure = example_trees.get_example_by_name('C-2 Greyhound')
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        stickfigure,
        grid_size=10,
        is_symmetric=False,
        config=config_lib.PackingConfig(
            traversal_mode=types.TraversalMode.RIVER_PRIORITY,
            enforce_proximity_constraints=True,
            start_with_hugging_river=True,
        ),
    )
    self.assertNotEmpty(packing_outputs)
    packing = packing_outputs[0]
    self.assertTrue(packing.success)

    shared_hinges_flaps = []
    for hinge in packing.hinges:  # pyrefly: ignore[not-iterable]
      if len(hinge.flap_names) == 2:
        shared_hinges_flaps.append(tuple(sorted(hinge.flap_names)))

    self.assertIn(
        tuple(sorted(('engine_nacelle', 'main_wing'))), shared_hinges_flaps
    )
    self.assertIn(
        tuple(sorted(('engine_nacelle', 'fuselage_front'))),
        shared_hinges_flaps,
    )

  def test_scorpion(self):
    stickfigure = example_trees.get_example_by_name('scorpion')
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        stickfigure,
        grid_size=32,
        is_symmetric=True,
        config=config_lib.PackingConfig(
            enforce_proximity_constraints=False,
            traversal_mode=types.TraversalMode.RIVER_PRIORITY,
            start_with_hugging_river=True,
        ),
        scoring_config=scoring.ScoringConfig(
            pruning_fn=scoring.canonical_flap_order_norm_score
        ),
    )
    self.assertNotEmpty(packing_outputs)
    self.assertTrue(packing_outputs[0].success)

  @mock.patch.object(utils_tree, 'compute_constraints_along_traversal')
  def test_sets_debug_stick_figure(self, mock_compute_constraints):
    mock_compute_constraints.side_effect = ValueError('dummy')
    stickfigure = copy.deepcopy(example_trees.HUMAN_SIMPLE)
    debug_config = debug_types.DebugConfig()
    utils_solver.find_tiling_and_generate_crease_pattern(
        stickfigure,
        grid_size=12,
        is_symmetric=False,
        debug=debug_config,
    )
    self.assertIsNotNone(debug_config.stick_figure)
    assert debug_config.stick_figure is not None
    self.assertEqual(debug_config.stick_figure.name, stickfigure.name)

  def test_bps_example_1(self):
    tree = typing.cast(
        examples.BoxPleatingTreeData,
        copy.deepcopy(example_trees.BPS_SIMPLE_STAR),
    )
    grid_size = 12
    stick_figure_val = _bps_to_stick_figure(tree)
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        stick_figure_val, grid_size, is_symmetric=False
    )
    self.assertNotEmpty(packing_outputs)
    self.assertTrue(packing_outputs[0].success)

  def test_bps_example_symmetric(self):
    tree_sym = typing.cast(
        examples.BoxPleatingTreeData,
        copy.deepcopy(example_trees.BPS_SYMMETRIC_STAR),
    )

    grid_size = 8
    stick_figure_val = _bps_to_stick_figure(tree_sym)
    symmetry_axes = {'0_1': True, '0_2': False, '0_3': True, '0_4': False}
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        stick_figure_val,
        grid_size,
        is_symmetric=True,
        symmetry_axes=symmetry_axes,
    )
    self.assertNotEmpty(packing_outputs)
    self.assertTrue(packing_outputs[0].success)

    packing_outputs_2 = utils_solver.find_tiling_and_generate_crease_pattern(
        stick_figure_val,
        grid_size,
        is_symmetric=True,
        symmetry_axes=symmetry_axes,
        allow_paired_axis_placement=True,
        config=config_lib.PackingConfig(enforce_proximity_constraints=False),
    )
    self.assertNotEmpty(packing_outputs_2)
    self.assertTrue(packing_outputs_2[0].success)

  def test_with_rivers_human_simple_grid_11_asymmetric(self):
    tree = copy.deepcopy(example_trees.HUMAN_SIMPLE)
    grid_size = 11
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        tree, grid_size, is_symmetric=False
    )
    self.assertNotEmpty(packing_outputs)
    packing = packing_outputs[0]
    self.assertTrue(packing.success)
    self.assertIsNotNone(packing.packing_cp)
    self.assertIsNotNone(packing.flap_rectangles)
    rect_names = [r.name for r in packing.flap_rectangles]
    self.assertIn('head', rect_names)
    self.assertIn('left_arm', rect_names)
    self.assertIn('right_arm', rect_names)
    self.assertIn('left_leg', rect_names)
    self.assertIn('right_leg', rect_names)

  def test_with_rivers_human_simple_grid_11_asymmetric_hugging(self):
    tree = copy.deepcopy(example_trees.HUMAN_SIMPLE)
    grid_size = 11
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        tree,
        grid_size,
        is_symmetric=False,
        config=config_lib.PackingConfig(start_with_hugging_river=True),
    )
    self.assertNotEmpty(packing_outputs)
    packing = packing_outputs[0]
    self.assertTrue(packing.success)
    self.assertIsNotNone(packing.packing_cp)
    self.assertIsNotNone(packing.flap_rectangles)
    rect_names = [r.name for r in packing.flap_rectangles]
    self.assertIn('head', rect_names)
    self.assertIn('left_arm', rect_names)
    self.assertIn('right_arm', rect_names)
    self.assertIn('left_leg', rect_names)
    self.assertIn('right_leg', rect_names)

  def test_with_rivers_human_simple_grid_12_symmetric(self):
    tree = copy.deepcopy(example_trees.HUMAN_SIMPLE)
    grid_size = 12
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        tree, grid_size, is_symmetric=True
    )
    self.assertNotEmpty(packing_outputs)
    packing = packing_outputs[0]
    self.assertTrue(packing.success)
    self.assertIsNotNone(packing.packing_cp)
    self.assertIsNotNone(packing.flap_rectangles)
    rect_names = [r.name for r in packing.flap_rectangles]
    self.assertIn('head', rect_names)
    self.assertIn('left_arm', rect_names)
    self.assertIn('right_arm', rect_names)
    self.assertIn('left_leg', rect_names)
    self.assertIn('right_leg', rect_names)

  def test_ridges_collinear_with_border(self):
    example = examples.load_cp_fixture('mini_human')
    stickfigure = _bps_to_stick_figure(example.tree_data)  # pyrefly: ignore[bad-argument-type]
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        stickfigure
    )
    self.assertNotEmpty(packing_outputs)
    packing = packing_outputs[0]
    self.assertTrue(packing.success)
    self.assertIsNotNone(packing.packing_cp)
    crease_pattern = packing.packing_cp
    self.assertIsNotNone(packing.flap_rectangles)

    if crease_pattern:
      for crease in crease_pattern.creases:
        if crease.fold == crease_lib.Fold.MOUNTAIN:
          self.assertFalse(
              crease.is_overlapping_border,
              f'Ridge crease {crease} is collinear with the border.',
          )

  def test_find_tiling_with_debug_config(self):
    tree = copy.deepcopy(example_trees.HUMAN_SIMPLE)
    grid_size = 12
    debug_config = debug_types.DebugConfig(live_plot=False)
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        tree, grid_size, is_symmetric=True, debug=debug_config
    )
    self.assertNotEmpty(packing_outputs)
    packing = packing_outputs[0]
    self.assertTrue(packing.success)
    self.assertIn('debug_history', packing.details)
    self.assertNotEmpty(packing.details['debug_history'])

  def test_three_consecutive_rivers(self):
    example = examples.load_cp_fixture('three_consecutive_rivers')
    stickfigure = _bps_to_stick_figure(example.tree_data)  # pyrefly: ignore[bad-argument-type]
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        stickfigure,
        grid_size=10,
        is_symmetric=False,
    )
    self.assertNotEmpty(packing_outputs)
    self.assertTrue(packing_outputs[0].success)

  def test_human_fold_symmetric_generates_circle_centers(self):
    tree = _bps_to_stick_figure(
        examples.load_cp_fixture('human').tree_data  # pyrefly: ignore[bad-argument-type]
    )
    grid_size = 16
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        tree,
        grid_size,
        is_symmetric=True,
        config=config_lib.PackingConfig(enforce_proximity_constraints=False),
    )
    self.assertNotEmpty(packing_outputs)
    packing = packing_outputs[0]
    self.assertTrue(packing.success)
    self.assertIsNotNone(packing.packing_cp)
    self.assertIsNotNone(packing.flap_rectangles)
    self.assertNotEmpty(packing.flap_rectangles)

    expected_centers = {
        '1_5': [point.Point(x=16.0, y=0.0, require_on_paper=False)],
        '1_4': [
            point.Point(x=8.0, y=-2.0, require_on_paper=False),
            point.Point(x=8.0, y=4.0, require_on_paper=False),
        ],
        '0_2': [point.Point(x=0.0, y=16.0, require_on_paper=False)],
        '1_6': [point.Point(x=0.0, y=0.0, require_on_paper=False)],
        '0_3': [point.Point(x=16.0, y=16.0, require_on_paper=False)],
    }
    expected_radii = {
        '1_5': 6 * math.sqrt(2),
        '1_4': 2 * math.sqrt(2),
        '0_2': 8 * math.sqrt(2),
        '1_6': 6 * math.sqrt(2),
        '0_3': 8 * math.sqrt(2),
    }
    for rect in packing.flap_rectangles:
      self.assertIn(rect.name, expected_centers)
      self.assertLen(rect.circle_centers, len(expected_centers[rect.name]))
      for center in rect.circle_centers:
        self.assertTrue(
            any(center.isclose(c) for c in expected_centers[rect.name])
        )
      tracker = packing.tracker
      self.assertIsNotNone(tracker)
      self.assertAlmostEqual(rect.radius, expected_radii[rect.name])

  def test_human_fold_symmetric_generates_circle_centers_enforced(self):
    tree = _bps_to_stick_figure(
        examples.load_cp_fixture('human').tree_data  # pyrefly: ignore[bad-argument-type]
    )
    grid_size = 16
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        tree,
        grid_size,
        is_symmetric=True,
        config=config_lib.PackingConfig(enforce_proximity_constraints=True),
    )
    self.assertNotEmpty(packing_outputs)
    packing = packing_outputs[0]
    self.assertTrue(packing.success)
    self.assertIsNotNone(packing.packing_cp)
    self.assertIsNotNone(packing.flap_rectangles)
    self.assertNotEmpty(packing.flap_rectangles)

    expected_centers = {
        '1_5': [point.Point(x=16.0, y=0.0, require_on_paper=False)],
        '1_4': [
            point.Point(x=8.0, y=0.0, require_on_paper=False),
            point.Point(x=8.0, y=4.0, require_on_paper=False),
        ],
        '0_2': [point.Point(x=0.0, y=16.0, require_on_paper=False)],
        '1_6': [point.Point(x=0.0, y=0.0, require_on_paper=False)],
        '0_3': [point.Point(x=16.0, y=16.0, require_on_paper=False)],
    }
    expected_radii = {
        '1_5': 6 * math.sqrt(2),
        '1_4': 2 * math.sqrt(2),
        '0_2': 8 * math.sqrt(2),
        '1_6': 6 * math.sqrt(2),
        '0_3': 8 * math.sqrt(2),
    }
    for rect in packing.flap_rectangles:
      self.assertIn(rect.name, expected_centers)
      self.assertLen(rect.circle_centers, len(expected_centers[rect.name]))
      for center in rect.circle_centers:
        self.assertTrue(
            any(center.isclose(c) for c in expected_centers[rect.name])
        )
      tracker = packing.tracker
      self.assertIsNotNone(tracker)
      self.assertAlmostEqual(rect.radius, expected_radii[rect.name])

  def test_flaps_between_rivers(self):
    example = examples.load_cp_fixture('flaps_between_rivers')
    stickfigure = _bps_to_stick_figure(example.tree_data)  # pyrefly: ignore[bad-argument-type]
    packing = utils_solver.find_tiling_and_generate_crease_pattern(
        stickfigure,
        grid_size=15,
        is_symmetric=False,
        config=config_lib.PackingConfig(
            traversal_mode=types.TraversalMode.RIVER_PRIORITY
        ),
    )
    self.assertNotEmpty(packing)
    self.assertTrue(packing[0].success)

  def test_valkyrie_xb70(self):
    stickfigure = example_trees.get_example_by_name('Valkyrie XB-70')
    grid_size = 12
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        stickfigure,
        grid_size=grid_size,
        is_symmetric=True,
        config=config_lib.PackingConfig(
            traversal_mode=types.TraversalMode.PROXIMITY
        ),
    )
    self.assertNotEmpty(packing_outputs)
    packing = packing_outputs[0]
    self.assertTrue(packing.success)
    self.assertIsNotNone(packing.packing_cp)

    solutions = hinges.cp_from_packing(
        packing.packing_cp,
        grid_size=grid_size,
        check_global_flat_foldability=False,
        max_number_of_cps=1,
        packing_information=packing,
    )
    self.assertNotEmpty(solutions)
    ff_cp = solutions[0].crease_pattern
    self.assertTrue(ff_cp.is_locally_foldable())

  def test_proximity_constraints_logging(self):
    tree = _bps_to_stick_figure(
        examples.load_cp_fixture('human').tree_data  # pyrefly: ignore[bad-argument-type]
    )
    grid_size = 16
    config = config_lib.PackingConfig(enforce_proximity_constraints=True)
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        tree,
        grid_size,
        is_symmetric=True,
        config=config,
    )
    self.assertNotEmpty(packing_outputs)
    packing = packing_outputs[0]
    self.assertTrue(packing.success)

    details = packing.details
    self.assertIn('constraint_satisfaction', details)
    self.assertIn('satisfied_constraints', details)
    self.assertIn('unsatisfied_constraints', details)

    self.assertNotEmpty(details['satisfied_constraints'])
    num_satisfied = len(details['satisfied_constraints'])
    num_unsatisfied = len(details['unsatisfied_constraints'])
    num_total = num_satisfied + num_unsatisfied
    self.assertEqual(
        details['constraint_satisfaction'],
        f'{num_satisfied} out of {num_total} satisfied',
    )

  def test_underwater_sensor_symmetric_grid_12(self):
    stickfigure = example_trees.UNDERWATER_SENSOR
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        stickfigure,
        grid_size=12,
        is_symmetric=True,
        debug=debug_types.DebugConfig(),
        config=config_lib.PackingConfig(
            traversal_mode=types.TraversalMode.RIVER_PRIORITY
        ),
    )
    self.assertNotEmpty(packing_outputs)
    self.assertTrue(packing_outputs[0].success)

  def test_symmetric_top_hugging_river(self):
    stickfigure = example_trees.LIZARD_ALEX
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        stickfigure,
        grid_size=18,
        is_symmetric=True,
    )
    self.assertNotEmpty(packing_outputs)
    self.assertTrue(packing_outputs[0].success)

  def test_exhaust_solutions_human(self):
    tree = _bps_to_stick_figure(
        examples.load_cp_fixture('human').tree_data  # pyrefly: ignore[bad-argument-type]
    )
    grid_size = 16
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        tree,
        grid_size,
        is_symmetric=True,
        max_solutions=10,
        config=config_lib.PackingConfig(exhaust_solutions=True),
    )
    self.assertNotEmpty(packing_outputs)
    self.assertGreater(len(packing_outputs), 1)
    for packing in packing_outputs:
      self.assertTrue(packing.success)

  def test_with_rivers_human_simple_remove_central_crease(self):
    tree = copy.deepcopy(example_trees.HUMAN_SIMPLE)
    grid_size = 18
    config = config_lib.PackingConfig(remove_central_crease=True)
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        tree, grid_size, is_symmetric=True, config=config
    )
    self.assertNotEmpty(packing_outputs)
    packing = packing_outputs[0]
    self.assertTrue(packing.success)
    self.assertIsNotNone(packing.flap_rectangles)

    half = grid_size // 2
    on_axis_sticks = {'torso', 'head'}
    self.assertIsNotNone(packing.tracker)
    tracker = packing.tracker
    assert tracker is not None
    for name, placement in tracker.packed_polygons.items():
      if name in on_axis_sticks:
        continue
      if name.startswith('axis_filler'):
        continue
      if placement.center.x >= 0.5:
        continue
      x, _ = placement.offset
      w, _ = placement.size
      self.assertLessEqual(
          x + w,
          half - 1,
          f'Non-axis flap {name} touches axis: offset={placement.offset},'
          f' size={placement.size}',
      )

    solutions = hinges.cp_from_packing(
        packing.packing_cp,
        grid_size=grid_size,
        check_global_flat_foldability=False,
        max_number_of_cps=1,
        packing_information=packing,
        remove_central_crease=True,
    )
    self.assertNotEmpty(solutions)
    ff_cp = solutions[0].crease_pattern
    self.assertTrue(ff_cp.is_locally_foldable())

    axis_x = 0.5
    for crease in ff_cp.creases:
      if crease.is_vertical and abs(crease.p1.x - axis_x) < 1e-9:
        self.fail(
            f'Final CP has a vertical crease at the symmetry axis: {crease}'
        )

  def test_unmerged_flap_cannot_tile_by_expanding_long_side(self):
    grid_size = 20
    arm_w, arm_h = 10, 14
    river_w, river_h = 10, 20

    tracker = utils_tracker.CreasePatternTracker(grid_size)
    arm_pl = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0),
        size=(arm_w, arm_h),
        grid_size=grid_size,
        require_on_paper=False,
    )
    tracker.add_polygon('arm', arm_pl)
    river_pl = types.PolygonPlacement.from_grid_coords(
        offset=(arm_w, 0),
        size=(river_w, river_h),
        grid_size=grid_size,
        require_on_paper=False,
    )
    tracker.add_polygon('river', river_pl)

    result = tiling_solver_local.find_perfect_tiling_from_local_expansions(
        tracker,
        is_symmetric=False,
        config=config_lib.LocalTilingConfig(),
        locked_long_side_flaps={'arm'},
    )
    if result is not None:
      arm_placement = result.packed_polygons['arm']
      _, actual_h = arm_placement.size
      self.assertEqual(
          actual_h,
          arm_h,
          f'Long side must stay locked at {arm_h}, got {actual_h}',
      )

  def test_solution_callback_collects_results(self):
    tree = example_trees.HUMAN_SIMPLE
    collected = []

    def callback(output):
      collected.append(output)
      return output

    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        tree,
        grid_size=16,
        is_symmetric=True,
        max_solutions=3,
        config=config_lib.PackingConfig(exhaust_solutions=True),
        solution_callback=callback,
    )
    self.assertNotEmpty(packing_outputs)
    self.assertEqual(collected, packing_outputs)

  def test_solution_callback_rejects_all(self):
    tree = example_trees.HUMAN_SIMPLE
    packing_outputs = utils_solver.find_tiling_and_generate_crease_pattern(
        tree,
        grid_size=16,
        is_symmetric=True,
        max_solutions=1,
        config=config_lib.PackingConfig(exhaust_solutions=True),
        solution_callback=lambda _: None,
    )
    self.assertEmpty(packing_outputs)


if __name__ == '__main__':
  absltest.main()
