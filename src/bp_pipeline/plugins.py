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

"""Pluggable engine registry for custom packers and hinge solvers."""

from collections.abc import Callable
from typing import Any

# Signature for high-level bp.pack() / benchmark plugins:
# (design, *, config, grid_size, max_solutions, timeout_seconds,
#  per_grid_timeout_seconds, num_workers, packer_config,
#  solution_callback) -> PackingOutput
PackerPluginFn = Callable[..., Any]

# Optional signature for single-grid pipeline._attempt_packing() plugins:
# (stick_figure_input, *, grid_size, is_symmetric, allow_paired_axis_placement,
#  max_solutions, config, solution_callback, packer_config)
#  -> list[PackingOutput]
GridPackerPluginFn = Callable[..., list[Any]]

# Signature for hinges.Solver.iter_solutions() plugins:
# (init_state, borders, config, *, source_cp) -> tuple[list[SolverResult], Any]
SolverPluginFn = Callable[..., tuple[list[Any], Any]]

_PACKERS: dict[str, PackerPluginFn] = {}
_GRID_PACKERS: dict[str, GridPackerPluginFn] = {}
_SOLVERS: dict[str, SolverPluginFn] = {}
_SOLVER_REQUIRES_RECOVERY: set[str] = set()


def register_packer(
    name: str,
    fn: PackerPluginFn,
    *,
    grid_fn: GridPackerPluginFn | None = None,
) -> None:
  """Registers an external packing engine."""
  _PACKERS[name] = fn
  if grid_fn is not None:
    _GRID_PACKERS[name] = grid_fn


def get_packer(name: str) -> PackerPluginFn | None:
  """Returns the registered packing engine function, or None."""
  return _PACKERS.get(name)


def get_grid_packer(name: str) -> GridPackerPluginFn | None:
  """Returns the registered single-grid packer function, or None."""
  return _GRID_PACKERS.get(name)


def list_packers() -> tuple[str, ...]:
  """Returns the names of all available packing engines."""
  return ('default',) + tuple(_PACKERS.keys())


def register_solver(
    name: str,
    fn: SolverPluginFn,
    *,
    requires_recovery: bool = False,
) -> None:
  """Registers an external hinge/crease pattern solver engine."""
  _SOLVERS[name] = fn
  if requires_recovery:
    _SOLVER_REQUIRES_RECOVERY.add(name)
  else:
    _SOLVER_REQUIRES_RECOVERY.discard(name)


def get_solver(name: str) -> SolverPluginFn | None:
  """Returns the registered solver engine function, or None."""
  return _SOLVERS.get(name)


def solver_requires_recovery(name: str) -> bool:
  """Returns whether the registered solver requires recovery preprocessing."""
  return name in _SOLVER_REQUIRES_RECOVERY


def list_solvers() -> tuple[str, ...]:
  """Returns the names of all available hinge/crease pattern solvers."""
  return ('default',) + tuple(_SOLVERS.keys())
