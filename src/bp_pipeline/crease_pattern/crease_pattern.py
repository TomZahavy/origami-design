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

import collections
from collections.abc import Collection, Sequence
import functools
import math
from typing import Any, Optional

from bp_pipeline import timeout as timeout_lib
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import point as point_utils
from bp_pipeline.crease_pattern import types
from bp_pipeline.crease_pattern import vertex


@functools.lru_cache(maxsize=100)
def create_grid_points(grid_size: int) -> tuple[point_utils.Point, ...]:
  """Creates grid points for the grid."""
  grid_points = []
  for i in range(grid_size + 1):
    for j in range(grid_size + 1):
      grid_points.append(point_utils.Point(x=i / grid_size, y=j / grid_size))
  return tuple(grid_points)


def creases_to_grid(
    creases: Sequence[crease.Crease],
    grid_points: Collection[point_utils.Point],
    grid_size: int,
) -> list[crease.Crease]:
  """Converts a sequence of creases to a list of grid points."""
  atol = 0.5 / grid_size - 1e-8
  if (
      isinstance(grid_points, Sequence)
      and len(grid_points) == (grid_size + 1) ** 2
  ):
    stride = grid_size + 1
    new_creases = []
    for c in creases:
      p1 = c.p1
      ix1 = round(p1.x * grid_size)
      iy1 = round(p1.y * grid_size)
      if 0 <= ix1 <= grid_size and 0 <= iy1 <= grid_size:
        cand1 = grid_points[ix1 * stride + iy1]
        if p1.isclose(cand1, atol=atol):
          p1 = cand1
      p2 = c.p2
      ix2 = round(p2.x * grid_size)
      iy2 = round(p2.y * grid_size)
      if 0 <= ix2 <= grid_size and 0 <= iy2 <= grid_size:
        cand2 = grid_points[ix2 * stride + iy2]
        if p2.isclose(cand2, atol=atol):
          p2 = cand2
      new_creases.append(
          crease.Crease(
              p1,
              p2,
              fold=c.fold,
              fold_percent=c.fold_percent,
              elevation=c.elevation,
          )
      )
    return new_creases

  new_creases = []
  for c in creases:
    new_points = []
    for p in [c.p1, c.p2]:
      found = False
      for grid_point in grid_points:
        if p.isclose(grid_point, atol=atol):
          found = True
          new_points.append(grid_point)
          break
      if not found:
        new_points.append(p)
    new_creases.append(
        crease.Crease(
            new_points[0],
            new_points[1],
            fold=c.fold,
            fold_percent=c.fold_percent,
            elevation=c.elevation,
        )
    )
  return new_creases


def get_tips_and_grid_creases(
    creases: Sequence[crease.Crease], grid_size: int | None
) -> tuple[frozenset[point_utils.Point], Sequence[crease.Crease]]:
  """Returns the tips and grid creases."""
  tips: set[point_utils.Point] = set()
  if grid_size is not None and grid_size > 0:
    grid_points = create_grid_points(grid_size)
    grid_creases = creases_to_grid(creases, grid_points, grid_size)
    tips.update(grid_points)
  else:
    grid_creases = creases
  for c in grid_creases:
    tips.add(c.p1)
    tips.add(c.p2)
  return frozenset(tips), grid_creases


_MIN_SPATIAL_INDEX_SIZE = 64


def get_non_overlapping_creases(
    creases: Sequence[crease.Crease],
) -> list[crease.Crease]:
  """Returns the non-overlapping creases."""
  non_overlapping: list[crease.Crease] = []
  if len(creases) < _MIN_SPATIAL_INDEX_SIZE:
    for c in creases:
      if not any(c.is_overlapping(oc) for oc in non_overlapping):
        non_overlapping.append(c)
    return non_overlapping

  bbox_index = crease.CreaseBBoxIndex()
  for c in creases:
    if not bbox_index.any_overlapping(c):
      non_overlapping.append(c)
      bbox_index.add(c)
  return non_overlapping


def split_creases(
    creases_to_split: Sequence[crease.Crease],
    other_creases: Sequence[crease.Crease],
    tips: frozenset[point_utils.Point] | None = None,
    tolerance: float = crease.DEFAULT_TOLERANCE,
) -> list[crease.Crease]:
  """Splits creases by intersections with other creases."""
  new_creases = [c for c in other_creases if c.fold == crease.Fold.TRIANGLE]
  if not creases_to_split:
    return new_creases
  new_creases.extend(
      crease.split_creases_batch(
          creases_to_split,
          other_creases,
          tips=tips or (),
          tolerance=tolerance,
      )
  )
  return new_creases


