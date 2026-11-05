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

"""Utility functions for box pleating pleats.

Supports three callable functions:
- create_pleats: Creates pleats from axial segments.
- valid_pleats: Verify that the pleats are valid.
- assign_pleats: Assigns folds to pleats.
"""

from collections.abc import Iterable, Sequence
import itertools
import math
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import crease_pattern
from bp_pipeline.crease_pattern import point
from bp_pipeline.crease_pattern import vertex
from bp_pipeline.solving import utils


def valid_pleats(
    pleats: list[crease.Crease],
    ridges: list[crease.Crease],
    grid_size: int,
) -> bool:
  """Verify that all internal grid points are covered by a pleat or a ridge."""
  grid_points = utils.create_grid_points(grid_size)
  unassigned_ridges, _ = utils.split_unassigned_and_central_ridges(ridges)
  pleats_by_y: dict[int, list[crease.Crease]] = {}
  pleats_by_x: dict[int, list[crease.Crease]] = {}
  for pleat in pleats:
    if pleat.is_horizontal:
      pleats_by_y.setdefault(round(pleat.p1.y * grid_size), []).append(pleat)
    elif pleat.is_vertical:
      pleats_by_x.setdefault(round(pleat.p1.x * grid_size), []).append(pleat)
    else:
      raise ValueError(f'Pleat is not horizontal or vertical: {pleat}')
  ridge_tips = utils.TipIndex(unassigned_ridges, grid_size=grid_size)
  for grid_point in grid_points:
    if grid_point.is_border:
      continue
    gx_key = round(grid_point.x * grid_size)
    gy_key = round(grid_point.y * grid_size)
    covered = any(
        p.p1.x <= grid_point.x <= p.p2.x for p in pleats_by_y.get(gy_key, ())
    ) or any(
        p.p1.y <= grid_point.y <= p.p2.y for p in pleats_by_x.get(gx_key, ())
    )
    if not covered and not ridge_tips.has_tip(grid_point):
      print(
          f'Grid point {grid_point} is not covered by a pleat or a ridge tip.'
          f' Grid size: {grid_size}'
      )
      return False
  return True


def _axials(grid_size: int) -> Sequence[crease.Crease]:
  """Returns all the axial creases for a given grid size."""
  axials = []
  for i in range(1, grid_size):
    axials.append(
        crease.Crease(
            point.Point(x=0, y=i / grid_size),
            point.Point(x=1, y=i / grid_size),
            fold=crease.Fold.HINGE,
        )
    )
    axials.append(
        crease.Crease(
            point.Point(x=i / grid_size, y=0),
            point.Point(x=i / grid_size, y=1),
            fold=crease.Fold.HINGE,
        )
    )
  return axials


def _pleats_from_hinges(
    hinges: list[crease.Crease],
    split_axials: Sequence[crease.Crease],
) -> list[crease.Crease]:
  """Adds split_axials that are perpendicular to and intersect hinges."""
  pleats = []
  for hinge in hinges:
    for split_axial in split_axials:
      if not split_axial.is_perpendicular(hinge):
        continue
      intersection_point = split_axial.vertex_with_crease(hinge)
      if intersection_point:
        pleats.append(split_axial)
  return utils.deduplicate(pleats)


def _remove_nones(
    points_or_nones: list[point.Point | None],
) -> list[point.Point]:
  return [point_ for point_ in points_or_nones if point_ is not None]


def valid_points(
    pleat_points: list[point.Point],
    ridge_points: list[point.Point],
) -> bool:
  """Returns true if any point in the pleat points is also in the ridge points."""
  for pleat_point in pleat_points:
    if pleat_point is None:
      continue
    if not any(
        pleat_point.isclose(ridge_point) for ridge_point in ridge_points
    ):
      return False
  return True


def _axial_step_from_tip(
    axial: crease.Crease, tip: point.Point
) -> tuple[int, int] | None:
  """Returns the integer unit direction (ux, uy) from `tip` along `axial`."""
  if not axial.is_tip(tip):
    return None
  other = axial.p2 if axial.p1.isclose(tip) else axial.p1
  if axial.is_horizontal:
    return (1 if other.x > tip.x else -1, 0)
  if axial.is_vertical:
    return (0, 1 if other.y > tip.y else -1)
  return None


