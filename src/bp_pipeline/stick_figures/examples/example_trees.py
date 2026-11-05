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

"""Stick figure tree examples.

Useful for testing and multi-shot prompting.
"""

import dataclasses

from .. import stick as stick_lib
from .. import stick_figure


def list_examples() -> list[stick_figure.StickFigure]:
  return [
      CAT_SIMPLE,
      CAT_LEGS_WIDTH_2,
      SPIDER_SIMPLE,
      SPIKE,
      ELEPHANT_DETAILED,
      HUMAN_SIMPLE,
      PALM_TREE_SIMPLE,
      GIRAFFE_SIMPLE,
      SCORPION_EXAMPLE,
      FRANCESCO_EXAMPLE,
      LA_FIGHTER,
      DASH_8,
      TARGET_DRONE,
      C2_GREYHOUND,
      JUNCO_SKELETON,
      HUMAN_WITH_KNEES,
      QUEEN_ANGELFISH,
      CATERPILLAR,
      FORAGING_SNIPE,
      GREY_WINGED_TRUMPETER,
      HORNED_OWL,
      VALKYRIE_XB70,
      HUMAN_WITH_BICEPS,
      HUMAN_LIMBS_WIDTH_2,
      HUMAN_LIMBS_WIDTH_2_SPLIT,
      HUMAN_BIG_BELLY,
      HUMAN_BIG_BELLY_AND_HEAD,
      HUMAN_ALL_WIDE_BUT_HEAD,
      LEVEL_SHIFTER_2_RIVERS,
      HUMAN_LIMBS_WIDTH_3,
      PHANTOM_F4,
      UNDERWATER_SENSOR,
      WILD_LYNX,
      SPRAYER,
      JAGUAR,
      LANTERN_STAND,
      EMBEDDED_ENGINE,
      PAYLOAD_BAY,
      WAVED_ALBATROSS,
      RIVER_STAIRCASE,
      PACKING_DANCER,
      COAT_RACK,
      PULL_UP_BAR,
      MOOSE,
      RED_CLAW_SCORPION,
      DIVER_BACKFLIP,
      ELF_ARCHER,
  ]


def load_examples(
    names: list[str] | None = None,
) -> dict[str, stick_figure.StickFigure]:
  """Returns all the examples defined in this file.

  Args:
    names: An optional list of example names to load. If None, all examples are
      returned.

  Returns:
    A dictionary mapping example names to StickFigure instances.
  """
  all_examples = list_examples()
  example_dict = {e.name: e for e in all_examples}
  if names is None:
    return example_dict
  else:
    names_set = set(names)
    unknown_names = names_set - example_dict.keys()
    if unknown_names:
      raise ValueError(f"Unknown example names: {unknown_names}")
    return {name: example_dict[name] for name in names_set}


def get_example_by_name(name: str) -> stick_figure.StickFigure:
  """Returns the example with the given name.

  Args:
    name: The name of the example to return.

  Returns:
    The example with the given name.

  Raises:
    ValueError: If no example with the given name is found, or if multiple
      examples with the given name are found.
  """
  examples = [e for e in list_examples() if e.name == name]
  if not examples:
    raise ValueError(f"No example with name {name} found.")
  if len(examples) > 1:
    raise ValueError(f"Multiple examples with name {name} found.")
  return examples[0]


def get_examples_for_prompting(
    *,
    use_shaping_flaps: bool,
    symmetry: bool,
) -> list[stick_figure.StickFigure]:
  """Returns the examples for prompting."""
  if use_shaping_flaps:
    return [HUMAN_WITH_KNEES, HUMAN_WITH_BICEPS, TAIL_SIMPLE]

  if symmetry:
    return [HUMAN_SIMPLE, SPIDER_SIMPLE]

  return [CAT_SIMPLE, ELEPHANT_DETAILED, RED_CLAW_SCORPION]


FAILING_EXAMPLE_JSON = """
{"name": "interceptor jet", "category": "airplanes", "complexity": 1, "root": "fuselage_front", "view": "side",
"children":
[{"name": "fuselage_front", "start": "nose", "end": "wing_root",
"azimuth_angle": -90, "length": 3, "is_flap": true, "is_river": false},
{"name": "fuselage_rear_tail_fin", "start": "wing_root", "end": "fin_tip",
"azimuth_angle": 0, "length": 5, "is_flap": true, "is_river": false},
{"name": "main_wing", "start": "wing_root", "end": "wingtip",
"azimuth_angle": -180, "length": 3, "is_flap": true, "is_river": false}]}
"""


CAT_SIMPLE = stick_figure.StickFigure(
    name="cat",
    complexity=1,
    color_top=[255, 196, 0],
    color_bottom=[255, 196, 0],
    category="domestic animal",
    root="body",
    children=[
        stick_lib.Stick(
            name="body",
            start="hips",
            end="shoulders",
            length=4,
            azimuth_angle=0,
            elevation_angle=0,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="nose",
            length=1,
            azimuth_angle=0,
            elevation_angle=45,
        ),
        stick_lib.Stick(
            name="front_left_leg",
            start="shoulders",
            end="front_left_paw",
            length=3,
            azimuth_angle=90,
            elevation_angle=-70,
        ),
        stick_lib.Stick(
            name="front_right_leg",
            start="shoulders",
            end="front_right_paw",
            length=3,
            azimuth_angle=-90,
            elevation_angle=-70,
        ),
        stick_lib.Stick(
            name="rear_left_leg",
            start="hips",
            end="rear_left_paw",
            length=3,
            azimuth_angle=90,
            elevation_angle=-70,
        ),
        stick_lib.Stick(
            name="rear_right_leg",
            start="hips",
            end="rear_right_paw",
            length=3,
            azimuth_angle=-90,
            elevation_angle=-70,
        ),
        stick_lib.Stick(
            name="tail",
            start="hips",
            end="tail_tip",
            length=3,
            azimuth_angle=180,
            elevation_angle=30,
        ),
    ],
)

CAT_LEGS_WIDTH_2 = stick_figure.StickFigure(
    name="cat_legs_width_2",
    complexity=1,
    category="domestic animal",
    root="body",
    children=[
        stick_lib.Stick(
            name="body",
            start="hips",
            end="shoulders",
            length=4,
            azimuth_angle=0,
            elevation_angle=0,
            width=1,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="nose",
            length=1,
            azimuth_angle=0,
            elevation_angle=45,
            width=1,
        ),
        stick_lib.Stick(
            name="front_left_leg",
            start="shoulders",
            end="front_left_paw",
            length=3,
            azimuth_angle=90,
            elevation_angle=-90,
            width=2,
        ),
        stick_lib.Stick(
            name="front_right_leg",
            start="shoulders",
            end="front_right_paw",
            length=3,
            azimuth_angle=-90,
            elevation_angle=-90,
            width=2,
        ),
        stick_lib.Stick(
            name="rear_left_leg",
            start="hips",
            end="rear_left_paw",
            length=3,
            azimuth_angle=90,
            elevation_angle=-90,
            width=2,
        ),
        stick_lib.Stick(
            name="rear_right_leg",
            start="hips",
            end="rear_right_paw",
            length=3,
            azimuth_angle=-90,
            elevation_angle=-90,
            width=2,
        ),
        stick_lib.Stick(
            name="tail",
            start="hips",
            end="tail_tip",
            length=3,
            azimuth_angle=180,
            elevation_angle=30,
            width=1,
        ),
    ],
)

SPIDER_SIMPLE = stick_figure.StickFigure(
    name="spider",
    category="insects",
    color_top=[0, 0, 0],
    color_bottom=[0, 0, 0],
    complexity=1,
    root="abdomen",
    children=[
        stick_lib.Stick(
            name="abdomen",
            start="abdomen_front",
            end="abdomen_rear",
            length=2,
            azimuth_angle=180,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="leg_1_left",
            start="abdomen_front",
            end="leg_1_left_tip",
            length=3,
            azimuth_angle=-120,
            elevation_angle=-30,
        ),
        stick_lib.Stick(
            name="leg_2_left",
            start="abdomen_front",
            end="leg_2_left_tip",
            length=3,
            azimuth_angle=-90,
            elevation_angle=-30,
        ),
        stick_lib.Stick(
            name="leg_3_left",
            start="abdomen_front",
            end="leg_3_left_tip",
            length=3,
            azimuth_angle=-60,
            elevation_angle=-30,
        ),
        stick_lib.Stick(
            name="leg_4_left",
            start="abdomen_front",
            end="leg_4_left_tip",
            length=3,
            azimuth_angle=-30,
            elevation_angle=-30,
        ),
        stick_lib.Stick(
            name="leg_1_right",
            start="abdomen_front",
            end="leg_1_right_tip",
            length=3,
            azimuth_angle=120,
            elevation_angle=-30,
        ),
        stick_lib.Stick(
            name="leg_2_right",
            start="abdomen_front",
            end="leg_2_right_tip",
            length=3,
            azimuth_angle=90,
            elevation_angle=-30,
        ),
        stick_lib.Stick(
            name="leg_3_right",
            start="abdomen_front",
            end="leg_3_right_tip",
            length=3,
            azimuth_angle=60,
            elevation_angle=-30,
        ),
        stick_lib.Stick(
            name="leg_4_right",
            start="abdomen_front",
            end="leg_4_right_tip",
            length=3,
            azimuth_angle=30,
            elevation_angle=-30,
        ),
    ],
)


SPIKE = stick_figure.StickFigure(
    name="spike",
    category="shape",
    complexity=1,
    root="stick_0",
    children=[
        stick_lib.Stick(
            name="stick_0",
            start="center",
            end="tip_0",
            length=2,
            azimuth_angle=0.0,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="stick_1",
            start="center",
            end="tip_1",
            length=2,
            azimuth_angle=40.0,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="stick_2",
            start="center",
            end="tip_2",
            length=2,
            azimuth_angle=80.0,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="stick_3",
            start="center",
            end="tip_3",
            length=2,
            azimuth_angle=120.0,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="stick_4",
            start="center",
            end="tip_4",
            length=2,
            azimuth_angle=160.0,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="stick_5",
            start="center",
            end="tip_5",
            length=2,
            azimuth_angle=-160.0,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="stick_6",
            start="center",
            end="tip_6",
            length=2,
            azimuth_angle=-120.0,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="stick_7",
            start="center",
            end="tip_7",
            length=2,
            azimuth_angle=-80.0,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="stick_8",
            start="center",
            end="tip_8",
            length=2,
            azimuth_angle=-40.0,
            elevation_angle=0.0,
        ),
    ],
)


ELEPHANT_DETAILED = stick_figure.StickFigure(
    name="Elephant with a curved trunk",
    category="wild animal",
    color_top=[158, 155, 144],
    color_bottom=[158, 155, 144],
    complexity=2,
    root="body",
    children=[
        stick_lib.Stick(
            name="body",
            start="rear_body",
            end="front_body",
            length=6,
            width=4,
            azimuth_angle=0,
            elevation_angle=0,
        ),
        stick_lib.Stick(
            name="neck",
            start="front_body",
            end="neck",
            length=2,
            width=2,
            azimuth_angle=0,
            elevation_angle=30,
        ),
        stick_lib.Stick(
            name="head",
            start="neck",
            end="head_top",
            length=2,
            width=3,
            azimuth_angle=0,
            elevation_angle=0,
        ),
        stick_lib.Stick(
            name="trunk_upper",
            start="head_top",
            end="trunk_mid",
            length=3,
            azimuth_angle=0,
            elevation_angle=-45,
        ),
        stick_lib.Stick(
            name="trunk_lower",
            start="trunk_mid",
            end="trunk_tip",
            length=3,
            azimuth_angle=0,
            elevation_angle=-70,
        ),
        stick_lib.Stick(
            name="left_ear",
            start="neck",
            end="left_ear_tip",
            length=3,
            width=4,
            azimuth_angle=60,
            elevation_angle=0,
        ),
        stick_lib.Stick(
            name="right_ear",
            start="neck",
            end="right_ear_tip",
            length=3,
            width=4,
            azimuth_angle=-60,
            elevation_angle=0,
        ),
        stick_lib.Stick(
            name="left_tusk",
            start="head_top",
            end="left_tusk_tip",
            length=3,
            width=0.5,
            azimuth_angle=20,
            elevation_angle=-40,
        ),
        stick_lib.Stick(
            name="right_tusk",
            start="head_top",
            end="right_tusk_tip",
            length=3,
            width=0.5,
            azimuth_angle=-20,
            elevation_angle=-40,
        ),
        stick_lib.Stick(
            name="front_left_leg_upper",
            start="front_body",
            end="fl_knee",
            length=3,
            width=2,
            azimuth_angle=90,
            elevation_angle=-60,
        ),
        stick_lib.Stick(
            name="front_left_leg_lower",
            start="fl_knee",
            end="fl_foot",
            length=3,
            width=2,
            azimuth_angle=90,
            elevation_angle=-70,
        ),
        stick_lib.Stick(
            name="front_right_leg_upper",
            start="front_body",
            end="fr_knee",
            length=3,
            width=2,
            azimuth_angle=-90,
            elevation_angle=-60,
        ),
        stick_lib.Stick(
            name="front_right_leg_lower",
            start="fr_knee",
            end="fr_foot",
            length=3,
            width=2,
            azimuth_angle=-90,
            elevation_angle=-70,
        ),
        stick_lib.Stick(
            name="rear_left_leg_upper",
            start="rear_body",
            end="rl_knee",
            length=3,
            width=2,
            azimuth_angle=90,
            elevation_angle=-60,
        ),
        stick_lib.Stick(
            name="rear_left_leg_lower",
            start="rl_knee",
            end="rl_foot",
            length=3,
            width=2,
            azimuth_angle=90,
            elevation_angle=-70,
        ),
        stick_lib.Stick(
            name="rear_right_leg_upper",
            start="rear_body",
            end="rr_knee",
            length=3,
            width=2,
            azimuth_angle=-90,
            elevation_angle=-60,
        ),
        stick_lib.Stick(
            name="rear_right_leg_lower",
            start="rr_knee",
            end="rr_foot",
            length=3,
            width=2,
            azimuth_angle=-90,
            elevation_angle=-70,
        ),
        stick_lib.Stick(
            name="tail",
            start="rear_body",
            end="tail_end",
            length=3,
            width=0.5,
            azimuth_angle=180,
            elevation_angle=-45,
        ),
    ],
)


TAIL_SIMPLE = stick_figure.StickFigure(
    name="tail",
    category="body",
    color_top=[226, 154, 134],
    color_bottom=[255, 255, 255],
    complexity=2,
    root="flap_3",
    children=[
        stick_lib.Stick(
            name="flap_1",
            start="tail_end",
            end="flap_1_end",
            azimuth_angle=90,
            elevation_angle=90,
            length=2,
            width=2,
            shaping_flap=True,
        ),
        stick_lib.Stick(
            name="flap_2",
            start="tail_middle_top",
            end="flap_2_end",
            azimuth_angle=90,
            elevation_angle=90,
            length=2,
            width=2,
            shaping_flap=True,
        ),
        stick_lib.Stick(
            name="flap_3",
            start="tail_middle_bottom",
            end="flap_3_end",
            azimuth_angle=90,
            elevation_angle=90,
            length=2,
            width=2,
            shaping_flap=True,
        ),
        stick_lib.Stick(
            name="tail_top",
            start="tail_middle_top",
            end="tail_end",
            azimuth_angle=0,
            elevation_angle=0,
            length=2,
            width=2,
            shaping_flap=False,
        ),
        stick_lib.Stick(
            name="body",
            start="tail_end",
            end="body_top",
            azimuth_angle=0,
            elevation_angle=0,
            length=2,
            width=2,
            shaping_flap=False,
        ),
        stick_lib.Stick(
            name="head_1",
            start="body_top",
            end="head_1_end",
            azimuth_angle=10,
            elevation_angle=0,
            length=2,
            width=1,
            shaping_flap=False,
        ),
        stick_lib.Stick(
            name="head_2",
            start="body_top",
            end="head_2_end",
            azimuth_angle=-10,
            elevation_angle=0,
            length=2,
            width=1,
            shaping_flap=False,
        ),
        stick_lib.Stick(
            name="left_arm",
            start="body_top",
            end="left_end",
            azimuth_angle=45,
            elevation_angle=0,
            length=2,
            width=1,
            shaping_flap=False,
        ),
        stick_lib.Stick(
            name="right_arm",
            start="body_top",
            end="right_end",
            azimuth_angle=-45,
            elevation_angle=0,
            length=2,
            width=1,
            shaping_flap=False,
        ),
        stick_lib.Stick(
            name="tail_middle",
            start="tail_middle_bottom",
            end="tail_middle_top",
            azimuth_angle=0,
            elevation_angle=0,
            length=2,
            width=2,
            shaping_flap=False,
        ),
    ],
)


HUMAN_SIMPLE = stick_figure.StickFigure(
    name="human",
    category="humans",
    color_top=[247, 215, 216],
    color_bottom=[247, 215, 216],
    complexity=1,
    root="torso",
    children=[
        stick_lib.Stick(
            name="torso",
            start="hips",
            end="shoulders",
            azimuth_angle=0,
            length=4,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="head_top",
            azimuth_angle=0,
            length=1,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="right_arm",
            start="shoulders",
            end="right_hand",
            azimuth_angle=-165,
            length=3,
            elevation_angle=-20.0,
        ),
        stick_lib.Stick(
            name="left_arm",
            start="shoulders",
            end="left_hand",
            azimuth_angle=165,
            length=3,
            elevation_angle=-20.0,
        ),
        stick_lib.Stick(
            name="right_leg",
            start="hips",
            end="right_foot",
            azimuth_angle=-90,
            length=4,
            elevation_angle=-60.0,
        ),
        stick_lib.Stick(
            name="left_leg",
            start="hips",
            end="left_foot",
            azimuth_angle=90,
            length=4,
            elevation_angle=-60.0,
        ),
    ],
)

WAVING_HUMAN_SIMPLE = stick_figure.StickFigure(
    name="human",
    category="humans",
    complexity=1,
    root="torso",
    children=[
        stick_lib.Stick(
            name="torso",
            start="hips",
            end="shoulders",
            azimuth_angle=0,
            length=4,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="head_top",
            azimuth_angle=0,
            length=1,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="right_arm_lower",
            start="shoulders",
            end="right_elbow",
            azimuth_angle=-165,
            length=2,
            elevation_angle=-20.0,
        ),
        stick_lib.Stick(
            name="right_arm_upper",
            start="right_elbow",
            end="right_hand",
            azimuth_angle=-120,
            length=1,
            elevation_angle=-20.0,
        ),
        stick_lib.Stick(
            name="left_arm",
            start="shoulders",
            end="left_hand",
            azimuth_angle=165,
            length=3,
            elevation_angle=-20.0,
        ),
        stick_lib.Stick(
            name="right_leg",
            start="hips",
            end="right_foot",
            azimuth_angle=-90,
            length=4,
            elevation_angle=-60.0,
        ),
        stick_lib.Stick(
            name="left_leg",
            start="hips",
            end="left_foot",
            azimuth_angle=90,
            length=4,
            elevation_angle=-60.0,
        ),
    ],
)

KNEELING_HUMAN_MERGE_CONVERTER = dict(
    torso="torso",
    head="head",
    right_arm_lower_right_arm_upper="right_arm",
    left_arm_lower_left_arm_upper="left_arm",
    right_leg_lower_right_leg_upper="right_leg",
    left_leg_lower_left_leg_upper="left_leg",
)
KNEELING_HUMAN = stick_figure.StickFigure(
    name="human",
    category="humans",
    color_top=[247, 215, 216],
    color_bottom=[247, 215, 216],
    complexity=1,
    root="torso",
    children=[
        stick_lib.Stick(
            name="torso",
            start="hips",
            end="shoulders",
            azimuth_angle=0,
            length=1 * 4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="head_top",
            azimuth_angle=0,
            length=1 * 4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="right_arm_lower",
            start="shoulders",
            end="right_hand",
            azimuth_angle=-135,
            length=2 * 4,
            elevation_angle=0,
        ),
        stick_lib.Stick(
            name="right_arm_upper",
            start="right_hand",
            end="right_finger_tips",
            azimuth_angle=-90,
            length=1 * 4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="left_arm_lower",
            start="shoulders",
            end="left_hand",
            azimuth_angle=135,
            length=2 * 4,
            elevation_angle=0,
        ),
        stick_lib.Stick(
            name="left_arm_upper",
            start="left_hand",
            end="left_finger_tips",
            azimuth_angle=45,
            length=1 * 4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="right_leg_lower",
            start="hips",
            end="right_foot",
            azimuth_angle=-135,
            length=2 * 4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="right_leg_upper",
            start="right_foot",
            end="right_toes",
            azimuth_angle=90,
            length=2 * 4,
            elevation_angle=0,
        ),
        stick_lib.Stick(
            name="left_leg_lower",
            start="hips",
            end="left_foot",
            azimuth_angle=135,
            length=2 * 4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="left_leg_upper",
            start="left_foot",
            end="left_toes",
            azimuth_angle=0,
            length=2 * 4,
            elevation_angle=0,
        ),
    ],
)

