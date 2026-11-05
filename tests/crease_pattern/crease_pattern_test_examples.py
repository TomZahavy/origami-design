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

"""Contains crease pattern examples for Origami Discovery tests."""

import dataclasses
import enum


class CreasePatternType(enum.Enum):
  """This enum contains the different types of variants.

  WEB: a Crease pattern from the web.
  TEST: a test case.
  """

  WEB = 'web'
  TEST = 'test'


@dataclasses.dataclass(frozen=True)
class CreasePatternTestExample:
  """Contains a single variant of a problem."""

  name: str
  xml: str
  crease_pattern_type: CreasePatternType
  source: str | None = None
  valid_xml: bool = True
  valid_svg: bool = True
  valid_crease_pattern: bool = True
  flat_foldable: bool = True
  maekawa_foldable: bool = True
  blb_foldable: bool = True
  kawasaki_foldable: bool = True
  crimp_foldable: bool = True
  invalid_ratio: float = 0.0


def get_test_examples() -> list[CreasePatternTestExample]:
  """Returns the test examples."""
  return _TEST_EXAMPLES


_CP_PAIRS = [
    [
        CreasePatternTestExample(
            name='11',
            xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2 2"><rect stroke="black" x="0" y="0" width="2" height="2" /><line stroke="#f00" opacity="1" x1="0" y1="0" x2="1" y2="1"/><line stroke="#f00" opacity="1" x1="1" y1="1" x2="2" y2="2"/></svg>""",
            crease_pattern_type=CreasePatternType.TEST,
        ),
        CreasePatternTestExample(
            name='21',
            xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2 2"><rect stroke="black" x="0" y="0" width="2" height="2" /><line stroke="#f00" opacity="1" x1="0" y1="0" x2="2" y2="1"/></svg>""",
            crease_pattern_type=CreasePatternType.TEST,
        ),
    ],
]


