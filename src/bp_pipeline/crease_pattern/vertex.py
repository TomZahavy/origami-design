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

"""Utilities for Crease Patterns."""

import bisect
from collections.abc import Sequence
import copy
import functools
import math
from typing import NewType, cast

from bp_pipeline.crease_pattern import angle_utils as utils
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import point
import numpy as np

Radians = NewType('Radians', float)


def rotation_matrix(angle: Radians, axis: str) -> np.ndarray:
  """Returns the rotation matrix for the angle across the given axis."""
  match axis:
    case 'z':  # sector angle
      return np.array(
          [
              [math.cos(angle), -math.sin(angle), 0.0],
              [math.sin(angle), math.cos(angle), 0.0],
              [0.0, 0.0, 1.0],
          ],
          dtype=float,
      )
    case 'x':  # fold angle
      return np.array(
          [
              [1.0, 0.0, 0.0],
              [0.0, math.cos(angle), -math.sin(angle)],
              [0.0, math.sin(angle), math.cos(angle)],
          ],
          dtype=float,
      )
    case _:
      raise ValueError(f'Unsupported axis: {axis}')


def crease_rotation_matrix(
    *, fold_angle: Radians, angle: Radians
) -> np.ndarray:
  """Returns the rotation matrix for the crease."""
  a = rotation_matrix(angle, 'z')
  b = rotation_matrix(fold_angle, 'x')
  return (a @ b) @ np.transpose(a)


