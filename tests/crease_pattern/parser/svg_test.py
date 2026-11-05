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

"""Test for SVG parser."""

import dataclasses
import math
import random
import textwrap

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import crease_pattern
from bp_pipeline.crease_pattern import point
from bp_pipeline.crease_pattern.parser import svg as parser
from crease_pattern import crease_pattern_test_examples as examples
import lxml.etree as ET


class StyleMapTest(parameterized.TestCase):
  """Test style map parsing."""

  @parameterized.parameters([
      dict(
          style="stroke: #000; opacity: 0.5",
          expected_style_map={"stroke": "#000", "opacity": "0.5"},
      ),
      dict(
          style="stroke:#000;opacity:0.5;fill:#000",
          expected_style_map={
              "stroke": "#000",
              "opacity": "0.5",
              "fill": "#000",
          },
      ),
      dict(style="stroke:red;", expected_style_map={"stroke": "red"}),
      dict(style="", expected_style_map={}),
  ])
  def test_valid_style_map(
      self, style: str, expected_style_map: dict[str, str]
  ):
    style_map = parser._get_style_map(style)
    self.assertEqual(style_map, expected_style_map)


class ValidTest(parameterized.TestCase):
  """Test validation functions."""

  @parameterized.parameters([
      ("<line stroke='#000' x1='0' y1='0' x2='1' y2='1' />", "line"),
      (
          (
              "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'><line"
              " x1='0' y1='0' x2='1' y2='1' /></svg>"
          ),
          "svg",
      ),
      ("<line />", "line"),
      ("<rect />", "rect"),
  ])
  def test_check_tag(self, el: str, expected: str):
    el = ET.fromstring(el)
    self.assertTrue(parser.check_tag(el, expected))

  @parameterized.parameters([
      (
          "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'></svg>",
          True,
      ),
      ("<svg viewBox='0 0 1 1'></svg>", True),
      ("<svg></svg>", False),
      ("<rect />", False),
  ])
  def test_valid_root_tag(self, el: str, expected: bool):
    el = ET.fromstring(el)
    self.assertEqual(parser.valid_root(el), expected)

  @parameterized.parameters(examples._TestExamples)
  def test_valid_xml(self, example: examples.CreasePatternTestExample):
    self.assertEqual(parser.valid_xml(example.xml), example.valid_xml)

  @parameterized.parameters(examples._TestExamples)
  def test_valid_svg(self, example: examples.CreasePatternTestExample):
    valid = example.valid_svg and example.valid_xml
    self.assertEqual(parser.valid_svg(example.xml), valid)

  @parameterized.parameters([
      ("<line stroke='#000' x1='0' y1='0' x2='1' y2='1' />", True),
      ("<line stroke='#000' x1='0' y1='0' x2='1' />", False),
      ("<line x1='0' y1='0' x2='1' y2='1' />", False),
      ("<rect stroke='#000' x1='0' y1='0' x2='1' y2='1' />", False),
      (
          "<line style='stroke: #000' x1='0' y1='0' x2='1' y2='1' />",
          True,
      ),
      (
          (
              "<line style='stroke: #000; opacity: 0.5' x1='0' y1='0' x2='1'"
              " y2='1' />"
          ),
          True,
      ),
  ])
  def test_valid_line(self, el: str, expected: bool):
    el = ET.fromstring(el)
    self.assertEqual(parser.valid_line(el), expected)

  @parameterized.parameters([
      (
          "<line stroke='#000' x1='0' y1='0' x2='1' y2='1' />",
          dict(line=1, svg=0),
      ),
      (
          """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'>
          <!-- A Comment --><line /><line /><line /></svg>""",
          dict(line=3, rect=0, svg=1),
      ),
      (
          """<svg viewBox='0 0 1 1'>
          <g><line /><rect></rect><line></line></g></svg>""",
          dict(line=2, rect=1, g=1, svg=1),
      ),
  ])
  def test_find_all_elements(self, xml: str, expected: dict[str, int]):
    el = ET.fromstring(xml)
    for tag, expected_count in expected.items():
      matches = list(parser.find_elements(el, tag))
      self.assertLen(matches, expected_count)
      for match in matches:
        self.assertTrue(parser.check_tag(match, tag))