_TEST_EXAMPLES: list[CreasePatternTestExample] = [
    CreasePatternTestExample(
        name='invalidsvg_1',
        xml=(
            '<svg xmlns="http://www.w3.org/2000/svg"'
            ' viewBox="1270.7930000000001 2998.793 914.4839999999997'
            ' 914.414"></svg>'
        ),
        crease_pattern_type=CreasePatternType.TEST,
        valid_svg=False,
    ),
    CreasePatternTestExample(
        name='invalidsvg_2',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBoxer="1270.7930000000001 2998.793 914.4839999999997 914.414"><line stroke="#000" opacity="1" x1="1982.401" y1="3836.93" x2="2109.0699999999997" y2="3836.929" stroke-width="2.5402333333333322"/></svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        valid_svg=False,
    ),
    CreasePatternTestExample(
        name='invalidsvg_3',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="1270.7930000000001 2998.793 914.4839999999997 914.414" 914.414"><line stroke="#000" opacity="1" x1="1982.401" y1="3836.93" x2="2109.0699999999997" y2="3836.929" stroke-width="2.5402333333333322"/></svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        valid_svg=False,
        valid_xml=False,
    ),
    CreasePatternTestExample(
        name='invalidsvg_4',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="1270.7930000000001 2998.793 914.4839999999997 914.414" 914.414"><lines stroke="#000" opacity="1" x1="1982.401" y1="3836.93" x2="2109.0699999999997" y2="3836.929" stroke-width="2.5402333333333322"/></svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        valid_svg=False,
        valid_xml=False,
    ),
    CreasePatternTestExample(
        name='invalidsvg_5',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="1270.7930000000001 2998.793 914.4839999999997 914.414" 914.414"><line strokes="#000" opacity="1" x1="1982.401" y1="3836.93" x2="2109.0699999999997" y2="3836.929" stroke-width="2.5402333333333322"/></svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        valid_svg=False,
        valid_xml=False,
    ),
    CreasePatternTestExample(
        name='invalidxml_encoding_declaration',
        xml="""<?xml version="1.0" encoding="utf-8"?><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><rect stroke="black" x="0" y="0" width="200" height="200" /><line stroke="red" x1="100" y1="100" x2="50" y2="50" /><line stroke="red" x1="50" y1="50" x2="0" y2="50" /><line stroke="red" x1="50" y1="50" x2="100" y2="50" /><line stroke="red" x1="100" y1="50" x2="150" y2="50" /><line stroke="red" x1="150" y1="50" x2="200" y2="50" /><line stroke="blue" x1="50" y1="100" x2="50" y2="0" /><line stroke="blue" x1="50" y1="50" x2="150" y2="50" /><line stroke="blue" x1="150" y1="150" x2="150" y2="100" /><line stroke="blue" x1="150" y1="100" x2="100" y2="50" /><line stroke="red" x1="150" y1="50" x2="100" y2="0" /><line stroke="red" x1="100" y1="0" x2="50" y2="0" /></svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        valid_xml=False,
        valid_svg=False,
    ),
    CreasePatternTestExample(
        name='invalidxml_1',
        xml="""svg xmlns="http://www.w3.org/2000/svg" viewBox="1270.7930000000001 2998.793 914.4839999999997 914.414"><line stroke="#000" opacity="1" x1="1982.401" y1="3836.93" x2="2109.0699999999997" y2="3836.929" stroke-width="2.5402333333333322"/></svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        valid_xml=False,
    ),
    CreasePatternTestExample(
        name='invalidxml_2',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="1270.7930000000001 2998.793 914.4839999999997 914.414"><line stroke="#000" opacity="1" x1="1982.401" y1="3836.93" x2="2109.0699999999997" y2="3836.929" stroke-width="2.5402333333333322"</svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        valid_xml=False,
    ),
    CreasePatternTestExample(
        name='invalidxml_3',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="1270.7930000000001 2998.793 914.4839999999997 914.414"><line stroke="#000" opacity="1" x1="1982.401" y1="3836.93" x2="2109.0699999999997" y2="3836.929" stroke-width="2.5402333333333322"/>""",
        crease_pattern_type=CreasePatternType.TEST,
        valid_xml=False,
    ),
    CreasePatternTestExample(
        name='overlapping_creases',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect stroke="black" x="0" y="0" width="100" height="100" /><line stroke="#f00" opacity="1" x1="0" y1="0" x2="100" y2="100" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="100" y2="100" stroke-width="2"/></svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        invalid_ratio=0.166,
    ),
    CreasePatternTestExample(
        name='overlapping_creases_2',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><line stroke="#f00" opacity="1" x1="0" y1="0" x2="100" y2="100" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="110" y2="110" stroke-width="2"/></svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        valid_crease_pattern=False,
    ),
    CreasePatternTestExample(
        name='coincident_creases',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect stroke="black" x="0" y="0" width="100" height="100" /><line stroke="#f00" opacity="1" x1="50" y1="50" x2="100" y2="100" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="100" y2="100" stroke-width="2"/></svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        invalid_ratio=0.1666,
        maekawa_foldable=False,
        kawasaki_foldable=False,
        flat_foldable=False,
        crimp_foldable=False,
    ),
    CreasePatternTestExample(
        name='simple_svg',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><line stroke="#f00" opacity="1" x1="50" y1="50" x2="100" y2="50" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="50" y2="100" stroke-width="2"/><line stroke="#f00" opacity="1" x1="50" y1="50" x2="0" y2="50" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="50" y2="0" stroke-width="2"/> <rect stroke="black" x="0" y="0" width="100" height="100" /> </svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        maekawa_foldable=False,
        crimp_foldable=False,
        flat_foldable=False,
    ),
    CreasePatternTestExample(
        name='simple_svg_no_namespace',
        xml="""<svg viewBox="0 0 100 100"><line stroke="#f00" opacity="1" x1="50" y1="50" x2="100" y2="50" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="50" y2="100" stroke-width="2"/><line stroke="#f00" opacity="1" x1="50" y1="50" x2="0" y2="50" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="50" y2="0" stroke-width="2"/> <rect stroke="black" x="0" y="0" width="100" height="100" /> </svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        maekawa_foldable=False,
        crimp_foldable=False,
        flat_foldable=False,
    ),
    CreasePatternTestExample(
        name='simple_svg_group',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><g><line stroke="#f00" opacity="1" x1="50" y1="50" x2="100" y2="50" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="50" y2="100" stroke-width="2"/><line stroke="#f00" opacity="1" x1="50" y1="50" x2="0" y2="50" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="50" y2="0" stroke-width="2"/></g> <rect stroke="black" x="0" y="0" width="100" height="100" /> </svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        maekawa_foldable=False,
        crimp_foldable=False,
        flat_foldable=False,
    ),
    CreasePatternTestExample(
        name='three_creases_svg',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect stroke="black" x="0" y="0" width="100" height="100" /><line stroke="#f00" opacity="1" x1="50" y1="50" x2="100" y2="50" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="50" y2="100" stroke-width="2"/><line stroke="#f00" opacity="1" x1="50" y1="50" x2="0" y2="50" stroke-width="2"/></svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        maekawa_foldable=False,
        crimp_foldable=False,
        flat_foldable=False,
        kawasaki_foldable=False,
    ),
    CreasePatternTestExample(
        name='non_flat_svg',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><line stroke="#00f" opacity="1" x1="50" y1="50" x2="100" y2="50" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="70" y2="100" stroke-width="2"/><line stroke="#f00" opacity="1" x1="50" y1="50" x2="0" y2="50" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="50" y2="0" stroke-width="2"/> <rect stroke="black" x="0" y="0" width="100" height="100" /> </svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        blb_foldable=False,
        kawasaki_foldable=False,
        flat_foldable=False,
    ),
    CreasePatternTestExample(
        name='six_creases_svg',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><line stroke="#f00" opacity="1" x1="50" y1="50" x2="100" y2="50" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="75" y2="93.3" stroke-width="2"/><line stroke="#f00" opacity="1" x1="50" y1="50" x2="25" y2="93.3" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="0" y2="50" stroke-width="2"/><line stroke="#f00" opacity="1" x1="50" y1="50" x2="25" y2="6.7" stroke-width="2"/>    <line stroke="#00f" opacity="1" x1="50" y1="50" x2="75" y2="6.7" stroke-width="2"/> <rect stroke="black" x="0" y="0" width="100" height="100" /> </svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        flat_foldable=False,
        maekawa_foldable=False,
        crimp_foldable=False,
        kawasaki_foldable=False,
    ),
    CreasePatternTestExample(
        name='two_lines_svg',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><line stroke="#f00" opacity="1" x1="0" y1="0" x2="100" y2="100" stroke-width="2"/><line stroke="#00f" opacity="1" x1="0" y1="100" x2="100" y2="0" stroke-width="2"/> <rect stroke="black" x="0" y="0" width="100" height="100" /> </svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        flat_foldable=False,
        crimp_foldable=False,
        maekawa_foldable=False,
    ),
    CreasePatternTestExample(
        name='five_lines_svg',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect stroke="black" x="0" y="0" width="100" height="100" /><line stroke="#f00" opacity="1" x1="50" y1="50" x2="100" y2="50" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="50" y2="100" stroke-width="2"/><line stroke="#f00" opacity="1" x1="50" y1="50" x2="0" y2="50" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="50" y2="0" stroke-width="2"/><line stroke="#f00" opacity="1" x1="50" y1="50" x2="80" y2="20" stroke-width="2"/></svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        flat_foldable=False,
        crimp_foldable=False,
        maekawa_foldable=False,
        kawasaki_foldable=False,
    ),
    CreasePatternTestExample(
        name='eight_lines_svg',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><line stroke="#f00" opacity="1" x1="100" y1="100" x2="150" y2="100" stroke-width="2"/><line stroke="#00f" opacity="1" x1="100" y1="100" x2="100" y2="150" stroke-width="2"/><line stroke="#f00" opacity="1" x1="100" y1="100" x2="50" y2="100" stroke-width="2"/><line stroke="#00f" opacity="1" x1="100" y1="100" x2="100" y2="50" stroke-width="2"/><line stroke="#f00" opacity="1" x1="100" y1="100" x2="135.35" y2="64.64" stroke-width="2"/><line stroke="#00f" opacity="1" x1="100" y1="100" x2="64.64" y2="135.35" stroke-width="2"/><line stroke="#f00" opacity="1" x1="100" y1="100" x2="64.64" y2="64.64" stroke-width="2"/><line stroke="#00f" opacity="1" x1="100" y1="100" x2="135.35" y2="135.35" stroke-width="2"/> <rect stroke="black" x="0" y="0" width="200" height="200" /> </svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        flat_foldable=False,
        maekawa_foldable=False,
        crimp_foldable=False,
        kawasaki_foldable=False,
    ),
    CreasePatternTestExample(
        name='min_angle_pass_svg',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><line stroke="#f00" opacity="1" x1="50" y1="50" x2="100" y2="50" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="50" y2="100" stroke-width="2"/><line stroke="#f00" opacity="1" x1="50" y1="50" x2="0" y2="50" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="60" y2="40" stroke-width="2"/> <rect stroke="black" x="0" y="0" width="100" height="100" /> </svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        flat_foldable=False,
        maekawa_foldable=False,
        crimp_foldable=False,
        kawasaki_foldable=False,
    ),
    CreasePatternTestExample(
        name='min_angle_smaller_pass_svg',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect stroke="black" x="0" y="0" width="100" height="100" /><line stroke="#f00" opacity="1" x1="50" y1="50" x2="100" y2="50" stroke-width="2"/>  <line stroke="#00f" opacity="1" x1="50" y1="50" x2="85" y2="85" stroke-width="2"/>  <line stroke="#f00" opacity="1" x1="50" y1="50" x2="0" y2="50" stroke-width="2"/>    <line stroke="#00f" opacity="1" x1="50" y1="50" x2="50" y2="0" stroke-width="2"/></svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        flat_foldable=False,
        maekawa_foldable=False,
        crimp_foldable=False,
        kawasaki_foldable=False,
    ),
    CreasePatternTestExample(
        name='min_angle_smaller_fail_svg',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><line stroke="#f00" opacity="1" x1="50" y1="50" x2="100" y2="50" stroke-width="2"/>  <line stroke="#f00" opacity="1" x1="50" y1="50" x2="85" y2="85" stroke-width="2"/>  <line stroke="#f00" opacity="1" x1="50" y1="50" x2="0" y2="50" stroke-width="2"/>    <line stroke="#00f" opacity="1" x1="50" y1="50" x2="50" y2="0" stroke-width="2"/> <rect stroke="black" x="0" y="0" width="100" height="100" /> </svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        flat_foldable=False,
        blb_foldable=False,
        kawasaki_foldable=False,
        crimp_foldable=False,
        maekawa_foldable=False,
    ),
    CreasePatternTestExample(
        name='all_same_type_svg',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect stroke="black" x="0" y="0" width="100" height="100" /><line stroke="#00f" opacity="1" x1="50" y1="50" x2="100" y2="50" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="50" y2="100" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="0" y2="50" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="60" y2="40" stroke-width="2"/></svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        flat_foldable=False,
        blb_foldable=False,
        maekawa_foldable=False,
        crimp_foldable=False,
        kawasaki_foldable=False,
    ),
    CreasePatternTestExample(
        name='two_creases_svg',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><line stroke="#f00" opacity="1" x1="50" y1="50" x2="100" y2="50" stroke-width="2"/><line stroke="#00f" opacity="1" x1="50" y1="50" x2="50" y2="100" stroke-width="2"/> <rect stroke="black" x="0" y="0" width="100" height="100" /> </svg>""",
        crease_pattern_type=CreasePatternType.TEST,
        flat_foldable=False,
        maekawa_foldable=False,
        crimp_foldable=False,
        kawasaki_foldable=False,
    ),
    CreasePatternTestExample(
        name='scorpion_base',
        source='synthetic',
        xml="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
              <line stroke="red" x1="0" y1="0" x2="31" y2="31"/>
              <line stroke="black" x1="0" y1="0" x2="125" y2="0"/>
              <line stroke="black" x1="0" y1="0" x2="0" y2="250"/>
              <line stroke="blue" x1="31" y1="31" x2="62" y2="62"/>
              <line stroke="red" x1="31" y1="31" x2="125" y2="31"/>
              <line stroke="red" x1="31" y1="31" x2="31" y2="250"/>
              <line stroke="red" x1="62" y1="62" x2="94" y2="94"/>
              <line stroke="blue" x1="62" y1="62" x2="125" y2="62"/>
              <line stroke="blue" x1="62" y1="62" x2="62" y2="250"/>
              <line stroke="blue" x1="125" y1="0" x2="125" y2="31"/>
              <line stroke="black" x1="125" y1="0" x2="250" y2="0"/>
              <line stroke="red" x1="125" y1="31" x2="125" y2="62"/>
              <line stroke="red" x1="125" y1="31" x2="219" y2="31"/>
              <line stroke="red" x1="94" y1="94" x2="125" y2="94"/>
              <line stroke="blue" x1="94" y1="94" x2="125" y2="125"/>
              <line stroke="red" x1="94" y1="94" x2="94" y2="250"/>
              <line stroke="blue" x1="125" y1="62" x2="125" y2="94"/>
              <line stroke="blue" x1="125" y1="62" x2="188" y2="62"/>
              <line stroke="red" x1="125" y1="94" x2="125" y2="125"/>
              <line stroke="red" x1="125" y1="94" x2="156" y2="94"/>
              <line stroke="blue" x1="125" y1="125" x2="156" y2="94"/>
              <line stroke="blue" x1="125" y1="125" x2="125" y2="250"/>
              <line stroke="red" x1="156" y1="94" x2="188" y2="62"/>
              <line stroke="red" x1="156" y1="94" x2="156" y2="250"/>
              <line stroke="blue" x1="188" y1="62" x2="219" y2="31"/>
              <line stroke="blue" x1="188" y1="62" x2="188" y2="250"/>
              <line stroke="red" x1="219" y1="31" x2="250" y2="0"/>
              <line stroke="red" x1="219" y1="31" x2="219" y2="250"/>
              <line stroke="blue" x1="0" y1="250" x2="31" y2="250"/>
              <line stroke="black" x1="0" y1="250" x2="0" y2="375"/>
              <line stroke="red" x1="250" y1="0" x2="281" y2="31"/>
              <line stroke="blue" x1="250" y1="0" x2="250" y2="250"/>
              <line stroke="black" x1="250" y1="0" x2="500" y2="0"/>
              <line stroke="red" x1="31" y1="250" x2="62" y2="250"/>
              <line stroke="red" x1="31" y1="250" x2="31" y2="344"/>
              <line stroke="blue" x1="62" y1="250" x2="94" y2="250"/>
              <line stroke="blue" x1="62" y1="250" x2="62" y2="312"/>
              <line stroke="red" x1="94" y1="250" x2="125" y2="250"/>
              <line stroke="red" x1="94" y1="250" x2="94" y2="281"/>
              <line stroke="blue" x1="125" y1="250" x2="156" y2="250"/>
              <line stroke="blue" x1="125" y1="250" x2="94" y2="281"/>
              <line stroke="red" x1="125" y1="250" x2="125" y2="281"/>
              <line stroke="blue" x1="125" y1="250" x2="156" y2="281"/>
              <line stroke="blue" x1="281" y1="31" x2="312" y2="62"/>
              <line stroke="red" x1="281" y1="31" x2="281" y2="250"/>
              <line stroke="red" x1="281" y1="31" x2="469" y2="31"/>
              <line stroke="red" x1="156" y1="250" x2="188" y2="250"/>
              <line stroke="red" x1="156" y1="250" x2="156" y2="281"/>
              <line stroke="red" x1="94" y1="281" x2="125" y2="281"/>
              <line stroke="red" x1="94" y1="281" x2="62" y2="312"/>
              <line stroke="red" x1="125" y1="281" x2="156" y2="281"/>
              <line stroke="blue" x1="125" y1="281" x2="125" y2="312"/>
              <line stroke="blue" x1="188" y1="250" x2="219" y2="250"/>
              <line stroke="blue" x1="188" y1="250" x2="188" y2="312"/>
              <line stroke="blue" x1="62" y1="312" x2="125" y2="312"/>
              <line stroke="blue" x1="62" y1="312" x2="31" y2="344"/>
              <line stroke="red" x1="312" y1="62" x2="344" y2="94"/>
              <line stroke="blue" x1="312" y1="62" x2="312" y2="250"/>
              <line stroke="blue" x1="312" y1="62" x2="500" y2="62"/>
              <line stroke="red" x1="156" y1="281" x2="188" y2="312"/>
              <line stroke="red" x1="219" y1="250" x2="250" y2="250"/>
              <line stroke="red" x1="219" y1="250" x2="219" y2="344"/>
              <line stroke="blue" x1="125" y1="312" x2="188" y2="312"/>
              <line stroke="red" x1="125" y1="312" x2="125" y2="344"/>
              <line stroke="red" x1="31" y1="344" x2="125" y2="344"/>
              <line stroke="red" x1="31" y1="344" x2="0" y2="375"/>
              <line stroke="blue" x1="250" y1="250" x2="281" y2="250"/>
              <line stroke="blue" x1="250" y1="250" x2="250" y2="375"/>
              <line stroke="blue" x1="344" y1="94" x2="375" y2="125"/>
              <line stroke="red" x1="344" y1="94" x2="344" y2="250"/>
              <line stroke="red" x1="344" y1="94" x2="469" y2="94"/>
              <line stroke="blue" x1="188" y1="312" x2="219" y2="344"/>
              <line stroke="blue" x1="125" y1="344" x2="125" y2="375"/>
              <line stroke="red" x1="125" y1="344" x2="219" y2="344"/>
              <line stroke="blue" x1="0" y1="375" x2="125" y2="375"/>
              <line stroke="red" x1="0" y1="375" x2="31" y2="406"/>
              <line stroke="black" x1="0" y1="375" x2="0" y2="500"/>
              <line stroke="red" x1="281" y1="250" x2="312" y2="250"/>
              <line stroke="red" x1="281" y1="250" x2="281" y2="344"/>
              <line stroke="blue" x1="125" y1="375" x2="125" y2="406"/>
              <line stroke="red" x1="125" y1="375" x2="250" y2="375"/>
              <line stroke="red" x1="375" y1="125" x2="406" y2="156"/>
              <line stroke="blue" x1="375" y1="125" x2="375" y2="250"/>
              <line stroke="blue" x1="375" y1="125" x2="500" y2="125"/>
              <line stroke="blue" x1="312" y1="250" x2="344" y2="250"/>
              <line stroke="blue" x1="312" y1="250" x2="312" y2="312"/>
              <line stroke="red" x1="31" y1="406" x2="125" y2="406"/>
              <line stroke="blue" x1="31" y1="406" x2="62" y2="438"/>
              <line stroke="red" x1="31" y1="406" x2="31" y2="500"/>
              <line stroke="red" x1="219" y1="344" x2="250" y2="375"/>
              <line stroke="red" x1="125" y1="406" x2="125" y2="438"/>
              <line stroke="red" x1="125" y1="406" x2="219" y2="406"/>
              <line stroke="red" x1="344" y1="250" x2="344" y2="281"/>
              <line stroke="red" x1="344" y1="250" x2="375" y2="250"/>
              <line stroke="blue" x1="406" y1="156" x2="438" y2="188"/>
              <line stroke="red" x1="406" y1="156" x2="406" y2="281"/>
              <line stroke="red" x1="406" y1="156" x2="469" y2="156"/>
              <line stroke="blue" x1="312" y1="312" x2="281" y2="344"/>
              <line stroke="red" x1="312" y1="312" x2="344" y2="281"/>
              <line stroke="blue" x1="312" y1="312" x2="375" y2="312"/>
              <line stroke="blue" x1="62" y1="438" x2="125" y2="438"/>
              <line stroke="red" x1="62" y1="438" x2="94" y2="469"/>
              <line stroke="blue" x1="62" y1="438" x2="62" y2="500"/>
              <line stroke="red" x1="281" y1="344" x2="250" y2="375"/>
              <line stroke="red" x1="281" y1="344" x2="406" y2="344"/>
              <line stroke="blue" x1="344" y1="281" x2="375" y2="250"/>
              <line stroke="red" x1="344" y1="281" x2="406" y2="281"/>
              <line stroke="red" x1="250" y1="375" x2="219" y2="406"/>
              <line stroke="red" x1="250" y1="375" x2="281" y2="406"/>
              <line stroke="blue" x1="250" y1="375" x2="375" y2="375"/>
              <line stroke="blue" x1="250" y1="375" x2="250" y2="562"/>
              <line stroke="blue" x1="375" y1="250" x2="406" y2="281"/>
              <line stroke="blue" x1="125" y1="438" x2="188" y2="438"/>
              <line stroke="blue" x1="125" y1="438" x2="125" y2="469"/>
              <line stroke="blue" x1="219" y1="406" x2="188" y2="438"/>
              <line stroke="red" x1="219" y1="406" x2="219" y2="562"/>
              <line stroke="blue" x1="469" y1="31" x2="500" y2="0"/>
              <line stroke="red" x1="469" y1="31" x2="500" y2="62"/>
              <line stroke="red" x1="469" y1="31" x2="531" y2="31"/>
              <line stroke="red" x1="188" y1="438" x2="156" y2="469"/>
              <line stroke="blue" x1="188" y1="438" x2="188" y2="562"/>
              <line stroke="red" x1="438" y1="188" x2="469" y2="219"/>
              <line stroke="blue" x1="438" y1="188" x2="438" y2="281"/>
              <line stroke="blue" x1="438" y1="188" x2="500" y2="188"/>
              <line stroke="red" x1="94" y1="469" x2="125" y2="469"/>
              <line stroke="red" x1="94" y1="469" x2="94" y2="500"/>
              <line stroke="blue" x1="94" y1="469" x2="125" y2="500"/>
              <line stroke="blue" x1="469" y1="94" x2="500" y2="62"/>
              <line stroke="red" x1="469" y1="94" x2="500" y2="125"/>
              <line stroke="red" x1="469" y1="94" x2="531" y2="94"/>
              <line stroke="red" x1="125" y1="469" x2="156" y2="469"/>
              <line stroke="red" x1="125" y1="469" x2="125" y2="500"/>
              <line stroke="blue" x1="375" y1="312" x2="406" y2="281"/>
              <line stroke="red" x1="375" y1="312" x2="406" y2="312"/>
              <line stroke="blue" x1="375" y1="312" x2="406" y2="344"/>
              <line stroke="blue" x1="281" y1="406" x2="312" y2="438"/>
              <line stroke="red" x1="281" y1="406" x2="406" y2="406"/>
              <line stroke="red" x1="281" y1="406" x2="281" y2="562"/>
              <line stroke="red" x1="406" y1="281" x2="406" y2="312"/>
              <line stroke="red" x1="406" y1="281" x2="438" y2="281"/>
              <line stroke="blue" x1="156" y1="469" x2="125" y2="500"/>
              <line stroke="red" x1="156" y1="469" x2="156" y2="531"/>
              <line stroke="blue" x1="469" y1="156" x2="500" y2="125"/>
              <line stroke="red" x1="469" y1="156" x2="500" y2="188"/>
              <line stroke="red" x1="469" y1="156" x2="531" y2="156"/>
              <line stroke="blue" x1="0" y1="500" x2="31" y2="500"/>
              <line stroke="black" x1="0" y1="500" x2="0" y2="625"/>
              <line stroke="blue" x1="500" y1="0" x2="531" y2="31"/>
              <line stroke="black" x1="500" y1="0" x2="750" y2="0"/>
              <line stroke="red" x1="31" y1="500" x2="62" y2="500"/>
              <line stroke="red" x1="31" y1="500" x2="31" y2="594"/>
              <line stroke="blue" x1="500" y1="62" x2="531" y2="94"/>
              <line stroke="blue" x1="500" y1="62" x2="688" y2="62"/>
              <line stroke="blue" x1="62" y1="500" x2="94" y2="500"/>
              <line stroke="blue" x1="62" y1="500" x2="62" y2="562"/>
              <line stroke="red" x1="500" y1="62" x2="531" y2="31"/>
              <line stroke="red" x1="94" y1="500" x2="125" y2="500"/>
              <line stroke="red" x1="94" y1="500" x2="94" y2="531"/>
              <line stroke="red" x1="406" y1="312" x2="406" y2="344"/>
              <line stroke="blue" x1="406" y1="312" x2="438" y2="312"/>
              <line stroke="blue" x1="125" y1="500" x2="94" y2="531"/>
              <line stroke="blue" x1="125" y1="500" x2="156" y2="531"/>
              <line stroke="red" x1="500" y1="125" x2="531" y2="94"/>
              <line stroke="blue" x1="500" y1="125" x2="531" y2="156"/>
              <line stroke="blue" x1="500" y1="125" x2="625" y2="125"/>
              <line stroke="blue" x1="469" y1="219" x2="500" y2="188"/>
              <line stroke="red" x1="469" y1="219" x2="469" y2="281"/>
              <line stroke="red" x1="469" y1="219" x2="531" y2="219"/>
              <line stroke="blue" x1="438" y1="281" x2="438" y2="312"/>
              <line stroke="blue" x1="438" y1="281" x2="469" y2="281"/>
              <line stroke="blue" x1="375" y1="375" x2="406" y2="344"/>
              <line stroke="red" x1="375" y1="375" x2="406" y2="375"/>
              <line stroke="blue" x1="375" y1="375" x2="406" y2="406"/>
              <line stroke="red" x1="531" y1="31" x2="719" y2="31"/>
              <line stroke="red" x1="406" y1="344" x2="406" y2="375"/>
              <line stroke="red" x1="406" y1="344" x2="438" y2="344"/>
              <line stroke="red" x1="500" y1="188" x2="531" y2="156"/>
              <line stroke="blue" x1="500" y1="188" x2="531" y2="219"/>
              <line stroke="blue" x1="500" y1="188" x2="562" y2="188"/>
              <line stroke="blue" x1="312" y1="438" x2="375" y2="438"/>
              <line stroke="red" x1="312" y1="438" x2="344" y2="469"/>
              <line stroke="blue" x1="312" y1="438" x2="312" y2="562"/>
              <line stroke="blue" x1="438" y1="312" x2="438" y2="344"/>
              <line stroke="red" x1="438" y1="312" x2="469" y2="312"/>
              <line stroke="red" x1="94" y1="531" x2="156" y2="531"/>
              <line stroke="red" x1="94" y1="531" x2="62" y2="562"/>
              <line stroke="red" x1="531" y1="94" x2="656" y2="94"/>
              <line stroke="red" x1="469" y1="281" x2="469" y2="312"/>
              <line stroke="red" x1="469" y1="281" x2="531" y2="281"/>
              <line stroke="red" x1="406" y1="375" x2="406" y2="406"/>
              <line stroke="blue" x1="406" y1="375" x2="438" y2="375"/>
              <line stroke="red" x1="156" y1="531" x2="188" y2="562"/>
              <line stroke="red" x1="531" y1="156" x2="594" y2="156"/>
              <line stroke="blue" x1="438" y1="344" x2="438" y2="375"/>
              <line stroke="blue" x1="438" y1="344" x2="469" y2="344"/>
              <line stroke="red" x1="469" y1="312" x2="469" y2="344"/>
              <line stroke="blue" x1="469" y1="312" x2="531" y2="312"/>
              <line stroke="blue" x1="62" y1="562" x2="188" y2="562"/>
              <line stroke="blue" x1="62" y1="562" x2="31" y2="594"/>
              <line stroke="blue" x1="406" y1="406" x2="375" y2="438"/>
              <line stroke="red" x1="406" y1="406" x2="406" y2="438"/>
              <line stroke="red" x1="406" y1="406" x2="438" y2="406"/>
              <line stroke="red" x1="531" y1="219" x2="562" y2="188"/>
              <line stroke="red" x1="531" y1="219" x2="531" y2="281"/>
              <line stroke="red" x1="375" y1="438" x2="406" y2="438"/>
              <line stroke="blue" x1="375" y1="438" x2="406" y2="469"/>
              <line stroke="blue" x1="438" y1="375" x2="438" y2="406"/>
              <line stroke="red" x1="438" y1="375" x2="469" y2="375"/>
              <line stroke="red" x1="344" y1="469" x2="406" y2="469"/>
              <line stroke="blue" x1="344" y1="469" x2="375" y2="500"/>
              <line stroke="red" x1="344" y1="469" x2="344" y2="562"/>
              <line stroke="red" x1="469" y1="344" x2="469" y2="375"/>
              <line stroke="red" x1="469" y1="344" x2="531" y2="344"/>
              <line stroke="blue" x1="188" y1="562" x2="219" y2="562"/>
              <line stroke="red" x1="188" y1="562" x2="156" y2="594"/>
              <line stroke="blue" x1="188" y1="562" x2="188" y2="625"/>
              <line stroke="blue" x1="562" y1="188" x2="594" y2="156"/>
              <line stroke="blue" x1="562" y1="188" x2="562" y2="281"/>
              <line stroke="red" x1="31" y1="594" x2="156" y2="594"/>
              <line stroke="red" x1="31" y1="594" x2="0" y2="625"/>
              <line stroke="blue" x1="406" y1="438" x2="438" y2="438"/>
              <line stroke="red" x1="406" y1="438" x2="406" y2="469"/>
              <line stroke="blue" x1="438" y1="406" x2="438" y2="438"/>
              <line stroke="blue" x1="438" y1="406" x2="469" y2="406"/>
              <line stroke="red" x1="469" y1="375" x2="469" y2="406"/>
              <line stroke="blue" x1="469" y1="375" x2="531" y2="375"/>
              <line stroke="red" x1="531" y1="281" x2="531" y2="312"/>
              <line stroke="blue" x1="531" y1="281" x2="562" y2="281"/>
              <line stroke="red" x1="219" y1="562" x2="250" y2="562"/>
              <line stroke="red" x1="219" y1="562" x2="219" y2="625"/>
              <line stroke="blue" x1="156" y1="594" x2="125" y2="625"/>
              <line stroke="red" x1="156" y1="594" x2="156" y2="625"/>
              <line stroke="red" x1="594" y1="156" x2="625" y2="125"/>
              <line stroke="red" x1="594" y1="156" x2="594" y2="281"/>
              <line stroke="blue" x1="250" y1="562" x2="281" y2="562"/>
              <line stroke="blue" x1="250" y1="562" x2="250" y2="625"/>
              <line stroke="red" x1="531" y1="312" x2="531" y2="344"/>
              <line stroke="red" x1="531" y1="312" x2="562" y2="312"/>
              <line stroke="blue" x1="438" y1="438" x2="438" y2="469"/>
              <line stroke="red" x1="438" y1="438" x2="469" y2="438"/>
              <line stroke="blue" x1="406" y1="469" x2="375" y2="500"/>
              <line stroke="red" x1="406" y1="469" x2="438" y2="469"/>
              <line stroke="red" x1="406" y1="469" x2="406" y2="500"/>
              <line stroke="red" x1="469" y1="406" x2="469" y2="438"/>
              <line stroke="red" x1="469" y1="406" x2="531" y2="406"/>
              <line stroke="blue" x1="0" y1="625" x2="125" y2="625"/>
              <line stroke="red" x1="0" y1="625" x2="31" y2="656"/>
              <line stroke="black" x1="0" y1="625" x2="0" y2="750"/>
              <line stroke="red" x1="375" y1="500" x2="406" y2="500"/>
              <line stroke="blue" x1="375" y1="500" x2="375" y2="562"/>
              <line stroke="red" x1="281" y1="562" x2="312" y2="562"/>
              <line stroke="red" x1="281" y1="562" x2="281" y2="625"/>
              <line stroke="blue" x1="562" y1="281" x2="562" y2="312"/>
              <line stroke="red" x1="562" y1="281" x2="594" y2="281"/>
              <line stroke="red" x1="531" y1="344" x2="531" y2="375"/>
              <line stroke="blue" x1="531" y1="344" x2="562" y2="344"/>
              <line stroke="red" x1="125" y1="625" x2="156" y2="625"/>
              <line stroke="blue" x1="125" y1="625" x2="156" y2="656"/>
              <line stroke="blue" x1="625" y1="125" x2="656" y2="94"/>
              <line stroke="blue" x1="625" y1="125" x2="625" y2="250"/>
              <line stroke="blue" x1="438" y1="469" x2="469" y2="469"/>
              <line stroke="blue" x1="438" y1="469" x2="438" y2="500"/>
              <line stroke="red" x1="469" y1="438" x2="469" y2="469"/>
              <line stroke="blue" x1="469" y1="438" x2="531" y2="438"/>
              <line stroke="blue" x1="312" y1="562" x2="344" y2="562"/>
              <line stroke="blue" x1="312" y1="562" x2="312" y2="625"/>
              <line stroke="blue" x1="562" y1="312" x2="562" y2="344"/>
              <line stroke="blue" x1="562" y1="312" x2="594" y2="312"/>
              <line stroke="blue" x1="406" y1="500" x2="438" y2="500"/>
              <line stroke="red" x1="406" y1="500" x2="406" y2="562"/>
              <line stroke="blue" x1="156" y1="625" x2="188" y2="625"/>
              <line stroke="red" x1="156" y1="625" x2="156" y2="656"/>
              <line stroke="red" x1="531" y1="375" x2="531" y2="406"/>
              <line stroke="red" x1="531" y1="375" x2="562" y2="375"/>
              <line stroke="red" x1="188" y1="625" x2="219" y2="625"/>
              <line stroke="blue" x1="188" y1="625" x2="188" y2="688"/>
              <line stroke="red" x1="31" y1="656" x2="156" y2="656"/>
              <line stroke="blue" x1="31" y1="656" x2="62" y2="688"/>
              <line stroke="red" x1="31" y1="656" x2="31" y2="750"/>
              <line stroke="red" x1="594" y1="281" x2="594" y2="312"/>
              <line stroke="blue" x1="594" y1="281" x2="625" y2="250"/>
              <line stroke="blue" x1="594" y1="281" x2="625" y2="312"/>
              <line stroke="red" x1="594" y1="281" x2="656" y2="281"/>
              <line stroke="red" x1="344" y1="562" x2="375" y2="562"/>
              <line stroke="red" x1="344" y1="562" x2="344" y2="625"/>
              <line stroke="blue" x1="562" y1="344" x2="562" y2="375"/>
              <line stroke="red" x1="562" y1="344" x2="594" y2="344"/>
              <line stroke="blue" x1="219" y1="625" x2="250" y2="625"/>
              <line stroke="red" x1="219" y1="625" x2="219" y2="719"/>
              <line stroke="red" x1="656" y1="94" x2="688" y2="62"/>
              <line stroke="red" x1="656" y1="94" x2="656" y2="250"/>
              <line stroke="red" x1="469" y1="469" x2="469" y2="500"/>
              <line stroke="red" x1="469" y1="469" x2="531" y2="469"/>
              <line stroke="red" x1="438" y1="500" x2="469" y2="500"/>
              <line stroke="blue" x1="438" y1="500" x2="438" y2="562"/>
              <line stroke="red" x1="531" y1="406" x2="531" y2="438"/>
              <line stroke="blue" x1="531" y1="406" x2="562" y2="406"/>
              <line stroke="red" x1="594" y1="312" x2="594" y2="344"/>
              <line stroke="red" x1="594" y1="312" x2="625" y2="312"/>
              <line stroke="red" x1="250" y1="625" x2="281" y2="625"/>
              <line stroke="blue" x1="250" y1="625" x2="250" y2="750"/>
              <line stroke="red" x1="625" y1="250" x2="656" y2="250"/>
              <line stroke="blue" x1="625" y1="250" x2="656" y2="281"/>
              <line stroke="red" x1="156" y1="656" x2="188" y2="688"/>
              <line stroke="blue" x1="375" y1="562" x2="406" y2="562"/>
              <line stroke="blue" x1="375" y1="562" x2="375" y2="625"/>
              <line stroke="blue" x1="562" y1="375" x2="562" y2="406"/>
              <line stroke="blue" x1="562" y1="375" x2="594" y2="375"/>
              <line stroke="blue" x1="281" y1="625" x2="312" y2="625"/>
              <line stroke="red" x1="281" y1="625" x2="281" y2="781"/>
              <line stroke="blue" x1="469" y1="500" x2="531" y2="500"/>
              <line stroke="red" x1="469" y1="500" x2="469" y2="562"/>
              <line stroke="blue" x1="594" y1="344" x2="625" y2="312"/>
              <line stroke="red" x1="594" y1="344" x2="594" y2="375"/>
              <line stroke="blue" x1="594" y1="344" x2="625" y2="375"/>
              <line stroke="red" x1="594" y1="344" x2="719" y2="344"/>
              <line stroke="red" x1="531" y1="438" x2="531" y2="469"/>
              <line stroke="red" x1="531" y1="438" x2="562" y2="438"/>
              <line stroke="blue" x1="62" y1="688" x2="188" y2="688"/>
              <line stroke="red" x1="62" y1="688" x2="94" y2="719"/>
              <line stroke="blue" x1="62" y1="688" x2="62" y2="750"/>
              <line stroke="blue" x1="688" y1="62" x2="719" y2="31"/>
              <line stroke="blue" x1="688" y1="62" x2="688" y2="250"/>
              <line stroke="red" x1="406" y1="562" x2="438" y2="562"/>
              <line stroke="red" x1="406" y1="562" x2="406" y2="625"/>
              <line stroke="blue" x1="562" y1="406" x2="562" y2="438"/>
              <line stroke="red" x1="562" y1="406" x2="594" y2="406"/>
              <line stroke="red" x1="312" y1="625" x2="344" y2="625"/>
              <line stroke="blue" x1="312" y1="625" x2="312" y2="812"/>
              <line stroke="blue" x1="625" y1="312" x2="688" y2="312"/>
              <line stroke="red" x1="656" y1="250" x2="656" y2="281"/>
              <line stroke="blue" x1="656" y1="250" x2="688" y2="250"/>
              <line stroke="red" x1="594" y1="375" x2="594" y2="406"/>
              <line stroke="red" x1="594" y1="375" x2="625" y2="375"/>
              <line stroke="red" x1="531" y1="469" x2="531" y2="500"/>
              <line stroke="blue" x1="531" y1="469" x2="562" y2="469"/>
              <line stroke="blue" x1="438" y1="562" x2="469" y2="562"/>
              <line stroke="blue" x1="438" y1="562" x2="438" y2="625"/>
              <line stroke="blue" x1="562" y1="438" x2="562" y2="469"/>
              <line stroke="blue" x1="562" y1="438" x2="594" y2="438"/>
              <line stroke="blue" x1="188" y1="688" x2="219" y2="719"/>
              <line stroke="blue" x1="344" y1="625" x2="375" y2="625"/>
              <line stroke="red" x1="344" y1="625" x2="344" y2="844"/>
              <line stroke="red" x1="656" y1="281" x2="688" y2="312"/>
              <line stroke="blue" x1="594" y1="406" x2="625" y2="375"/>
              <line stroke="red" x1="594" y1="406" x2="594" y2="438"/>
              <line stroke="blue" x1="594" y1="406" x2="625" y2="438"/>
              <line stroke="red" x1="594" y1="406" x2="719" y2="406"/>
              <line stroke="red" x1="719" y1="31" x2="750" y2="0"/>
              <line stroke="red" x1="719" y1="31" x2="719" y2="250"/>
              <line stroke="red" x1="94" y1="719" x2="219" y2="719"/>
              <line stroke="red" x1="94" y1="719" x2="94" y2="750"/>
              <line stroke="blue" x1="94" y1="719" x2="125" y2="750"/>
              <line stroke="red" x1="375" y1="625" x2="406" y2="625"/>
              <line stroke="blue" x1="375" y1="625" x2="375" y2="875"/>
              <line stroke="blue" x1="625" y1="375" x2="750" y2="375"/>
              <line stroke="red" x1="531" y1="500" x2="562" y2="500"/>
              <line stroke="red" x1="531" y1="500" x2="531" y2="562"/>
              <line stroke="red" x1="469" y1="562" x2="531" y2="562"/>
              <line stroke="red" x1="469" y1="562" x2="469" y2="625"/>
              <line stroke="blue" x1="562" y1="469" x2="562" y2="500"/>
              <line stroke="red" x1="562" y1="469" x2="594" y2="469"/>
              <line stroke="blue" x1="688" y1="250" x2="688" y2="312"/>
              <line stroke="red" x1="688" y1="250" x2="719" y2="250"/>
              <line stroke="red" x1="594" y1="438" x2="594" y2="469"/>
              <line stroke="red" x1="594" y1="438" x2="625" y2="438"/>
              <line stroke="blue" x1="406" y1="625" x2="438" y2="625"/>
              <line stroke="red" x1="406" y1="625" x2="406" y2="906"/>
              <line stroke="blue" x1="0" y1="750" x2="31" y2="750"/>
              <line stroke="black" x1="0" y1="750" x2="0" y2="875"/>
              <line stroke="red" x1="750" y1="0" x2="781" y2="31"/>
              <line stroke="blue" x1="750" y1="0" x2="750" y2="250"/>
              <line stroke="black" x1="750" y1="0" x2="875" y2="0"/>
              <line stroke="red" x1="31" y1="750" x2="62" y2="750"/>
              <line stroke="red" x1="31" y1="750" x2="31" y2="844"/>
              <line stroke="red" x1="219" y1="719" x2="250" y2="750"/>
              <line stroke="blue" x1="562" y1="500" x2="594" y2="500"/>
              <line stroke="blue" x1="562" y1="500" x2="562" y2="562"/>
              <line stroke="blue" x1="62" y1="750" x2="94" y2="750"/>
              <line stroke="blue" x1="62" y1="750" x2="62" y2="812"/>
              <line stroke="blue" x1="688" y1="312" x2="719" y2="344"/>
              <line stroke="red" x1="94" y1="750" x2="125" y2="750"/>
              <line stroke="red" x1="94" y1="750" x2="94" y2="781"/>
              <line stroke="blue" x1="594" y1="469" x2="625" y2="438"/>
              <line stroke="red" x1="594" y1="469" x2="594" y2="500"/>
              <line stroke="blue" x1="594" y1="469" x2="625" y2="500"/>
              <line stroke="red" x1="594" y1="469" x2="656" y2="469"/>
              <line stroke="blue" x1="125" y1="750" x2="94" y2="781"/>
              <line stroke="blue" x1="125" y1="750" x2="250" y2="750"/>
              <line stroke="blue" x1="719" y1="250" x2="750" y2="250"/>
              <line stroke="red" x1="719" y1="250" x2="719" y2="344"/>
              <line stroke="red" x1="438" y1="625" x2="469" y2="625"/>
              <line stroke="blue" x1="438" y1="625" x2="438" y2="938"/>
              <line stroke="blue" x1="625" y1="438" x2="688" y2="438"/>
              <line stroke="blue" x1="531" y1="562" x2="562" y2="562"/>
              <line stroke="red" x1="531" y1="562" x2="531" y2="625"/>
              <line stroke="red" x1="594" y1="500" x2="625" y2="500"/>
              <line stroke="red" x1="594" y1="500" x2="594" y2="562"/>
              <line stroke="blue" x1="469" y1="625" x2="531" y2="625"/>
              <line stroke="red" x1="469" y1="625" x2="469" y2="969"/>
              <line stroke="blue" x1="781" y1="31" x2="812" y2="62"/>
              <line stroke="red" x1="781" y1="31" x2="781" y2="250"/>
              <line stroke="red" x1="781" y1="31" x2="875" y2="31"/>
              <line stroke="red" x1="94" y1="781" x2="62" y2="812"/>
              <line stroke="red" x1="94" y1="781" x2="281" y2="781"/>
              <line stroke="blue" x1="250" y1="750" x2="281" y2="781"/>
              <line stroke="red" x1="750" y1="250" x2="781" y2="250"/>
              <line stroke="blue" x1="750" y1="250" x2="750" y2="375"/>
              <line stroke="red" x1="562" y1="562" x2="594" y2="562"/>
              <line stroke="blue" x1="562" y1="562" x2="562" y2="625"/>
              <line stroke="red" x1="719" y1="344" x2="750" y2="375"/>
              <line stroke="blue" x1="625" y1="500" x2="656" y2="469"/>
              <line stroke="blue" x1="625" y1="500" x2="625" y2="562"/>
              <line stroke="red" x1="656" y1="469" x2="688" y2="438"/>
              <line stroke="red" x1="656" y1="469" x2="656" y2="562"/>
              <line stroke="blue" x1="62" y1="812" x2="31" y2="844"/>
              <line stroke="blue" x1="62" y1="812" x2="312" y2="812"/>
              <line stroke="red" x1="812" y1="62" x2="844" y2="94"/>
              <line stroke="blue" x1="812" y1="62" x2="812" y2="250"/>
              <line stroke="blue" x1="812" y1="62" x2="875" y2="62"/>
              <line stroke="blue" x1="688" y1="438" x2="719" y2="406"/>
              <line stroke="blue" x1="688" y1="438" x2="688" y2="562"/>
              <line stroke="blue" x1="594" y1="562" x2="625" y2="562"/>
              <line stroke="red" x1="594" y1="562" x2="594" y2="625"/>
              <line stroke="blue" x1="781" y1="250" x2="812" y2="250"/>
              <line stroke="red" x1="781" y1="250" x2="781" y2="344"/>
              <line stroke="red" x1="531" y1="625" x2="562" y2="625"/>
              <line stroke="red" x1="531" y1="625" x2="531" y2="969"/>
              <line stroke="red" x1="719" y1="406" x2="750" y2="375"/>
              <line stroke="red" x1="719" y1="406" x2="719" y2="562"/>
              <line stroke="red" x1="281" y1="781" x2="312" y2="812"/>
              <line stroke="red" x1="750" y1="375" x2="781" y2="344"/>
              <line stroke="red" x1="750" y1="375" x2="781" y2="406"/>
              <line stroke="blue" x1="750" y1="375" x2="750" y2="562"/>
              <line stroke="red" x1="750" y1="375" x2="875" y2="375"/>
              <line stroke="blue" x1="562" y1="625" x2="594" y2="625"/>
              <line stroke="blue" x1="562" y1="625" x2="562" y2="938"/>
              <line stroke="red" x1="625" y1="562" x2="656" y2="562"/>
              <line stroke="blue" x1="625" y1="562" x2="625" y2="625"/>
              <line stroke="red" x1="31" y1="844" x2="0" y2="875"/>
              <line stroke="red" x1="31" y1="844" x2="344" y2="844"/>
              <line stroke="red" x1="844" y1="94" x2="875" y2="94"/>
              <line stroke="red" x1="844" y1="94" x2="844" y2="250"/>
              <line stroke="blue" x1="844" y1="94" x2="875" y2="125"/>
              <line stroke="blue" x1="812" y1="250" x2="812" y2="312"/>
              <line stroke="red" x1="812" y1="250" x2="844" y2="250"/>
              <line stroke="blue" x1="781" y1="344" x2="812" y2="312"/>
              <line stroke="red" x1="781" y1="344" x2="875" y2="344"/>
              <line stroke="red" x1="594" y1="625" x2="625" y2="625"/>
              <line stroke="red" x1="594" y1="625" x2="594" y2="906"/>
              <line stroke="blue" x1="656" y1="562" x2="688" y2="562"/>
              <line stroke="red" x1="656" y1="562" x2="656" y2="625"/>
              <line stroke="blue" x1="312" y1="812" x2="344" y2="844"/>
              <line stroke="red" x1="812" y1="312" x2="844" y2="281"/>
              <line stroke="blue" x1="812" y1="312" x2="875" y2="312"/>
              <line stroke="red" x1="0" y1="875" x2="31" y2="906"/>
              <line stroke="blue" x1="0" y1="875" x2="375" y2="875"/>
              <line stroke="black" x1="0" y1="875" x2="0" y2="1000"/>
              <line stroke="blue" x1="875" y1="0" x2="875" y2="31"/>
              <line stroke="black" x1="875" y1="0" x2="1000" y2="0"/>
              <line stroke="red" x1="875" y1="31" x2="875" y2="62"/>
              <line stroke="red" x1="875" y1="31" x2="969" y2="31"/>
              <line stroke="blue" x1="875" y1="62" x2="875" y2="94"/>
              <line stroke="blue" x1="875" y1="62" x2="938" y2="62"/>
              <line stroke="red" x1="875" y1="94" x2="875" y2="125"/>
              <line stroke="red" x1="875" y1="94" x2="906" y2="94"/>
              <line stroke="blue" x1="781" y1="406" x2="812" y2="438"/>
              <line stroke="red" x1="781" y1="406" x2="781" y2="562"/>
              <line stroke="red" x1="781" y1="406" x2="875" y2="406"/>
              <line stroke="red" x1="844" y1="250" x2="844" y2="281"/>
              <line stroke="blue" x1="844" y1="250" x2="875" y2="250"/>
              <line stroke="blue" x1="625" y1="625" x2="656" y2="625"/>
              <line stroke="blue" x1="625" y1="625" x2="625" y2="875"/>
              <line stroke="blue" x1="875" y1="125" x2="875" y2="250"/>
              <line stroke="blue" x1="875" y1="125" x2="906" y2="94"/>
              <line stroke="red" x1="688" y1="562" x2="719" y2="562"/>
              <line stroke="blue" x1="688" y1="562" x2="688" y2="625"/>
              <line stroke="blue" x1="844" y1="281" x2="875" y2="250"/>
              <line stroke="red" x1="844" y1="281" x2="875" y2="281"/>
              <line stroke="red" x1="656" y1="625" x2="688" y2="625"/>
              <line stroke="red" x1="656" y1="625" x2="656" y2="844"/>
              <line stroke="blue" x1="31" y1="906" x2="62" y2="938"/>
              <line stroke="red" x1="31" y1="906" x2="406" y2="906"/>
              <line stroke="red" x1="31" y1="906" x2="31" y2="1000"/>
              <line stroke="red" x1="875" y1="250" x2="875" y2="281"/>
              <line stroke="red" x1="875" y1="250" x2="906" y2="250"/>
              <line stroke="blue" x1="875" y1="250" x2="906" y2="281"/>
              <line stroke="red" x1="906" y1="94" x2="906" y2="250"/>
              <line stroke="red" x1="906" y1="94" x2="938" y2="62"/>
              <line stroke="red" x1="344" y1="844" x2="375" y2="875"/>
              <line stroke="blue" x1="719" y1="562" x2="750" y2="562"/>
              <line stroke="red" x1="719" y1="562" x2="719" y2="625"/>
              <line stroke="blue" x1="875" y1="281" x2="875" y2="312"/>
              <line stroke="red" x1="875" y1="281" x2="906" y2="281"/>
              <line stroke="red" x1="812" y1="438" x2="844" y2="469"/>
              <line stroke="blue" x1="812" y1="438" x2="875" y2="438"/>
              <line stroke="blue" x1="812" y1="438" x2="812" y2="562"/>
              <line stroke="red" x1="875" y1="312" x2="875" y2="344"/>
              <line stroke="blue" x1="875" y1="312" x2="938" y2="312"/>
              <line stroke="blue" x1="688" y1="625" x2="719" y2="625"/>
              <line stroke="blue" x1="688" y1="625" x2="688" y2="812"/>
              <line stroke="red" x1="750" y1="562" x2="781" y2="562"/>
              <line stroke="blue" x1="750" y1="562" x2="750" y2="625"/>
              <line stroke="red" x1="906" y1="250" x2="906" y2="281"/>
              <line stroke="blue" x1="906" y1="250" x2="938" y2="250"/>
              <line stroke="red" x1="62" y1="938" x2="94" y2="969"/>
              <line stroke="blue" x1="62" y1="938" x2="62" y2="1000"/>
              <line stroke="blue" x1="62" y1="938" x2="438" y2="938"/>
              <line stroke="blue" x1="938" y1="62" x2="969" y2="31"/>
              <line stroke="blue" x1="938" y1="62" x2="938" y2="250"/>
              <line stroke="blue" x1="875" y1="344" x2="875" y2="375"/>
              <line stroke="red" x1="875" y1="344" x2="969" y2="344"/>
              <line stroke="red" x1="906" y1="281" x2="938" y2="312"/>
              <line stroke="blue" x1="375" y1="875" x2="406" y2="906"/>
              <line stroke="blue" x1="875" y1="375" x2="875" y2="406"/>
              <line stroke="blue" x1="875" y1="375" x2="1000" y2="375"/>
              <line stroke="red" x1="719" y1="625" x2="750" y2="625"/>
              <line stroke="red" x1="719" y1="625" x2="719" y2="781"/>
              <line stroke="blue" x1="781" y1="562" x2="812" y2="562"/>
              <line stroke="red" x1="781" y1="562" x2="781" y2="625"/>
              <line stroke="red" x1="875" y1="406" x2="875" y2="438"/>
              <line stroke="red" x1="875" y1="406" x2="969" y2="406"/>
              <line stroke="red" x1="844" y1="469" x2="875" y2="469"/>
              <line stroke="red" x1="844" y1="469" x2="844" y2="531"/>
              <line stroke="blue" x1="844" y1="469" x2="875" y2="500"/>
              <line stroke="red" x1="969" y1="31" x2="1000" y2="0"/>
              <line stroke="red" x1="969" y1="31" x2="969" y2="250"/>
              <line stroke="blue" x1="938" y1="250" x2="938" y2="312"/>
              <line stroke="red" x1="938" y1="250" x2="969" y2="250"/>
              <line stroke="red" x1="94" y1="969" x2="94" y2="1000"/>
              <line stroke="blue" x1="94" y1="969" x2="125" y2="1000"/>
              <line stroke="red" x1="94" y1="969" x2="469" y2="969"/>
              <line stroke="blue" x1="750" y1="625" x2="781" y2="625"/>
              <line stroke="blue" x1="750" y1="625" x2="750" y2="750"/>
              <line stroke="blue" x1="875" y1="438" x2="875" y2="469"/>
              <line stroke="blue" x1="875" y1="438" x2="938" y2="438"/>
              <line stroke="red" x1="812" y1="562" x2="844" y2="531"/>
              <line stroke="blue" x1="812" y1="562" x2="812" y2="625"/>
              <line stroke="red" x1="812" y1="562" x2="844" y2="594"/>
              <line stroke="blue" x1="812" y1="562" x2="938" y2="562"/>
              <line stroke="blue" x1="938" y1="312" x2="969" y2="344"/>
              <line stroke="red" x1="875" y1="469" x2="875" y2="500"/>
              <line stroke="red" x1="875" y1="469" x2="906" y2="469"/>
              <line stroke="red" x1="406" y1="906" x2="438" y2="938"/>
              <line stroke="blue" x1="844" y1="531" x2="875" y2="500"/>
              <line stroke="red" x1="844" y1="531" x2="906" y2="531"/>
              <line stroke="black" x1="0" y1="1000" x2="31" y2="1000"/>
              <line stroke="black" x1="1000" y1="0" x2="1000" y2="250"/>
              <line stroke="red" x1="781" y1="625" x2="812" y2="625"/>
              <line stroke="red" x1="781" y1="625" x2="781" y2="719"/>
              <line stroke="black" x1="31" y1="1000" x2="62" y2="1000"/>
              <line stroke="red" x1="969" y1="250" x2="969" y2="344"/>
              <line stroke="blue" x1="969" y1="250" x2="1000" y2="250"/>
              <line stroke="black" x1="62" y1="1000" x2="94" y2="1000"/>
              <line stroke="black" x1="94" y1="1000" x2="125" y2="1000"/>
              <line stroke="black" x1="125" y1="1000" x2="500" y2="1000"/>
              <line stroke="blue" x1="875" y1="500" x2="906" y2="469"/>
              <line stroke="red" x1="875" y1="500" x2="906" y2="500"/>
              <line stroke="blue" x1="875" y1="500" x2="906" y2="531"/>
              <line stroke="red" x1="906" y1="469" x2="906" y2="500"/>
              <line stroke="red" x1="906" y1="469" x2="938" y2="438"/>
              <line stroke="blue" x1="812" y1="625" x2="844" y2="625"/>
              <line stroke="blue" x1="812" y1="625" x2="812" y2="688"/>
              <line stroke="red" x1="969" y1="344" x2="1000" y2="375"/>
              <line stroke="black" x1="1000" y1="250" x2="1000" y2="375"/>
              <line stroke="red" x1="844" y1="594" x2="844" y2="625"/>
              <line stroke="blue" x1="844" y1="594" x2="875" y2="625"/>
              <line stroke="red" x1="844" y1="594" x2="969" y2="594"/>
              <line stroke="red" x1="906" y1="500" x2="906" y2="531"/>
              <line stroke="blue" x1="906" y1="500" x2="938" y2="500"/>
              <line stroke="blue" x1="438" y1="938" x2="469" y2="969"/>
              <line stroke="blue" x1="938" y1="438" x2="969" y2="406"/>
              <line stroke="blue" x1="938" y1="438" x2="938" y2="500"/>
              <line stroke="red" x1="906" y1="531" x2="938" y2="562"/>
              <line stroke="red" x1="844" y1="625" x2="844" y2="656"/>
              <line stroke="red" x1="844" y1="625" x2="875" y2="625"/>
              <line stroke="red" x1="969" y1="406" x2="1000" y2="375"/>
              <line stroke="red" x1="969" y1="406" x2="969" y2="500"/>
              <line stroke="blue" x1="750" y1="750" x2="719" y2="781"/>
              <line stroke="red" x1="750" y1="750" x2="781" y2="719"/>
              <line stroke="blue" x1="750" y1="750" x2="875" y2="750"/>
              <line stroke="red" x1="719" y1="781" x2="688" y2="812"/>
              <line stroke="red" x1="719" y1="781" x2="906" y2="781"/>
              <line stroke="blue" x1="781" y1="719" x2="812" y2="688"/>
              <line stroke="red" x1="781" y1="719" x2="906" y2="719"/>
              <line stroke="red" x1="938" y1="500" x2="969" y2="500"/>
              <line stroke="blue" x1="938" y1="500" x2="938" y2="562"/>
              <line stroke="blue" x1="688" y1="812" x2="656" y2="844"/>
              <line stroke="blue" x1="688" y1="812" x2="938" y2="812"/>
              <line stroke="red" x1="812" y1="688" x2="844" y2="656"/>
              <line stroke="blue" x1="812" y1="688" x2="938" y2="688"/>
              <line stroke="black" x1="1000" y1="375" x2="1000" y2="500"/>
              <line stroke="red" x1="656" y1="844" x2="625" y2="875"/>
              <line stroke="red" x1="656" y1="844" x2="969" y2="844"/>
              <line stroke="blue" x1="844" y1="656" x2="875" y2="625"/>
              <line stroke="red" x1="844" y1="656" x2="969" y2="656"/>
              <line stroke="blue" x1="625" y1="875" x2="594" y2="906"/>
              <line stroke="blue" x1="625" y1="875" x2="1000" y2="875"/>
              <line stroke="blue" x1="875" y1="625" x2="1000" y2="625"/>
              <line stroke="red" x1="469" y1="969" x2="500" y2="1000"/>
              <line stroke="red" x1="594" y1="906" x2="562" y2="938"/>
              <line stroke="red" x1="594" y1="906" x2="969" y2="906"/>
              <line stroke="blue" x1="969" y1="500" x2="1000" y2="500"/>
              <line stroke="red" x1="969" y1="500" x2="969" y2="594"/>
              <line stroke="blue" x1="562" y1="938" x2="531" y2="969"/>
              <line stroke="blue" x1="562" y1="938" x2="938" y2="938"/>
              <line stroke="blue" x1="938" y1="562" x2="969" y2="594"/>
              <line stroke="red" x1="531" y1="969" x2="500" y2="1000"/>
              <line stroke="red" x1="531" y1="969" x2="906" y2="969"/>
              <line stroke="black" x1="500" y1="1000" x2="875" y2="1000"/>
              <line stroke="black" x1="1000" y1="500" x2="1000" y2="625"/>
              <line stroke="red" x1="969" y1="594" x2="1000" y2="625"/>
              <line stroke="blue" x1="875" y1="750" x2="906" y2="719"/>
              <line stroke="red" x1="875" y1="750" x2="906" y2="750"/>
              <line stroke="blue" x1="875" y1="750" x2="906" y2="781"/>
              <line stroke="red" x1="906" y1="719" x2="938" y2="688"/>
              <line stroke="red" x1="906" y1="719" x2="906" y2="750"/>
              <line stroke="blue" x1="938" y1="688" x2="969" y2="656"/>
              <line stroke="blue" x1="938" y1="688" x2="938" y2="750"/>
              <line stroke="red" x1="969" y1="656" x2="1000" y2="625"/>
              <line stroke="red" x1="969" y1="656" x2="969" y2="750"/>
              <line stroke="red" x1="906" y1="750" x2="906" y2="781"/>
              <line stroke="blue" x1="906" y1="750" x2="938" y2="750"/>
              <line stroke="black" x1="1000" y1="625" x2="1000" y2="750"/>
              <line stroke="red" x1="906" y1="781" x2="938" y2="812"/>
              <line stroke="red" x1="938" y1="750" x2="969" y2="750"/>
              <line stroke="blue" x1="938" y1="750" x2="938" y2="812"/>
              <line stroke="blue" x1="969" y1="750" x2="1000" y2="750"/>
              <line stroke="red" x1="969" y1="750" x2="969" y2="844"/>
              <line stroke="blue" x1="938" y1="812" x2="969" y2="844"/>
              <line stroke="black" x1="1000" y1="750" x2="1000" y2="875"/>
              <line stroke="red" x1="969" y1="844" x2="1000" y2="875"/>
              <line stroke="red" x1="938" y1="938" x2="906" y2="969"/>
              <line stroke="blue" x1="938" y1="938" x2="969" y2="906"/>
              <line stroke="blue" x1="938" y1="938" x2="938" y2="1000"/>
              <line stroke="blue" x1="906" y1="969" x2="875" y2="1000"/>
              <line stroke="red" x1="906" y1="969" x2="906" y2="1000"/>
              <line stroke="red" x1="969" y1="906" x2="1000" y2="875"/>
              <line stroke="red" x1="969" y1="906" x2="969" y2="1000"/>
              <line stroke="black" x1="875" y1="1000" x2="906" y2="1000"/>
              <line stroke="black" x1="1000" y1="875" x2="1000" y2="1000"/>
              <line stroke="black" x1="906" y1="1000" x2="938" y2="1000"/>
              <line stroke="black" x1="938" y1="1000" x2="969" y2="1000"/>
              <line stroke="black" x1="969" y1="1000" x2="1000" y2="1000"/>
            </svg>""",
        crease_pattern_type=CreasePatternType.WEB,
    ),
]

_CP_pairs = _CP_PAIRS  # pylint: disable=invalid-name
_TestExamples = _TEST_EXAMPLES  # pylint: disable=invalid-name
