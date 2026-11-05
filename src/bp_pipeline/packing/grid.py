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

"""Classes for working with a 2D grid."""

from collections.abc import Iterator
import dataclasses
import enum
import functools
import math
import types
import typing
from typing import Self


class Axis(enum.IntEnum):
  """Represents the two axes of a grid."""

  VERTICAL = 0
  HORIZONTAL = 1


@dataclasses.dataclass(frozen=True, eq=True, kw_only=True)
class Delta:
  """Represents a delta in a 2D grid."""

  di: int
  dj: int

  def __add__(self, other: object) -> Self | types.NotImplementedType:
    if not isinstance(other, Delta):
      return NotImplemented
    return Delta(di=self.di + other.di, dj=self.dj + other.dj)

  def __sub__(self, other: object) -> Self | types.NotImplementedType:
    if not isinstance(other, Delta):
      return NotImplemented
    return Delta(di=self.di - other.di, dj=self.dj - other.dj)

  def scale(self, factor: int) -> Self:
    """Returns a new delta with both components scaled by the given factor."""
    return Delta(di=self.di * factor, dj=self.dj * factor)  # pyrefly: ignore[bad-return]

  @property
  def l1_norm(self) -> int:
    return abs(self.di) + abs(self.dj)

  def is_subdelta_of(self, other: Self) -> bool:
    """Checks if this delta is a subdelta of another delta.

    A delta is a subdelta of another delta if they are collinear, point in the
    same direction, and the magnitude of the first delta is less than or equal
    to the magnitude of the second delta.

    Args:
      other: The other Delta.

    Returns:
      True if this delta is a subdelta of the other delta.
    """
    if self.di * other.dj != self.dj * other.di:
      return False

    return (
        self.di * other.di >= 0
        and self.dj * other.dj >= 0
        and abs(self.di) <= abs(other.di)
        and abs(self.dj) <= abs(other.dj)
    )

  @property
  def inverse(self) -> Self:
    """A new delta with both components inverted."""
    return Delta(di=-self.di, dj=-self.dj)  # pyrefly: ignore[bad-return]

  @property
  def direction(self) -> 'Direction':
    """The direction of the single-component delta."""
    match (self.di, self.dj):
      case (0, 0):
        raise ValueError('Delta must be non-zero.')
      case (0, dx):
        return Direction.EAST if dx > 0 else Direction.WEST
      case (dy, 0):
        return Direction.SOUTH if dy > 0 else Direction.NORTH
      case _:
        raise ValueError(f'Delta {self} is a diagonal.')


