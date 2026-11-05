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

"""Utility functions for removing central folds."""

import math

from bp_pipeline import rectangle as rectangle_lib
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import crease_pattern as cp_utils
from bp_pipeline.crease_pattern import point
from bp_pipeline.crease_pattern import symmetry
from bp_pipeline.packing import packing_output
from bp_pipeline.packing import types as packing_types
from bp_pipeline.solving import utils as box_pleating_utils

_DEFAULT_TOLERANCE = 1e-3


def _one_hinge_at_central_point(
    point_: point.Point, hinges: list[crease.Crease]
) -> bool:
  """Checks if there is exactly one hinge at the given point."""
  return (
      sum(hinge.is_tip(point_) for hinge in hinges) == 1
      and not point_.is_border
  )


def should_try_to_remove_central_crease(
    creases: list[crease.Crease], hinges: list[crease.Crease]
) -> bool:
  """Returns true if the central crease should be removed."""
  for hinge in hinges:
    if _one_hinge_at_central_point(hinge.p1, hinges):
      return False
    elif _one_hinge_at_central_point(hinge.p2, hinges):
      return False
  creases_ = [
      c
      for c in creases
      if c.is_vertical and math.isclose(c.p1.x, 0.5, rel_tol=_DEFAULT_TOLERANCE)
  ]
  if not creases_:
    return False
  symmetry_crease = merge_to_unfolded_crease(creases_)
  return math.isclose(
      symmetry_crease.p1.y, 0, rel_tol=_DEFAULT_TOLERANCE
  ) and math.isclose(symmetry_crease.p2.y, 1, rel_tol=_DEFAULT_TOLERANCE)


def whether_crease_on_symmetry_axis(
    crease_: crease.Crease, transform: symmetry.Transform
) -> bool:
  """Returns true if crease_ is on the symmetry axis."""
  if transform == symmetry.Transform.VERTICAL_FLIP:
    if not crease_.is_vertical:
      return False
    return crease_.p1.x == 0.5
  elif transform == symmetry.Transform.HORIZONTAL_FLIP:
    if not crease_.is_horizontal:
      return False
    return crease_.p1.y == 0.5
  else:
    raise ValueError(f'Unsupported transform: {transform}')


def central_crease_from_transform(
    transform: symmetry.Transform,
) -> crease.Crease:
  """Returns the central crease for a given symmetry transform."""
  if transform == symmetry.Transform.VERTICAL_FLIP:
    return crease.Crease(
        point.Point(x=0.5, y=0), point.Point(x=0.5, y=1), fold=crease.Fold.HINGE
    )
  elif transform == symmetry.Transform.HORIZONTAL_FLIP:
    return crease.Crease(
        point.Point(x=0, y=0.5), point.Point(x=1, y=0.5), fold=crease.Fold.HINGE
    )
  else:
    raise ValueError(f'Unsupported transform: {transform}')


def merge_to_unfolded_crease(creases: list[crease.Crease]) -> crease.Crease:
  """Merges a list of connected creases into a single unfolded crease.

  Args:
    creases: The creases to check.

  Returns:
    The merged crease.
  """
  unassinged_creases = [
      crease.Crease(c.p1, c.p2, fold=crease.Fold.TRIANGLE) for c in creases
  ]
  merged_crease = unassinged_creases[0].merge_with_segments(unassinged_creases)
  return merged_crease


def is_valid_central_crease_removal(
    creases: list[crease.Crease], central_crease: crease.Crease
) -> bool:
  """Returns whether central crease removal is valid.

  A valid central crease removal is possible if the central crease is fully
  contained within the creases.

  Args:
    creases: The creases to check.
    central_crease: The central crease to check.
  """
  if not creases:
    return False
  merged_crease = merge_to_unfolded_crease(creases)
  return merged_crease.isclose(central_crease)


