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

import copy
import re
from unittest import mock

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline import rectangle as shaping_utils
from bp_pipeline.crease_pattern import crease as crease_lib
from bp_pipeline.crease_pattern import point as point_lib
from bp_pipeline.crease_pattern import symmetry
from bp_pipeline.crease_pattern.parser import svg as svg_parser
from bp_pipeline.packing import river as river_lib
from bp_pipeline.packing import types
from bp_pipeline.packing import utils_packing_svg
from bp_pipeline.packing import utils_river_solver
from bp_pipeline.packing import utils_tracker
from bp_pipeline.packing.debug import debug_types
from bp_pipeline.stick_figures import stick as stick_lib
from bp_pipeline.stick_figures import stick_figure as stick_figure_lib
from bp_pipeline.stick_figures.examples import example_trees


class SvgGenerationTest(parameterized.TestCase):

  @parameterized.named_parameters(
      dict(
          testcase_name="horizontal_line_on_top_border",
          p1=(2.0, 0.0),
          p2=(8.0, 0.0),
          grid_size=10,
          expected=True,
      ),
      dict(
          testcase_name="horizontal_line_on_bottom_border",
          p1=(2.0, 10.0),
          p2=(8.0, 10.0),
          grid_size=10,
          expected=True,
      ),
      dict(
          testcase_name="vertical_line_on_left_border",
          p1=(0.0, 2.0),
          p2=(0.0, 8.0),
          grid_size=10,
          expected=True,
      ),
      dict(
          testcase_name="vertical_line_on_right_border",
          p1=(10.0, 2.0),
          p2=(10.0, 8.0),
          grid_size=10,
          expected=True,
      ),
      dict(
          testcase_name="internal_horizontal_line",
          p1=(2.0, 5.0),
          p2=(8.0, 5.0),
          grid_size=10,
          expected=False,
      ),
      dict(
          testcase_name="diagonal_line_is_not_on_border",
          p1=(0.0, 0.0),
          p2=(5.0, 5.0),
          grid_size=10,
          expected=False,
      ),
  )
  def test_filter_border_line(self, p1, p2, grid_size, expected):
    self.assertEqual(
        utils_packing_svg._filter_border_line(p1, p2, grid_size), expected
    )

  def test_convert_packing_to_svg(self):
    """Tests the main SVG function for correct structure and line counts."""
    tracker = utils_tracker.CreasePatternTracker(10)
    tracker.add_polygon(
        "p_center",
        types.PolygonPlacement.from_grid_coords(
            offset=(4, 4), size=(2, 2), grid_size=10
        ),
    )
    tracker.add_polygon(
        "p_edge",
        types.PolygonPlacement.from_grid_coords(
            offset=(8, 4), size=(2, 2), grid_size=10
        ),
    )

    svg_string = utils_packing_svg.convert_packing_to_svg(10, tracker)[0]

    self.assertTrue(svg_string.startswith("<svg"))
    self.assertTrue(svg_string.strip().endswith("</svg>"))
    self.assertIn('viewBox="0 0 10 10"', svg_string)

    green_lines = re.findall(r'<line stroke="green".*?/>', svg_string)
    red_lines = re.findall(r'<line stroke="red".*?/>', svg_string)

    self.assertLen(green_lines, 7)
    self.assertLen(red_lines, 5)

  def test_convert_packing_to_svg_with_overlapping_hinges(self):
    grid_size = 6
    tracker = utils_tracker.CreasePatternTracker(grid_size)
    tracker.add_polygon(
        "p1",
        types.PolygonPlacement.from_grid_coords(
            offset=(0, 0), size=(2, 4), grid_size=grid_size
        ),
    )
    tracker.add_polygon(
        "p2",
        types.PolygonPlacement.from_grid_coords(
            offset=(2, 2), size=(2, 4), grid_size=grid_size
        ),
    )
    svg_string = utils_packing_svg.convert_packing_to_svg(grid_size, tracker)[0]
    green_lines = re.findall(r'<line stroke="green".*?/>', svg_string)

    lines_at_x2 = []
    for l in green_lines:
      m = re.search(r'x1="([^"]+)" y1="([^"]+)" x2="([^"]+)" y2="([^"]+)"', l)
      if m:
        x1, y1, x2, y2 = map(float, m.groups())
        if abs(x1 - 2.0) < 1e-3 and abs(x2 - 2.0) < 1e-3:
          lines_at_x2.append(tuple(sorted((y1, y2))))

    self.assertLen(lines_at_x2, 1)
    y_coords = lines_at_x2[0]
    self.assertAlmostEqual(y_coords[0], 0.0)
    self.assertAlmostEqual(y_coords[1], 6.0)

  def test_convert_packing_to_svg_with_l_shape_river(self):
    grid_size = 5
    tracker = utils_tracker.CreasePatternTracker(grid_size)
    river = river_lib.LShapedRiver(
        width=1,
        grid_size=5,
        l_shape_type=river_lib.LShapeType.BOTTOM_LEFT,
        turn_x=2,
        turn_y=2,
    )
    tracker.add_river("l_shape_river", river)
    svg_string = utils_packing_svg.convert_packing_to_svg(grid_size, tracker)[0]
    green_lines = re.findall(r'<line stroke="green".*?/>', svg_string)
    self.assertLen(green_lines, 4)