def _is_internal_to_45_degree_ridge(
    pt: point.Point,
    unassigned_ridges: Sequence[crease.Crease],
) -> bool:
  """Returns True if `pt` lies strictly in the interior of a 45-degree ridge."""
  for r in unassigned_ridges:
    if (
        r.is_diagonal
        and r.point_status(pt) == crease.PointStatus.INTERNAL
        and math.isclose(
            abs(r.p2.x - r.p1.x),
            abs(r.p2.y - r.p1.y),
            abs_tol=point.DEFAULT_TOLERANCE,
        )
    ):
      return True
  return False


def _is_valid_ridge_reflection(
    pleat: crease.Crease,
    split_axial: crease.Crease,
    intersection_point: point.Point,
    unassigned_ridges: Sequence[crease.Crease],
) -> bool:
  """Returns True if split_axial reflects pleat across a 45-degree ridge at intersection_point."""
  if not pleat.is_perpendicular(split_axial):
    return False
  step_p = _axial_step_from_tip(pleat, intersection_point)
  step_a = _axial_step_from_tip(split_axial, intersection_point)
  if step_p is None or step_a is None:
    return False
  ux_p, uy_p = step_p
  for r in unassigned_ridges:
    if (
        not r.is_diagonal
        or r.point_status(intersection_point) != crease.PointStatus.INTERNAL
    ):
      continue
    rx = r.p2.x - r.p1.x
    ry = r.p2.y - r.p1.y
    if not math.isclose(abs(rx), abs(ry), abs_tol=point.DEFAULT_TOLERANCE):
      continue
    slope_sign = 1 if rx * ry > 0 else -1
    if step_a == (slope_sign * uy_p, slope_sign * ux_p):
      return True
  return False


def _continue_pleats(
    unassigned_ridges: list[crease.Crease],
    pleats: list[crease.Crease],
    split_axials: list[crease.Crease],
    grid_size: int | None = None,
    recovery: bool = False,
) -> list[crease.Crease]:
  """Adds split_axials that "continue" pleats across ridges.

  - intersect at unassigned ridges
  - either intersect borders (standard continuation) or, if recovery is True,
    have both tips strictly internal to 45-degree turn ridges and reflect across
    the ridge at each intersection point (multi-turn river continuation)
  - are perpendicular to the existing pleats
  - have parallel existing pleats at the intersection points

  Args:
    unassigned_ridges: The ridges that have not been assigned to a pleat.
    pleats: The pleats that have already been added.
    split_axials: The axials that have been split by the ridges.
    grid_size: Optional grid size for integer lattice bucketing.
    recovery: Whether to enable extended multi-turn river pleat continuation.

  Returns:
    The new pleats that have been added.
  """
  new_pleats = []
  pleats_overlap_index = utils.LineOverlapIndex(pleats, grid_size=grid_size)
  for split_axial in split_axials:
    if recovery:
      if not split_axial.intersects_border and not (
          _is_internal_to_45_degree_ridge(split_axial.p1, unassigned_ridges)
          and _is_internal_to_45_degree_ridge(split_axial.p2, unassigned_ridges)
      ):
        continue
    else:
      if not split_axial.intersects_border:
        continue
    if pleats_overlap_index.has_overlap(split_axial):
      continue
    ridge_intersection_points = _remove_nones(
        [ridge.vertex_with_crease(split_axial) for ridge in unassigned_ridges]
    )
    if not ridge_intersection_points:
      continue
    intersecting_pleats, pleat_intersection_points = [], []
    for pleat in pleats:
      intersection_point = pleat.vertex_with_crease(split_axial)
      if intersection_point:
        intersecting_pleats.append(pleat)
        pleat_intersection_points.append(intersection_point)

    if not intersecting_pleats or not all(
        intersecting_pleat.is_parallel(intersecting_pleats[0])
        for intersecting_pleat in intersecting_pleats
    ):
      continue
    if not valid_points(pleat_intersection_points, ridge_intersection_points):
      continue
    if split_axial.intersects_border:
      for pleat, pleat_intersection_point in zip(
          intersecting_pleats, pleat_intersection_points
      ):
        if pleat_intersection_point and pleat.is_perpendicular(split_axial):
          new_pleats.append(split_axial)
          break
    elif recovery and all(
        pleat_intersection_point is not None
        and _is_valid_ridge_reflection(
            pleat,
            split_axial,
            pleat_intersection_point,
            unassigned_ridges,
        )
        for pleat, pleat_intersection_point in zip(
            intersecting_pleats, pleat_intersection_points
        )
    ):
      new_pleats.append(split_axial)
  return new_pleats


