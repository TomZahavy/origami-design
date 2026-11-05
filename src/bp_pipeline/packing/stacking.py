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

"""Stack packing: packs a stick figure into a crease pattern tracker.

Flaps are packed vertically in traversal order with full grid width; rivers are
placed via contour-hugging around the already-placed flaps. Also referred to as
the "string-of-beads" algorithm by Robert Lang in the Treemaker manual.
"""

import collections
import dataclasses
import itertools
import logging

from ..stick_figures import stick as stick_lib
from ..stick_figures import stick_figure as sf_lib
from ..stick_figures import traversal
from . import config as config_lib
from . import packing_output
from . import river as river_lib
from . import types as packing_types
from . import utils_packing_svg
from . import utils_solver
from . import utils_tracker
from .debug import debug_types


class TrackerError(Exception):
  """Error returning an incomplete tracker."""

  def __init__(self, message: str, tracker: utils_tracker.CreasePatternTracker):
    super().__init__(message)
    self.tracker = tracker

  def plot(self):
    return utils_tracker.plot_tracker(self.tracker, title='TrackerError')


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class StackLayoutConfig:
  """Configuration for computing a stack layout from a stick figure."""

  level_shifters: bool = False
  shift_both_river_sides: bool = False
  fallback_to_asymmetric: bool = False

  def __post_init__(self):
    if self.shift_both_river_sides:
      raise NotImplementedError(
          'Shifting both river sides is not implemented yet.'
      )


