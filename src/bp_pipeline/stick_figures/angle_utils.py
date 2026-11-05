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

"""Angle utility functions for stick figures."""

import logging
import math
from typing import Literal, TypeAlias
import numpy as np

Angles: TypeAlias = Literal['azimuth', 'elevation']
AZIMUTH_PERIOD = 360.0
ELEVATION_PERIOD = 90.0


def wrap_angle_centered(angle: float, period: float) -> float:
  """Wraps an angle to the range [-period/2, period/2)."""
  return (angle + period / 2) % period - period / 2


def are_azimuth_angles_the_same(
    angle1: float, angle2: float, abs_tol: float = 1e-3
) -> bool:
  """Checks if two angles are approximately equal, handling wrapping around 360 degrees."""
  shortest_diff = wrap_angle_centered(angle1 - angle2, AZIMUTH_PERIOD)
  return math.isclose(shortest_diff, 0.0, abs_tol=abs_tol)


def are_azimuth_angles_collinear(
    angle1: float, angle2: float, abs_tol: float = 1e-3
) -> bool:
  """Checks if two angles are collinear (approximately equal or opposite)."""
  return are_azimuth_angles_the_same(
      angle1, angle2, abs_tol=abs_tol
  ) or are_azimuth_angles_the_same(
      angle1, angle2 + AZIMUTH_PERIOD / 2, abs_tol=abs_tol
  )


def get_reflection_angle(
    angle: float, axis_angle: float, axis: Angles
) -> float:
  """Reflect an angle across an axis defined by `axis_angle`."""
  # Rotate the coordinate system so the axis of symmetry is the x-axis.
  rotated_angle = angle - axis_angle
  # Reflect across the new x-axis.
  reflected_rotated_angle = -rotated_angle
  # Rotate back to the original coordinate system.
  reflected_angle = reflected_rotated_angle + axis_angle
  if axis == 'azimuth':
    return wrap_angle_centered(reflected_angle, AZIMUTH_PERIOD)
  return reflected_angle


def cartesian_to_spherical(p: np.ndarray) -> tuple[float, float]:
  """Converts Cartesian coordinates (x, y, z) back to spherical coordinates.

  Args:
    p: A 3-dimensional NumPy array representing the Cartesian coordinates.

  Returns:
    A tuple of azimuth and elevation angles in degrees.
  """
  if p.shape != (3,):
    raise ValueError(f'Input array must be shape (3,), got {p.shape} shape.')

  x, y, z = p
  length = np.linalg.norm(p)

  if math.isclose(length, 0.0):
    logging.warning('Length of the vector is 0.0, returning (0.0, 0.0).')
    return 0.0, 0.0

  # Elevation is the angle with the XY plane, calculated from z
  elevation_rad = math.asin(z / length)

  # Azimuth is calculated from the Y-axis (North) using atan2(-x, y)
  azimuth_rad = math.atan2(-x, y)

  return math.degrees(azimuth_rad), math.degrees(elevation_rad)


def get_rotation_matrix_from_axis_angle(
    axis_vec: np.ndarray, angle_deg: float
) -> np.ndarray:
  """Calculates the 3D rotation matrix from an arbitrary axis and an angle.

  This implementation uses the Rodrigues' rotation formula.

  Args:
    axis_vec: A 3D NumPy array defining the axis of rotation.
    angle_deg: The angle of rotation in degrees.

  Returns:
    A 3x3 NumPy array representing the rotation matrix.
  """
  angle_rad = math.radians(angle_deg)

  # Normalize the rotation axis to ensure it is a unit vector
  axis = axis_vec / np.linalg.norm(axis_vec)

  k = axis
  c = math.cos(angle_rad)
  s = math.sin(angle_rad)
  t = 1 - c
  x, y, z = k

  # The matrix form of Rodrigues' rotation formula
  return np.array([
      [t * x * x + c, t * x * y - s * z, t * x * z + s * y],
      [t * x * y + s * z, t * y * y + c, t * y * z - s * x],
      [t * x * z - s * y, t * y * z + s * x, t * z * z + c],
  ])


def get_rotation_matrix_to_align(
    vec_start: np.ndarray, vec_target: np.ndarray
) -> np.ndarray:
  """Calculates the rotation matrix that aligns a starting vector with a target vector.

  Note that the input vectors are normalized to unit vectors for calculation.
  the rotation matrix.

  Args:
    vec_start: The initial 3D vector.
    vec_target: The target 3D vector.

  Returns:
    A 3x3 NumPy array representing the rotation matrix.
  """

  # 1. Normalize the input vectors to unit vectors
  v_start = vec_start / np.linalg.norm(vec_start)
  v_target = vec_target / np.linalg.norm(vec_target)

  # 2. Handle edge cases
  # If vectors are already aligned, return the identity matrix (no rotation)
  if np.allclose(v_start, v_target):
    return np.identity(3)

  # If vectors are diametrically opposed (180 degrees apart)
  if np.allclose(v_start, -v_target):
    # Find an arbitrary perpendicular vector to use as the rotation axis.
    # We can find this by taking the cross product with a non-parallel vector.
    axis = np.cross(v_start, [0, 0, 1])
    if np.linalg.norm(axis) < 1e-6:  # If v_start is parallel to the Z-axis
      axis = np.cross(v_start, [0, 1, 0])
    return get_rotation_matrix_from_axis_angle(axis, 180.0)

  # 3. Find the rotation axis via the cross product
  axis = np.cross(v_start, v_target)

  # 4. Find the rotation angle via the dot product
  # The dot product of two unit vectors is the cosine of the angle between them.
  angle_rad = np.arccos(np.dot(v_start, v_target))
  angle_deg = math.degrees(angle_rad)

  # 5. Generate the final rotation matrix using the axis and angle
  return get_rotation_matrix_from_axis_angle(axis, angle_deg)