def _central_pleats(
    unassigned_ridges: list[crease.Crease],
    pleats: list[crease.Crease],
    split_axials: list[crease.Crease],
    grid_size: int | None = None,
) -> list[crease.Crease]:
  """Adds split_axials that intersect 4 ridges.

  All four axials must be added in this case.

  Args:
    unassigned_ridges: The ridges that have not been assigned to a pleat.
    pleats: The pleats that have already been added.
    split_axials: The axials that have been split by the ridges.
    grid_size: Optional grid size for integer lattice bucketing.

  Returns:
    The new pleats that have been added.
  """
  new_pleats = []
  pleats_overlap_index = utils.LineOverlapIndex(pleats, grid_size=grid_size)
  ridges_tip_index = utils.TipIndex(unassigned_ridges, grid_size=grid_size)
  for split_axial in split_axials:
    if pleats_overlap_index.has_overlap(split_axial):
      continue
    for tip in [split_axial.p1, split_axial.p2]:
      if ridges_tip_index.count_at_tip(tip) == 4:
        new_pleats.append(split_axial)
        break
  return utils.deduplicate(new_pleats)


def _add_non_intersecting_pleats(
    pleats: list[crease.Crease],
    grid_points: Iterable[point.Point],
    split_axials: list[crease.Crease],
    grid_size: int | None = None,
) -> list[crease.Crease]:
  """At each grid point, add axials, that do not intersect pleats.

  Args:
    pleats: The pleats that have already been added.
    grid_points: The grid points.
    split_axials: The axials that have been split by the ridges.
    grid_size: Optional grid size for integer lattice bucketing.

  Returns:
    A list of new pleats that do not intersect existing pleats.
  """
  scale = float(grid_size) if grid_size is not None and grid_size > 0 else 500.0
  pleats_by_y: dict[int, list[crease.Crease]] = {}
  pleats_by_x: dict[int, list[crease.Crease]] = {}
  for pleat in pleats:
    if pleat.is_horizontal:
      pleats_by_y.setdefault(round(pleat.p1.y * scale), []).append(pleat)
    elif pleat.is_vertical:
      pleats_by_x.setdefault(round(pleat.p1.x * scale), []).append(pleat)
    else:
      raise ValueError(f'Pleat is not horizontal or vertical: {pleat}')

  axials_by_y: dict[int, list[tuple[int, crease.Crease]]] = {}
  axials_by_x: dict[int, list[tuple[int, crease.Crease]]] = {}
  for idx, axial in enumerate(split_axials):
    if axial.is_horizontal:
      axials_by_y.setdefault(round(axial.p1.y * scale), []).append((idx, axial))
    elif axial.is_vertical:
      axials_by_x.setdefault(round(axial.p1.x * scale), []).append((idx, axial))
    else:
      raise ValueError(f'Pleat is not horizontal or vertical: {axial}')

  overlap_index = utils.LineOverlapIndex(pleats, grid_size=grid_size)
  axial_intersects_pleat_cache: dict[int, bool] = {}
  new_pleats = []
  for p in grid_points:
    gx = p.x
    gy = p.y
    gx_key = round(gx * scale)
    gy_key = round(gy * scale)
    # If there is already a pleat that intersects the grid point, skip.
    if any(
        pleat.p1.x <= gx <= pleat.p2.x for pleat in pleats_by_y.get(gy_key, ())
    ) or any(
        pleat.p1.y <= gy <= pleat.p2.y for pleat in pleats_by_x.get(gx_key, ())
    ):
      continue
    # Find all the axials that intersect at p in split_axials order.
    candidates = [
        (idx, axial)
        for idx, axial in axials_by_y.get(gy_key, ())
        if axial.p1.x <= gx <= axial.p2.x
    ] + [
        (idx, axial)
        for idx, axial in axials_by_x.get(gx_key, ())
        if axial.p1.y <= gy <= axial.p2.y
    ]
    if len(candidates) > 1:
      candidates.sort(key=lambda item: item[0])
    for _, axial in candidates:
      if overlap_index.has_overlap(axial):
        continue
      axial_id = id(axial)
      intersects_pleat = axial_intersects_pleat_cache.get(axial_id)
      if intersects_pleat is None:
        intersects_pleat = any(
            pleat.vertex_with_crease(axial) is not None for pleat in pleats
        )
        axial_intersects_pleat_cache[axial_id] = intersects_pleat
      # If the crease does not intersect other pleats, add it to pleats.
      if not intersects_pleat:
        new_pleats.append(axial)
        overlap_index.add(axial)
  return new_pleats