class FoldTest(parameterized.TestCase):
  """Test fold color parsing."""

  @parameterized.parameters([
      " red ",
      "red",
      "#ff0000",
      "#f00",
      "#FF0000",
      "#F00",
      "rgb(255,0,0)",
      "rgb(255, 0, 0)",
      "rgb(100%,0%,0%)",
      "rgb(100%, 0%, 0%)",
  ])
  def test_mountain_fold(self, color: str):
    fold = parser.get_fold(color)
    self.assertEqual(fold, crease.Fold.MOUNTAIN)

  @parameterized.parameters([
      " blue ",
      "blue",
      "#0000ff",
      "#00f",
      "#0000FF",
      "#00F",
      "rgb(0,0,255)",
      "rgb(0, 0, 255)",
      "rgb(0%,0%,100%)",
      "rgb(0%, 0%, 100%)",
  ])
  def test_valley_fold(self, color: str):
    fold = parser.get_fold(color)
    self.assertEqual(fold, crease.Fold.VALLEY)

  @parameterized.parameters([
      " black ",
      "black",
      "#000000",
      "#000",
      "rgb(0,0,0)",
      "rgb(0, 0, 0)",
      "rgb(0%,0%,0%)",
      "rgb(0%, 0%, 0%)",
  ])
  def test_border_fold(self, color: str):
    fold = parser.get_fold(color)
    self.assertEqual(fold, crease.Fold.BORDER)

  @parameterized.parameters([
      " yellow ",
      "yellow",
      "#ffff00",
      "#ff0",
      "#FFFF00",
      "#FF0",
      "rgb(255,255,0)",
      "rgb(255, 255, 0)",
      "rgb(100%,100%,0%)",
      "rgb(100%, 100%, 0%)",
  ])
  def test_triangle_fold(self, color: str):
    fold = parser.get_fold(color)
    self.assertEqual(fold, crease.Fold.TRIANGLE)

  @parameterized.parameters(["purple", "f00", "#009", "hsv(0, 100%, 100%)"])
  def test_invalid_fold(self, color: str):
    with self.assertRaises(ValueError):
      parser.get_fold(color)


@dataclasses.dataclass(frozen=True)
class CreaseTestExample:
  """Contains a single variant of a crease."""

  line: str
  expected_p1: point.Point | None = None
  expected_p2: point.Point | None = None
  expected_fold: crease.Fold | None = None
  expected_fold_percent: float | None = None
  expected_fold_step: int = 0
  expected_elevation: int | None = None