class CreasePattern:
  """Creates an object to represent a Crease Pattern in Origami from an SVG."""

  def __init__(
      self,
      creases: Sequence[crease.Crease],
      light_mode: bool = False,
      num_invalid_creases: int = 0,
      grid_size: int = -1,
      is_empty: bool = False,
      merge_trivial: bool = False,
      tolerance: float = crease.DEFAULT_TOLERANCE,
  ):
    if len(creases) < 1 and not is_empty:
      raise ValueError(
          'At least one crease is required to create a pattern. '
          'Set is_empty to True if you want to create an empty pattern.'
      )
    self.light_mode = light_mode  # Light mode skips some steps in the pipeline
    # that are slow. This could be useful when the SVG was already processed.
    self.grid_size = grid_size
    self.tolerance = tolerance
    self.num_merged_creases = 0
    self.invalid_creases_ratio = num_invalid_creases
    self.creases: list[crease.Crease] = []
    tips, creases = get_tips_and_grid_creases(creases, grid_size)
    self.tips: frozenset[point_utils.Point] = tips
    self.create_creases(list(creases))
    if not self.light_mode and merge_trivial:
      self.merge_creases(only_trivial=True)
    self.sort_creases()
    self.vertices: list[vertex.Vertex] = []
    self.create_vertices_from_tips()
    total_creases = len(creases) + num_invalid_creases
    if total_creases == 0:
      self.invalid_creases_ratio = 0.0
    else:
      self.invalid_creases_ratio /= total_creases
    self.sort_vertices()

  @property
  def non_border_creases(self) -> list[crease.Crease]:
    """Returns the non-border creases in the pattern."""
    return [c for c in self.creases if c.fold != crease.Fold.BORDER]

  @property
  def num_fold_steps(self) -> int:
    """Returns the number of fold steps."""
    return max(c.fold_step for c in self.creases) + 1

  def sort_creases(self):
    """Sorts the creases by their first point."""
    self.creases.sort(
        key=lambda c: (c.p1.norm, c.p1.x, c.p1.y, c.p2.norm, c.p2.x, c.p2.y)
    )

  def update_with_shaping_creases(
      self,
      shaping_creases: Sequence[crease.Crease],
      split_base_by_shaping: bool = True,
      split_shaping_by_base: bool = True,
      split_shaping_by_shaping: bool = True,
  ) -> 'CreasePattern':
    """Updates the crease pattern with the shaping creases.

    NOTE: This method assumes that shaping creases are already split
      w.r.t themselve.

    Args:
      shaping_creases: The shaping creases to add to the crease pattern.
      split_base_by_shaping: Whether to split the base creases by the shaping
        creases. If False, the base creases are not split.
      split_shaping_by_base: Whether to split the shaping creases by the base
        creases. If False, the shaping creases are not split.
      split_shaping_by_shaping: Whether to split the shaping creases by the
        shaping creases. If False, the shaping creases are not split w.r.t
        themselves.

    Returns:
      A new CreasePattern with the shaping creases added.
    """
    if not shaping_creases:
      return self

    tips, _ = get_tips_and_grid_creases(
        creases=[*self.creases, *shaping_creases], grid_size=-1
    )

    if split_base_by_shaping:
      processed_base_creases = split_creases(
          self.creases,
          shaping_creases,
          tips,
          tolerance=self.tolerance,
      )
    else:
      processed_base_creases = self.creases

    if split_shaping_by_base or split_shaping_by_shaping:
      splitting_creases = []
      if split_shaping_by_base:
        splitting_creases.extend(self.creases)
      if split_shaping_by_shaping:
        splitting_creases.extend(shaping_creases)
      processed_shaping_creases = split_creases(
          shaping_creases,
          splitting_creases,
          tips,
          tolerance=self.tolerance,
      )
    else:
      processed_shaping_creases = shaping_creases

    return CreasePattern(
        creases=[*processed_base_creases, *processed_shaping_creases],
        light_mode=True,
        tolerance=self.tolerance,
    )

  def sort_vertices(self):
    """Sorts the creases by their first point."""
    self.vertices.sort(key=lambda v: (v.point.norm, v.point.x, v.point.y))

  def create_creases(self, creases: list[crease.Crease], cpp: bool = False):
    """Given a set of line creases, splits them into segments."""
    del cpp
    non_overlapping_creases = get_non_overlapping_creases(creases)
    self.invalid_creases_ratio += len(creases) - len(non_overlapping_creases)
    if self.light_mode:
      self.creases = non_overlapping_creases
      return
    no_triangles = []
    for c in non_overlapping_creases:
      if c.fold == crease.Fold.TRIANGLE:
        self.creases.append(c)
      else:
        no_triangles.append(c)
    if not no_triangles:
      return
    sorted_tips, sorted_xs = crease.prepare_sorted_tips(self.tips)
    if len(no_triangles) >= 32:
      bbox_index = crease.CreaseBBoxIndex()
      for oc in no_triangles:
        bbox_index.add(oc)
      for c1 in no_triangles:
        try:
          split_ts = bbox_index.collect_split_ts(c1, self.tolerance)
          self.creases.extend(
              c1._segments_from_split_ts(  # pylint: disable=protected-access
                  split_ts, sorted_tips, sorted_xs, self.tolerance
              )
          )
        except ValueError:
          self.invalid_creases_ratio += 1
      return

    for i, c1 in enumerate(no_triangles):
      try:
        self.creases.extend(
            c1.split_to_segments(
                no_triangles[:i] + no_triangles[i + 1 :],
                tips=sorted_tips,
                cpp=False,
                tolerance=self.tolerance,
            )
        )
      except ValueError:
        self.invalid_creases_ratio += 1

  def create_vertices_from_tips(self, cpp: bool = False):
    """Finds all the vertices from the tips of the creases."""
    del cpp
    tol = self.tolerance
    vertices = self.vertices
    if tol <= 0 or len(self.creases) < 32:
      for c1 in self.creases:
        if c1.fold == crease.Fold.TRIANGLE:
          continue
        for p in (c1.p1, c1.p2):
          matched_idx = -1
          for i, v in enumerate(vertices):
            if v.point.isclose(p, atol=tol):
              matched_idx = i
              break
          if matched_idx < 0:
            vertices.append(vertex.Vertex(creases=[c1], vertex_point=p))
          else:
            vertices[matched_idx].add_crease(c1)
      return

    # Use a cell size slightly exceeding `tol` so any pair of points within
    # `Point.isclose(atol=tol)` falls inside a 3x3 cell neighborhood. Taking
    # the smallest matching index preserves bit-for-bit parity with sequential
    # linear scan.
    inv_cell = 1.0 / (tol * 1.01 + 1e-9)
    grid: dict[tuple[int, int], list[tuple[int, point_utils.Point]]] = (
        collections.defaultdict(list)
    )
    for c1 in self.creases:
      if c1.fold == crease.Fold.TRIANGLE:
        continue
      for p in (c1.p1, c1.p2):
        cx = math.floor(p.x * inv_cell)
        cy = math.floor(p.y * inv_cell)
        best_idx = -1
        for dx in (-1, 0, 1):
          for dy in (-1, 0, 1):
            bucket = grid.get((cx + dx, cy + dy))
            if not bucket:
              continue
            for v_idx, v_pt in bucket:
              if (best_idx < 0 or v_idx < best_idx) and v_pt.isclose(
                  p, atol=tol
              ):
                best_idx = v_idx
        if best_idx < 0:
          new_idx = len(vertices)
          vertices.append(vertex.Vertex(creases=[c1], vertex_point=p))
          grid[(cx, cy)].append((new_idx, p))
        else:
          vertices[best_idx].add_crease(c1)

  def merge_creases(
      self, only_trivial: bool = False, merge_zebra: bool = False
  ):
    """Merges segments into longer creases."""
    num_creases = len(self.creases)
    self.creases = crease.merge_creases(self.creases, only_trivial, merge_zebra)
    self.num_merged_creases = num_creases - len(self.creases)

  def local_flat_foldability(
      self,
      *,
      check_maekawa: bool = False,
      check_blb: bool = False,
      check_kawasaki: bool = True,
      check_crimp: bool = True,
  ) -> bool:
    """Checks if the Crease Pattern satisfied necessary conditions for flat foldablity."""
    for v in self.vertices:
      if v.internal:
        if check_kawasaki and not v.check_kawasaki:
          return False
        if check_maekawa and not v.check_maekawa:
          return False
        if check_crimp and not v.check_crimp_angles:
          return False
        if check_blb and not v.check_blb:
          return False

    return True

  def is_locally_foldable(self) -> bool:
    """Determines whether the Crease Pattern is locally foldable."""
    return all(v.is_foldable for v in self.vertices if v.internal)

  def transform(
      self, weight: types.Matrix2x2, bias: types.Vector2D
  ) -> 'CreasePattern':
    """Applies a linear transform to all creases in the pattern, returning a new pattern.

    Args:
      weight: A 2x2 matrix for scaling and rotation.
      bias: A 2D offset vector (b1, b2).

    Returns:
      A new CreasePattern with the transformed coordinates.
    """
    creases = [c.transform(weight, bias) for c in self.creases]
    return CreasePattern(creases, light_mode=True, tolerance=self.tolerance)

  def is_subset(self, other: 'CreasePattern', match_fold: bool = True) -> bool:
    """Returns true if this CreasePattern is a subset of the other CreasePattern.

    To be a subset, every crease in this CP has to fall within some crease in
    the other CP.

    WARNING: A crease could be contained by two different but colinear creases
    in the other CP. Call other.merge_creases(only_trivial=False) to capture
    these cases.

    Args:
      other: The other crease pattern to check against.
      match_fold: Whether the fold type (and percentage) need to match.
    """
    for c in self.creases:
      if not any(
          c.is_within(other_c, match_fold)
          for other_c in other.creases
          if not c.not_in_encompassing_rectangles(other_c)  # Faster on average
      ):
        return False
    return True

  def get_incident_creases(
      self, point: point_utils.Point
  ) -> list[crease.Crease]:
    """Returns the creases incident to the given point."""
    return [
        c
        for c in self.creases
        if point.isclose(c.p1, atol=self.tolerance)
        or point.isclose(c.p2, atol=self.tolerance)
    ]

  def stats(self) -> dict[str, Any]:
    """Returns a dictionary of statistics about the Crease Pattern."""
    stats = {
        'invalid_ratio': self.invalid_creases_ratio,
        'num_creases': len(self.creases),
        'num_vertices': len(self.vertices),
    }
    return stats

  def vertex_flat_foldability_percentage(
      self,
      target: Optional['CreasePattern'] = None,
      *,
      check_maekawa: bool = False,
      check_blb: bool = False,
      check_kawasaki: bool = True,
      check_crimp: bool = True,
  ) -> tuple[float, list[vertex.Vertex], list[vertex.Vertex]]:
    """Percentage of flat foldable internal vertices.

    Args:
      target: An optional crease pattern whose number of flat foldable internal
        vertices is used as the target count. If None, the target is all of the
        internal vertices in the pattern.
      check_maekawa: Whether to check for Maekawa when determining flat
        foldability.
      check_blb: Whether to check for BLB when determining flat foldability.
      check_kawasaki: Whether to check for Kawasaki when determining flat
        foldability.
      check_crimp: Whether to check for crimps when determining flat
        foldability.

    Returns:
      foldability_percentage: The percentage of flat foldable internal vertices,
        between [0, 1].
      foldable_vertices: The list of internal vertices that are flat-foldable.
      non_foldable_vertices: The list of internal vertices that are not
        flat-foldable.
    """
    foldable_vertices = []
    non_foldable_vertices = []

    target_vertices = 0
    flat_internal_vertices = 0
    for v in self.vertices:
      if v.internal:
        target_vertices += 1
        if v.check_foldability_constraints(
            check_maekawa=check_maekawa,
            check_blb=check_blb,
            check_kawasaki=check_kawasaki,
            check_crimp=check_crimp,
        ):
          foldable_vertices.append(v)
          flat_internal_vertices += 1
        else:
          non_foldable_vertices.append(v)

    if target is not None:
      target_vertices = 0
      for v in target.vertices:
        if v.internal:
          target_vertices += v.check_foldability_constraints(
              check_maekawa=check_maekawa,
              check_blb=check_blb,
              check_kawasaki=check_kawasaki,
              check_crimp=check_crimp,
          )

    target_vertices = max(target_vertices, 1.0)
    flat_foldability = min(1.0, flat_internal_vertices / target_vertices)
    return flat_foldability, foldable_vertices, non_foldable_vertices

  def get_matching_creases(
      self, creases: Sequence[crease.Crease]
  ) -> list[crease.Crease]:
    """Given a list of creases, return the creases in this CP that are close to them."""
    matching_creases: list[crease.Crease] = []
    for crease_to_match in creases:
      timeout_lib.maybe_timeout_cooperatively()
      for matching_crease in self.creases:
        if matching_crease.isclose(crease_to_match, atol=self.tolerance):
          matching_creases.append(matching_crease)
          break
    return matching_creases

  @functools.cached_property
  def hash_value(self) -> int:
    """Returns a hash of the crease pattern based on its creases.

    NOTE: This hash value should be used carefully; the hash is only safe when
    the creases are on a grid, or, if the numerical accuracy of the creases is
    controlled by other means, i.e., floats are not safe for hashing.

    See `crease.Creases` and `crease.CreaseWithExactMatch` to see how the hash
    is computed.
    """
    # The creases are sorted, so this is a canonical representation.
    return hash(crease.Creases.create_from_creases(creases=self.creases))

  def __repr__(self) -> str:
    """Returns a string representation of the crease pattern."""
    return f'CreasePattern(n_creases={len(self.creases)})'