class MirrorSymmetricPlacementsTest(absltest.TestCase):

  def _check_symmetry_with_creases(self, river, grid_size):
    tracker = utils_tracker.CreasePatternTracker(grid_size)
    tracker.add_river("r1", river)
    svg1 = utils_packing_svg.convert_packing_to_svg(grid_size, tracker)[0]
    cp1 = svg_parser.parse_svg(svg1, grid_size=grid_size)

    mirrored_river = river.mirror(grid_size)
    tracker_m = utils_tracker.CreasePatternTracker(grid_size)
    tracker_m.add_river("r1m", mirrored_river)
    svg_m = utils_packing_svg.convert_packing_to_svg(grid_size, tracker_m)[0]
    cp_m = svg_parser.parse_svg(svg_m, grid_size=grid_size)

    cp1_flipped = symmetry.Transform.VERTICAL_FLIP(cp1)
    self.assertEqual(len(cp1_flipped.creases), len(cp_m.creases))
    for c1 in cp1_flipped.creases:
      self.assertTrue(any(c1.isclose(c2) for c2 in cp_m.creases))

  def test_mirror_polygon_off_axis_with_stick_figure(self):
    tracker = utils_tracker.CreasePatternTracker(10)
    stick_figure = stick_figure_lib.StickFigure(
        name="test",
        category="test",
        complexity=1,
        root="p1",
        children=[
            stick_lib.Stick(
                name="p1", start="a", end="b", azimuth_angle=0, length=1
            ),
            stick_lib.Stick(
                name="p2", start="c", end="d", azimuth_angle=0, length=1
            ),
        ],
    )
    stick_figure["p1"].symmetric_stick_name = "p2"
    stick_figure["p2"].symmetric_stick_name = "p1"
    tracker.add_polygon(
        "p1",
        types.PolygonPlacement.from_grid_coords(
            offset=(0, 0), size=(2, 2), grid_size=10
        ),
    )
    utils_packing_svg.mirror_symmetric_placements(tracker, 10, stick_figure)
    self.assertIn("p2", tracker.packed_polygons)
    mirrored_placement = tracker.packed_polygons["p2"]
    self.assertEqual(mirrored_placement.offset, (8, 0))
    self.assertEqual(mirrored_placement.size, (2, 2))

  def test_mirror_river_off_axis_with_stick_figure(self):
    tracker = utils_tracker.CreasePatternTracker(10)
    r1 = stick_lib.Stick(
        name="r1", start="a", end="b", azimuth_angle=90, length=1
    )
    r1.is_river = True
    r2 = stick_lib.Stick(
        name="r2", start="c", end="d", azimuth_angle=90, length=1
    )
    r2.is_river = True
    stick_figure = stick_figure_lib.StickFigure(
        name="test",
        category="test",
        complexity=1,
        root="r1",
        children=[r1, r2],
    )
    stick_figure["r1"].symmetric_stick_name = "r2"
    stick_figure["r2"].symmetric_stick_name = "r1"
    river1 = river_lib.River(
        width=1,
        offset=0,
        orientation=river_lib.RiverOrientation.VERTICAL,
        grid_size=10,
    )
    tracker.add_river("r1", river1)
    utils_packing_svg.mirror_symmetric_placements(tracker, 10, stick_figure)
    self.assertIn("r2", tracker.packed_rivers)
    self.assertEqual(tracker.packed_rivers["r2"], river1.mirror(10))
    self.assertTrue(river_lib.is_mirror_correct(river1, 10))
    self._check_symmetry_with_creases(river1, 10)

  def test_skip_polygon_on_axis(self):
    tracker = utils_tracker.CreasePatternTracker(10)
    tracker.add_polygon(
        "p_axis",
        types.PolygonPlacement.from_grid_coords(
            offset=(4, 0), size=(2, 2), grid_size=10
        ),
    )
    self.assertLen(tracker.packed_polygons, 1)
    utils_packing_svg.mirror_symmetric_placements(tracker, 10)
    self.assertLen(tracker.packed_polygons, 1)
    self.assertNotIn("p_axis_mirrored", tracker.packed_polygons)

  def test_skip_mirrored_and_copy_polygons(self):
    tracker = utils_tracker.CreasePatternTracker(10)
    tracker.add_polygon(
        "p1_mirrored",
        types.PolygonPlacement.from_grid_coords(
            offset=(0, 0), size=(2, 2), grid_size=10
        ),
    )
    tracker.add_polygon(
        "p2_copy",
        types.PolygonPlacement.from_grid_coords(
            offset=(0, 4), size=(2, 2), grid_size=10
        ),
    )
    self.assertLen(tracker.packed_polygons, 2)
    utils_packing_svg.mirror_symmetric_placements(tracker, 10)
    self.assertLen(tracker.packed_polygons, 2)

  def test_empty_tracker_mirroring(self):
    tracker = utils_tracker.CreasePatternTracker(10)
    utils_packing_svg.mirror_symmetric_placements(tracker, 10)
    self.assertEmpty(tracker.packed_polygons)


