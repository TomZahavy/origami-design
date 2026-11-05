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

import datetime
import time
from unittest import mock

from absl.testing import absltest
from bp_pipeline import timeout
from bp_pipeline.packing import types
from bp_pipeline.packing import utils_backtracking
from bp_pipeline.packing import utils_tracker
from bp_pipeline.packing.debug import debug_types


class UtilsBacktrackingTest(absltest.TestCase):

  def test_try_to_advance_success(self):
    candidates = [
        {'stick_name': 's1', 'type': 'FLAP', 'placement': mock.Mock()},
    ]
    candidate_iterator = iter(candidates)
    add_fn = mock.Mock(return_value=['id1'])
    stack = []
    stack_frame_cls = types.StackFrame
    step_index = 0
    tracker = mock.create_autospec(utils_tracker.CreasePatternTracker)
    debug = debug_types.DebugConfig()
    mock_record_step = self.enter_context(
        mock.patch.object(debug, 'record_step', autospec=True)
    )

    result = utils_backtracking.try_to_advance(
        candidate_iterator,
        add_fn,
        stack,
        stack_frame_cls,
        step_index,
        tracker,
        debug,
    )

    self.assertTrue(result)
    self.assertLen(stack, 1)
    add_fn.assert_called_once_with(candidates[0])
    mock_record_step.assert_called_once_with(
        tracker,
        'ATTEMPT',
        'Place s1. Success',
        cand=candidates[0],
    )

  def test_try_to_advance_fail_once_then_success(self):
    candidates = [
        {'stick_name': 's1', 'type': 'FLAP', 'placement': mock.Mock()},
        {'stick_name': 's2', 'type': 'FLAP', 'placement': mock.Mock()},
    ]
    candidate_iterator = iter(candidates)
    add_fn = mock.Mock(side_effect=[ValueError, ['id2']])
    stack = []
    stack_frame_cls = types.StackFrame
    step_index = 0
    tracker = mock.create_autospec(utils_tracker.CreasePatternTracker)
    debug = debug_types.DebugConfig()
    mock_record_step = self.enter_context(
        mock.patch.object(debug, 'record_step', autospec=True)
    )

    result = utils_backtracking.try_to_advance(
        candidate_iterator,
        add_fn,
        stack,
        stack_frame_cls,
        step_index,
        tracker,
        debug,
    )

    self.assertTrue(result)
    self.assertLen(stack, 1)
    self.assertEqual(stack[0].applied_candidate['stick_name'], 's2')
    self.assertEqual(add_fn.call_count, 2)
    add_fn.assert_has_calls(
        [mock.call(candidates[0]), mock.call(candidates[1])]
    )
    self.assertEqual(mock_record_step.call_count, 2)
    mock_record_step.assert_has_calls([
        mock.call(
            tracker, 'FAIL', 'Placement failed for s1.', cand=candidates[0]
        ),
        mock.call(tracker, 'ATTEMPT', 'Place s2. Success', cand=candidates[1]),
    ])

  def test_try_to_advance_iterator_empty(self):
    candidate_iterator = iter([])
    add_fn = mock.Mock()
    stack = []
    stack_frame_cls = types.StackFrame
    step_index = 0
    tracker = mock.create_autospec(utils_tracker.CreasePatternTracker)
    debug = debug_types.DebugConfig()
    mock_record_step = self.enter_context(
        mock.patch.object(debug, 'record_step', autospec=True)
    )

    result = utils_backtracking.try_to_advance(
        candidate_iterator,
        add_fn,
        stack,
        stack_frame_cls,
        step_index,
        tracker,
        debug,
    )

    self.assertFalse(result)
    self.assertEmpty(stack)
    add_fn.assert_not_called()
    mock_record_step.assert_not_called()

  def test_try_to_advance_all_candidates_fail(self):
    candidates = [
        {'stick_name': 's1', 'type': 'FLAP', 'placement': mock.Mock()},
    ]
    candidate_iterator = iter(candidates)
    add_fn = mock.Mock(side_effect=ValueError)
    stack = []
    stack_frame_cls = types.StackFrame
    step_index = 0
    tracker = mock.create_autospec(utils_tracker.CreasePatternTracker)
    debug = debug_types.DebugConfig()
    mock_record_step = self.enter_context(
        mock.patch.object(debug, 'record_step', autospec=True)
    )

    result = utils_backtracking.try_to_advance(
        candidate_iterator,
        add_fn,
        stack,
        stack_frame_cls,
        step_index,
        tracker,
        debug,
    )

    self.assertFalse(result)
    self.assertEmpty(stack)
    add_fn.assert_called_once_with(candidates[0])
    mock_record_step.assert_called_once_with(
        tracker,
        'FAIL',
        'Placement failed for s1.',
        cand=candidates[0],
    )

  def test_try_to_backtrack_empty_stack(self):
    stack = []
    add_fn = mock.Mock()
    remove_fn = mock.Mock()
    tracker = mock.create_autospec(utils_tracker.CreasePatternTracker)
    debug = debug_types.DebugConfig()
    mock_record_step = self.enter_context(
        mock.patch.object(debug, 'record_step', autospec=True)
    )
    result = utils_backtracking.try_to_backtrack(
        stack, add_fn, remove_fn, tracker, debug
    )
    self.assertIsNone(result)
    mock_record_step.assert_called_once_with(
        tracker,
        'BACKTRACK_FAILED',
        'Stack empty, backtracking failed.',
        cand=None,
    )

  def test_try_to_backtrack_iterator_exhausted(self):
    cand1 = {'stick_name': 's1', 'type': 'FLAP', 'placement': mock.Mock()}
    frame = types.StackFrame(
        step_index=0,
        iterator=iter([]),
        applied_candidate=cand1,
        object_ids=['id1'],
    )
    stack = [frame]
    add_fn = mock.Mock()
    remove_fn = mock.Mock()
    tracker = mock.create_autospec(utils_tracker.CreasePatternTracker)
    debug = debug_types.DebugConfig()
    mock_record_step = self.enter_context(
        mock.patch.object(debug, 'record_step', autospec=True)
    )
    result = utils_backtracking.try_to_backtrack(
        stack, add_fn, remove_fn, tracker, debug
    )
    self.assertIsNone(result)
    self.assertEmpty(stack)
    remove_fn.assert_called_once_with(['id1'])
    add_fn.assert_not_called()
    self.assertEqual(mock_record_step.call_count, 3)
    mock_record_step.assert_has_calls([
        mock.call(
            tracker,
            'BACKTRACK',
            'Backtracking: removing s1',
            cand=cand1,
        ),
        mock.call(
            tracker,
            'FAIL',
            'Place s1. Exhausted.',
            cand=cand1,
        ),
        mock.call(
            tracker,
            'BACKTRACK_FAILED',
            'Stack empty, backtracking failed.',
            cand=None,
        ),
    ])

  def test_try_to_backtrack_found_alternative(self):
    cand1 = {'stick_name': 's1', 'type': 'FLAP', 'placement': mock.Mock()}
    cand2 = {'stick_name': 's2', 'type': 'FLAP', 'placement': mock.Mock()}
    frame = types.StackFrame(
        step_index=0,
        iterator=iter([cand2]),
        applied_candidate=cand1,
        object_ids=['id1'],
    )
    stack = [frame]
    add_fn = mock.Mock(return_value=['id2'])
    remove_fn = mock.Mock()
    tracker = mock.create_autospec(utils_tracker.CreasePatternTracker)
    debug = debug_types.DebugConfig()
    mock_record_step = self.enter_context(
        mock.patch.object(debug, 'record_step', autospec=True)
    )
    result = utils_backtracking.try_to_backtrack(
        stack, add_fn, remove_fn, tracker, debug
    )
    self.assertEqual(result, 1)
    self.assertLen(stack, 1)
    self.assertEqual(stack[0].applied_candidate, cand2)
    self.assertEqual(stack[0].object_ids, ['id2'])
    remove_fn.assert_called_once_with(['id1'])
    add_fn.assert_called_once_with(cand2)
    self.assertEqual(mock_record_step.call_count, 2)
    mock_record_step.assert_has_calls([
        mock.call(
            tracker,
            'BACKTRACK',
            'Backtracking: removing s1',
            cand=cand1,
        ),
        mock.call(
            tracker,
            'ATTEMPT',
            'Place s2. Success',
            cand=cand2,
        ),
    ])

  def test_try_to_backtrack_alternative_fails(self):
    cand1 = {'stick_name': 's1', 'type': 'FLAP', 'placement': mock.Mock()}
    cand2 = {'stick_name': 's2', 'type': 'FLAP', 'placement': mock.Mock()}
    frame = types.StackFrame(
        step_index=0,
        iterator=iter([cand2]),
        applied_candidate=cand1,
        object_ids=['id1'],
    )
    stack = [frame]
    add_fn = mock.Mock(side_effect=ValueError)
    remove_fn = mock.Mock()
    tracker = mock.create_autospec(utils_tracker.CreasePatternTracker)
    debug = debug_types.DebugConfig()
    mock_record_step = self.enter_context(
        mock.patch.object(debug, 'record_step', autospec=True)
    )
    result = utils_backtracking.try_to_backtrack(
        stack, add_fn, remove_fn, tracker, debug
    )
    self.assertIsNone(result)
    self.assertEmpty(stack)
    remove_fn.assert_called_once_with(['id1'])
    add_fn.assert_called_once_with(cand2)
    self.assertEqual(mock_record_step.call_count, 4)
    mock_record_step.assert_has_calls([
        mock.call(
            tracker,
            'BACKTRACK',
            'Backtracking: removing s1',
            cand=cand1,
        ),
        mock.call(
            tracker,
            'FAIL',
            'Placement failed for s2.',
            cand=cand2,
        ),
        mock.call(
            tracker,
            'FAIL',
            'Place s1. Exhausted.',
            cand=cand1,
        ),
        mock.call(
            tracker,
            'BACKTRACK_FAILED',
            'Stack empty, backtracking failed.',
            cand=None,
        ),
    ])

  def test_try_to_advance_raises_cooperative_timeout(self):
    candidates = [
        {'stick_name': 's1', 'type': 'FLAP', 'placement': mock.Mock()},
    ]
    candidate_iterator = iter(candidates)
    add_fn = mock.Mock()
    stack = []
    tracker = mock.create_autospec(utils_tracker.CreasePatternTracker)
    debug = debug_types.DebugConfig()

    with timeout.cooperative_timeout(datetime.timedelta(microseconds=1)):
      time.sleep(0.002)
      with self.assertRaises(timeout.CooperativeTimeoutError):
        utils_backtracking.try_to_advance(
            candidate_iterator,
            add_fn,
            stack,
            types.StackFrame,
            0,
            tracker,
            debug,
        )

  def test_try_to_backtrack_raises_cooperative_timeout(self):
    stack = [
        types.StackFrame(
            step_index=0,
            iterator=iter([{'stick_name': 's2'}]),
            applied_candidate={'stick_name': 's1'},
            object_ids=['id1'],
        )
    ]
    add_fn = mock.Mock()
    remove_fn = mock.Mock()
    tracker = mock.create_autospec(utils_tracker.CreasePatternTracker)
    debug = debug_types.DebugConfig()

    with timeout.cooperative_timeout(datetime.timedelta(microseconds=1)):
      time.sleep(0.002)
      with self.assertRaises(timeout.CooperativeTimeoutError):
        utils_backtracking.try_to_backtrack(
            stack, add_fn, remove_fn, tracker, debug
        )


if __name__ == '__main__':
  absltest.main()
