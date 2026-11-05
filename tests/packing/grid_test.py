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
from bp_pipeline.packing import grid


class GridDeltaTest(parameterized.TestCase):

  def test_add(self):
    delta1 = grid.Delta(di=1, dj=2)
    delta2 = grid.Delta(di=-1, dj=1)
    self.assertEqual(delta1 + delta2, grid.Delta(di=0, dj=3))

  def test_sub(self):
    delta1 = grid.Delta(di=1, dj=2)
    delta2 = grid.Delta(di=-1, dj=1)
    self.assertEqual(delta1 - delta2, grid.Delta(di=2, dj=1))

  @parameterized.named_parameters(
      ('pos', grid.Delta(di=2, dj=3), 5),
      ('neg', grid.Delta(di=-2, dj=-3), 5),
      ('zero', grid.Delta(di=0, dj=0), 0),
  )
  def test_l1_norm(self, delta, expected_norm):
    self.assertEqual(delta.l1_norm, expected_norm)

  @parameterized.parameters(
      (grid.Delta(di=1, dj=2), True),
      (grid.Delta(di=0, dj=0), True),
      (grid.Delta(di=2, dj=4), True),
      (grid.Delta(di=1, dj=1), False),
      (grid.Delta(di=3, dj=6), False),
  )
  def test_is_subdelta_of(self, subdelta, expected):
    delta = grid.Delta(di=2, dj=4)
    self.assertEqual(subdelta.is_subdelta_of(delta), expected)

  def test_inverse(self):
    self.assertEqual(grid.Delta(di=1, dj=-2).inverse, grid.Delta(di=-1, dj=2))

  @parameterized.parameters(
      (grid.Delta(di=-1, dj=0), grid.Direction.NORTH),
      (grid.Delta(di=1, dj=0), grid.Direction.SOUTH),
      (grid.Delta(di=0, dj=1), grid.Direction.EAST),
      (grid.Delta(di=0, dj=-1), grid.Direction.WEST),
  )
  def test_direction(self, delta, expected_direction):
    self.assertEqual(delta.direction, expected_direction)

  @parameterized.parameters(
      grid.Delta(di=0, dj=0),
      grid.Delta(di=1, dj=1),
  )
  def test_direction_raises_error(self, delta):
    with self.assertRaises(ValueError):
      _ = delta.direction

  @parameterized.named_parameters(
      (
          'positive_i',
          grid.Delta(di=2, dj=0),
          (
              grid.Delta(di=0, dj=0),
              grid.Delta(di=1, dj=0),
              grid.Delta(di=2, dj=0),
          ),
      ),
      (
          'positive_j',
          grid.Delta(di=0, dj=2),
          (
              grid.Delta(di=0, dj=0),
              grid.Delta(di=0, dj=1),
              grid.Delta(di=0, dj=2),
          ),
      ),
      (
          'positive_i_j',
          grid.Delta(di=2, dj=2),
          (
              grid.Delta(di=0, dj=0),
              grid.Delta(di=1, dj=1),
              grid.Delta(di=2, dj=2),
          ),
      ),
      (
          'negative_i_j',
          grid.Delta(di=-1, dj=-1),
          (
              grid.Delta(di=0, dj=0),
              grid.Delta(di=-1, dj=-1),
          ),
      ),
      (
          'zero',
          grid.Delta(di=0, dj=0),
          (grid.Delta(di=0, dj=0),),
      ),
  )
  def test_all_subdeltas(self, delta, expected_subdeltas):
    self.assertEqual(grid.all_subdeltas(delta), expected_subdeltas)