class ExtractHingesInfoTest(parameterized.TestCase):

  def test_single_polygon(self):
    tracker = utils_tracker.CreasePatternTracker(10)
    tracker.add_polygon(
        "p1",
        types.PolygonPlacement.from_grid_coords(
            offset=(4, 4), size=(2, 2), grid_size=10
        ),
    )
    hinges = utils_packing_svg.extract_hinges_info(tracker, 10)
    self.assertLen(hinges, 4)
    for hinge in hinges:
      self.assertEqual(hinge.flap_names, ("p1",))
      self.assertFalse(hinge.assigned)

  def test_two_adjacent_polygons(self):
    tracker = utils_tracker.CreasePatternTracker(10)
    tracker.add_polygon(
        "p1",
        types.PolygonPlacement.from_grid_coords(
            offset=(4, 4), size=(2, 2), grid_size=10
        ),
    )
    tracker.add_polygon(
        "p2",
        types.PolygonPlacement.from_grid_coords(
            offset=(6, 4), size=(2, 2), grid_size=10
        ),
    )
    hinges = utils_packing_svg.extract_hinges_info(tracker, 10)

    shared_hinge_found = False
    for hinge in hinges:
      if len(hinge.flap_names) == 2:
        self.assertCountEqual(hinge.flap_names, ("p1", "p2"))
        self.assertEqual(
            hinge.coordinate,
            crease_lib.Crease(
                point_lib.Point(x=0.6, y=0.4),
                point_lib.Point(x=0.6, y=0.6),
                fold=crease_lib.Fold.HINGE,
            ),
        )
        shared_hinge_found = True
    self.assertTrue(shared_hinge_found)
    self.assertLen(hinges, 7)

  def test_polygon_on_border(self):
    tracker = utils_tracker.CreasePatternTracker(10)
    tracker.add_polygon(
        "p1",
        types.PolygonPlacement.from_grid_coords(
            offset=(8, 4), size=(2, 2), grid_size=10
        ),
    )
    hinges = utils_packing_svg.extract_hinges_info(tracker, 10)
    self.assertLen(hinges, 3)

  def test_hinge_splitting_at_t_junction(self):
    """Tests that hinges are split at intersections."""
    grid_size = 4
    tracker = utils_tracker.CreasePatternTracker(grid_size)
    tracker.add_polygon(
        "p1",
        types.PolygonPlacement.from_grid_coords(
            offset=(0, 0), size=(2, 2), grid_size=grid_size
        ),
    )
    tracker.add_polygon(
        "p2",
        types.PolygonPlacement.from_grid_coords(
            offset=(1, 2), size=(2, 2), grid_size=grid_size
        ),
    )
    hinges = utils_packing_svg.extract_hinges_info(tracker, grid_size)

    h1 = crease_lib.Crease(
        point_lib.Point(x=0, y=0.5),
        point_lib.Point(x=0.25, y=0.5),
        fold=crease_lib.Fold.HINGE,
    )
    h2 = crease_lib.Crease(
        point_lib.Point(x=0.25, y=0.5),
        point_lib.Point(x=0.5, y=0.5),
        fold=crease_lib.Fold.HINGE,
    )
    h3 = crease_lib.Crease(
        point_lib.Point(x=0.5, y=0.5),
        point_lib.Point(x=0.75, y=0.5),
        fold=crease_lib.Fold.HINGE,
    )

    shared_hinge_count = 0
    h1_found, h2_found, h3_found = False, False, False
    for h in hinges:
      if h.coordinate and h.coordinate.isclose(h1):
        self.assertEqual(h.flap_names, ("p1",))
        h1_found = True
      elif h.coordinate and h.coordinate.isclose(h2):
        self.assertEqual(h.flap_names, ("p1", "p2"))
        h2_found = True
      elif h.coordinate and h.coordinate.isclose(h3):
        self.assertEqual(h.flap_names, ("p2",))
        h3_found = True
      if len(h.flap_names) == 2:
        shared_hinge_count += 1

    self.assertTrue(h1_found, "Hinge 1 not found")
    self.assertTrue(h2_found, "Hinge 2 not found")
    self.assertTrue(h3_found, "Hinge 3 not found")
    self.assertEqual(shared_hinge_count, 1)
    self.assertLen(hinges, 6)

  def test_human_packing_hinges(self):
    tree = copy.deepcopy(example_trees.HUMAN_SIMPLE)
    grid_size = 12
    is_symmetric = True
    stick_figure_to_pack = tree.get_symmetric_half()
    symmetry_axes = {
        stick.name: stick.is_on_symmetry_axis
        for stick in stick_figure_to_pack.children
    }
    final_placements = utils_river_solver.solve_rivers_iteratively(
        stick_figure_to_pack,
        grid_size=grid_size,
        is_symmetric=is_symmetric,
        symmetry_axes=symmetry_axes,
        debug=debug_types.DebugConfig(),
    )
    self.assertNotEmpty(final_placements)
    final_placement = final_placements[0]
    utils_packing_svg.mirror_symmetric_placements(
        final_placement, grid_size, tree
    )
    hinges = utils_packing_svg.extract_hinges_info(final_placement, grid_size)
    shared_hinges_flaps = []
    for hinge in hinges:
      if len(hinge.flap_names) == 2:
        shared_hinges_flaps.append(tuple(sorted(hinge.flap_names)))

    expected_shared_hinges = [
        tuple(sorted(("head", "left_arm"))),
        tuple(sorted(("left_arm", "torso"))),
        tuple(sorted(("head", "right_arm"))),
        tuple(sorted(("head", "torso"))),
        tuple(sorted(("left_leg", "torso"))),
        tuple(sorted(("left_leg", "right_leg"))),
        tuple(sorted(("right_arm", "torso"))),
        tuple(sorted(("right_leg", "torso"))),
    ]
    self.assertCountEqual(shared_hinges_flaps, expected_shared_hinges)