VALID_CREASES = [
    CreaseTestExample(
        line="<line stroke='#000' x1='0' y1='0' x2='1' y2='1' />",
        expected_fold=crease.Fold.BORDER,
        expected_fold_percent=1.0,
        expected_p1=point.Point(x=0, y=0),
        expected_p2=point.Point(x=1, y=1),
    ),
    CreaseTestExample(
        line="<line stroke='#000' x1='0' y1='0' x2='1' y2='1'>Some text</line>",
        expected_fold=crease.Fold.BORDER,
        expected_fold_percent=1.0,
        expected_p1=point.Point(x=0, y=0),
        expected_p2=point.Point(x=1, y=1),
    ),
    CreaseTestExample(
        line="<line stroke='#00f' x1='1' y1='1' x2='0' y2='0' />",
        expected_fold=crease.Fold.VALLEY,
        expected_fold_percent=1.0,
        expected_p1=point.Point(x=1, y=1),
        expected_p2=point.Point(x=0, y=0),
    ),
    CreaseTestExample(
        line="<line stroke='#f00' x1='1.00001' y1='1' x2='0' y2='-0.00001' />",
        expected_fold=crease.Fold.MOUNTAIN,
        expected_fold_percent=1.0,
        expected_p1=point.Point(x=1, y=1),
        expected_p2=point.Point(x=0, y=0),
    ),
    CreaseTestExample(
        line="<line stroke='#f00' opacity='0.5' x1='1' y1='1' x2='0' y2='0' />",
        expected_fold=crease.Fold.MOUNTAIN,
        expected_fold_percent=0.5,
        expected_p1=point.Point(x=1, y=1),
        expected_p2=point.Point(x=0, y=0),
    ),
    CreaseTestExample(
        line=(
            "<line style='stroke: #f00; opacity: 0.1' x1='1' y1='1' x2='0'"
            " y2='0' />"
        ),
        expected_fold=crease.Fold.MOUNTAIN,
        expected_fold_percent=0.1,
        expected_p1=point.Point(x=1, y=1),
        expected_p2=point.Point(x=0, y=0),
    ),
    CreaseTestExample(
        line=(
            "<line style='stroke: #009' stroke='#F00' x1='1' y1='1' x2='0'"
            " y2='0' />"
        ),
        expected_fold=crease.Fold.MOUNTAIN,
        expected_fold_percent=1.0,
        expected_p1=point.Point(x=1, y=1),
        expected_p2=point.Point(x=0, y=0),
    ),
    CreaseTestExample(
        line=(
            "<line style='stroke: #009' stroke='#F00' fold-step='1' x1='1'"
            " y1='1' x2='0' y2='0' />"
        ),
        expected_fold=crease.Fold.MOUNTAIN,
        expected_fold_percent=1.0,
        expected_p1=point.Point(x=1, y=1),
        expected_p2=point.Point(x=0, y=0),
        expected_fold_step=1,
        expected_elevation=None,
    ),
]

INVALID_CREASES = [
    CreaseTestExample(  # invalid color
        "<line stroke='#009' x1='0' y1='0' x2='1' y2='1' />",
    ),
    CreaseTestExample(  # invalid color
        "<line style='stroke: #009' x1='0' y1='0' x2='1' y2='1' />",
    ),
    CreaseTestExample(  # missing stroke
        "<line x1='0' y1='0' x2='1' y2='1' />",
    ),
    CreaseTestExample(  # outside of viewbox
        "<line stroke='#000' x1='0' y1='0' x2='1' y2='2' />",
    ),
    CreaseTestExample(  # invalid opacity
        "<line stroke='#000' opacity='1.1' x1='0' y1='0' x2='1' y2='1' />",
    ),
    CreaseTestExample(  # invalid opacity
        "<line stroke='#000' opacity='-0.1' x1='0' y1='0' x2='1' y2='1' />",
    ),
    CreaseTestExample(  # invalid opacity
        "<line stroke='#000' opacity='abc' x1='0' y1='0' x2='1' y2='1' />",
    ),
]


class CreaseTest(parameterized.TestCase):
  """Test parse_crease on individual creases."""

  @parameterized.parameters(VALID_CREASES)
  def test_valid_crease(self, example: CreaseTestExample):
    line = ET.fromstring(example.line)
    self.assertTrue(parser.valid_line(line))
    viewbox = (0, 0, 1, 1)
    crease_obj = parser.parse_line(line, viewbox)
    self.assertIsInstance(crease_obj, crease.Crease)
    # The points of the crease are sorted when a crease is created.
    self.assertTrue(
        crease_obj.p1.isclose(example.expected_p1)
        or crease_obj.p1.isclose(example.expected_p2)
    )
    self.assertTrue(
        crease_obj.p2.isclose(example.expected_p2)
        or crease_obj.p2.isclose(example.expected_p1)
    )
    self.assertFalse(crease_obj.p1.isclose(crease_obj.p2))
    self.assertEqual(crease_obj.fold, example.expected_fold)
    self.assertEqual(crease_obj.fold_percent, example.expected_fold_percent)
    self.assertEqual(crease_obj.fold_step, example.expected_fold_step)
    self.assertEqual(crease_obj.elevation, example.expected_elevation)

  @parameterized.parameters(INVALID_CREASES)
  def test_invalid_crease(self, example: CreaseTestExample):
    line = ET.fromstring(example.line)
    with self.assertRaises(ValueError):
      parser.parse_line(line, (0, 0, 1, 1))


