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

"""Stores configuration options for the packing solver."""

from collections.abc import Mapping
import dataclasses
import enum
import typing
from typing import Any, TypedDict

from . import types


class _ClassOrInstanceMethod:
  """Descriptor allowing a method to be called on either a class or an instance."""

  def __init__(self, func: Any):
    self.func = func

  def __get__(self, obj: Any, cls: Any = None) -> Any:
    if obj is not None:
      return lambda *args, **kwargs: self.func(obj, *args, **kwargs)
    return lambda *args, **kwargs: self.func(cls, *args, **kwargs)


class LocalTilingSearchType(enum.StrEnum):
  """The type of search to use if multiple tiling solutions seem possible.

  Attributes:
    SKIP: Skips the local tiling search - misses solutions. Used for debugging.
    BRUTE_FORCE: Exhaustively tries all solutions but very slow.
    BACKTRACK: Uses a backtracking search. This should be the default.
  """

  SKIP = 'skip'
  BRUTE_FORCE = 'brute_force'
  BACKTRACK = 'backtrack'


class LocalTilingConfigDict(TypedDict):
  """A dictionary representation of LocalTilingConfig."""

  search_type: LocalTilingSearchType
  disable_wide_central_flaps: bool
  use_river_tiling: bool


@dataclasses.dataclass(frozen=True, kw_only=True)
class LocalTilingConfig:
  """Configuration for the local tiling solver.

  Attributes:
    search_type: Algorithm to use for searching alternative possibilities.
    disable_wide_central_flaps: Whether to allow central flap expansions (other
      than horizontally from the symmetry axis)
    use_river_tiling: Whether to use river tiling.
  """

  search_type: LocalTilingSearchType = LocalTilingSearchType.BACKTRACK
  disable_wide_central_flaps: bool = True
  use_river_tiling: bool = False

  def __post_init__(self):
    if self.use_river_tiling:
      raise NotImplementedError('River tiling is not yet supported.')

  @classmethod
  def from_dict(cls, data: Mapping[str, Any]) -> 'LocalTilingConfig':
    valid_fields = {f.name for f in dataclasses.fields(cls) if f.init}
    unknown = set(data.keys()) - valid_fields
    if unknown:
      raise ValueError(f'Unknown LocalTilingConfig fields: {sorted(unknown)}')
    kwargs = dict(data)
    if 'search_type' in kwargs and kwargs['search_type'] is not None:
      kwargs['search_type'] = LocalTilingSearchType(kwargs['search_type'])
    return cls(**kwargs)


class PackingConfigDict(TypedDict):
  """A dictionary representation of PackingConfig."""

  enforce_proximity_constraints: bool
  local_tiling_config: LocalTilingConfigDict | None
  max_delta_combinations: int
  traversal_mode: types.TraversalMode
  start_stick_name: str | None
  start_with_hugging_river: bool
  use_level_shifter: bool
  use_l_shaped_level_shifter: bool
  exhaust_solutions: bool
  easy_mode: bool
  remove_central_crease: bool
  include_straight_rivers: bool
  include_lshape_rivers: bool
  y_ridge_at_border: bool
  river_backtracking: bool
  legacy_iteration_order: bool
  reject_degenerate_hugging_rivers: bool
  star_hub_rivers: bool
  symmetry_line_obstacles: bool
  prune_partial_border_overhang: bool
  stretch_intermediate_pocket_flaps: bool
  memoize_pocket_tiling: bool
  reject_provably_unsolvable_packings: bool


