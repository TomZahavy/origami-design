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

"""Generic backtracking helper functions."""

from collections.abc import MutableSequence
import logging
from typing import Callable, Iterator, Type, TypeVar

from .. import timeout
from ..stick_figures import stick as stick_lib
from . import config as config_lib
from . import types
from . import utils_tracker
from .debug import debug_types

StackFrameT = TypeVar('StackFrameT', types.StackFrame, types.RiverStackFrame)
CandidateT = TypeVar('CandidateT', types.Candidate, types.RiverCandidate)


def try_to_advance(
    candidate_iterator: Iterator[CandidateT],
    add_fn: Callable[[CandidateT], list[str]],
    stack: MutableSequence[StackFrameT],
    stack_frame_cls: Type[StackFrameT],
    step_index: int,
    tracker: utils_tracker.CreasePatternTracker,
    debug: debug_types.DebugConfig,
    stick: stick_lib.Stick | None = None,
    config: config_lib.PackingConfig | None = None,
) -> bool:
  """Tries to advance one step in backtracking search."""
  del stick, config
  for candidate in candidate_iterator:
    timeout.maybe_timeout_cooperatively()
    try:
      object_ids = add_fn(candidate)
      debug.record_step(
          tracker,
          'ATTEMPT',
          f"Place {candidate['stick_name']}. Success",
          cand=candidate,
      )
      frame = stack_frame_cls(
          step_index=step_index,
          iterator=candidate_iterator,
          applied_candidate=candidate,
          object_ids=object_ids,
      )
      stack.append(frame)
      return True
    except ValueError:
      debug.record_step(
          tracker,
          'FAIL',
          f"Placement failed for {candidate['stick_name']}.",
          cand=candidate,
      )
      continue
  return False


def try_to_backtrack(
    stack: MutableSequence[StackFrameT],
    add_fn: Callable[[CandidateT], list[str]],
    remove_fn: Callable[[list[str]], None],
    tracker: utils_tracker.CreasePatternTracker,
    debug: debug_types.DebugConfig,
) -> int | None:
  """Tries to backtrack in backtracking search."""
  while stack:
    timeout.maybe_timeout_cooperatively()
    last_level = stack[-1]
    debug.record_step(
        tracker,
        'BACKTRACK',
        'Backtracking: removing'
        f" {last_level.applied_candidate['stick_name']}",
        cand=last_level.applied_candidate,
    )
    remove_fn(last_level.object_ids)

    for next_candidate in last_level.iterator:
      timeout.maybe_timeout_cooperatively()
      try:
        new_object_ids = add_fn(next_candidate)
        debug.record_step(
            tracker,
            'ATTEMPT',
            f"Place {next_candidate['stick_name']}. Success",
            cand=next_candidate,
        )
        last_level.object_ids = new_object_ids
        last_level.applied_candidate = next_candidate
        break
      except ValueError:
        debug.record_step(
            tracker,
            'FAIL',
            f"Placement failed for {next_candidate['stick_name']}.",
            cand=next_candidate,
        )
        continue
    else:
      failed_level = stack.pop()
      cand_that_failed = failed_level.applied_candidate
      debug.record_step(
          tracker,
          'FAIL',
          f"Place {cand_that_failed['stick_name']}. Exhausted.",
          cand=cand_that_failed,
      )
      continue
    return last_level.step_index + 1

  logging.info('FAILURE: Stack is empty. All possibilities exhausted.')
  if debug:
    debug.record_step(
        tracker,
        'BACKTRACK_FAILED',
        'Stack empty, backtracking failed.',
        cand=None,
    )
  return None
