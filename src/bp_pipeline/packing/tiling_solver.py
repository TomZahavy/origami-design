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

"""Contains helper functions for packing flaps."""

from collections.abc import Iterator
import copy
import dataclasses
import functools
import logging
import math

import numpy as np

from .. import timeout
from ..crease_pattern import point as point_lib
from ..stick_figures import stick as stick_lib
from ..stick_figures import stick_figure
from . import config as config_lib
from . import flap_placement as flap_placement_lib
from . import scoring
from . import tiling_solver_local
from . import types
from . import utils_backtracking
from . import utils_packing_flaps
from . import utils_packing_svg
from . import utils_tracker
from .debug import debug_types

NoPackingFoundError = types.NoPackingFoundError


def solve_packing_iteratively(
    traversal_plan: list[types.TraversalStep],
    tracker: utils_tracker.CreasePatternTracker,
    stick_name_to_dims: dict[str, tuple[int, int]],
    grid_width: int,
    grid_height: int,
    debug: debug_types.DebugConfig,
    is_symmetric: bool = False,
    symmetry_axes: dict[str, bool] | None = None,
    allow_paired_axis_placement: bool = False,
    enforce_proximity_constraints: bool = True,
    require_perfect_tiling: bool = False,
    occupancy_mask: np.ndarray | None = None,
    scoring_config: scoring.ScoringConfig = scoring.ScoringConfig(),
    river_adjacent_cells: list[tuple[int, int]] | None = None,
    config: config_lib.PackingConfig = config_lib.PackingConfig(),
) -> Iterator[int]:
  """Iterative backtracking solver that finds a valid packing.

  This function orchestrates calls to helper functions that handle the
  forward (advancing) and backward (backtracking) phases of the search.

  Args:
      traversal_plan: An ordered list of dictionaries, where each dictionary
        defines an object to place and its constraints.
      tracker: An initialized CreasePatternTracker to manage the grid state.
      stick_name_to_dims: A mapping from stick name to polygon dimensions.
      grid_width: The grid width to use for packing.
      grid_height: The grid height to use for packing.
      debug: Debug configuration object.
      is_symmetric: If True, symmetry constraints are applied.
      symmetry_axes: A dict indicating which stick names are on a symmetry axis.
      allow_paired_axis_placement: If True, allow paired placement on axis.
      enforce_proximity_constraints: If True, enforce EQUAL 0 constraints.
      require_perfect_tiling: If True, only return True if a solution with zero
        unfilled area is found.
      occupancy_mask: If provided, used for perfect tiling check.
      scoring_config: The configuration used to score potential flap placements.
      river_adjacent_cells: If provided, and this is the first flap being
        placed, only placements touching these cells will be considered.
      config: The configuration options for packing.

  Yields:
      The unfilled area in the tracker of the latest solution.
  """
  stack = []
  step_index = 0
  packing_grid_width = grid_width // 2 if is_symmetric else grid_width
  add_poly_cand = functools.partial(
      flap_placement_lib.add_polygon_candidate, tracker
  )
  remove_poly_cand = functools.partial(
      flap_placement_lib.remove_polygon_candidate, tracker
  )

  step_count = 0
  while step_index is not None:
    # Periodically check for timeout.
    if (step_count & 63) == 0:
      timeout.maybe_timeout_cooperatively()
    step_count += 1

    assert step_index <= len(traversal_plan)
    if step_index == len(traversal_plan):
      # A solution is found.
      placement_for_util = [
          (p.size, p.offset[0], p.offset[1])
          for p in tracker.packed_polygons.values()
      ]
      unfilled_area = utils_packing_flaps.compute_unfilled_area(
          packing_grid_width,
          grid_height,
          placement_for_util,
          initial_mask=occupancy_mask,
      )
      debug.record_step(
          tracker, 'PACKING', f'Found full packing solution: {unfilled_area=}'
      )
      assert unfilled_area >= 0
      if require_perfect_tiling:
        if unfilled_area == 0:
          logging.info(
              'SUCCESS: Reached end of traversal. Perfect tiling found!'
          )
          yield unfilled_area
          timeout.maybe_timeout_cooperatively()
          backtrack_message = 'Searching for next solution...'
        else:
          backtrack_message = (
              f'Solution found but {unfilled_area=} > 0. Backtracking...'
          )
          logging.info(backtrack_message)

      else:
        # Not requiring perfect tiling, so first solution is enough
        logging.info('SUCCESS: (Potentially imperfect) solution found!')
        yield unfilled_area
        timeout.maybe_timeout_cooperatively()
        backtrack_message = 'Searching for next solution...'
    else:
      # Try to progress
      current_step = traversal_plan[step_index]
      current_stick = current_step['stick']
      current_stick_name = current_stick.name
      active_constraints = current_step.get('constraints', {})
      logging.debug(
          'Step %d, Attempting to place polygon %s',
          step_index,
          current_stick_name,
      )
      candidate_iterator = flap_placement_lib.find_possible_flap_placements(
          tracker=tracker,
          stick=current_stick,
          current_stick_name=current_stick_name,
          constraints=active_constraints,
          stick_name_to_dims=stick_name_to_dims,
          is_symmetric=is_symmetric,
          symmetry_axes=symmetry_axes,
          allow_paired_axis_placement=allow_paired_axis_placement,
          enforce_proximity_constraints=enforce_proximity_constraints,
          scoring_config=scoring_config,
          river_adjacent_cells=river_adjacent_cells,
          config=config,
      )

      if utils_backtracking.try_to_advance(
          candidate_iterator,
          add_poly_cand,
          stack,
          types.StackFrame,
          step_index,
          tracker,
          debug,
          stick=current_stick,
          config=config,
      ):
        step_index += 1
        continue
      else:
        backtrack_message = (
            f'No candidates found for {current_stick_name}. Backtracking...'
        )

    if debug.is_active():
      debug.record_step(tracker, 'BACKTRACK', backtrack_message, cand=None)
    step_index = utils_backtracking.try_to_backtrack(
        stack, add_poly_cand, remove_poly_cand, tracker, debug
    )

  # No more solutions found.


