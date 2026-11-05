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

"""Functions for traversing stick figures."""

import collections
from collections.abc import Iterator, Mapping
import typing

from absl import logging

from ..packing import types as packing_types
from . import angle_utils
from . import stick as stick_lib
from . import stick_figure as sf


def stick_parent_pairs_dfs(
    tree: sf.StickFigure,
) -> Iterator[tuple[stick_lib.Stick, stick_lib.Stick | None]]:
  """Yields (stick, parent) tuples using DFS traversal of the stick figure."""

  stack = [(tree[tree.root], None)]
  visited = {tree.root}
  while stack:
    stick, parent = stack.pop()
    yield stick, parent
    for joint_name in [stick.start, stick.end]:
      if joint_name in tree.joints:
        for neighbor in reversed(tree.joints[joint_name].sticks):
          if neighbor.name not in visited:
            visited.add(neighbor.name)
            stack.append((neighbor, stick))  # pyrefly: ignore[bad-argument-type]


def get_sticks_relative_angles(
    tree: sf.StickFigure,
) -> list[tuple[str, tuple[float, float]]]:
  """Returns a list of stick names and relative (azimuth, elevation) angles.

  Args:
    tree: The stick figure to get sticks' the relative angles for.

  Returns:
    A list of (stick name, (relative azimuth, relative elevation)) tuples. The
    list is ordered by the DFS traversal of the tree from the root stick. Angles
    are relative to the parent stick.
  """

  angle_map = []
  for stick, parent in stick_parent_pairs_dfs(tree):
    if parent is None:
      angle_map.append((stick.name, (0.0, 0.0)))
    else:
      rel_azimuth = stick.azimuth_angle - parent.azimuth_angle
      rel_elevation = stick.elevation_angle - parent.elevation_angle

      angle_map.append((
          stick.name,
          (
              angle_utils.wrap_angle_centered(rel_azimuth, 360),
              angle_utils.wrap_angle_centered(rel_elevation, 360),
          ),
      ))
  return angle_map


def breadth_first_traversal(
    stick_figure: sf.StickFigure,
    start_joint: str | None = None,
    start_stick_name: str | None = None,
    excluded_stick_names: set[str] | None = None,
) -> Iterator[stick_lib.Stick]:
  """Yields stick children in breadth-first order from a given starting stick or joint.

  If no start is provided, it starts with the root stick.

  Args:
    stick_figure: The stick figure to traverse.
    start_joint: The name of the joint to start traversal from.
    start_stick_name: The name of the stick to start traversal from. Defaults to
      the root stick.
    excluded_stick_names: A set of stick names to exclude from traversal.

  Yields:
    Sticks in breadth-first order.
  """
  excluded_stick_names = excluded_stick_names or set()
  queue = collections.deque()
  visited_stick_names = set()

  def _add_to_queue_if_unvisited(stick: stick_lib.Stick):
    """Adds a stick to the queue if it hasn't been visited or excluded."""
    if (
        stick.name not in visited_stick_names
        and stick.name not in excluded_stick_names
    ):
      visited_stick_names.add(stick.name)
      queue.append(stick)

  # Get initial sticks to start traversal from.
  if start_joint is not None:  # joint was provided
    if start_joint in stick_figure.joints:
      for stick in stick_figure.joints[start_joint].sticks:
        _add_to_queue_if_unvisited(stick)
  else:
    # If no start joint, start with a single stick.
    start_stick = stick_figure[start_stick_name or stick_figure.root]
    _add_to_queue_if_unvisited(start_stick)

  while queue:
    stick = queue.popleft()
    yield stick

    for joint_name in (stick.start, stick.end):
      if joint_name in stick_figure.joints:
        for neighbor_stick in stick_figure.joints[joint_name].sticks:
          _add_to_queue_if_unvisited(neighbor_stick)


