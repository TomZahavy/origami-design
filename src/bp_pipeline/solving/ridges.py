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

"""Utility functions for box pleating ridges.

The main function is assign_ridges which assigns folds to ridges in two steps.
"""

from collections.abc import Sequence
import math
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import vertex
from bp_pipeline.solving import utils


def _y_fold_from_ridge(
    ref_ridge: crease.Crease,
    ridges: Sequence[crease.Crease],
    pleats: Sequence[crease.Crease],
    *,
    pleats_tip_index: utils.TipIndex | None = None,
) -> crease.Fold | None:
  """Check if a ridge intersects another ridge and a pleat to form a Y shape.

  If so, returns the fold of the pleat and None otherwise.

  Args:
    ref_ridge: The reference ridge.
    ridges: The list of all ridges.
    pleats: The list of all pleats.
    pleats_tip_index: Optional spatial tip index over pleats.

  Returns:
    The fold of the pleat or None.
  """
  for ridge in ridges:
    if ref_ridge.is_parallel(ridge):
      continue
    intersection_point = ref_ridge.vertex_with_crease(ridge)
    if not intersection_point:
      continue  # 2 ridges
    if pleats_tip_index is not None:
      intersecting_pleats = pleats_tip_index.creases_at_tip(intersection_point)
    else:
      intersecting_pleats = [
          pleat for pleat in pleats if pleat.is_tip(intersection_point)
      ]
    if len(intersecting_pleats) != 1:
      continue
    # we need to distinguish "arrow like" vertices from Y shaped intersection
    v = vertex.Vertex(intersecting_pleats + [ridge, ref_ridge])  # check Y
    sector_angles = sorted([angle for angle, _, _ in v.sector_angles()])
    if all(
        math.isclose(sector_angle, ref_angle)
        for sector_angle, ref_angle in zip(
            sector_angles, [90.0, 135.0, 135.0], strict=True
        )
    ):
      return intersecting_pleats[0].fold
  return None


def _get_fold_from_intersection(
    ridge: crease.Crease,
    intersecting_ridge: crease.Crease,
    intersecting_ridges: Sequence[crease.Crease],
) -> crease.Fold:
  """Return the fold of the ridge based on intersections with other ridges.

  Ridges are at 45 degrees, therefore there are only intersections with 2 or 4
  ridges. There are 3 cases for assignment:
      1. Four ridges intersect in an X shape - same fold.
      2. Two parallel ridges - different fold.
      3. Two perpendicular ridges - same fold.

  Args:
    ridge: The ridge to assign the fold to.
    intersecting_ridge: The ridge that intersects the ridge.
    intersecting_ridges: The list of ridges that intersect the ridge.

  Returns:
    The fold of the ridge.
  """
  interesecting_ridges_intersections = len(
      utils.get_interesecting_non_overlapping_creases(
          intersecting_ridge, intersecting_ridges
      )
  )
  # A crease in an x shape intersect 4 creaes, three are in the x, and one is
  # not. It can also intersect 6 creases, 3 in each x shape.
  # Each one of the three that are in the x, intersects the two others.
  # In the case of 6 intersections, all folds should be the same.
  # Finally, when an X shape is on the border, one of the 4 creases can already
  # be assigned and there will be only 3 intersecting ridges because the border
  # crease is not included in the list of intersecting ridges.
  if (
      len(intersecting_ridges) in [3, 4, 6]
      and interesecting_ridges_intersections == 2
  ):
    return ridge.fold
  elif intersecting_ridge.is_parallel(ridge):
    return ridge.mountain_to_valley()
  else:
    return ridge.fold


def _no_fold_hash(crease_: crease.Crease) -> int:
  """Returns a hash of the crease points."""
  return hash(
      tuple([
          hash(crease_.p1.x),
          hash(crease_.p1.y),
          hash(crease_.p2.x),
          hash(crease_.p2.y),
      ])
  )


def border_ridge_fold(
    ridge: crease.Crease,
    intersecting_pleats: list[crease.Crease],
) -> crease.Fold:
  """Returns the fold of the ridge based on intersections with pleats."""
  # Sometimes the border ridge will be connected to a vertex with 4 hinges
  # (see cp_test_fixtures.WATERBOMB); in this case, intersecting pleats will be
  # empty and cannot be used to determine the fold.
  if (ridge.p1.is_border and ridge.p2.is_border) or not intersecting_pleats:
    return crease.Fold.MOUNTAIN  # Arbitrarily assign mountain fold.
  fold = intersecting_pleats[0].fold
  if len(intersecting_pleats) == 2:
    vertex_ = vertex.Vertex([ridge] + intersecting_pleats)
    sector_angles = sorted([angle for angle, _, _ in vertex_.sector_angles()])
    if all(
        math.isclose(sector_angle, ref_angle)
        for sector_angle, ref_angle in zip(
            sector_angles, [45.0, 45.0, 270.0], strict=True
        )
    ):
      fold = fold.flip()
    return fold
  elif len(intersecting_pleats) > 2:
    fold = fold.flip()
  return fold


