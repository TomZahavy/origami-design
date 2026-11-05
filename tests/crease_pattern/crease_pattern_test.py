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

"""Tests for Crease Patterns."""

import math

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import crease_pattern
from bp_pipeline.crease_pattern import point
from bp_pipeline.crease_pattern import validate
from bp_pipeline.crease_pattern.parser import svg
from crease_pattern import crease_pattern_test_examples as examples

BORDER_CREASES = [
    crease.Crease(
        point.Point(x=0.0, y=0.0),
        point.Point(x=1.0, y=0.0),
        fold=crease.Fold.BORDER,
    ),
    crease.Crease(
        point.Point(x=1.0, y=0.0),
        point.Point(x=1.0, y=1.0),
        fold=crease.Fold.BORDER,
    ),
    crease.Crease(
        point.Point(x=1.0, y=1.0),
        point.Point(x=0.0, y=1.0),
        fold=crease.Fold.BORDER,
    ),
    crease.Crease(
        point.Point(x=0.0, y=1.0),
        point.Point(x=0.0, y=0.0),
        fold=crease.Fold.BORDER,
    ),
]


def _assert_cp_equivalent(
    test_case: absltest.TestCase,
    actual: crease_pattern.CreasePattern,
    expected: crease_pattern.CreasePattern,
    *,
    abs_tol: float,
) -> None:
  """Asserts two CPs have matching vertices and creases up to `abs_tol`."""
  test_case.assertLen(actual.creases, len(expected.creases))
  test_case.assertLen(actual.vertices, len(expected.vertices))

  remaining_vertices = list(expected.vertices)
  for v in actual.vertices:
    match_idx = next(
        (
            i
            for i, cand in enumerate(remaining_vertices)
            if math.isclose(v.point.x, cand.point.x, abs_tol=abs_tol)
            and math.isclose(v.point.y, cand.point.y, abs_tol=abs_tol)
        ),
        None,
    )
    test_case.assertIsNotNone(match_idx, msg=f'Unmatched vertex: {v.point}')
    remaining_vertices.pop(match_idx)

  def _matches(c1: crease.Crease, c2: crease.Crease) -> bool:
    if c1.fold != c2.fold:
      return False
    direct = (
        math.isclose(c1.p1.x, c2.p1.x, abs_tol=abs_tol)
        and math.isclose(c1.p1.y, c2.p1.y, abs_tol=abs_tol)
        and math.isclose(c1.p2.x, c2.p2.x, abs_tol=abs_tol)
        and math.isclose(c1.p2.y, c2.p2.y, abs_tol=abs_tol)
    )
    flipped = (
        math.isclose(c1.p1.x, c2.p2.x, abs_tol=abs_tol)
        and math.isclose(c1.p1.y, c2.p2.y, abs_tol=abs_tol)
        and math.isclose(c1.p2.x, c2.p1.x, abs_tol=abs_tol)
        and math.isclose(c1.p2.y, c2.p1.y, abs_tol=abs_tol)
    )
    return direct or flipped

  remaining_creases = list(expected.creases)
  for c in actual.creases:
    match_idx = next(
        (i for i, cand in enumerate(remaining_creases) if _matches(c, cand)),
        None,
    )
    test_case.assertIsNotNone(match_idx, msg=f'Unmatched crease: {c}')
    remaining_creases.pop(match_idx)


