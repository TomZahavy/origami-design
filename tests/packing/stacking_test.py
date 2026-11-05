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

"""Tests for the stacking packing module."""

from unittest import mock

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.packing import stacking
from bp_pipeline.packing import utils_tracker
from bp_pipeline.stick_figures import stick_figure as sf_lib
from bp_pipeline.stick_figures.examples import example_trees

# The default traversal for this stick figure starts with a river.
DEER = sf_lib.StickFigure.from_json(
    """{"name": "A deer resting in tall grass, ears twitching.", "category": "Mammals", "color_top": [160, 82, 45], "color_bottom": [222, 184, 135], "complexity": 2, "root": "spine", "children": [{"name": "spine", "start": "mid_body", "end": "front_shoulder", "azimuth_angle": 0, "elevation_angle": 0.0, "length": 4, "width": 2.0, "shaping_flap": false}, {"name": "pelvis", "start": "mid_body", "end": "hips", "azimuth_angle": 180, "elevation_angle": 0.0, "length": 3, "width": 2.0, "shaping_flap": false}, {"name": "neck", "start": "front_shoulder", "end": "head_base", "azimuth_angle": 315, "elevation_angle": 8.0, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "f_l_leg", "start": "front_shoulder", "end": "f_l_knee", "azimuth_angle": 270, "elevation_angle": 8.0, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "f_r_leg", "start": "front_shoulder", "end": "f_r_knee", "azimuth_angle": 90, "elevation_angle": 8.0, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "b_l_leg", "start": "hips", "end": "b_l_knee", "azimuth_angle": 225, "elevation_angle": 16.0, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "b_r_leg", "start": "hips", "end": "b_r_knee", "azimuth_angle": 135, "elevation_angle": 16.0, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "head", "start": "head_base", "end": "nose", "azimuth_angle": 315, "elevation_angle": 8.0, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "l_ear", "start": "head_base", "end": "l_tip", "azimuth_angle": 270, "elevation_angle": 8.0, "length": 1, "width": 1.0, "shaping_flap": false}, {"name": "r_ear", "start": "head_base", "end": "r_tip", "azimuth_angle": 0, "elevation_angle": 8.0, "length": 1, "width": 1.0, "shaping_flap": false}, {"name": "grass_1", "start": "mid_body", "end": "g1", "azimuth_angle": 280, "elevation_angle": 8.0, "length": 5, "width": 1.0, "shaping_flap": false}, {"name": "grass_2", "start": "hips", "end": "g2", "azimuth_angle": 160, "elevation_angle": 0.0, "length": 6, "width": 1.0, "shaping_flap": false}, {"name": "grass_3", "start": "front_shoulder", "end": "g3", "azimuth_angle": 80, "elevation_angle": 16.0, "length": 4, "width": 1.0, "shaping_flap": false}], "views": []}"""
)