def get_sticks_from_river_side(
    stick_figure: sf.StickFigure,
    start_joint: str,
    excluded_stick: stick_lib.Stick,
    sticks_to_exclude: set[str],
) -> list[stick_lib.Stick]:
  """Returns a list of sticks on one side of a river.

  It performs a BFS graph traversal starting from start_joint,
  not crossing excluded_stick, and not including any stick in
  sticks_to_exclude.

  Args:
    stick_figure: The stick figure to traverse.
    start_joint: The name of the joint to start traversal from.
    excluded_stick: The stick to not cross during traversal (the river stick).
    sticks_to_exclude: A set of stick names to exclude from traversal and
      summation (sticks traversed before previous river).

  Returns:
    A list of sticks reachable from start_joint.
  """
  excluded_stick_names = sticks_to_exclude | {excluded_stick.name}
  return list(
      breadth_first_traversal(
          stick_figure,
          start_joint=start_joint,
          excluded_stick_names=excluded_stick_names,
      )
  )


def _navigate_rivers_to_start_joint(
    stick_figure: sf.StickFigure,
    start_joint_name: str,
    start_river: stick_lib.Stick,
) -> tuple[str, stick_lib.Stick]:
  """Follows rivers counter-clockwise until a joint with only one river is found.

  This function is used to find the start joint for river-priority traversal.
  If the initially chosen start joint has only one river connecting to it
  (and that river is not on the symmetry axis), it may not be the optimal
  starting point for packing. This function navigates along river sticks in
  counter-clockwise order (by azimuth angle) until it finds a joint that is an
  endpoint of a river chain (i.e., has only one river connected), which is a
  better starting point.

  Args:
    stick_figure: The stick figure to traverse.
    start_joint_name: The name of the joint to start traversal from.
    start_river: The river stick to start traversal from.

  Returns:
    The name of the joint with only one river, and the start stick for
    proximity traversal from that joint.

  Raises:
    ValueError: If a cycle is detected while navigating rivers.
    RuntimeError: If > 1 river is found at a joint but no next river can be
      found to hop to.
  """
  current_river = start_river
  source_joint_name = start_joint_name
  visited_rivers = set()

  while True:
    if current_river.name in visited_rivers:
      raise ValueError(
          'Cycle detected while navigating rivers to find start joint.'
      )
    visited_rivers.add(current_river.name)

    current_joint_name = current_river.other_joint_name(source_joint_name)
    current_joint = stick_figure.joints[current_joint_name]

    rivers_at_joint = [s for s in current_joint.sticks if s.is_river]
    if len(rivers_at_joint) == 1:
      # Found target joint with only 1 river.
      start_stick = find_start_stick_for_proximity_traversal(
          stick_figure, current_joint_name
      )
      return current_joint_name, start_stick

    # If > 1 river, find next river in counter-clockwise order and continue
    # hopping.
    arriving_stick_index = current_joint.sticks.index(current_river)
    number_of_sticks = len(current_joint.sticks)
    found_next_river = False
    for i in range(1, number_of_sticks):
      next_stick_candidate = current_joint.sticks[
          (arriving_stick_index + i) % number_of_sticks
      ]
      if next_stick_candidate.is_river:
        source_joint_name = current_joint_name
        current_river = next_stick_candidate
        found_next_river = True
        break
    if not found_next_river:
      raise RuntimeError(
          f'Joint {current_joint_name} reported > 1 river but could not find'
          ' next river to hop to.'
      )


def find_start_stick_for_size_traversal(
    stick_figure: sf.StickFigure, joint_name: str
) -> stick_lib.Stick:
  """Finds the default starting stick for size traversal from a given joint."""
  joint = stick_figure.joints[joint_name]
  return max(joint.sticks, key=lambda s: s.length)


def find_start_stick_for_proximity_traversal(
    stick_figure: sf.StickFigure, joint_name: str
) -> stick_lib.Stick:
  """Finds the default starting stick for proximity traversal from a given joint."""
  joint = stick_figure.joints[joint_name]
  sticks = joint.sticks

  river_indices = [i for i, s in enumerate(sticks) if s.is_river]
  if river_indices:
    last_river_index = river_indices[-1]
    return sticks[(last_river_index + 1) % len(sticks)]
  else:
    # If no river, fall back to the size-based selection logic.
    return find_start_stick_for_size_traversal(stick_figure, joint_name)


