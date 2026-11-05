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

"""An object for a Point in an Origami Crease Pattern."""

from collections.abc import Iterable
import dataclasses
import functools
import math
from typing import Any

from bp_pipeline.crease_pattern import types

DEFAULT_TOLERANCE = 1e-3


def in_range(
    x: float, min_val: float, max_val: float, strict: bool = False
) -> bool:
  """Checks if a number is in the range (min_val, max_val) or [min_val, max_val]."""
  if strict:
    return min_val + DEFAULT_TOLERANCE < x < max_val - DEFAULT_TOLERANCE
  return min_val - DEFAULT_TOLERANCE <= x <= max_val + DEFAULT_TOLERANCE


def in_zero_one_range(x: float, strict: bool = False) -> bool:
  """Checks if a number is (optionally strictly) in the range [0, 1]."""
  return in_range(x, 0, 1, strict=strict)


def tuple_on_paper(x: float, y: float) -> bool:
  """Checks if a point is on the paper."""
  return in_zero_one_range(x) and in_zero_one_range(y)


def sort_by_norm(p1: 'Point', p2: 'Point') -> tuple['Point', 'Point']:
  """Returns the first point between two points.

  Points with smaller norm are considered first, and points with equal norm are
  decided by their x coordinate.

  Args:
    p1: One point.
    p2: A second point.

  Returns:
    The two points sorted by norm and x coordinate.
  """
  if p1.norm == p2.norm:
    return sort_by_x(p1, p2)
  elif p1.norm < p2.norm:
    return p1, p2
  else:
    return p2, p1


def sort_by_x(p1: 'Point', p2: 'Point') -> tuple['Point', 'Point']:
  """Returns the points sorted by ascending x coordinate.

  Args:
    p1: One point.
    p2: A second point.

  Returns:
    The two points sorted by ascending x coordinate.
  """
  if p1.x < p2.x:
    return p1, p2
  else:
    return p2, p1


def sort_by_y(p1: 'Point', p2: 'Point') -> tuple['Point', 'Point']:
  """Returns the points sorted by ascending y coordinate.

  Args:
    p1: One point.
    p2: A second point.

  Returns:
    The two points sorted by ascending y coordinate.
  """
  if p1.y < p2.y:
    return p1, p2
  else:
    return p2, p1


def is_collinear(
    p1: 'Point', p2: 'Point', p3: 'Point', atol: float = DEFAULT_TOLERANCE
) -> bool:
  """Checks if three distinct points are collinear.

  Args:
    p1: The first point.
    p2: The second point.
    p3: The third point.
    atol: The tolerance for the cross product.

  Returns:
    True if the three points are collinear, False otherwise.

  Checks if the cross product is 0.
  """
  p12_x = p2.x - p1.x
  p12_y = p2.y - p1.y
  p12_norm = math.sqrt(p12_x**2 + p12_y**2)
  p13_x = p3.x - p1.x
  p13_y = p3.y - p1.y
  p13_norm = math.sqrt(p13_x**2 + p13_y**2)
  p23_x = p3.x - p2.x
  p23_y = p3.y - p2.y
  p23_norm = math.sqrt(p23_x**2 + p23_y**2)
  return (
      math.isclose(
          p12_x * p13_y, p12_y * p13_x, abs_tol=atol * p12_norm * p13_norm
      )
      and math.isclose(
          p12_x * p23_y, p12_y * p23_x, abs_tol=atol * p12_norm * p23_norm
      )
      and math.isclose(
          p13_x * p23_y, p13_y * p23_x, abs_tol=atol * p13_norm * p23_norm
      )
  )


def midpoint(point1: 'Point', point2: 'Point') -> 'Point':
  """A method that finds the midpoint of 2 points."""
  return Point(
      x=(point1.x + point2.x) / 2.0,
      y=(point1.y + point2.y) / 2.0,
      require_on_paper=point1.require_on_paper and point2.require_on_paper,
  )


def distance(point1: 'Point', point2: 'Point') -> float:
  """A method that finds the distance between 2 points."""
  return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)


def distance_with_tuple(point1: 'Point', point2: tuple[float, float]) -> float:
  """A method that finds the distance an internal and an external point.

  Args:
    point1: The first point.
    point2: The second point as a tuple (x, y).

  Returns:
    The Euclidean distance between point1 and point2.
  """
  return math.sqrt((point1.x - point2[0]) ** 2 + (point1.y - point2[1]) ** 2)


def find_x_on_line(y: float, p1: 'Point', p2: 'Point') -> float:
  """Given an input y-coordinate, returns the x-coordinate that lies on the line formed by p1 and p2."""
  if math.isclose(p2.y, p1.y):
    raise ValueError(
        f'Cannot find x on line {p1} to {p2} for y={y} because the line is'
        ' horizontal!'
    )
  return (p2.x - p1.x) / (p2.y - p1.y) * (y - p1.y) + p1.x


def find_y_on_line(x: float, p1: 'Point', p2: 'Point') -> float:
  """Given an input x-coordinate, returns the y-coordinate that lies on the line formed by p1 and p2."""
  if math.isclose(p2.x, p1.x):
    raise ValueError(
        f'Cannot find y on line {p1} to {p2} for x={x} because the line is'
        ' vertical!'
    )
  return (p2.y - p1.y) / (p2.x - p1.x) * (x - p1.x) + p1.y


def cross_product_2d(
    o: 'Point',
    a: 'Point',
    b: 'Point',
) -> float:
  """Returns the z-component of the cross product of vectors (a-o) and (b-o).

  Args:
      o: The origin point.
      a: The first point.
      b: The second point.

  Returns:
      The z-component of the cross product of vectors (a-o) and (b-o).
  """
  return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x)


