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

"""Tests for Box Pleating hinges."""

import dataclasses
from unittest import mock

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import crease_pattern
from bp_pipeline.crease_pattern import point
from bp_pipeline.packing import packing_output
from bp_pipeline.packing import types
from bp_pipeline.solving import hinges as hinge_utils
from bp_pipeline.stick_figures import stick_figure as sf
import cp_test_fixtures as examples

_BORDERS = [
    crease.Crease(
        point.Point(x=0, y=0),
        point.Point(x=1, y=0),
        fold=crease.Fold.BORDER,
    ),
    crease.Crease(
        point.Point(x=0, y=1),
        point.Point(x=1, y=1),
        fold=crease.Fold.BORDER,
    ),
    crease.Crease(
        point.Point(x=0, y=0),
        point.Point(x=0, y=1),
        fold=crease.Fold.BORDER,
    ),
    crease.Crease(
        point.Point(x=1, y=0),
        point.Point(x=1, y=1),
        fold=crease.Fold.BORDER,
    ),
]

_SolverConfig = hinge_utils.SolverConfig(
    grid_size=8,
    check_local_flat_foldability=True,
    check_global_flat_foldability=False,
    tie_break_by_hinge_symmetry=False,
    remove_central_crease=False,
    max_steps=1000,
    max_number_of_cps=1,
    log_progress=False,
)


