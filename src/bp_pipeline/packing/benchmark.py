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

"""Benchmarking utilities and harness for box-pleating packers."""

from collections.abc import Callable, Mapping, Sequence
import concurrent.futures
import copy
import dataclasses
import os
import time
from typing import Any, Literal

from absl import logging

from .. import bus
from .. import pipeline
from ..crease_pattern import global_foldability
from ..packing import config as packing_config_lib
from ..packing import packing_output as packing_output_lib
from ..packing import river as river_lib
from ..solving import solvability
from ..stick_figures import stick_figure as stick_figure_lib
from ..stick_figures.examples import example_trees

PackerType = Literal['default', 'stacking'] | str


def compute_stick_signature(tree: Any) -> str:
  """Computes a canonical stick signature string for a tree."""
  children = getattr(tree, 'children', None)
  if children is None and isinstance(tree, Mapping):
    children = tree.get('children', [])
  if not children:
    return ''
  items = []
  for c in children:
    if isinstance(c, Mapping):
      name = str(c.get('name', ''))
      start = str(c.get('start', ''))
      end = str(c.get('end', ''))
      length = int(c.get('length', 0))
    else:
      name = str(getattr(c, 'name', ''))
      start = str(getattr(c, 'start', ''))
      end = str(getattr(c, 'end', ''))
      length = int(getattr(c, 'length', 0))
    items.append((name, start, end, length))
  items.sort()
  return ';'.join(f'{n}:{s}->{e}:{l}' for n, s, e, l in items)


@dataclasses.dataclass(frozen=True, kw_only=True)
class BenchmarkRecord:
  """Detailed per-tree benchmark record."""

  tree_name: str
  tree_index: int | None = None
  stick_signature: str | None = None
  packer: str
  pack_status: str  # 'success', 'failed', 'timeout', 'error', 'unavailable'
  pack_time_s: float
  grid_size: int | None = None
  unused_area: int | None = None
  validation_passed: bool = False
  validation_error: str | None = None
  solvability_passed: bool = False
  solvability_reason: str | None = None
  step0_solvable: bool = False
  step0_reason: str | None = None
  river_types: tuple[str, ...] = ()
  solve_status: str = (
      'skipped'  # 'solved', 'unsolved', 'timeout', 'skipped', 'error'
  )
  solve_time_s: float = 0.0
  solve_steps: int = 0
  globally_flat_foldable: bool | None = None
  errors: tuple[str, ...] = ()
  load_start: tuple[float, float, float] = (0.0, 0.0, 0.0)
  load_end: tuple[float, float, float] = (0.0, 0.0, 0.0)
  is_load_suspect: bool = False
  packed_obj: Any = None
  solved_obj: Any = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class BenchmarkSummary:
  """Aggregate benchmark metrics for a single packer over a dataset."""

  packer: str
  total_trees: int
  pack_success_count: int
  pack_yield: float
  validation_pass_count: int
  validation_yield: float
  solvability_pass_count: int
  solvability_yield: float
  step0_pass_count: int
  step0_yield: float
  solve_success_count: int
  solve_yield: float
  flat_foldable_count: int
  flat_foldable_yield: float
  mean_pack_time_s: float
  mean_solve_time_s: float
  mean_grid_size: float
  river_type_counts: dict[str, int] = dataclasses.field(default_factory=dict)
  river_type_solve_yields: dict[str, float] = dataclasses.field(
      default_factory=dict
  )
  records: list[BenchmarkRecord] = dataclasses.field(default_factory=list)


def extract_river_types(
    packing_output: packing_output_lib.PackingOutput,
) -> tuple[str, ...]:
  """Extracts standardized river types present in a PackingOutput."""
  if not packing_output.tracker or not packing_output.tracker.packed_rivers:
    return ()
  types_list: list[str] = []
  for r in packing_output.tracker.packed_rivers.values():
    rtype = getattr(r, 'river_type', None)
    if rtype is None:
      if isinstance(r, river_lib.River):
        rtype = 'straight'
      elif isinstance(r, river_lib.LShapedRiver):
        rtype = 'l_shaped'
      elif isinstance(r, river_lib.HuggingRiver):
        rtype = 'hugging'
      elif hasattr(r, 'rectangles') and len(r.rectangles) == 1:
        rtype = 'straight'
      elif hasattr(r, 'rectangles') and len(r.rectangles) == 2:
        rtype = 'l_shaped'
      else:
        rtype = 'hugging'
    types_list.append(str(rtype))
  return tuple(sorted(types_list))


