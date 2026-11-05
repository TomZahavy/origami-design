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

"""Pre-solve solvability checks for box-pleating crease patterns.

Provides fast O(V) mathematical checks to determine if a packed crease pattern
is provably unsolvable before invoking the full combinatorial search solver.
"""

from collections.abc import Iterator
import dataclasses
from typing import Any

from bp_pipeline import bus
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import crease_pattern
from bp_pipeline.crease_pattern import point
from bp_pipeline.solving import hinges


@dataclasses.dataclass(frozen=True)
class SolvabilityResult:
  """Result of a pre-solve solvability check."""

  is_solvable: bool
  reason: str | None = None


def check_solvability(
    packed_cp: bus.PackedCreasePattern | crease_pattern.CreasePattern,
) -> SolvabilityResult:
  """Fast O(V) check for mathematical solvability of a packed crease pattern.

  Evaluates geometric sheet boundaries, Kawasaki vertex degree parity,
  Maekawa theorem discrepancy bounds, and pleat-ridge alignment invariants.

  Args:
    packed_cp: A PackedCreasePattern bus record or CreasePattern to check.

  Returns:
    SolvabilityResult indicating if the pattern can be solved, with an
    actionable failure explanation if provably unsolvable.
  """
  candidate_hinge_endpoints: set[tuple[int, int]] = set()
  candidate_hinge_counts: dict[tuple[int, int], int] = {}

  if isinstance(packed_cp, bus.PackedCreasePattern):
    grid_size = packed_cp.grid_size
    cp = packed_cp.creases

    # Check flap boundary and center validity against grid dimensions.
    for flap_id, flap in packed_cp.flaps.items():
      rect = flap.rect
      min_x, min_y = rect.x, rect.y
      max_x, max_y = rect.x + rect.width, rect.y + rect.height
      if min_x < 0 or min_y < 0 or max_x > grid_size or max_y > grid_size:
        return SolvabilityResult(
            is_solvable=False,
            reason=(
                f'Flap {flap_id} rect ({min_x}, {min_y}) - '
                f'({max_x}, {max_y}) exceeds sheet bounds [0, {grid_size}]'
            ),
        )
      for center in flap.circle_centers:
        if not (0 <= center.x <= grid_size and 0 <= center.y <= grid_size):
          return SolvabilityResult(
              is_solvable=False,
              reason=(
                  f'Flap {flap_id} center ({center.x}, {center.y}) '
                  f'outside sheet bounds [0, {grid_size}]'
              ),
          )

    # Index candidate hinges by integer lattice endpoint.
    for h in packed_cp.hinges:
      p1_key = (h.segment.p1.x, h.segment.p1.y)
      p2_key = (h.segment.p2.x, h.segment.p2.y)
      candidate_hinge_endpoints.add(p1_key)
      candidate_hinge_endpoints.add(p2_key)
      candidate_hinge_counts[p1_key] = candidate_hinge_counts.get(p1_key, 0) + 1
      candidate_hinge_counts[p2_key] = candidate_hinge_counts.get(p2_key, 0) + 1
    has_hinge_metadata = True
  elif isinstance(packed_cp, crease_pattern.CreasePattern):
    cp = packed_cp
    grid_size = cp.grid_size if cp.grid_size is not None else 1
    has_hinge_metadata = False
  else:
    return SolvabilityResult(
        is_solvable=False,
        reason=f'Unsupported input type: {type(packed_cp).__name__}',
    )

  if grid_size <= 0:
    return SolvabilityResult(
        is_solvable=False,
        reason=f'Invalid grid size {grid_size} <= 0',
    )

  # Check interior vertices for Kawasaki parity and Maekawa bounds.
  tol = point.DEFAULT_TOLERANCE
  scale = float(grid_size)

  for v in cp.vertices:
    pt = v.point
    # Skip boundary vertices (theorems apply only to internal vertices).
    if pt.x <= tol or pt.x >= 1.0 - tol or pt.y <= tol or pt.y >= 1.0 - tol:
      continue

    lattice_key = (round(pt.x * scale), round(pt.y * scale))
    h_count = (
        candidate_hinge_counts.get(lattice_key, 0)
        if has_hinge_metadata
        else 999
    )

    mountains = sum(c.fold == crease.Fold.MOUNTAIN for c in v.creases)
    valleys = sum(c.fold == crease.Fold.VALLEY for c in v.creases)
    fixed_degree = len(v.creases)

    # Kawasaki Parity: Interior vertices must have even degree in flat folding.
    # If odd and no candidate hinges can reach this vertex, it is impossible.
    if has_hinge_metadata and h_count == 0:
      if fixed_degree % 2 != 0:
        return SolvabilityResult(
            is_solvable=False,
            reason=(
                f'Interior vertex at ({pt.x:.4f}, {pt.y:.4f}) has odd degree '
                f'{fixed_degree} with 0 candidate hinges '
                '(Kawasaki parity violation)'
            ),
        )

      # Maekawa Theorem: Fully fixed interior vertices must satisfy |M - V| = 2.
      if abs(mountains - valleys) != 2:
        return SolvabilityResult(
            is_solvable=False,
            reason=(
                f'Interior vertex at ({pt.x:.4f}, {pt.y:.4f}) has |M - V| = '
                f'{abs(mountains - valleys)} != 2 with 0 available creases '
                '(Maekawa violation)'
            ),
        )

      if not v.vertex_.check_foldability_constraints(check_maekawa=True):
        return SolvabilityResult(
            is_solvable=False,
            reason=(
                f'Interior vertex at ({pt.x:.4f}, {pt.y:.4f}) violates '
                'flat-foldability bounds with 0 available creases'
            ),
        )

    # Discrepancy Bound: Maekawa gap exceeds max possible crease additions.
    # Each added hinge can adjust M - V by at most 1.
    maekawa_gap = abs(abs(mountains - valleys) - 2)
    max_adjustment = h_count
    if has_hinge_metadata and maekawa_gap > max_adjustment:
      return SolvabilityResult(
          is_solvable=False,
          reason=(
              f'Interior vertex at ({pt.x:.4f}, {pt.y:.4f}) has Maekawa gap '
              f'{maekawa_gap} > max possible adjustment {max_adjustment}'
          ),
      )

  # Check pleat-ridge misaligned intersections.
  unassigned_pleats = [
      c for c in cp.creases if c.is_horizontal or c.is_vertical
  ]
  ridges = [
      c
      for c in cp.creases
      if c.fold in (crease.Fold.MOUNTAIN, crease.Fold.VALLEY)
      and c.fold != crease.Fold.BORDER
      and not (c.is_horizontal or c.is_vertical)
  ]
  if unassigned_pleats and ridges:
    misaligned = False
    for pleat in unassigned_pleats:
      for ridge in ridges:
        v = pleat.vertex_with_crease(ridge)
        if v and not (v.isclose(ridge.midpoint) or ridge.is_tip(v)):
          misaligned = True
          break
      if misaligned:
        break
    if misaligned:
      return SolvabilityResult(
          is_solvable=False,
          reason=(
              'Axial pleat has misaligned non-midpoint intersection with'
              ' fixed ridge'
          ),
      )

  if _has_opposing_incompatible_pleats(cp):
    return SolvabilityResult(
        is_solvable=False,
        reason=(
            'Opposing axial pleats trapped in a ridge-free corridor with'
            ' incompatible parity'
        ),
    )

  return SolvabilityResult(is_solvable=True)