def _get_counter_clockwise_sticks(
    sticks: list[stick_lib.Stick],
    start_stick: stick_lib.Stick,
    start_index: int = 0,
) -> list[stick_lib.Stick]:
  """Returns sticks in counter-clockwise order, starting from start_stick + start_index.

  Args:
    sticks: A list of sticks sorted in counter-clockwise order.
    start_stick: The stick to start from.
    start_index: The index relative to start_stick to begin counter-clockwise
      traversal from. If 0, includes start_stick. If 1, starts from stick after
      start_stick.

  Returns:
    A list of sticks in counter-clockwise order.
  """
  try:
    stick_index = sticks.index(start_stick)
  except ValueError:
    return []
  num_sticks = len(sticks)
  return [
      sticks[(stick_index + i) % num_sticks]
      for i in range(start_index, num_sticks)
  ]


def _apply_river_priority_ordering(
    *,
    unvisited_rivers: list[stick_lib.Stick],
    unvisited_flaps: list[stick_lib.Stick],
    joint_name: str,
    symmetric_connecting_joints: list[str],
) -> list[stick_lib.Stick]:
  """Orders sticks based on river count and symmetry for river-priority traversal.

  If more than one river is present, rivers are prioritized, followed by
  flaps. If a symmetric connecting joint is encountered, the river on
  the symmetry axis is visited last among rivers. Otherwise, flaps are
  prioritized, followed by rivers.

  Args:
    unvisited_rivers: A list of unvisited river sticks connected to the joint,
      in counter-clockwise order.
    unvisited_flaps: A list of unvisited flaps sticks connected to the joint, in
      counter-clockwise order.
    joint_name: The name of the joint being processed.
    symmetric_connecting_joints: A list of joints on the symmetry axis.

  Returns:
    A list of sticks in the order they should be visited.
  """
  if len(unvisited_rivers) > 1:
    # River-Priority
    rivers_to_visit = unvisited_rivers
    if joint_name in symmetric_connecting_joints:
      axis_river = next(
          (r for r in unvisited_rivers if r.is_on_symmetry_axis), None
      )
      if axis_river:
        index = unvisited_rivers.index(axis_river)
        rivers_to_visit = (
            unvisited_rivers[index + 1 :]
            + unvisited_rivers[:index]
            + [axis_river]
        )
    return rivers_to_visit + unvisited_flaps
  else:
    # Flap-Priority
    return unvisited_flaps + unvisited_rivers


def _get_sticks_in_river_priority_order(
    sticks_in_counter_clockwise_order: list[stick_lib.Stick],
    visited_sticks: set[str],
    joint_name: str,
    symmetric_connecting_joints: list[str],
) -> list[stick_lib.Stick]:
  """Get sticks in river priority order from a list of sticks in counter-clockwise order.

  Args:
    sticks_in_counter_clockwise_order: A list of sticks in counter-clockwise
      order.
    visited_sticks: A set of names of visited sticks.
    joint_name: The name of the joint being processed.
    symmetric_connecting_joints: A list of joints on the symmetry axis.

  Returns:
    A list of sticks in river priority order.
  """
  unvisited_rivers = []
  unvisited_flaps = []
  for s in sticks_in_counter_clockwise_order:
    if s.name not in visited_sticks:
      if s.is_river:
        unvisited_rivers.append(s)
      else:
        unvisited_flaps.append(s)
  return _apply_river_priority_ordering(
      unvisited_rivers=unvisited_rivers,
      unvisited_flaps=unvisited_flaps,
      joint_name=joint_name,
      symmetric_connecting_joints=symmetric_connecting_joints,
  )


