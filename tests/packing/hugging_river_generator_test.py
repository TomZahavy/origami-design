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
from bp_pipeline.packing import hugging_river_generator
from bp_pipeline.packing import river as river_lib
import numpy as np


class GeneratePathVariantsHelpersTest(absltest.TestCase):

  def test_extend_straight_to_boundary_simple(self):
    grid = np.zeros((3, 3), dtype=bool)
    path = hugging_river_generator.extend_straight_to_boundary(
        start_node=(0, 0),
        direction=river_lib.Direction.EAST,
        grid_size=3,
        occupancy_grid=grid,
        current_path_prefix=[],
    )
    self.assertEqual(path, ((0, 0), (0, 1), (0, 2)))

  def test_extend_straight_to_boundary_with_obstacle(self):
    grid = np.zeros((3, 3), dtype=bool)
    grid[0, 2] = True
    path = hugging_river_generator.extend_straight_to_boundary(
        start_node=(0, 0),
        direction=river_lib.Direction.EAST,
        grid_size=3,
        occupancy_grid=grid,
        current_path_prefix=[],
    )
    self.assertIsNone(path)

  def test_extend_straight_to_boundary_with_path_collision(self):
    grid = np.zeros((3, 3), dtype=bool)
    path = hugging_river_generator.extend_straight_to_boundary(
        start_node=(1, 0),
        direction=river_lib.Direction.EAST,
        grid_size=3,
        occupancy_grid=grid,
        current_path_prefix=[(1, 1)],
    )
    self.assertIsNone(path)

  def test_generate_turn_away_variant_simple(self):
    state = river_lib.NeighborState(
        is_hugging_occupied=False,
        is_front_occupied=False,
        is_opposite_occupied=False,
        hugging_cell=(1, 1),
        front_cell=(1, 2),
        opposite_cell=(2, 2),
    )
    grid = np.zeros((3, 3), dtype=bool)
    path = hugging_river_generator.generate_turn_away_variant(
        state=state,
        direction=river_lib.Direction.EAST,
        away_turn=-1,
        grid_size=3,
        occupancy_grid=grid,
        path_prefix=[(0, 0)],
        visited_in_prefix={(0, 0)},
    )
    self.assertIsNone(path)

  def test_generate_turn_away_variant_opposite_occupied(self):
    state = river_lib.NeighborState(
        is_hugging_occupied=False,
        is_front_occupied=False,
        is_opposite_occupied=True,
        hugging_cell=(1, 1),
        front_cell=(1, 2),
        opposite_cell=(2, 2),
    )
    grid = np.zeros((3, 3), dtype=bool)
    path = hugging_river_generator.generate_turn_away_variant(
        state=state,
        direction=river_lib.Direction.EAST,
        away_turn=-1,
        grid_size=3,
        occupancy_grid=grid,
        path_prefix=[(0, 0)],
        visited_in_prefix={(0, 0)},
    )
    self.assertIsNone(path)

  def test_generate_continue_straight_variant_simple(self):
    state = river_lib.NeighborState(
        is_hugging_occupied=False,
        is_front_occupied=False,
        is_opposite_occupied=False,
        hugging_cell=(1, 1),
        front_cell=(2, 3),
        opposite_cell=(3, 1),
    )
    grid = np.zeros((3, 3), dtype=bool)
    path = hugging_river_generator.generate_continue_straight_variant(
        state=state,
        direction=river_lib.Direction.EAST,
        grid_size=3,
        occupancy_grid=grid,
        path_prefix=[(1, 0)],
        visited_in_prefix={(1, 0)},
    )
    self.assertIsNone(path)

  def test_generate_continue_straight_variant_front_occupied(self):
    state = river_lib.NeighborState(
        is_hugging_occupied=False,
        is_front_occupied=True,
        is_opposite_occupied=False,
        hugging_cell=(1, 1),
        front_cell=(2, 3),
        opposite_cell=(3, 1),
    )
    grid = np.zeros((3, 3), dtype=bool)
    path = hugging_river_generator.generate_continue_straight_variant(
        state=state,
        direction=river_lib.Direction.EAST,
        grid_size=3,
        occupancy_grid=grid,
        path_prefix=[(1, 0)],
        visited_in_prefix={(1, 0)},
    )
    self.assertIsNone(path)

  def test_generate_corner_variant_inner_corner(self):
    state = river_lib.NeighborState(
        is_hugging_occupied=False,
        is_front_occupied=True,
        is_opposite_occupied=False,
        hugging_cell=(1, 2),
        front_cell=(2, 3),
        opposite_cell=(3, 2),
    )
    grid = np.zeros((3, 3), dtype=bool)
    padded_grid = np.pad(grid, 1, 'constant', constant_values=False)
    path = hugging_river_generator.generate_corner_variant(
        state=state,
        direction=river_lib.Direction.EAST,
        hug_side=river_lib.HugSide.RIGHT,
        padded_grid=padded_grid,
        grid_size=3,
        occupancy_grid=grid,
        path_prefix=[(0, 0)],
        visited_in_prefix={(0, 0)},
    )
    self.assertEqual(path, ((0, 0), (0, 1), (1, 1), (2, 1)))

  def test_generate_corner_variant_outer_corner(self):
    state = river_lib.NeighborState(
        is_hugging_occupied=False,
        is_front_occupied=False,
        is_opposite_occupied=False,
        hugging_cell=(1, 2),
        front_cell=(2, 3),
        opposite_cell=(3, 2),
    )
    grid = np.zeros((3, 3), dtype=bool)
    padded_grid = np.pad(grid, 1, 'constant', constant_values=False)
    path = hugging_river_generator.generate_corner_variant(
        state=state,
        direction=river_lib.Direction.EAST,
        hug_side=river_lib.HugSide.RIGHT,
        padded_grid=padded_grid,
        grid_size=3,
        occupancy_grid=grid,
        path_prefix=[(1, 1)],
        visited_in_prefix={(1, 1)},
    )
    self.assertIsNone(path)

  def test_generate_path_variants_no_obstacle(self):
    grid = np.zeros((3, 3), dtype=bool)
    paths = list(
        hugging_river_generator.generate_path_variants(
            grid_size=3,
            occupancy_grid=grid,
            start_cell=(0, 1),
            hug_side=river_lib.HugSide.RIGHT,
        )
    )
    self.assertEmpty(paths)

  def test_generate_path_variants_6x6_l_shape_obstacle(self):
    grid = np.zeros((6, 6), dtype=bool)
    grid[0, 1:4] = True
    grid[1:4, 3] = True
    paths = list(
        hugging_river_generator.generate_path_variants(
            grid_size=6,
            occupancy_grid=grid,
            start_cell=(0, 0),
            hug_side=river_lib.HugSide.LEFT,
        )
    )
    path_tuples = {p for p, _ in paths}
    expected_paths = [
        (
            (0, 0),
            (1, 0),
            (1, 1),
            (1, 2),
            (2, 2),
            (3, 2),
            (4, 2),
            (4, 3),
            (4, 4),
            (3, 4),
            (2, 4),
            (1, 4),
            (0, 4),
        ),
        ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)),
        ((0, 0), (1, 0), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1)),
        ((0, 0), (1, 0), (1, 1), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2)),
        ((0, 0), (1, 0), (1, 1), (1, 2), (2, 2), (2, 1), (2, 0)),
        ((0, 0), (1, 0), (1, 1), (1, 2), (2, 2), (3, 2), (3, 1), (3, 0)),
        (
            (0, 0),
            (1, 0),
            (1, 1),
            (1, 2),
            (2, 2),
            (3, 2),
            (4, 2),
            (4, 1),
            (4, 0),
        ),
        (
            (0, 0),
            (1, 0),
            (1, 1),
            (1, 2),
            (2, 2),
            (3, 2),
            (4, 2),
            (4, 3),
            (5, 3),
        ),
        (
            (0, 0),
            (1, 0),
            (1, 1),
            (1, 2),
            (2, 2),
            (3, 2),
            (4, 2),
            (4, 3),
            (4, 4),
            (4, 5),
        ),
        (
            (0, 0),
            (1, 0),
            (1, 1),
            (1, 2),
            (2, 2),
            (3, 2),
            (4, 2),
            (4, 3),
            (4, 4),
            (5, 4),
        ),
        (
            (0, 0),
            (1, 0),
            (1, 1),
            (1, 2),
            (2, 2),
            (3, 2),
            (4, 2),
            (4, 3),
            (4, 4),
            (3, 4),
            (3, 5),
        ),
        (
            (0, 0),
            (1, 0),
            (1, 1),
            (1, 2),
            (2, 2),
            (3, 2),
            (4, 2),
            (4, 3),
            (4, 4),
            (3, 4),
            (2, 4),
            (2, 5),
        ),
        (
            (0, 0),
            (1, 0),
            (1, 1),
            (1, 2),
            (2, 2),
            (3, 2),
            (4, 2),
            (4, 3),
            (4, 4),
            (3, 4),
            (2, 4),
            (1, 4),
            (1, 5),
        ),
        (
            (0, 0),
            (1, 0),
            (1, 1),
            (1, 2),
            (2, 2),
            (3, 2),
            (4, 2),
            (4, 3),
            (4, 4),
            (3, 4),
            (2, 4),
            (1, 4),
            (0, 4),
            (0, 5),
        ),
    ]
    self.assertLen(path_tuples, 14)
    for i, path in enumerate(expected_paths):
      with self.subTest(f'path_{i}'):
        self.assertIn(path, path_tuples)


