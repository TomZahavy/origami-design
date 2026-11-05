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

import json

from absl.testing import absltest
from bp_pipeline import rectangle as shaping_utils
from bp_pipeline.crease_pattern import crease as crease_lib
from bp_pipeline.crease_pattern import crease_pattern as crease_pattern_lib
from bp_pipeline.crease_pattern import point
from bp_pipeline.packing import config as config_lib
from bp_pipeline.packing import packing_output
from bp_pipeline.packing import river as river_lib
from bp_pipeline.packing import types
from bp_pipeline.packing import utils_tracker
from bp_pipeline.packing.debug import debug_types
from bp_pipeline.stick_figures import stick as stick_lib
from bp_pipeline.stick_figures import stick_figure as stick_figure_lib
import numpy as np


class NumpyEncoderTest(absltest.TestCase):

  def test_numpy_encoder(self):
    data = {
        'int64': np.int64(42),
        'float64': np.float64(3.14),
        'array': np.array([1, 2, 3]),
        'int': 10,
        'float': 2.0,
        'list': [4, 5],
    }
    expected_dict = {
        'int64': 42,
        'float64': 3.14,
        'array': [1, 2, 3],
        'int': 10,
        'float': 2.0,
        'list': [4, 5],
    }

    result = json.dumps(data, cls=packing_output.NumpyEncoder)
    self.assertEqual(json.loads(result), expected_dict)


class PackingOutputTest(absltest.TestCase):

  def test_asdict_is_json_serializable(self):
    """Tests that the output of asdict() is JSON serializable."""
    rect1 = shaping_utils.Rectangle(
        name='flap1',
        x_start=0,
        y_start=0,
        x_len=1,
        y_len=1,
        circle_centers=[point.Point(x=0.5, y=0.5, require_on_paper=False)],
    )
    river1 = river_lib.River(
        width=1,
        offset=1,
        orientation=river_lib.RiverOrientation.HORIZONTAL,
        grid_size=16,
    )
    hinge1 = types.HingeInfo(
        coordinate=crease_lib.Crease(
            p1_init=point.Point(x=0, y=0, require_on_paper=False),
            p2_init=point.Point(x=1, y=1, require_on_paper=False),
            fold=crease_lib.Fold.HINGE,
        ),
        assigned=True,
        flap_names=('flap1', 'river1'),
    )
    details: debug_types.TilingDetails = {
        'grid_size': 16,
        'is_symmetric': False,
        'unused_area': 0,
        'perfect_tiling_found': True,
    }
    config = config_lib.PackingConfig()
    output = packing_output.PackingOutput(
        success=True,
        packing_cp=None,
        stick_figure=None,
        tracker=None,
        flap_rectangles=[rect1],
        packing_rivers={'river1': river1},
        hinges=[hinge1],
        details=details,
        config=config,
    )

    output_dict = output.asdict()

    try:
      json_str = json.dumps(output_dict)
      self.assertIsInstance(json_str, str)
    except TypeError as e:
      self.fail(f'asdict() output is not JSON serializable: {e}')

    self.assertTrue(output_dict['success'])
    self.assertEqual(output_dict['details'], details)
    self.assertEqual(output_dict['config']['type'], 'PackingConfig')

    self.assertEqual(
        output_dict['flap_rectangles'],
        [{
            'name': 'flap1',
            'bounds': [0, 0, 1, 1],
            'circle_centers': [0.5, 0.5],
        }],
    )
    self.assertEqual(
        output_dict['packing_rivers'],
        {
            'river1': {
                'name': 'river1',
                'rectangles': [{
                    'name': '',
                    'bounds': [0, 1, 16, 1],
                    'circle_centers': [],
                }],
                'river_type': 'straight',
                'width': 1,
                'offset': 1,
                'orientation': 'horizontal',
                'grid_size': 16,
            }
        },
    )
    self.assertEqual(
        output_dict['hinges'],
        [{
            'coordinate': {
                'p1': {'x': 0.0, 'y': 0.0, 'require_on_paper': False},
                'p2': {'x': 1.0, 'y': 1.0, 'require_on_paper': False},
                'fold': 7,
                'fold_percent': 1.0,
                'fold_step': 0,
            },
            'assigned': True,
            'flap_names': ['flap1', 'river1'],
        }],
    )

  def test_sacrificial_flaps_serialization(self):
    placement1 = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=4
    )
    placement2 = types.PolygonPlacement.from_grid_coords(
        offset=(2, 0), size=(2, 2), grid_size=4
    )
    sf = types.SacrificialFlap.from_flap_placement(
        polygon_name='sf1',
        placement=placement1,
        shifted_element_name='base',
        orientation='vertical',
        main_placement=placement2,
    )
    output = packing_output.PackingOutput(
        success=True,
        sacrificial_flaps=[sf],
    )
    output_dict = output.asdict()
    self.assertIn('sacrificial_flaps', output_dict)
    self.assertIsInstance(output_dict['sacrificial_flaps'], list)
    sf_list_from_dict = output_dict['sacrificial_flaps']
    self.assertLen(sf_list_from_dict, 1)
    self.assertEqual(sf_list_from_dict[0]['polygon_name'], 'sf1')

  def test_corner_sacrificial_flap_serialization(self):
    corner_placement = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(2, 2), grid_size=4
    )
    main_placement = types.PolygonPlacement.from_grid_coords(
        offset=(2, 2), size=(2, 2), grid_size=4
    )
    sf = types.SacrificialFlap.from_flap_placement(
        polygon_name='f1__corner',
        placement=corner_placement,
        shifted_element_name='f1',
        orientation='corner',
        main_placement=main_placement,
    )
    self.assertTrue(sf.is_corner)
    self.assertEqual(sf.crimp_direction, 'bottom_right')

    output = packing_output.PackingOutput(
        success=True,
        sacrificial_flaps=[sf],
    )
    unpacked = json.loads(json.dumps(output.asdict()))
    sf_list = unpacked['sacrificial_flaps']
    self.assertLen(sf_list, 1)
    reconstructed = types.SacrificialFlap.from_dict(sf_list[0])
    self.assertEqual(reconstructed, sf)


