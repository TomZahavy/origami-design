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

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.crease_pattern import crease as crease_utils
from bp_pipeline.crease_pattern import point as point_utils
from bp_pipeline.crease_pattern import rotation
import numpy as np


class RotationTest(parameterized.TestCase):

  @parameterized.named_parameters(
      dict(
          testcase_name="rotate_over_z_axis_90_deg",
          line_start=np.array([0.0, 0.0, 0.0]),
          line_end=np.array([0.0, 0.0, 1.0]),
          point=np.array([1.0, 0.0, 0.0]),
          theta=np.pi / 2,
          expected_rotated_point=np.array([0.0, 1.0, 0.0]),
      ),
      dict(
          testcase_name="rotate_over_z_axis_180_deg",
          line_start=np.array([0.0, 0.0, 0.0]),
          line_end=np.array([0.0, 0.0, 1.0]),
          point=np.array([1.0, 0.0, 0.0]),
          theta=np.pi,
          expected_rotated_point=np.array([-1.0, 0.0, 0.0]),
      ),
      dict(
          testcase_name="rotate_over_x_axis_90_deg",
          line_start=np.array([0.0, 0.0, 0.0]),
          line_end=np.array([1.0, 0.0, 0.0]),
          point=np.array([0.0, 1.0, 0.0]),
          theta=np.pi / 2,
          expected_rotated_point=np.array([0.0, 0.0, 1.0]),
      ),
      dict(
          testcase_name="rotate_over_y_axis_90_deg",
          line_start=np.array([0.0, 0.0, 0.0]),
          line_end=np.array([0.0, 1.0, 0.0]),
          point=np.array([1.0, 0.0, 0.0]),
          theta=np.pi / 2,
          expected_rotated_point=np.array([0.0, 0.0, -1.0]),
      ),
      dict(
          testcase_name="rotate_over_z_axis_90_deg_with_offset",
          line_start=np.array([1.0, 1.0, 1.0]),
          line_end=np.array([1.0, 1.0, 2.0]),
          point=np.array([2.0, 1.0, 1.0]),
          theta=np.pi / 2,
          expected_rotated_point=np.array([1.0, 2.0, 1.0]),
      ),
  )
  def test_rotate_point_around_line(
      self, line_start, line_end, point, theta, expected_rotated_point
  ):
    rotated_point = rotation.rotate_point_around_line(
        line_start, line_end, point, theta
    )
    np.testing.assert_allclose(rotated_point, expected_rotated_point, atol=1e-7)

  @parameterized.named_parameters(
      dict(
          testcase_name="rotate_360_deg",
          point=np.array([1.5, -2.5, 4.7]),
          line_start=np.array([2.0, -1.2, 8.7]),
          line_end=np.array([12.0, 6.2, -2.7]),
          n=10,
      ),
      dict(
          testcase_name="rotate_360_deg_2",
          point=np.array([1.0, 0.0, 0.0]),
          line_start=np.array([0.0, 0.0, 0.0]),
          line_end=np.array([0.0, 0.0, 1.0]),
          n=4,
      ),
  )
  def test_rotation_loop(self, point, line_start, line_end, n):
    theta_delta = 2 * np.pi / n
    point_rotated = np.array(point)
    np.testing.assert_allclose(point_rotated, point, atol=1e-7)
    for i in range(n):
      point_rotated = rotation.rotate_point_around_line(
          line_start, line_end, point_rotated, theta_delta
      )
      if i != n - 1:
        with self.assertRaises(AssertionError):
          np.testing.assert_allclose(point_rotated, point, atol=1e-7)
    np.testing.assert_allclose(point_rotated, point, atol=1e-7)

  @parameterized.named_parameters(
      dict(
          testcase_name="rotate_coord_system_over_vertical_vector_180_deg",
          vector=np.array([0.0, 1.0, 0.0]),
          theta=np.pi,
          expected_rotated_coord_system=np.array(
              [[-1, 0, 0], [0, 1, 0], [0, 0, -1]]
          ),
      ),
      dict(
          testcase_name="rotate_coord_system_over_horizontal_vector_180_deg",
          vector=np.array([1.0, 0.0, 0.0]),
          theta=np.pi,
          expected_rotated_coord_system=np.array(
              [[1, 0, 0], [0, -1, 0], [0, 0, -1]]
          ),
      ),
      dict(
          testcase_name="rotate_coord_system_over_right_diag_vector_180_deg",
          vector=np.array([1.0, 1.0, 0.0]),
          theta=np.pi,
          expected_rotated_coord_system=np.array(
              [[0, 1, 0], [1, 0, 0], [0, 0, -1]]
          ),
      ),
      dict(
          testcase_name="rotate_coord_system_over_left_diag_vector_180_deg",
          vector=np.array([-1.0, 1.0, 0.0]),
          theta=np.pi,
          expected_rotated_coord_system=np.array(
              [[0, -1, 0], [-1, 0, 0], [0, 0, -1]]
          ),
      ),
  )
  def test_rotate_coord_system_around_vector(
      self, vector, theta, expected_rotated_coord_system
  ):
    coord_system = rotation.default_coord_system()
    rotated_coord_system = rotation.rotate_coord_system_around_vector(
        coord_system, vector, theta
    )
    np.testing.assert_allclose(
        rotated_coord_system, expected_rotated_coord_system, atol=1e-7
    )

  @parameterized.named_parameters(
      dict(
          testcase_name="rotate_over_z_axis_90_deg",
          vector=np.array([0.0, 0.0, 1.0]),
          point=np.array([1.0, 0.0, 0.0]),
          theta=np.pi / 2,
          expected_rotated_point=np.array([0.0, 1.0, 0.0]),
      ),
      dict(
          testcase_name="rotate_over_z_axis_180_deg",
          vector=np.array([0.0, 0.0, 1.0]),
          point=np.array([1.0, 0.0, 0.0]),
          theta=np.pi,
          expected_rotated_point=np.array([-1.0, 0.0, 0.0]),
      ),
      dict(
          testcase_name="rotate_over_x_axis_90_deg",
          vector=np.array([1.0, 0.0, 0.0]),
          point=np.array([0.0, 1.0, 0.0]),
          theta=np.pi / 2,
          expected_rotated_point=np.array([0.0, 0.0, 1.0]),
      ),
      dict(
          testcase_name="rotate_over_y_axis_90_deg",
          vector=np.array([0.0, 1.0, 0.0]),
          point=np.array([1.0, 0.0, 0.0]),
          theta=np.pi / 2,
          expected_rotated_point=np.array([0.0, 0.0, -1.0]),
      ),
  )
  def test_rotate_point_around_vector(
      self, vector, point, theta, expected_rotated_point
  ):
    rotated_point = rotation.rotate_point_around_vector(vector, point, theta)
    np.testing.assert_allclose(rotated_point, expected_rotated_point, atol=1e-7)