def is_provably_unsolvable(
    packed_cp: bus.PackedCreasePattern | crease_pattern.CreasePattern,
) -> bool:
  """Fast O(V) predicate returning True if a packing is mathematically unsolvable.

  Designed for use in packer solution callbacks and pre-solve rejection filters
  to discard invalid packings in <10ms without invoking the full search solver.

  Args:
    packed_cp: A PackedCreasePattern bus record or CreasePattern.

  Returns:
    True if the pattern is provably unsolvable; False if it is potentially
    solvable.
  """
  return not check_solvability(packed_cp).is_solvable


def _has_opposing_incompatible_pleats(cp: crease_pattern.CreasePattern) -> bool:
  """Checks for opposing incompatible pleats without an intervening ridge."""
  vertical_pleats = {}
  horizontal_pleats = {}
  ridges = []

  for c in cp.creases:
    if c.fold not in (crease.Fold.MOUNTAIN, crease.Fold.VALLEY):
      continue
    if c.is_vertical:
      vertical_pleats.setdefault(round(c.p1.x, 4), []).append(c)
    elif c.is_horizontal:
      horizontal_pleats.setdefault(round(c.p1.y, 4), []).append(c)
    else:
      ridges.append(c)

  for x, pleats in vertical_pleats.items():
    if len(pleats) < 2:
      continue
    pleats.sort(key=lambda c: min(c.p1.y, c.p2.y))
    for i in range(len(pleats) - 1):
      p1 = pleats[i]
      p2 = pleats[i + 1]
      if p1.fold != p2.fold:
        y1_max = max(p1.p1.y, p1.p2.y)
        y2_min = min(p2.p1.y, p2.p2.y)
        if y1_max < y2_min + 1e-4:
          intersected = False
          for r in ridges:
            if min(r.p1.x, r.p2.x) - 1e-4 <= x <= max(r.p1.x, r.p2.x) + 1e-4:
              if abs(r.p1.x - r.p2.x) > 1e-4:
                t = (x - r.p1.x) / (r.p2.x - r.p1.x)
                y_int = r.p1.y + t * (r.p2.y - r.p1.y)
                if y1_max - 1e-4 <= y_int <= y2_min + 1e-4:
                  intersected = True
                  break
          if not intersected:
            return True

  for y, pleats in horizontal_pleats.items():
    if len(pleats) < 2:
      continue
    pleats.sort(key=lambda c: min(c.p1.x, c.p2.x))
    for i in range(len(pleats) - 1):
      p1 = pleats[i]
      p2 = pleats[i + 1]
      if p1.fold != p2.fold:
        x1_max = max(p1.p1.x, p1.p2.x)
        x2_min = min(p2.p1.x, p2.p2.x)
        if x1_max < x2_min + 1e-4:
          intersected = False
          for r in ridges:
            if min(r.p1.y, r.p2.y) - 1e-4 <= y <= max(r.p1.y, r.p2.y) + 1e-4:
              if abs(r.p1.y - r.p2.y) > 1e-4:
                t = (y - r.p1.y) / (r.p2.y - r.p1.y)
                x_int = r.p1.x + t * (r.p2.x - r.p1.x)
                if x1_max - 1e-4 <= x_int <= x2_min + 1e-4:
                  intersected = True
                  break
          if not intersected:
            return True
  return False