class HingeSolvingTest(parameterized.TestCase):

  @parameterized.parameters([
      dict(example=examples.SPIDER),
      dict(example=examples.SCORPION),
      dict(example=examples.THREEFLAPSETSTWORIVERS),
      dict(example=examples.RIVERONEFLAP),
      dict(example=examples.GENERATED1),
      # examples.GENERATED2, central hinges issue with pleats
      dict(example=examples.WATERBOMB),
      dict(example=examples.GENERATED3),
      dict(example=examples.GENERATED4),
      dict(example=examples.GENERATED5),
      dict(example=examples.GENERATED6),
      dict(example=examples.GENERATED7),
      dict(example=examples.X_TEST),
      dict(example=examples.CENTRALFLAP4HINGE),
      dict(example=examples.CENTRALFOLDONLYPLEATS),
      dict(example=examples.CENTRALRIDGENOVERTICES),
      dict(example=examples.HINGENOVERTICES),
      dict(example=examples.HUMAN),
      dict(example=examples.GEMINI),
      dict(example=examples.INTERLEAVEDRIDGE),
      dict(example=examples.BORDERPLEATNOVERTEX_TEST),
      dict(example=examples.BORDERRIDGE_TEST),
      dict(example=examples.FFCENTRALFLAP_TEST),
      dict(example=examples.FULLRIDGE),
      dict(example=examples.VERTICALFULLRIDGE),
      dict(example=examples.XSHAPEDEDGEFLAP),
  ])
  def test_hinges(
      self,
      example: examples.BoxPleatingCreasePatternExample,
      check_global_ff: bool = True,
  ):
    packing_cp = example.packing_cp
    solutions = hinge_utils.cp_from_packing(
        cp=packing_cp,
        grid_size=example.grid_size,
        check_global_flat_foldability=check_global_ff,
        use_python_flat_folder=True,
        tie_break_by_hinge_symmetry=False,
        disallow_trapping_edge_flaps=False,
    )
    ff_cps = [sol.crease_pattern for sol in solutions]
    ff_cps.sort(key=lambda x: len(x.creases))
    self.assertNotEmpty(ff_cps)
    for cp in ff_cps:
      self.assertTrue(cp.local_flat_foldability())

    # Check that time_taken is populated and is greater than 0.
    time_taken = [sol.time_taken for sol in solutions]
    self.assertLen(time_taken, len(ff_cps))
    for time_taken_value in time_taken:
      self.assertGreater(time_taken_value, 0.0)

  @parameterized.parameters([
      dict(example=examples.CENTRALFOLDONLYPLEATS),
      dict(example=examples.HUMAN),
      dict(example=examples.SCORPION),
      dict(example=examples.GEMINI),
      dict(example=examples.FULLRIDGE),
      dict(example=examples.CENTRALFOLD1),
      dict(example=examples.CENTRALFOLD2),
      dict(example=examples.CENTRALFOLD3, check_global_ff=False),
      dict(example=examples.CENTRALFOLD4),
      dict(example=examples.CENTRALFOLD5),
      dict(example=examples.CENTRALFOLD6),
      dict(example=examples.CENTRALFOLD7),
      dict(example=examples.CENTRALFOLD8),
      dict(example=examples.CENTRALFOLD9),
      dict(example=examples.CENTRALFOLD10),
  ])
  def test_remove_central_crease(
      self,
      example: examples.BoxPleatingCreasePatternExample,
      check_global_ff: bool = True,
  ):
    packing_cp = example.packing_cp
    solutions = hinge_utils.cp_from_packing(
        cp=packing_cp,
        grid_size=example.grid_size,
        check_global_flat_foldability=check_global_ff,
        use_python_flat_folder=True,
        tie_break_by_hinge_symmetry=True,
        remove_central_crease=True,
    )
    ff_cps = [sol.crease_pattern for sol in solutions]
    ff_cps.sort(key=lambda x: len(x.creases))
    self.assertNotEmpty(ff_cps)
    for cp in ff_cps:
      self.assertTrue(cp.local_flat_foldability())

  @parameterized.parameters([
      dict(example=examples.CENTRALFOLD11),
  ])
  def test_cannot_remove_central_crease(
      self,
      example: examples.BoxPleatingCreasePatternExample,
  ):
    packing_cp = example.packing_cp
    with self.assertRaisesRegex(
        hinge_utils.NoSolutionError, 'Cannot remove central crease.'
    ):
      hinge_utils.cp_from_packing(
          cp=packing_cp,
          grid_size=example.grid_size,
          check_global_flat_foldability=False,
          use_python_flat_folder=True,
          tie_break_by_hinge_symmetry=True,
          remove_central_crease=True,
      )

  @parameterized.parameters(1, 2, 3)
  def test_max_attempts_per_cp(self, n_solutions: int):
    example = examples.HUMAN
    packing_cp = example.packing_cp
    self.enterContext(
        mock.patch.object(
            hinge_utils.SolverConfig,
            'is_valid_crease_pattern',
            autospec=True,
            return_value=False,
        )
    )
    solver_config = hinge_utils.SolverConfig(
        grid_size=example.grid_size,
        check_global_flat_foldability=False,
        max_number_of_cps=n_solutions,
        max_attempts_per_cp=1,
        log_progress=True,
    )
    solver = solver_config.make_from_cp(packing_cp)
    with self.assertLogs(level='WARNING') as logs:
      with self.assertRaisesRegex(
          hinge_utils.NoSolutionError, 'No solutions found'
      ):
        solver.solve()
      self.assertIn(
          'Maximum number of validity attempts reached.', logs.output[0]
      )
    self.assertEqual(solver._n_solution_attempts, n_solutions)

  def test_solution_callback(self):
    example = examples.WATERBOMB
    packing_cp = example.packing_cp
    solution_list = []

    def custom_callback(solution: hinge_utils.SolverResult):
      solution_list.append(solution)
      return solution

    solver_config = hinge_utils.SolverConfig(
        grid_size=example.grid_size,
        check_global_flat_foldability=False,
        tie_break_by_hinge_symmetry=False,
        solution_callback=custom_callback,
    )
    solver = solver_config.make_from_cp(packing_cp)
    solutions = solver.solve()
    self.assertNotEmpty(solutions)
    self.assertLen(solution_list, len(solutions))
    self.assertEqual(solution_list, solutions)

  def test_unsolveable_vertices_no_unvisited_hinges(self):
    # Create a vertex with 2 mountains and 2 valley, not flat foldable
    pleats = [
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1, y=0),
            fold=crease.Fold.VALLEY,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1, y=1),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0, y=1),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0, y=0),
            fold=crease.Fold.VALLEY,
        ),
    ]
    state = hinge_utils.State.init_state(
        pleats=pleats,
        unassigned_pleats=[],
        hinges=[],
        borders=_BORDERS,
        solver_config=_SolverConfig,
        ridges=[],
        partition_order=None,
    )
    self.assertTrue(state.is_invalid(0))

  def test_unsolveable_vertices_solveable_with_hinge(self):
    # Create a vertex with 2 mountains and 1 valley, not flat foldable
    pleats = [
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1, y=0),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1, y=1),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0, y=0),
            fold=crease.Fold.VALLEY,
        ),
    ]
    # Add a hinge that intersects the vertex
    hinge = crease.Crease(
        point.Point(x=0.5, y=0.5),
        point.Point(x=0.5, y=1),
        fold=crease.Fold.HINGE,
    )
    state = hinge_utils.State.init_state(
        pleats=pleats,
        unassigned_pleats=[],
        hinges=[hinge],
        borders=_BORDERS,
        solver_config=_SolverConfig,
        ridges=[],
        partition_order=None,
    )
    self.assertFalse(state.is_invalid(0))

  def test_unsolveable_vertices_solveable_with_central_pleat(self):
    # Create a vertex with 2 mountains and 1 valley, not flat foldable
    pleats = [
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1, y=0),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1, y=1),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0, y=0),
            fold=crease.Fold.VALLEY,
        ),
    ]
    # Add a hinge with a central pleat that intersects the vertex
    hinge = crease.Crease(
        point.Point(x=0.1, y=0.1),
        point.Point(x=0.1, y=0.9),
        fold=crease.Fold.HINGE,
    )
    central_pleat = crease.Crease(
        point.Point(x=0.1, y=0.5),
        point.Point(x=0.5, y=0.5),
        fold=crease.Fold.MOUNTAIN,
    )
    state = hinge_utils.State.init_state(
        pleats=pleats,
        unassigned_pleats=[central_pleat],
        hinges=[hinge],
        ridges=[],
        borders=_BORDERS,
        solver_config=_SolverConfig,
        partition_order=None,
    )
    self.assertFalse(state.is_invalid(0))

  def test_unsolveable_vertices_already_solveable(self):
    # Create a vertex with 2 mountains and 2 valleys, not flat foldable
    pleats = [
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1, y=0),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1, y=1),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0, y=1),
            fold=crease.Fold.VALLEY,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0, y=0),
            fold=crease.Fold.VALLEY,
        ),
    ]
    state = hinge_utils.State.init_state(
        pleats=pleats,
        unassigned_pleats=[],
        hinges=[],
        borders=_BORDERS,
        solver_config=_SolverConfig,
        ridges=[],
        partition_order=None,
    )
    self.assertTrue(state.is_invalid(0))

  def test_get_hinge_options_border_hinge(self):
    hinges = [
        crease.Crease(
            point.Point(x=0, y=0.5),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=1, y=0.5),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.VALLEY,
        ),
    ]
    state = hinge_utils.State.init_state(
        pleats=[],
        unassigned_pleats=[],
        hinges=hinges,
        borders=_BORDERS,
        solver_config=_SolverConfig,
        ridges=[
            crease.Crease(
                point.Point(x=0, y=0),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.VALLEY,
            )
        ],
        partition_order=None,
    )
    interleave_options, fold_options = hinge_utils.get_hinge_options(
        hinges[0], state.hinge_dict, [], state.vertices
    )
    self.assertEqual(interleave_options, [True])
    self.assertEqual(fold_options, [crease.Fold.VALLEY])

  def test_get_hinge_options_central_hinge_no_pleats(self):
    hinge = crease.Crease(
        point.Point(x=0.1, y=0.5),
        point.Point(x=0.9, y=0.5),
        fold=crease.Fold.HINGE,
    )
    segments = [
        crease.Crease(
            point.Point(x=0.1, y=0.5),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.HINGE,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0.9, y=0.5),
            fold=crease.Fold.HINGE,
        ),
    ]
    hinge_info = hinge_utils.HingeMetaData(
        hinge=hinge, segments=segments, central_pleats=[]
    )
    hinge_dict = {hinge.hash_value: hinge_info}
    interleave_options, fold_options = hinge_utils.get_hinge_options(
        hinge, hinge_dict, [], {}
    )
    self.assertEqual(interleave_options, [True])
    self.assertEqual(fold_options, [crease.Fold.MOUNTAIN, crease.Fold.VALLEY])

  def test_get_hinge_options_central_hinge_with_unassigned_pleat(self):
    hinge = crease.Crease(
        point.Point(x=0.1, y=0.5),
        point.Point(x=0.9, y=0.5),
        fold=crease.Fold.HINGE,
    )
    unassigned_pleats = [
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0.5, y=0.9),
            fold=crease.Fold.MOUNTAIN,
        )
    ]
    ridges = [
        crease.Crease(
            point.Point(x=0, y=0),
            point.Point(x=1, y=1),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0, y=1),
            point.Point(x=1, y=0),
            fold=crease.Fold.VALLEY,
        ),
    ]
    solver_config = hinge_utils.SolverConfig(
        grid_size=10,
        check_local_flat_foldability=True,
        check_global_flat_foldability=False,
        tie_break_by_hinge_symmetry=False,
        remove_central_crease=False,
        max_steps=1000,
        max_number_of_cps=1,
        log_progress=False,
    )

    state = hinge_utils.State.init_state(
        pleats=[],
        unassigned_pleats=unassigned_pleats,
        hinges=[hinge],
        borders=_BORDERS,
        solver_config=solver_config,
        ridges=ridges,
        partition_order=None,
    )
    interleave_options, fold_options = hinge_utils.get_hinge_options(
        hinge, state.hinge_dict, state.unassigned_pleats, state.vertices
    )
    self.assertEqual(interleave_options, [False])
    self.assertEqual(fold_options, [crease.Fold.MOUNTAIN, crease.Fold.VALLEY])

  def test_get_hinge_options_central_hinge_with_assigned_pleat(self):
    hinges = [
        crease.Crease(
            point.Point(x=0.1, y=0.5),
            point.Point(x=0.9, y=0.5),
            fold=crease.Fold.HINGE,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0.5, y=0.1),
            fold=crease.Fold.HINGE,
        ),
    ]
    pleats = [
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0.5, y=0.9),
            fold=crease.Fold.MOUNTAIN,
        )
    ]
    unassigned_pleats = []
    state = hinge_utils.State.init_state(
        pleats=pleats,
        unassigned_pleats=unassigned_pleats,
        hinges=hinges,
        borders=_BORDERS,
        solver_config=_SolverConfig,
        ridges=[],
        partition_order=None,
    )
    interleave_options, fold_options = hinge_utils.get_hinge_options(
        hinges[0], state.hinge_dict, state.unassigned_pleats, state.vertices
    )
    self.assertEqual(interleave_options, [True, False])
    self.assertEqual(fold_options, [crease.Fold.MOUNTAIN, crease.Fold.VALLEY])

  def test_get_hinge_options_central_hinge_odd_segments(self):
    hinge = crease.Crease(
        point.Point(x=0.1, y=0.5),
        point.Point(x=0.9, y=0.5),
        fold=crease.Fold.HINGE,
    )
    # Create a hinge dict with an odd number of segments
    segments = [
        crease.Crease(
            point.Point(x=0.1, y=0.5),
            point.Point(x=0.3, y=0.5),
            fold=crease.Fold.HINGE,
        ),
        crease.Crease(
            point.Point(x=0.3, y=0.5),
            point.Point(x=0.6, y=0.5),
            fold=crease.Fold.HINGE,
        ),
        crease.Crease(
            point.Point(x=0.6, y=0.5),
            point.Point(x=0.9, y=0.5),
            fold=crease.Fold.HINGE,
        ),
    ]
    hinge_info = hinge_utils.HingeMetaData(
        hinge=hinge, segments=segments, central_pleats=[]
    )
    hinge_dict = {hinge.hash_value: hinge_info}
    interleave_options, fold_options = hinge_utils.get_hinge_options(
        hinge, hinge_dict, [], {}
    )
    self.assertEqual(interleave_options, [True])  # Cannot be symmetrical
    self.assertEqual(fold_options, [crease.Fold.MOUNTAIN, crease.Fold.VALLEY])

  def test_get_hinge_options_central_hinge_no_central_pleats(self):
    hinge = crease.Crease(
        point.Point(x=0.1, y=0.5),
        point.Point(x=0.9, y=0.5),
        fold=crease.Fold.HINGE,
    )
    # Hinge dict with no central pleats
    segments = [
        crease.Crease(
            point.Point(x=0.1, y=0.5),
            point.Point(x=0.4, y=0.5),
            fold=crease.Fold.HINGE,
        ),
        crease.Crease(
            point.Point(x=0.4, y=0.5),
            point.Point(x=0.9, y=0.5),
            fold=crease.Fold.HINGE,
        ),
    ]
    hinge_info = hinge_utils.HingeMetaData(
        hinge=hinge, segments=segments, central_pleats=[]
    )
    hinge_dict = {hinge.hash_value: hinge_info}
    interleave_options, fold_options = hinge_utils.get_hinge_options(
        hinge, hinge_dict, [], {}
    )
    self.assertEqual(interleave_options, [True])
    self.assertEqual(fold_options, [crease.Fold.MOUNTAIN, crease.Fold.VALLEY])