def generate_delta_combinations(
    unused_area: int,
    base_square_dims: dict[str, tuple[int, int]],
    grid_width: int,
    grid_height: int,
    max_delta_combinations: int = 1_000_000,
) -> tuple[list[tuple[int, ...]], list[types.SortedFlap]]:
  """Generates all delta combinations to tile the unused area.

  This function uses heuristics to find sets of "deltas" (changes in rectangle
  dimensions) that could potentially sum to fill the empty space left after
  the initial packing.

  Args:
      unused_area: The total area in grid units that needs to be filled.
      base_square_dims: The dimensions of the initial squares.
      grid_width: The width of the grid.
      grid_height: The height of the grid.
      max_delta_combinations: The maximum number of delta combinations to try.

  Returns:
      A tuple containing:
        - A tuple of all delta vectors to try.
        - A list of flap data (SortedFlap), sorted by size.
  """
  logging.info('Phase 2: Finding delta combinations to fill area.')
  all_flaps_sorted: list[types.SortedFlap] = sorted(
      [
          {'stick_name': i, 'side': dims[0]}
          for i, dims in base_square_dims.items()
      ],
      key=lambda x: x['side'],
      reverse=True,
  )
  lengths_for_delta = [f['side'] for f in all_flaps_sorted]
  unique_delta_combinations_tried = set()
  all_deltas_to_try: list[tuple[int, ...]] = []
  max_overall_possible_delta = max(grid_width, grid_height)

  single_deltas = utils_packing_flaps.find_single_delta_combinations(
      unused_area,
      lengths_for_delta,  # pyrefly: ignore[bad-argument-type]
      max_overall_possible_delta,
      unique_delta_combinations_tried,
      max_combinations=max_delta_combinations,
  )
  all_deltas_to_try.extend(single_deltas)

  for num_non_zeros_k in range(2, len(lengths_for_delta) + 1):
    for max_d_limit in range(2, max_overall_possible_delta + 1, 2):
      sparse_deltas = utils_packing_flaps.find_delta_combinations(
          unused_area,
          lengths_for_delta,  # pyrefly: ignore[bad-argument-type]
          num_non_zeros_k,
          max_d_limit,
          unique_delta_combinations_tried,
          max_combinations=max_delta_combinations,
      )
      all_deltas_to_try.extend(sparse_deltas)
  return all_deltas_to_try, all_flaps_sorted