def can_transform_central_crease(
    pleats: list[crease.Crease],
    ridges: list[crease.Crease],
    hinges: list[crease.Crease],
    unsplit_hinges: list[crease.Crease] | None = None,
    *,
    transform: symmetry.Transform = symmetry.Transform.VERTICAL_FLIP,
    grid_size: int | None = None,
    check_should_try: bool = True,
    candidate_hinges_for_should_try: list[crease.Crease] | None = None,
) -> bool:
  """Oracle returning whether central-crease opening can transform the creases.

  Delegates to `should_try_to_remove_central_crease`,
  `remove_creases_overlapping_central_crease`,
  `is_valid_central_crease_removal`, and (when `grid_size` is provided)
  verifies that the diagonal replacement and pleat reassignment steps complete
  without error.

  Args:
    pleats: Active pleat creases in the pattern.
    ridges: Active ridge creases in the pattern.
    hinges: Active hinge creases (or unsplit hinges) in the pattern.
    unsplit_hinges: Optional unsplit macro-hinges corresponding to `hinges`.
      Defaults to `hinges` when omitted.
    transform: Symmetry transform of the pattern.
    grid_size: Optional grid size for validating diagonal replacement.
    check_should_try: If True, also verifies
      `should_try_to_remove_central_crease`.
    candidate_hinges_for_should_try: Optional full list of unvisited
      macro-hinges for `should_try_to_remove_central_crease` (defaults to
      `unsplit_hinges` or `hinges`).

  Returns:
    True if central crease removal is valid and transformable.
  """
  if transform not in (
      symmetry.Transform.HORIZONTAL_FLIP,
      symmetry.Transform.VERTICAL_FLIP,
  ):
    return False
  if unsplit_hinges is not None:
    eff_unsplit = list(unsplit_hinges)
  else:
    eff_unsplit = list(hinges)
  eff_should_try_hinges = (
      list(candidate_hinges_for_should_try)
      if candidate_hinges_for_should_try is not None
      else eff_unsplit
  )
  try:
    if check_should_try and not should_try_to_remove_central_crease(
        list(eff_should_try_hinges) + list(ridges) + list(pleats),
        list(eff_should_try_hinges),
    ):
      return False
    rem_pleats, removed_pleats = remove_creases_overlapping_central_crease(
        list(pleats), transform
    )
    rem_ridges, removed_ridges = remove_creases_overlapping_central_crease(
        list(ridges), transform
    )
    _, removed_hinges = remove_creases_overlapping_central_crease(
        list(hinges), transform
    )
    _, removed_unsplit_hinges = remove_creases_overlapping_central_crease(
        eff_unsplit, transform
    )
    central_crease = central_crease_from_transform(transform)
    if not is_valid_central_crease_removal(
        removed_pleats + removed_ridges + removed_hinges,
        central_crease,
    ):
      return False
    if grid_size is not None:
      _ = reassign_pleats(
          list(rem_pleats),
          list(removed_unsplit_hinges),
          grid_size,
          list(rem_ridges),
      )
      diag_ridges = list(rem_ridges) + add_diagonals_to_removed_ridges(
          list(removed_ridges), grid_size
      )
      _ = add_diagonals_to_removed_hinges_and_shorten_flaps(
          diag_ridges, list(removed_unsplit_hinges), grid_size
      )
  except (ValueError, IndexError, ZeroDivisionError):
    return False
  return True


def remove_creases_overlapping_central_crease(
    creases: list[crease.Crease],
    transform: symmetry.Transform,
) -> tuple[list[crease.Crease], list[crease.Crease]]:
  """Removes creases that overlap the symmetry axis.

  Args:
    creases: The creases to remove central creases from.
    transform: The symmetry transform to use.

  Returns:
    A tuple of two lists of crease patterns:
      - The first list contains the creases that do not overlap the symmetry
        axis.
      - The second list contains the creases that do overlap the symmetry
        axis.
  """
  symmetry_crease = central_crease_from_transform(transform)
  new_creases = []
  removed_creases = []
  for c in creases:
    if c.is_overlapping(symmetry_crease):
      removed_creases.append(c)
    else:
      new_creases.append(c)
  return new_creases, removed_creases