class ValidatePackingOutputTest(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.grid_size = 4
    self.stick_figure = stick_figure_lib.StickFigure(
        name='test',
        category='test',
        complexity=1,
        root='s1',
        children=[
            stick_lib.Stick(
                name='s1', start='a', end='b', azimuth_angle=0, length=2
            )
        ],
    )
    self.tracker = utils_tracker.CreasePatternTracker(self.grid_size)
    self.tracker.add_polygon(
        's1',
        types.PolygonPlacement.from_grid_coords(
            offset=(0, 0), size=(4, 4), grid_size=self.grid_size
        ),
    )
    self.details = debug_types.TilingDetails(
        grid_size=self.grid_size,
        is_symmetric=False,
        perfect_tiling_found=True,
        unused_area=0,
    )
    self.cp = crease_pattern_lib.CreasePattern([], is_empty=True)
    self.hinges = []
    self.packing_output = packing_output.PackingOutput(
        success=True,
        packing_cp=self.cp,
        flap_rectangles=[],
        packing_rivers=dict(),
        stick_figure=self.stick_figure,
        details=self.details,
        hinges=self.hinges,
        tracker=self.tracker,
    )

  def test_valid_packing_output_passes(self):
    try:
      self.packing_output.validate()
    except packing_output.PackingValidationError as e:
      self.fail(f'validate() raised PackingError: {e}')

  def test_imperfect_tiling_fails(self):
    self.details['perfect_tiling_found'] = False
    packing = packing_output.PackingOutput(
        success=True,
        packing_cp=self.cp,
        flap_rectangles=[],
        packing_rivers=dict(),
        stick_figure=self.stick_figure,
        details=self.details,
        hinges=self.hinges,
        tracker=self.tracker,
    )
    with self.assertRaisesRegex(
        packing_output.PackingValidationError,
        'perfect_tiling_found is not True',
    ):
      packing.validate()

  def test_non_zero_unused_area_fails(self):
    self.details['unused_area'] = 1
    packing = packing_output.PackingOutput(
        success=True,
        packing_cp=self.cp,
        flap_rectangles=[],
        packing_rivers=dict(),
        stick_figure=self.stick_figure,
        details=self.details,
        hinges=self.hinges,
        tracker=self.tracker,
    )
    with self.assertRaisesRegex(
        packing_output.PackingValidationError, 'unused_area is not 0'
    ):
      packing.validate()

  def test_missing_stick_fails(self):
    stick_figure = stick_figure_lib.StickFigure(
        name='test',
        category='test',
        complexity=1,
        root='s1',
        children=[
            stick_lib.Stick(
                name='s1', start='a', end='b', azimuth_angle=0, length=1
            ),
            stick_lib.Stick(
                name='s2', start='b', end='c', azimuth_angle=0, length=1
            ),
        ],
    )
    packing = packing_output.PackingOutput(
        success=True,
        packing_cp=self.cp,
        flap_rectangles=[],
        packing_rivers=dict(),
        stick_figure=stick_figure,
        details=self.details,
        hinges=self.hinges,
        tracker=self.tracker,
    )
    with self.assertRaisesRegex(
        packing_output.PackingValidationError,
        'Stick s2 from stick figure not found',
    ):
      packing.validate()

  def test_missing_cp_fails(self):
    packing = packing_output.PackingOutput(
        success=True,
        packing_cp=None,
        flap_rectangles=[],
        packing_rivers=dict(),
        stick_figure=self.stick_figure,
        details=self.details,
        hinges=self.hinges,
        tracker=self.tracker,
    )
    with self.assertRaisesRegex(
        packing_output.PackingValidationError, 'packing_cp is None'
    ):
      packing.validate()

  def test_missing_hinges_fails(self):
    packing = packing_output.PackingOutput(
        success=True,
        packing_cp=self.cp,
        flap_rectangles=[],
        packing_rivers=dict(),
        stick_figure=self.stick_figure,
        details=self.details,
        hinges=None,
        tracker=self.tracker,
    )
    with self.assertRaisesRegex(
        packing_output.PackingValidationError, 'hinges is None'
    ):
      packing.validate()


if __name__ == '__main__':
  absltest.main()
