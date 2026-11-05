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

"""Tests for packing benchmark harness and invariant validation."""

import copy

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline import bus
from bp_pipeline import pipeline
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import crease_pattern as cp_lib
from bp_pipeline.packing import benchmark
from bp_pipeline.packing import packing_output as packing_output_lib
from bp_pipeline.solving import hinges as hinge_utils
from bp_pipeline.solving import solvability
from bp_pipeline.stick_figures.examples import example_trees


class PackingBenchmarkTest(parameterized.TestCase):

  def test_load_dataset_example_trees(self):
    all_trees = benchmark.load_dataset('example_trees')
    self.assertLen(all_trees, 47)
    first_tree = all_trees[0]
    self.assertIsNotNone(first_tree.name)

    sliced_trees = benchmark.load_dataset('example_trees', max_count=5)
    self.assertLen(sliced_trees, 5)

  @parameterized.parameters('cat', 'human', 'spider')
  def test_benchmark_single_tree_default_packer(self, tree_name: str):
    tree = example_trees.get_example_by_name(tree_name)
    record = benchmark.benchmark_single_tree(
        tree,
        packer='default',
        timeout_s=30.0,
        solve_max_steps=1000,
    )
    self.assertEqual(record.tree_name, tree.name)
    self.assertEqual(record.packer, 'default')
    self.assertEqual(record.pack_status, 'success')
    self.assertGreater(record.pack_time_s, 0.0)
    self.assertIsNotNone(record.grid_size)
    self.assertGreater(record.grid_size, 0)
    self.assertEqual(record.unused_area, 0)
    self.assertTrue(record.validation_passed)
    self.assertIsNone(record.validation_error)
    self.assertTrue(record.solvability_passed)
    self.assertTrue(record.step0_solvable)
    self.assertEqual(record.solve_status, 'solved')
    self.assertGreater(record.solve_time_s, 0.0)
    self.assertGreaterEqual(record.solve_steps, 0)
    self.assertTrue(record.globally_flat_foldable)
    self.assertIsNotNone(record.stick_signature)
    self.assertNotEmpty(record.stick_signature)

  def test_compute_stick_signature(self):
    cat_tree = example_trees.CAT_SIMPLE
    sig1 = benchmark.compute_stick_signature(cat_tree)
    self.assertIsInstance(sig1, str)
    self.assertIn('head', sig1)

    spider_tree = example_trees.SPIDER_SIMPLE
    sig2 = benchmark.compute_stick_signature(spider_tree)
    self.assertNotEqual(sig1, sig2)

  def test_run_benchmark_suite_and_summarize(self):
    test_trees = [
        example_trees.CAT_SIMPLE,
        example_trees.HUMAN_SIMPLE,
    ]
    summaries = benchmark.run_benchmark_suite(
        test_trees,
        packers=['default'],
        timeout_s=30.0,
        solve_max_steps=1000,
    )
    self.assertIn('default', summaries)
    summary = summaries['default']
    self.assertEqual(summary.total_trees, 2)
    self.assertEqual(summary.records[0].tree_index, 0)
    self.assertEqual(summary.records[1].tree_index, 1)
    self.assertIsNotNone(summary.records[0].stick_signature)
    self.assertIsNotNone(summary.records[1].stick_signature)
    self.assertEqual(summary.pack_success_count, 2)
    self.assertEqual(summary.pack_yield, 1.0)
    self.assertEqual(summary.validation_pass_count, 2)
    self.assertEqual(summary.validation_yield, 1.0)
    self.assertEqual(summary.solvability_pass_count, 2)
    self.assertEqual(summary.solvability_yield, 1.0)
    self.assertEqual(summary.step0_pass_count, 2)
    self.assertEqual(summary.step0_yield, 1.0)
    self.assertEqual(summary.solve_success_count, 2)
    self.assertEqual(summary.solve_yield, 1.0)
    self.assertEqual(summary.flat_foldable_count, 2)
    self.assertGreater(summary.mean_pack_time_s, 0.0)
    self.assertGreater(summary.mean_solve_time_s, 0.0)
    self.assertGreater(summary.mean_grid_size, 0.0)

    table_md = benchmark.format_benchmark_table(summaries)
    self.assertIn('default', table_md)
    self.assertIn('Pack Yield', table_md)
    self.assertIn('100.0%', table_md)

    river_table_md = benchmark.format_river_breakdown_table(summary)
    self.assertIn('River Geometry', river_table_md)

  def test_zero_unused_area_hard_requirement_confirmation(self):
    """Confirms that non-tiled crease patterns fail validation and solvability."""
    tree = example_trees.HUMAN_SIMPLE
    pack_res = pipeline.pack_crease_pattern(
        tree,
        config=pipeline.PackingTaskConfig(
            max_cps_per_grid_size=1,
            max_number_of_cps=1,
        ),
    )
    self.assertNotEmpty(pack_res.packing_outputs)
    valid_output = pack_res.packing_outputs[0]

    # 1. Valid packing passes validate() and check_solvability()
    valid_output.validate()
    solv_res_valid = solvability.check_solvability(valid_output.packing_cp)
    self.assertTrue(solv_res_valid.is_solvable)

    step0_valid, _ = benchmark.check_step0_solvability(valid_output, tree)
    self.assertTrue(step0_valid)

    # 2. Deliberately non-tiled metadata: PackingOutput.validate() fails
    non_tiled_details = copy.deepcopy(valid_output.details)
    non_tiled_details['unused_area'] = 4
    non_tiled_details['perfect_tiling_found'] = False
    invalid_meta_output = valid_output.model_copy(
        update={'details': non_tiled_details}
    )
    with self.assertRaises(packing_output_lib.PackingValidationError):
      invalid_meta_output.validate()

    # 3. Deliberately non-tiled geometric crease pattern:
    # Remove one internal diagonal ridge to simulate an uncovered grid cell
    # that leaves an interior vertex with odd degree (Kawasaki parity
    # violation).
    orig_creases = list(valid_output.packing_cp.creases)
    internal_ridges = [
        c
        for c in orig_creases
        if c.fold in (crease.Fold.MOUNTAIN, crease.Fold.VALLEY)
        and not (c.is_horizontal or c.is_vertical)
    ]
    self.assertNotEmpty(internal_ridges)
    corrupted_creases = [c for c in orig_creases if c != internal_ridges[0]]
    corrupted_cp = cp_lib.CreasePattern(
        corrupted_creases, grid_size=valid_output.packing_cp.grid_size
    )

    # Construct PackedCreasePattern with empty hinges so solvability check
    # evaluates Kawasaki parity and Maekawa bounds on fixed vertices without
    # candidate hinges.
    corrupted_packed = bus.PackedCreasePattern(
        design=None,
        packed_tree=None,
        grid_size=valid_output.packing_cp.grid_size,
        creases=corrupted_cp,
        flaps={},
        rivers={},
        hinges=(),
        config=None,  # pyrefly: ignore[bad-argument-type]
        diagnostics=bus.PackingDiagnostics(
            grid_size=valid_output.packing_cp.grid_size
        ),
    )

    # Solvability check detects Kawasaki parity or Maekawa violation
    solv_res_corrupted = solvability.check_solvability(corrupted_packed)
    self.assertFalse(solv_res_corrupted.is_solvable)
    self.assertIsNotNone(solv_res_corrupted.reason)
    self.assertIn('violation', solv_res_corrupted.reason.lower())

    # Step-0 solver check detects unsolveable vertex
    solver_cfg = hinge_utils.SolverConfig(
        grid_size=valid_output.packing_cp.grid_size,
        hinges_from_stick_figure=True,
    )
    solver = solver_cfg.make_from_cp(corrupted_cp)
    self.assertTrue(
        solver.init_state._has_unsolveable_vertex()  # pylint: disable=protected-access
    )

  def test_pipeline_configs_match_solve_cascade(self):
    """Verifies default configs match internal pipeline and with_recovery equals solve_cascade."""
    base_task = pipeline.SolvingTaskConfig.default()
    self.assertLen(list(base_task.config_iter()), 6)
    self.assertEmpty(list(base_task.fallback_config_iter()))

    recovery_task = pipeline.SolvingTaskConfig.with_recovery()
    recovery_solver = recovery_task.to_solver_config()
    recovery_configs = [
        c.to_solver_config() for c in recovery_task.config_iter()
    ] + [c.to_solver_config() for c in recovery_task.fallback_config_iter()]
    expected_configs = list(solvability.solve_cascade(recovery_solver))
    self.assertEqual(recovery_configs, expected_configs)

  def test_is_bankable_invalid_design_type_raises(self):
    """Verifies is_bankable raises TypeError when non-DesignTree is passed."""
    tree = example_trees.HUMAN_SIMPLE
    pack_res = pipeline.pack_crease_pattern(
        tree,
        config=pipeline.PackingTaskConfig(
            max_cps_per_grid_size=1,
            max_number_of_cps=1,
        ),
    )
    valid_output = pack_res.packing_outputs[0]

    with self.assertRaises(TypeError):
      solvability.is_bankable(valid_output, design='invalid_string')  # pyrefly: ignore[bad-argument-type]
    with self.assertRaises(TypeError):
      solvability.is_bankable(valid_output, design=tree)  # pyrefly: ignore[bad-argument-type]

    design = bus.DesignTree.from_stick_figure(tree)
    res = solvability.is_bankable(valid_output, design=design)
    self.assertTrue(res.ok)


if __name__ == '__main__':
  absltest.main()