@dataclasses.dataclass(frozen=True, kw_only=True)
class PackingConfig:
  """Configuration for the packing solver.

  Attributes:
    local_tiling_config: Configuration for the local tiling solver or None to
      disable local tiling.
    max_delta_combinations: Limit on the number of delta combinations try when
      using non-local tiling.
    enforce_proximity_constraints: If True, enforce distance (EQUAL 0)
      constraints between consecutive flaps in the plan.
    traversal_mode: The traversal mode to use for packing_traversal.
    start_stick_name: If provided, start traversal from this stick.
    start_with_hugging_river: If True, pack flaps in the first river pocket
      before river solving.
    use_level_shifter: If True, use level shifter logic for flap dimension
      calculation.
    use_l_shaped_level_shifter: If True, single width>1 sticks are left for
      L-shaped level shifter handling. If False, they use nested decomposition.
    exhaust_solutions: If True, exhaust all possible solutions instead of
      finding diverse ones.
    easy_mode: If True, restrict flap placement to border-only centers and skip
      all tiling phases.
    remove_central_crease: If True, reserve axis columns during packing for
      central crease diagonals. Non-axis flaps cannot touch the symmetry axis.
    include_straight_rivers: Whether to include straight rivers in the river
      solver search.
    include_lshape_rivers: Whether to include L-shaped rivers in the river
      solver search.
    y_ridge_at_border: Whether to apply Y-ridges when a rectangle touches the
      grid border.
    river_backtracking: Whether downstream leaf-pocket failures reject a river
      candidate and trigger local river backtracking rather than counting toward
      `max_solutions`.
    legacy_iteration_order: Whether to use legacy `set`-based candidate
      deduplication and unordered set traversal instead of insertion-order
      (`dict.fromkeys` / `list`) candidate ordering, matching the baseline
      reference search order.
    reject_degenerate_hugging_rivers: Whether to filter out hugging river
      candidates whose primary contour makes a 180-degree hairpin U-turn or
      whose consecutive layers diverge around opposite sides of a flap.
    star_hub_rivers: Whether multi-river star joints (>= 3 boundary rivers
      meeting at a hub joint) pack without requiring pairwise geometric
      adjacency between all boundary rivers separated by intermediate flaps.
    symmetry_line_obstacles: Whether off-axis rivers treat symmetry-line flap
      allocations as obstacles during river candidate generation.
    prune_partial_border_overhang: Whether to prune flap placements with partial
      border overhang where center lies strictly inside the paper.
    stretch_intermediate_pocket_flaps: Whether intermediate-pocket flaps yield
      horizontal axis-aligned and border-stretching variants.
    memoize_pocket_tiling: Whether to memoize intermediate pocket flap tiling
      solutions and failure sets during river backtracking.
    reject_provably_unsolvable_packings: Whether to reject candidate packings
      that violate flat-foldability invariants (<10ms solvability check).
    recovery: If True, enables recovery logic.
  """

  enforce_proximity_constraints: bool = True
  local_tiling_config: LocalTilingConfig | None = LocalTilingConfig()
  max_delta_combinations: int = 1_000_000
  traversal_mode: types.TraversalMode = types.TraversalMode.RIVER_PRIORITY
  start_stick_name: str | None = None
  start_with_hugging_river: bool = False
  use_level_shifter: bool = False
  use_l_shaped_level_shifter: bool = True
  exhaust_solutions: bool = False
  easy_mode: bool = False
  remove_central_crease: bool = False
  include_straight_rivers: bool = True
  include_lshape_rivers: bool = True
  y_ridge_at_border: bool = True
  river_backtracking: bool = False
  legacy_iteration_order: bool = True
  reject_degenerate_hugging_rivers: bool = False
  star_hub_rivers: bool = False
  symmetry_line_obstacles: bool = False
  prune_partial_border_overhang: bool = False
  stretch_intermediate_pocket_flaps: bool = False
  memoize_pocket_tiling: bool = False
  reject_provably_unsolvable_packings: bool = False
  recovery: bool = False

  @_ClassOrInstanceMethod
  def with_recovery(  # pylint: disable=no-self-argument
      self_or_cls: Any, **overrides: Any
  ) -> 'PackingConfig':
    """Returns a PackingConfig with extended recovery and backtracking enabled."""
    if isinstance(self_or_cls, PackingConfig):
      opts: dict[str, Any] = {
          'river_backtracking': True,
          'legacy_iteration_order': False,
          'reject_degenerate_hugging_rivers': True,
          'star_hub_rivers': True,
          'memoize_pocket_tiling': True,
          'recovery': True,
      }
      opts.update(overrides)
      return dataclasses.replace(self_or_cls, **opts)
    defaults = {
        'river_backtracking': True,
        'legacy_iteration_order': False,
        'reject_degenerate_hugging_rivers': True,
        'star_hub_rivers': True,
        'memoize_pocket_tiling': True,
        'recovery': True,
    }
    defaults.update(overrides)
    return self_or_cls(**defaults)

  def __post_init__(self):
    if self.max_delta_combinations > 1_000_000:
      raise ValueError(
          'max_delta_combinations must be less than or equal to 1,000,000.'
      )
    if self.easy_mode and not self.start_with_hugging_river:
      raise ValueError(
          'start_with_hugging_river must be True when easy_mode is True.'
      )
    if self.easy_mode and self.traversal_mode != types.TraversalMode.PROXIMITY:
      raise ValueError(
          'traversal_mode must be PROXIMITY when easy_mode is True.'
      )
    if (
        not self.include_straight_rivers
        and not self.include_lshape_rivers
        and not self.start_with_hugging_river
    ):
      raise ValueError(
          'start_with_hugging_river must be True when both'
          ' include_straight_rivers and include_lshape_rivers are False.'
      )

  def to_dict(self) -> PackingConfigDict:
    local_tiling_config_dict = None
    if self.local_tiling_config:
      local_tiling_config_dict = typing.cast(
          LocalTilingConfigDict, dataclasses.asdict(self.local_tiling_config)
      )
    return PackingConfigDict(
        enforce_proximity_constraints=self.enforce_proximity_constraints,
        local_tiling_config=local_tiling_config_dict,
        max_delta_combinations=self.max_delta_combinations,
        traversal_mode=self.traversal_mode,
        start_stick_name=self.start_stick_name,
        start_with_hugging_river=self.start_with_hugging_river,
        use_level_shifter=self.use_level_shifter,
        use_l_shaped_level_shifter=self.use_l_shaped_level_shifter,
        exhaust_solutions=self.exhaust_solutions,
        easy_mode=self.easy_mode,
        remove_central_crease=self.remove_central_crease,
        include_straight_rivers=self.include_straight_rivers,
        include_lshape_rivers=self.include_lshape_rivers,
        y_ridge_at_border=self.y_ridge_at_border,
        river_backtracking=self.river_backtracking,
        legacy_iteration_order=self.legacy_iteration_order,
        reject_degenerate_hugging_rivers=self.reject_degenerate_hugging_rivers,
        star_hub_rivers=self.star_hub_rivers,
        symmetry_line_obstacles=self.symmetry_line_obstacles,
        prune_partial_border_overhang=self.prune_partial_border_overhang,
        stretch_intermediate_pocket_flaps=self.stretch_intermediate_pocket_flaps,
        memoize_pocket_tiling=self.memoize_pocket_tiling,
        reject_provably_unsolvable_packings=self.reject_provably_unsolvable_packings,
    )

  @classmethod
  def from_dict(cls, data: Mapping[str, Any]) -> 'PackingConfig':
    """Constructs a PackingConfig from a dictionary."""
    valid_fields = {f.name for f in dataclasses.fields(cls) if f.init}
    unknown = set(data.keys()) - valid_fields
    if unknown:
      raise ValueError(f'Unknown PackingConfig fields: {sorted(unknown)}')
    kwargs: dict[str, Any] = dict(data)
    if 'traversal_mode' in kwargs and kwargs['traversal_mode'] is not None:
      kwargs['traversal_mode'] = types.TraversalMode(kwargs['traversal_mode'])
    if 'local_tiling_config' in kwargs and isinstance(
        kwargs['local_tiling_config'], Mapping
    ):
      kwargs['local_tiling_config'] = LocalTilingConfig.from_dict(
          kwargs['local_tiling_config']
      )
    return cls(**kwargs)