def find_perfect_tiling_from_deltas(
    all_deltas_to_try: list[tuple[int, ...]],
    all_flaps_sorted: list[types.SortedFlap],
    base_square_dims: dict[str, tuple[int, int]],
    traversal_plan: list[types.TraversalStep],
    grid_size_for_tracker: int,
    grid_width: int,
    grid_height: int,
    debug: debug_types.DebugConfig,
    is_symmetric: bool = False,
    symmetry_axes: dict[str, bool] | None = None,
    allow_paired_axis_placement: bool = False,
    occupancy_mask: np.ndarray | None = None,
    scoring_config: scoring.ScoringConfig = scoring.ScoringConfig(),
    config: config_lib.PackingConfig = config_lib.PackingConfig(),
    river_adjacent_cells: list[tuple[int, int]] | None = None,
) -> utils_tracker.CreasePatternTracker | None:
  """Iterates through delta combinations to find a perfect tiling.

  This function contains the main solver loop for the tiling phase. It takes a
  list of potential delta combinations, constructs the corresponding rectangle
  dimensions for each, and runs the backtracking solver to see if a perfect,
  zero-unfilled-area packing can be found.

  Args:
      all_deltas_to_try: A list of delta vectors, where each vector represents a
        set of changes to the base square dimensions.
      all_flaps_sorted: A list of flap data, sorted by size.
      base_square_dims: The original dimensions of the squares.
      traversal_plan: The fixed traversal plan for the solver.
      grid_size_for_tracker: The grid size to use for the tracker.
      grid_width: The grid width to use for packing.
      grid_height: The grid height to use for packing.
      debug: Debug configuration object.
      is_symmetric: If True, symmetry constraints are applied.
      symmetry_axes: A dict indicating which stick names are on a symmetry axis.
      allow_paired_axis_placement: If True, allow paired placement on axis.
      occupancy_mask: If provided, initializes tracker with blocked cells.
      scoring_config: The configuration used to score potential flap placements.
      config: The configuration options for packing.
      river_adjacent_cells: If provided, and this is the first flap being
        placed, only placements touching these cells will be considered.

  Returns:
      A CreasePatternTracker containing the perfect tiling if one is found,
      otherwise None.
  """
  logging.info(
      'Phase 3: Testing %d delta vectors with the constraint solver.',
      len(all_deltas_to_try),
  )
  lengths_for_delta = [f['side'] for f in all_flaps_sorted]

  for delta in all_deltas_to_try:
    timeout.maybe_timeout_cooperatively()
    rectangle_sets = utils_packing_flaps.generate_rectangle_configurations(
        lengths_for_delta, delta, max_combinations=config.max_delta_combinations  # pyrefly: ignore[bad-argument-type]
    )
    for i, r_set in enumerate(rectangle_sets):
      timeout.maybe_timeout_cooperatively()
      for j, dims in enumerate(r_set):
        stick_name = all_flaps_sorted[j]['stick_name']
        base_width, base_height = base_square_dims[stick_name]
        if dims[0] > base_width and dims[1] > base_height:
          raise ValueError(
              f'Flap {stick_name} cannot increase in both width and height:'
              f' from ({base_width}, {base_height}) to ({dims[0]}, {dims[1]})'
          )
      stick_name_to_dims = base_square_dims.copy()
      delta_dims = {
          all_flaps_sorted[j]['stick_name']: r_set[j] for j in range(len(r_set))
      }
      stick_name_to_dims.update(delta_dims)

      logging.info(
          '--- Testing Combination (Delta: %s, Orientation: %d) ---',
          delta,
          i + 1,
      )

      successful_tracker = utils_tracker.CreasePatternTracker(
          grid_size_for_tracker, occupancy_mask=occupancy_mask
      )
      for unfilled_area in solve_packing_iteratively(
          traversal_plan,
          successful_tracker,
          stick_name_to_dims,
          grid_width,
          grid_height,
          debug=debug,
          is_symmetric=is_symmetric,
          symmetry_axes=symmetry_axes,
          allow_paired_axis_placement=allow_paired_axis_placement,
          enforce_proximity_constraints=config.enforce_proximity_constraints,
          require_perfect_tiling=True,
          occupancy_mask=occupancy_mask,
          scoring_config=scoring_config,
          river_adjacent_cells=river_adjacent_cells,
          config=config,
      ):
        if not unfilled_area:
          logging.info(
              '>>> SUCCESS: Found a valid, constrained, perfect tiling!'
          )
          return successful_tracker
      else:
        logging.info(
            '--- Combination (Delta: %s, Orientation: %d) did not yield a'
            ' perfect tiling. ---',
            delta,
            i + 1,
        )

  logging.warning(
      '--- FAILURE: Tested all rectangle combinations, no perfect tiling'
      ' found. ---'
  )
  return None


def add_axis_filler_polygons(
    tracker: utils_tracker.CreasePatternTracker,
    grid_size: int,
) -> None:
  """Fills empty cells in the two axis columns with fictitious 2×k polygons."""
  half = grid_size // 2
  left_col = half - 1
  right_col = half
  segment_start = None
  filler_idx = 0
  for row in range(grid_size):
    both_empty = (
        not tracker.occupancy_grid[row, left_col]
        and not tracker.occupancy_grid[row, right_col]
    )
    if both_empty:
      if segment_start is None:
        segment_start = row
    else:
      if segment_start is not None:
        height = row - segment_start
        inv = 1.0 / grid_size
        center = point_lib.Point(
            x=(left_col + 1) * inv,
            y=(segment_start + height * 0.5) * inv,
            require_on_paper=False,
        )
        placement = types.PolygonPlacement(
            offset=(left_col, segment_start),
            size=(2, height),
            center=center,
        )
        tracker.add_polygon(
            f'{types.AXIS_FILLER_PREFIX}_{filler_idx}', placement
        )
        filler_idx += 1
        segment_start = None
  if segment_start is not None:
    height = grid_size - segment_start
    inv = 1.0 / grid_size
    center = point_lib.Point(
        x=(left_col + 1) * inv,
        y=(segment_start + height * 0.5) * inv,
        require_on_paper=False,
    )
    placement = types.PolygonPlacement(
        offset=(left_col, segment_start),
        size=(2, height),
        center=center,
    )
    tracker.add_polygon(f'{types.AXIS_FILLER_PREFIX}_{filler_idx}', placement)


