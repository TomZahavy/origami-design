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

"""Utils (Flaps and pockets) for stick figures."""

import collections
import itertools
import logging
from typing import TypedDict

from ..packing import config as config_lib
from ..packing import types
from . import stick as stick_lib
from . import stick_figure as sf
from . import traversal


class FlapPocket(TypedDict):
  """Represents a pocket of flaps and their boundary rivers.

  Attributes:
    flaps: A list of Stick objects in the pocket.
    flap_names: A set of stick names in the pocket.
    boundary_rivers: A set of river stick names bordering the pocket.
  """

  flaps: list[stick_lib.Stick]
  flap_names: set[str]
  boundary_rivers: set[str]


def get_pocket_area(
    pocket: FlapPocket,
    stick: stick_lib.Stick,
    side_areas: dict[str, float],
    joint_to_side: dict[str, str],
) -> float:
  """Returns area of river side where pocket should be placed.

  Args:
    pocket: The flap pocket to compute area for.
    stick: The river stick.
    side_areas: A dict mapping side name to area.
    joint_to_side: A dict mapping joint name to side name.

  Returns:
    The area of river side where pocket should be placed.
  """
  pocket_joints = set()
  for f in pocket['flaps']:
    pocket_joints.add(f.start)
    pocket_joints.add(f.end)
  shared_with_start = stick.start in pocket_joints
  shared_with_end = stick.end in pocket_joints
  pocket_joint_name = None
  if shared_with_start and not shared_with_end:
    pocket_joint_name = stick.start
  elif shared_with_end and not shared_with_start:
    pocket_joint_name = stick.end

  if pocket_joint_name and pocket_joint_name in joint_to_side:
    return side_areas[joint_to_side[pocket_joint_name]]
  return float('inf')


def make_pocket(
    stick_figure: sf.StickFigure,
    flaps: list[stick_lib.Stick],
) -> FlapPocket | None:
  """Creates a FlapPocket from a list of flaps.

  Args:
    stick_figure: The StickFigure containing the joints and sticks.
    flaps: A list of connected Stick objects forming a pocket.

  Returns:
    A FlapPocket dict, or None if flaps is empty.
  """
  if not flaps:
    return None
  boundaries = set()
  for s in flaps:
    for joint_name in [s.start, s.end]:
      if joint_name in stick_figure.joints:
        for neighbor in stick_figure.joints[joint_name].sticks:
          if neighbor.is_river:
            boundaries.add(neighbor.name)
  return {
      'flaps': flaps,
      'flap_names': {s.name for s in flaps},
      'boundary_rivers': boundaries,
  }


def _compute_sector_adjacency(
    stick_figure: sf.StickFigure,
) -> collections.defaultdict[str, set[str]]:
  """Builds flap adjacency respecting angular sectors between rivers.

  At joints with fewer than two rivers, all non-river sticks are adjacent.
  At joints with two or more rivers, the angularly-sorted sticks are walked
  and grouped into sectors separated by rivers; only sticks in the same
  sector are considered adjacent.

  Args:
    stick_figure: The StickFigure to analyze.

  Returns:
    A dict mapping each flap stick name to the set of flap stick names it
    is adjacent to (through shared joints).
  """
  adjacency: collections.defaultdict[str, set[str]] = collections.defaultdict(
      set
  )
  for joint in stick_figure.joints.values():
    river_indices = [i for i, s in enumerate(joint.sticks) if s.is_river]

    if len(river_indices) < 2:
      flaps_at_joint = [s.name for s in joint.sticks if not s.is_river]
      for flap_name in flaps_at_joint:
        adjacency[flap_name].update(flaps_at_joint)
    else:
      n = len(joint.sticks)
      sectors: list[list[str]] = []
      for k, start_idx in enumerate(river_indices):
        end_idx = river_indices[(k + 1) % len(river_indices)]
        sector: list[str] = []
        sticks_after_start = itertools.islice(
            itertools.cycle(joint.sticks), start_idx + 1, start_idx + n
        )
        for s in sticks_after_start:
          if s is joint.sticks[end_idx]:
            break
          if not s.is_river:
            sector.append(s.name)
        if sector:
          sectors.append(sector)

      for sector in sectors:
        for flap_name in sector:
          adjacency[flap_name].update(sector)

  return adjacency