BABY_ELEPHANT = sf_lib.StickFigure.from_json(
    '{"name": "A baby elephant splashing water with its trunk playfully.",'
    ' "category": "Mammals", "color_top": [173, 216, 230], "color_bottom":'
    ' [140, 140, 150], "complexity": 3, "root": "body_core", "children":'
    ' [{"name": "body_core", "start": "hips", "end": "shoulders",'
    ' "azimuth_angle": 0, "elevation_angle": 0.0, "length": 5, "width": 2,'
    ' "shaping_flap": false}, {"name": "neck_to_head", "start": "shoulders",'
    ' "end": "head_base", "azimuth_angle": 0, "elevation_angle": 0.0,'
    ' "length": 2, "width": 2, "shaping_flap": false}, {"name":'
    ' "trunk_lower_trunk_upper", "start": "head_base", "end": "trunk_tip",'
    ' "azimuth_angle": -0.0, "elevation_angle": 0.0, "length": 6, "width": 2,'
    ' "shaping_flap": false}, {"name": "water_jet_main", "start": "trunk_tip",'
    ' "end": "water_peak", "azimuth_angle": 0, "elevation_angle": 70,'
    ' "length": 2, "width": 1.0, "shaping_flap": false}, {"name":'
    ' "water_spray_left", "start": "trunk_tip", "end": "water_l",'
    ' "azimuth_angle": 45, "elevation_angle": 45, "length": 1, "width": 1.0,'
    ' "shaping_flap": false}, {"name": "water_spray_right", "start":'
    ' "trunk_tip", "end": "water_r", "azimuth_angle": -45, "elevation_angle":'
    ' 45, "length": 1, "width": 1.0, "shaping_flap": false}, {"name":'
    ' "ear_left_main", "start": "head_base", "end": "ear_l_tip",'
    ' "azimuth_angle": 95, "elevation_angle": 10, "length": 3, "width": 1.0,'
    ' "shaping_flap": false}, {"name": "ear_right_main", "start": "head_base",'
    ' "end": "ear_r_tip", "azimuth_angle": -95, "elevation_angle": 10,'
    ' "length": 3, "width": 1.0, "shaping_flap": false}, {"name":'
    ' "front_leg_left", "start": "shoulders", "end": "foot_fl",'
    ' "azimuth_angle": 110, "elevation_angle": -75, "length": 3, "width": 2,'
    ' "shaping_flap": false}, {"name": "front_leg_right", "start":'
    ' "shoulders", "end": "foot_fr", "azimuth_angle": -110,'
    ' "elevation_angle": -75, "length": 3, "width": 2, "shaping_flap":'
    ' false}, {"name": "rear_leg_left", "start": "hips", "end": "foot_rl",'
    ' "azimuth_angle": 130, "elevation_angle": -80, "length": 3, "width": 2,'
    ' "shaping_flap": false}, {"name": "rear_leg_right", "start": "hips",'
    ' "end": "foot_rr", "azimuth_angle": -130, "elevation_angle": -80,'
    ' "length": 3, "width": 2, "shaping_flap": false}, {"name":'
    ' "playful_tail", "start": "hips", "end": "tail_tip", "azimuth_angle":'
    ' 180, "elevation_angle": 40, "length": 2, "width": 1.0, "shaping_flap":'
    ' false}], "views": []}'
)


class PackStickFigureTest(parameterized.TestCase):

  def _check_tracker(
      self,
      stick_figure: sf_lib.StickFigure,
      tracker: utils_tracker.CreasePatternTracker,
  ):
    self.assertTrue(tracker.occupancy_grid.all(), 'Occupancy grid is not full.')

    for stick in stick_figure.children:
      if stick.is_river:
        self.assertIn(stick.name, tracker.packed_rivers)
        self.assertEqual(stick.length, tracker.packed_rivers[stick.name].width)
      else:
        self.assertIn(stick.name, tracker.packed_polygons)
        self.assertEqual(
            min(tracker.packed_polygons[stick.name].size), 2 * stick.length
        )

  def _check_symmetric_tracker(
      self,
      stick_figure: sf_lib.StickFigure,
      tracker: utils_tracker.CreasePatternTracker,
  ):
    for stick in stick_figure.children:
      sym_name = stick.symmetric_stick_name
      if stick.is_river:
        self.assertIn(stick.name, tracker.packed_rivers)
        river = tracker.packed_rivers[stick.name]
        if sym_name is None:
          self.assertTrue(stick.is_on_symmetry_axis)
          continue
        self.assertIn(sym_name, tracker.packed_rivers)
        mirror = tracker.packed_rivers[sym_name]
        self.assertEqual(river.width, mirror.width)
        self.assertEqual(river.start_cell[0], mirror.start_cell[0])
      else:
        self.assertIn(stick.name, tracker.packed_polygons)
        placement = tracker.packed_polygons[stick.name]
        if sym_name is None:
          self.assertTrue(stick.is_on_symmetry_axis)
          self.assertEqual(placement.center.x, 0.5)
          continue
        self.assertIn(sym_name, tracker.packed_polygons)
        mirror = tracker.packed_polygons[sym_name]
        self.assertEqual(placement.size, mirror.size)
        self.assertEqual(placement.offset[1], mirror.offset[1])
        self.assertAlmostEqual(
            placement.center.x + mirror.center.x,
            1.0,
            msg=f'{stick.name} center not mirrored',
        )

  @parameterized.parameters([
      example_trees.HUMAN_SIMPLE,
      example_trees.SPIDER_SIMPLE,
      example_trees.CAT_SIMPLE,
      DEER,
  ])
  def test_pack_stick_figure(self, stick_figure):
    tracker, _ = stacking._create_tracker_with_stacking(
        stick_figure, force_asymmetric=True
    )
    self._check_tracker(stick_figure, tracker)

  @parameterized.parameters([
      example_trees.HUMAN_SIMPLE,
      example_trees.GOALIE_3D,
  ])
  def test_pack_symmetric_stick_figure(self, stick_figure):
    self.assertTrue(stick_figure.is_symmetric_tree)
    tracker, _ = stacking._create_tracker_with_stacking(stick_figure)
    self._check_tracker(stick_figure, tracker)
    self._check_symmetric_tracker(stick_figure, tracker)

  @parameterized.parameters([
      example_trees.SPIDER_MONKEY,
  ])
  def test_pack_symmetric_stick_figure_requires_straightening(
      self, stick_figure
  ):
    with self.subTest('no_straightening_fail'):
      with mock.patch.object(
          sf_lib.StickFigure,
          'straighten_symmetry_axis',
          side_effect=stick_figure,
      ):
        with self.assertRaises((ValueError, KeyError)):
          stacking._create_tracker_with_stacking(stick_figure)

    self.assertTrue(stick_figure.is_symmetric_tree)
    with self.subTest('default_straightening_pass'):
      tracker, _ = stacking._create_tracker_with_stacking(stick_figure)
      self._check_tracker(stick_figure, tracker)
      self._check_symmetric_tracker(stick_figure, tracker)

  @parameterized.parameters([example_trees.HAMMERHEAD_SHARK])
  def test_pack_symmetric_stick_figure_branched_axis(self, stick_figure):
    with self.assertRaises(ValueError):
      stacking._create_tracker_with_stacking(stick_figure)