def create_diagonal_creases(
    crease_: crease.Crease,
    grid_size: int,
    offset: int = 0,
    fold: crease.Fold = crease.Fold.VALLEY,
    central_hinge: bool = False,
) -> list[crease.Crease]:
  """Create two zigzag lines with 90 degree angles around crease_.

  Start in p1 (higher) and walk down.
  If offset is 0, the diagonals start from p1. If its 1, they start next to p1.
  For example, for a line that looks like:
  ------,
  the following creases will be returned:
  <><><>.
  The diagonals change direction every grid size.

  The fold assignment of the diagonal creases is as follows:
    1. Starts with the given fold.
    2. Flips in every grid size.
    3. The two diagonal lines are symmetric.

  Args:
    crease_: A single unassigned merged crease representing an entire ridge or
      hinge.
    grid_size: The grid size used for discretizing the crease pattern.
    offset: The offset to apply to the diagonal creases, to reflect the fact
      that they could be shortened (offset=1).
    fold: The fold to use for the diagonal creases.
    central_hinge: Whether the crease_ is a central hinge.

  Returns:
    A list of `crease.Crease` objects forming the diagonal zigzag pattern.
  """
  if not crease_.is_vertical:
    raise ValueError(f'Expected vertical crease, got {crease_}')
  start_point = crease_.p1  # the point with the smallest y
  length_in_grid_points = round(crease_.length * grid_size)
  digonal_creases = []
  x_plus = start_point.x + 1 / grid_size
  x_minus = start_point.x - 1 / grid_size
  x0 = start_point.x
  symmetric = (
      central_hinge
      and length_in_grid_points % 2 == 0
      and length_in_grid_points % 4 != 0
  )

  for i in range(length_in_grid_points):
    y = start_point.y + i / grid_size
    y_up = start_point.y + (i + 1) / grid_size
    if (i + offset) % 2 == 0:
      digonal_creases.append(
          crease.Crease(
              point.Point(x=x0, y=y),
              point.Point(x=x_minus, y=y_up),
              fold=fold,
          )
      )
      digonal_creases.append(
          crease.Crease(
              point.Point(x=x0, y=y),
              point.Point(x=x_plus, y=y_up),
              fold=fold,
          )
      )
    else:
      digonal_creases.append(
          crease.Crease(
              point.Point(x=x0, y=y_up),
              point.Point(x=x_minus, y=y),
              fold=fold,
          )
      )
      digonal_creases.append(
          crease.Crease(
              point.Point(x=x0, y=y_up),
              point.Point(x=x_plus, y=y),
              fold=fold,
          )
      )
    fold = fold.flip()
    if symmetric and i == length_in_grid_points // 2 - 1:
      fold = fold.flip()
  return digonal_creases


def add_diagonals_to_removed_ridges(
    ridges: list[crease.Crease],
    grid_size: int,
) -> list[crease.Crease]:
  """Adds diagonal creases to replace removed ridges.

  The removed ridges are organized into paths (connected components). For each
  path, a single unfolded crease is created, and then diagonal creases are
  created around it.

  Args:
    ridges: The ridges to add diagonals to.
    grid_size: The grid size used for discretizing the crease pattern.

  Returns:
    The diagonal creases.
  """
  diagonal_creases = []
  paths = box_pleating_utils.creases_to_paths(ridges)
  for path in paths:
    merged_ridge = merge_to_unfolded_crease(path)
    odd = round(merged_ridge.length * grid_size) % 2 == 1
    offset = odd if merged_ridge.p1.is_border else 0
    diagonal_creases.extend(
        create_diagonal_creases(merged_ridge, grid_size, offset=offset)
    )
  return diagonal_creases


def shorten_hinge(
    hinge: crease.Crease, grid_size: int, central_hinge: bool
) -> crease.Crease:
  """Shortens a hinge by a single grid size."""
  if not hinge.is_vertical:
    raise ValueError(f'Expected vertical hinge, got {hinge}')
  x = hinge.p1.x
  y1 = hinge.p1.y
  if central_hinge or not hinge.p1.is_border:
    y1 += 1 / grid_size
  y2 = hinge.p2.y
  if central_hinge or not hinge.p2.is_border:
    y2 -= 1 / grid_size
  return crease.Crease(
      point.Point(x=x, y=y1),
      point.Point(x=x, y=y2),
      fold=hinge.fold,
  )