def pack_and_tile_until_perfect(
    traversal_plan: list[types.TraversalStep],
    base_square_dims: dict[str, tuple[int, int]],
    grid_size: int,
    debug: debug_types.DebugConfig,
    is_symmetric: bool = False,
    symmetry_axes: dict[str, bool] | None = None,
    allow_paired_axis_placement: bool = False,
    occupancy_mask: np.ndarray | None = None,
    scoring_config: scoring.ScoringConfig = scoring.ScoringConfig(),
    config: config_lib.PackingConfig = config_lib.PackingConfig(),
    river_adjacent_cells: list[tuple[int, int]] | None = None,
    sacrificial_polygons: dict[str, types.PolygonPlacement] | None = None,
    locked_long_side_flaps: set[str] | None = None,
) -> tuple[utils_tracker.CreasePatternTracker, dict[str, tuple[int, int]], int]:
  """Pre-processes data and performs the initial packing of base squares.

  This function prepares the necessary data structures (traversal plan, base
  dimensions) and runs the solver once to get an initial, non-tiled
  placement. It then calculates the remaining area that needs to be filled.

  Args:
      traversal_plan: The traversal plan for the solver.
      base_square_dims: The original dimensions of the squares.
      grid_size: The grid size of the crease pattern.
      debug: Debug configuration object.
      is_symmetric: If True, symmetry constraints are applied.
      symmetry_axes: A dict indicating which stick names are on a symmetry axis.
      allow_paired_axis_placement: If True, allow paired placement on axis.
      occupancy_mask: If provided, initializes tracker with blocked cells.
      scoring_config: The configuration used to score potential flap placements.
      config: Configuration object that holds solver parameters.
      river_adjacent_cells: If provided, and this is the first flap being
        placed, only placements touching these cells will be considered.
      sacrificial_polygons: If provided, a dict of sacrificial polygon IDs to
        their placements. These are unblocked from the occupancy mask and added
        to the tracker before packing.
      locked_long_side_flaps: If provided, prevents these flaps from expanding
        along their long side during local tiling.

  Raises:
      NoPackingFoundError: If no packing solution can be found.

  Returns:
      A tuple containing the tracker from the initial run, the base square
      dimensions, and the calculated unused area.
  """

  if config.local_tiling_config is None:
    raise ValueError('config.local_tiling_config must not be None.')

  logging.info('Phase 1: Pre-processing and running initial packing.')
  effective_mask = occupancy_mask
  if sacrificial_polygons and effective_mask is not None:
    effective_mask = effective_mask.copy()
    for placement in sacrificial_polygons.values():
      offset_x, offset_y = placement.offset
      width, height = placement.size
      for i in range(max(0, offset_y), min(grid_size, offset_y + height)):
        for j in range(max(0, offset_x), min(grid_size, offset_x + width)):
          effective_mask[i, j] = False
  packing_tracker = utils_tracker.CreasePatternTracker(
      grid_size, occupancy_mask=effective_mask
  )
  if sacrificial_polygons:
    for poly_id, placement in sacrificial_polygons.items():
      packing_tracker.add_polygon(poly_id, placement)

  unfilled_area = None
  for unfilled_area in solve_packing_iteratively(
      traversal_plan,
      packing_tracker,
      base_square_dims,
      grid_size,
      grid_size,
      debug=debug,
      is_symmetric=is_symmetric,
      symmetry_axes=symmetry_axes,
      allow_paired_axis_placement=allow_paired_axis_placement,
      enforce_proximity_constraints=config.enforce_proximity_constraints,
      occupancy_mask=effective_mask,
      scoring_config=scoring_config,
      river_adjacent_cells=river_adjacent_cells,
      config=config,
  ):
    if unfilled_area == 0:
      logging.info('Packing iteration SUCCEEDED. Perfect tiling found.')
      return packing_tracker, base_square_dims, unfilled_area
    elif config.easy_mode:
      logging.info(
          'Easy mode: returning initial packing without tiling. '
          'Unused area: %d',
          unfilled_area,
      )
      return packing_tracker, base_square_dims, unfilled_area
    else:
      logging.info('Packing iteration SUCCEEDED. Searching for perfect tiling.')
      blocked_cells = []
      has_axis_flaps = symmetry_axes and any(
          symmetry_axes.get(step['stick'].name) for step in traversal_plan
      )
      if config.remove_central_crease and is_symmetric and not has_axis_flaps:
        axis_col = grid_size // 2 - 1
        on_axis_rows = set()
        for placement in packing_tracker.packed_polygons.values():
          if math.isclose(placement.center.x, 0.5):
            _, oy = placement.offset
            _, h = placement.size
            for r in range(oy, oy + h):
              on_axis_rows.add(r)
        for row in range(grid_size):
          if row not in on_axis_rows:
            if not packing_tracker.occupancy_grid[row, axis_col]:
              packing_tracker.occupancy_grid[row, axis_col] = True
              packing_tracker.grid[row, axis_col] = (
                  utils_packing_flaps.BlockedGridCellState
              )
              blocked_cells.append(row)
      perfect_tracker = (
          tiling_solver_local.find_perfect_tiling_from_local_expansions(
              packing_tracker,
              is_symmetric=is_symmetric,
              config=config.local_tiling_config,
              locked_long_side_flaps=locked_long_side_flaps,
              legacy_iteration_order=config.legacy_iteration_order,
          )
      )
      if blocked_cells:
        axis_col = grid_size // 2 - 1
        target = (
            perfect_tracker if perfect_tracker is not None else packing_tracker
        )
        for row in blocked_cells:
          cell_state = target.grid[row, axis_col]
          if cell_state is utils_packing_flaps.BlockedGridCellState:
            target.occupancy_grid[row, axis_col] = False
            target.grid[row, axis_col] = utils_packing_flaps.EmptyGridCellState
    if perfect_tracker is not None:
      return perfect_tracker, base_square_dims, 0
    else:
      logging.info('Tiling iteration FAILED. Searching for next packing.')

  if unfilled_area is None:
    logging.debug('Initial packing failed. Try increasing the grid size.')
    raise NoPackingFoundError(
        'Initial packing failed. Try increasing the grid size.'
    )

  logging.debug('Could not find a packing that could be locally-tiled.')
  return packing_tracker, base_square_dims, unfilled_area


