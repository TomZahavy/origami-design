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
from bp_pipeline import rectangle as shaping_utils
from bp_pipeline.packing import river as river_lib
from bp_pipeline.packing import river_adjacency
from bp_pipeline.packing import utils_tracker
from bp_pipeline.stick_figures import stick as stick_lib
from bp_pipeline.stick_figures import stick_figure as stick_figure_lib


class RiverAdjacencyUtilsTest(absltest.TestCase):

  def test_rects_adjacent(self):
    r1 = shaping_utils.Rectangle(
        x_start=0.0,
        y_start=0.0,
        x_len=2.0,
        y_len=2.0,
        name='r1',
        require_on_paper=False,
        circle_centers=None,
    )
    r2 = shaping_utils.Rectangle(
        x_start=2.0,
        y_start=0.0,
        x_len=2.0,
        y_len=2.0,
        name='r2',
        require_on_paper=False,
        circle_centers=None,
    )
    r3 = shaping_utils.Rectangle(
        x_start=0.0,
        y_start=2.0,
        x_len=2.0,
        y_len=2.0,
        name='r3',
        require_on_paper=False,
        circle_centers=None,
    )
    r4 = shaping_utils.Rectangle(
        x_start=3.0,
        y_start=3.0,
        x_len=1.0,
        y_len=1.0,
        name='r4',
        require_on_paper=False,
        circle_centers=None,
    )
    r5 = shaping_utils.Rectangle(
        x_start=2.0,
        y_start=2.5,
        x_len=2.0,
        y_len=2.0,
        name='r5',
        require_on_paper=False,
        circle_centers=None,
    )
    r6 = shaping_utils.Rectangle(
        x_start=0.0,
        y_start=2.0,
        x_len=1.0,
        y_len=1.0,
        name='r6',
        require_on_paper=False,
        circle_centers=None,
    )
    self.assertTrue(river_adjacency.rects_adjacent(r1, r2))
    self.assertTrue(river_adjacency.rects_adjacent(r2, r1))
    self.assertTrue(river_adjacency.rects_adjacent(r1, r3))
    self.assertTrue(river_adjacency.rects_adjacent(r3, r1))
    self.assertFalse(river_adjacency.rects_adjacent(r1, r4))
    self.assertFalse(river_adjacency.rects_adjacent(r1, r5))
    self.assertTrue(river_adjacency.rects_adjacent(r1, r6))
    self.assertTrue(river_adjacency.rects_adjacent(r6, r1))

  def test_are_rivers_geometrically_adjacent(self):
    r1 = river_lib.River(2, 0, river_lib.RiverOrientation.HORIZONTAL, 10)
    r2 = river_lib.River(2, 2, river_lib.RiverOrientation.HORIZONTAL, 10)
    r3 = river_lib.River(2, 5, river_lib.RiverOrientation.HORIZONTAL, 10)
    self.assertTrue(river_adjacency.are_rivers_geometrically_adjacent(r1, r2))
    self.assertFalse(river_adjacency.are_rivers_geometrically_adjacent(r1, r3))

  def test_share_joint_with_no_sticks_between(self):
    s1 = stick_lib.Stick(
        name='s1', start='j1', end='j2', length=1, azimuth_angle=0.0
    )
    s2 = stick_lib.Stick(
        name='s2', start='j2', end='j3', length=1, azimuth_angle=90.0
    )
    s3 = stick_lib.Stick(
        name='s3', start='j2', end='j4', length=1, azimuth_angle=270.0
    )
    s4 = stick_lib.Stick(
        name='s4', start='j5', end='j6', length=1, azimuth_angle=0.0
    )
    sf = stick_figure_lib.StickFigure(
        name='test',
        category='test',
        complexity=1,
        root='s1',
        children=[s1, s2, s3, s4],
    )
    self.assertTrue(
        river_adjacency.share_joint_with_no_sticks_between(s1, s2, sf)
    )
    self.assertTrue(
        river_adjacency.share_joint_with_no_sticks_between(s1, s3, sf)
    )
    self.assertFalse(
        river_adjacency.share_joint_with_no_sticks_between(s1, s4, sf)
    )

  def test_get_adjacent_river_constraints_horizontal(self):
    s1 = stick_lib.Stick(
        name='s1', start='j1', end='j2', length=1, azimuth_angle=0.0
    )
    s2 = stick_lib.Stick(
        name='s2', start='j2', end='j3', length=1, azimuth_angle=90.0
    )
    sf = stick_figure_lib.StickFigure(
        name='test',
        category='test',
        complexity=1,
        root='s1',
        children=[s1, s2],
    )
    grid_size = 5
    tracker = utils_tracker.CreasePatternTracker(grid_size)
    placed_river1 = river_lib.River(
        1, 0, river_lib.RiverOrientation.HORIZONTAL, grid_size
    )
    tracker.add_river('s1', placed_river1)
    river2 = river_lib.River(
        1, 1, river_lib.RiverOrientation.HORIZONTAL, grid_size
    )
    constraints = river_adjacency.get_adjacent_river_constraints(
        river2, s2, tracker, sf
    )
    self.assertEqual(constraints, {'j2': river_adjacency.Side.BOTTOM})

  def test_get_adjacent_river_constraints_vertical(self):
    s1 = stick_lib.Stick(
        name='s1', start='j1', end='j2', length=1, azimuth_angle=0.0
    )
    s2 = stick_lib.Stick(
        name='s2', start='j2', end='j3', length=1, azimuth_angle=90.0
    )
    sf = stick_figure_lib.StickFigure(
        name='test',
        category='test',
        complexity=1,
        root='s1',
        children=[s1, s2],
    )
    grid_size = 5
    tracker = utils_tracker.CreasePatternTracker(grid_size)
    placed_river1 = river_lib.River(
        1, 0, river_lib.RiverOrientation.VERTICAL, grid_size
    )
    tracker.add_river('s1', placed_river1)
    river2 = river_lib.River(
        1, 1, river_lib.RiverOrientation.VERTICAL, grid_size
    )
    constraints = river_adjacency.get_adjacent_river_constraints(
        river2, s2, tracker, sf
    )
    self.assertEqual(constraints, {'j2': river_adjacency.Side.RIGHT})


if __name__ == '__main__':
  absltest.main()