def grid_point_intermediate_pleat(
    grid_point: point.Point, pleat: crease.Crease
) -> bool:
  """Returns true if the grid point is an intermediate point of a pleat."""
  if pleat.is_horizontal:
    if grid_point.y != pleat.p1.y:
      return False
    return grid_point.x >= pleat.p1.x and pleat.p2.x >= grid_point.x
  elif pleat.is_vertical:
    if grid_point.x != pleat.p1.x:
      return False
    return grid_point.y >= pleat.p1.y and grid_point.y <= pleat.p2.y
  else:
    raise ValueError(f'Pleat is not horizontal or vertical: {pleat}')


def get_intersecting_ridges(
    axial: crease.Crease,
    ridges: list[crease.Crease],
    grid_points: Iterable[point.Point],
) -> list[crease.Crease]:
  """Ridge creases define a 2-color partition of the paper.

  For each color partition, all the axials are all vertical or all horizontal.
  Here we split the axials to segements based on interestions with ridges.
  There is one case where the axials may not split: when they intersect
  two ridge tips. In this case, there are two options. If the axial bisects the
  angle between the two ridges, then the axial is split into two segments.
  Otherwise, the axial is not split.

  Args:
    axial: The axial crease.
    ridges: The ridge creases.
    grid_points: The grid points.

  Returns:
    The intersecting ridges that will be used to split the axial.
  """
  valid_intersecting_ridges = []
  # Find all the ridges that intersect the axial and all the intersection
  # points.
  intersecting_ridges = []
  intersection_points = []
  for ridge in ridges:
    intersection_point = axial.vertex_with_crease(ridge)
    if intersection_point:
      intersection_points.append(intersection_point)
      intersecting_ridges.append(ridge)
      if not ridge.is_tip(intersection_point):
        valid_intersecting_ridges.append(ridge)
  # For each intersection point, find if exactly two ridges intersect it.
  # If so, check the angles at the intersection point.
  for intersection_point in intersection_points:
    intersecting_ridges_at_point = []
    # If the ridge does not intersect in a tip, it is valid.
    for ridge in intersecting_ridges:
      if ridge.is_tip(intersection_point):
        intersecting_ridges_at_point.append(ridge)
    # If the intersection point does not have two ridges it is valid.
    if len(intersecting_ridges_at_point) != 2:
      valid_intersecting_ridges.extend(intersecting_ridges_at_point)
    else:
      axial_copy = crease.Crease(axial.p1, axial.p2, fold=crease.Fold.MOUNTAIN)
      split_axials = axial_copy.split_to_segments(
          intersecting_ridges_at_point, grid_points
      )
      v = vertex.Vertex(
          split_axials + intersecting_ridges_at_point, intersection_point
      )
      sector_angles = sorted([angle for angle, _, _ in v.sector_angles()])
      rounded_angles = [round(angle) for angle in sector_angles]
      # If the pleat bisectes the angle between the two ridges it is valid.
      if rounded_angles == [45, 45, 135, 135]:
        valid_intersecting_ridges.extend(intersecting_ridges_at_point)

  return utils.deduplicate(valid_intersecting_ridges)