def shorten_points(
    hinge: crease.Crease, shortened_hinge: crease.Crease
) -> list[point.Point]:
  """Returns the points of a hinge that are not on the shortened hinge."""
  points = []
  for point_ in [hinge.p1, hinge.p2]:
    if not shortened_hinge.is_tip(point_):
      points.append(point_)
  return points


def get_offset_and_fold(
    merged_hinge: crease.Crease,
    shortened_hinge: crease.Crease,
    grid_size: int,
    fold: crease.Fold,
    central_hinge: bool = False,
) -> tuple[int, crease.Fold]:
  """Calculates the offset for creating diagonal creases.

  The offset ensures that the diagonal pattern starts correctly from the
  shortened hinge. The walk for creating diagonals always starts from the
  `p1` of the `merged_hinge`. We also need to flip the fold if the `p2` of the
  `merged_hinge` was shortened.

  Args:
    merged_hinge: The original, unshortened hinge.
    shortened_hinge: The hinge after being shortened.
    grid_size: The grid size used for discretizing the crease pattern.
    fold: The fold to use for the diagonal creases.
    central_hinge: Whether the hinge is a central hinge.

  Returns:
    A tuple of the offset and the fold to use for the diagonal creases.

  Raises:
    ValueError: If the shortened hinge is not a subsegment of the merged hinge
      starting or ending at one of its tips.
  """
  even = round(shortened_hinge.length * grid_size) % 2 == 0
  if central_hinge:
    return 1, fold.flip()
  elif merged_hinge.is_tip(shortened_hinge.p1):
    # p2, the lower point, was shortened. p1 is either border of shortened.
    return even, fold.flip() if even else fold
  elif merged_hinge.is_tip(shortened_hinge.p2):
    # p1, the higher point, was shortened. The walk will start from p1 so we
    # need to add an offset of 1 to the walk.
    return 1, fold
  else:
    raise ValueError('The shortened hinge is not a tip of the merged hinge.')


def _two_length_central_hinge(
    hinge: crease.Crease, grid_size: int, central_hinge: bool
) -> bool:
  """True if the hinge has length 2 and belongs to a one-length central flap."""
  length_in_grid_points = rectangle_lib.integer_crease_grid_length(
      hinge, grid_size
  )
  return length_in_grid_points == 2 and central_hinge


def _one_length_hinge(
    hinge: crease.Crease, grid_size: int, central_hinge: bool
) -> bool:
  """Returns true if the hinge belongs to a one-length flap."""
  length_in_grid_points = rectangle_lib.integer_crease_grid_length(
      hinge, grid_size
  )
  return length_in_grid_points == 1 or _two_length_central_hinge(
      hinge, grid_size, central_hinge
  )


def _border_hinge_with_two_ridges(
    hinge: crease.Crease, ridges: list[crease.Crease]
) -> bool:
  """Checks if the hinge is a border hinge with two ridges."""
  return (
      hinge.intersects_border
      and any(ridge.is_tip(hinge.p1) for ridge in ridges)
      and any(ridge.is_tip(hinge.p2) for ridge in ridges)
  )


def _central_hinge(hinge: crease.Crease, ridges: list[crease.Crease]) -> bool:
  """Checks if the hinge is a central hinge."""
  return (
      _border_hinge_with_two_ridges(hinge, ridges)
      or not hinge.intersects_border
  )


def _shorten_hinge_and_points(hinge, grid_size, central_hinge):
  if _one_length_hinge(hinge, grid_size, central_hinge):
    shorten_points_ = [hinge.p1, hinge.p2]
    shortened_hinge = hinge  # never used
  elif central_hinge:
    shorten_points_ = [hinge.p1, hinge.p2]  # use both tips, even if on border
    shortened_hinge = shorten_hinge(hinge, grid_size, central_hinge)
  else:
    shortened_hinge = shorten_hinge(hinge, grid_size, central_hinge)
    shorten_points_ = shorten_points(hinge, shortened_hinge)
  return shortened_hinge, shorten_points_


