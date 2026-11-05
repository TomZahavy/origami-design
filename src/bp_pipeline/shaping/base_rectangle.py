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

"""Base rectangle class for box pleating.

In packing, Rectangle is inherited by `PackingFlap` to represent flaps during
the packing phase. In shaping, Rectangle is inherited by `ShapingFlap` to
represent flaps during the shaping phase.
"""

from collections.abc import Sequence
import dataclasses
import functools
import math
from typing import Generic, Optional, TypeVar

from ..crease_pattern import crease as crease_utils
from ..crease_pattern import point as point_utils
from . import vector

Numeric = TypeVar('Numeric', int, float)


EPS = crease_utils.DEFAULT_TOLERANCE


def compare_points(
    p1: point_utils.Point,
    p2: point_utils.Point,
) -> int:
  """Compares two points approximately lexicographically."""
  # First approximately compare y values.
  if crease_utils.strict_less(p1.y, p2.y):
    return -1
  elif crease_utils.strict_less(p2.y, p1.y):
    return 1

  # y-values are close. Approximately compare x values.
  if crease_utils.strict_less(p1.x, p2.x):
    return -1
  elif crease_utils.strict_less(p2.x, p1.x):
    return 1

  # Points are close. Return 0.
  return 0


@dataclasses.dataclass(kw_only=True, frozen=True)
class Rectangle(Generic[Numeric]):
  """A box-pleating rectangle.

  Attributes:
    name: the rectangle's name.
    x_start: The x-coordinate of the top-left corner.
    y_start: The y-coordinate of the top-left corner.
    x_len: The length of the rectangle in the x-direction.
    y_len: The length of the rectangle in the y-direction.
  """

  name: str
  x_start: Numeric
  y_start: Numeric
  x_len: Numeric
  y_len: Numeric

  def __post_init__(self):
    if not any([self.is_square, self.is_wide, self.is_tall]):
      raise ValueError(
          'Rectangle must be exactly one of square, wide, or tall.'
      )

  @functools.cached_property
  def is_square(self) -> bool:
    """Whether the rectangle is a square."""
    return math.isclose(
        self.x_len, self.y_len, abs_tol=point_utils.DEFAULT_TOLERANCE
    )

  @functools.cached_property
  def is_wide(self) -> bool:
    """Whether the rectangle is wider than it is tall."""
    return self.x_len > self.y_len and not self.is_square

  @functools.cached_property
  def is_tall(self) -> bool:
    """Whether the rectangle is taller than it is wide."""
    return self.y_len > self.x_len and not self.is_square

  @classmethod
  def from_corners(
      cls,
      corners: Sequence[point_utils.Point],
      name: str,
  ) -> 'Rectangle':
    """Create a rectangle from its corners."""
    if len(corners) != 4:
      raise ValueError(f'Corners {corners} does not have 4 corners.')
    sorted_corners = sorted(corners, key=functools.cmp_to_key(compare_points))
    rotated_corners = sorted_corners[:2] + sorted_corners[2:][::-1]
    if not (
        math.isclose(rotated_corners[0].y, rotated_corners[1].y, abs_tol=EPS)
        and math.isclose(
            rotated_corners[1].x, rotated_corners[2].x, abs_tol=EPS
        )
        and math.isclose(
            rotated_corners[2].y, rotated_corners[3].y, abs_tol=EPS
        )
        and math.isclose(
            rotated_corners[3].x, rotated_corners[0].x, abs_tol=EPS
        )
    ):
      raise ValueError(f'Corners {corners} do not form a rectangle.')
    return cls(
        name=name,
        x_start=rotated_corners[0].x,
        y_start=rotated_corners[0].y,
        x_len=rotated_corners[1].x - rotated_corners[0].x,
        y_len=rotated_corners[3].y - rotated_corners[0].y,
    )

  @functools.cached_property
  def corners(
      self,
  ) -> tuple[
      point_utils.Point, point_utils.Point, point_utils.Point, point_utils.Point
  ]:
    """Get the corners of the rectangle in clockwise order starting from top-left."""
    return (
        point_utils.Point(
            x=self.x_start,
            y=self.y_start,
            require_on_paper=False,
        ),
        point_utils.Point(
            x=self.x_start + self.x_len,
            y=self.y_start,
            require_on_paper=False,
        ),
        point_utils.Point(
            x=self.x_start + self.x_len,
            y=self.y_start + self.y_len,
            require_on_paper=False,
        ),
        point_utils.Point(
            x=self.x_start,
            y=self.y_start + self.y_len,
            require_on_paper=False,
        ),
    )

  @functools.cached_property
  def edges(self) -> tuple[
      crease_utils.Crease,
      crease_utils.Crease,
      crease_utils.Crease,
      crease_utils.Crease,
  ]:
    """Get the edges of the rectangle."""
    corners = self.corners
    return tuple(  # pyrefly: ignore[bad-return]
        crease_utils.Crease(
            corners[i],
            corners[(i + 1) % 4],
            fold=crease_utils.Fold.HINGE,
        )
        for i in range(4)
    )

  def clip(
      self,
      xmin: Numeric,
      ymin: Numeric,
      xmax: Numeric,
      ymax: Numeric,
  ) -> Optional['Rectangle']:
    """Returns a new rectangle clipped to the given bounding box."""
    overlap_x_start = max(xmin, self.x_start)
    overlap_y_start = max(ymin, self.y_start)
    overlap_x_end = min(xmax, self.x_start + self.x_len)
    overlap_y_end = min(ymax, self.y_start + self.y_len)
    if overlap_x_end > overlap_x_start and overlap_y_end > overlap_y_start:
      return Rectangle(
          name=self.name,
          x_start=overlap_x_start,
          y_start=overlap_y_start,
          x_len=overlap_x_end - overlap_x_start,
          y_len=overlap_y_end - overlap_y_start,
      )
    return None

  def is_corner_inside_or_on_border(
      self, width: Numeric, height: Numeric
  ) -> bool:
    """Checks if at least one corner is within or on the border of (0,0,width,height)."""
    x_plus_w = self.x_start + self.x_len
    y_plus_h = self.y_start + self.y_len
    return (0 <= self.x_start <= width or 0 <= x_plus_w <= width) and (
        0 <= self.y_start <= height or 0 <= y_plus_h <= height
    )

  def overlaps(self, other: 'Rectangle') -> bool:
    """Checks if this rectangle overlaps with another rectangle."""
    is_separate = (
        (self.x_start + self.x_len <= other.x_start)
        or (self.x_start >= other.x_start + other.x_len)
        or (self.y_start + self.y_len <= other.y_start)
        or (self.y_start >= other.y_start + other.y_len)
    )
    return not is_separate

  def intersection_area(
      self, xmin: Numeric, ymin: Numeric, xmax: Numeric, ymax: Numeric
  ) -> Numeric:
    """Calculates intersection area with a bounding box."""
    overlap_x_start = max(xmin, self.x_start)
    overlap_y_start = max(ymin, self.y_start)
    overlap_x_end = min(xmax, self.x_start + self.x_len)
    overlap_y_end = min(ymax, self.y_start + self.y_len)
    if overlap_x_end > overlap_x_start and overlap_y_end > overlap_y_start:
      return (overlap_x_end - overlap_x_start) * (
          overlap_y_end - overlap_y_start
      )
    return 0  # pyrefly: ignore[bad-return]

  def get_unit_edge_vectors(self, grid_size: int) -> Sequence[vector.Vector]:
    """Get vectors pointing clockwise along rectangle edges with grid unit length."""
    grid_delta = 1 / grid_size
    return [
        grid_delta
        * (
            vector.Vector.from_point(self.corners[(i + 1) % 4])
            - vector.Vector.from_point(self.corners[i])
        ).normalize
        for i in range(4)
    ]

  def get_unit_depth_vectors(self, grid_size: int) -> Sequence[vector.Vector]:
    """Get vectors pointing into rectangle (orthogonal to respective edges) with grid unit length."""
    edge_vectors = self.get_unit_edge_vectors(grid_size)
    return [edge_vectors[(i + 1) % 4] for i in range(4)]

  def is_internal_point(
      self, p: point_utils.Point, strict: bool = False
  ) -> bool:
    """Checks if a point is inside the rectangle."""
    return point_utils.in_range(
        p.x, self.x_start, self.x_start + self.x_len, strict
    ) and point_utils.in_range(
        p.y, self.y_start, self.y_start + self.y_len, strict
    )

  def crease_is_within(
      self, crease: crease_utils.Crease, strict: bool = False
  ) -> bool:
    """Checks if a crease is within the rectangle."""
    return self.is_internal_point(crease.p1, strict) and self.is_internal_point(
        crease.p2, strict
    )

  def intersects_crease(self, crease: crease_utils.Crease) -> bool:
    """Checks if a crease intersects the rectangle."""
    contains_crease = self.is_internal_point(
        crease.p1
    ) and self.is_internal_point(crease.p2)
    intersects_border = any(
        crease.vertex_with_crease(edge) is not None for edge in self.edges
    )
    return contains_crease or intersects_border

  def is_edge_point(
      self, p: point_utils.Point, extend_edges: bool = False
  ) -> bool:
    """Checks if a point is on an edge of the rectangle."""
    if extend_edges:
      x_end = self.x_start + self.x_len
      y_end = self.y_start + self.y_len
      return (
          math.isclose(p.x, self.x_start, abs_tol=EPS)
          or math.isclose(p.x, x_end, abs_tol=EPS)
          or math.isclose(p.y, self.y_start, abs_tol=EPS)
          or math.isclose(p.y, y_end, abs_tol=EPS)
      )

    return any(
        edge.point_status(p)
        in (crease_utils.PointStatus.TIP, crease_utils.PointStatus.INTERNAL)
        for edge in self.edges
    )

  def overlaps_border(self, crease: crease_utils.Crease) -> bool:
    """Checks if a crease overlaps the rectangle's border."""
    return any(crease.is_overlapping(edge) for edge in self.edges)