class GridDirectionTest(parameterized.TestCase):

  def test_order(self):
    self.assertEqual(
        list(grid.Direction),
        [
            grid.Direction.NORTH,
            grid.Direction.EAST,
            grid.Direction.SOUTH,
            grid.Direction.WEST,
        ],
    )

  @parameterized.named_parameters(
      ('north', grid.Direction.NORTH, grid.Direction.WEST),
      ('east', grid.Direction.EAST, grid.Direction.NORTH),
      ('south', grid.Direction.SOUTH, grid.Direction.EAST),
      ('west', grid.Direction.WEST, grid.Direction.SOUTH),
  )
  def test_rotate_left(self, direction, expected):
    self.assertEqual(direction.rotate_left(), expected)

  @parameterized.named_parameters(
      ('north', grid.Direction.NORTH, grid.Direction.SOUTH),
      ('east', grid.Direction.EAST, grid.Direction.WEST),
      ('south', grid.Direction.SOUTH, grid.Direction.NORTH),
      ('west', grid.Direction.WEST, grid.Direction.EAST),
  )
  def test_flip(self, direction, expected):
    self.assertEqual(direction.flip(), expected)

  @parameterized.named_parameters(
      ('north', grid.Direction.NORTH, grid.Direction.EAST),
      ('east', grid.Direction.EAST, grid.Direction.SOUTH),
      ('south', grid.Direction.SOUTH, grid.Direction.WEST),
      ('west', grid.Direction.WEST, grid.Direction.NORTH),
  )
  def test_rotate_right(self, direction, expected):
    self.assertEqual(direction.rotate_right(), expected)

  @parameterized.named_parameters(
      ('north', grid.Direction.NORTH, False),
      ('east', grid.Direction.EAST, True),
      ('south', grid.Direction.SOUTH, False),
      ('west', grid.Direction.WEST, True),
  )
  def test_is_horizontal(self, direction, expected):
    self.assertEqual(direction.is_horizontal, expected)

  @parameterized.named_parameters(
      ('north', grid.Direction.NORTH, True),
      ('east', grid.Direction.EAST, False),
      ('south', grid.Direction.SOUTH, True),
      ('west', grid.Direction.WEST, False),
  )
  def test_is_vertical(self, direction, expected):
    self.assertEqual(direction.is_vertical, expected)

  def test_str(self):
    self.assertEqual(str(grid.Direction.NORTH), 'NORTH')

  @parameterized.named_parameters(
      ('north', grid.Direction.NORTH, grid.Delta(di=-1, dj=0)),
      ('east', grid.Direction.EAST, grid.Delta(di=0, dj=1)),
      ('south', grid.Direction.SOUTH, grid.Delta(di=1, dj=0)),
      ('west', grid.Direction.WEST, grid.Delta(di=0, dj=-1)),
  )
  def test_step_delta(self, direction, expected):
    self.assertEqual(direction.step_delta, expected)


class GridCellTest(parameterized.TestCase):

  def test_delta_to(self):
    cell1 = grid.Cell(i=1, j=2)
    cell2 = grid.Cell(i=0, j=4)
    self.assertEqual(cell2.delta_to(cell1), grid.Delta(di=1, dj=-2))

  def test_shift(self):
    cell = grid.Cell(i=1, j=2)
    delta = grid.Delta(di=-1, dj=1)
    self.assertEqual(cell.shift(delta), grid.Cell(i=0, j=3))

  def test_shift_with_delta_to(self):
    cell1 = grid.Cell(i=1, j=2)
    cell2 = grid.Cell(i=0, j=4)
    self.assertEqual(cell2.shift(cell2.delta_to(cell1)), cell1)

  @parameterized.parameters(
      (grid.Axis.VERTICAL, 1),
      (grid.Axis.HORIZONTAL, 2),
  )
  def test_axial_offset(self, direction, expected):
    cell = grid.Cell(i=1, j=2)
    self.assertEqual(cell.axial_offset(direction), expected)

  @parameterized.named_parameters(
      ('inside', grid.Cell(i=1, j=1), None, True),
      ('outside_i', grid.Cell(i=-1, j=1), None, False),
      ('outside_j', grid.Cell(i=1, j=-1), None, False),
      ('inside_vertical_axis', grid.Cell(i=1, j=-1), grid.Axis.VERTICAL, True),
      (
          'outside_vertical_axis',
          grid.Cell(i=-1, j=1),
          grid.Axis.VERTICAL,
          False,
      ),
      (
          'inside_horizontal_axis',
          grid.Cell(i=-1, j=1),
          grid.Axis.HORIZONTAL,
          True,
      ),
      (
          'outside_horizontal_axis',
          grid.Cell(i=1, j=-1),
          grid.Axis.HORIZONTAL,
          False,
      ),
  )
  def test_is_within_grid(self, cell, axis, expected):
    if axis is None:
      self.assertEqual(cell.is_within_grid(grid_size=3), expected)
    else:
      self.assertEqual(cell.is_within_grid(grid_size=3, axis=axis), expected)

  @parameterized.named_parameters(
      ('inside', grid.Cell(i=1, j=1), None, grid.Cell(i=1, j=1)),
      ('outside_i_neg_j_neg', grid.Cell(i=-1, j=-1), None, grid.Cell(i=0, j=0)),
      ('outside_i_pos_j_pos', grid.Cell(i=3, j=3), None, grid.Cell(i=2, j=2)),
      (
          'outside_i_pos_j_neg_vertical',
          grid.Cell(i=3, j=-1),
          grid.Axis.VERTICAL,
          grid.Cell(i=2, j=-1),
      ),
      (
          'outside_i_pos_j_neg_horizontal',
          grid.Cell(i=3, j=-1),
          grid.Axis.HORIZONTAL,
          grid.Cell(i=3, j=0),
      ),
  )
  def test_clamp(self, cell, axis, expected):
    if axis is None:
      self.assertEqual(cell.clamp(grid_size=3), expected)
    else:
      self.assertEqual(cell.clamp(grid_size=3, axis=axis), expected)