class CreasePatternsTest(parameterized.TestCase):

  @parameterized.parameters(examples._TestExamples)
  def test_crease_pattern_test_examples(
      self, test_cp: examples.CreasePatternTestExample
  ):
    valid_xml = svg.valid_xml(test_cp.xml)
    valid_svg = svg.valid_svg(test_cp.xml)
    self.assertEqual(
        valid_xml,
        test_cp.valid_xml,
        msg=test_cp.name + ' failed for valid xml',
    )
    if valid_xml:
      self.assertEqual(
          valid_svg,
          test_cp.valid_svg,
          msg=test_cp.name + ' failed for valid svg',
      )
    if valid_xml and valid_svg:
      if test_cp.valid_crease_pattern:
        pattern = svg.parse_svg(test_cp.xml)
        with self.subTest(name='is_valid'):
          self.assertTrue(validate.valid_pattern(pattern))

        self.assertEqual(pattern.num_fold_steps, 1)
        self.assertEqual(
            pattern.local_flat_foldability(
                check_blb=False,
                check_kawasaki=False,
                check_crimp=False,
                check_maekawa=True,
            ),
            test_cp.maekawa_foldable,
            msg=test_cp.name + ' failed for Maekawa',
        )
        self.assertEqual(
            pattern.local_flat_foldability(
                check_maekawa=False,
                check_kawasaki=False,
                check_crimp=False,
                check_blb=True,
            ),
            test_cp.blb_foldable,
            msg=test_cp.name + ' failed for BLB Lemma',
        )
        self.assertEqual(
            pattern.local_flat_foldability(
                check_maekawa=False,
                check_blb=False,
                check_kawasaki=True,
                check_crimp=False,
            ),
            test_cp.kawasaki_foldable,
            msg=test_cp.name + ' failed for Kawasaki theorem',
        )
        self.assertEqual(
            pattern.local_flat_foldability(
                check_maekawa=False,
                check_blb=False,
                check_kawasaki=False,
                check_crimp=True,
            ),
            test_cp.crimp_foldable,
            msg=test_cp.name + ' failed for crimp check',
        )
        self.assertEqual(
            pattern.local_flat_foldability(),
            test_cp.flat_foldable,
            msg=test_cp.name + ' failed for local flat foldability',
        )
        self.assertAlmostEqual(
            pattern.invalid_creases_ratio,
            test_cp.invalid_ratio,
            msg=test_cp.name + ' failed for invalid creases ratio',
            delta=1e-3,
        )

        stats = pattern.stats()
        expected_stats = {
            'invalid_ratio': test_cp.invalid_ratio,
            'num_creases': len(pattern.creases),
            'num_vertices': len(pattern.vertices),
        }
        for k, v in expected_stats.items():
          self.assertAlmostEqual(stats[k], v, delta=1e-3)
      else:
        with self.assertRaises(ValueError):
          svg.parse_svg(test_cp.xml)

  def test_merge_creases(self):
    """Merges segments into longer creases."""
    xml1 = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="-0.2 -0.2 2.4 2.4">
    <rect stroke="black" x="-0.2" y="-0.2" width="2.4" height="2.4" />
    <line stroke="#f00" opacity="1" x1="0" y1="1" x2="1" y2="1"/>
    <line stroke="#00f" opacity="1" x1="1" y1="0" x2="1" y2="1"/>
    <line stroke="#00f" opacity="1" x1="1" y1="1" x2="1" y2="2"/>
    <line stroke="#00f" opacity="1" x1="1" y1="1" x2="2" y2="1"/>
    </svg>
    """

    xml2 = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4 4">
    <line x1="1" y1="2" x2="2" y2="2" stroke="#ff0000"></line>
    <line x1="2" y1="2" x2="3" y2="2" stroke="#ff0000"></line>
    <line x1="3" y1="2" x2="4" y2="3" stroke="#ff0000"></line>
    <line x1="3" y1="2" x2="4" y2="1" stroke="#ff0000"></line>
    <line x1="1" y1="2" x2="0" y2="1" stroke="#ff0000"></line>
    <line x1="1" y1="2" x2="0" y2="3" stroke="#ff0000"></line>
    <line x1="1" y1="0" x2="1" y2="2" stroke="#0000ff"></line>
    <line x1="3" y1="0" x2="3" y2="2" stroke="#0000ff"></line>
    <line x1="1" y1="2" x2="1" y2="4" stroke="#ffff00"></line>
    <line x1="3" y1="2" x2="3" y2="4" stroke="#ffff00"></line>
    <line x1="2" y1="0" x2="2" y2="2" stroke="#ffff00"></line>
    <line x1="2" y1="2" x2="2" y2="4" stroke="#ffff00"></line>
    <line x1="0" y1="2" x2="1" y2="2" stroke="#ffff00"></line>
    <line x1="3" y1="2" x2="4" y2="2" stroke="#ffff00"></line>
    <line x1="0" y1="0" x2="0" y2="1" stroke="#000000"></line>
    <line x1="4" y1="4" x2="3" y2="4" stroke="#000000"></line>
    <line x1="4" y1="4" x2="4" y2="3" stroke="#000000"></line>
    <line x1="0" y1="0" x2="1" y2="0" stroke="#000000"></line>
    <line x1="1" y1="0" x2="2" y2="0" stroke="#000000"></line>
    <line x1="1" y1="4" x2="0" y2="4" stroke="#000000"></line>
    <line x1="2" y1="0" x2="3" y2="0" stroke="#000000"></line>
    <line x1="2" y1="4" x2="1" y2="4" stroke="#000000"></line>
    <line x1="3" y1="0" x2="4" y2="0" stroke="#000000"></line>
    <line x1="3" y1="4" x2="2" y2="4" stroke="#000000"></line>
    <line x1="0" y1="2" x2="0" y2="3" stroke="#000000"></line>
    <line x1="4" y1="2" x2="4" y2="1" stroke="#000000"></line>
    <line x1="4" y1="3" x2="4" y2="2" stroke="#000000"></line>
    <line x1="4" y1="1" x2="4" y2="0" stroke="#000000"></line>
    <line x1="0" y1="1" x2="0" y2="2" stroke="#000000"></line>
    <line x1="0" y1="3" x2="0" y2="4" stroke="#000000"></line>
    </svg>
    """

    xml3 = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="-0.5 -0.5 5 5">
    <line x1="1" y1="4" x2="1" y2="2" stroke="#ff0000"></line>
    <line x1="1" y1="2" x2="1" y2="0" stroke="#ff0000"></line>
    <line x1="0" y1="2" x2="1" y2="2" stroke="#ff0000"></line>
    <line x1="2" y1="4" x2="2" y2="2" stroke="#ff0000"></line>
    <line x1="2" y1="2" x2="2" y2="0" stroke="#ff0000"></line>
    <line x1="3" y1="4" x2="3" y2="2" stroke="#ff0000"></line>
    <line x1="3" y1="2" x2="3" y2="0" stroke="#ff0000"></line>
    <line x1="2" y1="2" x2="3" y2="2" stroke="#ff0000"></line>
    <line x1="1" y1="2" x2="2" y2="2" stroke="#0000ff"></line>
    <line x1="3" y1="2" x2="4" y2="2" stroke="#0000ff"></line>
    <line x1="0" y1="0" x2="0" y2="2" stroke="#000000"></line>
    <line x1="0" y1="2" x2="0" y2="4" stroke="#000000"></line>
    <line x1="3" y1="4" x2="4" y2="4" stroke="#000000"></line>
    <line x1="0" y1="4" x2="1" y2="4" stroke="#000000"></line>
    <line x1="1" y1="4" x2="2" y2="4" stroke="#000000"></line>
    <line x1="2" y1="4" x2="3" y2="4" stroke="#000000"></line>
    <line x1="4" y1="4" x2="4" y2="2" stroke="#000000"></line>
    <line x1="4" y1="2" x2="4" y2="0" stroke="#000000"></line>
    <line x1="1" y1="0" x2="0" y2="0" stroke="#000000"></line>
    <line x1="2" y1="0" x2="1" y2="0" stroke="#000000"></line>
    <line x1="4" y1="0" x2="3" y2="0" stroke="#000000"></line>
    <line x1="3" y1="0" x2="2" y2="0" stroke="#000000"></line>
    </svg>
    """

    cp1 = svg.parse_svg(xml1)
    cp2 = svg.parse_svg(xml2, merge_trivial=True)
    cp3 = svg.parse_svg(xml3)

    self.assertEqual(cp1.num_merged_creases, 0)
    self.assertEqual(cp2.num_merged_creases, 8)
    self.assertEqual(cp3.num_merged_creases, 0)

    self.assertLen(cp1.creases, 8)
    self.assertLen(cp2.creases, 22)
    self.assertLen(cp3.creases, 22)

    cp1.merge_creases()
    cp2.merge_creases()
    cp3.merge_creases()
    self.assertEqual(cp1.num_merged_creases, 1)
    self.assertEqual(cp2.num_merged_creases, 6)
    self.assertEqual(cp3.num_merged_creases, 11)

    self.assertLen(cp1.creases, 7)
    self.assertLen(cp2.creases, 16)
    self.assertLen(cp2.vertices, 12)
    self.assertLen(cp3.creases, 11)

    cp1.merge_creases(merge_zebra=True)
    cp2.merge_creases(merge_zebra=True)
    cp3.merge_creases(merge_zebra=True)
    self.assertLen(cp1.creases, 6)
    self.assertLen(cp2.creases, 16)
    self.assertLen(cp3.creases, 8)

  def test_merge_trivial_creases(self):
    """Merges segments into longer creases."""
    xml = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="-0.2 -0.2 2.4 2.4">
    <rect stroke="black" x="-0.2" y="-0.2" width="2.4" height="2.4" />
    <line stroke="#f00" opacity="1" x1="0" y1="1" x2="1" y2="1"/>
    <line stroke="#00f" opacity="1" x1="1" y1="0" x2="1" y2="1"/>
    <line stroke="#00f" opacity="1" x1="1" y1="1" x2="1" y2="2"/>
    <line stroke="#00f" opacity="1" x1="1" y1="1" x2="1.5" y2="1"/>
    <line stroke="#00f" opacity="1" x1="1.5" y1="1" x2="2" y2="1"/>
    </svg>
    """

    cp = svg.parse_svg(xml, merge_trivial=True)
    self.assertEqual(cp.num_merged_creases, 1)
    self.assertLen(cp.creases, 8)

  def test_light_mode(self):
    """Tests for light mode."""
    xml = examples._TestExamples[-1].xml
    cp = svg.parse_svg(xml)
    cp_light = svg.parse_svg(xml, light_mode=True)

    self.assertEqual(len(cp.creases), len(cp_light.creases))
    self.assertEqual(len(cp.vertices), len(cp_light.vertices))
    _assert_cp_equivalent(self, cp, cp_light, abs_tol=1e-7)

  def test_intersection_vertices(self):
    """Tests for intersection vertices."""
    svg_str = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100'
        ' 100"><line stroke="#f00" opacity="1" x1="0" y1="0" x2="100"'
        ' y2="100" stroke-width="2"/><line stroke="#00f" opacity="1" x1="0"'
        ' y1="100" x2="100" y2="0" stroke-width="2"/>'
        ' <rect stroke="black" x="0" y="0" width="100" height="100" />'
        ' </svg>'
    )
    cp = svg.parse_svg(svg_str)
    self.assertLen(cp.vertices, 5)
    cp = svg.parse_svg(svg_str, light_mode=True)
    self.assertLen(cp.vertices, 4)

  def test_scaling_viewbox(self):
    """Test scaling viewBox."""
    xml = """
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="-0.5 -0.5 5 5">
      <line x1="1" y1="2" x2="2" y2="2" stroke="#ff0000"></line>
      <line x1="2" y1="2" x2="3" y2="2" stroke="#ff0000"></line>
      <line x1="3" y1="2" x2="4" y2="3" stroke="#ff0000"></line>
      <line x1="3" y1="2" x2="4" y2="1" stroke="#ff0000"></line>
      <line x1="1" y1="2" x2="0" y2="1" stroke="#ff0000"></line>
      <line x1="1" y1="2" x2="0" y2="3" stroke="#ff0000"></line>
      <line x1="1" y1="0" x2="1" y2="2" stroke="#0000ff"></line>
      <line x1="3" y1="0" x2="3" y2="2" stroke="#0000ff"></line>
      <line x1="1" y1="2" x2="1" y2="4" stroke="#ffff00"></line>
      <line x1="3" y1="2" x2="3" y2="4" stroke="#ffff00"></line>
      <line x1="2" y1="0" x2="2" y2="2" stroke="#ffff00"></line>
      <line x1="2" y1="2" x2="2" y2="4" stroke="#ffff00"></line>
      <line x1="0" y1="2" x2="1" y2="2" stroke="#ffff00"></line>
      <line x1="3" y1="2" x2="4" y2="2" stroke="#ffff00"></line>
      <line x1="0" y1="0" x2="0" y2="1" stroke="#000000"></line>
      <line x1="4" y1="4" x2="3" y2="4" stroke="#000000"></line>
      <line x1="4" y1="4" x2="4" y2="3" stroke="#000000"></line>
      <line x1="0" y1="0" x2="1" y2="0" stroke="#000000"></line>
      <line x1="1" y1="0" x2="2" y2="0" stroke="#000000"></line>
      <line x1="1" y1="4" x2="0" y2="4" stroke="#000000"></line>
      <line x1="2" y1="0" x2="3" y2="0" stroke="#000000"></line>
      <line x1="2" y1="4" x2="1" y2="4" stroke="#000000"></line>
      <line x1="3" y1="0" x2="4" y2="0" stroke="#000000"></line>
      <line x1="3" y1="4" x2="2" y2="4" stroke="#000000"></line>
      <line x1="0" y1="2" x2="0" y2="3" stroke="#000000"></line>
      <line x1="4" y1="2" x2="4" y2="1" stroke="#000000"></line>
      <line x1="4" y1="3" x2="4" y2="2" stroke="#000000"></line>
      <line x1="4" y1="1" x2="4" y2="0" stroke="#000000"></line>
      <line x1="0" y1="1" x2="0" y2="2" stroke="#000000"></line>
      <line x1="0" y1="3" x2="0" y2="4" stroke="#000000"></line>
      </svg>
      """

    cp = svg.parse_svg(xml)

    def _is_one_zero(s1: float, s2: float) -> bool:
      """Checks if the two coordinates are equal, and are equal to 1 or 0."""
      return (math.isclose(s1, 1.0) and math.isclose(s2, 1.0)) or (
          math.isclose(s1, 0.0) and math.isclose(s2, 0.0)
      )

    for c in cp.creases:
      if c.fold == crease.Fold.BORDER:
        print(c)
        self.assertTrue(
            _is_one_zero(c.p1.x, c.p2.x) or _is_one_zero(c.p1.y, c.p2.y)
        )

  def test_sort_vertices(self):
    xml = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4 4">
    '<rect stroke="black" x="0" y="0" width="4" height="4" />'
    <line x1="1" y1="2" x2="2" y2="2" stroke="#ff0000"></line>
    <line x1="2" y1="2" x2="3" y2="2" stroke="#ff0000"></line>
    <line x1="3" y1="2" x2="4" y2="3" stroke="#ff0000"></line>
    <line x1="3" y1="2" x2="4" y2="1" stroke="#ff0000"></line>
    <line x1="1" y1="2" x2="0" y2="1" stroke="#ff0000"></line>
    </svg>
    """
    cp = svg.parse_svg(xml, merge_trivial=True)
    self.assertTrue(cp.vertices[0].point.isclose(point.Point(x=0.0, y=0.0)))
    self.assertTrue(cp.vertices[1].point.isclose(point.Point(x=0.0, y=0.25)))
    self.assertTrue(cp.vertices[2].point.isclose(point.Point(x=0.25, y=0.5)))
    self.assertTrue(cp.vertices[3].point.isclose(point.Point(x=0.75, y=0.5)))
    self.assertTrue(cp.vertices[4].point.isclose(point.Point(x=0.0, y=1.0)))
    self.assertTrue(cp.vertices[5].point.isclose(point.Point(x=1.0, y=0.0)))
    self.assertTrue(cp.vertices[6].point.isclose(point.Point(x=1.0, y=0.25)))
    self.assertTrue(cp.vertices[7].point.isclose(point.Point(x=1.0, y=0.75)))

  @parameterized.parameters(examples._TestExamples)
  def test_cycle(self, test_cp: examples.CreasePatternTestExample):
    if test_cp.crease_pattern_type == examples.CreasePatternType.WEB:
      xml = test_cp.xml
      cp = svg.parse_svg(xml)
      cp_cycle = svg.parse_svg(svg.to_svg(cp))

      self.assertEqual(len(cp.creases), len(cp_cycle.creases))
      self.assertEqual(len(cp.vertices), len(cp_cycle.vertices))
      _assert_cp_equivalent(self, cp, cp_cycle, abs_tol=1e-3)

  @parameterized.parameters(examples._TestExamples)
  def test_merge_cycle(self, test_cp: examples.CreasePatternTestExample):
    if test_cp.crease_pattern_type == examples.CreasePatternType.WEB:
      xml = test_cp.xml
      cp = svg.parse_svg(xml)
      cp_merge = svg.parse_svg(xml)
      cp_merge.merge_creases()
      cp_cycle = svg.parse_svg(svg.to_svg(cp_merge))

      self.assertEqual(len(cp.creases), len(cp_cycle.creases))
      self.assertEqual(len(cp.vertices), len(cp_cycle.vertices))
      _assert_cp_equivalent(self, cp, cp_cycle, abs_tol=1e-3)

  @parameterized.parameters(examples._TestExamples)
  def test_merge_zebra_cycle(self, test_cp: examples.CreasePatternTestExample):
    if test_cp.crease_pattern_type == examples.CreasePatternType.WEB:
      xml = test_cp.xml
      cp = svg.parse_svg(xml)
      cp_merge = svg.parse_svg(xml)
      cp_merge.merge_creases(merge_zebra=True)
      cp_cycle = svg.parse_svg(svg.to_svg(cp_merge))

      self.assertEqual(len(cp.creases), len(cp_cycle.creases))
      self.assertEqual(len(cp.vertices), len(cp_cycle.vertices))
      _assert_cp_equivalent(self, cp, cp_cycle, abs_tol=1e-3)

  def test_is_subset(self):
    xml1 = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2 2">
        <rect stroke="black" x="0" y="0" width="2" height="2" />
        <line stroke="#f00" opacity="1" x1="0" y1="1" x2="1" y2="1"/>
        <line stroke="#00f" opacity="1" x1="1" y1="1" x2="1" y2="2"/>
        <line stroke="#00f" opacity="1" x1="1" y1="1" x2="2" y2="1"/>
        </svg>
        """
    xml2 = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2 2">
        <rect stroke="black" x="0" y="0" width="2" height="2" />
        <line stroke="#f00" opacity="1" x1="0" y1="1" x2="1" y2="1"/>
        <line stroke="#00f" opacity="1" x1="1" y1="0" x2="1" y2="1"/>
        <line stroke="#00f" opacity="1" x1="1" y1="1" x2="1" y2="2"/>
        <line stroke="#00f" opacity="1" x1="1" y1="1" x2="2" y2="1"/>
        </svg>
        """
    cp1 = svg.parse_svg(xml1)
    cp2 = svg.parse_svg(xml2)
    cp2.merge_creases()
    self.assertTrue(cp1.is_subset(cp2))
    self.assertFalse(cp2.is_subset(cp1))

    with self.subTest(name='is_subset_self'):
      self.assertTrue(cp1.is_subset(cp1))
      self.assertTrue(cp2.is_subset(cp2))

  def test_get_incident_creases(self):
    xml = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2 2">
        <rect stroke="black" x="0" y="0" width="2" height="2" />
        <line stroke="#f00" opacity="1" x1="0" y1="1" x2="1" y2="1"/>
        <line stroke="#00f" opacity="1" x1="1" y1="1" x2="1" y2="2"/>
        <line stroke="#00f" opacity="1" x1="1" y1="1" x2="2" y2="1"/>
        </svg>
        """
    cp = svg.parse_svg(xml)
    incident_creases = cp.get_incident_creases(point.Point(x=0.5, y=0.5))
    self.assertLen(incident_creases, 3)
    self.assertIn(
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1, y=0.5),
            fold=crease.Fold.VALLEY,
        ),
        incident_creases,
    )
    self.assertIn(
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0.5, y=1),
            fold=crease.Fold.VALLEY,
        ),
        incident_creases,
    )
    self.assertIn(
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0, y=0.5),
            fold=crease.Fold.MOUNTAIN,
        ),
        incident_creases,
    )

  def test_empty_pattern_init(self):
    with self.assertRaises(ValueError):
      # Check default disallows empty patterns.
      crease_pattern.CreasePattern(creases=[])

    cp = crease_pattern.CreasePattern(creases=[], is_empty=True)
    self.assertEmpty(cp.creases)
    self.assertEmpty(cp.vertices)
    self.assertEqual(cp.num_merged_creases, 0)
    self.assertEqual(cp.invalid_creases_ratio, 0.0)
    self.assertEqual(cp.stats()['num_creases'], 0)
    self.assertEqual(cp.stats()['num_vertices'], 0)
    self.assertEqual(cp.stats()['invalid_ratio'], 0.0)

  @parameterized.parameters(100, 1000)
  def test_empty_pattern_to_svg(self, scale: int):
    cp = crease_pattern.CreasePattern(creases=[], is_empty=True)
    empty_svg = svg.to_svg(cp, scale=scale)
    self.assertEqual(
        empty_svg,
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0'
        f' {scale} {scale}"/>',
    )

    empty_svg_with_rect = svg.to_svg(cp, scale=scale, replace_border=True)
    self.assertEqual(
        empty_svg_with_rect,
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {scale}'
        f' {scale}"><rect stroke="black" x="0" y="0" width="{scale}"'
        f' height="{scale}" fill="none"/></svg>',
    )

  @parameterized.named_parameters(
      ('with_grid', 4),
      ('no_grid', -1),
  )
  def test_get_tips_and_grid_creases(self, grid_size: int):
    """Tests get_tips_and_grid_creases."""
    # Dummy data:
    # c1 and c2 share an endpoint (p2).
    # p4 is a grid point for grid_size=4.
    # After snapping to grid, c1, c2, and c3 will share an endpoint at
    # (0.25, 0.25), which is a grid point. This tests deduplication of tips.
    p1 = point.Point(x=0.1, y=0.1)
    p2 = point.Point(x=0.26, y=0.26)
    p3 = point.Point(x=0.6, y=0.6)
    p4 = point.Point(x=0.25, y=0.25)
    p5 = point.Point(x=0.8, y=0.3)
    c1 = crease.Crease(p1, p2, fold=crease.Fold.MOUNTAIN)
    c2 = crease.Crease(p2, p3, fold=crease.Fold.VALLEY)
    c3 = crease.Crease(p4, p5, fold=crease.Fold.MOUNTAIN)
    creases_data = [c1, c2, c3]

    tips, grid_creases = crease_pattern.get_tips_and_grid_creases(
        creases_data, grid_size
    )
    self.assertLen(grid_creases, 3)

    if grid_size > 0:
      # Check grid creases are snapped correctly.
      expected_c1 = crease.Crease(
          point.Point(x=0.0, y=0.0),
          point.Point(x=0.25, y=0.25),
          fold=crease.Fold.MOUNTAIN,
      )
      expected_c2 = crease.Crease(
          point.Point(x=0.25, y=0.25),
          point.Point(x=0.5, y=0.5),
          fold=crease.Fold.VALLEY,
      )
      expected_c3 = crease.Crease(
          point.Point(x=0.25, y=0.25),
          point.Point(x=0.75, y=0.25),
          fold=crease.Fold.MOUNTAIN,
      )
      self.assertEqual(grid_creases, [expected_c1, expected_c2, expected_c3])

      # Check tips contains all grid points, and nothing more.
      self.assertLen(tips, (grid_size + 1) * (grid_size + 1))
      expected_tips = set()
      for i in range(grid_size + 1):
        for j in range(grid_size + 1):
          expected_tips.add(
              point.Point(x=float(i) / grid_size, y=float(j) / grid_size)
          )
    else:
      self.assertEqual(grid_creases, creases_data)
      self.assertLen(tips, 5)
      expected_tips = {p1, p2, p3, p4, p5}

    self.assertEqual(set(tips), expected_tips)

  @parameterized.named_parameters(
      dict(
          testcase_name='vertex_is_foldable',
          internal_creases=[
              # A 3M/1V vertex.
              crease.Crease(
                  point.Point(x=0.5, y=0.5),
                  point.Point(x=1, y=0.5),
                  fold=crease.Fold.MOUNTAIN,
              ),
              crease.Crease(
                  point.Point(x=0.5, y=0.5),
                  point.Point(x=0.5, y=1),
                  fold=crease.Fold.MOUNTAIN,
              ),
              crease.Crease(
                  point.Point(x=0.5, y=0.5),
                  point.Point(x=0, y=0.5),
                  fold=crease.Fold.MOUNTAIN,
              ),
              crease.Crease(
                  point.Point(x=0.5, y=0.5),
                  point.Point(x=0.5, y=0),
                  fold=crease.Fold.VALLEY,
              ),
          ],
          bottom_border_creases=[
              crease.Crease(
                  point.Point(x=1, y=1),
                  point.Point(x=0.5, y=1),
                  fold=crease.Fold.BORDER,
              ),
              crease.Crease(
                  point.Point(x=0.5, y=1),
                  point.Point(x=0, y=1),
                  fold=crease.Fold.BORDER,
              ),
          ],
          expected_score=1.0,
      ),
      dict(
          testcase_name='vertex_is_not_foldable',
          internal_creases=[
              crease.Crease(
                  point.Point(x=0.5, y=0.5),
                  point.Point(x=1, y=0.5),
                  fold=crease.Fold.MOUNTAIN,
              ),
              crease.Crease(
                  point.Point(x=0.5, y=0.5),
                  point.Point(x=0.5, y=1),
                  fold=crease.Fold.MOUNTAIN,
              ),
              crease.Crease(
                  point.Point(x=0.5, y=0.5),
                  point.Point(x=0, y=0.5),
                  fold=crease.Fold.MOUNTAIN,
              ),
              crease.Crease(
                  point.Point(x=0.5, y=0.5),
                  point.Point(x=0.5, y=0),
                  fold=crease.Fold.MOUNTAIN,
              ),
          ],
          bottom_border_creases=[
              crease.Crease(
                  point.Point(x=1, y=1),
                  point.Point(x=0.5, y=1),
                  fold=crease.Fold.BORDER,
              ),
              crease.Crease(
                  point.Point(x=0.5, y=1),
                  point.Point(x=0, y=1),
                  fold=crease.Fold.BORDER,
              ),
          ],
          expected_score=0.0,
      ),
      dict(
          testcase_name='one_vertex_is_foldable_and_one_is_not',
          internal_creases=[
              crease.Crease(
                  point.Point(x=0.5, y=0.5),
                  point.Point(x=1, y=0.5),
                  fold=crease.Fold.MOUNTAIN,
              ),
              crease.Crease(
                  point.Point(x=0.5, y=0.5),
                  point.Point(x=0.5, y=0.75),
                  fold=crease.Fold.MOUNTAIN,
              ),
              crease.Crease(
                  point.Point(x=0.5, y=0.75),
                  point.Point(x=0.5, y=1),
                  fold=crease.Fold.VALLEY,
              ),
              crease.Crease(
                  point.Point(x=0.5, y=0.75),
                  point.Point(x=0.25, y=1),
                  fold=crease.Fold.MOUNTAIN,
              ),
              crease.Crease(
                  point.Point(x=0.5, y=0.75),
                  point.Point(x=0.75, y=1),
                  fold=crease.Fold.MOUNTAIN,
              ),
              crease.Crease(
                  point.Point(x=0.5, y=0.5),
                  point.Point(x=0, y=0.5),
                  fold=crease.Fold.MOUNTAIN,
              ),
              crease.Crease(
                  point.Point(x=0.5, y=0.5),
                  point.Point(x=0.5, y=0),
                  fold=crease.Fold.MOUNTAIN,
              ),
          ],
          bottom_border_creases=[
              crease.Crease(
                  point.Point(x=0, y=1),
                  point.Point(x=0.25, y=1),
                  fold=crease.Fold.BORDER,
              ),
              crease.Crease(
                  point.Point(x=0.25, y=1),
                  point.Point(x=0.5, y=1),
                  fold=crease.Fold.BORDER,
              ),
              crease.Crease(
                  point.Point(x=0.5, y=1),
                  point.Point(x=0.75, y=1),
                  fold=crease.Fold.BORDER,
              ),
              crease.Crease(
                  point.Point(x=0.75, y=1),
                  point.Point(x=1, y=1),
                  fold=crease.Fold.BORDER,
              ),
          ],
          expected_score=0.5,
      ),
  )
  def test_vertex_flat_foldability_percentage(
      self, internal_creases, bottom_border_creases, expected_score
  ):
    """Tests the flat foldability score calculation."""
    border_creases = [
        crease.Crease(
            point.Point(x=0, y=0),
            point.Point(x=0.5, y=0),
            fold=crease.Fold.BORDER,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0),
            point.Point(x=1, y=0),
            fold=crease.Fold.BORDER,
        ),
        crease.Crease(
            point.Point(x=1, y=0),
            point.Point(x=1, y=0.5),
            fold=crease.Fold.BORDER,
        ),
        crease.Crease(
            point.Point(x=1, y=0.5),
            point.Point(x=1, y=1),
            fold=crease.Fold.BORDER,
        ),
        crease.Crease(
            point.Point(x=0, y=1),
            point.Point(x=0, y=0.5),
            fold=crease.Fold.BORDER,
        ),
        crease.Crease(
            point.Point(x=0, y=0.5),
            point.Point(x=0, y=0),
            fold=crease.Fold.BORDER,
        ),
    ]
    all_creases = border_creases + bottom_border_creases + internal_creases
    cp = crease_pattern.CreasePattern(creases=all_creases, light_mode=True)
    score, _, _ = cp.vertex_flat_foldability_percentage()
    self.assertAlmostEqual(score, expected_score)

  def test_get_matching_creases(self):
    b1, b2, b3, b4, m = (
        crease.Crease(
            point.Point(x=0, y=0),
            point.Point(x=1, y=0),
            fold=crease.Fold.BORDER,
        ),
        crease.Crease(
            point.Point(x=1, y=0),
            point.Point(x=1, y=1),
            fold=crease.Fold.BORDER,
        ),
        crease.Crease(
            point.Point(x=0, y=1),
            point.Point(x=1, y=1),
            fold=crease.Fold.BORDER,
        ),
        crease.Crease(
            point.Point(x=0, y=0),
            point.Point(x=0, y=1),
            fold=crease.Fold.BORDER,
        ),
        crease.Crease(
            point.Point(x=1, y=0),
            point.Point(x=0, y=1),
            fold=crease.Fold.MOUNTAIN,
        ),
    )
    cp = crease_pattern.CreasePattern(creases=[b1, b2, b3, b4, m], grid_size=2)
    matching_creases = cp.get_matching_creases([b1, b3, m])
    for matched_crease, crease_to_match in zip(
        sorted(
            matching_creases,
            key=lambda c: (c.p1.x, c.p1.y, c.p2.x, c.p2.y),
        ),
        sorted(
            [b1, b3, m],
            key=lambda c: (c.p1.x, c.p1.y, c.p2.x, c.p2.y),
        ),
    ):
      self.assertTrue(matched_crease.isclose(crease_to_match))
      self.assertIsNot(matched_crease, crease_to_match)

  def test_get_non_overlapping_creases(self):
    p00 = point.Point(x=0, y=0)
    p10 = point.Point(x=0.1, y=0)
    p20 = point.Point(x=0.2, y=0)
    p050 = point.Point(x=0.05, y=0)
    p150 = point.Point(x=0.15, y=0)
    m = crease.Fold.MOUNTAIN
    c1 = crease.Crease(p00, p10, fold=m)
    c2 = crease.Crease(p10, p20, fold=m)
    c3 = crease.Crease(p050, p150, fold=m)  # overlaps with c1 and c2
    c4 = crease.Crease(p00, p10, fold=m)  # same as c1
    c5 = crease.Crease(
        point.Point(x=0, y=1), point.Point(x=1, y=1), fold=m
    )  # doesn't overlap with anything

    with self.subTest(name='identical_creases'):
      creases = [c1, c4, c5]
      non_overlapping = crease_pattern.get_non_overlapping_creases(creases)
      self.assertLen(non_overlapping, 2)
      self.assertIn(c5, non_overlapping)

    with self.subTest(name='two_non_overlapping_creases'):
      creases = [c1, c2, c5]
      non_overlapping = crease_pattern.get_non_overlapping_creases(creases)
      self.assertLen(non_overlapping, 3)
      self.assertIn(c1, non_overlapping)
      self.assertIn(c2, non_overlapping)
      self.assertIn(c5, non_overlapping)

    with self.subTest(name='overlapping_creases'):
      creases = [c1, c3, c5]
      non_overlapping = crease_pattern.get_non_overlapping_creases(creases)
      self.assertLen(non_overlapping, 2)
      self.assertIn(c5, non_overlapping)

    with self.subTest(name='multiple_overlapping_creases'):
      creases = [c1, c2, c3, c5]
      non_overlapping = crease_pattern.get_non_overlapping_creases(creases)
      self.assertLen(non_overlapping, 3)
      self.assertIn(c5, non_overlapping)

  @parameterized.named_parameters(
      dict(
          testcase_name='no_splitting',
          base_creases=[
              *BORDER_CREASES,
              *[
                  crease.Crease(
                      point.Point(x=0, y=0),
                      point.Point(x=1, y=1),
                      fold=crease.Fold.VALLEY,
                  ),
              ],
          ],
          shaping_creases=[
              crease.Crease(
                  point.Point(x=1, y=0),
                  point.Point(x=0, y=1),
                  fold=crease.Fold.VALLEY,
              ),
          ],
          splitting_params={
              'split_base_by_shaping': False,
              'split_shaping_by_base': False,
              'split_shaping_by_shaping': False,
          },
          expected_creases=[
              *BORDER_CREASES,
              *[
                  crease.Crease(
                      point.Point(x=0, y=0),
                      point.Point(x=1, y=1),
                      fold=crease.Fold.VALLEY,
                  ),
                  crease.Crease(
                      point.Point(x=1, y=0),
                      point.Point(x=0, y=1),
                      fold=crease.Fold.VALLEY,
                  ),
              ],
          ],
      ),
      dict(
          testcase_name='split_base_creases_by_shaping',
          base_creases=[
              *BORDER_CREASES,
              *[
                  crease.Crease(
                      point.Point(x=0, y=0),
                      point.Point(x=1, y=1),
                      fold=crease.Fold.VALLEY,
                  ),
              ],
          ],
          shaping_creases=[
              crease.Crease(
                  point.Point(x=1, y=0),
                  point.Point(x=0, y=1),
                  fold=crease.Fold.VALLEY,
              ),
          ],
          splitting_params={
              'split_base_by_shaping': True,
              'split_shaping_by_base': False,
              'split_shaping_by_shaping': False,
          },
          expected_creases=[
              *BORDER_CREASES,
              *[
                  crease.Crease(
                      point.Point(x=0, y=0),
                      point.Point(x=0.5, y=0.5),
                      fold=crease.Fold.VALLEY,
                  ),
                  crease.Crease(
                      point.Point(x=0.5, y=0.5),
                      point.Point(x=1, y=1),
                      fold=crease.Fold.VALLEY,
                  ),
                  crease.Crease(
                      point.Point(x=1, y=0),
                      point.Point(x=0, y=1),
                      fold=crease.Fold.VALLEY,
                  ),
              ],
          ],
      ),
      dict(
          testcase_name='split_base_creases_by_shaping_and_shaping_by_base',
          base_creases=[
              *BORDER_CREASES,
              *[
                  crease.Crease(
                      point.Point(x=0, y=0),
                      point.Point(x=1, y=1),
                      fold=crease.Fold.VALLEY,
                  ),
              ],
          ],
          shaping_creases=[
              crease.Crease(
                  point.Point(x=1, y=0),
                  point.Point(x=0, y=1),
                  fold=crease.Fold.VALLEY,
              ),
          ],
          splitting_params={
              'split_base_by_shaping': True,
              'split_shaping_by_base': True,
              'split_shaping_by_shaping': False,
          },
          expected_creases=[
              *BORDER_CREASES,
              *[
                  crease.Crease(
                      point.Point(x=0, y=0),
                      point.Point(x=0.5, y=0.5),
                      fold=crease.Fold.VALLEY,
                  ),
                  crease.Crease(
                      point.Point(x=0.5, y=0.5),
                      point.Point(x=1, y=1),
                      fold=crease.Fold.VALLEY,
                  ),
                  crease.Crease(
                      point.Point(x=1, y=0),
                      point.Point(x=0.5, y=0.5),
                      fold=crease.Fold.VALLEY,
                  ),
                  crease.Crease(
                      point.Point(x=0.5, y=0.5),
                      point.Point(x=0, y=1),
                      fold=crease.Fold.VALLEY,
                  ),
              ],
          ],
      ),
      dict(
          testcase_name='split_everything',
          base_creases=[
              *BORDER_CREASES,
              *[
                  crease.Crease(
                      point.Point(x=0, y=0),
                      point.Point(x=1, y=1),
                      fold=crease.Fold.VALLEY,
                  ),
              ],
          ],
          shaping_creases=[
              crease.Crease(
                  point.Point(x=1, y=0),
                  point.Point(x=0, y=1),
                  fold=crease.Fold.VALLEY,
              ),
              crease.Crease(
                  point.Point(x=0.5, y=0),
                  point.Point(x=1, y=0.5),
                  fold=crease.Fold.VALLEY,
              ),
          ],
          splitting_params={
              'split_base_by_shaping': True,
              'split_shaping_by_base': True,
              'split_shaping_by_shaping': True,
          },
          expected_creases=[
              *[
                  # Split border.
                  crease.Crease(
                      point.Point(x=0, y=0),
                      point.Point(x=0.5, y=0),
                      fold=crease.Fold.BORDER,
                  ),
                  crease.Crease(
                      point.Point(x=0.5, y=0),
                      point.Point(x=1, y=0),
                      fold=crease.Fold.BORDER,
                  ),
                  crease.Crease(
                      point.Point(x=1, y=0),
                      point.Point(x=1, y=0.5),
                      fold=crease.Fold.BORDER,
                  ),
                  crease.Crease(
                      point.Point(x=1, y=0.5),
                      point.Point(x=1, y=1),
                      fold=crease.Fold.BORDER,
                  ),
                  crease.Crease(
                      point.Point(x=0, y=0),
                      point.Point(x=0, y=1),
                      fold=crease.Fold.BORDER,
                  ),
                  crease.Crease(
                      point.Point(x=0, y=1),
                      point.Point(x=1, y=1),
                      fold=crease.Fold.BORDER,
                  ),
                  # Split base crease.
                  crease.Crease(
                      point.Point(x=0, y=0),
                      point.Point(x=0.5, y=0.5),
                      fold=crease.Fold.VALLEY,
                  ),
                  crease.Crease(
                      point.Point(x=0.5, y=0.5),
                      point.Point(x=1, y=1),
                      fold=crease.Fold.VALLEY,
                  ),
                  # Split first shaping crease.
                  crease.Crease(
                      point.Point(x=1, y=0),
                      point.Point(x=0.75, y=0.25),
                      fold=crease.Fold.VALLEY,
                  ),
                  crease.Crease(
                      point.Point(x=0.75, y=0.25),
                      point.Point(x=0.5, y=0.5),
                      fold=crease.Fold.VALLEY,
                  ),
                  crease.Crease(
                      point.Point(x=0.5, y=0.5),
                      point.Point(x=0, y=1),
                      fold=crease.Fold.VALLEY,
                  ),
                  # Split second shaping crease.
                  crease.Crease(
                      point.Point(x=0.5, y=0),
                      point.Point(x=0.75, y=0.25),
                      fold=crease.Fold.VALLEY,
                  ),
                  crease.Crease(
                      point.Point(x=0.75, y=0.25),
                      point.Point(x=1, y=0.5),
                      fold=crease.Fold.VALLEY,
                  ),
              ],
          ],
      ),
  )
  def test_update_with_shaping_creases(
      self, base_creases, shaping_creases, splitting_params, expected_creases
  ):
    base_cp = crease_pattern.CreasePattern(creases=base_creases)
    shaped_cp = base_cp.update_with_shaping_creases(
        shaping_creases, **splitting_params
    )
    new_creases = shaped_cp.creases
    self.assertLen(new_creases, len(expected_creases))
    for new_crease in new_creases:
      self.assertTrue(
          any(
              new_crease.isclose(expected_crease)
              for expected_crease in expected_creases
          )
      )

  def test_spatial_indexed_helpers_match_reference_on_large_pattern(self):
    creases = list(BORDER_CREASES)
    for k in range(1, 16):
      v = k / 16.0
      creases.append(
          crease.Crease(
              point.Point(x=v, y=0.0),
              point.Point(x=v, y=1.0),
              fold=crease.Fold.MOUNTAIN,
          )
      )
      creases.append(
          crease.Crease(
              point.Point(x=0.0, y=v),
              point.Point(x=1.0, y=v),
              fold=crease.Fold.VALLEY,
          )
      )
    # Add overlapping duplicates to verify exact filtering.
    creases.append(
        crease.Crease(
            point.Point(x=0.25, y=0.1),
            point.Point(x=0.25, y=0.4),
            fold=crease.Fold.MOUNTAIN,
        )
    )
    creases.append(
        crease.Crease(
            point.Point(x=0.0, y=0.0),
            point.Point(x=1.0, y=1.0),
            fold=crease.Fold.MOUNTAIN,
        )
    )

    ref_non_overlapping: list[crease.Crease] = []
    for c in creases:
      if not any(c.is_overlapping(oc) for oc in ref_non_overlapping):
        ref_non_overlapping.append(c)

    fast_non_overlapping = crease_pattern.get_non_overlapping_creases(creases)
    # Append extra independent tiny segments to cross `_MIN_SPATIAL_INDEX_SIZE`.
    extra = [
        crease.Crease(
            point.Point(x=0.01 + 0.012 * i, y=0.02),
            point.Point(x=0.015 + 0.012 * i, y=0.04),
            fold=crease.Fold.MOUNTAIN,
        )
        for i in range(60)
    ]
    self.assertEqual(fast_non_overlapping, ref_non_overlapping)
    large_input = [*creases, *extra]
    ref_large: list[crease.Crease] = []
    for c in large_input:
      if not any(c.is_overlapping(oc) for oc in ref_large):
        ref_large.append(c)
    self.assertEqual(
        crease_pattern.get_non_overlapping_creases(large_input), ref_large
    )

    cp = crease_pattern.CreasePattern(creases=creases, grid_size=16)
    # Verify spatial-grid `create_vertices_from_tips` matches exact linear scan.
    ref_vertices: list[tuple[point.Point, int]] = []
    for c1 in cp.creases:
      if c1.fold == crease.Fold.TRIANGLE:
        continue
      for p in (c1.p1, c1.p2):
        idx = next(
            (
                i
                for i, (vp, _) in enumerate(ref_vertices)
                if vp.isclose(p, atol=cp.tolerance)
            ),
            -1,
        )
        if idx < 0:
          ref_vertices.append((p, 1))
        else:
          vp, cnt = ref_vertices[idx]
          ref_vertices[idx] = (vp, cnt + 1)
    ref_vertices.sort(key=lambda item: (item[0].norm, item[0].x, item[0].y))
    self.assertLen(cp.vertices, len(ref_vertices))
    for got_v, (exp_p, exp_cnt) in zip(cp.vertices, ref_vertices):
      self.assertEqual(got_v.point, exp_p)
      self.assertLen(got_v.creases, exp_cnt)


if __name__ == '__main__':
  absltest.main()