HUMAN_WITH_KNEES = stick_figure.StickFigure(
    name="human_with_knees",
    category="humans",
    color_top=[224, 172, 105],
    color_bottom=[224, 172, 105],
    complexity=2,
    root="torso",
    children=[
        stick_lib.Stick(
            name="torso",
            start="hips",
            end="shoulders",
            azimuth_angle=0,
            length=4,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="head_top",
            azimuth_angle=0,
            length=1,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="right_arm",
            start="shoulders",
            end="right_hand",
            azimuth_angle=-165,
            length=3,
            elevation_angle=-20.0,
        ),
        stick_lib.Stick(
            name="left_arm",
            start="shoulders",
            end="left_hand",
            azimuth_angle=165,
            length=3,
            elevation_angle=-20.0,
        ),
        stick_lib.Stick(
            name="right_thigh",
            start="hips",
            end="right_knee",
            azimuth_angle=-90,
            length=2,
            elevation_angle=-60.0,
        ),
        stick_lib.Stick(
            name="right_knee_cap",
            start="right_knee",
            end="end_right_knee_cap",
            azimuth_angle=-90,
            length=1,
            elevation_angle=0.0,
            shaping_flap=True,
        ),
        stick_lib.Stick(
            name="right_calf",
            start="right_knee",
            end="right_foot",
            azimuth_angle=-90,
            length=2,
            elevation_angle=-60.0,
        ),
        stick_lib.Stick(
            name="left_thigh",
            start="hips",
            end="left_knee",
            azimuth_angle=90,
            length=2,
            elevation_angle=-60.0,
        ),
        stick_lib.Stick(
            name="left_knee_cap",
            start="left_knee",
            end="end_left_knee_cap",
            azimuth_angle=90,
            length=1,
            elevation_angle=0.0,
            shaping_flap=True,
        ),
        stick_lib.Stick(
            name="left_calf",
            start="left_knee",
            end="left_foot",
            azimuth_angle=90,
            length=2,
            elevation_angle=-60.0,
        ),
    ],
)

GOALIE_3D = stick_figure.StickFigure(
    name="human",
    category="humans",
    color_top=[247, 215, 216],
    color_bottom=[247, 215, 216],
    complexity=1,
    root="torso",
    children=[
        stick_lib.Stick(
            name="torso",
            start="hips",
            end="shoulders",
            azimuth_angle=0,
            length=1,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="head_top",
            azimuth_angle=0,
            length=1,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="left_arm",
            start="shoulders",
            end="left_hand",
            azimuth_angle=90,
            length=3,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="right_arm",
            start="shoulders",
            end="right_hand",
            azimuth_angle=-90,
            length=3,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="left_leg",
            start="hips",
            end="left_foot",
            azimuth_angle=90,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="right_leg",
            start="hips",
            end="right_foot",
            azimuth_angle=-90,
            length=4,
            elevation_angle=0.0,
        ),
    ],
)

HUMAN_WITH_BICEPS = stick_figure.StickFigure(
    name="human_with_biceps",
    category="humans",
    color_top=[126, 74, 60],
    color_bottom=[126, 74, 60],
    complexity=2,
    root="torso",
    children=[
        stick_lib.Stick(
            name="torso",
            start="hips",
            end="shoulders",
            azimuth_angle=0,
            length=4,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="head_top",
            azimuth_angle=0,
            length=1,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="right_bicep",
            start="shoulders",
            end="mid_arm_right",
            azimuth_angle=-165,
            length=1,
            elevation_angle=-20.0,
        ),
        stick_lib.Stick(
            name="right_deltoid",
            start="mid_arm_right",
            end="end_right_deltoid",
            azimuth_angle=-135,
            length=1,
            elevation_angle=0.0,
            shaping_flap=True,
        ),
        stick_lib.Stick(
            name="right_forearm",
            start="mid_arm_right",
            end="right_hand",
            azimuth_angle=-165,
            length=2,
            elevation_angle=-20.0,
        ),
        stick_lib.Stick(
            name="left_bicep",
            start="shoulders",
            end="mid_arm_left",
            azimuth_angle=165,
            length=1,
            elevation_angle=-20.0,
        ),
        stick_lib.Stick(
            name="left_deltoid",
            start="mid_arm_left",
            end="end_left_deltoid",
            azimuth_angle=135,
            length=1,
            elevation_angle=0.0,
            shaping_flap=True,
        ),
        stick_lib.Stick(
            name="left_forearm",
            start="mid_arm_left",
            end="left_hand",
            azimuth_angle=165,
            length=2,
            elevation_angle=-20.0,
        ),
        stick_lib.Stick(
            name="right_leg",
            start="hips",
            end="right_knee",
            azimuth_angle=-90,
            length=3,
            elevation_angle=-60.0,
        ),
        stick_lib.Stick(
            name="left_leg",
            start="hips",
            end="left_knee",
            azimuth_angle=90,
            length=3,
            elevation_angle=-60.0,
        ),
    ],
)

HUMAN_LIMBS_WIDTH_2 = stick_figure.StickFigure(
    name="human_limbs_width_2",
    category="humans",
    complexity=1,
    root="torso",
    children=[
        stick_lib.Stick(
            name="torso",
            start="hips",
            end="shoulders",
            azimuth_angle=0,
            length=4,
            elevation_angle=90.0,
            width=1,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="head_top",
            azimuth_angle=0,
            length=1,
            elevation_angle=90.0,
            width=1,
        ),
        stick_lib.Stick(
            name="right_arm",
            start="shoulders",
            end="right_hand",
            azimuth_angle=-165,
            length=3,
            elevation_angle=-20.0,
            width=2,
        ),
        stick_lib.Stick(
            name="left_arm",
            start="shoulders",
            end="left_hand",
            azimuth_angle=165,
            length=3,
            elevation_angle=-20.0,
            width=2,
        ),
        stick_lib.Stick(
            name="right_leg",
            start="hips",
            end="right_foot",
            azimuth_angle=-90,
            length=4,
            elevation_angle=-60.0,
            width=2,
        ),
        stick_lib.Stick(
            name="left_leg",
            start="hips",
            end="left_foot",
            azimuth_angle=90,
            length=4,
            elevation_angle=-60.0,
            width=2,
        ),
    ],
)

HUMAN_LIMBS_WIDTH_2_SPLIT = stick_figure.StickFigure(
    name="human_limbs_width_2_split",
    category="humans",
    complexity=1,
    root="torso",
    children=[
        stick_lib.Stick(
            name="torso",
            start="hips",
            end="shoulders",
            azimuth_angle=0,
            length=4,
            elevation_angle=90.0,
            width=1,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="head_top",
            azimuth_angle=0,
            length=1,
            elevation_angle=90.0,
            width=1,
        ),
        stick_lib.Stick(
            name="right_arm_1",
            start="shoulders",
            end="right_arm_split",
            azimuth_angle=-165,
            length=1,
            elevation_angle=-20.0,
            width=2,
        ),
        stick_lib.Stick(
            name="right_arm_2",
            start="right_arm_split",
            end="right_hand",
            azimuth_angle=-165,
            length=2,
            elevation_angle=-20.0,
            width=2,
        ),
        stick_lib.Stick(
            name="left_arm",
            start="shoulders",
            end="left_hand",
            azimuth_angle=165,
            length=3,
            elevation_angle=-20.0,
            width=2,
        ),
        stick_lib.Stick(
            name="right_leg",
            start="hips",
            end="right_foot",
            azimuth_angle=-90,
            length=4,
            elevation_angle=-60.0,
            width=2,
        ),
        stick_lib.Stick(
            name="left_leg_1",
            start="hips",
            end="left_leg_split",
            azimuth_angle=90,
            length=2,
            elevation_angle=-60.0,
            width=2,
        ),
        stick_lib.Stick(
            name="left_leg_2",
            start="left_leg_split",
            end="left_foot",
            azimuth_angle=90,
            length=2,
            elevation_angle=-60.0,
            width=2,
        ),
    ],
)

HUMAN_BIG_BELLY = stick_figure.StickFigure(
    name="human_big_belly",
    category="humans",
    complexity=1,
    root="torso",
    children=[
        stick_lib.Stick(
            name="torso",
            start="hips",
            end="shoulders",
            azimuth_angle=0,
            length=4,
            elevation_angle=90.0,
            width=2,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="head_top",
            azimuth_angle=0,
            length=1,
            elevation_angle=90.0,
            width=1,
        ),
        stick_lib.Stick(
            name="right_arm",
            start="shoulders",
            end="right_hand",
            azimuth_angle=-165,
            length=3,
            elevation_angle=-20.0,
            width=1,
        ),
        stick_lib.Stick(
            name="left_arm",
            start="shoulders",
            end="left_hand",
            azimuth_angle=165,
            length=3,
            elevation_angle=-20.0,
            width=1,
        ),
        stick_lib.Stick(
            name="right_leg",
            start="hips",
            end="right_foot",
            azimuth_angle=-90,
            length=4,
            elevation_angle=-60.0,
            width=1,
        ),
        stick_lib.Stick(
            name="left_leg",
            start="hips",
            end="left_foot",
            azimuth_angle=90,
            length=4,
            elevation_angle=-60.0,
            width=1,
        ),
    ],
)

HUMAN_BIG_BELLY_AND_HEAD = stick_figure.StickFigure(
    name="human_big_belly_and_head",
    category="humans",
    complexity=1,
    root="torso",
    children=[
        stick_lib.Stick(
            name="torso",
            start="hips",
            end="shoulders",
            azimuth_angle=0,
            length=4,
            elevation_angle=90.0,
            width=2,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="head_top",
            azimuth_angle=0,
            length=2,
            elevation_angle=90.0,
            width=1,
        ),
        stick_lib.Stick(
            name="right_arm",
            start="shoulders",
            end="right_hand",
            azimuth_angle=-165,
            length=3,
            elevation_angle=-20.0,
            width=1,
        ),
        stick_lib.Stick(
            name="left_arm",
            start="shoulders",
            end="left_hand",
            azimuth_angle=165,
            length=3,
            elevation_angle=-20.0,
            width=1,
        ),
        stick_lib.Stick(
            name="right_leg",
            start="hips",
            end="right_foot",
            azimuth_angle=-90,
            length=4,
            elevation_angle=-60.0,
            width=1,
        ),
        stick_lib.Stick(
            name="left_leg",
            start="hips",
            end="left_foot",
            azimuth_angle=90,
            length=4,
            elevation_angle=-60.0,
            width=1,
        ),
    ],
)


HUMAN_ALL_WIDE_BUT_HEAD = stick_figure.StickFigure(
    name="human_all_wide_but_head",
    category="humans",
    complexity=1,
    root="torso",
    children=[
        stick_lib.Stick(
            name="torso",
            start="hips",
            end="shoulders",
            azimuth_angle=0,
            length=4,
            elevation_angle=90.0,
            width=2,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="head_top",
            azimuth_angle=0,
            length=1,
            elevation_angle=90.0,
            width=1,
        ),
        stick_lib.Stick(
            name="right_arm",
            start="shoulders",
            end="right_hand",
            azimuth_angle=-165,
            length=3,
            elevation_angle=-20.0,
            width=2,
        ),
        stick_lib.Stick(
            name="left_arm",
            start="shoulders",
            end="left_hand",
            azimuth_angle=165,
            length=3,
            elevation_angle=-20.0,
            width=2,
        ),
        stick_lib.Stick(
            name="right_leg",
            start="hips",
            end="right_foot",
            azimuth_angle=-90,
            length=4,
            elevation_angle=-60.0,
            width=2,
        ),
        stick_lib.Stick(
            name="left_leg",
            start="hips",
            end="left_foot",
            azimuth_angle=90,
            length=4,
            elevation_angle=-60.0,
            width=2,
        ),
    ],
)

LEVEL_SHIFTER_2_RIVERS = stick_figure.StickFigure(
    name="level_shifter_2_rivers",
    category="custom",
    complexity=1,
    root="river1",
    children=[
        stick_lib.Stick(
            name="river1",
            start="group1",
            end="group2",
            azimuth_angle=0,
            length=4,
            elevation_angle=0.0,
            width=2,
        ),
        stick_lib.Stick(
            name="left_leg_back",
            start="group1",
            end="left_leg_back_tip",
            azimuth_angle=90,
            length=3,
            elevation_angle=0.0,
            width=1,
        ),
        stick_lib.Stick(
            name="tail",
            start="group1",
            end="tail_tip",
            azimuth_angle=180,
            length=3,
            elevation_angle=0.0,
            width=1,
        ),
        stick_lib.Stick(
            name="right_leg_back",
            start="group1",
            end="right_leg_back_tip",
            azimuth_angle=-90,
            length=3,
            elevation_angle=0.0,
            width=1,
        ),
        stick_lib.Stick(
            name="river2",
            start="group2",
            end="group3",
            azimuth_angle=0,
            length=4,
            elevation_angle=0.0,
            width=2,
        ),
        stick_lib.Stick(
            name="left_leg_mid",
            start="group2",
            end="left_leg_mid_tip",
            azimuth_angle=90,
            length=3,
            elevation_angle=0.0,
            width=1,
        ),
        stick_lib.Stick(
            name="right_leg_mid",
            start="group2",
            end="right_leg_mid_tip",
            azimuth_angle=-90,
            length=3,
            elevation_angle=0.0,
            width=1,
        ),
        stick_lib.Stick(
            name="left_leg_front",
            start="group3",
            end="left_leg_front_tip",
            azimuth_angle=90,
            length=3,
            elevation_angle=0.0,
            width=1,
        ),
        stick_lib.Stick(
            name="right_leg_front",
            start="group3",
            end="right_leg_front_tip",
            azimuth_angle=-90,
            length=3,
            elevation_angle=0.0,
            width=1,
        ),
    ],
)

HUMAN_LIMBS_WIDTH_3 = stick_figure.StickFigure(
    name="human_limbs_width_3",
    category="humans",
    complexity=1,
    root="torso",
    children=[
        stick_lib.Stick(
            name="torso",
            start="hips",
            end="shoulders",
            azimuth_angle=0,
            length=4,
            elevation_angle=90.0,
            width=1,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="head_top",
            azimuth_angle=0,
            length=1,
            elevation_angle=90.0,
            width=1,
        ),
        stick_lib.Stick(
            name="right_arm",
            start="shoulders",
            end="right_hand",
            azimuth_angle=-165,
            length=3,
            elevation_angle=-20.0,
            width=3,
        ),
        stick_lib.Stick(
            name="left_arm",
            start="shoulders",
            end="left_hand",
            azimuth_angle=165,
            length=3,
            elevation_angle=-20.0,
            width=3,
        ),
        stick_lib.Stick(
            name="right_leg",
            start="hips",
            end="right_foot",
            azimuth_angle=-90,
            length=4,
            elevation_angle=-60.0,
            width=3,
        ),
        stick_lib.Stick(
            name="left_leg",
            start="hips",
            end="left_foot",
            azimuth_angle=90,
            length=4,
            elevation_angle=-60.0,
            width=3,
        ),
    ],
)

CHAIN_STICK = stick_figure.StickFigure(
    name="chain",
    category="shape",
    complexity=1,
    root="bc",
    children=[
        stick_lib.Stick(
            name="ab",
            start="a",
            end="b",
            azimuth_angle=-90,
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="bc",
            start="b",
            end="c",
            azimuth_angle=-90,
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="cd",
            start="c",
            end="d",
            azimuth_angle=-90,
            length=2,
            elevation_angle=0.0,
        ),
    ],
)

PALM_TREE_SIMPLE = stick_figure.StickFigure(
    name="palm_tree",
    category="plant",
    complexity=1,
    root="trunk",
    children=[
        stick_lib.Stick(
            name="trunk",
            start="base",
            end="crown_base",
            azimuth_angle=0,
            length=3,
            elevation_angle=90,
        ),
        stick_lib.Stick(
            name="frond_1",
            start="crown_base",
            end="frond_1_tip",
            azimuth_angle=45,
            length=1,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="frond_2",
            start="crown_base",
            end="frond_2_tip",
            azimuth_angle=-45,
            length=1,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="frond_3",
            start="crown_base",
            end="frond_3_tip",
            azimuth_angle=90,
            length=1,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="frond_4",
            start="crown_base",
            end="frond_4_tip",
            azimuth_angle=-90,
            length=1,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="frond_5",
            start="crown_base",
            end="frond_5_tip",
            azimuth_angle=135,
            length=1,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="frond_6",
            start="crown_base",
            end="frond_6_tip",
            azimuth_angle=-135,
            length=1,
            elevation_angle=0.0,
        ),
    ],
)

GIRAFFE_SIMPLE = stick_figure.StickFigure(
    name="giraffe",
    category="wild animal",
    color_top=[255, 196, 0],
    color_bottom=[0, 0, 0],
    complexity=1,
    root="body",
    children=[
        stick_lib.Stick(
            name="body",
            start="rear_body",
            end="front_body",
            azimuth_angle=0,
            length=5,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="neck",
            start="front_body",
            end="head_joint",
            azimuth_angle=0,
            length=8,
            elevation_angle=75,
        ),
        stick_lib.Stick(
            name="head",
            start="head_joint",
            end="nose",
            azimuth_angle=0,
            length=1,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="front_left_leg",
            start="front_body",
            end="front_left_hoof",
            azimuth_angle=90,
            length=7,
            elevation_angle=-90,
        ),
        stick_lib.Stick(
            name="front_right_leg",
            start="front_body",
            end="front_right_hoof",
            azimuth_angle=-90,
            length=7,
            elevation_angle=-90,
        ),
        stick_lib.Stick(
            name="rear_left_leg",
            start="rear_body",
            end="rear_left_hoof",
            azimuth_angle=-90,
            length=7,
            elevation_angle=-90,
        ),
        stick_lib.Stick(
            name="rear_right_leg",
            start="rear_body",
            end="rear_right_hoof",
            azimuth_angle=90,
            length=7,
            elevation_angle=-90,
        ),
        stick_lib.Stick(
            name="tail",
            start="rear_body",
            end="tail_tip",
            azimuth_angle=180,
            length=3,
            elevation_angle=-45,
        ),
    ],
)

SCORPION_EXAMPLE = stick_figure.StickFigure(
    name="scorpion",
    category="animal",
    complexity=3,
    root="tail",
    children=[
        stick_lib.Stick(
            name="tail",
            start="tail_end",
            end="tail_top",
            azimuth_angle=-180.0,
            length=12,
            elevation_angle=20.0,
        ),
        stick_lib.Stick(
            name="appendage_1",
            start="tail_end",
            end="appendage_1_end",
            azimuth_angle=0.0,
            length=1,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="appendage_2",
            start="tail_end",
            end="appendage_2_end",
            azimuth_angle=0.0,
            length=1,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="limb1_right",
            start="tail_end",
            end="limb1_right_end",
            azimuth_angle=180.0,
            length=1,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb2_right",
            start="tail_end",
            end="limb2_right_end",
            azimuth_angle=-140.0,
            length=4,
            elevation_angle=0.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb3_right",
            start="tail_end",
            end="limb3_right_end",
            azimuth_angle=-120.0,
            length=4,
            elevation_angle=0.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb4_right",
            start="tail_end",
            end="limb4_right_end",
            azimuth_angle=-100.0,
            length=4,
            elevation_angle=0.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb5_right",
            start="tail_end",
            end="limb5_right_end",
            azimuth_angle=-90.0,
            length=4,
            elevation_angle=0.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb6_right",
            start="tail_end",
            end="limb6_right_end",
            azimuth_angle=-45.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb7",
            start="tail_end",
            end="limb7_end",
            azimuth_angle=0.0,
            length=1,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb1_left",
            start="tail_end",
            end="limb1_left_end",
            azimuth_angle=180.0,
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb2_left",
            start="tail_end",
            end="limb2_left_end",
            azimuth_angle=140.0,
            length=4,
            elevation_angle=0.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb3_left",
            start="tail_end",
            end="limb3_left_end",
            azimuth_angle=120.0,
            length=4,
            elevation_angle=0.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb4_left",
            start="tail_end",
            end="limb4_left_end",
            azimuth_angle=100.0,
            length=4,
            elevation_angle=0.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb5_left",
            start="tail_end",
            end="limb5_left_end",
            azimuth_angle=90.0,
            length=4,
            elevation_angle=0.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb6_left",
            start="tail_end",
            end="limb6_left_end",
            azimuth_angle=45.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="leftpincer_1",
            start="limb6_left_end",
            end="leftpincer_1_end",
            azimuth_angle=40.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="leftpincer_2",
            start="limb6_left_end",
            end="leftpincer_2_end",
            azimuth_angle=-40.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="rightpincer_1",
            start="limb6_right_end",
            end="rightpincer_1_end",
            azimuth_angle=40.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="rightpincer_2",
            start="limb6_right_end",
            end="rightpincer_2_end",
            azimuth_angle=-40.0,
            length=4,
            elevation_angle=0.0,
        ),
    ],
)

