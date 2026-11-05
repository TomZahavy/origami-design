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

"""Common functions for crease pattern parsing."""

import math

_TOLERANCE = 1e-3


def clip(value: float) -> float:
  """Clips a value to the range [0, 1]."""
  return max(0, min(value, 1))


def point_format(
    value: float, scale: float = 1000, ndigits: int = 3, grid: int = -1
) -> str:
  """Formats a point to a scale with `ndigits` significant digits.

  Args:
    value: The number to format, in the range [0, 1].
    scale: The scale factor to apply to the point.
    ndigits: The number of digits after the decimal point to keep.
    grid: The grid size to use for the point. If -1, no grid is used. If > 0,
      the value is multiplied by the grid size and rounded to the nearest
      integer.

  Returns:
    The formatted point string.
  """
  if ndigits < 1:
    raise ValueError('ndigits should be at least 1.')

  if not 0 <= value <= 1 and not (
      math.isclose(value, 0, abs_tol=_TOLERANCE)
      or math.isclose(value, 1, abs_tol=_TOLERANCE)
  ):
    raise ValueError(f'Value {value} is not in the range [0, 1].')
  if grid > 0:
    value *= grid
  else:
    value = clip(value)
  scaled_value = round(value, ndigits) * scale
  return f'{scaled_value:.{max(0, ndigits)}f}'.rstrip('0').rstrip('.')