class Vertex:
  """Represents a Vertex in Origami."""

  tolerance: float = 3  # A tolerance parameter in degrees between angles.

  def __init__(
      self,
      creases: Sequence[crease.Crease],
      vertex_point: point.Point | None = None,
  ):
    if len(creases) < 1:
      raise ValueError('At least one crease is required to create a vertex.')
    elif len(creases) == 1:
      if vertex_point is None:
        raise ValueError('Single vertex crease with non-existent point.')
    else:
      vertex_point = creases[0].vertex_with_crease(creases[1])
      if vertex_point is None:
        raise ValueError(f'{creases} does not intersect.')
      vertex_point = cast(point.Point, vertex_point)

    self.point = vertex_point
    self.creases: list[crease.Crease] = []
    self.angles: list[float] = []

    for c in creases:
      self.add_crease(c)

  def add_crease(self, c: crease.Crease):
    """Adds a crease to the list of creases at the vertex."""
    if c.p1.isclose(self.point):
      other_p = c.p2
    elif c.p2.isclose(self.point):
      other_p = c.p1
    else:
      if c.point_status(self.point) == crease.PointStatus.EXTERNAL:
        raise ValueError(
            f'Crease {c} does not intersect with Vertex {self.point}'
        )
      raise ValueError(
          f'Crease {c} intersects Vertex {self.point} internally, not at tip'
      )

    if not any(c.isclose(c2) for c2 in self.creases):
      cx = other_p.x - self.point.x
      cy = other_p.y - self.point.y
      crease_angle = utils.angle_from_vector_in_degrees(cx, cy)

      # Creases are sorted counter-clockwise around the vertex.
      idx = bisect.bisect_left(self.angles, crease_angle)
      self.angles.insert(idx, crease_angle)
      self.creases.insert(idx, c)
      self.clear_cached_properties()

  def remove_crease(self, c: crease.Crease):
    """Removes a crease from the list of creases at the vertex."""
    if not any(
        c.isclose(c2) and crease.equal_fold_and_fold_percent(c, c2)
        for c2 in self.creases
    ):
      raise ValueError(f'Crease {c} is not in Vertex {self.point}')

    cx, cy = self._crease_vector(c)
    if cx is None or cy is None:
      raise ValueError(
          f'Could not compute crease vector for {c} at {self.point}'
      )
    crease_angle = utils.angle_from_vector_in_degrees(cx, cy)
    # Creases are sorted counter-clockwise around the vertex.
    self.angles.remove(crease_angle)
    idx = self.creases.index(c)
    self.creases.pop(idx)
    self.clear_cached_properties()

  _CACHED_PROPERTIES = (
      'internal',
      'is_valid',
      'check_maekawa',
      'check_blb',
      'check_crimp_angles',
      'check_kawasaki',
      '_sector_angles',
      '_flat_foldability',
      '_flat_foldability_maekawa',
  )

  def clear_cached_properties(self):
    """Clears the cached properties of the vertex."""
    d = self.__dict__
    for attrname in self._CACHED_PROPERTIES:
      d.pop(attrname, None)

  @functools.cached_property
  def internal(self) -> bool:
    """Checks if the vertex is internal."""
    return all(c.internal for c in self.creases)

  @functools.cached_property
  def is_valid(self) -> bool:
    """Checks if the vertex is valid.

    - Checks if the vertex has only 2 internal creases, they shouldn't be
    collinear.
    - Checks if the vertex has exactly 0 or 2 border creases.

    Returns:
      True if the vertex is valid, False otherwise.
    """
    if self.internal and len(self.creases) == 2:
      c0 = self.creases[0]
      c1 = self.creases[1]
      if (
          c0.fold == c1.fold
          and c0.fold_percent == c1.fold_percent
          and point.is_collinear(c0.p1, c0.p2, c1.p1)
          and point.is_collinear(c0.p1, c0.p2, c1.p2)
      ):
        return False

    total_borders = sum((c.fold == crease.Fold.BORDER) for c in self.creases)
    if total_borders not in (0, 2):
      return False

    return True

  @functools.cached_property
  def check_maekawa(self) -> bool:
    """Check if the Vertex satisfies Maekawa's theorem.

    True if the |#Mountains-#Valleys| = 2.

    See: https://en.wikipedia.org/wiki/Maekawa%27s_theorem

    Returns:
        True if the vertex satisfies Maekawa's theorem, False otherwise.
    """
    diff = 0
    for c in self.creases:
      if c.fold == crease.Fold.MOUNTAIN:
        diff += 1
      elif c.fold == crease.Fold.VALLEY:
        diff -= 1
    return abs(diff) == 2

  @functools.cached_property
  def check_blb(self) -> bool:
    """Check if the Vertex satisfies Big-Little-Big (BLB) Lemma.

    For every 3 consecutive angles between creases, the smallest angle must have
    one mountain and one valley crease.

    See: https://en.wikipedia.org/wiki/Big-little-big_lemma

    Returns:
        True if the vertex satisfies Big little big lemma, False otherwise.
    """
    if len(self.creases) < 3:
      return True

    sector_angles = self.sector_angles()
    n = len(sector_angles)
    for i, (theta, fold1, fold2) in enumerate(sector_angles):
      prev_theta = sector_angles[(i - 1) % n][0]
      next_theta = sector_angles[(i + 1) % n][0]
      if (
          abs(theta) < abs(prev_theta) - self.tolerance
          and abs(theta) < abs(next_theta) - self.tolerance
      ):
        if fold1 == fold2:
          return False
    return True

  @functools.cached_property
  def check_crimp_angles(self) -> bool:
    """Check if the Vertex is flat foldable, using crimping.

    For every 3 consecutive angles between creases, the smallest angle must have
    one mountain and one valley crease. We iteratively crimp each such angle,
    until we have only two angles left which must have the same assignment.
    This method handles the case when consecutive sector angles are equal.
    It is sufficient to check if an internal vertex is flat foldable together
    with the Kawasaki theorem.

    See: https://doc.lagout.org/science/0_Computer%20Science/2_Algorithms/
    Geometric%20Folding%20Algorithms_%20Linkages%2C%20Origami%2C%20
    Polyhedra%20%5BDemaine%20%26%20O%27Rourke%202007-07-16%5D.pdf

    Returns:
        True if the vertex satisfies Big little big lemma, False otherwise.
    """
    if len(self.creases) < 2:
      return False

    sector_angles = self.sector_angles()
    n = len(sector_angles)
    if n < 2:
      return False

    next_angle = [(i + 1) % n for i in range(n)]
    prev_angle = [(i - 1 + n) % n for i in range(n)]
    tol = self.tolerance

    def _abs_less_equal_with_tolerance(a: float, b: float) -> bool:
      return abs(a) <= abs(b) + tol

    def _all_same_folds(indices: Sequence[int]) -> bool:
      folds = set()
      for idx in indices:
        _, left_fold, right_fold = sector_angles[idx]
        folds.add(left_fold)
        folds.add(right_fold)
      return len(folds) == 1

    def _check_angle_minima(idx: int) -> bool:
      theta, left_fold, right_fold = sector_angles[idx]
      if left_fold.value not in (1, 2) or right_fold.value not in (1, 2):
        return False
      if left_fold == right_fold:
        return False
      return _abs_less_equal_with_tolerance(
          theta, sector_angles[prev_angle[idx]][0]
      ) and _abs_less_equal_with_tolerance(
          theta, sector_angles[next_angle[idx]][0]
      )

    active_status = [True] * n
    n_active = n
    to_crimp = {i for i in range(n) if _check_angle_minima(i)}

    while to_crimp and n_active > 2:
      current_idx = to_crimp.pop()
      if not active_status[current_idx]:
        continue

      left_idx = prev_angle[current_idx]
      right_idx = next_angle[current_idx]
      if not active_status[left_idx] or not active_status[right_idx]:
        continue
      if not _check_angle_minima(current_idx):
        continue

      new_angle = (
          sector_angles[left_idx][0]
          - sector_angles[current_idx][0]
          + sector_angles[right_idx][0]
      )
      new_right_crease = sector_angles[right_idx][2]
      sector_angles[left_idx] = (
          new_angle,
          sector_angles[left_idx][1],
          new_right_crease,
      )

      active_status[current_idx] = False
      active_status[right_idx] = False
      n_active -= 2

      new_left = prev_angle[left_idx]
      new_right = next_angle[right_idx]
      next_angle[left_idx] = new_right
      prev_angle[new_right] = left_idx

      for idx in (new_left, left_idx, new_right):
        if _check_angle_minima(idx):
          to_crimp.add(idx)

    if n_active == 2:
      active_indices = [i for i, active in enumerate(active_status) if active]
      if _all_same_folds(active_indices):
        return True
    return False

  @functools.cached_property
  def check_kawasaki(self) -> bool:
    """Checks if the alternate sum of odd and even angles at the vertex is 180 degrees.

    See: https://en.wikipedia.org/wiki/Kawasaki%27s_theorem

    Returns:
        True if the condition is met, False otherwise.
    """
    if not self.internal:
      return False

    sectors = self._sector_angles
    if len(sectors) % 2 == 1:
      return False

    odd_sum = sum(angle for angle, _, _ in sectors[::2])
    even_sum = sum(angle for angle, _, _ in sectors[1::2])
    return math.isclose(
        odd_sum, 180.0, abs_tol=self.tolerance
    ) and math.isclose(even_sum, 180.0, abs_tol=self.tolerance)

  def _crease_vector(
      self, c: crease.Crease
  ) -> tuple[float | None, float | None]:
    """Given a crease, returns the vector pointing out of the vertex.

    Unlike a point which is constrained to be in [0, 1] the vector can be
    arbitrary, which gives us more flexibility in the angle computation.

    Args:
      c: The crease to compute the vector for.

    Returns:
      A tuple of (x, y) vector components.
    """
    if c.p1.isclose(self.point):
      other_p = c.p2
    elif c.p2.isclose(self.point):
      other_p = c.p1
    else:
      return None, None
    return other_p.x - self.point.x, other_p.y - self.point.y

  @functools.cached_property
  def _sector_angles(
      self,
  ) -> tuple[tuple[float, crease.Fold, crease.Fold], ...]:
    """Cached tuple of sector angles between mountain and valley creases."""
    angles_and_folds = [
        (a, c.fold)
        for a, c in zip(self.angles, self.creases)
        if c.mountain_or_valley()
    ]
    n = len(angles_and_folds)
    if n == 0:
      return ()
    return tuple(
        (
            (angles_and_folds[(i + 1) % n][0] - angle_1) % 360,
            fold_1,
            angles_and_folds[(i + 1) % n][1],
        )
        for i, (angle_1, fold_1) in enumerate(angles_and_folds)
    )

  def sector_angles(self) -> list[tuple[float, crease.Fold, crease.Fold]]:
    """Returns the sector angles between mountain and valley creases."""
    return list(self._sector_angles)

  def flat_foldability(self, *, check_maekawa: bool = False) -> bool:
    """Checks if the Vertex satisfies the flat foldability condition."""
    return self.check_foldability_constraints(check_maekawa=check_maekawa)

  def check_foldability_constraints(
      self,
      *,
      check_maekawa: bool = False,
      check_blb: bool = False,
      check_kawasaki: bool = True,
      check_crimp: bool = True,
  ) -> bool:
    """Checks if the Vertex satisfies optional flat foldability constraints."""
    if not self.internal:
      return True
    if check_maekawa and not self.check_maekawa:
      return False
    if check_kawasaki and not self.check_kawasaki:
      return False
    if check_crimp and not self.check_crimp_angles:
      return False
    if check_blb and not self.check_blb:
      return False
    return True

  @property
  def rotation_matrix(self) -> np.ndarray:
    """Returns the rotation matrix for the Vertex."""
    matrix = np.eye(3)
    for c, angle in zip(self.creases, self.angles, strict=True):
      matrix @= crease_rotation_matrix(
          fold_angle=Radians(c.fold_angle), angle=Radians(math.radians(angle))
      )
    return matrix

  @property
  def is_foldable(self) -> bool:
    """Whether the Vertex is foldable.

    Checks if the multiplication of crease rotation matrices is close to
    identity.

    See: https://www.sciencedirect.com/science/article/pii/S0024379501006085
    """
    # Only applies to internal vertices
    if not self.internal:
      return False
    return np.allclose(np.eye(3), self.rotation_matrix, atol=1e-1)

  def clone(self) -> 'Vertex':
    """Returns a copy of the Vertex but using the same creases and point."""
    new_vertex = copy.copy(self)
    # Shallow copy uses the same references for list attributes.
    # We need to copy these into new lists to avoid modifying the original.
    new_vertex.creases = copy.copy(self.creases)
    new_vertex.angles = copy.copy(self.angles)

    return new_vertex

  def __repr__(self) -> str:
    """Returns a string representation of the vertex."""
    xy = f'({self.point.x:.3f}, {self.point.y:.3f})'
    return f'Vertex(p={xy}, n_creases={len(self.creases)})'