def create_pleats(
    cp: crease_pattern.CreasePattern, grid_size: int, recovery: bool = False
) -> list[crease.Crease]:
  """Creates pleats from axial segments.

  There are three main steps:
  1. Add segments that are perpendicular to the hinges.
  2. Add segments that intersect 4 ridges (central pleats).
  3. Add segments that continue previous segments.

  Args:
    cp: The crease pattern to create pleats for.
    grid_size: int
    recovery: bool, if True enables extended multi-turn river pleat propagation.

  Returns:
    Sequence[crease.Crease]
  """
  all_ridges = [
      crease_ for crease_ in cp.creases if crease_.fold == crease.Fold.MOUNTAIN
  ]
  unassigned_ridges, central_ridges = utils.split_unassigned_and_central_ridges(
      all_ridges
  )
  hinges = [hinge for hinge in cp.creases if hinge.fold == crease.Fold.HINGE]
  axials = _axials(grid_size)
  grid_points = utils.create_grid_points(grid_size)
  central_and_hinges_index = utils.LineOverlapIndex(
      central_ridges + hinges, grid_size=grid_size
  )
  split_axials = []
  for axial in axials:
    intersecting_ridges = get_intersecting_ridges(
        axial, unassigned_ridges, grid_points
    )
    segments = axial.split_to_segments(intersecting_ridges, grid_points)
    non_overlapping_segments = [
        segment
        for segment in segments
        if not central_and_hinges_index.has_overlap(segment)
    ]
    split_axials.extend(non_overlapping_segments)
  pleats = _pleats_from_hinges(hinges, split_axials)
  pleats.extend(
      _central_pleats(
          unassigned_ridges, pleats, split_axials, grid_size=grid_size
      )
  )
  if recovery:
    # Iterate pleat continuation to a fixed point so multi-hop reflections
    # across turn ridges (e.g., U-shaped and closed-loop rivers) propagate
    # through every corner before non-intersecting pleats are added.
    for _ in range(len(split_axials) + 1):
      continued_pleats = _continue_pleats(
          unassigned_ridges,
          pleats,
          split_axials,
          grid_size=grid_size,
          recovery=True,
      )
      if not continued_pleats:
        break
      pleats.extend(continued_pleats)
  else:
    pleats.extend(
        _continue_pleats(
            unassigned_ridges,
            pleats,
            split_axials,
            grid_size=grid_size,
            recovery=False,
        )
    )
  pleats.extend(
      _add_non_intersecting_pleats(
          pleats, grid_points, split_axials, grid_size=grid_size
      )
  )
  # After we added all the pleats we need to split them again to get the final
  # segments. This is because the hinges algorithm will have the ability to
  # reassign folds to the segments.
  final_pleats = []
  for pleat in pleats:
    final_pleats.extend(pleat.split_to_segments(unassigned_ridges, grid_points))
  return final_pleats


def _path_order(creases: Sequence[crease.Crease], grid_size: int) -> int:
  """Find the path that is closest to the origin."""
  dists = [int(_dist_from_origin(crease_) * grid_size) for crease_ in creases]
  return min(dists)


def _dist_from_origin(crease_: crease.Crease) -> float:
  """Returns the distance of the crease from the origin.

  If the crease is horizontal, the distance is the y-coordinate of the crease.
  If the crease is vertical, the distance is the x-coordinate of the crease.

  Args:
    crease_: The crease to calculate the distance for.

  Returns:
    The distance of the crease from the origin.
  """
  if crease_.is_horizontal:
    return crease_.p1.y
  if not crease_.is_vertical:
    raise ValueError(f'{crease_} is not horizontal or vertical.')
  return crease_.p1.x


def path_grid_distance(
    path1: Sequence[crease.Crease], path2: Sequence[crease.Crease]
) -> float:
  """The min _crease_grid_distance among all pairs of creases in the paths."""
  return min([
      _crease_grid_distance(pair[0], pair[1])
      for pair in itertools.product(path1, path2)
  ])


def _crease_grid_distance(
    crease1: crease.Crease, crease2: crease.Crease
) -> float:
  """Returns a grid distance between two creases.

  If the creases are horizontal and overlap in the x coordinates,
  return the diff in y cooridates.
  If the creases or vertical and overlap in the y coordinates,
  return the diff in x cooridates.
  Otherwise, the distance is infinity.

  Args:
    crease1: The first crease.
    crease2: The second crease.

  Returns:
    The grid distance between the creases.
  """
  if crease1.is_horizontal and crease2.is_horizontal:
    if crease1.p2.x < crease2.p1.x or crease1.p1.x > crease2.p2.x:
      # The creases do not overlap, max1 < min2 or min1 > max2
      return math.inf
    return abs(crease1.p1.y - crease2.p1.y)
  elif crease1.is_vertical and crease2.is_vertical:
    if crease1.p2.y < crease2.p1.y or crease1.p1.y > crease2.p2.y:
      # The creases do not overlap, max1 < min2 or min1 > max2
      return math.inf
    return abs(crease1.p1.x - crease2.p1.x)
  else:
    return math.inf