def _compute_pockets(
    stick_figure: sf.StickFigure,
    use_sectors: bool = False,
    *,
    legacy_iteration_order: bool = False,
) -> list[FlapPocket]:
  """Computes connected components of non-river sticks.

  When ``use_sectors`` is True, flaps at joints with multiple rivers are
  split into angular sectors between rivers so that flaps in different
  sectors are not connected.

  Args:
    stick_figure: The StickFigure to analyze.
    use_sectors: Whether to split flaps into angular sectors at multi-river
      joints.
    legacy_iteration_order: Whether to iterate set neighbors directly instead of
      sorting by stick name.

  Returns:
      A list of FlapPocket dicts.
  """
  flap_sticks = [s for s in stick_figure.children if not s.is_river]
  if not flap_sticks:
    return []

  if use_sectors:
    adjacency = _compute_sector_adjacency(stick_figure)
  else:
    adjacency: dict[str, set[str]] = collections.defaultdict(set)
    for stick in flap_sticks:
      for joint_name in [stick.start, stick.end]:
        for other in stick_figure.joints[joint_name].sticks:
          if not other.is_river:
            adjacency[stick.name].add(other.name)

  visited: set[str] = set()
  pockets: list[FlapPocket] = []

  for seed in flap_sticks:
    if seed.name in visited:
      continue
    component = []
    queue = collections.deque([seed])
    visited.add(seed.name)
    while queue:
      current = queue.popleft()
      component.append(current)
      neighbors = (
          adjacency[current.name]
          if legacy_iteration_order
          else sorted(adjacency[current.name])
      )
      for neighbor_name in neighbors:
        if neighbor_name not in visited:
          visited.add(neighbor_name)
          queue.append(stick_figure[neighbor_name])

    pocket = make_pocket(stick_figure, component)
    if pocket is not None:
      pockets.append(pocket)

  return pockets


def precompute_flap_pockets(
    stick_figure: sf.StickFigure,
    config: config_lib.PackingConfig,
) -> list[FlapPocket]:
  """Identifies groups of connected non-river sticks and their river boundaries.

  A "flap pocket" is a connected component of non-river sticks in the stick
  figure's topology. Two non-river sticks are in the same pocket if they share
  a joint and can reach each other through other non-river sticks (without
  crossing a river).

  Args:
    stick_figure: The StickFigure to analyze.
    config: The packing configuration.

  Returns:
      A list of FlapPocket dicts.
  """
  use_sectors = config.traversal_mode == types.TraversalMode.PROXIMITY
  return _compute_pockets(
      stick_figure,
      use_sectors=use_sectors,
      legacy_iteration_order=config.legacy_iteration_order,
  )


def precompute_flap_pockets_for_symmetric_half(
    *,
    half_figure: sf.StickFigure,
    full_figure: sf.StickFigure,
    config: config_lib.PackingConfig,
) -> list[FlapPocket]:
  """Computes pockets on the full figure, filtered to the symmetric half.

  This is useful when ``half_figure`` is a symmetric half where a removed
  river would otherwise merge two distinct pockets.

  Args:
    half_figure: The symmetric half StickFigure.
    full_figure: The full (unsplit) StickFigure.
    config: The packing configuration.

  Returns:
      A list of FlapPocket dicts containing only flaps in ``half_figure``.
  """
  use_sectors = config.traversal_mode == types.TraversalMode.PROXIMITY
  half_flap_names = {s.name for s in half_figure.children if not s.is_river}
  full_pockets = _compute_pockets(
      full_figure,
      use_sectors=use_sectors,
      legacy_iteration_order=config.legacy_iteration_order,
  )

  filtered: list[FlapPocket] = []
  for pocket in full_pockets:
    kept_flaps = [f for f in pocket['flaps'] if f.name in half_flap_names]
    if kept_flaps:
      pocket = make_pocket(half_figure, kept_flaps)
      if pocket is not None:
        filtered.append(pocket)
  return filtered


def get_half_figure_and_start_stick_for_symmetric_packing(
    stick_figure: sf.StickFigure,
) -> tuple[sf.StickFigure, str | None]:
  """If stick_figure is symmetric, returns its half and symmetric start stick name.

  If stick_figure is not symmetric, it returns itself and None.
  This is used to setup symmetric packing, which runs on half of the figure
  but needs to determine the start stick based on symmetric joints of the full
  figure.

  Args:
    stick_figure: The potentially symmetric stick figure.

  Returns:
    A tuple of (figure_to_traverse, start_stick_name).
  """
  if not stick_figure.is_symmetric_tree:
    return stick_figure, None

  half_figure = stick_figure.get_symmetric_half()
  symmetric_joints = stick_figure.get_symmetric_connecting_joints()
  start_stick_name = None
  if symmetric_joints:
    start_joint_name = symmetric_joints[0]
    if start_joint_name in half_figure.joints:
      start_stick = traversal.find_start_stick_for_proximity_traversal(
          half_figure, start_joint_name
      )
      start_stick_name = start_stick.name
    else:
      logging.warning(
          'Symmetric connecting joint %s not in half figure, cannot determine'
          ' start stick.',
          start_joint_name,
      )
  return half_figure, start_stick_name