def score_packing_solvability(
    packed_cp: bus.PackedCreasePattern | crease_pattern.CreasePattern,
) -> tuple[bool, int, int]:
  """Scores a packed CP to rank solvable candidates ahead of unsolvable ones.

  Args:
    packed_cp: A PackedCreasePattern bus record or CreasePattern.

  Returns:
    (is_unsolvable, unassigned_pleat_count, conflict_count)
  """
  res = check_solvability(packed_cp)
  cp = (
      packed_cp.creases
      if isinstance(packed_cp, bus.PackedCreasePattern)
      else packed_cp
  )
  unassigned_pleat_count = sum(
      1
      for c in cp.creases
      if (c.is_horizontal or c.is_vertical) and c.fold == crease.Fold.HINGE
  )
  conflict_count = 0
  tol = point.DEFAULT_TOLERANCE
  for v in cp.vertices:
    pt = v.point
    if pt.x <= tol or pt.x >= 1.0 - tol or pt.y <= tol or pt.y >= 1.0 - tol:
      continue
    mountains = sum(c.fold == crease.Fold.MOUNTAIN for c in v.creases)
    valleys = sum(c.fold == crease.Fold.VALLEY for c in v.creases)
    if abs(mountains - valleys) != 2:
      conflict_count += 1
  return (not res.is_solvable, unassigned_pleat_count, conflict_count)


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class BankabilityResult:
  """Structured result of an is_bankable check."""

  reasons: tuple[str, ...] = ()
  first_passing_config: hinges.SolverConfig | None = None

  @property
  def ok(self) -> bool:
    """Returns True if there are zero bankability failure reasons."""
    return not self.reasons