@dataclasses.dataclass
class _AsymmetricStackLayout:
  """Computes a stack layout for a non-symmetric stick figure."""

  config: StackLayoutConfig = StackLayoutConfig()
  _river_stack: list[stick_lib.Stick] = dataclasses.field(
      default_factory=list, init=False
  )
  _y_offsets: list[int] = dataclasses.field(default_factory=list, init=False)
  _river_margins: list[int] = dataclasses.field(
      default_factory=list, init=False
  )
  _sticks: list[stick_lib.Stick] = dataclasses.field(
      default_factory=list, init=False
  )
  _sf_infos: list[packing_types.RiverSfInfo | None] = dataclasses.field(
      default_factory=list, init=False
  )

  @property
  def is_first_stick(self) -> bool:
    return not self._y_offsets

  def _open_or_close_river(self, stick: stick_lib.Stick):
    """Toggles a river stick on or off the river stack."""
    if not self._river_stack or stick != self._river_stack[-1]:
      self._river_stack.append(stick)
    else:
      self._river_stack.pop()

  def _add_river(self, stick: stick_lib.Stick):
    """Adds a river stick to the layout, updating y-offsets and river stack."""
    size = stick.length
    self._open_or_close_river(stick)

    if self.is_first_stick:
      self._y_offsets.append(0)

    self._y_offsets.append(self._y_offsets[-1] + size)

  def _add_flap(self, size: int):
    """Adds a flap of the given size to the layout, updating y-offsets."""
    if self.is_first_stick:
      self._y_offsets.append(-size)
    self._y_offsets.append(self._y_offsets[-1] + 2 * size)

  def _add_sacrificial_flap(
      self, stick: stick_lib.Stick, next_stick: stick_lib.Stick | None
  ):
    """Adds a sacrificial flap (level shifter) to a river stick."""
    if not self.config.level_shifters:
      return
    if stick.width <= 1:
      return
    if self.is_first_stick:
      return
    if not self.config.shift_both_river_sides and (
        self._river_stack and self._river_stack[-1] == stick
    ):
      return

    before = next_stick is None
    suffix = (
        packing_types.RIVER_SF1_SUFFIX
        if before
        else packing_types.RIVER_SF2_SUFFIX
    )
    ls_name = f'{stick.name}{suffix}'

    if next_stick is None:
      prev_stick = self._sticks[-1]
      [shared_joint] = stick.shared_joint_name(prev_stick)
    else:
      [shared_joint] = stick.shared_joint_name(next_stick)

    elevation_delta = 0.1 if before else -0.1
    elevation_angle = (
        stick.elevation_angle_at_joint(shared_joint) + elevation_delta
    )
    elevation_angle = min(90, max(-90, elevation_angle))
    ls_stick = stick_lib.Stick(
        name=ls_name,
        start=shared_joint,
        end=f'{ls_name}_end',
        azimuth_angle=stick.azimuth_angle_at_joint(shared_joint),
        elevation_angle=elevation_angle,
        length=1,
        width=1,
    )
    ls_stick.is_flap = True

    self.add_stick(
        ls_stick,
        sf_info=packing_types.RiverSfInfo(
            river_name=stick.name,
            river_side='top' if before else 'bottom',
            parent_joint=shared_joint,
        ),
    )

  def add_stick(
      self,
      stick: stick_lib.Stick,
      sf_info: packing_types.RiverSfInfo | None = None,
  ):
    """Adds a stick to the layout."""
    if stick.is_river:
      self._add_river(stick)
    else:
      self._add_flap(stick.length)

    self._sticks.append(stick)
    self._river_margins.append(sum(s.length for s in self._river_stack))
    self._sf_infos.append(sf_info)

  def _traversal(self, stick_figure: sf_lib.StickFigure):
    yield from traversal.packing_traversal(
        stick_figure,
        packing_types.TraversalMode.PROXIMITY,
        revisit_rivers=True,
    )

  def _validate_traversal(self, stick_figure: sf_lib.StickFigure):
    """Validates that all sticks in the stick figure were traversed."""
    unplaced_sticks = {s.name for s in stick_figure.children} - {
        s.name for s in self._sticks
    }
    if unplaced_sticks:
      raise ValueError(
          'Not all sticks in the stick figure were traversed:'
          f' {unplaced_sticks}'
      )

  def compute_from_sf_traversal(self, stick_figure: sf_lib.StickFigure):
    """Computes the layout from a stick figure traversal."""
    for stick, next_stick in itertools.pairwise(
        itertools.chain(self._traversal(stick_figure), [None])
    ):
      assert stick is not None
      self._add_sacrificial_flap(stick, next_stick=None)
      self.add_stick(stick)
      if next_stick is not None:
        self._add_sacrificial_flap(stick, next_stick=next_stick)

    self._validate_traversal(stick_figure)

  @property
  def req_height(self) -> int:
    """Minimum height of the grid to contain all flaps."""
    return self._y_offsets[-1] - self._sticks[-1].length

  @property
  def req_width(self) -> int:
    return max(
        r_width + s.length
        for r_width, s in zip(self._river_margins, self._sticks)
    )

  def _place_flaps(
      self, tracker: utils_tracker.CreasePatternTracker, target_width: int
  ):
    """Places all flap polygons onto the tracker."""
    for y, river_margin, stick, sf_info in zip(
        self._y_offsets, self._river_margins, self._sticks, self._sf_infos
    ):
      if stick.is_river:
        continue
      height = 2 * stick.length
      width = target_width - river_margin
      if width < stick.length:
        raise ValueError(f'Target width is too small for stick {stick.name}.')
      tracker.add_polygon(
          stick.name,
          placement=packing_types.PolygonPlacement.from_grid_coords(
              offset=(-width, y),
              size=(2 * width, height),
              grid_size=tracker.grid_size,
              river_sf_info=sf_info,
          ),
      )

  def _place_rivers(self, tracker: utils_tracker.CreasePatternTracker):
    """Places rivers via contour hugging around existing flaps."""
    placed_rivers: set[str] = set()
    negative_river_margins = [-rm for rm in self._river_margins]
    for _, y, stick in sorted(
        zip(negative_river_margins, self._y_offsets, self._sticks)
    ):
      if not stick.is_river:
        continue
      if stick.name in placed_rivers:
        continue
      placed_rivers.add(stick.name)
      river = river_lib.HuggingRiver.from_contour(
          grid_size=tracker.grid_size,
          width=stick.length,
          occupancy_grid=tracker.occupancy_grid,
          start_cell=(y + stick.length - 1, 0),
          hug_side=river_lib.HugSide.RIGHT,
      )
      tracker.add_river(stick.name, river)

  def make_tracker(self) -> utils_tracker.CreasePatternTracker:
    """Returns a CreasePatternTracker with all flaps and rivers placed."""
    tracker = utils_tracker.CreasePatternTracker(grid_size=self.req_height)
    try:
      self._place_flaps(tracker, tracker.grid_size)
      self._place_rivers(tracker)
      return tracker
    except Exception as e:
      raise TrackerError(str(e), tracker) from e


