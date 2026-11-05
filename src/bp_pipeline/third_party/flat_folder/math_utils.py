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
#
# Ported from Flat-Folder (https://github.com/origamimagiro/flat-folder),
# Copyright (c) 2022 Jason S. Ku (origamimagiro), licensed under the MIT
# License; see LICENSE in this directory.
# ==============================================================================

"""Math utility functions for 2D geometry."""

from collections.abc import Sequence
import math
from typing import Optional, TypeVar

Point = tuple[float, float]
Line = tuple[Point, Point]
Edge = list[int]
Comparable = TypeVar("Comparable")
T = TypeVar("T")

FLOAT_EPSILON = 1e-16


def near_zero(value: float) -> bool:
  """Checks if a floating point value is close to zero.

  Args:
    value: The floating-point number to check.

  Returns:
    True if abs(value) is less than FLOAT_EPSILON, False otherwise.
  """
  return math.isclose(value, 0.0, abs_tol=FLOAT_EPSILON)


def list_to_tuple(items: list[T]) -> tuple[T, ...]:
  """Encodes a list as a tuple.

  If all items in list are hashable, the resulting tuple can be used as a
  dictionary key.

  Args:
    items: The list to convert.

  Returns:
    A tuple containing the elements of list.
  """
  return tuple(items)


def encode_order_pair(
    pair: Sequence[Comparable],
) -> tuple[Comparable, Comparable]:
  """Encodes a pair as a tuple with elements in a consistent order.

  Ensures that (a,b) and (b,a) produce the same output based on comparison.

  Args:
    pair: A sequence of two comparable elements.

  Returns:
    A tuple with elements sorted.
  """
  a, b = pair
  return (a, b) if a < b else (b, a)  # pyrefly: ignore[unsupported-operation]


def tuple_to_list(encoded_tuple: tuple[T, ...]) -> list[T]:
  """Decodes a tuple back into a list.

  Args:
    encoded_tuple: The tuple to convert.

  Returns:
    A list containing elements of tuple.
  """
  return list(encoded_tuple)


def expand(indices: Sequence[int], vertices: list[Point]) -> list[Point]:
  """Returns vertices corresponding to a list of indices.

  Args:
    indices: List of vertex indices.
    vertices: List of vertices.

  Returns:
    List of vertices corresponding to indices.
  """
  return [vertices[vi] for vi in indices]


def multiply(vector: Point, scalar: float) -> Point:
  """Multiplies a 2D vector by a scalar.

  Args:
    vector: A 2D vector [x, y].
    scalar: Scalar value to multiply with.

  Returns:
    The resulting vector [x*scalar, y*scalar].
  """
  x, y = vector
  return x * scalar, y * scalar


def divide(vector: Point, scalar: float) -> Point:
  """Divides a 2D vector by a scalar.

  Args:
    vector: A 2D vector [x, y].
    scalar: Scalar value to divide by.

  Returns:
    The resulting vector [x/scalar, y/scalar].
  """
  return multiply(vector, 1.0 / scalar)


def add(vector1: Point, vector2: Point) -> Point:
  """Adds two 2D vectors.

  Args:
    vector1: First vector [x1, y1].
    vector2: Second vector [x2, y2].

  Returns:
    The sum vector [x1+x2, y1+y2].
  """
  x1, y1 = vector1
  x2, y2 = vector2
  return x1 + x2, y1 + y2


def subtract(vector1: Point, vector2: Point) -> Point:
  """Subtracts the second 2D vector from the first.

  Args:
    vector1: First vector [x1, y1].
    vector2: Second vector [x2, y2].

  Returns:
    The difference vector [x1-x2, y1-y2].
  """
  x1, y1 = vector1
  x2, y2 = vector2
  return x1 - x2, y1 - y2


def dot_product(vector1: Point, vector2: Point) -> float:
  """Computes dot product of two 2D vectors.

  Args:
    vector1: First vector [x1, y1].
    vector2: Second vector [x2, y2].

  Returns:
    The dot product x1*x2 + y1*y2.
  """
  x1, y1 = vector1
  x2, y2 = vector2
  return x1 * x2 + y1 * y2


def magnitude_squared(vector: Point) -> float:
  """Computes squared magnitude of a 2D vector.

  Args:
    vector: A 2D vector [x, y].

  Returns:
    The squared magnitude x*x + y*y.
  """
  return dot_product(vector, vector)