def traverse_sticks_river_priority(
    stick_figure: sf.StickFigure,
    stick: stick_lib.Stick,
    from_joint_name: str,
    joints: Mapping[str, sf.Joint],
    visited_sticks: set[str],
    symmetric_connecting_joints: list[str],
) -> Iterator[stick_lib.Stick]:
  """Recursive helper for river-priority traversal.

  This function recursively visits sticks in counter-clockwise order from the
  arriving stick. At each joint, it determines whether to visit rivers or
  flaps first, based on the number of unvisited rivers connected to that
  joint, and yields sticks in that order.

  Args:
    stick_figure: The stick figure being traversed.
    stick: The stick to start traversal from.
    from_joint_name: The name of the joint we are coming from.
    joints: A dictionary of all joints in the stick figure.
    visited_sticks: A set of names of visited sticks.
    symmetric_connecting_joints: A list of joint names that connect symmetric
      sticks.

  Yields:
    Sticks in river-priority traversal order.
  """
  if stick.name in visited_sticks:
    raise ValueError(f'Stick {stick.name} already visited.')

  visited_sticks.add(stick.name)
  yield stick

  current_joint_name = stick.other_joint_name(from_joint_name)
  current_joint = joints.get(current_joint_name)

  if not current_joint:
    return

  joint_sticks = current_joint.sticks
  counter_clockwise_candidate_sticks = _get_counter_clockwise_sticks(
      joint_sticks, stick, 1
  )

  visit_order = _get_sticks_in_river_priority_order(
      sticks_in_counter_clockwise_order=counter_clockwise_candidate_sticks,
      visited_sticks=visited_sticks,
      joint_name=current_joint_name,
      symmetric_connecting_joints=symmetric_connecting_joints,
  )

  for next_stick_to_visit in visit_order:
    if next_stick_to_visit.name not in visited_sticks:
      yield from traverse_sticks_river_priority(
          stick_figure,
          next_stick_to_visit,
          current_joint_name,
          joints,
          visited_sticks,
          symmetric_connecting_joints,
      )


def traverse_sticks(
    stick_figure: sf.StickFigure,
    stick: stick_lib.Stick,
    from_joint_name: str,
    joints: Mapping[str, sf.Joint],
    visited_sticks: set[str],
    revisit_rivers: bool = False,
) -> Iterator[stick_lib.Stick]:
  """Recursively traverses sticks from a joint.

  Args:
    stick_figure: The stick figure being traversed.
    stick: The stick to start traversal from.
    from_joint_name: The name of the joint we are coming from.
    joints: A dictionary of all joints in the stick figure.
    visited_sticks: A set of names of visited sticks.
    revisit_rivers: Whether to yield rivers when traversed again.

  Yields:
    Sticks in traversal order.
  """
  if stick.name in visited_sticks:
    return

  visited_sticks.add(stick.name)
  yield stick

  current_joint_name = stick.other_joint_name(from_joint_name)
  current_joint = joints[current_joint_name]
  joint_sticks = current_joint.sticks

  try:
    arriving_stick_index = joint_sticks.index(stick)
  except ValueError:
    # This should never happen but I'm too scared to remove the guard.
    logging.error(
        'Stick %s not found in joint %s', stick.name, current_joint_name
    )
    return

  num_sticks = len(joint_sticks)
  for i in range(1, num_sticks):
    next_stick_to_visit = joint_sticks[(arriving_stick_index + i) % num_sticks]
    if next_stick_to_visit.name not in visited_sticks:
      yield from traverse_sticks(
          stick_figure,
          next_stick_to_visit,
          current_joint_name,
          joints,
          visited_sticks,
          revisit_rivers=revisit_rivers,
      )
      if revisit_rivers and next_stick_to_visit.is_river:
        yield next_stick_to_visit