class GetAdjustedFlapRectangleTest(absltest.TestCase):

  def test_get_adjusted_flap_rectangle_not_square(self):
    grid_size = 8
    polygon = types.PolygonPlacement.from_grid_coords(
        offset=(1, 1), size=(2, 4), grid_size=grid_size
    )
    rect = utils_packing_svg._get_adjusted_flap_rectangle(
        "p1", polygon, grid_size
    )
    self.assertEqual(rect.x_start, 1.0)
    self.assertEqual(rect.y_start, 1.0)
    self.assertEqual(rect.x_len, 2.0)
    self.assertEqual(rect.y_len, 4.0)

  def test_get_adjusted_flap_rectangle_square_not_touching_border(self):
    grid_size = 8
    polygon = types.PolygonPlacement.from_grid_coords(
        offset=(2, 2), size=(4, 4), grid_size=grid_size
    )
    rect = utils_packing_svg._get_adjusted_flap_rectangle(
        "p1", polygon, grid_size
    )
    self.assertEqual(rect.x_start, 2.0)
    self.assertEqual(rect.y_start, 2.0)
    self.assertEqual(rect.x_len, 4.0)
    self.assertEqual(rect.y_len, 4.0)

  @mock.patch.object(
      shaping_utils.Rectangle, "treat_as_wide_on_border", return_value=True
  )
  def test_get_adjusted_flap_rectangle_square_touching_border_wide(
      self, mock_treat_as_wide
  ):
    grid_size = 8
    polygon = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(4, 4), grid_size=grid_size
    )
    rect = utils_packing_svg._get_adjusted_flap_rectangle(
        "p1", polygon, grid_size
    )
    self.assertEqual(rect.x_start, -4.0)
    self.assertEqual(rect.y_start, 0.0)
    self.assertEqual(rect.x_len, 8.0)
    self.assertEqual(rect.y_len, 4.0)
    mock_treat_as_wide.assert_called_once()

  @mock.patch.object(
      shaping_utils.Rectangle, "treat_as_wide_on_border", return_value=False
  )
  def test_get_adjusted_flap_rectangle_square_touching_border_tall(
      self, mock_treat_as_wide
  ):
    grid_size = 8
    polygon = types.PolygonPlacement.from_grid_coords(
        offset=(0, 0), size=(4, 4), grid_size=grid_size
    )
    rect = utils_packing_svg._get_adjusted_flap_rectangle(
        "p1", polygon, grid_size
    )
    self.assertEqual(rect.x_start, 0.0)
    self.assertEqual(rect.y_start, -4.0)
    self.assertEqual(rect.x_len, 4.0)
    self.assertEqual(rect.y_len, 8.0)
    mock_treat_as_wide.assert_called_once()


