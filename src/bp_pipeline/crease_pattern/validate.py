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

"""Validate crease patterns."""

import math

from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import crease_pattern


def valid_pattern(pattern: crease_pattern.CreasePattern) -> bool:
  """Returns true if the Crease Pattern is valid.

  Validates:
    - Must not contain any HINGE creases.
    - Borders must form a square.

  Args:
    pattern: The Crease Pattern to validate.

  Returns:
    True if the Crease Pattern is valid, False otherwise.
  """
  if any(c.fold == crease.Fold.HINGE for c in pattern.creases):
    return False

  try:
    validate_border_creases(pattern.creases)
  except ValueError:
    return False

  return True


def validate_border_creases(
    creases: list[crease.Crease],
) -> list[crease.Crease]:
  """Filters, merges, and validates border creases to ensure they form a square.

  Args:
    creases: A list of all creases in the pattern.

  Returns:
    A list containing the four validated, merged border creases.
  """
  border_segments = [c for c in creases if c.fold == crease.Fold.BORDER]
  merged_borders = crease.merge_creases(border_segments)

  # Should have exactly 4 sides.
  if len(merged_borders) != 4:
    raise ValueError(f'There are not 4 borders: {len(merged_borders)}')

  # All sides have the same length.
  first_length = merged_borders[0].length
  if not all(
      math.isclose(c.length, first_length, abs_tol=crease.DEFAULT_TOLERANCE)
      for c in merged_borders
  ):
    raise ValueError(f'The border lengths are not the same: {merged_borders}')

  # All sides are parallel or perpendicular to each other.
  parallel_pairs = 0
  perpendicular_pairs = 0
  for i, c1 in enumerate(merged_borders):
    for c2 in merged_borders[i + 1 :]:
      if c1.is_parallel(c2):
        parallel_pairs += 1
      elif c1.is_perpendicular(c2):
        perpendicular_pairs += 1
      else:
        raise ValueError(f'Borders do not form a square: {c1} and {c2}')

  if parallel_pairs != 2 or perpendicular_pairs != 4:
    raise ValueError(f'Borders do not form a square: {merged_borders}')

  return merged_borders
