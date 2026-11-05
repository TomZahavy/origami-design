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

"""Functions to perform rotation of points in 3D space."""

import math

from bp_pipeline.crease_pattern import crease as crease_utils
from bp_pipeline.crease_pattern import point as point_utils
import numpy as np


def rotation_matrix(k: np.ndarray, theta: float) -> np.ndarray:
  """Creates a rotation matrix using Rodrigues' formula.

  Args:
      k: A numpy array representing the unit rotation axis (line vector).
      theta: The rotation angle in radians.

  Returns:
      A 3x3 numpy array representing the rotation matrix.
  """
  norm_k = np.linalg.norm(k)
  if np.isclose(norm_k, 0.0):
    raise ValueError("Rotation axis k cannot be a zero vector.")
  k = k / norm_k  # Ensure k is a unit vector
  kx, ky, kz = k
  K = np.array([[0, -kz, ky], [kz, 0, -kx], [-ky, kx, 0]])  # pylint: disable=invalid-name
  I = np.identity(3)  # pylint: disable=invalid-name
  R = I + np.sin(theta) * K + (1 - np.cos(theta)) * np.dot(K, K)  # pylint: disable=invalid-name
  return R  # pylint: disable=invalid-name


def rotate_point_around_line(
    line_start: np.ndarray,
    line_end: np.ndarray,
    point: np.ndarray,
    theta: float,
) -> np.ndarray:
  k = line_end - line_start
  v = point - line_start
  R = rotation_matrix(k, theta)  # pylint: disable=invalid-name
  return np.dot(R, v) + line_start  # pylint: disable=invalid-name


def default_coord_system() -> np.ndarray:
  return np.identity(3)


def rotate_point_around_vector(
    vector: np.ndarray, point: np.ndarray, theta: float
) -> np.ndarray:
  return rotate_point_around_line(
      line_start=np.array([0.0, 0.0, 0.0]),
      line_end=vector,
      point=point,
      theta=theta,
  )


def rotate_coord_system_around_vector(
    coord_system: np.ndarray, vector: np.ndarray, theta: float
) -> np.ndarray:
  R = rotation_matrix(vector, theta)  # pylint: disable=invalid-name
  return np.dot(coord_system, R.T)


def rotate_point_clockwise(
    point_to_rotate: point_utils.Point,
    rotation_angle_degrees: float,
    rotation_origin_tip: point_utils.Point,
    require_on_paper: bool = True,
) -> point_utils.Point:
  """Rotates a point clockwise around another point.

  Args:
    point_to_rotate: The point to rotate.
    rotation_angle_degrees: The clockwise angle to rotate by in degrees.
    rotation_origin_tip: The point to rotate point_to_rotate around.
    require_on_paper: If True, the rotated point must be on the paper.

  Returns:
    The rotated point.
  """
  rotation_angle_rad = math.radians(rotation_angle_degrees)
  cos_theta = math.cos(rotation_angle_rad)
  sin_theta = math.sin(rotation_angle_rad)

  # 2D rotation matrix
  rotation_matrix_2d = np.array(
      [[cos_theta, -sin_theta], [sin_theta, cos_theta]]
  )

  identity = np.identity(2)
  origin_vector = np.array([rotation_origin_tip.x, rotation_origin_tip.y])
  bias = np.dot(identity - rotation_matrix_2d, origin_vector)

  return point_to_rotate.transform(
      tuple(map(tuple, rotation_matrix_2d)),  # type: ignore[arg-type]
      tuple(bias),  # type: ignore[arg-type]
      require_on_paper,
  )


def rotate_crease_clockwise(
    crease_to_rotate: crease_utils.Crease,
    rotation_angle_degrees: float,
    rotation_origin_tip: point_utils.Point,
    require_on_paper: bool = True,
) -> crease_utils.Crease:
  """Rotates a crease clockwise around one of its tips.

  Args:
    crease_to_rotate: The crease to rotate.
    rotation_angle_degrees: The clockwise angle to rotate by in degrees.
    rotation_origin_tip: The tip of the crease to rotate around.
    require_on_paper: If True, the rotated crease must be on the paper.

  Returns:
    A new crease object representing the rotated crease.

  Raises:
    ValueError: If the rotation origin is not one of the crease's tips.
  """
  if not (
      rotation_origin_tip.isclose(crease_to_rotate.p1)
      or rotation_origin_tip.isclose(crease_to_rotate.p2)
  ):
    raise ValueError("The rotation origin must be one of the crease's tips.")

  rotation_angle_rad = math.radians(rotation_angle_degrees)
  cos_theta = math.cos(rotation_angle_rad)
  sin_theta = math.sin(rotation_angle_rad)

  # 2D rotation matrix
  rotation_matrix_2d = np.array(
      [[cos_theta, -sin_theta], [sin_theta, cos_theta]]
  )

  identity = np.identity(2)
  origin_vector = np.array([rotation_origin_tip.x, rotation_origin_tip.y])
  bias = np.dot(identity - rotation_matrix_2d, origin_vector)

  return crease_to_rotate.transform(
      tuple(map(tuple, rotation_matrix_2d)),  # type: ignore[arg-type]
      tuple(bias),  # type: ignore[arg-type]
      require_on_paper,
  )