@dataclasses.dataclass(frozen=True, kw_only=True)
class RectTestExample:
  """Contains a single variant of a rect and its expected parsed creases."""

  rect_str: str
  bottom_left: point.Point | None = None
  top_left: point.Point | None = None
  top_right: point.Point | None = None
  bottom_right: point.Point | None = None
  expected_fold: crease.Fold | None = None
  expected_fold_percent: float | None = None


VALID_RECTS = [
    RectTestExample(
        rect_str="<rect stroke='#000' x='0' y='0' width='1' height='1' />",
        expected_fold=crease.Fold.BORDER,
        expected_fold_percent=1.0,
        bottom_left=point.Point(x=0, y=1),
        top_left=point.Point(x=0, y=0),
        top_right=point.Point(x=1, y=0),
        bottom_right=point.Point(x=1, y=1),
    ),
    RectTestExample(  # With fill and other ignored attrs
        rect_str=(
            "<rect fill='#fff' stroke='black' x='0.1' y='0.2' width='0.8'"
            " height='0.6' />"
        ),
        expected_fold=crease.Fold.BORDER,
        expected_fold_percent=1.0,
        bottom_left=point.Point(x=0.1, y=0.8),
        top_left=point.Point(x=0.1, y=0.2),
        top_right=point.Point(x=0.9, y=0.2),
        bottom_right=point.Point(x=0.9, y=0.8),
    ),
    RectTestExample(  # Mountain fold
        rect_str="<rect stroke='red' x='0' y='0' width='0.5' height='0.5' />",
        expected_fold=crease.Fold.MOUNTAIN,
        expected_fold_percent=1.0,
        bottom_left=point.Point(x=0, y=0.5),
        top_left=point.Point(x=0, y=0),
        top_right=point.Point(x=0.5, y=0),
        bottom_right=point.Point(x=0.5, y=0.5),
    ),
    RectTestExample(  # Valley fold with opacity
        rect_str=(
            "<rect stroke='#00f' opacity='0.7' x='0.2' y='0.2' width='0.6'"
            " height='0.6' />"
        ),
        expected_fold=crease.Fold.VALLEY,
        expected_fold_percent=0.7,
        bottom_left=point.Point(x=0.2, y=0.8),
        top_left=point.Point(x=0.2, y=0.2),
        top_right=point.Point(x=0.8, y=0.2),
        bottom_right=point.Point(x=0.8, y=0.8),
    ),
    RectTestExample(  # Using style attribute
        rect_str=(
            "<rect style='stroke: #f00; opacity: 0.3;' x='0' y='0.7'"
            " width='0.2' height='0.3' />"
        ),
        expected_fold=crease.Fold.MOUNTAIN,
        expected_fold_percent=0.3,
        bottom_left=point.Point(x=0, y=1),
        top_left=point.Point(x=0, y=0.7),
        top_right=point.Point(x=0.2, y=0.7),
        bottom_right=point.Point(x=0.2, y=1),
    ),
    RectTestExample(  # Direct attribute overrides style
        rect_str=(
            "<rect style='stroke: blue; opacity: 0.9;' stroke='red'"
            " opacity='0.1' x='0.1' y='0.1' width='0.1' height='0.1' />"
        ),
        expected_fold=crease.Fold.MOUNTAIN,
        expected_fold_percent=0.1,
        bottom_left=point.Point(x=0.1, y=0.2),
        top_left=point.Point(x=0.1, y=0.1),
        top_right=point.Point(x=0.2, y=0.1),
        bottom_right=point.Point(x=0.2, y=0.2),
    ),
    RectTestExample(  # Default x=0, y=0
        rect_str="<rect stroke='#000' width='0.4' height='0.4' />",
        expected_fold=crease.Fold.BORDER,
        expected_fold_percent=1.0,
        bottom_left=point.Point(x=0, y=0.4),
        top_left=point.Point(x=0, y=0),
        top_right=point.Point(x=0.4, y=0),
        bottom_right=point.Point(x=0.4, y=0.4),
    ),
]