SCORPION_3D_MERGE_CONVERTER = dict(
    tail_1_tail_2_tail_3_tail_4="tail",
    limb2_right_1_limb2_right_2="limb2_right",
    limb3_right_1_limb3_right_2="limb3_right",
    limb4_right_1_limb4_right_2="limb4_right",
    limb5_right_1_limb5_right_2="limb5_right",
    limb2_left_1_limb2_left_2="limb2_left",
    limb3_left_1_limb3_left_2="limb3_left",
    limb4_left_1_limb4_left_2="limb4_left",
    limb5_left_1_limb5_left_2="limb5_left",
    leftpincer_1="leftpincer_1",
    leftpincer_2="leftpincer_2",
    rightpincer_1="rightpincer_1",
    rightpincer_2="rightpincer_2",
    appendage_1="appendage_1",
    appendage_2="appendage_2",
    appendage_3="appendage_3",
    appendage_4="appendage_4",
    limb1_left="limb1_left",
    limb1_right="limb1_right",
    limb7="limb7",
    limb6_left="limb6_left",
    limb6_right="limb6_right",
)
SCORPION_3D = stick_figure.StickFigure(
    name="scorpion_3d",
    category="animal",
    complexity=3,
    root="tail_1",
    children=[
        stick_lib.Stick(
            name="tail_1",
            start="tail_end",
            end="tail_1",
            azimuth_angle=-180.0,
            length=3,
            elevation_angle=0,
        ),
        stick_lib.Stick(
            name="tail_2",
            start="tail_1",
            end="tail_2",
            azimuth_angle=-180.0,
            length=3,
            elevation_angle=45,
        ),
        stick_lib.Stick(
            name="tail_3",
            start="tail_2",
            end="tail_3",
            azimuth_angle=-180.0,
            length=3,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="tail_4",
            start="tail_3",
            end="tail_4",
            azimuth_angle=0,
            length=3,
            elevation_angle=45,
        ),
        stick_lib.Stick(
            name="appendage_1",
            start="tail_end",
            end="appendage_1_end",
            azimuth_angle=0.0,
            length=1,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="appendage_2",
            start="tail_end",
            end="appendage_2_end",
            azimuth_angle=0.0,
            length=1,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="limb1_right",
            start="tail_end",
            end="limb1_right_end",
            azimuth_angle=180.0,
            length=1,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb2_right_1",
            start="tail_end",
            end="limb2_right_1",
            azimuth_angle=-140.0,
            length=2,
            elevation_angle=0.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb2_right_2",
            start="limb2_right_1",
            end="limb2_right_end",
            azimuth_angle=-140.0,
            length=2,
            elevation_angle=-40.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb3_right_1",
            start="tail_end",
            end="limb3_right_1",
            azimuth_angle=-120.0,
            length=2,
            elevation_angle=0.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb3_right_2",
            start="limb3_right_1",
            end="limb3_right_end",
            azimuth_angle=-120.0,
            length=2,
            elevation_angle=-40.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb4_right_1",
            start="tail_end",
            end="limb4_right_1",
            azimuth_angle=-100.0,
            length=2,
            elevation_angle=0.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb4_right_2",
            start="limb4_right_1",
            end="limb4_right_end",
            azimuth_angle=-100.0,
            length=2,
            elevation_angle=-40.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb5_right_1",
            start="tail_end",
            end="limb5_right_1",
            azimuth_angle=-91.0,
            length=2,
            elevation_angle=0.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb5_right_2",
            start="limb5_right_1",
            end="limb5_right_end",
            azimuth_angle=-91.0,
            length=2,
            elevation_angle=-40.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb6_right",
            start="tail_end",
            end="limb6_right_end",
            azimuth_angle=-45.0,
            length=4,
            elevation_angle=20.0,
        ),
        stick_lib.Stick(
            name="limb7",
            start="tail_end",
            end="limb7_end",
            azimuth_angle=0.0,
            length=1,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb1_left",
            start="tail_end",
            end="limb1_left_end",
            azimuth_angle=180.0,
            length=2,
            elevation_angle=0.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb2_left_1",
            start="tail_end",
            end="limb2_left_1",
            azimuth_angle=140.0,
            length=2,
            elevation_angle=0.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb2_left_2",
            start="limb2_left_1",
            end="limb2_left_end",
            azimuth_angle=140.0,
            length=2,
            elevation_angle=-40.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb3_left_1",
            start="tail_end",
            end="limb3_left_1",
            azimuth_angle=120.0,
            length=2,
            elevation_angle=0.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb3_left_2",
            start="limb3_left_1",
            end="limb3_left_end",
            azimuth_angle=120.0,
            length=2,
            elevation_angle=-40.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb4_left_1",
            start="tail_end",
            end="limb4_left_1",
            azimuth_angle=100.0,
            length=2,
            elevation_angle=0.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb4_left_2",
            start="limb4_left_1",
            end="limb4_left_end",
            azimuth_angle=100.0,
            length=2,
            elevation_angle=-40.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb5_left_1",
            start="tail_end",
            end="limb5_left_1",
            azimuth_angle=91.0,
            length=2,
            elevation_angle=0.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb5_left_2",
            start="limb5_left_1",
            end="limb5_left_end",
            azimuth_angle=91.0,
            length=2,
            elevation_angle=-40.0,
            width=0.5,
        ),
        stick_lib.Stick(
            name="limb6_left",
            start="tail_end",
            end="limb6_left_end",
            azimuth_angle=45.0,
            length=4,
            elevation_angle=20.0,
        ),
        stick_lib.Stick(
            name="leftpincer_1",
            start="limb6_left_end",
            end="leftpincer_1_end",
            azimuth_angle=40.0,
            length=4,
            elevation_angle=20.0,
        ),
        stick_lib.Stick(
            name="leftpincer_2",
            start="limb6_left_end",
            end="leftpincer_2_end",
            azimuth_angle=-40.0,
            length=4,
            elevation_angle=20.0,
        ),
        stick_lib.Stick(
            name="rightpincer_1",
            start="limb6_right_end",
            end="rightpincer_1_end",
            azimuth_angle=40.0,
            length=4,
            elevation_angle=20.0,
        ),
        stick_lib.Stick(
            name="rightpincer_2",
            start="limb6_right_end",
            end="rightpincer_2_end",
            azimuth_angle=-40.0,
            length=4,
            elevation_angle=20.0,
        ),
    ],
)

SEGMENTED_SCORPION_MERGE_CONVERTER = {
    "tail_1_tail_2_tail_3_tail_4_tail_5_tail_6": "tail"
}
SEGMENTED_SCORPION = stick_figure.StickFigure(
    name="segmented_scorpion",
    category="animal",
    complexity=3,
    root="tail_1",
    children=[
        stick_lib.Stick(
            name="tail_1",
            start="tail_end",
            end="tail_middle_1",
            azimuth_angle=-180.0,
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="tail_2",
            start="tail_middle_1",
            end="tail_middle_2",
            azimuth_angle=-180.0,
            length=2,
            elevation_angle=30,
        ),
        stick_lib.Stick(
            name="tail_3",
            start="tail_middle_2",
            end="tail_middle_3",
            azimuth_angle=-180.0,
            length=2,
            elevation_angle=60,
        ),
        stick_lib.Stick(
            name="tail_4",
            start="tail_middle_3",
            end="tail_middle_4",
            azimuth_angle=-180.0,
            length=2,
            elevation_angle=90,
        ),
        stick_lib.Stick(
            name="tail_5",
            start="tail_middle_4",
            end="tail_middle_5",
            azimuth_angle=0,
            length=2,
            elevation_angle=45,
        ),
        stick_lib.Stick(
            name="tail_6",
            start="tail_middle_5",
            end="tail_middle_6",
            azimuth_angle=0,
            length=2,
            elevation_angle=00,
        ),
        stick_lib.Stick(
            name="appendage_1",
            start="tail_end",
            end="appendage_1_end",
            azimuth_angle=0.0,
            length=1,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="appendage_2",
            start="tail_end",
            end="appendage_2_end",
            azimuth_angle=0.0,
            length=1,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="limb1_right",
            start="tail_end",
            end="limb1_right_end",
            azimuth_angle=180.0,
            length=1,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb2_right",
            start="tail_end",
            end="limb2_right_end",
            azimuth_angle=-140.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb3_right",
            start="tail_end",
            end="limb3_right_end",
            azimuth_angle=-120.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb4_right",
            start="tail_end",
            end="limb4_right_end",
            azimuth_angle=-100.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb5_right",
            start="tail_end",
            end="limb5_right_end",
            azimuth_angle=-90.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb6_right",
            start="tail_end",
            end="limb6_right_end",
            azimuth_angle=-45.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb7",
            start="tail_end",
            end="limb7_end",
            azimuth_angle=0.0,
            length=1,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb1_left",
            start="tail_end",
            end="limb1_left_end",
            azimuth_angle=180.0,
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb2_left",
            start="tail_end",
            end="limb2_left_end",
            azimuth_angle=140.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb3_left",
            start="tail_end",
            end="limb3_left_end",
            azimuth_angle=120.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb4_left",
            start="tail_end",
            end="limb4_left_end",
            azimuth_angle=100.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb5_left",
            start="tail_end",
            end="limb5_left_end",
            azimuth_angle=90.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="limb6_left",
            start="tail_end",
            end="limb6_left_end",
            azimuth_angle=45.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="leftpincer_1",
            start="limb6_left_end",
            end="leftpincer_1_end",
            azimuth_angle=40.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="leftpincer_2",
            start="limb6_left_end",
            end="leftpincer_2_end",
            azimuth_angle=-40.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="rightpincer_1",
            start="limb6_right_end",
            end="rightpincer_1_end",
            azimuth_angle=40.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="rightpincer_2",
            start="limb6_right_end",
            end="rightpincer_2_end",
            azimuth_angle=-40.0,
            length=4,
            elevation_angle=0.0,
        ),
    ],
)

SNAKE_MERGE_CONVERTER = {
    "IS_ROOT_segment_2_segment_3_segment_4_segment_5_segment_6_segment_7_segment_8": (
        "body"
    )
}
SNAKE = stick_figure.StickFigure(
    name="twisting_snake",
    category="animal",
    complexity=3,
    root="IS_ROOT",
    children=[
        stick_lib.Stick(
            name="IS_ROOT",
            start="p1",
            end="p2",
            azimuth_angle=0,
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="segment_2",
            start="p2",
            end="p3",
            azimuth_angle=45,  # First turn right
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="segment_3",
            start="p3",
            end="p4",
            azimuth_angle=-45,  # Turn back left (to align with a wave)
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="segment_4",
            start="p4",
            end="p5",
            azimuth_angle=90,  # A sharper turn for a dramatic curve
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="segment_5",
            start="p5",
            end="p6",
            azimuth_angle=0,  # Straightens out briefly
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="segment_6",
            start="p6",
            end="p7",
            azimuth_angle=-45,  # Starts turning left
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="segment_7",
            start="p7",
            end="p8",
            azimuth_angle=45,  # Turns back right
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="segment_8",
            start="p8",
            end="p9",
            azimuth_angle=0,  # Final segment pointing forward
            length=2,
            elevation_angle=0.0,
        ),
    ],
)
SNAKE_ROOT_TEST = stick_figure.StickFigure(
    name="twisting_snake",
    category="animal",
    complexity=3,
    root="segment_1",
    children=[
        stick_lib.Stick(
            name="segment_1",
            start="p1",
            end="p2",
            azimuth_angle=0,
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="segment_2",
            start="p2",
            end="p3",
            azimuth_angle=45,  # First turn right
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="segment_3",
            start="p3",
            end="p4",
            azimuth_angle=-45,  # Turn back left (to align with a wave)
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="segment_4",
            start="p4",
            end="p5",
            azimuth_angle=90,  # A sharper turn for a dramatic curve
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="segment_5",
            start="p5",
            end="p6",
            azimuth_angle=0,  # Straightens out briefly
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="segment_6",
            start="p6",
            end="p7",
            azimuth_angle=-45,  # Starts turning left
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="segment_7",
            start="p7",
            end="p8",
            azimuth_angle=45,  # Turns back right
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="segment_8",
            start="p8",
            end="p9",
            azimuth_angle=0,  # Final segment pointing forward
            length=2,
            elevation_angle=0.0,
        ),
    ],
)

FRANCESCO_EXAMPLE = stick_figure.StickFigure(
    name="francesco_tree",
    category="tree",
    complexity=3,
    root="1a1b",
    children=[
        stick_lib.Stick(
            name="1a1b",
            start="1a",
            end="1b",
            azimuth_angle=0.0,
            length=1,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="1a1c",
            start="1a",
            end="1c",
            azimuth_angle=90.0,
            length=1,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="1a2a",
            start="1a",
            end="2a",
            azimuth_angle=-120.0,
            length=2,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="2a3a",
            start="2a",
            end="3a",
            azimuth_angle=-180.0,
            length=3,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="3a4a",
            start="3a",
            end="4a",
            azimuth_angle=90.0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="3a5a",
            start="3a",
            end="5a",
            azimuth_angle=135.0,
            length=5,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="5a6a",
            start="5a",
            end="6a",
            azimuth_angle=90.0,
            length=6,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="5a6b",
            start="5a",
            end="6b",
            azimuth_angle=-180.0,
            length=6,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="3a7a",
            start="3a",
            end="7a",
            azimuth_angle=-180.0,
            length=7,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="3a8a",
            start="3a",
            end="8a",
            azimuth_angle=-135.0,
            length=8,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="8a9a",
            start="8a",
            end="9a",
            azimuth_angle=-180.0,
            length=9,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="8a9b",
            start="8a",
            end="9b",
            azimuth_angle=-90.0,
            length=9,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="3a10a",
            start="3a",
            end="10a",
            azimuth_angle=-90.0,
            length=10,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="2a11a",
            start="2a",
            end="11a",
            azimuth_angle=-60.0,
            length=11,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="11a12a",
            start="11a",
            end="12a",
            azimuth_angle=-90.0,
            length=12,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="12a13a",
            start="12a",
            end="13a",
            azimuth_angle=-45.0,
            length=13,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="12a13b",
            start="12a",
            end="13b",
            azimuth_angle=-135.0,
            length=13,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="11a14a",
            start="11a",
            end="14a",
            azimuth_angle=0.0,
            length=14,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="14a15a",
            start="14a",
            end="15a",
            azimuth_angle=-45.0,
            length=15,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="14a15b",
            start="14a",
            end="15b",
            azimuth_angle=45.0,
            length=15,
            elevation_angle=0.0,
        ),
    ],
)

LA_FIGHTER = stick_figure.StickFigure(
    name="la_fighter",
    category="airplanes",
    complexity=1,
    root="fuselage_mid",
    children=[
        stick_lib.Stick(
            name="fuselage_front_propeller",
            start="propeller_tip",
            end="cockpit_start",
            azimuth_angle=0,
            length=3,
        ),
        stick_lib.Stick(
            name="fuselage_mid",
            start="cockpit_start",
            end="wing_root",
            azimuth_angle=0,
            length=2,
        ),
        stick_lib.Stick(
            name="fuselage_rear",
            start="wing_root",
            end="tail_joint",
            azimuth_angle=0,
            length=4,
        ),
        stick_lib.Stick(
            name="cockpit",
            start="cockpit_start",
            end="cockpit_peak",
            azimuth_angle=60,
            length=2,
        ),
        stick_lib.Stick(
            name="main_wing",
            start="wing_root",
            end="wing_tip",
            azimuth_angle=-45,
            length=3,
        ),
        stick_lib.Stick(
            name="tail_vertical",
            start="tail_joint",
            end="v_stab_tip",
            azimuth_angle=90,
            length=2,
        ),
        stick_lib.Stick(
            name="tail_horizontal",
            start="tail_joint",
            end="h_stab_tip",
            azimuth_angle=-180,
            length=2,
        ),
    ],
)

DASH_8 = stick_figure.StickFigure(
    name="dash_8",
    category="airplanes",
    complexity=1,
    root="aft_fuselage",
    children=[
        stick_lib.Stick(
            name="aft_fuselage",
            start="tail_joint",
            end="wing_mount_joint",
            azimuth_angle=0,
            length=2,
        ),
        stick_lib.Stick(
            name="fwd_fuselage",
            start="wing_mount_joint",
            end="nose_joint",
            azimuth_angle=0,
            length=5,
        ),
        stick_lib.Stick(
            name="horizontal_stabilizer",
            start="tail_joint",
            end="h_stab_tip",
            azimuth_angle=0,
            length=3,
        ),
        stick_lib.Stick(
            name="vertical_stabilizer",
            start="tail_joint",
            end="v_stab_tip",
            azimuth_angle=90,
            length=3,
        ),
        stick_lib.Stick(
            name="inner_wing",
            start="wing_mount_joint",
            end="engine_mount_joint",
            azimuth_angle=0,
            length=2,
        ),
        stick_lib.Stick(
            name="outer_wing",
            start="engine_mount_joint",
            end="wingtip_joint",
            azimuth_angle=0,
            length=3,
        ),
        stick_lib.Stick(
            name="engine_nacelle",
            start="engine_mount_joint",
            end="propeller_tip",
            azimuth_angle=-90,
            length=2,
        ),
    ],
)

STICK_FIGURE_WITH_TWO_CHILDREN = stick_figure.StickFigure(
    name="stick_figure_with_two_children",
    category="aeroplanes",
    complexity=1,
    root="aft_fuselage",
    children=[
        stick_lib.Stick(
            name="aft_fuselage",
            start="tail_joint",
            end="wing_mount_joint",
            azimuth_angle=0,
            length=2,
        ),
        stick_lib.Stick(
            name="fwd_fuselage",
            start="wing_mount_joint",
            end="nose_joint",
            azimuth_angle=0,
            length=5,
        ),
    ],
)

C2_GREYHOUND = stick_figure.StickFigure(
    name="C-2 Greyhound",
    category="airplanes",
    complexity=1,
    root="fuselage_rear",
    children=[
        stick_lib.Stick(
            name="fuselage_rear",
            start="tail_base",
            end="wing_root",
            azimuth_angle=-90,
            length=3,
        ),
        stick_lib.Stick(
            name="fuselage_front",
            start="wing_root",
            end="nose",
            azimuth_angle=-90,
            length=3,
        ),
        stick_lib.Stick(
            name="main_wing",
            start="wing_root",
            end="wing_tip",
            azimuth_angle=-120,
            length=4,
        ),
        stick_lib.Stick(
            name="vertical_stabilizer",
            start="tail_base",
            end="rudder_tip",
            azimuth_angle=0,
            length=2,
        ),
        stick_lib.Stick(
            name="horizontal_stabilizer",
            start="tail_base",
            end="h_stab_tip",
            azimuth_angle=90,
            length=1,
        ),
        stick_lib.Stick(
            name="engine_nacelle",
            start="wing_root",
            end="engine_front",
            azimuth_angle=-105,
            length=2,
        ),
    ],
)

TARGET_DRONE = stick_figure.StickFigure(
    name="target_drone",
    category="aeroplanes",
    complexity=1,
    root="fuselage_tail_section",
    children=[
        stick_lib.Stick(
            name="fuselage_tail_section",
            start="tail_joint",
            end="mid_fuselage_joint",
            azimuth_angle=-90,
            length=4,
        ),
        stick_lib.Stick(
            name="fuselage_nose_section",
            start="mid_fuselage_joint",
            end="nose_joint",
            azimuth_angle=-90,
            length=2,
        ),
        stick_lib.Stick(
            name="wing",
            start="mid_fuselage_joint",
            end="wing_tip",
            azimuth_angle=180,
            length=4,
        ),
        stick_lib.Stick(
            name="tail_fin",
            start="tail_joint",
            end="tail_fin_tip",
            azimuth_angle=0,
            length=3,
        ),
        stick_lib.Stick(
            name="horizontal_stabilizer",
            start="tail_joint",
            end="horizontal_stab_tip",
            azimuth_angle=180,
            length=2,
        ),
    ],
)

QUEEN_ANGELFISH = stick_figure.StickFigure.from_json("""{
  "name": "queen_angelfish",
  "category": "fish",
  "complexity": 1,
  "root": "body",
  "children": [
    {
      "name": "body",
      "start": "tail_joint",
      "end": "head_joint",
      "azimuth_angle": 0,
      "elevation_angle": 0.0,
      "length": 4,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "head",
      "start": "head_joint",
      "end": "mouth",
      "azimuth_angle": 0,
      "elevation_angle": 0.0,
      "length": 1,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "caudal_fin",
      "start": "tail_joint",
      "end": "caudal_tip",
      "azimuth_angle": 180,
      "elevation_angle": 0.0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "dorsal_fin",
      "start": "head_joint",
      "end": "dorsal_tip",
      "azimuth_angle": 150,
      "elevation_angle": 8.0,
      "length": 4,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "anal_fin",
      "start": "tail_joint",
      "end": "anal_tip",
      "azimuth_angle": -150,
      "elevation_angle": -8.0,
      "length": 4,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "pelvic_fin",
      "start": "head_joint",
      "end": "pelvic_tip",
      "azimuth_angle": -90,
      "elevation_angle": -8.0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "pectoral_fin",
      "start": "head_joint",
      "end": "pectoral_tip",
      "azimuth_angle": 45,
      "elevation_angle": 45.0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    }
  ]
}""")

LANTERN_STAND = stick_figure.StickFigure.from_json("""{
    "name": "lantern_stand",
    "category": "household items",
    "complexity": 1,
    "root": "hook_pole",
    "children": [
        {
            "name": "hook_pole",
            "start": "base",
            "end": "hook_end",
            "azimuth_angle": 0.0,
            "elevation_angle": 74.05460409907714,
            "length": 8,
            "width": 1,
            "shaping_flap": false
        },
        {
            "name": "left_leg",
            "start": "base",
            "end": "left_foot",
            "azimuth_angle": -90.0,
            "elevation_angle": -45.0,
            "length": 3,
            "width": 2,
            "shaping_flap": false
        },
        {
            "name": "right_leg",
            "start": "base",
            "end": "right_foot",
            "azimuth_angle": 90.0,
            "elevation_angle": -45.0,
            "length": 3,
            "width": 2,
            "shaping_flap": false
        }
    ]
    }""")