def pack_flaps_with_adjacency(
    traversal_plan: list[types.TraversalStep],
    base_square_dims: dict[str, tuple[int, int]],
    grid_size_for_tracker: int,
    grid_width: int,
    grid_height: int,
    debug: debug_types.DebugConfig,
    is_symmetric: bool = False,
    symmetry_axes: dict[str, bool] | None = None,
    allow_paired_axis_placement: bool = False,
    enforce_proximity_constraints: bool = True,
    occupancy_mask: np.ndarray | None = None,
    scoring_config: scoring.ScoringConfig = scoring.ScoringConfig(),
    river_adjacent_cells: list[tuple[int, int]] | None = None,
    config: config_lib.PackingConfig = config_lib.PackingConfig(),
    locked_long_side_flaps: set[str] | None = None,
) -> Iterator[
    tuple[utils_tracker.CreasePatternTracker, dict[str, tuple[int, int]], int]
]:
  """Pre-processes data and performs the initial packing of base squares.

  This function prepares the necessary data structures (traversal plan, base
  dimensions) and runs the solver once to get an initial, non-tiled
  placement. It then calculates the remaining area that needs to be filled.

  Args:
      traversal_plan: The traversal plan for the solver.
      base_square_dims: The original dimensions of the squares.
      grid_size_for_tracker: The grid size to use for the tracker.
      grid_width: The grid width to use for packing.
      grid_height: The grid height to use for packing.
      debug: Debug configuration object.
      is_symmetric: If True, symmetry constraints are applied.
      symmetry_axes: A dict indicating which stick names are on a symmetry axis.
      allow_paired_axis_placement: If True, allow paired placement on axis.
      enforce_proximity_constraints: If True, enforce EQUAL 0 constraints.
      occupancy_mask: If provided, initializes tracker with blocked cells.
      scoring_config: The configuration used to score potential flap placements.
      river_adjacent_cells: If provided, and this is the first flap being
        placed, only placements touching these cells will be considered.
      config: The configuration options for packing.
      locked_long_side_flaps: If provided, prevents these flaps from expanding
        along their long side during local tiling.

  Yields:
      A tuple containing the tracker from the initial run, the base square
      dimensions, and the calculated unused area. Returns None if the initial
      packing fails entirely.
  """
  logging.info('Phase 1: Pre-processing and running initial packing.')
  del locked_long_side_flaps
  traversal_plan_copy = copy.deepcopy(traversal_plan)
  if enforce_proximity_constraints:
    for i in range(1, len(traversal_plan_copy)):
      prev_stick_name = traversal_plan_copy[i - 1]['stick'].name
      traversal_plan_copy[i]['constraints'][prev_stick_name] = {
          'type': types.ConstraintType.EQUAL,
          'value': 0,
      }
  initial_tracker = utils_tracker.CreasePatternTracker(
      grid_size_for_tracker, occupancy_mask=occupancy_mask
  )
  found_solution = False
  for unfilled_area in solve_packing_iteratively(
      traversal_plan_copy,
      initial_tracker,
      base_square_dims,
      grid_width,
      grid_height,
      debug=debug,
      is_symmetric=is_symmetric,
      symmetry_axes=symmetry_axes,
      allow_paired_axis_placement=allow_paired_axis_placement,
      enforce_proximity_constraints=enforce_proximity_constraints,
      occupancy_mask=occupancy_mask,
      scoring_config=scoring_config,
      river_adjacent_cells=river_adjacent_cells,
      config=config,
  ):
    found_solution = True
    logging.info(
        'Initial packing SUCCEEDED. Unused area to fill: %d', unfilled_area
    )
    yield initial_tracker, base_square_dims, unfilled_area

  if not found_solution:
    logging.error('Initial packing of squares FAILED. Cannot proceed.')