def magnitude(vector: Point) -> float:
  """Computes magnitude of a 2D vector.

  Args:
    vector: A 2D vector [x, y].

  Returns:
    The magnitude sqrt(x*x + y*y).
  """
  return math.sqrt(magnitude_squared(vector))


def unit_vector(vector: Point) -> Point:
  """Computes unit vector in the same direction as input vector.

  Args:
    vector: A 2D vector [x, y].

  Returns:
    A unit vector [x', y'], or [0,0] if magnitude is 0.
  """
  mag = magnitude(vector)
  return multiply(vector, 1.0 / mag) if mag != 0 else (0.0, 0.0)


def perpendicular_vector(vector: Point) -> Point:
  """Computes perpendicular vector by rotating 90 degrees clockwise.

  For vector (x, y), returns (y, -x).

  Args:
    vector: A 2D vector [x, y].

  Returns:
    The perpendicular vector [y, -x].
  """
  x, y = vector
  return y, -x


def distance_squared(point1: Point, point2: Point) -> float:
  """Computes squared distance between two 2D points.

  Args:
    point1: First point [x1, y1].
    point2: Second point [x2, y2].

  Returns:
    Squared Euclidean distance between point1 and point2.
  """
  return magnitude_squared(subtract(point2, point1))


def distance(point1: Point, point2: Point) -> float:
  """Computes distance between two 2D points.

  Args:
    point1: First point [x1, y1].
    point2: Second point [x2, y2].

  Returns:
    Euclidean distance between point1 and point2.
  """
  return magnitude(subtract(point2, point1))


def are_close(point1: Point, point2: Point, epsilon: float) -> bool:
  """Checks if two 2D points are close to each other within epsilon.

  Args:
    point1: First point [x1, y1].
    point2: Second point [x2, y2].
    epsilon: Tolerance for comparison.

  Returns:
    True if distance in each coordinate is less than epsilon.
  """
  x1, y1 = point1
  x2, y2 = point2
  return abs(x1 - x2) < epsilon and abs(y1 - y2) < epsilon


def twice_signed_area(point1: Point, point2: Point, point3: Point) -> float:
  """Computes twice the signed area of the triangle (p1, p2, p3).

  Result is positive if points are counter-clockwise, negative if clockwise,
  and zero if collinear.

  Args:
    point1: First point [x1, y1].
    point2: Second point [x2, y2].
    point3: Third point [x3, y3].

  Returns:
    Twice the signed area.
  """
  x1, y1 = point1
  x2, y2 = point2
  x3, y3 = point3
  return (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)


def angle(vector: Point) -> float:
  """Computes angle of 2D vector in radians in range [0, 2*pi).

  Angle is measured counter-clockwise from the positive x-axis.

  Args:
    vector: A 2D vector [x, y].

  Returns:
    Angle in radians [0, 2*pi).
  """
  x, y = vector
  ang = math.atan2(y, x)
  return ang + (2 * math.pi if ang < 0 else 0)


def centroid(points: list[Point]) -> Point:
  """Computes centroid of a list of 2D points.

  Args:
    points: A list of points [[x1, y1], [x2, y2], ...].

  Returns:
    The centroid of the points [cx, cy].
  """
  n = len(points)
  if n == 0:
    return (0.0, 0.0)
  point_sum: Point = (0.0, 0.0)
  for i in range(n):
    point_sum = add(point_sum, points[i])
  return divide(point_sum, n)


def previous_in_list(list_: list[T], value: T) -> Optional[T]:
  """Finds previous element in list, with wrap around from start to end.

  Args:
    list_: The list to search in.
    value: The value whose predecessor is sought.

  Returns:
    The element before value in list_, or None if value not in list_.
  """
  for i, x in enumerate(list_):
    if x == value:
      return list_[len(list_) - 1] if i == 0 else list_[i - 1]
  return None


def min_line_length(lines: list[tuple[Point, Point]]) -> float:
  """Computes minimum line length from a list of lines.

  Each line tuple should contain at least two points as its first two
  elements, e.g., ([x1,y1], [x2,y2]) or ([x1,y1], [x2,y2], 'type').

  Args:
    lines: A list of line segments.

  Returns:
    The length of the shortest line segment.
  """
  min_lensq = float("inf")
  for line in lines:
    p, q = line[0], line[1]
    lensq = distance_squared(p, q)
    min_lensq = min(min_lensq, lensq)
  return min_lensq**0.5