@functools.lru_cache(maxsize=4 * 64)  # Most grid sizes should be less than 64.
def all_subdeltas(delta: Delta) -> tuple[Delta, ...]:
  """Returns the set of all collinear, integer deltas less than or equal to the given delta."""
  if delta.di == 0 and delta.dj == 0:
    return (Delta(di=0, dj=0),)
  gcd = math.gcd(delta.di, delta.dj)
  min_step = Delta(di=delta.di // gcd, dj=delta.dj // gcd)
  subdelta = Delta(di=0, dj=0)
  subdeltas = []
  while subdelta != delta:
    subdeltas.append(subdelta)
    subdelta = subdelta + min_step
  subdeltas.append(delta)
  return tuple(subdeltas)


class Direction(enum.IntEnum):
  """Represents the four cardinal directions on a grid."""

  NORTH = 0
  EAST = 1
  SOUTH = 2
  WEST = 3

  def rotate_left(self) -> Self:
    return Direction((self.value - 1 + 4) % 4)  # pyrefly: ignore[bad-return]

  def flip(self) -> Self:
    return Direction((self.value + 2) % 4)  # pyrefly: ignore[bad-return]

  def rotate_right(self) -> Self:
    return Direction((self.value + 1) % 4)  # pyrefly: ignore[bad-return]

  @property
  def is_horizontal(self) -> bool:
    return self.axis == Axis.HORIZONTAL

  @property
  def is_vertical(self) -> bool:
    return self.axis == Axis.VERTICAL

  @property
  def axis(self) -> Axis:
    return Axis(self.value % 2)

  def __str__(self) -> str:
    return self.name

  @property
  def step_delta(self) -> Delta:
    """A delta that represents a single step in this direction."""
    match self:
      case Direction.NORTH:
        return Delta(di=-1, dj=0)
      case Direction.EAST:
        return Delta(di=0, dj=1)
      case Direction.SOUTH:
        return Delta(di=1, dj=0)
      case Direction.WEST:
        return Delta(di=0, dj=-1)
      case _:
        typing.assert_never(self)


@dataclasses.dataclass(frozen=True, eq=True, kw_only=True)
class Cell:
  """Represents a cell in a 2D grid."""

  i: int
  j: int

  def delta_to(self, other: Self) -> Delta:
    """Returns a Delta that shifts from this cell to the other."""
    return Delta(di=other.i - self.i, dj=other.j - self.j)

  def shift(self, delta: Delta) -> Self:
    """Returns a new cell shifted by the given delta."""
    return Cell(i=self.i + delta.di, j=self.j + delta.dj)  # pyrefly: ignore[bad-return]

  def axial_offset(self, axis: Axis) -> int:
    """Returns the offset of the cell along the given direction's axis."""
    match axis:
      case Axis.VERTICAL:
        return self.i
      case Axis.HORIZONTAL:
        return self.j
      case _:
        typing.assert_never(axis)

  def is_within_grid(self, grid_size: int, axis: Axis | None = None) -> bool:
    """Returns whether the cell is within the grid's borders.

    Args:
      grid_size: The size of the square grid.
      axis: If specified, only checks the borders along this axis.
    """
    is_within_vertical = 0 <= self.i < grid_size
    is_within_horizontal = 0 <= self.j < grid_size
    match axis:
      case None:
        return is_within_vertical and is_within_horizontal
      case Axis.VERTICAL:
        return is_within_vertical
      case Axis.HORIZONTAL:
        return is_within_horizontal
      case _:
        typing.assert_never(axis)

  def clamp(self, grid_size: int, axis: Axis | None = None) -> Self:
    """Returns a new cell clamped to the grid's borders.

    Args:
      grid_size: The size of the square grid.
      axis: If specified, clamping is only applied along this axis.
    """
    clamp_i = max(0, min(grid_size - 1, self.i))
    clamp_j = max(0, min(grid_size - 1, self.j))
    match axis:
      case None:
        return Cell(i=clamp_i, j=clamp_j)  # pyrefly: ignore[bad-return]
      case Axis.VERTICAL:
        return Cell(i=clamp_i, j=self.j)  # pyrefly: ignore[bad-return]
      case Axis.HORIZONTAL:
        return Cell(i=self.i, j=clamp_j)  # pyrefly: ignore[bad-return]
      case _:
        typing.assert_never(axis)

  def is_on_border(self, grid_size: int, direction: Direction) -> bool:
    """Returns whether the cell lies on the specified border."""
    match direction:
      case Direction.NORTH:
        return self.i == 0
      case Direction.EAST:
        return self.j == grid_size - 1
      case Direction.SOUTH:
        return self.i == grid_size - 1
      case Direction.WEST:
        return self.j == 0
      case _:
        typing.assert_never(direction)


@dataclasses.dataclass(frozen=True, eq=True)
class Walk:
  """Represents a walk on a 2D grid starting from a cell in a given direction.

  The walk continues until it encounters a boundary or the maximum number of
  steps is reached. At least one step is guaranteed to be on the grid.

  Attributes:
    start_cell: The cell where the walk begins.
    direction: The direction of the walk.
    grid_size: The size of the square grid.
    steps: The maximum distance to walk.

  Raises:
    ValueError: If grid_size is not positive.
    ValueError: If steps is not positive.
    ValueError: If no part of the walk is on the grid.
  """

  start_cell: Cell
  direction: Direction
  grid_size: int
  steps: int | None = None  # None means no limit

  def __post_init__(self):
    if self.grid_size <= 0:
      raise ValueError(f'grid_size must be positive: {self.grid_size=}')
    if self.steps is not None and self.steps <= 0:
      raise ValueError(f'steps must be positive: {self.steps=}')

    if not self.clamped_start.is_within_grid(self.grid_size):
      # The walk doesn't start on the grid
      # and is in the wrong direction to arrive on the grid.
      raise ValueError(
          f'Walk is in the wrong direction to arrive on the grid: {self}'
      )
    if self.steps is not None and self._outside_distance >= self.steps:
      raise ValueError(f'Walk is too short to arrive on the grid: {self}')

  @functools.cached_property
  def clamped_start(self) -> Cell:
    """self.start_cell clamped to the appropriate grid border."""
    match self.direction:
      case Direction.NORTH:
        return Cell(
            i=min(self.start_cell.i, self.grid_size - 1), j=self.start_cell.j
        )
      case Direction.EAST:
        return Cell(i=self.start_cell.i, j=max(0, self.start_cell.j))
      case Direction.SOUTH:
        return Cell(i=max(0, self.start_cell.i), j=self.start_cell.j)
      case Direction.WEST:
        return Cell(
            i=self.start_cell.i, j=min(self.start_cell.j, self.grid_size - 1)
        )
      case _:
        typing.assert_never(self.direction)

  @functools.cached_property
  def _outside_distance(self) -> int:
    # One axis of this delta is always 0, so the norm only represents one axis.
    return self.clamped_start.delta_to(self.start_cell).l1_norm

  @functools.cached_property
  def end_cell(self) -> Cell:
    """The cell that the walk will stop at."""
    if self.steps is not None:
      end_cell = self.start_cell.shift(
          self.direction.step_delta.scale(self.steps - 1)
      )
    else:  # Unlimited steps.
      # The walk should be at most grid_size from the clamped start.
      end_cell = self.clamped_start.shift(
          self.direction.step_delta.scale(self.grid_size)
      )
    return end_cell

  @functools.cached_property
  def clamped_end(self) -> Cell:
    """self.end_cell clamped to the appropriate grid border."""
    return self.end_cell.clamp(self.grid_size, axis=self.direction.axis)

  def __len__(self) -> int:
    """Returns the number of steps in the walk."""
    return self.clamped_start.delta_to(self.clamped_end).l1_norm + 1

  def __iter__(self) -> Iterator[Cell]:
    """Yields cells along the walk, skipping those that are outside the grid.

    The walk starts from the cell on the grid border closest to the start_cell
    (along the walk's axis) and continues in the given direction until
    either the maximum number of steps is reached or the other grid boundary
    is encountered. Always yields at least one cell.
    """
    for delta in all_subdeltas(self.clamped_start.delta_to(self.clamped_end)):
      yield self.clamped_start.shift(delta)
