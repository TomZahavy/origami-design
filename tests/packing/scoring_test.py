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

from unittest import mock

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.crease_pattern import point
from bp_pipeline.packing import scoring
from bp_pipeline.packing import types
from bp_pipeline.packing import utils_tracker
import numpy as np

GRID_SIZE = 10

_CORNER_PLACEMENT = types.PolygonPlacement(
    offset=(-1, -1),
    size=(2, 2),
    center=point.Point(x=0, y=0),
)
_CENTER_PLACEMENT = types.PolygonPlacement(
    offset=(4, 4),
    size=(2, 2),
    center=point.Point(x=0.5, y=0.5),
)


class ScoringTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self._tracker = utils_tracker.CreasePatternTracker(grid_size=GRID_SIZE)

  def _make_flap_candidate(
      self, placement: types.PolygonPlacement
  ) -> types.Candidate:
    return types.Candidate(type='FLAP', stick_name='A', placement=placement)

  @parameterized.parameters(
      dict(placement=_CORNER_PLACEMENT, expected_score=1.0),
      dict(placement=_CENTER_PLACEMENT, expected_score=0.0),
  )
  def test_is_center_on_border_score(
      self, placement: types.PolygonPlacement, expected_score: float
  ):
    self.assertEqual(
        scoring.is_center_on_border_score(self._tracker, placement, None),
        expected_score,
    )

  def test_random_score(self):
    score = scoring.random_score(self._tracker, _CENTER_PLACEMENT, None)
    self.assertBetween(score, 0, 1)

  @parameterized.parameters(
      dict(
          placement=_CENTER_PLACEMENT,
          expected_score=-8.0,
      ),
      dict(
          placement=_CORNER_PLACEMENT,
          expected_score=-2.0,
      ),
      dict(
          placement=types.PolygonPlacement(
              offset=(0, 0), size=(2, 2), center=point.Point(x=0.1, y=0.1)
          ),
          expected_score=-4.0,
      ),
  )
  def test_perimeter_score_on_empty_grid(
      self, placement: types.PolygonPlacement, expected_score: float
  ):
    self.assertEqual(
        scoring.perimeter_score(self._tracker, placement, None),
        expected_score,
    )

  def test_perimeter_score_with_occupied_cells(self):
    self._tracker.occupancy_grid = np.ones_like(self._tracker.occupancy_grid)
    self._tracker.occupancy_grid[0, 0] = False
    self.assertEqual(
        scoring.perimeter_score(self._tracker, _CORNER_PLACEMENT, None), 0.0
    )

  def test_subproblem_perimeter_score_counts_subproblem_polygons(self):
    context = scoring.PackingContext(base_square_dims={'A': (2, 2)})
    self._tracker.add_polygon(
        'A',
        types.PolygonPlacement(
            offset=(2, 2), size=(2, 2), center=point.Point(x=0.1, y=0.1)
        ),
    )
    placement = types.PolygonPlacement(
        offset=(0, 2), size=(2, 2), center=point.Point(x=0.1, y=0.3)
    )
    self.assertEqual(
        scoring.subproblem_perimeter_score(self._tracker, placement, context),
        -6.0,
    )

  def test_subproblem_perimeter_score_ignores_non_subproblem_polygons(self):
    context = scoring.PackingContext(base_square_dims={'A': (2, 2)})
    self._tracker.add_polygon(
        'B',
        types.PolygonPlacement(
            offset=(2, 2), size=(2, 2), center=point.Point(x=0.1, y=0.1)
        ),
    )
    placement = types.PolygonPlacement(
        offset=(0, 2), size=(2, 2), center=point.Point(x=0.1, y=0.3)
    )
    self.assertEqual(
        scoring.subproblem_perimeter_score(self._tracker, placement, context),
        -8.0,
    )

  def test_subproblem_perimeter_score_ignores_border(self):
    context = scoring.PackingContext(base_square_dims={'A': (2, 2)})
    placement = types.PolygonPlacement(
        offset=(0, 0), size=(2, 2), center=point.Point(x=0.1, y=0.1)
    )
    self.assertEqual(
        scoring.subproblem_perimeter_score(self._tracker, placement, context),
        -8.0,
    )

  def test_hierarchical_score(self):
    score_fn1 = lambda tracker, placement, context: 1.0
    score_fn2 = lambda tracker, placement, context: 2.0
    hierarchical_score = scoring.HierarchicalScore([score_fn1, score_fn2])
    score = hierarchical_score(self._tracker, _CENTER_PLACEMENT, None)
    self.assertEqual(score, (1.0, 2.0))

  def test_hierarchical_score_flattens_scores(self):
    score_fn1 = lambda tracker, placement, context: 1.0
    score_fn2 = lambda tracker, placement, context: (2.0, 3.0)
    hierarchical_score = scoring.HierarchicalScore([score_fn1, score_fn2])
    score = hierarchical_score(self._tracker, _CENTER_PLACEMENT, None)
    self.assertEqual(score, (1.0, 2.0, 3.0))

  def test_pruning_score_no_context_raises_error(self):
    pruning_score = scoring.ImpossibleRemainingFlapsScore()
    with self.assertRaisesRegex(ValueError, 'Context is required'):
      pruning_score(self._tracker, _CENTER_PLACEMENT, None)

  @mock.patch.object(scoring, '_largest_possible_flap')
  def test_pruning_score_prunes_if_largest_remaining_too_big(
      self, mock_largest_possible_flap
  ):
    pruning_score = scoring.ImpossibleRemainingFlapsScore()
    context = scoring.PackingContext(base_square_dims={'A': (3, 3)})
    mock_largest_possible_flap.return_value = 2
    self.assertEqual(
        pruning_score(self._tracker, _CENTER_PLACEMENT, context), 0.0
    )

  @mock.patch.object(scoring, '_largest_possible_flap')
  def test_pruning_score_does_not_prune_if_largest_remaining_not_too_big(
      self, mock_largest_possible_flap
  ):
    pruning_score = scoring.ImpossibleRemainingFlapsScore()
    context = scoring.PackingContext(base_square_dims={'A': (3, 3)})
    mock_largest_possible_flap.return_value = 3
    self.assertEqual(
        pruning_score(self._tracker, _CENTER_PLACEMENT, context), 1.0
    )
    mock_largest_possible_flap.return_value = 4
    self.assertEqual(
        pruning_score(self._tracker, _CENTER_PLACEMENT, context), 1.0
    )
    mock_largest_possible_flap.return_value = np.inf
    self.assertEqual(
        pruning_score(self._tracker, _CENTER_PLACEMENT, context), 1.0
    )

  @mock.patch.object(scoring, '_largest_possible_flap')
  def test_pruning_score_with_packed_polygons(self, mock_largest_possible_flap):
    pruning_score = scoring.ImpossibleRemainingFlapsScore()
    context = scoring.PackingContext(
        base_square_dims={'A': (3, 3), 'B': (1, 1)}
    )
    self._tracker.packed_polygons['A'] = types.PolygonPlacement(
        offset=(0, 0), size=(3, 3), center=point.Point(x=0, y=0)
    )
    mock_largest_possible_flap.return_value = 0
    self.assertEqual(
        pruning_score(self._tracker, _CENTER_PLACEMENT, context), 0.0
    )
    mock_largest_possible_flap.return_value = 1
    self.assertEqual(
        pruning_score(self._tracker, _CENTER_PLACEMENT, context), 1.0
    )

  @parameterized.parameters(
      dict(
          scoring_fn=lambda tracker, placement, context: 10.0,
          expected_score=-10.0,
      ),
      dict(
          scoring_fn=lambda tracker, placement, context: (10.0, 20.0),
          expected_score=(-10.0, -20.0),
      ),
  )
  def test_key_from_scoring_fn(self, scoring_fn, expected_score):
    key_fn = scoring._key_from_scoring_fn(self._tracker, scoring_fn, None)
    candidate = self._make_flap_candidate(_CENTER_PLACEMENT)
    self.assertEqual(key_fn(candidate), expected_score)

  def test_key_from_scoring_fn_with_placement_index(self):
    placements = [
        _CORNER_PLACEMENT,
        _CENTER_PLACEMENT,
        types.PolygonPlacement(
            offset=(1, 1), size=(1, 1), center=point.Point(x=0.1, y=0.1)
        ),
    ]
    candidates = [self._make_flap_candidate(p) for p in placements]

    def index_scoring_fn(tracker, placement, context):
      del tracker, context
      try:
        return placements.index(placement)
      except ValueError:
        return -1

    key_fn = scoring._key_from_scoring_fn(self._tracker, index_scoring_fn, None)

    sorted_placements = [c['placement'] for c in sorted(candidates, key=key_fn)]
    self.assertEqual(sorted_placements, placements[::-1])


class CanonicalFlapOrderScoreTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self._tracker = utils_tracker.CreasePatternTracker(grid_size=GRID_SIZE)

  def test_canonical_flap_order_norm_score_empty(self):
    self.assertEqual(
        scoring.canonical_flap_order_norm_score(
            self._tracker, _CENTER_PLACEMENT, None
        ),
        1.0,
    )

  def test_canonical_flap_order_norm_score_violates(self):
    self._tracker.packed_polygons['A'] = _CENTER_PLACEMENT
    self.assertEqual(
        scoring.canonical_flap_order_norm_score(
            self._tracker, _CORNER_PLACEMENT, None
        ),
        0.0,
    )

  def test_canonical_flap_order_norm_score_does_not_violate(self):
    self._tracker.packed_polygons['A'] = _CORNER_PLACEMENT
    self.assertEqual(
        scoring.canonical_flap_order_norm_score(
            self._tracker, _CENTER_PLACEMENT, None
        ),
        1.0,
    )

  def test_canonical_flap_order_norm_score_equal_norm(self):
    self._tracker.packed_polygons['A'] = _CENTER_PLACEMENT
    self.assertEqual(
        scoring.canonical_flap_order_norm_score(
            self._tracker, _CENTER_PLACEMENT, None
        ),
        1.0,
    )

  def test_canonical_flap_order_norm_score_different_size(self):
    self._tracker.packed_polygons['A'] = _CENTER_PLACEMENT
    placement_diff_size = types.PolygonPlacement(
        offset=(-1, -1), size=(1, 1), center=point.Point(x=0, y=0)
    )
    self.assertEqual(
        scoring.canonical_flap_order_norm_score(
            self._tracker, placement_diff_size, None
        ),
        1.0,
    )

  def test_canonical_flap_order_norm_score_violates_but_ignored_by_context(
      self,
  ):
    self._tracker.packed_polygons['A'] = _CENTER_PLACEMENT
    context = scoring.PackingContext(base_square_dims={'B': (1, 1)})
    self.assertEqual(
        scoring.canonical_flap_order_norm_score(
            self._tracker, _CORNER_PLACEMENT, context
        ),
        1.0,
    )

  def test_canonical_flap_order_lexical_score_empty(self):
    self.assertEqual(
        scoring.canonical_flap_order_lexical_score(
            self._tracker, _CENTER_PLACEMENT, None
        ),
        1.0,
    )

  def test_canonical_flap_order_lexical_score_violates(self):
    exist_placement = types.PolygonPlacement(
        offset=(2, 2), size=(2, 2), center=point.Point(x=0.5, y=0.5)
    )
    self._tracker.packed_polygons['A'] = exist_placement
    placement_violates = types.PolygonPlacement(
        offset=(1, 2), size=(2, 2), center=point.Point(x=0.5, y=0.5)
    )
    self.assertEqual(
        scoring.canonical_flap_order_lexical_score(
            self._tracker, placement_violates, None
        ),
        0.0,
    )
    placement_violates2 = types.PolygonPlacement(
        offset=(2, 1), size=(2, 2), center=point.Point(x=0.5, y=0.5)
    )
    self.assertEqual(
        scoring.canonical_flap_order_lexical_score(
            self._tracker, placement_violates2, None
        ),
        0.0,
    )

  def test_canonical_flap_order_lexical_score_does_not_violate(self):
    exist_placement = types.PolygonPlacement(
        offset=(2, 2), size=(2, 2), center=point.Point(x=0.5, y=0.5)
    )
    self._tracker.packed_polygons['A'] = exist_placement
    placement_ok = types.PolygonPlacement(
        offset=(3, 2), size=(2, 2), center=point.Point(x=0.5, y=0.5)
    )
    self.assertEqual(
        scoring.canonical_flap_order_lexical_score(
            self._tracker, placement_ok, None
        ),
        1.0,
    )

  def test_canonical_flap_order_lexical_score_equal_offset(self):
    exist_placement = types.PolygonPlacement(
        offset=(2, 2), size=(2, 2), center=point.Point(x=0.5, y=0.5)
    )
    self._tracker.packed_polygons['A'] = exist_placement
    placement_equal = types.PolygonPlacement(
        offset=(2, 2), size=(2, 2), center=point.Point(x=0.5, y=0.5)
    )
    self.assertEqual(
        scoring.canonical_flap_order_lexical_score(
            self._tracker, placement_equal, None
        ),
        1.0,
    )

  def test_canonical_flap_order_lexical_score_different_size(self):
    exist_placement = types.PolygonPlacement(
        offset=(2, 2), size=(2, 2), center=point.Point(x=0.5, y=0.5)
    )
    self._tracker.packed_polygons['A'] = exist_placement
    placement_diff_size = types.PolygonPlacement(
        offset=(1, 1), size=(1, 1), center=point.Point(x=0.5, y=0.5)
    )
    self.assertEqual(
        scoring.canonical_flap_order_lexical_score(
            self._tracker, placement_diff_size, None
        ),
        1.0,
    )


