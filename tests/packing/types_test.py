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
from bp_pipeline.packing import types


class SacrificialFlapCreateTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self.grid_size = 10

  def _create_placement(self, offset, size):
    """Helper to create a PolygonPlacement."""
    return types.PolygonPlacement.from_grid_coords(
        offset=offset, size=size, grid_size=self.grid_size
    )

  @parameterized.named_parameters(
      dict(
          testcase_name='main_on_right',
          strip_offset=(0, 0),
          strip_size=(2, 4),
          main_offset=(2, 0),
          main_size=(4, 4),
          orientation='vertical',
          expected='right',
      ),
      dict(
          testcase_name='main_on_left',
          strip_offset=(4, 0),
          strip_size=(2, 4),
          main_offset=(0, 0),
          main_size=(4, 4),
          orientation='vertical',
          expected='left',
      ),
      dict(
          testcase_name='main_on_bottom',
          strip_offset=(0, 0),
          strip_size=(4, 2),
          main_offset=(0, 2),
          main_size=(4, 4),
          orientation='horizontal',
          expected='bottom',
      ),
      dict(
          testcase_name='main_on_top',
          strip_offset=(0, 4),
          strip_size=(4, 2),
          main_offset=(0, 0),
          main_size=(4, 4),
          orientation='horizontal',
          expected='top',
      ),
      dict(
          testcase_name='not_adjacent_touching_corner',
          strip_offset=(0, 0),
          strip_size=(2, 2),
          main_offset=(2, 2),
          main_size=(2, 2),
          orientation='vertical',
          expected='right',
      ),
  )
  def test_create_calculates_relative_position(
      self,
      strip_offset,
      strip_size,
      main_offset,
      main_size,
      orientation,
      expected,
  ):
    strip_placement = self._create_placement(strip_offset, strip_size)
    main_placement = self._create_placement(main_offset, main_size)

    sacrificial_flap = types.SacrificialFlap.from_flap_placement(
        polygon_name='sacrificial',
        placement=strip_placement,
        shifted_element_name='base',
        orientation=orientation,
        main_placement=main_placement,
    )
    self.assertEqual(sacrificial_flap.crimp_direction, expected)

  def test_disjoint_raises_error(self):
    strip_placement = self._create_placement((0, 0), (2, 2))
    main_placement = self._create_placement((4, 4), (2, 2))
    with self.assertRaises(ValueError):
      types.SacrificialFlap.from_flap_placement(
          polygon_name='sacrificial',
          placement=strip_placement,
          shifted_element_name='base',
          orientation='vertical',
          main_placement=main_placement,
      )


if __name__ == '__main__':
  absltest.main()