def _is_axis_linear(stick_figure: sf_lib.StickFigure) -> bool:
  """Returns whether the symmetry axis is linear. (Not branched.)"""
  symmetry_joints = collections.Counter()
  for stick_name in stick_figure.symmetry_axis:
    stick = stick_figure[stick_name]
    symmetry_joints[stick.start] += 1
    symmetry_joints[stick.end] += 1
  return all(c <= 2 for c in symmetry_joints.values())


@dataclasses.dataclass
class _SymmetricStackLayout(_AsymmetricStackLayout):
  """Stacking layout for symmetric stick figures."""

  _symmetry_axis: frozenset[str] = dataclasses.field(
      default_factory=frozenset, init=False
  )
  _on_axis: list[bool] = dataclasses.field(default_factory=list, init=False)
  _axis_rivers: dict[str, int] = dataclasses.field(
      default_factory=dict, init=False
  )

  def _is_axis_stick(self, stick: stick_lib.Stick) -> bool:
    return stick.name in self._symmetry_axis

  def _add_river(self, stick: stick_lib.Stick):
    """Adds a river stick to the layout, updating y-offsets and river stack."""
    super()._add_river(stick)
    if self._is_axis_stick(stick) and self._river_stack == [stick]:
      assert (
          stick.name not in self._axis_rivers
      ), f'Axis river {stick.name} already added: {self._axis_rivers}'
      self._axis_rivers[stick.name] = self._y_offsets[-2]
      self._river_stack.pop()

  def add_stick(
      self,
      stick: stick_lib.Stick,
      sf_info: packing_types.RiverSfInfo | None = None,
  ):
    """Adds a stick to the layout."""
    self._on_axis.append(self._is_axis_stick(stick))
    super().add_stick(stick, sf_info=sf_info)

  def _traversal(self, stick_figure: sf_lib.StickFigure):
    (
        start_stick,
        _,
    ) = _identify_symmetric_traversal_bounds(stick_figure)
    symmetry_joints = stick_figure.symmetry_joints
    start_joint_name = max(
        (start_stick.start, start_stick.end),
        key=lambda j_name: j_name in symmetry_joints,
    )

    visit_counts = collections.Counter()
    symmetric_half = stick_figure.get_symmetric_half()
    for stick in traversal.packing_traversal(
        symmetric_half,
        packing_types.TraversalMode.PROXIMITY,
        start_stick_name=start_stick.name,
        start_joint_name=start_joint_name,
        revisit_rivers=True,
    ):
      if stick.name in self._symmetry_axis and visit_counts[stick.name] > 0:
        break
      yield stick
      visit_counts[stick.name] += 1

  def _validate_traversal(self, stick_figure: sf_lib.StickFigure):
    """Validates that all sticks in the stick figure were traversed."""
    symmetric_half = stick_figure.get_symmetric_half()
    unplaced_sticks = {s.name for s in symmetric_half.children} - {
        s.name for s in self._sticks
    }
    if unplaced_sticks:
      raise ValueError(
          'Not all sticks in the (symmetric half of the) stick figure were'
          f' traversed: {unplaced_sticks}'
      )

  def compute_from_sf_traversal(self, stick_figure: sf_lib.StickFigure):
    """Computes the layout from traversing a symmetric half of the stick figure."""
    if not stick_figure.is_symmetric_tree:
      raise ValueError('Symmetric layout requires a symmetric stick figure.')
    if not _is_axis_linear(stick_figure):
      raise ValueError(
          'Symmetric layout requires a non-branched symmetry axis.'
      )

    stick_figure = stick_figure.straighten_symmetry_axis()
    self._symmetry_axis = frozenset(stick_figure.symmetry_axis)

    super().compute_from_sf_traversal(stick_figure)

  @property
  def req_height(self) -> int:
    """Minimum height of the grid to contain all flaps. Must be even."""
    height = super().req_height
    if height % 2 != 0:
      height += 1
    return height

  def _place_flaps(
      self, tracker: utils_tracker.CreasePatternTracker, target_width: int
  ):
    """Places all flap polygons onto the tracker."""
    for y, river_margin, stick, on_axis, sf_info in zip(
        self._y_offsets,
        self._river_margins,
        self._sticks,
        self._on_axis,
        self._sf_infos,
    ):
      if stick.is_river:
        continue
      if on_axis:
        assert (
            river_margin == 0
        ), f'Symmetric flap is blocked by a river: {stick.name}, {river_margin}'
        tracker.add_polygon(
            stick.name,
            placement=packing_types.PolygonPlacement.from_grid_coords(
                offset=(0, y),
                size=(tracker.grid_size, stick.length * 2),
                grid_size=tracker.grid_size,
                river_sf_info=sf_info,
            ),
        )
      else:
        height = 2 * stick.length
        width = target_width - river_margin
        tracker.add_polygon(
            stick.name,
            placement=packing_types.PolygonPlacement.from_grid_coords(
                offset=(-width, y),
                size=(2 * width, height),
                grid_size=tracker.grid_size,
                river_sf_info=sf_info,
            ),
        )

  def _place_rivers(self, tracker: utils_tracker.CreasePatternTracker):
    """Places rivers via contour hugging around existing flaps."""
    for river_name, offset in self._axis_rivers.items():
      stick = next(s for s in self._sticks if s.name == river_name)
      river = river_lib.River(
          width=stick.length,
          offset=offset,
          orientation=river_lib.RiverOrientation.HORIZONTAL,
          grid_size=tracker.grid_size,
      )
      tracker.add_river(river_name, river)

    placed_rivers: set[str] = set(self._axis_rivers.keys())
    negative_river_margins = [-rm for rm in self._river_margins]
    for _, y, stick in sorted(
        zip(negative_river_margins, self._y_offsets, self._sticks)
    ):
      if not stick.is_river:
        continue
      if stick.name in placed_rivers:
        continue
      placed_rivers.add(stick.name)
      river = river_lib.HuggingRiver.from_contour(
          grid_size=tracker.grid_size,
          width=stick.length,
          occupancy_grid=tracker.occupancy_grid,
          start_cell=(y + stick.length - 1, 0),
          hug_side=river_lib.HugSide.RIGHT,
      )
      tracker.add_river(stick.name, river)

  def make_tracker(self) -> utils_tracker.CreasePatternTracker:
    """Returns a CreasePatternTracker with all flaps and rivers placed."""
    tracker = utils_tracker.CreasePatternTracker(grid_size=self.req_height)
    try:
      self._place_flaps(tracker, tracker.grid_size // 2)
      self._place_rivers(tracker)
    except Exception as e:
      raise TrackerError(str(e), tracker) from e
    return tracker


def _identify_symmetric_traversal_bounds(
    stick_figure: sf_lib.StickFigure,
) -> tuple[stick_lib.Stick, stick_lib.Stick]:
  """Identifies the start and end sticks for symmetric layout traversal."""
  symmetry_axis = stick_figure.symmetry_axis
  if not symmetry_axis:
    raise ValueError('Symmetric stick figure has no symmetry axis.')
  symmetric_half = stick_figure.get_symmetric_half()

  non_axis_stick = next(
      (s for s in symmetric_half.children if s.name not in symmetry_axis), None
  )
  if non_axis_stick is None:
    logging.warning('Symmetric stick figure has no non-axis sticks.')
    return stick_figure[symmetry_axis[0]], stick_figure[symmetry_axis[-1]]

  n_consecutive_symmetric = 0
  end_stick = non_axis_stick
  prev_stick = None
  for start_stick in traversal.packing_traversal(
      symmetric_half,
      packing_types.TraversalMode.PROXIMITY,
      start_stick_name=non_axis_stick.name,
      start_joint_name=non_axis_stick.start,
      revisit_rivers=True,
  ):
    if n_consecutive_symmetric >= len(symmetry_axis):
      assert prev_stick is not None
      if prev_stick.is_flap:
        return prev_stick, end_stick
      else:
        return start_stick, end_stick

    if start_stick.name in symmetry_axis:
      if n_consecutive_symmetric == 0 and start_stick.is_flap:
        end_stick = start_stick
      n_consecutive_symmetric += 1
    else:
      end_stick = start_stick
      n_consecutive_symmetric = 0
    prev_stick = start_stick

  if n_consecutive_symmetric >= len(symmetry_axis):
    assert prev_stick is not None
    if prev_stick.is_flap:
      return prev_stick, end_stick
    else:
      return non_axis_stick, end_stick
  else:
    raise ValueError(
        f'No symmetric start stick found: {stick_figure.symmetry_axis}'
    )


def _create_tracker_with_stacking(
    stick_figure: sf_lib.StickFigure,
    force_asymmetric: bool = False,
    config: StackLayoutConfig = StackLayoutConfig(),
) -> tuple[utils_tracker.CreasePatternTracker, bool]:
  """Packs a stick figure into a CreasePatternTracker using stack packing."""
  is_symmetric = stick_figure.is_symmetric_tree and not force_asymmetric
  try:
    if is_symmetric:
      layout = _SymmetricStackLayout(config=config)
      layout.compute_from_sf_traversal(stick_figure)
      tracker = layout.make_tracker()
      utils_packing_svg.mirror_symmetric_placements(
          tracker, tracker.grid_size, stick_figure
      )
      return tracker, is_symmetric
  except ValueError as e:
    if not config.fallback_to_asymmetric:
      raise e
    logging.warning(e)
    logging.warning(
        'Symmetric packing failed, falling back to asymmetric packing.'
    )

  layout = _AsymmetricStackLayout(config=config)
  layout.compute_from_sf_traversal(stick_figure)
  tracker = layout.make_tracker()
  return tracker, False


def _identify_sacrificial_flaps(
    tracker: utils_tracker.CreasePatternTracker,
) -> list[packing_types.SacrificialFlap]:
  """Constructs SacrificialFlap objects from a stacking tracker."""
  sacrificial_flaps = []
  for polygon_name, placement in tracker.packed_polygons.items():
    sf_info = placement.river_sf_info
    if sf_info is None:
      continue

    shifted_element_name = sf_info.river_name
    shifted_element = tracker.get_element(shifted_element_name)
    if shifted_element is None:
      raise ValueError(
          f'Sacrificial flap {polygon_name} references missing element'
          f' {shifted_element_name}'
      )

    match sf_info.river_side:
      case 'top':
        crimp_direction = 'bottom'
      case 'bottom':
        crimp_direction = 'top'
      case _:
        raise ValueError(
            f'river_side should be top or bottom: {sf_info.river_side}'
        )

    sacrificial_flaps.append(
        packing_types.SacrificialFlap(
            polygon_name=polygon_name,
            placement=placement,
            shifted_element_name=shifted_element_name,
            orientation='horizontal',
            shifted_element=shifted_element,
            crimp_direction=crimp_direction,
        )
    )
  return sacrificial_flaps


def pack_stick_figure_with_stacking(
    stick_figure: sf_lib.StickFigure,
    force_asymmetric: bool = False,
    stacking_config: StackLayoutConfig = StackLayoutConfig(),
) -> packing_output.PackingOutput:
  """Packs a stick figure using stack packing and returns a PackingOutput."""
  tracker, is_symmetric = _create_tracker_with_stacking(
      stick_figure, force_asymmetric, stacking_config
  )
  unused_area = tracker.grid_size**2 - tracker.occupancy_grid.sum()
  config = config_lib.PackingConfig(
      enforce_proximity_constraints=True,
      local_tiling_config=None,
  )

  result = utils_solver.create_packing_output_from_tiling_solution(
      tracker,
      tracker.grid_size,
      stick_figure,
      details=debug_types.TilingDetails(
          grid_size=tracker.grid_size,
          is_symmetric=is_symmetric,
          perfect_tiling_found=unused_area == 0,
          unused_area=unused_area,
          reason='Deserialized from tracker state.',
      ),
      config=config,
  )

  if stacking_config.level_shifters:
    sfs = _identify_sacrificial_flaps(tracker)
    if sfs:
      result = result.model_copy(
          update={
              'sacrificial_flaps': sfs,
          }
      )
  return result