class SolverMetricsTest(parameterized.TestCase):

  def test_calc_metrics(self):
    example = examples.SPIDER
    packing_cp = example.packing_cp
    solver_config = hinge_utils.SolverConfig(
        grid_size=example.grid_size,
        log_progress=False,
    )
    solver = solver_config.make_from_cp(packing_cp)
    state = solver.init_state
    metrics = solver._calc_metrics(step=0, state=state)
    self.assertEqual(metrics.step, 0)
    self.assertLen(state.vertices, metrics.unsolved_vertices)
    self.assertEqual(metrics.states, 1)
    self.assertEqual(metrics.hinges, 0)
    self.assertLen(state.pleats, metrics.pleats)
    self.assertEqual(metrics.partitions, 0)
    self.assertEqual(metrics.solutions, 0)

  def test_handle_metrics_log_progress(self):
    solver_config = hinge_utils.SolverConfig(
        grid_size=8,
        log_progress=True,
    )
    metrics = hinge_utils.SolverMetrics(
        step=1,
        unsolved_vertices=2,
        states=3,
        hinges=4,
        pleats=5,
        partitions=6,
        solutions=7,
    )
    with self.assertLogs(level='INFO') as logs:
      solver_config.handle_metrics(metrics)
    self.assertIn(
        'step:1 Unsolved vertices:2 #States:3 #Hinges:4 #Pleats:5'
        ' #Partitions:6 #Solutions:7',
        logs.output[0],
    )

  def test_handle_metrics_custom_callback(self):
    metric_list = []

    def custom_callback(metrics: hinge_utils.SolverMetrics):
      metric_list.append(metrics)

    solver_config = hinge_utils.SolverConfig(
        grid_size=8,
        log_progress=False,
        custom_metric_callback=custom_callback,
    )
    metrics = hinge_utils.SolverMetrics(
        step=1,
        unsolved_vertices=2,
        states=3,
        hinges=4,
        pleats=5,
        partitions=6,
        solutions=7,
    )
    with self.assertNoLogs(level='INFO'):
      solver_config.handle_metrics(metrics)
    self.assertEqual(metric_list, [metrics])

  def test_handle_metrics_both_set(self):
    metric_list = []

    def custom_callback(metrics: hinge_utils.SolverMetrics):
      metric_list.append(metrics)

    solver_config = hinge_utils.SolverConfig(
        grid_size=8,
        log_progress=True,
        custom_metric_callback=custom_callback,
    )

    metrics = hinge_utils.SolverMetrics(
        step=1,
        unsolved_vertices=2,
        states=3,
        hinges=4,
        pleats=5,
        partitions=6,
        solutions=7,
    )

    with self.assertLogs(level='INFO') as logs:
      solver_config.handle_metrics(metrics)
      self.assertIn(
          'step:1 Unsolved vertices:2 #States:3 #Hinges:4 #Pleats:5'
          ' #Partitions:6 #Solutions:7',
          logs.output[0],
      )
    self.assertEqual(metric_list, [metrics])