def add_diagonals_to_removed_hinges_and_shorten_flaps(
    ridges: list[crease.Crease],
    hinges: list[crease.Crease],
    grid_size: int,
) -> list[crease.Crease]:
  """Adds diagonal creases to replace removed ridges.

  The removed ridges are organized into paths (connected components). For each
  path, a single unfolded crease is created, and then diagonal creases are
  created around it.

  Args:
    ridges: The ridges to add diagonals to.
    hinges: The hinges to add diagonals to.
    grid_size: The grid size used for discretizing the crease pattern.

  Returns:
    The diagonal creases.
  """
  ridges_to_remove = []
  for hinge in hinges:
    central_hinge = _central_hinge(hinge, ridges)
    shortened_hinge, shorten_points_ = _shorten_hinge_and_points(
        hinge, grid_size, central_hinge
    )
    fold = crease.Fold.VALLEY
    for point_ in shorten_points_:
      for ridge in ridges:
        if ridge.is_tip(point_):
          ridges_to_remove.append(ridge)
          fold = ridge.fold
    if not _one_length_hinge(hinge, grid_size, central_hinge):
      offset, fold = get_offset_and_fold(
          hinge, shortened_hinge, grid_size, fold, central_hinge
      )
      ridges.extend(
          create_diagonal_creases(
              shortened_hinge, grid_size, offset, fold, central_hinge
          )
      )
  for ridge in ridges_to_remove:
    if ridge in ridges:
      ridges.remove(ridge)
  return ridges


def reassign_pleats(
    pleats: list[crease.Crease],
    removed_hinges: list[crease.Crease],
    grid_size: int,
    ridges: list[crease.Crease],
) -> list[crease.Crease]:
  """Reassigns pleats to the new ridges."""
  new_pleats = []
  removed_pleats = []
  for hinge in removed_hinges:
    central_hinge = _central_hinge(hinge, ridges)
    if not (hinge.is_vertical and central_hinge):
      continue
    if _two_length_central_hinge(hinge, grid_size, central_hinge):
      pleats_to_check = [
          crease.Crease(
              point.Point(x=0.5 - 1 / grid_size, y=hinge.p1.y + 1 / grid_size),
              point.Point(x=0.5 + 1 / grid_size, y=hinge.p1.y + 1 / grid_size),
              fold=crease.Fold.MOUNTAIN,
          )
      ]
    else:
      shortened_hinge = shorten_hinge(hinge, grid_size, central_hinge)
      divided_by_four = round(shortened_hinge.length * grid_size) % 4 == 0
      y1 = shortened_hinge.p1.y
      y2 = shortened_hinge.p2.y
      pleats_to_check = [
          crease.Crease(
              point.Point(x=0.5 - 1 / grid_size, y=y1),
              point.Point(x=0.5 + 1 / grid_size, y=y1),
              fold=crease.Fold.MOUNTAIN,
          )
      ]
      if not divided_by_four:
        pleats_to_check.append(
            crease.Crease(
                point.Point(x=0.5 - 1 / grid_size, y=y2),
                point.Point(x=0.5 + 1 / grid_size, y=y2),
                fold=crease.Fold.MOUNTAIN,
            )
        )
    for pleat in pleats:
      if any(pleat.isclose(pleat_) for pleat_ in pleats_to_check):
        removed_pleats.append(pleat)
        new_pleat = pleat.flip_fold()
        new_pleats.append(new_pleat)
  pleats.extend(new_pleats)
  for pleat in removed_pleats:
    pleats.remove(pleat)
  return pleats


def _length_one_ridge(ridge: crease.Crease, grid_size: int) -> bool:
  """Checks if the ridge is a length-1."""
  return math.isclose(ridge.length, 1.0 / grid_size) or math.isclose(
      ridge.length, math.sqrt(2) / grid_size
  )


def try_to_append_point(x: float, y: float) -> list[point.Point]:
  """Clips x to the interval [0, 1]."""
  try:
    return [point.Point(x=x, y=y)]
  except ValueError:
    return []