def assign_ridges(
    ridges: list[crease.Crease],
    pleats: list[crease.Crease],
    grid_size: int,
    recovery: bool = False,
) -> list[crease.Crease]:
  """Assigns folds to ridges in two steps.

  The first step is to assign folds to the ridges that intersect a pleat and
  form a Y shape by the orientation of the pleat.
  The second step is to assign folds to the ridges that intersect other ridges.

  Args:
    ridges: The ridges to assign folds to.
    pleats: The pleats to assign folds to.
    grid_size: The size of the grid.
    recovery: Whether to enable extended interior tip seeding for closed rings.

  Returns:
    list[crease.Crease]
  """
  assigned_ridges = []
  assigned_overlap_index = utils.LineOverlapIndex(grid_size=grid_size)
  pleats_tip_index = utils.TipIndex(pleats, grid_size=grid_size)
  paths = utils.creases_to_paths(ridges)
  grid_points = utils.create_grid_points(grid_size)
  for path in paths:
    split_ridges = []
    for ridge in path:
      split_ridges.extend(ridge.split_to_segments(pleats, grid_points))

    seen = []
    for ridge in split_ridges:
      # Find a reference point with a 'Y' shape (two perpendicular ridges and a
      # pleat). All the creases in the Y shape vertex have the same fold, which
      # can be decided by the orientation of the pleat.
      fold = _y_fold_from_ridge(
          ridge, path, pleats, pleats_tip_index=pleats_tip_index
      )
      if fold is None:
        continue
      assigned_ridge = crease.Crease(ridge.p1, ridge.p2, fold=fold)
      assigned_ridges.append(assigned_ridge)
      assigned_overlap_index.add(assigned_ridge)
      seen.append(ridge)
    if not seen:  # if there was no Y shape in the path, assign border ridges
      for ridge in split_ridges:
        if ridge.intersects_border:
          internal_point = ridge.p1 if ridge.p2.is_border else ridge.p2
          intersecting_pleats = pleats_tip_index.creases_at_tip(internal_point)
          if not intersecting_pleats:
            continue
          assigned_ridge = crease.Crease(
              ridge.p1,
              ridge.p2,
              fold=border_ridge_fold(ridge, intersecting_pleats),
          )
          assigned_ridges.append(assigned_ridge)
          assigned_overlap_index.add(assigned_ridge)
          seen.append(ridge)
          break
    if recovery:
      if not seen:
        for ridge in split_ridges:
          for pt in (ridge.p1, ridge.p2):
            if pt.is_border:
              continue
            intersecting_pleats = pleats_tip_index.creases_at_tip(pt)
            if not intersecting_pleats:
              continue
            assigned_ridge = crease.Crease(
                ridge.p1,
                ridge.p2,
                fold=border_ridge_fold(ridge, intersecting_pleats),
            )
            assigned_ridges.append(assigned_ridge)
            assigned_overlap_index.add(assigned_ridge)
            seen.append(ridge)
            break
          if seen:
            break
      if not seen and split_ridges:
        ridge = split_ridges[0]
        assigned_ridge = crease.Crease(
            ridge.p1, ridge.p2, fold=crease.Fold.MOUNTAIN
        )
        assigned_ridges.append(assigned_ridge)
        assigned_overlap_index.add(assigned_ridge)
        seen.append(ridge)

    for ridge in seen:
      split_ridges.remove(ridge)
    all_path_ridges = split_ridges + assigned_ridges
    path_tip_index = utils.TipIndex(all_path_ridges, grid_size=grid_size)
    intersections = {
        _no_fold_hash(ridge): path_tip_index.non_overlapping_at_tip(ridge)
        for ridge in all_path_ridges
    }
    # Assign folds to the ridges that intersect other ridges.
    next_ridges = assigned_ridges[:]
    while next_ridges:
      new_ridges = []
      for ridge in next_ridges:
        interesecting_ridges = intersections[_no_fold_hash(ridge)]
        for interesecting_ridge in interesecting_ridges:
          if assigned_overlap_index.has_overlap(interesecting_ridge):
            continue
          fold = _get_fold_from_intersection(
              ridge, interesecting_ridge, interesecting_ridges
          )
          assigned_ridge = crease.Crease(
              interesecting_ridge.p1, interesecting_ridge.p2, fold=fold
          )
          new_ridges.append(assigned_ridge)
      next_ridges = new_ridges
      assigned_ridges.extend(new_ridges)
      for r in new_ridges:
        assigned_overlap_index.add(r)

  return utils.deduplicate(assigned_ridges)
