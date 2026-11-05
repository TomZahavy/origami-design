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

"""Measure symmetry of a crease pattern under various transformations."""

from collections.abc import Sequence
import dataclasses
import enum
import math
from typing import TypeVar

from absl import logging
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import crease_pattern

TransformableItem = TypeVar(
    'TransformableItem', crease_pattern.CreasePattern, crease.Crease
)


@enum.unique
class Transform(enum.Enum):
  """Symmetry transforms."""

  IDENTITY = enum.auto()

  HORIZONTAL_FLIP = enum.auto()
  VERTICAL_FLIP = enum.auto()
  DIAGONAL_FLIP = enum.auto()
  ANTIDIAGONAL_FLIP = enum.auto()

  ROTATE_90 = enum.auto()
  ROTATE_180 = enum.auto()
  ROTATE_270 = enum.auto()

  def weight_and_bias(
      self,
  ) -> tuple[
      tuple[tuple[float, float], tuple[float, float]], tuple[float, float]
  ]:
    """Returns the 2x2 weight matrix and 2D bias vector for the transform."""
    match self:
      case Transform.IDENTITY:
        return ((1.0, 0.0), (0.0, 1.0)), (0.0, 0.0)
      case Transform.HORIZONTAL_FLIP:
        return ((1.0, 0.0), (0.0, -1.0)), (0.0, 1.0)
      case Transform.VERTICAL_FLIP:
        return ((-1.0, 0.0), (0.0, 1.0)), (1.0, 0.0)
      case Transform.DIAGONAL_FLIP:
        return ((0.0, 1.0), (1.0, 0.0)), (0.0, 0.0)
      case Transform.ANTIDIAGONAL_FLIP:
        return ((0.0, -1.0), (-1.0, 0.0)), (1.0, 1.0)
      case Transform.ROTATE_90:
        return ((0.0, -1.0), (1.0, 0.0)), (1.0, 0.0)
      case Transform.ROTATE_180:
        return ((-1.0, 0.0), (0.0, -1.0)), (1.0, 1.0)
      case Transform.ROTATE_270:
        return ((0.0, 1.0), (-1.0, 0.0)), (0.0, 1.0)
      case _:
        raise ValueError(f'Transform {self} is not in the allowed list.')

  def __call__(self, item: TransformableItem) -> TransformableItem:
    """Transforms a crease pattern or crease according to the specified transform."""
    if self is Transform.IDENTITY:
      return item
    weight, bias = self.weight_and_bias()
    return item.transform(weight, bias)


FLIPS = [
    Transform.HORIZONTAL_FLIP,
    Transform.VERTICAL_FLIP,
    Transform.DIAGONAL_FLIP,
    Transform.ANTIDIAGONAL_FLIP,
]

ROTATIONS = [
    Transform.ROTATE_90,
    Transform.ROTATE_180,
    Transform.ROTATE_270,
]


def creases_transform_symmetry(
    creases: Sequence[crease.Crease],
    transform: Transform,
    dedup_input: bool = True,
    tolerance: float = crease.DEFAULT_TOLERANCE,
) -> float:
  """Counts symmetric creases under transform without building Vertex objects."""
  if not creases:
    return 1.0
  if dedup_input:
    pattern_creases: list[crease.Crease] = []
    for c in creases:
      if not any(c.is_overlapping(k) for k in pattern_creases):
        pattern_creases.append(c)
  else:
    pattern_creases = list(creases)
  total = len(pattern_creases)
  if total == 0:
    return 1.0
  if transform is Transform.IDENTITY:
    return 1.0
  try:
    raw_transformed = [transform(c) for c in pattern_creases]
  except ValueError:
    return -1.0
  transformed_creases: list[crease.Crease] = []
  for c in raw_transformed:
    if not any(c.is_overlapping(k) for k in transformed_creases):
      transformed_creases.append(c)
  by_fold: dict[crease.Fold, list[crease.Crease]] = {}
  for c2 in transformed_creases:
    by_fold.setdefault(c2.fold, []).append(c2)
  symmetric = 0
  for c1 in pattern_creases:
    candidates = by_fold.get(c1.fold)
    if candidates and any(
        math.isclose(c1.fold_percent, c2.fold_percent, abs_tol=tolerance)
        and c1.isclose(c2, atol=tolerance)
        for c2 in candidates
    ):
      symmetric += 1
  return symmetric / total


def transform_symmetry(
    pattern: crease_pattern.CreasePattern, transform: Transform
) -> float:
  """Counts the number of creases that are symmetric after a given transformation."""
  total = len(pattern.creases)
  if total == 0:
    return 1.0
  symmetric = 0
  try:
    transformed = transform(pattern)
  except ValueError:
    logging.exception('Failed to transform crease pattern: %s', pattern)
    return -1.0

  for c1 in pattern.creases:
    if any(
        c1.fold == c2.fold
        and math.isclose(
            c1.fold_percent, c2.fold_percent, abs_tol=crease.DEFAULT_TOLERANCE
        )
        and c1.isclose(c2)
        for c2 in transformed.creases
    ):
      symmetric += 1
  return symmetric / total


def symmetry_score(pattern: crease_pattern.CreasePattern) -> float:
  """Returns the maximum symmetry score across all defined transformations."""
  return max(transform_symmetry(pattern, flip) for flip in FLIPS)


def symmetry_axis(pattern: crease_pattern.CreasePattern) -> Transform:
  """Returns the maximum symmetry score across all defined transformations.

  If there is a tie and vertical flip has the same score as the horizontal flip,
  the vertical flip is returned.

  Args:
    pattern: The crease pattern to compute the symmetry axis for.
  """
  scores = [transform_symmetry(pattern, flip) for flip in FLIPS]
  vertical_index = FLIPS.index(Transform.VERTICAL_FLIP)
  if scores[vertical_index] == max(scores):
    return Transform.VERTICAL_FLIP
  max_index = scores.index(max(scores))
  return FLIPS[max_index]


def invert_crease_folds(
    pattern: crease_pattern.CreasePattern,
) -> crease_pattern.CreasePattern:
  """Inverts the fold direction of a crease pattern's creases.

  Note: zebra creases are split into regular m/v creases after inversion. Call
  `merge_creases(merge_zebra=True)` to merge them back.

  Args:
    pattern: The crease pattern to invert.

  Returns:
    The inverted crease pattern.
  """

  def change_color(line: crease.Crease) -> crease.Crease:
    if line.fold == crease.Fold.MOUNTAIN:
      fold = crease.Fold.VALLEY
    elif line.fold == crease.Fold.VALLEY:
      fold = crease.Fold.MOUNTAIN
    elif line.fold == crease.Fold.MOUNTAIN_ZEBRA:
      fold = crease.Fold.VALLEY_ZEBRA
    elif line.fold == crease.Fold.VALLEY_ZEBRA:
      fold = crease.Fold.MOUNTAIN_ZEBRA
    else:
      fold = line.fold

    return dataclasses.replace(line, fold=fold)

  creases = [change_color(c) for c in pattern.creases]
  return crease_pattern.CreasePattern(creases, light_mode=True)


def get_all_symmetries(
    pattern: crease_pattern.CreasePattern,
) -> list[crease_pattern.CreasePattern]:
  """Returns a list of all symmetrically transformed copies of a crease pattern."""
  patterns = []
  for transform in Transform:
    transformed_pattern = transform(pattern)
    patterns.append(transformed_pattern)
    patterns.append(invert_crease_folds(transformed_pattern))
  return patterns
