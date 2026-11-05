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
from bp_pipeline.packing import river as river_lib
from bp_pipeline.packing import types
from bp_pipeline.packing import utils_pack_river_flaps
from bp_pipeline.packing import utils_packing_flaps
from bp_pipeline.packing import utils_tracker
from bp_pipeline.stick_figures import stick as stick_lib
from bp_pipeline.stick_figures import stick_figure as stick_figure_lib
import numpy as np


class PackRiverFlapsTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.grid_size = 10
    self.flap1 = stick_lib.Stick(
        name='flap1', start='j1', end='j2', length=1, azimuth_angle=0.0
    )
    self.river1_stick = stick_lib.Stick(
        name='river1', start='j2', end='j3', length=1, azimuth_angle=0.0
    )
    self.river1_stick.is_river = True
    self.pocket = {
        'flap_names': {'flap1'},
        'flaps': [self.flap1],
        'boundary_rivers': {'river1'},
    }
    self.tracker = utils_tracker.CreasePatternTracker(self.grid_size)
    self.river = river_lib.River(
        1, 4, river_lib.RiverOrientation.HORIZONTAL, self.grid_size
    )
    self.tracker.add_river('river1', self.river)
    self.joint_to_side = {'j2': 'top', 'j3': 'bottom'}

    # manually setup river banks
    river_banks = []
    for i in range(self.grid_size):
      self.tracker.grid[3, i] = utils_packing_flaps.GridCellState(
          type=utils_packing_flaps.GridCellType.RIVER_ADJACENT, source_id='j2'
      )
      river_banks.append((3, i))
    for i in range(self.grid_size):
      self.tracker.grid[5, i] = utils_packing_flaps.GridCellState(
          type=utils_packing_flaps.GridCellType.RIVER_ADJACENT, source_id='j3'
      )
      river_banks.append((5, i))
    self.tracker.river_banks['river1'] = river_banks

  def test_get_pocket_mask_and_cells_horizontal_river(self):
    pocket_mask, pocket_river_adj_cells = (
        utils_pack_river_flaps.get_pocket_mask_and_cells(
            pocket=self.pocket,
            stick=self.river1_stick,
            river=self.river,
            grid_size=self.grid_size,
            joint_to_side=self.joint_to_side,
            tracker=self.tracker,
        )
    )

    self.assertIsNotNone(pocket_mask)
    self.assertEqual(pocket_mask.shape, (self.grid_size, self.grid_size))
    # Top mask should be true for rows 0,1,2,3
    for r in range(4):
      self.assertTrue(np.all(pocket_mask[r, :]))
    for r in range(4, self.grid_size):
      self.assertFalse(np.any(pocket_mask[r, :]))

    expected_adj_cells = [(3, i) for i in range(self.grid_size)]
    self.assertCountEqual(pocket_river_adj_cells, expected_adj_cells)

  def test_get_enclosed_pocket_mask(self):
    s1 = stick_lib.Stick(
        name='r1', start='j1', end='j2', length=1, azimuth_angle=0.0
    )
    s2 = stick_lib.Stick(
        name='r2', start='j2', end='j3', length=1, azimuth_angle=0.0
    )
    f1 = stick_lib.Stick(
        name='f1', start='j2', end='j4', length=1, azimuth_angle=0.0
    )
    tree = stick_figure_lib.StickFigure(
        name='test',
        children=[s1, s2, f1],
        root='r1',
        category='test',
        complexity=1,
    )
    pocket = {
        'flaps': [f1],
        'flap_names': {'f1'},
        'boundary_rivers': {'r1', 'r2'},
    }
    grid_size = 3

    river1 = river_lib.River(
        1, 1, river_lib.RiverOrientation.HORIZONTAL, grid_size
    )
    cand1 = {
        'stick_name': 'r1',
        'river': river1,
        'packed_flaps': {},
        'joint_to_side': {'j1': 'top', 'j2': 'bottom'},
    }
    frame1 = types.RiverStackFrame(
        step_index=0,
        iterator=iter([]),
        applied_candidate=cand1,
        object_ids=['r1'],
    )
    stack = [frame1]

    river2 = river_lib.River(
        1, 1, river_lib.RiverOrientation.VERTICAL, grid_size
    )
    cand2 = {
        'stick_name': 'r2',
        'river': river2,
        'packed_flaps': {},
        'joint_to_side': {'j2': 'left', 'j3': 'right'},
    }

    tracker_with_r1 = utils_tracker.CreasePatternTracker(grid_size)
    tracker_with_r1.add_river('r1', river1)

    mask = utils_pack_river_flaps.get_enclosed_pocket_mask(
        pocket, tracker_with_r1, tree, stack, cand2
    )

    expected_mask = np.array(
        [[False, False, False], [False, False, False], [True, False, False]],
        dtype=bool,
    )
    np.testing.assert_array_equal(mask, expected_mask)


if __name__ == '__main__':
  absltest.main()