class LargestPossibleFlapTest(parameterized.TestCase):

  def test_empty_grid(self):
    grid = np.array([[]], dtype=bool)
    self.assertEqual(scoring._largest_possible_flap(grid), 0)

  def test_fully_occupied_grid(self):
    grid = np.ones((3, 3), dtype=bool)
    self.assertEqual(scoring._largest_possible_flap(grid), 0)

  def test_fully_unoccupied_grid(self):
    grid = np.zeros((3, 3), dtype=bool)
    self.assertEqual(scoring._largest_possible_flap(grid), np.inf)

  def test_1x1_unoccupied_grid(self):
    grid = np.zeros((1, 1), dtype=bool)
    self.assertEqual(scoring._largest_possible_flap(grid), np.inf)

  def test_1x1_occupied_grid(self):
    grid = np.ones((1, 1), dtype=bool)
    self.assertEqual(scoring._largest_possible_flap(grid), 0)

  @parameterized.named_parameters(
      dict(
          testcase_name='1x1_hole',
          grid=np.array([[0]], dtype=bool),
          expected_s=np.inf,
      ),
      dict(
          testcase_name='1x1_hole_in_2x2_grid',
          grid=np.array([[1, 1], [1, 0]], dtype=bool),
          expected_s=2,
      ),
      dict(
          testcase_name='2x2_hole_in_4x4_grid',
          grid=np.array(
              [
                  [1, 1, 1, 1],
                  [1, 0, 0, 1],
                  [1, 0, 0, 1],
                  [1, 1, 1, 1],
              ],
              dtype=bool,
          ),
          expected_s=2,
      ),
      dict(
          testcase_name='3x3_hole_in_5x5_grid',
          grid=np.array(
              [
                  [1, 1, 1, 1, 1],
                  [1, 0, 0, 0, 1],
                  [1, 0, 0, 0, 1],
                  [1, 0, 0, 0, 1],
                  [1, 1, 1, 1, 1],
              ],
              dtype=bool,
          ),
          expected_s=3,
      ),
      dict(
          testcase_name='L_shape_hole',
          grid=np.array(
              [
                  [1, 1, 1, 1],
                  [1, 0, 0, 1],
                  [1, 0, 1, 1],
                  [1, 1, 1, 1],
              ],
              dtype=bool,
          ),
          expected_s=1,
      ),
      dict(
          testcase_name='corner_hole',
          grid=np.array(
              [
                  [1, 1, 1, 1],
                  [1, 0, 0, 0],
                  [1, 0, 0, 0],
                  [1, 0, 0, 0],
              ],
              dtype=bool,
          ),
          expected_s=6,
      ),
      dict(
          testcase_name='2x1_hole_in_3x3_grid',
          grid=np.array(
              [
                  [1, 1, 1],
                  [1, 0, 1],
                  [1, 0, 1],
              ],
              dtype=bool,
          ),
          expected_s=1,
      ),
      dict(
          testcase_name='1x2_hole_in_3x3_grid',
          grid=np.array(
              [
                  [1, 1, 1],
                  [1, 0, 0],
                  [1, 1, 1],
              ],
              dtype=bool,
          ),
          expected_s=1,
      ),
  )
  def test_partially_occupied_grid(self, grid, expected_s):
    self.assertEqual(scoring._largest_possible_flap(grid), expected_s)


class ScoringConfigTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self._tracker = utils_tracker.CreasePatternTracker(grid_size=GRID_SIZE)
    self._placements = [
        _CORNER_PLACEMENT,
        _CENTER_PLACEMENT,
        types.PolygonPlacement(
            offset=(1, 1), size=(1, 1), center=point.Point(x=0.1, y=0.1)
        ),
    ]
    self._candidates = [self._make_flap_candidate(p) for p in self._placements]

  def _make_flap_candidate(
      self, placement: types.PolygonPlacement
  ) -> types.Candidate:
    return types.Candidate(type='FLAP', stick_name='A', placement=placement)

  def test_sort_candidates(self):
    def index_scoring_fn(tracker, placement, context):
      del tracker, context
      try:
        return self._placements.index(placement)
      except ValueError:
        return -1

    config = scoring.ScoringConfig(scoring_fn=index_scoring_fn)
    sorted_candidates = config.sort_candidates(self._tracker, self._candidates)

    sorted_placements = [c['placement'] for c in sorted_candidates]
    self.assertEqual(sorted_placements, self._placements[::-1])

  def test_sort_candidates_with_none_scoring_fn(self):
    config = scoring.ScoringConfig(scoring_fn=None)
    sorted_candidates = config.sort_candidates(self._tracker, self._candidates)
    self.assertListEqual(sorted_candidates, self._candidates)

  def test_pruned_candidates(self):
    def prune_odd_index_fn(tracker, placement, context):
      del tracker, context
      try:
        index = self._placements.index(placement)
        return 1.0 if index % 2 == 0 else 0.0
      except ValueError:
        return 1.0

    config = scoring.ScoringConfig(
        scoring_fn=None, pruning_fn=prune_odd_index_fn
    )
    pruned_candidates = list(
        config.prune_candidates(self._tracker, self._candidates)
    )
    self.assertListEqual(
        pruned_candidates, [self._candidates[0], self._candidates[2]]
    )


class CcwBorderContinuityScoreTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self._tracker = utils_tracker.CreasePatternTracker(grid_size=40)

  def test_empty_tracker_prefers_low_ccw_index(self):
    top_left = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(10, 10), grid_size=40, require_on_paper=False
    )
    bottom_left = types.PolygonPlacement.from_grid_coords(
        offset=(0, 30), size=(10, 10), grid_size=40, require_on_paper=False
    )
    score_top_left = scoring.ccw_border_continuity_score(
        self._tracker, top_left, None
    )
    score_bottom_left = scoring.ccw_border_continuity_score(
        self._tracker, bottom_left, None
    )
    self.assertGreater(score_top_left, score_bottom_left)

  def test_ccw_close_placement_scores_higher(self):
    left_leg = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(10, 10), grid_size=40, require_on_paper=False
    )
    right_leg = types.PolygonPlacement.from_grid_coords(
        offset=(0, 10), size=(10, 10), grid_size=40, require_on_paper=False
    )
    self._tracker.add_polygon('left_leg', left_leg)
    self._tracker.add_polygon('right_leg', right_leg)

    ccw_close = types.PolygonPlacement.from_grid_coords(
        offset=(0, 20), size=(20, 20), grid_size=40, require_on_paper=False
    )
    ccw_far = types.PolygonPlacement.from_grid_coords(
        offset=(10, 0), size=(20, 20), grid_size=40, require_on_paper=False
    )

    score_close = scoring.ccw_border_continuity_score(
        self._tracker, ccw_close, None
    )
    score_far = scoring.ccw_border_continuity_score(
        self._tracker, ccw_far, None
    )
    self.assertGreater(
        score_close,
        score_far,
        f'CCW-close at offset (0,20) scored {score_close} but CCW-far at'
        f' offset (10,0) scored {score_far}. Expected close > far.',
    )

  def test_elf_scenario_draw_arm_positions(self):
    left_leg = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(10, 10), grid_size=40, require_on_paper=False
    )
    right_leg = types.PolygonPlacement.from_grid_coords(
        offset=(0, 10), size=(10, 10), grid_size=40, require_on_paper=False
    )
    self._tracker.add_polygon('left_leg', left_leg)
    self._tracker.add_polygon('right_leg', right_leg)

    draw_arm_bad = types.PolygonPlacement.from_grid_coords(
        offset=(9, -10), size=(20, 20), grid_size=40, require_on_paper=False
    )
    draw_arm_good = types.PolygonPlacement.from_grid_coords(
        offset=(0, 20), size=(20, 20), grid_size=40, require_on_paper=False
    )

    score_bad = scoring.ccw_border_continuity_score(
        self._tracker, draw_arm_bad, None
    )
    score_good = scoring.ccw_border_continuity_score(
        self._tracker, draw_arm_good, None
    )
    self.assertGreater(score_good, score_bad)


if __name__ == '__main__':
  absltest.main()