@dataclasses.dataclass(kw_only=True, frozen=True)
class Point:
  """Represents a point in an Origami Crease Pattern in the range [0, 1]."""

  x: float
  y: float
  require_on_paper: bool = True

  def __post_init__(self):
    if self.require_on_paper and not (
        -DEFAULT_TOLERANCE <= self.x <= 1.0 + DEFAULT_TOLERANCE
        and -DEFAULT_TOLERANCE <= self.y <= 1.0 + DEFAULT_TOLERANCE
    ):
      raise ValueError(
          f'Coordinates {self.x}, {self.y} are not in the range [0, 1].'
      )

  @classmethod
  def from_viewbox(cls, x: float, y: float, viewbox: types.ViewBox) -> 'Point':
    """Creates a Point object from a dictionary."""
    x_min, y_min, width, height = viewbox
    max_size = max(width, height)
    return cls(
        x=(x - x_min) / max_size,
        y=(y - y_min) / max_size,
    )

  @classmethod
  def from_dict(cls, point_dict: dict[str, Any]) -> 'Point':
    """Creates a Point object from a dictionary."""
    return cls(
        x=point_dict['x'],
        y=point_dict['y'],
        require_on_paper=point_dict.get('require_on_paper', True),
    )

  def as_dict(self) -> dict[str, Any]:
    """Returns a dictionary representation of the Point."""
    return {
        'x': float(self.x),
        'y': float(self.y),
        'require_on_paper': self.require_on_paper,
    }

  @classmethod
  def from_list(cls, p_list: list[float]) -> 'Point':
    """Converts a list [x, y] to a Point object."""
    return cls(x=p_list[0], y=p_list[1], require_on_paper=False)

  def relax_paper_requirement(self) -> 'Point':
    return Point(x=self.x, y=self.y, require_on_paper=False)

  def isclose(self, other: 'Point', atol: float = DEFAULT_TOLERANCE) -> bool:
    """Checks if two points are equal."""
    return math.isclose(self.x, other.x, abs_tol=atol) and math.isclose(
        self.y, other.y, abs_tol=atol
    )

  def closest_point(self, points: Iterable['Point']) -> 'Point':
    """Returns the closest point to this point from a list of reference points.

    Raises a ValueError if `points` is empty.

    Args:
      points: A list of reference points.

    Returns:
      The closest point to this point from the list of reference points.
    """
    return min(points, key=lambda p: distance(p, self))

  @functools.cached_property
  def is_internal(self) -> bool:
    """Checks if a point is (strictly) internal to the paper."""
    return in_zero_one_range(self.x, strict=True) and in_zero_one_range(
        self.y, strict=True
    )

  @functools.cached_property
  def on_paper(self) -> bool:
    """Checks if a point is on the paper."""
    return in_zero_one_range(self.x) and in_zero_one_range(self.y)

  @property
  def is_external(self) -> bool:
    """Checks if a point is on the border or a paper corner."""
    return not self.on_paper

  @functools.cached_property
  def is_border(self) -> bool:
    """Checks if a point is on the border."""
    return self.on_paper and not self.is_internal

  @functools.cached_property
  def is_paper_corner(self) -> bool:
    """Checks if a point is on a paper corner."""
    return (
        math.isclose(self.x, 0, abs_tol=DEFAULT_TOLERANCE)
        or math.isclose(self.x, 1, abs_tol=DEFAULT_TOLERANCE)
    ) and (
        math.isclose(self.y, 0, abs_tol=DEFAULT_TOLERANCE)
        or math.isclose(self.y, 1, abs_tol=DEFAULT_TOLERANCE)
    )

  @functools.cached_property
  def close_to_left_border(self) -> bool:
    return math.isclose(self.x, 0, abs_tol=DEFAULT_TOLERANCE)

  @functools.cached_property
  def close_to_right_border(self) -> bool:
    return math.isclose(self.x, 1, abs_tol=DEFAULT_TOLERANCE)

  @functools.cached_property
  def close_to_top_border(self) -> bool:
    return math.isclose(self.y, 0, abs_tol=DEFAULT_TOLERANCE)

  @functools.cached_property
  def close_to_bottom_border(self) -> bool:
    return math.isclose(self.y, 1, abs_tol=DEFAULT_TOLERANCE)

  def __sub__(self, other):
    """Subtracts two points."""
    return Point(
        x=self.x - other.x,
        y=self.y - other.y,
        require_on_paper=self.require_on_paper or other.require_on_paper,
    )

  def __add__(self, other):
    """Adds a vector to this point."""
    return Point(
        x=self.x + other.x,
        y=self.y + other.y,
        require_on_paper=self.require_on_paper,
    )

  @functools.cached_property
  def norm(self) -> float:
    """Returns the norm of the point."""
    return math.sqrt(self.x**2 + self.y**2)

  def transform(
      self,
      weight: types.Matrix2x2,
      bias: types.Vector2D,
      require_on_paper: bool = True,
  ) -> 'Point':
    """Applies a linear transformation (weight * self + bias).

    Args:
      weight: A 2x2 matrix for scaling and rotation.
      bias: A 2D offset vector (b1, b2).
      require_on_paper: Whether the transformed point must be on the paper.

    Returns:
      A new Point object with the transformed coordinates.

    Raises:
      ValueError: If the transformed coordinates are not in the range [0, 1].
    """
    new_x = weight[0][0] * self.x + weight[0][1] * self.y + bias[0]
    new_y = weight[1][0] * self.x + weight[1][1] * self.y + bias[1]
    return Point(x=new_x, y=new_y, require_on_paper=require_on_paper)