def find_constrained_tiling(
    traversal_plan: list[types.TraversalStep],
    base_square_dims: dict[str, tuple[int, int]],
    grid_size: int,
    debug: debug_types.DebugConfig,
    grid_height: int | None = None,
    is_symmetric: bool = False,
    symmetry_axes: dict[str, bool] | None = None,
    allow_paired_axis_placement: bool = False,
    occupancy_mask: np.ndarray | None = None,
    stick_figure_to_pack: stick_figure.StickFigure | None = None,
    scoring_config: scoring.ScoringConfig = scoring.ScoringConfig(),
    config: config_lib.PackingConfig = config_lib.PackingConfig(),
    river_adjacent_cells: list[tuple[int, int]] | None = None,
    sacrificial_polygons: dict[str, types.PolygonPlacement] | None = None,
    locked_long_side_flaps: set[str] | None = None,
) -> tuple[utils_tracker.CreasePatternTracker, debug_types.TilingDetails]:
  """Finds a perfect tiling of rectangles derived from a StickFigureOutput.

  This function orchestrates a multi-phase process to find a valid, perfect
  tiling by dispatching to helper functions for each logical step:
  1.  Performs an initial packing of base squares.
  2.  Generates combinations of rectangles ("deltas") to fill leftover space.
  3.  Iteratively tests each combination with the solver to find a perfect fit.

  Args:
      traversal_plan: The traversal plan for the solver.
      base_square_dims: The original dimensions of the squares.
      grid_size: The grid width to use for the tiling.
      debug: Debug configuration object.
      grid_height: The grid height to use for the tiling. If None, grid_size is
        used to form a square grid.
      is_symmetric: If True, symmetry constraints are applied.
      symmetry_axes: A dict indicating which stick names are on a symmetry axis.
      allow_paired_axis_placement: If True, allow paired placement on axis.
      occupancy_mask: If provided, initializes tracker with blocked cells.
      stick_figure_to_pack: The stick figure to pack, used for mirroring. If
        None, no mirroring is performed.
      scoring_config: The configuration used to score potential flap placements.
      config: The configuration options for packing.
      river_adjacent_cells: If provided, and this is the first flap being
        placed, only placements touching these cells will be considered.
      sacrificial_polygons: If provided, a dict of sacrificial polygon IDs to
        their placements, threaded through to pack_and_tile_until_perfect.
      locked_long_side_flaps: If provided, prevents these flaps from expanding
        along their long side during local tiling.

  Raises:
      NoPackingFoundError: If no packing solution can be found.

  Returns:
      A tuple containing:
        - A CreasePatternTracker containing tiling. If a perfect tiling is
          found, it's returned. If perfect tiling is not found but initial
          packing succeeded, the tracker from initial packing is returned.
        - A dictionary with details: unused_area, num_delta_combinations,
          perfect_tiling_found.
      stick_figure_to_pack: The stick figure to pack, used for mirroring.
  """
  grid_width = grid_size
  if grid_height is None:
    grid_height = grid_width
  grid_size_for_tracker = max(grid_width, grid_height)
  if is_symmetric and grid_width % 2 == 1:
    raise ValueError('Grid width must be even for symmetric packing.')
  if occupancy_mask is not None and occupancy_mask.shape != (
      grid_size_for_tracker,
      grid_size_for_tracker,
  ):
    raise ValueError(
        f'Occupancy mask shape {occupancy_mask.shape} does not match '
        f'grid size for tracker ({grid_size_for_tracker},'
        f' {grid_size_for_tracker}).'
    )

  # --- Phase 1: Pre-process and run initial packing ---
  if config.local_tiling_config is not None:
    if grid_width != grid_height:
      raise ValueError(
          'Grid width and height must be the same for local tiling.'
      )
    result = pack_and_tile_until_perfect(
        traversal_plan,
        base_square_dims,
        grid_size,
        debug=debug,
        is_symmetric=is_symmetric,
        symmetry_axes=symmetry_axes,
        allow_paired_axis_placement=allow_paired_axis_placement,
        occupancy_mask=occupancy_mask,
        scoring_config=scoring_config,
        config=config,
        river_adjacent_cells=river_adjacent_cells,
        sacrificial_polygons=sacrificial_polygons,
        locked_long_side_flaps=locked_long_side_flaps,
    )
  else:
    result = next(
        pack_flaps_with_adjacency(
            traversal_plan=traversal_plan,
            base_square_dims=base_square_dims,
            grid_size_for_tracker=grid_size_for_tracker,
            grid_width=grid_width,
            grid_height=grid_height,
            debug=debug,
            is_symmetric=is_symmetric,
            symmetry_axes=symmetry_axes,
            allow_paired_axis_placement=allow_paired_axis_placement,
            enforce_proximity_constraints=config.enforce_proximity_constraints,
            occupancy_mask=occupancy_mask,
            scoring_config=scoring_config,
            river_adjacent_cells=river_adjacent_cells,
            config=config,
            locked_long_side_flaps=locked_long_side_flaps,
        ),
        None,
    )
    if result is None:
      raise NoPackingFoundError('No packing found through initial packing.')

  tracker, _, unused_area = result
  details = debug_types.TilingDetails(
      grid_size=grid_width,
      grid_height=grid_height,
      is_symmetric=is_symmetric,
      unused_area=unused_area,
      perfect_tiling_found=False,
  )

  if unused_area <= 0:
    logging.info('Packing is already perfect. No tiling needed.')
    if is_symmetric:
      utils_packing_svg.mirror_symmetric_placements(
          tracker, grid_width, stick_figure_to_pack
      )
    if debug.save_history:
      details['debug_history'] = debug.history
    details['perfect_tiling_found'] = True
    return tracker, details
  elif config.easy_mode:
    logging.info(
        'Easy mode: skipping tiling phases. Unused area: %d', unused_area
    )
    if is_symmetric:
      utils_packing_svg.mirror_symmetric_placements(
          tracker, grid_width, stick_figure_to_pack
      )
    if debug.save_history:
      details['debug_history'] = debug.history
    details['perfect_tiling_found'] = True
    return tracker, details
  elif config.local_tiling_config is not None:
    # Local tiling has already been run and failed to find a solution
    logging.debug('No packing could be perfectly locally-tiled.')
    if debug.save_history:
      details['debug_history'] = debug.history
    return tracker, details

  assert (
      config.local_tiling_config is None
  ), 'Local tiling should have returned before this point.'

  # --- Phase 2: Generate delta combinations to try ---
  packing_grid_width = grid_width // 2 if is_symmetric else grid_width
  all_deltas_to_try, all_flaps_sorted = generate_delta_combinations(
      unused_area,
      base_square_dims,
      packing_grid_width,
      grid_height,
      max_delta_combinations=config.max_delta_combinations,
  )
  details['num_delta_combinations'] = len(all_deltas_to_try)
  if not all_deltas_to_try:
    logging.warning('No delta combinations found that can tile the area.')
    if debug.save_history:
      details['debug_history'] = debug.history
    return tracker, details

  # --- Phase 3: Test all combinations to find a perfect tiling ---

  final_tracker = find_perfect_tiling_from_deltas(
      all_deltas_to_try,
      all_flaps_sorted,
      base_square_dims,
      traversal_plan,
      grid_size_for_tracker,
      grid_width,
      grid_height,
      debug=debug,
      is_symmetric=is_symmetric,
      symmetry_axes=symmetry_axes,
      allow_paired_axis_placement=allow_paired_axis_placement,
      occupancy_mask=occupancy_mask,
      scoring_config=scoring_config,
      config=config,
      river_adjacent_cells=river_adjacent_cells,
  )

  if final_tracker:
    details['perfect_tiling_found'] = True
    details['unused_area'] = 0
    if is_symmetric:
      utils_packing_svg.mirror_symmetric_placements(
          final_tracker, grid_width, stick_figure_to_pack
      )
    if debug.save_history:
      details['debug_history'] = debug.history
    return final_tracker, details
  else:
    if debug.save_history:
      details['debug_history'] = debug.history
    return tracker, details