def solve_cascade(
    base: hinges.SolverConfig | None = None,
    *,
    grid_size: int | None = None,
    stage: str = 'all',
) -> Iterator[hinges.SolverConfig]:
  """Yields solver configurations in the canonical primary-then-fallback order.

  Args:
    base: An optional template SolverConfig to inherit non-cascade fields from.
    grid_size: Optional grid size to override on generated configs.
    stage: One of 'all', 'primary', or 'fallback'.
  """
  g = grid_size if base is None else (base.grid_size or grid_size)

  def _make(
      *,
      remove_central_crease: bool,
      hinges_from_stick_figure: bool,
      up_down_method: str = 'flaps_down',
      disallow_trapping_edge_flaps: bool = False,
      allow_misaligned_symmetric_hinges: bool = False,
      max_steps: int | None = None,
  ) -> hinges.SolverConfig:
    if base is None:
      return hinges.SolverConfig(
          grid_size=g,
          remove_central_crease=remove_central_crease,
          hinges_from_stick_figure=hinges_from_stick_figure,
          up_down_method=up_down_method,
          disallow_trapping_edge_flaps=disallow_trapping_edge_flaps,
          allow_misaligned_symmetric_hinges=allow_misaligned_symmetric_hinges,
          max_steps=max_steps if max_steps is not None else 8000,
      )
    overrides: dict[str, Any] = {
        'grid_size': g,
        'remove_central_crease': remove_central_crease,
        'hinges_from_stick_figure': hinges_from_stick_figure,
        'up_down_method': up_down_method,
        'disallow_trapping_edge_flaps': disallow_trapping_edge_flaps,
        'allow_misaligned_symmetric_hinges': allow_misaligned_symmetric_hinges,
    }
    if max_steps is not None:
      overrides['max_steps'] = max_steps
    return dataclasses.replace(base, **overrides)

  # Primary configurations
  if stage in ('all', 'primary'):
    # Guided configurations
    for rcc in (True, False):
      for method in ('azimuth', 'flaps_down'):
        yield _make(
            remove_central_crease=rcc,
            hinges_from_stick_figure=True,
            up_down_method=method,
            disallow_trapping_edge_flaps=True,
            allow_misaligned_symmetric_hinges=False,
        )
    # Unguided configurations
    for rcc in (True, False):
      yield _make(
          remove_central_crease=rcc,
          hinges_from_stick_figure=False,
          up_down_method='flaps_down',
          disallow_trapping_edge_flaps=True,
          allow_misaligned_symmetric_hinges=False,
      )

  # Fallback recovery configurations (relaxed heuristics)
  if stage in ('all', 'fallback'):
    # Scale-1 guided fallback
    for rcc in (True, False):
      for method in ('azimuth', 'flaps_down'):
        yield _make(
            remove_central_crease=rcc,
            hinges_from_stick_figure=True,
            up_down_method=method,
            disallow_trapping_edge_flaps=False,
            allow_misaligned_symmetric_hinges=True,
        )
    # Scale-2 guided fallback (relaxed heuristics with capped steps)
    s2_max_steps = (
        min(base.max_steps, 2500)
        if (base is not None and base.max_steps is not None)
        else 2500
    )
    for rcc in (True, False):
      for method in ('azimuth', 'flaps_down'):
        yield _make(
            remove_central_crease=rcc,
            hinges_from_stick_figure=True,
            up_down_method=method,
            disallow_trapping_edge_flaps=False,
            allow_misaligned_symmetric_hinges=True,
            max_steps=s2_max_steps,
        )