def shorten_ridge(
    ridge: crease.Crease, point_to_shorten: point.Point, grid_size: int
) -> crease.Crease:
  """Shortens a ridge by a single grid size."""
  point_to_shorten = (
      ridge.p1 if ridge.p1.isclose(point_to_shorten) else ridge.p2
  )
  point_to_keep = ridge.p1 if ridge.p2.isclose(point_to_shorten) else ridge.p2
  x = point_to_shorten.x
  y = point_to_shorten.y
  point_candidates = []
  point_candidates.extend(
      try_to_append_point(x + 1 / grid_size, y - 1 / grid_size)
  )
  point_candidates.extend(
      try_to_append_point(x - 1 / grid_size, y + 1 / grid_size)
  )
  point_candidates.extend(
      try_to_append_point(x + 1 / grid_size, y + 1 / grid_size)
  )
  point_candidates.extend(
      try_to_append_point(x - 1 / grid_size, y - 1 / grid_size)
  )
  for point_candidate in point_candidates:
    ridge_candidate = crease.Crease(
        point_candidate,
        point_to_keep,
        fold=crease.Fold.MOUNTAIN,
    )
    if (
        ridge_candidate.length < ridge.length
        and ridge_candidate.is_overlapping(ridge)
    ):
      return ridge_candidate
  raise ValueError(f'No valid shortening found for ridge: {ridge}')


def _new_hinges(hinge: crease.Crease, grid_size: int) -> list[crease.Crease]:
  """Returns two new hinges that are one grid size away from the given hinge."""
  if not hinge.is_vertical:
    raise ValueError(f'Expected vertical hinge, got {hinge}')
  return [
      crease.Crease(
          point.Point(x=hinge.p1.x + 1 / grid_size, y=hinge.p1.y),
          point.Point(x=hinge.p2.x + 1 / grid_size, y=hinge.p2.y),
          fold=crease.Fold.HINGE,
      ),
      crease.Crease(
          point.Point(x=hinge.p1.x - 1 / grid_size, y=hinge.p1.y),
          point.Point(x=hinge.p2.x - 1 / grid_size, y=hinge.p2.y),
          fold=crease.Fold.HINGE,
      ),
  ]


def _new_river_hinge(
    hinge: crease.Crease,
    shorten_points_: list[point.Point],
    grid_size: int,
    creases: list[crease.Crease],
    new_ridges: list[crease.Crease],
) -> list[crease.Crease]:
  """Returns a river hinge that is created from shortening the given hinge."""
  if not hinge.is_vertical:
    raise ValueError(f'Expected vertical hinge, got {hinge}')
  grid_points = box_pleating_utils.create_grid_points(grid_size)
  rivers = []
  for point_ in shorten_points_:
    river_hinge = crease.Crease(
        point.Point(x=0, y=point_.y),
        point.Point(x=1, y=point_.y),
        fold=crease.Fold.HINGE,
    )
    segments = river_hinge.split_to_segments(creases, grid_points)
    for segment in segments:
      if segment.p1.x < 0.5 and segment.p2.x > 0.5:
        # Don't add the segment that overlaps the symmetry axis.
        continue
      if any(segment.intersect_at_tip(ridge) for ridge in new_ridges):
        rivers.append(segment)
  return rivers


