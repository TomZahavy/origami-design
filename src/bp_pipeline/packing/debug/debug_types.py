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

"""Debug-related types for the packing solver."""

from collections.abc import Collection
import copy
import dataclasses
import enum
from typing import NotRequired, TypedDict

from ...stick_figures import stick_figure as stick_figure_lib
from .. import river as river_lib
from .. import types
from .. import utils_tracker


class DebugHistoryEntry(TypedDict):
  """A single entry in the debug history."""

  step: int
  action: str
  message: str
  tracker_snapshot: utils_tracker.CreasePatternTracker | None


class DebugStepType(enum.IntEnum):
  INTERVAL = enum.auto()
  RIVERS = enum.auto()
  PACKING = enum.auto()


@dataclasses.dataclass
class DebugConfig:
  """Configuration for packing solver debugging."""

  save_history: bool = True
  live_plot: bool = False
  plot_interval: int = 1
  plot_filter: Collection[DebugStepType] = frozenset({DebugStepType.INTERVAL})
  is_symmetric: bool = False
  step_counter: int = 0
  history: list[DebugHistoryEntry] = dataclasses.field(default_factory=list)
  stick_figure: stick_figure_lib.StickFigure | None = None
  max_steps: int | None = None

  def is_active(self) -> bool:
    return self.save_history or self.live_plot

  def get_step_types(
      self, action: str, cand: types.CandidateT | None
  ) -> set[DebugStepType]:
    """Returns the step types to be plotted for a given step."""
    step_types = set()
    if self.step_counter % self.plot_interval == 0:
      step_types.add(DebugStepType.INTERVAL)
    if cand and isinstance(cand.get('river'), types.RiverPlacementAlias):
      step_types.add(DebugStepType.RIVERS)
    if action == 'PACKING':
      step_types.add(DebugStepType.PACKING)
    return step_types

  def record_step(
      self,
      tracker: 'utils_tracker.CreasePatternTracker',
      action: str,
      message: str,
      cand: types.CandidateT | None = None,
  ):
    """Records a step in debug history and optionally plots."""
    if not self.is_active():
      return
    self.step_counter += 1

    is_river_step = cand and isinstance(
        cand.get('river'), types.RiverPlacementAlias
    )

    if cand and cand['stick_name'] in message:
      size_str = ''
      pos_str = ''
      if is_river_step:
        river: types.RiverPlacementAlias = cand['river']  # type: ignore[typeddict-item]
        width = river.width
        size_str = f'width={width}'
        if isinstance(river, river_lib.River):
          if river.orientation == river_lib.RiverOrientation.HORIZONTAL:
            start_cell = (river.offset, 0)
            pos_str = (
                f'offset={river.offset},{river.orientation.name[0]},'
                f' start={start_cell}'
            )
          else:  # VERTICAL
            start_cell = (river.grid_size - 1, river.offset)
            pos_str = (
                f'offset={river.offset},{river.orientation.name[0]},'
                f' start={start_cell}'
            )
        elif isinstance(river, river_lib.LShapedRiver):
          start_border = ''
          if river.l_shape_type in [
              river_lib.LShapeType.BOTTOM_LEFT,
              river_lib.LShapeType.TOP_LEFT,
          ]:
            start_border = 'L'
          elif river.l_shape_type == river_lib.LShapeType.TOP_RIGHT:
            start_border = 'B'
          elif river.l_shape_type == river_lib.LShapeType.BOTTOM_RIGHT:
            start_border = 'R'
          pos_str = (
              f'turn=({river.turn_x},{river.turn_y}), start={start_border}'
          )
        else:
          pos_str = 'hugging'
      elif 'placement' in cand:
        placement: types.PolygonPlacement = cand['placement']  # type: ignore[typeddict-item]
        size = placement.size
        size_str = f'{size[0]}x{size[1]}'
        pos_str = f'pos=({placement.offset[0]},{placement.offset[1]})'

      stick_name = cand['stick_name']
      message = message.replace(
          stick_name, f'{stick_name} ({size_str}, {pos_str})', 1
      )

    step_info = {
        'step': self.step_counter,
        'action': action,
        'message': message,
        'tracker_snapshot': (
            copy.deepcopy(tracker) if self.save_history else None
        ),
    }
    if self.save_history:
      self.history.append(step_info)

    if self.live_plot and self.get_step_types(action, cand).intersection(
        self.plot_filter
    ):
      highlight = cand if action == 'FAIL' else None
      print(f'Step {self.step_counter}: {message}')
      utils_tracker.plot_tracker(
          tracker,
          highlight_candidate=highlight,
          is_symmetric_packing=self.is_symmetric,
          stick_figure=self.stick_figure,
      )
    if self.max_steps and self.step_counter >= self.max_steps:
      raise types.NoPackingFoundError('Max steps reached.')


class TilingDetails(TypedDict):
  """Details about the tiling process."""

  grid_size: int
  grid_height: NotRequired[int | None]
  is_symmetric: bool
  perfect_tiling_found: bool
  unused_area: int
  num_delta_combinations: NotRequired[int]
  reason: NotRequired[str | None]
  suggestion: NotRequired[str]
  debug_history: NotRequired[list[DebugHistoryEntry]]
  constraint_satisfaction: NotRequired[str]
  satisfied_constraints: NotRequired[list[str]]
  unsatisfied_constraints: NotRequired[list[str]]
  needed_tiling_polish: NotRequired[bool]