class HighlightSacrificialTest(absltest.TestCase):

  def test_highlight_sacrificial_recolors_ridge_lines(self):
    tracker = utils_tracker.CreasePatternTracker(10)
    tracker.add_polygon(
        "torso",
        types.PolygonPlacement.from_grid_coords(
            offset=(0, 0), size=(4, 4), grid_size=10
        ),
    )
    tracker.add_polygon(
        f"torso{types.RIVER_SF1_SUFFIX}",
        types.PolygonPlacement.from_grid_coords(
            offset=(4, 0), size=(2, 4), grid_size=10
        ),
    )
    base_svg = utils_packing_svg.convert_packing_to_svg(10, tracker)[0]
    svg_string = utils_packing_svg.add_highlight_overlays(base_svg, 10, tracker)
    purple_rects = re.findall(r'<rect.*?fill="purple".*?/>', svg_string)
    self.assertNotEmpty(purple_rects)

  def test_no_overlay_no_purple_lines(self):
    tracker = utils_tracker.CreasePatternTracker(10)
    tracker.add_polygon(
        "torso",
        types.PolygonPlacement.from_grid_coords(
            offset=(0, 0), size=(4, 4), grid_size=10
        ),
    )
    tracker.add_polygon(
        f"torso{types.RIVER_SF1_SUFFIX}",
        types.PolygonPlacement.from_grid_coords(
            offset=(4, 0), size=(2, 4), grid_size=10
        ),
    )
    svg_string = utils_packing_svg.convert_packing_to_svg(10, tracker)[0]
    purple_rects = re.findall(r'<rect.*?fill="purple".*?/>', svg_string)
    self.assertEmpty(purple_rects)

  def test_purple_rects_ignored_by_parse_svg(self):
    tracker = utils_tracker.CreasePatternTracker(10)
    tracker.add_polygon(
        "torso",
        types.PolygonPlacement.from_grid_coords(
            offset=(0, 0), size=(4, 4), grid_size=10
        ),
    )
    tracker.add_polygon(
        f"torso{types.RIVER_SF1_SUFFIX}",
        types.PolygonPlacement.from_grid_coords(
            offset=(4, 0), size=(2, 4), grid_size=10
        ),
    )
    base_svg = utils_packing_svg.convert_packing_to_svg(10, tracker)[0]
    svg_with = utils_packing_svg.add_highlight_overlays(base_svg, 10, tracker)
    cp_with = svg_parser.parse_svg(svg_with, grid_size=10)
    cp_without = svg_parser.parse_svg(base_svg, grid_size=10)
    self.assertEqual(len(cp_with.creases), len(cp_without.creases))


if __name__ == "__main__":
  absltest.main()