def new_flap_rectangles(
    packing_information: packing_output.PackingOutput,
    grid_size: int,
) -> tuple[list[rectangle_lib.Rectangle], list[crease.Crease]]:
  """Returns a list of new flap rectangles, shortened if on the symmetry line.

  Args:
    packing_information: The packing information containing the flap rectangles.
    grid_size: The grid size used for discretizing the crease pattern.

  Returns:
    The new flap rectangles and the new hinges.
  """
  new_rectangles = []
  new_hinges = []
  for rect in packing_information.flap_rectangles:  # pyrefly: ignore[not-iterable]
    if rect.is_on_symmetry_line(grid_size):
      try:
        shortened_rectangle = rectangle_lib.Rectangle.shrinked_by_one(rect)
        if shortened_rectangle.x_len == 0 or shortened_rectangle.y_len == 0:
          continue
        new_rectangles.append(shortened_rectangle)
        clipped_rectangle = shortened_rectangle.clip(
            xmin=0.0,
            ymin=0.0,
            xmax=float(grid_size),
            ymax=float(grid_size),
        )
        if clipped_rectangle:
          edges = [
              edge
              for edge in clipped_rectangle.normalize_rectangle(grid_size).edges
              if not edge.is_overlapping_border
          ]
          new_hinges.extend(edges)
      except ValueError:
        # The rectangle was of size 1 and got shortened to size 0.
        pass
    else:
      new_rectangles.append(rect)
  return new_rectangles, new_hinges


def add_new_flap_hinges(
    hinge: crease.Crease, grid_size: int
) -> list[crease.Crease]:
  """Adds new hinges for 1-length flaps on the symmetry axis.

  Args:
    hinge: The central hinge crease.
    grid_size: The grid size for discretizing the crease pattern.

  Returns:
    A list of newly created hinge creases.
  """
  if not hinge.is_vertical:
    raise ValueError(f'Expected vertical hinge, got {hinge}')
  start_point = hinge.p1  # the point with the smallest y
  length_in_grid_points = rectangle_lib.integer_crease_grid_length(
      hinge, grid_size
  )
  new_hinges = []
  x_plus = 0.5 + 1 / grid_size
  x_minus = 0.5 - 1 / grid_size
  start_ind = 0
  end_ind = length_in_grid_points + 1
  if length_in_grid_points % 2 == 1:  # odd length, only one border
    if start_point.is_border:
      start_ind = 1
    else:
      end_ind = length_in_grid_points
  for i in range(start_ind, end_ind, 2):
    y = start_point.y + i / grid_size
    new_hinges.append(
        crease.Crease(
            point.Point(x=x_minus, y=y),
            point.Point(x=x_plus, y=y),
            fold=crease.Fold.HINGE,
        )
    )
  return new_hinges


def repack_cp_with_shortened_flaps(
    packing_information: packing_output.PackingOutput,
    grid_size: int,
) -> packing_output.PackingOutput:
  """Recomputes the packing cp with the shortened flaps.

  Note that we don't pack new flaps on the symmetry axis (we don't shape it).

  1. Find hinges on the symmetry axis.
  2. For each hinge:
    a. Shorten the hinge.
    b. Shorten the corresponding ridges.
    c. Add new "river" hinges.

  Don't repack on the symmetry axis (we don't shape it).

  Args:
    packing_information: The packing information used for packing.
    grid_size: The grid size used for discretizing the crease pattern.

  Returns:
    The new packing information with the shortened flaps, the new packing cp and
    the new hinges.
  """
  if not packing_information.packing_cp:
    raise ValueError('packing_information.packing_cp is required.')
  packing_cp = packing_information.packing_cp
  ridges = [c for c in packing_cp.creases if c.fold == crease.Fold.MOUNTAIN]
  hinges = [c for c in packing_cp.creases if c.fold == crease.Fold.HINGE]
  borders = [c for c in packing_cp.creases if c.fold == crease.Fold.BORDER]
  transform = symmetry.symmetry_axis(
      cp_utils.CreasePattern(hinges, light_mode=True)
  )
  removed_hinges = []
  hinges_on_symmetry_axis = []
  for hinge in hinges:
    if whether_crease_on_symmetry_axis(hinge, transform):
      hinges_on_symmetry_axis.append(hinge)
  for hinge in hinges_on_symmetry_axis:
    central_hinge = _central_hinge(hinge, ridges)
    if _one_length_hinge(hinge, grid_size, central_hinge):
      hinges.remove(hinge)
      removed_hinges.append(hinge)
      continue
    shortened_hinge, shorten_points_ = _shorten_hinge_and_points(
        hinge, grid_size, central_hinge
    )
    new_ridges = []
    for point_ in shorten_points_:
      for ridge in ridges:
        if ridge.is_tip(point_) and not _length_one_ridge(ridge, grid_size):
          new_ridges.append(shorten_ridge(ridge, point_, grid_size))
    hinges.remove(hinge)
    removed_hinges.append(hinge)
    hinges.extend(_new_hinges(shortened_hinge, grid_size))
    hinges.extend(add_new_flap_hinges(shortened_hinge, grid_size))
    hinges.extend(
        _new_river_hinge(
            shortened_hinge, shorten_points_, grid_size, ridges, new_ridges
        )
    )
    ridges.extend(new_ridges)
  ridges = add_diagonals_to_removed_hinges_and_shorten_flaps(
      ridges, removed_hinges, grid_size
  )
  new_packing_ridges = [
      crease.Crease(ridge.p1, ridge.p2, fold=crease.Fold.MOUNTAIN)
      for ridge in ridges
  ]
  new_flap_rectangles_, new_hinges = new_flap_rectangles(
      packing_information, grid_size
  )
  hinges.extend(new_hinges)
  new_hinges_info = create_hinges_information(
      hinge_infos=packing_information.hinges,  # pyrefly: ignore[bad-argument-type]
      rectangles=new_flap_rectangles_,
      hinges=hinges,
      grid_size=grid_size,
  )
  return packing_output.PackingOutput(
      success=packing_information.success,
      packing_cp=cp_utils.CreasePattern(
          creases=new_packing_ridges + borders + hinges, grid_size=grid_size
      ),
      flap_rectangles=packing_information.flap_rectangles,
      packing_rivers=packing_information.packing_rivers,
      stick_figure=packing_information.stick_figure,
      hinges=new_hinges_info,
      tracker=packing_information.tracker,
      error_message=packing_information.error_message,
      details=packing_information.details,
  )