def _assign_path(
    path: Sequence[crease.Crease], fold: crease.Fold, elevation: int
) -> list[crease.Crease]:
  """Assigns a fold to a path."""
  assigned_pleats = []
  for crease_ in path:
    assigned_pleats.append(
        crease.Crease(crease_.p1, crease_.p2, fold=fold, elevation=elevation)
    )
  return assigned_pleats


def _next_paths_from_path(
    path: Sequence[crease.Crease],
    paths: Sequence[Sequence[crease.Crease]],
    grid_size: int,
) -> set[int]:
  """Returns the indices of the paths that are adjacent to the path.

  Adjacency is defined as the distance between the grid points of the paths
  being the same as the grid size.

  Args:
    path: The path to find the adjacent paths for.
    paths: The paths to check for adjacency.
    grid_size: The size of the grid.

  Returns:
    The indices of the paths that are adjacent to the path.
  """
  return {
      ind
      for ind, path_ in enumerate(paths)
      if math.isclose(
          path_grid_distance(path, path_),
          1 / grid_size,
          abs_tol=1e-3,
      )
  }


def assign_pleats(
    unassigned_pleats: list[crease.Crease],
    grid_size: int,
    recovery: bool = False,
) -> list[crease.Crease]:
  """Assigns folds to unassigned_pleats.

  Pleats are divided into paths. A path is a sequence of pleats that are
  connected to each other via tips. All the pleats in the path are assigned the
  same fold. The first path is assigned a MOUNTAIN fold (arbitrarily). Then, we
  itereate over the paths, where any other path (separated from the current by
  one grid distance) has to interleave fold from mountain to valley and vice
  versa.

  Args:
    unassigned_pleats: The pleats to assign folds to.
    grid_size: The size of the grid.
    recovery: Whether to enable parity bridging across disconnected pleat paths.

  Returns:
    Sequence[crease.Crease]
  """
  paths = utils.creases_to_paths(unassigned_pleats)
  if not paths:
    return []

  paths.sort(key=lambda path: _path_order(path, grid_size))

  assigned_pleats = []
  current_fold = crease.Fold.MOUNTAIN
  elevation = 1
  # Use tips to find the 0 elevation curves in future refinements.
  assigned_paths_indices = {0}
  paths_to_assign_indices = {0}
  path_assignments: dict[int, tuple[crease.Fold, int]] = {}
  while paths_to_assign_indices:
    next_level_indices = set()
    for path_index in paths_to_assign_indices:
      path_to_assign = paths[path_index]
      path_assignments[path_index] = (current_fold, elevation)
      assigned_pleats.extend(
          _assign_path(path_to_assign, current_fold, elevation)
      )
      adjacent_indices = _next_paths_from_path(path_to_assign, paths, grid_size)
      for adj_index in adjacent_indices:
        if adj_index not in assigned_paths_indices:
          next_level_indices.add(adj_index)
          assigned_paths_indices.add(adj_index)
    current_fold = assigned_pleats[-1].mountain_to_valley()
    elevation = 0 if elevation == 1 else 1
    if (
        recovery
        and not next_level_indices
        and len(assigned_paths_indices) < len(paths)
    ):
      best_unassigned = None
      best_assigned = None
      min_dist = math.inf
      for u_idx in range(len(paths)):
        if u_idx in assigned_paths_indices:
          continue
        for a_idx in assigned_paths_indices:
          dist = path_grid_distance(paths[u_idx], paths[a_idx])
          if dist < min_dist:
            min_dist = dist
            best_unassigned = u_idx
            best_assigned = a_idx
      if best_unassigned is None:
        best_unassigned = min(set(range(len(paths))) - assigned_paths_indices)
        current_fold = crease.Fold.MOUNTAIN
        elevation = 1
      elif best_assigned is not None and not math.isinf(min_dist):
        ref_fold, ref_elev = path_assignments[best_assigned]
        steps = max(1, int(round(min_dist * grid_size)))
        if steps % 2 == 0:
          current_fold = ref_fold
          elevation = ref_elev
        else:
          current_fold = ref_fold.flip()
          elevation = 0 if ref_elev == 1 else 1
      else:
        current_fold = crease.Fold.MOUNTAIN
        elevation = 1
      assigned_paths_indices.add(best_unassigned)
      next_level_indices.add(best_unassigned)
    paths_to_assign_indices = next_level_indices
  return assigned_pleats