def _create_traversal_plan_for_flaps(
    traversal_plan: list[types.TraversalStep],
    flaps_to_pack: list[stick_lib.Stick],
    config: config_lib.PackingConfig,
) -> list[types.TraversalStep]:
  """Creates a traversal plan for packing a subset of flaps.

  It filters the given traversal plan to include only flaps in
  flaps_to_pack. If config.enforce_proximity_constraints is True, it adds
  distance (EQUAL 0) constraints between consecutive flaps in the plan.
  Otherwise, it
  sorts the flaps by length in descending order to pack largest flaps first.

  Args:
    traversal_plan: The original traversal plan for all flaps and rivers.
    flaps_to_pack: The list of flaps to include in the plan.
    config: The configuration options for packing.

  Returns:
    A traversal plan for packing the given flaps.
  """
  flap_names = {s.name for s in flaps_to_pack}
  flaps_traversal_plan = [
      copy.deepcopy(s) for s in traversal_plan if s['stick'].name in flap_names
  ]
  if config.enforce_proximity_constraints:
    for i in range(1, len(flaps_traversal_plan)):
      prev_stick_name = flaps_traversal_plan[i - 1]['stick'].name
      flaps_traversal_plan[i]['constraints'][prev_stick_name] = {
          'type': types.ConstraintType.EQUAL,
          'value': 0,
      }
  else:
    flaps_traversal_plan = sorted(
        flaps_traversal_plan,
        key=lambda s: s['stick'].length,
        reverse=True,
    )
  return flaps_traversal_plan


