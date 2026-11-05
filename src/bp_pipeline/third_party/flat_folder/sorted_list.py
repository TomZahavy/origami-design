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

"""Sorted list data structure."""

from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class SortedList(Generic[T]):
  """A Sorted List implementation behaving like an AVL tree via bisection.

  It maintains a sorted list of elements and provides insertion, removal,
  and search operations in logarithmic time complexity on average for
  searches, but linear time for insertions and removals due to list
  shifting.

  The sorting order is determined by a provided comparator function.
  CRITICAL: The comparator must always be called as comparator(query, node).
  """

  def __init__(self, comparator: Callable[[T, T], int]):
    """Initializes the sorted list with a comparator.

    Args:
        comparator: A function that takes two elements x and y, and returns <0
          if x < y, 0 if x == y, and >0 if x > y.
    """
    self.comparator: Callable[[T, T], int] = comparator
    self.data: list[T] = []

  @property
  def length(self) -> int:
    """Returns the number of elements in the list."""
    return len(self.data)

  def _bisect_left(self, x: T) -> int:
    """Finds insertion point for x to maintain sorted order."""
    lo, hi = 0, len(self.data)
    while lo < hi:
      mid = (lo + hi) // 2
      # We want first element where comparator(x, data[mid]) <= 0
      # i.e. x <= data[mid]
      if self.comparator(x, self.data[mid]) > 0:
        lo = mid + 1
      else:
        hi = mid
    return lo

  def _bisect_right(self, x: T) -> int:
    """Finds insertion point for x to maintain sorted order."""
    lo, hi = 0, len(self.data)
    while lo < hi:
      mid = (lo + hi) // 2
      # We want first element where comparator(x, data[mid]) < 0
      # i.e. x < data[mid]
      if self.comparator(x, self.data[mid]) < 0:
        hi = mid
      else:
        lo = mid + 1
    return lo

  def insert(self, x: T) -> T | None:
    """Inserts element x if not present, or returns existing element.

    Args:
        x: The element to insert.

    Returns:
        The existing element if a duplicate is found, otherwise None.
    """
    idx = self._bisect_left(x)
    if idx < len(self.data):
      if self.comparator(x, self.data[idx]) == 0:
        return self.data[idx]
    self.data.insert(idx, x)
    return None

  def remove(self, x: T) -> T | None:
    """Removes element x if present and returns it.

    Args:
        x: The element to remove.

    Returns:
        The removed element, or None if not found.
    """
    idx = self._bisect_left(x)
    if idx < len(self.data):
      if self.comparator(x, self.data[idx]) == 0:
        return self.data.pop(idx)
    return None

  def next(self, x: T) -> T | None:
    """Returns smallest element strictly greater than x.

    Args:
        x: The query element.

    Returns:
        The smallest element > x, or None if no such element exists.
    """
    idx = self._bisect_right(x)
    if idx < len(self.data):
      return self.data[idx]
    return None

  def prev(self, x: T) -> T | None:
    """Returns largest element strictly smaller than x.

    Args:
        x: The query element.

    Returns:
        The largest element < x, or None if no such element exists.
    """
    idx = self._bisect_left(x)
    if idx > 0:
      return self.data[idx - 1]
    return None

  def remove_next(self, x: T) -> T | None:
    """Removes and returns smallest element > x.

    Args:
        x: The query element.

    Returns:
        The removed element, or None if no element > x exists.
    """
    idx = self._bisect_right(x)
    if idx < len(self.data):
      return self.data.pop(idx)
    return None

  def remove_prev(self, x: T) -> T | None:
    """Removes and returns largest element < x.

    Args:
        x: The query element.

    Returns:
        The removed element, or None if no element < x exists.
    """
    idx = self._bisect_left(x)
    if idx > 0:
      return self.data.pop(idx - 1)
    return None