class GridWalkTest(parameterized.TestCase):

  @parameterized.named_parameters(
      dict(
          testcase_name='within_bounds',
          start_cell=grid.Cell(i=1, j=1),
          direction=grid.Direction.EAST,
          grid_size=3,
          steps=None,
          expected=[grid.Cell(i=1, j=1), grid.Cell(i=1, j=2)],
      ),
      dict(
          testcase_name='with_steps',
          start_cell=grid.Cell(i=0, j=0),
          direction=grid.Direction.SOUTH,
          grid_size=3,
          steps=2,
          expected=[grid.Cell(i=0, j=0), grid.Cell(i=1, j=0)],
      ),
      dict(
          testcase_name='hits_boundary',
          start_cell=grid.Cell(i=1, j=1),
          direction=grid.Direction.NORTH,
          grid_size=3,
          steps=None,
          expected=[grid.Cell(i=1, j=1), grid.Cell(i=0, j=1)],
      ),
      dict(
          testcase_name='start_outside_bounds_is_clamped',
          start_cell=grid.Cell(i=-1, j=1),
          direction=grid.Direction.SOUTH,
          grid_size=3,
          steps=None,
          expected=[
              grid.Cell(i=0, j=1),
              grid.Cell(i=1, j=1),
              grid.Cell(i=2, j=1),
          ],
      ),
      dict(
          testcase_name='with_none_steps_is_no_limit',
          start_cell=grid.Cell(i=0, j=0),
          direction=grid.Direction.EAST,
          grid_size=2,
          steps=None,
          expected=[grid.Cell(i=0, j=0), grid.Cell(i=0, j=1)],
      ),
      dict(
          testcase_name='start_outside_with_steps',
          start_cell=grid.Cell(i=3, j=0),
          direction=grid.Direction.NORTH,
          grid_size=3,
          steps=2,
          expected=[grid.Cell(i=2, j=0)],
      ),
      dict(
          testcase_name='start_outside_with_none_steps',
          start_cell=grid.Cell(i=0, j=-50),
          direction=grid.Direction.EAST,
          grid_size=2,
          steps=None,
          expected=[grid.Cell(i=0, j=0), grid.Cell(i=0, j=1)],
      ),
  )
  def test_iter(self, start_cell, direction, grid_size, steps, expected):
    walk = grid.Walk(
        start_cell=start_cell,
        direction=direction,
        grid_size=grid_size,
        steps=steps,
    )
    self.assertEqual(list(walk), expected)
    self.assertLen(walk, len(expected))

  def test_post_init_raises_error_for_non_positive_steps(self):
    with self.assertRaisesRegex(ValueError, 'steps must be positive'):
      grid.Walk(
          start_cell=grid.Cell(i=1, j=1),
          direction=grid.Direction.EAST,
          grid_size=3,
          steps=-1,
      )

  @parameterized.parameters(0, -1)
  def test_post_init_raises_error_for_non_positive_grid_size(self, grid_size):
    with self.assertRaisesRegex(ValueError, 'grid_size must be positive'):
      grid.Walk(
          start_cell=grid.Cell(i=1, j=1),
          direction=grid.Direction.EAST,
          grid_size=grid_size,
          steps=1,
      )

  @parameterized.named_parameters(
      dict(
          testcase_name='north_from_west',
          start_cell=grid.Cell(i=0, j=-1),
          direction=grid.Direction.NORTH,
      ),
      dict(
          testcase_name='south_from_east',
          start_cell=grid.Cell(i=0, j=3),
          direction=grid.Direction.SOUTH,
      ),
      dict(
          testcase_name='north from north',
          start_cell=grid.Cell(i=-1, j=0),
          direction=grid.Direction.NORTH,
      ),
  )
  def test_post_init_raises_error_for_wrong_direction(
      self, start_cell, direction
  ):
    with self.assertRaisesRegex(
        ValueError, 'Walk is in the wrong direction to arrive on the grid'
    ):
      grid.Walk(
          start_cell=start_cell,
          direction=direction,
          grid_size=3,
          steps=None,
      )

  @parameterized.parameters(
      (grid.Cell(i=-1, j=0), grid.Direction.SOUTH, 1),
      (grid.Cell(i=0, j=-1), grid.Direction.EAST, 1),
      (grid.Cell(i=-2, j=0), grid.Direction.SOUTH, 2),
  )
  def test_post_init_raises_error_for_too_short_walk(
      self, start_cell, direction, steps
  ):
    with self.assertRaisesRegex(
        ValueError, 'Walk is too short to arrive on the grid'
    ):
      grid.Walk(
          start_cell=start_cell,
          direction=direction,
          grid_size=3,
          steps=steps,
      )


if __name__ == '__main__':
  absltest.main()