def check_step0_solvability(
    packing_output: packing_output_lib.PackingOutput,
    tree: stick_figure_lib.StickFigure,
    solver_config: Any | None = None,
) -> tuple[bool, str | None]:
  """Checks Step-0 hinge/vertex solvability across the solver cascade."""
  design = bus.DesignTree.from_stick_figure(tree) if tree is not None else None
  res = solvability.is_bankable(
      packing_output, design=design, solver_config=solver_config
  )
  if not res.ok:
    return False, '; '.join(res.reasons)
  return True, None


def _run_default_packer(
    tree: stick_figure_lib.StickFigure,
    timeout_s: float,
    max_number_of_cps: int,
) -> tuple[packing_output_lib.PackingOutput | None, float, list[str]]:
  """Runs the standard iterative backtracking packer."""
  pack_cfg = pipeline.PackingTaskConfig(
      max_cps_per_grid_size=1,
      max_number_of_cps=max_number_of_cps,
      timeout_seconds=timeout_s,
      packing_config=packing_config_lib.PackingConfig(
          use_level_shifter=False,
          enforce_proximity_constraints=False,
      ),
  )
  start_time = time.perf_counter()
  try:
    result = pipeline.pack_crease_pattern(tree, config=pack_cfg)
    elapsed = time.perf_counter() - start_time
    if result.packing_outputs:
      return result.packing_outputs[0], elapsed, list(result.errors_per_retry)
    return (
        None,
        elapsed,
        list(result.errors_per_retry) or ['No packing outputs generated'],
    )
  except Exception as e:  # pylint: disable=broad-exception-caught
    elapsed = time.perf_counter() - start_time
    return None, elapsed, [str(e)]


def _run_stacking_packer(
    tree: stick_figure_lib.StickFigure,
) -> tuple[packing_output_lib.PackingOutput | None, float, list[str]]:
  """Runs the 1D strip stacking packer."""
  from . import stacking as stacking_lib  # pylint: disable=g-import-not-at-top

  start_time = time.perf_counter()
  try:
    output = stacking_lib.pack_stick_figure_with_stacking(
        copy.deepcopy(tree),
        force_asymmetric=False,
    )
    elapsed = time.perf_counter() - start_time
    return output, elapsed, []
  except Exception as e:  # pylint: disable=broad-exception-caught
    elapsed = time.perf_counter() - start_time
    return None, elapsed, [str(e)]