def river_priority_traversal(
    stick_figure: sf.StickFigure,
    start_stick: stick_lib.Stick,
    start_joint_name: str,
) -> Iterator[stick_lib.Stick]:
  """Performs a river-priority traversal of the stick figure.

  This method performs a depth-first traversal. At each joint, if there are
  more than 1 unvisited rivers, it visits rivers first in counter-clockwise
  order, then flaps in counter-clockwise order. Otherwise, it visits
  flaps first, then rivers. An exception applies for symmetric cases, see
  `traverse_sticks_river_priority`.

  Args:
    stick_figure: The stick figure to traverse.
    start_stick: The stick to start traversal from.
    start_joint_name: The name of the joint to start traversal from.

  Yields:
    Sticks in river-priority traversal order.
  """
  start_joint = stick_figure.joints[start_joint_name]
  rivers = [s for s in start_joint.sticks if s.is_river]
  if len(rivers) == 1 and not rivers[0].is_on_symmetry_axis:
    start_joint_name, start_stick = _navigate_rivers_to_start_joint(
        stick_figure, start_joint_name, rivers[0]
    )

  joint_sticks = stick_figure.joints[start_joint_name].sticks
  ordered_start_sticks = _get_counter_clockwise_sticks(
      joint_sticks, start_stick, 0
  )
  symmetric_connecting_joints = stick_figure.get_symmetric_connecting_joints()

  visited_sticks = set()
  visit_order_start = _get_sticks_in_river_priority_order(
      sticks_in_counter_clockwise_order=ordered_start_sticks,
      visited_sticks=visited_sticks,
      joint_name=start_joint_name,
      symmetric_connecting_joints=symmetric_connecting_joints,
  )

  for stick in visit_order_start:
    if stick.name not in visited_sticks:
      yield from traverse_sticks_river_priority(
          stick_figure,
          stick,
          start_joint_name,
          stick_figure.joints,
          visited_sticks,
          symmetric_connecting_joints,
      )


def external_counterclockwise_traversal(
    stick_figure: sf.StickFigure,
    start_stick: stick_lib.Stick,
    start_joint_name: str,
    revisit_rivers: bool = False,
) -> Iterator[stick_lib.Stick]:
  """Performs an external counter-clockwise traversal of the stick figure.

  This method performs a depth-first traversal, visiting neighboring sticks
  in a counter-clockwise order at each joint, creating an 'outer walk' of the
  figure.

  Args:
    stick_figure: The stick figure to traverse.
    start_stick: The stick to start traversal from.
    start_joint_name: The name of the joint to start traversal from.
    revisit_rivers: Whether to yield rivers when traversed again.

  Yields:
    Sticks in external counter-clockwise traversal order.
  """
  visited_sticks = set()
  joint_sticks = stick_figure.joints[start_joint_name].sticks
  start_stick_idx = joint_sticks.index(start_stick)

  num_sticks = len(joint_sticks)
  ordered_start_sticks = [
      joint_sticks[(start_stick_idx + i) % num_sticks]
      for i in range(num_sticks)
  ]

  for stick in ordered_start_sticks:
    if stick.name not in visited_sticks:
      yield from traverse_sticks(
          stick_figure,
          stick,
          start_joint_name,
          stick_figure.joints,
          visited_sticks,
          revisit_rivers=revisit_rivers,
      )
      if revisit_rivers and stick.is_river:
        yield stick


def get_size_traversal(
    stick_figure: sf.StickFigure,
    start_stick: stick_lib.Stick,
    start_joint_name: str,
) -> Iterator[stick_lib.Stick]:
  """Yields an iterator for packing using size-based heuristics.

  The traversal then yields sticks by visiting joints based on their size,
  and within each joint, visiting sticks by length.

  Args:
    stick_figure: The stick figure to traverse.
    start_stick: The stick to start traversal from.
    start_joint_name: The joint to start traversal from.

  Yields:
    An iterator of `Stick` objects in the determined packing order.
  """
  if not stick_figure.children:
    raise ValueError('Cannot traverse a stick figure with no children.')

  visited_sticks = set()
  joint_scores = {
      j_name: j.get_required_grid_size(stick_figure)
      for j_name, j in stick_figure.joints.items()
  }

  # Sorted list of joints based on required grid size.
  sorted_joint_names = sorted(
      stick_figure.joints.keys(),
      key=lambda j_name: joint_scores[j_name],
      reverse=True,
  )

  # Pre-sort sticks in each joint by length (desc.), then name (tiebreaker).
  sorted_sticks_by_joint = {
      j_name: sorted(j.sticks, key=lambda s: (-s.length, s.name))
      for j_name, j in stick_figure.joints.items()
  }

  yield start_stick
  visited_sticks.add(start_stick.name)

  if start_joint_name in sorted_joint_names:
    sorted_joint_names.remove(start_joint_name)
  joint_processing_order = [start_joint_name] + sorted_joint_names

  for j_name in joint_processing_order:
    for stick in sorted_sticks_by_joint[j_name]:
      if stick.name not in visited_sticks:
        yield stick
        visited_sticks.add(stick.name)


