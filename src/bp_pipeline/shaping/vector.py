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

"""A 2D vector class.

Unlike points, vectors are not restricted to the unit square [0, 1]^2.
"""

import dataclasses
import functools
import math
from typing import Union

from ..crease_pattern import point as point_utils

EPS = 1e-8  # threshold


@dataclasses.dataclass(kw_only=True)
class Vector:
  """A 2D vector.

  Attributes:
    x: The x-coordinate of the vector.
    y: The y-coordinate of the vector.
  """

  x: float
  y: float

  @classmethod
  def from_point(cls, p: point_utils.Point) -> 'Vector':
    """Converts a point to a vector."""
    return Vector(x=p.x, y=p.y)

  @classmethod
  def from_points(
      cls, start: point_utils.Point, end: point_utils.Point
  ) -> 'Vector':
    """Returns a vector from p1 to p2."""
    return Vector(x=end.x - start.x, y=end.y - start.y)

  def __add__(self, other: 'Vector') -> 'Vector':
    """Adds two vectors."""
    return Vector(x=self.x + other.x, y=self.y + other.y)

  def point_add(self, p: point_utils.Point) -> point_utils.Point:
    """Adds a vector to a point."""
    x, y = p.x + self.x, p.y + self.y
    return point_utils.Point(
        x=x,
        y=y,
        require_on_paper=p.require_on_paper,
    )

  def __sub__(self, other: 'Vector') -> 'Vector':
    """Subtracts two vectors."""
    return Vector(x=self.x - other.x, y=self.y - other.y)

  def dot(self, other: 'Vector') -> float:
    """Computes the dot product of two vectors."""
    return self.x * other.x + self.y * other.y

  def __mul__(self, s: Union[float, int]) -> 'Vector':
    """Multiplies a vector by a scalar."""
    return Vector(x=self.x * s, y=self.y * s)

  def __truediv__(self, s: Union[float, int]) -> 'Vector':
    """Divides a vector by a scalar."""
    if math.isclose(s, 0):
      raise ValueError('Cannot divide by zero!')
    return Vector(x=self.x / s, y=self.y / s)

  def __rmul__(self, s: Union[float, int]) -> 'Vector':
    """Multiplies a vector by a scalar."""
    return Vector(x=self.x * s, y=self.y * s)

  @functools.cached_property
  def norm(self) -> float:
    """Returns the norm of the vector."""
    return math.sqrt(self.x**2 + self.y**2)

  @functools.cached_property
  def inf_norm(self) -> float:
    """Returns the absolute value of the norm of the vector."""
    return max(abs(self.x), abs(self.y))

  @functools.cached_property
  def normalize(self) -> 'Vector':
    """Returns the normalized vector."""
    if self.norm > EPS:
      return Vector(x=self.x / self.norm, y=self.y / self.norm)
    else:
      return Vector(x=0, y=0)

  @functools.cached_property
  def inf_normalize(self) -> 'Vector':
    """Returns the inf normalized vector."""
    if self.inf_norm > EPS:
      return Vector(x=self.x / self.inf_norm, y=self.y / self.inf_norm)
    else:
      return Vector(x=0, y=0)

  @functools.cached_property
  def slope(self) -> float:
    """Returns the slope of the vector."""
    return self.y / self.x if abs(self.x) > EPS else float('inf')

  def to_tuple(self) -> tuple[float, float]:
    """Returns the vector as a tuple."""
    return (self.x, self.y)

  def __eq__(self, other: object) -> bool:
    """Checks if two vectors are equal."""
    if not isinstance(other, Vector):
      return False
    return (self - other).norm < EPS