def benchmark_single_tree(
    tree: stick_figure_lib.StickFigure | str,
    packer: (
        PackerType
        | str
        | Callable[
            [stick_figure_lib.StickFigure],
            packing_output_lib.PackingOutput | None,
        ]
    ) = 'default',
    *,
    timeout_s: float = 30.0,
    solve_max_steps: int = 1000,
    max_number_of_cps: int = 1,
    tree_index: int | None = None,
    stick_signature: str | None = None,
) -> BenchmarkRecord:
  """Benchmarks a single stick figure through packing and solving."""
  if isinstance(tree, str):
    tree_obj = example_trees.get_example_by_name(tree)
  else:
    tree_obj = copy.deepcopy(tree)
  tree_name = getattr(tree_obj, 'name', 'unnamed_tree')
  stick_sig = (
      stick_signature
      if stick_signature is not None
      else compute_stick_signature(tree_obj)
  )
  load_start = os.getloadavg()

  def make_record(**kwargs: Any) -> BenchmarkRecord:
    load_end = os.getloadavg()
    cpu_threshold = float(os.cpu_count() or 4)
    is_load_suspect = (
        load_start[0] > cpu_threshold or load_end[0] > cpu_threshold
    )
    return BenchmarkRecord(
        tree_name=tree_name,
        tree_index=tree_index,
        stick_signature=stick_sig,
        packer=packer_name,
        load_start=load_start,
        load_end=load_end,
        is_load_suspect=is_load_suspect,
        **kwargs,
    )

  packing_output: packing_output_lib.PackingOutput | None = None
  pack_time_s: float = 0.0
  pack_errors: list[str] = []

  if callable(packer):
    start_time = time.perf_counter()
    try:
      output = packer(copy.deepcopy(tree_obj))
      pack_time_s = time.perf_counter() - start_time
      if output is not None and not getattr(output, 'success', True):
        pack_errors.append(
            getattr(output, 'error_message', None) or 'Packer failed'
        )
      else:
        packing_output = output
    except Exception as e:  # pylint: disable=broad-exception-caught
      pack_time_s = time.perf_counter() - start_time
      pack_errors.append(str(e))
    packer_name = getattr(packer, '__name__', 'custom_packer')
  else:
    packer_name = str(packer)
    match packer_name:
      case 'default':
        packing_output, pack_time_s, pack_errors = _run_default_packer(
            tree_obj, timeout_s, max_number_of_cps
        )
      case 'stacking':
        packing_output, pack_time_s, pack_errors = _run_stacking_packer(
            tree_obj
        )
      case _:
        from bp_pipeline import plugins  # pylint: disable=g-import-not-at-top

        packer_fn = plugins.get_packer(packer_name)
        if packer_fn is not None:
          start_time = time.perf_counter()
          try:
            design = bus.DesignTree.from_stick_figure(tree_obj)
            output = packer_fn(design, timeout_seconds=timeout_s)
            pack_time_s = time.perf_counter() - start_time
            if output is not None and not getattr(output, 'success', True):
              pack_errors.append(
                  getattr(output, 'error_message', None) or 'Packer failed'
              )
            else:
              packing_output = output
          except Exception as e:  # pylint: disable=broad-exception-caught
            pack_time_s = time.perf_counter() - start_time
            pack_errors.append(str(e))
        else:
          return make_record(
              pack_status='error',
              pack_time_s=0.0,
              errors=(f'Unsupported or unregistered packer {packer_name!r}',),
          )

  if packing_output is None:
    status = (
        'timeout'
        if any('timeout' in err.lower() for err in pack_errors)
        else 'failed'
    )
    if any('not yet available' in err.lower() for err in pack_errors):
      status = 'unavailable'
    return make_record(
        pack_status=status,
        pack_time_s=pack_time_s,
        errors=tuple(pack_errors),
    )

  grid_size: int | None = None
  if (
      packing_output.packing_cp
      and packing_output.packing_cp.grid_size is not None
  ):
    grid_size = int(packing_output.packing_cp.grid_size)
  unused_area: int | None = (
      int(packing_output.details.get('unused_area', 0))
      if packing_output.details
      else None
  )
  river_types = extract_river_types(packing_output)

  validation_passed = False
  validation_error: str | None = None
  try:
    packing_output.validate()
    validation_passed = True
  except Exception as e:  # pylint: disable=broad-exception-caught
    validation_passed = False
    validation_error = str(e)

  solvability_passed = False
  solvability_reason: str | None = None
  if packing_output.packing_cp:
    solv_res = solvability.check_solvability(packing_output.packing_cp)
    solvability_passed = solv_res.is_solvable
    solvability_reason = solv_res.reason

  step0_solvable, step0_reason = check_step0_solvability(
      packing_output, tree_obj
  )

  solve_status = 'skipped'
  solve_time_s = 0.0
  solve_steps = 0
  globally_flat_foldable: bool | None = None
  solve_errors: list[str] = []
  solved_cp: Any = None

  if packing_output.packing_cp and grid_size is not None:
    solve_cfg = pipeline.SolvingTaskConfig(
        max_number_of_cps=1,
        max_steps=solve_max_steps,
        use_python_flat_folder=True,
        timeout_seconds=timeout_s,
    )
    solve_start = time.perf_counter()
    try:
      sf_input = pipeline.process_stick_figure(tree_obj)
      pack_res = pipeline.PackingResult(
          name=tree_name,
          packing_cps=[packing_output.packing_cp],
          packing_outputs=[packing_output],
          attempted_grid_sizes=[grid_size],
          time_spent_per_grid_sizes=[pack_time_s],
          sequence_status='SUCCESS in CREASE_PATTERN_PACKING',
          duration_seconds=pack_time_s,
          stick_figure_input=sf_input,
          packing_config=pipeline.PackingTaskConfig(),
      )
      solve_result = pipeline.solve_crease_pattern(pack_res, config=solve_cfg)
      solve_time_s = time.perf_counter() - solve_start
      solve_errors.extend(solve_result.solver_errors)

      if solve_result.flat_foldable_cps_count > 0:
        solve_status = 'solved'
        solved_cp = solve_result.flat_foldable_cps[0]
        try:
          globally_flat_foldable = global_foldability.is_globally_flat_foldable(
              solved_cp,
              scale=1,
              ndigits=3,
              grid=solved_cp.grid_size,
          )
        except Exception:  # pylint: disable=broad-exception-caught
          globally_flat_foldable = None

        if solve_result.solver_outputs:
          sol_out = solve_result.solver_outputs[0]
          solve_steps = (
              getattr(sol_out, 'step_count', None)
              or getattr(sol_out.final_state, 'step_count', None)
              or 1
          )
      else:
        solve_status = (
            'timeout'
            if any('timeout' in err.lower() for err in solve_errors)
            else 'unsolved'
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
      solve_time_s = time.perf_counter() - solve_start
      solve_status = 'error'
      solve_errors.append(str(e))

  return make_record(
      pack_status='success',
      pack_time_s=pack_time_s,
      grid_size=grid_size,
      unused_area=unused_area,
      validation_passed=validation_passed,
      validation_error=validation_error,
      solvability_passed=solvability_passed,
      solvability_reason=solvability_reason,
      step0_solvable=step0_solvable,
      step0_reason=step0_reason,
      river_types=river_types,
      solve_status=solve_status,
      solve_time_s=solve_time_s,
      solve_steps=solve_steps,
      globally_flat_foldable=globally_flat_foldable,
      errors=tuple(pack_errors + solve_errors),
      packed_obj=packing_output.packing_cp if packing_output else None,
      solved_obj=solved_cp if solve_status == 'solved' else None,
  )


def summarize_records(
    records: Sequence[BenchmarkRecord], packer: str
) -> BenchmarkSummary:
  """Aggregates a sequence of BenchmarkRecords into a BenchmarkSummary."""
  total = len(records)
  if total == 0:
    return BenchmarkSummary(
        packer=packer,
        total_trees=0,
        pack_success_count=0,
        pack_yield=0.0,
        validation_pass_count=0,
        validation_yield=0.0,
        solvability_pass_count=0,
        solvability_yield=0.0,
        step0_pass_count=0,
        step0_yield=0.0,
        solve_success_count=0,
        solve_yield=0.0,
        flat_foldable_count=0,
        flat_foldable_yield=0.0,
        mean_pack_time_s=0.0,
        mean_solve_time_s=0.0,
        mean_grid_size=0.0,
        records=[],
    )

  pack_success = [r for r in records if r.pack_status == 'success']
  pack_success_count = len(pack_success)
  validation_pass_count = sum(1 for r in pack_success if r.validation_passed)
  solvability_pass_count = sum(1 for r in pack_success if r.solvability_passed)
  step0_pass_count = sum(1 for r in pack_success if r.step0_solvable)
  solve_success_count = sum(1 for r in records if r.solve_status == 'solved')
  flat_foldable_count = sum(1 for r in records if r.globally_flat_foldable)

  mean_pack_time = sum(r.pack_time_s for r in records) / total
  mean_solve_time = (
      sum(r.solve_time_s for r in pack_success) / pack_success_count
      if pack_success_count > 0
      else 0.0
  )
  grid_sizes = [r.grid_size for r in pack_success if r.grid_size is not None]
  mean_grid_size = sum(grid_sizes) / len(grid_sizes) if grid_sizes else 0.0

  river_type_counts: dict[str, int] = {}
  river_type_solved: dict[str, int] = {}
  for r in pack_success:
    rtypes = set(r.river_types) if r.river_types else {'none'}
    for rt in rtypes:
      river_type_counts[rt] = river_type_counts.get(rt, 0) + 1
      if r.solve_status == 'solved':
        river_type_solved[rt] = river_type_solved.get(rt, 0) + 1

  river_type_solve_yields = {
      rt: river_type_solved.get(rt, 0) / count
      for rt, count in river_type_counts.items()
      if count > 0
  }

  return BenchmarkSummary(
      packer=packer,
      total_trees=total,
      pack_success_count=pack_success_count,
      pack_yield=pack_success_count / total,
      validation_pass_count=validation_pass_count,
      validation_yield=validation_pass_count / total,
      solvability_pass_count=solvability_pass_count,
      solvability_yield=solvability_pass_count / total,
      step0_pass_count=step0_pass_count,
      step0_yield=step0_pass_count / total,
      solve_success_count=solve_success_count,
      solve_yield=solve_success_count / total,
      flat_foldable_count=flat_foldable_count,
      flat_foldable_yield=flat_foldable_count / total,
      mean_pack_time_s=mean_pack_time,
      mean_solve_time_s=mean_solve_time,
      mean_grid_size=mean_grid_size,
      river_type_counts=river_type_counts,
      river_type_solve_yields=river_type_solve_yields,
      records=list(records),
  )


def run_benchmark_suite(
    trees: Sequence[stick_figure_lib.StickFigure | str],
    packers: Sequence[
        PackerType
        | str
        | Callable[
            [stick_figure_lib.StickFigure],
            packing_output_lib.PackingOutput | None,
        ]
    ] = ('default',),
    *,
    timeout_s: float = 30.0,
    solve_max_steps: int = 1000,
    max_workers: int = 1,
) -> dict[str, BenchmarkSummary]:
  """Runs a comprehensive comparative benchmark across trees and packers."""
  summaries: dict[str, BenchmarkSummary] = {}

  for packer in packers:
    packer_name = (
        packer
        if isinstance(packer, str)
        else getattr(packer, '__name__', 'custom')
    )
    records: list[BenchmarkRecord] = []

    if max_workers > 1:
      with concurrent.futures.ThreadPoolExecutor(
          max_workers=min(max_workers, 8)
      ) as executor:
        futures = {
            executor.submit(
                benchmark_single_tree,
                tree,
                packer=packer,
                timeout_s=timeout_s,
                solve_max_steps=solve_max_steps,
                tree_index=idx,
                stick_signature=compute_stick_signature(tree),
            ): (idx, tree)
            for idx, tree in enumerate(trees)
        }
        for future in concurrent.futures.as_completed(futures):
          try:
            records.append(future.result())
          except Exception as e:  # pylint: disable=broad-exception-caught
            idx, tree_item = futures[future]
            tname = (
                tree_item
                if isinstance(tree_item, str)
                else getattr(tree_item, 'name', 'unnamed')
            )
            records.append(
                BenchmarkRecord(
                    tree_name=tname,
                    tree_index=idx,
                    stick_signature=compute_stick_signature(tree_item),
                    packer=packer_name,
                    pack_status='error',
                    pack_time_s=0.0,
                    errors=(f'Worker execution exception: {e}',),
                )
            )
    else:
      for idx, tree in enumerate(trees):
        records.append(
            benchmark_single_tree(
                tree,
                packer=packer,
                timeout_s=timeout_s,
                solve_max_steps=solve_max_steps,
                tree_index=idx,
                stick_signature=compute_stick_signature(tree),
            )
        )

    records.sort(
        key=lambda r: (
            r.tree_index if r.tree_index is not None else 0,
            r.tree_name,
        )
    )

    summaries[packer_name] = summarize_records(records, packer_name)

  return summaries


def format_benchmark_table(
    summaries: Mapping[str, BenchmarkSummary] | Sequence[BenchmarkSummary],
) -> str:
  """Formats benchmark summaries into a GitHub-style Markdown table."""
  if isinstance(summaries, Mapping):
    items = list(summaries.values())
  else:
    items = list(summaries)

  headers = [
      'Packer',
      'Total',
      'Pack Yield',
      'Valid Yield',
      'Solv Check',
      'Step-0 Gate',
      'Solve @1k',
      'Flat Fold',
      'Mean Pack (s)',
      'Mean Solve (s)',
      'Mean G',
  ]
  rows: list[list[str]] = []
  for s in items:
    rows.append([
        s.packer,
        str(s.total_trees),
        f'{s.pack_success_count}/{s.total_trees} ({s.pack_yield * 100:.1f}%)',
        (
            f'{s.validation_pass_count}/{s.total_trees}'
            f' ({s.validation_yield * 100:.1f}%)'
        ),
        (
            f'{s.solvability_pass_count}/{s.total_trees}'
            f' ({s.solvability_yield * 100:.1f}%)'
        ),
        f'{s.step0_pass_count}/{s.total_trees} ({s.step0_yield * 100:.1f}%)',
        f'{s.solve_success_count}/{s.total_trees} ({s.solve_yield * 100:.1f}%)',
        (
            f'{s.flat_foldable_count}/{s.total_trees}'
            f' ({s.flat_foldable_yield * 100:.1f}%)'
        ),
        f'{s.mean_pack_time_s:.2f}',
        f'{s.mean_solve_time_s:.2f}',
        f'{s.mean_grid_size:.1f}',
    ])

  col_widths = [len(h) for h in headers]
  for row in rows:
    for i, cell in enumerate(row):
      col_widths[i] = max(col_widths[i], len(cell))

  header_line = (
      '| '
      + ' | '.join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
      + ' |'
  )
  sep_line = (
      '| ' + ' | '.join('-' * col_widths[i] for i in range(len(headers))) + ' |'
  )
  data_lines = [
      '| '
      + ' | '.join(cell.ljust(col_widths[i]) for i, cell in enumerate(row))
      + ' |'
      for row in rows
  ]
  return '\n'.join([header_line, sep_line] + data_lines)


def format_river_breakdown_table(summary: BenchmarkSummary) -> str:
  """Formats river-type solve yield breakdown as a Markdown table."""
  headers = ['River Geometry', 'Count', 'Solve Yield @ 1000 steps']
  rows: list[list[str]] = []
  for rt, count in sorted(summary.river_type_counts.items()):
    yld = summary.river_type_solve_yields.get(rt, 0.0)
    rows.append([rt, str(count), f'{yld * 100:.1f}%'])

  col_widths = [len(h) for h in headers]
  for row in rows:
    for i, cell in enumerate(row):
      col_widths[i] = max(col_widths[i], len(cell))

  header_line = (
      '| '
      + ' | '.join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
      + ' |'
  )
  sep_line = (
      '| ' + ' | '.join('-' * col_widths[i] for i in range(len(headers))) + ' |'
  )
  data_lines = [
      '| '
      + ' | '.join(cell.ljust(col_widths[i]) for i, cell in enumerate(row))
      + ' |'
      for row in rows
  ]
  return '\n'.join([header_line, sep_line] + data_lines)


def load_dataset(
    name_or_path: str = 'example_trees',
    max_count: int | None = None,
) -> list[stick_figure_lib.StickFigure]:
  """Loads trees for benchmarking from example_trees or a JSONL dataset."""
  if name_or_path == 'example_trees':
    trees = list(example_trees.list_examples())
    return trees[:max_count] if max_count is not None else trees

  candidate_paths: list[str] = []
  if os.path.exists(name_or_path):
    candidate_paths.append(name_or_path)

  loaded_trees: list[stick_figure_lib.StickFigure] = []
  for path in candidate_paths:
    if os.path.exists(path):
      with open(path, 'r', encoding='utf-8') as f:
        for line in f:
          line = line.strip()
          if not line:
            continue
          try:
            tree = stick_figure_lib.StickFigure.from_json(line)
            loaded_trees.append(tree)
            if max_count is not None and len(loaded_trees) >= max_count:
              return loaded_trees
          except Exception as e:  # pylint: disable=broad-exception-caught
            logging.warning('Could not parse stick figure from JSONL: %s', e)
      if loaded_trees:
        return loaded_trees

  # Fallback if dataset file is not locally available.
  logging.warning(
      'Could not load %s from path %r; falling back to example_trees',
      name_or_path,
      name_or_path,
  )
  fallback = list(example_trees.list_examples())
  return fallback[:max_count] if max_count is not None else fallback