class HuggingRiverGeneratorTest(parameterized.TestCase):

  def testGenerateHuggingRiverCandidatesSimple(self):
    grid = np.zeros((3, 3), dtype=bool)
    grid[0, 0] = True
    rivers = list(
        hugging_river_generator.generate_hugging_river_candidates(
            grid_size=3,
            width=1,
            occupancy_grid=grid,
            start_cell=(0, 1),
            hug_side=river_lib.HugSide.RIGHT,
        )
    )
    paths = set(tuple(r.path) for r in rivers)
    for path in paths:
      for i in range(len(path) - 1):
        self.assertEqual(
            abs(path[i][0] - path[i + 1][0]) + abs(path[i][1] - path[i + 1][1]),
            1,
            msg=f'Diagonal move in path {path}',
        )
    self.assertLen(rivers, 5)
    self.assertIn(((0, 1), (1, 1), (1, 0)), paths)
    self.assertIn(((0, 1), (1, 1), (1, 0), (2, 0)), paths)

  @parameterized.named_parameters(
      dict(
          testcase_name='start_top_border',
          obstacle_slice=(slice(0, 2), slice(0, 2)),
          start_cell=(0, 2),
          hug_side=river_lib.HugSide.RIGHT,
          num_paths=7,
      ),
      dict(
          testcase_name='start_left_border',
          obstacle_slice=(slice(0, 2), slice(0, 2)),
          start_cell=(2, 0),
          hug_side=river_lib.HugSide.LEFT,
          num_paths=7,
      ),
      dict(
          testcase_name='start_bottom_border',
          obstacle_slice=(slice(2, 4), slice(2, 4)),
          start_cell=(3, 1),
          hug_side=river_lib.HugSide.RIGHT,
          num_paths=7,
      ),
      dict(
          testcase_name='start_right_border',
          obstacle_slice=(slice(0, 2), slice(2, 4)),
          start_cell=(0, 1),
          hug_side=river_lib.HugSide.LEFT,
          num_paths=7,
      ),
  )
  def test_generate_hugging_river_candidates_2x2obstacle(
      self, obstacle_slice, start_cell, hug_side, num_paths
  ):
    grid = np.zeros((4, 4), dtype=bool)
    grid[obstacle_slice] = True
    rivers = list(
        hugging_river_generator.generate_hugging_river_candidates(
            grid_size=4,
            width=1,
            occupancy_grid=grid,
            start_cell=start_cell,
            hug_side=hug_side,
        )
    )
    paths = set(tuple(r.path) for r in rivers)
    self.assertLen(paths, num_paths)
    standard_river = river_lib.HuggingRiver.from_contour(
        grid_size=4,
        width=1,
        occupancy_grid=grid,
        start_cell=start_cell,
        hug_side=hug_side,
    )
    self.assertIn(tuple(standard_river.path), paths)

  def test_generate_hugging_river_candidates_width2(self):
    grid = np.zeros((10, 10), dtype=bool)
    grid[0:3, 0:3] = True
    rivers = list(
        hugging_river_generator.generate_hugging_river_candidates(
            grid_size=10,
            width=2,
            occupancy_grid=grid,
            start_cell=(0, 3),
            hug_side=river_lib.HugSide.RIGHT,
        )
    )
    self.assertLen(rivers, 8)
    for river in rivers:
      self.assertEqual(river.width, 2)
      self.assertLen(river.subriver_paths, 2)

    generated_paths = set(
        tuple(tuple(p) for p in r.subriver_paths) for r in rivers
    )
    expected_paths = set([
        (
            ((0, 3), (1, 3), (2, 3), (3, 3), (3, 2), (3, 1), (3, 0)),
            (
                (0, 4),
                (1, 4),
                (2, 4),
                (3, 4),
                (4, 4),
                (4, 3),
                (4, 2),
                (4, 1),
                (4, 0),
            ),
        ),
        (
            (
                (0, 3),
                (1, 3),
                (2, 3),
                (3, 3),
                (4, 3),
                (5, 3),
                (6, 3),
                (7, 3),
                (8, 3),
                (9, 3),
            ),
            (
                (0, 4),
                (1, 4),
                (2, 4),
                (3, 4),
                (4, 4),
                (5, 4),
                (6, 4),
                (7, 4),
                (8, 4),
                (9, 4),
            ),
        ),
        (
            ((0, 3), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9)),
            ((0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9)),
        ),
        (
            (
                (0, 3),
                (1, 3),
                (2, 3),
                (2, 4),
                (2, 5),
                (2, 6),
                (2, 7),
                (2, 8),
                (2, 9),
            ),
            ((0, 4), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9)),
        ),
        (
            (
                (0, 3),
                (1, 3),
                (2, 3),
                (3, 3),
                (3, 4),
                (3, 5),
                (3, 6),
                (3, 7),
                (3, 8),
                (3, 9),
            ),
            ((0, 4), (1, 4), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9)),
        ),
        (
            (
                (0, 3),
                (1, 3),
                (2, 3),
                (3, 3),
                (3, 2),
                (4, 2),
                (5, 2),
                (6, 2),
                (7, 2),
                (8, 2),
                (9, 2),
            ),
            (
                (0, 4),
                (1, 4),
                (2, 4),
                (3, 4),
                (4, 4),
                (4, 3),
                (5, 3),
                (6, 3),
                (7, 3),
                (8, 3),
                (9, 3),
            ),
        ),
        (
            (
                (0, 3),
                (1, 3),
                (2, 3),
                (3, 3),
                (3, 2),
                (3, 1),
                (4, 1),
                (5, 1),
                (6, 1),
                (7, 1),
                (8, 1),
                (9, 1),
            ),
            (
                (0, 4),
                (1, 4),
                (2, 4),
                (3, 4),
                (4, 4),
                (4, 3),
                (4, 2),
                (5, 2),
                (6, 2),
                (7, 2),
                (8, 2),
                (9, 2),
            ),
        ),
        (
            (
                (0, 3),
                (1, 3),
                (2, 3),
                (3, 3),
                (3, 2),
                (3, 1),
                (3, 0),
                (4, 0),
                (5, 0),
                (6, 0),
                (7, 0),
                (8, 0),
                (9, 0),
            ),
            (
                (0, 4),
                (1, 4),
                (2, 4),
                (3, 4),
                (4, 4),
                (4, 3),
                (4, 2),
                (4, 1),
                (5, 1),
                (6, 1),
                (7, 1),
                (8, 1),
                (9, 1),
            ),
        ),
    ])
    self.assertEqual(generated_paths, expected_paths)

  def test_generate_hugging_river_candidates_width3_offgrid_fallback(self):
    grid = np.zeros((10, 10), dtype=bool)
    grid[1:5, 0:4] = True
    rivers = list(
        hugging_river_generator.generate_hugging_river_candidates(
            grid_size=10,
            width=3,
            occupancy_grid=grid,
            start_cell=(0, 0),
            hug_side=river_lib.HugSide.LEFT,
            allow_off_grid=True,
            area_reqs={'side_a': 16.0, 'side_b': 0.0},
        )
    )
    self.assertNotEmpty(rivers)
    for river in rivers:
      self.assertEqual(river.width, 3)
      self.assertLen(river.subriver_paths, 3)
      for path in river.subriver_paths:
        for y, x in path:
          self.assertGreaterEqual(y, 0)
          self.assertGreaterEqual(x, 0)
          self.assertLess(y, 10)
          self.assertLess(x, 10)


if __name__ == '__main__':
  absltest.main()