def _flap_names_from_hinge_and_rectangles(
    hinge: crease.Crease,
    rectangles: list[rectangle_lib.Rectangle],
    grid_size: int,
) -> tuple[str, str]:
  """Returns the names of the flaps that overlap the given hinge."""
  flap_names = []
  for rect in rectangles:
    normalized_rect = rect.normalize_rectangle(grid_size)
    if any(hinge.is_overlapping(edge) for edge in normalized_rect.edges):
      flap_names.append(rect.name)
  if len(flap_names) >= 3:
    raise ValueError('A hinge can overlap at most two flaps.')
  flap_names.sort()
  return tuple(flap_names)


def create_hinges_information(
    hinge_infos: list[packing_types.HingeInfo],
    hinges: list[crease.Crease],
    rectangles: list[rectangle_lib.Rectangle],
    grid_size: int,
) -> list[packing_types.HingeInfo]:
  """This function creates a list of hinge information objects.

  Args:
    hinge_infos: The list of hinge info before the central fold removal.
    hinges: The list of new hinges, after the central fold removal.
    rectangles: The list of new flap rectangles.
    grid_size: The grid size used for discretizing the crease pattern.

  Returns:
    The list of hinge info after the central fold removal.
  """
  new_hinge_infos = []
  # Keep the hinge information of the hinges that were not removed
  hinges_with_hash = crease.Creases.create_from_creases(creases=hinges)
  for hinge_info in hinge_infos:
    if (
        crease.CreaseWithExactMatch(crease=hinge_info.coordinate)  # pyrefly: ignore[bad-argument-type]
        in hinges_with_hash
    ):
      new_hinge_infos.append(hinge_info)
  old_hinges = list(hinge_info.coordinate for hinge_info in new_hinge_infos)
  old_hinges_with_hash = crease.Creases.create_from_creases(creases=old_hinges)
  for hinge in hinges:
    if crease.CreaseWithExactMatch(crease=hinge) in old_hinges_with_hash:
      continue
    # A new hinge was added, so we need to add it to the hinge information.
    new_hinge_infos.append(
        packing_types.HingeInfo(
            coordinate=hinge,
            assigned=False,  # New hinges are never assigned.
            flap_names=_flap_names_from_hinge_and_rectangles(
                hinge, rectangles, grid_size
            ),
        )
    )
  return new_hinge_infos