WILD_LYNX = stick_figure.StickFigure.from_json("""{
    "name": "wild_lynx",
    "category": "constellations",
    "complexity": 1,
    "root": "body",
    "children": [
        {
            "name": "body",
            "start": "hip",
            "end": "shoulder",
            "azimuth_angle": 0,
            "elevation_angle": 0,
            "length": 4,
            "width": 1,
            "shaping_flap": false
        },
        {
            "name": "head",
            "start": "shoulder",
            "end": "head_top",
            "azimuth_angle": 0,
            "elevation_angle": 30,
            "length": 2, "width": 1,
            "shaping_flap": false
        },
        {
            "name": "tail",
            "start": "hip",
            "end": "tail_tip",
            "azimuth_angle": 180,
            "elevation_angle": 20,
            "length": 2,
            "width": 1,
            "shaping_flap": false
        },
        {
            "name": "front_left_leg",
            "start": "shoulder",
            "end": "front_left_paw",
            "azimuth_angle": -98,
            "elevation_angle": -82,
            "length": 3,
            "width": 1,
            "shaping_flap": false
        },
        {
            "name": "front_right_leg",
            "start": "shoulder",
            "end": "front_right_paw",
            "azimuth_angle": 98,
            "elevation_angle": -82,
            "length": 3, "width": 1,
            "shaping_flap": false
        },
        {
            "name": "rear_left_leg",
            "start": "hip",
            "end": "rear_left_paw",
            "azimuth_angle": -98,
            "elevation_angle": -82,
            "length": 3,
            "width": 1,
            "shaping_flap": false
        },
        {
            "name": "rear_right_leg",
            "start": "hip",
            "end": "rear_right_paw",
            "azimuth_angle": 98,
            "elevation_angle": -82,
            "length": 3,
            "width": 1,
            "shaping_flap": false
        },
        {
            "name": "left_ear_tuft",
            "start": "head_top",
            "end": "left_ear_tip",
            "azimuth_angle": -45,
            "elevation_angle": 60,
            "length": 1,
            "width": 1,
            "shaping_flap": false
        },
        {
            "name": "right_ear_tuft",
            "start": "head_top",
            "end": "right_ear_tip",
            "azimuth_angle": 45,
            "elevation_angle": 60,
            "length": 1,
            "width": 1,
            "shaping_flap": false
        }
    ]
    }""")


CATERPILLAR = stick_figure.StickFigure(
    name="asp caterpillar",
    category="insects",
    complexity=1,
    root="body_segment_1",
    children=[
        stick_lib.Stick(
            name="head",
            start="joint_body_1",
            end="joint_head",
            azimuth_angle=90,
            elevation_angle=0,
            length=2,
            width=1,
            shaping_flap=False,
        ),
        stick_lib.Stick(
            name="body_segment_1",
            start="joint_body_1",
            end="joint_body_2",
            azimuth_angle=-90,
            elevation_angle=0,
            length=3,
            width=1,
            shaping_flap=False,
        ),
        stick_lib.Stick(
            name="body_segment_2",
            start="joint_body_2",
            end="joint_body_3",
            azimuth_angle=-90,
            elevation_angle=0,
            length=3,
            width=1,
            shaping_flap=False,
        ),
        stick_lib.Stick(
            name="body_segment_3",
            start="joint_body_3",
            end="joint_tail",
            azimuth_angle=-90,
            elevation_angle=0,
            length=2,
            width=1,
            shaping_flap=False,
        ),
        stick_lib.Stick(
            name="leg_front",
            start="joint_body_1",
            end="front_leg_tip",
            azimuth_angle=-180,
            elevation_angle=0,
            length=2,
            width=1,
            shaping_flap=False,
        ),
        stick_lib.Stick(
            name="leg_middle",
            start="joint_body_2",
            end="middle_leg_tip",
            azimuth_angle=-180,
            elevation_angle=0,
            length=2,
            width=1,
            shaping_flap=False,
        ),
        stick_lib.Stick(
            name="leg_rear",
            start="joint_body_3",
            end="rear_leg_tip",
            azimuth_angle=-180,
            elevation_angle=0,
            length=2,
            width=1,
            shaping_flap=False,
        ),
    ],
)


# ----- Taskqueue debug examples -----


JUNCO_SKELETON = stick_figure.StickFigure.from_json("""{
  "name": "junco skeleton",
  "category": "birds",
  "complexity": 1,
  "root": "body",
  "children": [
    {
      "name": "body",
      "start": "shoulder_joint",
      "end": "hip_joint",
      "azimuth_angle": -90,
      "elevation_angle": 0,
      "length": 4,
      "width": 1,
      "shaping_flap": false,
      "is_flap": false,
      "is_river": true,
      "is_on_symmetry_axis": false,
      "symmetric_stick_name": null
    },
    {
      "name": "skull",
      "start": "shoulder_joint",
      "end": "skull_tip",
      "azimuth_angle": -60,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false,
      "is_flap": true,
      "is_river": false,
      "is_on_symmetry_axis": false,
      "symmetric_stick_name": null
    },
    {
      "name": "pelvis_tail",
      "start": "hip_joint",
      "end": "tail_tip",
      "azimuth_angle": 120,
      "elevation_angle": 0,
      "length": 4,
      "width": 1,
      "shaping_flap": false,
      "is_flap": true,
      "is_river": false,
      "is_on_symmetry_axis": false,
      "symmetric_stick_name": null
    },
    {
      "name": "left_leg",
      "start": "hip_joint",
      "end": "left_foot_tip",
      "azimuth_angle": -175,
      "elevation_angle": 0,
      "length": 3,
      "width": 1,
      "shaping_flap": false,
      "is_flap": true,
      "is_river": false,
      "is_on_symmetry_axis": false,
      "symmetric_stick_name": null
    },
    {
      "name": "right_leg",
      "start": "hip_joint",
      "end": "right_foot_tip",
      "azimuth_angle": -185,
      "elevation_angle": 0,
      "length": 3,
      "width": 1,
      "shaping_flap": false,
      "is_flap": true,
      "is_river": false,
      "is_on_symmetry_axis": false,
      "symmetric_stick_name": null
    },
    {
      "name": "left_wing",
      "start": "shoulder_joint",
      "end": "left_wing_tip",
      "azimuth_angle": -130,
      "elevation_angle": 0,
      "length": 5,
      "width": 1,
      "shaping_flap": false,
      "is_flap": true,
      "is_river": false,
      "is_on_symmetry_axis": false,
      "symmetric_stick_name": null
    },
    {
      "name": "right_wing",
      "start": "shoulder_joint",
      "end": "right_wing_tip",
      "azimuth_angle": -140,
      "elevation_angle": 0,
      "length": 5,
      "width": 1,
      "shaping_flap": false,
      "is_flap": true,
      "is_river": false,
      "is_on_symmetry_axis": false,
      "symmetric_stick_name": null
    },
    {
      "name": "sternum",
      "start": "shoulder_joint",
      "end": "sternum_end",
      "azimuth_angle": -150,
      "elevation_angle": 0,
      "length": 3,
      "width": 1,
      "shaping_flap": false,
      "is_flap": true,
      "is_river": false,
      "is_on_symmetry_axis": false,
      "symmetric_stick_name": null
    }
  ],
  "symmetry_axis": [],
  "is_symmetric_tree": false
}""")

FORAGING_SNIPE = stick_figure.StickFigure.from_json("""
    {
  "name": "foraging snipe",
  "category": "birds",
  "complexity": 1,
  "root": "beak_body_neck_head",
  "children": [
    {
      "name": "beak_body_neck_head",
      "start": "tail_base",
      "end": "beak_tip",
      "azimuth_angle": 120,
      "elevation_angle": 0,
      "length": 10,
      "width": 1,
      "shaping_flap": false,
      "is_flap": true,
      "is_river": false,
      "is_on_symmetry_axis": false,
      "symmetric_stick_name": null
    },
    {
      "name": "leg1",
      "start": "tail_base",
      "end": "foot1",
      "azimuth_angle": 0,
      "elevation_angle": 0,
      "length": 4,
      "width": 1,
      "shaping_flap": false,
      "is_flap": true,
      "is_river": false,
      "is_on_symmetry_axis": false,
      "symmetric_stick_name": null
    },
    {
      "name": "leg2",
      "start": "tail_base",
      "end": "foot2",
      "azimuth_angle": 5,
      "elevation_angle": 0,
      "length": 4,
      "width": 1,
      "shaping_flap": false,
      "is_flap": true,
      "is_river": false,
      "is_on_symmetry_axis": false,
      "symmetric_stick_name": null
    },
    {
      "name": "tail",
      "start": "tail_base",
      "end": "tail_tip",
      "azimuth_angle": 90,
      "elevation_angle": 0,
      "length": 1,
      "width": 1,
      "shaping_flap": false,
      "is_flap": true,
      "is_river": false,
      "is_on_symmetry_axis": false,
      "symmetric_stick_name": null
    }
  ],
  "symmetry_axis": [],
  "symmetry_plane_name": "azimuth",
  "is_symmetric_tree": false
}""")


GREY_WINGED_TRUMPETER = stick_figure.StickFigure.from_dict(
    dict(
        name="grey-winged trumpeter",
        category="birds",
        complexity=1,
        root="body",
        children=[
            dict(
                name="body",
                start="chest",
                end="rump",
                azimuth_angle=-80,
                elevation_angle=0,
                length=5,
                width=1,
                shaping_flap=False,
            ),
            dict(
                name="head_neck",
                start="chest",
                end="beak_tip",
                azimuth_angle=15,
                elevation_angle=0,
                length=4,
                width=1,
                shaping_flap=False,
            ),
            dict(
                name="wing",
                start="chest",
                end="wing_tip",
                azimuth_angle=-135,
                elevation_angle=0,
                length=4,
                width=1,
                shaping_flap=False,
            ),
            dict(
                name="leg_forward",
                start="rump",
                end="foot_forward",
                azimuth_angle=-170,
                elevation_angle=0,
                length=3,
                width=1,
                shaping_flap=False,
            ),
            dict(
                name="leg_back",
                start="rump",
                end="foot_back",
                azimuth_angle=-190,
                elevation_angle=0,
                length=3,
                width=1,
                shaping_flap=False,
            ),
            dict(
                name="tail",
                start="rump",
                end="tail_end",
                azimuth_angle=-100,
                elevation_angle=0,
                length=3,
                width=1,
                shaping_flap=False,
            ),
        ],
    )
)

# Symmetry edge cases.
SILVERFISH_NYMPH = stick_figure.StickFigure.from_json("""
{
  "name": "silverfish nymph",
  "category": "insects",
  "complexity": 1,
  "root": "body_abdomen",
  "children": [
    {
      "name": "body_abdomen",
      "start": "tail_base",
      "end": "mid_body",
      "azimuth_angle": -90,
      "elevation_angle": 0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "body_thorax",
      "start": "mid_body",
      "end": "head_base",
      "azimuth_angle": -90,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "head",
      "start": "head_base",
      "end": "head_tip",
      "azimuth_angle": 90,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "antenna_left",
      "start": "head_tip",
      "end": "antenna_left_tip",
      "azimuth_angle": -45,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "antenna_right",
      "start": "head_tip",
      "end": "antenna_right_tip",
      "azimuth_angle": -135,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "leg_front_left",
      "start": "head_base",
      "end": "leg_front_left_tip",
      "azimuth_angle": -20,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "leg_front_right",
      "start": "head_base",
      "end": "leg_front_right_tip",
      "azimuth_angle": -160,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "leg_mid_left",
      "start": "mid_body",
      "end": "leg_mid_left_tip",
      "azimuth_angle": 0,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "leg_mid_right",
      "start": "mid_body",
      "end": "leg_mid_right_tip",
      "azimuth_angle": -180,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "leg_rear_left",
      "start": "mid_body",
      "end": "leg_rear_left_tip",
      "azimuth_angle": 20,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "leg_rear_right",
      "start": "mid_body",
      "end": "leg_rear_right_tip",
      "azimuth_angle": -200,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "cercus_median",
      "start": "tail_base",
      "end": "cercus_median_tip",
      "azimuth_angle": 90,
      "elevation_angle": 0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "cercus_left",
      "start": "tail_base",
      "end": "cercus_left_tip",
      "azimuth_angle": 110,
      "elevation_angle": 0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "cercus_right",
      "start": "tail_base",
      "end": "cercus_right_tip",
      "azimuth_angle": 70,
      "elevation_angle": 0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    }
  ]
}""")

AMERICAN_LADY_BUTTERFLY = stick_figure.StickFigure.from_json("""
{
  "name": "American Lady",
  "category": "insects",
  "complexity": 1,
  "root": "thorax_front_segment",
  "children": [
    {
      "name": "body_head",
      "start": "head_base",
      "end": "head_tip",
      "azimuth_angle": -90,
      "elevation_angle": 0,
      "length": 1,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "thorax_front_segment",
      "start": "head_base",
      "end": "thorax_middle",
      "azimuth_angle": -90,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "thorax_rear_segment",
      "start": "thorax_middle",
      "end": "abdomen_base",
      "azimuth_angle": -90,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "body_abdomen",
      "start": "abdomen_base",
      "end": "abdomen_tip",
      "azimuth_angle": -90,
      "elevation_angle": 0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "left_front_wing",
      "start": "head_base",
      "end": "left_front_wing_tip",
      "azimuth_angle": -45,
      "elevation_angle": 0,
      "length": 4,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "right_front_wing",
      "start": "head_base",
      "end": "right_front_wing_tip",
      "azimuth_angle": -135,
      "elevation_angle": 0,
      "length": 4,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "left_rear_wing",
      "start": "thorax_middle",
      "end": "left_rear_wing_tip",
      "azimuth_angle": 45,
      "elevation_angle": 0,
      "length": 4,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "right_rear_wing",
      "start": "thorax_middle",
      "end": "right_rear_wing_tip",
      "azimuth_angle": -225,
      "elevation_angle": 0,
      "length": 4,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "left_leg_1",
      "start": "head_base",
      "end": "left_foot_1",
      "azimuth_angle": -15,
      "elevation_angle": 0,
      "length": 1,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "right_leg_1",
      "start": "head_base",
      "end": "right_foot_1",
      "azimuth_angle": -165,
      "elevation_angle": 0,
      "length": 1,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "left_leg_2",
      "start": "thorax_middle",
      "end": "left_foot_2",
      "azimuth_angle": 0,
      "elevation_angle": 0,
      "length": 1,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "right_leg_2",
      "start": "thorax_middle",
      "end": "right_foot_2",
      "azimuth_angle": -180,
      "elevation_angle": 0,
      "length": 1,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "left_leg_3",
      "start": "abdomen_base",
      "end": "left_foot_3",
      "azimuth_angle": 15,
      "elevation_angle": 0,
      "length": 1,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "right_leg_3",
      "start": "abdomen_base",
      "end": "right_foot_3",
      "azimuth_angle": -195,
      "elevation_angle": 0,
      "length": 1,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "left_antenna",
      "start": "head_base",
      "end": "left_antenna_tip",
      "azimuth_angle": -60,
      "elevation_angle": 0,
      "length": 1,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "right_antenna",
      "start": "head_base",
      "end": "right_antenna_tip",
      "azimuth_angle": -120,
      "elevation_angle": 0,
      "length": 1,
      "width": 1,
      "shaping_flap": false
    }
  ]
}""")

HORNED_OWL = stick_figure.StickFigure.from_json("""{
  "name": "Horned owl",
  "category": "animals",
  "complexity": 1,
  "root": "body",
  "children": [
    {
      "name": "body",
      "start": "body_bottom",
      "end": "body_top",
      "azimuth_angle": 0,
      "elevation_angle": 0,
      "length": 4,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "head",
      "start": "body_top",
      "end": "head_top",
      "azimuth_angle": 0,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "wing_right",
      "start": "body_top",
      "end": "wing_tip_right",
      "azimuth_angle": -45,
      "elevation_angle": 0,
      "length": 4,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "wing_left",
      "start": "body_top",
      "end": "wing_tip_left",
      "azimuth_angle": 45,
      "elevation_angle": 0,
      "length": 4,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "leg_right",
      "start": "body_bottom",
      "end": "foot_right",
      "azimuth_angle": -30,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "leg_left",
      "start": "body_bottom",
      "end": "foot_left",
      "azimuth_angle": 30,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "horn_tuft_right",
      "start": "head_top",
      "end": "tuft_tip_right",
      "azimuth_angle": -30,
      "elevation_angle": 0,
      "length": 1,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "horn_tuft_left",
      "start": "head_top",
      "end": "tuft_tip_left",
      "azimuth_angle": 30,
      "elevation_angle": 0,
      "length": 1,
      "width": 1,
      "shaping_flap": false
    }
  ]
}""")

VALKYRIE_XB70 = stick_figure.StickFigure.from_json("""
{"name": "Valkyrie XB-70", "category": "airplanes", "complexity": 1, "root": "rear_fuselage", "children": [{"name": "rear_fuselage", "start": "tail_base", "end": "wing_root", "azimuth_angle": 0, "elevation_angle": 0.0, "length": 2, "width": 2, "shaping_flap": false}, {"name": "front_fuselage", "start": "wing_root", "end": "nose", "azimuth_angle": 0, "elevation_angle": 0.0, "length": 2, "width": 2, "shaping_flap": false}, {"name": "left_wing", "start": "wing_root", "end": "left_wing_tip", "azimuth_angle": 135, "elevation_angle": -8.0, "length": 3, "width": 1, "shaping_flap": false}, {"name": "right_wing", "start": "wing_root", "end": "right_wing_tip", "azimuth_angle": -135, "elevation_angle": -8.0, "length": 3, "width": 1, "shaping_flap": false}, {"name": "left_canard", "start": "nose", "end": "left_canard_tip", "azimuth_angle": 110, "elevation_angle": -16.0, "length": 1, "width": 1, "shaping_flap": false}, {"name": "right_canard", "start": "nose", "end": "right_canard_tip", "azimuth_angle": -110, "elevation_angle": -16.0, "length": 1, "width": 1, "shaping_flap": false}, {"name": "left_tail_fin", "start": "tail_base", "end": "left_tail_tip", "azimuth_angle": 90, "elevation_angle": 90, "length": 1, "width": 1, "shaping_flap": false}, {"name": "right_tail_fin", "start": "tail_base", "end": "right_tail_tip", "azimuth_angle": -90, "elevation_angle": 90, "length": 1, "width": 1, "shaping_flap": false}]}
""")

WAVED_ALBATROSS = stick_figure.StickFigure.from_json("""
{"name": "waved_albatross", "category": "birds", "complexity": 2, "root": "body", "children": [{"name": "body", "start": "hips", "end": "chest", "azimuth_angle": 0, "elevation_angle": 0, "length": 4, "width": 2, "shaping_flap": false}, {"name": "neck_head_beak", "start": "chest", "end": "beak_tip", "azimuth_angle": -0.0, "elevation_angle": 39.00827799860619, "length": 5, "width": 1, "shaping_flap": false}, {"name": "left_wing_upper_left_wing_lower", "start": "chest", "end": "left_wing_tip", "azimuth_angle": 80.0, "elevation_angle": -8.0, "length": 12, "width": 1, "shaping_flap": false}, {"name": "right_wing_upper_right_wing_lower", "start": "chest", "end": "right_wing_tip", "azimuth_angle": -80.0, "elevation_angle": -8.0, "length": 12, "width": 1, "shaping_flap": false}, {"name": "left_leg_upper_left_leg_lower", "start": "hips", "end": "left_foot", "azimuth_angle": 90.0, "elevation_angle": -90.0, "length": 4, "width": 1, "shaping_flap": false}, {"name": "right_leg_upper_right_leg_lower", "start": "hips", "end": "right_foot", "azimuth_angle": -90.0, "elevation_angle": -90.0, "length": 4, "width": 1, "shaping_flap": false}, {"name": "tail", "start": "hips", "end": "tail_tip", "azimuth_angle": 180, "elevation_angle": -10, "length": 2, "width": 1, "shaping_flap": false}]}
""")

PHANTOM_F4 = stick_figure.StickFigure.from_json("""{
  "name": "phantom f-4",
  "category": "airplanes",
  "complexity": 1,
  "root": "fuselage_rear",
  "children": [
    {
      "name": "fuselage_rear",
      "start": "tail_base",
      "end": "wing_root",
      "azimuth_angle": -0.0,
      "elevation_angle": 0.0,
      "length": 5,
      "width": 2,
      "shaping_flap": false
    },
    {
      "name": "fuselage_front",
      "start": "wing_root",
      "end": "nose_tip",
      "azimuth_angle": -0.0,
      "elevation_angle": 0.0,
      "length": 4,
      "width": 2,
      "shaping_flap": false
    },
    {
      "name": "left_wing",
      "start": "wing_root",
      "end": "left_wing_tip",
      "azimuth_angle": 130.0,
      "elevation_angle": 8.0,
      "length": 5,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "right_wing",
      "start": "wing_root",
      "end": "right_wing_tip",
      "azimuth_angle": -130.0,
      "elevation_angle": 8.0,
      "length": 5,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "left_horizontal_stabilizer",
      "start": "tail_base",
      "end": "left_stabilizer_tip",
      "azimuth_angle": 140.0,
      "elevation_angle": -25.000000000000004,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "right_horizontal_stabilizer",
      "start": "tail_base",
      "end": "right_stabilizer_tip",
      "azimuth_angle": -140.0,
      "elevation_angle": -25.000000000000004,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "vertical_stabilizer",
      "start": "tail_base",
      "end": "fin_tip",
      "azimuth_angle": -0.0,
      "elevation_angle": 90.0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    }
  ]
}""")

UNDERWATER_SENSOR = stick_figure.StickFigure(
    name="underwater_sensor",
    category="watercraft",
    complexity=2,
    root="main_body",
    children=[
        stick_lib.Stick(
            name="main_body",
            start="rear_joint",
            end="front_joint",
            azimuth_angle=0,
            elevation_angle=0,
            length=5,
            width=2,
            shaping_flap=False,
        ),
        stick_lib.Stick(
            name="front_cone",
            start="front_joint",
            end="tip_joint",
            azimuth_angle=0,
            elevation_angle=8,
            length=1,
            width=2,
            shaping_flap=False,
        ),
        stick_lib.Stick(
            name="top_stabilizer",
            start="rear_joint",
            end="top_tip",
            azimuth_angle=0,
            elevation_angle=90,
            length=2,
            width=1,
            shaping_flap=False,
        ),
        stick_lib.Stick(
            name="bottom_stabilizer",
            start="rear_joint",
            end="bottom_tip",
            azimuth_angle=0,
            elevation_angle=-90,
            length=2,
            width=1,
            shaping_flap=False,
        ),
        stick_lib.Stick(
            name="left_sensor",
            start="front_joint",
            end="left_sensor_tip",
            azimuth_angle=90,
            elevation_angle=8,
            length=1,
            width=1,
            shaping_flap=False,
        ),
        stick_lib.Stick(
            name="right_sensor",
            start="front_joint",
            end="right_sensor_tip",
            azimuth_angle=-90,
            elevation_angle=8,
            length=1,
            width=1,
            shaping_flap=False,
        ),
    ],
)