class RotateCreaseTest(parameterized.TestCase):

  @parameterized.named_parameters(
      (
          "rotate_180_degrees_at_origin",
          (0.0, 0.0),
          (1.0, 0.0),
          180,
          (-1.0, 0.0),
          (2.0, 0.0),
      ),
      (
          "rotate_45_degrees_not_at_origin",
          (0.1, 0.1),
          (0.2, 0.1),
          45,
          (0.170710678118, 0.170710678118),
          (0.129289321882, 0.029289321882),
      ),
      (
          "rotate_neg_90_degrees_at_origin",
          (0.0, 0.0),
          (1.0, 0.0),
          -90,
          (0.0, -1.0),
          (1.0, 1.0),
      ),
      (
          "rotate_30_degrees_not_at_origin",
          (0.1, 0.2),
          (0.2, 0.2),
          30,
          (0.1866025, 0.25),
          (0.1133975, 0.15),
      ),
      (
          "rotate_60_degrees_not_at_origin",
          (0.1, 0.2),
          (0.2, 0.2),
          60,
          (0.15, 0.2866025),
          (0.15, 0.1133975),
      ),
      (
          "rotate_90_degrees_not_at_origin",
          (0.1, 0.2),
          (0.2, 0.2),
          90,
          (0.1, 0.3),
          (0.2, 0.1),
      ),
      (
          "rotate_diagonal_line",
          (0.1, 0.1),
          (0.2, 0.2),
          90,
          (0.0, 0.2),
          (0.3, 0.1),
      ),
      (
          "rotate_vertical_line",
          (0.1, 0.1),
          (0.1, 0.2),
          90,
          (0.0, 0.1),
          (0.2, 0.2),
      ),
  )
  def test_rotate_crease(
      self,
      p1_tuple,
      p2_tuple,
      angle_delta,
      expected_p1_tuple,
      expected_p2_tuple,
  ):
    p1 = point_utils.Point(x=p1_tuple[0], y=p1_tuple[1], require_on_paper=False)
    p2 = point_utils.Point(x=p2_tuple[0], y=p2_tuple[1], require_on_paper=False)
    c = crease_utils.Crease(p1, p2, fold=crease_utils.Fold.MOUNTAIN)

    # Test rotation about p1.
    expected_p1 = point_utils.Point(
        x=expected_p1_tuple[0], y=expected_p1_tuple[1], require_on_paper=False
    )
    rotated_c_p1 = rotation.rotate_crease_clockwise(
        crease_to_rotate=c,
        rotation_angle_degrees=angle_delta,
        rotation_origin_tip=p1,
        require_on_paper=expected_p1.on_paper,
    )
    self.assertTrue(rotated_c_p1.p1_init.isclose(p1))
    self.assertTrue(rotated_c_p1.p2_init.isclose(expected_p1))

    # Test rotating point p2 about p1.
    rotated_point = rotation.rotate_point_clockwise(
        point_to_rotate=p2,
        rotation_angle_degrees=angle_delta,
        rotation_origin_tip=p1,
        require_on_paper=expected_p1.on_paper,
    )
    self.assertTrue(rotated_point.isclose(expected_p1))

    # Test rotation about p2.
    expected_p2 = point_utils.Point(
        x=expected_p2_tuple[0], y=expected_p2_tuple[1], require_on_paper=False
    )
    rotated_c_p2 = rotation.rotate_crease_clockwise(
        crease_to_rotate=c,
        rotation_angle_degrees=angle_delta,
        rotation_origin_tip=p2,
        require_on_paper=expected_p2.on_paper,
    )
    self.assertTrue(rotated_c_p2.p1_init.isclose(expected_p2))
    self.assertTrue(rotated_c_p2.p2_init.isclose(p2))

    # Test rotating point p1 about p2.
    rotated_point = rotation.rotate_point_clockwise(
        point_to_rotate=p1,
        rotation_angle_degrees=angle_delta,
        rotation_origin_tip=p2,
        require_on_paper=expected_p2.on_paper,
    )
    self.assertTrue(rotated_point.isclose(expected_p2))

  def test_rotate_crease_invalid_origin(self):
    p1 = point_utils.Point(x=0.0, y=0.0, require_on_paper=False)
    p2 = point_utils.Point(x=1.0, y=0.0, require_on_paper=False)
    c = crease_utils.Crease(p1, p2, fold=crease_utils.Fold.MOUNTAIN)
    invalid_origin = point_utils.Point(x=0.5, y=0.5, require_on_paper=False)
    with self.assertRaises(ValueError):
      rotation.rotate_crease_clockwise(
          crease_to_rotate=c,
          rotation_angle_degrees=90,
          rotation_origin_tip=invalid_origin,
      )

    # rotate_point_clockwise does not have an invalid origin concept.
    # We can rotate p2 around invalid_origin.
    rotated_p2 = rotation.rotate_point_clockwise(
        point_to_rotate=p2,
        rotation_angle_degrees=90,
        rotation_origin_tip=invalid_origin,
        require_on_paper=False,
    )
    expected_point = point_utils.Point(x=1.0, y=1.0, require_on_paper=False)
    self.assertTrue(rotated_p2.isclose(expected_point))

  def test_rotate_crease_outside_paper_error(self):
    p1 = point_utils.Point(x=0.0, y=0.0)
    p2 = point_utils.Point(x=1.0, y=0.0)
    c = crease_utils.Crease(p1, p2, fold=crease_utils.Fold.MOUNTAIN)
    with self.assertRaises(ValueError):
      rotation.rotate_crease_clockwise(
          crease_to_rotate=c,
          rotation_angle_degrees=180,
          rotation_origin_tip=p1,
          require_on_paper=True,
      )

    with self.assertRaises(ValueError):
      rotation.rotate_point_clockwise(
          point_to_rotate=p2,
          rotation_angle_degrees=180,
          rotation_origin_tip=p1,
          require_on_paper=True,
      )


if __name__ == "__main__":
  absltest.main()