INVALID_RECTS = [
    RectTestExample(  # Missing width
        rect_str="<rect stroke='#000' x='0' y='0' height='1' />"
    ),
    RectTestExample(  # Missing height
        rect_str="<rect stroke='#000' x='0' y='0' width='1' />"
    ),
    RectTestExample(  # Zero width
        rect_str="<rect stroke='#000' x='0' y='0' width='0' height='1' />"
    ),
    RectTestExample(  # Negative height
        rect_str="<rect stroke='#000' x='0' y='0' width='1' height='-1' />"
    ),
    RectTestExample(  # Percentage width
        rect_str="<rect stroke='#000' x='0' y='0' width='100%' height='1' />"
    ),
]


class RectTest(parameterized.TestCase):
  """Test parse_rect for <rect> elements."""

  @parameterized.parameters(VALID_RECTS)
  def test_valid_rect(self, example: RectTestExample):
    """Tests parsing of valid <rect> elements."""
    rect_element = ET.fromstring(example.rect_str)
    viewbox = (0.0, 0.0, 1.0, 1.0)
    creases_list = parser.parse_rect(rect_element, viewbox)

    self.assertIsInstance(creases_list, list)
    self.assertLen(creases_list, 4)

    expected_creases = [
        crease.Crease(
            example.bottom_left,
            example.top_left,
            fold=example.expected_fold,
            fold_percent=example.expected_fold_percent,
        ),
        crease.Crease(
            example.top_left,
            example.top_right,
            fold=example.expected_fold,
            fold_percent=example.expected_fold_percent,
        ),
        crease.Crease(
            example.top_right,
            example.bottom_right,
            fold=example.expected_fold,
            fold_percent=example.expected_fold_percent,
        ),
        crease.Crease(
            example.bottom_right,
            example.bottom_left,
            fold=example.expected_fold,
            fold_percent=example.expected_fold_percent,
        ),
    ]

    for actual in creases_list:
      with self.subTest(crease=actual):
        self.assertIsInstance(actual, crease.Crease)
        with self.subTest("check actual crease endpoints aren't equal"):
          self.assertFalse(actual.p1.isclose(actual.p2))

        with self.subTest("check fold type"):
          self.assertEqual(actual.fold, example.expected_fold)
          self.assertAlmostEqual(
              actual.fold_percent, example.expected_fold_percent, places=7
          )
          self.assertEqual(actual.fold_step, 0)
          self.assertIsNone(actual.elevation)

    self.assertCountEqual(creases_list, expected_creases)

  @parameterized.parameters(INVALID_RECTS)
  def test_invalid_rect(self, example: RectTestExample):
    """Tests that invalid <rect> elements raise ValueError during parsing."""
    rect_element = ET.fromstring(example.rect_str)
    viewbox = (0.0, 0.0, 1.0, 1.0)
    with self.assertRaises(ValueError):
      parser.parse_rect(rect_element, viewbox)


_BROKEN_SVGS = [
    (  # unclosed line '/>'
        "<svg viewBox='0 0 1 1' xmlns='http://www.w3.org/2000/svg'><line"
        " stroke='red' x1='0' y1='0' x2='1' y2='1'"
        "<rect stroke='black' x='0' y='0' width='1' height='1' />"
        "</svg>"
    ),
    (  # missing closing svg tag
        "<svg viewBox='0 0 1 1'><line"
        " stroke='red' x1='0' y1='0' x2='1' y2='1'/>"
        "<rect stroke='black' x='0' y='0' width='1' height='1' />"
    ),
    (  # unclosed line '/>'
        "<svg viewBox='0 0 1 1' xmlns='http://www.w3.org/2000/svg'><line"
        " stroke='red' x1='0' y1='0' x2='1' y2='1'"
        "<rect stroke='black' x='0' y='0' width='1' height='1' />"
        "</svg>"
    ),
]