SPRAYER = stick_figure.StickFigure.from_json("""{
  "name": "sprayer",
  "category": "machines",
  "complexity": 1,
  "root": "chassis",
  "children": [
    {
      "name": "chassis",
      "start": "rear_axle",
      "end": "front_axle",
      "azimuth_angle": 0,
      "elevation_angle": 8.0,
      "length": 5,
      "width": 2,
      "shaping_flap": false
    },
    {
      "name": "cab",
      "start": "front_axle",
      "end": "cab_top",
      "azimuth_angle": 0,
      "elevation_angle": 60,
      "length": 2,
      "width": 2,
      "shaping_flap": false
    },
    {
      "name": "tank",
      "start": "rear_axle",
      "end": "tank_top",
      "azimuth_angle": 0,
      "elevation_angle": 90,
      "length": 3,
      "width": 2,
      "shaping_flap": false
    },
    {
      "name": "left_boom",
      "start": "rear_axle",
      "end": "left_boom_tip",
      "azimuth_angle": 90,
      "elevation_angle": 16.0,
      "length": 8,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "right_boom",
      "start": "rear_axle",
      "end": "right_boom_tip",
      "azimuth_angle": -90,
      "elevation_angle": 16.0,
      "length": 8,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "front_left_wheel",
      "start": "front_axle",
      "end": "front_left_contact",
      "azimuth_angle": 90,
      "elevation_angle": -90,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "front_right_wheel",
      "start": "front_axle",
      "end": "front_right_contact",
      "azimuth_angle": -90,
      "elevation_angle": -90,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "rear_left_wheel",
      "start": "rear_axle",
      "end": "rear_left_contact",
      "azimuth_angle": 90,
      "elevation_angle": -90,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "rear_right_wheel",
      "start": "rear_axle",
      "end": "rear_right_contact",
      "azimuth_angle": -90,
      "elevation_angle": -90,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    }
  ]
}""")


JAGUAR = stick_figure.StickFigure.from_json("""
{
  "name": "Jaguar",
  "category": "animals",
  "complexity": 1,
  "root": "body",
  "children": [
    {
      "name": "body",
      "start": "hips",
      "end": "shoulders",
      "azimuth_angle": -0.0,
      "elevation_angle": 0.0,
      "length": 5,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "tail",
      "start": "hips",
      "end": "tail_tip",
      "azimuth_angle": -180.0,
      "elevation_angle": 0.0,
      "length": 4,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "rear_left_leg",
      "start": "hips",
      "end": "rear_left_paw",
      "azimuth_angle": -80.0,
      "elevation_angle": 0.0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "rear_right_leg",
      "start": "hips",
      "end": "rear_right_paw",
      "azimuth_angle": 80.00000000000001,
      "elevation_angle": 0.0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "front_left_leg",
      "start": "shoulders",
      "end": "front_left_paw",
      "azimuth_angle": -100.0,
      "elevation_angle": 0.0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "head",
      "start": "shoulders",
      "end": "nose",
      "azimuth_angle": -0.0,
      "elevation_angle": 0.0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "front_right_leg",
      "start": "shoulders",
      "end": "front_right_paw",
      "azimuth_angle": 100.0,
      "elevation_angle": 0.0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    }
  ]
}""")


EMBEDDED_ENGINE = stick_figure.StickFigure.from_json("""
{
  "name": "embedded_engine",
  "category": "airplanes",
  "complexity": 1,
  "root": "nacelle_front",
  "children": [
    {
      "name": "nacelle_front",
      "start": "intake",
      "end": "pylon_mount",
      "azimuth_angle": -0.0,
      "elevation_angle": 0.0,
      "length": 2,
      "width": 2,
      "shaping_flap": false
    },
    {
      "name": "nacelle_rear",
      "start": "pylon_mount",
      "end": "exhaust",
      "azimuth_angle": -0.0,
      "elevation_angle": 0.0,
      "length": 3,
      "width": 2,
      "shaping_flap": false
    },
    {
      "name": "pylon",
      "start": "pylon_mount",
      "end": "wing_mount",
      "azimuth_angle": 8.0,
      "elevation_angle": 90.0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    }
  ]
}""")


PAYLOAD_BAY = stick_figure.StickFigure.from_json("""{
  "name": "payload_bay",
  "category": "airplanes",
  "complexity": 1,
  "root": "bay_floor",
  "children": [
    {
      "name": "bay_floor",
      "start": "rear_center",
      "end": "front_center",
      "azimuth_angle": -0.0,
      "elevation_angle": 0.0,
      "length": 8,
      "width": 2,
      "shaping_flap": false
    },
    {
      "name": "left_wall_strut",
      "start": "rear_center",
      "end": "left_rear_top",
      "azimuth_angle": -90.0,
      "elevation_angle": 8.0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "right_wall_strut",
      "start": "rear_center",
      "end": "right_rear_top",
      "azimuth_angle": 90.0,
      "elevation_angle": 8.0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "front_left_strut",
      "start": "front_center",
      "end": "left_front_top",
      "azimuth_angle": -90.0,
      "elevation_angle": 8.0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "front_right_strut",
      "start": "front_center",
      "end": "right_front_top",
      "azimuth_angle": 90.0,
      "elevation_angle": 8.0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    }
  ]
}""")


HUMAN_VARIANT_1 = stick_figure.StickFigure.from_json("""{
  "name": "topology_figure",
  "category": "custom",
  "complexity": 1,
  "root": "stick_1117",
  "children": [
    {
      "name": "stick_1117",
      "start": "j_2",
      "end": "j_1",
      "azimuth_angle": 90,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_8156",
      "start": "j_1",
      "end": "j_0",
      "azimuth_angle": 0,
      "elevation_angle": 0,
      "length": 1,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_8058",
      "start": "j_1",
      "end": "j_3",
      "azimuth_angle": 90,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_4362",
      "start": "j_4",
      "end": "j_1",
      "azimuth_angle": 0,
      "elevation_angle": 0,
      "length": 1,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_8355",
      "start": "j_4",
      "end": "j_5",
      "azimuth_angle": -89.91,
      "elevation_angle": 0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_4884",
      "start": "j_4",
      "end": "j_6",
      "azimuth_angle": 90,
      "elevation_angle": 0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    }
  ]
}""")


HUMAN_VARIANT_2 = stick_figure.StickFigure.from_json("""{
  "name": "topology_figure",
  "category": "custom",
  "complexity": 1,
  "root": "stick_1117",
  "children": [
    {
      "name": "stick_1117",
      "start": "j_2",
      "end": "j_1",
      "azimuth_angle": 125.55,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_8156",
      "start": "j_1",
      "end": "j_0",
      "azimuth_angle": -12.03,
      "elevation_angle": 0,
      "length": 1,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_8058",
      "start": "j_1",
      "end": "j_3",
      "azimuth_angle": 32.44,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_4362",
      "start": "j_4",
      "end": "j_1",
      "azimuth_angle": 0,
      "elevation_angle": 0,
      "length": 1,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_8355",
      "start": "j_4",
      "end": "j_5",
      "azimuth_angle": -82.76,
      "elevation_angle": 0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_4884",
      "start": "j_4",
      "end": "j_6",
      "azimuth_angle": 130.86,
      "elevation_angle": 0,
      "length": 3,
      "width": 1,
      "shaping_flap": false
    }
  ]
}""")


HUMAN_VARIANT_3 = stick_figure.StickFigure.from_json("""{
  "name": "topology_figure",
  "category": "custom",
  "complexity": 1,
  "root": "stick_1117",
  "children": [
    {
      "name": "stick_1117",
      "start": "j_2",
      "end": "j_1",
      "length": 2,
      "width": 1,
      "azimuth_angle": 125.55,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "stick_8156",
      "start": "j_1",
      "end": "j_0",
      "length": 1,
      "width": 1,
      "azimuth_angle": -12.03,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "stick_8058",
      "start": "j_1",
      "end": "j_3",
      "length": 2,
      "width": 1,
      "azimuth_angle": 32.44,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "stick_4362",
      "start": "j_4",
      "end": "j_1",
      "length": 1,
      "width": 1,
      "azimuth_angle": 0,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "stick_8355",
      "start": "j_4",
      "end": "j_5",
      "length": 3,
      "width": 1,
      "azimuth_angle": 104.24,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "stick_4884",
      "start": "j_4",
      "end": "j_6",
      "length": 3,
      "width": 1,
      "azimuth_angle": 130.86,
      "elevation_angle": 0,
      "shaping_flap": false
    }
  ]
}""")


HUMAN_VARIANT_4 = stick_figure.StickFigure.from_json("""{
  "name": "topology_figure",
  "category": "custom",
  "complexity": 1,
  "root": "stick_1117",
  "children": [
    {
      "name": "stick_1117",
      "start": "j_2",
      "end": "j_1",
      "length": 2,
      "width": 1,
      "azimuth_angle": -123.57,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "stick_8156",
      "start": "j_1",
      "end": "j_0",
      "length": 1,
      "width": 1,
      "azimuth_angle": -12.03,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "stick_8058",
      "start": "j_1",
      "end": "j_3",
      "length": 2,
      "width": 1,
      "azimuth_angle": -68.58,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "stick_4362",
      "start": "j_4",
      "end": "j_1",
      "length": 1,
      "width": 1,
      "azimuth_angle": 0,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "stick_8355",
      "start": "j_4",
      "end": "j_5",
      "length": 3,
      "width": 1,
      "azimuth_angle": -150.37,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "stick_4884",
      "start": "j_4",
      "end": "j_6",
      "length": 3,
      "width": 1,
      "azimuth_angle": 130.86,
      "elevation_angle": 0,
      "shaping_flap": false
    }
  ]
}""")


HUMAN_VARIANT_5 = stick_figure.StickFigure.from_json("""{
  "name": "topology_figure",
  "category": "custom",
  "complexity": 1,
  "root": "stick_1117",
  "children": [
    {
      "name": "stick_1117",
      "start": "j_2",
      "end": "j_1",
      "length": 2,
      "width": 1,
      "azimuth_angle": 90,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "stick_8156",
      "start": "j_1",
      "end": "j_0",
      "length": 2,
      "width": 1,
      "azimuth_angle": 0,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "stick_8058",
      "start": "j_1",
      "end": "j_3",
      "length": 2,
      "width": 1,
      "azimuth_angle": 90,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "stick_4362",
      "start": "j_4",
      "end": "j_1",
      "length": 1,
      "width": 1,
      "azimuth_angle": 0,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "stick_8355",
      "start": "j_4",
      "end": "j_5",
      "length": 3,
      "width": 1,
      "azimuth_angle": -90,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "stick_4884",
      "start": "j_4",
      "end": "j_6",
      "length": 3,
      "width": 1,
      "azimuth_angle": 90,
      "elevation_angle": 0,
      "shaping_flap": false
    }
  ]
}""")


RIVER_STAIRCASE = stick_figure.StickFigure.from_json("""{
  "name": "river_staircase",
  "category": "custom",
  "complexity": 1,
  "root": "stick_6594",
  "children": [
    {
      "name": "stick_6594",
      "start": "j_2",
      "end": "j_0",
      "azimuth_angle": 88.23,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_5159",
      "start": "j_1",
      "end": "j_2",
      "azimuth_angle": 0,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_3164",
      "start": "j_0",
      "end": "j_5",
      "azimuth_angle": 2.66,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_4660",
      "start": "j_1",
      "end": "j_4",
      "azimuth_angle": 178.21,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_194",
      "start": "j_1",
      "end": "j_3",
      "azimuth_angle": -90,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_7483",
      "start": "j_5",
      "end": "j_6",
      "azimuth_angle": 88.88,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_5744",
      "start": "j_6",
      "end": "j_7",
      "azimuth_angle": 1.03,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_6023",
      "start": "j_7",
      "end": "j_8",
      "azimuth_angle": 90.01,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_3974",
      "start": "j_8",
      "end": "j_10",
      "azimuth_angle": 0.01,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "stick_2728",
      "start": "j_8",
      "end": "j_9",
      "azimuth_angle": 90.01,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    }
  ]
}""")


PACKING_HUMAN_32X32 = stick_figure.StickFigure.from_json("""{
  "name": "human",
  "category": "custom",
  "complexity": 1,
  "root": "torso",
  "children": [
    {
      "name": "head",
      "start": "chest",
      "end": "head",
      "length": 4,
      "width": 1,
      "azimuth_angle": 0,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "right_arm",
      "start": "chest",
      "end": "right_hand",
      "length": 12,
      "width": 1,
      "azimuth_angle": -90,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "left_arm",
      "start": "chest",
      "end": "left_hand",
      "length": 12,
      "width": 1,
      "azimuth_angle": 90,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "torso",
      "start": "hips",
      "end": "chest",
      "length": 4,
      "width": 1,
      "azimuth_angle": 0,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "right_leg",
      "start": "hips",
      "end": "right_foot",
      "length": 16,
      "width": 1,
      "azimuth_angle": -90,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "left_leg",
      "start": "hips",
      "end": "left_foot",
      "length": 16,
      "width": 1,
      "azimuth_angle": 90,
      "elevation_angle": 0,
      "shaping_flap": false
    }
  ]
}""")

PACKING_DANCER = dataclasses.replace(PACKING_HUMAN_32X32, name="packing_dancer")

PACKING_HUMAN_32X32_CONTORTION = stick_figure.StickFigure(
    name="human",
    category="humans",
    color_top=[247, 215, 216],
    color_bottom=[247, 215, 216],
    complexity=1,
    root="torso",
    children=[
        stick_lib.Stick(
            name="torso",
            start="hips",
            end="shoulders",
            azimuth_angle=0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="head_top",
            azimuth_angle=0,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="right_arm_lower",
            start="shoulders",
            end="right_hand",
            azimuth_angle=-135,
            length=8,
            elevation_angle=0,
        ),
        stick_lib.Stick(
            name="right_arm_upper",
            start="right_hand",
            end="right_finger_tips",
            azimuth_angle=-90,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="left_arm_lower",
            start="shoulders",
            end="left_hand",
            azimuth_angle=135,
            length=8,
            elevation_angle=0,
        ),
        stick_lib.Stick(
            name="left_arm_upper",
            start="left_hand",
            end="left_finger_tips",
            azimuth_angle=45,
            length=4,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="right_leg_lower",
            start="hips",
            end="right_foot",
            azimuth_angle=-135,
            length=8,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="right_leg_upper",
            start="right_foot",
            end="right_toes",
            azimuth_angle=90,
            length=8,
            elevation_angle=0,
        ),
        stick_lib.Stick(
            name="left_leg_lower",
            start="hips",
            end="left_foot",
            azimuth_angle=135,
            length=8,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="left_leg_upper",
            start="left_foot",
            end="left_toes",
            azimuth_angle=0,
            length=8,
            elevation_angle=0,
        ),
    ],
)

