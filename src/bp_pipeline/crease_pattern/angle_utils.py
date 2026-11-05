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

"""Utility functions for angles."""

import math

from bp_pipeline.crease_pattern import point


def find_angle_from_points(p1: point.Point, p2: point.Point) -> float:
  """Finds the angle between the x-axis and the line from p1 and p2."""
  return find_angle_from_vector(p2.x - p1.x, p2.y - p1.y) % (2 * math.pi)


def find_angle_from_vector(vx: float, vy: float) -> float:
  """Finds the angle between the x-axis and vector (dx, dy)."""
  return math.atan2(vy, vx)


def angle_from_vector_in_degrees(vx: float, vy: float) -> float:
  """Converts an angle to degrees."""
  return math.degrees(find_angle_from_vector(vx, vy)) % 360