def is_bankable(
    packing_output: Any,
    *,
    design: bus.DesignTree | None = None,
    solver_config: Any = None,
) -> BankabilityResult:
  """Single universal acceptance gate for banking packed crease patterns.

  Evaluates geometric validity, zero unused area, Kawasaki parity, Maekawa
  bounds, river notch/separated layers, and Step-0 solvability across the solver
  cascade.
  Accepts a packing if Step 0 passes under ANY configuration that the
  downstream solving cascade will attempt.

  Args:
    packing_output: The PackingOutput instance to evaluate.
    design: Optional bus.DesignTree describing stick figure geometry and
      metrics.
    solver_config: Optional SolvingTaskConfig or SolverConfig.

  Returns:
    BankabilityResult with reasons (empty tuple if bankable) and the
    first_passing_config.
  Raises:
    TypeError: If design is not a bus.DesignTree.
  """
  if design is not None and not isinstance(design, bus.DesignTree):
    raise TypeError(
        f'design must be a bus.DesignTree, got {type(design).__name__}.'
        ' Call bus.DesignTree.from_stick_figure(tree) first.'
    )

  if packing_output is None or not getattr(packing_output, 'success', False):
    return BankabilityResult(
        reasons=('Packing output is None or marked unsuccessful.',)
    )

  reasons: list[str] = []

  # 1. Zero unused area and geometric sheet boundary validation
  try:
    packing_output.validate()
  except Exception as e:  # pylint: disable=broad-exception-caught
    reasons.append(f'Validation failed: {e}')

  # 2. Check for river separated layers / narrow self-colliding notches
  if hasattr(packing_output, 'tracker') and packing_output.tracker:
    for rname, r in getattr(
        packing_output.tracker, 'packed_rivers', {}
    ).items():
      if hasattr(r, 'has_separated_layers') and r.has_separated_layers():
        reasons.append(f'River {rname} has separated layers / narrow notch.')

  # 3. Mathematical solvability (Kawasaki parity, Maekawa bounds, pleat
  # alignment)
  cp = getattr(packing_output, 'packing_cp', None)
  if cp is not None:
    solv_res = check_solvability(cp)
    if not solv_res.is_solvable and solv_res.reason:
      reasons.append(f'Solvability check failed: {solv_res.reason}')
  else:
    reasons.append('Missing packing crease pattern.')

  if reasons:
    return BankabilityResult(reasons=tuple(reasons))

  # 4. Step-0 solvability across the solver cascade
  from . import hinges as hinge_utils  # pylint: disable=g-import-not-at-top

  grid_size = cp.grid_size
  packed_info = None
  if design is not None:
    packed_info = bus.PackedCreasePattern.from_packing_output(
        packing_output, design=design
    )
  else:
    try:
      packed_info = bus.PackedCreasePattern.from_packing_output(packing_output)
    except (ValueError, KeyError, AttributeError):
      packed_info = None

  # Derive configs from solver_config or canonical cascade
  configs_to_try: list[hinges.SolverConfig] = []
  if isinstance(solver_config, hinges.SolverConfig):
    configs_to_try = [dataclasses.replace(solver_config, grid_size=grid_size)]
  elif solver_config is not None and hasattr(solver_config, 'to_solver_config'):
    configs_to_try = list(
        solve_cascade(solver_config.to_solver_config(), grid_size=grid_size)
    )
  elif solver_config is not None and hasattr(solver_config, 'config_iter'):
    for cfg in solver_config.config_iter():
      configs_to_try.append(
          hinges.SolverConfig(
              grid_size=grid_size,
              remove_central_crease=getattr(cfg, 'remove_central_crease', True),
              hinges_from_stick_figure=getattr(
                  cfg, 'hinges_from_stick_figure', True
              ),
              up_down_method=getattr(cfg, 'up_down_method', 'flaps_down'),
          )
      )
    if hasattr(solver_config, 'fallback_config_iter'):
      for cfg in solver_config.fallback_config_iter():
        configs_to_try.append(
            hinges.SolverConfig(
                grid_size=grid_size,
                remove_central_crease=getattr(
                    cfg, 'remove_central_crease', False
                ),
                hinges_from_stick_figure=getattr(
                    cfg, 'hinges_from_stick_figure', True
                ),
                up_down_method=getattr(cfg, 'up_down_method', 'flaps_down'),
            )
        )
  if not configs_to_try:
    configs_to_try = list(solve_cascade(grid_size=grid_size))

  first_passing: hinges.SolverConfig | None = None
  step0_errors: list[str] = []
  for s_cfg in configs_to_try:
    rcc = s_cfg.remove_central_crease
    hsf = s_cfg.hinges_from_stick_figure
    try:
      s = s_cfg.make_from_cp(cp, packing_information=packed_info)
      if s.init_state._has_unsolveable_vertex():  # pylint: disable=protected-access
        step0_errors.append(
            f'Config (rcc={rcc}, hsf={hsf}) has unsolveable vertex'
        )
        continue
      if rcc:
        can_rcc = (
            hinge_utils.central_fold_utils.should_try_to_remove_central_crease(
                s.init_state.unvisited_hinges
                + s.init_state.ridges
                + s.init_state.pleats
                + s.init_state.unassigned_pleats,
                s.init_state.unvisited_hinges,
            )
        )
        if not can_rcc:
          step0_errors.append(
              f'Config (rcc={rcc}, hsf={hsf}) cannot remove central crease'
          )
          continue
      first_passing = s_cfg
      break
    except Exception as e:  # pylint: disable=broad-exception-caught
      step0_errors.append(f'Config (rcc={rcc}, hsf={hsf}) error: {e}')

  if first_passing is None:
    reasons.append(
        f'All Step-0 configurations failed: {"; ".join(step0_errors[:2])}'
    )
    return BankabilityResult(reasons=tuple(reasons), first_passing_config=None)

  return BankabilityResult(reasons=(), first_passing_config=first_passing)