LIZARD_ALEX = stick_figure.StickFigure.from_dict({
    "name": "topology_figure",
    "category": "custom",
    "complexity": 1,
    "root": "stick_3209",
    "children": [
        {
            "name": "stick_3209",
            "start": "j_0",
            "end": "j_1",
            "length": 4,
            "width": 1,
            "azimuth_angle": -180,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_4106",
            "start": "j_3",
            "end": "j_2",
            "length": 1,
            "width": 1,
            "azimuth_angle": 180,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_4190",
            "start": "j_2",
            "end": "j_5",
            "length": 1,
            "width": 1,
            "azimuth_angle": 90,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_4490",
            "start": "j_2",
            "end": "j_4",
            "length": 1,
            "width": 1,
            "azimuth_angle": 180,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_5470",
            "start": "j_2",
            "end": "j_0",
            "length": 2,
            "width": 1,
            "azimuth_angle": -90,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_1581",
            "start": "j_0",
            "end": "j_6",
            "length": 2,
            "width": 1,
            "azimuth_angle": -90,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_115",
            "start": "j_6",
            "end": "j_7",
            "length": 1,
            "width": 1,
            "azimuth_angle": 180,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_8067",
            "start": "j_6",
            "end": "j_8",
            "length": 1,
            "width": 1,
            "azimuth_angle": -90,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_5555",
            "start": "j_6",
            "end": "j_9",
            "length": 1,
            "width": 1,
            "azimuth_angle": 0,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_2513",
            "start": "j_11",
            "end": "j_10",
            "length": 1,
            "width": 1,
            "azimuth_angle": 180,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_3797",
            "start": "j_12",
            "end": "j_10",
            "length": 1,
            "width": 1,
            "azimuth_angle": 90,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_5192",
            "start": "j_13",
            "end": "j_10",
            "length": 1,
            "width": 1,
            "azimuth_angle": 0,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_4528",
            "start": "j_1",
            "end": "j_10",
            "length": 2,
            "width": 1,
            "azimuth_angle": -90,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_4563",
            "start": "j_1",
            "end": "j_14",
            "length": 2,
            "width": 1,
            "azimuth_angle": 90,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_704",
            "start": "j_14",
            "end": "j_15",
            "length": 1,
            "width": 1,
            "azimuth_angle": 0,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_3043",
            "start": "j_14",
            "end": "j_16",
            "length": 1,
            "width": 1,
            "azimuth_angle": 90,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_1433",
            "start": "j_14",
            "end": "j_17",
            "length": 1,
            "width": 1,
            "azimuth_angle": 180,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_4336",
            "start": "j_18",
            "end": "j_0",
            "length": 2,
            "width": 1,
            "azimuth_angle": 180,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
        {
            "name": "stick_3613",
            "start": "j_1",
            "end": "j_19",
            "length": 6,
            "width": 1,
            "azimuth_angle": 180,
            "elevation_angle": 0,
            "shaping_flap": False,
        },
    ],
})


SKIER = stick_figure.StickFigure.from_json("""{
  "name": "skier",
  "category": "custom",
  "complexity": 1,
  "root": "Left Thigh",
  "children": [
    {
      "name": "Left Thigh",
      "start": "Hips / Pelvis",
      "end": "Left Knee",
      "azimuth_angle": 105.8,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Left Shin",
      "start": "Left Knee",
      "end": "Left Ankle",
      "azimuth_angle": 162.06,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Left Boot",
      "start": "Left Ankle",
      "end": "Left Heel / Ski Attachment",
      "azimuth_angle": -179.11,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Left Ski Rear-Tail",
      "start": "Left Heel / Ski Attachment",
      "end": "Left Ski Tail Segment",
      "azimuth_angle": 104.7,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Left Ski Rear",
      "start": "Left Ski Tail Segment",
      "end": "Left Ski Rear Segment",
      "azimuth_angle": 106.53,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Left Ski Underfoot",
      "start": "Left Ski Rear Segment",
      "end": "Left Ski Mid Segment",
      "azimuth_angle": -77.88,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Left Ski Front",
      "start": "Left Ski Mid Segment",
      "end": "Left Ski Front Segment",
      "azimuth_angle": -79.11,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Left Ski Tip",
      "start": "Left Ski Front Segment",
      "end": "Left Ski Tip",
      "azimuth_angle": -79.11,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Lower Spine",
      "start": "Hips / Pelvis",
      "end": "Mid-Torso",
      "azimuth_angle": -0.78,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Upper Spine",
      "start": "Mid-Torso",
      "end": "Neck / Shoulders",
      "azimuth_angle": 0.08,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Left Upper Arm",
      "start": "Neck / Shoulders",
      "end": "Left Elbow",
      "azimuth_angle": 121.85,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Left Forearm",
      "start": "Left Elbow",
      "end": "Left Wrist / Hand",
      "azimuth_angle": 36.36,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Left Ski Pole Upper",
      "start": "Left Wrist / Hand",
      "end": "Left Ski Pole Segment 1",
      "azimuth_angle": 128.8,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Left Ski Pole Mid-Upper",
      "start": "Left Ski Pole Segment 1",
      "end": "Left Ski Pole Segment 2",
      "azimuth_angle": 128.8,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Left Ski Pole Mid-Lower",
      "start": "Left Ski Pole Segment 2",
      "end": "Left Ski Pole Segment 3",
      "azimuth_angle": 128.8,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Left Ski Pole Lower",
      "start": "Left Ski Pole Segment 3",
      "end": "Left Ski Pole Tip",
      "azimuth_angle": 128.8,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Right Thigh",
      "start": "Hips / Pelvis",
      "end": "Right Knee",
      "azimuth_angle": 141.05,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Right Shin",
      "start": "Right Knee",
      "end": "Right Ankle",
      "azimuth_angle": 177.53,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Right Boot",
      "start": "Right Ankle",
      "end": "Right Heel / Ski Attachment",
      "azimuth_angle": 176.13,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Right Ski Rear-Tail",
      "start": "Right Heel / Ski Attachment",
      "end": "Right Ski Tail Segment",
      "azimuth_angle": 105.76,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Right Ski Rear",
      "start": "Right Ski Tail Segment",
      "end": "Right Ski Rear Segment",
      "azimuth_angle": 105.29,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Right Ski Underfoot",
      "start": "Right Ski Rear Segment",
      "end": "Right Ski Mid Segment",
      "azimuth_angle": -79.25,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Right Ski Front",
      "start": "Right Ski Mid Segment",
      "end": "Right Ski Front Segment",
      "azimuth_angle": -79.25,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Right Ski Tip",
      "start": "Right Ski Front Segment",
      "end": "Right Ski Tip",
      "azimuth_angle": -79.25,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Right Upper Arm",
      "start": "Neck / Shoulders",
      "end": "Right Elbow",
      "azimuth_angle": -160.54,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Right Forearm",
      "start": "Right Elbow",
      "end": "Right Wrist / Hand",
      "azimuth_angle": -73.63,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Right Ski Pole Upper",
      "start": "Right Wrist / Hand",
      "end": "Right Ski Pole Segment 1",
      "azimuth_angle": 174.82,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Right Ski Pole Mid-Upper",
      "start": "Right Ski Pole Segment 1",
      "end": "Right Ski Pole Segment 2",
      "azimuth_angle": 174.82,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Right Ski Pole Mid-Lower",
      "start": "Right Ski Pole Segment 2",
      "end": "Right Ski Pole Segment 3",
      "azimuth_angle": 174.82,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Right Ski Pole Lower",
      "start": "Right Ski Pole Segment 3",
      "end": "Right Ski Pole Tip",
      "azimuth_angle": 174.82,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Neck Column",
      "start": "Neck / Shoulders",
      "end": "Base of Head / Upper Neck",
      "azimuth_angle": 0.08,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "Head Structure",
      "start": "Base of Head / Upper Neck",
      "end": "Top of Head",
      "azimuth_angle": -171.16,
      "elevation_angle": 0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    }
  ]
}""")


# NOTE: cow made from 32x32 human stick figure.
merge_converter = {
    "head": "head",
    "forward_right_leg": "right_arm",
    "forward_left_leg": "left_arm",
    "torso": "torso",
    "backward_right_leg": "right_leg",
    "backward_left_leg": "left_leg",
}
COW_HUMAN = stick_figure.StickFigure.from_json("""{
  "name": "simple_cow_human",
  "category": "custom",
  "complexity": 1,
  "root": "head",
  "children": [
    {
      "name": "head",
      "start": "chest",
      "end": "head",
      "length": 4,
      "width": 1,
      "azimuth_angle": 66.24,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "forward_right_leg",
      "start": "chest",
      "end": "forward_right_hoof",
      "length": 12,
      "width": 1,
      "azimuth_angle": 158.94,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "forward_left_leg",
      "start": "chest",
      "end": "forward_left_hoof",
      "length": 12,
      "width": 1,
      "azimuth_angle": 179.85,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "torso",
      "start": "hips",
      "end": "chest",
      "length": 4,
      "width": 1,
      "azimuth_angle": 89.85,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "backward_right_leg",
      "start": "hips",
      "end": "backward_right_hoof",
      "length": 16,
      "width": 1,
      "azimuth_angle": -179.76,
      "elevation_angle": 0,
      "shaping_flap": false
    },
    {
      "name": "backward_left_leg",
      "start": "hips",
      "end": "backward_left_hoof",
      "length": 16,
      "width": 1,
      "azimuth_angle": -156.4,
      "elevation_angle": 0,
      "shaping_flap": false
    }
  ]
}""")


GROSBEAK = stick_figure.StickFigure.from_json("""{
  "name": "Grosbeak",
  "category": "birds",
  "complexity": 1,
  "root": "body",
  "children": [
    {
      "name": "body",
      "start": "tail_base",
      "end": "neck_base",
      "azimuth_angle": 0.0,
      "elevation_angle": 8.0,
      "length": 3,
      "width": 3,
      "shaping_flap": false
    },
    {
      "name": "head",
      "start": "neck_base",
      "end": "head_top",
      "azimuth_angle": -45.0,
      "elevation_angle": 8.0,
      "length": 2,
      "width": 3,
      "shaping_flap": false
    },
    {
      "name": "beak",
      "start": "neck_base",
      "end": "beak_tip",
      "azimuth_angle": 0.0,
      "elevation_angle": 0.0,
      "length": 1,
      "width": 2,
      "shaping_flap": false
    },
    {
      "name": "tail",
      "start": "tail_base",
      "end": "tail_tip",
      "azimuth_angle": 180.0,
      "elevation_angle": 8.0,
      "length": 2,
      "width": 2,
      "shaping_flap": false
    },
    {
      "name": "leg",
      "start": "tail_base",
      "end": "foot",
      "azimuth_angle": 90.0,
      "elevation_angle": -8.0,
      "length": 2,
      "width": 1,
      "shaping_flap": false
    },
    {
      "name": "wing",
      "start": "neck_base",
      "end": "wing_tip",
      "azimuth_angle": 135.0,
      "elevation_angle": 8.0,
      "length": 3,
      "width": 2,
      "shaping_flap": false
    }
  ]
}""")

COAT_RACK = stick_figure.StickFigure(
    name="coat_rack",
    category="Furniture",
    color_top=[80, 80, 80],
    color_bottom=[80, 80, 80],
    complexity=3,
    root="main_pole",
    children=[
        stick_lib.Stick(
            name="main_pole",
            start="base",
            end="top",
            azimuth_angle=0,
            elevation_angle=90,
            length=8,
            width=2,
        ),
        stick_lib.Stick(
            name="leg_front_left",
            start="base",
            end="leg_fl_tip",
            azimuth_angle=45,
            elevation_angle=-75,
            length=3,
            width=2,
        ),
        stick_lib.Stick(
            name="leg_front_right",
            start="base",
            end="leg_fr_tip",
            azimuth_angle=-45,
            elevation_angle=-75,
            length=3,
            width=2,
        ),
        stick_lib.Stick(
            name="leg_back_left",
            start="base",
            end="leg_bl_tip",
            azimuth_angle=135,
            elevation_angle=-75,
            length=3,
            width=2,
        ),
        stick_lib.Stick(
            name="leg_back_right",
            start="base",
            end="leg_br_tip",
            azimuth_angle=-135,
            elevation_angle=-75,
            length=3,
            width=2,
        ),
        stick_lib.Stick(
            name="bar_left_inner",
            start="top",
            end="hook4_mount",
            azimuth_angle=90,
            length=2,
            width=2,
        ),
        stick_lib.Stick(
            name="bar_left_outer",
            start="hook4_mount",
            end="bar_left_end",
            azimuth_angle=90,
            length=2,
            width=2,
        ),
        stick_lib.Stick(
            name="bar_right_inner",
            start="top",
            end="hook5_mount",
            azimuth_angle=-90,
            length=2,
            width=2,
        ),
        stick_lib.Stick(
            name="bar_right_outer",
            start="hook5_mount",
            end="bar_right_end",
            azimuth_angle=-90,
            length=2,
            width=2,
        ),
        stick_lib.Stick(
            name="hook1_shank",
            start="bar_left_end",
            end="hook1_bend",
            azimuth_angle=0,
            elevation_angle=-90,
            length=2,
        ),
        stick_lib.Stick(
            name="hook1_curve",
            start="hook1_bend",
            end="hook1_tip",
            azimuth_angle=0,
            elevation_angle=-45,
            length=1,
        ),
        stick_lib.Stick(
            name="hook4_shank",
            start="hook4_mount",
            end="hook4_bend",
            azimuth_angle=0,
            elevation_angle=-90,
            length=2,
        ),
        stick_lib.Stick(
            name="hook4_curve",
            start="hook4_bend",
            end="hook4_tip",
            azimuth_angle=0,
            elevation_angle=-45,
            length=1,
        ),
        stick_lib.Stick(
            name="hook2_shank",
            start="top",
            end="hook2_bend",
            azimuth_angle=0,
            elevation_angle=-90,
            length=2,
        ),
        stick_lib.Stick(
            name="hook2_curve",
            start="hook2_bend",
            end="hook2_tip",
            azimuth_angle=0,
            elevation_angle=-45,
            length=1,
        ),
        stick_lib.Stick(
            name="hook5_shank",
            start="hook5_mount",
            end="hook5_bend",
            azimuth_angle=0,
            elevation_angle=-90,
            length=2,
        ),
        stick_lib.Stick(
            name="hook5_curve",
            start="hook5_bend",
            end="hook5_tip",
            azimuth_angle=0,
            elevation_angle=-45,
            length=1,
        ),
        stick_lib.Stick(
            name="hook3_shank",
            start="bar_right_end",
            end="hook3_bend",
            azimuth_angle=0,
            elevation_angle=-90,
            length=2,
        ),
        stick_lib.Stick(
            name="hook3_curve",
            start="hook3_bend",
            end="hook3_tip",
            azimuth_angle=0,
            elevation_angle=-45,
            length=1,
        ),
    ],
)

PULL_UP_BAR = stick_figure.StickFigure(
    name="pull_up_bar",
    category="Sports Equipment",
    color_top=[50, 50, 50],
    color_bottom=[50, 50, 50],
    complexity=3,
    root="bar_center",
    children=[
        stick_lib.Stick(
            name="bar_center",
            start="center_left_joint",
            end="center_right_joint",
            azimuth_angle=90,
            length=2,
            width=2,
        ),
        stick_lib.Stick(
            name="bar_left_section",
            start="center_left_joint",
            end="bar_left_mount_joint",
            azimuth_angle=-90,
            length=3,
            width=2,
        ),
        stick_lib.Stick(
            name="bar_right_section",
            start="center_right_joint",
            end="bar_right_mount_joint",
            azimuth_angle=90,
            length=3,
            width=2,
        ),
        stick_lib.Stick(
            name="left_angled_grip",
            start="bar_left_mount_joint",
            end="left_angled_grip_end",
            azimuth_angle=315,
            elevation_angle=8,
            length=2,
            width=2,
        ),
        stick_lib.Stick(
            name="right_angled_grip",
            start="bar_right_mount_joint",
            end="right_angled_grip_end",
            azimuth_angle=45,
            elevation_angle=8,
            length=2,
            width=2,
        ),
        stick_lib.Stick(
            name="left_short_grip",
            start="center_left_joint",
            end="left_short_grip_end",
            azimuth_angle=0,
            length=2,
            width=2,
        ),
        stick_lib.Stick(
            name="right_short_grip",
            start="center_right_joint",
            end="right_short_grip_end",
            azimuth_angle=0,
            length=2,
            width=2,
        ),
        stick_lib.Stick(
            name="left_mount",
            start="bar_left_mount_joint",
            end="door_left_mount_point",
            azimuth_angle=180,
            length=1,
        ),
        stick_lib.Stick(
            name="right_mount",
            start="bar_right_mount_joint",
            end="door_right_mount_point",
            azimuth_angle=180,
            length=1,
        ),
        stick_lib.Stick(
            name="door_left_post_up",
            start="door_left_mount_point",
            end="top_left_corner",
            azimuth_angle=0,
            elevation_angle=8,
            length=2,
        ),
        stick_lib.Stick(
            name="door_left_post_down",
            start="door_left_mount_point",
            end="floor_left",
            azimuth_angle=180,
            length=6,
        ),
        stick_lib.Stick(
            name="door_right_post_up",
            start="door_right_mount_point",
            end="top_right_corner",
            azimuth_angle=0,
            elevation_angle=8,
            length=2,
        ),
        stick_lib.Stick(
            name="door_right_post_down",
            start="door_right_mount_point",
            end="floor_right",
            azimuth_angle=180,
            length=6,
        ),
    ],
)


BUTTERFLY = stick_figure.StickFigure.from_json("""{
  "name": "Butterfly opening its wings in the category Anatomy",
  "category": "Anatomy",
  "color_top": [
    255,
    140,
    0
  ],
  "color_bottom": [
    255,
    215,
    0
  ],
  "complexity": 3,
  "root": "body",
  "children": [
    {
      "name": "body",
      "start": "abdomen_tip",
      "end": "thorax",
      "azimuth_angle": 180,
      "elevation_angle": 0.0,
      "length": 4,
      "width": 1.0,
      "shaping_flap": false
    },
    {
      "name": "head",
      "start": "thorax",
      "end": "head_joint",
      "azimuth_angle": 0,
      "elevation_angle": 0.0,
      "length": 1,
      "width": 1.0,
      "shaping_flap": false
    },
    {
      "name": "left_antenna",
      "start": "head_joint",
      "end": "left_antenna_tip",
      "azimuth_angle": -45,
      "elevation_angle": 8.0,
      "length": 3,
      "width": 1.0,
      "shaping_flap": false
    },
    {
      "name": "right_antenna",
      "start": "head_joint",
      "end": "right_antenna_tip",
      "azimuth_angle": 45,
      "elevation_angle": 8.0,
      "length": 3,
      "width": 1.0,
      "shaping_flap": false
    },
    {
      "name": "left_forewing_base",
      "start": "thorax",
      "end": "left_forewing_joint",
      "azimuth_angle": -80,
      "elevation_angle": 0.0,
      "length": 5,
      "width": 2.0,
      "shaping_flap": false
    },
    {
      "name": "right_forewing_base",
      "start": "thorax",
      "end": "right_forewing_joint",
      "azimuth_angle": 80,
      "elevation_angle": 0.0,
      "length": 5,
      "width": 2.0,
      "shaping_flap": false
    },
    {
      "name": "left_forewing_edge",
      "start": "left_forewing_joint",
      "end": "left_forewing_tip",
      "azimuth_angle": -45,
      "elevation_angle": 0.0,
      "length": 4,
      "width": 2.0,
      "shaping_flap": false
    },
    {
      "name": "right_forewing_edge",
      "start": "right_forewing_joint",
      "end": "right_forewing_tip",
      "azimuth_angle": 45,
      "elevation_angle": 0.0,
      "length": 4,
      "width": 2.0,
      "shaping_flap": false
    },
    {
      "name": "left_hindwing_base",
      "start": "thorax",
      "end": "left_hindwing_joint",
      "azimuth_angle": -135,
      "elevation_angle": 0.0,
      "length": 4,
      "width": 2.0,
      "shaping_flap": false
    },
    {
      "name": "right_hindwing_base",
      "start": "thorax",
      "end": "right_hindwing_joint",
      "azimuth_angle": 135,
      "elevation_angle": 0.0,
      "length": 4,
      "width": 2.0,
      "shaping_flap": false
    },
    {
      "name": "left_hindwing_edge",
      "start": "left_hindwing_joint",
      "end": "left_hindwing_tip",
      "azimuth_angle": -160,
      "elevation_angle": 0.0,
      "length": 5,
      "width": 2.0,
      "shaping_flap": false
    },
    {
      "name": "right_hindwing_edge",
      "start": "right_hindwing_joint",
      "end": "right_hindwing_tip",
      "azimuth_angle": 160,
      "elevation_angle": 0.0,
      "length": 5,
      "width": 2.0,
      "shaping_flap": false
    }
  ],
  "shaping_flaps_limit": 0
}""")


MOOSE = stick_figure.StickFigure(
    name="Moose with intricate branching antler patterns and points",
    category="Wild Animal",
    color_top=[92, 64, 51],
    color_bottom=[160, 120, 90],
    complexity=3,
    root="body_core",
    children=[
        stick_lib.Stick(
            name="body_core",
            start="rear_hips",
            end="front_shoulders",
            azimuth_angle=0,
            elevation_angle=0.0,
            length=6,
            width=4,
        ),
        stick_lib.Stick(
            name="neck",
            start="front_shoulders",
            end="head_base",
            azimuth_angle=0,
            elevation_angle=45,
            length=3,
            width=2,
        ),
        stick_lib.Stick(
            name="head",
            start="head_base",
            end="muzzle",
            azimuth_angle=0,
            elevation_angle=-15,
            length=2,
            width=2,
        ),
        stick_lib.Stick(
            name="front_left_upper",
            start="front_shoulders",
            end="fl_knee",
            azimuth_angle=90,
            elevation_angle=-60,
            length=4,
            width=1.0,
        ),
        stick_lib.Stick(
            name="front_left_lower",
            start="fl_knee",
            end="fl_hoof",
            azimuth_angle=90,
            elevation_angle=-90,
            length=4,
            width=1.0,
        ),
        stick_lib.Stick(
            name="front_right_upper",
            start="front_shoulders",
            end="fr_knee",
            azimuth_angle=-90,
            elevation_angle=-60,
            length=4,
            width=1.0,
        ),
        stick_lib.Stick(
            name="front_right_lower",
            start="fr_knee",
            end="fr_hoof",
            azimuth_angle=-90,
            elevation_angle=-90,
            length=4,
            width=1.0,
        ),
        stick_lib.Stick(
            name="rear_left_upper",
            start="rear_hips",
            end="rl_knee",
            azimuth_angle=90,
            elevation_angle=-60,
            length=4,
            width=1.0,
        ),
        stick_lib.Stick(
            name="rear_left_lower",
            start="rl_knee",
            end="rl_hoof",
            azimuth_angle=90,
            elevation_angle=-90,
            length=4,
            width=1.0,
        ),
        stick_lib.Stick(
            name="rear_right_upper",
            start="rear_hips",
            end="rr_knee",
            azimuth_angle=-90,
            elevation_angle=-60,
            length=4,
            width=1.0,
        ),
        stick_lib.Stick(
            name="rear_right_lower",
            start="rr_knee",
            end="rr_hoof",
            azimuth_angle=-90,
            elevation_angle=-90,
            length=4,
            width=1.0,
        ),
        stick_lib.Stick(
            name="tail",
            start="rear_hips",
            end="tail_tip",
            azimuth_angle=180,
            elevation_angle=-20,
            length=1,
            width=1.0,
        ),
        stick_lib.Stick(
            name="l_antler_main",
            start="head_base",
            end="l_hub",
            azimuth_angle=90,
            elevation_angle=60,
            length=2,
            width=1.0,
        ),
        stick_lib.Stick(
            name="r_antler_main",
            start="head_base",
            end="r_hub",
            azimuth_angle=-90,
            elevation_angle=60,
            length=2,
            width=1.0,
        ),
        stick_lib.Stick(
            name="l_palm_1",
            start="l_hub",
            end="l_p1",
            azimuth_angle=60,
            elevation_angle=30,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="l_p1_pt1",
            start="l_p1",
            end="l_p1a",
            azimuth_angle=50,
            elevation_angle=50,
            length=1,
            width=0.25,
        ),
        stick_lib.Stick(
            name="l_p1_pt2",
            start="l_p1",
            end="l_p1b",
            azimuth_angle=70,
            elevation_angle=50,
            length=1,
            width=0.25,
        ),
        stick_lib.Stick(
            name="l_palm_2",
            start="l_hub",
            end="l_p2",
            azimuth_angle=90,
            elevation_angle=20,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="l_p2_pt1",
            start="l_p2",
            end="l_p2a",
            azimuth_angle=85,
            elevation_angle=50,
            length=1,
            width=0.25,
        ),
        stick_lib.Stick(
            name="l_p2_pt2",
            start="l_p2",
            end="l_p2b",
            azimuth_angle=95,
            elevation_angle=50,
            length=1,
            width=0.25,
        ),
        stick_lib.Stick(
            name="l_palm_3",
            start="l_hub",
            end="l_p3",
            azimuth_angle=120,
            elevation_angle=30,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="l_p3_pt1",
            start="l_p3",
            end="l_p3a",
            azimuth_angle=110,
            elevation_angle=50,
            length=1,
            width=0.25,
        ),
        stick_lib.Stick(
            name="l_p3_pt2",
            start="l_p3",
            end="l_p3b",
            azimuth_angle=130,
            elevation_angle=50,
            length=1,
            width=0.25,
        ),
        stick_lib.Stick(
            name="r_palm_1",
            start="r_hub",
            end="r_p1",
            azimuth_angle=-60,
            elevation_angle=30,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="r_p1_pt1",
            start="r_p1",
            end="r_p1a",
            azimuth_angle=-50,
            elevation_angle=50,
            length=1,
            width=0.25,
        ),
        stick_lib.Stick(
            name="r_p1_pt2",
            start="r_p1",
            end="r_p1b",
            azimuth_angle=-70,
            elevation_angle=50,
            length=1,
            width=0.25,
        ),
        stick_lib.Stick(
            name="r_palm_2",
            start="r_hub",
            end="r_p2",
            azimuth_angle=-90,
            elevation_angle=20,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="r_p2_pt1",
            start="r_p2",
            end="r_p2a",
            azimuth_angle=-85,
            elevation_angle=50,
            length=1,
            width=0.25,
        ),
        stick_lib.Stick(
            name="r_p2_pt2",
            start="r_p2",
            end="r_p2b",
            azimuth_angle=-95,
            elevation_angle=50,
            length=1,
            width=0.25,
        ),
        stick_lib.Stick(
            name="r_palm_3",
            start="r_hub",
            end="r_p3",
            azimuth_angle=-120,
            elevation_angle=30,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="r_p3_pt1",
            start="r_p3",
            end="r_p3a",
            azimuth_angle=-110,
            elevation_angle=50,
            length=1,
            width=0.25,
        ),
        stick_lib.Stick(
            name="r_p3_pt2",
            start="r_p3",
            end="r_p3b",
            azimuth_angle=-130,
            elevation_angle=50,
            length=1,
            width=0.25,
        ),
    ],
)

RED_CLAW_SCORPION = stick_figure.StickFigure(
    name="Red claw scorpion with distinctive reddish pincers",
    category="diverse scorpions",
    color_top=[30, 30, 30],
    complexity=3,
    root="body_1",
    children=[
        stick_lib.Stick(
            name="body_1",
            start="hips",
            end="m1",
            azimuth_angle=0,
            elevation_angle=0,
            length=1,
            width=3,
        ),
        stick_lib.Stick(
            name="body_2",
            start="m1",
            end="m2",
            azimuth_angle=0,
            elevation_angle=0,
            length=1,
            width=3,
        ),
        stick_lib.Stick(
            name="body_3",
            start="m2",
            end="shoulders",
            azimuth_angle=0,
            elevation_angle=0,
            length=1,
            width=3,
        ),
        stick_lib.Stick(
            name="tail_1",
            start="hips",
            end="tj1",
            azimuth_angle=180,
            elevation_angle=10,
            length=3,
            width=2,
        ),
        stick_lib.Stick(
            name="tail_2",
            start="tj1",
            end="tj2",
            azimuth_angle=180,
            elevation_angle=40,
            length=2,
            width=2,
        ),
        stick_lib.Stick(
            name="tail_3",
            start="tj2",
            end="tj3",
            azimuth_angle=180,
            elevation_angle=80,
            length=2,
            width=2,
        ),
        stick_lib.Stick(
            name="tail_4",
            start="tj3",
            end="tj4",
            azimuth_angle=0,
            elevation_angle=45,
            length=2,
            width=2,
        ),
        stick_lib.Stick(
            name="stinger",
            start="tj4",
            end="sting",
            azimuth_angle=0,
            elevation_angle=-10,
            length=1,
            width=0.5,
        ),
        stick_lib.Stick(
            name="leg_L1_p",
            start="shoulders",
            end="kL1",
            azimuth_angle=70,
            elevation_angle=45,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="leg_L1_d",
            start="kL1",
            end="fL1",
            azimuth_angle=45,
            elevation_angle=-60,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="leg_R1_p",
            start="shoulders",
            end="kR1",
            azimuth_angle=-70,
            elevation_angle=45,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="leg_R1_d",
            start="kR1",
            end="fR1",
            azimuth_angle=-45,
            elevation_angle=-60,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="leg_L2_p",
            start="m2",
            end="kL2",
            azimuth_angle=75,
            elevation_angle=45,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="leg_L2_d",
            start="kL2",
            end="fL2",
            azimuth_angle=75,
            elevation_angle=-60,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="leg_R2_p",
            start="m2",
            end="kR2",
            azimuth_angle=-75,
            elevation_angle=45,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="leg_R2_d",
            start="kR2",
            end="fR2",
            azimuth_angle=-75,
            elevation_angle=-60,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="leg_L3_p",
            start="m1",
            end="kL3",
            azimuth_angle=105,
            elevation_angle=45,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="leg_L3_d",
            start="kL3",
            end="fL3",
            azimuth_angle=105,
            elevation_angle=-60,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="leg_R3_p",
            start="m1",
            end="kR3",
            azimuth_angle=-105,
            elevation_angle=45,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="leg_R3_d",
            start="kR3",
            end="fR3",
            azimuth_angle=-105,
            elevation_angle=-60,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="leg_L4_p",
            start="hips",
            end="kL4",
            azimuth_angle=135,
            elevation_angle=45,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="leg_L4_d",
            start="kL4",
            end="fL4",
            azimuth_angle=135,
            elevation_angle=-40,
            length=3,
            width=0.5,
        ),
        stick_lib.Stick(
            name="leg_R4_p",
            start="hips",
            end="kR4",
            azimuth_angle=-135,
            elevation_angle=45,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="leg_R4_d",
            start="kR4",
            end="fR4",
            azimuth_angle=-135,
            elevation_angle=-40,
            length=3,
            width=0.5,
        ),
        stick_lib.Stick(
            name="pedi_L_arm",
            start="shoulders",
            end="eL",
            azimuth_angle=40,
            elevation_angle=10,
            length=3,
            width=1.0,
        ),
        stick_lib.Stick(
            name="pedi_L_hand",
            start="eL",
            end="wL",
            azimuth_angle=30,
            elevation_angle=0,
            length=2,
            width=1.0,
        ),
        stick_lib.Stick(
            name="pincer_L_upper",
            start="wL",
            end="tLU",
            azimuth_angle=20,
            elevation_angle=0,
            length=4,
            width=0.5,
        ),
        stick_lib.Stick(
            name="pincer_L_lower",
            start="wL",
            end="tLL",
            azimuth_angle=50,
            elevation_angle=0,
            length=3,
            width=2,
        ),
        stick_lib.Stick(
            name="pincer_L_lower_2",
            start="tLL",
            end="tLL2",
            azimuth_angle=20,
            elevation_angle=0,
            length=2,
            width=0.5,
        ),
        stick_lib.Stick(
            name="pedi_R_arm",
            start="shoulders",
            end="eR",
            azimuth_angle=-40,
            elevation_angle=10,
            length=3,
            width=1.0,
        ),
        stick_lib.Stick(
            name="pedi_R_hand",
            start="eR",
            end="wR",
            azimuth_angle=-30,
            elevation_angle=0,
            length=2,
            width=1.0,
        ),
        stick_lib.Stick(
            name="pincer_R_upper",
            start="wR",
            end="tRU",
            azimuth_angle=-10,
            elevation_angle=0,
            length=4,
            width=0.5,
        ),
        stick_lib.Stick(
            name="pincer_R_lower",
            start="wR",
            end="tRL",
            azimuth_angle=-50,
            elevation_angle=0,
            length=3,
            width=2,
        ),
        stick_lib.Stick(
            name="pincer_R_lower_2",
            start="tRL",
            end="tRL2",
            azimuth_angle=-20,
            elevation_angle=0,
            length=2,
            width=0.5,
        ),
    ],
)

SIMPLE_STAR = stick_figure.StickFigure(
    name="simple_star",
    category="custom",
    complexity=1,
    root="s1",
    children=[
        stick_lib.Stick(
            name="s1",
            start="j0",
            end="j1",
            azimuth_angle=0,
            length=4,
        ),
        stick_lib.Stick(
            name="s2",
            start="j0",
            end="j2",
            azimuth_angle=180,
            length=4,
        ),
        stick_lib.Stick(
            name="s3",
            start="j0",
            end="j3",
            azimuth_angle=90,
            length=4,
        ),
        stick_lib.Stick(
            name="s4",
            start="j0",
            end="j4",
            azimuth_angle=-90,
            length=4,
        ),
    ],
)

BPS_SIMPLE_STAR = {
    "version": "0.7",
    "design": {
        "title": "SimpleStarBPS",
        "mode": "tree",
        "description": "",
        "layout": {
            "sheet": {"type": "rect", "height": 16, "width": 16},
            "flaps": [
                {"id": 1, "x": 8, "y": 10, "width": 0, "height": 0},
                {"id": 2, "x": 8, "y": 6, "width": 0, "height": 0},
                {"id": 3, "x": 12, "y": 8, "width": 0, "height": 0},
                {"id": 4, "x": 5, "y": 8, "width": 0, "height": 0},
            ],
            "stretches": [],
        },
        "tree": {
            "sheet": {"type": "rect", "height": 20, "width": 20},
            "nodes": [
                {"id": 0, "name": "", "x": 10, "y": 10},
                {"id": 1, "name": "", "x": 10, "y": 13},
                {"id": 2, "name": "", "x": 10, "y": 7},
                {"id": 3, "name": "", "x": 15, "y": 10},
                {"id": 4, "name": "", "x": 6, "y": 10},
            ],
            "edges": [
                {"n1": 0, "n2": 1, "length": 4},
                {"n1": 0, "n2": 2, "length": 4},
                {"n1": 0, "n2": 3, "length": 4},
                {"n1": 0, "n2": 4, "length": 4},
            ],
        },
    },
}

BPS_SYMMETRIC_STAR = {
    "version": "0.7",
    "design": {
        "title": "Untitled",
        "mode": "tree",
        "description": "",
        "layout": {
            "sheet": {"type": "rect", "height": 16, "width": 16},
            "flaps": [
                {"id": 1, "x": 8, "y": 10, "width": 0, "height": 0},
                {"id": 2, "x": 6, "y": 9, "width": 0, "height": 0},
                {"id": 3, "x": 8, "y": 6, "width": 0, "height": 0},
                {"id": 4, "x": 6, "y": 7, "width": 0, "height": 0},
            ],
            "stretches": [],
        },
        "tree": {
            "sheet": {"type": "rect", "height": 20, "width": 20},
            "nodes": [
                {"id": 0, "name": "", "x": 10, "y": 10},
                {"id": 1, "name": "", "x": 10, "y": 13},
                {"id": 2, "name": "", "x": 13, "y": 9},
                {"id": 3, "name": "", "x": 10, "y": 7},
                {"id": 4, "name": "", "x": 7, "y": 9},
            ],
            "edges": [
                {"n1": 0, "n2": 1, "length": 2},
                {"n1": 0, "n2": 4, "length": 2},
                {"n1": 0, "n2": 3, "length": 2},
                {"n1": 0, "n2": 2, "length": 2},
            ],
        },
    },
}

DIVER_BACKFLIP = stick_figure.StickFigure(
    name="diver_backflip",
    category="humans",
    complexity=2,
    root="torso",
    children=[
        stick_lib.Stick(
            name="torso",
            start="shoulders",
            end="hips",
            length=4,
            azimuth_angle=0,
            elevation_angle=-90.0,
        ),
        stick_lib.Stick(
            name="neck_head",
            start="shoulders",
            end="head_top",
            length=3,
            width=2,
            azimuth_angle=0,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="left_upper_arm_left_forearm",
            start="shoulders",
            end="left_hand",
            length=4,
            azimuth_angle=135,
            elevation_angle=-20.0,
        ),
        stick_lib.Stick(
            name="right_upper_arm_right_forearm",
            start="shoulders",
            end="right_hand",
            length=4,
            azimuth_angle=-135,
            elevation_angle=-20.0,
        ),
        stick_lib.Stick(
            name="left_thigh_left_calf",
            start="hips",
            end="left_foot",
            length=6,
            azimuth_angle=135,
            elevation_angle=-60.0,
        ),
        stick_lib.Stick(
            name="right_thigh_right_calf",
            start="hips",
            end="right_foot",
            length=6,
            azimuth_angle=-135,
            elevation_angle=-60.0,
        ),
    ],
)

ARTIST_SCULPTING = stick_figure.StickFigure(
    name="An artist sculpting a clay pot",
    category="Characters",
    complexity=2,
    root="torso",
    children=[
        stick_lib.Stick(
            name="torso",
            start="shoulders",
            end="hips",
            length=4,
            azimuth_angle=0,
            elevation_angle=-90.0,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="head_top",
            length=2,
            azimuth_angle=0,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="left_upper_arm_left_forearm",
            start="shoulders",
            end="left_hand",
            length=5,
            azimuth_angle=135,
            elevation_angle=-20.0,
        ),
        stick_lib.Stick(
            name="right_upper_arm_right_forearm",
            start="shoulders",
            end="right_hand",
            length=5,
            azimuth_angle=-135,
            elevation_angle=-20.0,
        ),
        stick_lib.Stick(
            name="left_thigh_left_shin",
            start="hips",
            end="left_foot",
            length=6,
            azimuth_angle=135,
            elevation_angle=-60.0,
        ),
        stick_lib.Stick(
            name="right_thigh_right_shin",
            start="hips",
            end="right_foot",
            length=6,
            azimuth_angle=-135,
            elevation_angle=-60.0,
        ),
        stick_lib.Stick(
            name="wheel_post_pot_base_pot_body_pot_neck",
            start="hips",
            end="pot_top",
            length=8,
            azimuth_angle=0,
            elevation_angle=-90.0,
        ),
    ],
)

FROG_LEAPING = stick_figure.StickFigure(
    name="Frog leaping in air",
    category="Anatomy",
    complexity=2,
    root="torso",
    children=[
        stick_lib.Stick(
            name="torso",
            start="shoulders",
            end="hips",
            length=4,
            azimuth_angle=0,
            elevation_angle=-90.0,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="head_top",
            length=2,
            azimuth_angle=0,
            elevation_angle=90.0,
        ),
        stick_lib.Stick(
            name="left_eye",
            start="head_top",
            end="left_eye_tip",
            length=1,
            azimuth_angle=135,
            elevation_angle=30.0,
        ),
        stick_lib.Stick(
            name="right_eye",
            start="head_top",
            end="right_eye_tip",
            length=1,
            azimuth_angle=-135,
            elevation_angle=30.0,
        ),
        stick_lib.Stick(
            name="left_upper_arm_left_forearm",
            start="shoulders",
            end="left_hand",
            length=4,
            azimuth_angle=135,
            elevation_angle=-20.0,
        ),
        stick_lib.Stick(
            name="right_upper_arm_right_forearm",
            start="shoulders",
            end="right_hand",
            length=4,
            azimuth_angle=-135,
            elevation_angle=-20.0,
        ),
        stick_lib.Stick(
            name="left_thigh_left_shin_left_foot",
            start="hips",
            end="left_foot",
            length=8,
            azimuth_angle=135,
            elevation_angle=-60.0,
        ),
        stick_lib.Stick(
            name="right_thigh_right_shin_right_foot",
            start="hips",
            end="right_foot",
            length=8,
            azimuth_angle=-135,
            elevation_angle=-60.0,
        ),
    ],
)


ELF_ARCHER = stick_figure.StickFigure(
    name="Elf",
    category="Mythology",
    color_top=[34, 139, 34],
    color_bottom=[244, 164, 96],
    complexity=3,
    root="torso",
    children=[
        stick_lib.Stick(
            name="torso",
            start="pelvis",
            end="shoulders",
            length=4,
            azimuth_angle=0,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="head",
            start="shoulders",
            end="head_top",
            length=2,
            azimuth_angle=0,
            elevation_angle=90,
        ),
        stick_lib.Stick(
            name="left_leg",
            start="pelvis",
            end="left_foot",
            length=5,
            azimuth_angle=-150,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="right_leg",
            start="pelvis",
            end="right_foot",
            length=5,
            azimuth_angle=150,
            elevation_angle=8,
        ),
        stick_lib.Stick(
            name="bow_arm",
            start="shoulders",
            end="left_hand",
            length=4,
            azimuth_angle=-110,
            elevation_angle=0.0,
        ),
        stick_lib.Stick(
            name="draw_arm_upper_draw_arm_lower_arrow",
            start="shoulders",
            end="arrow_tip",
            length=10,
            azimuth_angle=-134.08482197448626,
            elevation_angle=6.643633658233627,
        ),
        stick_lib.Stick(
            name="bow_upper_limb",
            start="left_hand",
            end="bow_top",
            length=4,
            azimuth_angle=-20,
            elevation_angle=8,
        ),
        stick_lib.Stick(
            name="bow_lower_limb",
            start="left_hand",
            end="bow_bottom",
            length=4,
            azimuth_angle=160,
            elevation_angle=-8,
        ),
    ],
)

TAILLESS_WHIP_SCORPION = stick_figure.StickFigure(
    name="Tailless whip scorpion",
    category="Arachnids",
    color_top=[60, 45, 30],
    color_bottom=[60, 45, 30],
    complexity=3,
    root="cephalothorax",
    children=[
        stick_lib.Stick(
            name="cephalothorax",
            start="abdomen_joint",
            end="head_joint",
            azimuth_angle=0,
            length=3,
        ),
        stick_lib.Stick(
            name="abdomen",
            start="abdomen_joint",
            end="abdomen_tip",
            azimuth_angle=180,
            length=4,
        ),
        stick_lib.Stick(
            name="left_pedipalp_base_left_pedipalp_pincer",
            start="head_joint",
            end="left_pedipalp_tip",
            azimuth_angle=-21.86271488737456,
            elevation_angle=-36.45838192975706,
            length=5,
        ),
        stick_lib.Stick(
            name="right_pedipalp_base_right_pedipalp_pincer",
            start="head_joint",
            end="right_pedipalp_tip",
            azimuth_angle=21.86271488737456,
            elevation_angle=-36.45838192975706,
            length=5,
        ),
        stick_lib.Stick(
            name="left_feeler_1_left_feeler_2",
            start="head_joint",
            end="left_feeler_tip",
            azimuth_angle=-74.47736243562552,
            elevation_angle=-50.106353667039,
            length=16,
        ),
        stick_lib.Stick(
            name="right_feeler_1_right_feeler_2",
            start="head_joint",
            end="right_feeler_tip",
            azimuth_angle=74.47736243562552,
            elevation_angle=-50.106353667039,
            length=16,
        ),
        stick_lib.Stick(
            name="left_leg2_1_left_leg2_2",
            start="abdomen_joint",
            end="left_leg2_foot",
            azimuth_angle=-104.08469692269274,
            elevation_angle=-50.231441734870494,
            length=10,
        ),
        stick_lib.Stick(
            name="right_leg2_1_right_leg2_2",
            start="abdomen_joint",
            end="right_leg2_foot",
            azimuth_angle=104.08469692269274,
            elevation_angle=-50.231441734870494,
            length=10,
        ),
        stick_lib.Stick(
            name="left_leg3_1_left_leg3_2",
            start="abdomen_joint",
            end="left_leg3_foot",
            azimuth_angle=-139.08469692269276,
            elevation_angle=-50.231441734870494,
            length=10,
        ),
        stick_lib.Stick(
            name="right_leg3_1_right_leg3_2",
            start="abdomen_joint",
            end="right_leg3_foot",
            azimuth_angle=139.08469692269276,
            elevation_angle=-50.231441734870494,
            length=10,
        ),
        stick_lib.Stick(
            name="left_leg4_1_left_leg4_2",
            start="abdomen_joint",
            end="left_leg4_foot",
            azimuth_angle=-169.08469692269273,
            elevation_angle=-50.231441734870494,
            length=10,
        ),
        stick_lib.Stick(
            name="right_leg4_1_right_leg4_2",
            start="abdomen_joint",
            end="right_leg4_foot",
            azimuth_angle=169.08469692269273,
            elevation_angle=-50.231441734870494,
            length=10,
        ),
    ],
)


def _make_human_with_fingers_sticks():
  """Builds shared, right-arm, and left-arm sticks for a human with fingers."""

  widths = [1, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]
  lengths = [6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

  right_arm_substicks = []
  prev_joint = "shoulders"
  for i, (l, w) in enumerate(zip(lengths, widths)):
    end_joint = (
        f"right_arm_j{i+1}" if i < len(widths) - 1 else "right_fingertip"
    )
    right_arm_substicks.append(
        stick_lib.Stick(
            name=f"right_arm_{i}",
            start=prev_joint,
            end=end_joint,
            azimuth_angle=-165,
            elevation_angle=-20.0,
            length=l,
            width=w,
        )
    )
    prev_joint = end_joint

  left_arm_substicks = []
  prev_joint = "shoulders"
  for i, (l, w) in enumerate(zip(lengths, widths)):
    end_joint = f"left_arm_j{i+1}" if i < len(widths) - 1 else "left_fingertip"
    left_arm_substicks.append(
        stick_lib.Stick(
            name=f"left_arm_{i}",
            start=prev_joint,
            end=end_joint,
            azimuth_angle=165,
            elevation_angle=-20.0,
            length=l,
            width=w,
        )
    )
    prev_joint = end_joint

  shared_sticks = [
      stick_lib.Stick(
          name="torso",
          start="hips",
          end="shoulders",
          azimuth_angle=0,
          length=4,
          width=2,
          elevation_angle=90.0,
      ),
      stick_lib.Stick(
          name="head",
          start="shoulders",
          end="head_top",
          azimuth_angle=0,
          length=2,
          width=1,
          elevation_angle=90.0,
      ),
      stick_lib.Stick(
          name="right_leg",
          start="hips",
          end="right_foot",
          azimuth_angle=-90,
          length=8,
          width=1,
          elevation_angle=-60.0,
      ),
      stick_lib.Stick(
          name="left_leg",
          start="hips",
          end="left_foot",
          azimuth_angle=90,
          length=8,
          width=1,
          elevation_angle=-60.0,
      ),
  ]

  total_arm_length = sum(lengths)
  return (
      shared_sticks,
      right_arm_substicks,
      left_arm_substicks,
      total_arm_length,
      widths,
  )


_HWF_SHARED, _HWF_RIGHT, _HWF_LEFT, _HWF_ARM_LEN, _HWF_WIDTHS = (
    _make_human_with_fingers_sticks()
)

HUMAN_WITH_FINGERS = stick_figure.StickFigure(
    name="human_with_fingers",
    category="humans",
    complexity=3,
    root="torso",
    children=[
        *_HWF_SHARED,
        stick_lib.Stick(
            name="right_arm",
            start="shoulders",
            end="right_fingertip",
            azimuth_angle=-165,
            elevation_angle=-20.0,
            length=_HWF_ARM_LEN,
            width=1,
        ),
        stick_lib.Stick(
            name="left_arm",
            start="shoulders",
            end="left_fingertip",
            azimuth_angle=165,
            elevation_angle=-20.0,
            length=_HWF_ARM_LEN,
            width=1,
        ),
    ],
)

HUMAN_WITH_FINGERS_UNMERGED = stick_figure.StickFigure(
    name="human_with_fingers_unmerged",
    category="humans",
    complexity=3,
    root="torso",
    children=[*_HWF_SHARED, *_HWF_RIGHT, *_HWF_LEFT],
)

HUMAN_WITH_FINGERS_MERGE_CONVERTER = {}
for _i in range(len(_HWF_WIDTHS)):
  HUMAN_WITH_FINGERS_MERGE_CONVERTER[f"right_arm_{_i}"] = "right_arm"
  HUMAN_WITH_FINGERS_MERGE_CONVERTER[f"left_arm_{_i}"] = "left_arm"

VIOLET_GROUND_BEETLE = stick_figure.StickFigure.from_json(
    r"""{"name": "Violet ground beetle with a purple shimmering shell edge", "category": "beetles", "color_top": [148, 0, 211], "color_bottom": [255, 255, 255], "complexity": 1, "root": "body_front", "children": [{"name": "body_front", "start": "center", "end": "anterior", "azimuth_angle": 0, "elevation_angle": 0.0, "length": 2, "width": 2, "shaping_flap": false}, {"name": "body_rear", "start": "center", "end": "posterior", "azimuth_angle": 180, "elevation_angle": 0.0, "length": 3, "width": 2, "shaping_flap": false}, {"name": "head", "start": "anterior", "end": "head_tip", "azimuth_angle": 0, "elevation_angle": 0.0, "length": 1, "width": 1.0, "shaping_flap": false}, {"name": "leg_fl", "start": "anterior", "end": "fl_tip", "azimuth_angle": 90, "elevation_angle": -45, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "leg_fr", "start": "anterior", "end": "fr_tip", "azimuth_angle": -90, "elevation_angle": -45, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "leg_ml", "start": "center", "end": "ml_tip", "azimuth_angle": 110, "elevation_angle": -45, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "leg_mr", "start": "center", "end": "mr_tip", "azimuth_angle": -110, "elevation_angle": -45, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "leg_bl", "start": "posterior", "end": "bl_tip", "azimuth_angle": 150, "elevation_angle": -45, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "leg_br", "start": "posterior", "end": "br_tip", "azimuth_angle": -150, "elevation_angle": -45, "length": 3, "width": 1.0, "shaping_flap": false}], "views": []}"""
)

AMERICAN_LOBSTER = stick_figure.StickFigure.from_json(
    r"""{"name": "American lobster", "category": "Crustaceans", "color_top": [84, 38, 38], "color_bottom": [180, 140, 100], "complexity": 3, "root": "cephalothorax", "children": [{"name": "cephalothorax", "start": "thorax_posterior", "end": "thorax_anterior", "azimuth_angle": 0, "elevation_angle": 0.0, "length": 5, "width": 2, "shaping_flap": false}, {"name": "abdomen", "start": "thorax_posterior", "end": "abdomen_mid", "azimuth_angle": 180, "elevation_angle": 0.0, "length": 4, "width": 2, "shaping_flap": false}, {"name": "tail_fan_center", "start": "abdomen_mid", "end": "telson_tip", "azimuth_angle": 180, "elevation_angle": 0.0, "length": 2, "width": 2, "shaping_flap": false}, {"name": "tail_fan_left", "start": "abdomen_mid", "end": "uropod_L_tip", "azimuth_angle": 210, "elevation_angle": 0.0, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "tail_fan_right", "start": "abdomen_mid", "end": "uropod_R_tip", "azimuth_angle": 150, "elevation_angle": 0.0, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "left_arm", "start": "thorax_anterior", "end": "wrist_L", "azimuth_angle": 45, "elevation_angle": 45, "length": 3, "width": 2, "shaping_flap": false}, {"name": "left_crusher_claw", "start": "wrist_L", "end": "crusher_tip", "azimuth_angle": 30, "elevation_angle": 30, "length": 4, "width": 2, "shaping_flap": false}, {"name": "left_dactyl", "start": "wrist_L", "end": "dactyl_L_tip", "azimuth_angle": 60, "elevation_angle": 15, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "right_arm", "start": "thorax_anterior", "end": "wrist_R", "azimuth_angle": -45, "elevation_angle": 45, "length": 3, "width": 2, "shaping_flap": false}, {"name": "right_pincer_claw", "start": "wrist_R", "end": "pincer_tip", "azimuth_angle": -30, "elevation_angle": 30, "length": 4, "width": 2, "shaping_flap": false}, {"name": "right_dactyl", "start": "wrist_R", "end": "dactyl_R_tip", "azimuth_angle": -60, "elevation_angle": 15, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "antenna_L", "start": "thorax_anterior", "end": "ant_tip_L", "azimuth_angle": 20, "elevation_angle": 10, "length": 8, "width": 1.0, "shaping_flap": false}, {"name": "antenna_R", "start": "thorax_anterior", "end": "ant_tip_R", "azimuth_angle": -20, "elevation_angle": 10, "length": 8, "width": 1.0, "shaping_flap": false}, {"name": "walking_leg_1L", "start": "thorax_posterior", "end": "foot_1L", "azimuth_angle": 90, "elevation_angle": -60, "length": 4, "width": 1.0, "shaping_flap": false}, {"name": "walking_leg_1R", "start": "thorax_posterior", "end": "foot_1R", "azimuth_angle": -90, "elevation_angle": -60, "length": 4, "width": 1.0, "shaping_flap": false}, {"name": "walking_leg_2L", "start": "thorax_posterior", "end": "foot_2L", "azimuth_angle": 110, "elevation_angle": -60, "length": 4, "width": 1.0, "shaping_flap": false}, {"name": "walking_leg_2R", "start": "thorax_posterior", "end": "foot_2R", "azimuth_angle": -110, "elevation_angle": -60, "length": 4, "width": 1.0, "shaping_flap": false}, {"name": "walking_leg_3L", "start": "thorax_anterior", "end": "foot_3L", "azimuth_angle": 70, "elevation_angle": -60, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "walking_leg_3R", "start": "thorax_anterior", "end": "foot_3R", "azimuth_angle": -70, "elevation_angle": -60, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "walking_leg_4L", "start": "thorax_posterior", "end": "foot_4L", "azimuth_angle": 130, "elevation_angle": -60, "length": 4, "width": 1.0, "shaping_flap": false}, {"name": "walking_leg_4R", "start": "thorax_posterior", "end": "foot_4R", "azimuth_angle": -130, "elevation_angle": -60, "length": 4, "width": 1.0, "shaping_flap": false}, {"name": "rostrum", "start": "thorax_anterior", "end": "rostrum_tip", "azimuth_angle": 0, "elevation_angle": 20, "length": 1, "width": 1.0, "shaping_flap": false}], "views": []}"""
)

SCORPION_LARGE_PINCERS = stick_figure.StickFigure.from_json("""{
  "name": "Scorpion with tail tip touching back and large pincers wide",
  "category": "scorpions with large pincers",
  "color_top": [30, 30, 30],
  "color_bottom": [255, 255, 255],
  "complexity": 2,
  "root": "body_mid",
  "children": [
    {"name": "body_mid", "start": "m1", "end": "m2", "azimuth_angle": 0.0, "elevation_angle": 0.0, "length": 2, "width": 3, "shaping_flap": false},
    {"name": "body_front", "start": "m2", "end": "shoulders", "azimuth_angle": 0.0, "elevation_angle": 0.0, "length": 2, "width": 3, "shaping_flap": false},
    {"name": "body_rear", "start": "m1", "end": "hips", "azimuth_angle": 180.0, "elevation_angle": 0.0, "length": 2, "width": 3, "shaping_flap": false},
    {"name": "tail_1", "start": "hips", "end": "tj1", "azimuth_angle": 180.0, "elevation_angle": 20.0, "length": 2, "width": 2, "shaping_flap": false},
    {"name": "tail_2", "start": "tj1", "end": "tj2", "azimuth_angle": 180.0, "elevation_angle": 65.0, "length": 2, "width": 2, "shaping_flap": false},
    {"name": "tail_3", "start": "tj2", "end": "tj3", "azimuth_angle": 0.0, "elevation_angle": 60.0, "length": 3, "width": 2, "shaping_flap": false},
    {"name": "tail_4", "start": "tj3", "end": "tj4", "azimuth_angle": 0.0, "elevation_angle": -10.0, "length": 2, "width": 1.0, "shaping_flap": false},
    {"name": "stinger", "start": "tj4", "end": "sting", "azimuth_angle": 0.0, "elevation_angle": -50.0, "length": 2, "width": 0.5, "shaping_flap": false},
    {"name": "pedi_L_arm", "start": "shoulders", "end": "eL", "azimuth_angle": 60.0, "elevation_angle": 10.0, "length": 4, "width": 1.0, "shaping_flap": false},
    {"name": "pincer_L_fixed", "start": "eL", "end": "pLf", "azimuth_angle": 95.0, "elevation_angle": 0.0, "length": 3, "width": 2, "shaping_flap": false},
    {"name": "pincer_L_move", "start": "eL", "end": "pLm", "azimuth_angle": 35.0, "elevation_angle": 0.0, "length": 3, "width": 0.5, "shaping_flap": false},
    {"name": "pedi_R_arm", "start": "shoulders", "end": "eR", "azimuth_angle": -60.0, "elevation_angle": 10.0, "length": 4, "width": 1.0, "shaping_flap": false},
    {"name": "pincer_R_fixed", "start": "eR", "end": "pRf", "azimuth_angle": -95.0, "elevation_angle": 0.0, "length": 3, "width": 2, "shaping_flap": false},
    {"name": "pincer_R_move", "start": "eR", "end": "pRm", "azimuth_angle": -35.0, "elevation_angle": 0.0, "length": 3, "width": 0.5, "shaping_flap": false},
    {"name": "leg_L1", "start": "shoulders", "end": "fL1", "azimuth_angle": 110.0, "elevation_angle": -35.0, "length": 3, "width": 0.5, "shaping_flap": false},
    {"name": "leg_R1", "start": "shoulders", "end": "fR1", "azimuth_angle": -110.0, "elevation_angle": -35.0, "length": 3, "width": 0.5, "shaping_flap": false},
    {"name": "leg_L2", "start": "m2", "end": "fL2", "azimuth_angle": 130.0, "elevation_angle": -35.0, "length": 3, "width": 0.5, "shaping_flap": false},
    {"name": "leg_R2", "start": "m2", "end": "fR2", "azimuth_angle": -130.0, "elevation_angle": -35.0, "length": 3, "width": 0.5, "shaping_flap": false},
    {"name": "leg_L3", "start": "m1", "end": "fL3", "azimuth_angle": 150.0, "elevation_angle": -35.0, "length": 3, "width": 0.5, "shaping_flap": false},
    {"name": "leg_R3", "start": "m1", "end": "fR3", "azimuth_angle": -150.0, "elevation_angle": -35.0, "length": 3, "width": 0.5, "shaping_flap": false},
    {"name": "leg_L4", "start": "hips", "end": "fL4", "azimuth_angle": 170.0, "elevation_angle": -35.0, "length": 3, "width": 0.5, "shaping_flap": false},
    {"name": "leg_R4", "start": "hips", "end": "fR4", "azimuth_angle": -170.0, "elevation_angle": -35.0, "length": 3, "width": 0.5, "shaping_flap": false}
  ],
  "views": [[8, 8, 8], [-8, 8, 8], [8, -8, 8], [-8, -8, 8], [0, 12, 2], [12, 0, 2], [0, 0, 15]]
}""")

SPIDER_MONKEY = stick_figure.StickFigure.from_json(
    r"""{"name": "Spider monkey with long limbs and a prehensile tail", "category": "animals with bizarre proportions", "color_top": [45, 30, 20], "color_bottom": [100, 80, 60], "complexity": 3, "root": "body_segment_main", "children": [{"name": "body_segment_main", "start": "pelvis", "end": "shoulders", "azimuth_angle": 0, "elevation_angle": 10, "length": 4, "width": 2, "shaping_flap": false}, {"name": "neck_head", "start": "shoulders", "end": "snout", "azimuth_angle": -0.0, "elevation_angle": 24.999999999999993, "length": 4, "width": 1.0, "shaping_flap": false}, {"name": "arm_left_upper_arm_left_lower", "start": "shoulders", "end": "wrist_left", "azimuth_angle": 85.6262995752614, "elevation_angle": 15.053842546016659, "length": 16, "width": 0.5, "shaping_flap": false}, {"name": "hand_left_1", "start": "wrist_left", "end": "finger_tip_L1", "azimuth_angle": 80, "elevation_angle": -40, "length": 2, "width": 0.25, "shaping_flap": false}, {"name": "hand_left_2", "start": "wrist_left", "end": "finger_tip_L2", "azimuth_angle": 100, "elevation_angle": -40, "length": 2, "width": 0.25, "shaping_flap": false}, {"name": "arm_right_upper_arm_right_lower", "start": "shoulders", "end": "wrist_right", "azimuth_angle": -85.6262995752614, "elevation_angle": 15.053842546016659, "length": 16, "width": 0.5, "shaping_flap": false}, {"name": "hand_right_1", "start": "wrist_right", "end": "finger_tip_R1", "azimuth_angle": -80, "elevation_angle": -40, "length": 2, "width": 0.25, "shaping_flap": false}, {"name": "hand_right_2", "start": "wrist_right", "end": "finger_tip_R2", "azimuth_angle": -100, "elevation_angle": -40, "length": 2, "width": 0.25, "shaping_flap": false}, {"name": "leg_left_upper_leg_left_lower", "start": "pelvis", "end": "ankle_left", "azimuth_angle": 148.50557128266396, "elevation_angle": -40.422839164441484, "length": 14, "width": 0.5, "shaping_flap": false}, {"name": "toe_left_1", "start": "ankle_left", "end": "toe_tip_L1", "azimuth_angle": 150, "elevation_angle": -80, "length": 2, "width": 0.25, "shaping_flap": false}, {"name": "toe_left_2", "start": "ankle_left", "end": "toe_tip_L2", "azimuth_angle": 170, "elevation_angle": -80, "length": 2, "width": 0.25, "shaping_flap": false}, {"name": "leg_right_upper_leg_right_lower", "start": "pelvis", "end": "ankle_right", "azimuth_angle": -148.50557128266396, "elevation_angle": -40.422839164441484, "length": 14, "width": 0.5, "shaping_flap": false}, {"name": "toe_right_1", "start": "ankle_right", "end": "toe_tip_R1", "azimuth_angle": -150, "elevation_angle": -80, "length": 2, "width": 0.25, "shaping_flap": false}, {"name": "toe_right_2", "start": "ankle_right", "end": "toe_tip_R2", "azimuth_angle": -170, "elevation_angle": -80, "length": 2, "width": 0.25, "shaping_flap": false}, {"name": "tail_seg_1_tail_seg_2_tail_seg_3_tail_seg_4", "start": "pelvis", "end": "tail_tip", "azimuth_angle": -6.441790574050209e-15, "elevation_angle": 66.56505117707799, "length": 24, "width": 0.5, "shaping_flap": false}], "views": [[20, 20, 20, 0, 0, 0, 0, 1, 0, 10, 0, 0, 0, 10, 0, 0, 0, 10, 5, 5, 5], [-20, 10, 10, 0, 0, 0, 0, 1, 0, -10, 0, 0, 0, 10, 0, 0, 0, 10, -5, 5, 5], [10, -20, 10, 0, 0, 0, 0, 1, 0, 10, 0, 0, 0, -10, 0, 0, 0, 10, 5, -5, 5]]}"""
)

HAMMERHEAD_SHARK = stick_figure.StickFigure.from_json(
    r"""{"name": "Hammerhead shark with a wide flat T-shaped head", "category": "animals with bizarre proportions", "color_top": [112, 128, 144], "color_bottom": [245, 245, 245], "complexity": 2, "root": "torso_core", "children": [{"name": "torso_core", "start": "mid_point", "end": "shoulder_joint", "azimuth_angle": 0, "elevation_angle": 0.0, "length": 3, "width": 4, "shaping_flap": false}, {"name": "torso_rear", "start": "mid_point", "end": "hip_joint", "azimuth_angle": 180, "elevation_angle": 0.0, "length": 4, "width": 4, "shaping_flap": false}, {"name": "neck", "start": "shoulder_joint", "end": "head_center", "azimuth_angle": 0, "elevation_angle": 0.0, "length": 2, "width": 4, "shaping_flap": false}, {"name": "hammer_left", "start": "head_center", "end": "eye_left", "azimuth_angle": 90, "elevation_angle": 0.0, "length": 4, "width": 2, "shaping_flap": false}, {"name": "hammer_right", "start": "head_center", "end": "eye_right", "azimuth_angle": -90, "elevation_angle": 0.0, "length": 4, "width": 2, "shaping_flap": false}, {"name": "pectoral_fin_L", "start": "shoulder_joint", "end": "pec_L_tip", "azimuth_angle": 120, "elevation_angle": -20, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "pectoral_fin_R", "start": "shoulder_joint", "end": "pec_R_tip", "azimuth_angle": -120, "elevation_angle": -20, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "dorsal_fin", "start": "mid_point", "end": "dorsal_tip", "azimuth_angle": 180, "elevation_angle": 70, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "tail_top", "start": "hip_joint", "end": "caudal_upper", "azimuth_angle": 180, "elevation_angle": 40, "length": 4, "width": 1.0, "shaping_flap": false}, {"name": "tail_bottom", "start": "hip_joint", "end": "caudal_lower", "azimuth_angle": 180, "elevation_angle": -40, "length": 2, "width": 1.0, "shaping_flap": false}], "views": [[12, 12, 12], [-12, 12, 12], [12, -12, 12], [12, 12, -12], [0, 18, 5], [18, 0, 5], [0, 5, 18]]}"""
)

SCORPION_WIDE_STANCE = stick_figure.StickFigure.from_json(
    r"""{"name": "Wide-pincered desert scorpion with thin tail and low stance", "category": "scorpions with distinct anatomy", "color_top": [237, 201, 175], "color_bottom": [255, 255, 255], "complexity": 2, "root": "body_mid", "children": [{"name": "body_mid", "start": "node_mid_rear", "end": "node_mid_front", "azimuth_angle": 0, "elevation_angle": 0.0, "length": 2, "width": 3, "shaping_flap": false}, {"name": "body_rear", "start": "node_mid_rear", "end": "node_rear", "azimuth_angle": 180, "elevation_angle": 0.0, "length": 2, "width": 3, "shaping_flap": false}, {"name": "body_front", "start": "node_mid_front", "end": "node_front", "azimuth_angle": 0, "elevation_angle": 0.0, "length": 2, "width": 3, "shaping_flap": false}, {"name": "leg_L1_u", "start": "node_front", "end": "kL1", "azimuth_angle": 60, "elevation_angle": 15, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "leg_L1_l", "start": "kL1", "end": "fL1", "azimuth_angle": 60, "elevation_angle": -60, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "leg_R1_u", "start": "node_front", "end": "kR1", "azimuth_angle": -60, "elevation_angle": 15, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "leg_R1_l", "start": "kR1", "end": "fR1", "azimuth_angle": -60, "elevation_angle": -60, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "leg_L2_u", "start": "node_mid_front", "end": "kL2", "azimuth_angle": 90, "elevation_angle": 15, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "leg_L2_l", "start": "kL2", "end": "fL2", "azimuth_angle": 90, "elevation_angle": -60, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "leg_R2_u", "start": "node_mid_front", "end": "kR2", "azimuth_angle": -90, "elevation_angle": 15, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "leg_R2_l", "start": "kR2", "end": "fR2", "azimuth_angle": -90, "elevation_angle": -60, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "leg_L3_u", "start": "node_mid_rear", "end": "kL3", "azimuth_angle": 120, "elevation_angle": 15, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "leg_L3_l", "start": "kL3", "end": "fL3", "azimuth_angle": 120, "elevation_angle": -60, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "leg_R3_u", "start": "node_mid_rear", "end": "kR3", "azimuth_angle": -120, "elevation_angle": 15, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "leg_R3_l", "start": "kR3", "end": "fR3", "azimuth_angle": -120, "elevation_angle": -60, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "leg_L4_u", "start": "node_rear", "end": "kL4", "azimuth_angle": 150, "elevation_angle": 15, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "leg_L4_l", "start": "kL4", "end": "fL4", "azimuth_angle": 150, "elevation_angle": -60, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "leg_R4_u", "start": "node_rear", "end": "kR4", "azimuth_angle": -150, "elevation_angle": 15, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "leg_R4_l", "start": "kR4", "end": "fR4", "azimuth_angle": -150, "elevation_angle": -60, "length": 2, "width": 1.0, "shaping_flap": false}, {"name": "tail_1", "start": "node_rear", "end": "tj1", "azimuth_angle": 180, "elevation_angle": 30, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "tail_2", "start": "tj1", "end": "tj2", "azimuth_angle": 180, "elevation_angle": 60, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "tail_3", "start": "tj2", "end": "stinger", "azimuth_angle": 0, "elevation_angle": 45, "length": 2, "width": 0.5, "shaping_flap": false}, {"name": "ped_L_a", "start": "node_front", "end": "elbow_L", "azimuth_angle": 40, "elevation_angle": 5, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "ped_L_w", "start": "elbow_L", "end": "wrist_L", "azimuth_angle": 15, "elevation_angle": 0.0, "length": 2, "width": 3, "shaping_flap": false}, {"name": "claw_L_u", "start": "wrist_L", "end": "tip_LU", "azimuth_angle": -10, "elevation_angle": 0.0, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "claw_L_l", "start": "wrist_L", "end": "tip_LL", "azimuth_angle": 40, "elevation_angle": 0.0, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "ped_R_a", "start": "node_front", "end": "elbow_R", "azimuth_angle": -40, "elevation_angle": 5, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "ped_R_w", "start": "elbow_R", "end": "wrist_R", "azimuth_angle": -15, "elevation_angle": 0.0, "length": 2, "width": 3, "shaping_flap": false}, {"name": "claw_R_u", "start": "wrist_R", "end": "tip_RU", "azimuth_angle": 10, "elevation_angle": 0.0, "length": 3, "width": 1.0, "shaping_flap": false}, {"name": "claw_R_l", "start": "wrist_R", "end": "tip_RL", "azimuth_angle": -40, "elevation_angle": 0.0, "length": 3, "width": 1.0, "shaping_flap": false}], "views": [[8, 8, 8], [-8, 8, 8], [8, -8, 8], [-8, -8, 8], [0, 10, 2], [0, -10, 5], [10, 0, 5]]}"""
)