class IdentifySymmetricTraversalBoundsTest(parameterized.TestCase):

  @parameterized.parameters([
      (BABY_ELEPHANT, 'water_jet_main', 'playful_tail'),
      (example_trees.AMERICAN_LOBSTER, 'rostrum', 'tail_fan_center'),
  ])
  def test_identify_symmetric_traversal_bounds(
      self, sf, expected_start, expected_end
  ):
    self.assertTrue(sf.is_symmetric_tree)
    start_stick, end_stick = stacking._identify_symmetric_traversal_bounds(sf)
    self.assertEqual(start_stick.name, expected_start)
    self.assertEqual(end_stick.name, expected_end)

  @parameterized.parameters([
      BABY_ELEPHANT,
      example_trees.AMERICAN_LOBSTER,
  ])
  def test_elephant_symmetric_packing(self, sf):
    tracker, _ = stacking._create_tracker_with_stacking(sf)
    self.assertTrue(tracker.occupancy_grid.all(), 'Occupancy grid is not full.')


class TraversalTest(parameterized.TestCase):

  def test_asymmetric_traversal(self):
    sf = example_trees.AMERICAN_LOBSTER
    layout = stacking._AsymmetricStackLayout(
        config=stacking.StackLayoutConfig()
    )
    layout.compute_from_sf_traversal(sf)
    sticks = [s.name for s in layout._sticks]
    self.assertEqual(
        sticks,
        [
            'tail_fan_right',
            'tail_fan_center',
            'tail_fan_left',
            'abdomen',
            'walking_leg_4R',
            'walking_leg_2R',
            'walking_leg_1R',
            'cephalothorax',
            'walking_leg_3R',
            'right_arm',
            'right_dactyl',
            'right_pincer_claw',
            'right_arm',
            'antenna_R',
            'rostrum',
            'antenna_L',
            'left_arm',
            'left_crusher_claw',
            'left_dactyl',
            'left_arm',
            'walking_leg_3L',
            'cephalothorax',
            'walking_leg_1L',
            'walking_leg_2L',
            'walking_leg_4L',
            'abdomen',
        ],
    )

  def test_symmetric_traversal(self):
    sf = example_trees.AMERICAN_LOBSTER
    layout = stacking._SymmetricStackLayout(config=stacking.StackLayoutConfig())
    layout.compute_from_sf_traversal(sf)
    sticks = [s.name for s in layout._sticks]
    self.assertEqual(
        sticks,
        [
            'rostrum',
            'antenna_L',
            'left_arm',
            'left_crusher_claw',
            'left_dactyl',
            'left_arm',
            'walking_leg_3L',
            'cephalothorax',
            'walking_leg_1L',
            'walking_leg_2L',
            'walking_leg_4L',
            'abdomen',
            'tail_fan_right',
            'tail_fan_center',
        ],
    )


if __name__ == '__main__':
  absltest.main()