def packing_traversal(
    stick_figure: sf.StickFigure,
    mode: packing_types.TraversalMode,
    start_stick_name: str | None = None,
    start_joint_name: str | None = None,
    revisit_rivers: bool = False,
) -> Iterator[stick_lib.Stick]:
  """Yields an iterator over the stick figure in an order suitable for packing.

  This method provides different traversal strategies depending on the `mode`.

  - 'proximity': Performs a depth-first 'outer walk' of the stick figure,
    visiting sticks in a counter-clockwise order at each joint. See
    `external_counterclockwise_traversal` for more details.
  - 'size': Traverses sticks based on the size of joints and sticks,
    prioritizing larger elements first. See `get_size_traversal` for
    details on the heuristics.
  - 'river_priority': Traverses sticks based on river count at joints.

  Args:
    stick_figure: The stick figure to traverse.
    mode: The traversal mode.
    start_stick_name: An optional name of the stick to start traversal from. If
      not provided, a starting stick is determined by the chosen mode's logic.
    start_joint_name: An optional name of the joint of the start stick to start
      traversal from. Can affect whether the traversal comes or goes from a
      river stick.
    revisit_rivers: Whether to yield rivers when traversed multiple times.

  Yields:
    An iterator of `Stick` objects in the specified packing order.
  """
  if not stick_figure.children:
    raise ValueError('Cannot traverse a stick figure with no children.')
  if revisit_rivers and mode != packing_types.TraversalMode.PROXIMITY:
    raise NotImplementedError(
        'Revisit rivers is only implemented for proximity traversal.'
    )

  if start_stick_name:
    start_stick = stick_figure[start_stick_name]
    # find the best joint to start traversal from
    if start_joint_name is None:
      start_joint_name = max(
          (start_stick.start, start_stick.end),
          key=lambda j_name: stick_figure.joints[j_name].get_required_grid_size(
              stick_figure
          ),
      )
    elif start_joint_name not in (start_stick.start, start_stick.end):
      raise ValueError(
          f'Start joint {start_joint_name} not in start stick'
          f' {start_stick.name}.'
      )
  else:
    if start_joint_name is not None:
      raise ValueError(
          'start_joint_name is only supported when start_joint_name is'
          ' provided.'
      )
    if stick_figure.is_symmetric_tree:
      symmetric_joints = stick_figure.get_symmetric_connecting_joints()
      start_joint_name = (
          symmetric_joints[0]
          if symmetric_joints
          else stick_figure.get_largest_joint_name()
      )
    else:
      start_joint_name = stick_figure.get_largest_joint_name()
    if mode == 'proximity' or mode == 'river_priority':
      start_stick = find_start_stick_for_proximity_traversal(
          stick_figure, start_joint_name
      )
    elif mode == 'size':
      start_stick = find_start_stick_for_size_traversal(
          stick_figure, start_joint_name
      )
    else:
      raise ValueError(f'Unsupported mode: {mode}')

  match mode:
    case packing_types.TraversalMode.PROXIMITY:
      yield from external_counterclockwise_traversal(
          stick_figure,
          start_stick,
          start_joint_name,
          revisit_rivers=revisit_rivers,
      )
    case packing_types.TraversalMode.RIVER_PRIORITY:
      yield from river_priority_traversal(
          stick_figure, start_stick, start_joint_name
      )
    case packing_types.TraversalMode.SIZE:
      yield from get_size_traversal(stick_figure, start_stick, start_joint_name)
    case _:
      typing.assert_never(mode)