class ParseSvgTest(parameterized.TestCase):
  """Test parse_svg on complete SVGs."""

  @parameterized.parameters(examples._TestExamples)
  def test_parse_svg(self, example: examples.CreasePatternTestExample):
    if (
        example.valid_xml
        and example.valid_svg
        and example.valid_crease_pattern
        and example.invalid_ratio == 0.0
    ):
      cp = parser.parse_svg(example.xml)
      self.assertIsInstance(cp, crease_pattern.CreasePattern)
      svg_string = parser.to_svg(cp)
      self.assertIsInstance(svg_string, str)
      self.assertTrue(parser.valid_svg(svg_string))

    elif example.invalid_ratio == 0.0:
      with self.assertRaises(ValueError):
        parser.parse_svg(example.xml)

  def test_overlapping_creases(self):
    xml = """
     <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1">
       <rect stroke="black" x="0" y="0" width="1" height="1" />
          <g class="boundaries" fill="white" stroke="#000">
            <line x1="0.0" y1="0.0" x2="1.0" y2="0.0" stroke="#000"/>
            <line x1="1.0" y1="0.0" x2="1.0" y2="1.0" stroke="#000"/>
          </g>
          <g class="edges" stroke="#000">
            <line x1="0.0" y1="0.0" x2="1.0" y2="0.0" stroke="#000"/>
            <line x1="1.0" y1="0.0" x2="1.0" y2="1.0" stroke="#000"/>
          </g>
        </svg>
      """
    cp = parser.parse_svg(xml)
    self.assertAlmostEqual(cp.invalid_creases_ratio, 0.5)

  @parameterized.parameters(examples._TestExamples)
  def test_parse_svg_idempotent(
      self, example: examples.CreasePatternTestExample
  ):
    if (
        example.valid_xml
        and example.valid_svg
        and example.valid_crease_pattern
        and example.invalid_ratio == 0.0
        and example.source == examples.CreasePatternType.WEB
    ):
      cp1 = parser.parse_svg(example.xml)
      svg_string1 = parser.to_svg(cp1)
      cp2 = parser.parse_svg(svg_string1)

      self.assertEqual(len(cp1.creases), len(cp2.creases))
      self.assertEqual(len(cp1.vertices), len(cp2.vertices))

      # Vertex order is a by-product of our implementation which we use here
      # but generally, 2 crease patterns can be the same with a different order.
      # The vertices will not be identical if the borders are rescaled to match
      # the viewBox of the SVG, so we limit the test to WEB crease patterns that
      # are already scaled to the viewBox.
      for v1, v2 in zip(cp1.vertices, cp2.vertices):
        self.assertTrue(v1.point.isclose(v2.point))
        self.assertEqual(len(v1.creases), len(v2.creases))
        self.assertCountEqual(v1.creases, v2.creases)

      svg_string2 = parser.to_svg(cp2)
      self.assertEqual(svg_string1, svg_string2)

  @parameterized.parameters(_BROKEN_SVGS)
  def test_repair_parse_svg(self, example: str):
    with self.assertRaises(ValueError):
      parser.parse_svg(example)

    cp = parser.parse_svg(example, repair=True)
    self.assertIsInstance(cp, crease_pattern.CreasePattern)

  def test_scale_parse_svg(self):
    unscaled_svg = (
        "<svg viewBox='0 0 1 1' xmlns='http://www.w3.org/2000/svg'>"
        "<line stroke='#000' x1='0.25' y1='0.25' x2='0.25' y2='0.75'/>"
        "<line stroke='#000' x1='0.25' y1='0.25' x2='0.75' y2='0.25'/>"
        "<line stroke='#000' x1='0.25' y1='0.75' x2='0.75' y2='0.75'/>"
        "<line stroke='#000' x1='0.75' y1='0.25' x2='0.75' y2='0.75'/>"
        "<line stroke='#f00' x1='0.5' y1='0.25' x2='0.5' y2='0.75'/>"
        "</svg>"
    )
    scaled_svg = (
        "<svg viewBox='0.25 0.25 0.5 0.5' xmlns='http://www.w3.org/2000/svg'>"
        "<line stroke='#000' x1='0.25' y1='0.25' x2='0.25' y2='0.75'/>"
        "<line stroke='#000' x1='0.25' y1='0.25' x2='0.75' y2='0.25'/>"
        "<line stroke='#000' x1='0.25' y1='0.75' x2='0.75' y2='0.75'/>"
        "<line stroke='#000' x1='0.75' y1='0.25' x2='0.75' y2='0.75'/>"
        "<line stroke='#f00' x1='0.5' y1='0.25' x2='0.5' y2='0.75'/>"
        "</svg>"
    )

    cp = parser.parse_svg(unscaled_svg)
    target_cp = parser.parse_svg(scaled_svg)

    self.assertLen(cp.creases, len(target_cp.creases))
    self.assertLen(cp.vertices, len(target_cp.vertices))
    for v1, v2 in zip(cp.vertices, target_cp.vertices, strict=True):
      self.assertAlmostEqual(v1.point.x, v2.point.x, places=5)
      self.assertAlmostEqual(v1.point.y, v2.point.y, places=5)

    remaining = list(target_cp.creases)
    for c in cp.creases:
      match_idx = next(
          (
              i
              for i, cand in enumerate(remaining)
              if c.fold == cand.fold
              and (
                  (
                      math.isclose(c.p1.x, cand.p1.x, abs_tol=1e-5)
                      and math.isclose(c.p1.y, cand.p1.y, abs_tol=1e-5)
                      and math.isclose(c.p2.x, cand.p2.x, abs_tol=1e-5)
                      and math.isclose(c.p2.y, cand.p2.y, abs_tol=1e-5)
                  )
                  or (
                      math.isclose(c.p1.x, cand.p2.x, abs_tol=1e-5)
                      and math.isclose(c.p1.y, cand.p2.y, abs_tol=1e-5)
                      and math.isclose(c.p2.x, cand.p1.x, abs_tol=1e-5)
                      and math.isclose(c.p2.y, cand.p1.y, abs_tol=1e-5)
                  )
              )
          ),
          None,
      )
      self.assertIsNotNone(match_idx, msg=f"Unmatched crease: {c}")
      remaining.pop(match_idx)