class HingeMetaDataTest(parameterized.TestCase):

  def test_simple_property(self):
    hinge_on_border = crease.Crease(
        point.Point(x=0, y=0.5),
        point.Point(x=0.5, y=0.5),
        fold=crease.Fold.MOUNTAIN,
    )
    hinge_not_on_border = crease.Crease(
        point.Point(x=0.1, y=0.5),
        point.Point(x=0.5, y=0.5),
        fold=crease.Fold.MOUNTAIN,
    )
    central_pleat = crease.Crease(
        point.Point(x=0.2, y=0.5),
        point.Point(x=0.2, y=0.8),
        fold=crease.Fold.MOUNTAIN,
    )
    # Hinge on border, no central pleats -> simple=True
    hinge_metadata = hinge_utils.HingeMetaData(
        hinge=hinge_on_border, segments=[], central_pleats=[]
    )
    self.assertTrue(hinge_metadata.simple)
    # Hinge on border, with central pleats -> simple=False
    hinge_metadata = hinge_utils.HingeMetaData(
        hinge=hinge_on_border, segments=[], central_pleats=[central_pleat]
    )
    self.assertFalse(hinge_metadata.simple)
    # Hinge not on border, no central pleats -> simple=False
    hinge_metadata = hinge_utils.HingeMetaData(
        hinge=hinge_not_on_border, segments=[], central_pleats=[]
    )
    self.assertFalse(hinge_metadata.simple)

  def test_allow_symmetric_property(self):
    segments = [
        crease.Crease(
            point.Point(x=0.1, y=0.5),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0.9, y=0.5),
            fold=crease.Fold.MOUNTAIN,
        ),
    ]
    central_pleat = crease.Crease(
        point.Point(x=0.5, y=0.5),
        point.Point(x=0.5, y=0.8),
        fold=crease.Fold.MOUNTAIN,
    )
    hinge = crease.Crease(
        point.Point(x=0.1, y=0.5),
        point.Point(x=0.9, y=0.5),
        fold=crease.Fold.MOUNTAIN,
    )
    # Even segments, central pleats -> allow_symmetric=True
    hinge_metadata = hinge_utils.HingeMetaData(
        hinge=hinge, segments=segments, central_pleats=[central_pleat]
    )
    self.assertTrue(hinge_metadata.allow_symmetric)

    # Same as above but with ban_symmetric=True -> allow_symmetric=False
    hinge_metadata = hinge_utils.HingeMetaData(
        hinge=hinge,
        segments=segments,
        central_pleats=[central_pleat],
        ban_symmetric=True,
    )
    self.assertFalse(hinge_metadata.allow_symmetric)

    # Odd segments, central pleats -> allow_symmetric=False
    hinge_metadata = hinge_utils.HingeMetaData(
        hinge=hinge, segments=[segments[0]], central_pleats=[central_pleat]
    )
    self.assertFalse(hinge_metadata.allow_symmetric)
    # Even segments, no central pleats -> allow_symmetric=False
    hinge_metadata = hinge_utils.HingeMetaData(
        hinge=hinge, segments=segments, central_pleats=[]
    )
    self.assertFalse(hinge_metadata.allow_symmetric)

  def test_flat_property_both_sticks_up_is_not_flat(self):
    sf_dict = {
        'name': 'test',
        'category': 'test',
        'complexity': 1,
        'root': 's1',
        'children': [
            {
                'name': 's1',
                'start': 'j1',
                'end': 'j2',
                'azimuth_angle': 90,
                'length': 1,
            },
            {
                'name': 's2',
                'start': 'j1',
                'end': 'j3',
                'azimuth_angle': 90,
                'length': 1,
            },
        ],
    }
    stick_figure = sf.StickFigure.from_dict(sf_dict)
    hinge_crease = crease.Crease(
        point.Point(x=0, y=-1, require_on_paper=False),
        point.Point(x=0, y=1, require_on_paper=False),
        fold=crease.Fold.HINGE,
    )
    hinge_info = types.HingeInfo(
        coordinate=hinge_crease,
        assigned=False,
        flap_names=('s1', 's2'),
    )
    packing_information = (
        hinge_utils.bus.PackedCreasePattern.from_packing_output(
            packing_output.PackingOutput(
                success=True,
                packing_cp=hinge_utils.crease_pattern.CreasePattern(
                    _BORDERS, grid_size=8, light_mode=True
                ),
                flap_rectangles=None,
                packing_rivers=dict(),
                stick_figure=stick_figure,
                hinges=[hinge_info],
                tracker=None,
            ),
            design=None,
        )
    )
    solver_config = hinge_utils.SolverConfig(
        grid_size=8,
        hinges_from_stick_figure=True,
        packing_information=packing_information,
    )
    hinge_metadata = hinge_utils.HingeMetaData(
        hinge=hinge_crease,
        segments=[],
        central_pleats=[],
        solver_config=solver_config,
    )
    self.assertFalse(hinge_metadata.flat)

  def test_reference_init_state_vertex_set_predicate(self):
    """Verifies default flat_foldability() and reference init_state."""
    center = point.Point(x=0.5, y=0.5)
    # 4 creases at (0.5, 0.5) with angles 0 (M), 45 (V), 90 (M), 225 (V):
    # satisfies Kawasaki (45+135=180) and crimp_angles, fails Maekawa (2M, 2V).
    maekawa_only_pleats = [
        crease.Crease(
            center, point.Point(x=1.0, y=0.5), fold=crease.Fold.MOUNTAIN
        ),
        crease.Crease(
            center, point.Point(x=1.0, y=1.0), fold=crease.Fold.VALLEY
        ),
        crease.Crease(
            center, point.Point(x=0.5, y=1.0), fold=crease.Fold.MOUNTAIN
        ),
        crease.Crease(
            point.Point(x=0.0, y=0.0), center, fold=crease.Fold.VALLEY
        ),
    ]
    v_test = hinge_utils.vertex.Vertex(maekawa_only_pleats, vertex_point=center)
    self.assertTrue(
        v_test.check_foldability_constraints(
            check_crimp=False, check_maekawa=False
        )
    )
    self.assertFalse(
        v_test.check_foldability_constraints(
            check_crimp=False, check_maekawa=True
        )
    )
    self.assertEqual(
        v_test.flat_foldability(),
        v_test.check_crimp_angles and v_test.check_kawasaki,
    )

    ref_cfg = hinge_utils.SolverConfig(
        grid_size=examples.HUMAN.grid_size,
        recovery=False,
        allow_constraint_relaxation=False,
    )
    solver = ref_cfg.make_from_cp(examples.HUMAN.packing_cp)
    init_state = solver.init_state
    init_cp = hinge_utils.crease_pattern.CreasePattern(
        solver.borders + init_state.pleats + init_state.ridges,
        grid_size=solver.config.grid_size,
    )
    ref_base_vertices = [
        v
        for v in init_cp.vertices
        if (not (not v.internal or (v.check_crimp_angles and v.check_kawasaki)))
        or hinge_utils._four_ridges_vertex(v, init_state.ridges)
    ]
    ref_vertices = hinge_utils._vertices_from_crease_intersections(
        init_cp, init_state.unvisited_hinges, ref_base_vertices
    )
    self.assertEqual(
        set(init_state.vertices.keys()),
        {v.point for v in ref_vertices},
    )

  def test_tip_index_and_line_overlap_index(self):
    """Verifies TipIndex and LineOverlapIndex match naive O(N^2) scans."""
    all_creases = list(examples.SCORPION.packing_cp.creases) + list(
        examples.GENERATED2.packing_cp.creases
    )
    tip_idx = hinge_utils.box_pleating_utils.TipIndex(all_creases)
    overlap_idx = hinge_utils.box_pleating_utils.LineOverlapIndex(all_creases)
    indexed_res = [
        (
            overlap_idx.has_overlap(c),
            len(tip_idx.non_overlapping_at_tip(c)),
            tip_idx.count_at_tip(c.p1),
        )
        for c in all_creases
    ]
    naive_res = [
        (
            any(c.is_overlapping(o) for o in all_creases),
            len(
                hinge_utils.box_pleating_utils.get_interesecting_non_overlapping_creases(
                    c, all_creases
                )
            ),
            sum(1 for o in all_creases if o.is_tip(c.p1)),
        )
        for c in all_creases
    ]
    self.assertEqual(indexed_res, naive_res)

  def test_solver_step_count_and_exhaustion_on_resume(self):
    cp = examples.WATERBOMB.packing_cp
    config = hinge_utils.SolverConfig(
        max_steps=5,
        max_number_of_cps=1,
        remove_central_crease=False,
    )
    solver = config.make_from_cp(cp)
    self.assertEqual(solver.step_count, 0)
    self.assertFalse(solver.is_exhausted)

    _ = list(solver.iter_solutions())
    self.assertGreaterEqual(solver.step_count, 1)

    prev_step_count = solver.step_count
    _ = list(solver.iter_solutions())
    self.assertGreaterEqual(solver.step_count, prev_step_count)

  def test_make_from_cp_infers_grid_size_when_none(self):
    orig_grid = examples.WATERBOMB.packing_cp.grid_size
    mock_cp = crease_pattern.CreasePattern(
        list(examples.WATERBOMB.packing_cp.creases)
    )
    mock_cp.grid_size = None
    config = hinge_utils.SolverConfig(
        max_steps=5,
        max_number_of_cps=1,
    )
    solver = config.make_from_cp(mock_cp)
    self.assertEqual(solver.config.grid_size, orig_grid)
    _ = config.is_valid_crease_pattern(mock_cp)

  def test_max_branching_factor_limits_expansion(self):
    cp = examples.SPIDER.packing_cp
    config = hinge_utils.SolverConfig(
        grid_size=examples.SPIDER.grid_size,
        max_branching_factor=1,
    )
    solver = config.make_from_cp(cp)

    st = solver.init_state
    active_states = {hash(st): st}

    # Force expansion
    st.get_next_states(active_states)

    # Active states should have the original state + exactly
    # max_branching_factor new states
    self.assertLen(active_states, 2)

  @parameterized.parameters([
      dict(example=examples.HUMAN),
      dict(example=examples.SPIDER),
  ])
  def test_record_stages_retains_central_ridges_in_stage_4(
      self,
      example: examples.BoxPleatingCreasePatternExample,
  ):
    config = hinge_utils.SolverConfig(grid_size=example.grid_size)
    solver = config.make_from_cp(example.packing_cp, record_stages=True)
    stages = dict(solver.initial_stage_snapshots)
    self.assertIn('(3) Assigned Pleats', stages)
    self.assertIn('(4) Assigned Ridges', stages)
    self.assertIn('(5) Central Ridges', stages)

    packing_ridges = [
        c for c in example.packing_cp.creases if c.fold == crease.Fold.MOUNTAIN
    ]
    _, central_ridges = (
        hinge_utils.box_pleating_utils.split_unassigned_and_central_ridges(
            packing_ridges
        )
    )
    self.assertNotEmpty(central_ridges)

    stage3_cp = stages['(3) Assigned Pleats']
    stage4_cp = stages['(4) Assigned Ridges']
    stage5_cp = stages['(5) Central Ridges']

    for v in stage4_cp.vertices:
      if v.point.is_border:
        self.assertFalse(v.internal)

    for cr in central_ridges:
      stage3_overlapping = [
          c for c in stage3_cp.creases if cr.is_overlapping(c)
      ]
      stage4_overlapping = [
          c for c in stage4_cp.creases if cr.is_overlapping(c)
      ]
      stage5_overlapping = [
          c for c in stage5_cp.creases if cr.is_overlapping(c)
      ]
      self.assertNotEmpty(stage3_overlapping)
      self.assertEqual(stage4_overlapping, stage3_overlapping)
      self.assertNotEmpty(stage5_overlapping)

  def test_state_from_hinge_reassigned_shared_central_pleat(self):
    h1 = crease.Crease(
        point.Point(x=0.25, y=0.25),
        point.Point(x=0.25, y=0.75),
        fold=crease.Fold.HINGE,
    )
    h2 = crease.Crease(
        point.Point(x=0.75, y=0.25),
        point.Point(x=0.75, y=0.75),
        fold=crease.Fold.HINGE,
    )
    # A collinear horizontal hinge segment on the y=0.5 line at (0.25, 0.5)
    # that must survive in v.creases when shared_central_pleat is reassigned.
    collinear_hinge_seg = crease.Crease(
        point.Point(x=0.25, y=0.5),
        point.Point(x=0.5, y=0.5),
        fold=crease.Fold.HINGE,
    )
    shared_central_pleat = crease.Crease(
        point.Point(x=0.0, y=0.5),
        point.Point(x=1.0, y=0.5),
        fold=crease.Fold.MOUNTAIN,
        elevation=0,
    )
    ridges = [
        crease.Crease(
            point.Point(x=0.0, y=0.0),
            point.Point(x=0.25, y=0.25),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.0, y=1.0),
            point.Point(x=0.25, y=0.75),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=1.0, y=0.0),
            point.Point(x=0.75, y=0.25),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=1.0, y=1.0),
            point.Point(x=0.75, y=0.75),
            fold=crease.Fold.MOUNTAIN,
        ),
    ]
    solver_config = hinge_utils.SolverConfig(
        grid_size=4,
        check_local_flat_foldability=True,
        check_global_flat_foldability=False,
        recovery=True,
    )
    state = hinge_utils.State.init_state(
        pleats=[shared_central_pleat],
        unassigned_pleats=[],
        hinges=[h1, h2],
        borders=_BORDERS,
        solver_config=solver_config,
        ridges=ridges,
        partition_order=None,
    )
    # Simulate h1 being assigned symmetric first while h2 is initially flat
    # (so shared_central_pleat gets split and reassigned into state.pleats),
    # followed by h2 being relaxed and assigned symmetric.
    state.hinge_dict = dict(state.hinge_dict)
    state.hinge_dict[h2.hash_value].__dict__['flat'] = True
    state._pleat_blocking_hinges_cache.clear()  # pylint: disable=protected-access
    state_after_h1 = hinge_utils.state_from_hinge(
        state,
        h1,
        state.hinge_dict,
        hinge_utils.box_pleating_utils.HingeAssignmentType(
            fold=crease.Fold.VALLEY, symmetric=True
        ),
    )
    self.assertNotIn(shared_central_pleat, state_after_h1.unassigned_pleats)
    state_after_h1.hinge_dict = dict(state_after_h1.hinge_dict)
    state_after_h1.hinge_dict[h2.hash_value] = dataclasses.replace(
        state_after_h1.hinge_dict[h2.hash_value],
        force_non_flat=True,
    )
    state_after_h1._pleat_blocking_hinges_cache.clear()  # pylint: disable=protected-access
    # Attach collinear_hinge_seg to vertex (0.25, 0.5) before reassigning h2
    # to verify that vertex cleanup only removes matching_pleats and preserves
    # collinear hinge segments on the same line.
    v_at_h1 = state_after_h1.vertices.get(point.Point(x=0.25, y=0.5))
    if v_at_h1 is not None:
      v_at_h1.add_crease(collinear_hinge_seg)
    state_after_h2 = hinge_utils.state_from_hinge(
        state_after_h1,
        h2,
        state_after_h1.hinge_dict,
        hinge_utils.box_pleating_utils.HingeAssignmentType(
            fold=crease.Fold.VALLEY, symmetric=True
        ),
    )
    self.assertIsNotNone(state_after_h2)
    v_at_h1_after = state_after_h2.vertices.get(point.Point(x=0.25, y=0.5))
    if v_at_h1_after is not None:
      self.assertIn(collinear_hinge_seg, v_at_h1_after.creases)


if __name__ == '__main__':
  absltest.main()