def pack_flaps(
    *,
    tracker: utils_tracker.CreasePatternTracker,
    flaps_to_pack: list[stick_lib.Stick],
    traversal_plan: list[types.TraversalStep],
    debug: debug_types.DebugConfig,
    fast_packing_debug: bool = False,
    is_symmetric: bool = False,
    symmetry_axes: dict[str, bool] | None = None,
    confine_to_mask: np.ndarray | None = None,
    scoring_config: scoring.ScoringConfig = scoring.ScoringConfig(),
    config: config_lib.PackingConfig = config_lib.PackingConfig(),
    river_adjacent_cells: list[tuple[int, int]] | None = None,
    sacrificial_polygons: dict[str, types.PolygonPlacement] | None = None,
    base_square_dims_override: dict[str, tuple[int, int]] | None = None,
) -> dict[str, types.PolygonPlacement] | None:
  """Packs a list of flaps into the available space in tracker.

  Args:
    tracker: The tracker to use for packing.
    flaps_to_pack: The list of flaps to pack.
    traversal_plan: The original traversal plan for all flaps and rivers.
    debug: Debug configuration object.
    fast_packing_debug: If True, use initial packing check instead of
      find_constrained_tiling.
    is_symmetric: If True, symmetry constraints are applied.
    symmetry_axes: A dict indicating which stick names are on a symmetry axis.
    confine_to_mask: If provided, initializes tracker with blocked cells.
    scoring_config: The configuration used to score potential flap placements.
    config: The configuration options for packing.
    river_adjacent_cells: If provided, and this is the first flap being placed,
      only placements touching these cells will be considered.
    sacrificial_polygons: If provided, a dict of sacrificial polygon IDs to
      their placements, threaded through to find_constrained_tiling.
    base_square_dims_override: If provided, overrides locally computed dims.

  Returns:
    A dictionary mapping flap names to their packed placements, or None if
    packing fails.
  """
  timeout.maybe_timeout_cooperatively()

  flaps_traversal_plan = _create_traversal_plan_for_flaps(
      traversal_plan, flaps_to_pack, config
  )
  if not flaps_traversal_plan:
    return {}

  base_square_dims = {}
  for step in flaps_traversal_plan:
    stick = step['stick']
    if base_square_dims_override and stick.name in base_square_dims_override:
      base_square_dims[stick.name] = base_square_dims_override[stick.name]
    else:
      dim = utils_packing_flaps.get_flap_dim(stick, config.use_level_shifter)
      base_square_dims[stick.name] = (dim, dim)
  scoring_config = dataclasses.replace(
      scoring_config,
      context=scoring.PackingContext(base_square_dims=base_square_dims),
  )
  locked_long_side_flaps = None
  if base_square_dims_override:
    locked_long_side_flaps = {
        name
        for name, dims in base_square_dims_override.items()
        if dims[0] != dims[1]
    }

  if confine_to_mask is not None:
    occupancy_mask = tracker.occupancy_grid | (~confine_to_mask)
  else:
    occupancy_mask = tracker.occupancy_grid
  # If fast_packing_debug or to avoid slow tiling, use initial packing check
  # instead of find_constrained_tiling.
  if fast_packing_debug or config.easy_mode:
    packing_result = next(
        pack_flaps_with_adjacency(
            traversal_plan=flaps_traversal_plan,
            base_square_dims=base_square_dims,
            grid_size_for_tracker=tracker.grid_size,
            grid_width=tracker.grid_size,
            grid_height=tracker.grid_size,
            debug=debug,
            occupancy_mask=occupancy_mask,
            enforce_proximity_constraints=config.enforce_proximity_constraints,
            is_symmetric=is_symmetric,
            symmetry_axes=symmetry_axes,
            scoring_config=scoring_config,
            river_adjacent_cells=river_adjacent_cells,
            config=config,
            locked_long_side_flaps=locked_long_side_flaps,
        ),
        None,
    )
    if packing_result is None:
      logging.debug('Initial packing of flaps failed.')
      return None
    flaps_tracker, _, _ = packing_result
    return flaps_tracker.packed_polygons
  else:
    try:
      flaps_tracker, details = find_constrained_tiling(
          traversal_plan=flaps_traversal_plan,
          base_square_dims=base_square_dims,
          grid_size=tracker.grid_size,
          debug=debug,
          grid_height=tracker.grid_size,
          occupancy_mask=occupancy_mask,
          is_symmetric=is_symmetric,
          symmetry_axes=symmetry_axes,
          scoring_config=scoring_config,
          config=config,
          river_adjacent_cells=river_adjacent_cells,
          sacrificial_polygons=sacrificial_polygons,
          locked_long_side_flaps=locked_long_side_flaps,
      )
    except NoPackingFoundError:
      logging.debug('Constrained tiling of flaps failed.')
      return None
    if details['perfect_tiling_found']:
      return flaps_tracker.packed_polygons
    else:
      logging.debug('Perfect tiling of flaps failed.')
      return None