SQUARE_BASE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {full} {full}">
  <line stroke="blue" x1="0" y1="{half}" x2="{half}" y2="{half}" fold-step="1"/>
  <line stroke="red" x1="{half}" y1="0" x2="{half}" y2="{half}"/>
  <line stroke="red" x1="{half}" y1="{half}" x2="{half}" y2="{full}"/>
  <line stroke="red" x1="{half}" y1="{half}" x2="{full}" y2="{half}"/>
</svg>
"""


class SvgExportTest(parameterized.TestCase):

  @parameterized.parameters([10, 100, 1000])
  def test_to_svg(self, scale: int):
    pattern = crease_pattern.CreasePattern(
        creases=[
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=0, y=0.5),
                fold=crease.Fold.VALLEY,
                fold_step=1,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=0.5, y=0),
                fold=crease.Fold.MOUNTAIN,
            ),
            crease.Crease(
                point.Point(x=0.5, y=1),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
            crease.Crease(
                point.Point(x=1, y=0.5),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
        ],
    )

    svg = parser.to_svg(pattern, scale=scale, pretty=True)
    self.assertEqual(pattern.num_fold_steps, 2)
    self.assertEqual(svg, SQUARE_BASE.format(full=scale, half=scale // 2))

  @parameterized.parameters([10, 100, 1000])
  def test_to_svg_with_replace_border(self, scale: int):
    pattern = crease_pattern.CreasePattern(
        creases=[
            crease.Crease(
                point.Point(x=1, y=0),
                point.Point(x=0, y=0),
                fold=crease.Fold.BORDER,
            )
        ]
    )
    expected_svg = textwrap.dedent(f"""\
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {scale} {scale}">
        <rect stroke="black" x="0" y="0" width="{scale}" height="{scale}" fill="none"/>
      </svg>""")

    svg = parser.to_svg(pattern, scale=scale, replace_border=True, pretty=True)

    self.assertEqual(svg.strip(), expected_svg.strip())

  def test_to_svg_with_replace_border_and_stroke_width(self):
    pattern = crease_pattern.CreasePattern(
        creases=[
            crease.Crease(
                point.Point(x=1, y=0),
                point.Point(x=0, y=0),
                fold=crease.Fold.BORDER,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0),
                point.Point(x=0.5, y=1),
                fold=crease.Fold.MOUNTAIN,
            ),
        ]
    )
    svg = parser.to_svg(
        pattern,
        grid=20,
        replace_border=True,
        stroke_width=0.0444,
        pretty=True,
    )
    self.assertIn('stroke-width="0.0444"', svg)
    self.assertIn('fill="none"', svg)
    self.assertIn("<rect", svg)
    self.assertIn("<line", svg)

  def test_to_svg_with_shuffle_order(self):
    n = 9
    # Crease pattern with n - 1 horizontal creases.
    pattern = crease_pattern.CreasePattern(
        creases=[
            crease.Crease(
                point.Point(x=0, y=i / n),
                point.Point(x=1, y=i / n),
                fold=crease.Fold.MOUNTAIN,
            )
            for i in range(1, n)
        ]
    )
    random.seed(42)
    svg_no_shuffle = parser.to_svg(pattern)
    svg_shuffle = parser.to_svg(
        pattern, replace_border=True, shuffle_order=True
    )
    self.assertNotEqual(svg_no_shuffle, svg_shuffle)
    self.assertTrue(parser.valid_svg(svg_shuffle))

    with self.assertRaises(ValueError):
      parser.to_svg(pattern, shuffle_order=True)

  def test_to_svg_with_group(self):
    pattern = crease_pattern.CreasePattern(
        creases=[
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=0, y=0.5),
                fold=crease.Fold.VALLEY,
                fold_step=1,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=0.5, y=0),
                fold=crease.Fold.MOUNTAIN,
            ),
            crease.Crease(
                point.Point(x=0.5, y=1),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
            crease.Crease(
                point.Point(x=1, y=0.5),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
        ],
    )
    svg = parser.to_svg(pattern, group=True, pretty=True)
    expected_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <g>
    <g stroke="red">
      <line x1="500" y1="0" x2="500" y2="500"/>
      <line x1="500" y1="500" x2="500" y2="1000"/>
      <line x1="500" y1="500" x2="1000" y2="500"/>
    </g>
  </g>
  <g fold-step="1">
    <g stroke="blue">
      <line x1="0" y1="500" x2="500" y2="500"/>
    </g>
  </g>
</svg>
"""
    self.assertEqual(svg, expected_svg)

  def test_grouped_svg_roundtrip(self):
    cp1 = parser.parse_svg(
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <rect stroke="black" x="0" y="0" width="1000" height="1000"/>
  <line stroke="blue" x1="0" y1="500" x2="500" y2="500" fold-step="1"/>
  <line stroke="red" x1="500" y1="0" x2="500" y2="500"/>
  <line stroke="red" x1="500" y1="500" x2="500" y2="1000"/>
  <line stroke="red" x1="500" y1="500" x2="1000" y2="500"/>
</svg>
"""
    )

    svg1 = parser.to_svg(cp1, group=True, replace_border=True)
    cp2 = parser.parse_svg(svg1)
    svg2 = parser.to_svg(cp2, group=True, replace_border=True)
    self.assertEqual(svg1, svg2)

    self.assertEqual(len(cp1.creases), len(cp2.creases))
    for c1, c2 in zip(
        sorted(cp1.creases, key=lambda c: (c.p1.x, c.p1.y)),
        sorted(cp2.creases, key=lambda c: (c.p1.x, c.p1.y)),
    ):
      self.assertEqual(c1.fold, c2.fold)
      self.assertEqual(c1.fold_step, c2.fold_step)


if __name__ == "__main__":
  absltest.main()