def polygon_twice_signed_area(points: list[Point]) -> float:
  """Computes twice the signed area of a polygon using the shoelace formula.

  Args:
    points: List of polygon vertices in order [[x1, y1], [x2, y2], ...].

  Returns:
    Twice the signed area of the polygon.
  """
  if not points:
    return 0.0
  area = 0.0
  x1, y1 = points[-1]
  for p2 in points:
    x2, y2 = p2
    area += (x1 + x2) * (y2 - y1)
    x1, y1 = x2, y2
  return area


def sort_faces(
    face_vertex_indices: list[list[int]], vertices: list[Point]
) -> None:
  """Sorts faces in place by area, from largest to smallest.

  Args:
    face_vertex_indices: List of faces, where each face is a list of vertex
      indices.
    vertices: List of vertex coordinates.
  """
  face_vertex_indices.sort(
      key=lambda f: polygon_twice_signed_area(expand(f, vertices)),
      reverse=True,
  )


def bounding_box(
    points: list[Point],
) -> tuple[Point, Point]:
  """Computes bounding box of a list of 2D points.

  Args:
    points: A list of points [[x1, y1], [x2, y2], ...].

  Returns:
    A list containing min and max points: [[x_min, y_min], [x_max, y_max]].
  """
  x_min, x_max = float("inf"), float("-inf")
  y_min, y_max = float("inf"), float("-inf")
  for x, y in points:
    if x < x_min:
      x_min = x
    if x > x_max:
      x_max = x
    if y < y_min:
      y_min = y
    if y > y_max:
      y_max = y
  return ((x_min, y_min), (x_max, y_max))


def normalize_points(
    points: list[Point],
) -> list[Point]:
  """Normalizes points to fit in a 0.5 radius box centered at (0.5, 0.5).

  Scales points such that the largest dimension of their bounding box is 1.0,
  and centers them within the [0,1]x[0,1] square.

  Args:
    points: A list of points [[x1, y1], [x2, y2], ...].

  Returns:
    A list of normalized points.
  """
  if not points:
    return []
  p_min, p_max = bounding_box(points)
  x_diff, y_diff = subtract(p_max, p_min)
  is_tall = x_diff < y_diff
  diff = y_diff if is_tall else x_diff
  if diff == 0:
    return [tuple(p) for p in points]  # pyrefly: ignore[bad-return]
  offset = subtract((0.5, 0.5), divide((x_diff, y_diff), 2 * diff))
  return [add(divide(subtract(p, p_min), diff), offset) for p in points]


def interior_point(points: list[Point]) -> Point:
  """Computes a point in polygon interior using ear clipping.

  For simple polygons, this point is guaranteed to be in the interior.
  It finds the largest "ear" of the polygon and returns its centroid.
  An ear is a triangle formed by three consecutive vertices v1,v2,v3 such
  that no other vertices of the polygon lie inside it.
  If no ear is found (e.g. for degenerate polygons), it returns polygon
  centroid as fallback, which may be outside for concave polygons.

  Args:
    points: List of polygon vertices in order [[x1, y1], [x2, y2], ...].

  Returns:
    A point [x,y] that is inside the polygon. Note: in degenerate cases where
    no ear is found, polygon centroid is returned, which can be outside of
    concave polygons.
  """
  if len(points) < 3:
    if not points:
      raise ValueError("Input polygon must not be empty.")
    return centroid(points)

  points_copy = list(points)
  if polygon_twice_signed_area(points_copy) < 0:
    points_copy.reverse()
  n = len(points_copy)
  largest_ear: Optional[list[Sequence[float]]] = None
  max_area = float("-inf")
  p1, p2 = points_copy[n - 2], points_copy[n - 1]
  for p3 in points_copy:
    area = twice_signed_area(p1, p2, p3)
    if area <= 0:
      p1, p2 = p2, p3
      continue
    is_ear = True
    for p_test in points_copy:
      if (
          p_test != p1
          and p_test != p2
          and p_test != p3
          and (
              twice_signed_area(p1, p2, p_test) >= 0
              and twice_signed_area(p2, p3, p_test) >= 0
              and twice_signed_area(p3, p1, p_test) >= 0
          )
      ):
        is_ear = False
        break
    if is_ear:
      if max_area < area:
        max_area = area
        largest_ear = [p1, p2, p3]
    p1, p2 = p2, p3
  if largest_ear is None:
    return centroid(points)
  return centroid(largest_ear)  # pyrefly: ignore[bad-argument-type]
