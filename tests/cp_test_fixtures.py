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

"""Pre-packed SVG crease pattern test fixtures for Box Pleating unit tests."""

import dataclasses
import functools

from bp_pipeline import bps_types
from bp_pipeline.crease_pattern import crease as crease_utils
from bp_pipeline.crease_pattern import crease_pattern
from bp_pipeline.crease_pattern.parser import svg as parser
from bp_pipeline.stick_figures import stick_figure as stick_figure_utils
from bp_pipeline.stick_figures.examples import example_trees as stick_figure_examples

BoxPleatingTreeData = bps_types.BoxPleatingTreeData


@dataclasses.dataclass(frozen=True, repr=False)
class BoxPleatingCreasePatternExample:
  """Contains a single box-pleating crease pattern test fixture."""

  name: str
  packing_svg: str
  grid_size: int
  tree_data: BoxPleatingTreeData | None = None
  stick_figure: stick_figure_utils.StickFigure | None = None
  unmerged_stick_figure: stick_figure_utils.StickFigure | None = None
  assigned_pleats_svg: str | None = None
  assigned_ridges_svg: str | None = None
  base_svg: str | None = None
  central_crease_removed: bool = False

  def __repr__(self) -> str:
    return f"{self.__class__.__name__}(name={self.name!r})"

  @functools.cached_property
  def packing_cp(self) -> crease_pattern.CreasePattern:
    return parser.parse_svg(self.packing_svg, grid_size=self.grid_size)

  @functools.cached_property
  def assigned_pleats_cp(self) -> crease_pattern.CreasePattern | None:
    if self.assigned_pleats_svg is None:
      return None
    return parser.parse_svg(self.assigned_pleats_svg, grid_size=self.grid_size)

  @functools.cached_property
  def assigned_ridges_cp(self) -> crease_pattern.CreasePattern | None:
    if self.assigned_ridges_svg is None:
      return None
    return parser.parse_svg(self.assigned_ridges_svg, grid_size=self.grid_size)

  @functools.cached_property
  def base_cp(self) -> crease_pattern.CreasePattern | None:
    if self.base_svg is None:
      return None
    return parser.parse_svg(self.base_svg, grid_size=self.grid_size)

  @functools.cached_property
  def base_creases(self) -> list[crease_utils.Crease]:
    """Returns the creases of the base crease pattern."""
    if self.base_cp is None:
      return []
    return self.base_cp.creases


def list_cp_fixtures() -> list[BoxPleatingCreasePatternExample]:
  """Returns a list of crease-pattern test fixture instances."""
  return [
      FLAPS_BETWEEN_RIVERS,
      MINI_HUMAN,
      NINE_TAIL,
      GENERATED1,
      GENERATED2,
      GENERATED3,
      GENERATED4,
      GENERATED5,
      GENERATED6,
      WATERBOMB,
      SPIDER,
      SCORPION,
      THREEFLAPSETSTWORIVERS,
      RIVERONEFLAP,
      GEMINI,
      HUMAN,
      HUMAN_WITH_CENTER,
      TALL_SHAPING_TEST_1,
      X_TEST,
      THREE_CONSECUTIVE_RIVERS,
      VALUTED_CANOPY,
      NONE_OVERLAPPING_PLEATS,
      SCORPION_LARGE_PINCERS,
  ]


def load_cp_fixture(name: str) -> BoxPleatingCreasePatternExample:
  """Returns the crease-pattern test fixture with the given name."""
  return load_cp_fixtures([name])[name]


def load_cp_fixtures(
    names: list[str] | None = None,
) -> dict[str, BoxPleatingCreasePatternExample]:
  """Returns all crease-pattern test fixtures defined in this file."""
  all_fixtures = list_cp_fixtures()
  fixture_dict = {e.name: e for e in all_fixtures}
  if names is None:
    return fixture_dict
  names_set = set(names)
  unknown_names = names_set - fixture_dict.keys()
  if unknown_names:
    raise ValueError(f"Unknown fixture names: {unknown_names}")
  return {name: fixture_dict[name] for name in names_set}


THREE_CONSECUTIVE_RIVERS = BoxPleatingCreasePatternExample(
    name="three_consecutive_rivers",
    tree_data={
        "version": "0.7",
        "design": {
            "title": "Three consecutive rivers",
            "mode": "tree",
            "description": "",
            "layout": {
                "sheet": {"type": "rect", "height": 16, "width": 16},
                "flaps": [
                    {"id": 1, "x": 7, "y": 10, "width": 0, "height": 0},
                    {"id": 2, "x": 4, "y": 10, "width": 0, "height": 0},
                    {"id": 7, "x": 10, "y": 2, "width": 0, "height": 0},
                    {"id": 8, "x": 6, "y": 2, "width": 0, "height": 0},
                    {"id": 4, "x": 13, "y": 8, "width": 0, "height": 0},
                    {"id": 9, "x": 10, "y": 10, "width": 0, "height": 0},
                ],
                "stretches": [],
            },
            "tree": {
                "sheet": {"type": "rect", "height": 20, "width": 20},
                "nodes": [
                    {"id": 0, "name": "", "x": 7, "y": 10},
                    {"id": 1, "name": "", "x": 9, "y": 13},
                    {"id": 2, "name": "", "x": 5, "y": 13},
                    {"id": 3, "name": "", "x": 10, "y": 8},
                    {"id": 4, "name": "", "x": 16, "y": 10},
                    {"id": 5, "name": "", "x": 13, "y": 10},
                    {"id": 6, "name": "", "x": 9, "y": 5},
                    {"id": 7, "name": "", "x": 12, "y": 2},
                    {"id": 8, "name": "", "x": 8, "y": 2},
                    {"id": 9, "name": "", "x": 13, "y": 13},
                ],
                "edges": [
                    {"n1": 3, "n2": 6, "length": 1},
                    {"n1": 3, "n2": 0, "length": 1},
                    {"n1": 3, "n2": 5, "length": 1},
                    {"n1": 6, "n2": 7, "length": 2},
                    {"n1": 6, "n2": 8, "length": 2},
                    {"n1": 0, "n2": 1, "length": 2},
                    {"n1": 0, "n2": 2, "length": 2},
                    {"n1": 5, "n2": 4, "length": 2},
                    {"n1": 5, "n2": 9, "length": 2},
                ],
            },
        },
    },
    packing_svg="",
    grid_size=0,
)

FLAPS_BETWEEN_RIVERS = BoxPleatingCreasePatternExample(
    name="flaps_between_rivers",
    tree_data={
        "version": "0.7",
        "design": {
            "title": "Untitled",
            "mode": "tree",
            "description": "",
            "layout": {
                "sheet": {"type": "rect", "height": 16, "width": 16},
                "flaps": [
                    {"id": 3, "x": 6, "y": 9, "width": 0, "height": 0},
                    {"id": 4, "x": 6, "y": 7, "width": 0, "height": 0},
                    {"id": 5, "x": 8, "y": 13, "width": 0, "height": 0},
                    {"id": 6, "x": 6, "y": 12, "width": 0, "height": 0},
                    {"id": 7, "x": 9, "y": 4, "width": 0, "height": 0},
                    {"id": 8, "x": 7, "y": 4, "width": 0, "height": 0},
                    {"id": 9, "x": 10, "y": 7, "width": 0, "height": 0},
                    {"id": 10, "x": 10, "y": 9, "width": 0, "height": 0},
                ],
                "stretches": [],
            },
            "tree": {
                "sheet": {"type": "rect", "height": 20, "width": 20},
                "nodes": [
                    {"id": 0, "name": "", "x": 10, "y": 10},
                    {"id": 1, "name": "", "x": 10, "y": 13},
                    {"id": 2, "name": "", "x": 10, "y": 7},
                    {"id": 3, "name": "", "x": 8, "y": 11},
                    {"id": 4, "name": "", "x": 8, "y": 9},
                    {"id": 5, "name": "", "x": 10, "y": 16},
                    {"id": 6, "name": "", "x": 8, "y": 15},
                    {"id": 7, "name": "", "x": 11, "y": 5},
                    {"id": 8, "name": "", "x": 9, "y": 5},
                    {"id": 9, "name": "", "x": 12, "y": 9},
                    {"id": 10, "name": "", "x": 13, "y": 11},
                ],
                "edges": [
                    {"n1": 0, "n2": 1, "length": 1},
                    {"n1": 0, "n2": 2, "length": 1},
                    {"n1": 0, "n2": 3, "length": 2},
                    {"n1": 0, "n2": 4, "length": 2},
                    {"n1": 0, "n2": 9, "length": 2},
                    {"n1": 0, "n2": 10, "length": 2},
                    {"n1": 1, "n2": 5, "length": 4},
                    {"n1": 1, "n2": 6, "length": 4},
                    {"n1": 2, "n2": 7, "length": 4},
                    {"n1": 2, "n2": 8, "length": 4},
                ],
            },
        },
    },
    packing_svg="",
    grid_size=15,
)

MINI_HUMAN = BoxPleatingCreasePatternExample(
    name="mini_human",
    tree_data={
        "version": "0.7",
        "design": {
            "title": "mini_human",
            "mode": "tree",
            "description": "",
            "layout": {
                "sheet": {"type": "rect", "height": 16, "width": 16},
                "flaps": [
                    {"id": 1, "x": 8, "y": 10, "width": 0, "height": 0},
                    {"id": 3, "x": 10, "y": 10, "width": 0, "height": 0},
                    {"id": 4, "x": 6, "y": 10, "width": 0, "height": 0},
                    {"id": 5, "x": 9, "y": 7, "width": 0, "height": 0},
                    {"id": 6, "x": 7, "y": 7, "width": 0, "height": 0},
                ],
                "stretches": [],
            },
            "tree": {
                "sheet": {"type": "rect", "height": 20, "width": 20},
                "nodes": [
                    {"id": 0, "name": "", "x": 10, "y": 12},
                    {"id": 1, "name": "", "x": 10, "y": 13},
                    {"id": 2, "name": "", "x": 10, "y": 11},
                    {"id": 3, "name": "", "x": 12, "y": 12},
                    {"id": 4, "name": "", "x": 8, "y": 12},
                    {"id": 5, "name": "", "x": 11, "y": 9},
                    {"id": 6, "name": "", "x": 9, "y": 9},
                ],
                "edges": [
                    {"n1": 0, "n2": 2, "length": 1},
                    {"n1": 0, "n2": 1, "length": 1},
                    {"n1": 0, "n2": 3, "length": 2},
                    {"n1": 0, "n2": 4, "length": 2},
                    {"n1": 2, "n2": 5, "length": 2},
                    {"n1": 2, "n2": 6, "length": 2},
                ],
            },
        },
    },
    packing_svg="",
    grid_size=0,
)

NINE_TAIL = BoxPleatingCreasePatternExample(
    name="nine_tail",
    tree_data={
        "version": "0.7",
        "design": {
            "title": "Untitled",
            "mode": "tree",
            "description": "",
            "layout": {
                "sheet": {"type": "rect", "height": 16, "width": 16},
                "flaps": [
                    {"id": 1, "x": 4, "y": 14, "width": 0, "height": 0},
                    {"id": 3, "x": 12, "y": 12, "width": 0, "height": 0},
                    {"id": 4, "x": 6, "y": 14, "width": 0, "height": 0},
                    {"id": 5, "x": 4, "y": 10, "width": 0, "height": 0},
                    {"id": 6, "x": 4, "y": 12, "width": 0, "height": 0},
                    {"id": 7, "x": 10, "y": 14, "width": 0, "height": 0},
                    {"id": 8, "x": 13, "y": 10, "width": 0, "height": 0},
                    {"id": 9, "x": 12, "y": 14, "width": 0, "height": 0},
                    {"id": 10, "x": 8, "y": 15, "width": 0, "height": 0},
                    {"id": 13, "x": 4, "y": 9, "width": 0, "height": 0},
                    {"id": 14, "x": 5, "y": 8, "width": 0, "height": 0},
                    {"id": 15, "x": 4, "y": 8, "width": 0, "height": 0},
                    {"id": 16, "x": 6, "y": 9, "width": 0, "height": 0},
                    {"id": 17, "x": 12, "y": 8, "width": 0, "height": 0},
                    {"id": 19, "x": 11, "y": 8, "width": 0, "height": 0},
                    {"id": 18, "x": 12, "y": 9, "width": 0, "height": 0},
                    {"id": 20, "x": 10, "y": 9, "width": 0, "height": 0},
                    {"id": 22, "x": 10, "y": 6, "width": 0, "height": 0},
                    {"id": 23, "x": 6, "y": 6, "width": 0, "height": 0},
                    {"id": 24, "x": 8, "y": 6, "width": 0, "height": 0},
                    {"id": 25, "x": 9, "y": 6, "width": 0, "height": 0},
                    {"id": 26, "x": 9, "y": 8, "width": 0, "height": 0},
                    {"id": 27, "x": 7, "y": 8, "width": 0, "height": 0},
                    {"id": 30, "x": 10, "y": 8, "width": 0, "height": 0},
                    {"id": 31, "x": 10, "y": 8, "width": 0, "height": 0},
                    {"id": 32, "x": 10, "y": 7, "width": 0, "height": 0},
                    {"id": 33, "x": 6, "y": 7, "width": 0, "height": 0},
                    {"id": 34, "x": 6, "y": 8, "width": 0, "height": 0},
                    {"id": 35, "x": 6, "y": 8, "width": 0, "height": 0},
                    {"id": 38, "x": 6, "y": 6, "width": 0, "height": 0},
                    {"id": 39, "x": 4, "y": 6, "width": 0, "height": 0},
                    {"id": 40, "x": 5, "y": 6, "width": 0, "height": 0},
                    {"id": 41, "x": 4, "y": 6, "width": 0, "height": 0},
                    {"id": 42, "x": 6, "y": 6, "width": 0, "height": 0},
                    {"id": 43, "x": 12, "y": 6, "width": 0, "height": 0},
                    {"id": 44, "x": 10, "y": 6, "width": 0, "height": 0},
                    {"id": 45, "x": 11, "y": 6, "width": 0, "height": 0},
                    {"id": 46, "x": 10, "y": 6, "width": 0, "height": 0},
                    {"id": 47, "x": 12, "y": 6, "width": 0, "height": 0},
                    {"id": 48, "x": 11, "y": 10, "width": 0, "height": 0},
                    {"id": 49, "x": 5, "y": 10, "width": 0, "height": 0},
                ],
                "stretches": [],
            },
            "tree": {
                "sheet": {"type": "rect", "height": 20, "width": 20},
                "nodes": [
                    {"id": 0, "name": "", "x": 10, "y": 13},
                    {"id": 1, "name": "", "x": 5, "y": 18},
                    {"id": 2, "name": "", "x": 6, "y": 11},
                    {"id": 3, "name": "", "x": 15, "y": 15},
                    {"id": 4, "name": "", "x": 8, "y": 18},
                    {"id": 5, "name": "", "x": 5, "y": 13},
                    {"id": 6, "name": "", "x": 5, "y": 15},
                    {"id": 7, "name": "", "x": 12, "y": 18},
                    {"id": 8, "name": "", "x": 16, "y": 13},
                    {"id": 9, "name": "", "x": 15, "y": 18},
                    {"id": 10, "name": "", "x": 10, "y": 19},
                    {"id": 11, "name": "", "x": 14, "y": 11},
                    {"id": 12, "name": "", "x": 10, "y": 10},
                    {"id": 13, "name": "", "x": 5, "y": 11},
                    {"id": 14, "name": "", "x": 6, "y": 10},
                    {"id": 15, "name": "", "x": 5, "y": 10},
                    {"id": 16, "name": "", "x": 7, "y": 11},
                    {"id": 17, "name": "", "x": 15, "y": 10},
                    {"id": 18, "name": "", "x": 15, "y": 11},
                    {"id": 19, "name": "", "x": 14, "y": 10},
                    {"id": 20, "name": "", "x": 13, "y": 11},
                    {"id": 21, "name": "", "x": 10, "y": 8},
                    {"id": 22, "name": "", "x": 12, "y": 7},
                    {"id": 23, "name": "", "x": 8, "y": 7},
                    {"id": 24, "name": "", "x": 10, "y": 7},
                    {"id": 25, "name": "", "x": 11, "y": 7},
                    {"id": 26, "name": "", "x": 11, "y": 10},
                    {"id": 27, "name": "", "x": 9, "y": 10},
                    {"id": 28, "name": "", "x": 12, "y": 9},
                    {"id": 29, "name": "", "x": 8, "y": 9},
                    {"id": 30, "name": "", "x": 13, "y": 10},
                    {"id": 31, "name": "", "x": 12, "y": 10},
                    {"id": 32, "name": "", "x": 13, "y": 9},
                    {"id": 33, "name": "", "x": 7, "y": 9},
                    {"id": 34, "name": "", "x": 8, "y": 10},
                    {"id": 35, "name": "", "x": 7, "y": 10},
                    {"id": 36, "name": "", "x": 14, "y": 8},
                    {"id": 37, "name": "", "x": 6, "y": 8},
                    {"id": 38, "name": "", "x": 7, "y": 8},
                    {"id": 39, "name": "", "x": 5, "y": 7},
                    {"id": 40, "name": "", "x": 6, "y": 7},
                    {"id": 41, "name": "", "x": 5, "y": 8},
                    {"id": 42, "name": "", "x": 7, "y": 7},
                    {"id": 43, "name": "", "x": 15, "y": 8},
                    {"id": 44, "name": "", "x": 13, "y": 7},
                    {"id": 45, "name": "", "x": 14, "y": 7},
                    {"id": 46, "name": "", "x": 13, "y": 8},
                    {"id": 47, "name": "", "x": 15, "y": 7},
                    {"id": 48, "name": "", "x": 14, "y": 12},
                    {"id": 49, "name": "", "x": 6, "y": 12},
                ],
                "edges": [
                    {"n1": 12, "n2": 29, "length": 3},
                    {"n1": 12, "n2": 28, "length": 3},
                    {"n1": 12, "n2": 0, "length": 4},
                    {"n1": 12, "n2": 26, "length": 2},
                    {"n1": 12, "n2": 21, "length": 2},
                    {"n1": 12, "n2": 27, "length": 2},
                    {"n1": 29, "n2": 37, "length": 3},
                    {"n1": 29, "n2": 33, "length": 1},
                    {"n1": 29, "n2": 35, "length": 1},
                    {"n1": 29, "n2": 34, "length": 1},
                    {"n1": 28, "n2": 36, "length": 3},
                    {"n1": 28, "n2": 30, "length": 1},
                    {"n1": 28, "n2": 32, "length": 1},
                    {"n1": 28, "n2": 31, "length": 1},
                    {"n1": 0, "n2": 2, "length": 6},
                    {"n1": 0, "n2": 6, "length": 10},
                    {"n1": 0, "n2": 11, "length": 6},
                    {"n1": 0, "n2": 4, "length": 10},
                    {"n1": 0, "n2": 1, "length": 12},
                    {"n1": 0, "n2": 3, "length": 10},
                    {"n1": 0, "n2": 7, "length": 10},
                    {"n1": 0, "n2": 8, "length": 10},
                    {"n1": 0, "n2": 9, "length": 12},
                    {"n1": 0, "n2": 10, "length": 10},
                    {"n1": 0, "n2": 5, "length": 10},
                    {"n1": 21, "n2": 22, "length": 4},
                    {"n1": 21, "n2": 23, "length": 4},
                    {"n1": 21, "n2": 24, "length": 2},
                    {"n1": 21, "n2": 25, "length": 2},
                    {"n1": 37, "n2": 38, "length": 2},
                    {"n1": 37, "n2": 39, "length": 2},
                    {"n1": 37, "n2": 40, "length": 2},
                    {"n1": 37, "n2": 41, "length": 2},
                    {"n1": 37, "n2": 42, "length": 2},
                    {"n1": 36, "n2": 43, "length": 2},
                    {"n1": 36, "n2": 44, "length": 2},
                    {"n1": 36, "n2": 45, "length": 2},
                    {"n1": 36, "n2": 46, "length": 2},
                    {"n1": 36, "n2": 47, "length": 2},
                    {"n1": 2, "n2": 13, "length": 2},
                    {"n1": 2, "n2": 14, "length": 2},
                    {"n1": 2, "n2": 15, "length": 2},
                    {"n1": 2, "n2": 16, "length": 1},
                    {"n1": 2, "n2": 49, "length": 1},
                    {"n1": 11, "n2": 18, "length": 2},
                    {"n1": 11, "n2": 17, "length": 2},
                    {"n1": 11, "n2": 19, "length": 2},
                    {"n1": 11, "n2": 20, "length": 1},
                    {"n1": 11, "n2": 48, "length": 1},
                ],
            },
        },
    },
    grid_size=64,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <line stroke="black" x1="0" y1="0" x2="0" y2="12"/>
  <line stroke="black" x1="0" y1="0" x2="12" y2="0"/>
  <line stroke="red" x1="0" y1="0" x2="12" y2="12"/>
  <line stroke="green" x1="0" y1="12" x2="12" y2="12"/>
  <line stroke="black" x1="0" y1="12" x2="0" y2="22"/>
  <line stroke="green" x1="12" y1="0" x2="12" y2="12"/>
  <line stroke="black" x1="12" y1="0" x2="22" y2="0"/>
  <line stroke="red" x1="12" y1="12" x2="2" y2="22"/>
  <line stroke="red" x1="12" y1="12" x2="22" y2="2"/>
  <line stroke="red" x1="12" y1="12" x2="22" y2="22"/>
  <line stroke="green" x1="12" y1="12" x2="12" y2="32"/>
  <line stroke="green" x1="12" y1="12" x2="32" y2="12"/>
  <line stroke="red" x1="0" y1="22" x2="2" y2="22"/>
  <line stroke="black" x1="0" y1="22" x2="0" y2="32"/>
  <line stroke="red" x1="22" y1="0" x2="22" y2="2"/>
  <line stroke="black" x1="22" y1="0" x2="32" y2="0"/>
  <line stroke="red" x1="2" y1="22" x2="12" y2="32"/>
  <line stroke="red" x1="22" y1="2" x2="32" y2="12"/>
  <line stroke="red" x1="22" y1="22" x2="12" y2="32"/>
  <line stroke="red" x1="22" y1="22" x2="32" y2="12"/>
  <line stroke="red" x1="22" y1="22" x2="32" y2="32"/>
  <line stroke="green" x1="0" y1="32" x2="12" y2="32"/>
  <line stroke="black" x1="0" y1="32" x2="0" y2="38"/>
  <line stroke="green" x1="32" y1="0" x2="32" y2="12"/>
  <line stroke="black" x1="32" y1="0" x2="42" y2="0"/>
  <line stroke="green" x1="12" y1="32" x2="22" y2="32"/>
  <line stroke="red" x1="32" y1="12" x2="42" y2="2"/>
  <line stroke="green" x1="32" y1="12" x2="32" y2="32"/>
  <line stroke="red" x1="32" y1="12" x2="42" y2="22"/>
  <line stroke="green" x1="32" y1="12" x2="52" y2="12"/>
  <line stroke="green" x1="0" y1="38" x2="2" y2="38"/>
  <line stroke="black" x1="0" y1="38" x2="0" y2="40"/>
  <line stroke="green" x1="2" y1="38" x2="6" y2="38"/>
  <line stroke="red" x1="2" y1="38" x2="0" y2="40"/>
  <line stroke="red" x1="2" y1="38" x2="4" y2="40"/>
  <line stroke="green" x1="2" y1="38" x2="2" y2="42"/>
  <line stroke="green" x1="6" y1="38" x2="10" y2="38"/>
  <line stroke="red" x1="6" y1="38" x2="4" y2="40"/>
  <line stroke="red" x1="6" y1="38" x2="8" y2="40"/>
  <line stroke="green" x1="6" y1="38" x2="6" y2="42"/>
  <line stroke="red" x1="22" y1="32" x2="16" y2="38"/>
  <line stroke="green" x1="22" y1="32" x2="32" y2="32"/>
  <line stroke="red" x1="22" y1="32" x2="32" y2="42"/>
  <line stroke="green" x1="22" y1="32" x2="22" y2="48"/>
  <line stroke="red" x1="10" y1="38" x2="11" y2="39"/>
  <line stroke="red" x1="10" y1="38" x2="8" y2="40"/>
  <line stroke="green" x1="10" y1="38" x2="16" y2="38"/>
  <line stroke="green" x1="10" y1="38" x2="10" y2="42"/>
  <line stroke="black" x1="0" y1="40" x2="0" y2="42"/>
  <line stroke="red" x1="0" y1="40" x2="2" y2="42"/>
  <line stroke="red" x1="4" y1="40" x2="2" y2="42"/>
  <line stroke="red" x1="4" y1="40" x2="6" y2="42"/>
  <line stroke="green" x1="11" y1="39" x2="13" y2="39"/>
  <line stroke="red" x1="11" y1="39" x2="12" y2="40"/>
  <line stroke="green" x1="11" y1="39" x2="11" y2="41"/>
  <line stroke="red" x1="8" y1="40" x2="6" y2="42"/>
  <line stroke="red" x1="8" y1="40" x2="10" y2="42"/>
  <line stroke="green" x1="13" y1="39" x2="15" y2="39"/>
  <line stroke="red" x1="13" y1="39" x2="12" y2="40"/>
  <line stroke="red" x1="13" y1="39" x2="14" y2="40"/>
  <line stroke="green" x1="13" y1="39" x2="13" y2="41"/>
  <line stroke="red" x1="16" y1="38" x2="15" y2="39"/>
  <line stroke="green" x1="16" y1="38" x2="16" y2="42"/>
  <line stroke="red" x1="15" y1="39" x2="14" y2="40"/>
  <line stroke="green" x1="15" y1="39" x2="15" y2="41"/>
  <line stroke="red" x1="12" y1="40" x2="11" y2="41"/>
  <line stroke="red" x1="12" y1="40" x2="13" y2="41"/>
  <line stroke="green" x1="0" y1="42" x2="2" y2="42"/>
  <line stroke="black" x1="0" y1="42" x2="0" y2="48"/>
  <line stroke="red" x1="42" y1="0" x2="42" y2="2"/>
  <line stroke="black" x1="42" y1="0" x2="52" y2="0"/>
  <line stroke="green" x1="2" y1="42" x2="6" y2="42"/>
  <line stroke="red" x1="42" y1="2" x2="52" y2="12"/>
  <line stroke="red" x1="14" y1="40" x2="13" y2="41"/>
  <line stroke="red" x1="14" y1="40" x2="15" y2="41"/>
  <line stroke="green" x1="6" y1="42" x2="10" y2="42"/>
  <line stroke="green" x1="11" y1="41" x2="13" y2="41"/>
  <line stroke="red" x1="11" y1="41" x2="10" y2="42"/>
  <line stroke="green" x1="13" y1="41" x2="15" y2="41"/>
  <line stroke="green" x1="10" y1="42" x2="16" y2="42"/>
  <line stroke="red" x1="15" y1="41" x2="16" y2="42"/>
  <line stroke="red" x1="16" y1="42" x2="22" y2="48"/>
  <line stroke="red" x1="32" y1="32" x2="42" y2="22"/>
  <line stroke="green" x1="32" y1="32" x2="42" y2="32"/>
  <line stroke="red" x1="42" y1="22" x2="52" y2="12"/>
  <line stroke="red" x1="42" y1="22" x2="52" y2="32"/>
  <line stroke="black" x1="0" y1="48" x2="0" y2="52"/>
  <line stroke="green" x1="0" y1="48" x2="22" y2="48"/>
  <line stroke="green" x1="0" y1="52" x2="12" y2="52"/>
  <line stroke="black" x1="0" y1="52" x2="0" y2="55"/>
  <line stroke="green" x1="52" y1="0" x2="52" y2="12"/>
  <line stroke="black" x1="52" y1="0" x2="64" y2="0"/>
  <line stroke="red" x1="32" y1="42" x2="42" y2="32"/>
  <line stroke="red" x1="32" y1="42" x2="22" y2="52"/>
  <line stroke="red" x1="32" y1="42" x2="42" y2="52"/>
  <line stroke="green" x1="42" y1="32" x2="52" y2="32"/>
  <line stroke="red" x1="42" y1="32" x2="48" y2="38"/>
  <line stroke="green" x1="42" y1="32" x2="42" y2="48"/>
  <line stroke="red" x1="22" y1="48" x2="18" y2="52"/>
  <line stroke="green" x1="22" y1="48" x2="22" y2="52"/>
  <line stroke="green" x1="12" y1="52" x2="18" y2="52"/>
  <line stroke="red" x1="12" y1="52" x2="9" y2="55"/>
  <line stroke="red" x1="12" y1="52" x2="14" y2="54"/>
  <line stroke="green" x1="12" y1="52" x2="12" y2="56"/>
  <line stroke="green" x1="52" y1="12" x2="52" y2="32"/>
  <line stroke="red" x1="52" y1="12" x2="64" y2="0"/>
  <line stroke="green" x1="52" y1="12" x2="64" y2="12"/>
  <line stroke="red" x1="52" y1="12" x2="62" y2="22"/>
  <line stroke="green" x1="0" y1="55" x2="9" y2="55"/>
  <line stroke="black" x1="0" y1="55" x2="0" y2="58"/>
  <line stroke="red" x1="18" y1="52" x2="16" y2="54"/>
  <line stroke="green" x1="18" y1="52" x2="18" y2="56"/>
  <line stroke="red" x1="9" y1="55" x2="6" y2="58"/>
  <line stroke="green" x1="9" y1="55" x2="9" y2="59"/>
  <line stroke="red" x1="14" y1="54" x2="16" y2="54"/>
  <line stroke="red" x1="14" y1="54" x2="12" y2="56"/>
  <line stroke="red" x1="16" y1="54" x2="18" y2="56"/>
  <line stroke="red" x1="22" y1="52" x2="18" y2="56"/>
  <line stroke="green" x1="22" y1="52" x2="42" y2="52"/>
  <line stroke="green" x1="12" y1="56" x2="18" y2="56"/>
  <line stroke="red" x1="12" y1="56" x2="9" y2="59"/>
  <line stroke="green" x1="0" y1="58" x2="2" y2="58"/>
  <line stroke="black" x1="0" y1="58" x2="0" y2="60"/>
  <line stroke="green" x1="2" y1="58" x2="6" y2="58"/>
  <line stroke="red" x1="2" y1="58" x2="0" y2="60"/>
  <line stroke="red" x1="2" y1="58" x2="4" y2="60"/>
  <line stroke="green" x1="2" y1="58" x2="2" y2="62"/>
  <line stroke="red" x1="6" y1="58" x2="4" y2="60"/>
  <line stroke="green" x1="6" y1="58" x2="6" y2="62"/>
  <line stroke="red" x1="18" y1="56" x2="15" y2="59"/>
  <line stroke="red" x1="18" y1="56" x2="20" y2="58"/>
  <line stroke="green" x1="18" y1="56" x2="18" y2="64"/>
  <line stroke="green" x1="18" y1="56" x2="46" y2="56"/>
  <line stroke="green" x1="9" y1="59" x2="13" y2="59"/>
  <line stroke="red" x1="9" y1="59" x2="6" y2="62"/>
  <line stroke="black" x1="0" y1="60" x2="0" y2="62"/>
  <line stroke="red" x1="0" y1="60" x2="2" y2="62"/>
  <line stroke="red" x1="4" y1="60" x2="2" y2="62"/>
  <line stroke="red" x1="4" y1="60" x2="6" y2="62"/>
  <line stroke="green" x1="13" y1="59" x2="15" y2="59"/>
  <line stroke="red" x1="13" y1="59" x2="14" y2="60"/>
  <line stroke="green" x1="13" y1="59" x2="13" y2="61"/>
  <line stroke="red" x1="13" y1="59" x2="10" y2="62"/>
  <line stroke="red" x1="15" y1="59" x2="14" y2="60"/>
  <line stroke="green" x1="15" y1="59" x2="15" y2="61"/>
  <line stroke="red" x1="52" y1="32" x2="62" y2="22"/>
  <line stroke="green" x1="52" y1="32" x2="64" y2="32"/>
  <line stroke="red" x1="48" y1="38" x2="49" y2="39"/>
  <line stroke="green" x1="48" y1="38" x2="48" y2="42"/>
  <line stroke="green" x1="48" y1="38" x2="54" y2="38"/>
  <line stroke="green" x1="20" y1="58" x2="28" y2="58"/>
  <line stroke="red" x1="20" y1="58" x2="24" y2="62"/>
  <line stroke="green" x1="20" y1="58" x2="20" y2="64"/>
  <line stroke="red" x1="14" y1="60" x2="13" y2="61"/>
  <line stroke="red" x1="14" y1="60" x2="15" y2="61"/>
  <line stroke="green" x1="0" y1="62" x2="2" y2="62"/>
  <line stroke="black" x1="0" y1="62" x2="0" y2="64"/>
  <line stroke="green" x1="2" y1="62" x2="6" y2="62"/>
  <line stroke="red" x1="2" y1="62" x2="0" y2="64"/>
  <line stroke="green" x1="2" y1="62" x2="2" y2="64"/>
  <line stroke="red" x1="2" y1="62" x2="4" y2="64"/>
  <line stroke="green" x1="6" y1="62" x2="10" y2="62"/>
  <line stroke="red" x1="6" y1="62" x2="4" y2="64"/>
  <line stroke="green" x1="6" y1="62" x2="6" y2="64"/>
  <line stroke="red" x1="6" y1="62" x2="8" y2="64"/>
  <line stroke="green" x1="13" y1="61" x2="15" y2="61"/>
  <line stroke="red" x1="13" y1="61" x2="14" y2="62"/>
  <line stroke="green" x1="13" y1="61" x2="13" y2="63"/>
  <line stroke="green" x1="49" y1="39" x2="49" y2="41"/>
  <line stroke="red" x1="49" y1="39" x2="50" y2="40"/>
  <line stroke="green" x1="49" y1="39" x2="51" y2="39"/>
  <line stroke="red" x1="15" y1="61" x2="14" y2="62"/>
  <line stroke="green" x1="15" y1="61" x2="15" y2="63"/>
  <line stroke="red" x1="10" y1="62" x2="8" y2="64"/>
  <line stroke="green" x1="10" y1="62" x2="10" y2="64"/>
  <line stroke="red" x1="14" y1="62" x2="13" y2="63"/>
  <line stroke="red" x1="14" y1="62" x2="15" y2="63"/>
  <line stroke="red" x1="42" y1="48" x2="48" y2="42"/>
  <line stroke="green" x1="42" y1="48" x2="42" y2="52"/>
  <line stroke="red" x1="42" y1="48" x2="46" y2="52"/>
  <line stroke="green" x1="42" y1="48" x2="64" y2="48"/>
  <line stroke="red" x1="48" y1="42" x2="49" y2="41"/>
  <line stroke="green" x1="48" y1="42" x2="54" y2="42"/>
  <line stroke="red" x1="49" y1="41" x2="50" y2="40"/>
  <line stroke="green" x1="49" y1="41" x2="51" y2="41"/>
  <line stroke="black" x1="0" y1="64" x2="2" y2="64"/>
  <line stroke="black" x1="64" y1="0" x2="64" y2="12"/>
  <line stroke="red" x1="50" y1="40" x2="51" y2="39"/>
  <line stroke="red" x1="50" y1="40" x2="51" y2="41"/>
  <line stroke="black" x1="2" y1="64" x2="4" y2="64"/>
  <line stroke="black" x1="4" y1="64" x2="6" y2="64"/>
  <line stroke="green" x1="51" y1="39" x2="51" y2="41"/>
  <line stroke="red" x1="51" y1="39" x2="52" y2="40"/>
  <line stroke="green" x1="51" y1="39" x2="53" y2="39"/>
  <line stroke="black" x1="6" y1="64" x2="8" y2="64"/>
  <line stroke="green" x1="13" y1="63" x2="15" y2="63"/>
  <line stroke="green" x1="13" y1="63" x2="13" y2="64"/>
  <line stroke="red" x1="13" y1="63" x2="14" y2="64"/>
  <line stroke="red" x1="28" y1="58" x2="24" y2="62"/>
  <line stroke="red" x1="28" y1="58" x2="30" y2="60"/>
  <line stroke="green" x1="28" y1="58" x2="28" y2="62"/>
  <line stroke="green" x1="28" y1="58" x2="36" y2="58"/>
  <line stroke="black" x1="8" y1="64" x2="10" y2="64"/>
  <line stroke="red" x1="15" y1="63" x2="14" y2="64"/>
  <line stroke="green" x1="15" y1="63" x2="15" y2="64"/>
  <line stroke="black" x1="10" y1="64" x2="13" y2="64"/>
  <line stroke="black" x1="64" y1="12" x2="64" y2="22"/>
  <line stroke="black" x1="13" y1="64" x2="14" y2="64"/>
  <line stroke="red" x1="51" y1="41" x2="52" y2="40"/>
  <line stroke="green" x1="51" y1="41" x2="53" y2="41"/>
  <line stroke="black" x1="14" y1="64" x2="15" y2="64"/>
  <line stroke="red" x1="52" y1="40" x2="53" y2="39"/>
  <line stroke="red" x1="52" y1="40" x2="53" y2="41"/>
  <line stroke="black" x1="15" y1="64" x2="18" y2="64"/>
  <line stroke="red" x1="53" y1="39" x2="54" y2="38"/>
  <line stroke="green" x1="53" y1="39" x2="53" y2="41"/>
  <line stroke="red" x1="62" y1="22" x2="64" y2="22"/>
  <line stroke="green" x1="54" y1="38" x2="54" y2="42"/>
  <line stroke="red" x1="54" y1="38" x2="56" y2="40"/>
  <line stroke="green" x1="54" y1="38" x2="58" y2="38"/>
  <line stroke="black" x1="18" y1="64" x2="20" y2="64"/>
  <line stroke="red" x1="24" y1="62" x2="24" y2="64"/>
  <line stroke="red" x1="42" y1="52" x2="46" y2="56"/>
  <line stroke="red" x1="53" y1="41" x2="54" y2="42"/>
  <line stroke="black" x1="20" y1="64" x2="24" y2="64"/>
  <line stroke="red" x1="30" y1="60" x2="28" y2="62"/>
  <line stroke="red" x1="30" y1="60" x2="34" y2="60"/>
  <line stroke="black" x1="64" y1="22" x2="64" y2="32"/>
  <line stroke="green" x1="28" y1="62" x2="28" y2="64"/>
  <line stroke="red" x1="28" y1="62" x2="30" y2="64"/>
  <line stroke="green" x1="28" y1="62" x2="36" y2="62"/>
  <line stroke="red" x1="36" y1="58" x2="34" y2="60"/>
  <line stroke="green" x1="36" y1="58" x2="36" y2="62"/>
  <line stroke="green" x1="36" y1="58" x2="44" y2="58"/>
  <line stroke="red" x1="36" y1="58" x2="40" y2="62"/>
  <line stroke="black" x1="24" y1="64" x2="28" y2="64"/>
  <line stroke="red" x1="54" y1="42" x2="56" y2="40"/>
  <line stroke="green" x1="54" y1="42" x2="58" y2="42"/>
  <line stroke="red" x1="56" y1="40" x2="58" y2="38"/>
  <line stroke="red" x1="56" y1="40" x2="58" y2="42"/>
  <line stroke="red" x1="34" y1="60" x2="36" y2="62"/>
  <line stroke="green" x1="58" y1="38" x2="58" y2="42"/>
  <line stroke="red" x1="58" y1="38" x2="60" y2="40"/>
  <line stroke="green" x1="58" y1="38" x2="62" y2="38"/>
  <line stroke="red" x1="46" y1="52" x2="48" y2="54"/>
  <line stroke="green" x1="46" y1="52" x2="46" y2="56"/>
  <line stroke="green" x1="46" y1="52" x2="52" y2="52"/>
  <line stroke="black" x1="28" y1="64" x2="30" y2="64"/>
  <line stroke="black" x1="30" y1="64" x2="34" y2="64"/>
  <line stroke="black" x1="64" y1="32" x2="64" y2="38"/>
  <line stroke="red" x1="58" y1="42" x2="60" y2="40"/>
  <line stroke="green" x1="58" y1="42" x2="62" y2="42"/>
  <line stroke="red" x1="36" y1="62" x2="34" y2="64"/>
  <line stroke="green" x1="36" y1="62" x2="36" y2="64"/>
  <line stroke="red" x1="60" y1="40" x2="62" y2="38"/>
  <line stroke="red" x1="60" y1="40" x2="62" y2="42"/>
  <line stroke="red" x1="48" y1="54" x2="46" y2="56"/>
  <line stroke="red" x1="48" y1="54" x2="50" y2="54"/>
  <line stroke="black" x1="34" y1="64" x2="36" y2="64"/>
  <line stroke="red" x1="46" y1="56" x2="44" y2="58"/>
  <line stroke="green" x1="46" y1="56" x2="52" y2="56"/>
  <line stroke="red" x1="46" y1="56" x2="49" y2="59"/>
  <line stroke="green" x1="46" y1="56" x2="46" y2="64"/>
  <line stroke="green" x1="62" y1="38" x2="64" y2="38"/>
  <line stroke="green" x1="62" y1="38" x2="62" y2="42"/>
  <line stroke="red" x1="62" y1="38" x2="64" y2="40"/>
  <line stroke="red" x1="44" y1="58" x2="40" y2="62"/>
  <line stroke="green" x1="44" y1="58" x2="44" y2="64"/>
  <line stroke="black" x1="36" y1="64" x2="40" y2="64"/>
  <line stroke="red" x1="52" y1="52" x2="50" y2="54"/>
  <line stroke="green" x1="52" y1="52" x2="52" y2="56"/>
  <line stroke="red" x1="52" y1="52" x2="55" y2="55"/>
  <line stroke="green" x1="52" y1="52" x2="64" y2="52"/>
  <line stroke="red" x1="50" y1="54" x2="52" y2="56"/>
  <line stroke="red" x1="40" y1="62" x2="40" y2="64"/>
  <line stroke="black" x1="64" y1="38" x2="64" y2="40"/>
  <line stroke="red" x1="62" y1="42" x2="64" y2="40"/>
  <line stroke="green" x1="62" y1="42" x2="64" y2="42"/>
  <line stroke="black" x1="40" y1="64" x2="44" y2="64"/>
  <line stroke="black" x1="64" y1="40" x2="64" y2="42"/>
  <line stroke="red" x1="52" y1="56" x2="55" y2="59"/>
  <line stroke="black" x1="64" y1="42" x2="64" y2="48"/>
  <line stroke="green" x1="49" y1="59" x2="51" y2="59"/>
  <line stroke="red" x1="49" y1="59" x2="50" y2="60"/>
  <line stroke="green" x1="49" y1="59" x2="49" y2="61"/>
  <line stroke="black" x1="44" y1="64" x2="46" y2="64"/>
  <line stroke="green" x1="55" y1="55" x2="55" y2="59"/>
  <line stroke="red" x1="55" y1="55" x2="58" y2="58"/>
  <line stroke="green" x1="55" y1="55" x2="64" y2="55"/>
  <line stroke="red" x1="51" y1="59" x2="50" y2="60"/>
  <line stroke="green" x1="51" y1="59" x2="51" y2="61"/>
  <line stroke="green" x1="51" y1="59" x2="55" y2="59"/>
  <line stroke="red" x1="51" y1="59" x2="54" y2="62"/>
  <line stroke="red" x1="50" y1="60" x2="49" y2="61"/>
  <line stroke="red" x1="50" y1="60" x2="51" y2="61"/>
  <line stroke="green" x1="49" y1="61" x2="51" y2="61"/>
  <line stroke="red" x1="49" y1="61" x2="50" y2="62"/>
  <line stroke="green" x1="49" y1="61" x2="49" y2="63"/>
  <line stroke="black" x1="46" y1="64" x2="49" y2="64"/>
  <line stroke="red" x1="51" y1="61" x2="50" y2="62"/>
  <line stroke="green" x1="51" y1="61" x2="51" y2="63"/>
  <line stroke="red" x1="50" y1="62" x2="49" y2="63"/>
  <line stroke="red" x1="50" y1="62" x2="51" y2="63"/>
  <line stroke="green" x1="49" y1="63" x2="49" y2="64"/>
  <line stroke="green" x1="49" y1="63" x2="51" y2="63"/>
  <line stroke="red" x1="49" y1="63" x2="50" y2="64"/>
  <line stroke="black" x1="64" y1="48" x2="64" y2="52"/>
  <line stroke="black" x1="49" y1="64" x2="50" y2="64"/>
  <line stroke="red" x1="55" y1="59" x2="58" y2="62"/>
  <line stroke="red" x1="51" y1="63" x2="50" y2="64"/>
  <line stroke="green" x1="51" y1="63" x2="51" y2="64"/>
  <line stroke="black" x1="50" y1="64" x2="51" y2="64"/>
  <line stroke="black" x1="51" y1="64" x2="54" y2="64"/>
  <line stroke="red" x1="58" y1="58" x2="60" y2="60"/>
  <line stroke="green" x1="58" y1="58" x2="58" y2="62"/>
  <line stroke="green" x1="58" y1="58" x2="62" y2="58"/>
  <line stroke="green" x1="54" y1="62" x2="54" y2="64"/>
  <line stroke="green" x1="54" y1="62" x2="58" y2="62"/>
  <line stroke="red" x1="54" y1="62" x2="56" y2="64"/>
  <line stroke="black" x1="64" y1="52" x2="64" y2="55"/>
  <line stroke="black" x1="54" y1="64" x2="56" y2="64"/>
  <line stroke="black" x1="64" y1="55" x2="64" y2="58"/>
  <line stroke="red" x1="60" y1="60" x2="58" y2="62"/>
  <line stroke="red" x1="60" y1="60" x2="62" y2="58"/>
  <line stroke="red" x1="60" y1="60" x2="62" y2="62"/>
  <line stroke="red" x1="58" y1="62" x2="56" y2="64"/>
  <line stroke="green" x1="58" y1="62" x2="58" y2="64"/>
  <line stroke="green" x1="58" y1="62" x2="62" y2="62"/>
  <line stroke="red" x1="58" y1="62" x2="60" y2="64"/>
  <line stroke="green" x1="62" y1="58" x2="64" y2="58"/>
  <line stroke="green" x1="62" y1="58" x2="62" y2="62"/>
  <line stroke="red" x1="62" y1="58" x2="64" y2="60"/>
  <line stroke="black" x1="56" y1="64" x2="58" y2="64"/>
  <line stroke="black" x1="58" y1="64" x2="60" y2="64"/>
  <line stroke="black" x1="64" y1="58" x2="64" y2="60"/>
  <line stroke="red" x1="62" y1="62" x2="60" y2="64"/>
  <line stroke="red" x1="62" y1="62" x2="64" y2="60"/>
  <line stroke="green" x1="62" y1="62" x2="62" y2="64"/>
  <line stroke="green" x1="62" y1="62" x2="64" y2="62"/>
  <line stroke="red" x1="62" y1="62" x2="64" y2="64"/>
  <line stroke="black" x1="60" y1="64" x2="62" y2="64"/>
  <line stroke="black" x1="64" y1="60" x2="64" y2="62"/>
  <line stroke="black" x1="62" y1="64" x2="64" y2="64"/>
  <line stroke="black" x1="64" y1="62" x2="64" y2="64"/>
</svg>
""",
)

GENERATED1 = BoxPleatingCreasePatternExample(
    name="generated1",
    grid_size=8,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8">
  <line stroke="black" x1="0" y1="0" x2="0" y2="2"/>
  <line stroke="black" x1="0" y1="0" x2="2" y2="0"/>
  <line stroke="black" x1="0" y1="2" x2="0" y2="3"/>
  <line stroke="green" x1="0" y1="2" x2="4" y2="2"/>
  <line stroke="black" x1="2" y1="0" x2="4" y2="0"/>
  <line stroke="red" x1="2" y1="0" x2="4" y2="2"/>
  <line stroke="green" x1="0" y1="3" x2="2" y2="3"/>
  <line stroke="black" x1="0" y1="3" x2="0" y2="4"/>
  <line stroke="red" x1="2" y1="3" x2="1" y2="4"/>
  <line stroke="red" x1="2" y1="3" x2="4" y2="5"/>
  <line stroke="green" x1="2" y1="3" x2="6" y2="3"/>
  <line stroke="green" x1="2" y1="3" x2="2" y2="8"/>
  <line stroke="green" x1="0" y1="4" x2="1" y2="4"/>
  <line stroke="black" x1="0" y1="4" x2="0" y2="5"/>
  <line stroke="green" x1="4" y1="0" x2="4" y2="2"/>
  <line stroke="black" x1="4" y1="0" x2="6" y2="0"/>
  <line stroke="red" x1="1" y1="4" x2="0" y2="5"/>
  <line stroke="green" x1="1" y1="4" x2="1" y2="6"/>
  <line stroke="red" x1="4" y1="2" x2="6" y2="0"/>
  <line stroke="green" x1="4" y1="2" x2="8" y2="2"/>
  <line stroke="black" x1="0" y1="5" x2="0" y2="6"/>
  <line stroke="red" x1="0" y1="5" x2="1" y2="6"/>
  <line stroke="green" x1="0" y1="6" x2="1" y2="6"/>
  <line stroke="black" x1="0" y1="6" x2="0" y2="7"/>
  <line stroke="black" x1="6" y1="0" x2="8" y2="0"/>
  <line stroke="red" x1="6" y1="0" x2="8" y2="2"/>
  <line stroke="red" x1="1" y1="6" x2="0" y2="7"/>
  <line stroke="green" x1="1" y1="6" x2="1" y2="8"/>
  <line stroke="red" x1="4" y1="5" x2="6" y2="3"/>
  <line stroke="red" x1="4" y1="5" x2="4" y2="7"/>
  <line stroke="green" x1="6" y1="3" x2="8" y2="3"/>
  <line stroke="red" x1="6" y1="3" x2="8" y2="5"/>
  <line stroke="green" x1="6" y1="3" x2="6" y2="8"/>
  <line stroke="black" x1="0" y1="7" x2="0" y2="8"/>
  <line stroke="red" x1="0" y1="7" x2="1" y2="8"/>
  <line stroke="black" x1="0" y1="8" x2="1" y2="8"/>
  <line stroke="black" x1="8" y1="0" x2="8" y2="2"/>
  <line stroke="black" x1="1" y1="8" x2="2" y2="8"/>
  <line stroke="red" x1="4" y1="7" x2="3" y2="8"/>
  <line stroke="red" x1="4" y1="7" x2="5" y2="8"/>
  <line stroke="black" x1="2" y1="8" x2="3" y2="8"/>
  <line stroke="black" x1="8" y1="2" x2="8" y2="3"/>
  <line stroke="black" x1="3" y1="8" x2="5" y2="8"/>
  <line stroke="black" x1="8" y1="3" x2="8" y2="5"/>
  <line stroke="black" x1="5" y1="8" x2="6" y2="8"/>
  <line stroke="black" x1="8" y1="5" x2="8" y2="7"/>
  <line stroke="black" x1="6" y1="8" x2="7" y2="8"/>
  <line stroke="red" x1="7" y1="8" x2="8" y2="7"/>
  <line stroke="black" x1="7" y1="8" x2="8" y2="8"/>
  <line stroke="black" x1="8" y1="7" x2="8" y2="8"/>
</svg>""",
)

GENERATED2 = BoxPleatingCreasePatternExample(
    name="generated2",
    packing_svg="""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
        <line stroke="black" x1="0.0" y1="0.0" x2="1000.0" y2="0.0"/>
        <line stroke="black" x1="1000.0" y1="0.0" x2="1000.0" y2="1000.0"/>
        <line stroke="black" x1="1000.0" y1="1000.0" x2="0.0" y2="1000.0"/>
        <line stroke="black" x1="0.0" y1="1000.0" x2="0.0" y2="0.0"/>
        <line stroke="green" x1="700.0" y1="200.0" x2="800.0" y2="200.0"/>
        <line stroke="green" x1="600.0" y1="300.0" x2="700.0" y2="300.0"/>
        <line stroke="green" x1="200.0" y1="200.0" x2="300.0" y2="200.0"/>
        <line stroke="green" x1="500.0" y1="300.0" x2="600.0" y2="300.0"/>
        <line stroke="green" x1="300.0" y1="200.0" x2="400.0" y2="200.0"/>
        <line stroke="green" x1="100.0" y1="300.0" x2="200.0" y2="300.0"/>
        <line stroke="green" x1="400.0" y1="200.0" x2="500.0" y2="200.0"/>
        <line stroke="green" x1="800.0" y1="200.0" x2="900.0" y2="200.0"/>
        <line stroke="green" x1="1000.0" y1="200.0" x2="1000.0" y2="300.0"/>
        <line stroke="green" x1="0.0" y1="200.0" x2="0.0" y2="300.0"/>
        <line stroke="green" x1="100.0" y1="200.0" x2="200.0" y2="200.0"/>
        <line stroke="green" x1="0.0" y1="300.0" x2="100.0" y2="300.0"/>
        <line stroke="green" x1="600.0" y1="200.0" x2="700.0" y2="200.0"/>
        <line stroke="green" x1="400.0" y1="300.0" x2="500.0" y2="300.0"/>
        <line stroke="green" x1="200.0" y1="300.0" x2="300.0" y2="300.0"/>
        <line stroke="green" x1="800.0" y1="300.0" x2="900.0" y2="300.0"/>
        <line stroke="green" x1="0.0" y1="200.0" x2="100.0" y2="200.0"/>
        <line stroke="green" x1="500.0" y1="200.0" x2="600.0" y2="200.0"/>
        <line stroke="green" x1="900.0" y1="200.0" x2="1000.0" y2="200.0"/>
        <line stroke="green" x1="700.0" y1="300.0" x2="800.0" y2="300.0"/>
        <line stroke="green" x1="900.0" y1="300.0" x2="1000.0" y2="300.0"/>
        <line stroke="green" x1="300.0" y1="300.0" x2="400.0" y2="300.0"/>
        <line stroke="green" x1="800.0" y1="700.0" x2="800.0" y2="800.0"/>
        <line stroke="green" x1="800.0" y1="600.0" x2="800.0" y2="700.0"/>
        <line stroke="green" x1="700.0" y1="400.0" x2="700.0" y2="500.0"/>
        <line stroke="green" x1="700.0" y1="700.0" x2="700.0" y2="800.0"/>
        <line stroke="green" x1="700.0" y1="900.0" x2="700.0" y2="1000.0"/>
        <line stroke="green" x1="700.0" y1="600.0" x2="700.0" y2="700.0"/>
        <line stroke="green" x1="500.0" y1="400.0" x2="600.0" y2="400.0"/>
        <line stroke="green" x1="600.0" y1="300.0" x2="700.0" y2="300.0"/>
        <line stroke="green" x1="500.0" y1="300.0" x2="600.0" y2="300.0"/>
        <line stroke="green" x1="600.0" y1="400.0" x2="700.0" y2="400.0"/>
        <line stroke="green" x1="800.0" y1="900.0" x2="800.0" y2="1000.0"/>
        <line stroke="green" x1="800.0" y1="300.0" x2="800.0" y2="400.0"/>
        <line stroke="green" x1="100.0" y1="300.0" x2="200.0" y2="300.0"/>
        <line stroke="green" x1="700.0" y1="500.0" x2="700.0" y2="600.0"/>
        <line stroke="green" x1="700.0" y1="800.0" x2="700.0" y2="900.0"/>
        <line stroke="green" x1="0.0" y1="300.0" x2="100.0" y2="300.0"/>
        <line stroke="green" x1="200.0" y1="400.0" x2="300.0" y2="400.0"/>
        <line stroke="green" x1="800.0" y1="400.0" x2="800.0" y2="500.0"/>
        <line stroke="green" x1="300.0" y1="400.0" x2="400.0" y2="400.0"/>
        <line stroke="green" x1="400.0" y1="300.0" x2="500.0" y2="300.0"/>
        <line stroke="green" x1="800.0" y1="500.0" x2="800.0" y2="600.0"/>
        <line stroke="green" x1="800.0" y1="800.0" x2="800.0" y2="900.0"/>
        <line stroke="green" x1="0.0" y1="400.0" x2="100.0" y2="400.0"/>
        <line stroke="green" x1="100.0" y1="400.0" x2="200.0" y2="400.0"/>
        <line stroke="green" x1="200.0" y1="300.0" x2="300.0" y2="300.0"/>
        <line stroke="green" x1="400.0" y1="400.0" x2="500.0" y2="400.0"/>
        <line stroke="green" x1="700.0" y1="1000.0" x2="800.0" y2="1000.0"/>
        <line stroke="green" x1="0.0" y1="300.0" x2="0.0" y2="400.0"/>
        <line stroke="green" x1="700.0" y1="300.0" x2="800.0" y2="300.0"/>
        <line stroke="green" x1="300.0" y1="300.0" x2="400.0" y2="300.0"/>
        <line stroke="green" x1="600.0" y1="0.0" x2="600.0" y2="200.0"/>
        <line stroke="green" x1="600.0" y1="200.0" x2="0.0" y2="200.0"/>
        <line stroke="green" x1="0.0" y1="200.0" x2="0.0" y2="0.0"/>
        <line stroke="green" x1="1000.0" y1="0.0" x2="1000.0" y2="200.0"/>
        <line stroke="green" x1="1000.0" y1="200.0" x2="600.0" y2="200.0"/>
        <line stroke="green" x1="600.0" y1="200.0" x2="600.0" y2="0.0"/>
        <line stroke="green" x1="800.0" y1="300.0" x2="1000.0" y2="300.0"/>
        <line stroke="green" x1="1000.0" y1="300.0" x2="1000.0" y2="900.0"/>
        <line stroke="green" x1="1000.0" y1="900.0" x2="800.0" y2="900.0"/>
        <line stroke="green" x1="800.0" y1="900.0" x2="800.0" y2="300.0"/>
        <line stroke="green" x1="800.0" y1="900.0" x2="1000.0" y2="900.0"/>
        <line stroke="green" x1="1000.0" y1="900.0" x2="1000.0" y2="1000.0"/>
        <line stroke="green" x1="800.0" y1="1000.0" x2="800.0" y2="900.0"/>
        <line stroke="green" x1="0.0" y1="400.0" x2="300.0" y2="400.0"/>
        <line stroke="green" x1="300.0" y1="400.0" x2="300.0" y2="1000.0"/>
        <line stroke="green" x1="300.0" y1="400.0" x2="700.0" y2="400.0"/>
        <line stroke="green" x1="700.0" y1="400.0" x2="700.0" y2="1000.0"/>
        <line stroke="green" x1="700.0" y1="1000.0" x2="300.0" y2="1000.0"/>
        <line stroke="green" x1="300.0" y1="1000.0" x2="300.0" y2="400.0"/>
        <line stroke="red" x1="700.0" y1="400.0" x2="800.0" y2="300.0"/>
        <line stroke="red" x1="200.0" y1="0.0" x2="200.0" y2="0.0"/>
        <line stroke="red" x1="400.0" y1="0.0" x2="400.0" y2="0.0"/>
        <line stroke="red" x1="0.0" y1="200.0" x2="200.0" y2="0.0"/>
        <line stroke="red" x1="600.0" y1="200.0" x2="400.0" y2="0.0"/>
        <line stroke="red" x1="200.0" y1="0.0" x2="400.0" y2="0.0"/>
        <line stroke="red" x1="800.0" y1="0.0" x2="1000.0" y2="200.0"/>
        <line stroke="red" x1="600.0" y1="200.0" x2="800.0" y2="0.0"/>
        <line stroke="red" x1="800.0" y1="300.0" x2="900.0" y2="400.0"/>
        <line stroke="red" x1="1000.0" y1="300.0" x2="900.0" y2="400.0"/>
        <line stroke="red" x1="800.0" y1="900.0" x2="900.0" y2="800.0"/>
        <line stroke="red" x1="1000.0" y1="900.0" x2="900.0" y2="800.0"/>
        <line stroke="red" x1="900.0" y1="400.0" x2="900.0" y2="800.0"/>
        <line stroke="red" x1="800.0" y1="900.0" x2="900.0" y2="1000.0"/>
        <line stroke="red" x1="900.0" y1="1000.0" x2="1000.0" y2="900.0"/>
        <line stroke="red" x1="0.0" y1="500.0" x2="100.0" y2="600.0"/>
        <line stroke="red" x1="300.0" y1="400.0" x2="100.0" y2="600.0"/>
        <line stroke="red" x1="100.0" y1="1000.0" x2="100.0" y2="1000.0"/>
        <line stroke="red" x1="100.0" y1="1000.0" x2="100.0" y2="1000.0"/>
        <line stroke="red" x1="100.0" y1="600.0" x2="100.0" y2="1000.0"/>
        <line stroke="red" x1="300.0" y1="400.0" x2="500.0" y2="600.0"/>
        <line stroke="red" x1="700.0" y1="400.0" x2="500.0" y2="600.0"/>
        <line stroke="red" x1="300.0" y1="1000.0" x2="500.0" y2="800.0"/>
        <line stroke="red" x1="700.0" y1="1000.0" x2="500.0" y2="800.0"/>
        <line stroke="red" x1="500.0" y1="600.0" x2="500.0" y2="800.0"/>
        </svg>""",
    grid_size=10,
)

GENERATED3 = BoxPleatingCreasePatternExample(
    name="generated3",
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 9 9">
  <line stroke="black" x1="0" y1="0" x2="0" y2="1"/>
  <line stroke="black" x1="0" y1="0" x2="1" y2="0"/>
  <line stroke="red" x1="0" y1="1" x2="1" y2="0"/>
  <line stroke="black" x1="0" y1="1" x2="0" y2="2"/>
  <line stroke="black" x1="1" y1="0" x2="3" y2="0"/>
  <line stroke="black" x1="0" y1="2" x2="0" y2="3"/>
  <line stroke="green" x1="0" y1="2" x2="5" y2="2"/>
  <line stroke="black" x1="0" y1="3" x2="0" y2="4"/>
  <line stroke="green" x1="0" y1="3" x2="7" y2="3"/>
  <line stroke="black" x1="3" y1="0" x2="5" y2="0"/>
  <line stroke="red" x1="3" y1="0" x2="5" y2="2"/>
  <line stroke="green" x1="0" y1="4" x2="2" y2="4"/>
  <line stroke="black" x1="0" y1="4" x2="0" y2="6"/>
  <line stroke="red" x1="2" y1="4" x2="0" y2="6"/>
  <line stroke="red" x1="2" y1="4" x2="4" y2="6"/>
  <line stroke="green" x1="2" y1="4" x2="6" y2="4"/>
  <line stroke="green" x1="2" y1="4" x2="2" y2="9"/>
  <line stroke="green" x1="5" y1="0" x2="5" y2="2"/>
  <line stroke="black" x1="5" y1="0" x2="7" y2="0"/>
  <line stroke="red" x1="5" y1="2" x2="7" y2="0"/>
  <line stroke="green" x1="5" y1="2" x2="9" y2="2"/>
  <line stroke="black" x1="0" y1="6" x2="0" y2="8"/>
  <line stroke="black" x1="7" y1="0" x2="9" y2="0"/>
  <line stroke="red" x1="7" y1="0" x2="9" y2="2"/>
  <line stroke="red" x1="4" y1="6" x2="6" y2="4"/>
  <line stroke="red" x1="4" y1="6" x2="4" y2="8"/>
  <line stroke="red" x1="6" y1="4" x2="7" y2="3"/>
  <line stroke="green" x1="6" y1="4" x2="6" y2="9"/>
  <line stroke="red" x1="7" y1="3" x2="8" y2="4"/>
  <line stroke="green" x1="7" y1="3" x2="9" y2="3"/>
  <line stroke="green" x1="7" y1="3" x2="7" y2="7"/>
  <line stroke="black" x1="0" y1="8" x2="0" y2="9"/>
  <line stroke="red" x1="0" y1="8" x2="1" y2="9"/>
  <line stroke="red" x1="4" y1="8" x2="3" y2="9"/>
  <line stroke="red" x1="4" y1="8" x2="5" y2="9"/>
  <line stroke="red" x1="8" y1="4" x2="9" y2="3"/>
  <line stroke="red" x1="8" y1="4" x2="8" y2="6"/>
  <line stroke="black" x1="0" y1="9" x2="1" y2="9"/>
  <line stroke="black" x1="9" y1="0" x2="9" y2="2"/>
  <line stroke="black" x1="1" y1="9" x2="2" y2="9"/>
  <line stroke="black" x1="2" y1="9" x2="3" y2="9"/>
  <line stroke="black" x1="9" y1="2" x2="9" y2="3"/>
  <line stroke="black" x1="3" y1="9" x2="5" y2="9"/>
  <line stroke="black" x1="9" y1="3" x2="9" y2="7"/>
  <line stroke="red" x1="7" y1="7" x2="8" y2="6"/>
  <line stroke="red" x1="7" y1="7" x2="8" y2="8"/>
  <line stroke="green" x1="7" y1="7" x2="7" y2="9"/>
  <line stroke="green" x1="7" y1="7" x2="9" y2="7"/>
  <line stroke="red" x1="8" y1="6" x2="9" y2="7"/>
  <line stroke="black" x1="5" y1="9" x2="6" y2="9"/>
  <line stroke="black" x1="6" y1="9" x2="7" y2="9"/>
  <line stroke="red" x1="8" y1="8" x2="7" y2="9"/>
  <line stroke="red" x1="8" y1="8" x2="9" y2="7"/>
  <line stroke="red" x1="8" y1="8" x2="9" y2="9"/>
  <line stroke="black" x1="7" y1="9" x2="9" y2="9"/>
  <line stroke="black" x1="9" y1="7" x2="9" y2="9"/>
</svg>""",
    grid_size=9,
)

GENERATED6 = BoxPleatingCreasePatternExample(
    name="generated6",
    packing_svg="""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
        <line stroke="black" x1="0.0" y1="0.0" x2="1000.0" y2="0.0"/>
        <line stroke="black" x1="1000.0" y1="0.0" x2="1000.0" y2="1000.0"/>
        <line stroke="black" x1="1000.0" y1="1000.0" x2="0.0" y2="1000.0"/>
        <line stroke="black" x1="0.0" y1="1000.0" x2="0.0" y2="0.0"/>
        <line stroke="green" x1="333.3333333333333" y1="0.0" x2="333.3333333333333" y2="333.3333333333333"/>
        <line stroke="green" x1="333.3333333333333" y1="333.3333333333333" x2="0.0" y2="333.3333333333333"/>
        <line stroke="green" x1="1000.0" y1="0.0" x2="1000.0" y2="333.3333333333333"/>
        <line stroke="green" x1="1000.0" y1="333.3333333333333" x2="333.3333333333333" y2="333.3333333333333"/>
        <line stroke="green" x1="333.3333333333333" y1="333.3333333333333" x2="333.3333333333333" y2="0.0"/>
        <line stroke="green" x1="0.0" y1="666.6666666666666" x2="333.3333333333333" y2="666.6666666666666"/>
        <line stroke="green" x1="333.3333333333333" y1="666.6666666666666" x2="333.3333333333333" y2="1000.0"/>
        <line stroke="green" x1="333.3333333333333" y1="666.6666666666666" x2="1000.0" y2="666.6666666666666"/>
        <line stroke="green" x1="1000.0" y1="666.6666666666666" x2="1000.0" y2="1000.0"/>
        <line stroke="green" x1="333.3333333333333" y1="1000.0" x2="333.3333333333333" y2="666.6666666666666"/>
        <line stroke="green" x1="0.0" y1="333.3333333333333" x2="166.66666666666666" y2="333.3333333333333"/>
        <line stroke="green" x1="166.66666666666666" y1="333.3333333333333" x2="166.66666666666666" y2="666.6666666666666"/>
        <line stroke="green" x1="166.66666666666666" y1="666.6666666666666" x2="0.0" y2="666.6666666666666"/>
        <line stroke="green" x1="166.66666666666666" y1="333.3333333333333" x2="500.0" y2="333.3333333333333"/>
        <line stroke="green" x1="500.0" y1="333.3333333333333" x2="500.0" y2="666.6666666666666"/>
        <line stroke="green" x1="500.0" y1="666.6666666666666" x2="166.66666666666666" y2="666.6666666666666"/>
        <line stroke="green" x1="166.66666666666666" y1="666.6666666666666" x2="166.66666666666666" y2="333.3333333333333"/>
        <line stroke="green" x1="500.0" y1="333.3333333333333" x2="833.3333333333333" y2="333.3333333333333"/>
        <line stroke="green" x1="833.3333333333333" y1="333.3333333333333" x2="833.3333333333333" y2="666.6666666666666"/>
        <line stroke="green" x1="833.3333333333333" y1="666.6666666666666" x2="500.0" y2="666.6666666666666"/>
        <line stroke="green" x1="500.0" y1="666.6666666666666" x2="500.0" y2="333.3333333333333"/>
        <line stroke="green" x1="833.3333333333333" y1="333.3333333333333" x2="1000.0" y2="333.3333333333333"/>
        <line stroke="green" x1="1000.0" y1="666.6666666666666" x2="833.3333333333333" y2="666.6666666666666"/>
        <line stroke="green" x1="833.3333333333333" y1="666.6666666666666" x2="833.3333333333333" y2="333.3333333333333"/>
        <line stroke="red" x1="0.0" y1="0.0" x2="333.3333333333333" y2="333.3333333333333"/>
        <line stroke="red" x1="0.0" y1="0.0" x2="0.0" y2="0.0"/>
        <line stroke="red" x1="666.6666666666666" y1="0.0" x2="1000.0" y2="333.3333333333333"/>
        <line stroke="red" x1="333.3333333333333" y1="333.3333333333333" x2="666.6666666666666" y2="0.0"/>
        <line stroke="red" x1="0.0" y1="1000.0" x2="0.0" y2="1000.0"/>
        <line stroke="red" x1="0.0" y1="1000.0" x2="333.3333333333333" y2="666.6666666666666"/>
        <line stroke="red" x1="333.3333333333333" y1="666.6666666666666" x2="666.6666666666666" y2="1000.0"/>
        <line stroke="red" x1="666.6666666666666" y1="1000.0" x2="1000.0" y2="666.6666666666666"/>
        <line stroke="red" x1="0.0" y1="500.0" x2="166.66666666666666" y2="666.6666666666666"/>
        <line stroke="red" x1="0.0" y1="500.0" x2="166.66666666666666" y2="333.3333333333333"/>
        <line stroke="red" x1="166.66666666666666" y1="333.3333333333333" x2="500.0" y2="666.6666666666666"/>
        <line stroke="red" x1="166.66666666666666" y1="666.6666666666666" x2="500.0" y2="333.3333333333333"/>
        <line stroke="red" x1="500.0" y1="333.3333333333333" x2="833.3333333333333" y2="666.6666666666666"/>
        <line stroke="red" x1="500.0" y1="666.6666666666666" x2="833.3333333333333" y2="333.3333333333333"/>
        <line stroke="red" x1="833.3333333333333" y1="333.3333333333333" x2="1000.0" y2="500.0"/>
        <line stroke="red" x1="833.3333333333333" y1="666.6666666666666" x2="1000.0" y2="500.0"/>
        </svg>""",
    grid_size=12,
)

WATERBOMB = BoxPleatingCreasePatternExample(
    name="waterbomb",
    packing_svg="""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8">
        <rect stroke="black" x="0" y="0" width="8" height="8"/>
        <line stroke="red" x1="0" y1="0" x2="8" y2="8"/>
        <line stroke="green" x1="0" y1="4" x2="8" y2="4"/>
        <line stroke="green" x1="4" y1="0" x2="4" y2="8"/>
        <line stroke="red" x1="0" y1="8" x2="8" y2="0"/>
        </svg>""",
    grid_size=2,
)

SPIDER = BoxPleatingCreasePatternExample(
    name="spider",
    tree_data={
        "version": "0.7",
        "design": {
            "title": "Spider",
            "mode": "tree",
            "description": "",
            "layout": {
                "sheet": {"type": "rect", "height": 32, "width": 32},
                "flaps": [
                    {"id": 8, "x": 0, "y": 16, "width": 0, "height": 0},
                    {"id": 1, "x": 0, "y": 32, "width": 0, "height": 0},
                    {"id": 5, "x": 14, "y": 32, "width": 4, "height": 0},
                    {"id": 4, "x": 14, "y": 0, "width": 4, "height": 0},
                    {"id": 6, "x": 0, "y": 0, "width": 0, "height": 0},
                    {"id": 7, "x": 32, "y": 0, "width": 0, "height": 0},
                    {"id": 9, "x": 32, "y": 32, "width": 0, "height": 0},
                    {"id": 10, "x": 32, "y": 16, "width": 0, "height": 0},
                    {"id": 0, "x": 14, "y": 12, "width": 4, "height": 0},
                    {"id": 2, "x": 12, "y": 22, "width": 0, "height": 0},
                    {"id": 11, "x": 20, "y": 22, "width": 0, "height": 0},
                ],
                "stretches": [],
            },
            "tree": {
                "sheet": {"type": "rect", "height": 20, "width": 20},
                "nodes": [
                    {"id": 0, "name": "", "x": 10, "y": 5},
                    {"id": 1, "name": "", "x": 6, "y": 12},
                    {"id": 2, "name": "", "x": 11, "y": 11},
                    {"id": 3, "name": "", "x": 10, "y": 9},
                    {"id": 4, "name": "", "x": 14, "y": 10},
                    {"id": 5, "name": "", "x": 7, "y": 10},
                    {"id": 6, "name": "", "x": 15, "y": 8},
                    {"id": 7, "name": "", "x": 5, "y": 8},
                    {"id": 8, "name": "", "x": 14, "y": 12},
                    {"id": 9, "name": "", "x": 6, "y": 6},
                    {"id": 10, "name": "", "x": 14, "y": 6},
                    {"id": 11, "name": "", "x": 9, "y": 11},
                ],
                "edges": [
                    {"n1": 3, "n2": 8, "length": 8},
                    {"n1": 3, "n2": 10, "length": 8},
                    {"n1": 3, "n2": 7, "length": 8},
                    {"n1": 3, "n2": 1, "length": 8},
                    {"n1": 3, "n2": 4, "length": 6},
                    {"n1": 3, "n2": 6, "length": 8},
                    {"n1": 3, "n2": 0, "length": 6},
                    {"n1": 3, "n2": 5, "length": 6},
                    {"n1": 3, "n2": 9, "length": 8},
                    {"n1": 3, "n2": 2, "length": 4},
                    {"n1": 3, "n2": 11, "length": 4},
                ],
            },
        },
    },
    grid_size=32,
    packing_svg="""
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
        <line stroke="black" x1="0" y1="0" x2="0" y2="250"/>
        <line stroke="black" x1="0" y1="0" x2="250" y2="0"/>
        <line stroke="red" x1="0" y1="0" x2="250" y2="250"/>
        <line stroke="green" x1="0" y1="250" x2="250" y2="250"/>
        <line stroke="black" x1="0" y1="250" x2="0" y2="500"/>
        <line stroke="green" x1="250" y1="0" x2="250" y2="188"/>
        <line stroke="black" x1="250" y1="0" x2="438" y2="0"/>
        <line stroke="green" x1="250" y1="188" x2="250" y2="250"/>
        <line stroke="red" x1="250" y1="188" x2="438" y2="0"/>
        <line stroke="red" x1="250" y1="188" x2="375" y2="312"/>
        <line stroke="green" x1="250" y1="188" x2="500" y2="188"/>
        <line stroke="red" x1="250" y1="250" x2="0" y2="500"/>
        <line stroke="green" x1="250" y1="250" x2="250" y2="438"/>
        <line stroke="black" x1="438" y1="0" x2="562" y2="0"/>
        <line stroke="red" x1="375" y1="312" x2="250" y2="438"/>
        <line stroke="red" x1="375" y1="312" x2="500" y2="188"/>
        <line stroke="red" x1="375" y1="312" x2="500" y2="438"/>
        <line stroke="black" x1="0" y1="500" x2="0" y2="750"/>
        <line stroke="red" x1="0" y1="500" x2="250" y2="750"/>
        <line stroke="green" x1="250" y1="438" x2="500" y2="438"/>
        <line stroke="red" x1="250" y1="438" x2="438" y2="625"/>
        <line stroke="green" x1="250" y1="438" x2="250" y2="750"/>
        <line stroke="green" x1="500" y1="188" x2="500" y2="438"/>
        <line stroke="red" x1="500" y1="188" x2="625" y2="312"/>
        <line stroke="green" x1="500" y1="188" x2="750" y2="188"/>
        <line stroke="black" x1="562" y1="0" x2="750" y2="0"/>
        <line stroke="red" x1="562" y1="0" x2="750" y2="188"/>
        <line stroke="red" x1="500" y1="438" x2="625" y2="312"/>
        <line stroke="green" x1="500" y1="438" x2="750" y2="438"/>
        <line stroke="red" x1="625" y1="312" x2="750" y2="188"/>
        <line stroke="red" x1="625" y1="312" x2="750" y2="438"/>
        <line stroke="green" x1="0" y1="750" x2="250" y2="750"/>
        <line stroke="black" x1="0" y1="750" x2="0" y2="1000"/>
        <line stroke="green" x1="750" y1="0" x2="750" y2="188"/>
        <line stroke="black" x1="750" y1="0" x2="1000" y2="0"/>
        <line stroke="red" x1="438" y1="625" x2="562" y2="625"/>
        <line stroke="red" x1="438" y1="625" x2="250" y2="812"/>
        <line stroke="green" x1="750" y1="188" x2="750" y2="250"/>
        <line stroke="green" x1="250" y1="750" x2="250" y2="812"/>
        <line stroke="red" x1="250" y1="750" x2="0" y2="1000"/>
        <line stroke="green" x1="750" y1="250" x2="750" y2="438"/>
        <line stroke="red" x1="750" y1="250" x2="1000" y2="0"/>
        <line stroke="green" x1="750" y1="250" x2="1000" y2="250"/>
        <line stroke="red" x1="750" y1="250" x2="1000" y2="500"/>
        <line stroke="red" x1="562" y1="625" x2="750" y2="438"/>
        <line stroke="red" x1="562" y1="625" x2="750" y2="812"/>
        <line stroke="green" x1="250" y1="812" x2="250" y2="1000"/>
        <line stroke="red" x1="250" y1="812" x2="438" y2="1000"/>
        <line stroke="green" x1="250" y1="812" x2="750" y2="812"/>
        <line stroke="green" x1="750" y1="438" x2="750" y2="750"/>
        <line stroke="black" x1="0" y1="1000" x2="250" y2="1000"/>
        <line stroke="black" x1="1000" y1="0" x2="1000" y2="250"/>
        <line stroke="black" x1="250" y1="1000" x2="438" y2="1000"/>
        <line stroke="black" x1="1000" y1="250" x2="1000" y2="500"/>
        <line stroke="green" x1="750" y1="750" x2="750" y2="812"/>
        <line stroke="red" x1="750" y1="750" x2="1000" y2="500"/>
        <line stroke="green" x1="750" y1="750" x2="1000" y2="750"/>
        <line stroke="red" x1="750" y1="750" x2="1000" y2="1000"/>
        <line stroke="black" x1="438" y1="1000" x2="562" y2="1000"/>
        <line stroke="red" x1="750" y1="812" x2="562" y2="1000"/>
        <line stroke="green" x1="750" y1="812" x2="750" y2="1000"/>
        <line stroke="black" x1="1000" y1="500" x2="1000" y2="750"/>
        <line stroke="black" x1="562" y1="1000" x2="750" y2="1000"/>
        <line stroke="black" x1="750" y1="1000" x2="1000" y2="1000"/>
        <line stroke="black" x1="1000" y1="750" x2="1000" y2="1000"/>
      </svg>""",
    assigned_pleats_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <line stroke="black" x1="0" y1="0" x2="14" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="16"/>
  <line stroke="red" x1="1" y1="1" x2="13" y2="1"/>
  <line stroke="red" x1="1" y1="1" x2="1" y2="15"/>
  <line stroke="blue" x1="2" y1="2" x2="12" y2="2"/>
  <line stroke="blue" x1="2" y1="2" x2="2" y2="14"/>
  <line stroke="red" x1="3" y1="3" x2="11" y2="3"/>
  <line stroke="red" x1="3" y1="3" x2="3" y2="13"/>
  <line stroke="blue" x1="4" y1="4" x2="10" y2="4"/>
  <line stroke="blue" x1="4" y1="4" x2="4" y2="12"/>
  <line stroke="red" x1="5" y1="5" x2="9" y2="5"/>
  <line stroke="red" x1="5" y1="5" x2="5" y2="11"/>
  <line stroke="blue" x1="6" y1="6" x2="8" y2="6"/>
  <line stroke="blue" x1="6" y1="6" x2="6" y2="10"/>
  <line stroke="red" x1="7" y1="7" x2="7" y2="9"/>
  <line stroke="red" x1="7" y1="7" x2="9" y2="7"/>
  <line stroke="red" x1="9" y1="5" x2="9" y2="7"/>
  <line stroke="blue" x1="10" y1="4" x2="10" y2="8"/>
  <line stroke="blue" x1="8" y1="8" x2="10" y2="8"/>
  <line stroke="red" x1="7" y1="9" x2="11" y2="9"/>
  <line stroke="red" x1="11" y1="3" x2="11" y2="9"/>
  <line stroke="blue" x1="6" y1="10" x2="12" y2="10"/>
  <line stroke="red" x1="5" y1="11" x2="11" y2="11"/>
  <line stroke="blue" x1="12" y1="2" x2="12" y2="10"/>
  <line stroke="blue" x1="4" y1="12" x2="10" y2="12"/>
  <line stroke="red" x1="13" y1="1" x2="13" y2="9"/>
  <line stroke="red" x1="3" y1="13" x2="9" y2="13"/>
  <line stroke="black" x1="14" y1="0" x2="15" y2="0"/>
  <line stroke="blue" x1="14" y1="0" x2="14" y2="8"/>
  <line stroke="blue" x1="2" y1="14" x2="8" y2="14"/>
  <line stroke="black" x1="15" y1="0" x2="16" y2="0"/>
  <line stroke="red" x1="15" y1="0" x2="15" y2="7"/>
  <line stroke="red" x1="1" y1="15" x2="9" y2="15"/>
  <line stroke="red" x1="11" y1="11" x2="11" y2="17"/>
  <line stroke="blue" x1="10" y1="12" x2="10" y2="16"/>
  <line stroke="blue" x1="12" y1="10" x2="12" y2="18"/>
  <line stroke="blue" x1="12" y1="10" x2="20" y2="10"/>
  <line stroke="red" x1="9" y1="13" x2="9" y2="15"/>
  <line stroke="red" x1="13" y1="9" x2="19" y2="9"/>
  <line stroke="blue" x1="0" y1="16" x2="10" y2="16"/>
  <line stroke="black" x1="0" y1="16" x2="0" y2="32"/>
  <line stroke="black" x1="16" y1="0" x2="17" y2="0"/>
  <line stroke="blue" x1="16" y1="0" x2="16" y2="6"/>
  <line stroke="blue" x1="14" y1="8" x2="18" y2="8"/>
  <line stroke="red" x1="15" y1="7" x2="17" y2="7"/>
  <line stroke="black" x1="17" y1="0" x2="18" y2="0"/>
  <line stroke="red" x1="17" y1="0" x2="17" y2="7"/>
  <line stroke="red" x1="1" y1="17" x2="11" y2="17"/>
  <line stroke="red" x1="1" y1="17" x2="1" y2="31"/>
  <line stroke="red" x1="13" y1="11" x2="19" y2="11"/>
  <line stroke="red" x1="13" y1="11" x2="13" y2="19"/>
  <line stroke="blue" x1="18" y1="0" x2="18" y2="8"/>
  <line stroke="black" x1="18" y1="0" x2="32" y2="0"/>
  <line stroke="blue" x1="2" y1="18" x2="12" y2="18"/>
  <line stroke="blue" x1="2" y1="18" x2="2" y2="30"/>
  <line stroke="blue" x1="14" y1="12" x2="18" y2="12"/>
  <line stroke="blue" x1="14" y1="12" x2="14" y2="20"/>
  <line stroke="red" x1="19" y1="1" x2="19" y2="9"/>
  <line stroke="red" x1="19" y1="1" x2="31" y2="1"/>
  <line stroke="red" x1="3" y1="19" x2="13" y2="19"/>
  <line stroke="red" x1="3" y1="19" x2="3" y2="29"/>
  <line stroke="red" x1="15" y1="13" x2="17" y2="13"/>
  <line stroke="red" x1="15" y1="13" x2="15" y2="32"/>
  <line stroke="blue" x1="20" y1="2" x2="20" y2="10"/>
  <line stroke="blue" x1="20" y1="2" x2="30" y2="2"/>
  <line stroke="blue" x1="4" y1="20" x2="14" y2="20"/>
  <line stroke="blue" x1="4" y1="20" x2="4" y2="28"/>
  <line stroke="red" x1="21" y1="3" x2="21" y2="9"/>
  <line stroke="red" x1="21" y1="3" x2="29" y2="3"/>
  <line stroke="blue" x1="16" y1="14" x2="16" y2="32"/>
  <line stroke="red" x1="17" y1="13" x2="17" y2="32"/>
  <line stroke="red" x1="5" y1="21" x2="13" y2="21"/>
  <line stroke="red" x1="5" y1="21" x2="5" y2="27"/>
  <line stroke="blue" x1="18" y1="12" x2="18" y2="20"/>
  <line stroke="red" x1="19" y1="11" x2="19" y2="19"/>
  <line stroke="blue" x1="20" y1="10" x2="20" y2="18"/>
  <line stroke="blue" x1="20" y1="10" x2="26" y2="10"/>
  <line stroke="blue" x1="22" y1="4" x2="22" y2="8"/>
  <line stroke="blue" x1="22" y1="4" x2="28" y2="4"/>
  <line stroke="blue" x1="6" y1="22" x2="12" y2="22"/>
  <line stroke="blue" x1="6" y1="22" x2="6" y2="26"/>
  <line stroke="red" x1="21" y1="9" x2="25" y2="9"/>
  <line stroke="blue" x1="22" y1="8" x2="24" y2="8"/>
  <line stroke="red" x1="23" y1="5" x2="23" y2="7"/>
  <line stroke="red" x1="23" y1="5" x2="27" y2="5"/>
  <line stroke="red" x1="21" y1="11" x2="21" y2="17"/>
  <line stroke="red" x1="21" y1="11" x2="27" y2="11"/>
  <line stroke="red" x1="7" y1="23" x2="11" y2="23"/>
  <line stroke="red" x1="7" y1="23" x2="7" y2="25"/>
  <line stroke="red" x1="23" y1="7" x2="25" y2="7"/>
  <line stroke="blue" x1="14" y1="20" x2="14" y2="32"/>
  <line stroke="red" x1="13" y1="21" x2="13" y2="31"/>
  <line stroke="blue" x1="24" y1="6" x2="26" y2="6"/>
  <line stroke="blue" x1="12" y1="22" x2="12" y2="30"/>
  <line stroke="blue" x1="22" y1="12" x2="22" y2="16"/>
  <line stroke="blue" x1="22" y1="12" x2="28" y2="12"/>
  <line stroke="blue" x1="8" y1="24" x2="10" y2="24"/>
  <line stroke="red" x1="11" y1="23" x2="11" y2="29"/>
  <line stroke="red" x1="7" y1="25" x2="9" y2="25"/>
  <line stroke="red" x1="25" y1="7" x2="25" y2="9"/>
  <line stroke="blue" x1="10" y1="24" x2="10" y2="28"/>
  <line stroke="red" x1="23" y1="13" x2="23" y2="15"/>
  <line stroke="red" x1="23" y1="13" x2="29" y2="13"/>
  <line stroke="red" x1="9" y1="25" x2="9" y2="27"/>
  <line stroke="blue" x1="6" y1="26" x2="8" y2="26"/>
  <line stroke="blue" x1="26" y1="6" x2="26" y2="10"/>
  <line stroke="red" x1="19" y1="19" x2="29" y2="19"/>
  <line stroke="blue" x1="18" y1="20" x2="28" y2="20"/>
  <line stroke="blue" x1="18" y1="20" x2="18" y2="32"/>
  <line stroke="blue" x1="20" y1="18" x2="30" y2="18"/>
  <line stroke="red" x1="21" y1="17" x2="31" y2="17"/>
  <line stroke="blue" x1="22" y1="16" x2="32" y2="16"/>
  <line stroke="red" x1="5" y1="27" x2="9" y2="27"/>
  <line stroke="red" x1="23" y1="15" x2="31" y2="15"/>
  <line stroke="red" x1="27" y1="5" x2="27" y2="11"/>
  <line stroke="blue" x1="24" y1="14" x2="30" y2="14"/>
  <line stroke="blue" x1="4" y1="28" x2="10" y2="28"/>
  <line stroke="blue" x1="28" y1="4" x2="28" y2="12"/>
  <line stroke="red" x1="19" y1="21" x2="27" y2="21"/>
  <line stroke="red" x1="19" y1="21" x2="19" y2="31"/>
  <line stroke="red" x1="3" y1="29" x2="11" y2="29"/>
  <line stroke="red" x1="29" y1="3" x2="29" y2="13"/>
  <line stroke="blue" x1="20" y1="22" x2="26" y2="22"/>
  <line stroke="blue" x1="20" y1="22" x2="20" y2="30"/>
  <line stroke="blue" x1="2" y1="30" x2="12" y2="30"/>
  <line stroke="blue" x1="30" y1="2" x2="30" y2="14"/>
  <line stroke="red" x1="1" y1="31" x2="13" y2="31"/>
  <line stroke="red" x1="31" y1="1" x2="31" y2="15"/>
  <line stroke="red" x1="21" y1="23" x2="25" y2="23"/>
  <line stroke="red" x1="21" y1="23" x2="21" y2="29"/>
  <line stroke="black" x1="0" y1="32" x2="14" y2="32"/>
  <line stroke="black" x1="32" y1="0" x2="32" y2="16"/>
  <line stroke="blue" x1="22" y1="24" x2="24" y2="24"/>
  <line stroke="blue" x1="22" y1="24" x2="22" y2="28"/>
  <line stroke="red" x1="23" y1="25" x2="25" y2="25"/>
  <line stroke="red" x1="23" y1="25" x2="23" y2="27"/>
  <line stroke="red" x1="25" y1="23" x2="25" y2="25"/>
  <line stroke="blue" x1="26" y1="22" x2="26" y2="26"/>
  <line stroke="red" x1="27" y1="21" x2="27" y2="27"/>
  <line stroke="blue" x1="28" y1="20" x2="28" y2="28"/>
  <line stroke="red" x1="29" y1="19" x2="29" y2="29"/>
  <line stroke="black" x1="14" y1="32" x2="15" y2="32"/>
  <line stroke="blue" x1="30" y1="18" x2="30" y2="30"/>
  <line stroke="black" x1="15" y1="32" x2="16" y2="32"/>
  <line stroke="red" x1="31" y1="17" x2="31" y2="31"/>
  <line stroke="blue" x1="24" y1="26" x2="26" y2="26"/>
  <line stroke="red" x1="23" y1="27" x2="27" y2="27"/>
  <line stroke="blue" x1="22" y1="28" x2="28" y2="28"/>
  <line stroke="black" x1="16" y1="32" x2="17" y2="32"/>
  <line stroke="black" x1="32" y1="16" x2="32" y2="32"/>
  <line stroke="red" x1="21" y1="29" x2="29" y2="29"/>
  <line stroke="blue" x1="20" y1="30" x2="30" y2="30"/>
  <line stroke="black" x1="17" y1="32" x2="18" y2="32"/>
  <line stroke="red" x1="19" y1="31" x2="31" y2="31"/>
  <line stroke="black" x1="18" y1="32" x2="32" y2="32"/>
</svg>""",
    assigned_ridges_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="red" x1="0" y1="0" x2="31" y2="31"/>
  <line stroke="black" x1="0" y1="0" x2="438" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="500"/>
  <line stroke="blue" x1="31" y1="31" x2="62" y2="62"/>
  <line stroke="red" x1="31" y1="31" x2="406" y2="31"/>
  <line stroke="red" x1="31" y1="31" x2="31" y2="469"/>
  <line stroke="red" x1="62" y1="62" x2="94" y2="94"/>
  <line stroke="blue" x1="62" y1="62" x2="375" y2="62"/>
  <line stroke="blue" x1="62" y1="62" x2="62" y2="438"/>
  <line stroke="blue" x1="94" y1="94" x2="125" y2="125"/>
  <line stroke="red" x1="94" y1="94" x2="344" y2="94"/>
  <line stroke="red" x1="94" y1="94" x2="94" y2="406"/>
  <line stroke="red" x1="125" y1="125" x2="156" y2="156"/>
  <line stroke="blue" x1="125" y1="125" x2="312" y2="125"/>
  <line stroke="blue" x1="125" y1="125" x2="125" y2="375"/>
  <line stroke="blue" x1="156" y1="156" x2="188" y2="188"/>
  <line stroke="red" x1="156" y1="156" x2="281" y2="156"/>
  <line stroke="red" x1="156" y1="156" x2="156" y2="344"/>
  <line stroke="red" x1="188" y1="188" x2="219" y2="219"/>
  <line stroke="blue" x1="188" y1="188" x2="250" y2="188"/>
  <line stroke="blue" x1="188" y1="188" x2="188" y2="312"/>
  <line stroke="blue" x1="219" y1="219" x2="250" y2="250"/>
  <line stroke="red" x1="219" y1="219" x2="219" y2="281"/>
  <line stroke="red" x1="219" y1="219" x2="281" y2="219"/>
  <line stroke="blue" x1="250" y1="188" x2="281" y2="156"/>
  <line stroke="blue" x1="250" y1="188" x2="281" y2="219"/>
  <line stroke="red" x1="281" y1="156" x2="312" y2="125"/>
  <line stroke="red" x1="281" y1="156" x2="281" y2="219"/>
  <line stroke="blue" x1="312" y1="125" x2="344" y2="94"/>
  <line stroke="blue" x1="312" y1="125" x2="312" y2="250"/>
  <line stroke="blue" x1="250" y1="250" x2="219" y2="281"/>
  <line stroke="blue" x1="250" y1="250" x2="312" y2="250"/>
  <line stroke="red" x1="219" y1="281" x2="188" y2="312"/>
  <line stroke="red" x1="219" y1="281" x2="344" y2="281"/>
  <line stroke="red" x1="281" y1="219" x2="312" y2="250"/>
  <line stroke="red" x1="344" y1="94" x2="375" y2="62"/>
  <line stroke="red" x1="344" y1="94" x2="344" y2="281"/>
  <line stroke="blue" x1="188" y1="312" x2="156" y2="344"/>
  <line stroke="blue" x1="188" y1="312" x2="375" y2="312"/>
  <line stroke="red" x1="156" y1="344" x2="125" y2="375"/>
  <line stroke="red" x1="156" y1="344" x2="344" y2="344"/>
  <line stroke="blue" x1="375" y1="62" x2="406" y2="31"/>
  <line stroke="blue" x1="375" y1="62" x2="375" y2="312"/>
  <line stroke="blue" x1="125" y1="375" x2="94" y2="406"/>
  <line stroke="blue" x1="125" y1="375" x2="312" y2="375"/>
  <line stroke="blue" x1="312" y1="250" x2="344" y2="281"/>
  <line stroke="red" x1="406" y1="31" x2="438" y2="0"/>
  <line stroke="red" x1="406" y1="31" x2="406" y2="281"/>
  <line stroke="red" x1="94" y1="406" x2="62" y2="438"/>
  <line stroke="red" x1="94" y1="406" x2="281" y2="406"/>
  <line stroke="black" x1="438" y1="0" x2="469" y2="0"/>
  <line stroke="blue" x1="438" y1="0" x2="438" y2="250"/>
  <line stroke="blue" x1="62" y1="438" x2="31" y2="469"/>
  <line stroke="blue" x1="62" y1="438" x2="250" y2="438"/>
  <line stroke="red" x1="344" y1="281" x2="375" y2="312"/>
  <line stroke="black" x1="469" y1="0" x2="500" y2="0"/>
  <line stroke="red" x1="469" y1="0" x2="469" y2="219"/>
  <line stroke="red" x1="31" y1="469" x2="0" y2="500"/>
  <line stroke="red" x1="31" y1="469" x2="281" y2="469"/>
  <line stroke="blue" x1="344" y1="344" x2="312" y2="375"/>
  <line stroke="red" x1="344" y1="344" x2="375" y2="312"/>
  <line stroke="red" x1="344" y1="344" x2="344" y2="531"/>
  <line stroke="red" x1="312" y1="375" x2="281" y2="406"/>
  <line stroke="blue" x1="312" y1="375" x2="312" y2="500"/>
  <line stroke="red" x1="375" y1="312" x2="406" y2="281"/>
  <line stroke="red" x1="375" y1="312" x2="406" y2="344"/>
  <line stroke="blue" x1="375" y1="312" x2="375" y2="562"/>
  <line stroke="blue" x1="375" y1="312" x2="625" y2="312"/>
  <line stroke="blue" x1="281" y1="406" x2="250" y2="438"/>
  <line stroke="red" x1="281" y1="406" x2="281" y2="469"/>
  <line stroke="blue" x1="406" y1="281" x2="438" y2="250"/>
  <line stroke="red" x1="406" y1="281" x2="594" y2="281"/>
  <line stroke="red" x1="0" y1="500" x2="31" y2="531"/>
  <line stroke="blue" x1="0" y1="500" x2="312" y2="500"/>
  <line stroke="black" x1="0" y1="500" x2="0" y2="1000"/>
  <line stroke="black" x1="500" y1="0" x2="531" y2="0"/>
  <line stroke="blue" x1="500" y1="0" x2="500" y2="188"/>
  <line stroke="blue" x1="250" y1="438" x2="281" y2="469"/>
  <line stroke="red" x1="438" y1="250" x2="469" y2="219"/>
  <line stroke="blue" x1="438" y1="250" x2="562" y2="250"/>
  <line stroke="blue" x1="469" y1="219" x2="500" y2="188"/>
  <line stroke="red" x1="469" y1="219" x2="531" y2="219"/>
  <line stroke="black" x1="531" y1="0" x2="562" y2="0"/>
  <line stroke="red" x1="531" y1="0" x2="531" y2="219"/>
  <line stroke="blue" x1="31" y1="531" x2="62" y2="562"/>
  <line stroke="red" x1="31" y1="531" x2="344" y2="531"/>
  <line stroke="red" x1="31" y1="531" x2="31" y2="969"/>
  <line stroke="blue" x1="406" y1="344" x2="438" y2="375"/>
  <line stroke="red" x1="406" y1="344" x2="594" y2="344"/>
  <line stroke="red" x1="406" y1="344" x2="406" y2="594"/>
  <line stroke="blue" x1="500" y1="188" x2="531" y2="219"/>
  <line stroke="red" x1="281" y1="469" x2="312" y2="500"/>
  <line stroke="red" x1="562" y1="0" x2="594" y2="31"/>
  <line stroke="blue" x1="562" y1="0" x2="562" y2="250"/>
  <line stroke="black" x1="562" y1="0" x2="1000" y2="0"/>
  <line stroke="red" x1="62" y1="562" x2="94" y2="594"/>
  <line stroke="blue" x1="62" y1="562" x2="375" y2="562"/>
  <line stroke="blue" x1="62" y1="562" x2="62" y2="938"/>
  <line stroke="red" x1="531" y1="219" x2="562" y2="250"/>
  <line stroke="red" x1="438" y1="375" x2="469" y2="406"/>
  <line stroke="blue" x1="438" y1="375" x2="562" y2="375"/>
  <line stroke="blue" x1="438" y1="375" x2="438" y2="625"/>
  <line stroke="blue" x1="312" y1="500" x2="344" y2="531"/>
  <line stroke="blue" x1="594" y1="31" x2="625" y2="62"/>
  <line stroke="red" x1="594" y1="31" x2="594" y2="281"/>
  <line stroke="red" x1="594" y1="31" x2="969" y2="31"/>
  <line stroke="blue" x1="94" y1="594" x2="125" y2="625"/>
  <line stroke="red" x1="94" y1="594" x2="406" y2="594"/>
  <line stroke="red" x1="94" y1="594" x2="94" y2="906"/>
  <line stroke="blue" x1="562" y1="250" x2="594" y2="281"/>
  <line stroke="blue" x1="469" y1="406" x2="500" y2="438"/>
  <line stroke="red" x1="469" y1="406" x2="531" y2="406"/>
  <line stroke="red" x1="469" y1="406" x2="469" y2="1000"/>
  <line stroke="red" x1="625" y1="62" x2="656" y2="94"/>
  <line stroke="blue" x1="625" y1="62" x2="625" y2="312"/>
  <line stroke="blue" x1="625" y1="62" x2="938" y2="62"/>
  <line stroke="red" x1="344" y1="531" x2="375" y2="562"/>
  <line stroke="red" x1="125" y1="625" x2="156" y2="656"/>
  <line stroke="blue" x1="125" y1="625" x2="438" y2="625"/>
  <line stroke="blue" x1="125" y1="625" x2="125" y2="875"/>
  <line stroke="red" x1="594" y1="281" x2="625" y2="312"/>
  <line stroke="blue" x1="656" y1="94" x2="688" y2="125"/>
  <line stroke="red" x1="656" y1="94" x2="656" y2="281"/>
  <line stroke="red" x1="656" y1="94" x2="906" y2="94"/>
  <line stroke="blue" x1="500" y1="438" x2="531" y2="406"/>
  <line stroke="blue" x1="500" y1="438" x2="500" y2="1000"/>
  <line stroke="red" x1="531" y1="406" x2="562" y2="375"/>
  <line stroke="red" x1="531" y1="406" x2="531" y2="1000"/>
  <line stroke="blue" x1="156" y1="656" x2="188" y2="688"/>
  <line stroke="red" x1="156" y1="656" x2="406" y2="656"/>
  <line stroke="red" x1="156" y1="656" x2="156" y2="844"/>
  <line stroke="blue" x1="375" y1="562" x2="406" y2="594"/>
  <line stroke="blue" x1="562" y1="375" x2="594" y2="344"/>
  <line stroke="blue" x1="562" y1="375" x2="562" y2="625"/>
  <line stroke="red" x1="594" y1="344" x2="625" y2="312"/>
  <line stroke="red" x1="594" y1="344" x2="594" y2="594"/>
  <line stroke="red" x1="625" y1="312" x2="656" y2="281"/>
  <line stroke="red" x1="625" y1="312" x2="656" y2="344"/>
  <line stroke="blue" x1="625" y1="312" x2="625" y2="562"/>
  <line stroke="blue" x1="625" y1="312" x2="812" y2="312"/>
  <line stroke="blue" x1="688" y1="125" x2="688" y2="250"/>
  <line stroke="red" x1="688" y1="125" x2="719" y2="156"/>
  <line stroke="blue" x1="688" y1="125" x2="875" y2="125"/>
  <line stroke="red" x1="188" y1="688" x2="219" y2="719"/>
  <line stroke="blue" x1="188" y1="688" x2="375" y2="688"/>
  <line stroke="blue" x1="188" y1="688" x2="188" y2="812"/>
  <line stroke="blue" x1="656" y1="281" x2="688" y2="250"/>
  <line stroke="red" x1="656" y1="281" x2="781" y2="281"/>
  <line stroke="red" x1="406" y1="594" x2="438" y2="625"/>
  <line stroke="red" x1="688" y1="250" x2="719" y2="219"/>
  <line stroke="blue" x1="688" y1="250" x2="750" y2="250"/>
  <line stroke="red" x1="719" y1="156" x2="719" y2="219"/>
  <line stroke="blue" x1="719" y1="156" x2="750" y2="188"/>
  <line stroke="red" x1="719" y1="156" x2="844" y2="156"/>
  <line stroke="blue" x1="656" y1="344" x2="688" y2="375"/>
  <line stroke="red" x1="656" y1="344" x2="656" y2="531"/>
  <line stroke="red" x1="656" y1="344" x2="844" y2="344"/>
  <line stroke="blue" x1="219" y1="719" x2="250" y2="750"/>
  <line stroke="red" x1="219" y1="719" x2="344" y2="719"/>
  <line stroke="red" x1="219" y1="719" x2="219" y2="781"/>
  <line stroke="blue" x1="719" y1="219" x2="750" y2="188"/>
  <line stroke="red" x1="719" y1="219" x2="781" y2="219"/>
  <line stroke="red" x1="438" y1="625" x2="406" y2="656"/>
  <line stroke="blue" x1="438" y1="625" x2="438" y2="1000"/>
  <line stroke="blue" x1="406" y1="656" x2="375" y2="688"/>
  <line stroke="red" x1="406" y1="656" x2="406" y2="969"/>
  <line stroke="blue" x1="750" y1="188" x2="812" y2="188"/>
  <line stroke="red" x1="375" y1="688" x2="344" y2="719"/>
  <line stroke="blue" x1="375" y1="688" x2="375" y2="938"/>
  <line stroke="red" x1="688" y1="375" x2="719" y2="406"/>
  <line stroke="blue" x1="688" y1="375" x2="688" y2="500"/>
  <line stroke="blue" x1="688" y1="375" x2="875" y2="375"/>
  <line stroke="blue" x1="250" y1="750" x2="219" y2="781"/>
  <line stroke="blue" x1="250" y1="750" x2="312" y2="750"/>
  <line stroke="blue" x1="750" y1="250" x2="781" y2="219"/>
  <line stroke="blue" x1="750" y1="250" x2="781" y2="281"/>
  <line stroke="blue" x1="344" y1="719" x2="312" y2="750"/>
  <line stroke="red" x1="344" y1="719" x2="344" y2="906"/>
  <line stroke="red" x1="219" y1="781" x2="281" y2="781"/>
  <line stroke="red" x1="219" y1="781" x2="188" y2="812"/>
  <line stroke="red" x1="781" y1="219" x2="781" y2="281"/>
  <line stroke="red" x1="781" y1="219" x2="812" y2="188"/>
  <line stroke="red" x1="312" y1="750" x2="281" y2="781"/>
  <line stroke="blue" x1="312" y1="750" x2="312" y2="875"/>
  <line stroke="red" x1="719" y1="406" x2="719" y2="469"/>
  <line stroke="blue" x1="719" y1="406" x2="750" y2="438"/>
  <line stroke="red" x1="719" y1="406" x2="906" y2="406"/>
  <line stroke="blue" x1="281" y1="781" x2="250" y2="812"/>
  <line stroke="red" x1="281" y1="781" x2="281" y2="844"/>
  <line stroke="red" x1="781" y1="281" x2="812" y2="312"/>
  <line stroke="blue" x1="188" y1="812" x2="250" y2="812"/>
  <line stroke="blue" x1="188" y1="812" x2="156" y2="844"/>
  <line stroke="blue" x1="812" y1="188" x2="844" y2="156"/>
  <line stroke="blue" x1="812" y1="188" x2="812" y2="312"/>
  <line stroke="red" x1="594" y1="594" x2="562" y2="625"/>
  <line stroke="blue" x1="594" y1="594" x2="625" y2="562"/>
  <line stroke="red" x1="594" y1="594" x2="906" y2="594"/>
  <line stroke="red" x1="562" y1="625" x2="594" y2="656"/>
  <line stroke="blue" x1="562" y1="625" x2="875" y2="625"/>
  <line stroke="blue" x1="562" y1="625" x2="562" y2="1000"/>
  <line stroke="red" x1="625" y1="562" x2="656" y2="531"/>
  <line stroke="blue" x1="625" y1="562" x2="938" y2="562"/>
  <line stroke="blue" x1="656" y1="531" x2="688" y2="500"/>
  <line stroke="red" x1="656" y1="531" x2="969" y2="531"/>
  <line stroke="blue" x1="250" y1="812" x2="281" y2="844"/>
  <line stroke="red" x1="688" y1="500" x2="719" y2="469"/>
  <line stroke="blue" x1="688" y1="500" x2="1000" y2="500"/>
  <line stroke="red" x1="156" y1="844" x2="125" y2="875"/>
  <line stroke="red" x1="156" y1="844" x2="281" y2="844"/>
  <line stroke="blue" x1="719" y1="469" x2="750" y2="438"/>
  <line stroke="red" x1="719" y1="469" x2="969" y2="469"/>
  <line stroke="red" x1="844" y1="156" x2="875" y2="125"/>
  <line stroke="red" x1="844" y1="156" x2="844" y2="344"/>
  <line stroke="blue" x1="750" y1="438" x2="938" y2="438"/>
  <line stroke="blue" x1="812" y1="312" x2="844" y2="344"/>
  <line stroke="blue" x1="125" y1="875" x2="94" y2="906"/>
  <line stroke="blue" x1="125" y1="875" x2="312" y2="875"/>
  <line stroke="blue" x1="875" y1="125" x2="906" y2="94"/>
  <line stroke="blue" x1="875" y1="125" x2="875" y2="375"/>
  <line stroke="blue" x1="594" y1="656" x2="625" y2="688"/>
  <line stroke="red" x1="594" y1="656" x2="844" y2="656"/>
  <line stroke="red" x1="594" y1="656" x2="594" y2="969"/>
  <line stroke="red" x1="281" y1="844" x2="312" y2="875"/>
  <line stroke="red" x1="94" y1="906" x2="62" y2="938"/>
  <line stroke="red" x1="94" y1="906" x2="344" y2="906"/>
  <line stroke="red" x1="844" y1="344" x2="875" y2="375"/>
  <line stroke="red" x1="906" y1="94" x2="938" y2="62"/>
  <line stroke="red" x1="906" y1="94" x2="906" y2="406"/>
  <line stroke="blue" x1="312" y1="875" x2="344" y2="906"/>
  <line stroke="red" x1="625" y1="688" x2="656" y2="719"/>
  <line stroke="blue" x1="625" y1="688" x2="812" y2="688"/>
  <line stroke="blue" x1="625" y1="688" x2="625" y2="938"/>
  <line stroke="blue" x1="62" y1="938" x2="31" y2="969"/>
  <line stroke="blue" x1="62" y1="938" x2="375" y2="938"/>
  <line stroke="blue" x1="938" y1="62" x2="969" y2="31"/>
  <line stroke="blue" x1="938" y1="62" x2="938" y2="438"/>
  <line stroke="blue" x1="875" y1="375" x2="906" y2="406"/>
  <line stroke="red" x1="31" y1="969" x2="0" y2="1000"/>
  <line stroke="red" x1="31" y1="969" x2="406" y2="969"/>
  <line stroke="red" x1="344" y1="906" x2="375" y2="938"/>
  <line stroke="red" x1="969" y1="31" x2="1000" y2="0"/>
  <line stroke="red" x1="969" y1="31" x2="969" y2="469"/>
  <line stroke="blue" x1="656" y1="719" x2="688" y2="750"/>
  <line stroke="red" x1="656" y1="719" x2="781" y2="719"/>
  <line stroke="red" x1="656" y1="719" x2="656" y2="906"/>
  <line stroke="red" x1="906" y1="406" x2="938" y2="438"/>
  <line stroke="black" x1="0" y1="1000" x2="438" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="500"/>
  <line stroke="blue" x1="375" y1="938" x2="406" y2="969"/>
  <line stroke="blue" x1="688" y1="750" x2="750" y2="750"/>
  <line stroke="red" x1="688" y1="750" x2="719" y2="781"/>
  <line stroke="blue" x1="688" y1="750" x2="688" y2="875"/>
  <line stroke="blue" x1="938" y1="438" x2="969" y2="469"/>
  <line stroke="red" x1="406" y1="969" x2="438" y2="1000"/>
  <line stroke="blue" x1="750" y1="750" x2="781" y2="719"/>
  <line stroke="blue" x1="750" y1="750" x2="781" y2="781"/>
  <line stroke="red" x1="719" y1="781" x2="781" y2="781"/>
  <line stroke="blue" x1="719" y1="781" x2="750" y2="812"/>
  <line stroke="red" x1="719" y1="781" x2="719" y2="844"/>
  <line stroke="red" x1="781" y1="719" x2="812" y2="688"/>
  <line stroke="red" x1="781" y1="719" x2="781" y2="781"/>
  <line stroke="blue" x1="812" y1="688" x2="844" y2="656"/>
  <line stroke="blue" x1="812" y1="688" x2="812" y2="812"/>
  <line stroke="red" x1="844" y1="656" x2="875" y2="625"/>
  <line stroke="red" x1="844" y1="656" x2="844" y2="844"/>
  <line stroke="blue" x1="875" y1="625" x2="906" y2="594"/>
  <line stroke="blue" x1="875" y1="625" x2="875" y2="875"/>
  <line stroke="red" x1="969" y1="469" x2="1000" y2="500"/>
  <line stroke="red" x1="906" y1="594" x2="938" y2="562"/>
  <line stroke="red" x1="906" y1="594" x2="906" y2="906"/>
  <line stroke="black" x1="438" y1="1000" x2="469" y2="1000"/>
  <line stroke="blue" x1="938" y1="562" x2="969" y2="531"/>
  <line stroke="blue" x1="938" y1="562" x2="938" y2="938"/>
  <line stroke="black" x1="469" y1="1000" x2="500" y2="1000"/>
  <line stroke="red" x1="781" y1="781" x2="812" y2="812"/>
  <line stroke="red" x1="969" y1="531" x2="1000" y2="500"/>
  <line stroke="red" x1="969" y1="531" x2="969" y2="969"/>
  <line stroke="blue" x1="750" y1="812" x2="719" y2="844"/>
  <line stroke="blue" x1="750" y1="812" x2="812" y2="812"/>
  <line stroke="red" x1="719" y1="844" x2="688" y2="875"/>
  <line stroke="red" x1="719" y1="844" x2="844" y2="844"/>
  <line stroke="blue" x1="688" y1="875" x2="656" y2="906"/>
  <line stroke="blue" x1="688" y1="875" x2="875" y2="875"/>
  <line stroke="black" x1="500" y1="1000" x2="531" y2="1000"/>
  <line stroke="black" x1="1000" y1="500" x2="1000" y2="1000"/>
  <line stroke="red" x1="656" y1="906" x2="625" y2="938"/>
  <line stroke="red" x1="656" y1="906" x2="906" y2="906"/>
  <line stroke="blue" x1="625" y1="938" x2="594" y2="969"/>
  <line stroke="blue" x1="625" y1="938" x2="938" y2="938"/>
  <line stroke="black" x1="531" y1="1000" x2="562" y2="1000"/>
  <line stroke="red" x1="594" y1="969" x2="562" y2="1000"/>
  <line stroke="red" x1="594" y1="969" x2="969" y2="969"/>
  <line stroke="black" x1="562" y1="1000" x2="1000" y2="1000"/>
  <line stroke="blue" x1="812" y1="812" x2="844" y2="844"/>
  <line stroke="red" x1="844" y1="844" x2="875" y2="875"/>
  <line stroke="blue" x1="875" y1="875" x2="906" y2="906"/>
  <line stroke="red" x1="906" y1="906" x2="938" y2="938"/>
  <line stroke="blue" x1="938" y1="938" x2="969" y2="969"/>
  <line stroke="red" x1="969" y1="969" x2="1000" y2="1000"/>
</svg>""",
)

SCORPION = BoxPleatingCreasePatternExample(
    name="scorpion",
    tree_data={
        "version": "0.7",
        "design": {
            "title": "Scorpion",
            "mode": "layout",
            "description": "",
            "layout": {
                "sheet": {"type": "rect", "height": 32, "width": 32},
                "flaps": [
                    {"id": 1, "x": 32, "y": 32, "width": 0, "height": 0},
                    {"id": 2, "x": 24, "y": 32, "width": 0, "height": 0},
                    {"id": 5, "x": 8, "y": 32, "width": 0, "height": 0},
                    {"id": 6, "x": 0, "y": 32, "width": 0, "height": 0},
                    {"id": 7, "x": 0, "y": 12, "width": 0, "height": 0},
                    {"id": 8, "x": 0, "y": 20, "width": 0, "height": 0},
                    {"id": 9, "x": 0, "y": 4, "width": 0, "height": 0},
                    {"id": 10, "x": 32, "y": 20, "width": 0, "height": 0},
                    {"id": 11, "x": 32, "y": 12, "width": 0, "height": 0},
                    {"id": 12, "x": 32, "y": 4, "width": 0, "height": 0},
                    {"id": 13, "x": 24, "y": 20, "width": 0, "height": 0},
                    {"id": 14, "x": 8, "y": 20, "width": 0, "height": 0},
                    {"id": 15, "x": 16, "y": 0, "width": 0, "height": 0},
                    {"id": 16, "x": 6, "y": 14, "width": 20, "height": 0},
                    {"id": 18, "x": 13, "y": 17, "width": 6, "height": 0},
                    {"id": 17, "x": 13, "y": 19, "width": 6, "height": 0},
                    {"id": 19, "x": 13, "y": 23, "width": 6, "height": 0},
                    {"id": 20, "x": 13, "y": 21, "width": 6, "height": 0},
                ],
                "stretches": [],
            },
            "tree": {
                "sheet": {"type": "rect", "height": 20, "width": 20},
                "nodes": [
                    {"id": 0, "name": "", "x": 6, "y": 13},
                    {"id": 1, "name": "", "x": 4, "y": 15},
                    {"id": 2, "name": "", "x": 8, "y": 15},
                    {"id": 3, "name": "", "x": 10, "y": 11},
                    {"id": 4, "name": "", "x": 14, "y": 13},
                    {"id": 5, "name": "", "x": 16, "y": 15},
                    {"id": 6, "name": "", "x": 12, "y": 15},
                    {"id": 7, "name": "", "x": 14, "y": 8},
                    {"id": 8, "name": "", "x": 14, "y": 11},
                    {"id": 9, "name": "", "x": 6, "y": 6},
                    {"id": 10, "name": "", "x": 6, "y": 10},
                    {"id": 11, "name": "", "x": 14, "y": 10},
                    {"id": 12, "name": "", "x": 14, "y": 6},
                    {"id": 13, "name": "", "x": 6, "y": 11},
                    {"id": 14, "name": "", "x": 6, "y": 8},
                    {"id": 15, "name": "", "x": 10, "y": 2},
                    {"id": 16, "name": "", "x": 9, "y": 9},
                    {"id": 17, "name": "", "x": 11, "y": 9},
                    {"id": 18, "name": "", "x": 10, "y": 12},
                    {"id": 19, "name": "", "x": 11, "y": 11},
                    {"id": 20, "name": "", "x": 10, "y": 10},
                ],
                "edges": [
                    {"n1": 3, "n2": 4, "length": 4},
                    {"n1": 3, "n2": 0, "length": 4},
                    {"n1": 3, "n2": 10, "length": 4},
                    {"n1": 3, "n2": 12, "length": 4},
                    {"n1": 3, "n2": 15, "length": 12},
                    {"n1": 3, "n2": 7, "length": 4},
                    {"n1": 3, "n2": 11, "length": 4},
                    {"n1": 3, "n2": 8, "length": 4},
                    {"n1": 3, "n2": 13, "length": 4},
                    {"n1": 3, "n2": 14, "length": 4},
                    {"n1": 3, "n2": 9, "length": 4},
                    {"n1": 3, "n2": 16, "length": 2},
                    {"n1": 3, "n2": 17, "length": 1},
                    {"n1": 3, "n2": 18, "length": 1},
                    {"n1": 3, "n2": 19, "length": 1},
                    {"n1": 3, "n2": 20, "length": 1},
                    {"n1": 4, "n2": 5, "length": 4},
                    {"n1": 4, "n2": 6, "length": 4},
                    {"n1": 0, "n2": 1, "length": 4},
                    {"n1": 0, "n2": 2, "length": 4},
                ],
            },
        },
    },
    grid_size=32,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <line stroke="black" x1="0" y1="0" x2="0" y2="4"/>
  <line stroke="black" x1="0" y1="0" x2="4" y2="0"/>
  <line stroke="red" x1="0" y1="0" x2="4" y2="4"/>
  <line stroke="green" x1="0" y1="4" x2="4" y2="4"/>
  <line stroke="black" x1="0" y1="4" x2="0" y2="8"/>
  <line stroke="green" x1="4" y1="0" x2="4" y2="4"/>
  <line stroke="black" x1="4" y1="0" x2="8" y2="0"/>
  <line stroke="red" x1="4" y1="4" x2="8" y2="0"/>
  <line stroke="green" x1="4" y1="4" x2="12" y2="4"/>
  <line stroke="green" x1="0" y1="8" x2="4" y2="8"/>
  <line stroke="black" x1="0" y1="8" x2="0" y2="12"/>
  <line stroke="black" x1="8" y1="0" x2="12" y2="0"/>
  <line stroke="red" x1="8" y1="0" x2="12" y2="4"/>
  <line stroke="red" x1="4" y1="8" x2="0" y2="12"/>
  <line stroke="red" x1="4" y1="8" x2="8" y2="12"/>
  <line stroke="green" x1="4" y1="8" x2="12" y2="8"/>
  <line stroke="green" x1="4" y1="8" x2="4" y2="16"/>
  <line stroke="black" x1="0" y1="12" x2="0" y2="16"/>
  <line stroke="red" x1="0" y1="12" x2="4" y2="16"/>
  <line stroke="green" x1="12" y1="0" x2="12" y2="4"/>
  <line stroke="black" x1="12" y1="0" x2="16" y2="0"/>
  <line stroke="red" x1="12" y1="4" x2="16" y2="8"/>
  <line stroke="red" x1="8" y1="12" x2="12" y2="8"/>
  <line stroke="red" x1="8" y1="12" x2="4" y2="16"/>
  <line stroke="red" x1="8" y1="12" x2="12" y2="16"/>
  <line stroke="green" x1="12" y1="8" x2="12" y2="10"/>
  <line stroke="red" x1="12" y1="8" x2="13" y2="9"/>
  <line stroke="green" x1="12" y1="8" x2="16" y2="8"/>
  <line stroke="red" x1="12" y1="10" x2="13" y2="9"/>
  <line stroke="green" x1="12" y1="10" x2="12" y2="12"/>
  <line stroke="red" x1="12" y1="10" x2="13" y2="11"/>
  <line stroke="green" x1="12" y1="10" x2="20" y2="10"/>
  <line stroke="red" x1="13" y1="9" x2="19" y2="9"/>
  <line stroke="green" x1="0" y1="16" x2="4" y2="16"/>
  <line stroke="black" x1="0" y1="16" x2="0" y2="20"/>
  <line stroke="green" x1="16" y1="0" x2="16" y2="8"/>
  <line stroke="black" x1="16" y1="0" x2="20" y2="0"/>
  <line stroke="red" x1="4" y1="16" x2="6" y2="18"/>
  <line stroke="red" x1="4" y1="16" x2="0" y2="20"/>
  <line stroke="green" x1="4" y1="16" x2="12" y2="16"/>
  <line stroke="green" x1="4" y1="16" x2="4" y2="20"/>
  <line stroke="red" x1="12" y1="12" x2="13" y2="11"/>
  <line stroke="red" x1="12" y1="12" x2="13" y2="13"/>
  <line stroke="green" x1="12" y1="12" x2="12" y2="14"/>
  <line stroke="green" x1="12" y1="12" x2="20" y2="12"/>
  <line stroke="red" x1="13" y1="11" x2="19" y2="11"/>
  <line stroke="red" x1="16" y1="8" x2="20" y2="4"/>
  <line stroke="green" x1="16" y1="8" x2="20" y2="8"/>
  <line stroke="red" x1="13" y1="13" x2="12" y2="14"/>
  <line stroke="red" x1="13" y1="13" x2="19" y2="13"/>
  <line stroke="red" x1="12" y1="14" x2="13" y2="15"/>
  <line stroke="green" x1="12" y1="14" x2="12" y2="16"/>
  <line stroke="green" x1="12" y1="14" x2="20" y2="14"/>
  <line stroke="red" x1="6" y1="18" x2="4" y2="20"/>
  <line stroke="red" x1="6" y1="18" x2="26" y2="18"/>
  <line stroke="red" x1="13" y1="15" x2="12" y2="16"/>
  <line stroke="red" x1="13" y1="15" x2="19" y2="15"/>
  <line stroke="black" x1="0" y1="20" x2="0" y2="24"/>
  <line stroke="red" x1="0" y1="20" x2="4" y2="24"/>
  <line stroke="green" x1="12" y1="16" x2="20" y2="16"/>
  <line stroke="green" x1="20" y1="0" x2="20" y2="4"/>
  <line stroke="black" x1="20" y1="0" x2="24" y2="0"/>
  <line stroke="green" x1="4" y1="20" x2="4" y2="24"/>
  <line stroke="green" x1="4" y1="20" x2="28" y2="20"/>
  <line stroke="red" x1="4" y1="20" x2="16" y2="32"/>
  <line stroke="red" x1="20" y1="4" x2="24" y2="0"/>
  <line stroke="green" x1="20" y1="4" x2="28" y2="4"/>
  <line stroke="red" x1="19" y1="9" x2="20" y2="8"/>
  <line stroke="red" x1="19" y1="9" x2="20" y2="10"/>
  <line stroke="green" x1="20" y1="8" x2="20" y2="10"/>
  <line stroke="red" x1="20" y1="8" x2="24" y2="12"/>
  <line stroke="green" x1="20" y1="8" x2="28" y2="8"/>
  <line stroke="red" x1="19" y1="11" x2="20" y2="10"/>
  <line stroke="red" x1="19" y1="11" x2="20" y2="12"/>
  <line stroke="green" x1="20" y1="10" x2="20" y2="12"/>
  <line stroke="red" x1="19" y1="13" x2="20" y2="12"/>
  <line stroke="red" x1="19" y1="13" x2="20" y2="14"/>
  <line stroke="green" x1="20" y1="12" x2="20" y2="14"/>
  <line stroke="green" x1="0" y1="24" x2="4" y2="24"/>
  <line stroke="black" x1="0" y1="24" x2="0" y2="28"/>
  <line stroke="black" x1="24" y1="0" x2="28" y2="0"/>
  <line stroke="red" x1="24" y1="0" x2="28" y2="4"/>
  <line stroke="red" x1="19" y1="15" x2="20" y2="14"/>
  <line stroke="red" x1="19" y1="15" x2="20" y2="16"/>
  <line stroke="red" x1="4" y1="24" x2="0" y2="28"/>
  <line stroke="green" x1="4" y1="24" x2="4" y2="32"/>
  <line stroke="green" x1="20" y1="14" x2="20" y2="16"/>
  <line stroke="red" x1="20" y1="16" x2="24" y2="12"/>
  <line stroke="green" x1="20" y1="16" x2="28" y2="16"/>
  <line stroke="red" x1="24" y1="12" x2="28" y2="8"/>
  <line stroke="red" x1="24" y1="12" x2="28" y2="16"/>
  <line stroke="black" x1="0" y1="28" x2="0" y2="32"/>
  <line stroke="red" x1="0" y1="28" x2="4" y2="32"/>
  <line stroke="green" x1="28" y1="0" x2="28" y2="4"/>
  <line stroke="black" x1="28" y1="0" x2="32" y2="0"/>
  <line stroke="red" x1="28" y1="4" x2="32" y2="0"/>
  <line stroke="green" x1="28" y1="4" x2="32" y2="4"/>
  <line stroke="green" x1="28" y1="8" x2="28" y2="16"/>
  <line stroke="green" x1="28" y1="8" x2="32" y2="8"/>
  <line stroke="red" x1="28" y1="8" x2="32" y2="12"/>
  <line stroke="red" x1="26" y1="18" x2="28" y2="16"/>
  <line stroke="red" x1="26" y1="18" x2="28" y2="20"/>
  <line stroke="black" x1="0" y1="32" x2="4" y2="32"/>
  <line stroke="black" x1="32" y1="0" x2="32" y2="4"/>
  <line stroke="black" x1="4" y1="32" x2="16" y2="32"/>
  <line stroke="red" x1="28" y1="16" x2="32" y2="12"/>
  <line stroke="green" x1="28" y1="16" x2="28" y2="20"/>
  <line stroke="green" x1="28" y1="16" x2="32" y2="16"/>
  <line stroke="red" x1="28" y1="16" x2="32" y2="20"/>
  <line stroke="black" x1="32" y1="4" x2="32" y2="8"/>
  <line stroke="black" x1="32" y1="8" x2="32" y2="12"/>
  <line stroke="black" x1="32" y1="12" x2="32" y2="16"/>
  <line stroke="red" x1="28" y1="20" x2="16" y2="32"/>
  <line stroke="green" x1="28" y1="20" x2="28" y2="24"/>
  <line stroke="black" x1="16" y1="32" x2="28" y2="32"/>
  <line stroke="black" x1="32" y1="16" x2="32" y2="20"/>
  <line stroke="red" x1="28" y1="24" x2="32" y2="20"/>
  <line stroke="green" x1="28" y1="24" x2="32" y2="24"/>
  <line stroke="green" x1="28" y1="24" x2="28" y2="32"/>
  <line stroke="red" x1="28" y1="24" x2="32" y2="28"/>
  <line stroke="black" x1="32" y1="20" x2="32" y2="24"/>
  <line stroke="black" x1="32" y1="24" x2="32" y2="28"/>
  <line stroke="red" x1="28" y1="32" x2="32" y2="28"/>
  <line stroke="black" x1="28" y1="32" x2="32" y2="32"/>
  <line stroke="black" x1="32" y1="28" x2="32" y2="32"/>
</svg>
""",
    assigned_pleats_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <line stroke="black" x1="0" y1="0" x2="8" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="12"/>
  <line stroke="red" x1="1" y1="1" x2="7" y2="1"/>
  <line stroke="red" x1="1" y1="1" x2="1" y2="11"/>
  <line stroke="blue" x1="2" y1="2" x2="6" y2="2"/>
  <line stroke="blue" x1="2" y1="2" x2="2" y2="10"/>
  <line stroke="red" x1="3" y1="3" x2="5" y2="3"/>
  <line stroke="red" x1="3" y1="3" x2="3" y2="9"/>
  <line stroke="blue" x1="4" y1="4" x2="4" y2="8"/>
  <line stroke="red" x1="5" y1="3" x2="5" y2="9"/>
  <line stroke="blue" x1="6" y1="2" x2="6" y2="10"/>
  <line stroke="red" x1="7" y1="1" x2="7" y2="11"/>
  <line stroke="blue" x1="8" y1="0" x2="8" y2="12"/>
  <line stroke="black" x1="8" y1="0" x2="24" y2="0"/>
  <line stroke="red" x1="9" y1="1" x2="9" y2="11"/>
  <line stroke="red" x1="9" y1="1" x2="23" y2="1"/>
  <line stroke="red" x1="3" y1="9" x2="5" y2="9"/>
  <line stroke="blue" x1="2" y1="10" x2="6" y2="10"/>
  <line stroke="blue" x1="10" y1="2" x2="10" y2="10"/>
  <line stroke="blue" x1="10" y1="2" x2="22" y2="2"/>
  <line stroke="red" x1="1" y1="11" x2="7" y2="11"/>
  <line stroke="red" x1="11" y1="3" x2="11" y2="9"/>
  <line stroke="red" x1="11" y1="3" x2="21" y2="3"/>
  <line stroke="blue" x1="0" y1="12" x2="8" y2="12"/>
  <line stroke="black" x1="0" y1="12" x2="0" y2="20"/>
  <line stroke="blue" x1="12" y1="4" x2="12" y2="8"/>
  <line stroke="blue" x1="12" y1="4" x2="20" y2="4"/>
  <line stroke="red" x1="1" y1="13" x2="7" y2="13"/>
  <line stroke="red" x1="1" y1="13" x2="1" y2="19"/>
  <line stroke="red" x1="13" y1="5" x2="13" y2="9"/>
  <line stroke="red" x1="13" y1="5" x2="19" y2="5"/>
  <line stroke="blue" x1="2" y1="14" x2="6" y2="14"/>
  <line stroke="blue" x1="2" y1="14" x2="2" y2="18"/>
  <line stroke="blue" x1="10" y1="10" x2="12" y2="10"/>
  <line stroke="red" x1="9" y1="11" x2="13" y2="11"/>
  <line stroke="red" x1="11" y1="9" x2="13" y2="9"/>
  <line stroke="blue" x1="8" y1="12" x2="12" y2="12"/>
  <line stroke="blue" x1="8" y1="12" x2="8" y2="24"/>
  <line stroke="red" x1="7" y1="13" x2="7" y2="23"/>
  <line stroke="blue" x1="6" y1="14" x2="6" y2="18"/>
  <line stroke="blue" x1="14" y1="6" x2="18" y2="6"/>
  <line stroke="blue" x1="14" y1="6" x2="14" y2="30"/>
  <line stroke="red" x1="3" y1="15" x2="5" y2="15"/>
  <line stroke="red" x1="3" y1="15" x2="3" y2="17"/>
  <line stroke="red" x1="5" y1="15" x2="5" y2="17"/>
  <line stroke="red" x1="9" y1="13" x2="13" y2="13"/>
  <line stroke="red" x1="9" y1="13" x2="9" y2="25"/>
  <line stroke="red" x1="13" y1="9" x2="13" y2="11"/>
  <line stroke="red" x1="15" y1="7" x2="17" y2="7"/>
  <line stroke="red" x1="15" y1="7" x2="15" y2="31"/>
  <line stroke="red" x1="13" y1="11" x2="13" y2="13"/>
  <line stroke="blue" x1="10" y1="14" x2="12" y2="14"/>
  <line stroke="blue" x1="10" y1="14" x2="10" y2="26"/>
  <line stroke="red" x1="3" y1="17" x2="5" y2="17"/>
  <line stroke="blue" x1="16" y1="8" x2="16" y2="32"/>
  <line stroke="blue" x1="2" y1="18" x2="6" y2="18"/>
  <line stroke="red" x1="13" y1="13" x2="13" y2="15"/>
  <line stroke="red" x1="17" y1="7" x2="17" y2="31"/>
  <line stroke="red" x1="11" y1="15" x2="13" y2="15"/>
  <line stroke="red" x1="11" y1="15" x2="11" y2="27"/>
  <line stroke="blue" x1="6" y1="18" x2="6" y2="22"/>
  <line stroke="blue" x1="18" y1="6" x2="18" y2="30"/>
  <line stroke="red" x1="1" y1="19" x2="5" y2="19"/>
  <line stroke="red" x1="5" y1="19" x2="5" y2="21"/>
  <line stroke="red" x1="19" y1="5" x2="19" y2="9"/>
  <line stroke="red" x1="13" y1="15" x2="13" y2="29"/>
  <line stroke="blue" x1="0" y1="20" x2="4" y2="20"/>
  <line stroke="black" x1="0" y1="20" x2="0" y2="28"/>
  <line stroke="blue" x1="12" y1="16" x2="12" y2="28"/>
  <line stroke="blue" x1="20" y1="4" x2="20" y2="8"/>
  <line stroke="red" x1="1" y1="21" x2="5" y2="21"/>
  <line stroke="red" x1="1" y1="21" x2="1" y2="27"/>
  <line stroke="red" x1="19" y1="9" x2="19" y2="11"/>
  <line stroke="red" x1="19" y1="9" x2="21" y2="9"/>
  <line stroke="red" x1="21" y1="3" x2="21" y2="9"/>
  <line stroke="red" x1="19" y1="11" x2="19" y2="13"/>
  <line stroke="red" x1="19" y1="11" x2="23" y2="11"/>
  <line stroke="blue" x1="2" y1="22" x2="6" y2="22"/>
  <line stroke="blue" x1="2" y1="22" x2="2" y2="26"/>
  <line stroke="blue" x1="22" y1="2" x2="22" y2="10"/>
  <line stroke="blue" x1="20" y1="10" x2="22" y2="10"/>
  <line stroke="red" x1="19" y1="13" x2="19" y2="15"/>
  <line stroke="red" x1="19" y1="13" x2="23" y2="13"/>
  <line stroke="red" x1="23" y1="1" x2="23" y2="11"/>
  <line stroke="red" x1="3" y1="23" x2="7" y2="23"/>
  <line stroke="red" x1="3" y1="23" x2="3" y2="25"/>
  <line stroke="blue" x1="20" y1="12" x2="24" y2="12"/>
  <line stroke="blue" x1="24" y1="0" x2="24" y2="12"/>
  <line stroke="black" x1="24" y1="0" x2="32" y2="0"/>
  <line stroke="red" x1="19" y1="15" x2="21" y2="15"/>
  <line stroke="red" x1="19" y1="15" x2="19" y2="29"/>
  <line stroke="blue" x1="4" y1="24" x2="8" y2="24"/>
  <line stroke="blue" x1="20" y1="14" x2="22" y2="14"/>
  <line stroke="red" x1="25" y1="1" x2="25" y2="11"/>
  <line stroke="red" x1="25" y1="1" x2="31" y2="1"/>
  <line stroke="red" x1="3" y1="25" x2="9" y2="25"/>
  <line stroke="blue" x1="20" y1="16" x2="20" y2="28"/>
  <line stroke="red" x1="21" y1="15" x2="21" y2="27"/>
  <line stroke="blue" x1="2" y1="26" x2="10" y2="26"/>
  <line stroke="blue" x1="22" y1="14" x2="22" y2="26"/>
  <line stroke="blue" x1="26" y1="2" x2="26" y2="10"/>
  <line stroke="blue" x1="26" y1="2" x2="30" y2="2"/>
  <line stroke="red" x1="23" y1="13" x2="23" y2="25"/>
  <line stroke="blue" x1="24" y1="12" x2="24" y2="24"/>
  <line stroke="blue" x1="24" y1="12" x2="32" y2="12"/>
  <line stroke="red" x1="1" y1="27" x2="11" y2="27"/>
  <line stroke="red" x1="27" y1="3" x2="27" y2="9"/>
  <line stroke="red" x1="27" y1="3" x2="29" y2="3"/>
  <line stroke="red" x1="25" y1="11" x2="31" y2="11"/>
  <line stroke="blue" x1="26" y1="10" x2="30" y2="10"/>
  <line stroke="blue" x1="0" y1="28" x2="12" y2="28"/>
  <line stroke="black" x1="0" y1="28" x2="0" y2="32"/>
  <line stroke="red" x1="25" y1="13" x2="31" y2="13"/>
  <line stroke="red" x1="25" y1="13" x2="25" y2="23"/>
  <line stroke="blue" x1="28" y1="4" x2="28" y2="8"/>
  <line stroke="red" x1="27" y1="9" x2="29" y2="9"/>
  <line stroke="red" x1="1" y1="29" x2="13" y2="29"/>
  <line stroke="red" x1="1" y1="29" x2="1" y2="32"/>
  <line stroke="red" x1="29" y1="3" x2="29" y2="9"/>
  <line stroke="blue" x1="26" y1="14" x2="26" y2="18"/>
  <line stroke="blue" x1="26" y1="14" x2="30" y2="14"/>
  <line stroke="blue" x1="2" y1="30" x2="2" y2="32"/>
  <line stroke="blue" x1="2" y1="30" x2="14" y2="30"/>
  <line stroke="blue" x1="30" y1="2" x2="30" y2="10"/>
  <line stroke="red" x1="27" y1="15" x2="27" y2="17"/>
  <line stroke="red" x1="27" y1="15" x2="29" y2="15"/>
  <line stroke="red" x1="31" y1="1" x2="31" y2="11"/>
  <line stroke="red" x1="3" y1="31" x2="3" y2="32"/>
  <line stroke="red" x1="3" y1="31" x2="15" y2="31"/>
  <line stroke="blue" x1="26" y1="18" x2="26" y2="22"/>
  <line stroke="blue" x1="26" y1="18" x2="30" y2="18"/>
  <line stroke="red" x1="27" y1="17" x2="29" y2="17"/>
  <line stroke="black" x1="0" y1="32" x2="1" y2="32"/>
  <line stroke="black" x1="32" y1="0" x2="32" y2="12"/>
  <line stroke="black" x1="1" y1="32" x2="2" y2="32"/>
  <line stroke="black" x1="2" y1="32" x2="3" y2="32"/>
  <line stroke="black" x1="3" y1="32" x2="16" y2="32"/>
  <line stroke="red" x1="29" y1="15" x2="29" y2="17"/>
  <line stroke="red" x1="27" y1="19" x2="27" y2="21"/>
  <line stroke="red" x1="27" y1="19" x2="31" y2="19"/>
  <line stroke="blue" x1="30" y1="14" x2="30" y2="18"/>
  <line stroke="red" x1="31" y1="13" x2="31" y2="19"/>
  <line stroke="blue" x1="24" y1="24" x2="28" y2="24"/>
  <line stroke="red" x1="23" y1="25" x2="29" y2="25"/>
  <line stroke="red" x1="25" y1="23" x2="29" y2="23"/>
  <line stroke="blue" x1="22" y1="26" x2="30" y2="26"/>
  <line stroke="blue" x1="26" y1="22" x2="30" y2="22"/>
  <line stroke="black" x1="32" y1="12" x2="32" y2="20"/>
  <line stroke="red" x1="21" y1="27" x2="31" y2="27"/>
  <line stroke="red" x1="27" y1="21" x2="31" y2="21"/>
  <line stroke="blue" x1="20" y1="28" x2="32" y2="28"/>
  <line stroke="blue" x1="28" y1="20" x2="32" y2="20"/>
  <line stroke="red" x1="19" y1="29" x2="31" y2="29"/>
  <line stroke="blue" x1="18" y1="30" x2="30" y2="30"/>
  <line stroke="red" x1="17" y1="31" x2="29" y2="31"/>
  <line stroke="black" x1="16" y1="32" x2="29" y2="32"/>
  <line stroke="red" x1="29" y1="23" x2="29" y2="25"/>
  <line stroke="blue" x1="30" y1="22" x2="30" y2="26"/>
  <line stroke="red" x1="31" y1="21" x2="31" y2="27"/>
  <line stroke="black" x1="32" y1="20" x2="32" y2="28"/>
  <line stroke="blue" x1="30" y1="30" x2="30" y2="32"/>
  <line stroke="red" x1="29" y1="31" x2="29" y2="32"/>
  <line stroke="red" x1="31" y1="29" x2="31" y2="32"/>
  <line stroke="black" x1="32" y1="28" x2="32" y2="32"/>
  <line stroke="black" x1="29" y1="32" x2="30" y2="32"/>
  <line stroke="black" x1="30" y1="32" x2="31" y2="32"/>
  <line stroke="black" x1="31" y1="32" x2="32" y2="32"/>
</svg>""",
    assigned_ridges_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="red" x1="0" y1="0" x2="31" y2="31"/>
  <line stroke="black" x1="0" y1="0" x2="250" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="375"/>
  <line stroke="blue" x1="31" y1="31" x2="62" y2="62"/>
  <line stroke="red" x1="31" y1="31" x2="219" y2="31"/>
  <line stroke="red" x1="31" y1="31" x2="31" y2="344"/>
  <line stroke="red" x1="62" y1="62" x2="94" y2="94"/>
  <line stroke="blue" x1="62" y1="62" x2="188" y2="62"/>
  <line stroke="blue" x1="62" y1="62" x2="62" y2="312"/>
  <line stroke="blue" x1="94" y1="94" x2="125" y2="125"/>
  <line stroke="red" x1="94" y1="94" x2="156" y2="94"/>
  <line stroke="red" x1="94" y1="94" x2="94" y2="281"/>
  <line stroke="blue" x1="125" y1="125" x2="156" y2="94"/>
  <line stroke="blue" x1="125" y1="125" x2="125" y2="250"/>
  <line stroke="red" x1="156" y1="94" x2="188" y2="62"/>
  <line stroke="red" x1="156" y1="94" x2="156" y2="281"/>
  <line stroke="blue" x1="188" y1="62" x2="219" y2="31"/>
  <line stroke="blue" x1="188" y1="62" x2="188" y2="312"/>
  <line stroke="red" x1="219" y1="31" x2="250" y2="0"/>
  <line stroke="red" x1="219" y1="31" x2="219" y2="344"/>
  <line stroke="red" x1="250" y1="0" x2="281" y2="31"/>
  <line stroke="blue" x1="250" y1="0" x2="250" y2="375"/>
  <line stroke="black" x1="250" y1="0" x2="750" y2="0"/>
  <line stroke="blue" x1="125" y1="250" x2="94" y2="281"/>
  <line stroke="blue" x1="125" y1="250" x2="156" y2="281"/>
  <line stroke="blue" x1="281" y1="31" x2="312" y2="62"/>
  <line stroke="red" x1="281" y1="31" x2="281" y2="344"/>
  <line stroke="red" x1="281" y1="31" x2="719" y2="31"/>
  <line stroke="red" x1="94" y1="281" x2="62" y2="312"/>
  <line stroke="red" x1="94" y1="281" x2="156" y2="281"/>
  <line stroke="blue" x1="62" y1="312" x2="31" y2="344"/>
  <line stroke="blue" x1="62" y1="312" x2="188" y2="312"/>
  <line stroke="red" x1="312" y1="62" x2="344" y2="94"/>
  <line stroke="blue" x1="312" y1="62" x2="312" y2="312"/>
  <line stroke="blue" x1="312" y1="62" x2="688" y2="62"/>
  <line stroke="red" x1="156" y1="281" x2="188" y2="312"/>
  <line stroke="red" x1="31" y1="344" x2="0" y2="375"/>
  <line stroke="red" x1="31" y1="344" x2="219" y2="344"/>
  <line stroke="blue" x1="344" y1="94" x2="375" y2="125"/>
  <line stroke="red" x1="344" y1="94" x2="344" y2="281"/>
  <line stroke="red" x1="344" y1="94" x2="656" y2="94"/>
  <line stroke="blue" x1="188" y1="312" x2="219" y2="344"/>
  <line stroke="red" x1="0" y1="375" x2="31" y2="406"/>
  <line stroke="blue" x1="0" y1="375" x2="250" y2="375"/>
  <line stroke="black" x1="0" y1="375" x2="0" y2="625"/>
  <line stroke="red" x1="375" y1="125" x2="406" y2="156"/>
  <line stroke="blue" x1="375" y1="125" x2="375" y2="250"/>
  <line stroke="blue" x1="375" y1="125" x2="625" y2="125"/>
  <line stroke="blue" x1="31" y1="406" x2="62" y2="438"/>
  <line stroke="red" x1="31" y1="406" x2="219" y2="406"/>
  <line stroke="red" x1="31" y1="406" x2="31" y2="594"/>
  <line stroke="red" x1="219" y1="344" x2="250" y2="375"/>
  <line stroke="blue" x1="406" y1="156" x2="438" y2="188"/>
  <line stroke="red" x1="406" y1="156" x2="406" y2="281"/>
  <line stroke="red" x1="406" y1="156" x2="594" y2="156"/>
  <line stroke="blue" x1="62" y1="438" x2="188" y2="438"/>
  <line stroke="red" x1="62" y1="438" x2="94" y2="469"/>
  <line stroke="blue" x1="62" y1="438" x2="62" y2="562"/>
  <line stroke="blue" x1="312" y1="312" x2="281" y2="344"/>
  <line stroke="red" x1="312" y1="312" x2="344" y2="281"/>
  <line stroke="blue" x1="312" y1="312" x2="375" y2="312"/>
  <line stroke="red" x1="281" y1="344" x2="250" y2="375"/>
  <line stroke="red" x1="281" y1="344" x2="406" y2="344"/>
  <line stroke="blue" x1="344" y1="281" x2="375" y2="250"/>
  <line stroke="red" x1="344" y1="281" x2="406" y2="281"/>
  <line stroke="red" x1="250" y1="375" x2="219" y2="406"/>
  <line stroke="red" x1="250" y1="375" x2="281" y2="406"/>
  <line stroke="blue" x1="250" y1="375" x2="375" y2="375"/>
  <line stroke="blue" x1="250" y1="375" x2="250" y2="750"/>
  <line stroke="blue" x1="375" y1="250" x2="406" y2="281"/>
  <line stroke="blue" x1="219" y1="406" x2="188" y2="438"/>
  <line stroke="red" x1="219" y1="406" x2="219" y2="719"/>
  <line stroke="red" x1="188" y1="438" x2="156" y2="469"/>
  <line stroke="blue" x1="188" y1="438" x2="188" y2="562"/>
  <line stroke="red" x1="438" y1="188" x2="469" y2="219"/>
  <line stroke="blue" x1="438" y1="188" x2="562" y2="188"/>
  <line stroke="blue" x1="438" y1="188" x2="438" y2="938"/>
  <line stroke="red" x1="94" y1="469" x2="156" y2="469"/>
  <line stroke="blue" x1="94" y1="469" x2="125" y2="500"/>
  <line stroke="red" x1="94" y1="469" x2="94" y2="531"/>
  <line stroke="blue" x1="375" y1="312" x2="406" y2="281"/>
  <line stroke="blue" x1="375" y1="312" x2="406" y2="344"/>
  <line stroke="blue" x1="156" y1="469" x2="125" y2="500"/>
  <line stroke="red" x1="156" y1="469" x2="156" y2="531"/>
  <line stroke="blue" x1="281" y1="406" x2="312" y2="438"/>
  <line stroke="red" x1="281" y1="406" x2="406" y2="406"/>
  <line stroke="red" x1="281" y1="406" x2="281" y2="781"/>
  <line stroke="red" x1="406" y1="281" x2="406" y2="344"/>
  <line stroke="blue" x1="125" y1="500" x2="94" y2="531"/>
  <line stroke="blue" x1="125" y1="500" x2="156" y2="531"/>
  <line stroke="blue" x1="469" y1="219" x2="500" y2="250"/>
  <line stroke="red" x1="469" y1="219" x2="531" y2="219"/>
  <line stroke="red" x1="469" y1="219" x2="469" y2="969"/>
  <line stroke="blue" x1="375" y1="375" x2="406" y2="344"/>
  <line stroke="blue" x1="375" y1="375" x2="406" y2="406"/>
  <line stroke="red" x1="406" y1="344" x2="406" y2="406"/>
  <line stroke="blue" x1="312" y1="438" x2="375" y2="438"/>
  <line stroke="red" x1="312" y1="438" x2="344" y2="469"/>
  <line stroke="blue" x1="312" y1="438" x2="312" y2="812"/>
  <line stroke="red" x1="94" y1="531" x2="156" y2="531"/>
  <line stroke="red" x1="94" y1="531" x2="62" y2="562"/>
  <line stroke="red" x1="156" y1="531" x2="188" y2="562"/>
  <line stroke="blue" x1="500" y1="250" x2="531" y2="219"/>
  <line stroke="blue" x1="500" y1="250" x2="500" y2="1000"/>
  <line stroke="blue" x1="62" y1="562" x2="188" y2="562"/>
  <line stroke="blue" x1="62" y1="562" x2="31" y2="594"/>
  <line stroke="blue" x1="406" y1="406" x2="375" y2="438"/>
  <line stroke="red" x1="406" y1="406" x2="406" y2="469"/>
  <line stroke="red" x1="531" y1="219" x2="562" y2="188"/>
  <line stroke="red" x1="531" y1="219" x2="531" y2="969"/>
  <line stroke="blue" x1="375" y1="438" x2="406" y2="469"/>
  <line stroke="red" x1="344" y1="469" x2="406" y2="469"/>
  <line stroke="blue" x1="344" y1="469" x2="375" y2="500"/>
  <line stroke="red" x1="344" y1="469" x2="344" y2="844"/>
  <line stroke="red" x1="188" y1="562" x2="156" y2="594"/>
  <line stroke="blue" x1="188" y1="562" x2="188" y2="688"/>
  <line stroke="blue" x1="562" y1="188" x2="594" y2="156"/>
  <line stroke="blue" x1="562" y1="188" x2="562" y2="938"/>
  <line stroke="red" x1="31" y1="594" x2="156" y2="594"/>
  <line stroke="red" x1="31" y1="594" x2="0" y2="625"/>
  <line stroke="blue" x1="156" y1="594" x2="125" y2="625"/>
  <line stroke="red" x1="156" y1="594" x2="156" y2="656"/>
  <line stroke="red" x1="594" y1="156" x2="625" y2="125"/>
  <line stroke="red" x1="594" y1="156" x2="594" y2="281"/>
  <line stroke="blue" x1="406" y1="469" x2="375" y2="500"/>
  <line stroke="red" x1="406" y1="469" x2="406" y2="906"/>
  <line stroke="blue" x1="0" y1="625" x2="125" y2="625"/>
  <line stroke="red" x1="0" y1="625" x2="31" y2="656"/>
  <line stroke="black" x1="0" y1="625" x2="0" y2="875"/>
  <line stroke="blue" x1="375" y1="500" x2="375" y2="875"/>
  <line stroke="blue" x1="125" y1="625" x2="156" y2="656"/>
  <line stroke="blue" x1="625" y1="125" x2="656" y2="94"/>
  <line stroke="blue" x1="625" y1="125" x2="625" y2="250"/>
  <line stroke="red" x1="31" y1="656" x2="156" y2="656"/>
  <line stroke="blue" x1="31" y1="656" x2="62" y2="688"/>
  <line stroke="red" x1="31" y1="656" x2="31" y2="844"/>
  <line stroke="blue" x1="594" y1="281" x2="625" y2="250"/>
  <line stroke="red" x1="594" y1="281" x2="594" y2="344"/>
  <line stroke="blue" x1="594" y1="281" x2="625" y2="312"/>
  <line stroke="red" x1="594" y1="281" x2="656" y2="281"/>
  <line stroke="red" x1="656" y1="94" x2="688" y2="62"/>
  <line stroke="red" x1="656" y1="94" x2="656" y2="281"/>
  <line stroke="blue" x1="625" y1="250" x2="656" y2="281"/>
  <line stroke="red" x1="156" y1="656" x2="188" y2="688"/>
  <line stroke="blue" x1="594" y1="344" x2="625" y2="312"/>
  <line stroke="red" x1="594" y1="344" x2="594" y2="406"/>
  <line stroke="blue" x1="594" y1="344" x2="625" y2="375"/>
  <line stroke="red" x1="594" y1="344" x2="719" y2="344"/>
  <line stroke="blue" x1="62" y1="688" x2="188" y2="688"/>
  <line stroke="red" x1="62" y1="688" x2="94" y2="719"/>
  <line stroke="blue" x1="62" y1="688" x2="62" y2="812"/>
  <line stroke="blue" x1="688" y1="62" x2="719" y2="31"/>
  <line stroke="blue" x1="688" y1="62" x2="688" y2="312"/>
  <line stroke="blue" x1="625" y1="312" x2="688" y2="312"/>
  <line stroke="blue" x1="188" y1="688" x2="219" y2="719"/>
  <line stroke="red" x1="656" y1="281" x2="688" y2="312"/>
  <line stroke="blue" x1="594" y1="406" x2="625" y2="375"/>
  <line stroke="red" x1="594" y1="406" x2="594" y2="469"/>
  <line stroke="blue" x1="594" y1="406" x2="625" y2="438"/>
  <line stroke="red" x1="594" y1="406" x2="719" y2="406"/>
  <line stroke="red" x1="719" y1="31" x2="750" y2="0"/>
  <line stroke="red" x1="719" y1="31" x2="719" y2="344"/>
  <line stroke="red" x1="94" y1="719" x2="219" y2="719"/>
  <line stroke="blue" x1="94" y1="719" x2="125" y2="750"/>
  <line stroke="red" x1="94" y1="719" x2="94" y2="781"/>
  <line stroke="blue" x1="625" y1="375" x2="750" y2="375"/>
  <line stroke="red" x1="750" y1="0" x2="781" y2="31"/>
  <line stroke="blue" x1="750" y1="0" x2="750" y2="375"/>
  <line stroke="black" x1="750" y1="0" x2="1000" y2="0"/>
  <line stroke="red" x1="219" y1="719" x2="250" y2="750"/>
  <line stroke="blue" x1="688" y1="312" x2="719" y2="344"/>
  <line stroke="blue" x1="594" y1="469" x2="625" y2="438"/>
  <line stroke="blue" x1="594" y1="469" x2="625" y2="500"/>
  <line stroke="red" x1="594" y1="469" x2="656" y2="469"/>
  <line stroke="red" x1="594" y1="469" x2="594" y2="906"/>
  <line stroke="blue" x1="125" y1="750" x2="94" y2="781"/>
  <line stroke="blue" x1="125" y1="750" x2="250" y2="750"/>
  <line stroke="blue" x1="625" y1="438" x2="688" y2="438"/>
  <line stroke="blue" x1="781" y1="31" x2="812" y2="62"/>
  <line stroke="red" x1="781" y1="31" x2="781" y2="344"/>
  <line stroke="red" x1="781" y1="31" x2="969" y2="31"/>
  <line stroke="red" x1="94" y1="781" x2="62" y2="812"/>
  <line stroke="red" x1="94" y1="781" x2="281" y2="781"/>
  <line stroke="blue" x1="250" y1="750" x2="281" y2="781"/>
  <line stroke="red" x1="719" y1="344" x2="750" y2="375"/>
  <line stroke="blue" x1="625" y1="500" x2="656" y2="469"/>
  <line stroke="blue" x1="625" y1="500" x2="625" y2="875"/>
  <line stroke="red" x1="656" y1="469" x2="688" y2="438"/>
  <line stroke="red" x1="656" y1="469" x2="656" y2="844"/>
  <line stroke="blue" x1="62" y1="812" x2="31" y2="844"/>
  <line stroke="blue" x1="62" y1="812" x2="312" y2="812"/>
  <line stroke="blue" x1="688" y1="438" x2="719" y2="406"/>
  <line stroke="blue" x1="688" y1="438" x2="688" y2="812"/>
  <line stroke="red" x1="812" y1="62" x2="844" y2="94"/>
  <line stroke="blue" x1="812" y1="62" x2="812" y2="312"/>
  <line stroke="blue" x1="812" y1="62" x2="938" y2="62"/>
  <line stroke="red" x1="719" y1="406" x2="750" y2="375"/>
  <line stroke="red" x1="719" y1="406" x2="719" y2="781"/>
  <line stroke="red" x1="281" y1="781" x2="312" y2="812"/>
  <line stroke="red" x1="750" y1="375" x2="781" y2="344"/>
  <line stroke="red" x1="750" y1="375" x2="781" y2="406"/>
  <line stroke="blue" x1="750" y1="375" x2="750" y2="750"/>
  <line stroke="blue" x1="750" y1="375" x2="1000" y2="375"/>
  <line stroke="red" x1="31" y1="844" x2="0" y2="875"/>
  <line stroke="red" x1="31" y1="844" x2="344" y2="844"/>
  <line stroke="blue" x1="844" y1="94" x2="875" y2="125"/>
  <line stroke="red" x1="844" y1="94" x2="844" y2="281"/>
  <line stroke="red" x1="844" y1="94" x2="906" y2="94"/>
  <line stroke="blue" x1="781" y1="344" x2="812" y2="312"/>
  <line stroke="red" x1="781" y1="344" x2="969" y2="344"/>
  <line stroke="blue" x1="312" y1="812" x2="344" y2="844"/>
  <line stroke="red" x1="812" y1="312" x2="844" y2="281"/>
  <line stroke="blue" x1="812" y1="312" x2="938" y2="312"/>
  <line stroke="red" x1="0" y1="875" x2="31" y2="906"/>
  <line stroke="blue" x1="0" y1="875" x2="375" y2="875"/>
  <line stroke="black" x1="0" y1="875" x2="0" y2="1000"/>
  <line stroke="blue" x1="781" y1="406" x2="812" y2="438"/>
  <line stroke="red" x1="781" y1="406" x2="969" y2="406"/>
  <line stroke="red" x1="781" y1="406" x2="781" y2="719"/>
  <line stroke="blue" x1="875" y1="125" x2="875" y2="250"/>
  <line stroke="blue" x1="875" y1="125" x2="906" y2="94"/>
  <line stroke="blue" x1="844" y1="281" x2="875" y2="250"/>
  <line stroke="red" x1="844" y1="281" x2="906" y2="281"/>
  <line stroke="blue" x1="31" y1="906" x2="62" y2="938"/>
  <line stroke="red" x1="31" y1="906" x2="406" y2="906"/>
  <line stroke="red" x1="31" y1="906" x2="31" y2="1000"/>
  <line stroke="blue" x1="875" y1="250" x2="906" y2="281"/>
  <line stroke="red" x1="344" y1="844" x2="375" y2="875"/>
  <line stroke="red" x1="906" y1="94" x2="938" y2="62"/>
  <line stroke="red" x1="906" y1="94" x2="906" y2="281"/>
  <line stroke="red" x1="812" y1="438" x2="844" y2="469"/>
  <line stroke="blue" x1="812" y1="438" x2="812" y2="562"/>
  <line stroke="blue" x1="812" y1="438" x2="938" y2="438"/>
  <line stroke="red" x1="62" y1="938" x2="94" y2="969"/>
  <line stroke="blue" x1="62" y1="938" x2="62" y2="1000"/>
  <line stroke="blue" x1="62" y1="938" x2="438" y2="938"/>
  <line stroke="blue" x1="938" y1="62" x2="969" y2="31"/>
  <line stroke="blue" x1="938" y1="62" x2="938" y2="312"/>
  <line stroke="red" x1="906" y1="281" x2="938" y2="312"/>
  <line stroke="blue" x1="375" y1="875" x2="406" y2="906"/>
  <line stroke="red" x1="844" y1="469" x2="844" y2="531"/>
  <line stroke="blue" x1="844" y1="469" x2="875" y2="500"/>
  <line stroke="red" x1="844" y1="469" x2="906" y2="469"/>
  <line stroke="red" x1="969" y1="31" x2="1000" y2="0"/>
  <line stroke="red" x1="969" y1="31" x2="969" y2="344"/>
  <line stroke="red" x1="94" y1="969" x2="94" y2="1000"/>
  <line stroke="blue" x1="94" y1="969" x2="125" y2="1000"/>
  <line stroke="red" x1="94" y1="969" x2="469" y2="969"/>
  <line stroke="red" x1="812" y1="562" x2="844" y2="531"/>
  <line stroke="red" x1="812" y1="562" x2="844" y2="594"/>
  <line stroke="blue" x1="812" y1="562" x2="812" y2="688"/>
  <line stroke="blue" x1="812" y1="562" x2="938" y2="562"/>
  <line stroke="blue" x1="938" y1="312" x2="969" y2="344"/>
  <line stroke="red" x1="406" y1="906" x2="438" y2="938"/>
  <line stroke="blue" x1="844" y1="531" x2="875" y2="500"/>
  <line stroke="red" x1="844" y1="531" x2="906" y2="531"/>
  <line stroke="black" x1="0" y1="1000" x2="31" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="375"/>
  <line stroke="black" x1="31" y1="1000" x2="62" y2="1000"/>
  <line stroke="black" x1="62" y1="1000" x2="94" y2="1000"/>
  <line stroke="black" x1="94" y1="1000" x2="125" y2="1000"/>
  <line stroke="black" x1="125" y1="1000" x2="500" y2="1000"/>
  <line stroke="blue" x1="875" y1="500" x2="906" y2="469"/>
  <line stroke="blue" x1="875" y1="500" x2="906" y2="531"/>
  <line stroke="red" x1="906" y1="469" x2="938" y2="438"/>
  <line stroke="red" x1="906" y1="469" x2="906" y2="531"/>
  <line stroke="red" x1="969" y1="344" x2="1000" y2="375"/>
  <line stroke="red" x1="844" y1="594" x2="844" y2="656"/>
  <line stroke="blue" x1="844" y1="594" x2="875" y2="625"/>
  <line stroke="red" x1="844" y1="594" x2="969" y2="594"/>
  <line stroke="blue" x1="438" y1="938" x2="469" y2="969"/>
  <line stroke="blue" x1="938" y1="438" x2="969" y2="406"/>
  <line stroke="blue" x1="938" y1="438" x2="938" y2="562"/>
  <line stroke="red" x1="906" y1="531" x2="938" y2="562"/>
  <line stroke="red" x1="969" y1="406" x2="1000" y2="375"/>
  <line stroke="red" x1="969" y1="406" x2="969" y2="594"/>
  <line stroke="blue" x1="750" y1="750" x2="719" y2="781"/>
  <line stroke="red" x1="750" y1="750" x2="781" y2="719"/>
  <line stroke="blue" x1="750" y1="750" x2="875" y2="750"/>
  <line stroke="red" x1="719" y1="781" x2="688" y2="812"/>
  <line stroke="red" x1="719" y1="781" x2="906" y2="781"/>
  <line stroke="blue" x1="781" y1="719" x2="812" y2="688"/>
  <line stroke="red" x1="781" y1="719" x2="906" y2="719"/>
  <line stroke="blue" x1="688" y1="812" x2="656" y2="844"/>
  <line stroke="blue" x1="688" y1="812" x2="938" y2="812"/>
  <line stroke="red" x1="812" y1="688" x2="844" y2="656"/>
  <line stroke="blue" x1="812" y1="688" x2="938" y2="688"/>
  <line stroke="black" x1="1000" y1="375" x2="1000" y2="625"/>
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
  <line stroke="blue" x1="562" y1="938" x2="531" y2="969"/>
  <line stroke="blue" x1="562" y1="938" x2="938" y2="938"/>
  <line stroke="blue" x1="938" y1="562" x2="969" y2="594"/>
  <line stroke="red" x1="531" y1="969" x2="500" y2="1000"/>
  <line stroke="red" x1="531" y1="969" x2="906" y2="969"/>
  <line stroke="black" x1="500" y1="1000" x2="875" y2="1000"/>
  <line stroke="red" x1="969" y1="594" x2="1000" y2="625"/>
  <line stroke="blue" x1="875" y1="750" x2="906" y2="719"/>
  <line stroke="blue" x1="875" y1="750" x2="906" y2="781"/>
  <line stroke="red" x1="906" y1="719" x2="938" y2="688"/>
  <line stroke="red" x1="906" y1="719" x2="906" y2="781"/>
  <line stroke="blue" x1="938" y1="688" x2="969" y2="656"/>
  <line stroke="blue" x1="938" y1="688" x2="938" y2="812"/>
  <line stroke="red" x1="969" y1="656" x2="1000" y2="625"/>
  <line stroke="red" x1="969" y1="656" x2="969" y2="844"/>
  <line stroke="black" x1="1000" y1="625" x2="1000" y2="875"/>
  <line stroke="red" x1="906" y1="781" x2="938" y2="812"/>
  <line stroke="blue" x1="938" y1="812" x2="969" y2="844"/>
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
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <line stroke="red" x1="0" y1="0" x2="1" y2="1"/>
  <line stroke="black" x1="0" y1="0" x2="4" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="8"/>
  <line stroke="blue" x1="1" y1="1" x2="2" y2="2"/>
  <line stroke="red" x1="1" y1="1" x2="4" y2="1"/>
  <line stroke="red" x1="1" y1="1" x2="1" y2="8"/>
  <line stroke="red" x1="2" y1="2" x2="3" y2="3"/>
  <line stroke="blue" x1="2" y1="2" x2="4" y2="2"/>
  <line stroke="blue" x1="2" y1="2" x2="2" y2="8"/>
  <line stroke="blue" x1="4" y1="0" x2="4" y2="1"/>
  <line stroke="black" x1="4" y1="0" x2="8" y2="0"/>
  <line stroke="red" x1="4" y1="1" x2="4" y2="2"/>
  <line stroke="red" x1="4" y1="1" x2="7" y2="1"/>
  <line stroke="red" x1="3" y1="3" x2="4" y2="3"/>
  <line stroke="blue" x1="3" y1="3" x2="4" y2="4"/>
  <line stroke="red" x1="3" y1="3" x2="3" y2="8"/>
  <line stroke="blue" x1="4" y1="2" x2="4" y2="3"/>
  <line stroke="blue" x1="4" y1="2" x2="6" y2="2"/>
  <line stroke="red" x1="4" y1="3" x2="4" y2="4"/>
  <line stroke="red" x1="4" y1="3" x2="5" y2="3"/>
  <line stroke="blue" x1="4" y1="4" x2="5" y2="3"/>
  <line stroke="blue" x1="4" y1="4" x2="4" y2="8"/>
  <line stroke="red" x1="5" y1="3" x2="6" y2="2"/>
  <line stroke="red" x1="5" y1="3" x2="5" y2="8"/>
  <line stroke="blue" x1="6" y1="2" x2="7" y2="1"/>
  <line stroke="blue" x1="6" y1="2" x2="6" y2="8"/>
  <line stroke="red" x1="7" y1="1" x2="8" y2="0"/>
  <line stroke="red" x1="7" y1="1" x2="7" y2="8"/>
  <line stroke="blue" x1="0" y1="8" x2="1" y2="8"/>
  <line stroke="black" x1="0" y1="8" x2="0" y2="12"/>
  <line stroke="red" x1="8" y1="0" x2="9" y2="1"/>
  <line stroke="blue" x1="8" y1="0" x2="8" y2="8"/>
  <line stroke="black" x1="8" y1="0" x2="16" y2="0"/>
  <line stroke="red" x1="1" y1="8" x2="2" y2="8"/>
  <line stroke="red" x1="1" y1="8" x2="1" y2="11"/>
  <line stroke="blue" x1="2" y1="8" x2="3" y2="8"/>
  <line stroke="blue" x1="2" y1="8" x2="2" y2="10"/>
  <line stroke="red" x1="3" y1="8" x2="4" y2="8"/>
  <line stroke="red" x1="3" y1="8" x2="3" y2="9"/>
  <line stroke="blue" x1="4" y1="8" x2="5" y2="8"/>
  <line stroke="blue" x1="4" y1="8" x2="3" y2="9"/>
  <line stroke="red" x1="4" y1="8" x2="4" y2="9"/>
  <line stroke="blue" x1="4" y1="8" x2="5" y2="9"/>
  <line stroke="blue" x1="9" y1="1" x2="10" y2="2"/>
  <line stroke="red" x1="9" y1="1" x2="9" y2="8"/>
  <line stroke="red" x1="9" y1="1" x2="15" y2="1"/>
  <line stroke="red" x1="5" y1="8" x2="6" y2="8"/>
  <line stroke="red" x1="5" y1="8" x2="5" y2="9"/>
  <line stroke="red" x1="3" y1="9" x2="4" y2="9"/>
  <line stroke="red" x1="3" y1="9" x2="2" y2="10"/>
  <line stroke="red" x1="4" y1="9" x2="5" y2="9"/>
  <line stroke="blue" x1="4" y1="9" x2="4" y2="10"/>
  <line stroke="blue" x1="6" y1="8" x2="7" y2="8"/>
  <line stroke="blue" x1="6" y1="8" x2="6" y2="10"/>
  <line stroke="blue" x1="2" y1="10" x2="4" y2="10"/>
  <line stroke="blue" x1="2" y1="10" x2="1" y2="11"/>
  <line stroke="red" x1="10" y1="2" x2="11" y2="3"/>
  <line stroke="blue" x1="10" y1="2" x2="10" y2="8"/>
  <line stroke="blue" x1="10" y1="2" x2="16" y2="2"/>
  <line stroke="red" x1="5" y1="9" x2="6" y2="10"/>
  <line stroke="red" x1="7" y1="8" x2="8" y2="8"/>
  <line stroke="red" x1="7" y1="8" x2="7" y2="11"/>
  <line stroke="blue" x1="4" y1="10" x2="6" y2="10"/>
  <line stroke="red" x1="4" y1="10" x2="4" y2="11"/>
  <line stroke="red" x1="1" y1="11" x2="4" y2="11"/>
  <line stroke="red" x1="1" y1="11" x2="0" y2="12"/>
  <line stroke="blue" x1="8" y1="8" x2="9" y2="8"/>
  <line stroke="blue" x1="8" y1="8" x2="8" y2="12"/>
  <line stroke="blue" x1="11" y1="3" x2="12" y2="4"/>
  <line stroke="red" x1="11" y1="3" x2="11" y2="8"/>
  <line stroke="red" x1="11" y1="3" x2="15" y2="3"/>
  <line stroke="blue" x1="6" y1="10" x2="7" y2="11"/>
  <line stroke="blue" x1="4" y1="11" x2="4" y2="12"/>
  <line stroke="red" x1="4" y1="11" x2="7" y2="11"/>
  <line stroke="blue" x1="0" y1="12" x2="4" y2="12"/>
  <line stroke="red" x1="0" y1="12" x2="1" y2="13"/>
  <line stroke="black" x1="0" y1="12" x2="0" y2="16"/>
  <line stroke="red" x1="9" y1="8" x2="10" y2="8"/>
  <line stroke="red" x1="9" y1="8" x2="9" y2="11"/>
  <line stroke="blue" x1="4" y1="12" x2="4" y2="13"/>
  <line stroke="red" x1="4" y1="12" x2="8" y2="12"/>
  <line stroke="red" x1="12" y1="4" x2="13" y2="5"/>
  <line stroke="blue" x1="12" y1="4" x2="12" y2="8"/>
  <line stroke="blue" x1="12" y1="4" x2="16" y2="4"/>
  <line stroke="blue" x1="10" y1="8" x2="11" y2="8"/>
  <line stroke="blue" x1="10" y1="8" x2="10" y2="10"/>
  <line stroke="red" x1="1" y1="13" x2="4" y2="13"/>
  <line stroke="blue" x1="1" y1="13" x2="2" y2="14"/>
  <line stroke="red" x1="1" y1="13" x2="1" y2="16"/>
  <line stroke="red" x1="7" y1="11" x2="8" y2="12"/>
  <line stroke="red" x1="4" y1="13" x2="4" y2="14"/>
  <line stroke="red" x1="4" y1="13" x2="7" y2="13"/>
  <line stroke="red" x1="11" y1="8" x2="11" y2="9"/>
  <line stroke="red" x1="11" y1="8" x2="12" y2="8"/>
  <line stroke="blue" x1="13" y1="5" x2="14" y2="6"/>
  <line stroke="red" x1="13" y1="5" x2="13" y2="9"/>
  <line stroke="red" x1="13" y1="5" x2="15" y2="5"/>
  <line stroke="blue" x1="10" y1="10" x2="9" y2="11"/>
  <line stroke="red" x1="10" y1="10" x2="11" y2="9"/>
  <line stroke="blue" x1="10" y1="10" x2="12" y2="10"/>
  <line stroke="blue" x1="2" y1="14" x2="4" y2="14"/>
  <line stroke="red" x1="2" y1="14" x2="3" y2="15"/>
  <line stroke="blue" x1="2" y1="14" x2="2" y2="16"/>
  <line stroke="red" x1="9" y1="11" x2="8" y2="12"/>
  <line stroke="red" x1="9" y1="11" x2="13" y2="11"/>
  <line stroke="blue" x1="11" y1="9" x2="12" y2="8"/>
  <line stroke="red" x1="11" y1="9" x2="13" y2="9"/>
  <line stroke="red" x1="8" y1="12" x2="7" y2="13"/>
  <line stroke="red" x1="8" y1="12" x2="9" y2="13"/>
  <line stroke="blue" x1="8" y1="12" x2="12" y2="12"/>
  <line stroke="blue" x1="8" y1="12" x2="8" y2="18"/>
  <line stroke="blue" x1="12" y1="8" x2="13" y2="9"/>
  <line stroke="blue" x1="4" y1="14" x2="6" y2="14"/>
  <line stroke="blue" x1="4" y1="14" x2="4" y2="15"/>
  <line stroke="blue" x1="7" y1="13" x2="6" y2="14"/>
  <line stroke="red" x1="7" y1="13" x2="7" y2="18"/>
  <line stroke="blue" x1="15" y1="1" x2="16" y2="0"/>
  <line stroke="red" x1="15" y1="1" x2="16" y2="2"/>
  <line stroke="red" x1="15" y1="1" x2="17" y2="1"/>
  <line stroke="red" x1="6" y1="14" x2="5" y2="15"/>
  <line stroke="blue" x1="6" y1="14" x2="6" y2="18"/>
  <line stroke="red" x1="14" y1="6" x2="15" y2="7"/>
  <line stroke="blue" x1="14" y1="6" x2="14" y2="9"/>
  <line stroke="blue" x1="14" y1="6" x2="16" y2="6"/>
  <line stroke="red" x1="3" y1="15" x2="4" y2="15"/>
  <line stroke="red" x1="3" y1="15" x2="3" y2="16"/>
  <line stroke="blue" x1="3" y1="15" x2="4" y2="16"/>
  <line stroke="blue" x1="15" y1="3" x2="16" y2="2"/>
  <line stroke="red" x1="15" y1="3" x2="16" y2="4"/>
  <line stroke="red" x1="15" y1="3" x2="17" y2="3"/>
  <line stroke="red" x1="4" y1="15" x2="5" y2="15"/>
  <line stroke="red" x1="4" y1="15" x2="4" y2="16"/>
  <line stroke="blue" x1="12" y1="10" x2="13" y2="9"/>
  <line stroke="red" x1="12" y1="10" x2="13" y2="10"/>
  <line stroke="blue" x1="12" y1="10" x2="13" y2="11"/>
  <line stroke="blue" x1="9" y1="13" x2="10" y2="14"/>
  <line stroke="red" x1="9" y1="13" x2="13" y2="13"/>
  <line stroke="red" x1="9" y1="13" x2="9" y2="18"/>
  <line stroke="red" x1="13" y1="9" x2="13" y2="10"/>
  <line stroke="red" x1="13" y1="9" x2="14" y2="9"/>
  <line stroke="blue" x1="5" y1="15" x2="4" y2="16"/>
  <line stroke="red" x1="5" y1="15" x2="5" y2="17"/>
  <line stroke="blue" x1="15" y1="5" x2="16" y2="4"/>
  <line stroke="red" x1="15" y1="5" x2="16" y2="6"/>
  <line stroke="red" x1="15" y1="5" x2="17" y2="5"/>
  <line stroke="blue" x1="0" y1="16" x2="1" y2="16"/>
  <line stroke="black" x1="0" y1="16" x2="0" y2="20"/>
  <line stroke="blue" x1="16" y1="0" x2="17" y2="1"/>
  <line stroke="black" x1="16" y1="0" x2="24" y2="0"/>
  <line stroke="red" x1="1" y1="16" x2="2" y2="16"/>
  <line stroke="red" x1="1" y1="16" x2="1" y2="19"/>
  <line stroke="red" x1="16" y1="2" x2="17" y2="1"/>
  <line stroke="blue" x1="16" y1="2" x2="17" y2="3"/>
  <line stroke="blue" x1="16" y1="2" x2="22" y2="2"/>
  <line stroke="blue" x1="2" y1="16" x2="3" y2="16"/>
  <line stroke="blue" x1="2" y1="16" x2="2" y2="18"/>
  <line stroke="red" x1="3" y1="16" x2="4" y2="16"/>
  <line stroke="red" x1="3" y1="16" x2="3" y2="17"/>
  <line stroke="red" x1="13" y1="10" x2="13" y2="11"/>
  <line stroke="blue" x1="13" y1="10" x2="14" y2="10"/>
  <line stroke="blue" x1="4" y1="16" x2="3" y2="17"/>
  <line stroke="blue" x1="4" y1="16" x2="5" y2="17"/>
  <line stroke="red" x1="16" y1="4" x2="17" y2="3"/>
  <line stroke="blue" x1="16" y1="4" x2="17" y2="5"/>
  <line stroke="blue" x1="16" y1="4" x2="20" y2="4"/>
  <line stroke="blue" x1="15" y1="7" x2="16" y2="6"/>
  <line stroke="red" x1="15" y1="7" x2="15" y2="9"/>
  <line stroke="red" x1="15" y1="7" x2="17" y2="7"/>
  <line stroke="blue" x1="14" y1="9" x2="14" y2="10"/>
  <line stroke="blue" x1="14" y1="9" x2="15" y2="9"/>
  <line stroke="blue" x1="12" y1="12" x2="13" y2="11"/>
  <line stroke="red" x1="12" y1="12" x2="13" y2="12"/>
  <line stroke="blue" x1="12" y1="12" x2="13" y2="13"/>
  <line stroke="red" x1="17" y1="1" x2="23" y2="1"/>
  <line stroke="red" x1="13" y1="11" x2="13" y2="12"/>
  <line stroke="red" x1="13" y1="11" x2="14" y2="11"/>
  <line stroke="red" x1="16" y1="6" x2="17" y2="5"/>
  <line stroke="blue" x1="16" y1="6" x2="17" y2="7"/>
  <line stroke="blue" x1="16" y1="6" x2="18" y2="6"/>
  <line stroke="blue" x1="10" y1="14" x2="12" y2="14"/>
  <line stroke="red" x1="10" y1="14" x2="11" y2="15"/>
  <line stroke="blue" x1="10" y1="14" x2="10" y2="18"/>
  <line stroke="blue" x1="14" y1="10" x2="14" y2="11"/>
  <line stroke="red" x1="14" y1="10" x2="15" y2="10"/>
  <line stroke="red" x1="3" y1="17" x2="5" y2="17"/>
  <line stroke="red" x1="3" y1="17" x2="2" y2="18"/>
  <line stroke="red" x1="17" y1="3" x2="21" y2="3"/>
  <line stroke="red" x1="15" y1="9" x2="15" y2="10"/>
  <line stroke="red" x1="15" y1="9" x2="17" y2="9"/>
  <line stroke="red" x1="13" y1="12" x2="13" y2="13"/>
  <line stroke="blue" x1="13" y1="12" x2="14" y2="12"/>
  <line stroke="red" x1="5" y1="17" x2="6" y2="18"/>
  <line stroke="red" x1="17" y1="5" x2="19" y2="5"/>
  <line stroke="blue" x1="14" y1="11" x2="14" y2="12"/>
  <line stroke="blue" x1="14" y1="11" x2="15" y2="11"/>
  <line stroke="red" x1="15" y1="10" x2="15" y2="11"/>
  <line stroke="blue" x1="15" y1="10" x2="17" y2="10"/>
  <line stroke="blue" x1="2" y1="18" x2="6" y2="18"/>
  <line stroke="blue" x1="2" y1="18" x2="1" y2="19"/>
  <line stroke="blue" x1="13" y1="13" x2="12" y2="14"/>
  <line stroke="red" x1="13" y1="13" x2="13" y2="14"/>
  <line stroke="red" x1="13" y1="13" x2="14" y2="13"/>
  <line stroke="red" x1="17" y1="7" x2="18" y2="6"/>
  <line stroke="red" x1="17" y1="7" x2="17" y2="9"/>
  <line stroke="red" x1="12" y1="14" x2="13" y2="14"/>
  <line stroke="blue" x1="12" y1="14" x2="13" y2="15"/>
  <line stroke="blue" x1="14" y1="12" x2="14" y2="13"/>
  <line stroke="red" x1="14" y1="12" x2="15" y2="12"/>
  <line stroke="red" x1="11" y1="15" x2="13" y2="15"/>
  <line stroke="blue" x1="11" y1="15" x2="12" y2="16"/>
  <line stroke="red" x1="11" y1="15" x2="11" y2="18"/>
  <line stroke="red" x1="15" y1="11" x2="15" y2="12"/>
  <line stroke="red" x1="15" y1="11" x2="17" y2="11"/>
  <line stroke="blue" x1="6" y1="18" x2="7" y2="18"/>
  <line stroke="red" x1="6" y1="18" x2="5" y2="19"/>
  <line stroke="blue" x1="6" y1="18" x2="6" y2="20"/>
  <line stroke="blue" x1="18" y1="6" x2="19" y2="5"/>
  <line stroke="blue" x1="18" y1="6" x2="18" y2="9"/>
  <line stroke="red" x1="1" y1="19" x2="5" y2="19"/>
  <line stroke="red" x1="1" y1="19" x2="0" y2="20"/>
  <line stroke="blue" x1="13" y1="14" x2="14" y2="14"/>
  <line stroke="red" x1="13" y1="14" x2="13" y2="15"/>
  <line stroke="blue" x1="14" y1="13" x2="14" y2="14"/>
  <line stroke="blue" x1="14" y1="13" x2="15" y2="13"/>
  <line stroke="red" x1="15" y1="12" x2="15" y2="13"/>
  <line stroke="blue" x1="15" y1="12" x2="17" y2="12"/>
  <line stroke="red" x1="17" y1="9" x2="17" y2="10"/>
  <line stroke="blue" x1="17" y1="9" x2="18" y2="9"/>
  <line stroke="red" x1="7" y1="18" x2="8" y2="18"/>
  <line stroke="red" x1="7" y1="18" x2="7" y2="20"/>
  <line stroke="blue" x1="5" y1="19" x2="4" y2="20"/>
  <line stroke="red" x1="5" y1="19" x2="5" y2="20"/>
  <line stroke="red" x1="19" y1="5" x2="20" y2="4"/>
  <line stroke="red" x1="19" y1="5" x2="19" y2="9"/>
  <line stroke="blue" x1="8" y1="18" x2="9" y2="18"/>
  <line stroke="blue" x1="8" y1="18" x2="8" y2="20"/>
  <line stroke="red" x1="17" y1="10" x2="17" y2="11"/>
  <line stroke="red" x1="17" y1="10" x2="18" y2="10"/>
  <line stroke="blue" x1="14" y1="14" x2="14" y2="15"/>
  <line stroke="red" x1="14" y1="14" x2="15" y2="14"/>
  <line stroke="blue" x1="13" y1="15" x2="12" y2="16"/>
  <line stroke="red" x1="13" y1="15" x2="14" y2="15"/>
  <line stroke="red" x1="13" y1="15" x2="13" y2="16"/>
  <line stroke="red" x1="15" y1="13" x2="15" y2="14"/>
  <line stroke="red" x1="15" y1="13" x2="17" y2="13"/>
  <line stroke="blue" x1="0" y1="20" x2="4" y2="20"/>
  <line stroke="red" x1="0" y1="20" x2="1" y2="21"/>
  <line stroke="black" x1="0" y1="20" x2="0" y2="24"/>
  <line stroke="red" x1="12" y1="16" x2="13" y2="16"/>
  <line stroke="blue" x1="12" y1="16" x2="12" y2="18"/>
  <line stroke="red" x1="9" y1="18" x2="10" y2="18"/>
  <line stroke="red" x1="9" y1="18" x2="9" y2="20"/>
  <line stroke="blue" x1="18" y1="9" x2="18" y2="10"/>
  <line stroke="red" x1="18" y1="9" x2="19" y2="9"/>
  <line stroke="red" x1="17" y1="11" x2="17" y2="12"/>
  <line stroke="blue" x1="17" y1="11" x2="18" y2="11"/>
  <line stroke="red" x1="4" y1="20" x2="5" y2="20"/>
  <line stroke="blue" x1="4" y1="20" x2="5" y2="21"/>
  <line stroke="blue" x1="20" y1="4" x2="21" y2="3"/>
  <line stroke="blue" x1="20" y1="4" x2="20" y2="8"/>
  <line stroke="blue" x1="14" y1="15" x2="15" y2="15"/>
  <line stroke="blue" x1="14" y1="15" x2="14" y2="16"/>
  <line stroke="red" x1="15" y1="14" x2="15" y2="15"/>
  <line stroke="blue" x1="15" y1="14" x2="17" y2="14"/>
  <line stroke="blue" x1="10" y1="18" x2="11" y2="18"/>
  <line stroke="blue" x1="10" y1="18" x2="10" y2="20"/>
  <line stroke="blue" x1="18" y1="10" x2="18" y2="11"/>
  <line stroke="blue" x1="18" y1="10" x2="19" y2="10"/>
  <line stroke="blue" x1="13" y1="16" x2="14" y2="16"/>
  <line stroke="red" x1="13" y1="16" x2="13" y2="18"/>
  <line stroke="blue" x1="5" y1="20" x2="6" y2="20"/>
  <line stroke="red" x1="5" y1="20" x2="5" y2="21"/>
  <line stroke="red" x1="17" y1="12" x2="17" y2="13"/>
  <line stroke="red" x1="17" y1="12" x2="18" y2="12"/>
  <line stroke="red" x1="6" y1="20" x2="7" y2="20"/>
  <line stroke="blue" x1="6" y1="20" x2="6" y2="22"/>
  <line stroke="red" x1="1" y1="21" x2="5" y2="21"/>
  <line stroke="blue" x1="1" y1="21" x2="2" y2="22"/>
  <line stroke="red" x1="1" y1="21" x2="1" y2="24"/>
  <line stroke="red" x1="19" y1="9" x2="19" y2="10"/>
  <line stroke="blue" x1="19" y1="9" x2="20" y2="8"/>
  <line stroke="blue" x1="19" y1="9" x2="20" y2="10"/>
  <line stroke="red" x1="19" y1="9" x2="21" y2="9"/>
  <line stroke="red" x1="11" y1="18" x2="12" y2="18"/>
  <line stroke="red" x1="11" y1="18" x2="11" y2="20"/>
  <line stroke="blue" x1="18" y1="11" x2="18" y2="12"/>
  <line stroke="red" x1="18" y1="11" x2="19" y2="11"/>
  <line stroke="blue" x1="7" y1="20" x2="8" y2="20"/>
  <line stroke="red" x1="7" y1="20" x2="7" y2="23"/>
  <line stroke="red" x1="21" y1="3" x2="22" y2="2"/>
  <line stroke="red" x1="21" y1="3" x2="21" y2="8"/>
  <line stroke="red" x1="15" y1="15" x2="15" y2="16"/>
  <line stroke="red" x1="15" y1="15" x2="17" y2="15"/>
  <line stroke="red" x1="14" y1="16" x2="15" y2="16"/>
  <line stroke="blue" x1="14" y1="16" x2="14" y2="18"/>
  <line stroke="red" x1="17" y1="13" x2="17" y2="14"/>
  <line stroke="blue" x1="17" y1="13" x2="18" y2="13"/>
  <line stroke="red" x1="19" y1="10" x2="19" y2="11"/>
  <line stroke="red" x1="19" y1="10" x2="20" y2="10"/>
  <line stroke="red" x1="8" y1="20" x2="9" y2="20"/>
  <line stroke="blue" x1="8" y1="20" x2="8" y2="24"/>
  <line stroke="red" x1="20" y1="8" x2="21" y2="8"/>
  <line stroke="blue" x1="20" y1="8" x2="21" y2="9"/>
  <line stroke="red" x1="5" y1="21" x2="6" y2="22"/>
  <line stroke="blue" x1="12" y1="18" x2="13" y2="18"/>
  <line stroke="blue" x1="12" y1="18" x2="12" y2="20"/>
  <line stroke="blue" x1="18" y1="12" x2="18" y2="13"/>
  <line stroke="blue" x1="18" y1="12" x2="19" y2="12"/>
  <line stroke="blue" x1="9" y1="20" x2="10" y2="20"/>
  <line stroke="red" x1="9" y1="20" x2="9" y2="25"/>
  <line stroke="blue" x1="15" y1="16" x2="17" y2="16"/>
  <line stroke="red" x1="15" y1="16" x2="15" y2="18"/>
  <line stroke="blue" x1="19" y1="11" x2="20" y2="10"/>
  <line stroke="red" x1="19" y1="11" x2="19" y2="12"/>
  <line stroke="blue" x1="19" y1="11" x2="20" y2="12"/>
  <line stroke="red" x1="19" y1="11" x2="23" y2="11"/>
  <line stroke="red" x1="17" y1="14" x2="17" y2="15"/>
  <line stroke="red" x1="17" y1="14" x2="18" y2="14"/>
  <line stroke="blue" x1="2" y1="22" x2="6" y2="22"/>
  <line stroke="red" x1="2" y1="22" x2="3" y2="23"/>
  <line stroke="blue" x1="2" y1="22" x2="2" y2="24"/>
  <line stroke="blue" x1="22" y1="2" x2="23" y2="1"/>
  <line stroke="blue" x1="22" y1="2" x2="22" y2="8"/>
  <line stroke="red" x1="13" y1="18" x2="14" y2="18"/>
  <line stroke="red" x1="13" y1="18" x2="13" y2="20"/>
  <line stroke="blue" x1="18" y1="13" x2="18" y2="14"/>
  <line stroke="red" x1="18" y1="13" x2="19" y2="13"/>
  <line stroke="red" x1="10" y1="20" x2="11" y2="20"/>
  <line stroke="blue" x1="10" y1="20" x2="10" y2="26"/>
  <line stroke="blue" x1="20" y1="10" x2="22" y2="10"/>
  <line stroke="red" x1="21" y1="8" x2="21" y2="9"/>
  <line stroke="blue" x1="21" y1="8" x2="22" y2="8"/>
  <line stroke="red" x1="19" y1="12" x2="19" y2="13"/>
  <line stroke="red" x1="19" y1="12" x2="20" y2="12"/>
  <line stroke="red" x1="17" y1="15" x2="17" y2="16"/>
  <line stroke="blue" x1="17" y1="15" x2="18" y2="15"/>
  <line stroke="blue" x1="14" y1="18" x2="15" y2="18"/>
  <line stroke="blue" x1="14" y1="18" x2="14" y2="20"/>
  <line stroke="blue" x1="18" y1="14" x2="18" y2="15"/>
  <line stroke="blue" x1="18" y1="14" x2="19" y2="14"/>
  <line stroke="blue" x1="6" y1="22" x2="7" y2="23"/>
  <line stroke="blue" x1="11" y1="20" x2="12" y2="20"/>
  <line stroke="red" x1="11" y1="20" x2="11" y2="27"/>
  <line stroke="red" x1="21" y1="9" x2="22" y2="10"/>
  <line stroke="blue" x1="19" y1="13" x2="20" y2="12"/>
  <line stroke="red" x1="19" y1="13" x2="19" y2="14"/>
  <line stroke="blue" x1="19" y1="13" x2="20" y2="14"/>
  <line stroke="red" x1="19" y1="13" x2="23" y2="13"/>
  <line stroke="red" x1="23" y1="1" x2="24" y2="0"/>
  <line stroke="red" x1="23" y1="1" x2="23" y2="8"/>
  <line stroke="red" x1="3" y1="23" x2="7" y2="23"/>
  <line stroke="red" x1="3" y1="23" x2="3" y2="24"/>
  <line stroke="blue" x1="3" y1="23" x2="4" y2="24"/>
  <line stroke="red" x1="12" y1="20" x2="13" y2="20"/>
  <line stroke="blue" x1="12" y1="20" x2="12" y2="28"/>
  <line stroke="blue" x1="20" y1="12" x2="24" y2="12"/>
  <line stroke="red" x1="17" y1="16" x2="18" y2="16"/>
  <line stroke="red" x1="17" y1="16" x2="17" y2="18"/>
  <line stroke="red" x1="15" y1="18" x2="17" y2="18"/>
  <line stroke="red" x1="15" y1="18" x2="15" y2="20"/>
  <line stroke="blue" x1="18" y1="15" x2="18" y2="16"/>
  <line stroke="red" x1="18" y1="15" x2="19" y2="15"/>
  <line stroke="blue" x1="22" y1="8" x2="22" y2="10"/>
  <line stroke="red" x1="22" y1="8" x2="23" y2="8"/>
  <line stroke="red" x1="19" y1="14" x2="19" y2="15"/>
  <line stroke="red" x1="19" y1="14" x2="20" y2="14"/>
  <line stroke="blue" x1="13" y1="20" x2="14" y2="20"/>
  <line stroke="red" x1="13" y1="20" x2="13" y2="29"/>
  <line stroke="blue" x1="0" y1="24" x2="1" y2="24"/>
  <line stroke="black" x1="0" y1="24" x2="0" y2="28"/>
  <line stroke="red" x1="24" y1="0" x2="25" y2="1"/>
  <line stroke="blue" x1="24" y1="0" x2="24" y2="8"/>
  <line stroke="black" x1="24" y1="0" x2="28" y2="0"/>
  <line stroke="red" x1="1" y1="24" x2="2" y2="24"/>
  <line stroke="red" x1="1" y1="24" x2="1" y2="27"/>
  <line stroke="red" x1="7" y1="23" x2="8" y2="24"/>
  <line stroke="blue" x1="18" y1="16" x2="19" y2="16"/>
  <line stroke="blue" x1="18" y1="16" x2="18" y2="18"/>
  <line stroke="blue" x1="2" y1="24" x2="3" y2="24"/>
  <line stroke="blue" x1="2" y1="24" x2="2" y2="26"/>
  <line stroke="blue" x1="22" y1="10" x2="23" y2="11"/>
  <line stroke="red" x1="3" y1="24" x2="4" y2="24"/>
  <line stroke="red" x1="3" y1="24" x2="3" y2="25"/>
  <line stroke="blue" x1="19" y1="15" x2="20" y2="14"/>
  <line stroke="red" x1="19" y1="15" x2="19" y2="16"/>
  <line stroke="blue" x1="19" y1="15" x2="20" y2="16"/>
  <line stroke="red" x1="19" y1="15" x2="21" y2="15"/>
  <line stroke="blue" x1="4" y1="24" x2="3" y2="25"/>
  <line stroke="blue" x1="4" y1="24" x2="8" y2="24"/>
  <line stroke="blue" x1="23" y1="8" x2="24" y2="8"/>
  <line stroke="red" x1="23" y1="8" x2="23" y2="11"/>
  <line stroke="red" x1="14" y1="20" x2="15" y2="20"/>
  <line stroke="blue" x1="14" y1="20" x2="14" y2="30"/>
  <line stroke="blue" x1="20" y1="14" x2="22" y2="14"/>
  <line stroke="blue" x1="17" y1="18" x2="18" y2="18"/>
  <line stroke="red" x1="17" y1="18" x2="17" y2="20"/>
  <line stroke="red" x1="19" y1="16" x2="20" y2="16"/>
  <line stroke="red" x1="19" y1="16" x2="19" y2="18"/>
  <line stroke="blue" x1="15" y1="20" x2="17" y2="20"/>
  <line stroke="red" x1="15" y1="20" x2="15" y2="31"/>
  <line stroke="blue" x1="25" y1="1" x2="26" y2="2"/>
  <line stroke="red" x1="25" y1="1" x2="25" y2="8"/>
  <line stroke="red" x1="25" y1="1" x2="28" y2="1"/>
  <line stroke="red" x1="3" y1="25" x2="2" y2="26"/>
  <line stroke="red" x1="3" y1="25" x2="9" y2="25"/>
  <line stroke="blue" x1="8" y1="24" x2="9" y2="25"/>
  <line stroke="red" x1="24" y1="8" x2="25" y2="8"/>
  <line stroke="blue" x1="24" y1="8" x2="24" y2="12"/>
  <line stroke="red" x1="18" y1="18" x2="19" y2="18"/>
  <line stroke="blue" x1="18" y1="18" x2="18" y2="20"/>
  <line stroke="red" x1="23" y1="11" x2="24" y2="12"/>
  <line stroke="blue" x1="20" y1="16" x2="21" y2="15"/>
  <line stroke="blue" x1="20" y1="16" x2="20" y2="18"/>
  <line stroke="red" x1="21" y1="15" x2="22" y2="14"/>
  <line stroke="red" x1="21" y1="15" x2="21" y2="18"/>
  <line stroke="blue" x1="2" y1="26" x2="1" y2="27"/>
  <line stroke="blue" x1="2" y1="26" x2="10" y2="26"/>
  <line stroke="red" x1="26" y1="2" x2="27" y2="3"/>
  <line stroke="blue" x1="26" y1="2" x2="26" y2="8"/>
  <line stroke="blue" x1="26" y1="2" x2="28" y2="2"/>
  <line stroke="blue" x1="22" y1="14" x2="23" y2="13"/>
  <line stroke="blue" x1="22" y1="14" x2="22" y2="18"/>
  <line stroke="blue" x1="19" y1="18" x2="20" y2="18"/>
  <line stroke="red" x1="19" y1="18" x2="19" y2="20"/>
  <line stroke="blue" x1="25" y1="8" x2="26" y2="8"/>
  <line stroke="red" x1="25" y1="8" x2="25" y2="11"/>
  <line stroke="red" x1="17" y1="20" x2="18" y2="20"/>
  <line stroke="red" x1="17" y1="20" x2="17" y2="31"/>
  <line stroke="red" x1="23" y1="13" x2="24" y2="12"/>
  <line stroke="red" x1="23" y1="13" x2="23" y2="18"/>
  <line stroke="red" x1="9" y1="25" x2="10" y2="26"/>
  <line stroke="red" x1="24" y1="12" x2="25" y2="11"/>
  <line stroke="red" x1="24" y1="12" x2="25" y2="13"/>
  <line stroke="blue" x1="24" y1="12" x2="24" y2="18"/>
  <line stroke="red" x1="24" y1="12" x2="28" y2="12"/>
  <line stroke="blue" x1="18" y1="20" x2="19" y2="20"/>
  <line stroke="blue" x1="18" y1="20" x2="18" y2="30"/>
  <line stroke="red" x1="20" y1="18" x2="21" y2="18"/>
  <line stroke="blue" x1="20" y1="18" x2="20" y2="20"/>
  <line stroke="red" x1="1" y1="27" x2="0" y2="28"/>
  <line stroke="red" x1="1" y1="27" x2="11" y2="27"/>
  <line stroke="red" x1="27" y1="3" x2="28" y2="3"/>
  <line stroke="red" x1="27" y1="3" x2="27" y2="8"/>
  <line stroke="blue" x1="27" y1="3" x2="28" y2="4"/>
  <line stroke="blue" x1="26" y1="8" x2="26" y2="10"/>
  <line stroke="red" x1="26" y1="8" x2="27" y2="8"/>
  <line stroke="blue" x1="25" y1="11" x2="26" y2="10"/>
  <line stroke="red" x1="25" y1="11" x2="28" y2="11"/>
  <line stroke="red" x1="19" y1="20" x2="20" y2="20"/>
  <line stroke="red" x1="19" y1="20" x2="19" y2="29"/>
  <line stroke="blue" x1="21" y1="18" x2="22" y2="18"/>
  <line stroke="red" x1="21" y1="18" x2="21" y2="20"/>
  <line stroke="blue" x1="10" y1="26" x2="11" y2="27"/>
  <line stroke="red" x1="26" y1="10" x2="27" y2="9"/>
  <line stroke="blue" x1="26" y1="10" x2="28" y2="10"/>
  <line stroke="red" x1="0" y1="28" x2="1" y2="29"/>
  <line stroke="blue" x1="0" y1="28" x2="12" y2="28"/>
  <line stroke="black" x1="0" y1="28" x2="0" y2="32"/>
  <line stroke="blue" x1="28" y1="0" x2="28" y2="1"/>
  <line stroke="black" x1="28" y1="0" x2="32" y2="0"/>
  <line stroke="red" x1="28" y1="1" x2="28" y2="2"/>
  <line stroke="red" x1="28" y1="1" x2="31" y2="1"/>
  <line stroke="blue" x1="28" y1="2" x2="28" y2="3"/>
  <line stroke="blue" x1="28" y1="2" x2="30" y2="2"/>
  <line stroke="red" x1="28" y1="3" x2="28" y2="4"/>
  <line stroke="red" x1="28" y1="3" x2="29" y2="3"/>
  <line stroke="blue" x1="25" y1="13" x2="26" y2="14"/>
  <line stroke="red" x1="25" y1="13" x2="25" y2="18"/>
  <line stroke="red" x1="25" y1="13" x2="28" y2="13"/>
  <line stroke="red" x1="27" y1="8" x2="27" y2="9"/>
  <line stroke="blue" x1="27" y1="8" x2="28" y2="8"/>
  <line stroke="blue" x1="20" y1="20" x2="21" y2="20"/>
  <line stroke="blue" x1="20" y1="20" x2="20" y2="28"/>
  <line stroke="blue" x1="28" y1="4" x2="28" y2="8"/>
  <line stroke="blue" x1="28" y1="4" x2="29" y2="3"/>
  <line stroke="red" x1="22" y1="18" x2="23" y2="18"/>
  <line stroke="blue" x1="22" y1="18" x2="22" y2="20"/>
  <line stroke="blue" x1="27" y1="9" x2="28" y2="8"/>
  <line stroke="red" x1="27" y1="9" x2="28" y2="9"/>
  <line stroke="red" x1="21" y1="20" x2="22" y2="20"/>
  <line stroke="red" x1="21" y1="20" x2="21" y2="27"/>
  <line stroke="blue" x1="1" y1="29" x2="2" y2="30"/>
  <line stroke="red" x1="1" y1="29" x2="13" y2="29"/>
  <line stroke="red" x1="1" y1="29" x2="1" y2="32"/>
  <line stroke="red" x1="28" y1="8" x2="28" y2="9"/>
  <line stroke="red" x1="28" y1="8" x2="29" y2="8"/>
  <line stroke="blue" x1="28" y1="8" x2="29" y2="9"/>
  <line stroke="red" x1="29" y1="3" x2="29" y2="8"/>
  <line stroke="red" x1="29" y1="3" x2="30" y2="2"/>
  <line stroke="red" x1="11" y1="27" x2="12" y2="28"/>
  <line stroke="blue" x1="23" y1="18" x2="24" y2="18"/>
  <line stroke="red" x1="23" y1="18" x2="23" y2="20"/>
  <line stroke="blue" x1="28" y1="9" x2="28" y2="10"/>
  <line stroke="red" x1="28" y1="9" x2="29" y2="9"/>
  <line stroke="red" x1="26" y1="14" x2="27" y2="15"/>
  <line stroke="blue" x1="26" y1="14" x2="28" y2="14"/>
  <line stroke="blue" x1="26" y1="14" x2="26" y2="18"/>
  <line stroke="red" x1="28" y1="10" x2="28" y2="11"/>
  <line stroke="blue" x1="28" y1="10" x2="30" y2="10"/>
  <line stroke="blue" x1="22" y1="20" x2="23" y2="20"/>
  <line stroke="blue" x1="22" y1="20" x2="22" y2="26"/>
  <line stroke="red" x1="24" y1="18" x2="25" y2="18"/>
  <line stroke="blue" x1="24" y1="18" x2="24" y2="20"/>
  <line stroke="red" x1="29" y1="8" x2="29" y2="9"/>
  <line stroke="blue" x1="29" y1="8" x2="30" y2="8"/>
  <line stroke="red" x1="2" y1="30" x2="3" y2="31"/>
  <line stroke="blue" x1="2" y1="30" x2="2" y2="32"/>
  <line stroke="blue" x1="2" y1="30" x2="14" y2="30"/>
  <line stroke="blue" x1="30" y1="2" x2="31" y2="1"/>
  <line stroke="blue" x1="30" y1="2" x2="30" y2="8"/>
  <line stroke="blue" x1="28" y1="11" x2="28" y2="12"/>
  <line stroke="red" x1="28" y1="11" x2="31" y2="11"/>
  <line stroke="red" x1="29" y1="9" x2="30" y2="10"/>
  <line stroke="blue" x1="12" y1="28" x2="13" y2="29"/>
  <line stroke="blue" x1="28" y1="12" x2="28" y2="13"/>
  <line stroke="blue" x1="28" y1="12" x2="32" y2="12"/>
  <line stroke="red" x1="23" y1="20" x2="24" y2="20"/>
  <line stroke="red" x1="23" y1="20" x2="23" y2="25"/>
  <line stroke="blue" x1="25" y1="18" x2="26" y2="18"/>
  <line stroke="red" x1="25" y1="18" x2="25" y2="20"/>
  <line stroke="red" x1="28" y1="13" x2="28" y2="14"/>
  <line stroke="red" x1="28" y1="13" x2="31" y2="13"/>
  <line stroke="red" x1="27" y1="15" x2="28" y2="15"/>
  <line stroke="red" x1="27" y1="15" x2="27" y2="17"/>
  <line stroke="blue" x1="27" y1="15" x2="28" y2="16"/>
  <line stroke="red" x1="31" y1="1" x2="32" y2="0"/>
  <line stroke="red" x1="31" y1="1" x2="31" y2="8"/>
  <line stroke="blue" x1="30" y1="8" x2="30" y2="10"/>
  <line stroke="red" x1="30" y1="8" x2="31" y2="8"/>
  <line stroke="red" x1="3" y1="31" x2="3" y2="32"/>
  <line stroke="blue" x1="3" y1="31" x2="4" y2="32"/>
  <line stroke="red" x1="3" y1="31" x2="15" y2="31"/>
  <line stroke="blue" x1="24" y1="20" x2="25" y2="20"/>
  <line stroke="blue" x1="24" y1="20" x2="24" y2="24"/>
  <line stroke="blue" x1="28" y1="14" x2="28" y2="15"/>
  <line stroke="blue" x1="28" y1="14" x2="30" y2="14"/>
  <line stroke="red" x1="26" y1="18" x2="27" y2="17"/>
  <line stroke="blue" x1="26" y1="18" x2="26" y2="20"/>
  <line stroke="red" x1="26" y1="18" x2="27" y2="19"/>
  <line stroke="blue" x1="26" y1="18" x2="30" y2="18"/>
  <line stroke="blue" x1="30" y1="10" x2="31" y2="11"/>
  <line stroke="red" x1="28" y1="15" x2="28" y2="16"/>
  <line stroke="red" x1="28" y1="15" x2="29" y2="15"/>
  <line stroke="red" x1="13" y1="29" x2="14" y2="30"/>
  <line stroke="blue" x1="27" y1="17" x2="28" y2="16"/>
  <line stroke="red" x1="27" y1="17" x2="29" y2="17"/>
  <line stroke="black" x1="0" y1="32" x2="1" y2="32"/>
  <line stroke="black" x1="32" y1="0" x2="32" y2="8"/>
  <line stroke="red" x1="25" y1="20" x2="26" y2="20"/>
  <line stroke="red" x1="25" y1="20" x2="25" y2="23"/>
  <line stroke="black" x1="1" y1="32" x2="2" y2="32"/>
  <line stroke="red" x1="31" y1="8" x2="31" y2="11"/>
  <line stroke="blue" x1="31" y1="8" x2="32" y2="8"/>
  <line stroke="black" x1="2" y1="32" x2="3" y2="32"/>
  <line stroke="black" x1="3" y1="32" x2="4" y2="32"/>
  <line stroke="black" x1="4" y1="32" x2="16" y2="32"/>
  <line stroke="blue" x1="28" y1="16" x2="29" y2="15"/>
  <line stroke="red" x1="28" y1="16" x2="29" y2="16"/>
  <line stroke="blue" x1="28" y1="16" x2="29" y2="17"/>
  <line stroke="red" x1="29" y1="15" x2="29" y2="16"/>
  <line stroke="red" x1="29" y1="15" x2="30" y2="14"/>
  <line stroke="blue" x1="26" y1="20" x2="27" y2="20"/>
  <line stroke="blue" x1="26" y1="20" x2="26" y2="22"/>
  <line stroke="red" x1="31" y1="11" x2="32" y2="12"/>
  <line stroke="black" x1="32" y1="8" x2="32" y2="12"/>
  <line stroke="red" x1="27" y1="19" x2="27" y2="20"/>
  <line stroke="blue" x1="27" y1="19" x2="28" y2="20"/>
  <line stroke="red" x1="27" y1="19" x2="31" y2="19"/>
  <line stroke="red" x1="29" y1="16" x2="29" y2="17"/>
  <line stroke="blue" x1="29" y1="16" x2="30" y2="16"/>
  <line stroke="blue" x1="14" y1="30" x2="15" y2="31"/>
  <line stroke="blue" x1="30" y1="14" x2="31" y2="13"/>
  <line stroke="blue" x1="30" y1="14" x2="30" y2="16"/>
  <line stroke="red" x1="29" y1="17" x2="30" y2="18"/>
  <line stroke="red" x1="27" y1="20" x2="27" y2="21"/>
  <line stroke="red" x1="27" y1="20" x2="28" y2="20"/>
  <line stroke="red" x1="31" y1="13" x2="32" y2="12"/>
  <line stroke="red" x1="31" y1="13" x2="31" y2="16"/>
  <line stroke="blue" x1="24" y1="24" x2="23" y2="25"/>
  <line stroke="red" x1="24" y1="24" x2="25" y2="23"/>
  <line stroke="blue" x1="24" y1="24" x2="28" y2="24"/>
  <line stroke="red" x1="23" y1="25" x2="22" y2="26"/>
  <line stroke="red" x1="23" y1="25" x2="29" y2="25"/>
  <line stroke="blue" x1="25" y1="23" x2="26" y2="22"/>
  <line stroke="red" x1="25" y1="23" x2="29" y2="23"/>
  <line stroke="red" x1="30" y1="16" x2="31" y2="16"/>
  <line stroke="blue" x1="30" y1="16" x2="30" y2="18"/>
  <line stroke="blue" x1="22" y1="26" x2="21" y2="27"/>
  <line stroke="blue" x1="22" y1="26" x2="30" y2="26"/>
  <line stroke="red" x1="26" y1="22" x2="27" y2="21"/>
  <line stroke="blue" x1="26" y1="22" x2="30" y2="22"/>
  <line stroke="black" x1="32" y1="12" x2="32" y2="16"/>
  <line stroke="red" x1="21" y1="27" x2="20" y2="28"/>
  <line stroke="red" x1="21" y1="27" x2="31" y2="27"/>
  <line stroke="blue" x1="27" y1="21" x2="28" y2="20"/>
  <line stroke="red" x1="27" y1="21" x2="31" y2="21"/>
  <line stroke="blue" x1="20" y1="28" x2="19" y2="29"/>
  <line stroke="blue" x1="20" y1="28" x2="32" y2="28"/>
  <line stroke="blue" x1="28" y1="20" x2="32" y2="20"/>
  <line stroke="red" x1="15" y1="31" x2="16" y2="32"/>
  <line stroke="red" x1="19" y1="29" x2="18" y2="30"/>
  <line stroke="red" x1="19" y1="29" x2="31" y2="29"/>
  <line stroke="blue" x1="31" y1="16" x2="32" y2="16"/>
  <line stroke="red" x1="31" y1="16" x2="31" y2="19"/>
  <line stroke="blue" x1="18" y1="30" x2="17" y2="31"/>
  <line stroke="blue" x1="18" y1="30" x2="30" y2="30"/>
  <line stroke="blue" x1="30" y1="18" x2="31" y2="19"/>
  <line stroke="red" x1="17" y1="31" x2="16" y2="32"/>
  <line stroke="red" x1="17" y1="31" x2="29" y2="31"/>
  <line stroke="black" x1="16" y1="32" x2="28" y2="32"/>
  <line stroke="black" x1="32" y1="16" x2="32" y2="20"/>
  <line stroke="red" x1="31" y1="19" x2="32" y2="20"/>
  <line stroke="blue" x1="28" y1="24" x2="29" y2="23"/>
  <line stroke="red" x1="28" y1="24" x2="29" y2="24"/>
  <line stroke="blue" x1="28" y1="24" x2="29" y2="25"/>
  <line stroke="red" x1="29" y1="23" x2="30" y2="22"/>
  <line stroke="red" x1="29" y1="23" x2="29" y2="24"/>
  <line stroke="blue" x1="30" y1="22" x2="31" y2="21"/>
  <line stroke="blue" x1="30" y1="22" x2="30" y2="24"/>
  <line stroke="red" x1="31" y1="21" x2="32" y2="20"/>
  <line stroke="red" x1="31" y1="21" x2="31" y2="24"/>
  <line stroke="red" x1="29" y1="24" x2="29" y2="25"/>
  <line stroke="blue" x1="29" y1="24" x2="30" y2="24"/>
  <line stroke="black" x1="32" y1="20" x2="32" y2="24"/>
  <line stroke="red" x1="29" y1="25" x2="30" y2="26"/>
  <line stroke="red" x1="30" y1="24" x2="31" y2="24"/>
  <line stroke="blue" x1="30" y1="24" x2="30" y2="26"/>
  <line stroke="blue" x1="31" y1="24" x2="32" y2="24"/>
  <line stroke="red" x1="31" y1="24" x2="31" y2="27"/>
  <line stroke="blue" x1="30" y1="26" x2="31" y2="27"/>
  <line stroke="black" x1="32" y1="24" x2="32" y2="28"/>
  <line stroke="red" x1="31" y1="27" x2="32" y2="28"/>
  <line stroke="red" x1="30" y1="30" x2="29" y2="31"/>
  <line stroke="blue" x1="30" y1="30" x2="31" y2="29"/>
  <line stroke="blue" x1="30" y1="30" x2="30" y2="32"/>
  <line stroke="blue" x1="29" y1="31" x2="28" y2="32"/>
  <line stroke="red" x1="29" y1="31" x2="29" y2="32"/>
  <line stroke="red" x1="31" y1="29" x2="32" y2="28"/>
  <line stroke="red" x1="31" y1="29" x2="31" y2="32"/>
  <line stroke="black" x1="28" y1="32" x2="29" y2="32"/>
  <line stroke="black" x1="32" y1="28" x2="32" y2="32"/>
  <line stroke="black" x1="29" y1="32" x2="30" y2="32"/>
  <line stroke="black" x1="30" y1="32" x2="31" y2="32"/>
  <line stroke="black" x1="31" y1="32" x2="32" y2="32"/>
</svg>""",
)

SCORPION_WITH_ELEVATION = BoxPleatingCreasePatternExample(
    name="scorpion_with_elevation",
    grid_size=32,
    central_crease_removed=True,
    packing_svg=SCORPION.packing_svg,
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <line stroke="red" x1="0" y1="0" x2="1" y2="1"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="4"/>
  <line stroke="black" x1="0" y1="0" x2="8" y2="0"/>
  <line stroke="blue" x1="1" y1="1" x2="2" y2="2"/>
  <line stroke="red" x1="1" y1="1" x2="1" y2="4" elevation="1"/>
  <line stroke="red" x1="1" y1="1" x2="7" y2="1" elevation="1"/>
  <line stroke="red" x1="2" y1="2" x2="3" y2="3"/>
  <line stroke="blue" x1="2" y1="2" x2="2" y2="4" elevation="0"/>
  <line stroke="blue" x1="2" y1="2" x2="6" y2="2" elevation="0"/>
  <line stroke="blue" x1="0" y1="4" x2="1" y2="4"/>
  <line stroke="black" x1="0" y1="4" x2="0" y2="8"/>
  <line stroke="red" x1="1" y1="4" x2="2" y2="4"/>
  <line stroke="red" x1="1" y1="4" x2="1" y2="8" elevation="1"/>
  <line stroke="red" x1="3" y1="3" x2="3" y2="4" elevation="1"/>
  <line stroke="blue" x1="3" y1="3" x2="4" y2="4"/>
  <line stroke="red" x1="3" y1="3" x2="5" y2="3" elevation="1"/>
  <line stroke="blue" x1="2" y1="4" x2="3" y2="4"/>
  <line stroke="blue" x1="2" y1="4" x2="2" y2="8" elevation="0"/>
  <line stroke="red" x1="3" y1="4" x2="4" y2="4"/>
  <line stroke="red" x1="3" y1="4" x2="3" y2="8" elevation="1"/>
  <line stroke="blue" x1="4" y1="4" x2="5" y2="3"/>
  <line stroke="blue" x1="4" y1="4" x2="4" y2="8" elevation="0"/>
  <line stroke="red" x1="5" y1="3" x2="6" y2="2"/>
  <line stroke="red" x1="5" y1="3" x2="5" y2="8" elevation="1"/>
  <line stroke="blue" x1="6" y1="2" x2="7" y2="1"/>
  <line stroke="blue" x1="6" y1="2" x2="6" y2="8" elevation="0"/>
  <line stroke="red" x1="7" y1="1" x2="8" y2="0"/>
  <line stroke="red" x1="7" y1="1" x2="7" y2="8" elevation="1"/>
  <line stroke="blue" x1="0" y1="8" x2="1" y2="8"/>
  <line stroke="black" x1="0" y1="8" x2="0" y2="12"/>
  <line stroke="red" x1="8" y1="0" x2="9" y2="1"/>
  <line stroke="blue" x1="8" y1="0" x2="8" y2="8" elevation="0"/>
  <line stroke="black" x1="8" y1="0" x2="16" y2="0"/>
  <line stroke="red" x1="1" y1="8" x2="2" y2="8"/>
  <line stroke="red" x1="1" y1="8" x2="1" y2="11" elevation="1"/>
  <line stroke="blue" x1="2" y1="8" x2="3" y2="8"/>
  <line stroke="blue" x1="2" y1="8" x2="2" y2="10" elevation="0"/>
  <line stroke="red" x1="3" y1="8" x2="4" y2="8"/>
  <line stroke="red" x1="3" y1="8" x2="3" y2="9" elevation="1"/>
  <line stroke="red" x1="4" y1="8" x2="5" y2="8"/>
  <line stroke="blue" x1="4" y1="8" x2="3" y2="9"/>
  <line stroke="blue" x1="4" y1="8" x2="4" y2="9"/>
  <line stroke="blue" x1="4" y1="8" x2="5" y2="9"/>
  <line stroke="blue" x1="9" y1="1" x2="10" y2="2"/>
  <line stroke="red" x1="9" y1="1" x2="9" y2="8" elevation="1"/>
  <line stroke="red" x1="9" y1="1" x2="15" y2="1" elevation="1"/>
  <line stroke="blue" x1="5" y1="8" x2="6" y2="8"/>
  <line stroke="red" x1="5" y1="8" x2="5" y2="9" elevation="1"/>
  <line stroke="red" x1="3" y1="9" x2="4" y2="9" elevation="1"/>
  <line stroke="red" x1="3" y1="9" x2="2" y2="10"/>
  <line stroke="red" x1="4" y1="9" x2="5" y2="9" elevation="1"/>
  <line stroke="red" x1="4" y1="9" x2="4" y2="10"/>
  <line stroke="red" x1="6" y1="8" x2="7" y2="8"/>
  <line stroke="blue" x1="6" y1="8" x2="6" y2="10" elevation="0"/>
  <line stroke="blue" x1="2" y1="10" x2="4" y2="10" elevation="0"/>
  <line stroke="blue" x1="2" y1="10" x2="1" y2="11"/>
  <line stroke="red" x1="10" y1="2" x2="11" y2="3"/>
  <line stroke="blue" x1="10" y1="2" x2="10" y2="8" elevation="0"/>
  <line stroke="blue" x1="10" y1="2" x2="16" y2="2" elevation="0"/>
  <line stroke="red" x1="5" y1="9" x2="6" y2="10"/>
  <line stroke="blue" x1="7" y1="8" x2="8" y2="8"/>
  <line stroke="red" x1="7" y1="8" x2="7" y2="11" elevation="1"/>
  <line stroke="blue" x1="4" y1="10" x2="6" y2="10" elevation="0"/>
  <line stroke="blue" x1="4" y1="10" x2="4" y2="11"/>
  <line stroke="red" x1="1" y1="11" x2="4" y2="11" elevation="1"/>
  <line stroke="red" x1="1" y1="11" x2="0" y2="12"/>
  <line stroke="blue" x1="8" y1="8" x2="9" y2="8"/>
  <line stroke="red" x1="8" y1="8" x2="8" y2="12" elevation="0"/>
  <line stroke="blue" x1="11" y1="3" x2="12" y2="4"/>
  <line stroke="red" x1="11" y1="3" x2="11" y2="8" elevation="1"/>
  <line stroke="red" x1="11" y1="3" x2="15" y2="3" elevation="1"/>
  <line stroke="blue" x1="6" y1="10" x2="7" y2="11"/>
  <line stroke="red" x1="4" y1="11" x2="4" y2="12"/>
  <line stroke="red" x1="4" y1="11" x2="7" y2="11" elevation="1"/>
  <line stroke="blue" x1="0" y1="12" x2="4" y2="12" elevation="0"/>
  <line stroke="red" x1="0" y1="12" x2="1" y2="13"/>
  <line stroke="black" x1="0" y1="12" x2="0" y2="16"/>
  <line stroke="red" x1="9" y1="8" x2="10" y2="8"/>
  <line stroke="red" x1="9" y1="8" x2="9" y2="11" elevation="1"/>
  <line stroke="blue" x1="4" y1="12" x2="4" y2="13"/>
  <line stroke="blue" x1="4" y1="12" x2="8" y2="12" elevation="0"/>
  <line stroke="red" x1="12" y1="4" x2="13" y2="5"/>
  <line stroke="blue" x1="12" y1="4" x2="12" y2="8" elevation="0"/>
  <line stroke="blue" x1="12" y1="4" x2="16" y2="4" elevation="0"/>
  <line stroke="blue" x1="10" y1="8" x2="11" y2="8"/>
  <line stroke="blue" x1="10" y1="8" x2="10" y2="10" elevation="0"/>
  <line stroke="red" x1="1" y1="13" x2="4" y2="13" elevation="1"/>
  <line stroke="blue" x1="1" y1="13" x2="2" y2="14"/>
  <line stroke="red" x1="1" y1="13" x2="1" y2="16" elevation="1"/>
  <line stroke="red" x1="7" y1="11" x2="8" y2="12"/>
  <line stroke="red" x1="4" y1="13" x2="4" y2="14"/>
  <line stroke="red" x1="4" y1="13" x2="7" y2="13" elevation="1"/>
  <line stroke="red" x1="11" y1="8" x2="11" y2="9" elevation="1"/>
  <line stroke="red" x1="11" y1="8" x2="12" y2="8"/>
  <line stroke="blue" x1="13" y1="5" x2="14" y2="6"/>
  <line stroke="red" x1="13" y1="5" x2="13" y2="9" elevation="1"/>
  <line stroke="red" x1="13" y1="5" x2="15" y2="5" elevation="1"/>
  <line stroke="blue" x1="2" y1="14" x2="4" y2="14" elevation="0"/>
  <line stroke="red" x1="2" y1="14" x2="3" y2="15"/>
  <line stroke="blue" x1="2" y1="14" x2="2" y2="16" elevation="0"/>
  <line stroke="blue" x1="10" y1="10" x2="9" y2="11"/>
  <line stroke="red" x1="10" y1="10" x2="11" y2="9"/>
  <line stroke="blue" x1="10" y1="10" x2="12" y2="10" elevation="0"/>
  <line stroke="red" x1="9" y1="11" x2="8" y2="12"/>
  <line stroke="red" x1="9" y1="11" x2="13" y2="11" elevation="1"/>
  <line stroke="blue" x1="11" y1="9" x2="12" y2="8"/>
  <line stroke="red" x1="11" y1="9" x2="13" y2="9" elevation="1"/>
  <line stroke="red" x1="8" y1="12" x2="7" y2="13"/>
  <line stroke="red" x1="8" y1="12" x2="9" y2="13"/>
  <line stroke="blue" x1="8" y1="12" x2="12" y2="12" elevation="0"/>
  <line stroke="blue" x1="8" y1="12" x2="8" y2="18" elevation="0"/>
  <line stroke="blue" x1="12" y1="8" x2="13" y2="9"/>
  <line stroke="blue" x1="4" y1="14" x2="6" y2="14" elevation="0"/>
  <line stroke="blue" x1="4" y1="14" x2="4" y2="15"/>
  <line stroke="blue" x1="7" y1="13" x2="6" y2="14"/>
  <line stroke="red" x1="7" y1="13" x2="7" y2="18" elevation="1"/>
  <line stroke="blue" x1="15" y1="1" x2="16" y2="0"/>
  <line stroke="red" x1="15" y1="1" x2="16" y2="2"/>
  <line stroke="red" x1="15" y1="1" x2="17" y2="1" elevation="1"/>
  <line stroke="red" x1="6" y1="14" x2="5" y2="15"/>
  <line stroke="blue" x1="6" y1="14" x2="6" y2="18" elevation="0"/>
  <line stroke="red" x1="14" y1="6" x2="15" y2="7"/>
  <line stroke="blue" x1="14" y1="6" x2="14" y2="9" elevation="0"/>
  <line stroke="blue" x1="14" y1="6" x2="16" y2="6" elevation="0"/>
  <line stroke="red" x1="3" y1="15" x2="4" y2="15" elevation="1"/>
  <line stroke="red" x1="3" y1="15" x2="3" y2="16" elevation="1"/>
  <line stroke="blue" x1="3" y1="15" x2="4" y2="16"/>
  <line stroke="blue" x1="15" y1="3" x2="16" y2="2"/>
  <line stroke="red" x1="15" y1="3" x2="16" y2="4"/>
  <line stroke="red" x1="15" y1="3" x2="17" y2="3" elevation="1"/>
  <line stroke="red" x1="4" y1="15" x2="5" y2="15" elevation="1"/>
  <line stroke="red" x1="4" y1="15" x2="4" y2="16"/>
  <line stroke="blue" x1="12" y1="10" x2="13" y2="9"/>
  <line stroke="red" x1="12" y1="10" x2="13" y2="10"/>
  <line stroke="blue" x1="12" y1="10" x2="13" y2="11"/>
  <line stroke="blue" x1="5" y1="15" x2="4" y2="16"/>
  <line stroke="red" x1="5" y1="15" x2="5" y2="17" elevation="1"/>
  <line stroke="blue" x1="9" y1="13" x2="10" y2="14"/>
  <line stroke="red" x1="9" y1="13" x2="13" y2="13" elevation="1"/>
  <line stroke="red" x1="9" y1="13" x2="9" y2="18" elevation="1"/>
  <line stroke="red" x1="13" y1="9" x2="13" y2="10" elevation="1"/>
  <line stroke="red" x1="13" y1="9" x2="14" y2="9"/>
  <line stroke="blue" x1="15" y1="5" x2="16" y2="4"/>
  <line stroke="red" x1="15" y1="5" x2="16" y2="6"/>
  <line stroke="red" x1="15" y1="5" x2="17" y2="5" elevation="1"/>
  <line stroke="blue" x1="0" y1="16" x2="1" y2="16"/>
  <line stroke="black" x1="0" y1="16" x2="0" y2="20"/>
  <line stroke="blue" x1="16" y1="0" x2="17" y2="1"/>
  <line stroke="black" x1="16" y1="0" x2="24" y2="0"/>
  <line stroke="red" x1="1" y1="16" x2="2" y2="16"/>
  <line stroke="red" x1="1" y1="16" x2="1" y2="19" elevation="1"/>
  <line stroke="blue" x1="2" y1="16" x2="3" y2="16"/>
  <line stroke="blue" x1="2" y1="16" x2="2" y2="18" elevation="0"/>
  <line stroke="red" x1="16" y1="2" x2="17" y2="1"/>
  <line stroke="blue" x1="16" y1="2" x2="17" y2="3"/>
  <line stroke="blue" x1="16" y1="2" x2="22" y2="2" elevation="0"/>
  <line stroke="red" x1="3" y1="16" x2="4" y2="16"/>
  <line stroke="red" x1="3" y1="16" x2="3" y2="17" elevation="1"/>
  <line stroke="red" x1="13" y1="10" x2="13" y2="11" elevation="1"/>
  <line stroke="blue" x1="13" y1="10" x2="14" y2="10"/>
  <line stroke="blue" x1="4" y1="16" x2="3" y2="17"/>
  <line stroke="blue" x1="4" y1="16" x2="5" y2="17"/>
  <line stroke="red" x1="16" y1="4" x2="17" y2="3"/>
  <line stroke="blue" x1="16" y1="4" x2="17" y2="5"/>
  <line stroke="blue" x1="16" y1="4" x2="20" y2="4" elevation="0"/>
  <line stroke="blue" x1="15" y1="7" x2="16" y2="6"/>
  <line stroke="red" x1="15" y1="7" x2="15" y2="9" elevation="1"/>
  <line stroke="red" x1="15" y1="7" x2="17" y2="7" elevation="1"/>
  <line stroke="blue" x1="14" y1="9" x2="14" y2="10" elevation="0"/>
  <line stroke="blue" x1="14" y1="9" x2="15" y2="9"/>
  <line stroke="blue" x1="12" y1="12" x2="13" y2="11"/>
  <line stroke="red" x1="12" y1="12" x2="13" y2="12"/>
  <line stroke="blue" x1="12" y1="12" x2="13" y2="13"/>
  <line stroke="red" x1="13" y1="11" x2="13" y2="12" elevation="1"/>
  <line stroke="red" x1="13" y1="11" x2="14" y2="11"/>
  <line stroke="red" x1="17" y1="1" x2="23" y2="1" elevation="1"/>
  <line stroke="red" x1="16" y1="6" x2="17" y2="5"/>
  <line stroke="blue" x1="16" y1="6" x2="17" y2="7"/>
  <line stroke="blue" x1="16" y1="6" x2="18" y2="6" elevation="0"/>
  <line stroke="blue" x1="10" y1="14" x2="12" y2="14" elevation="0"/>
  <line stroke="red" x1="10" y1="14" x2="11" y2="15"/>
  <line stroke="blue" x1="10" y1="14" x2="10" y2="18" elevation="0"/>
  <line stroke="blue" x1="14" y1="10" x2="14" y2="11" elevation="0"/>
  <line stroke="red" x1="14" y1="10" x2="15" y2="10"/>
  <line stroke="red" x1="3" y1="17" x2="5" y2="17" elevation="1"/>
  <line stroke="red" x1="3" y1="17" x2="2" y2="18"/>
  <line stroke="red" x1="17" y1="3" x2="21" y2="3" elevation="1"/>
  <line stroke="red" x1="15" y1="9" x2="15" y2="10" elevation="1"/>
  <line stroke="red" x1="15" y1="9" x2="17" y2="9"/>
  <line stroke="red" x1="13" y1="12" x2="13" y2="13" elevation="1"/>
  <line stroke="blue" x1="13" y1="12" x2="14" y2="12"/>
  <line stroke="red" x1="5" y1="17" x2="6" y2="18"/>
  <line stroke="red" x1="17" y1="5" x2="19" y2="5" elevation="1"/>
  <line stroke="blue" x1="14" y1="11" x2="14" y2="12" elevation="0"/>
  <line stroke="blue" x1="14" y1="11" x2="15" y2="11"/>
  <line stroke="red" x1="15" y1="10" x2="15" y2="11" elevation="1"/>
  <line stroke="blue" x1="15" y1="10" x2="17" y2="10"/>
  <line stroke="blue" x1="2" y1="18" x2="6" y2="18" elevation="0"/>
  <line stroke="blue" x1="2" y1="18" x2="1" y2="19"/>
  <line stroke="blue" x1="13" y1="13" x2="12" y2="14"/>
  <line stroke="red" x1="13" y1="13" x2="13" y2="14" elevation="1"/>
  <line stroke="red" x1="13" y1="13" x2="14" y2="13"/>
  <line stroke="red" x1="17" y1="7" x2="18" y2="6"/>
  <line stroke="red" x1="17" y1="7" x2="17" y2="9" elevation="1"/>
  <line stroke="red" x1="12" y1="14" x2="13" y2="14"/>
  <line stroke="blue" x1="12" y1="14" x2="13" y2="15"/>
  <line stroke="blue" x1="14" y1="12" x2="14" y2="13" elevation="0"/>
  <line stroke="red" x1="14" y1="12" x2="15" y2="12"/>
  <line stroke="red" x1="11" y1="15" x2="13" y2="15" elevation="1"/>
  <line stroke="blue" x1="11" y1="15" x2="12" y2="16"/>
  <line stroke="red" x1="11" y1="15" x2="11" y2="18" elevation="1"/>
  <line stroke="red" x1="15" y1="11" x2="15" y2="12" elevation="1"/>
  <line stroke="red" x1="15" y1="11" x2="17" y2="11"/>
  <line stroke="blue" x1="6" y1="18" x2="7" y2="18"/>
  <line stroke="red" x1="6" y1="18" x2="5" y2="19"/>
  <line stroke="blue" x1="6" y1="18" x2="6" y2="20" elevation="0"/>
  <line stroke="blue" x1="18" y1="6" x2="19" y2="5"/>
  <line stroke="blue" x1="18" y1="6" x2="18" y2="9" elevation="0"/>
  <line stroke="red" x1="1" y1="19" x2="5" y2="19" elevation="1"/>
  <line stroke="red" x1="1" y1="19" x2="0" y2="20"/>
  <line stroke="blue" x1="13" y1="14" x2="14" y2="14"/>
  <line stroke="red" x1="13" y1="14" x2="13" y2="15" elevation="1"/>
  <line stroke="blue" x1="14" y1="13" x2="14" y2="14" elevation="0"/>
  <line stroke="blue" x1="14" y1="13" x2="15" y2="13"/>
  <line stroke="red" x1="15" y1="12" x2="15" y2="13" elevation="1"/>
  <line stroke="blue" x1="15" y1="12" x2="17" y2="12"/>
  <line stroke="red" x1="17" y1="9" x2="17" y2="10" elevation="1"/>
  <line stroke="blue" x1="17" y1="9" x2="18" y2="9"/>
  <line stroke="red" x1="7" y1="18" x2="8" y2="18"/>
  <line stroke="red" x1="7" y1="18" x2="7" y2="20" elevation="1"/>
  <line stroke="blue" x1="5" y1="19" x2="4" y2="20"/>
  <line stroke="red" x1="5" y1="19" x2="5" y2="20" elevation="1"/>
  <line stroke="red" x1="19" y1="5" x2="20" y2="4"/>
  <line stroke="red" x1="19" y1="5" x2="19" y2="9" elevation="1"/>
  <line stroke="blue" x1="8" y1="18" x2="9" y2="18"/>
  <line stroke="blue" x1="8" y1="18" x2="8" y2="20" elevation="0"/>
  <line stroke="red" x1="17" y1="10" x2="17" y2="11" elevation="1"/>
  <line stroke="red" x1="17" y1="10" x2="18" y2="10"/>
  <line stroke="blue" x1="14" y1="14" x2="14" y2="15" elevation="0"/>
  <line stroke="red" x1="14" y1="14" x2="15" y2="14"/>
  <line stroke="blue" x1="13" y1="15" x2="12" y2="16"/>
  <line stroke="red" x1="13" y1="15" x2="14" y2="15"/>
  <line stroke="red" x1="13" y1="15" x2="13" y2="16" elevation="1"/>
  <line stroke="red" x1="15" y1="13" x2="15" y2="14" elevation="1"/>
  <line stroke="red" x1="15" y1="13" x2="17" y2="13"/>
  <line stroke="blue" x1="0" y1="20" x2="4" y2="20" elevation="0"/>
  <line stroke="red" x1="0" y1="20" x2="1" y2="21"/>
  <line stroke="black" x1="0" y1="20" x2="0" y2="24"/>
  <line stroke="red" x1="12" y1="16" x2="13" y2="16"/>
  <line stroke="blue" x1="12" y1="16" x2="12" y2="18" elevation="0"/>
  <line stroke="red" x1="9" y1="18" x2="10" y2="18"/>
  <line stroke="red" x1="9" y1="18" x2="9" y2="20" elevation="1"/>
  <line stroke="blue" x1="18" y1="9" x2="18" y2="10" elevation="0"/>
  <line stroke="red" x1="18" y1="9" x2="19" y2="9"/>
  <line stroke="red" x1="17" y1="11" x2="17" y2="12" elevation="1"/>
  <line stroke="blue" x1="17" y1="11" x2="18" y2="11"/>
  <line stroke="red" x1="4" y1="20" x2="5" y2="20"/>
  <line stroke="blue" x1="4" y1="20" x2="5" y2="21"/>
  <line stroke="blue" x1="20" y1="4" x2="21" y2="3"/>
  <line stroke="blue" x1="20" y1="4" x2="20" y2="8" elevation="0"/>
  <line stroke="blue" x1="14" y1="15" x2="15" y2="15"/>
  <line stroke="blue" x1="14" y1="15" x2="14" y2="16" elevation="0"/>
  <line stroke="red" x1="15" y1="14" x2="15" y2="15" elevation="1"/>
  <line stroke="blue" x1="15" y1="14" x2="17" y2="14"/>
  <line stroke="blue" x1="10" y1="18" x2="11" y2="18"/>
  <line stroke="blue" x1="10" y1="18" x2="10" y2="20" elevation="0"/>
  <line stroke="blue" x1="18" y1="10" x2="18" y2="11" elevation="0"/>
  <line stroke="blue" x1="18" y1="10" x2="19" y2="10"/>
  <line stroke="blue" x1="5" y1="20" x2="6" y2="20"/>
  <line stroke="red" x1="5" y1="20" x2="5" y2="21" elevation="1"/>
  <line stroke="blue" x1="13" y1="16" x2="14" y2="16"/>
  <line stroke="red" x1="13" y1="16" x2="13" y2="18" elevation="1"/>
  <line stroke="red" x1="17" y1="12" x2="17" y2="13" elevation="1"/>
  <line stroke="red" x1="17" y1="12" x2="18" y2="12"/>
  <line stroke="red" x1="6" y1="20" x2="7" y2="20"/>
  <line stroke="blue" x1="6" y1="20" x2="6" y2="22" elevation="0"/>
  <line stroke="red" x1="1" y1="21" x2="5" y2="21" elevation="1"/>
  <line stroke="blue" x1="1" y1="21" x2="2" y2="22"/>
  <line stroke="red" x1="1" y1="21" x2="1" y2="24" elevation="1"/>
  <line stroke="red" x1="19" y1="9" x2="19" y2="10" elevation="1"/>
  <line stroke="blue" x1="19" y1="9" x2="20" y2="8"/>
  <line stroke="blue" x1="19" y1="9" x2="20" y2="10"/>
  <line stroke="red" x1="19" y1="9" x2="21" y2="9" elevation="1"/>
  <line stroke="red" x1="11" y1="18" x2="12" y2="18"/>
  <line stroke="red" x1="11" y1="18" x2="11" y2="20" elevation="1"/>
  <line stroke="blue" x1="18" y1="11" x2="18" y2="12" elevation="0"/>
  <line stroke="red" x1="18" y1="11" x2="19" y2="11"/>
  <line stroke="blue" x1="7" y1="20" x2="8" y2="20"/>
  <line stroke="red" x1="7" y1="20" x2="7" y2="23" elevation="1"/>
  <line stroke="red" x1="15" y1="15" x2="15" y2="16" elevation="1"/>
  <line stroke="red" x1="15" y1="15" x2="17" y2="15"/>
  <line stroke="red" x1="21" y1="3" x2="22" y2="2"/>
  <line stroke="red" x1="21" y1="3" x2="21" y2="8" elevation="1"/>
  <line stroke="red" x1="14" y1="16" x2="15" y2="16"/>
  <line stroke="blue" x1="14" y1="16" x2="14" y2="18" elevation="0"/>
  <line stroke="red" x1="17" y1="13" x2="17" y2="14" elevation="1"/>
  <line stroke="blue" x1="17" y1="13" x2="18" y2="13"/>
  <line stroke="red" x1="19" y1="10" x2="19" y2="11" elevation="1"/>
  <line stroke="red" x1="19" y1="10" x2="20" y2="10"/>
  <line stroke="red" x1="8" y1="20" x2="9" y2="20"/>
  <line stroke="blue" x1="8" y1="20" x2="8" y2="24" elevation="0"/>
  <line stroke="red" x1="20" y1="8" x2="21" y2="8"/>
  <line stroke="blue" x1="20" y1="8" x2="21" y2="9"/>
  <line stroke="red" x1="5" y1="21" x2="6" y2="22"/>
  <line stroke="blue" x1="12" y1="18" x2="13" y2="18"/>
  <line stroke="blue" x1="12" y1="18" x2="12" y2="20" elevation="0"/>
  <line stroke="blue" x1="18" y1="12" x2="18" y2="13" elevation="0"/>
  <line stroke="blue" x1="18" y1="12" x2="19" y2="12"/>
  <line stroke="blue" x1="9" y1="20" x2="10" y2="20"/>
  <line stroke="red" x1="9" y1="20" x2="9" y2="25" elevation="1"/>
  <line stroke="blue" x1="15" y1="16" x2="17" y2="16"/>
  <line stroke="red" x1="15" y1="16" x2="15" y2="18" elevation="1"/>
  <line stroke="blue" x1="19" y1="11" x2="20" y2="10"/>
  <line stroke="red" x1="19" y1="11" x2="19" y2="12" elevation="1"/>
  <line stroke="blue" x1="19" y1="11" x2="20" y2="12"/>
  <line stroke="red" x1="19" y1="11" x2="23" y2="11" elevation="1"/>
  <line stroke="red" x1="17" y1="14" x2="17" y2="15" elevation="1"/>
  <line stroke="red" x1="17" y1="14" x2="18" y2="14"/>
  <line stroke="blue" x1="2" y1="22" x2="6" y2="22" elevation="0"/>
  <line stroke="red" x1="2" y1="22" x2="3" y2="23"/>
  <line stroke="blue" x1="2" y1="22" x2="2" y2="24" elevation="0"/>
  <line stroke="blue" x1="22" y1="2" x2="23" y2="1"/>
  <line stroke="blue" x1="22" y1="2" x2="22" y2="8" elevation="0"/>
  <line stroke="red" x1="13" y1="18" x2="14" y2="18"/>
  <line stroke="red" x1="13" y1="18" x2="13" y2="20" elevation="1"/>
  <line stroke="blue" x1="18" y1="13" x2="18" y2="14" elevation="0"/>
  <line stroke="red" x1="18" y1="13" x2="19" y2="13"/>
  <line stroke="red" x1="10" y1="20" x2="11" y2="20"/>
  <line stroke="blue" x1="10" y1="20" x2="10" y2="26" elevation="0"/>
  <line stroke="blue" x1="20" y1="10" x2="22" y2="10" elevation="0"/>
  <line stroke="red" x1="19" y1="12" x2="19" y2="13" elevation="1"/>
  <line stroke="red" x1="19" y1="12" x2="20" y2="12"/>
  <line stroke="red" x1="21" y1="8" x2="21" y2="9" elevation="1"/>
  <line stroke="blue" x1="21" y1="8" x2="22" y2="8"/>
  <line stroke="red" x1="17" y1="15" x2="17" y2="16" elevation="1"/>
  <line stroke="blue" x1="17" y1="15" x2="18" y2="15"/>
  <line stroke="blue" x1="6" y1="22" x2="7" y2="23"/>
  <line stroke="blue" x1="14" y1="18" x2="15" y2="18"/>
  <line stroke="blue" x1="14" y1="18" x2="14" y2="20" elevation="0"/>
  <line stroke="blue" x1="18" y1="14" x2="18" y2="15" elevation="0"/>
  <line stroke="blue" x1="18" y1="14" x2="19" y2="14"/>
  <line stroke="blue" x1="11" y1="20" x2="12" y2="20"/>
  <line stroke="red" x1="11" y1="20" x2="11" y2="27" elevation="1"/>
  <line stroke="red" x1="21" y1="9" x2="22" y2="10"/>
  <line stroke="blue" x1="19" y1="13" x2="20" y2="12"/>
  <line stroke="red" x1="19" y1="13" x2="19" y2="14" elevation="1"/>
  <line stroke="blue" x1="19" y1="13" x2="20" y2="14"/>
  <line stroke="red" x1="19" y1="13" x2="23" y2="13" elevation="1"/>
  <line stroke="red" x1="23" y1="1" x2="24" y2="0"/>
  <line stroke="red" x1="23" y1="1" x2="23" y2="8" elevation="1"/>
  <line stroke="red" x1="3" y1="23" x2="7" y2="23" elevation="1"/>
  <line stroke="red" x1="3" y1="23" x2="3" y2="24" elevation="1"/>
  <line stroke="blue" x1="3" y1="23" x2="4" y2="24"/>
  <line stroke="red" x1="12" y1="20" x2="13" y2="20"/>
  <line stroke="blue" x1="12" y1="20" x2="12" y2="28" elevation="0"/>
  <line stroke="blue" x1="20" y1="12" x2="24" y2="12" elevation="0"/>
  <line stroke="red" x1="17" y1="16" x2="18" y2="16"/>
  <line stroke="red" x1="17" y1="16" x2="17" y2="18" elevation="1"/>
  <line stroke="blue" x1="22" y1="8" x2="22" y2="10" elevation="0"/>
  <line stroke="red" x1="22" y1="8" x2="23" y2="8"/>
  <line stroke="red" x1="15" y1="18" x2="17" y2="18"/>
  <line stroke="red" x1="15" y1="18" x2="15" y2="20" elevation="1"/>
  <line stroke="blue" x1="18" y1="15" x2="18" y2="16" elevation="0"/>
  <line stroke="red" x1="18" y1="15" x2="19" y2="15"/>
  <line stroke="red" x1="19" y1="14" x2="19" y2="15" elevation="1"/>
  <line stroke="red" x1="19" y1="14" x2="20" y2="14"/>
  <line stroke="blue" x1="13" y1="20" x2="14" y2="20"/>
  <line stroke="red" x1="13" y1="20" x2="13" y2="29" elevation="1"/>
  <line stroke="blue" x1="0" y1="24" x2="1" y2="24"/>
  <line stroke="black" x1="0" y1="24" x2="0" y2="28"/>
  <line stroke="red" x1="24" y1="0" x2="25" y2="1"/>
  <line stroke="blue" x1="24" y1="0" x2="24" y2="8" elevation="0"/>
  <line stroke="black" x1="24" y1="0" x2="32" y2="0"/>
  <line stroke="red" x1="1" y1="24" x2="2" y2="24"/>
  <line stroke="red" x1="1" y1="24" x2="1" y2="27" elevation="1"/>
  <line stroke="red" x1="7" y1="23" x2="8" y2="24"/>
  <line stroke="blue" x1="2" y1="24" x2="3" y2="24"/>
  <line stroke="blue" x1="2" y1="24" x2="2" y2="26" elevation="0"/>
  <line stroke="blue" x1="18" y1="16" x2="19" y2="16"/>
  <line stroke="blue" x1="18" y1="16" x2="18" y2="18" elevation="0"/>
  <line stroke="blue" x1="22" y1="10" x2="23" y2="11"/>
  <line stroke="red" x1="3" y1="24" x2="4" y2="24"/>
  <line stroke="red" x1="3" y1="24" x2="3" y2="25" elevation="1"/>
  <line stroke="blue" x1="19" y1="15" x2="20" y2="14"/>
  <line stroke="red" x1="19" y1="15" x2="19" y2="16" elevation="1"/>
  <line stroke="blue" x1="19" y1="15" x2="20" y2="16"/>
  <line stroke="red" x1="19" y1="15" x2="21" y2="15" elevation="1"/>
  <line stroke="blue" x1="4" y1="24" x2="3" y2="25"/>
  <line stroke="blue" x1="4" y1="24" x2="8" y2="24" elevation="0"/>
  <line stroke="blue" x1="23" y1="8" x2="24" y2="8"/>
  <line stroke="red" x1="23" y1="8" x2="23" y2="11" elevation="1"/>
  <line stroke="red" x1="14" y1="20" x2="15" y2="20"/>
  <line stroke="blue" x1="14" y1="20" x2="14" y2="30" elevation="0"/>
  <line stroke="blue" x1="20" y1="14" x2="22" y2="14" elevation="0"/>
  <line stroke="blue" x1="17" y1="18" x2="18" y2="18"/>
  <line stroke="red" x1="17" y1="18" x2="17" y2="20" elevation="1"/>
  <line stroke="red" x1="19" y1="16" x2="20" y2="16"/>
  <line stroke="red" x1="19" y1="16" x2="19" y2="18" elevation="1"/>
  <line stroke="blue" x1="15" y1="20" x2="17" y2="20"/>
  <line stroke="red" x1="15" y1="20" x2="15" y2="31" elevation="1"/>
  <line stroke="blue" x1="25" y1="1" x2="26" y2="2"/>
  <line stroke="red" x1="25" y1="1" x2="25" y2="8" elevation="1"/>
  <line stroke="red" x1="25" y1="1" x2="31" y2="1" elevation="1"/>
  <line stroke="red" x1="3" y1="25" x2="2" y2="26"/>
  <line stroke="red" x1="3" y1="25" x2="9" y2="25" elevation="1"/>
  <line stroke="blue" x1="8" y1="24" x2="9" y2="25"/>
  <line stroke="blue" x1="24" y1="8" x2="25" y2="8"/>
  <line stroke="red" x1="24" y1="8" x2="24" y2="12" elevation="0"/>
  <line stroke="red" x1="18" y1="18" x2="19" y2="18"/>
  <line stroke="blue" x1="18" y1="18" x2="18" y2="20" elevation="0"/>
  <line stroke="red" x1="23" y1="11" x2="24" y2="12"/>
  <line stroke="blue" x1="20" y1="16" x2="21" y2="15"/>
  <line stroke="blue" x1="20" y1="16" x2="20" y2="18" elevation="0"/>
  <line stroke="red" x1="21" y1="15" x2="22" y2="14"/>
  <line stroke="red" x1="21" y1="15" x2="21" y2="18" elevation="1"/>
  <line stroke="blue" x1="2" y1="26" x2="1" y2="27"/>
  <line stroke="blue" x1="2" y1="26" x2="10" y2="26" elevation="0"/>
  <line stroke="blue" x1="22" y1="14" x2="23" y2="13"/>
  <line stroke="blue" x1="22" y1="14" x2="22" y2="18" elevation="0"/>
  <line stroke="red" x1="26" y1="2" x2="27" y2="3"/>
  <line stroke="blue" x1="26" y1="2" x2="26" y2="8" elevation="0"/>
  <line stroke="blue" x1="26" y1="2" x2="30" y2="2" elevation="0"/>
  <line stroke="blue" x1="19" y1="18" x2="20" y2="18"/>
  <line stroke="red" x1="19" y1="18" x2="19" y2="20" elevation="1"/>
  <line stroke="red" x1="17" y1="20" x2="18" y2="20"/>
  <line stroke="red" x1="17" y1="20" x2="17" y2="31" elevation="1"/>
  <line stroke="red" x1="25" y1="8" x2="26" y2="8"/>
  <line stroke="red" x1="25" y1="8" x2="25" y2="11" elevation="1"/>
  <line stroke="red" x1="23" y1="13" x2="24" y2="12"/>
  <line stroke="red" x1="23" y1="13" x2="23" y2="18" elevation="1"/>
  <line stroke="red" x1="9" y1="25" x2="10" y2="26"/>
  <line stroke="red" x1="24" y1="12" x2="25" y2="11"/>
  <line stroke="red" x1="24" y1="12" x2="25" y2="13"/>
  <line stroke="blue" x1="24" y1="12" x2="24" y2="18" elevation="0"/>
  <line stroke="blue" x1="24" y1="12" x2="28" y2="12" elevation="0"/>
  <line stroke="blue" x1="18" y1="20" x2="19" y2="20"/>
  <line stroke="blue" x1="18" y1="20" x2="18" y2="30" elevation="0"/>
  <line stroke="red" x1="20" y1="18" x2="21" y2="18"/>
  <line stroke="blue" x1="20" y1="18" x2="20" y2="20" elevation="0"/>
  <line stroke="red" x1="1" y1="27" x2="0" y2="28"/>
  <line stroke="red" x1="1" y1="27" x2="11" y2="27" elevation="1"/>
  <line stroke="red" x1="27" y1="3" x2="27" y2="8" elevation="1"/>
  <line stroke="blue" x1="27" y1="3" x2="28" y2="4"/>
  <line stroke="red" x1="27" y1="3" x2="29" y2="3" elevation="1"/>
  <line stroke="blue" x1="26" y1="8" x2="26" y2="10" elevation="0"/>
  <line stroke="blue" x1="26" y1="8" x2="27" y2="8"/>
  <line stroke="blue" x1="25" y1="11" x2="26" y2="10"/>
  <line stroke="red" x1="25" y1="11" x2="28" y2="11" elevation="1"/>
  <line stroke="red" x1="19" y1="20" x2="20" y2="20"/>
  <line stroke="red" x1="19" y1="20" x2="19" y2="29" elevation="1"/>
  <line stroke="blue" x1="21" y1="18" x2="22" y2="18"/>
  <line stroke="red" x1="21" y1="18" x2="21" y2="20" elevation="1"/>
  <line stroke="blue" x1="10" y1="26" x2="11" y2="27"/>
  <line stroke="red" x1="26" y1="10" x2="27" y2="9"/>
  <line stroke="blue" x1="26" y1="10" x2="28" y2="10" elevation="0"/>
  <line stroke="red" x1="0" y1="28" x2="1" y2="29"/>
  <line stroke="blue" x1="0" y1="28" x2="12" y2="28" elevation="0"/>
  <line stroke="black" x1="0" y1="28" x2="0" y2="32"/>
  <line stroke="red" x1="27" y1="8" x2="27" y2="9" elevation="1"/>
  <line stroke="red" x1="27" y1="8" x2="28" y2="8"/>
  <line stroke="blue" x1="25" y1="13" x2="26" y2="14"/>
  <line stroke="red" x1="25" y1="13" x2="25" y2="18" elevation="1"/>
  <line stroke="red" x1="25" y1="13" x2="28" y2="13" elevation="1"/>
  <line stroke="blue" x1="20" y1="20" x2="21" y2="20"/>
  <line stroke="blue" x1="20" y1="20" x2="20" y2="28" elevation="0"/>
  <line stroke="blue" x1="28" y1="4" x2="28" y2="8" elevation="0"/>
  <line stroke="blue" x1="28" y1="4" x2="29" y2="3"/>
  <line stroke="red" x1="28" y1="4" x2="29" y2="4"/>
  <line stroke="red" x1="22" y1="18" x2="23" y2="18"/>
  <line stroke="blue" x1="22" y1="18" x2="22" y2="20" elevation="0"/>
  <line stroke="blue" x1="27" y1="9" x2="28" y2="8"/>
  <line stroke="red" x1="27" y1="9" x2="28" y2="9" elevation="1"/>
  <line stroke="red" x1="21" y1="20" x2="22" y2="20"/>
  <line stroke="red" x1="21" y1="20" x2="21" y2="27" elevation="1"/>
  <line stroke="blue" x1="1" y1="29" x2="2" y2="30"/>
  <line stroke="red" x1="1" y1="29" x2="13" y2="29" elevation="1"/>
  <line stroke="red" x1="1" y1="29" x2="1" y2="32" elevation="1"/>
  <line stroke="blue" x1="28" y1="8" x2="28" y2="9"/>
  <line stroke="red" x1="28" y1="8" x2="29" y2="8"/>
  <line stroke="blue" x1="28" y1="8" x2="29" y2="9"/>
  <line stroke="red" x1="11" y1="27" x2="12" y2="28"/>
  <line stroke="red" x1="29" y1="3" x2="29" y2="4" elevation="1"/>
  <line stroke="red" x1="29" y1="3" x2="30" y2="2"/>
  <line stroke="blue" x1="23" y1="18" x2="24" y2="18"/>
  <line stroke="red" x1="23" y1="18" x2="23" y2="20" elevation="1"/>
  <line stroke="red" x1="29" y1="4" x2="29" y2="8" elevation="1"/>
  <line stroke="blue" x1="29" y1="4" x2="30" y2="4"/>
  <line stroke="red" x1="28" y1="9" x2="28" y2="10"/>
  <line stroke="red" x1="28" y1="9" x2="29" y2="9" elevation="1"/>
  <line stroke="red" x1="26" y1="14" x2="27" y2="15"/>
  <line stroke="blue" x1="26" y1="14" x2="28" y2="14" elevation="0"/>
  <line stroke="blue" x1="26" y1="14" x2="26" y2="18" elevation="0"/>
  <line stroke="blue" x1="22" y1="20" x2="23" y2="20"/>
  <line stroke="blue" x1="22" y1="20" x2="22" y2="26" elevation="0"/>
  <line stroke="blue" x1="28" y1="10" x2="28" y2="11"/>
  <line stroke="blue" x1="28" y1="10" x2="30" y2="10" elevation="0"/>
  <line stroke="red" x1="24" y1="18" x2="25" y2="18"/>
  <line stroke="blue" x1="24" y1="18" x2="24" y2="20" elevation="0"/>
  <line stroke="red" x1="2" y1="30" x2="3" y2="31"/>
  <line stroke="blue" x1="2" y1="30" x2="2" y2="32" elevation="0"/>
  <line stroke="blue" x1="2" y1="30" x2="14" y2="30" elevation="0"/>
  <line stroke="blue" x1="30" y1="2" x2="30" y2="4" elevation="0"/>
  <line stroke="blue" x1="30" y1="2" x2="31" y2="1"/>
  <line stroke="red" x1="28" y1="11" x2="28" y2="12"/>
  <line stroke="red" x1="28" y1="11" x2="31" y2="11" elevation="1"/>
  <line stroke="red" x1="29" y1="8" x2="29" y2="9" elevation="1"/>
  <line stroke="blue" x1="29" y1="8" x2="30" y2="8"/>
  <line stroke="blue" x1="30" y1="4" x2="30" y2="8" elevation="0"/>
  <line stroke="red" x1="30" y1="4" x2="31" y2="4"/>
  <line stroke="red" x1="29" y1="9" x2="30" y2="10"/>
  <line stroke="blue" x1="12" y1="28" x2="13" y2="29"/>
  <line stroke="blue" x1="28" y1="12" x2="28" y2="13"/>
  <line stroke="blue" x1="28" y1="12" x2="32" y2="12" elevation="0"/>
  <line stroke="red" x1="23" y1="20" x2="24" y2="20"/>
  <line stroke="red" x1="23" y1="20" x2="23" y2="25" elevation="1"/>
  <line stroke="blue" x1="25" y1="18" x2="26" y2="18"/>
  <line stroke="red" x1="25" y1="18" x2="25" y2="20" elevation="1"/>
  <line stroke="red" x1="28" y1="13" x2="28" y2="14"/>
  <line stroke="red" x1="28" y1="13" x2="31" y2="13" elevation="1"/>
  <line stroke="red" x1="27" y1="15" x2="28" y2="15" elevation="1"/>
  <line stroke="red" x1="27" y1="15" x2="27" y2="17" elevation="1"/>
  <line stroke="blue" x1="27" y1="15" x2="28" y2="16"/>
  <line stroke="red" x1="31" y1="1" x2="31" y2="4" elevation="1"/>
  <line stroke="red" x1="31" y1="1" x2="32" y2="0"/>
  <line stroke="blue" x1="30" y1="8" x2="30" y2="10" elevation="0"/>
  <line stroke="red" x1="30" y1="8" x2="31" y2="8"/>
  <line stroke="red" x1="3" y1="31" x2="3" y2="32" elevation="1"/>
  <line stroke="blue" x1="3" y1="31" x2="4" y2="32"/>
  <line stroke="red" x1="3" y1="31" x2="15" y2="31" elevation="1"/>
  <line stroke="blue" x1="24" y1="20" x2="25" y2="20"/>
  <line stroke="blue" x1="24" y1="20" x2="24" y2="24" elevation="0"/>
  <line stroke="red" x1="31" y1="4" x2="31" y2="8" elevation="1"/>
  <line stroke="blue" x1="31" y1="4" x2="32" y2="4"/>
  <line stroke="blue" x1="28" y1="14" x2="28" y2="15"/>
  <line stroke="blue" x1="28" y1="14" x2="30" y2="14" elevation="0"/>
  <line stroke="red" x1="26" y1="18" x2="27" y2="17"/>
  <line stroke="blue" x1="26" y1="18" x2="26" y2="20" elevation="0"/>
  <line stroke="red" x1="26" y1="18" x2="27" y2="19"/>
  <line stroke="blue" x1="26" y1="18" x2="30" y2="18" elevation="0"/>
  <line stroke="blue" x1="30" y1="10" x2="31" y2="11"/>
  <line stroke="red" x1="28" y1="15" x2="28" y2="16"/>
  <line stroke="red" x1="28" y1="15" x2="29" y2="15" elevation="1"/>
  <line stroke="red" x1="13" y1="29" x2="14" y2="30"/>
  <line stroke="blue" x1="27" y1="17" x2="28" y2="16"/>
  <line stroke="red" x1="27" y1="17" x2="29" y2="17" elevation="1"/>
  <line stroke="black" x1="0" y1="32" x2="1" y2="32"/>
  <line stroke="black" x1="32" y1="0" x2="32" y2="4"/>
  <line stroke="black" x1="1" y1="32" x2="2" y2="32"/>
  <line stroke="red" x1="25" y1="20" x2="26" y2="20"/>
  <line stroke="red" x1="25" y1="20" x2="25" y2="23" elevation="1"/>
  <line stroke="red" x1="31" y1="8" x2="31" y2="11" elevation="1"/>
  <line stroke="blue" x1="31" y1="8" x2="32" y2="8"/>
  <line stroke="black" x1="2" y1="32" x2="3" y2="32"/>
  <line stroke="black" x1="3" y1="32" x2="4" y2="32"/>
  <line stroke="black" x1="4" y1="32" x2="16" y2="32"/>
  <line stroke="blue" x1="28" y1="16" x2="29" y2="15"/>
  <line stroke="red" x1="28" y1="16" x2="29" y2="16"/>
  <line stroke="blue" x1="28" y1="16" x2="29" y2="17"/>
  <line stroke="black" x1="32" y1="4" x2="32" y2="8"/>
  <line stroke="red" x1="29" y1="15" x2="30" y2="14"/>
  <line stroke="red" x1="29" y1="15" x2="29" y2="16" elevation="1"/>
  <line stroke="blue" x1="26" y1="20" x2="27" y2="20"/>
  <line stroke="blue" x1="26" y1="20" x2="26" y2="22" elevation="0"/>
  <line stroke="red" x1="31" y1="11" x2="32" y2="12"/>
  <line stroke="black" x1="32" y1="8" x2="32" y2="12"/>
  <line stroke="red" x1="27" y1="19" x2="27" y2="20" elevation="1"/>
  <line stroke="blue" x1="27" y1="19" x2="28" y2="20"/>
  <line stroke="red" x1="27" y1="19" x2="31" y2="19" elevation="1"/>
  <line stroke="blue" x1="14" y1="30" x2="15" y2="31"/>
  <line stroke="blue" x1="30" y1="14" x2="31" y2="13"/>
  <line stroke="blue" x1="30" y1="14" x2="30" y2="16" elevation="0"/>
  <line stroke="red" x1="29" y1="16" x2="29" y2="17" elevation="1"/>
  <line stroke="blue" x1="29" y1="16" x2="30" y2="16"/>
  <line stroke="red" x1="27" y1="20" x2="27" y2="21" elevation="1"/>
  <line stroke="red" x1="27" y1="20" x2="28" y2="20"/>
  <line stroke="red" x1="29" y1="17" x2="30" y2="18"/>
  <line stroke="red" x1="31" y1="13" x2="32" y2="12"/>
  <line stroke="red" x1="31" y1="13" x2="31" y2="16" elevation="1"/>
  <line stroke="blue" x1="24" y1="24" x2="23" y2="25"/>
  <line stroke="red" x1="24" y1="24" x2="25" y2="23"/>
  <line stroke="blue" x1="24" y1="24" x2="28" y2="24" elevation="0"/>
  <line stroke="red" x1="23" y1="25" x2="22" y2="26"/>
  <line stroke="red" x1="23" y1="25" x2="29" y2="25" elevation="1"/>
  <line stroke="blue" x1="25" y1="23" x2="26" y2="22"/>
  <line stroke="red" x1="25" y1="23" x2="29" y2="23" elevation="1"/>
  <line stroke="red" x1="30" y1="16" x2="31" y2="16"/>
  <line stroke="blue" x1="30" y1="16" x2="30" y2="18" elevation="0"/>
  <line stroke="blue" x1="22" y1="26" x2="21" y2="27"/>
  <line stroke="blue" x1="22" y1="26" x2="30" y2="26" elevation="0"/>
  <line stroke="red" x1="26" y1="22" x2="27" y2="21"/>
  <line stroke="blue" x1="26" y1="22" x2="30" y2="22" elevation="0"/>
  <line stroke="black" x1="32" y1="12" x2="32" y2="16"/>
  <line stroke="red" x1="21" y1="27" x2="20" y2="28"/>
  <line stroke="red" x1="21" y1="27" x2="31" y2="27" elevation="1"/>
  <line stroke="blue" x1="27" y1="21" x2="28" y2="20"/>
  <line stroke="red" x1="27" y1="21" x2="31" y2="21" elevation="1"/>
  <line stroke="blue" x1="20" y1="28" x2="19" y2="29"/>
  <line stroke="blue" x1="20" y1="28" x2="32" y2="28" elevation="0"/>
  <line stroke="blue" x1="28" y1="20" x2="32" y2="20" elevation="0"/>
  <line stroke="red" x1="15" y1="31" x2="16" y2="32"/>
  <line stroke="red" x1="19" y1="29" x2="18" y2="30"/>
  <line stroke="red" x1="19" y1="29" x2="31" y2="29" elevation="1"/>
  <line stroke="blue" x1="31" y1="16" x2="32" y2="16"/>
  <line stroke="red" x1="31" y1="16" x2="31" y2="19" elevation="1"/>
  <line stroke="blue" x1="18" y1="30" x2="17" y2="31"/>
  <line stroke="blue" x1="18" y1="30" x2="30" y2="30" elevation="0"/>
  <line stroke="blue" x1="30" y1="18" x2="31" y2="19"/>
  <line stroke="red" x1="17" y1="31" x2="16" y2="32"/>
  <line stroke="red" x1="17" y1="31" x2="29" y2="31" elevation="1"/>
  <line stroke="black" x1="16" y1="32" x2="28" y2="32"/>
  <line stroke="black" x1="32" y1="16" x2="32" y2="20"/>
  <line stroke="red" x1="31" y1="19" x2="32" y2="20"/>
  <line stroke="blue" x1="28" y1="24" x2="29" y2="23"/>
  <line stroke="red" x1="28" y1="24" x2="29" y2="24"/>
  <line stroke="blue" x1="28" y1="24" x2="29" y2="25"/>
  <line stroke="red" x1="29" y1="23" x2="30" y2="22"/>
  <line stroke="red" x1="29" y1="23" x2="29" y2="24" elevation="1"/>
  <line stroke="blue" x1="30" y1="22" x2="31" y2="21"/>
  <line stroke="blue" x1="30" y1="22" x2="30" y2="24" elevation="0"/>
  <line stroke="red" x1="31" y1="21" x2="32" y2="20"/>
  <line stroke="red" x1="31" y1="21" x2="31" y2="24" elevation="1"/>
  <line stroke="red" x1="29" y1="24" x2="29" y2="25" elevation="1"/>
  <line stroke="blue" x1="29" y1="24" x2="30" y2="24"/>
  <line stroke="black" x1="32" y1="20" x2="32" y2="24"/>
  <line stroke="red" x1="29" y1="25" x2="30" y2="26"/>
  <line stroke="red" x1="30" y1="24" x2="31" y2="24"/>
  <line stroke="blue" x1="30" y1="24" x2="30" y2="26" elevation="0"/>
  <line stroke="blue" x1="31" y1="24" x2="32" y2="24"/>
  <line stroke="red" x1="31" y1="24" x2="31" y2="27" elevation="1"/>
  <line stroke="blue" x1="30" y1="26" x2="31" y2="27"/>
  <line stroke="black" x1="32" y1="24" x2="32" y2="28"/>
  <line stroke="red" x1="31" y1="27" x2="32" y2="28"/>
  <line stroke="red" x1="30" y1="30" x2="29" y2="31"/>
  <line stroke="blue" x1="30" y1="30" x2="31" y2="29"/>
  <line stroke="blue" x1="30" y1="30" x2="30" y2="32" elevation="0"/>
  <line stroke="blue" x1="29" y1="31" x2="28" y2="32"/>
  <line stroke="red" x1="29" y1="31" x2="29" y2="32" elevation="1"/>
  <line stroke="red" x1="31" y1="29" x2="32" y2="28"/>
  <line stroke="red" x1="31" y1="29" x2="31" y2="32" elevation="1"/>
  <line stroke="black" x1="28" y1="32" x2="29" y2="32"/>
  <line stroke="black" x1="32" y1="28" x2="32" y2="32"/>
  <line stroke="black" x1="29" y1="32" x2="30" y2="32"/>
  <line stroke="black" x1="30" y1="32" x2="31" y2="32"/>
  <line stroke="black" x1="31" y1="32" x2="32" y2="32"/>
</svg>""",
)

SNAKE = BoxPleatingCreasePatternExample(
    name="snake",
    grid_size=16,
    central_crease_removed=False,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svgjs="http://svgjs.dev/svgjs" viewBox="-0.5 -0.5 17 17" width="17cm" height="17cm"><g class="crease"><line x1="0" y1="0" x2="16" y2="16" class="M" stroke-opacity="1" data-index="4" stroke-width="0.1" stroke="#ff0000"></line><line x1="0" y1="16" x2="16" y2="16" class="B" stroke-opacity="1" data-index="0" stroke="#000000" stroke-width="0.1"></line><line x1="16" y1="16" x2="16" y2="0" class="B" stroke-opacity="1" data-index="1" stroke="#000000" stroke-width="0.1"></line><line x1="16" y1="0" x2="0" y2="0" class="B" stroke-opacity="1" data-index="2" stroke="#000000" stroke-width="0.1"></line><line x1="0" y1="0" x2="0" y2="16" class="B" stroke-opacity="1" data-index="3" stroke="#000000" stroke-width="0.1"></line></g><style>line { stroke-linecap: round; }</style></svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <rect stroke="black" x="0" y="0" width="16" height="16"/>
  <line stroke="blue" x1="0" y1="0" x2="1" y2="1"/>
  <line stroke="red" x1="0" y1="1" x2="1" y2="1" elevation="1"/>
  <line stroke="red" x1="1" y1="0" x2="1" y2="1" elevation="1"/>
  <line stroke="red" x1="1" y1="1" x2="2" y2="2"/>
  <line stroke="blue" x1="0" y1="2" x2="2" y2="2" elevation="0"/>
  <line stroke="blue" x1="2" y1="0" x2="2" y2="2" elevation="0"/>
  <line stroke="blue" x1="2" y1="2" x2="3" y2="3"/>
  <line stroke="red" x1="0" y1="3" x2="3" y2="3" elevation="1"/>
  <line stroke="red" x1="3" y1="0" x2="3" y2="3" elevation="1"/>
  <line stroke="blue" x1="0" y1="4" x2="4" y2="4" elevation="0"/>
  <line stroke="blue" x1="4" y1="0" x2="4" y2="4" elevation="0"/>
  <line stroke="red" x1="3" y1="3" x2="4" y2="4"/>
  <line stroke="red" x1="0" y1="5" x2="5" y2="5" elevation="1"/>
  <line stroke="red" x1="5" y1="0" x2="5" y2="5" elevation="1"/>
  <line stroke="blue" x1="4" y1="4" x2="5" y2="5"/>
  <line stroke="blue" x1="0" y1="6" x2="6" y2="6" elevation="0"/>
  <line stroke="blue" x1="6" y1="0" x2="6" y2="6" elevation="0"/>
  <line stroke="red" x1="0" y1="7" x2="7" y2="7" elevation="1"/>
  <line stroke="red" x1="7" y1="0" x2="7" y2="7" elevation="1"/>
  <line stroke="red" x1="5" y1="5" x2="6" y2="6"/>
  <line stroke="blue" x1="0" y1="8" x2="8" y2="8" elevation="0"/>
  <line stroke="blue" x1="8" y1="0" x2="8" y2="8" elevation="0"/>
  <line stroke="blue" x1="6" y1="6" x2="7" y2="7"/>
  <line stroke="red" x1="0" y1="9" x2="9" y2="9" elevation="1"/>
  <line stroke="red" x1="9" y1="0" x2="9" y2="9" elevation="1"/>
  <line stroke="red" x1="7" y1="7" x2="8" y2="8"/>
  <line stroke="blue" x1="0" y1="10" x2="10" y2="10" elevation="0"/>
  <line stroke="blue" x1="10" y1="0" x2="10" y2="10" elevation="0"/>
  <line stroke="red" x1="0" y1="11" x2="11" y2="11" elevation="1"/>
  <line stroke="red" x1="11" y1="0" x2="11" y2="11" elevation="1"/>
  <line stroke="blue" x1="8" y1="8" x2="9" y2="9"/>
  <line stroke="blue" x1="0" y1="12" x2="12" y2="12" elevation="0"/>
  <line stroke="blue" x1="12" y1="0" x2="12" y2="12" elevation="0"/>
  <line stroke="red" x1="9" y1="9" x2="10" y2="10"/>
  <line stroke="red" x1="0" y1="13" x2="13" y2="13" elevation="1"/>
  <line stroke="red" x1="13" y1="0" x2="13" y2="13" elevation="1"/>
  <line stroke="blue" x1="0" y1="14" x2="14" y2="14" elevation="0"/>
  <line stroke="blue" x1="14" y1="0" x2="14" y2="14" elevation="0"/>
  <line stroke="blue" x1="10" y1="10" x2="11" y2="11"/>
  <line stroke="red" x1="0" y1="15" x2="15" y2="15" elevation="1"/>
  <line stroke="red" x1="15" y1="0" x2="15" y2="15" elevation="1"/>
  <line stroke="red" x1="11" y1="11" x2="12" y2="12"/>
  <line stroke="blue" x1="12" y1="12" x2="13" y2="13"/>
  <line stroke="red" x1="13" y1="13" x2="14" y2="14"/>
  <line stroke="blue" x1="14" y1="14" x2="15" y2="15"/>
  <line stroke="red" x1="15" y1="15" x2="16" y2="16"/>
</svg>""",
)

JAGUAR = BoxPleatingCreasePatternExample(
    name="jaguar",
    grid_size=14,
    central_crease_removed=False,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14">
  <rect stroke="black" x="0" y="0" width="14" height="14"/>
  <line stroke="red" x1="2" y1="0" x2="5" y2="3"/>
  <line stroke="green" x1="0" y1="3" x2="5" y2="3"/>
  <line stroke="green" x1="5" y1="0" x2="5" y2="3"/>
  <line stroke="red" x1="5" y1="3" x2="7" y2="1"/>
  <line stroke="green" x1="5" y1="3" x2="9" y2="3"/>
  <line stroke="red" x1="7" y1="0" x2="7" y2="1"/>
  <line stroke="red" x1="7" y1="1" x2="9" y2="3"/>
  <line stroke="green" x1="0" y1="8" x2="3" y2="8"/>
  <line stroke="red" x1="3" y1="8" x2="0" y2="11"/>
  <line stroke="green" x1="3" y1="8" x2="11" y2="8"/>
  <line stroke="red" x1="3" y1="8" x2="7" y2="12"/>
  <line stroke="green" x1="3" y1="8" x2="3" y2="14"/>
  <line stroke="green" x1="9" y1="0" x2="9" y2="3"/>
  <line stroke="red" x1="9" y1="3" x2="12" y2="0"/>
  <line stroke="green" x1="9" y1="3" x2="14" y2="3"/>
  <line stroke="red" x1="11" y1="8" x2="7" y2="12"/>
  <line stroke="green" x1="11" y1="8" x2="14" y2="8"/>
  <line stroke="green" x1="11" y1="8" x2="11" y2="14"/>
  <line stroke="red" x1="11" y1="8" x2="14" y2="11"/>
  <line stroke="red" x1="7" y1="12" x2="7" y2="14"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14">
  <rect stroke="black" x="0" y="0" width="14" height="14"/>
  <line stroke="red" x1="1" y1="0" x2="1" y2="8" elevation="1"/>
  <line stroke="red" x1="2" y1="0" x2="3" y2="1"/>
  <line stroke="blue" x1="2" y1="0" x2="2" y2="8" elevation="0"/>
  <line stroke="blue" x1="3" y1="1" x2="4" y2="2"/>
  <line stroke="red" x1="3" y1="1" x2="5" y2="1" elevation="1"/>
  <line stroke="red" x1="3" y1="1" x2="3" y2="8" elevation="1"/>
  <line stroke="blue" x1="4" y1="2" x2="5" y2="2" elevation="0"/>
  <line stroke="red" x1="4" y1="2" x2="5" y2="3"/>
  <line stroke="blue" x1="4" y1="2" x2="4" y2="9" elevation="0"/>
  <line stroke="blue" x1="5" y1="0" x2="5" y2="1"/>
  <line stroke="red" x1="5" y1="1" x2="5" y2="2"/>
  <line stroke="red" x1="5" y1="1" x2="7" y2="1" elevation="1"/>
  <line stroke="blue" x1="5" y1="2" x2="5" y2="3"/>
  <line stroke="blue" x1="5" y1="2" x2="6" y2="2" elevation="0"/>
  <line stroke="red" x1="5" y1="3" x2="6" y2="2"/>
  <line stroke="red" x1="5" y1="3" x2="5" y2="10" elevation="1"/>
  <line stroke="blue" x1="6" y1="2" x2="7" y2="1"/>
  <line stroke="blue" x1="6" y1="2" x2="6" y2="11" elevation="0"/>
  <line stroke="red" x1="7" y1="0" x2="7" y2="1"/>
  <line stroke="blue" x1="7" y1="1" x2="8" y2="2"/>
  <line stroke="red" x1="7" y1="1" x2="9" y2="1" elevation="1"/>
  <line stroke="red" x1="7" y1="1" x2="7" y2="12" elevation="1"/>
  <line stroke="blue" x1="0" y1="8" x2="1" y2="8"/>
  <line stroke="red" x1="1" y1="8" x2="2" y2="8"/>
  <line stroke="red" x1="1" y1="8" x2="1" y2="10" elevation="1"/>
  <line stroke="blue" x1="2" y1="8" x2="3" y2="8"/>
  <line stroke="blue" x1="2" y1="8" x2="2" y2="9" elevation="0"/>
  <line stroke="blue" x1="8" y1="2" x2="9" y2="2" elevation="0"/>
  <line stroke="red" x1="8" y1="2" x2="9" y2="3"/>
  <line stroke="blue" x1="8" y1="2" x2="8" y2="11" elevation="0"/>
  <line stroke="red" x1="3" y1="8" x2="2" y2="9"/>
  <line stroke="red" x1="3" y1="8" x2="4" y2="9"/>
  <line stroke="blue" x1="9" y1="0" x2="9" y2="1"/>
  <line stroke="red" x1="9" y1="1" x2="9" y2="2"/>
  <line stroke="red" x1="9" y1="1" x2="11" y2="1" elevation="1"/>
  <line stroke="blue" x1="2" y1="9" x2="4" y2="9" elevation="0"/>
  <line stroke="blue" x1="2" y1="9" x2="1" y2="10"/>
  <line stroke="blue" x1="9" y1="2" x2="9" y2="3"/>
  <line stroke="blue" x1="9" y1="2" x2="10" y2="2" elevation="0"/>
  <line stroke="red" x1="9" y1="3" x2="10" y2="2"/>
  <line stroke="red" x1="9" y1="3" x2="9" y2="10" elevation="1"/>
  <line stroke="blue" x1="4" y1="9" x2="5" y2="10"/>
  <line stroke="red" x1="1" y1="10" x2="0" y2="11"/>
  <line stroke="red" x1="1" y1="10" x2="5" y2="10" elevation="1"/>
  <line stroke="blue" x1="10" y1="2" x2="11" y2="1"/>
  <line stroke="blue" x1="10" y1="2" x2="10" y2="9" elevation="0"/>
  <line stroke="blue" x1="0" y1="11" x2="6" y2="11" elevation="0"/>
  <line stroke="red" x1="11" y1="1" x2="12" y2="0"/>
  <line stroke="red" x1="11" y1="1" x2="11" y2="8" elevation="1"/>
  <line stroke="red" x1="5" y1="10" x2="6" y2="11"/>
  <line stroke="red" x1="0" y1="12" x2="7" y2="12" elevation="1"/>
  <line stroke="blue" x1="12" y1="0" x2="12" y2="8" elevation="0"/>
  <line stroke="blue" x1="6" y1="11" x2="7" y2="12"/>
  <line stroke="blue" x1="0" y1="13" x2="7" y2="13" elevation="0"/>
  <line stroke="red" x1="13" y1="0" x2="13" y2="8" elevation="1"/>
  <line stroke="blue" x1="9" y1="10" x2="10" y2="9"/>
  <line stroke="red" x1="9" y1="10" x2="8" y2="11"/>
  <line stroke="red" x1="9" y1="10" x2="13" y2="10" elevation="1"/>
  <line stroke="red" x1="10" y1="9" x2="11" y2="8"/>
  <line stroke="blue" x1="10" y1="9" x2="12" y2="9" elevation="0"/>
  <line stroke="blue" x1="8" y1="11" x2="7" y2="12"/>
  <line stroke="blue" x1="8" y1="11" x2="14" y2="11" elevation="0"/>
  <line stroke="blue" x1="11" y1="8" x2="12" y2="8"/>
  <line stroke="red" x1="11" y1="8" x2="12" y2="9"/>
  <line stroke="red" x1="7" y1="12" x2="7" y2="13"/>
  <line stroke="red" x1="7" y1="12" x2="14" y2="12" elevation="1"/>
  <line stroke="blue" x1="12" y1="8" x2="12" y2="9" elevation="0"/>
  <line stroke="red" x1="12" y1="8" x2="13" y2="8"/>
  <line stroke="blue" x1="7" y1="13" x2="7" y2="14"/>
  <line stroke="blue" x1="7" y1="13" x2="14" y2="13" elevation="0"/>
  <line stroke="blue" x1="12" y1="9" x2="13" y2="10"/>
  <line stroke="blue" x1="13" y1="8" x2="14" y2="8"/>
  <line stroke="red" x1="13" y1="8" x2="13" y2="10" elevation="1"/>
  <line stroke="red" x1="13" y1="10" x2="14" y2="11"/>
</svg>""",
)

THREEFLAPSETSTWORIVERS = BoxPleatingCreasePatternExample(
    name="threeflapsetstworivers",
    grid_size=8,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="0" y2="375"/>
  <line stroke="black" x1="0" y1="0" x2="375" y2="0"/>
  <line stroke="red" x1="0" y1="0" x2="375" y2="375"/>
  <line stroke="green" x1="0" y1="375" x2="125" y2="375"/>
  <line stroke="black" x1="0" y1="375" x2="0" y2="500"/>
  <line stroke="black" x1="375" y1="0" x2="500" y2="0"/>
  <line stroke="green" x1="375" y1="0" x2="375" y2="375"/>
  <line stroke="red" x1="125" y1="375" x2="0" y2="500"/>
  <line stroke="green" x1="125" y1="375" x2="375" y2="375"/>
  <line stroke="red" x1="125" y1="375" x2="250" y2="500"/>
  <line stroke="green" x1="125" y1="375" x2="125" y2="625"/>
  <line stroke="black" x1="0" y1="500" x2="0" y2="625"/>
  <line stroke="red" x1="0" y1="500" x2="125" y2="625"/>
  <line stroke="green" x1="500" y1="0" x2="500" y2="500"/>
  <line stroke="black" x1="500" y1="0" x2="1000" y2="0"/>
  <line stroke="red" x1="375" y1="375" x2="500" y2="500"/>
  <line stroke="green" x1="250" y1="500" x2="500" y2="500"/>
  <line stroke="red" x1="250" y1="500" x2="375" y2="625"/>
  <line stroke="green" x1="250" y1="500" x2="250" y2="750"/>
  <line stroke="green" x1="0" y1="625" x2="125" y2="625"/>
  <line stroke="black" x1="0" y1="625" x2="0" y2="750"/>
  <line stroke="red" x1="125" y1="625" x2="250" y2="750"/>
  <line stroke="red" x1="500" y1="500" x2="375" y2="625"/>
  <line stroke="red" x1="500" y1="500" x2="625" y2="625"/>
  <line stroke="green" x1="500" y1="500" x2="500" y2="750"/>
  <line stroke="red" x1="500" y1="500" x2="1000" y2="0"/>
  <line stroke="green" x1="500" y1="500" x2="1000" y2="500"/>
  <line stroke="red" x1="375" y1="625" x2="250" y2="750"/>
  <line stroke="red" x1="375" y1="625" x2="500" y2="750"/>
  <line stroke="green" x1="0" y1="750" x2="250" y2="750"/>
  <line stroke="black" x1="0" y1="750" x2="0" y2="1000"/>
  <line stroke="green" x1="250" y1="750" x2="500" y2="750"/>
  <line stroke="red" x1="250" y1="750" x2="375" y2="875"/>
  <line stroke="red" x1="250" y1="750" x2="0" y2="1000"/>
  <line stroke="green" x1="250" y1="750" x2="250" y2="1000"/>
  <line stroke="green" x1="625" y1="625" x2="625" y2="875"/>
  <line stroke="green" x1="625" y1="625" x2="1000" y2="625"/>
  <line stroke="red" x1="625" y1="625" x2="1000" y2="1000"/>
  <line stroke="red" x1="500" y1="750" x2="625" y2="875"/>
  <line stroke="green" x1="375" y1="875" x2="375" y2="1000"/>
  <line stroke="green" x1="375" y1="875" x2="625" y2="875"/>
  <line stroke="red" x1="375" y1="875" x2="500" y2="1000"/>
  <line stroke="black" x1="0" y1="1000" x2="250" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="500"/>
  <line stroke="black" x1="250" y1="1000" x2="375" y2="1000"/>
  <line stroke="black" x1="375" y1="1000" x2="500" y2="1000"/>
  <line stroke="red" x1="625" y1="875" x2="500" y2="1000"/>
  <line stroke="green" x1="625" y1="875" x2="625" y2="1000"/>
  <line stroke="black" x1="500" y1="1000" x2="625" y2="1000"/>
  <line stroke="black" x1="1000" y1="500" x2="1000" y2="625"/>
  <line stroke="black" x1="625" y1="1000" x2="1000" y2="1000"/>
  <line stroke="black" x1="1000" y1="625" x2="1000" y2="1000"/>
</svg>""",
    base_svg="",
)

VERTICALFULLRIDGE = BoxPleatingCreasePatternExample(
    name="verticalfullridge",
    grid_size=16,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <line stroke="black" x1="0" y1="0" x2="0" y2="5"/>
  <line stroke="black" x1="0" y1="0" x2="5" y2="0"/>
  <line stroke="red" x1="0" y1="0" x2="5" y2="5"/>
  <line stroke="green" x1="0" y1="5" x2="5" y2="5"/>
  <line stroke="black" x1="0" y1="5" x2="0" y2="10"/>
  <line stroke="green" x1="5" y1="0" x2="5" y2="5"/>
  <line stroke="black" x1="5" y1="0" x2="8" y2="0"/>
  <line stroke="red" x1="5" y1="5" x2="0" y2="10"/>
  <line stroke="green" x1="5" y1="5" x2="5" y2="16"/>
  <line stroke="black" x1="8" y1="0" x2="11" y2="0"/>
  <line stroke="red" x1="8" y1="0" x2="8" y2="16"/>
  <line stroke="black" x1="0" y1="10" x2="0" y2="16"/>
  <line stroke="green" x1="11" y1="0" x2="11" y2="5"/>
  <line stroke="black" x1="11" y1="0" x2="16" y2="0"/>
  <line stroke="red" x1="11" y1="5" x2="16" y2="0"/>
  <line stroke="green" x1="11" y1="5" x2="16" y2="5"/>
  <line stroke="red" x1="11" y1="5" x2="16" y2="10"/>
  <line stroke="green" x1="11" y1="5" x2="11" y2="16"/>
  <line stroke="black" x1="0" y1="16" x2="5" y2="16"/>
  <line stroke="black" x1="16" y1="0" x2="16" y2="5"/>
  <line stroke="black" x1="5" y1="16" x2="8" y2="16"/>
  <line stroke="black" x1="16" y1="5" x2="16" y2="10"/>
  <line stroke="black" x1="8" y1="16" x2="11" y2="16"/>
  <line stroke="black" x1="16" y1="10" x2="16" y2="16"/>
  <line stroke="black" x1="11" y1="16" x2="16" y2="16"/>
  </svg>
    """,
)

XSHAPEDEDGEFLAP = BoxPleatingCreasePatternExample(
    name="xshapededgeflap",
    grid_size=28,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 28">
  <rect stroke="black" x="0" y="0" width="28" height="28"/>
  <line stroke="red" x1="0" y1="0" x2="12" y2="12"/>
  <line stroke="green" x1="0" y1="4" x2="12" y2="4"/>
  <line stroke="green" x1="4" y1="0" x2="4" y2="12"/>
  <line stroke="red" x1="0" y1="8" x2="8" y2="0"/>
  <line stroke="red" x1="0" y1="8" x2="4" y2="12"/>
  <line stroke="red" x1="8" y1="0" x2="12" y2="4"/>
  <line stroke="green" x1="0" y1="12" x2="28" y2="12"/>
  <line stroke="green" x1="12" y1="0" x2="12" y2="12"/>
  <line stroke="red" x1="4" y1="12" x2="12" y2="4"/>
  <line stroke="green" x1="0" y1="16" x2="28" y2="16"/>
  <line stroke="red" x1="5" y1="16" x2="0" y2="21"/>
  <line stroke="red" x1="5" y1="16" x2="13" y2="24"/>
  <line stroke="green" x1="5" y1="16" x2="5" y2="28"/>
  <line stroke="red" x1="12" y1="12" x2="24" y2="0"/>
  <line stroke="red" x1="13" y1="16" x2="5" y2="24"/>
  <line stroke="red" x1="13" y1="16" x2="18" y2="21"/>
  <line stroke="green" x1="13" y1="16" x2="13" y2="28"/>
  <line stroke="red" x1="24" y1="0" x2="28" y2="4"/>
  <line stroke="green" x1="5" y1="24" x2="13" y2="24"/>
  <line stroke="red" x1="5" y1="24" x2="9" y2="28"/>
  <line stroke="red" x1="13" y1="24" x2="9" y2="28"/>
  <line stroke="red" x1="18" y1="21" x2="23" y2="16"/>
  <line stroke="red" x1="18" y1="21" x2="18" y2="28"/>
  <line stroke="red" x1="23" y1="16" x2="28" y2="21"/>
  <line stroke="green" x1="23" y1="16" x2="23" y2="28"/>
  <line stroke="red" x1="23" y1="24" x2="28" y2="19"/>
  <line stroke="green" x1="23" y1="24" x2="28" y2="24"/>
  <line stroke="red" x1="23" y1="24" x2="27" y2="28"/>
  <line stroke="red" x1="27" y1="28" x2="28" y2="27"/>
</svg>
    """,
)

FULLRIDGE = BoxPleatingCreasePatternExample(
    name="fullridge",
    grid_size=16,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <rect stroke="black" x="0" y="0" width="16" height="16"/>
  <line stroke="red" x1="0" y1="1" x2="3" y2="1"/>
  <line stroke="green" x1="0" y1="3" x2="5" y2="3"/>
  <line stroke="red" x1="3" y1="1" x2="4" y2="0"/>
  <line stroke="red" x1="3" y1="1" x2="5" y2="3"/>
  <line stroke="red" x1="0" y1="4" x2="16" y2="4"/>
  <line stroke="green" x1="0" y1="5" x2="16" y2="5"/>
  <line stroke="green" x1="5" y1="0" x2="5" y2="3"/>
  <line stroke="red" x1="5" y1="3" x2="8" y2="0"/>
  <line stroke="green" x1="5" y1="3" x2="11" y2="3"/>
  <line stroke="green" x1="0" y1="8" x2="5" y2="8"/>
  <line stroke="red" x1="8" y1="0" x2="11" y2="3"/>
  <line stroke="red" x1="5" y1="8" x2="1" y2="12"/>
  <line stroke="red" x1="5" y1="8" x2="7" y2="10"/>
  <line stroke="green" x1="5" y1="8" x2="5" y2="12"/>
  <line stroke="green" x1="5" y1="8" x2="11" y2="8"/>
  <line stroke="green" x1="11" y1="0" x2="11" y2="3"/>
  <line stroke="red" x1="11" y1="3" x2="13" y2="1"/>
  <line stroke="green" x1="11" y1="3" x2="16" y2="3"/>
  <line stroke="red" x1="0" y1="12" x2="1" y2="12"/>
  <line stroke="red" x1="12" y1="0" x2="13" y2="1"/>
  <line stroke="red" x1="1" y1="12" x2="5" y2="16"/>
  <line stroke="red" x1="7" y1="10" x2="5" y2="12"/>
  <line stroke="red" x1="7" y1="10" x2="9" y2="10"/>
  <line stroke="green" x1="5" y1="12" x2="11" y2="12"/>
  <line stroke="green" x1="5" y1="12" x2="5" y2="16"/>
  <line stroke="red" x1="5" y1="12" x2="8" y2="15"/>
  <line stroke="red" x1="13" y1="1" x2="16" y2="1"/>
  <line stroke="red" x1="9" y1="10" x2="11" y2="8"/>
  <line stroke="red" x1="9" y1="10" x2="11" y2="12"/>
  <line stroke="green" x1="11" y1="8" x2="11" y2="12"/>
  <line stroke="green" x1="11" y1="8" x2="16" y2="8"/>
  <line stroke="red" x1="11" y1="8" x2="15" y2="12"/>
  <line stroke="red" x1="11" y1="12" x2="8" y2="15"/>
  <line stroke="green" x1="11" y1="12" x2="11" y2="16"/>
  <line stroke="red" x1="8" y1="15" x2="8" y2="16"/>
  <line stroke="red" x1="15" y1="12" x2="11" y2="16"/>
  <line stroke="red" x1="15" y1="12" x2="16" y2="12"/>
</svg>""",
)

CENTRALFOLD1 = BoxPleatingCreasePatternExample(
    name="centralfold1",
    grid_size=12,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12">
  <rect stroke="black" x="0" y="0" width="12" height="12"/>
  <line stroke="green" x1="0" y1="2" x2="5" y2="2"/>
  <line stroke="red" x1="3" y1="0" x2="5" y2="2"/>
  <line stroke="green" x1="5" y1="0" x2="5" y2="2"/>
  <line stroke="red" x1="5" y1="2" x2="6" y2="1"/>
  <line stroke="green" x1="5" y1="2" x2="7" y2="2"/>
  <line stroke="green" x1="0" y1="6" x2="6" y2="6"/>
  <line stroke="red" x1="6" y1="0" x2="6" y2="1"/>
  <line stroke="red" x1="6" y1="1" x2="7" y2="2"/>
  <line stroke="green" x1="7" y1="0" x2="7" y2="2"/>
  <line stroke="red" x1="7" y1="2" x2="9" y2="0"/>
  <line stroke="green" x1="7" y1="2" x2="12" y2="2"/>
  <line stroke="red" x1="6" y1="6" x2="0" y2="12"/>
  <line stroke="green" x1="6" y1="6" x2="6" y2="12"/>
  <line stroke="green" x1="6" y1="6" x2="12" y2="6"/>
  <line stroke="red" x1="6" y1="6" x2="12" y2="12"/>
</svg>""",
)

CENTRALFOLD2 = BoxPleatingCreasePatternExample(
    name="centralfold2",
    grid_size=36,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36">
  <rect stroke="black" x="0" y="0" width="36" height="36"/>
  <line stroke="red" x1="0" y1="0" x2="6" y2="6"/>
  <line stroke="green" x1="0" y1="6" x2="6" y2="6"/>
  <line stroke="green" x1="6" y1="0" x2="6" y2="6"/>
  <line stroke="red" x1="6" y1="6" x2="3" y2="9"/>
  <line stroke="green" x1="6" y1="6" x2="6" y2="12"/>
  <line stroke="red" x1="0" y1="9" x2="3" y2="9"/>
  <line stroke="red" x1="3" y1="9" x2="6" y2="12"/>
  <line stroke="green" x1="0" y1="12" x2="6" y2="12"/>
  <line stroke="red" x1="12" y1="0" x2="12" y2="6"/>
  <line stroke="red" x1="6" y1="12" x2="12" y2="6"/>
  <line stroke="green" x1="6" y1="12" x2="18" y2="12"/>
  <line stroke="red" x1="12" y1="6" x2="18" y2="12"/>
  <line stroke="green" x1="0" y1="15" x2="14" y2="15"/>
  <line stroke="green" x1="18" y1="0" x2="18" y2="12"/>
  <line stroke="red" x1="14" y1="15" x2="8" y2="21"/>
  <line stroke="red" x1="14" y1="15" x2="18" y2="19"/>
  <line stroke="green" x1="14" y1="15" x2="22" y2="15"/>
  <line stroke="green" x1="14" y1="15" x2="14" y2="27"/>
  <line stroke="red" x1="0" y1="21" x2="8" y2="21"/>
  <line stroke="red" x1="18" y1="12" x2="24" y2="6"/>
  <line stroke="green" x1="18" y1="12" x2="30" y2="12"/>
  <line stroke="red" x1="8" y1="21" x2="14" y2="27"/>
  <line stroke="red" x1="24" y1="0" x2="24" y2="6"/>
  <line stroke="red" x1="24" y1="6" x2="30" y2="12"/>
  <line stroke="red" x1="18" y1="19" x2="22" y2="15"/>
  <line stroke="red" x1="18" y1="19" x2="18" y2="36"/>
  <line stroke="green" x1="22" y1="15" x2="22" y2="27"/>
  <line stroke="red" x1="22" y1="15" x2="28" y2="21"/>
  <line stroke="green" x1="22" y1="15" x2="36" y2="15"/>
  <line stroke="green" x1="0" y1="27" x2="14" y2="27"/>
  <line stroke="green" x1="30" y1="0" x2="30" y2="6"/>
  <line stroke="red" x1="14" y1="27" x2="8" y2="33"/>
  <line stroke="green" x1="14" y1="27" x2="14" y2="36"/>
  <line stroke="green" x1="30" y1="6" x2="30" y2="12"/>
  <line stroke="red" x1="30" y1="6" x2="33" y2="9"/>
  <line stroke="red" x1="30" y1="6" x2="36" y2="0"/>
  <line stroke="green" x1="30" y1="6" x2="36" y2="6"/>
  <line stroke="red" x1="30" y1="12" x2="33" y2="9"/>
  <line stroke="green" x1="30" y1="12" x2="36" y2="12"/>
  <line stroke="red" x1="0" y1="33" x2="8" y2="33"/>
  <line stroke="red" x1="8" y1="33" x2="11" y2="36"/>
  <line stroke="red" x1="33" y1="9" x2="36" y2="9"/>
  <line stroke="red" x1="22" y1="27" x2="28" y2="21"/>
  <line stroke="green" x1="22" y1="27" x2="22" y2="36"/>
  <line stroke="red" x1="22" y1="27" x2="28" y2="33"/>
  <line stroke="green" x1="22" y1="27" x2="36" y2="27"/>
  <line stroke="red" x1="28" y1="21" x2="36" y2="21"/>
  <line stroke="red" x1="28" y1="33" x2="25" y2="36"/>
  <line stroke="red" x1="28" y1="33" x2="36" y2="33"/>
</svg>""",
)

CENTRALFOLD3 = BoxPleatingCreasePatternExample(
    name="centralfold3",
    grid_size=32,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect stroke="black" x="0" y="0" width="32" height="32"/>
  <line stroke="green" x1="0" y1="2" x2="14" y2="2"/>
  <line stroke="green" x1="0" y1="6" x2="4" y2="6"/>
  <line stroke="red" x1="4" y1="6" x2="5" y2="7"/>
  <line stroke="red" x1="4" y1="6" x2="0" y2="10"/>
  <line stroke="green" x1="4" y1="6" x2="4" y2="14"/>
  <line stroke="green" x1="4" y1="6" x2="28" y2="6"/>
  <line stroke="red" x1="5" y1="7" x2="6" y2="8"/>
  <line stroke="green" x1="5" y1="7" x2="5" y2="15"/>
  <line stroke="green" x1="5" y1="7" x2="27" y2="7"/>
  <line stroke="red" x1="0" y1="10" x2="4" y2="14"/>
  <line stroke="red" x1="6" y1="8" x2="7" y2="9"/>
  <line stroke="green" x1="6" y1="8" x2="6" y2="16"/>
  <line stroke="green" x1="6" y1="8" x2="26" y2="8"/>
  <line stroke="red" x1="7" y1="9" x2="8" y2="10"/>
  <line stroke="green" x1="7" y1="9" x2="7" y2="17"/>
  <line stroke="green" x1="7" y1="9" x2="25" y2="9"/>
  <line stroke="red" x1="12" y1="0" x2="14" y2="2"/>
  <line stroke="red" x1="8" y1="10" x2="12" y2="14"/>
  <line stroke="green" x1="8" y1="10" x2="16" y2="10"/>
  <line stroke="green" x1="8" y1="10" x2="8" y2="18"/>
  <line stroke="green" x1="0" y1="14" x2="4" y2="14"/>
  <line stroke="green" x1="14" y1="0" x2="14" y2="2"/>
  <line stroke="red" x1="14" y1="2" x2="16" y2="0"/>
  <line stroke="green" x1="14" y1="2" x2="18" y2="2"/>
  <line stroke="red" x1="4" y1="14" x2="5" y2="15"/>
  <line stroke="green" x1="0" y1="15" x2="5" y2="15"/>
  <line stroke="red" x1="5" y1="15" x2="6" y2="16"/>
  <line stroke="green" x1="0" y1="16" x2="6" y2="16"/>
  <line stroke="red" x1="16" y1="0" x2="18" y2="2"/>
  <line stroke="green" x1="0" y1="17" x2="7" y2="17"/>
  <line stroke="red" x1="6" y1="16" x2="7" y2="17"/>
  <line stroke="green" x1="0" y1="18" x2="6" y2="18"/>
  <line stroke="green" x1="18" y1="0" x2="18" y2="2"/>
  <line stroke="red" x1="18" y1="2" x2="20" y2="0"/>
  <line stroke="green" x1="18" y1="2" x2="32" y2="2"/>
  <line stroke="red" x1="7" y1="17" x2="8" y2="18"/>
  <line stroke="red" x1="12" y1="14" x2="16" y2="10"/>
  <line stroke="red" x1="12" y1="14" x2="8" y2="18"/>
  <line stroke="red" x1="12" y1="14" x2="16" y2="18"/>
  <line stroke="green" x1="16" y1="10" x2="16" y2="18"/>
  <line stroke="red" x1="16" y1="10" x2="20" y2="14"/>
  <line stroke="green" x1="16" y1="10" x2="24" y2="10"/>
  <line stroke="green" x1="6" y1="18" x2="8" y2="18"/>
  <line stroke="red" x1="6" y1="18" x2="1" y2="23"/>
  <line stroke="red" x1="6" y1="18" x2="11" y2="23"/>
  <line stroke="green" x1="6" y1="18" x2="6" y2="32"/>
  <line stroke="green" x1="8" y1="18" x2="16" y2="18"/>
  <line stroke="red" x1="0" y1="22" x2="1" y2="23"/>
  <line stroke="red" x1="1" y1="23" x2="1" y2="32"/>
  <line stroke="red" x1="16" y1="18" x2="20" y2="14"/>
  <line stroke="red" x1="16" y1="18" x2="11" y2="23"/>
  <line stroke="green" x1="16" y1="18" x2="24" y2="18"/>
  <line stroke="red" x1="16" y1="18" x2="21" y2="23"/>
  <line stroke="green" x1="16" y1="18" x2="16" y2="32"/>
  <line stroke="red" x1="20" y1="14" x2="24" y2="10"/>
  <line stroke="red" x1="20" y1="14" x2="24" y2="18"/>
  <line stroke="red" x1="11" y1="23" x2="11" y2="32"/>
  <line stroke="red" x1="24" y1="10" x2="25" y2="9"/>
  <line stroke="green" x1="24" y1="10" x2="24" y2="18"/>
  <line stroke="red" x1="25" y1="9" x2="26" y2="8"/>
  <line stroke="green" x1="25" y1="9" x2="25" y2="17"/>
  <line stroke="red" x1="26" y1="8" x2="27" y2="7"/>
  <line stroke="green" x1="26" y1="8" x2="26" y2="16"/>
  <line stroke="red" x1="27" y1="7" x2="28" y2="6"/>
  <line stroke="green" x1="27" y1="7" x2="27" y2="15"/>
  <line stroke="green" x1="28" y1="6" x2="28" y2="14"/>
  <line stroke="green" x1="28" y1="6" x2="32" y2="6"/>
  <line stroke="red" x1="28" y1="6" x2="32" y2="10"/>
  <line stroke="red" x1="24" y1="18" x2="25" y2="17"/>
  <line stroke="green" x1="24" y1="18" x2="26" y2="18"/>
  <line stroke="red" x1="25" y1="17" x2="26" y2="16"/>
  <line stroke="green" x1="25" y1="17" x2="32" y2="17"/>
  <line stroke="red" x1="26" y1="16" x2="27" y2="15"/>
  <line stroke="green" x1="26" y1="16" x2="32" y2="16"/>
  <line stroke="red" x1="27" y1="15" x2="28" y2="14"/>
  <line stroke="green" x1="27" y1="15" x2="32" y2="15"/>
  <line stroke="red" x1="21" y1="23" x2="26" y2="18"/>
  <line stroke="red" x1="21" y1="23" x2="21" y2="32"/>
  <line stroke="red" x1="28" y1="14" x2="32" y2="10"/>
  <line stroke="green" x1="28" y1="14" x2="32" y2="14"/>
  <line stroke="green" x1="26" y1="18" x2="32" y2="18"/>
  <line stroke="red" x1="26" y1="18" x2="31" y2="23"/>
  <line stroke="green" x1="26" y1="18" x2="26" y2="32"/>
  <line stroke="red" x1="31" y1="23" x2="32" y2="22"/>
  <line stroke="red" x1="31" y1="23" x2="31" y2="32"/>
</svg>""",
)

CENTRALFOLD4 = BoxPleatingCreasePatternExample(
    name="centralfold4",
    grid_size=30,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30">
  <rect stroke="black" x="0" y="0" width="30" height="30"/>
  <line stroke="red" x1="2" y1="0" x2="9" y2="7"/>
  <line stroke="green" x1="0" y1="7" x2="9" y2="7"/>
  <line stroke="green" x1="9" y1="0" x2="9" y2="7"/>
  <line stroke="red" x1="9" y1="7" x2="12" y2="4"/>
  <line stroke="green" x1="9" y1="7" x2="15" y2="7"/>
  <line stroke="red" x1="12" y1="0" x2="12" y2="4"/>
  <line stroke="red" x1="12" y1="4" x2="15" y2="7"/>
  <line stroke="green" x1="0" y1="13" x2="15" y2="13"/>
  <line stroke="green" x1="15" y1="0" x2="15" y2="7"/>
  <line stroke="red" x1="15" y1="7" x2="18" y2="4"/>
  <line stroke="green" x1="15" y1="7" x2="21" y2="7"/>
  <line stroke="red" x1="0" y1="17" x2="11" y2="17"/>
  <line stroke="red" x1="18" y1="0" x2="18" y2="4"/>
  <line stroke="red" x1="18" y1="4" x2="21" y2="7"/>
  <line stroke="red" x1="15" y1="13" x2="11" y2="17"/>
  <line stroke="red" x1="15" y1="13" x2="19" y2="17"/>
  <line stroke="green" x1="15" y1="13" x2="15" y2="21"/>
  <line stroke="green" x1="15" y1="13" x2="30" y2="13"/>
  <line stroke="red" x1="11" y1="17" x2="15" y2="21"/>
  <line stroke="green" x1="0" y1="21" x2="9" y2="21"/>
  <line stroke="green" x1="21" y1="0" x2="21" y2="7"/>
  <line stroke="red" x1="21" y1="7" x2="28" y2="0"/>
  <line stroke="green" x1="21" y1="7" x2="30" y2="7"/>
  <line stroke="green" x1="9" y1="21" x2="15" y2="21"/>
  <line stroke="red" x1="9" y1="21" x2="12" y2="24"/>
  <line stroke="green" x1="9" y1="21" x2="9" y2="27"/>
  <line stroke="red" x1="9" y1="21" x2="1" y2="29"/>
  <line stroke="red" x1="19" y1="17" x2="15" y2="21"/>
  <line stroke="red" x1="19" y1="17" x2="30" y2="17"/>
  <line stroke="red" x1="15" y1="21" x2="12" y2="24"/>
  <line stroke="green" x1="15" y1="21" x2="21" y2="21"/>
  <line stroke="red" x1="15" y1="21" x2="18" y2="24"/>
  <line stroke="green" x1="15" y1="21" x2="15" y2="27"/>
  <line stroke="red" x1="12" y1="24" x2="9" y2="27"/>
  <line stroke="red" x1="12" y1="24" x2="15" y2="27"/>
  <line stroke="green" x1="9" y1="27" x2="15" y2="27"/>
  <line stroke="green" x1="9" y1="27" x2="9" y2="30"/>
  <line stroke="red" x1="9" y1="27" x2="12" y2="30"/>
  <line stroke="red" x1="0" y1="29" x2="1" y2="29"/>
  <line stroke="red" x1="1" y1="29" x2="2" y2="30"/>
  <line stroke="red" x1="21" y1="21" x2="18" y2="24"/>
  <line stroke="green" x1="21" y1="21" x2="21" y2="27"/>
  <line stroke="green" x1="21" y1="21" x2="30" y2="21"/>
  <line stroke="red" x1="21" y1="21" x2="29" y2="29"/>
  <line stroke="red" x1="18" y1="24" x2="15" y2="27"/>
  <line stroke="red" x1="18" y1="24" x2="21" y2="27"/>
  <line stroke="red" x1="15" y1="27" x2="12" y2="30"/>
  <line stroke="green" x1="15" y1="27" x2="15" y2="30"/>
  <line stroke="green" x1="15" y1="27" x2="21" y2="27"/>
  <line stroke="red" x1="15" y1="27" x2="18" y2="30"/>
  <line stroke="red" x1="21" y1="27" x2="18" y2="30"/>
  <line stroke="green" x1="21" y1="27" x2="21" y2="30"/>
  <line stroke="red" x1="29" y1="29" x2="28" y2="30"/>
  <line stroke="red" x1="29" y1="29" x2="30" y2="29"/>
</svg>""",
)

CENTRALFOLD5 = BoxPleatingCreasePatternExample(
    name="centralfold5",
    grid_size=12,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12">
  <rect stroke="black" x="0" y="0" width="12" height="12"/>
  <line stroke="green" x1="0" y1="3" x2="6" y2="3"/>
  <line stroke="red" x1="3" y1="0" x2="6" y2="3"/>
  <line stroke="green" x1="6" y1="0" x2="6" y2="3"/>
  <line stroke="red" x1="6" y1="3" x2="9" y2="0"/>
  <line stroke="green" x1="6" y1="3" x2="12" y2="3"/>
  <line stroke="green" x1="0" y1="8" x2="4" y2="8"/>
  <line stroke="green" x1="4" y1="8" x2="8" y2="8"/>
  <line stroke="red" x1="4" y1="8" x2="6" y2="10"/>
  <line stroke="red" x1="4" y1="8" x2="0" y2="12"/>
  <line stroke="green" x1="4" y1="8" x2="4" y2="12"/>
  <line stroke="red" x1="8" y1="8" x2="6" y2="10"/>
  <line stroke="green" x1="8" y1="8" x2="8" y2="12"/>
  <line stroke="green" x1="8" y1="8" x2="12" y2="8"/>
  <line stroke="red" x1="8" y1="8" x2="12" y2="12"/>
  <line stroke="red" x1="6" y1="10" x2="6" y2="12"/>
</svg>""",
)

CENTRALFOLD6 = BoxPleatingCreasePatternExample(
    name="centralfold6",
    grid_size=6,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 6 6">
  <rect stroke="black" x="0" y="0" width="6" height="6"/>
  <line stroke="green" x1="0" y1="1" x2="3" y2="1"/>
  <line stroke="green" x1="0" y1="2" x2="1" y2="2"/>
  <line stroke="red" x1="2" y1="0" x2="3" y2="1"/>
  <line stroke="red" x1="1" y1="2" x2="0" y2="3"/>
  <line stroke="red" x1="1" y1="2" x2="3" y2="4"/>
  <line stroke="green" x1="1" y1="2" x2="5" y2="2"/>
  <line stroke="green" x1="1" y1="2" x2="1" y2="6"/>
  <line stroke="green" x1="3" y1="0" x2="3" y2="1"/>
  <line stroke="red" x1="3" y1="1" x2="4" y2="0"/>
  <line stroke="green" x1="3" y1="1" x2="6" y2="1"/>
  <line stroke="red" x1="3" y1="4" x2="5" y2="2"/>
  <line stroke="red" x1="3" y1="4" x2="3" y2="6"/>
  <line stroke="green" x1="5" y1="2" x2="6" y2="2"/>
  <line stroke="red" x1="5" y1="2" x2="6" y2="3"/>
  <line stroke="green" x1="5" y1="2" x2="5" y2="6"/>
</svg>""",
)

CENTRALFOLD7 = BoxPleatingCreasePatternExample(
    name="centralfold7",
    grid_size=14,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14">
  <rect stroke="black" x="0" y="0" width="14" height="14"/>
  <line stroke="red" x1="0" y1="0" x2="3" y2="3"/>
  <line stroke="green" x1="0" y1="3" x2="3" y2="3"/>
  <line stroke="green" x1="3" y1="0" x2="3" y2="3"/>
  <line stroke="red" x1="4" y1="0" x2="4" y2="2"/>
  <line stroke="red" x1="3" y1="3" x2="4" y2="2"/>
  <line stroke="green" x1="3" y1="3" x2="5" y2="3"/>
  <line stroke="red" x1="4" y1="2" x2="5" y2="3"/>
  <line stroke="green" x1="5" y1="0" x2="5" y2="3"/>
  <line stroke="red" x1="5" y1="3" x2="7" y2="1"/>
  <line stroke="green" x1="5" y1="3" x2="9" y2="3"/>
  <line stroke="green" x1="0" y1="6" x2="7" y2="6"/>
  <line stroke="red" x1="7" y1="0" x2="7" y2="1"/>
  <line stroke="red" x1="7" y1="1" x2="9" y2="3"/>
  <line stroke="green" x1="9" y1="0" x2="9" y2="3"/>
  <line stroke="red" x1="7" y1="6" x2="3" y2="10"/>
  <line stroke="red" x1="7" y1="6" x2="11" y2="10"/>
  <line stroke="green" x1="7" y1="6" x2="14" y2="6"/>
  <line stroke="green" x1="7" y1="6" x2="7" y2="14"/>
  <line stroke="red" x1="9" y1="3" x2="10" y2="2"/>
  <line stroke="green" x1="9" y1="3" x2="11" y2="3"/>
  <line stroke="red" x1="0" y1="10" x2="3" y2="10"/>
  <line stroke="red" x1="10" y1="0" x2="10" y2="2"/>
  <line stroke="red" x1="10" y1="2" x2="11" y2="3"/>
  <line stroke="red" x1="3" y1="10" x2="7" y2="14"/>
  <line stroke="green" x1="11" y1="0" x2="11" y2="3"/>
  <line stroke="red" x1="11" y1="3" x2="14" y2="0"/>
  <line stroke="green" x1="11" y1="3" x2="14" y2="3"/>
  <line stroke="red" x1="11" y1="10" x2="7" y2="14"/>
  <line stroke="red" x1="11" y1="10" x2="14" y2="10"/>
</svg>""",
)

CENTRALFOLD8 = BoxPleatingCreasePatternExample(
    name="centralfold8",
    grid_size=22,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 22 22">
  <rect stroke="black" x="0" y="0" width="22" height="22"/>
  <line stroke="green" x1="8" y1="0" x2="8" y2="22"/>
  <line stroke="red" x1="11" y1="0" x2="11" y2="22"/>
  <line stroke="green" x1="14" y1="0" x2="14" y2="22"/>
</svg>""",
)

CENTRALFOLD9 = BoxPleatingCreasePatternExample(
    name="centralfold9",
    grid_size=12,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12">
  <rect stroke="black" x="0" y="0" width="12" height="12"/>
  <line stroke="green" x1="0" y1="6" x2="12" y2="6"/>
  <line stroke="red" x1="0" y1="8" x2="12" y2="8"/>
  <line stroke="green" x1="0" y1="10" x2="6" y2="10"/>
  <line stroke="red" x1="0" y1="11" x2="5" y2="11"/>
  <line stroke="red" x1="6" y1="10" x2="5" y2="11"/>
  <line stroke="red" x1="6" y1="10" x2="7" y2="11"/>
  <line stroke="green" x1="6" y1="10" x2="6" y2="12"/>
  <line stroke="green" x1="6" y1="10" x2="12" y2="10"/>
  <line stroke="red" x1="5" y1="11" x2="6" y2="12"/>
  <line stroke="red" x1="7" y1="11" x2="6" y2="12"/>
  <line stroke="red" x1="7" y1="11" x2="12" y2="11"/>
</svg>""",
)

CENTRALFOLD10 = BoxPleatingCreasePatternExample(
    name="centralfold10",
    grid_size=4,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4 4">
  <line stroke="black" x1="0" y1="0" x2="0" y2="1"/>
  <line stroke="black" x1="0" y1="0" x2="4" y2="0"/>
  <line stroke="black" x1="0" y1="1" x2="0" y2="2"/>
  <line stroke="green" x1="0" y1="1" x2="2" y2="1"/>
  <line stroke="red" x1="0" y1="2" x2="1" y2="2"/>
  <line stroke="black" x1="0" y1="2" x2="0" y2="3"/>
  <line stroke="red" x1="1" y1="2" x2="2" y2="1"/>
  <line stroke="red" x1="1" y1="2" x2="2" y2="3"/>
  <line stroke="green" x1="2" y1="1" x2="2" y2="3"/>
  <line stroke="red" x1="2" y1="1" x2="3" y2="2"/>
  <line stroke="green" x1="2" y1="1" x2="4" y2="1"/>
  <line stroke="green" x1="0" y1="3" x2="2" y2="3"/>
  <line stroke="black" x1="0" y1="3" x2="0" y2="4"/>
  <line stroke="red" x1="2" y1="3" x2="3" y2="2"/>
  <line stroke="green" x1="2" y1="3" x2="4" y2="3"/>
  <line stroke="red" x1="3" y1="2" x2="4" y2="2"/>
  <line stroke="black" x1="0" y1="4" x2="4" y2="4"/>
  <line stroke="black" x1="4" y1="0" x2="4" y2="1"/>
  <line stroke="black" x1="4" y1="1" x2="4" y2="2"/>
  <line stroke="black" x1="4" y1="2" x2="4" y2="3"/>
  <line stroke="black" x1="4" y1="3" x2="4" y2="4"/>
</svg>""",
)

CENTRALFOLD11 = BoxPleatingCreasePatternExample(
    name="centralfold11",
    grid_size=38,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 38 38">
  <rect stroke="black" x="0" y="0" width="38" height="38"/>
  <line stroke="red" x1="0" y1="1" x2="4" y2="1"/>
  <line stroke="red" x1="4" y1="1" x2="5" y2="0"/>
  <line stroke="red" x1="4" y1="1" x2="12" y2="9"/>
  <line stroke="green" x1="0" y1="9" x2="12" y2="9"/>
  <line stroke="green" x1="12" y1="0" x2="12" y2="19"/>
  <line stroke="red" x1="0" y1="14" x2="7" y2="14"/>
  <line stroke="red" x1="12" y1="9" x2="7" y2="14"/>
  <line stroke="red" x1="7" y1="14" x2="12" y2="19"/>
  <line stroke="green" x1="0" y1="19" x2="38" y2="19"/>
  <line stroke="red" x1="19" y1="0" x2="19" y2="12"/>
  <line stroke="green" x1="0" y1="21" x2="38" y2="21"/>
  <line stroke="red" x1="5" y1="21" x2="0" y2="26"/>
  <line stroke="green" x1="5" y1="21" x2="5" y2="31"/>
  <line stroke="red" x1="5" y1="21" x2="22" y2="38"/>
  <line stroke="red" x1="12" y1="19" x2="19" y2="12"/>
  <line stroke="red" x1="19" y1="12" x2="26" y2="19"/>
  <line stroke="green" x1="6" y1="22" x2="6" y2="32"/>
  <line stroke="green" x1="6" y1="22" x2="32" y2="22"/>
  <line stroke="green" x1="7" y1="23" x2="7" y2="33"/>
  <line stroke="green" x1="7" y1="23" x2="31" y2="23"/>
  <line stroke="red" x1="0" y1="26" x2="7" y2="33"/>
  <line stroke="green" x1="26" y1="0" x2="26" y2="19"/>
  <line stroke="red" x1="26" y1="9" x2="31" y2="14"/>
  <line stroke="red" x1="26" y1="9" x2="34" y2="1"/>
  <line stroke="green" x1="26" y1="9" x2="38" y2="9"/>
  <line stroke="red" x1="17" y1="23" x2="19" y2="25"/>
  <line stroke="red" x1="17" y1="23" x2="7" y2="33"/>
  <line stroke="green" x1="17" y1="23" x2="17" y2="33"/>
  <line stroke="green" x1="18" y1="24" x2="20" y2="24"/>
  <line stroke="green" x1="18" y1="24" x2="18" y2="34"/>
  <line stroke="green" x1="0" y1="31" x2="5" y2="31"/>
  <line stroke="red" x1="21" y1="23" x2="19" y2="25"/>
  <line stroke="green" x1="21" y1="23" x2="21" y2="33"/>
  <line stroke="red" x1="21" y1="23" x2="31" y2="33"/>
  <line stroke="green" x1="20" y1="24" x2="20" y2="34"/>
  <line stroke="green" x1="19" y1="25" x2="19" y2="38"/>
  <line stroke="green" x1="0" y1="32" x2="6" y2="32"/>
  <line stroke="red" x1="26" y1="19" x2="31" y2="14"/>
  <line stroke="green" x1="0" y1="33" x2="17" y2="33"/>
  <line stroke="red" x1="33" y1="0" x2="34" y2="1"/>
  <line stroke="green" x1="0" y1="34" x2="18" y2="34"/>
  <line stroke="red" x1="31" y1="14" x2="38" y2="14"/>
  <line stroke="red" x1="34" y1="1" x2="38" y2="1"/>
  <line stroke="green" x1="0" y1="35" x2="38" y2="35"/>
  <line stroke="red" x1="1" y1="35" x2="0" y2="36"/>
  <line stroke="green" x1="1" y1="35" x2="1" y2="38"/>
  <line stroke="red" x1="1" y1="35" x2="4" y2="38"/>
  <line stroke="green" x1="31" y1="23" x2="31" y2="33"/>
  <line stroke="green" x1="32" y1="22" x2="32" y2="32"/>
  <line stroke="green" x1="21" y1="33" x2="38" y2="33"/>
  <line stroke="red" x1="33" y1="21" x2="16" y2="38"/>
  <line stroke="green" x1="33" y1="21" x2="33" y2="31"/>
  <line stroke="red" x1="33" y1="21" x2="38" y2="26"/>
  <line stroke="green" x1="20" y1="34" x2="38" y2="34"/>
  <line stroke="green" x1="32" y1="32" x2="38" y2="32"/>
  <line stroke="red" x1="31" y1="33" x2="38" y2="26"/>
  <line stroke="green" x1="33" y1="31" x2="38" y2="31"/>
  <line stroke="red" x1="37" y1="35" x2="34" y2="38"/>
  <line stroke="red" x1="37" y1="35" x2="38" y2="36"/>
  <line stroke="green" x1="37" y1="35" x2="37" y2="38"/>
</svg>""",
)

RIVERONEFLAP = BoxPleatingCreasePatternExample(
    name="riveroneflap",
    grid_size=8,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="0" y2="125"/>
  <line stroke="black" x1="0" y1="0" x2="125" y2="0"/>
  <line stroke="black" x1="0" y1="125" x2="0" y2="250"/>
  <line stroke="red" x1="0" y1="125" x2="125" y2="250"/>
  <line stroke="green" x1="125" y1="0" x2="125" y2="250"/>
  <line stroke="black" x1="125" y1="0" x2="375" y2="0"/>
  <line stroke="green" x1="0" y1="250" x2="125" y2="250"/>
  <line stroke="black" x1="0" y1="250" x2="0" y2="375"/>
  <line stroke="red" x1="125" y1="250" x2="375" y2="0"/>
  <line stroke="green" x1="125" y1="250" x2="500" y2="250"/>
  <line stroke="black" x1="0" y1="375" x2="0" y2="500"/>
  <line stroke="red" x1="0" y1="375" x2="375" y2="375"/>
  <line stroke="black" x1="375" y1="0" x2="625" y2="0"/>
  <line stroke="red" x1="375" y1="0" x2="625" y2="250"/>
  <line stroke="green" x1="0" y1="500" x2="500" y2="500"/>
  <line stroke="black" x1="0" y1="500" x2="0" y2="1000"/>
  <line stroke="red" x1="375" y1="375" x2="500" y2="250"/>
  <line stroke="red" x1="375" y1="375" x2="500" y2="500"/>
  <line stroke="green" x1="500" y1="250" x2="625" y2="250"/>
  <line stroke="green" x1="500" y1="250" x2="500" y2="500"/>
  <line stroke="red" x1="500" y1="250" x2="625" y2="375"/>
  <line stroke="green" x1="625" y1="0" x2="625" y2="250"/>
  <line stroke="black" x1="625" y1="0" x2="750" y2="0"/>
  <line stroke="red" x1="625" y1="0" x2="750" y2="125"/>
  <line stroke="red" x1="625" y1="250" x2="750" y2="125"/>
  <line stroke="green" x1="625" y1="250" x2="750" y2="250"/>
  <line stroke="red" x1="500" y1="500" x2="625" y2="375"/>
  <line stroke="red" x1="500" y1="500" x2="625" y2="625"/>
  <line stroke="green" x1="500" y1="500" x2="750" y2="500"/>
  <line stroke="red" x1="500" y1="500" x2="0" y2="1000"/>
  <line stroke="green" x1="500" y1="500" x2="500" y2="1000"/>
  <line stroke="red" x1="625" y1="375" x2="750" y2="250"/>
  <line stroke="red" x1="625" y1="375" x2="750" y2="500"/>
  <line stroke="black" x1="750" y1="0" x2="875" y2="0"/>
  <line stroke="red" x1="750" y1="0" x2="875" y2="125"/>
  <line stroke="green" x1="750" y1="125" x2="875" y2="125"/>
  <line stroke="green" x1="750" y1="250" x2="750" y2="375"/>
  <line stroke="red" x1="750" y1="250" x2="875" y2="125"/>
  <line stroke="green" x1="750" y1="375" x2="750" y2="500"/>
  <line stroke="red" x1="750" y1="375" x2="875" y2="250"/>
  <line stroke="green" x1="750" y1="375" x2="1000" y2="375"/>
  <line stroke="red" x1="750" y1="375" x2="1000" y2="625"/>
  <line stroke="green" x1="875" y1="0" x2="875" y2="125"/>
  <line stroke="black" x1="875" y1="0" x2="1000" y2="0"/>
  <line stroke="red" x1="625" y1="625" x2="750" y2="500"/>
  <line stroke="red" x1="625" y1="625" x2="625" y2="1000"/>
  <line stroke="green" x1="875" y1="125" x2="875" y2="250"/>
  <line stroke="red" x1="875" y1="125" x2="1000" y2="0"/>
  <line stroke="green" x1="875" y1="125" x2="1000" y2="125"/>
  <line stroke="red" x1="875" y1="125" x2="1000" y2="250"/>
  <line stroke="green" x1="750" y1="500" x2="750" y2="875"/>
  <line stroke="red" x1="875" y1="250" x2="1000" y2="375"/>
  <line stroke="black" x1="0" y1="1000" x2="500" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="125"/>
  <line stroke="black" x1="1000" y1="125" x2="1000" y2="250"/>
  <line stroke="black" x1="1000" y1="250" x2="1000" y2="375"/>
  <line stroke="black" x1="1000" y1="375" x2="1000" y2="625"/>
  <line stroke="black" x1="500" y1="1000" x2="625" y2="1000"/>
  <line stroke="red" x1="750" y1="875" x2="1000" y2="625"/>
  <line stroke="green" x1="750" y1="875" x2="750" y2="1000"/>
  <line stroke="red" x1="750" y1="875" x2="875" y2="1000"/>
  <line stroke="green" x1="750" y1="875" x2="1000" y2="875"/>
  <line stroke="black" x1="625" y1="1000" x2="750" y2="1000"/>
  <line stroke="black" x1="1000" y1="625" x2="1000" y2="875"/>
  <line stroke="black" x1="750" y1="1000" x2="875" y2="1000"/>
  <line stroke="black" x1="875" y1="1000" x2="1000" y2="1000"/>
  <line stroke="black" x1="1000" y1="875" x2="1000" y2="1000"/>
</svg>""",
)

INTERLEAVEDRIDGE = BoxPleatingCreasePatternExample(
    name="interleavedridge",
    grid_size=20,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
  <rect stroke="black" x="0" y="0" width="20" height="20"/>
  <line stroke="green" x1="0" y1="4" x2="20" y2="4"/>
  <line stroke="red" x1="0" y1="6" x2="20" y2="6"/>
  <line stroke="green" x1="0" y1="8" x2="20" y2="8"/>
  <line stroke="green" x1="0" y1="12" x2="3" y2="12"/>
  <line stroke="red" x1="3" y1="12" x2="0" y2="15"/>
  <line stroke="red" x1="3" y1="12" x2="7" y2="16"/>
  <line stroke="green" x1="3" y1="12" x2="3" y2="20"/>
  <line stroke="green" x1="3" y1="12" x2="17" y2="12"/>
  <line stroke="red" x1="7" y1="16" x2="3" y2="20"/>
  <line stroke="red" x1="7" y1="16" x2="13" y2="16"/>
  <line stroke="red" x1="13" y1="16" x2="17" y2="12"/>
  <line stroke="red" x1="13" y1="16" x2="17" y2="20"/>
  <line stroke="green" x1="17" y1="12" x2="20" y2="12"/>
  <line stroke="red" x1="17" y1="12" x2="20" y2="15"/>
  <line stroke="green" x1="17" y1="12" x2="17" y2="20"/>
</svg>
""",
)

BORDERPLEATNOVERTEX_TEST = BoxPleatingCreasePatternExample(
    name="borderpleatnovertex_test",
    grid_size=32,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect stroke="black" x="0" y="0" width="32" height="32"/>
  <line stroke="green" x1="0" y1="7" x2="8" y2="7"/>
  <line stroke="red" x1="8" y1="7" x2="4" y2="11"/>
  <line stroke="red" x1="8" y1="7" x2="12" y2="11"/>
  <line stroke="green" x1="8" y1="7" x2="8" y2="15"/>
  <line stroke="green" x1="8" y1="7" x2="16" y2="7"/>
  <line stroke="red" x1="0" y1="11" x2="4" y2="11"/>
  <line stroke="red" x1="4" y1="11" x2="8" y2="15"/>
  <line stroke="green" x1="0" y1="15" x2="8" y2="15"/>
  <line stroke="red" x1="12" y1="11" x2="8" y2="15"/>
  <line stroke="red" x1="12" y1="11" x2="16" y2="7"/>
  <line stroke="red" x1="12" y1="11" x2="16" y2="15"/>
  <line stroke="green" x1="8" y1="15" x2="16" y2="15"/>
  <line stroke="green" x1="16" y1="7" x2="16" y2="15"/>
  <line stroke="red" x1="16" y1="7" x2="20" y2="11"/>
  <line stroke="green" x1="16" y1="7" x2="24" y2="7"/>
  <line stroke="green" x1="0" y1="19" x2="16" y2="19"/>
  <line stroke="red" x1="16" y1="15" x2="20" y2="11"/>
  <line stroke="green" x1="16" y1="15" x2="24" y2="15"/>
  <line stroke="red" x1="20" y1="11" x2="24" y2="7"/>
  <line stroke="red" x1="20" y1="11" x2="24" y2="15"/>
  <line stroke="red" x1="0" y1="23" x2="12" y2="23"/>
  <line stroke="red" x1="16" y1="19" x2="12" y2="23"/>
  <line stroke="red" x1="16" y1="19" x2="20" y2="23"/>
  <line stroke="green" x1="16" y1="19" x2="16" y2="27"/>
  <line stroke="green" x1="16" y1="19" x2="32" y2="19"/>
  <line stroke="green" x1="24" y1="7" x2="24" y2="15"/>
  <line stroke="red" x1="24" y1="7" x2="28" y2="11"/>
  <line stroke="green" x1="24" y1="7" x2="32" y2="7"/>
  <line stroke="red" x1="12" y1="23" x2="16" y2="27"/>
  <line stroke="green" x1="0" y1="27" x2="4" y2="27"/>
  <line stroke="red" x1="4" y1="27" x2="0" y2="31"/>
  <line stroke="green" x1="4" y1="27" x2="16" y2="27"/>
  <line stroke="red" x1="4" y1="27" x2="8" y2="31"/>
  <line stroke="green" x1="4" y1="27" x2="4" y2="32"/>
  <line stroke="red" x1="24" y1="15" x2="28" y2="11"/>
  <line stroke="green" x1="24" y1="15" x2="32" y2="15"/>
  <line stroke="red" x1="28" y1="11" x2="32" y2="11"/>
  <line stroke="red" x1="20" y1="23" x2="16" y2="27"/>
  <line stroke="red" x1="20" y1="23" x2="32" y2="23"/>
  <line stroke="red" x1="16" y1="27" x2="12" y2="31"/>
  <line stroke="green" x1="16" y1="27" x2="16" y2="32"/>
  <line stroke="red" x1="16" y1="27" x2="20" y2="31"/>
  <line stroke="green" x1="16" y1="27" x2="28" y2="27"/>
  <line stroke="red" x1="8" y1="31" x2="7" y2="32"/>
  <line stroke="red" x1="8" y1="31" x2="12" y2="31"/>
  <line stroke="red" x1="12" y1="31" x2="13" y2="32"/>
  <line stroke="red" x1="20" y1="31" x2="19" y2="32"/>
  <line stroke="red" x1="20" y1="31" x2="24" y2="31"/>
  <line stroke="red" x1="28" y1="27" x2="24" y2="31"/>
  <line stroke="green" x1="28" y1="27" x2="32" y2="27"/>
  <line stroke="green" x1="28" y1="27" x2="28" y2="32"/>
  <line stroke="red" x1="28" y1="27" x2="32" y2="31"/>
  <line stroke="red" x1="24" y1="31" x2="25" y2="32"/>
</svg>
""",
)

CENTRALFOLDONLYPLEATS = BoxPleatingCreasePatternExample(
    name="centralfoldonlypleats",
    grid_size=16,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <line stroke="black" x1="0" y1="0" x2="0" y2="4"/>
  <line stroke="black" x1="0" y1="0" x2="4" y2="0"/>
  <line stroke="red" x1="0" y1="0" x2="4" y2="4"/>
  <line stroke="green" x1="0" y1="4" x2="2" y2="4"/>
  <line stroke="black" x1="0" y1="4" x2="0" y2="6"/>
  <line stroke="green" x1="4" y1="0" x2="4" y2="4"/>
  <line stroke="black" x1="4" y1="0" x2="8" y2="0"/>
  <line stroke="green" x1="2" y1="4" x2="4" y2="4"/>
  <line stroke="red" x1="2" y1="4" x2="0" y2="6"/>
  <line stroke="red" x1="2" y1="4" x2="4" y2="6"/>
  <line stroke="green" x1="2" y1="4" x2="2" y2="8"/>
  <line stroke="green" x1="4" y1="4" x2="6" y2="4"/>
  <line stroke="red" x1="4" y1="4" x2="8" y2="0"/>
  <line stroke="black" x1="0" y1="6" x2="0" y2="8"/>
  <line stroke="red" x1="0" y1="6" x2="2" y2="8"/>
  <line stroke="red" x1="4" y1="6" x2="6" y2="4"/>
  <line stroke="red" x1="4" y1="6" x2="2" y2="8"/>
  <line stroke="red" x1="4" y1="6" x2="6" y2="8"/>
  <line stroke="green" x1="6" y1="4" x2="6" y2="8"/>
  <line stroke="red" x1="6" y1="4" x2="8" y2="6"/>
  <line stroke="green" x1="6" y1="4" x2="10" y2="4"/>
  <line stroke="green" x1="0" y1="8" x2="2" y2="8"/>
  <line stroke="black" x1="0" y1="8" x2="0" y2="12"/>
  <line stroke="black" x1="8" y1="0" x2="12" y2="0"/>
  <line stroke="red" x1="8" y1="0" x2="12" y2="4"/>
  <line stroke="green" x1="2" y1="8" x2="6" y2="8"/>
  <line stroke="red" x1="6" y1="8" x2="8" y2="6"/>
  <line stroke="green" x1="6" y1="8" x2="10" y2="8"/>
  <line stroke="red" x1="8" y1="6" x2="10" y2="4"/>
  <line stroke="red" x1="8" y1="6" x2="10" y2="8"/>
  <line stroke="green" x1="10" y1="4" x2="12" y2="4"/>
  <line stroke="green" x1="10" y1="4" x2="10" y2="8"/>
  <line stroke="red" x1="10" y1="4" x2="12" y2="6"/>
  <line stroke="green" x1="0" y1="12" x2="4" y2="12"/>
  <line stroke="black" x1="0" y1="12" x2="0" y2="16"/>
  <line stroke="green" x1="12" y1="0" x2="12" y2="4"/>
  <line stroke="black" x1="12" y1="0" x2="16" y2="0"/>
  <line stroke="red" x1="4" y1="12" x2="0" y2="16"/>
  <line stroke="green" x1="4" y1="12" x2="4" y2="16"/>
  <line stroke="green" x1="4" y1="12" x2="12" y2="12"/>
  <line stroke="red" x1="4" y1="12" x2="8" y2="16"/>
  <line stroke="green" x1="12" y1="4" x2="14" y2="4"/>
  <line stroke="red" x1="12" y1="4" x2="16" y2="0"/>
  <line stroke="red" x1="10" y1="8" x2="12" y2="6"/>
  <line stroke="green" x1="10" y1="8" x2="14" y2="8"/>
  <line stroke="red" x1="12" y1="6" x2="14" y2="4"/>
  <line stroke="red" x1="12" y1="6" x2="14" y2="8"/>
  <line stroke="green" x1="14" y1="4" x2="14" y2="8"/>
  <line stroke="green" x1="14" y1="4" x2="16" y2="4"/>
  <line stroke="red" x1="14" y1="4" x2="16" y2="6"/>
  <line stroke="black" x1="0" y1="16" x2="4" y2="16"/>
  <line stroke="black" x1="16" y1="0" x2="16" y2="4"/>
  <line stroke="red" x1="14" y1="8" x2="16" y2="6"/>
  <line stroke="green" x1="14" y1="8" x2="16" y2="8"/>
  <line stroke="black" x1="4" y1="16" x2="8" y2="16"/>
  <line stroke="black" x1="16" y1="4" x2="16" y2="6"/>
  <line stroke="red" x1="12" y1="12" x2="8" y2="16"/>
  <line stroke="green" x1="12" y1="12" x2="12" y2="16"/>
  <line stroke="green" x1="12" y1="12" x2="16" y2="12"/>
  <line stroke="red" x1="12" y1="12" x2="16" y2="16"/>
  <line stroke="black" x1="16" y1="6" x2="16" y2="8"/>
  <line stroke="black" x1="8" y1="16" x2="12" y2="16"/>
  <line stroke="black" x1="16" y1="8" x2="16" y2="12"/>
  <line stroke="black" x1="12" y1="16" x2="16" y2="16"/>
  <line stroke="black" x1="16" y1="12" x2="16" y2="16"/>
</svg>
""",
)

CENTRALFOLDCOMMONSYMHINGE = BoxPleatingCreasePatternExample(
    name="centralfoldcommonsymhinge",
    grid_size=10,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">
  <rect stroke="black" x="0" y="0" width="10" height="10"/>
  <line stroke="red" x1="0" y1="0" x2="1" y2="1"/>
  <line stroke="red" x1="1" y1="1" x2="3" y2="3"/>
  <line stroke="green" x1="1" y1="1" x2="1" y2="5"/>
  <line stroke="green" x1="1" y1="1" x2="5" y2="1"/>
  <line stroke="red" x1="0" y1="4" x2="1" y2="5"/>
  <line stroke="red" x1="3" y1="3" x2="1" y2="5"/>
  <line stroke="red" x1="3" y1="3" x2="5" y2="1"/>
  <line stroke="red" x1="3" y1="3" x2="5" y2="5"/>
  <line stroke="green" x1="0" y1="5" x2="1" y2="5"/>
  <line stroke="green" x1="1" y1="5" x2="5" y2="5"/>
  <line stroke="green" x1="5" y1="1" x2="5" y2="5"/>
  <line stroke="red" x1="5" y1="1" x2="7" y2="3"/>
  <line stroke="green" x1="5" y1="1" x2="9" y2="1"/>
  <line stroke="red" x1="5" y1="5" x2="7" y2="3"/>
  <line stroke="red" x1="5" y1="5" x2="0" y2="10"/>
  <line stroke="green" x1="5" y1="5" x2="9" y2="5"/>
  <line stroke="green" x1="5" y1="5" x2="5" y2="10"/>
  <line stroke="red" x1="5" y1="5" x2="10" y2="10"/>
  <line stroke="red" x1="7" y1="3" x2="9" y2="1"/>
  <line stroke="red" x1="7" y1="3" x2="9" y2="5"/>
  <line stroke="red" x1="9" y1="1" x2="10" y2="0"/>
  <line stroke="green" x1="9" y1="1" x2="9" y2="5"/>
  <line stroke="red" x1="9" y1="5" x2="10" y2="4"/>
  <line stroke="green" x1="9" y1="5" x2="10" y2="5"/>
</svg>""",
    base_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">
  <rect stroke="black" x="0" y="0" width="10" height="10"/>
  <line stroke="red" x1="0" y1="0" x2="1" y2="1"/>
  <line stroke="blue" x1="0" y1="1" x2="1" y2="1"/>
  <line stroke="blue" x1="1" y1="0" x2="1" y2="1"/>
  <line stroke="blue" x1="1" y1="1" x2="2" y2="2"/>
  <line stroke="red" x1="0" y1="2" x2="2" y2="2"/>
  <line stroke="red" x1="2" y1="0" x2="2" y2="2"/>
  <line stroke="red" x1="2" y1="2" x2="3" y2="3"/>
  <line stroke="blue" x1="0" y1="3" x2="3" y2="3"/>
  <line stroke="blue" x1="3" y1="0" x2="3" y2="3"/>
  <line stroke="red" x1="0" y1="4" x2="2" y2="4"/>
  <line stroke="blue" x1="0" y1="4" x2="1" y2="5"/>
  <line stroke="red" x1="4" y1="0" x2="4" y2="2"/>
  <line stroke="red" x1="3" y1="3" x2="2" y2="4"/>
  <line stroke="red" x1="3" y1="3" x2="4" y2="2"/>
  <line stroke="red" x1="3" y1="3" x2="4" y2="4"/>
  <line stroke="red" x1="3" y1="3" x2="5" y2="3"/>
  <line stroke="blue" x1="3" y1="3" x2="3" y2="7"/>
  <line stroke="blue" x1="2" y1="4" x2="1" y2="5"/>
  <line stroke="red" x1="2" y1="4" x2="2" y2="8"/>
  <line stroke="blue" x1="4" y1="2" x2="5" y2="3"/>
  <line stroke="red" x1="4" y1="2" x2="6" y2="2"/>
  <line stroke="red" x1="0" y1="5" x2="1" y2="5"/>
  <line stroke="blue" x1="1" y1="5" x2="1" y2="9"/>
  <line stroke="blue" x1="4" y1="4" x2="5" y2="3"/>
  <line stroke="red" x1="4" y1="4" x2="4" y2="6"/>
  <line stroke="red" x1="4" y1="4" x2="6" y2="4"/>
  <line stroke="blue" x1="5" y1="3" x2="6" y2="2"/>
  <line stroke="blue" x1="5" y1="3" x2="6" y2="4"/>
  <line stroke="red" x1="5" y1="3" x2="7" y2="3"/>
  <line stroke="red" x1="6" y1="0" x2="6" y2="2"/>
  <line stroke="red" x1="6" y1="2" x2="7" y2="3"/>
  <line stroke="blue" x1="7" y1="0" x2="7" y2="3"/>
  <line stroke="red" x1="4" y1="6" x2="3" y2="7"/>
  <line stroke="red" x1="4" y1="6" x2="6" y2="6"/>
  <line stroke="blue" x1="4" y1="6" x2="5" y2="7"/>
  <line stroke="red" x1="6" y1="4" x2="7" y2="3"/>
  <line stroke="red" x1="6" y1="4" x2="6" y2="6"/>
  <line stroke="blue" x1="3" y1="7" x2="2" y2="8"/>
  <line stroke="blue" x1="3" y1="7" x2="5" y2="7"/>
  <line stroke="red" x1="7" y1="3" x2="8" y2="2"/>
  <line stroke="red" x1="7" y1="3" x2="8" y2="4"/>
  <line stroke="blue" x1="7" y1="3" x2="7" y2="7"/>
  <line stroke="blue" x1="7" y1="3" x2="10" y2="3"/>
  <line stroke="red" x1="8" y1="0" x2="8" y2="2"/>
  <line stroke="red" x1="2" y1="8" x2="4" y2="8"/>
  <line stroke="red" x1="2" y1="8" x2="1" y2="9"/>
  <line stroke="blue" x1="8" y1="2" x2="9" y2="1"/>
  <line stroke="red" x1="8" y1="2" x2="10" y2="2"/>
  <line stroke="blue" x1="6" y1="6" x2="5" y2="7"/>
  <line stroke="red" x1="6" y1="6" x2="7" y2="7"/>
  <line stroke="red" x1="5" y1="7" x2="4" y2="8"/>
  <line stroke="blue" x1="5" y1="7" x2="7" y2="7"/>
  <line stroke="red" x1="5" y1="7" x2="6" y2="8"/>
  <line stroke="red" x1="4" y1="8" x2="6" y2="8"/>
  <line stroke="blue" x1="4" y1="8" x2="5" y2="9"/>
  <line stroke="blue" x1="8" y1="4" x2="9" y2="5"/>
  <line stroke="red" x1="8" y1="4" x2="10" y2="4"/>
  <line stroke="red" x1="8" y1="4" x2="8" y2="8"/>
  <line stroke="blue" x1="9" y1="0" x2="9" y2="1"/>
  <line stroke="blue" x1="1" y1="9" x2="0" y2="10"/>
  <line stroke="blue" x1="1" y1="9" x2="5" y2="9"/>
  <line stroke="red" x1="9" y1="1" x2="10" y2="0"/>
  <line stroke="blue" x1="9" y1="1" x2="10" y2="1"/>
  <line stroke="blue" x1="7" y1="7" x2="8" y2="8"/>
  <line stroke="blue" x1="6" y1="8" x2="5" y2="9"/>
  <line stroke="red" x1="6" y1="8" x2="8" y2="8"/>
  <line stroke="red" x1="5" y1="9" x2="4" y2="10"/>
  <line stroke="red" x1="5" y1="9" x2="6" y2="10"/>
  <line stroke="blue" x1="5" y1="9" x2="9" y2="9"/>
  <line stroke="blue" x1="9" y1="5" x2="10" y2="4"/>
  <line stroke="red" x1="9" y1="5" x2="10" y2="5"/>
  <line stroke="blue" x1="9" y1="5" x2="9" y2="9"/>
  <line stroke="red" x1="8" y1="8" x2="9" y2="9"/>
  <line stroke="blue" x1="9" y1="9" x2="10" y2="10"/>
</svg>""",
    central_crease_removed=True,
)

CENTRALFLAP4HINGE = BoxPleatingCreasePatternExample(
    name="centralflap4hinge",
    grid_size=8,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8">
  <line stroke="black" x1="0" y1="0" x2="0" y2="2"/>
  <line stroke="black" x1="0" y1="0" x2="2" y2="0"/>
  <line stroke="red" x1="0" y1="0" x2="2" y2="2"/>
  <line stroke="green" x1="0" y1="2" x2="2" y2="2"/>
  <line stroke="red" x1="0" y1="2" x2="1" y2="3"/>
  <line stroke="black" x1="0" y1="2" x2="0" y2="4"/>
  <line stroke="green" x1="2" y1="0" x2="2" y2="2"/>
  <line stroke="black" x1="2" y1="0" x2="4" y2="0"/>
  <line stroke="red" x1="2" y1="2" x2="1" y2="3"/>
  <line stroke="red" x1="2" y1="2" x2="4" y2="0"/>
  <line stroke="red" x1="2" y1="2" x2="3" y2="3"/>
  <line stroke="green" x1="2" y1="2" x2="2" y2="4"/>
  <line stroke="green" x1="2" y1="2" x2="4" y2="2"/>
  <line stroke="red" x1="1" y1="3" x2="0" y2="4"/>
  <line stroke="red" x1="1" y1="3" x2="2" y2="4"/>
  <line stroke="green" x1="0" y1="4" x2="2" y2="4"/>
  <line stroke="black" x1="0" y1="4" x2="0" y2="6"/>
  <line stroke="black" x1="4" y1="0" x2="6" y2="0"/>
  <line stroke="red" x1="4" y1="0" x2="6" y2="2"/>
  <line stroke="red" x1="3" y1="3" x2="2" y2="4"/>
  <line stroke="red" x1="3" y1="3" x2="4" y2="2"/>
  <line stroke="red" x1="3" y1="3" x2="4" y2="4"/>
  <line stroke="green" x1="2" y1="4" x2="4" y2="4"/>
  <line stroke="green" x1="4" y1="2" x2="4" y2="4"/>
  <line stroke="red" x1="4" y1="2" x2="5" y2="3"/>
  <line stroke="green" x1="4" y1="2" x2="6" y2="2"/>
  <line stroke="red" x1="4" y1="4" x2="5" y2="3"/>
  <line stroke="green" x1="4" y1="4" x2="6" y2="4"/>
  <line stroke="red" x1="5" y1="3" x2="6" y2="2"/>
  <line stroke="red" x1="5" y1="3" x2="6" y2="4"/>
  <line stroke="green" x1="0" y1="6" x2="2" y2="6"/>
  <line stroke="black" x1="0" y1="6" x2="0" y2="8"/>
  <line stroke="green" x1="6" y1="0" x2="6" y2="2"/>
  <line stroke="black" x1="6" y1="0" x2="8" y2="0"/>
  <line stroke="red" x1="2" y1="6" x2="0" y2="8"/>
  <line stroke="green" x1="2" y1="6" x2="2" y2="8"/>
  <line stroke="green" x1="2" y1="6" x2="6" y2="6"/>
  <line stroke="red" x1="2" y1="6" x2="4" y2="8"/>
  <line stroke="green" x1="6" y1="2" x2="6" y2="4"/>
  <line stroke="red" x1="6" y1="2" x2="7" y2="3"/>
  <line stroke="red" x1="6" y1="2" x2="8" y2="0"/>
  <line stroke="green" x1="6" y1="2" x2="8" y2="2"/>
  <line stroke="red" x1="6" y1="4" x2="7" y2="3"/>
  <line stroke="green" x1="6" y1="4" x2="8" y2="4"/>
  <line stroke="red" x1="7" y1="3" x2="8" y2="2"/>
  <line stroke="red" x1="7" y1="3" x2="8" y2="4"/>
  <line stroke="black" x1="0" y1="8" x2="2" y2="8"/>
  <line stroke="black" x1="8" y1="0" x2="8" y2="2"/>
  <line stroke="black" x1="2" y1="8" x2="4" y2="8"/>
  <line stroke="black" x1="8" y1="2" x2="8" y2="4"/>
  <line stroke="red" x1="6" y1="6" x2="4" y2="8"/>
  <line stroke="green" x1="6" y1="6" x2="6" y2="8"/>
  <line stroke="green" x1="6" y1="6" x2="8" y2="6"/>
  <line stroke="red" x1="6" y1="6" x2="8" y2="8"/>
  <line stroke="black" x1="4" y1="8" x2="6" y2="8"/>
  <line stroke="black" x1="8" y1="4" x2="8" y2="6"/>
  <line stroke="black" x1="6" y1="8" x2="8" y2="8"/>
  <line stroke="black" x1="8" y1="6" x2="8" y2="8"/>
</svg>
""",
)

CENTRALRIDGENOVERTICES = BoxPleatingCreasePatternExample(
    name="central_ridge_no_vertices",
    grid_size=9,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 9 9">
  <rect stroke="black" x="0" y="0" width="9" height="9"/>
  <line stroke="red" x1="0" y1="0" x2="5" y2="5"/>
  <line stroke="green" x1="0" y1="5" x2="5" y2="5"/>
  <line stroke="green" x1="5" y1="0" x2="5" y2="5"/>
  <line stroke="red" x1="5" y1="5" x2="1" y2="9"/>
  <line stroke="green" x1="5" y1="5" x2="5" y2="9"/>
  <line stroke="red" x1="0" y1="8" x2="1" y2="9"/>
  <line stroke="red" x1="8" y1="0" x2="8" y2="9"/>
</svg>""",
)

HINGENOVERTICES = BoxPleatingCreasePatternExample(
    name="hinge_no_vertices",
    grid_size=8,
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8">
  <rect stroke="black" x="0" y="0" width="8" height="8"/>
  <line stroke="green" x1="0" y1="1" x2="2" y2="1"/>
  <line stroke="red" x1="1" y1="0" x2="2" y2="1"/>
  <line stroke="red" x1="0" y1="2" x2="8" y2="2"/>
  <line stroke="green" x1="2" y1="0" x2="2" y2="1"/>
  <line stroke="red" x1="2" y1="1" x2="3" y2="0"/>
  <line stroke="green" x1="2" y1="1" x2="6" y2="1"/>
  <line stroke="green" x1="0" y1="3" x2="8" y2="3"/>
  <line stroke="green" x1="0" y1="5" x2="3" y2="5"/>
  <line stroke="red" x1="5" y1="0" x2="6" y2="1"/>
  <line stroke="red" x1="3" y1="5" x2="1" y2="7"/>
  <line stroke="green" x1="3" y1="5" x2="5" y2="5"/>
  <line stroke="red" x1="3" y1="5" x2="4" y2="6"/>
  <line stroke="green" x1="3" y1="5" x2="3" y2="8"/>
  <line stroke="green" x1="6" y1="0" x2="6" y2="1"/>
  <line stroke="red" x1="6" y1="1" x2="7" y2="0"/>
  <line stroke="green" x1="6" y1="1" x2="8" y2="1"/>
  <line stroke="red" x1="0" y1="7" x2="1" y2="7"/>
  <line stroke="red" x1="1" y1="7" x2="2" y2="8"/>
  <line stroke="red" x1="5" y1="5" x2="4" y2="6"/>
  <line stroke="green" x1="5" y1="5" x2="5" y2="8"/>
  <line stroke="green" x1="5" y1="5" x2="8" y2="5"/>
  <line stroke="red" x1="5" y1="5" x2="7" y2="7"/>
  <line stroke="red" x1="4" y1="6" x2="4" y2="8"/>
  <line stroke="red" x1="7" y1="7" x2="6" y2="8"/>
  <line stroke="red" x1="7" y1="7" x2="8" y2="7"/>
</svg>""",
)

HUMAN = BoxPleatingCreasePatternExample(
    name="human",
    grid_size=8,
    central_crease_removed=True,
    tree_data={
        "version": "0.7",
        "design": {
            "title": "human",
            "mode": "tree",
            "description": "",
            "layout": {
                "sheet": {"type": "rect", "height": 16, "width": 16},
                "flaps": [
                    {"id": 2, "x": 8, "y": 6, "width": 0, "height": 0},
                    {"id": 3, "x": 10, "y": 3, "width": 0, "height": 0},
                    {"id": 4, "x": 8, "y": 12, "width": 0, "height": 0},
                    {"id": 5, "x": 11, "y": 9, "width": 0, "height": 0},
                    {"id": 6, "x": 4, "y": 9, "width": 0, "height": 0},
                ],
                "stretches": [],
            },
            "tree": {
                "sheet": {"type": "rect", "height": 20, "width": 20},
                "nodes": [
                    {"id": 0, "name": "", "x": 10, "y": 10},
                    {"id": 1, "name": "", "x": 10, "y": 13},
                    {"id": 2, "name": "", "x": 7, "y": 4},
                    {"id": 3, "name": "", "x": 13, "y": 4},
                    {"id": 4, "name": "", "x": 10, "y": 15},
                    {"id": 5, "name": "", "x": 14, "y": 11},
                    {"id": 6, "name": "", "x": 6, "y": 11},
                ],
                "edges": [
                    {"n1": 0, "n2": 1, "length": 2},
                    {"n1": 0, "n2": 2, "length": 8},
                    {"n1": 0, "n2": 3, "length": 8},
                    {"n1": 1, "n2": 6, "length": 6},
                    {"n1": 1, "n2": 5, "length": 6},
                    {"n1": 1, "n2": 4, "length": 2},
                ],
            },
        },
    },
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8">
  <line stroke="black" x1="0" y1="0" x2="0" y2="3"/>
  <line stroke="black" x1="0" y1="0" x2="3" y2="0"/>
  <line stroke="red" x1="0" y1="0" x2="3" y2="3"/>
  <line stroke="black" x1="0" y1="3" x2="0" y2="4"/>
  <line stroke="green" x1="0" y1="3" x2="3" y2="3"/>
  <line stroke="black" x1="3" y1="0" x2="4" y2="0"/>
  <line stroke="green" x1="3" y1="0" x2="3" y2="3"/>
  <line stroke="green" x1="0" y1="4" x2="4" y2="4"/>
  <line stroke="black" x1="0" y1="4" x2="0" y2="8"/>
  <line stroke="red" x1="4" y1="0" x2="4" y2="2"/>
  <line stroke="black" x1="4" y1="0" x2="5" y2="0"/>
  <line stroke="red" x1="3" y1="3" x2="4" y2="2"/>
  <line stroke="green" x1="3" y1="3" x2="5" y2="3"/>
  <line stroke="red" x1="4" y1="2" x2="5" y2="3"/>
  <line stroke="green" x1="5" y1="0" x2="5" y2="3"/>
  <line stroke="black" x1="5" y1="0" x2="8" y2="0"/>
  <line stroke="red" x1="4" y1="4" x2="0" y2="8"/>
  <line stroke="green" x1="4" y1="4" x2="4" y2="8"/>
  <line stroke="green" x1="4" y1="4" x2="8" y2="4"/>
  <line stroke="red" x1="4" y1="4" x2="8" y2="8"/>
  <line stroke="red" x1="5" y1="3" x2="8" y2="0"/>
  <line stroke="green" x1="5" y1="3" x2="8" y2="3"/>
  <line stroke="black" x1="0" y1="8" x2="4" y2="8"/>
  <line stroke="black" x1="8" y1="0" x2="8" y2="3"/>
  <line stroke="black" x1="8" y1="3" x2="8" y2="4"/>
  <line stroke="black" x1="4" y1="8" x2="8" y2="8"/>
  <line stroke="black" x1="8" y1="4" x2="8" y2="8"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="red" x1="0" y1="0" x2="125" y2="125"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="375"/>
  <line stroke="black" x1="0" y1="0" x2="500" y2="0"/>
  <line stroke="blue" x1="125" y1="125" x2="250" y2="250"/>
  <line stroke="red" x1="125" y1="125" x2="125" y2="375"/>
  <line stroke="red" x1="125" y1="125" x2="375" y2="125"/>
  <line stroke="blue" x1="250" y1="250" x2="250" y2="375"/>
  <line stroke="red" x1="250" y1="250" x2="375" y2="375"/>
  <line stroke="blue" x1="250" y1="250" x2="500" y2="250"/>
  <line stroke="blue" x1="0" y1="375" x2="125" y2="375"/>
  <line stroke="black" x1="0" y1="375" x2="0" y2="1000"/>
  <line stroke="red" x1="125" y1="375" x2="250" y2="375"/>
  <line stroke="red" x1="125" y1="375" x2="125" y2="875"/>
  <line stroke="blue" x1="375" y1="125" x2="500" y2="0"/>
  <line stroke="red" x1="375" y1="125" x2="500" y2="250"/>
  <line stroke="red" x1="375" y1="125" x2="625" y2="125"/>
  <line stroke="blue" x1="250" y1="375" x2="375" y2="375"/>
  <line stroke="blue" x1="250" y1="375" x2="250" y2="750"/>
  <line stroke="blue" x1="500" y1="0" x2="625" y2="125"/>
  <line stroke="black" x1="500" y1="0" x2="1000" y2="0"/>
  <line stroke="red" x1="375" y1="375" x2="500" y2="250"/>
  <line stroke="red" x1="375" y1="375" x2="375" y2="625"/>
  <line stroke="red" x1="500" y1="250" x2="625" y2="125"/>
  <line stroke="red" x1="500" y1="250" x2="625" y2="375"/>
  <line stroke="blue" x1="500" y1="250" x2="750" y2="250"/>
  <line stroke="red" x1="625" y1="125" x2="875" y2="125"/>
  <line stroke="red" x1="375" y1="625" x2="250" y2="750"/>
  <line stroke="red" x1="375" y1="625" x2="625" y2="625"/>
  <line stroke="blue" x1="375" y1="625" x2="500" y2="750"/>
  <line stroke="red" x1="625" y1="375" x2="750" y2="250"/>
  <line stroke="blue" x1="625" y1="375" x2="750" y2="375"/>
  <line stroke="red" x1="625" y1="375" x2="625" y2="625"/>
  <line stroke="blue" x1="250" y1="750" x2="125" y2="875"/>
  <line stroke="blue" x1="250" y1="750" x2="500" y2="750"/>
  <line stroke="blue" x1="750" y1="250" x2="750" y2="375"/>
  <line stroke="blue" x1="750" y1="250" x2="875" y2="125"/>
  <line stroke="red" x1="750" y1="375" x2="875" y2="375"/>
  <line stroke="blue" x1="750" y1="375" x2="750" y2="750"/>
  <line stroke="red" x1="125" y1="875" x2="375" y2="875"/>
  <line stroke="red" x1="125" y1="875" x2="0" y2="1000"/>
  <line stroke="blue" x1="625" y1="625" x2="500" y2="750"/>
  <line stroke="red" x1="625" y1="625" x2="750" y2="750"/>
  <line stroke="red" x1="875" y1="125" x2="875" y2="375"/>
  <line stroke="red" x1="875" y1="125" x2="1000" y2="0"/>
  <line stroke="red" x1="500" y1="750" x2="375" y2="875"/>
  <line stroke="blue" x1="500" y1="750" x2="750" y2="750"/>
  <line stroke="red" x1="500" y1="750" x2="625" y2="875"/>
  <line stroke="red" x1="375" y1="875" x2="625" y2="875"/>
  <line stroke="blue" x1="375" y1="875" x2="500" y2="1000"/>
  <line stroke="blue" x1="875" y1="375" x2="1000" y2="375"/>
  <line stroke="red" x1="875" y1="375" x2="875" y2="875"/>
  <line stroke="black" x1="0" y1="1000" x2="500" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="375"/>
  <line stroke="blue" x1="750" y1="750" x2="875" y2="875"/>
  <line stroke="black" x1="1000" y1="375" x2="1000" y2="1000"/>
  <line stroke="blue" x1="625" y1="875" x2="500" y2="1000"/>
  <line stroke="red" x1="625" y1="875" x2="875" y2="875"/>
  <line stroke="black" x1="500" y1="1000" x2="1000" y2="1000"/>
  <line stroke="red" x1="875" y1="875" x2="1000" y2="1000"/>
</svg>""",
)

HUMAN_WITH_CENTER = BoxPleatingCreasePatternExample(
    name="human_with_center",
    grid_size=16,
    tree_data={
        "version": "0.7",
        "design": {
            "title": "human_with_center",
            "mode": "tree",
            "description": "",
            "layout": {
                "sheet": {"type": "rect", "height": 16, "width": 16},
                "flaps": [
                    {"id": 2, "x": 8, "y": 6, "width": 0, "height": 0},
                    {"id": 3, "x": 10, "y": 3, "width": 0, "height": 0},
                    {"id": 4, "x": 8, "y": 12, "width": 0, "height": 0},
                    {"id": 5, "x": 11, "y": 9, "width": 0, "height": 0},
                    {"id": 6, "x": 4, "y": 9, "width": 0, "height": 0},
                ],
                "stretches": [],
            },
            "tree": {
                "sheet": {"type": "rect", "height": 20, "width": 20},
                "nodes": [
                    {"id": 0, "name": "", "x": 10, "y": 10},
                    {"id": 1, "name": "", "x": 10, "y": 13},
                    {"id": 2, "name": "", "x": 6, "y": 4},
                    {"id": 3, "name": "", "x": 13, "y": 4},
                    {"id": 4, "name": "", "x": 10, "y": 15},
                    {"id": 5, "name": "", "x": 14, "y": 11},
                    {"id": 6, "name": "", "x": 5, "y": 11},
                ],
                "edges": [
                    {"n1": 0, "n2": 1, "length": 2},
                    {"n1": 0, "n2": 2, "length": 8},
                    {"n1": 0, "n2": 3, "length": 8},
                    {"n1": 1, "n2": 4, "length": 2},
                    {"n1": 1, "n2": 5, "length": 6},
                    {"n1": 1, "n2": 6, "length": 6},
                ],
            },
        },
    },
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <line stroke="black" x1="0" y1="0" x2="0" y2="6"/>
  <line stroke="black" x1="0" y1="0" x2="6" y2="0"/>
  <line stroke="red" x1="0" y1="0" x2="6" y2="6"/>
  <line stroke="black" x1="0" y1="6" x2="0" y2="8"/>
  <line stroke="green" x1="0" y1="6" x2="6" y2="6"/>
  <line stroke="black" x1="6" y1="0" x2="8" y2="0"/>
  <line stroke="green" x1="6" y1="0" x2="6" y2="6"/>
  <line stroke="green" x1="0" y1="8" x2="8" y2="8"/>
  <line stroke="black" x1="0" y1="8" x2="0" y2="16"/>
  <line stroke="red" x1="8" y1="0" x2="8" y2="4"/>
  <line stroke="black" x1="8" y1="0" x2="10" y2="0"/>
  <line stroke="red" x1="6" y1="6" x2="8" y2="4"/>
  <line stroke="green" x1="6" y1="6" x2="10" y2="6"/>
  <line stroke="red" x1="8" y1="4" x2="10" y2="6"/>
  <line stroke="green" x1="10" y1="0" x2="10" y2="6"/>
  <line stroke="black" x1="10" y1="0" x2="16" y2="0"/>
  <line stroke="red" x1="8" y1="8" x2="0" y2="16"/>
  <line stroke="green" x1="8" y1="8" x2="8" y2="16"/>
  <line stroke="green" x1="8" y1="8" x2="16" y2="8"/>
  <line stroke="red" x1="8" y1="8" x2="16" y2="16"/>
  <line stroke="red" x1="10" y1="6" x2="16" y2="0"/>
  <line stroke="green" x1="10" y1="6" x2="16" y2="6"/>
  <line stroke="black" x1="0" y1="16" x2="8" y2="16"/>
  <line stroke="black" x1="16" y1="0" x2="16" y2="6"/>
  <line stroke="black" x1="16" y1="6" x2="16" y2="8"/>
  <line stroke="black" x1="8" y1="16" x2="16" y2="16"/>
  <line stroke="black" x1="16" y1="8" x2="16" y2="16"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <line stroke="red" x1="0" y1="0" x2="1" y2="1"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="6"/>
  <line stroke="black" x1="0" y1="0" x2="8" y2="0"/>
  <line stroke="blue" x1="1" y1="1" x2="2" y2="2"/>
  <line stroke="red" x1="1" y1="1" x2="1" y2="6"/>
  <line stroke="red" x1="1" y1="1" x2="8" y2="1"/>
  <line stroke="red" x1="2" y1="2" x2="3" y2="3"/>
  <line stroke="blue" x1="2" y1="2" x2="2" y2="6"/>
  <line stroke="blue" x1="2" y1="2" x2="8" y2="2"/>
  <line stroke="blue" x1="3" y1="3" x2="4" y2="4"/>
  <line stroke="red" x1="3" y1="3" x2="3" y2="6"/>
  <line stroke="red" x1="3" y1="3" x2="8" y2="3"/>
  <line stroke="red" x1="4" y1="4" x2="5" y2="5"/>
  <line stroke="blue" x1="4" y1="4" x2="4" y2="6"/>
  <line stroke="blue" x1="4" y1="4" x2="8" y2="4"/>
  <line stroke="blue" x1="0" y1="6" x2="1" y2="6"/>
  <line stroke="black" x1="0" y1="6" x2="0" y2="16"/>
  <line stroke="red" x1="1" y1="6" x2="2" y2="6"/>
  <line stroke="red" x1="1" y1="6" x2="1" y2="15"/>
  <line stroke="blue" x1="2" y1="6" x2="3" y2="6"/>
  <line stroke="blue" x1="2" y1="6" x2="2" y2="14"/>
  <line stroke="red" x1="3" y1="6" x2="4" y2="6"/>
  <line stroke="red" x1="3" y1="6" x2="3" y2="13"/>
  <line stroke="red" x1="5" y1="5" x2="5" y2="6"/>
  <line stroke="blue" x1="5" y1="5" x2="6" y2="6"/>
  <line stroke="red" x1="5" y1="5" x2="7" y2="5"/>
  <line stroke="blue" x1="4" y1="6" x2="5" y2="6"/>
  <line stroke="blue" x1="4" y1="6" x2="4" y2="12"/>
  <line stroke="red" x1="5" y1="6" x2="6" y2="6"/>
  <line stroke="red" x1="5" y1="6" x2="5" y2="11"/>
  <line stroke="red" x1="8" y1="0" x2="8" y2="1"/>
  <line stroke="black" x1="8" y1="0" x2="16" y2="0"/>
  <line stroke="blue" x1="8" y1="1" x2="8" y2="2"/>
  <line stroke="red" x1="8" y1="1" x2="15" y2="1"/>
  <line stroke="red" x1="8" y1="2" x2="8" y2="3"/>
  <line stroke="blue" x1="8" y1="2" x2="14" y2="2"/>
  <line stroke="blue" x1="6" y1="6" x2="7" y2="5"/>
  <line stroke="blue" x1="6" y1="6" x2="6" y2="10"/>
  <line stroke="blue" x1="8" y1="3" x2="8" y2="4"/>
  <line stroke="red" x1="8" y1="3" x2="13" y2="3"/>
  <line stroke="red" x1="7" y1="5" x2="8" y2="4"/>
  <line stroke="red" x1="7" y1="5" x2="7" y2="9"/>
  <line stroke="red" x1="8" y1="4" x2="9" y2="5"/>
  <line stroke="blue" x1="8" y1="4" x2="8" y2="8"/>
  <line stroke="blue" x1="8" y1="4" x2="12" y2="4"/>
  <line stroke="blue" x1="9" y1="5" x2="10" y2="6"/>
  <line stroke="red" x1="9" y1="5" x2="11" y2="5"/>
  <line stroke="red" x1="9" y1="5" x2="9" y2="9"/>
  <line stroke="blue" x1="8" y1="8" x2="7" y2="9"/>
  <line stroke="red" x1="8" y1="8" x2="8" y2="9"/>
  <line stroke="blue" x1="8" y1="8" x2="9" y2="9"/>
  <line stroke="red" x1="7" y1="9" x2="6" y2="10"/>
  <line stroke="red" x1="7" y1="9" x2="8" y2="9"/>
  <line stroke="blue" x1="6" y1="10" x2="5" y2="11"/>
  <line stroke="blue" x1="6" y1="10" x2="8" y2="10"/>
  <line stroke="blue" x1="10" y1="6" x2="11" y2="5"/>
  <line stroke="red" x1="10" y1="6" x2="11" y2="6"/>
  <line stroke="blue" x1="10" y1="6" x2="10" y2="10"/>
  <line stroke="red" x1="8" y1="9" x2="9" y2="9"/>
  <line stroke="blue" x1="8" y1="9" x2="8" y2="10"/>
  <line stroke="red" x1="5" y1="11" x2="4" y2="12"/>
  <line stroke="red" x1="5" y1="11" x2="8" y2="11"/>
  <line stroke="red" x1="11" y1="5" x2="11" y2="6"/>
  <line stroke="red" x1="11" y1="5" x2="12" y2="4"/>
  <line stroke="blue" x1="11" y1="6" x2="12" y2="6"/>
  <line stroke="red" x1="11" y1="6" x2="11" y2="11"/>
  <line stroke="blue" x1="4" y1="12" x2="3" y2="13"/>
  <line stroke="blue" x1="4" y1="12" x2="8" y2="12"/>
  <line stroke="blue" x1="12" y1="4" x2="13" y2="3"/>
  <line stroke="blue" x1="12" y1="4" x2="12" y2="6"/>
  <line stroke="red" x1="9" y1="9" x2="10" y2="10"/>
  <line stroke="red" x1="8" y1="10" x2="8" y2="11"/>
  <line stroke="blue" x1="8" y1="10" x2="10" y2="10"/>
  <line stroke="red" x1="3" y1="13" x2="2" y2="14"/>
  <line stroke="red" x1="3" y1="13" x2="8" y2="13"/>
  <line stroke="red" x1="13" y1="3" x2="14" y2="2"/>
  <line stroke="red" x1="13" y1="3" x2="13" y2="6"/>
  <line stroke="red" x1="12" y1="6" x2="13" y2="6"/>
  <line stroke="blue" x1="12" y1="6" x2="12" y2="12"/>
  <line stroke="blue" x1="8" y1="11" x2="8" y2="12"/>
  <line stroke="red" x1="8" y1="11" x2="11" y2="11"/>
  <line stroke="blue" x1="2" y1="14" x2="1" y2="15"/>
  <line stroke="blue" x1="2" y1="14" x2="8" y2="14"/>
  <line stroke="blue" x1="10" y1="10" x2="11" y2="11"/>
  <line stroke="blue" x1="14" y1="2" x2="15" y2="1"/>
  <line stroke="blue" x1="14" y1="2" x2="14" y2="6"/>
  <line stroke="blue" x1="13" y1="6" x2="14" y2="6"/>
  <line stroke="red" x1="13" y1="6" x2="13" y2="13"/>
  <line stroke="red" x1="8" y1="12" x2="8" y2="13"/>
  <line stroke="blue" x1="8" y1="12" x2="12" y2="12"/>
  <line stroke="red" x1="1" y1="15" x2="0" y2="16"/>
  <line stroke="red" x1="1" y1="15" x2="8" y2="15"/>
  <line stroke="red" x1="15" y1="1" x2="16" y2="0"/>
  <line stroke="red" x1="15" y1="1" x2="15" y2="6"/>
  <line stroke="red" x1="14" y1="6" x2="15" y2="6"/>
  <line stroke="blue" x1="14" y1="6" x2="14" y2="14"/>
  <line stroke="blue" x1="8" y1="13" x2="8" y2="14"/>
  <line stroke="red" x1="8" y1="13" x2="13" y2="13"/>
  <line stroke="red" x1="11" y1="11" x2="12" y2="12"/>
  <line stroke="black" x1="0" y1="16" x2="8" y2="16"/>
  <line stroke="black" x1="16" y1="0" x2="16" y2="6"/>
  <line stroke="red" x1="8" y1="14" x2="8" y2="15"/>
  <line stroke="blue" x1="8" y1="14" x2="14" y2="14"/>
  <line stroke="blue" x1="15" y1="6" x2="16" y2="6"/>
  <line stroke="red" x1="15" y1="6" x2="15" y2="15"/>
  <line stroke="blue" x1="12" y1="12" x2="13" y2="13"/>
  <line stroke="blue" x1="8" y1="15" x2="8" y2="16"/>
  <line stroke="red" x1="8" y1="15" x2="15" y2="15"/>
  <line stroke="black" x1="16" y1="6" x2="16" y2="16"/>
  <line stroke="black" x1="8" y1="16" x2="16" y2="16"/>
  <line stroke="red" x1="13" y1="13" x2="14" y2="14"/>
  <line stroke="blue" x1="14" y1="14" x2="15" y2="15"/>
  <line stroke="red" x1="15" y1="15" x2="16" y2="16"/>
</svg>""",
)

HUMAN_WITH_CENTER_8X8 = BoxPleatingCreasePatternExample(
    name="human_with_center_8x8",
    grid_size=8,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8">
  <line stroke="black" x1="0" y1="0" x2="0" y2="3"/>
  <line stroke="black" x1="0" y1="0" x2="3" y2="0"/>
  <line stroke="red" x1="0" y1="0" x2="3" y2="3"/>
  <line stroke="black" x1="0" y1="3" x2="0" y2="4"/>
  <line stroke="green" x1="0" y1="3" x2="3" y2="3"/>
  <line stroke="black" x1="3" y1="0" x2="4" y2="0"/>
  <line stroke="green" x1="3" y1="0" x2="3" y2="3"/>
  <line stroke="green" x1="0" y1="4" x2="4" y2="4"/>
  <line stroke="black" x1="0" y1="4" x2="0" y2="8"/>
  <line stroke="red" x1="4" y1="0" x2="4" y2="2"/>
  <line stroke="black" x1="4" y1="0" x2="5" y2="0"/>
  <line stroke="red" x1="3" y1="3" x2="4" y2="2"/>
  <line stroke="green" x1="3" y1="3" x2="5" y2="3"/>
  <line stroke="red" x1="4" y1="2" x2="5" y2="3"/>
  <line stroke="green" x1="5" y1="0" x2="5" y2="3"/>
  <line stroke="black" x1="5" y1="0" x2="8" y2="0"/>
  <line stroke="red" x1="4" y1="4" x2="0" y2="8"/>
  <line stroke="green" x1="4" y1="4" x2="4" y2="8"/>
  <line stroke="green" x1="4" y1="4" x2="8" y2="4"/>
  <line stroke="red" x1="4" y1="4" x2="8" y2="8"/>
  <line stroke="red" x1="5" y1="3" x2="8" y2="0"/>
  <line stroke="green" x1="5" y1="3" x2="8" y2="3"/>
  <line stroke="black" x1="0" y1="8" x2="4" y2="8"/>
  <line stroke="black" x1="8" y1="0" x2="8" y2="3"/>
  <line stroke="black" x1="8" y1="3" x2="8" y2="4"/>
  <line stroke="black" x1="4" y1="8" x2="8" y2="8"/>
  <line stroke="black" x1="8" y1="4" x2="8" y2="8"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8">
  <line stroke="red" x1="0" y1="0" x2="1" y2="1"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="3"/>
  <line stroke="black" x1="0" y1="0" x2="4" y2="0"/>
  <line stroke="blue" x1="1" y1="1" x2="2" y2="2"/>
  <line stroke="red" x1="1" y1="1" x2="1" y2="3"/>
  <line stroke="red" x1="1" y1="1" x2="4" y2="1"/>
  <line stroke="blue" x1="2" y1="2" x2="2" y2="3"/>
  <line stroke="red" x1="2" y1="2" x2="3" y2="3"/>
  <line stroke="blue" x1="2" y1="2" x2="4" y2="2"/>
  <line stroke="blue" x1="0" y1="3" x2="1" y2="3"/>
  <line stroke="black" x1="0" y1="3" x2="0" y2="8"/>
  <line stroke="red" x1="1" y1="3" x2="2" y2="3"/>
  <line stroke="red" x1="1" y1="3" x2="1" y2="7"/>
  <line stroke="blue" x1="2" y1="3" x2="3" y2="3"/>
  <line stroke="blue" x1="2" y1="3" x2="2" y2="6"/>
  <line stroke="red" x1="4" y1="0" x2="4" y2="1"/>
  <line stroke="black" x1="4" y1="0" x2="8" y2="0"/>
  <line stroke="blue" x1="4" y1="1" x2="4" y2="2"/>
  <line stroke="red" x1="4" y1="1" x2="7" y2="1"/>
  <line stroke="red" x1="3" y1="3" x2="4" y2="2"/>
  <line stroke="red" x1="3" y1="3" x2="3" y2="5"/>
  <line stroke="blue" x1="4" y1="2" x2="4" y2="4"/>
  <line stroke="red" x1="4" y1="2" x2="5" y2="3"/>
  <line stroke="blue" x1="4" y1="2" x2="6" y2="2"/>
  <line stroke="blue" x1="4" y1="4" x2="3" y2="5"/>
  <line stroke="red" x1="4" y1="4" x2="4" y2="5"/>
  <line stroke="blue" x1="4" y1="4" x2="5" y2="5"/>
  <line stroke="red" x1="3" y1="5" x2="2" y2="6"/>
  <line stroke="red" x1="3" y1="5" x2="4" y2="5"/>
  <line stroke="red" x1="5" y1="3" x2="6" y2="2"/>
  <line stroke="blue" x1="5" y1="3" x2="6" y2="3"/>
  <line stroke="red" x1="5" y1="3" x2="5" y2="5"/>
  <line stroke="blue" x1="2" y1="6" x2="1" y2="7"/>
  <line stroke="blue" x1="2" y1="6" x2="4" y2="6"/>
  <line stroke="blue" x1="6" y1="2" x2="6" y2="3"/>
  <line stroke="blue" x1="6" y1="2" x2="7" y2="1"/>
  <line stroke="red" x1="4" y1="5" x2="5" y2="5"/>
  <line stroke="blue" x1="4" y1="5" x2="4" y2="6"/>
  <line stroke="red" x1="6" y1="3" x2="7" y2="3"/>
  <line stroke="blue" x1="6" y1="3" x2="6" y2="6"/>
  <line stroke="red" x1="1" y1="7" x2="0" y2="8"/>
  <line stroke="red" x1="1" y1="7" x2="4" y2="7"/>
  <line stroke="red" x1="5" y1="5" x2="6" y2="6"/>
  <line stroke="red" x1="7" y1="1" x2="7" y2="3"/>
  <line stroke="red" x1="7" y1="1" x2="8" y2="0"/>
  <line stroke="red" x1="4" y1="6" x2="4" y2="7"/>
  <line stroke="blue" x1="4" y1="6" x2="6" y2="6"/>
  <line stroke="blue" x1="7" y1="3" x2="8" y2="3"/>
  <line stroke="red" x1="7" y1="3" x2="7" y2="7"/>
  <line stroke="black" x1="0" y1="8" x2="4" y2="8"/>
  <line stroke="black" x1="8" y1="0" x2="8" y2="3"/>
  <line stroke="blue" x1="4" y1="7" x2="4" y2="8"/>
  <line stroke="red" x1="4" y1="7" x2="7" y2="7"/>
  <line stroke="blue" x1="6" y1="6" x2="7" y2="7"/>
  <line stroke="black" x1="8" y1="3" x2="8" y2="8"/>
  <line stroke="black" x1="4" y1="8" x2="8" y2="8"/>
  <line stroke="red" x1="7" y1="7" x2="8" y2="8"/>
</svg>""",
)

HUMAN_32X32_ARMS_UP = BoxPleatingCreasePatternExample(
    name="human_32x32_arms_up",
    grid_size=32,
    packing_svg=HUMAN.packing_svg,
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect stroke="black" x="0" y="0" width="32" height="32"/>
  <line stroke="red" x1="0" y1="0" x2="1" y2="1"/>
  <line stroke="blue" x1="1" y1="1" x2="2" y2="2"/>
  <line stroke="red" x1="1" y1="1" x2="12" y2="1" elevation="1"/>
  <line stroke="red" x1="1" y1="1" x2="1" y2="31" elevation="1"/>
  <line stroke="red" x1="2" y1="2" x2="3" y2="3"/>
  <line stroke="blue" x1="2" y1="2" x2="12" y2="2" elevation="0"/>
  <line stroke="blue" x1="2" y1="2" x2="2" y2="30" elevation="0"/>
  <line stroke="blue" x1="3" y1="3" x2="4" y2="4"/>
  <line stroke="red" x1="3" y1="3" x2="12" y2="3" elevation="1"/>
  <line stroke="red" x1="3" y1="3" x2="3" y2="29" elevation="1"/>
  <line stroke="red" x1="4" y1="4" x2="5" y2="5"/>
  <line stroke="blue" x1="4" y1="4" x2="12" y2="4" elevation="0"/>
  <line stroke="blue" x1="4" y1="4" x2="4" y2="28" elevation="0"/>
  <line stroke="blue" x1="5" y1="5" x2="6" y2="6"/>
  <line stroke="red" x1="5" y1="5" x2="12" y2="5" elevation="1"/>
  <line stroke="red" x1="5" y1="5" x2="5" y2="27" elevation="1"/>
  <line stroke="red" x1="6" y1="6" x2="7" y2="7"/>
  <line stroke="blue" x1="6" y1="6" x2="12" y2="6" elevation="0"/>
  <line stroke="blue" x1="6" y1="6" x2="6" y2="26" elevation="0"/>
  <line stroke="blue" x1="7" y1="7" x2="8" y2="8"/>
  <line stroke="red" x1="7" y1="7" x2="12" y2="7" elevation="1"/>
  <line stroke="red" x1="7" y1="7" x2="7" y2="25" elevation="1"/>
  <line stroke="red" x1="8" y1="8" x2="9" y2="9"/>
  <line stroke="blue" x1="8" y1="8" x2="12" y2="8" elevation="0"/>
  <line stroke="blue" x1="8" y1="8" x2="8" y2="24" elevation="0"/>
  <line stroke="blue" x1="12" y1="0" x2="12" y2="1"/>
  <line stroke="red" x1="12" y1="1" x2="12" y2="2"/>
  <line stroke="red" x1="12" y1="1" x2="16" y2="1" elevation="1"/>
  <line stroke="blue" x1="12" y1="2" x2="12" y2="3"/>
  <line stroke="blue" x1="12" y1="2" x2="16" y2="2" elevation="0"/>
  <line stroke="red" x1="12" y1="3" x2="12" y2="4"/>
  <line stroke="red" x1="12" y1="3" x2="16" y2="3" elevation="1"/>
  <line stroke="blue" x1="12" y1="4" x2="12" y2="5"/>
  <line stroke="blue" x1="12" y1="4" x2="16" y2="4" elevation="0"/>
  <line stroke="blue" x1="9" y1="9" x2="10" y2="10"/>
  <line stroke="red" x1="9" y1="9" x2="12" y2="9" elevation="1"/>
  <line stroke="red" x1="9" y1="9" x2="9" y2="23" elevation="1"/>
  <line stroke="red" x1="12" y1="5" x2="12" y2="6"/>
  <line stroke="red" x1="12" y1="5" x2="16" y2="5" elevation="1"/>
  <line stroke="blue" x1="12" y1="6" x2="12" y2="7"/>
  <line stroke="blue" x1="12" y1="6" x2="16" y2="6" elevation="0"/>
  <line stroke="red" x1="12" y1="7" x2="12" y2="8"/>
  <line stroke="red" x1="12" y1="7" x2="16" y2="7" elevation="1"/>
  <line stroke="red" x1="10" y1="10" x2="11" y2="11"/>
  <line stroke="blue" x1="10" y1="10" x2="12" y2="10" elevation="0"/>
  <line stroke="blue" x1="10" y1="10" x2="10" y2="22" elevation="0"/>
  <line stroke="blue" x1="12" y1="8" x2="12" y2="9"/>
  <line stroke="blue" x1="12" y1="8" x2="16" y2="8" elevation="0"/>
  <line stroke="red" x1="12" y1="9" x2="12" y2="10"/>
  <line stroke="red" x1="12" y1="9" x2="15" y2="9" elevation="1"/>
  <line stroke="red" x1="11" y1="11" x2="12" y2="11" elevation="1"/>
  <line stroke="blue" x1="11" y1="11" x2="12" y2="12"/>
  <line stroke="red" x1="11" y1="11" x2="11" y2="21" elevation="1"/>
  <line stroke="blue" x1="12" y1="10" x2="12" y2="11"/>
  <line stroke="blue" x1="12" y1="10" x2="14" y2="10" elevation="0"/>
  <line stroke="red" x1="16" y1="0" x2="16" y2="1"/>
  <line stroke="blue" x1="16" y1="1" x2="16" y2="2"/>
  <line stroke="red" x1="16" y1="1" x2="20" y2="1" elevation="1"/>
  <line stroke="red" x1="16" y1="2" x2="16" y2="3"/>
  <line stroke="blue" x1="16" y1="2" x2="20" y2="2" elevation="0"/>
  <line stroke="red" x1="12" y1="11" x2="12" y2="12"/>
  <line stroke="red" x1="12" y1="11" x2="13" y2="11" elevation="1"/>
  <line stroke="blue" x1="16" y1="3" x2="16" y2="4"/>
  <line stroke="red" x1="16" y1="3" x2="20" y2="3" elevation="1"/>
  <line stroke="red" x1="16" y1="4" x2="16" y2="5"/>
  <line stroke="blue" x1="16" y1="4" x2="20" y2="4" elevation="0"/>
  <line stroke="blue" x1="16" y1="5" x2="16" y2="6"/>
  <line stroke="red" x1="16" y1="5" x2="20" y2="5" elevation="1"/>
  <line stroke="blue" x1="12" y1="12" x2="13" y2="11"/>
  <line stroke="blue" x1="12" y1="12" x2="12" y2="20" elevation="0"/>
  <line stroke="red" x1="13" y1="11" x2="14" y2="10"/>
  <line stroke="red" x1="13" y1="11" x2="13" y2="19" elevation="1"/>
  <line stroke="red" x1="16" y1="6" x2="16" y2="7"/>
  <line stroke="blue" x1="16" y1="6" x2="20" y2="6" elevation="0"/>
  <line stroke="blue" x1="14" y1="10" x2="15" y2="9"/>
  <line stroke="blue" x1="14" y1="10" x2="14" y2="18" elevation="0"/>
  <line stroke="blue" x1="16" y1="7" x2="16" y2="8"/>
  <line stroke="red" x1="16" y1="7" x2="20" y2="7" elevation="1"/>
  <line stroke="red" x1="15" y1="9" x2="16" y2="8"/>
  <line stroke="red" x1="15" y1="9" x2="15" y2="17" elevation="1"/>
  <line stroke="red" x1="16" y1="8" x2="17" y2="9"/>
  <line stroke="blue" x1="16" y1="8" x2="20" y2="8" elevation="0"/>
  <line stroke="blue" x1="16" y1="8" x2="16" y2="16" elevation="0"/>
  <line stroke="blue" x1="17" y1="9" x2="18" y2="10"/>
  <line stroke="red" x1="17" y1="9" x2="20" y2="9" elevation="1"/>
  <line stroke="red" x1="17" y1="9" x2="17" y2="17" elevation="1"/>
  <line stroke="blue" x1="20" y1="0" x2="20" y2="1"/>
  <line stroke="red" x1="20" y1="1" x2="20" y2="2"/>
  <line stroke="red" x1="20" y1="1" x2="31" y2="1" elevation="1"/>
  <line stroke="blue" x1="20" y1="2" x2="20" y2="3"/>
  <line stroke="blue" x1="20" y1="2" x2="30" y2="2" elevation="0"/>
  <line stroke="red" x1="20" y1="3" x2="20" y2="4"/>
  <line stroke="red" x1="20" y1="3" x2="29" y2="3" elevation="1"/>
  <line stroke="blue" x1="20" y1="4" x2="20" y2="5"/>
  <line stroke="blue" x1="20" y1="4" x2="28" y2="4" elevation="0"/>
  <line stroke="red" x1="18" y1="10" x2="19" y2="11"/>
  <line stroke="blue" x1="18" y1="10" x2="20" y2="10" elevation="0"/>
  <line stroke="blue" x1="18" y1="10" x2="18" y2="18" elevation="0"/>
  <line stroke="red" x1="20" y1="5" x2="20" y2="6"/>
  <line stroke="red" x1="20" y1="5" x2="27" y2="5" elevation="1"/>
  <line stroke="blue" x1="20" y1="6" x2="20" y2="7"/>
  <line stroke="blue" x1="20" y1="6" x2="26" y2="6" elevation="0"/>
  <line stroke="red" x1="20" y1="7" x2="20" y2="8"/>
  <line stroke="red" x1="20" y1="7" x2="25" y2="7" elevation="1"/>
  <line stroke="blue" x1="20" y1="8" x2="20" y2="9"/>
  <line stroke="blue" x1="20" y1="8" x2="24" y2="8" elevation="0"/>
  <line stroke="red" x1="20" y1="9" x2="20" y2="10"/>
  <line stroke="red" x1="20" y1="9" x2="23" y2="9" elevation="1"/>
  <line stroke="red" x1="19" y1="11" x2="20" y2="11" elevation="1"/>
  <line stroke="blue" x1="19" y1="11" x2="20" y2="12"/>
  <line stroke="red" x1="19" y1="11" x2="19" y2="19" elevation="1"/>
  <line stroke="blue" x1="20" y1="10" x2="20" y2="11"/>
  <line stroke="blue" x1="20" y1="10" x2="22" y2="10" elevation="0"/>
  <line stroke="blue" x1="16" y1="16" x2="15" y2="17"/>
  <line stroke="red" x1="16" y1="16" x2="16" y2="17"/>
  <line stroke="blue" x1="16" y1="16" x2="17" y2="17"/>
  <line stroke="red" x1="15" y1="17" x2="14" y2="18"/>
  <line stroke="red" x1="15" y1="17" x2="16" y2="17" elevation="1"/>
  <line stroke="blue" x1="14" y1="18" x2="13" y2="19"/>
  <line stroke="blue" x1="14" y1="18" x2="16" y2="18" elevation="0"/>
  <line stroke="red" x1="20" y1="11" x2="20" y2="12"/>
  <line stroke="red" x1="20" y1="11" x2="21" y2="11" elevation="1"/>
  <line stroke="red" x1="13" y1="19" x2="12" y2="20"/>
  <line stroke="red" x1="13" y1="19" x2="16" y2="19" elevation="1"/>
  <line stroke="blue" x1="12" y1="20" x2="11" y2="21"/>
  <line stroke="blue" x1="12" y1="20" x2="16" y2="20" elevation="0"/>
  <line stroke="blue" x1="20" y1="12" x2="21" y2="11"/>
  <line stroke="blue" x1="20" y1="12" x2="20" y2="20" elevation="0"/>
  <line stroke="red" x1="16" y1="17" x2="17" y2="17" elevation="1"/>
  <line stroke="blue" x1="16" y1="17" x2="16" y2="18"/>
  <line stroke="red" x1="11" y1="21" x2="10" y2="22"/>
  <line stroke="red" x1="11" y1="21" x2="16" y2="21" elevation="1"/>
  <line stroke="red" x1="21" y1="11" x2="22" y2="10"/>
  <line stroke="red" x1="21" y1="11" x2="21" y2="21" elevation="1"/>
  <line stroke="red" x1="17" y1="17" x2="18" y2="18"/>
  <line stroke="red" x1="16" y1="18" x2="16" y2="19"/>
  <line stroke="blue" x1="16" y1="18" x2="18" y2="18" elevation="0"/>
  <line stroke="blue" x1="10" y1="22" x2="9" y2="23"/>
  <line stroke="blue" x1="10" y1="22" x2="16" y2="22" elevation="0"/>
  <line stroke="blue" x1="22" y1="10" x2="23" y2="9"/>
  <line stroke="blue" x1="22" y1="10" x2="22" y2="22" elevation="0"/>
  <line stroke="red" x1="9" y1="23" x2="8" y2="24"/>
  <line stroke="red" x1="9" y1="23" x2="16" y2="23" elevation="1"/>
  <line stroke="red" x1="23" y1="9" x2="24" y2="8"/>
  <line stroke="red" x1="23" y1="9" x2="23" y2="23" elevation="1"/>
  <line stroke="blue" x1="16" y1="19" x2="16" y2="20"/>
  <line stroke="red" x1="16" y1="19" x2="19" y2="19" elevation="1"/>
  <line stroke="blue" x1="8" y1="24" x2="7" y2="25"/>
  <line stroke="blue" x1="8" y1="24" x2="16" y2="24" elevation="0"/>
  <line stroke="blue" x1="24" y1="8" x2="25" y2="7"/>
  <line stroke="blue" x1="24" y1="8" x2="24" y2="24" elevation="0"/>
  <line stroke="blue" x1="18" y1="18" x2="19" y2="19"/>
  <line stroke="red" x1="16" y1="20" x2="16" y2="21"/>
  <line stroke="blue" x1="16" y1="20" x2="20" y2="20" elevation="0"/>
  <line stroke="red" x1="7" y1="25" x2="6" y2="26"/>
  <line stroke="red" x1="7" y1="25" x2="16" y2="25" elevation="1"/>
  <line stroke="red" x1="25" y1="7" x2="26" y2="6"/>
  <line stroke="red" x1="25" y1="7" x2="25" y2="25" elevation="1"/>
  <line stroke="blue" x1="16" y1="21" x2="16" y2="22"/>
  <line stroke="red" x1="16" y1="21" x2="21" y2="21" elevation="1"/>
  <line stroke="blue" x1="6" y1="26" x2="5" y2="27"/>
  <line stroke="blue" x1="6" y1="26" x2="16" y2="26" elevation="0"/>
  <line stroke="blue" x1="26" y1="6" x2="27" y2="5"/>
  <line stroke="blue" x1="26" y1="6" x2="26" y2="26" elevation="0"/>
  <line stroke="red" x1="19" y1="19" x2="20" y2="20"/>
  <line stroke="red" x1="16" y1="22" x2="16" y2="23"/>
  <line stroke="blue" x1="16" y1="22" x2="22" y2="22" elevation="0"/>
  <line stroke="red" x1="5" y1="27" x2="4" y2="28"/>
  <line stroke="red" x1="5" y1="27" x2="16" y2="27" elevation="1"/>
  <line stroke="red" x1="27" y1="5" x2="28" y2="4"/>
  <line stroke="red" x1="27" y1="5" x2="27" y2="27" elevation="1"/>
  <line stroke="blue" x1="16" y1="23" x2="16" y2="24"/>
  <line stroke="red" x1="16" y1="23" x2="23" y2="23" elevation="1"/>
  <line stroke="blue" x1="4" y1="28" x2="3" y2="29"/>
  <line stroke="blue" x1="4" y1="28" x2="16" y2="28" elevation="0"/>
  <line stroke="blue" x1="20" y1="20" x2="21" y2="21"/>
  <line stroke="blue" x1="28" y1="4" x2="29" y2="3"/>
  <line stroke="blue" x1="28" y1="4" x2="28" y2="28" elevation="0"/>
  <line stroke="red" x1="16" y1="24" x2="16" y2="25"/>
  <line stroke="blue" x1="16" y1="24" x2="24" y2="24" elevation="0"/>
  <line stroke="red" x1="3" y1="29" x2="2" y2="30"/>
  <line stroke="red" x1="3" y1="29" x2="16" y2="29" elevation="1"/>
  <line stroke="red" x1="29" y1="3" x2="30" y2="2"/>
  <line stroke="red" x1="29" y1="3" x2="29" y2="29" elevation="1"/>
  <line stroke="blue" x1="16" y1="25" x2="16" y2="26"/>
  <line stroke="red" x1="16" y1="25" x2="25" y2="25" elevation="1"/>
  <line stroke="red" x1="21" y1="21" x2="22" y2="22"/>
  <line stroke="blue" x1="2" y1="30" x2="1" y2="31"/>
  <line stroke="blue" x1="2" y1="30" x2="16" y2="30" elevation="0"/>
  <line stroke="blue" x1="30" y1="2" x2="31" y2="1"/>
  <line stroke="blue" x1="30" y1="2" x2="30" y2="30" elevation="0"/>
  <line stroke="red" x1="16" y1="26" x2="16" y2="27"/>
  <line stroke="blue" x1="16" y1="26" x2="26" y2="26" elevation="0"/>
  <line stroke="red" x1="1" y1="31" x2="0" y2="32"/>
  <line stroke="red" x1="1" y1="31" x2="16" y2="31" elevation="1"/>
  <line stroke="red" x1="31" y1="1" x2="32" y2="0"/>
  <line stroke="red" x1="31" y1="1" x2="31" y2="31" elevation="1"/>
  <line stroke="blue" x1="22" y1="22" x2="23" y2="23"/>
  <line stroke="blue" x1="16" y1="27" x2="16" y2="28"/>
  <line stroke="red" x1="16" y1="27" x2="27" y2="27" elevation="1"/>
  <line stroke="red" x1="16" y1="28" x2="16" y2="29"/>
  <line stroke="blue" x1="16" y1="28" x2="28" y2="28" elevation="0"/>
  <line stroke="red" x1="23" y1="23" x2="24" y2="24"/>
  <line stroke="blue" x1="16" y1="29" x2="16" y2="30"/>
  <line stroke="red" x1="16" y1="29" x2="29" y2="29" elevation="1"/>
  <line stroke="blue" x1="24" y1="24" x2="25" y2="25"/>
  <line stroke="red" x1="16" y1="30" x2="16" y2="31"/>
  <line stroke="blue" x1="16" y1="30" x2="30" y2="30" elevation="0"/>
  <line stroke="blue" x1="16" y1="31" x2="16" y2="32"/>
  <line stroke="red" x1="16" y1="31" x2="31" y2="31" elevation="1"/>
  <line stroke="red" x1="25" y1="25" x2="26" y2="26"/>
  <line stroke="blue" x1="26" y1="26" x2="27" y2="27"/>
  <line stroke="red" x1="27" y1="27" x2="28" y2="28"/>
  <line stroke="blue" x1="28" y1="28" x2="29" y2="29"/>
  <line stroke="red" x1="29" y1="29" x2="30" y2="30"/>
  <line stroke="blue" x1="30" y1="30" x2="31" y2="31"/>
  <line stroke="red" x1="31" y1="31" x2="32" y2="32"/>
</svg>""",
)

HUMAN_32X32 = BoxPleatingCreasePatternExample(
    name="human_32x32",
    grid_size=32,
    packing_svg=HUMAN.packing_svg,
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect stroke="black" x="0" y="0" width="32" height="32"/>
  <line stroke="red" x1="0" y1="0" x2="1" y2="1"/>
  <line stroke="blue" x1="1" y1="1" x2="2" y2="2"/>
  <line stroke="red" x1="1" y1="1" x2="1" y2="12" elevation="1"/>
  <line stroke="red" x1="1" y1="1" x2="16" y2="1" elevation="1"/>
  <line stroke="red" x1="2" y1="2" x2="3" y2="3"/>
  <line stroke="blue" x1="2" y1="2" x2="2" y2="12" elevation="0"/>
  <line stroke="blue" x1="2" y1="2" x2="16" y2="2" elevation="0"/>
  <line stroke="blue" x1="3" y1="3" x2="4" y2="4"/>
  <line stroke="red" x1="3" y1="3" x2="3" y2="12" elevation="1"/>
  <line stroke="red" x1="3" y1="3" x2="16" y2="3" elevation="1"/>
  <line stroke="red" x1="4" y1="4" x2="5" y2="5"/>
  <line stroke="blue" x1="4" y1="4" x2="4" y2="12" elevation="0"/>
  <line stroke="blue" x1="4" y1="4" x2="16" y2="4" elevation="0"/>
  <line stroke="blue" x1="5" y1="5" x2="6" y2="6"/>
  <line stroke="red" x1="5" y1="5" x2="5" y2="12" elevation="1"/>
  <line stroke="red" x1="5" y1="5" x2="16" y2="5" elevation="1"/>
  <line stroke="red" x1="6" y1="6" x2="7" y2="7"/>
  <line stroke="blue" x1="6" y1="6" x2="6" y2="12" elevation="0"/>
  <line stroke="blue" x1="6" y1="6" x2="16" y2="6" elevation="0"/>
  <line stroke="blue" x1="7" y1="7" x2="8" y2="8"/>
  <line stroke="red" x1="7" y1="7" x2="7" y2="12" elevation="1"/>
  <line stroke="red" x1="7" y1="7" x2="16" y2="7" elevation="1"/>
  <line stroke="red" x1="8" y1="8" x2="9" y2="9"/>
  <line stroke="blue" x1="8" y1="8" x2="8" y2="12" elevation="0"/>
  <line stroke="blue" x1="8" y1="8" x2="16" y2="8" elevation="0"/>
  <line stroke="blue" x1="0" y1="12" x2="1" y2="12"/>
  <line stroke="red" x1="1" y1="12" x2="2" y2="12"/>
  <line stroke="red" x1="1" y1="12" x2="1" y2="31" elevation="1"/>
  <line stroke="blue" x1="2" y1="12" x2="3" y2="12"/>
  <line stroke="blue" x1="2" y1="12" x2="2" y2="30" elevation="0"/>
  <line stroke="red" x1="3" y1="12" x2="4" y2="12"/>
  <line stroke="red" x1="3" y1="12" x2="3" y2="29" elevation="1"/>
  <line stroke="blue" x1="4" y1="12" x2="5" y2="12"/>
  <line stroke="blue" x1="4" y1="12" x2="4" y2="28" elevation="0"/>
  <line stroke="blue" x1="9" y1="9" x2="10" y2="10"/>
  <line stroke="red" x1="9" y1="9" x2="9" y2="12" elevation="1"/>
  <line stroke="red" x1="9" y1="9" x2="15" y2="9" elevation="1"/>
  <line stroke="red" x1="5" y1="12" x2="6" y2="12"/>
  <line stroke="red" x1="5" y1="12" x2="5" y2="27" elevation="1"/>
  <line stroke="blue" x1="6" y1="12" x2="7" y2="12"/>
  <line stroke="blue" x1="6" y1="12" x2="6" y2="26" elevation="0"/>
  <line stroke="red" x1="7" y1="12" x2="8" y2="12"/>
  <line stroke="red" x1="7" y1="12" x2="7" y2="25" elevation="1"/>
  <line stroke="red" x1="10" y1="10" x2="11" y2="11"/>
  <line stroke="blue" x1="10" y1="10" x2="10" y2="12" elevation="0"/>
  <line stroke="blue" x1="10" y1="10" x2="14" y2="10" elevation="0"/>
  <line stroke="blue" x1="8" y1="12" x2="9" y2="12"/>
  <line stroke="blue" x1="8" y1="12" x2="8" y2="24" elevation="0"/>
  <line stroke="red" x1="9" y1="12" x2="10" y2="12"/>
  <line stroke="red" x1="9" y1="12" x2="9" y2="23" elevation="1"/>
  <line stroke="red" x1="11" y1="11" x2="11" y2="12" elevation="1"/>
  <line stroke="blue" x1="11" y1="11" x2="12" y2="12"/>
  <line stroke="red" x1="11" y1="11" x2="13" y2="11" elevation="1"/>
  <line stroke="blue" x1="10" y1="12" x2="11" y2="12"/>
  <line stroke="blue" x1="10" y1="12" x2="10" y2="22" elevation="0"/>
  <line stroke="red" x1="16" y1="0" x2="16" y2="1"/>
  <line stroke="blue" x1="16" y1="1" x2="16" y2="2"/>
  <line stroke="red" x1="16" y1="1" x2="31" y2="1" elevation="1"/>
  <line stroke="red" x1="16" y1="2" x2="16" y2="3"/>
  <line stroke="blue" x1="16" y1="2" x2="30" y2="2" elevation="0"/>
  <line stroke="red" x1="11" y1="12" x2="12" y2="12"/>
  <line stroke="red" x1="11" y1="12" x2="11" y2="21" elevation="1"/>
  <line stroke="blue" x1="16" y1="3" x2="16" y2="4"/>
  <line stroke="red" x1="16" y1="3" x2="29" y2="3" elevation="1"/>
  <line stroke="red" x1="16" y1="4" x2="16" y2="5"/>
  <line stroke="blue" x1="16" y1="4" x2="28" y2="4" elevation="0"/>
  <line stroke="blue" x1="16" y1="5" x2="16" y2="6"/>
  <line stroke="red" x1="16" y1="5" x2="27" y2="5" elevation="1"/>
  <line stroke="blue" x1="12" y1="12" x2="13" y2="11"/>
  <line stroke="blue" x1="12" y1="12" x2="12" y2="20" elevation="0"/>
  <line stroke="red" x1="13" y1="11" x2="14" y2="10"/>
  <line stroke="red" x1="13" y1="11" x2="13" y2="19" elevation="1"/>
  <line stroke="red" x1="16" y1="6" x2="16" y2="7"/>
  <line stroke="blue" x1="16" y1="6" x2="26" y2="6" elevation="0"/>
  <line stroke="blue" x1="14" y1="10" x2="15" y2="9"/>
  <line stroke="blue" x1="14" y1="10" x2="14" y2="18" elevation="0"/>
  <line stroke="blue" x1="16" y1="7" x2="16" y2="8"/>
  <line stroke="red" x1="16" y1="7" x2="25" y2="7" elevation="1"/>
  <line stroke="red" x1="15" y1="9" x2="16" y2="8"/>
  <line stroke="red" x1="15" y1="9" x2="15" y2="17" elevation="1"/>
  <line stroke="red" x1="16" y1="8" x2="17" y2="9"/>
  <line stroke="blue" x1="16" y1="8" x2="16" y2="16" elevation="0"/>
  <line stroke="blue" x1="16" y1="8" x2="24" y2="8" elevation="0"/>
  <line stroke="blue" x1="17" y1="9" x2="18" y2="10"/>
  <line stroke="red" x1="17" y1="9" x2="17" y2="17" elevation="1"/>
  <line stroke="red" x1="17" y1="9" x2="23" y2="9" elevation="1"/>
  <line stroke="red" x1="18" y1="10" x2="19" y2="11"/>
  <line stroke="blue" x1="18" y1="10" x2="22" y2="10" elevation="0"/>
  <line stroke="blue" x1="18" y1="10" x2="18" y2="18" elevation="0"/>
  <line stroke="blue" x1="19" y1="11" x2="20" y2="12"/>
  <line stroke="red" x1="19" y1="11" x2="21" y2="11" elevation="1"/>
  <line stroke="red" x1="19" y1="11" x2="19" y2="19" elevation="1"/>
  <line stroke="blue" x1="16" y1="16" x2="15" y2="17"/>
  <line stroke="red" x1="16" y1="16" x2="16" y2="17"/>
  <line stroke="blue" x1="16" y1="16" x2="17" y2="17"/>
  <line stroke="red" x1="15" y1="17" x2="14" y2="18"/>
  <line stroke="red" x1="15" y1="17" x2="16" y2="17" elevation="1"/>
  <line stroke="blue" x1="14" y1="18" x2="13" y2="19"/>
  <line stroke="blue" x1="14" y1="18" x2="16" y2="18" elevation="0"/>
  <line stroke="red" x1="13" y1="19" x2="12" y2="20"/>
  <line stroke="red" x1="13" y1="19" x2="16" y2="19" elevation="1"/>
  <line stroke="blue" x1="12" y1="20" x2="11" y2="21"/>
  <line stroke="blue" x1="12" y1="20" x2="16" y2="20" elevation="0"/>
  <line stroke="blue" x1="20" y1="12" x2="21" y2="11"/>
  <line stroke="red" x1="20" y1="12" x2="21" y2="12"/>
  <line stroke="blue" x1="20" y1="12" x2="20" y2="20" elevation="0"/>
  <line stroke="red" x1="16" y1="17" x2="17" y2="17" elevation="1"/>
  <line stroke="blue" x1="16" y1="17" x2="16" y2="18"/>
  <line stroke="red" x1="11" y1="21" x2="10" y2="22"/>
  <line stroke="red" x1="11" y1="21" x2="16" y2="21" elevation="1"/>
  <line stroke="red" x1="21" y1="11" x2="22" y2="10"/>
  <line stroke="red" x1="21" y1="11" x2="21" y2="12" elevation="1"/>
  <line stroke="red" x1="17" y1="17" x2="18" y2="18"/>
  <line stroke="red" x1="16" y1="18" x2="16" y2="19"/>
  <line stroke="blue" x1="16" y1="18" x2="18" y2="18" elevation="0"/>
  <line stroke="blue" x1="10" y1="22" x2="9" y2="23"/>
  <line stroke="blue" x1="10" y1="22" x2="16" y2="22" elevation="0"/>
  <line stroke="blue" x1="22" y1="10" x2="23" y2="9"/>
  <line stroke="blue" x1="22" y1="10" x2="22" y2="12" elevation="0"/>
  <line stroke="blue" x1="21" y1="12" x2="22" y2="12"/>
  <line stroke="red" x1="21" y1="12" x2="21" y2="21" elevation="1"/>
  <line stroke="red" x1="9" y1="23" x2="8" y2="24"/>
  <line stroke="red" x1="9" y1="23" x2="16" y2="23" elevation="1"/>
  <line stroke="red" x1="23" y1="9" x2="24" y2="8"/>
  <line stroke="red" x1="23" y1="9" x2="23" y2="12" elevation="1"/>
  <line stroke="blue" x1="16" y1="19" x2="16" y2="20"/>
  <line stroke="red" x1="16" y1="19" x2="19" y2="19" elevation="1"/>
  <line stroke="red" x1="22" y1="12" x2="23" y2="12"/>
  <line stroke="blue" x1="22" y1="12" x2="22" y2="22" elevation="0"/>
  <line stroke="blue" x1="8" y1="24" x2="7" y2="25"/>
  <line stroke="blue" x1="8" y1="24" x2="16" y2="24" elevation="0"/>
  <line stroke="blue" x1="24" y1="8" x2="25" y2="7"/>
  <line stroke="blue" x1="24" y1="8" x2="24" y2="12" elevation="0"/>
  <line stroke="blue" x1="18" y1="18" x2="19" y2="19"/>
  <line stroke="red" x1="16" y1="20" x2="16" y2="21"/>
  <line stroke="blue" x1="16" y1="20" x2="20" y2="20" elevation="0"/>
  <line stroke="blue" x1="23" y1="12" x2="24" y2="12"/>
  <line stroke="red" x1="23" y1="12" x2="23" y2="23" elevation="1"/>
  <line stroke="red" x1="7" y1="25" x2="6" y2="26"/>
  <line stroke="red" x1="7" y1="25" x2="16" y2="25" elevation="1"/>
  <line stroke="red" x1="25" y1="7" x2="26" y2="6"/>
  <line stroke="red" x1="25" y1="7" x2="25" y2="12" elevation="1"/>
  <line stroke="blue" x1="16" y1="21" x2="16" y2="22"/>
  <line stroke="red" x1="16" y1="21" x2="21" y2="21" elevation="1"/>
  <line stroke="blue" x1="6" y1="26" x2="5" y2="27"/>
  <line stroke="blue" x1="6" y1="26" x2="16" y2="26" elevation="0"/>
  <line stroke="blue" x1="26" y1="6" x2="27" y2="5"/>
  <line stroke="blue" x1="26" y1="6" x2="26" y2="12" elevation="0"/>
  <line stroke="red" x1="24" y1="12" x2="25" y2="12"/>
  <line stroke="blue" x1="24" y1="12" x2="24" y2="24" elevation="0"/>
  <line stroke="red" x1="19" y1="19" x2="20" y2="20"/>
  <line stroke="red" x1="16" y1="22" x2="16" y2="23"/>
  <line stroke="blue" x1="16" y1="22" x2="22" y2="22" elevation="0"/>
  <line stroke="red" x1="5" y1="27" x2="4" y2="28"/>
  <line stroke="red" x1="5" y1="27" x2="16" y2="27" elevation="1"/>
  <line stroke="red" x1="27" y1="5" x2="28" y2="4"/>
  <line stroke="red" x1="27" y1="5" x2="27" y2="12" elevation="1"/>
  <line stroke="blue" x1="25" y1="12" x2="26" y2="12"/>
  <line stroke="red" x1="25" y1="12" x2="25" y2="25" elevation="1"/>
  <line stroke="blue" x1="16" y1="23" x2="16" y2="24"/>
  <line stroke="red" x1="16" y1="23" x2="23" y2="23" elevation="1"/>
  <line stroke="blue" x1="4" y1="28" x2="3" y2="29"/>
  <line stroke="blue" x1="4" y1="28" x2="16" y2="28" elevation="0"/>
  <line stroke="blue" x1="20" y1="20" x2="21" y2="21"/>
  <line stroke="blue" x1="28" y1="4" x2="29" y2="3"/>
  <line stroke="blue" x1="28" y1="4" x2="28" y2="12" elevation="0"/>
  <line stroke="red" x1="26" y1="12" x2="27" y2="12"/>
  <line stroke="blue" x1="26" y1="12" x2="26" y2="26" elevation="0"/>
  <line stroke="red" x1="16" y1="24" x2="16" y2="25"/>
  <line stroke="blue" x1="16" y1="24" x2="24" y2="24" elevation="0"/>
  <line stroke="red" x1="3" y1="29" x2="2" y2="30"/>
  <line stroke="red" x1="3" y1="29" x2="16" y2="29" elevation="1"/>
  <line stroke="red" x1="29" y1="3" x2="30" y2="2"/>
  <line stroke="red" x1="29" y1="3" x2="29" y2="12" elevation="1"/>
  <line stroke="blue" x1="27" y1="12" x2="28" y2="12"/>
  <line stroke="red" x1="27" y1="12" x2="27" y2="27" elevation="1"/>
  <line stroke="blue" x1="16" y1="25" x2="16" y2="26"/>
  <line stroke="red" x1="16" y1="25" x2="25" y2="25" elevation="1"/>
  <line stroke="red" x1="21" y1="21" x2="22" y2="22"/>
  <line stroke="blue" x1="2" y1="30" x2="1" y2="31"/>
  <line stroke="blue" x1="2" y1="30" x2="16" y2="30" elevation="0"/>
  <line stroke="blue" x1="30" y1="2" x2="31" y2="1"/>
  <line stroke="blue" x1="30" y1="2" x2="30" y2="12" elevation="0"/>
  <line stroke="red" x1="28" y1="12" x2="29" y2="12"/>
  <line stroke="blue" x1="28" y1="12" x2="28" y2="28" elevation="0"/>
  <line stroke="red" x1="16" y1="26" x2="16" y2="27"/>
  <line stroke="blue" x1="16" y1="26" x2="26" y2="26" elevation="0"/>
  <line stroke="red" x1="1" y1="31" x2="0" y2="32"/>
  <line stroke="red" x1="1" y1="31" x2="16" y2="31" elevation="1"/>
  <line stroke="red" x1="31" y1="1" x2="32" y2="0"/>
  <line stroke="red" x1="31" y1="1" x2="31" y2="12" elevation="1"/>
  <line stroke="blue" x1="22" y1="22" x2="23" y2="23"/>
  <line stroke="blue" x1="16" y1="27" x2="16" y2="28"/>
  <line stroke="red" x1="16" y1="27" x2="27" y2="27" elevation="1"/>
  <line stroke="blue" x1="29" y1="12" x2="30" y2="12"/>
  <line stroke="red" x1="29" y1="12" x2="29" y2="29" elevation="1"/>
  <line stroke="red" x1="16" y1="28" x2="16" y2="29"/>
  <line stroke="blue" x1="16" y1="28" x2="28" y2="28" elevation="0"/>
  <line stroke="red" x1="30" y1="12" x2="31" y2="12"/>
  <line stroke="blue" x1="30" y1="12" x2="30" y2="30" elevation="0"/>
  <line stroke="red" x1="23" y1="23" x2="24" y2="24"/>
  <line stroke="blue" x1="16" y1="29" x2="16" y2="30"/>
  <line stroke="red" x1="16" y1="29" x2="29" y2="29" elevation="1"/>
  <line stroke="blue" x1="31" y1="12" x2="32" y2="12"/>
  <line stroke="red" x1="31" y1="12" x2="31" y2="31" elevation="1"/>
  <line stroke="blue" x1="24" y1="24" x2="25" y2="25"/>
  <line stroke="red" x1="16" y1="30" x2="16" y2="31"/>
  <line stroke="blue" x1="16" y1="30" x2="30" y2="30" elevation="0"/>
  <line stroke="blue" x1="16" y1="31" x2="16" y2="32"/>
  <line stroke="red" x1="16" y1="31" x2="31" y2="31" elevation="1"/>
  <line stroke="red" x1="25" y1="25" x2="26" y2="26"/>
  <line stroke="blue" x1="26" y1="26" x2="27" y2="27"/>
  <line stroke="red" x1="27" y1="27" x2="28" y2="28"/>
  <line stroke="blue" x1="28" y1="28" x2="29" y2="29"/>
  <line stroke="red" x1="29" y1="29" x2="30" y2="30"/>
  <line stroke="blue" x1="30" y1="30" x2="31" y2="31"/>
  <line stroke="red" x1="31" y1="31" x2="32" y2="32"/>
</svg>""",
)

CHOUGH = BoxPleatingCreasePatternExample(
    name="chough",
    grid_size=12,
    packing_svg="",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="0" y2="83.3"/>
  <line stroke="black" x1="0" y1="0" x2="83.3" y2="0"/>
  <line stroke="red" x1="0" y1="83.3" x2="83.3" y2="83.3"/>
  <line stroke="black" x1="0" y1="83.3" x2="0" y2="250"/>
  <line stroke="red" x1="83.3" y1="0" x2="83.3" y2="83.3"/>
  <line stroke="black" x1="83.3" y1="0" x2="166.7" y2="0"/>
  <line stroke="blue" x1="83.3" y1="83.3" x2="166.7" y2="0"/>
  <line stroke="blue" x1="83.3" y1="83.3" x2="166.7" y2="166.7"/>
  <line stroke="red" x1="83.3" y1="83.3" x2="83.3" y2="250"/>
  <line stroke="red" x1="83.3" y1="83.3" x2="416.7" y2="83.3"/>
  <line stroke="black" x1="166.7" y1="0" x2="500" y2="0"/>
  <line stroke="blue" x1="166.7" y1="166.7" x2="166.7" y2="250"/>
  <line stroke="red" x1="166.7" y1="166.7" x2="250" y2="250"/>
  <line stroke="blue" x1="166.7" y1="166.7" x2="333.3" y2="166.7"/>
  <line stroke="blue" x1="0" y1="250" x2="83.3" y2="250"/>
  <line stroke="black" x1="0" y1="250" x2="0" y2="833.3"/>
  <line stroke="red" x1="83.3" y1="250" x2="166.7" y2="250"/>
  <line stroke="red" x1="83.3" y1="250" x2="83.3" y2="750"/>
  <line stroke="blue" x1="166.7" y1="250" x2="250" y2="250"/>
  <line stroke="blue" x1="166.7" y1="250" x2="166.7" y2="666.7"/>
  <line stroke="red" x1="250" y1="250" x2="333.3" y2="166.7"/>
  <line stroke="red" x1="250" y1="250" x2="250" y2="583.3"/>
  <line stroke="blue" x1="333.3" y1="166.7" x2="416.7" y2="83.3"/>
  <line stroke="blue" x1="333.3" y1="166.7" x2="333.3" y2="500"/>
  <line stroke="red" x1="416.7" y1="83.3" x2="500" y2="0"/>
  <line stroke="red" x1="416.7" y1="83.3" x2="416.7" y2="583.3"/>
  <line stroke="red" x1="500" y1="0" x2="583.3" y2="83.3"/>
  <line stroke="black" x1="500" y1="0" x2="750" y2="0"/>
  <line stroke="blue" x1="583.3" y1="83.3" x2="666.7" y2="166.7"/>
  <line stroke="red" x1="583.3" y1="83.3" x2="750" y2="83.3"/>
  <line stroke="red" x1="583.3" y1="83.3" x2="583.3" y2="583.3"/>
  <line stroke="blue" x1="333.3" y1="500" x2="250" y2="583.3"/>
  <line stroke="red" x1="333.3" y1="500" x2="333.3" y2="583.3"/>
  <line stroke="blue" x1="333.3" y1="500" x2="416.7" y2="583.3"/>
  <line stroke="red" x1="250" y1="583.3" x2="333.3" y2="583.3"/>
  <line stroke="red" x1="250" y1="583.3" x2="166.7" y2="666.7"/>
  <line stroke="red" x1="333.3" y1="583.3" x2="416.7" y2="583.3"/>
  <line stroke="blue" x1="333.3" y1="583.3" x2="333.3" y2="666.7"/>
  <line stroke="blue" x1="166.7" y1="666.7" x2="333.3" y2="666.7"/>
  <line stroke="blue" x1="166.7" y1="666.7" x2="83.3" y2="750"/>
  <line stroke="blue" x1="666.7" y1="166.7" x2="750" y2="166.7"/>
  <line stroke="red" x1="666.7" y1="166.7" x2="750" y2="250"/>
  <line stroke="blue" x1="666.7" y1="166.7" x2="666.7" y2="500"/>
  <line stroke="red" x1="416.7" y1="583.3" x2="500" y2="666.7"/>
  <line stroke="red" x1="333.3" y1="666.7" x2="333.3" y2="750"/>
  <line stroke="blue" x1="333.3" y1="666.7" x2="500" y2="666.7"/>
  <line stroke="blue" x1="750" y1="0" x2="750" y2="83.3"/>
  <line stroke="black" x1="750" y1="0" x2="833.3" y2="0"/>
  <line stroke="red" x1="83.3" y1="750" x2="333.3" y2="750"/>
  <line stroke="red" x1="83.3" y1="750" x2="0" y2="833.3"/>
  <line stroke="red" x1="750" y1="83.3" x2="750" y2="166.7"/>
  <line stroke="red" x1="750" y1="83.3" x2="916.7" y2="83.3"/>
  <line stroke="blue" x1="750" y1="166.7" x2="750" y2="250"/>
  <line stroke="blue" x1="750" y1="166.7" x2="833.3" y2="166.7"/>
  <line stroke="red" x1="750" y1="250" x2="833.3" y2="166.7"/>
  <line stroke="red" x1="750" y1="250" x2="750" y2="583.3"/>
  <line stroke="red" x1="333.3" y1="750" x2="416.7" y2="750"/>
  <line stroke="blue" x1="333.3" y1="750" x2="333.3" y2="833.3"/>
  <line stroke="red" x1="583.3" y1="583.3" x2="500" y2="666.7"/>
  <line stroke="blue" x1="583.3" y1="583.3" x2="666.7" y2="500"/>
  <line stroke="red" x1="583.3" y1="583.3" x2="666.7" y2="583.3"/>
  <line stroke="blue" x1="0" y1="833.3" x2="333.3" y2="833.3"/>
  <line stroke="black" x1="0" y1="833.3" x2="0" y2="916.7"/>
  <line stroke="blue" x1="500" y1="666.7" x2="416.7" y2="750"/>
  <line stroke="blue" x1="500" y1="666.7" x2="666.7" y2="666.7"/>
  <line stroke="blue" x1="500" y1="666.7" x2="583.3" y2="750"/>
  <line stroke="red" x1="666.7" y1="500" x2="666.7" y2="583.3"/>
  <line stroke="blue" x1="666.7" y1="500" x2="750" y2="583.3"/>
  <line stroke="black" x1="833.3" y1="0" x2="916.7" y2="0"/>
  <line stroke="blue" x1="833.3" y1="0" x2="916.7" y2="83.3"/>
  <line stroke="blue" x1="833.3" y1="166.7" x2="916.7" y2="83.3"/>
  <line stroke="blue" x1="833.3" y1="166.7" x2="833.3" y2="666.7"/>
  <line stroke="red" x1="416.7" y1="750" x2="583.3" y2="750"/>
  <line stroke="red" x1="416.7" y1="750" x2="500" y2="833.3"/>
  <line stroke="blue" x1="666.7" y1="583.3" x2="666.7" y2="666.7"/>
  <line stroke="red" x1="666.7" y1="583.3" x2="750" y2="583.3"/>
  <line stroke="blue" x1="333.3" y1="833.3" x2="500" y2="833.3"/>
  <line stroke="red" x1="333.3" y1="833.3" x2="333.3" y2="916.7"/>
  <line stroke="red" x1="0" y1="916.7" x2="333.3" y2="916.7"/>
  <line stroke="black" x1="0" y1="916.7" x2="0" y2="1000"/>
  <line stroke="red" x1="916.7" y1="0" x2="916.7" y2="83.3"/>
  <line stroke="black" x1="916.7" y1="0" x2="1000" y2="0"/>
  <line stroke="red" x1="916.7" y1="83.3" x2="1000" y2="83.3"/>
  <line stroke="red" x1="916.7" y1="83.3" x2="916.7" y2="750"/>
  <line stroke="red" x1="666.7" y1="666.7" x2="666.7" y2="750"/>
  <line stroke="blue" x1="666.7" y1="666.7" x2="833.3" y2="666.7"/>
  <line stroke="red" x1="583.3" y1="750" x2="500" y2="833.3"/>
  <line stroke="red" x1="583.3" y1="750" x2="666.7" y2="750"/>
  <line stroke="red" x1="750" y1="583.3" x2="833.3" y2="666.7"/>
  <line stroke="blue" x1="500" y1="833.3" x2="416.7" y2="916.7"/>
  <line stroke="blue" x1="500" y1="833.3" x2="666.7" y2="833.3"/>
  <line stroke="blue" x1="500" y1="833.3" x2="583.3" y2="916.7"/>
  <line stroke="red" x1="333.3" y1="916.7" x2="416.7" y2="916.7"/>
  <line stroke="blue" x1="333.3" y1="916.7" x2="333.3" y2="1000"/>
  <line stroke="black" x1="0" y1="1000" x2="333.3" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="83.3"/>
  <line stroke="blue" x1="666.7" y1="750" x2="666.7" y2="833.3"/>
  <line stroke="red" x1="666.7" y1="750" x2="916.7" y2="750"/>
  <line stroke="black" x1="1000" y1="83.3" x2="1000" y2="833.3"/>
  <line stroke="red" x1="416.7" y1="916.7" x2="583.3" y2="916.7"/>
  <line stroke="red" x1="416.7" y1="916.7" x2="500" y2="1000"/>
  <line stroke="black" x1="333.3" y1="1000" x2="500" y2="1000"/>
  <line stroke="red" x1="666.7" y1="833.3" x2="666.7" y2="916.7"/>
  <line stroke="blue" x1="666.7" y1="833.3" x2="1000" y2="833.3"/>
  <line stroke="blue" x1="833.3" y1="666.7" x2="916.7" y2="750"/>
  <line stroke="red" x1="583.3" y1="916.7" x2="500" y2="1000"/>
  <line stroke="red" x1="583.3" y1="916.7" x2="666.7" y2="916.7"/>
  <line stroke="black" x1="500" y1="1000" x2="666.7" y2="1000"/>
  <line stroke="blue" x1="666.7" y1="916.7" x2="666.7" y2="1000"/>
  <line stroke="red" x1="666.7" y1="916.7" x2="1000" y2="916.7"/>
  <line stroke="red" x1="916.7" y1="750" x2="1000" y2="833.3"/>
  <line stroke="black" x1="666.7" y1="1000" x2="1000" y2="1000"/>
  <line stroke="black" x1="1000" y1="833.3" x2="1000" y2="916.7"/>
  <line stroke="black" x1="1000" y1="916.7" x2="1000" y2="1000"/>
</svg>""",
)

VORTEX_LATTICE = BoxPleatingCreasePatternExample(
    name="vortex_lattice",
    grid_size=18,
    packing_svg="",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="55.6" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="777.8"/>
  <line stroke="black" x1="55.6" y1="0" x2="111.1" y2="0"/>
  <line stroke="blue" x1="55.6" y1="0" x2="55.6" y2="722.2"/>
  <line stroke="black" x1="111.1" y1="0" x2="166.7" y2="0"/>
  <line stroke="red" x1="111.1" y1="0" x2="111.1" y2="666.7"/>
  <line stroke="red" x1="166.7" y1="0" x2="222.2" y2="55.6"/>
  <line stroke="black" x1="166.7" y1="0" x2="333.3" y2="0"/>
  <line stroke="blue" x1="166.7" y1="0" x2="166.7" y2="611.1"/>
  <line stroke="blue" x1="222.2" y1="55.6" x2="277.8" y2="111.1"/>
  <line stroke="red" x1="222.2" y1="55.6" x2="333.3" y2="55.6"/>
  <line stroke="red" x1="222.2" y1="55.6" x2="222.2" y2="555.6"/>
  <line stroke="blue" x1="277.8" y1="111.1" x2="333.3" y2="111.1"/>
  <line stroke="red" x1="277.8" y1="111.1" x2="333.3" y2="166.7"/>
  <line stroke="blue" x1="277.8" y1="111.1" x2="277.8" y2="500"/>
  <line stroke="blue" x1="333.3" y1="0" x2="333.3" y2="55.6"/>
  <line stroke="black" x1="333.3" y1="0" x2="500" y2="0"/>
  <line stroke="red" x1="333.3" y1="55.6" x2="333.3" y2="111.1"/>
  <line stroke="red" x1="333.3" y1="55.6" x2="444.4" y2="55.6"/>
  <line stroke="blue" x1="333.3" y1="111.1" x2="333.3" y2="166.7"/>
  <line stroke="blue" x1="333.3" y1="111.1" x2="388.9" y2="111.1"/>
  <line stroke="red" x1="333.3" y1="166.7" x2="388.9" y2="111.1"/>
  <line stroke="red" x1="333.3" y1="166.7" x2="333.3" y2="444.4"/>
  <line stroke="blue" x1="388.9" y1="111.1" x2="444.4" y2="55.6"/>
  <line stroke="blue" x1="388.9" y1="111.1" x2="388.9" y2="500"/>
  <line stroke="red" x1="444.4" y1="55.6" x2="500" y2="0"/>
  <line stroke="red" x1="444.4" y1="55.6" x2="444.4" y2="555.6"/>
  <line stroke="red" x1="500" y1="0" x2="555.6" y2="55.6"/>
  <line stroke="black" x1="500" y1="0" x2="666.7" y2="0"/>
  <line stroke="blue" x1="500" y1="0" x2="500" y2="611.1"/>
  <line stroke="red" x1="333.3" y1="444.4" x2="277.8" y2="500"/>
  <line stroke="blue" x1="333.3" y1="444.4" x2="333.3" y2="500"/>
  <line stroke="red" x1="333.3" y1="444.4" x2="388.9" y2="500"/>
  <line stroke="blue" x1="555.6" y1="55.6" x2="611.1" y2="111.1"/>
  <line stroke="red" x1="555.6" y1="55.6" x2="666.7" y2="55.6"/>
  <line stroke="red" x1="555.6" y1="55.6" x2="555.6" y2="555.6"/>
  <line stroke="blue" x1="277.8" y1="500" x2="222.2" y2="555.6"/>
  <line stroke="blue" x1="277.8" y1="500" x2="333.3" y2="500"/>
  <line stroke="red" x1="222.2" y1="555.6" x2="166.7" y2="611.1"/>
  <line stroke="red" x1="222.2" y1="555.6" x2="333.3" y2="555.6"/>
  <line stroke="blue" x1="333.3" y1="500" x2="388.9" y2="500"/>
  <line stroke="red" x1="333.3" y1="500" x2="333.3" y2="555.6"/>
  <line stroke="blue" x1="611.1" y1="111.1" x2="666.7" y2="111.1"/>
  <line stroke="red" x1="611.1" y1="111.1" x2="666.7" y2="166.7"/>
  <line stroke="blue" x1="611.1" y1="111.1" x2="611.1" y2="500"/>
  <line stroke="blue" x1="166.7" y1="611.1" x2="111.1" y2="666.7"/>
  <line stroke="blue" x1="166.7" y1="611.1" x2="333.3" y2="611.1"/>
  <line stroke="blue" x1="388.9" y1="500" x2="444.4" y2="555.6"/>
  <line stroke="blue" x1="333.3" y1="555.6" x2="333.3" y2="611.1"/>
  <line stroke="red" x1="333.3" y1="555.6" x2="444.4" y2="555.6"/>
  <line stroke="blue" x1="666.7" y1="0" x2="666.7" y2="55.6"/>
  <line stroke="black" x1="666.7" y1="0" x2="833.3" y2="0"/>
  <line stroke="red" x1="666.7" y1="55.6" x2="666.7" y2="111.1"/>
  <line stroke="red" x1="666.7" y1="55.6" x2="777.8" y2="55.6"/>
  <line stroke="red" x1="111.1" y1="666.7" x2="55.6" y2="722.2"/>
  <line stroke="red" x1="111.1" y1="666.7" x2="333.3" y2="666.7"/>
  <line stroke="blue" x1="666.7" y1="111.1" x2="666.7" y2="166.7"/>
  <line stroke="blue" x1="666.7" y1="111.1" x2="722.2" y2="111.1"/>
  <line stroke="red" x1="666.7" y1="166.7" x2="722.2" y2="111.1"/>
  <line stroke="red" x1="666.7" y1="166.7" x2="666.7" y2="444.4"/>
  <line stroke="red" x1="333.3" y1="611.1" x2="333.3" y2="666.7"/>
  <line stroke="blue" x1="333.3" y1="611.1" x2="500" y2="611.1"/>
  <line stroke="red" x1="444.4" y1="555.6" x2="500" y2="611.1"/>
  <line stroke="blue" x1="55.6" y1="722.2" x2="0" y2="777.8"/>
  <line stroke="blue" x1="55.6" y1="722.2" x2="333.3" y2="722.2"/>
  <line stroke="blue" x1="722.2" y1="111.1" x2="777.8" y2="55.6"/>
  <line stroke="blue" x1="722.2" y1="111.1" x2="722.2" y2="500"/>
  <line stroke="blue" x1="333.3" y1="666.7" x2="333.3" y2="722.2"/>
  <line stroke="red" x1="333.3" y1="666.7" x2="500" y2="666.7"/>
  <line stroke="black" x1="0" y1="777.8" x2="0" y2="833.3"/>
  <line stroke="red" x1="0" y1="777.8" x2="333.3" y2="777.8"/>
  <line stroke="red" x1="777.8" y1="55.6" x2="833.3" y2="0"/>
  <line stroke="red" x1="777.8" y1="55.6" x2="777.8" y2="555.6"/>
  <line stroke="red" x1="555.6" y1="555.6" x2="500" y2="611.1"/>
  <line stroke="blue" x1="555.6" y1="555.6" x2="611.1" y2="500"/>
  <line stroke="red" x1="555.6" y1="555.6" x2="666.7" y2="555.6"/>
  <line stroke="blue" x1="500" y1="611.1" x2="500" y2="666.7"/>
  <line stroke="blue" x1="500" y1="611.1" x2="666.7" y2="611.1"/>
  <line stroke="red" x1="611.1" y1="500" x2="666.7" y2="444.4"/>
  <line stroke="blue" x1="611.1" y1="500" x2="666.7" y2="500"/>
  <line stroke="red" x1="333.3" y1="722.2" x2="333.3" y2="777.8"/>
  <line stroke="blue" x1="333.3" y1="722.2" x2="500" y2="722.2"/>
  <line stroke="blue" x1="666.7" y1="444.4" x2="666.7" y2="500"/>
  <line stroke="red" x1="666.7" y1="444.4" x2="722.2" y2="500"/>
  <line stroke="black" x1="0" y1="833.3" x2="0" y2="888.9"/>
  <line stroke="blue" x1="0" y1="833.3" x2="333.3" y2="833.3"/>
  <line stroke="red" x1="500" y1="666.7" x2="500" y2="722.2"/>
  <line stroke="red" x1="500" y1="666.7" x2="666.7" y2="666.7"/>
  <line stroke="red" x1="666.7" y1="500" x2="666.7" y2="555.6"/>
  <line stroke="blue" x1="666.7" y1="500" x2="722.2" y2="500"/>
  <line stroke="black" x1="833.3" y1="0" x2="888.9" y2="0"/>
  <line stroke="blue" x1="833.3" y1="0" x2="833.3" y2="611.1"/>
  <line stroke="blue" x1="333.3" y1="777.8" x2="333.3" y2="833.3"/>
  <line stroke="red" x1="333.3" y1="777.8" x2="500" y2="777.8"/>
  <line stroke="blue" x1="666.7" y1="555.6" x2="666.7" y2="611.1"/>
  <line stroke="red" x1="666.7" y1="555.6" x2="777.8" y2="555.6"/>
  <line stroke="blue" x1="500" y1="722.2" x2="500" y2="777.8"/>
  <line stroke="blue" x1="500" y1="722.2" x2="666.7" y2="722.2"/>
  <line stroke="blue" x1="722.2" y1="500" x2="777.8" y2="555.6"/>
  <line stroke="black" x1="0" y1="888.9" x2="0" y2="944.4"/>
  <line stroke="red" x1="0" y1="888.9" x2="333.3" y2="888.9"/>
  <line stroke="black" x1="888.9" y1="0" x2="944.4" y2="0"/>
  <line stroke="red" x1="888.9" y1="0" x2="888.9" y2="666.7"/>
  <line stroke="red" x1="333.3" y1="833.3" x2="333.3" y2="888.9"/>
  <line stroke="blue" x1="333.3" y1="833.3" x2="500" y2="833.3"/>
  <line stroke="red" x1="666.7" y1="611.1" x2="666.7" y2="666.7"/>
  <line stroke="blue" x1="666.7" y1="611.1" x2="833.3" y2="611.1"/>
  <line stroke="red" x1="500" y1="777.8" x2="500" y2="833.3"/>
  <line stroke="red" x1="500" y1="777.8" x2="666.7" y2="777.8"/>
  <line stroke="blue" x1="666.7" y1="666.7" x2="666.7" y2="722.2"/>
  <line stroke="red" x1="666.7" y1="666.7" x2="888.9" y2="666.7"/>
  <line stroke="black" x1="0" y1="944.4" x2="0" y2="1000"/>
  <line stroke="blue" x1="0" y1="944.4" x2="333.3" y2="944.4"/>
  <line stroke="black" x1="944.4" y1="0" x2="1000" y2="0"/>
  <line stroke="blue" x1="944.4" y1="0" x2="944.4" y2="722.2"/>
  <line stroke="blue" x1="333.3" y1="888.9" x2="333.3" y2="944.4"/>
  <line stroke="red" x1="333.3" y1="888.9" x2="500" y2="888.9"/>
  <line stroke="red" x1="777.8" y1="555.6" x2="833.3" y2="611.1"/>
  <line stroke="blue" x1="500" y1="833.3" x2="500" y2="888.9"/>
  <line stroke="blue" x1="500" y1="833.3" x2="666.7" y2="833.3"/>
  <line stroke="red" x1="666.7" y1="722.2" x2="666.7" y2="777.8"/>
  <line stroke="blue" x1="666.7" y1="722.2" x2="944.4" y2="722.2"/>
  <line stroke="black" x1="0" y1="1000" x2="333.3" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="777.8"/>
  <line stroke="red" x1="333.3" y1="944.4" x2="333.3" y2="1000"/>
  <line stroke="blue" x1="333.3" y1="944.4" x2="500" y2="944.4"/>
  <line stroke="red" x1="500" y1="888.9" x2="500" y2="944.4"/>
  <line stroke="red" x1="500" y1="888.9" x2="666.7" y2="888.9"/>
  <line stroke="blue" x1="666.7" y1="777.8" x2="666.7" y2="833.3"/>
  <line stroke="red" x1="666.7" y1="777.8" x2="1000" y2="777.8"/>
  <line stroke="blue" x1="833.3" y1="611.1" x2="888.9" y2="666.7"/>
  <line stroke="black" x1="333.3" y1="1000" x2="500" y2="1000"/>
  <line stroke="red" x1="666.7" y1="833.3" x2="666.7" y2="888.9"/>
  <line stroke="blue" x1="666.7" y1="833.3" x2="1000" y2="833.3"/>
  <line stroke="blue" x1="500" y1="944.4" x2="500" y2="1000"/>
  <line stroke="blue" x1="500" y1="944.4" x2="666.7" y2="944.4"/>
  <line stroke="blue" x1="666.7" y1="888.9" x2="666.7" y2="944.4"/>
  <line stroke="red" x1="666.7" y1="888.9" x2="1000" y2="888.9"/>
  <line stroke="red" x1="888.9" y1="666.7" x2="944.4" y2="722.2"/>
  <line stroke="black" x1="500" y1="1000" x2="666.7" y2="1000"/>
  <line stroke="red" x1="666.7" y1="944.4" x2="666.7" y2="1000"/>
  <line stroke="blue" x1="666.7" y1="944.4" x2="1000" y2="944.4"/>
  <line stroke="blue" x1="944.4" y1="722.2" x2="1000" y2="777.8"/>
  <line stroke="black" x1="666.7" y1="1000" x2="1000" y2="1000"/>
  <line stroke="black" x1="1000" y1="777.8" x2="1000" y2="833.3"/>
  <line stroke="black" x1="1000" y1="833.3" x2="1000" y2="888.9"/>
  <line stroke="black" x1="1000" y1="888.9" x2="1000" y2="944.4"/>
  <line stroke="black" x1="1000" y1="944.4" x2="1000" y2="1000"/>
</svg>""",
)

INFINITE_NARROWING_EDGE_CASE = BoxPleatingCreasePatternExample(
    name="infinite_narrowing_edge_case",
    grid_size=14,
    packing_svg="",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="red" x1="0" y1="0" x2="71.4" y2="71.4"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="285.7"/>
  <line stroke="black" x1="0" y1="0" x2="571.4" y2="0"/>
  <line stroke="blue" x1="71.4" y1="71.4" x2="142.9" y2="142.9"/>
  <line stroke="red" x1="71.4" y1="71.4" x2="71.4" y2="285.7"/>
  <line stroke="red" x1="71.4" y1="71.4" x2="500" y2="71.4"/>
  <line stroke="red" x1="142.9" y1="142.9" x2="214.3" y2="214.3"/>
  <line stroke="blue" x1="142.9" y1="142.9" x2="142.9" y2="285.7"/>
  <line stroke="blue" x1="142.9" y1="142.9" x2="428.6" y2="142.9"/>
  <line stroke="blue" x1="0" y1="285.7" x2="71.4" y2="285.7"/>
  <line stroke="black" x1="0" y1="285.7" x2="0" y2="928.6"/>
  <line stroke="red" x1="71.4" y1="285.7" x2="142.9" y2="285.7"/>
  <line stroke="red" x1="71.4" y1="285.7" x2="71.4" y2="857.1"/>
  <line stroke="red" x1="214.3" y1="214.3" x2="214.3" y2="285.7"/>
  <line stroke="blue" x1="214.3" y1="214.3" x2="285.7" y2="285.7"/>
  <line stroke="red" x1="214.3" y1="214.3" x2="357.1" y2="214.3"/>
  <line stroke="blue" x1="142.9" y1="285.7" x2="214.3" y2="285.7"/>
  <line stroke="blue" x1="142.9" y1="285.7" x2="142.9" y2="785.7"/>
  <line stroke="red" x1="214.3" y1="285.7" x2="285.7" y2="285.7"/>
  <line stroke="red" x1="214.3" y1="285.7" x2="214.3" y2="714.3"/>
  <line stroke="blue" x1="285.7" y1="285.7" x2="357.1" y2="214.3"/>
  <line stroke="blue" x1="285.7" y1="285.7" x2="285.7" y2="642.9"/>
  <line stroke="red" x1="357.1" y1="214.3" x2="428.6" y2="142.9"/>
  <line stroke="red" x1="357.1" y1="214.3" x2="357.1" y2="571.4"/>
  <line stroke="blue" x1="428.6" y1="142.9" x2="500" y2="71.4"/>
  <line stroke="blue" x1="428.6" y1="142.9" x2="428.6" y2="500"/>
  <line stroke="red" x1="500" y1="71.4" x2="571.4" y2="0"/>
  <line stroke="red" x1="500" y1="71.4" x2="500" y2="500"/>
  <line stroke="black" x1="571.4" y1="0" x2="642.9" y2="0"/>
  <line stroke="blue" x1="571.4" y1="0" x2="571.4" y2="500"/>
  <line stroke="black" x1="642.9" y1="0" x2="714.3" y2="0"/>
  <line stroke="red" x1="642.9" y1="0" x2="642.9" y2="500"/>
  <line stroke="blue" x1="428.6" y1="500" x2="357.1" y2="571.4"/>
  <line stroke="red" x1="428.6" y1="500" x2="500" y2="500"/>
  <line stroke="blue" x1="428.6" y1="500" x2="500" y2="571.4"/>
  <line stroke="red" x1="357.1" y1="571.4" x2="285.7" y2="642.9"/>
  <line stroke="red" x1="357.1" y1="571.4" x2="500" y2="571.4"/>
  <line stroke="blue" x1="285.7" y1="642.9" x2="214.3" y2="714.3"/>
  <line stroke="blue" x1="285.7" y1="642.9" x2="571.4" y2="642.9"/>
  <line stroke="red" x1="500" y1="500" x2="500" y2="571.4"/>
  <line stroke="blue" x1="500" y1="500" x2="571.4" y2="500"/>
  <line stroke="black" x1="714.3" y1="0" x2="785.7" y2="0"/>
  <line stroke="blue" x1="714.3" y1="0" x2="714.3" y2="500"/>
  <line stroke="red" x1="214.3" y1="714.3" x2="142.9" y2="785.7"/>
  <line stroke="red" x1="214.3" y1="714.3" x2="571.4" y2="714.3"/>
  <line stroke="red" x1="500" y1="571.4" x2="571.4" y2="642.9"/>
  <line stroke="red" x1="571.4" y1="500" x2="642.9" y2="500"/>
  <line stroke="blue" x1="571.4" y1="500" x2="571.4" y2="642.9"/>
  <line stroke="black" x1="785.7" y1="0" x2="857.1" y2="0"/>
  <line stroke="red" x1="785.7" y1="0" x2="785.7" y2="500"/>
  <line stroke="blue" x1="142.9" y1="785.7" x2="71.4" y2="857.1"/>
  <line stroke="blue" x1="142.9" y1="785.7" x2="571.4" y2="785.7"/>
  <line stroke="red" x1="642.9" y1="500" x2="642.9" y2="571.4"/>
  <line stroke="blue" x1="642.9" y1="500" x2="714.3" y2="500"/>
  <line stroke="black" x1="857.1" y1="0" x2="928.6" y2="0"/>
  <line stroke="blue" x1="857.1" y1="0" x2="857.1" y2="500"/>
  <line stroke="red" x1="71.4" y1="857.1" x2="0" y2="928.6"/>
  <line stroke="red" x1="71.4" y1="857.1" x2="571.4" y2="857.1"/>
  <line stroke="red" x1="571.4" y1="642.9" x2="642.9" y2="571.4"/>
  <line stroke="blue" x1="571.4" y1="642.9" x2="571.4" y2="714.3"/>
  <line stroke="blue" x1="571.4" y1="642.9" x2="714.3" y2="642.9"/>
  <line stroke="blue" x1="642.9" y1="571.4" x2="714.3" y2="500"/>
  <line stroke="red" x1="642.9" y1="571.4" x2="714.3" y2="571.4"/>
  <line stroke="red" x1="714.3" y1="500" x2="714.3" y2="571.4"/>
  <line stroke="red" x1="714.3" y1="500" x2="785.7" y2="500"/>
  <line stroke="blue" x1="714.3" y1="500" x2="785.7" y2="571.4"/>
  <line stroke="red" x1="571.4" y1="714.3" x2="571.4" y2="785.7"/>
  <line stroke="red" x1="571.4" y1="714.3" x2="714.3" y2="714.3"/>
  <line stroke="blue" x1="714.3" y1="571.4" x2="714.3" y2="642.9"/>
  <line stroke="red" x1="714.3" y1="571.4" x2="785.7" y2="571.4"/>
  <line stroke="black" x1="0" y1="928.6" x2="0" y2="1000"/>
  <line stroke="blue" x1="0" y1="928.6" x2="571.4" y2="928.6"/>
  <line stroke="black" x1="928.6" y1="0" x2="1000" y2="0"/>
  <line stroke="red" x1="928.6" y1="0" x2="928.6" y2="500"/>
  <line stroke="red" x1="785.7" y1="500" x2="785.7" y2="571.4"/>
  <line stroke="blue" x1="785.7" y1="500" x2="857.1" y2="500"/>
  <line stroke="red" x1="714.3" y1="642.9" x2="714.3" y2="714.3"/>
  <line stroke="blue" x1="714.3" y1="642.9" x2="857.1" y2="642.9"/>
  <line stroke="blue" x1="571.4" y1="785.7" x2="571.4" y2="857.1"/>
  <line stroke="blue" x1="571.4" y1="785.7" x2="714.3" y2="785.7"/>
  <line stroke="red" x1="785.7" y1="571.4" x2="857.1" y2="642.9"/>
  <line stroke="red" x1="857.1" y1="500" x2="928.6" y2="500"/>
  <line stroke="blue" x1="857.1" y1="500" x2="857.1" y2="642.9"/>
  <line stroke="black" x1="0" y1="1000" x2="571.4" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="500"/>
  <line stroke="blue" x1="714.3" y1="714.3" x2="714.3" y2="785.7"/>
  <line stroke="red" x1="714.3" y1="714.3" x2="928.6" y2="714.3"/>
  <line stroke="red" x1="571.4" y1="857.1" x2="571.4" y2="928.6"/>
  <line stroke="red" x1="571.4" y1="857.1" x2="714.3" y2="857.1"/>
  <line stroke="blue" x1="928.6" y1="500" x2="1000" y2="500"/>
  <line stroke="red" x1="928.6" y1="500" x2="928.6" y2="714.3"/>
  <line stroke="red" x1="714.3" y1="785.7" x2="714.3" y2="857.1"/>
  <line stroke="blue" x1="714.3" y1="785.7" x2="1000" y2="785.7"/>
  <line stroke="blue" x1="857.1" y1="642.9" x2="928.6" y2="714.3"/>
  <line stroke="blue" x1="571.4" y1="928.6" x2="571.4" y2="1000"/>
  <line stroke="blue" x1="571.4" y1="928.6" x2="714.3" y2="928.6"/>
  <line stroke="blue" x1="714.3" y1="857.1" x2="714.3" y2="928.6"/>
  <line stroke="red" x1="714.3" y1="857.1" x2="1000" y2="857.1"/>
  <line stroke="black" x1="1000" y1="500" x2="1000" y2="785.7"/>
  <line stroke="black" x1="571.4" y1="1000" x2="714.3" y2="1000"/>
  <line stroke="red" x1="714.3" y1="928.6" x2="714.3" y2="1000"/>
  <line stroke="blue" x1="714.3" y1="928.6" x2="1000" y2="928.6"/>
  <line stroke="red" x1="928.6" y1="714.3" x2="1000" y2="785.7"/>
  <line stroke="black" x1="714.3" y1="1000" x2="1000" y2="1000"/>
  <line stroke="black" x1="1000" y1="785.7" x2="1000" y2="857.1"/>
  <line stroke="black" x1="1000" y1="857.1" x2="1000" y2="928.6"/>
  <line stroke="black" x1="1000" y1="928.6" x2="1000" y2="1000"/>
</svg>""",
)

GEMINI = BoxPleatingCreasePatternExample(
    name="gemini",
    grid_size=14,
    tree_data={
        "version": "0.7",
        "design": {
            "title": "Untitled",
            "mode": "tree",
            "description": "",
            "layout": {
                "sheet": {"type": "rect", "height": 32, "width": 16},
                "flaps": [
                    {"id": 2, "x": 16, "y": 32, "width": 0, "height": 0},
                    {"id": 3, "x": 2, "y": 16, "width": 0, "height": 0},
                    {"id": 5, "x": 9, "y": 26, "width": 0, "height": 0},
                    {"id": 6, "x": 13, "y": 25, "width": 0, "height": 0},
                    {"id": 7, "x": 5, "y": 27, "width": 0, "height": 0},
                    {"id": 8, "x": 4, "y": 29, "width": 0, "height": 0},
                    {"id": 10, "x": 16, "y": 0, "width": 0, "height": 0},
                    {"id": 11, "x": 0, "y": 0, "width": 0, "height": 0},
                ],
                "stretches": [],
            },
            "tree": {
                "sheet": {"type": "rect", "height": 20, "width": 20},
                "nodes": [
                    {"id": 0, "name": "", "x": 10, "y": 6},
                    {"id": 1, "name": "", "x": 10, "y": 8},
                    {"id": 2, "name": "", "x": 13, "y": 6},
                    {"id": 3, "name": "", "x": 7, "y": 6},
                    {"id": 4, "name": "", "x": 10, "y": 10},
                    {"id": 5, "name": "", "x": 9, "y": 8},
                    {"id": 6, "name": "", "x": 11, "y": 8},
                    {"id": 7, "name": "", "x": 11, "y": 10},
                    {"id": 8, "name": "", "x": 9, "y": 10},
                    {"id": 9, "name": "", "x": 10, "y": 12},
                    {"id": 10, "name": "", "x": 7, "y": 12},
                    {"id": 11, "name": "", "x": 13, "y": 12},
                ],
                "edges": [
                    {"n1": 1, "n2": 4, "length": 2},
                    {"n1": 1, "n2": 0, "length": 2},
                    {"n1": 1, "n2": 6, "length": 1},
                    {"n1": 1, "n2": 5, "length": 1},
                    {"n1": 4, "n2": 9, "length": 2},
                    {"n1": 4, "n2": 8, "length": 1},
                    {"n1": 4, "n2": 7, "length": 1},
                    {"n1": 0, "n2": 3, "length": 3},
                    {"n1": 0, "n2": 2, "length": 3},
                    {"n1": 9, "n2": 10, "length": 3},
                    {"n1": 9, "n2": 11, "length": 3},
                ],
            },
        },
    },
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14">
  <line stroke="black" x1="0" y1="0" x2="0" y2="2"/>
  <line stroke="black" x1="0" y1="0" x2="2" y2="0"/>
  <line stroke="red" x1="0" y1="2" x2="2" y2="0"/>
  <line stroke="black" x1="0" y1="2" x2="0" y2="5"/>
  <line stroke="red" x1="0" y1="2" x2="3" y2="5"/>
  <line stroke="black" x1="2" y1="0" x2="3" y2="0"/>
  <line stroke="black" x1="3" y1="0" x2="5" y2="0"/>
  <line stroke="green" x1="3" y1="0" x2="3" y2="5"/>
  <line stroke="green" x1="0" y1="5" x2="3" y2="5"/>
  <line stroke="black" x1="0" y1="5" x2="0" y2="7"/>
  <line stroke="black" x1="5" y1="0" x2="6" y2="0"/>
  <line stroke="green" x1="5" y1="0" x2="5" y2="7"/>
  <line stroke="red" x1="3" y1="5" x2="5" y2="7"/>
  <line stroke="black" x1="6" y1="0" x2="7" y2="0"/>
  <line stroke="red" x1="6" y1="0" x2="6" y2="6"/>
  <line stroke="green" x1="0" y1="7" x2="5" y2="7"/>
  <line stroke="black" x1="0" y1="7" x2="0" y2="9"/>
  <line stroke="black" x1="7" y1="0" x2="8" y2="0"/>
  <line stroke="green" x1="7" y1="0" x2="7" y2="7"/>
  <line stroke="black" x1="8" y1="0" x2="9" y2="0"/>
  <line stroke="red" x1="8" y1="0" x2="8" y2="6"/>
  <line stroke="red" x1="6" y1="6" x2="5" y2="7"/>
  <line stroke="red" x1="6" y1="6" x2="7" y2="7"/>
  <line stroke="green" x1="5" y1="7" x2="7" y2="7"/>
  <line stroke="green" x1="0" y1="9" x2="5" y2="9"/>
  <line stroke="black" x1="0" y1="9" x2="0" y2="11"/>
  <line stroke="black" x1="9" y1="0" x2="11" y2="0"/>
  <line stroke="green" x1="9" y1="0" x2="9" y2="7"/>
  <line stroke="red" x1="7" y1="7" x2="8" y2="6"/>
  <line stroke="green" x1="7" y1="7" x2="9" y2="7"/>
  <line stroke="red" x1="8" y1="6" x2="9" y2="7"/>
  <line stroke="red" x1="5" y1="9" x2="3" y2="11"/>
  <line stroke="green" x1="5" y1="9" x2="7" y2="9"/>
  <line stroke="red" x1="5" y1="9" x2="6" y2="10"/>
  <line stroke="green" x1="5" y1="9" x2="5" y2="14"/>
  <line stroke="green" x1="0" y1="11" x2="3" y2="11"/>
  <line stroke="black" x1="0" y1="11" x2="0" y2="14"/>
  <line stroke="black" x1="11" y1="0" x2="12" y2="0"/>
  <line stroke="green" x1="11" y1="0" x2="11" y2="5"/>
  <line stroke="red" x1="3" y1="11" x2="0" y2="14"/>
  <line stroke="green" x1="3" y1="11" x2="3" y2="14"/>
  <line stroke="red" x1="7" y1="9" x2="6" y2="10"/>
  <line stroke="green" x1="7" y1="9" x2="9" y2="9"/>
  <line stroke="red" x1="7" y1="9" x2="8" y2="10"/>
  <line stroke="green" x1="7" y1="9" x2="7" y2="14"/>
  <line stroke="red" x1="9" y1="7" x2="11" y2="5"/>
  <line stroke="green" x1="9" y1="7" x2="14" y2="7"/>
  <line stroke="red" x1="6" y1="10" x2="6" y2="14"/>
  <line stroke="black" x1="12" y1="0" x2="14" y2="0"/>
  <line stroke="red" x1="12" y1="0" x2="14" y2="2"/>
  <line stroke="red" x1="11" y1="5" x2="14" y2="2"/>
  <line stroke="green" x1="11" y1="5" x2="14" y2="5"/>
  <line stroke="red" x1="9" y1="9" x2="8" y2="10"/>
  <line stroke="red" x1="9" y1="9" x2="11" y2="11"/>
  <line stroke="green" x1="9" y1="9" x2="9" y2="14"/>
  <line stroke="green" x1="9" y1="9" x2="14" y2="9"/>
  <line stroke="red" x1="8" y1="10" x2="8" y2="14"/>
  <line stroke="black" x1="0" y1="14" x2="3" y2="14"/>
  <line stroke="black" x1="14" y1="0" x2="14" y2="2"/>
  <line stroke="black" x1="14" y1="2" x2="14" y2="5"/>
  <line stroke="black" x1="3" y1="14" x2="5" y2="14"/>
  <line stroke="black" x1="5" y1="14" x2="6" y2="14"/>
  <line stroke="black" x1="14" y1="5" x2="14" y2="7"/>
  <line stroke="black" x1="6" y1="14" x2="7" y2="14"/>
  <line stroke="green" x1="11" y1="11" x2="11" y2="14"/>
  <line stroke="green" x1="11" y1="11" x2="14" y2="11"/>
  <line stroke="red" x1="11" y1="11" x2="14" y2="14"/>
  <line stroke="black" x1="7" y1="14" x2="8" y2="14"/>
  <line stroke="black" x1="14" y1="7" x2="14" y2="9"/>
  <line stroke="black" x1="8" y1="14" x2="9" y2="14"/>
  <line stroke="black" x1="9" y1="14" x2="11" y2="14"/>
  <line stroke="black" x1="14" y1="9" x2="14" y2="11"/>
  <line stroke="black" x1="11" y1="14" x2="14" y2="14"/>
  <line stroke="black" x1="14" y1="11" x2="14" y2="14"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14">
  <line stroke="black" x1="0" y1="0" x2="1" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="2"/>
  <line stroke="red" x1="1" y1="0" x2="1" y2="1"/>
  <line stroke="black" x1="1" y1="0" x2="2" y2="0"/>
  <line stroke="red" x1="1" y1="1" x2="0" y2="2"/>
  <line stroke="blue" x1="1" y1="1" x2="2" y2="0"/>
  <line stroke="red" x1="1" y1="1" x2="5" y2="1"/>
  <line stroke="red" x1="0" y1="2" x2="1" y2="3"/>
  <line stroke="blue" x1="0" y1="2" x2="5" y2="2"/>
  <line stroke="black" x1="0" y1="2" x2="0" y2="9"/>
  <line stroke="black" x1="2" y1="0" x2="5" y2="0"/>
  <line stroke="blue" x1="1" y1="3" x2="2" y2="4"/>
  <line stroke="red" x1="1" y1="3" x2="5" y2="3"/>
  <line stroke="red" x1="1" y1="3" x2="1" y2="9"/>
  <line stroke="red" x1="2" y1="4" x2="3" y2="5"/>
  <line stroke="blue" x1="2" y1="4" x2="5" y2="4"/>
  <line stroke="blue" x1="2" y1="4" x2="2" y2="9"/>
  <line stroke="blue" x1="5" y1="0" x2="5" y2="1"/>
  <line stroke="black" x1="5" y1="0" x2="6" y2="0"/>
  <line stroke="red" x1="5" y1="1" x2="5" y2="2"/>
  <line stroke="red" x1="5" y1="1" x2="6" y2="1"/>
  <line stroke="blue" x1="5" y1="2" x2="5" y2="3"/>
  <line stroke="blue" x1="5" y1="2" x2="6" y2="2"/>
  <line stroke="red" x1="3" y1="5" x2="5" y2="5"/>
  <line stroke="blue" x1="3" y1="5" x2="4" y2="6"/>
  <line stroke="red" x1="3" y1="5" x2="3" y2="9"/>
  <line stroke="red" x1="5" y1="3" x2="5" y2="4"/>
  <line stroke="red" x1="5" y1="3" x2="6" y2="3"/>
  <line stroke="red" x1="6" y1="0" x2="6" y2="1"/>
  <line stroke="black" x1="6" y1="0" x2="7" y2="0"/>
  <line stroke="blue" x1="6" y1="1" x2="6" y2="2"/>
  <line stroke="red" x1="6" y1="1" x2="7" y2="1"/>
  <line stroke="red" x1="6" y1="2" x2="6" y2="3"/>
  <line stroke="blue" x1="6" y1="2" x2="7" y2="2"/>
  <line stroke="blue" x1="5" y1="4" x2="5" y2="5"/>
  <line stroke="blue" x1="5" y1="4" x2="6" y2="4"/>
  <line stroke="blue" x1="6" y1="3" x2="6" y2="4"/>
  <line stroke="red" x1="6" y1="3" x2="7" y2="3"/>
  <line stroke="blue" x1="7" y1="0" x2="7" y2="1"/>
  <line stroke="black" x1="7" y1="0" x2="8" y2="0"/>
  <line stroke="red" x1="5" y1="5" x2="5" y2="6"/>
  <line stroke="red" x1="5" y1="5" x2="6" y2="5"/>
  <line stroke="red" x1="7" y1="1" x2="7" y2="2"/>
  <line stroke="red" x1="7" y1="1" x2="8" y2="1"/>
  <line stroke="blue" x1="4" y1="6" x2="5" y2="6"/>
  <line stroke="red" x1="4" y1="6" x2="5" y2="7"/>
  <line stroke="blue" x1="4" y1="6" x2="4" y2="9"/>
  <line stroke="red" x1="6" y1="4" x2="6" y2="5"/>
  <line stroke="blue" x1="6" y1="4" x2="7" y2="4"/>
  <line stroke="blue" x1="7" y1="2" x2="7" y2="3"/>
  <line stroke="blue" x1="7" y1="2" x2="8" y2="2"/>
  <line stroke="red" x1="7" y1="3" x2="7" y2="4"/>
  <line stroke="red" x1="7" y1="3" x2="8" y2="3"/>
  <line stroke="blue" x1="5" y1="6" x2="6" y2="6"/>
  <line stroke="blue" x1="5" y1="6" x2="5" y2="7"/>
  <line stroke="blue" x1="6" y1="5" x2="6" y2="6"/>
  <line stroke="red" x1="6" y1="5" x2="7" y2="5"/>
  <line stroke="red" x1="8" y1="0" x2="8" y2="1"/>
  <line stroke="black" x1="8" y1="0" x2="9" y2="0"/>
  <line stroke="blue" x1="7" y1="4" x2="7" y2="5"/>
  <line stroke="blue" x1="7" y1="4" x2="8" y2="4"/>
  <line stroke="blue" x1="8" y1="1" x2="8" y2="2"/>
  <line stroke="red" x1="8" y1="1" x2="9" y2="1"/>
  <line stroke="red" x1="8" y1="2" x2="8" y2="3"/>
  <line stroke="blue" x1="8" y1="2" x2="9" y2="2"/>
  <line stroke="red" x1="6" y1="6" x2="5" y2="7"/>
  <line stroke="blue" x1="6" y1="6" x2="7" y2="6"/>
  <line stroke="red" x1="6" y1="6" x2="7" y2="7"/>
  <line stroke="blue" x1="6" y1="6" x2="6" y2="10"/>
  <line stroke="blue" x1="8" y1="3" x2="8" y2="4"/>
  <line stroke="red" x1="8" y1="3" x2="9" y2="3"/>
  <line stroke="red" x1="5" y1="7" x2="5" y2="9"/>
  <line stroke="red" x1="7" y1="5" x2="7" y2="6"/>
  <line stroke="red" x1="7" y1="5" x2="8" y2="5"/>
  <line stroke="red" x1="8" y1="4" x2="8" y2="5"/>
  <line stroke="blue" x1="8" y1="4" x2="9" y2="4"/>
  <line stroke="blue" x1="0" y1="9" x2="1" y2="9"/>
  <line stroke="black" x1="0" y1="9" x2="0" y2="14"/>
  <line stroke="blue" x1="9" y1="0" x2="9" y2="1"/>
  <line stroke="black" x1="9" y1="0" x2="12" y2="0"/>
  <line stroke="red" x1="1" y1="9" x2="2" y2="9"/>
  <line stroke="red" x1="1" y1="9" x2="1" y2="13"/>
  <line stroke="red" x1="9" y1="1" x2="9" y2="2"/>
  <line stroke="red" x1="9" y1="1" x2="13" y2="1"/>
  <line stroke="blue" x1="7" y1="6" x2="7" y2="7"/>
  <line stroke="blue" x1="7" y1="6" x2="8" y2="6"/>
  <line stroke="blue" x1="2" y1="9" x2="3" y2="9"/>
  <line stroke="blue" x1="2" y1="9" x2="2" y2="12"/>
  <line stroke="blue" x1="9" y1="2" x2="9" y2="3"/>
  <line stroke="blue" x1="9" y1="2" x2="14" y2="2"/>
  <line stroke="blue" x1="8" y1="5" x2="8" y2="6"/>
  <line stroke="red" x1="8" y1="5" x2="9" y2="5"/>
  <line stroke="red" x1="3" y1="9" x2="4" y2="9"/>
  <line stroke="red" x1="3" y1="9" x2="3" y2="11"/>
  <line stroke="red" x1="9" y1="3" x2="9" y2="4"/>
  <line stroke="red" x1="9" y1="3" x2="13" y2="3"/>
  <line stroke="blue" x1="4" y1="9" x2="5" y2="9"/>
  <line stroke="blue" x1="4" y1="9" x2="4" y2="10"/>
  <line stroke="blue" x1="9" y1="4" x2="9" y2="5"/>
  <line stroke="blue" x1="9" y1="4" x2="12" y2="4"/>
  <line stroke="red" x1="7" y1="7" x2="8" y2="6"/>
  <line stroke="red" x1="7" y1="7" x2="7" y2="9"/>
  <line stroke="blue" x1="8" y1="6" x2="9" y2="6"/>
  <line stroke="red" x1="8" y1="6" x2="9" y2="7"/>
  <line stroke="blue" x1="8" y1="6" x2="8" y2="10"/>
  <line stroke="red" x1="5" y1="9" x2="4" y2="10"/>
  <line stroke="red" x1="5" y1="9" x2="6" y2="10"/>
  <line stroke="red" x1="9" y1="5" x2="9" y2="6"/>
  <line stroke="red" x1="9" y1="5" x2="11" y2="5"/>
  <line stroke="blue" x1="4" y1="10" x2="3" y2="11"/>
  <line stroke="blue" x1="4" y1="10" x2="6" y2="10"/>
  <line stroke="blue" x1="9" y1="6" x2="9" y2="7"/>
  <line stroke="blue" x1="9" y1="6" x2="10" y2="6"/>
  <line stroke="red" x1="3" y1="11" x2="2" y2="12"/>
  <line stroke="red" x1="3" y1="11" x2="6" y2="11"/>
  <line stroke="red" x1="7" y1="9" x2="6" y2="10"/>
  <line stroke="blue" x1="7" y1="9" x2="7" y2="10"/>
  <line stroke="red" x1="7" y1="9" x2="8" y2="10"/>
  <line stroke="red" x1="9" y1="7" x2="10" y2="6"/>
  <line stroke="red" x1="9" y1="7" x2="9" y2="9"/>
  <line stroke="blue" x1="6" y1="10" x2="7" y2="10"/>
  <line stroke="blue" x1="6" y1="10" x2="6" y2="11"/>
  <line stroke="blue" x1="10" y1="6" x2="11" y2="5"/>
  <line stroke="blue" x1="10" y1="6" x2="10" y2="9"/>
  <line stroke="black" x1="12" y1="0" x2="13" y2="0"/>
  <line stroke="blue" x1="12" y1="0" x2="13" y2="1"/>
  <line stroke="red" x1="11" y1="5" x2="12" y2="4"/>
  <line stroke="red" x1="11" y1="5" x2="11" y2="9"/>
  <line stroke="blue" x1="2" y1="12" x2="1" y2="13"/>
  <line stroke="blue" x1="2" y1="12" x2="6" y2="12"/>
  <line stroke="blue" x1="7" y1="10" x2="8" y2="10"/>
  <line stroke="red" x1="7" y1="10" x2="7" y2="11"/>
  <line stroke="red" x1="6" y1="11" x2="7" y2="11"/>
  <line stroke="red" x1="6" y1="11" x2="6" y2="12"/>
  <line stroke="blue" x1="12" y1="4" x2="13" y2="3"/>
  <line stroke="blue" x1="12" y1="4" x2="12" y2="9"/>
  <line stroke="red" x1="9" y1="9" x2="8" y2="10"/>
  <line stroke="blue" x1="9" y1="9" x2="10" y2="9"/>
  <line stroke="red" x1="9" y1="9" x2="10" y2="10"/>
  <line stroke="blue" x1="8" y1="10" x2="8" y2="11"/>
  <line stroke="blue" x1="8" y1="10" x2="10" y2="10"/>
  <line stroke="red" x1="13" y1="0" x2="13" y2="1"/>
  <line stroke="black" x1="13" y1="0" x2="14" y2="0"/>
  <line stroke="red" x1="1" y1="13" x2="0" y2="14"/>
  <line stroke="red" x1="1" y1="13" x2="6" y2="13"/>
  <line stroke="red" x1="7" y1="11" x2="8" y2="11"/>
  <line stroke="blue" x1="7" y1="11" x2="7" y2="12"/>
  <line stroke="red" x1="13" y1="1" x2="14" y2="2"/>
  <line stroke="red" x1="13" y1="3" x2="14" y2="2"/>
  <line stroke="red" x1="13" y1="3" x2="13" y2="9"/>
  <line stroke="blue" x1="6" y1="12" x2="7" y2="12"/>
  <line stroke="blue" x1="6" y1="12" x2="6" y2="13"/>
  <line stroke="blue" x1="10" y1="9" x2="10" y2="10"/>
  <line stroke="red" x1="10" y1="9" x2="11" y2="9"/>
  <line stroke="red" x1="8" y1="11" x2="8" y2="12"/>
  <line stroke="red" x1="8" y1="11" x2="11" y2="11"/>
  <line stroke="blue" x1="7" y1="12" x2="8" y2="12"/>
  <line stroke="red" x1="7" y1="12" x2="7" y2="13"/>
  <line stroke="black" x1="0" y1="14" x2="6" y2="14"/>
  <line stroke="black" x1="14" y1="0" x2="14" y2="2"/>
  <line stroke="blue" x1="10" y1="10" x2="11" y2="11"/>
  <line stroke="black" x1="14" y1="2" x2="14" y2="9"/>
  <line stroke="blue" x1="11" y1="9" x2="12" y2="9"/>
  <line stroke="red" x1="11" y1="9" x2="11" y2="11"/>
  <line stroke="red" x1="6" y1="13" x2="7" y2="13"/>
  <line stroke="red" x1="6" y1="13" x2="6" y2="14"/>
  <line stroke="blue" x1="8" y1="12" x2="8" y2="13"/>
  <line stroke="blue" x1="8" y1="12" x2="12" y2="12"/>
  <line stroke="red" x1="7" y1="13" x2="8" y2="13"/>
  <line stroke="blue" x1="7" y1="13" x2="7" y2="14"/>
  <line stroke="red" x1="12" y1="9" x2="13" y2="9"/>
  <line stroke="blue" x1="12" y1="9" x2="12" y2="12"/>
  <line stroke="black" x1="6" y1="14" x2="7" y2="14"/>
  <line stroke="red" x1="8" y1="13" x2="8" y2="14"/>
  <line stroke="red" x1="8" y1="13" x2="13" y2="13"/>
  <line stroke="red" x1="11" y1="11" x2="12" y2="12"/>
  <line stroke="black" x1="7" y1="14" x2="8" y2="14"/>
  <line stroke="blue" x1="13" y1="9" x2="14" y2="9"/>
  <line stroke="red" x1="13" y1="9" x2="13" y2="13"/>
  <line stroke="black" x1="8" y1="14" x2="14" y2="14"/>
  <line stroke="black" x1="14" y1="9" x2="14" y2="14"/>
  <line stroke="blue" x1="12" y1="12" x2="13" y2="13"/>
  <line stroke="red" x1="13" y1="13" x2="14" y2="14"/>
</svg>""",
)

GEMINI_V2 = BoxPleatingCreasePatternExample(
    name="gemini_v2",
    grid_size=16,
    tree_data=None,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <line stroke="black" x1="0" y1="0" x2="0" y2="2"/>
  <line stroke="black" x1="0" y1="0" x2="2" y2="0"/>
  <line stroke="red" x1="0" y1="2" x2="2" y2="0"/>
  <line stroke="black" x1="0" y1="2" x2="0" y2="5"/>
  <line stroke="red" x1="0" y1="2" x2="3" y2="5"/>
  <line stroke="black" x1="2" y1="0" x2="3" y2="0"/>
  <line stroke="black" x1="3" y1="0" x2="5" y2="0"/>
  <line stroke="green" x1="3" y1="0" x2="3" y2="5"/>
  <line stroke="green" x1="0" y1="5" x2="3" y2="5"/>
  <line stroke="black" x1="0" y1="5" x2="0" y2="7"/>
  <line stroke="black" x1="5" y1="0" x2="7" y2="0"/>
  <line stroke="green" x1="5" y1="0" x2="5" y2="7"/>
  <line stroke="red" x1="3" y1="5" x2="5" y2="7"/>
  <line stroke="green" x1="0" y1="7" x2="5" y2="7"/>
  <line stroke="black" x1="0" y1="7" x2="0" y2="11"/>
  <line stroke="red" x1="7" y1="0" x2="7" y2="5"/>
  <line stroke="black" x1="7" y1="0" x2="9" y2="0"/>
  <line stroke="red" x1="5" y1="7" x2="7" y2="5"/>
  <line stroke="green" x1="5" y1="7" x2="9" y2="7"/>
  <line stroke="red" x1="7" y1="5" x2="9" y2="7"/>
  <line stroke="black" x1="9" y1="0" x2="10" y2="0"/>
  <line stroke="green" x1="9" y1="0" x2="9" y2="7"/>
  <line stroke="black" x1="10" y1="0" x2="11" y2="0"/>
  <line stroke="red" x1="10" y1="0" x2="10" y2="6"/>
  <line stroke="green" x1="0" y1="11" x2="5" y2="11"/>
  <line stroke="black" x1="0" y1="11" x2="0" y2="13"/>
  <line stroke="black" x1="11" y1="0" x2="13" y2="0"/>
  <line stroke="green" x1="11" y1="0" x2="11" y2="7"/>
  <line stroke="red" x1="9" y1="7" x2="10" y2="6"/>
  <line stroke="green" x1="9" y1="7" x2="11" y2="7"/>
  <line stroke="red" x1="10" y1="6" x2="11" y2="7"/>
  <line stroke="red" x1="5" y1="11" x2="3" y2="13"/>
  <line stroke="green" x1="5" y1="11" x2="9" y2="11"/>
  <line stroke="red" x1="5" y1="11" x2="7" y2="13"/>
  <line stroke="green" x1="5" y1="11" x2="5" y2="16"/>
  <line stroke="green" x1="0" y1="13" x2="3" y2="13"/>
  <line stroke="black" x1="0" y1="13" x2="0" y2="16"/>
  <line stroke="green" x1="13" y1="0" x2="13" y2="5"/>
  <line stroke="black" x1="13" y1="0" x2="14" y2="0"/>
  <line stroke="red" x1="11" y1="7" x2="13" y2="5"/>
  <line stroke="green" x1="11" y1="7" x2="16" y2="7"/>
  <line stroke="red" x1="3" y1="13" x2="0" y2="16"/>
  <line stroke="green" x1="3" y1="13" x2="3" y2="16"/>
  <line stroke="red" x1="13" y1="5" x2="16" y2="2"/>
  <line stroke="green" x1="13" y1="5" x2="16" y2="5"/>
  <line stroke="black" x1="14" y1="0" x2="16" y2="0"/>
  <line stroke="red" x1="14" y1="0" x2="16" y2="2"/>
  <line stroke="red" x1="9" y1="11" x2="7" y2="13"/>
  <line stroke="green" x1="9" y1="11" x2="11" y2="11"/>
  <line stroke="red" x1="9" y1="11" x2="10" y2="12"/>
  <line stroke="green" x1="9" y1="11" x2="9" y2="16"/>
  <line stroke="red" x1="7" y1="13" x2="7" y2="16"/>
  <line stroke="red" x1="11" y1="11" x2="10" y2="12"/>
  <line stroke="red" x1="11" y1="11" x2="13" y2="13"/>
  <line stroke="green" x1="11" y1="11" x2="11" y2="16"/>
  <line stroke="green" x1="11" y1="11" x2="16" y2="11"/>
  <line stroke="red" x1="10" y1="12" x2="10" y2="16"/>
  <line stroke="black" x1="0" y1="16" x2="3" y2="16"/>
  <line stroke="black" x1="16" y1="0" x2="16" y2="2"/>
  <line stroke="black" x1="16" y1="2" x2="16" y2="5"/>
  <line stroke="black" x1="3" y1="16" x2="5" y2="16"/>
  <line stroke="black" x1="5" y1="16" x2="7" y2="16"/>
  <line stroke="black" x1="16" y1="5" x2="16" y2="7"/>
  <line stroke="black" x1="7" y1="16" x2="9" y2="16"/>
  <line stroke="black" x1="16" y1="7" x2="16" y2="11"/>
  <line stroke="black" x1="9" y1="16" x2="10" y2="16"/>
  <line stroke="green" x1="13" y1="13" x2="13" y2="16"/>
  <line stroke="green" x1="13" y1="13" x2="16" y2="13"/>
  <line stroke="red" x1="13" y1="13" x2="16" y2="16"/>
  <line stroke="black" x1="10" y1="16" x2="11" y2="16"/>
  <line stroke="black" x1="11" y1="16" x2="13" y2="16"/>
  <line stroke="black" x1="16" y1="11" x2="16" y2="13"/>
  <line stroke="black" x1="13" y1="16" x2="16" y2="16"/>
  <line stroke="black" x1="16" y1="13" x2="16" y2="16"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <line stroke="black" x1="0" y1="0" x2="1" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="2"/>
  <line stroke="red" x1="1" y1="0" x2="1" y2="1"/>
  <line stroke="black" x1="1" y1="0" x2="2" y2="0"/>
  <line stroke="red" x1="1" y1="1" x2="0" y2="2"/>
  <line stroke="blue" x1="1" y1="1" x2="2" y2="0"/>
  <line stroke="red" x1="1" y1="1" x2="5" y2="1"/>
  <line stroke="red" x1="0" y1="2" x2="1" y2="3"/>
  <line stroke="blue" x1="0" y1="2" x2="5" y2="2"/>
  <line stroke="black" x1="0" y1="2" x2="0" y2="11"/>
  <line stroke="black" x1="2" y1="0" x2="5" y2="0"/>
  <line stroke="blue" x1="1" y1="3" x2="2" y2="4"/>
  <line stroke="red" x1="1" y1="3" x2="5" y2="3"/>
  <line stroke="red" x1="1" y1="3" x2="1" y2="11"/>
  <line stroke="red" x1="2" y1="4" x2="3" y2="5"/>
  <line stroke="blue" x1="2" y1="4" x2="5" y2="4"/>
  <line stroke="blue" x1="2" y1="4" x2="2" y2="11"/>
  <line stroke="blue" x1="5" y1="0" x2="5" y2="1"/>
  <line stroke="black" x1="5" y1="0" x2="7" y2="0"/>
  <line stroke="red" x1="5" y1="1" x2="5" y2="2"/>
  <line stroke="red" x1="5" y1="1" x2="7" y2="1"/>
  <line stroke="blue" x1="5" y1="2" x2="5" y2="3"/>
  <line stroke="blue" x1="5" y1="2" x2="7" y2="2"/>
  <line stroke="red" x1="3" y1="5" x2="5" y2="5"/>
  <line stroke="blue" x1="3" y1="5" x2="4" y2="6"/>
  <line stroke="red" x1="3" y1="5" x2="3" y2="11"/>
  <line stroke="red" x1="5" y1="3" x2="5" y2="4"/>
  <line stroke="red" x1="5" y1="3" x2="7" y2="3"/>
  <line stroke="blue" x1="5" y1="4" x2="5" y2="5"/>
  <line stroke="blue" x1="5" y1="4" x2="7" y2="4"/>
  <line stroke="red" x1="7" y1="0" x2="7" y2="1"/>
  <line stroke="black" x1="7" y1="0" x2="9" y2="0"/>
  <line stroke="red" x1="5" y1="5" x2="5" y2="6"/>
  <line stroke="red" x1="5" y1="5" x2="7" y2="5"/>
  <line stroke="blue" x1="7" y1="1" x2="7" y2="2"/>
  <line stroke="red" x1="7" y1="1" x2="9" y2="1"/>
  <line stroke="blue" x1="4" y1="6" x2="5" y2="6"/>
  <line stroke="red" x1="4" y1="6" x2="5" y2="7"/>
  <line stroke="blue" x1="4" y1="6" x2="4" y2="11"/>
  <line stroke="red" x1="7" y1="2" x2="7" y2="3"/>
  <line stroke="blue" x1="7" y1="2" x2="9" y2="2"/>
  <line stroke="blue" x1="7" y1="3" x2="7" y2="4"/>
  <line stroke="red" x1="7" y1="3" x2="9" y2="3"/>
  <line stroke="blue" x1="5" y1="6" x2="6" y2="6"/>
  <line stroke="blue" x1="5" y1="6" x2="5" y2="7"/>
  <line stroke="red" x1="7" y1="4" x2="7" y2="5"/>
  <line stroke="blue" x1="7" y1="4" x2="9" y2="4"/>
  <line stroke="red" x1="6" y1="6" x2="5" y2="7"/>
  <line stroke="blue" x1="6" y1="6" x2="7" y2="5"/>
  <line stroke="blue" x1="6" y1="6" x2="6" y2="11"/>
  <line stroke="red" x1="5" y1="7" x2="5" y2="11"/>
  <line stroke="blue" x1="7" y1="5" x2="8" y2="6"/>
  <line stroke="red" x1="7" y1="5" x2="9" y2="5"/>
  <line stroke="red" x1="7" y1="5" x2="7" y2="11"/>
  <line stroke="blue" x1="9" y1="0" x2="9" y2="1"/>
  <line stroke="black" x1="9" y1="0" x2="10" y2="0"/>
  <line stroke="red" x1="9" y1="1" x2="9" y2="2"/>
  <line stroke="red" x1="9" y1="1" x2="10" y2="1"/>
  <line stroke="blue" x1="9" y1="2" x2="9" y2="3"/>
  <line stroke="blue" x1="9" y1="2" x2="10" y2="2"/>
  <line stroke="red" x1="9" y1="3" x2="9" y2="4"/>
  <line stroke="red" x1="9" y1="3" x2="10" y2="3"/>
  <line stroke="blue" x1="9" y1="4" x2="9" y2="5"/>
  <line stroke="blue" x1="9" y1="4" x2="10" y2="4"/>
  <line stroke="blue" x1="8" y1="6" x2="9" y2="6"/>
  <line stroke="red" x1="8" y1="6" x2="9" y2="7"/>
  <line stroke="blue" x1="8" y1="6" x2="8" y2="11"/>
  <line stroke="red" x1="10" y1="0" x2="10" y2="1"/>
  <line stroke="black" x1="10" y1="0" x2="11" y2="0"/>
  <line stroke="blue" x1="10" y1="1" x2="10" y2="2"/>
  <line stroke="red" x1="10" y1="1" x2="11" y2="1"/>
  <line stroke="red" x1="10" y1="2" x2="10" y2="3"/>
  <line stroke="blue" x1="10" y1="2" x2="11" y2="2"/>
  <line stroke="red" x1="9" y1="5" x2="9" y2="6"/>
  <line stroke="red" x1="9" y1="5" x2="10" y2="5"/>
  <line stroke="blue" x1="10" y1="3" x2="10" y2="4"/>
  <line stroke="red" x1="10" y1="3" x2="11" y2="3"/>
  <line stroke="red" x1="10" y1="4" x2="10" y2="5"/>
  <line stroke="blue" x1="10" y1="4" x2="11" y2="4"/>
  <line stroke="blue" x1="9" y1="6" x2="9" y2="7"/>
  <line stroke="blue" x1="9" y1="6" x2="10" y2="6"/>
  <line stroke="blue" x1="0" y1="11" x2="1" y2="11"/>
  <line stroke="black" x1="0" y1="11" x2="0" y2="16"/>
  <line stroke="blue" x1="11" y1="0" x2="11" y2="1"/>
  <line stroke="black" x1="11" y1="0" x2="14" y2="0"/>
  <line stroke="red" x1="1" y1="11" x2="2" y2="11"/>
  <line stroke="red" x1="1" y1="11" x2="1" y2="15"/>
  <line stroke="red" x1="11" y1="1" x2="11" y2="2"/>
  <line stroke="red" x1="11" y1="1" x2="15" y2="1"/>
  <line stroke="blue" x1="2" y1="11" x2="3" y2="11"/>
  <line stroke="blue" x1="2" y1="11" x2="2" y2="14"/>
  <line stroke="blue" x1="10" y1="5" x2="10" y2="6"/>
  <line stroke="red" x1="10" y1="5" x2="11" y2="5"/>
  <line stroke="blue" x1="11" y1="2" x2="11" y2="3"/>
  <line stroke="blue" x1="11" y1="2" x2="16" y2="2"/>
  <line stroke="red" x1="3" y1="11" x2="4" y2="11"/>
  <line stroke="red" x1="3" y1="11" x2="3" y2="13"/>
  <line stroke="red" x1="9" y1="7" x2="10" y2="6"/>
  <line stroke="red" x1="9" y1="7" x2="9" y2="11"/>
  <line stroke="red" x1="11" y1="3" x2="11" y2="4"/>
  <line stroke="red" x1="11" y1="3" x2="15" y2="3"/>
  <line stroke="blue" x1="10" y1="6" x2="11" y2="6"/>
  <line stroke="red" x1="10" y1="6" x2="11" y2="7"/>
  <line stroke="blue" x1="10" y1="6" x2="10" y2="11"/>
  <line stroke="blue" x1="4" y1="11" x2="5" y2="11"/>
  <line stroke="blue" x1="4" y1="11" x2="4" y2="12"/>
  <line stroke="blue" x1="11" y1="4" x2="11" y2="5"/>
  <line stroke="blue" x1="11" y1="4" x2="14" y2="4"/>
  <line stroke="red" x1="5" y1="11" x2="6" y2="11"/>
  <line stroke="red" x1="5" y1="11" x2="4" y2="12"/>
  <line stroke="blue" x1="5" y1="11" x2="5" y2="12"/>
  <line stroke="red" x1="5" y1="11" x2="6" y2="12"/>
  <line stroke="red" x1="11" y1="5" x2="11" y2="6"/>
  <line stroke="red" x1="11" y1="5" x2="13" y2="5"/>
  <line stroke="blue" x1="6" y1="11" x2="7" y2="11"/>
  <line stroke="blue" x1="6" y1="11" x2="6" y2="12"/>
  <line stroke="blue" x1="11" y1="6" x2="11" y2="7"/>
  <line stroke="blue" x1="11" y1="6" x2="12" y2="6"/>
  <line stroke="blue" x1="4" y1="12" x2="5" y2="12"/>
  <line stroke="blue" x1="4" y1="12" x2="3" y2="13"/>
  <line stroke="blue" x1="5" y1="12" x2="6" y2="12"/>
  <line stroke="red" x1="5" y1="12" x2="5" y2="13"/>
  <line stroke="red" x1="7" y1="11" x2="8" y2="11"/>
  <line stroke="red" x1="7" y1="11" x2="7" y2="13"/>
  <line stroke="red" x1="11" y1="7" x2="12" y2="6"/>
  <line stroke="red" x1="11" y1="7" x2="11" y2="11"/>
  <line stroke="red" x1="3" y1="13" x2="5" y2="13"/>
  <line stroke="red" x1="3" y1="13" x2="2" y2="14"/>
  <line stroke="blue" x1="6" y1="12" x2="7" y2="13"/>
  <line stroke="blue" x1="12" y1="6" x2="13" y2="5"/>
  <line stroke="blue" x1="12" y1="6" x2="12" y2="12"/>
  <line stroke="blue" x1="8" y1="11" x2="9" y2="11"/>
  <line stroke="blue" x1="8" y1="11" x2="8" y2="12"/>
  <line stroke="red" x1="5" y1="13" x2="7" y2="13"/>
  <line stroke="blue" x1="5" y1="13" x2="5" y2="14"/>
  <line stroke="red" x1="13" y1="5" x2="14" y2="4"/>
  <line stroke="red" x1="13" y1="5" x2="13" y2="13"/>
  <line stroke="black" x1="14" y1="0" x2="15" y2="0"/>
  <line stroke="blue" x1="14" y1="0" x2="15" y2="1"/>
  <line stroke="blue" x1="2" y1="14" x2="5" y2="14"/>
  <line stroke="blue" x1="2" y1="14" x2="1" y2="15"/>
  <line stroke="red" x1="9" y1="11" x2="8" y2="12"/>
  <line stroke="red" x1="9" y1="11" x2="10" y2="11"/>
  <line stroke="blue" x1="9" y1="11" x2="9" y2="12"/>
  <line stroke="red" x1="9" y1="11" x2="10" y2="12"/>
  <line stroke="blue" x1="8" y1="12" x2="7" y2="13"/>
  <line stroke="blue" x1="8" y1="12" x2="9" y2="12"/>
  <line stroke="blue" x1="14" y1="4" x2="15" y2="3"/>
  <line stroke="blue" x1="14" y1="4" x2="14" y2="14"/>
  <line stroke="red" x1="7" y1="13" x2="7" y2="14"/>
  <line stroke="red" x1="7" y1="13" x2="9" y2="13"/>
  <line stroke="blue" x1="5" y1="14" x2="7" y2="14"/>
  <line stroke="red" x1="5" y1="14" x2="5" y2="15"/>
  <line stroke="blue" x1="10" y1="11" x2="11" y2="11"/>
  <line stroke="blue" x1="10" y1="11" x2="10" y2="12"/>
  <line stroke="blue" x1="9" y1="12" x2="10" y2="12"/>
  <line stroke="red" x1="9" y1="12" x2="9" y2="13"/>
  <line stroke="red" x1="15" y1="0" x2="15" y2="1"/>
  <line stroke="black" x1="15" y1="0" x2="16" y2="0"/>
  <line stroke="red" x1="1" y1="15" x2="5" y2="15"/>
  <line stroke="red" x1="1" y1="15" x2="0" y2="16"/>
  <line stroke="red" x1="15" y1="1" x2="16" y2="2"/>
  <line stroke="red" x1="15" y1="3" x2="16" y2="2"/>
  <line stroke="red" x1="15" y1="3" x2="15" y2="15"/>
  <line stroke="red" x1="11" y1="11" x2="10" y2="12"/>
  <line stroke="red" x1="11" y1="11" x2="12" y2="12"/>
  <line stroke="blue" x1="10" y1="12" x2="10" y2="13"/>
  <line stroke="blue" x1="10" y1="12" x2="12" y2="12"/>
  <line stroke="blue" x1="7" y1="14" x2="7" y2="15"/>
  <line stroke="blue" x1="7" y1="14" x2="9" y2="14"/>
  <line stroke="red" x1="5" y1="15" x2="7" y2="15"/>
  <line stroke="blue" x1="5" y1="15" x2="5" y2="16"/>
  <line stroke="red" x1="9" y1="13" x2="10" y2="13"/>
  <line stroke="blue" x1="9" y1="13" x2="9" y2="14"/>
  <line stroke="black" x1="0" y1="16" x2="5" y2="16"/>
  <line stroke="black" x1="16" y1="0" x2="16" y2="2"/>
  <line stroke="black" x1="16" y1="2" x2="16" y2="16"/>
  <line stroke="red" x1="10" y1="13" x2="10" y2="14"/>
  <line stroke="red" x1="10" y1="13" x2="13" y2="13"/>
  <line stroke="red" x1="7" y1="15" x2="7" y2="16"/>
  <line stroke="red" x1="7" y1="15" x2="9" y2="15"/>
  <line stroke="blue" x1="9" y1="14" x2="10" y2="14"/>
  <line stroke="red" x1="9" y1="14" x2="9" y2="15"/>
  <line stroke="black" x1="5" y1="16" x2="7" y2="16"/>
  <line stroke="blue" x1="12" y1="12" x2="13" y2="13"/>
  <line stroke="blue" x1="10" y1="14" x2="10" y2="15"/>
  <line stroke="blue" x1="10" y1="14" x2="14" y2="14"/>
  <line stroke="black" x1="7" y1="16" x2="9" y2="16"/>
  <line stroke="red" x1="9" y1="15" x2="10" y2="15"/>
  <line stroke="blue" x1="9" y1="15" x2="9" y2="16"/>
  <line stroke="red" x1="10" y1="15" x2="10" y2="16"/>
  <line stroke="red" x1="10" y1="15" x2="15" y2="15"/>
  <line stroke="black" x1="9" y1="16" x2="10" y2="16"/>
  <line stroke="red" x1="13" y1="13" x2="14" y2="14"/>
  <line stroke="black" x1="10" y1="16" x2="16" y2="16"/>
  <line stroke="blue" x1="14" y1="14" x2="15" y2="15"/>
  <line stroke="red" x1="15" y1="15" x2="16" y2="16"/>
</svg>
""",
)

GEMINI_V5 = BoxPleatingCreasePatternExample(
    name="gemini_v5",
    grid_size=14,
    tree_data=None,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14">
  <line stroke="black" x1="0" y1="0" x2="1" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="2"/>
  <line stroke="black" x1="1" y1="0" x2="3" y2="0"/>
  <line stroke="green" x1="1" y1="0" x2="1" y2="3"/>
  <line stroke="black" x1="0" y1="2" x2="0" y2="3"/>
  <line stroke="red" x1="0" y1="2" x2="1" y2="3"/>
  <line stroke="green" x1="0" y1="3" x2="1" y2="3"/>
  <line stroke="black" x1="0" y1="3" x2="0" y2="5"/>
  <line stroke="red" x1="3" y1="0" x2="3" y2="1"/>
  <line stroke="black" x1="3" y1="0" x2="5" y2="0"/>
  <line stroke="red" x1="1" y1="3" x2="3" y2="1"/>
  <line stroke="green" x1="1" y1="3" x2="5" y2="3"/>
  <line stroke="red" x1="3" y1="1" x2="5" y2="3"/>
  <line stroke="green" x1="0" y1="5" x2="3" y2="5"/>
  <line stroke="black" x1="0" y1="5" x2="0" y2="8"/>
  <line stroke="green" x1="5" y1="0" x2="5" y2="3"/>
  <line stroke="black" x1="5" y1="0" x2="9" y2="0"/>
  <line stroke="red" x1="3" y1="5" x2="5" y2="3"/>
  <line stroke="red" x1="3" y1="5" x2="0" y2="8"/>
  <line stroke="green" x1="3" y1="5" x2="3" y2="11"/>
  <line stroke="green" x1="5" y1="3" x2="5" y2="14"/>
  <line stroke="black" x1="0" y1="8" x2="0" y2="11"/>
  <line stroke="red" x1="0" y1="8" x2="3" y2="11"/>
  <line stroke="green" x1="9" y1="0" x2="9" y2="3"/>
  <line stroke="black" x1="9" y1="0" x2="11" y2="0"/>
  <line stroke="red" x1="9" y1="3" x2="11" y2="1"/>
  <line stroke="red" x1="9" y1="3" x2="11" y2="5"/>
  <line stroke="green" x1="9" y1="3" x2="13" y2="3"/>
  <line stroke="green" x1="9" y1="3" x2="9" y2="14"/>
  <line stroke="green" x1="0" y1="11" x2="3" y2="11"/>
  <line stroke="black" x1="0" y1="11" x2="0" y2="14"/>
  <line stroke="red" x1="11" y1="0" x2="11" y2="1"/>
  <line stroke="black" x1="11" y1="0" x2="13" y2="0"/>
  <line stroke="red" x1="11" y1="1" x2="13" y2="3"/>
  <line stroke="red" x1="3" y1="11" x2="0" y2="14"/>
  <line stroke="green" x1="3" y1="11" x2="3" y2="14"/>
  <line stroke="green" x1="11" y1="5" x2="14" y2="5"/>
  <line stroke="green" x1="11" y1="5" x2="11" y2="11"/>
  <line stroke="red" x1="11" y1="5" x2="14" y2="8"/>
  <line stroke="green" x1="13" y1="0" x2="13" y2="3"/>
  <line stroke="black" x1="13" y1="0" x2="14" y2="0"/>
  <line stroke="red" x1="13" y1="3" x2="14" y2="2"/>
  <line stroke="green" x1="13" y1="3" x2="14" y2="3"/>
  <line stroke="black" x1="0" y1="14" x2="3" y2="14"/>
  <line stroke="black" x1="14" y1="0" x2="14" y2="2"/>
  <line stroke="black" x1="14" y1="2" x2="14" y2="3"/>
  <line stroke="black" x1="3" y1="14" x2="5" y2="14"/>
  <line stroke="black" x1="14" y1="3" x2="14" y2="5"/>
  <line stroke="black" x1="5" y1="14" x2="9" y2="14"/>
  <line stroke="black" x1="14" y1="5" x2="14" y2="8"/>
  <line stroke="red" x1="11" y1="11" x2="14" y2="8"/>
  <line stroke="green" x1="11" y1="11" x2="11" y2="14"/>
  <line stroke="green" x1="11" y1="11" x2="14" y2="11"/>
  <line stroke="red" x1="11" y1="11" x2="14" y2="14"/>
  <line stroke="black" x1="14" y1="8" x2="14" y2="11"/>
  <line stroke="black" x1="9" y1="14" x2="11" y2="14"/>
  <line stroke="black" x1="11" y1="14" x2="14" y2="14"/>
  <line stroke="black" x1="14" y1="11" x2="14" y2="14"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14">
  <line stroke="black" x1="0" y1="0" x2="0" y2="1"/>
  <line stroke="black" x1="0" y1="0" x2="1" y2="0"/>
  <line stroke="red" x1="0" y1="1" x2="1" y2="1"/>
  <line stroke="black" x1="0" y1="1" x2="0" y2="2"/>
  <line stroke="blue" x1="1" y1="0" x2="1" y2="1"/>
  <line stroke="black" x1="1" y1="0" x2="3" y2="0"/>
  <line stroke="red" x1="1" y1="1" x2="1" y2="2"/>
  <line stroke="red" x1="1" y1="1" x2="3" y2="1"/>
  <line stroke="blue" x1="0" y1="2" x2="1" y2="2"/>
  <line stroke="red" x1="0" y1="2" x2="1" y2="3"/>
  <line stroke="black" x1="0" y1="2" x2="0" y2="8"/>
  <line stroke="blue" x1="1" y1="2" x2="2" y2="2"/>
  <line stroke="blue" x1="1" y1="2" x2="1" y2="3"/>
  <line stroke="red" x1="2" y1="2" x2="1" y2="3"/>
  <line stroke="blue" x1="2" y1="2" x2="3" y2="1"/>
  <line stroke="blue" x1="2" y1="2" x2="2" y2="6"/>
  <line stroke="red" x1="3" y1="0" x2="3" y2="1"/>
  <line stroke="black" x1="3" y1="0" x2="5" y2="0"/>
  <line stroke="red" x1="1" y1="3" x2="1" y2="7"/>
  <line stroke="blue" x1="3" y1="1" x2="4" y2="2"/>
  <line stroke="red" x1="3" y1="1" x2="5" y2="1"/>
  <line stroke="red" x1="3" y1="1" x2="3" y2="5"/>
  <line stroke="blue" x1="4" y1="2" x2="5" y2="2"/>
  <line stroke="blue" x1="4" y1="2" x2="4" y2="4"/>
  <line stroke="red" x1="4" y1="2" x2="5" y2="3"/>
  <line stroke="blue" x1="5" y1="0" x2="5" y2="1"/>
  <line stroke="black" x1="5" y1="0" x2="9" y2="0"/>
  <line stroke="red" x1="5" y1="1" x2="5" y2="2"/>
  <line stroke="red" x1="5" y1="1" x2="9" y2="1"/>
  <line stroke="blue" x1="5" y1="2" x2="5" y2="3"/>
  <line stroke="blue" x1="5" y1="2" x2="9" y2="2"/>
  <line stroke="blue" x1="4" y1="4" x2="3" y2="5"/>
  <line stroke="red" x1="4" y1="4" x2="5" y2="3"/>
  <line stroke="blue" x1="4" y1="4" x2="10" y2="4"/>
  <line stroke="red" x1="3" y1="5" x2="2" y2="6"/>
  <line stroke="red" x1="3" y1="5" x2="11" y2="5"/>
  <line stroke="red" x1="5" y1="3" x2="9" y2="3"/>
  <line stroke="blue" x1="2" y1="6" x2="1" y2="7"/>
  <line stroke="blue" x1="2" y1="6" x2="12" y2="6"/>
  <line stroke="red" x1="1" y1="7" x2="0" y2="8"/>
  <line stroke="red" x1="1" y1="7" x2="13" y2="7"/>
  <line stroke="red" x1="0" y1="8" x2="1" y2="9"/>
  <line stroke="black" x1="0" y1="8" x2="0" y2="11"/>
  <line stroke="blue" x1="0" y1="8" x2="14" y2="8"/>
  <line stroke="blue" x1="9" y1="0" x2="9" y2="1"/>
  <line stroke="black" x1="9" y1="0" x2="11" y2="0"/>
  <line stroke="blue" x1="1" y1="9" x2="2" y2="10"/>
  <line stroke="red" x1="1" y1="9" x2="1" y2="11"/>
  <line stroke="red" x1="1" y1="9" x2="13" y2="9"/>
  <line stroke="red" x1="9" y1="1" x2="9" y2="2"/>
  <line stroke="red" x1="9" y1="1" x2="11" y2="1"/>
  <line stroke="blue" x1="9" y1="2" x2="9" y2="3"/>
  <line stroke="blue" x1="9" y1="2" x2="10" y2="2"/>
  <line stroke="red" x1="9" y1="3" x2="10" y2="2"/>
  <line stroke="red" x1="9" y1="3" x2="10" y2="4"/>
  <line stroke="blue" x1="2" y1="10" x2="2" y2="11"/>
  <line stroke="red" x1="2" y1="10" x2="3" y2="11"/>
  <line stroke="blue" x1="2" y1="10" x2="12" y2="10"/>
  <line stroke="blue" x1="10" y1="2" x2="10" y2="4"/>
  <line stroke="blue" x1="10" y1="2" x2="11" y2="1"/>
  <line stroke="blue" x1="10" y1="4" x2="11" y2="5"/>
  <line stroke="blue" x1="0" y1="11" x2="1" y2="11"/>
  <line stroke="black" x1="0" y1="11" x2="0" y2="14"/>
  <line stroke="red" x1="11" y1="0" x2="11" y2="1"/>
  <line stroke="black" x1="11" y1="0" x2="13" y2="0"/>
  <line stroke="red" x1="1" y1="11" x2="2" y2="11"/>
  <line stroke="red" x1="1" y1="11" x2="1" y2="13"/>
  <line stroke="red" x1="11" y1="1" x2="11" y2="5"/>
  <line stroke="blue" x1="11" y1="1" x2="12" y2="2"/>
  <line stroke="red" x1="11" y1="1" x2="13" y2="1"/>
  <line stroke="blue" x1="2" y1="11" x2="3" y2="11"/>
  <line stroke="blue" x1="2" y1="11" x2="2" y2="12"/>
  <line stroke="red" x1="3" y1="11" x2="2" y2="12"/>
  <line stroke="red" x1="3" y1="11" x2="11" y2="11"/>
  <line stroke="red" x1="11" y1="5" x2="12" y2="6"/>
  <line stroke="blue" x1="2" y1="12" x2="1" y2="13"/>
  <line stroke="blue" x1="2" y1="12" x2="12" y2="12"/>
  <line stroke="blue" x1="12" y1="2" x2="13" y2="2"/>
  <line stroke="red" x1="12" y1="2" x2="13" y2="3"/>
  <line stroke="blue" x1="12" y1="2" x2="12" y2="6"/>
  <line stroke="blue" x1="13" y1="0" x2="13" y2="1"/>
  <line stroke="black" x1="13" y1="0" x2="14" y2="0"/>
  <line stroke="red" x1="1" y1="13" x2="0" y2="14"/>
  <line stroke="red" x1="1" y1="13" x2="13" y2="13"/>
  <line stroke="red" x1="13" y1="1" x2="13" y2="2"/>
  <line stroke="red" x1="13" y1="1" x2="14" y2="1"/>
  <line stroke="blue" x1="13" y1="2" x2="13" y2="3"/>
  <line stroke="blue" x1="13" y1="2" x2="14" y2="2"/>
  <line stroke="red" x1="13" y1="3" x2="14" y2="2"/>
  <line stroke="red" x1="13" y1="3" x2="13" y2="7"/>
  <line stroke="blue" x1="12" y1="6" x2="13" y2="7"/>
  <line stroke="black" x1="0" y1="14" x2="14" y2="14"/>
  <line stroke="black" x1="14" y1="0" x2="14" y2="1"/>
  <line stroke="black" x1="14" y1="1" x2="14" y2="2"/>
  <line stroke="black" x1="14" y1="2" x2="14" y2="8"/>
  <line stroke="red" x1="13" y1="7" x2="14" y2="8"/>
  <line stroke="red" x1="11" y1="11" x2="12" y2="10"/>
  <line stroke="blue" x1="11" y1="11" x2="12" y2="11"/>
  <line stroke="red" x1="11" y1="11" x2="12" y2="12"/>
  <line stroke="blue" x1="12" y1="10" x2="13" y2="9"/>
  <line stroke="blue" x1="12" y1="10" x2="12" y2="11"/>
  <line stroke="red" x1="13" y1="9" x2="14" y2="8"/>
  <line stroke="red" x1="13" y1="9" x2="13" y2="11"/>
  <line stroke="black" x1="14" y1="8" x2="14" y2="11"/>
  <line stroke="blue" x1="12" y1="11" x2="12" y2="12"/>
  <line stroke="red" x1="12" y1="11" x2="13" y2="11"/>
  <line stroke="blue" x1="12" y1="12" x2="13" y2="13"/>
  <line stroke="blue" x1="13" y1="11" x2="14" y2="11"/>
  <line stroke="red" x1="13" y1="11" x2="13" y2="13"/>
  <line stroke="black" x1="14" y1="11" x2="14" y2="14"/>
  <line stroke="red" x1="13" y1="13" x2="14" y2="14"/>
</svg>""",
)

GEMINI_V5_GRID_28 = BoxPleatingCreasePatternExample(
    name="gemini_v5",
    grid_size=28,
    stick_figure=stick_figure_utils.StickFigure.from_dict({
        "name": "gemini",
        "root": "linked_arms",
        "category": "constellation",
        "complexity": 2,
        "children": [
            {
                "name": "linked_arms",
                "start": "right_neck",
                "end": "left_neck",
                "azimuth_angle": 90,
                "is_flap": False,
                "is_river": True,
                "length": 4,
                "elevation_angle": 0,
                "width": 1,
                "shaping_flap": False,
                "is_on_symmetry_axis": False,
                "symmetric_stick_name": None,
            },
            {
                "name": "left_body",
                "start": "left_neck",
                "end": "left_core",
                "azimuth_angle": 180,
                "is_flap": False,
                "is_river": True,
                "length": 2,
                "elevation_angle": 0,
                "width": 1,
                "shaping_flap": False,
                "is_on_symmetry_axis": False,
                "symmetric_stick_name": None,
            },
            {
                "name": "left_head",
                "start": "left_neck",
                "end": "left_eyes",
                "azimuth_angle": 0,
                "elevation_angle": 0,
                "length": 1,
                "is_flap": True,
                "is_river": False,
                "width": 1,
                "shaping_flap": False,
                "is_on_symmetry_axis": False,
                "symmetric_stick_name": None,
            },
            {
                "name": "left_arm",
                "start": "left_neck",
                "end": "left_hand",
                "azimuth_angle": 90,
                "elevation_angle": 0,
                "length": 2,
                "is_flap": True,
                "is_river": False,
                "width": 1,
                "shaping_flap": False,
                "is_on_symmetry_axis": False,
                "symmetric_stick_name": None,
            },
            {
                "name": "left_left_leg",
                "start": "left_core",
                "end": "left_left_foot",
                "azimuth_angle": 135,
                "length": 3,
                "is_flap": True,
                "is_river": False,
                "elevation_angle": 0,
                "width": 1,
                "shaping_flap": False,
                "is_on_symmetry_axis": False,
                "symmetric_stick_name": None,
            },
            {
                "name": "left_right_leg",
                "start": "left_core",
                "end": "left_right_foot",
                "azimuth_angle": 225,
                "length": 3,
                "is_flap": True,
                "is_river": False,
                "elevation_angle": 0,
                "width": 1,
                "shaping_flap": False,
                "is_on_symmetry_axis": False,
                "symmetric_stick_name": None,
            },
            {
                "name": "right_body",
                "start": "right_neck",
                "end": "right_core",
                "azimuth_angle": 180,
                "length": 2,
                "is_flap": False,
                "is_river": True,
                "elevation_angle": 0,
                "width": 1,
                "shaping_flap": False,
                "is_on_symmetry_axis": False,
                "symmetric_stick_name": None,
            },
            {
                "name": "right_head",
                "start": "right_neck",
                "end": "right_eyes",
                "azimuth_angle": 0,
                "length": 1,
                "is_flap": True,
                "is_river": False,
                "elevation_angle": 0,
                "width": 1,
                "shaping_flap": False,
                "is_on_symmetry_axis": False,
                "symmetric_stick_name": None,
            },
            {
                "name": "right_arm",
                "start": "right_neck",
                "end": "right_hand",
                "azimuth_angle": 270,
                "length": 2,
                "is_flap": True,
                "is_river": False,
                "elevation_angle": 0,
                "width": 1,
                "shaping_flap": False,
                "is_on_symmetry_axis": False,
                "symmetric_stick_name": None,
            },
            {
                "name": "right_left_leg",
                "start": "right_core",
                "end": "right_left_foot",
                "azimuth_angle": 135,
                "length": 3,
                "is_flap": True,
                "is_river": False,
                "elevation_angle": 0,
                "width": 1,
                "shaping_flap": False,
                "is_on_symmetry_axis": False,
                "symmetric_stick_name": None,
            },
            {
                "name": "right_right_leg",
                "start": "right_core",
                "end": "right_right_foot",
                "azimuth_angle": 225,
                "length": 3,
                "is_flap": True,
                "is_river": False,
                "elevation_angle": 0,
                "width": 1,
                "shaping_flap": False,
                "is_on_symmetry_axis": False,
                "symmetric_stick_name": None,
            },
        ],
        "shaping_flaps_limit": 0,
        "symmetry_axis": [],
        "symmetry_plane_name": "azimuth",
        "is_symmetric_tree": False,
    }),
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 28">
  <line stroke="black" x1="0" y1="0" x2="2" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="4"/>
  <line stroke="black" x1="2" y1="0" x2="6" y2="0"/>
  <line stroke="green" x1="2" y1="0" x2="2" y2="6"/>
  <line stroke="black" x1="0" y1="4" x2="0" y2="6"/>
  <line stroke="red" x1="0" y1="4" x2="2" y2="6"/>
  <line stroke="green" x1="0" y1="6" x2="2" y2="6"/>
  <line stroke="black" x1="0" y1="6" x2="0" y2="10"/>
  <line stroke="red" x1="6" y1="0" x2="6" y2="2"/>
  <line stroke="black" x1="6" y1="0" x2="10" y2="0"/>
  <line stroke="red" x1="2" y1="6" x2="6" y2="2"/>
  <line stroke="green" x1="2" y1="6" x2="10" y2="6"/>
  <line stroke="red" x1="6" y1="2" x2="10" y2="6"/>
  <line stroke="green" x1="0" y1="10" x2="6" y2="10"/>
  <line stroke="black" x1="0" y1="10" x2="0" y2="16"/>
  <line stroke="green" x1="10" y1="0" x2="10" y2="6"/>
  <line stroke="black" x1="10" y1="0" x2="18" y2="0"/>
  <line stroke="red" x1="6" y1="10" x2="10" y2="6"/>
  <line stroke="red" x1="6" y1="10" x2="0" y2="16"/>
  <line stroke="green" x1="6" y1="10" x2="6" y2="22"/>
  <line stroke="green" x1="10" y1="6" x2="10" y2="28"/>
  <line stroke="black" x1="0" y1="16" x2="0" y2="22"/>
  <line stroke="red" x1="0" y1="16" x2="6" y2="22"/>
  <line stroke="green" x1="18" y1="0" x2="18" y2="6"/>
  <line stroke="black" x1="18" y1="0" x2="22" y2="0"/>
  <line stroke="red" x1="18" y1="6" x2="22" y2="2"/>
  <line stroke="red" x1="18" y1="6" x2="22" y2="10"/>
  <line stroke="green" x1="18" y1="6" x2="26" y2="6"/>
  <line stroke="green" x1="18" y1="6" x2="18" y2="28"/>
  <line stroke="green" x1="0" y1="22" x2="6" y2="22"/>
  <line stroke="black" x1="0" y1="22" x2="0" y2="28"/>
  <line stroke="red" x1="22" y1="0" x2="22" y2="2"/>
  <line stroke="black" x1="22" y1="0" x2="26" y2="0"/>
  <line stroke="red" x1="22" y1="2" x2="26" y2="6"/>
  <line stroke="red" x1="6" y1="22" x2="0" y2="28"/>
  <line stroke="green" x1="6" y1="22" x2="6" y2="28"/>
  <line stroke="green" x1="22" y1="10" x2="28" y2="10"/>
  <line stroke="green" x1="22" y1="10" x2="22" y2="22"/>
  <line stroke="red" x1="22" y1="10" x2="28" y2="16"/>
  <line stroke="green" x1="26" y1="0" x2="26" y2="6"/>
  <line stroke="black" x1="26" y1="0" x2="28" y2="0"/>
  <line stroke="red" x1="26" y1="6" x2="28" y2="4"/>
  <line stroke="green" x1="26" y1="6" x2="28" y2="6"/>
  <line stroke="black" x1="0" y1="28" x2="6" y2="28"/>
  <line stroke="black" x1="28" y1="0" x2="28" y2="4"/>
  <line stroke="black" x1="28" y1="4" x2="28" y2="6"/>
  <line stroke="black" x1="6" y1="28" x2="10" y2="28"/>
  <line stroke="black" x1="28" y1="6" x2="28" y2="10"/>
  <line stroke="black" x1="10" y1="28" x2="18" y2="28"/>
  <line stroke="black" x1="28" y1="10" x2="28" y2="16"/>
  <line stroke="red" x1="22" y1="22" x2="28" y2="16"/>
  <line stroke="green" x1="22" y1="22" x2="22" y2="28"/>
  <line stroke="green" x1="22" y1="22" x2="28" y2="22"/>
  <line stroke="red" x1="22" y1="22" x2="28" y2="28"/>
  <line stroke="black" x1="28" y1="16" x2="28" y2="22"/>
  <line stroke="black" x1="18" y1="28" x2="22" y2="28"/>
  <line stroke="black" x1="22" y1="28" x2="28" y2="28"/>
  <line stroke="black" x1="28" y1="22" x2="28" y2="28"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="0" y2="36"/>
  <line stroke="black" x1="0" y1="0" x2="71" y2="0"/>
  <line stroke="black" x1="0" y1="36" x2="0" y2="71"/>
  <line stroke="red" x1="0" y1="36" x2="71" y2="36"/>
  <line stroke="blue" x1="0" y1="71" x2="71" y2="71"/>
  <line stroke="black" x1="0" y1="71" x2="0" y2="107"/>
  <line stroke="blue" x1="71" y1="0" x2="71" y2="36"/>
  <line stroke="black" x1="71" y1="0" x2="214" y2="0"/>
  <line stroke="red" x1="71" y1="36" x2="71" y2="71"/>
  <line stroke="red" x1="71" y1="36" x2="214" y2="36"/>
  <line stroke="blue" x1="71" y1="71" x2="71" y2="107"/>
  <line stroke="blue" x1="71" y1="71" x2="214" y2="71"/>
  <line stroke="red" x1="0" y1="107" x2="71" y2="107"/>
  <line stroke="black" x1="0" y1="107" x2="0" y2="143"/>
  <line stroke="red" x1="71" y1="107" x2="71" y2="143"/>
  <line stroke="red" x1="71" y1="107" x2="179" y2="107"/>
  <line stroke="blue" x1="0" y1="143" x2="71" y2="143"/>
  <line stroke="red" x1="0" y1="143" x2="36" y2="179"/>
  <line stroke="black" x1="0" y1="143" x2="0" y2="571"/>
  <line stroke="blue" x1="71" y1="143" x2="71" y2="179"/>
  <line stroke="blue" x1="71" y1="143" x2="143" y2="143"/>
  <line stroke="red" x1="36" y1="179" x2="71" y2="179"/>
  <line stroke="blue" x1="36" y1="179" x2="71" y2="214"/>
  <line stroke="red" x1="36" y1="179" x2="36" y2="536"/>
  <line stroke="red" x1="71" y1="179" x2="107" y2="179"/>
  <line stroke="red" x1="71" y1="179" x2="71" y2="214"/>
  <line stroke="red" x1="143" y1="143" x2="107" y2="179"/>
  <line stroke="blue" x1="143" y1="143" x2="179" y2="107"/>
  <line stroke="blue" x1="143" y1="143" x2="143" y2="429"/>
  <line stroke="blue" x1="107" y1="179" x2="71" y2="214"/>
  <line stroke="red" x1="107" y1="179" x2="107" y2="464"/>
  <line stroke="red" x1="179" y1="107" x2="214" y2="71"/>
  <line stroke="red" x1="179" y1="107" x2="179" y2="393"/>
  <line stroke="red" x1="214" y1="0" x2="214" y2="36"/>
  <line stroke="black" x1="214" y1="0" x2="357" y2="0"/>
  <line stroke="blue" x1="214" y1="36" x2="214" y2="71"/>
  <line stroke="red" x1="214" y1="36" x2="357" y2="36"/>
  <line stroke="blue" x1="71" y1="214" x2="71" y2="500"/>
  <line stroke="red" x1="214" y1="71" x2="250" y2="107"/>
  <line stroke="blue" x1="214" y1="71" x2="357" y2="71"/>
  <line stroke="blue" x1="214" y1="71" x2="214" y2="357"/>
  <line stroke="blue" x1="250" y1="107" x2="286" y2="143"/>
  <line stroke="red" x1="250" y1="107" x2="357" y2="107"/>
  <line stroke="red" x1="250" y1="107" x2="250" y2="321"/>
  <line stroke="red" x1="286" y1="143" x2="321" y2="179"/>
  <line stroke="blue" x1="286" y1="143" x2="357" y2="143"/>
  <line stroke="blue" x1="286" y1="143" x2="286" y2="286"/>
  <line stroke="blue" x1="357" y1="0" x2="357" y2="36"/>
  <line stroke="black" x1="357" y1="0" x2="643" y2="0"/>
  <line stroke="red" x1="357" y1="36" x2="357" y2="71"/>
  <line stroke="red" x1="357" y1="36" x2="643" y2="36"/>
  <line stroke="blue" x1="357" y1="71" x2="357" y2="107"/>
  <line stroke="blue" x1="357" y1="71" x2="643" y2="71"/>
  <line stroke="red" x1="321" y1="179" x2="357" y2="179"/>
  <line stroke="red" x1="321" y1="179" x2="321" y2="250"/>
  <line stroke="blue" x1="321" y1="179" x2="357" y2="214"/>
  <line stroke="red" x1="357" y1="107" x2="357" y2="143"/>
  <line stroke="red" x1="357" y1="107" x2="643" y2="107"/>
  <line stroke="blue" x1="357" y1="143" x2="357" y2="179"/>
  <line stroke="blue" x1="357" y1="143" x2="643" y2="143"/>
  <line stroke="red" x1="357" y1="179" x2="357" y2="214"/>
  <line stroke="red" x1="357" y1="179" x2="643" y2="179"/>
  <line stroke="blue" x1="286" y1="286" x2="250" y2="321"/>
  <line stroke="red" x1="286" y1="286" x2="321" y2="250"/>
  <line stroke="blue" x1="286" y1="286" x2="714" y2="286"/>
  <line stroke="red" x1="250" y1="321" x2="214" y2="357"/>
  <line stroke="red" x1="250" y1="321" x2="750" y2="321"/>
  <line stroke="blue" x1="321" y1="250" x2="357" y2="214"/>
  <line stroke="red" x1="321" y1="250" x2="679" y2="250"/>
  <line stroke="blue" x1="214" y1="357" x2="179" y2="393"/>
  <line stroke="blue" x1="214" y1="357" x2="786" y2="357"/>
  <line stroke="blue" x1="357" y1="214" x2="643" y2="214"/>
  <line stroke="red" x1="179" y1="393" x2="143" y2="429"/>
  <line stroke="red" x1="179" y1="393" x2="821" y2="393"/>
  <line stroke="blue" x1="143" y1="429" x2="107" y2="464"/>
  <line stroke="blue" x1="143" y1="429" x2="857" y2="429"/>
  <line stroke="red" x1="107" y1="464" x2="71" y2="500"/>
  <line stroke="red" x1="107" y1="464" x2="893" y2="464"/>
  <line stroke="blue" x1="71" y1="500" x2="36" y2="536"/>
  <line stroke="blue" x1="71" y1="500" x2="929" y2="500"/>
  <line stroke="red" x1="36" y1="536" x2="0" y2="571"/>
  <line stroke="red" x1="36" y1="536" x2="964" y2="536"/>
  <line stroke="red" x1="0" y1="571" x2="36" y2="607"/>
  <line stroke="black" x1="0" y1="571" x2="0" y2="786"/>
  <line stroke="blue" x1="0" y1="571" x2="1000" y2="571"/>
  <line stroke="blue" x1="36" y1="607" x2="71" y2="643"/>
  <line stroke="red" x1="36" y1="607" x2="36" y2="786"/>
  <line stroke="red" x1="36" y1="607" x2="964" y2="607"/>
  <line stroke="blue" x1="643" y1="0" x2="643" y2="36"/>
  <line stroke="black" x1="643" y1="0" x2="786" y2="0"/>
  <line stroke="red" x1="643" y1="36" x2="643" y2="71"/>
  <line stroke="red" x1="643" y1="36" x2="786" y2="36"/>
  <line stroke="red" x1="71" y1="643" x2="107" y2="679"/>
  <line stroke="blue" x1="71" y1="643" x2="71" y2="786"/>
  <line stroke="blue" x1="71" y1="643" x2="929" y2="643"/>
  <line stroke="blue" x1="643" y1="71" x2="643" y2="107"/>
  <line stroke="blue" x1="643" y1="71" x2="786" y2="71"/>
  <line stroke="red" x1="643" y1="107" x2="643" y2="143"/>
  <line stroke="red" x1="643" y1="107" x2="750" y2="107"/>
  <line stroke="blue" x1="643" y1="143" x2="643" y2="179"/>
  <line stroke="blue" x1="643" y1="143" x2="714" y2="143"/>
  <line stroke="red" x1="643" y1="179" x2="643" y2="214"/>
  <line stroke="red" x1="643" y1="179" x2="679" y2="179"/>
  <line stroke="blue" x1="643" y1="214" x2="679" y2="179"/>
  <line stroke="blue" x1="643" y1="214" x2="679" y2="250"/>
  <line stroke="blue" x1="107" y1="679" x2="143" y2="714"/>
  <line stroke="red" x1="107" y1="679" x2="107" y2="786"/>
  <line stroke="red" x1="107" y1="679" x2="893" y2="679"/>
  <line stroke="red" x1="679" y1="179" x2="679" y2="250"/>
  <line stroke="red" x1="679" y1="179" x2="714" y2="143"/>
  <line stroke="red" x1="679" y1="250" x2="714" y2="286"/>
  <line stroke="red" x1="143" y1="714" x2="179" y2="750"/>
  <line stroke="blue" x1="143" y1="714" x2="143" y2="786"/>
  <line stroke="blue" x1="143" y1="714" x2="857" y2="714"/>
  <line stroke="blue" x1="714" y1="143" x2="750" y2="107"/>
  <line stroke="blue" x1="714" y1="143" x2="714" y2="286"/>
  <line stroke="red" x1="750" y1="107" x2="786" y2="71"/>
  <line stroke="red" x1="750" y1="107" x2="750" y2="321"/>
  <line stroke="blue" x1="714" y1="286" x2="750" y2="321"/>
  <line stroke="red" x1="179" y1="750" x2="179" y2="786"/>
  <line stroke="blue" x1="179" y1="750" x2="214" y2="786"/>
  <line stroke="red" x1="179" y1="750" x2="821" y2="750"/>
  <line stroke="blue" x1="0" y1="786" x2="36" y2="786"/>
  <line stroke="black" x1="0" y1="786" x2="0" y2="1000"/>
  <line stroke="red" x1="786" y1="0" x2="786" y2="36"/>
  <line stroke="black" x1="786" y1="0" x2="929" y2="0"/>
  <line stroke="red" x1="36" y1="786" x2="71" y2="786"/>
  <line stroke="red" x1="36" y1="786" x2="36" y2="964"/>
  <line stroke="blue" x1="786" y1="36" x2="786" y2="71"/>
  <line stroke="red" x1="786" y1="36" x2="929" y2="36"/>
  <line stroke="blue" x1="71" y1="786" x2="107" y2="786"/>
  <line stroke="blue" x1="71" y1="786" x2="71" y2="929"/>
  <line stroke="red" x1="786" y1="71" x2="821" y2="107"/>
  <line stroke="blue" x1="786" y1="71" x2="786" y2="357"/>
  <line stroke="blue" x1="786" y1="71" x2="929" y2="71"/>
  <line stroke="red" x1="107" y1="786" x2="143" y2="786"/>
  <line stroke="red" x1="107" y1="786" x2="107" y2="893"/>
  <line stroke="blue" x1="143" y1="786" x2="179" y2="786"/>
  <line stroke="blue" x1="143" y1="786" x2="143" y2="857"/>
  <line stroke="red" x1="179" y1="786" x2="214" y2="786"/>
  <line stroke="red" x1="179" y1="786" x2="179" y2="821"/>
  <line stroke="blue" x1="214" y1="786" x2="179" y2="821"/>
  <line stroke="blue" x1="214" y1="786" x2="786" y2="786"/>
  <line stroke="red" x1="750" y1="321" x2="786" y2="357"/>
  <line stroke="blue" x1="821" y1="107" x2="857" y2="143"/>
  <line stroke="red" x1="821" y1="107" x2="821" y2="393"/>
  <line stroke="red" x1="821" y1="107" x2="929" y2="107"/>
  <line stroke="red" x1="179" y1="821" x2="143" y2="857"/>
  <line stroke="red" x1="179" y1="821" x2="821" y2="821"/>
  <line stroke="blue" x1="786" y1="357" x2="821" y2="393"/>
  <line stroke="blue" x1="143" y1="857" x2="107" y2="893"/>
  <line stroke="blue" x1="143" y1="857" x2="857" y2="857"/>
  <line stroke="red" x1="857" y1="143" x2="893" y2="179"/>
  <line stroke="blue" x1="857" y1="143" x2="929" y2="143"/>
  <line stroke="blue" x1="857" y1="143" x2="857" y2="429"/>
  <line stroke="red" x1="107" y1="893" x2="71" y2="929"/>
  <line stroke="red" x1="107" y1="893" x2="893" y2="893"/>
  <line stroke="red" x1="821" y1="393" x2="857" y2="429"/>
  <line stroke="red" x1="893" y1="179" x2="929" y2="179"/>
  <line stroke="blue" x1="893" y1="179" x2="929" y2="214"/>
  <line stroke="red" x1="893" y1="179" x2="893" y2="464"/>
  <line stroke="blue" x1="929" y1="0" x2="929" y2="36"/>
  <line stroke="black" x1="929" y1="0" x2="1000" y2="0"/>
  <line stroke="red" x1="929" y1="36" x2="929" y2="71"/>
  <line stroke="red" x1="929" y1="36" x2="1000" y2="36"/>
  <line stroke="blue" x1="71" y1="929" x2="36" y2="964"/>
  <line stroke="blue" x1="71" y1="929" x2="929" y2="929"/>
  <line stroke="blue" x1="929" y1="71" x2="929" y2="107"/>
  <line stroke="blue" x1="929" y1="71" x2="1000" y2="71"/>
  <line stroke="red" x1="929" y1="107" x2="929" y2="143"/>
  <line stroke="red" x1="929" y1="107" x2="1000" y2="107"/>
  <line stroke="blue" x1="929" y1="143" x2="929" y2="179"/>
  <line stroke="blue" x1="929" y1="143" x2="1000" y2="143"/>
  <line stroke="red" x1="929" y1="179" x2="929" y2="214"/>
  <line stroke="red" x1="929" y1="179" x2="964" y2="179"/>
  <line stroke="blue" x1="929" y1="214" x2="964" y2="179"/>
  <line stroke="blue" x1="929" y1="214" x2="929" y2="500"/>
  <line stroke="blue" x1="857" y1="429" x2="893" y2="464"/>
  <line stroke="red" x1="36" y1="964" x2="0" y2="1000"/>
  <line stroke="red" x1="36" y1="964" x2="964" y2="964"/>
  <line stroke="red" x1="964" y1="179" x2="1000" y2="143"/>
  <line stroke="red" x1="964" y1="179" x2="964" y2="536"/>
  <line stroke="black" x1="0" y1="1000" x2="1000" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="36"/>
  <line stroke="black" x1="1000" y1="36" x2="1000" y2="71"/>
  <line stroke="black" x1="1000" y1="71" x2="1000" y2="107"/>
  <line stroke="black" x1="1000" y1="107" x2="1000" y2="143"/>
  <line stroke="red" x1="893" y1="464" x2="929" y2="500"/>
  <line stroke="black" x1="1000" y1="143" x2="1000" y2="571"/>
  <line stroke="blue" x1="929" y1="500" x2="964" y2="536"/>
  <line stroke="red" x1="964" y1="536" x2="1000" y2="571"/>
  <line stroke="blue" x1="786" y1="786" x2="821" y2="750"/>
  <line stroke="red" x1="786" y1="786" x2="821" y2="786"/>
  <line stroke="blue" x1="786" y1="786" x2="821" y2="821"/>
  <line stroke="red" x1="821" y1="750" x2="857" y2="714"/>
  <line stroke="red" x1="821" y1="750" x2="821" y2="786"/>
  <line stroke="blue" x1="857" y1="714" x2="893" y2="679"/>
  <line stroke="blue" x1="857" y1="714" x2="857" y2="786"/>
  <line stroke="red" x1="893" y1="679" x2="929" y2="643"/>
  <line stroke="red" x1="893" y1="679" x2="893" y2="786"/>
  <line stroke="blue" x1="929" y1="643" x2="964" y2="607"/>
  <line stroke="blue" x1="929" y1="643" x2="929" y2="786"/>
  <line stroke="red" x1="821" y1="786" x2="821" y2="821"/>
  <line stroke="blue" x1="821" y1="786" x2="857" y2="786"/>
  <line stroke="red" x1="964" y1="607" x2="1000" y2="571"/>
  <line stroke="red" x1="964" y1="607" x2="964" y2="786"/>
  <line stroke="black" x1="1000" y1="571" x2="1000" y2="786"/>
  <line stroke="red" x1="821" y1="821" x2="857" y2="857"/>
  <line stroke="red" x1="857" y1="786" x2="893" y2="786"/>
  <line stroke="blue" x1="857" y1="786" x2="857" y2="857"/>
  <line stroke="blue" x1="893" y1="786" x2="929" y2="786"/>
  <line stroke="red" x1="893" y1="786" x2="893" y2="893"/>
  <line stroke="blue" x1="857" y1="857" x2="893" y2="893"/>
  <line stroke="red" x1="929" y1="786" x2="964" y2="786"/>
  <line stroke="blue" x1="929" y1="786" x2="929" y2="929"/>
  <line stroke="blue" x1="964" y1="786" x2="1000" y2="786"/>
  <line stroke="red" x1="964" y1="786" x2="964" y2="964"/>
  <line stroke="red" x1="893" y1="893" x2="929" y2="929"/>
  <line stroke="black" x1="1000" y1="786" x2="1000" y2="1000"/>
  <line stroke="blue" x1="929" y1="929" x2="964" y2="964"/>
  <line stroke="red" x1="964" y1="964" x2="1000" y2="1000"/>
</svg>""",
)

SMALL_GEMINI = BoxPleatingCreasePatternExample(
    name="small_gemini",
    grid_size=16,
    tree_data={
        "version": "0.7",
        "design": {
            "title": "Untitled",
            "mode": "tree",
            "description": "",
            "layout": {
                "sheet": {"type": "rect", "height": 32, "width": 16},
                "flaps": [
                    {"id": 2, "x": 16, "y": 32, "width": 0, "height": 0},
                    {"id": 3, "x": 2, "y": 16, "width": 0, "height": 0},
                    {"id": 5, "x": 9, "y": 26, "width": 0, "height": 0},
                    {"id": 6, "x": 13, "y": 25, "width": 0, "height": 0},
                    {"id": 7, "x": 5, "y": 27, "width": 0, "height": 0},
                    {"id": 8, "x": 4, "y": 29, "width": 0, "height": 0},
                    {"id": 10, "x": 16, "y": 0, "width": 0, "height": 0},
                    {"id": 11, "x": 0, "y": 0, "width": 0, "height": 0},
                ],
                "stretches": [],
            },
            "tree": {
                "sheet": {"type": "rect", "height": 20, "width": 20},
                "nodes": [
                    {"id": 0, "name": "", "x": 10, "y": 6},
                    {"id": 1, "name": "", "x": 10, "y": 8},
                    {"id": 2, "name": "", "x": 13, "y": 6},
                    {"id": 3, "name": "", "x": 7, "y": 6},
                    {"id": 4, "name": "", "x": 10, "y": 10},
                    {"id": 5, "name": "", "x": 9, "y": 8},
                    {"id": 6, "name": "", "x": 11, "y": 8},
                    {"id": 7, "name": "", "x": 11, "y": 10},
                    {"id": 8, "name": "", "x": 9, "y": 10},
                    {"id": 9, "name": "", "x": 10, "y": 12},
                    {"id": 10, "name": "", "x": 7, "y": 12},
                    {"id": 11, "name": "", "x": 13, "y": 12},
                ],
                "edges": [
                    {"n1": 1, "n2": 4, "length": 2},
                    {"n1": 1, "n2": 0, "length": 2},
                    {"n1": 1, "n2": 6, "length": 1},
                    {"n1": 1, "n2": 5, "length": 1},
                    {"n1": 4, "n2": 9, "length": 2},
                    {"n1": 4, "n2": 8, "length": 1},
                    {"n1": 4, "n2": 7, "length": 1},
                    {"n1": 0, "n2": 3, "length": 3},
                    {"n1": 0, "n2": 2, "length": 3},
                    {"n1": 9, "n2": 10, "length": 3},
                    {"n1": 9, "n2": 11, "length": 3},
                ],
            },
        },
    },
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="0" y2="125"/>
  <line stroke="black" x1="0" y1="0" x2="125" y2="0"/>
  <line stroke="red" x1="0" y1="125" x2="125" y2="0"/>
  <line stroke="black" x1="0" y1="125" x2="0" y2="250"/>
  <line stroke="red" x1="0" y1="125" x2="125" y2="250"/>
  <line stroke="black" x1="125" y1="0" x2="250" y2="0"/>
  <line stroke="green" x1="125" y1="0" x2="125" y2="250"/>
  <line stroke="green" x1="0" y1="250" x2="125" y2="250"/>
  <line stroke="black" x1="0" y1="250" x2="0" y2="375"/>
  <line stroke="black" x1="250" y1="0" x2="375" y2="0"/>
  <line stroke="green" x1="250" y1="0" x2="250" y2="375"/>
  <line stroke="red" x1="125" y1="250" x2="250" y2="375"/>
  <line stroke="green" x1="0" y1="375" x2="250" y2="375"/>
  <line stroke="black" x1="0" y1="375" x2="0" y2="625"/>
  <line stroke="red" x1="375" y1="0" x2="375" y2="250"/>
  <line stroke="black" x1="375" y1="0" x2="500" y2="0"/>
  <line stroke="red" x1="250" y1="375" x2="375" y2="250"/>
  <line stroke="green" x1="250" y1="375" x2="500" y2="375"/>
  <line stroke="red" x1="375" y1="250" x2="500" y2="375"/>
  <line stroke="green" x1="500" y1="0" x2="500" y2="375"/>
  <line stroke="black" x1="500" y1="0" x2="625" y2="0"/>
  <line stroke="green" x1="0" y1="625" x2="250" y2="625"/>
  <line stroke="black" x1="0" y1="625" x2="0" y2="750"/>
  <line stroke="red" x1="500" y1="375" x2="625" y2="250"/>
  <line stroke="green" x1="500" y1="375" x2="750" y2="375"/>
  <line stroke="red" x1="625" y1="0" x2="625" y2="250"/>
  <line stroke="black" x1="625" y1="0" x2="750" y2="0"/>
  <line stroke="red" x1="250" y1="625" x2="125" y2="750"/>
  <line stroke="green" x1="250" y1="625" x2="500" y2="625"/>
  <line stroke="red" x1="250" y1="625" x2="375" y2="750"/>
  <line stroke="green" x1="250" y1="625" x2="250" y2="1000"/>
  <line stroke="red" x1="625" y1="250" x2="750" y2="375"/>
  <line stroke="green" x1="0" y1="750" x2="125" y2="750"/>
  <line stroke="black" x1="0" y1="750" x2="0" y2="875"/>
  <line stroke="green" x1="750" y1="0" x2="750" y2="375"/>
  <line stroke="black" x1="750" y1="0" x2="875" y2="0"/>
  <line stroke="red" x1="125" y1="750" x2="0" y2="875"/>
  <line stroke="green" x1="125" y1="750" x2="125" y2="1000"/>
  <line stroke="red" x1="500" y1="625" x2="375" y2="750"/>
  <line stroke="red" x1="500" y1="625" x2="625" y2="750"/>
  <line stroke="green" x1="500" y1="625" x2="750" y2="625"/>
  <line stroke="green" x1="500" y1="625" x2="500" y2="1000"/>
  <line stroke="red" x1="375" y1="750" x2="375" y2="1000"/>
  <line stroke="red" x1="750" y1="375" x2="875" y2="250"/>
  <line stroke="green" x1="750" y1="375" x2="1000" y2="375"/>
  <line stroke="black" x1="0" y1="875" x2="0" y2="1000"/>
  <line stroke="red" x1="0" y1="875" x2="125" y2="1000"/>
  <line stroke="green" x1="875" y1="0" x2="875" y2="250"/>
  <line stroke="black" x1="875" y1="0" x2="1000" y2="0"/>
  <line stroke="red" x1="875" y1="0" x2="1000" y2="125"/>
  <line stroke="red" x1="875" y1="250" x2="1000" y2="125"/>
  <line stroke="green" x1="875" y1="250" x2="1000" y2="250"/>
  <line stroke="red" x1="625" y1="750" x2="750" y2="625"/>
  <line stroke="red" x1="625" y1="750" x2="625" y2="1000"/>
  <line stroke="red" x1="750" y1="625" x2="875" y2="750"/>
  <line stroke="green" x1="750" y1="625" x2="1000" y2="625"/>
  <line stroke="green" x1="750" y1="625" x2="750" y2="1000"/>
  <line stroke="black" x1="0" y1="1000" x2="125" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="125"/>
  <line stroke="black" x1="125" y1="1000" x2="250" y2="1000"/>
  <line stroke="black" x1="1000" y1="125" x2="1000" y2="250"/>
  <line stroke="black" x1="250" y1="1000" x2="375" y2="1000"/>
  <line stroke="black" x1="1000" y1="250" x2="1000" y2="375"/>
  <line stroke="black" x1="375" y1="1000" x2="500" y2="1000"/>
  <line stroke="black" x1="1000" y1="375" x2="1000" y2="625"/>
  <line stroke="black" x1="500" y1="1000" x2="625" y2="1000"/>
  <line stroke="green" x1="875" y1="750" x2="1000" y2="750"/>
  <line stroke="green" x1="875" y1="750" x2="875" y2="1000"/>
  <line stroke="red" x1="875" y1="750" x2="1000" y2="875"/>
  <line stroke="black" x1="625" y1="1000" x2="750" y2="1000"/>
  <line stroke="black" x1="1000" y1="625" x2="1000" y2="750"/>
  <line stroke="black" x1="750" y1="1000" x2="875" y2="1000"/>
  <line stroke="black" x1="1000" y1="750" x2="1000" y2="875"/>
  <line stroke="red" x1="875" y1="1000" x2="1000" y2="875"/>
  <line stroke="black" x1="875" y1="1000" x2="1000" y2="1000"/>
  <line stroke="black" x1="1000" y1="875" x2="1000" y2="1000"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="62" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="125"/>
  <line stroke="red" x1="62" y1="0" x2="62" y2="62"/>
  <line stroke="black" x1="62" y1="0" x2="125" y2="0"/>
  <line stroke="red" x1="62" y1="62" x2="0" y2="125"/>
  <line stroke="blue" x1="62" y1="62" x2="125" y2="0"/>
  <line stroke="red" x1="62" y1="62" x2="250" y2="62"/>
  <line stroke="red" x1="0" y1="125" x2="62" y2="188"/>
  <line stroke="blue" x1="0" y1="125" x2="250" y2="125"/>
  <line stroke="black" x1="0" y1="125" x2="0" y2="875"/>
  <line stroke="black" x1="125" y1="0" x2="250" y2="0"/>
  <line stroke="blue" x1="62" y1="188" x2="125" y2="250"/>
  <line stroke="red" x1="62" y1="188" x2="250" y2="188"/>
  <line stroke="red" x1="62" y1="188" x2="62" y2="812"/>
  <line stroke="blue" x1="250" y1="0" x2="250" y2="62"/>
  <line stroke="black" x1="250" y1="0" x2="375" y2="0"/>
  <line stroke="red" x1="250" y1="62" x2="250" y2="125"/>
  <line stroke="red" x1="250" y1="62" x2="375" y2="62"/>
  <line stroke="blue" x1="125" y1="250" x2="250" y2="250"/>
  <line stroke="red" x1="125" y1="250" x2="188" y2="312"/>
  <line stroke="blue" x1="125" y1="250" x2="125" y2="750"/>
  <line stroke="blue" x1="250" y1="125" x2="250" y2="188"/>
  <line stroke="blue" x1="250" y1="125" x2="375" y2="125"/>
  <line stroke="red" x1="250" y1="188" x2="250" y2="250"/>
  <line stroke="red" x1="250" y1="188" x2="375" y2="188"/>
  <line stroke="blue" x1="250" y1="250" x2="250" y2="312"/>
  <line stroke="blue" x1="250" y1="250" x2="375" y2="250"/>
  <line stroke="red" x1="188" y1="312" x2="250" y2="312"/>
  <line stroke="blue" x1="188" y1="312" x2="250" y2="375"/>
  <line stroke="red" x1="188" y1="312" x2="188" y2="688"/>
  <line stroke="red" x1="375" y1="0" x2="375" y2="62"/>
  <line stroke="black" x1="375" y1="0" x2="625" y2="0"/>
  <line stroke="blue" x1="375" y1="62" x2="375" y2="125"/>
  <line stroke="red" x1="375" y1="62" x2="625" y2="62"/>
  <line stroke="red" x1="375" y1="125" x2="375" y2="188"/>
  <line stroke="blue" x1="375" y1="125" x2="625" y2="125"/>
  <line stroke="red" x1="250" y1="312" x2="312" y2="312"/>
  <line stroke="red" x1="250" y1="312" x2="250" y2="375"/>
  <line stroke="blue" x1="375" y1="188" x2="375" y2="250"/>
  <line stroke="red" x1="375" y1="188" x2="625" y2="188"/>
  <line stroke="blue" x1="312" y1="312" x2="250" y2="375"/>
  <line stroke="red" x1="312" y1="312" x2="375" y2="250"/>
  <line stroke="red" x1="312" y1="312" x2="312" y2="688"/>
  <line stroke="blue" x1="250" y1="375" x2="250" y2="625"/>
  <line stroke="red" x1="375" y1="250" x2="438" y2="312"/>
  <line stroke="blue" x1="375" y1="250" x2="625" y2="250"/>
  <line stroke="blue" x1="375" y1="250" x2="375" y2="750"/>
  <line stroke="blue" x1="438" y1="312" x2="500" y2="375"/>
  <line stroke="red" x1="438" y1="312" x2="562" y2="312"/>
  <line stroke="red" x1="438" y1="312" x2="438" y2="688"/>
  <line stroke="blue" x1="500" y1="375" x2="562" y2="312"/>
  <line stroke="red" x1="500" y1="375" x2="562" y2="375"/>
  <line stroke="blue" x1="500" y1="375" x2="500" y2="625"/>
  <line stroke="red" x1="625" y1="0" x2="625" y2="62"/>
  <line stroke="black" x1="625" y1="0" x2="750" y2="0"/>
  <line stroke="blue" x1="625" y1="62" x2="625" y2="125"/>
  <line stroke="red" x1="625" y1="62" x2="750" y2="62"/>
  <line stroke="red" x1="625" y1="125" x2="625" y2="188"/>
  <line stroke="blue" x1="625" y1="125" x2="750" y2="125"/>
  <line stroke="red" x1="562" y1="312" x2="625" y2="250"/>
  <line stroke="red" x1="562" y1="312" x2="562" y2="375"/>
  <line stroke="blue" x1="625" y1="188" x2="625" y2="250"/>
  <line stroke="red" x1="625" y1="188" x2="750" y2="188"/>
  <line stroke="blue" x1="250" y1="625" x2="188" y2="688"/>
  <line stroke="red" x1="250" y1="625" x2="250" y2="688"/>
  <line stroke="blue" x1="250" y1="625" x2="312" y2="688"/>
  <line stroke="blue" x1="625" y1="250" x2="625" y2="375"/>
  <line stroke="red" x1="625" y1="250" x2="688" y2="312"/>
  <line stroke="blue" x1="625" y1="250" x2="750" y2="250"/>
  <line stroke="blue" x1="562" y1="375" x2="625" y2="375"/>
  <line stroke="red" x1="562" y1="375" x2="562" y2="625"/>
  <line stroke="red" x1="188" y1="688" x2="250" y2="688"/>
  <line stroke="red" x1="188" y1="688" x2="125" y2="750"/>
  <line stroke="red" x1="625" y1="375" x2="688" y2="375"/>
  <line stroke="blue" x1="625" y1="375" x2="625" y2="625"/>
  <line stroke="red" x1="250" y1="688" x2="312" y2="688"/>
  <line stroke="blue" x1="250" y1="688" x2="250" y2="750"/>
  <line stroke="blue" x1="750" y1="0" x2="750" y2="62"/>
  <line stroke="black" x1="750" y1="0" x2="875" y2="0"/>
  <line stroke="red" x1="750" y1="62" x2="750" y2="125"/>
  <line stroke="red" x1="750" y1="62" x2="938" y2="62"/>
  <line stroke="red" x1="312" y1="688" x2="375" y2="750"/>
  <line stroke="red" x1="688" y1="312" x2="688" y2="375"/>
  <line stroke="red" x1="688" y1="312" x2="750" y2="312"/>
  <line stroke="blue" x1="688" y1="312" x2="750" y2="375"/>
  <line stroke="blue" x1="125" y1="750" x2="250" y2="750"/>
  <line stroke="blue" x1="125" y1="750" x2="62" y2="812"/>
  <line stroke="blue" x1="750" y1="125" x2="750" y2="188"/>
  <line stroke="blue" x1="750" y1="125" x2="1000" y2="125"/>
  <line stroke="red" x1="750" y1="188" x2="750" y2="250"/>
  <line stroke="red" x1="750" y1="188" x2="938" y2="188"/>
  <line stroke="blue" x1="688" y1="375" x2="750" y2="375"/>
  <line stroke="red" x1="688" y1="375" x2="688" y2="625"/>
  <line stroke="blue" x1="250" y1="750" x2="375" y2="750"/>
  <line stroke="red" x1="250" y1="750" x2="250" y2="812"/>
  <line stroke="blue" x1="750" y1="250" x2="750" y2="312"/>
  <line stroke="blue" x1="750" y1="250" x2="875" y2="250"/>
  <line stroke="blue" x1="500" y1="625" x2="438" y2="688"/>
  <line stroke="red" x1="500" y1="625" x2="562" y2="625"/>
  <line stroke="blue" x1="500" y1="625" x2="562" y2="688"/>
  <line stroke="red" x1="750" y1="312" x2="750" y2="375"/>
  <line stroke="red" x1="750" y1="312" x2="812" y2="312"/>
  <line stroke="red" x1="62" y1="812" x2="250" y2="812"/>
  <line stroke="red" x1="62" y1="812" x2="0" y2="875"/>
  <line stroke="red" x1="438" y1="688" x2="375" y2="750"/>
  <line stroke="red" x1="438" y1="688" x2="562" y2="688"/>
  <line stroke="blue" x1="375" y1="750" x2="375" y2="812"/>
  <line stroke="blue" x1="375" y1="750" x2="625" y2="750"/>
  <line stroke="blue" x1="750" y1="375" x2="812" y2="312"/>
  <line stroke="red" x1="750" y1="375" x2="812" y2="375"/>
  <line stroke="blue" x1="750" y1="375" x2="750" y2="625"/>
  <line stroke="blue" x1="562" y1="625" x2="625" y2="625"/>
  <line stroke="red" x1="562" y1="625" x2="562" y2="688"/>
  <line stroke="red" x1="250" y1="812" x2="375" y2="812"/>
  <line stroke="blue" x1="250" y1="812" x2="250" y2="875"/>
  <line stroke="red" x1="812" y1="312" x2="812" y2="375"/>
  <line stroke="red" x1="812" y1="312" x2="875" y2="250"/>
  <line stroke="blue" x1="0" y1="875" x2="250" y2="875"/>
  <line stroke="red" x1="0" y1="875" x2="62" y2="938"/>
  <line stroke="black" x1="0" y1="875" x2="0" y2="1000"/>
  <line stroke="black" x1="875" y1="0" x2="938" y2="0"/>
  <line stroke="blue" x1="875" y1="0" x2="938" y2="62"/>
  <line stroke="red" x1="625" y1="625" x2="688" y2="625"/>
  <line stroke="blue" x1="625" y1="625" x2="625" y2="750"/>
  <line stroke="red" x1="562" y1="688" x2="625" y2="750"/>
  <line stroke="red" x1="375" y1="812" x2="375" y2="875"/>
  <line stroke="red" x1="375" y1="812" x2="625" y2="812"/>
  <line stroke="blue" x1="812" y1="375" x2="875" y2="375"/>
  <line stroke="red" x1="812" y1="375" x2="812" y2="625"/>
  <line stroke="blue" x1="250" y1="875" x2="375" y2="875"/>
  <line stroke="red" x1="250" y1="875" x2="250" y2="938"/>
  <line stroke="blue" x1="875" y1="250" x2="875" y2="375"/>
  <line stroke="blue" x1="875" y1="250" x2="938" y2="188"/>
  <line stroke="red" x1="688" y1="625" x2="688" y2="688"/>
  <line stroke="blue" x1="688" y1="625" x2="750" y2="625"/>
  <line stroke="red" x1="938" y1="0" x2="938" y2="62"/>
  <line stroke="black" x1="938" y1="0" x2="1000" y2="0"/>
  <line stroke="red" x1="62" y1="938" x2="250" y2="938"/>
  <line stroke="red" x1="62" y1="938" x2="62" y2="1000"/>
  <line stroke="blue" x1="62" y1="938" x2="125" y2="1000"/>
  <line stroke="red" x1="938" y1="62" x2="1000" y2="125"/>
  <line stroke="blue" x1="375" y1="875" x2="375" y2="938"/>
  <line stroke="blue" x1="375" y1="875" x2="625" y2="875"/>
  <line stroke="red" x1="875" y1="375" x2="938" y2="375"/>
  <line stroke="blue" x1="875" y1="375" x2="875" y2="625"/>
  <line stroke="red" x1="938" y1="188" x2="1000" y2="125"/>
  <line stroke="red" x1="938" y1="188" x2="938" y2="375"/>
  <line stroke="red" x1="250" y1="938" x2="375" y2="938"/>
  <line stroke="blue" x1="250" y1="938" x2="250" y2="1000"/>
  <line stroke="red" x1="688" y1="688" x2="625" y2="750"/>
  <line stroke="blue" x1="688" y1="688" x2="750" y2="625"/>
  <line stroke="red" x1="688" y1="688" x2="750" y2="688"/>
  <line stroke="blue" x1="625" y1="750" x2="625" y2="812"/>
  <line stroke="blue" x1="625" y1="750" x2="750" y2="750"/>
  <line stroke="red" x1="750" y1="625" x2="750" y2="688"/>
  <line stroke="red" x1="750" y1="625" x2="812" y2="625"/>
  <line stroke="blue" x1="750" y1="625" x2="812" y2="688"/>
  <line stroke="black" x1="0" y1="1000" x2="62" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="125"/>
  <line stroke="black" x1="62" y1="1000" x2="125" y2="1000"/>
  <line stroke="black" x1="125" y1="1000" x2="250" y2="1000"/>
  <line stroke="black" x1="1000" y1="125" x2="1000" y2="375"/>
  <line stroke="red" x1="375" y1="938" x2="375" y2="1000"/>
  <line stroke="red" x1="375" y1="938" x2="625" y2="938"/>
  <line stroke="blue" x1="938" y1="375" x2="1000" y2="375"/>
  <line stroke="red" x1="938" y1="375" x2="938" y2="625"/>
  <line stroke="blue" x1="750" y1="688" x2="750" y2="750"/>
  <line stroke="red" x1="750" y1="688" x2="812" y2="688"/>
  <line stroke="red" x1="625" y1="812" x2="625" y2="875"/>
  <line stroke="red" x1="625" y1="812" x2="750" y2="812"/>
  <line stroke="red" x1="812" y1="625" x2="812" y2="688"/>
  <line stroke="blue" x1="812" y1="625" x2="875" y2="625"/>
  <line stroke="black" x1="250" y1="1000" x2="375" y2="1000"/>
  <line stroke="red" x1="750" y1="750" x2="750" y2="812"/>
  <line stroke="blue" x1="750" y1="750" x2="875" y2="750"/>
  <line stroke="red" x1="812" y1="688" x2="875" y2="750"/>
  <line stroke="black" x1="375" y1="1000" x2="625" y2="1000"/>
  <line stroke="black" x1="1000" y1="375" x2="1000" y2="625"/>
  <line stroke="blue" x1="625" y1="875" x2="625" y2="938"/>
  <line stroke="blue" x1="625" y1="875" x2="750" y2="875"/>
  <line stroke="red" x1="875" y1="625" x2="938" y2="625"/>
  <line stroke="blue" x1="875" y1="625" x2="875" y2="750"/>
  <line stroke="blue" x1="750" y1="812" x2="750" y2="875"/>
  <line stroke="red" x1="750" y1="812" x2="938" y2="812"/>
  <line stroke="red" x1="625" y1="938" x2="625" y2="1000"/>
  <line stroke="red" x1="625" y1="938" x2="750" y2="938"/>
  <line stroke="blue" x1="938" y1="625" x2="1000" y2="625"/>
  <line stroke="red" x1="938" y1="625" x2="938" y2="812"/>
  <line stroke="red" x1="750" y1="875" x2="750" y2="938"/>
  <line stroke="blue" x1="750" y1="875" x2="1000" y2="875"/>
  <line stroke="blue" x1="875" y1="750" x2="938" y2="812"/>
  <line stroke="black" x1="625" y1="1000" x2="750" y2="1000"/>
  <line stroke="black" x1="1000" y1="625" x2="1000" y2="875"/>
  <line stroke="blue" x1="750" y1="938" x2="750" y2="1000"/>
  <line stroke="red" x1="750" y1="938" x2="938" y2="938"/>
  <line stroke="red" x1="938" y1="812" x2="1000" y2="875"/>
  <line stroke="black" x1="750" y1="1000" x2="875" y2="1000"/>
  <line stroke="blue" x1="938" y1="938" x2="875" y2="1000"/>
  <line stroke="red" x1="938" y1="938" x2="1000" y2="875"/>
  <line stroke="red" x1="938" y1="938" x2="938" y2="1000"/>
  <line stroke="black" x1="875" y1="1000" x2="938" y2="1000"/>
  <line stroke="black" x1="1000" y1="875" x2="1000" y2="1000"/>
  <line stroke="black" x1="938" y1="1000" x2="1000" y2="1000"/>
</svg>""",
)

TALL_SHAPING_TEST_1 = BoxPleatingCreasePatternExample(
    name="tall_border_flap",
    grid_size=8,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="500" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="1000"/>
  <line stroke="red" x1="500" y1="0" x2="500" y2="375"/>
  <line stroke="black" x1="500" y1="0" x2="1000" y2="0"/>
  <line stroke="red" x1="375" y1="500" x2="500" y2="375"/>
  <line stroke="red" x1="500" y1="375" x2="625" y2="500"/>
  <line stroke="black" x1="0" y1="1000" x2="1000" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="1000"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="500" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="1000"/>
  <line stroke="blue" x1="375" y1="125" x2="500" y2="125"/>
  <line stroke="red" x1="375" y1="250" x2="500" y2="250"/>
  <line stroke="blue" x1="500" y1="0" x2="500" y2="125"/>
  <line stroke="black" x1="500" y1="0" x2="1000" y2="0"/>
  <line stroke="red" x1="500" y1="125" x2="500" y2="250"/>
  <line stroke="blue" x1="500" y1="125" x2="625" y2="125"/>
  <line stroke="red" x1="375" y1="375" x2="500" y2="375"/>
  <line stroke="blue" x1="500" y1="250" x2="500" y2="375"/>
  <line stroke="red" x1="500" y1="250" x2="625" y2="250"/>
  <line stroke="red" x1="375" y1="500" x2="500" y2="375"/>
  <line stroke="blue" x1="500" y1="375" x2="500" y2="500"/>
  <line stroke="red" x1="500" y1="375" x2="625" y2="375"/>
  <line stroke="red" x1="500" y1="375" x2="625" y2="500"/>
  <line stroke="black" x1="0" y1="1000" x2="1000" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="1000"/>
</svg>""",
)

TALL_SHAPING_TEST_2 = BoxPleatingCreasePatternExample(
    name="tall_central_flap",
    grid_size=8,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="0" y2="1000"/>
  <line stroke="black" x1="0" y1="0" x2="1000" y2="0"/>
  <line stroke="red" x1="375" y1="125" x2="500" y2="250"/>
  <line stroke="red" x1="500" y1="250" x2="625" y2="125"/>
  <line stroke="red" x1="500" y1="250" x2="500" y2="500"/>
  <line stroke="red" x1="500" y1="500" x2="375" y2="625"/>
  <line stroke="red" x1="500" y1="500" x2="625" y2="625"/>
  <line stroke="black" x1="0" y1="1000" x2="1000" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="1000"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="0" y2="1000"/>
  <line stroke="black" x1="0" y1="0" x2="1000" y2="0"/>
  <line stroke="red" x1="375" y1="125" x2="500" y2="250"/>
  <line stroke="blue" x1="375" y1="250" x2="500" y2="250"/>
  <line stroke="blue" x1="500" y1="125" x2="500" y2="250"/>
  <line stroke="red" x1="375" y1="375" x2="500" y2="375"/>
  <line stroke="blue" x1="500" y1="250" x2="500" y2="375"/>
  <line stroke="red" x1="500" y1="250" x2="625" y2="125"/>
  <line stroke="blue" x1="500" y1="250" x2="625" y2="250"/>
  <line stroke="blue" x1="375" y1="500" x2="500" y2="500"/>
  <line stroke="red" x1="500" y1="375" x2="500" y2="500"/>
  <line stroke="red" x1="500" y1="375" x2="625" y2="375"/>
  <line stroke="red" x1="500" y1="500" x2="375" y2="625"/>
  <line stroke="red" x1="500" y1="500" x2="500" y2="625"/>
  <line stroke="blue" x1="500" y1="500" x2="625" y2="500"/>
  <line stroke="red" x1="500" y1="500" x2="625" y2="625"/>
  <line stroke="black" x1="0" y1="1000" x2="1000" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="1000"/>
</svg>
""",
)

X_TEST = BoxPleatingCreasePatternExample(
    name="x_test",
    grid_size=8,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8">
  <line stroke="black" x1="0" y1="0" x2="0" y2="4"/>
  <line stroke="black" x1="0" y1="0" x2="4" y2="0"/>
  <line stroke="red" x1="0" y1="0" x2="4" y2="4"/>
  <line stroke="green" x1="0" y1="4" x2="4" y2="4"/>
  <line stroke="black" x1="0" y1="4" x2="0" y2="8"/>
  <line stroke="green" x1="4" y1="0" x2="4" y2="4"/>
  <line stroke="black" x1="4" y1="0" x2="8" y2="0"/>
  <line stroke="red" x1="4" y1="4" x2="0" y2="8"/>
  <line stroke="red" x1="4" y1="4" x2="8" y2="0"/>
  <line stroke="green" x1="4" y1="4" x2="4" y2="8"/>
  <line stroke="green" x1="4" y1="4" x2="8" y2="4"/>
  <line stroke="red" x1="4" y1="4" x2="8" y2="8"/>
  <line stroke="black" x1="0" y1="8" x2="4" y2="8"/>
  <line stroke="black" x1="8" y1="0" x2="8" y2="4"/>
  <line stroke="black" x1="4" y1="8" x2="8" y2="8"/>
  <line stroke="black" x1="8" y1="4" x2="8" y2="8"/>
</svg>""",
)

GENERATED4 = BoxPleatingCreasePatternExample(
    name="generated4",
    grid_size=9,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 9 9">
  <rect stroke="black" x="0" y="0" width="9" height="9"/>
  <line stroke="green" x1="0" y1="1" x2="4" y2="1"/>
  <line stroke="red" x1="1" y1="0" x2="2" y2="1"/>
  <line stroke="green" x1="2" y1="0" x2="2" y2="1"/>
  <line stroke="red" x1="2" y1="1" x2="3" y2="0"/>
  <line stroke="red" x1="3" y1="0" x2="4" y2="1"/>
  <line stroke="green" x1="4" y1="0" x2="4" y2="9"/>
  <line stroke="red" x1="4" y1="1" x2="0" y2="5"/>
  <line stroke="red" x1="0" y1="5" x2="4" y2="9"/>
  <line stroke="red" x1="7" y1="0" x2="9" y2="2"/>
  <line stroke="red" x1="4" y1="9" x2="9" y2="4"/>
</svg>""",
)

NONE_OVERLAPPING_PLEATS = BoxPleatingCreasePatternExample(
    name="none_overlapping_pleats",
    grid_size=13,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 13 13">
  <rect stroke="black" x="0" y="0" width="13" height="13"/>
  <line stroke="red" x1="0" y1="0" x2="2" y2="2"/>
  <line stroke="green" x1="0" y1="2" x2="2" y2="2"/>
  <line stroke="green" x1="2" y1="0" x2="2" y2="2"/>
  <line stroke="red" x1="2" y1="2" x2="3" y2="1"/>
  <line stroke="green" x1="2" y1="2" x2="4" y2="2"/>
  <line stroke="red" x1="3" y1="0" x2="3" y2="1"/>
  <line stroke="red" x1="3" y1="1" x2="4" y2="2"/>
  <line stroke="green" x1="0" y1="4" x2="3" y2="4"/>
  <line stroke="green" x1="4" y1="0" x2="4" y2="2"/>
  <line stroke="red" x1="4" y1="2" x2="6" y2="4"/>
  <line stroke="red" x1="3" y1="4" x2="4" y2="5"/>
  <line stroke="red" x1="3" y1="4" x2="0" y2="7"/>
  <line stroke="green" x1="3" y1="4" x2="6" y2="4"/>
  <line stroke="green" x1="3" y1="4" x2="3" y2="10"/>
  <line stroke="green" x1="6" y1="0" x2="6" y2="4"/>
  <line stroke="red" x1="4" y1="5" x2="5" y2="6"/>
  <line stroke="green" x1="4" y1="5" x2="7" y2="5"/>
  <line stroke="green" x1="4" y1="5" x2="4" y2="13"/>
  <line stroke="red" x1="0" y1="7" x2="3" y2="10"/>
  <line stroke="green" x1="7" y1="0" x2="7" y2="5"/>
  <line stroke="red" x1="6" y1="4" x2="7" y2="5"/>
  <line stroke="red" x1="5" y1="6" x2="6" y2="7"/>
  <line stroke="green" x1="5" y1="6" x2="8" y2="6"/>
  <line stroke="green" x1="5" y1="6" x2="5" y2="13"/>
  <line stroke="green" x1="8" y1="0" x2="8" y2="6"/>
  <line stroke="red" x1="7" y1="5" x2="8" y2="6"/>
  <line stroke="green" x1="9" y1="0" x2="9" y2="7"/>
  <line stroke="red" x1="6" y1="7" x2="7" y2="8"/>
  <line stroke="green" x1="6" y1="7" x2="9" y2="7"/>
  <line stroke="green" x1="6" y1="7" x2="6" y2="13"/>
  <line stroke="green" x1="0" y1="10" x2="3" y2="10"/>
  <line stroke="red" x1="8" y1="6" x2="9" y2="7"/>
  <line stroke="green" x1="10" y1="0" x2="10" y2="8"/>
  <line stroke="red" x1="3" y1="10" x2="0" y2="13"/>
  <line stroke="green" x1="3" y1="10" x2="3" y2="13"/>
  <line stroke="green" x1="7" y1="8" x2="10" y2="8"/>
  <line stroke="red" x1="7" y1="8" x2="9" y2="10"/>
  <line stroke="green" x1="7" y1="8" x2="7" y2="13"/>
  <line stroke="red" x1="9" y1="7" x2="10" y2="8"/>
  <line stroke="red" x1="12" y1="0" x2="12" y2="6"/>
  <line stroke="red" x1="10" y1="8" x2="12" y2="6"/>
  <line stroke="green" x1="10" y1="8" x2="11" y2="8"/>
  <line stroke="red" x1="12" y1="6" x2="13" y2="7"/>
  <line stroke="red" x1="9" y1="10" x2="11" y2="8"/>
  <line stroke="red" x1="9" y1="10" x2="9" y2="13"/>
  <line stroke="green" x1="11" y1="8" x2="13" y2="8"/>
  <line stroke="red" x1="11" y1="8" x2="13" y2="10"/>
  <line stroke="green" x1="11" y1="8" x2="11" y2="13"/>
</svg>""",
)

GENERATED5 = BoxPleatingCreasePatternExample(
    name="generated5",
    grid_size=14,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14">
  <line stroke="black" x1="0" y1="0" x2="0" y2="8"/>
  <line stroke="black" x1="0" y1="0" x2="8" y2="0"/>
  <line stroke="red" x1="0" y1="0" x2="8" y2="8"/>
  <line stroke="green" x1="0" y1="8" x2="8" y2="8"/>
  <line stroke="black" x1="0" y1="8" x2="0" y2="12"/>
  <line stroke="green" x1="8" y1="0" x2="8" y2="8"/>
  <line stroke="red" x1="8" y1="0" x2="12" y2="4"/>
  <line stroke="black" x1="8" y1="0" x2="14" y2="0"/>
  <line stroke="red" x1="8" y1="8" x2="2" y2="14"/>
  <line stroke="green" x1="8" y1="8" x2="8" y2="14"/>
  <line stroke="black" x1="0" y1="12" x2="0" y2="14"/>
  <line stroke="red" x1="0" y1="12" x2="2" y2="14"/>
  <line stroke="red" x1="12" y1="4" x2="14" y2="2"/>
  <line stroke="red" x1="12" y1="4" x2="12" y2="10"/>
  <line stroke="black" x1="0" y1="14" x2="2" y2="14"/>
  <line stroke="black" x1="14" y1="0" x2="14" y2="2"/>
  <line stroke="black" x1="2" y1="14" x2="8" y2="14"/>
  <line stroke="black" x1="14" y1="2" x2="14" y2="12"/>
  <line stroke="red" x1="12" y1="10" x2="8" y2="14"/>
  <line stroke="red" x1="12" y1="10" x2="14" y2="12"/>
  <line stroke="black" x1="8" y1="14" x2="14" y2="14"/>
  <line stroke="black" x1="14" y1="12" x2="14" y2="14"/>
</svg>""",
)

BORDERRIDGE_TEST = BoxPleatingCreasePatternExample(
    name="borderridge_test",
    grid_size=3,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3 3">
  <rect stroke="black" x="0" y="0" width="3" height="3"/>
  <line stroke="red" x1="0" y1="0" x2="1" y2="1"/>
  <line stroke="green" x1="0" y1="1" x2="1" y2="1"/>
  <line stroke="green" x1="1" y1="0" x2="1" y2="1"/>
  <line stroke="red" x1="1" y1="1" x2="0" y2="2"/>
  <line stroke="red" x1="1" y1="1" x2="2" y2="0"/>
  <line stroke="red" x1="1" y1="1" x2="2" y2="2"/>
  <line stroke="green" x1="1" y1="1" x2="1" y2="3"/>
  <line stroke="green" x1="1" y1="1" x2="3" y2="1"/>
  <line stroke="red" x1="2" y1="2" x2="1" y2="3"/>
  <line stroke="red" x1="2" y1="2" x2="3" y2="2"/>
</svg>""",
)

FFCENTRALFLAP_TEST = BoxPleatingCreasePatternExample(
    name="ffcentralflap_test",
    grid_size=20,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
  <rect stroke="black" x="0" y="0" width="20" height="20"/>
  <line stroke="red" x1="0" y1="1" x2="7" y2="1"/>
  <line stroke="green" x1="0" y1="2" x2="8" y2="2"/>
  <line stroke="green" x1="0" y1="4" x2="5" y2="4"/>
  <line stroke="red" x1="5" y1="4" x2="1" y2="8"/>
  <line stroke="red" x1="5" y1="4" x2="10" y2="9"/>
  <line stroke="green" x1="5" y1="4" x2="5" y2="14"/>
  <line stroke="green" x1="5" y1="4" x2="15" y2="4"/>
  <line stroke="red" x1="0" y1="7" x2="1" y2="8"/>
  <line stroke="red" x1="7" y1="1" x2="8" y2="0"/>
  <line stroke="red" x1="7" y1="1" x2="8" y2="2"/>
  <line stroke="green" x1="8" y1="0" x2="8" y2="2"/>
  <line stroke="red" x1="1" y1="8" x2="1" y2="10"/>
  <line stroke="red" x1="8" y1="2" x2="10" y2="0"/>
  <line stroke="green" x1="8" y1="2" x2="12" y2="2"/>
  <line stroke="red" x1="10" y1="0" x2="12" y2="2"/>
  <line stroke="red" x1="1" y1="10" x2="0" y2="11"/>
  <line stroke="red" x1="1" y1="10" x2="5" y2="14"/>
  <line stroke="green" x1="12" y1="0" x2="12" y2="2"/>
  <line stroke="red" x1="12" y1="0" x2="13" y2="1"/>
  <line stroke="red" x1="12" y1="2" x2="13" y2="1"/>
  <line stroke="green" x1="12" y1="2" x2="20" y2="2"/>
  <line stroke="red" x1="13" y1="1" x2="20" y2="1"/>
  <line stroke="red" x1="10" y1="9" x2="5" y2="14"/>
  <line stroke="red" x1="10" y1="9" x2="15" y2="4"/>
  <line stroke="red" x1="10" y1="9" x2="15" y2="14"/>
  <line stroke="green" x1="0" y1="14" x2="5" y2="14"/>
  <line stroke="green" x1="5" y1="14" x2="10" y2="14"/>
  <line stroke="green" x1="15" y1="4" x2="20" y2="4"/>
  <line stroke="green" x1="15" y1="4" x2="15" y2="14"/>
  <line stroke="red" x1="15" y1="4" x2="19" y2="8"/>
  <line stroke="red" x1="10" y1="14" x2="4" y2="20"/>
  <line stroke="green" x1="10" y1="14" x2="15" y2="14"/>
  <line stroke="green" x1="10" y1="14" x2="10" y2="20"/>
  <line stroke="red" x1="10" y1="14" x2="16" y2="20"/>
  <line stroke="red" x1="15" y1="14" x2="19" y2="10"/>
  <line stroke="green" x1="15" y1="14" x2="20" y2="14"/>
  <line stroke="red" x1="19" y1="8" x2="20" y2="7"/>
  <line stroke="red" x1="19" y1="8" x2="19" y2="10"/>
  <line stroke="red" x1="19" y1="10" x2="20" y2="11"/>
</svg>""",
)

GENERATED7 = BoxPleatingCreasePatternExample(
    name="generated7",
    grid_size=13,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 13 13">
  <line stroke="black" x1="0" y1="0" x2="0" y2="3"/>
  <line stroke="black" x1="0" y1="0" x2="3" y2="0"/>
  <line stroke="green" x1="0" y1="3" x2="6" y2="3"/>
  <line stroke="black" x1="0" y1="3" x2="0" y2="9"/>
  <line stroke="black" x1="3" y1="0" x2="6" y2="0"/>
  <line stroke="red" x1="3" y1="0" x2="6" y2="3"/>
  <line stroke="green" x1="6" y1="0" x2="6" y2="3"/>
  <line stroke="black" x1="6" y1="0" x2="7" y2="0"/>
  <line stroke="red" x1="6" y1="3" x2="0" y2="9"/>
  <line stroke="green" x1="6" y1="3" x2="6" y2="13"/>
  <line stroke="black" x1="7" y1="0" x2="13" y2="0"/>
  <line stroke="red" x1="7" y1="0" x2="13" y2="6"/>
  <line stroke="black" x1="0" y1="9" x2="0" y2="11"/>
  <line stroke="black" x1="0" y1="11" x2="0" y2="13"/>
  <line stroke="red" x1="0" y1="11" x2="2" y2="13"/>
  <line stroke="black" x1="0" y1="13" x2="2" y2="13"/>
  <line stroke="black" x1="13" y1="0" x2="13" y2="6"/>
  <line stroke="black" x1="2" y1="13" x2="6" y2="13"/>
  <line stroke="red" x1="6" y1="13" x2="13" y2="6"/>
  <line stroke="black" x1="6" y1="13" x2="13" y2="13"/>
  <line stroke="black" x1="13" y1="6" x2="13" y2="13"/>
</svg>""",
)

VERTICAL_FAN_OUT_SHAPING_TEST1 = BoxPleatingCreasePatternExample(
    name="vertical_fan_out_shaping_test1",
    grid_size=8,
    packing_svg="",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8">
  <line stroke="black" x1="0" y1="0" x2="2" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="4"/>
  <line stroke="black" x1="2" y1="0" x2="4" y2="0"/>
  <line stroke="blue" x1="2" y1="0" x2="2" y2="4"/>
  <line stroke="blue" x1="0" y1="4" x2="2" y2="4"/>
  <line stroke="black" x1="0" y1="4" x2="0" y2="8"/>
  <line stroke="red" x1="4" y1="0" x2="4" y2="4"/>
  <line stroke="black" x1="4" y1="0" x2="6" y2="0"/>
  <line stroke="red" x1="2" y1="4" x2="4" y2="4"/>
  <line stroke="blue" x1="2" y1="4" x2="2" y2="8"/>
  <line stroke="blue" x1="4" y1="4" x2="6" y2="4"/>
  <line stroke="red" x1="4" y1="4" x2="4" y2="8"/>
  <line stroke="blue" x1="6" y1="0" x2="6" y2="4"/>
  <line stroke="black" x1="6" y1="0" x2="8" y2="0"/>
  <line stroke="red" x1="6" y1="4" x2="8" y2="4"/>
  <line stroke="blue" x1="6" y1="4" x2="6" y2="8"/>
  <line stroke="black" x1="0" y1="8" x2="2" y2="8"/>
  <line stroke="black" x1="8" y1="0" x2="8" y2="4"/>
  <line stroke="black" x1="2" y1="8" x2="4" y2="8"/>
  <line stroke="black" x1="4" y1="8" x2="6" y2="8"/>
  <line stroke="black" x1="8" y1="4" x2="8" y2="8"/>
  <line stroke="black" x1="6" y1="8" x2="8" y2="8"/>
</svg>
""",
)

VERTICAL_FAN_OUT_SHAPING_TEST2 = BoxPleatingCreasePatternExample(
    name="vertical_fan_out_shaping_test2",
    grid_size=8,
    packing_svg="",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="0" y2="500"/>
  <line stroke="black" x1="0" y1="0" x2="500" y2="0"/>
  <line stroke="red" x1="0" y1="0" x2="500" y2="500"/>
  <line stroke="red" x1="0" y1="500" x2="500" y2="500"/>
  <line stroke="black" x1="0" y1="500" x2="0" y2="1000"/>
  <line stroke="blue" x1="500" y1="0" x2="500" y2="500"/>
  <line stroke="black" x1="500" y1="0" x2="1000" y2="0"/>
  <line stroke="red" x1="500" y1="500" x2="0" y2="1000"/>
  <line stroke="red" x1="500" y1="500" x2="1000" y2="0"/>
  <line stroke="blue" x1="500" y1="500" x2="500" y2="1000"/>
  <line stroke="blue" x1="500" y1="500" x2="1000" y2="500"/>
  <line stroke="red" x1="500" y1="500" x2="1000" y2="1000"/>
  <line stroke="black" x1="0" y1="1000" x2="500" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="500"/>
  <line stroke="black" x1="500" y1="1000" x2="1000" y2="1000"/>
  <line stroke="black" x1="1000" y1="500" x2="1000" y2="1000"/>
</svg>""",
)

HARD_TILING_ODD = BoxPleatingCreasePatternExample(
    name="hard_tiling_odd",
    tree_data={
        "version": "0.7",
        "design": {
            "title": "tiling hard odd",
            "mode": "layout",
            "description": "",
            "layout": {
                "sheet": {"type": "rect", "height": 14, "width": 14},
                "flaps": [
                    {"id": 1, "x": 13, "y": 14, "width": 0, "height": 0},
                    {"id": 7, "x": 14, "y": 5, "width": 0, "height": 0},
                    {"id": 2, "x": 9, "y": 6, "width": 0, "height": 0},
                    {"id": 5, "x": 12, "y": 1, "width": 0, "height": 0},
                    {"id": 8, "x": 9, "y": 0, "width": 0, "height": 0},
                    {"id": 6, "x": 3, "y": 3, "width": 0, "height": 0},
                    {"id": 3, "x": 0, "y": 14, "width": 0, "height": 0},
                ],
                "stretches": [],
            },
            "tree": {
                "sheet": {"type": "rect", "height": 8, "width": 8},
                "nodes": [
                    {"id": 0, "name": "", "x": 2, "y": 2},
                    {"id": 1, "name": "", "x": 4, "y": 0},
                    {"id": 2, "name": "", "x": 4, "y": 2},
                    {"id": 3, "name": "", "x": 0, "y": 0},
                    {"id": 5, "name": "", "x": 1, "y": 3},
                    {"id": 6, "name": "", "x": 4, "y": 4},
                    {"id": 7, "name": "", "x": 2, "y": 0},
                    {"id": 8, "name": "", "x": 0, "y": 2},
                ],
                "edges": [
                    {"n1": 0, "n2": 1, "length": 6},
                    {"n1": 0, "n2": 3, "length": 7},
                    {"n1": 0, "n2": 2, "length": 2},
                    {"n1": 0, "n2": 7, "length": 3},
                    {"n1": 0, "n2": 5, "length": 1},
                    {"n1": 0, "n2": 8, "length": 2},
                    {"n1": 0, "n2": 6, "length": 4},
                ],
            },
        },
    },
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14">
  <rect stroke="black" x="0" y="0" width="14" height="14"/>
  <line stroke="red" x1="0" y1="0" x2="7" y2="7"/>
  <line stroke="green" x1="0" y1="7" x2="2" y2="7"/>
  <line stroke="green" x1="7" y1="0" x2="7" y2="7"/>
  <line stroke="red" x1="2" y1="7" x2="0" y2="9"/>
  <line stroke="green" x1="2" y1="7" x2="6" y2="7"/>
  <line stroke="red" x1="2" y1="7" x2="4" y2="9"/>
  <line stroke="green" x1="2" y1="7" x2="2" y2="11"/>
  <line stroke="red" x1="8" y1="0" x2="11" y2="3"/>
  <line stroke="red" x1="0" y1="9" x2="2" y2="11"/>
  <line stroke="red" x1="6" y1="7" x2="4" y2="9"/>
  <line stroke="green" x1="6" y1="7" x2="7" y2="7"/>
  <line stroke="red" x1="6" y1="7" x2="7" y2="8"/>
  <line stroke="green" x1="6" y1="7" x2="6" y2="11"/>
  <line stroke="red" x1="4" y1="9" x2="2" y2="11"/>
  <line stroke="red" x1="4" y1="9" x2="6" y2="11"/>
  <line stroke="green" x1="7" y1="7" x2="8" y2="7"/>
  <line stroke="red" x1="7" y1="7" x2="11" y2="3"/>
  <line stroke="red" x1="7" y1="8" x2="8" y2="7"/>
  <line stroke="red" x1="7" y1="8" x2="7" y2="14"/>
  <line stroke="green" x1="8" y1="7" x2="14" y2="7"/>
  <line stroke="green" x1="8" y1="7" x2="8" y2="14"/>
  <line stroke="red" x1="8" y1="7" x2="14" y2="13"/>
  <line stroke="green" x1="0" y1="11" x2="2" y2="11"/>
  <line stroke="red" x1="0" y1="11" x2="3" y2="14"/>
  <line stroke="green" x1="2" y1="11" x2="6" y2="11"/>
  <line stroke="red" x1="11" y1="3" x2="14" y2="0"/>
  <line stroke="red" x1="11" y1="3" x2="14" y2="6"/>
  <line stroke="red" x1="6" y1="11" x2="3" y2="14"/>
  <line stroke="green" x1="6" y1="11" x2="6" y2="14"/>
  <line stroke="red" x1="13" y1="14" x2="14" y2="13"/>
</svg>
    """,
    grid_size=14,
)

HARD_PACKING_TIGHT = BoxPleatingCreasePatternExample(
    name="hard_packing_tight",
    tree_data={
        "version": "0.7",
        "design": {
            "title": "packing hard tight",
            "mode": "layout",
            "description": "",
            "layout": {
                "sheet": {"type": "rect", "height": 16, "width": 16},
                "flaps": [
                    {"id": 5, "x": 13, "y": 9, "width": 0, "height": 0},
                    {"id": 6, "x": 0, "y": 16, "width": 0, "height": 0},
                    {"id": 3, "x": 16, "y": 0, "width": 0, "height": 0},
                    {"id": 2, "x": 10, "y": 10, "width": 0, "height": 0},
                    {"id": 1, "x": 16, "y": 16, "width": 0, "height": 0},
                    {"id": 7, "x": 0, "y": 0, "width": 0, "height": 0},
                    {"id": 4, "x": 10, "y": 16, "width": 0, "height": 0},
                    {"id": 8, "x": 16, "y": 10, "width": 0, "height": 0},
                    {"id": 9, "x": 11, "y": 13, "width": 0, "height": 0},
                    {"id": 10, "x": 13, "y": 11, "width": 0, "height": 0},
                    {"id": 11, "x": 9, "y": 13, "width": 0, "height": 0},
                ],
                "stretches": [],
            },
            "tree": {
                "sheet": {"type": "rect", "height": 20, "width": 20},
                "nodes": [
                    {"id": 0, "name": "", "x": 10, "y": 10},
                    {"id": 1, "name": "", "x": 14, "y": 14},
                    {"id": 2, "name": "", "x": 13, "y": 9},
                    {"id": 3, "name": "", "x": 14, "y": 6},
                    {"id": 4, "name": "", "x": 12, "y": 12},
                    {"id": 5, "name": "", "x": 12, "y": 11},
                    {"id": 6, "name": "", "x": 6, "y": 6},
                    {"id": 7, "name": "", "x": 6, "y": 14},
                    {"id": 8, "name": "", "x": 9, "y": 13},
                    {"id": 9, "name": "", "x": 11, "y": 12},
                    {"id": 10, "name": "", "x": 12, "y": 10},
                    {"id": 11, "name": "", "x": 10, "y": 12},
                ],
                "edges": [
                    {"n1": 0, "n2": 6, "length": 8},
                    {"n1": 0, "n2": 5, "length": 1},
                    {"n1": 0, "n2": 3, "length": 8},
                    {"n1": 0, "n2": 2, "length": 2},
                    {"n1": 0, "n2": 1, "length": 4},
                    {"n1": 0, "n2": 7, "length": 8},
                    {"n1": 0, "n2": 4, "length": 2},
                    {"n1": 0, "n2": 8, "length": 2},
                    {"n1": 0, "n2": 9, "length": 1},
                    {"n1": 0, "n2": 10, "length": 1},
                    {"n1": 0, "n2": 11, "length": 1},
                ],
            },
        },
    },
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <rect stroke="black" x="0" y="0" width="16" height="16"/>
  <line stroke="red" x1="0" y1="0" x2="8" y2="8"/>
  <line stroke="green" x1="0" y1="8" x2="8" y2="8"/>
  <line stroke="green" x1="8" y1="0" x2="8" y2="8"/>
  <line stroke="red" x1="8" y1="8" x2="9" y2="9"/>
  <line stroke="green" x1="8" y1="8" x2="8" y2="10"/>
  <line stroke="green" x1="8" y1="8" x2="10" y2="8"/>
  <line stroke="red" x1="8" y1="8" x2="0" y2="16"/>
  <line stroke="red" x1="8" y1="8" x2="16" y2="0"/>
  <line stroke="red" x1="9" y1="9" x2="8" y2="10"/>
  <line stroke="red" x1="9" y1="9" x2="10" y2="8"/>
  <line stroke="red" x1="9" y1="9" x2="10" y2="10"/>
  <line stroke="green" x1="8" y1="10" x2="10" y2="10"/>
  <line stroke="red" x1="8" y1="10" x2="9" y2="11"/>
  <line stroke="green" x1="8" y1="10" x2="8" y2="12"/>
  <line stroke="green" x1="10" y1="8" x2="10" y2="10"/>
  <line stroke="red" x1="10" y1="8" x2="12" y2="10"/>
  <line stroke="green" x1="10" y1="8" x2="14" y2="8"/>
  <line stroke="red" x1="10" y1="10" x2="9" y2="11"/>
  <line stroke="green" x1="10" y1="10" x2="10" y2="12"/>
  <line stroke="red" x1="9" y1="11" x2="8" y2="12"/>
  <line stroke="red" x1="9" y1="11" x2="10" y2="12"/>
  <line stroke="green" x1="8" y1="12" x2="10" y2="12"/>
  <line stroke="red" x1="8" y1="12" x2="9" y2="13"/>
  <line stroke="green" x1="8" y1="12" x2="8" y2="14"/>
  <line stroke="red" x1="10" y1="12" x2="12" y2="10"/>
  <line stroke="red" x1="10" y1="12" x2="9" y2="13"/>
  <line stroke="green" x1="10" y1="12" x2="12" y2="12"/>
  <line stroke="red" x1="10" y1="12" x2="11" y2="13"/>
  <line stroke="green" x1="10" y1="12" x2="10" y2="14"/>
  <line stroke="red" x1="12" y1="10" x2="14" y2="8"/>
  <line stroke="red" x1="12" y1="10" x2="14" y2="12"/>
  <line stroke="red" x1="9" y1="13" x2="8" y2="14"/>
  <line stroke="red" x1="9" y1="13" x2="10" y2="14"/>
  <line stroke="green" x1="8" y1="14" x2="10" y2="14"/>
  <line stroke="green" x1="8" y1="14" x2="8" y2="16"/>
  <line stroke="red" x1="8" y1="14" x2="10" y2="16"/>
  <line stroke="green" x1="14" y1="8" x2="16" y2="8"/>
  <line stroke="green" x1="14" y1="8" x2="14" y2="12"/>
  <line stroke="red" x1="14" y1="8" x2="16" y2="10"/>
  <line stroke="red" x1="12" y1="12" x2="11" y2="13"/>
  <line stroke="green" x1="12" y1="12" x2="12" y2="14"/>
  <line stroke="green" x1="12" y1="12" x2="14" y2="12"/>
  <line stroke="red" x1="12" y1="12" x2="16" y2="16"/>
  <line stroke="red" x1="11" y1="13" x2="10" y2="14"/>
  <line stroke="red" x1="11" y1="13" x2="12" y2="14"/>
  <line stroke="green" x1="10" y1="14" x2="12" y2="14"/>
  <line stroke="red" x1="12" y1="14" x2="10" y2="16"/>
  <line stroke="green" x1="12" y1="14" x2="12" y2="16"/>
  <line stroke="red" x1="14" y1="12" x2="16" y2="10"/>
  <line stroke="green" x1="14" y1="12" x2="16" y2="12"/>
</svg>""",
    grid_size=16,
)

HARD_PACKING_TIGHT2 = BoxPleatingCreasePatternExample(
    name="hard_packing_tight2",
    tree_data={
        "version": "0.7",
        "design": {
            "title": "packing hard tight 2",
            "mode": "tree",
            "description": "",
            "layout": {
                "sheet": {"type": "rect", "height": 22, "width": 22},
                "flaps": [
                    {"id": 1, "x": 8, "y": 22, "width": 0, "height": 0},
                    {"id": 2, "x": 14, "y": 22, "width": 0, "height": 0},
                    {"id": 3, "x": 14, "y": 0, "width": 0, "height": 0},
                    {"id": 4, "x": 22, "y": 0, "width": 0, "height": 0},
                    {"id": 5, "x": 8, "y": 14, "width": 0, "height": 0},
                    {"id": 6, "x": 8, "y": 8, "width": 0, "height": 0},
                    {"id": 7, "x": 22, "y": 22, "width": 0, "height": 0},
                    {"id": 8, "x": 0, "y": 0, "width": 0, "height": 0},
                    {"id": 9, "x": 22, "y": 14, "width": 0, "height": 0},
                    {"id": 10, "x": 0, "y": 8, "width": 0, "height": 0},
                    {"id": 11, "x": 8, "y": 0, "width": 0, "height": 0},
                    {"id": 12, "x": 0, "y": 14, "width": 0, "height": 0},
                    {"id": 13, "x": 14, "y": 4, "width": 0, "height": 0},
                    {"id": 14, "x": 0, "y": 22, "width": 0, "height": 0},
                    {"id": 15, "x": 4, "y": 14, "width": 0, "height": 0},
                    {"id": 16, "x": 18, "y": 8, "width": 0, "height": 0},
                    {"id": 17, "x": 22, "y": 8, "width": 0, "height": 0},
                    {"id": 18, "x": 14, "y": 8, "width": 0, "height": 0},
                    {"id": 19, "x": 8, "y": 18, "width": 0, "height": 0},
                    {"id": 20, "x": 15, "y": 15, "width": 0, "height": 0},
                    {"id": 21, "x": 13, "y": 11, "width": 0, "height": 0},
                    {"id": 22, "x": 11, "y": 15, "width": 0, "height": 0},
                    {"id": 23, "x": 11, "y": 17, "width": 0, "height": 0},
                    {"id": 24, "x": 15, "y": 11, "width": 0, "height": 0},
                    {"id": 25, "x": 11, "y": 13, "width": 0, "height": 0},
                    {"id": 26, "x": 17, "y": 11, "width": 0, "height": 0},
                ],
                "stretches": [],
            },
            "tree": {
                "sheet": {"type": "rect", "height": 20, "width": 20},
                "nodes": [
                    {"id": 0, "name": "", "x": 10, "y": 10},
                    {"id": 1, "name": "", "x": 8, "y": 13},
                    {"id": 2, "name": "", "x": 14, "y": 14},
                    {"id": 3, "name": "", "x": 8, "y": 9},
                    {"id": 4, "name": "", "x": 16, "y": 4},
                    {"id": 5, "name": "", "x": 7, "y": 9},
                    {"id": 6, "name": "", "x": 14, "y": 10},
                    {"id": 7, "name": "", "x": 6, "y": 6},
                    {"id": 8, "name": "", "x": 10, "y": 14},
                    {"id": 9, "name": "", "x": 10, "y": 6},
                    {"id": 10, "name": "", "x": 7, "y": 8},
                    {"id": 11, "name": "", "x": 6, "y": 10},
                    {"id": 12, "name": "", "x": 17, "y": 9},
                    {"id": 13, "name": "", "x": 9, "y": 8},
                    {"id": 14, "name": "", "x": 4, "y": 16},
                    {"id": 15, "name": "", "x": 15, "y": 13},
                    {"id": 16, "name": "", "x": 12, "y": 9},
                    {"id": 17, "name": "", "x": 13, "y": 16},
                    {"id": 18, "name": "", "x": 14, "y": 8},
                    {"id": 19, "name": "", "x": 12, "y": 13},
                    {"id": 20, "name": "", "x": 11, "y": 14},
                    {"id": 21, "name": "", "x": 13, "y": 12},
                    {"id": 22, "name": "", "x": 9, "y": 13},
                    {"id": 23, "name": "", "x": 5, "y": 12},
                    {"id": 24, "name": "", "x": 5, "y": 13},
                    {"id": 25, "name": "", "x": 8, "y": 10},
                    {"id": 26, "name": "", "x": 16, "y": 12},
                ],
                "edges": [
                    {"n1": 0, "n2": 1, "length": 2},
                    {"n1": 0, "n2": 2, "length": 4},
                    {"n1": 0, "n2": 3, "length": 2},
                    {"n1": 0, "n2": 4, "length": 6},
                    {"n1": 0, "n2": 5, "length": 2},
                    {"n1": 0, "n2": 6, "length": 4},
                    {"n1": 0, "n2": 7, "length": 4},
                    {"n1": 0, "n2": 8, "length": 4},
                    {"n1": 0, "n2": 9, "length": 4},
                    {"n1": 0, "n2": 10, "length": 4},
                    {"n1": 0, "n2": 11, "length": 4},
                    {"n1": 0, "n2": 12, "length": 2},
                    {"n1": 0, "n2": 13, "length": 2},
                    {"n1": 0, "n2": 14, "length": 6},
                    {"n1": 0, "n2": 15, "length": 2},
                    {"n1": 0, "n2": 16, "length": 2},
                    {"n1": 0, "n2": 17, "length": 2},
                    {"n1": 0, "n2": 18, "length": 2},
                    {"n1": 0, "n2": 19, "length": 2},
                    {"n1": 0, "n2": 20, "length": 3},
                    {"n1": 0, "n2": 21, "length": 1},
                    {"n1": 0, "n2": 22, "length": 1},
                    {"n1": 0, "n2": 23, "length": 1},
                    {"n1": 0, "n2": 24, "length": 1},
                    {"n1": 0, "n2": 25, "length": 1},
                    {"n1": 0, "n2": 26, "length": 1},
                ],
            },
        },
    },
    packing_svg="""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 22 22">
  <rect stroke="black" x="0" y="0" width="22" height="22"/>
  <line stroke="red" x1="0" y1="0" x2="6" y2="6"/>
  <line stroke="green" x1="0" y1="6" x2="2" y2="6"/>
  <line stroke="green" x1="6" y1="0" x2="6" y2="2"/>
  <line stroke="red" x1="2" y1="6" x2="0" y2="8"/>
  <line stroke="green" x1="2" y1="6" x2="6" y2="6"/>
  <line stroke="red" x1="2" y1="6" x2="4" y2="8"/>
  <line stroke="green" x1="2" y1="6" x2="2" y2="10"/>
  <line stroke="red" x1="6" y1="2" x2="8" y2="0"/>
  <line stroke="green" x1="6" y1="2" x2="6" y2="6"/>
  <line stroke="red" x1="6" y1="2" x2="8" y2="4"/>
  <line stroke="green" x1="6" y1="2" x2="10" y2="2"/>
  <line stroke="red" x1="0" y1="8" x2="2" y2="10"/>
  <line stroke="red" x1="8" y1="0" x2="10" y2="2"/>
  <line stroke="red" x1="6" y1="6" x2="4" y2="8"/>
  <line stroke="red" x1="6" y1="6" x2="8" y2="4"/>
  <line stroke="red" x1="6" y1="6" x2="8" y2="8"/>
  <line stroke="green" x1="6" y1="6" x2="6" y2="10"/>
  <line stroke="green" x1="6" y1="6" x2="10" y2="6"/>
  <line stroke="red" x1="4" y1="8" x2="2" y2="10"/>
  <line stroke="red" x1="4" y1="8" x2="6" y2="10"/>
  <line stroke="red" x1="8" y1="4" x2="10" y2="2"/>
  <line stroke="red" x1="8" y1="4" x2="10" y2="6"/>
  <line stroke="green" x1="0" y1="10" x2="2" y2="10"/>
  <line stroke="green" x1="10" y1="0" x2="10" y2="2"/>
  <line stroke="green" x1="2" y1="10" x2="4" y2="10"/>
  <line stroke="green" x1="10" y1="2" x2="10" y2="4"/>
  <line stroke="green" x1="4" y1="10" x2="6" y2="10"/>
  <line stroke="red" x1="4" y1="10" x2="0" y2="14"/>
  <line stroke="red" x1="4" y1="10" x2="8" y2="14"/>
  <line stroke="green" x1="4" y1="10" x2="4" y2="18"/>
  <line stroke="green" x1="10" y1="4" x2="10" y2="6"/>
  <line stroke="red" x1="10" y1="4" x2="11" y2="5"/>
  <line stroke="green" x1="10" y1="4" x2="12" y2="4"/>
  <line stroke="red" x1="10" y1="4" x2="14" y2="0"/>
  <line stroke="red" x1="8" y1="8" x2="6" y2="10"/>
  <line stroke="red" x1="8" y1="8" x2="10" y2="6"/>
  <line stroke="red" x1="8" y1="8" x2="10" y2="10"/>
  <line stroke="green" x1="6" y1="10" x2="10" y2="10"/>
  <line stroke="red" x1="10" y1="6" x2="11" y2="5"/>
  <line stroke="green" x1="10" y1="6" x2="10" y2="8"/>
  <line stroke="red" x1="10" y1="6" x2="11" y2="7"/>
  <line stroke="green" x1="10" y1="6" x2="12" y2="6"/>
  <line stroke="red" x1="11" y1="5" x2="12" y2="4"/>
  <line stroke="red" x1="11" y1="5" x2="12" y2="6"/>
  <line stroke="green" x1="12" y1="4" x2="12" y2="6"/>
  <line stroke="red" x1="12" y1="4" x2="15" y2="7"/>
  <line stroke="green" x1="12" y1="4" x2="18" y2="4"/>
  <line stroke="red" x1="10" y1="8" x2="11" y2="7"/>
  <line stroke="green" x1="10" y1="8" x2="10" y2="10"/>
  <line stroke="red" x1="10" y1="8" x2="11" y2="9"/>
  <line stroke="green" x1="10" y1="8" x2="12" y2="8"/>
  <line stroke="red" x1="11" y1="7" x2="12" y2="6"/>
  <line stroke="red" x1="11" y1="7" x2="12" y2="8"/>
  <line stroke="green" x1="12" y1="6" x2="12" y2="8"/>
  <line stroke="red" x1="0" y1="14" x2="4" y2="18"/>
  <line stroke="red" x1="14" y1="0" x2="18" y2="4"/>
  <line stroke="red" x1="10" y1="10" x2="11" y2="9"/>
  <line stroke="green" x1="10" y1="10" x2="12" y2="10"/>
  <line stroke="red" x1="11" y1="9" x2="12" y2="8"/>
  <line stroke="red" x1="11" y1="9" x2="12" y2="10"/>
  <line stroke="green" x1="12" y1="8" x2="12" y2="10"/>
  <line stroke="red" x1="12" y1="10" x2="8" y2="14"/>
  <line stroke="red" x1="12" y1="10" x2="15" y2="7"/>
  <line stroke="green" x1="12" y1="10" x2="12" y2="12"/>
  <line stroke="red" x1="12" y1="10" x2="13" y2="11"/>
  <line stroke="green" x1="12" y1="10" x2="14" y2="10"/>
  <line stroke="red" x1="8" y1="14" x2="4" y2="18"/>
  <line stroke="red" x1="8" y1="14" x2="12" y2="18"/>
  <line stroke="red" x1="15" y1="7" x2="18" y2="4"/>
  <line stroke="red" x1="15" y1="7" x2="18" y2="10"/>
  <line stroke="red" x1="12" y1="12" x2="13" y2="11"/>
  <line stroke="green" x1="12" y1="12" x2="14" y2="12"/>
  <line stroke="red" x1="12" y1="12" x2="14" y2="14"/>
  <line stroke="green" x1="12" y1="12" x2="12" y2="16"/>
  <line stroke="red" x1="13" y1="11" x2="14" y2="10"/>
  <line stroke="red" x1="13" y1="11" x2="14" y2="12"/>
  <line stroke="green" x1="14" y1="10" x2="14" y2="12"/>
  <line stroke="red" x1="14" y1="10" x2="15" y2="11"/>
  <line stroke="green" x1="14" y1="10" x2="16" y2="10"/>
  <line stroke="green" x1="0" y1="18" x2="4" y2="18"/>
  <line stroke="green" x1="18" y1="0" x2="18" y2="4"/>
  <line stroke="red" x1="14" y1="12" x2="15" y2="11"/>
  <line stroke="green" x1="14" y1="12" x2="16" y2="12"/>
  <line stroke="green" x1="4" y1="18" x2="12" y2="18"/>
  <line stroke="red" x1="4" y1="18" x2="0" y2="22"/>
  <line stroke="green" x1="4" y1="18" x2="4" y2="22"/>
  <line stroke="red" x1="4" y1="18" x2="8" y2="22"/>
  <line stroke="green" x1="18" y1="4" x2="18" y2="10"/>
  <line stroke="red" x1="18" y1="4" x2="22" y2="0"/>
  <line stroke="green" x1="18" y1="4" x2="22" y2="4"/>
  <line stroke="red" x1="18" y1="4" x2="22" y2="8"/>
  <line stroke="red" x1="15" y1="11" x2="16" y2="10"/>
  <line stroke="red" x1="15" y1="11" x2="16" y2="12"/>
  <line stroke="green" x1="16" y1="10" x2="16" y2="12"/>
  <line stroke="red" x1="16" y1="10" x2="17" y2="11"/>
  <line stroke="green" x1="16" y1="10" x2="18" y2="10"/>
  <line stroke="red" x1="14" y1="14" x2="12" y2="16"/>
  <line stroke="red" x1="14" y1="14" x2="16" y2="12"/>
  <line stroke="red" x1="14" y1="14" x2="16" y2="16"/>
  <line stroke="green" x1="12" y1="16" x2="12" y2="18"/>
  <line stroke="green" x1="12" y1="16" x2="16" y2="16"/>
  <line stroke="red" x1="12" y1="16" x2="14" y2="18"/>
  <line stroke="red" x1="16" y1="12" x2="17" y2="11"/>
  <line stroke="green" x1="16" y1="12" x2="18" y2="12"/>
  <line stroke="green" x1="16" y1="12" x2="16" y2="16"/>
  <line stroke="red" x1="16" y1="12" x2="18" y2="14"/>
  <line stroke="red" x1="17" y1="11" x2="18" y2="10"/>
  <line stroke="red" x1="17" y1="11" x2="18" y2="12"/>
  <line stroke="green" x1="18" y1="10" x2="18" y2="12"/>
  <line stroke="green" x1="12" y1="18" x2="12" y2="20"/>
  <line stroke="red" x1="12" y1="18" x2="8" y2="22"/>
  <line stroke="green" x1="18" y1="12" x2="20" y2="12"/>
  <line stroke="red" x1="18" y1="12" x2="22" y2="8"/>
  <line stroke="red" x1="16" y1="16" x2="14" y2="18"/>
  <line stroke="red" x1="16" y1="16" x2="18" y2="14"/>
  <line stroke="green" x1="16" y1="16" x2="16" y2="20"/>
  <line stroke="green" x1="16" y1="16" x2="20" y2="16"/>
  <line stroke="red" x1="16" y1="16" x2="22" y2="22"/>
  <line stroke="red" x1="14" y1="18" x2="12" y2="20"/>
  <line stroke="red" x1="14" y1="18" x2="16" y2="20"/>
  <line stroke="red" x1="18" y1="14" x2="20" y2="12"/>
  <line stroke="red" x1="18" y1="14" x2="20" y2="16"/>
  <line stroke="green" x1="12" y1="20" x2="12" y2="22"/>
  <line stroke="green" x1="12" y1="20" x2="16" y2="20"/>
  <line stroke="red" x1="12" y1="20" x2="14" y2="22"/>
  <line stroke="green" x1="20" y1="12" x2="22" y2="12"/>
  <line stroke="green" x1="20" y1="12" x2="20" y2="16"/>
  <line stroke="red" x1="20" y1="12" x2="22" y2="14"/>
  <line stroke="red" x1="16" y1="20" x2="14" y2="22"/>
  <line stroke="green" x1="16" y1="20" x2="16" y2="22"/>
  <line stroke="red" x1="20" y1="16" x2="22" y2="14"/>
  <line stroke="green" x1="20" y1="16" x2="22" y2="16"/>
</svg>""",
    grid_size=22,
)

SQUARE_FLAP = BoxPleatingCreasePatternExample(
    name="square_flap",
    grid_size=8,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8">
  <line stroke="red" x1="0" y1="0" x2="4" y2="4"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="8"/>
  <line stroke="black" x1="0" y1="0" x2="8" y2="0"/>
  <line stroke="red" x1="4" y1="4" x2="0" y2="8"/>
  <line stroke="red" x1="4" y1="4" x2="8" y2="0"/>
  <line stroke="red" x1="4" y1="4" x2="8" y2="8"/>
  <line stroke="black" x1="0" y1="8" x2="8" y2="8"/>
  <line stroke="black" x1="8" y1="0" x2="8" y2="8"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8">
  <line stroke="black" x1="0" y1="0" x2="0" y2="1"/>
  <line stroke="black" x1="0" y1="0" x2="1" y2="0"/>
  <line stroke="blue" x1="0" y1="0" x2="1" y2="1"/>
  <line stroke="red" x1="0" y1="1" x2="1" y2="1"/>
  <line stroke="black" x1="0" y1="1" x2="0" y2="2"/>
  <line stroke="red" x1="1" y1="0" x2="1" y2="1"/>
  <line stroke="black" x1="1" y1="0" x2="2" y2="0"/>
  <line stroke="red" x1="1" y1="1" x2="2" y2="2"/>
  <line stroke="blue" x1="0" y1="2" x2="2" y2="2"/>
  <line stroke="black" x1="0" y1="2" x2="0" y2="3"/>
  <line stroke="blue" x1="2" y1="0" x2="2" y2="2"/>
  <line stroke="black" x1="2" y1="0" x2="3" y2="0"/>
  <line stroke="blue" x1="2" y1="2" x2="3" y2="3"/>
  <line stroke="black" x1="0" y1="3" x2="0" y2="4"/>
  <line stroke="red" x1="0" y1="3" x2="3" y2="3"/>
  <line stroke="black" x1="3" y1="0" x2="4" y2="0"/>
  <line stroke="red" x1="3" y1="0" x2="3" y2="3"/>
  <line stroke="black" x1="0" y1="4" x2="0" y2="5"/>
  <line stroke="blue" x1="0" y1="4" x2="4" y2="4"/>
  <line stroke="black" x1="4" y1="0" x2="5" y2="0"/>
  <line stroke="red" x1="4" y1="0" x2="4" y2="4"/>
  <line stroke="red" x1="3" y1="3" x2="4" y2="4"/>
  <line stroke="red" x1="0" y1="5" x2="3" y2="5"/>
  <line stroke="black" x1="0" y1="5" x2="0" y2="6"/>
  <line stroke="red" x1="5" y1="0" x2="5" y2="3"/>
  <line stroke="black" x1="5" y1="0" x2="6" y2="0"/>
  <line stroke="red" x1="4" y1="4" x2="3" y2="5"/>
  <line stroke="red" x1="4" y1="4" x2="5" y2="3"/>
  <line stroke="red" x1="4" y1="4" x2="5" y2="5"/>
  <line stroke="blue" x1="4" y1="4" x2="4" y2="8"/>
  <line stroke="blue" x1="4" y1="4" x2="8" y2="4"/>
  <line stroke="blue" x1="3" y1="5" x2="2" y2="6"/>
  <line stroke="red" x1="3" y1="5" x2="3" y2="8"/>
  <line stroke="blue" x1="5" y1="3" x2="6" y2="2"/>
  <line stroke="red" x1="5" y1="3" x2="8" y2="3"/>
  <line stroke="blue" x1="0" y1="6" x2="2" y2="6"/>
  <line stroke="black" x1="0" y1="6" x2="0" y2="7"/>
  <line stroke="blue" x1="6" y1="0" x2="6" y2="2"/>
  <line stroke="black" x1="6" y1="0" x2="7" y2="0"/>
  <line stroke="red" x1="2" y1="6" x2="1" y2="7"/>
  <line stroke="blue" x1="2" y1="6" x2="2" y2="8"/>
  <line stroke="red" x1="6" y1="2" x2="7" y2="1"/>
  <line stroke="blue" x1="6" y1="2" x2="8" y2="2"/>
  <line stroke="red" x1="0" y1="7" x2="1" y2="7"/>
  <line stroke="black" x1="0" y1="7" x2="0" y2="8"/>
  <line stroke="red" x1="7" y1="0" x2="7" y2="1"/>
  <line stroke="black" x1="7" y1="0" x2="8" y2="0"/>
  <line stroke="blue" x1="1" y1="7" x2="0" y2="8"/>
  <line stroke="red" x1="1" y1="7" x2="1" y2="8"/>
  <line stroke="blue" x1="5" y1="5" x2="6" y2="6"/>
  <line stroke="red" x1="5" y1="5" x2="5" y2="8"/>
  <line stroke="red" x1="5" y1="5" x2="8" y2="5"/>
  <line stroke="blue" x1="7" y1="1" x2="8" y2="0"/>
  <line stroke="red" x1="7" y1="1" x2="8" y2="1"/>
  <line stroke="black" x1="0" y1="8" x2="1" y2="8"/>
  <line stroke="black" x1="8" y1="0" x2="8" y2="1"/>
  <line stroke="black" x1="1" y1="8" x2="2" y2="8"/>
  <line stroke="black" x1="8" y1="1" x2="8" y2="2"/>
  <line stroke="black" x1="2" y1="8" x2="3" y2="8"/>
  <line stroke="black" x1="8" y1="2" x2="8" y2="3"/>
  <line stroke="red" x1="6" y1="6" x2="7" y2="7"/>
  <line stroke="blue" x1="6" y1="6" x2="6" y2="8"/>
  <line stroke="blue" x1="6" y1="6" x2="8" y2="6"/>
  <line stroke="black" x1="3" y1="8" x2="4" y2="8"/>
  <line stroke="black" x1="8" y1="3" x2="8" y2="4"/>
  <line stroke="black" x1="4" y1="8" x2="5" y2="8"/>
  <line stroke="black" x1="8" y1="4" x2="8" y2="5"/>
  <line stroke="black" x1="5" y1="8" x2="6" y2="8"/>
  <line stroke="black" x1="8" y1="5" x2="8" y2="6"/>
  <line stroke="red" x1="7" y1="7" x2="7" y2="8"/>
  <line stroke="red" x1="7" y1="7" x2="8" y2="7"/>
  <line stroke="blue" x1="7" y1="7" x2="8" y2="8"/>
  <line stroke="black" x1="6" y1="8" x2="7" y2="8"/>
  <line stroke="black" x1="8" y1="6" x2="8" y2="7"/>
  <line stroke="black" x1="7" y1="8" x2="8" y2="8"/>
  <line stroke="black" x1="8" y1="7" x2="8" y2="8"/>
</svg>""",
)


WIDE_FLAPS = BoxPleatingCreasePatternExample(
    name="wide_flaps",
    grid_size=16,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <line stroke="red" x1="0" y1="0" x2="4" y2="4"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="8"/>
  <line stroke="black" x1="0" y1="0" x2="16" y2="0"/>
  <line stroke="red" x1="4" y1="4" x2="0" y2="8"/>
  <line stroke="red" x1="4" y1="4" x2="12" y2="4"/>
  <line stroke="red" x1="0" y1="8" x2="4" y2="12"/>
  <line stroke="black" x1="0" y1="8" x2="0" y2="16"/>
  <line stroke="blue" x1="0" y1="8" x2="16" y2="8"/>
  <line stroke="red" x1="4" y1="12" x2="0" y2="16"/>
  <line stroke="red" x1="4" y1="12" x2="12" y2="12"/>
  <line stroke="red" x1="12" y1="4" x2="16" y2="0"/>
  <line stroke="red" x1="12" y1="4" x2="16" y2="8"/>
  <line stroke="black" x1="0" y1="16" x2="16" y2="16"/>
  <line stroke="black" x1="16" y1="0" x2="16" y2="8"/>
  <line stroke="red" x1="12" y1="12" x2="16" y2="8"/>
  <line stroke="red" x1="12" y1="12" x2="16" y2="16"/>
  <line stroke="black" x1="16" y1="8" x2="16" y2="16"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <line stroke="black" x1="0" y1="0" x2="0" y2="1"/>
  <line stroke="black" x1="0" y1="0" x2="1" y2="0"/>
  <line stroke="blue" x1="0" y1="0" x2="1" y2="1"/>
  <line stroke="red" x1="0" y1="1" x2="1" y2="1"/>
  <line stroke="black" x1="0" y1="1" x2="0" y2="2"/>
  <line stroke="red" x1="1" y1="0" x2="1" y2="1"/>
  <line stroke="black" x1="1" y1="0" x2="2" y2="0"/>
  <line stroke="red" x1="1" y1="1" x2="2" y2="2"/>
  <line stroke="blue" x1="0" y1="2" x2="2" y2="2"/>
  <line stroke="black" x1="0" y1="2" x2="0" y2="3"/>
  <line stroke="blue" x1="2" y1="0" x2="2" y2="2"/>
  <line stroke="black" x1="2" y1="0" x2="3" y2="0"/>
  <line stroke="blue" x1="2" y1="2" x2="3" y2="3"/>
  <line stroke="black" x1="0" y1="3" x2="0" y2="4"/>
  <line stroke="red" x1="0" y1="3" x2="3" y2="3"/>
  <line stroke="black" x1="3" y1="0" x2="4" y2="0"/>
  <line stroke="red" x1="3" y1="0" x2="3" y2="3"/>
  <line stroke="black" x1="0" y1="4" x2="0" y2="5"/>
  <line stroke="blue" x1="0" y1="4" x2="4" y2="4"/>
  <line stroke="black" x1="4" y1="0" x2="5" y2="0"/>
  <line stroke="blue" x1="4" y1="0" x2="4" y2="4"/>
  <line stroke="red" x1="3" y1="3" x2="4" y2="4"/>
  <line stroke="red" x1="0" y1="5" x2="3" y2="5"/>
  <line stroke="black" x1="0" y1="5" x2="0" y2="6"/>
  <line stroke="black" x1="5" y1="0" x2="6" y2="0"/>
  <line stroke="red" x1="5" y1="0" x2="5" y2="4"/>
  <line stroke="red" x1="4" y1="4" x2="3" y2="5"/>
  <line stroke="blue" x1="4" y1="4" x2="5" y2="4"/>
  <line stroke="blue" x1="4" y1="4" x2="4" y2="12"/>
  <line stroke="blue" x1="3" y1="5" x2="2" y2="6"/>
  <line stroke="red" x1="3" y1="5" x2="3" y2="11"/>
  <line stroke="blue" x1="0" y1="6" x2="2" y2="6"/>
  <line stroke="black" x1="0" y1="6" x2="0" y2="7"/>
  <line stroke="black" x1="6" y1="0" x2="7" y2="0"/>
  <line stroke="blue" x1="6" y1="0" x2="6" y2="4"/>
  <line stroke="red" x1="2" y1="6" x2="1" y2="7"/>
  <line stroke="blue" x1="2" y1="6" x2="2" y2="10"/>
  <line stroke="red" x1="5" y1="4" x2="6" y2="4"/>
  <line stroke="red" x1="5" y1="4" x2="5" y2="12"/>
  <line stroke="red" x1="0" y1="7" x2="1" y2="7"/>
  <line stroke="black" x1="0" y1="7" x2="0" y2="8"/>
  <line stroke="black" x1="7" y1="0" x2="8" y2="0"/>
  <line stroke="red" x1="7" y1="0" x2="7" y2="4"/>
  <line stroke="blue" x1="1" y1="7" x2="0" y2="8"/>
  <line stroke="red" x1="1" y1="7" x2="1" y2="9"/>
  <line stroke="blue" x1="6" y1="4" x2="7" y2="4"/>
  <line stroke="blue" x1="6" y1="4" x2="6" y2="12"/>
  <line stroke="black" x1="0" y1="8" x2="0" y2="9"/>
  <line stroke="blue" x1="0" y1="8" x2="1" y2="9"/>
  <line stroke="red" x1="8" y1="0" x2="8" y2="4"/>
  <line stroke="black" x1="8" y1="0" x2="9" y2="0"/>
  <line stroke="red" x1="7" y1="4" x2="8" y2="4"/>
  <line stroke="red" x1="7" y1="4" x2="7" y2="12"/>
  <line stroke="red" x1="8" y1="4" x2="9" y2="4"/>
  <line stroke="blue" x1="8" y1="4" x2="8" y2="12"/>
  <line stroke="red" x1="0" y1="9" x2="1" y2="9"/>
  <line stroke="black" x1="0" y1="9" x2="0" y2="10"/>
  <line stroke="red" x1="9" y1="0" x2="9" y2="4"/>
  <line stroke="black" x1="9" y1="0" x2="10" y2="0"/>
  <line stroke="red" x1="1" y1="9" x2="2" y2="10"/>
  <line stroke="blue" x1="9" y1="4" x2="10" y2="4"/>
  <line stroke="red" x1="9" y1="4" x2="9" y2="12"/>
  <line stroke="blue" x1="0" y1="10" x2="2" y2="10"/>
  <line stroke="black" x1="0" y1="10" x2="0" y2="11"/>
  <line stroke="blue" x1="10" y1="0" x2="10" y2="4"/>
  <line stroke="black" x1="10" y1="0" x2="11" y2="0"/>
  <line stroke="blue" x1="2" y1="10" x2="3" y2="11"/>
  <line stroke="red" x1="10" y1="4" x2="11" y2="4"/>
  <line stroke="blue" x1="10" y1="4" x2="10" y2="12"/>
  <line stroke="red" x1="0" y1="11" x2="3" y2="11"/>
  <line stroke="black" x1="0" y1="11" x2="0" y2="12"/>
  <line stroke="red" x1="11" y1="0" x2="11" y2="4"/>
  <line stroke="black" x1="11" y1="0" x2="12" y2="0"/>
  <line stroke="red" x1="3" y1="11" x2="4" y2="12"/>
  <line stroke="blue" x1="11" y1="4" x2="12" y2="4"/>
  <line stroke="red" x1="11" y1="4" x2="11" y2="12"/>
  <line stroke="blue" x1="0" y1="12" x2="4" y2="12"/>
  <line stroke="black" x1="0" y1="12" x2="0" y2="13"/>
  <line stroke="blue" x1="12" y1="0" x2="12" y2="4"/>
  <line stroke="black" x1="12" y1="0" x2="13" y2="0"/>
  <line stroke="blue" x1="4" y1="12" x2="5" y2="12"/>
  <line stroke="red" x1="4" y1="12" x2="3" y2="13"/>
  <line stroke="blue" x1="4" y1="12" x2="4" y2="16"/>
  <line stroke="red" x1="12" y1="4" x2="13" y2="3"/>
  <line stroke="red" x1="12" y1="4" x2="13" y2="5"/>
  <line stroke="blue" x1="12" y1="4" x2="16" y2="4"/>
  <line stroke="blue" x1="12" y1="4" x2="12" y2="12"/>
  <line stroke="red" x1="0" y1="13" x2="3" y2="13"/>
  <line stroke="black" x1="0" y1="13" x2="0" y2="14"/>
  <line stroke="red" x1="13" y1="0" x2="13" y2="3"/>
  <line stroke="black" x1="13" y1="0" x2="14" y2="0"/>
  <line stroke="red" x1="5" y1="12" x2="6" y2="12"/>
  <line stroke="red" x1="5" y1="12" x2="5" y2="16"/>
  <line stroke="blue" x1="3" y1="13" x2="2" y2="14"/>
  <line stroke="red" x1="3" y1="13" x2="3" y2="16"/>
  <line stroke="blue" x1="13" y1="3" x2="14" y2="2"/>
  <line stroke="red" x1="13" y1="3" x2="16" y2="3"/>
  <line stroke="blue" x1="6" y1="12" x2="7" y2="12"/>
  <line stroke="blue" x1="6" y1="12" x2="6" y2="16"/>
  <line stroke="red" x1="7" y1="12" x2="8" y2="12"/>
  <line stroke="red" x1="7" y1="12" x2="7" y2="16"/>
  <line stroke="blue" x1="13" y1="5" x2="14" y2="6"/>
  <line stroke="red" x1="13" y1="5" x2="16" y2="5"/>
  <line stroke="red" x1="13" y1="5" x2="13" y2="11"/>
  <line stroke="blue" x1="0" y1="14" x2="2" y2="14"/>
  <line stroke="black" x1="0" y1="14" x2="0" y2="15"/>
  <line stroke="blue" x1="14" y1="0" x2="14" y2="2"/>
  <line stroke="black" x1="14" y1="0" x2="15" y2="0"/>
  <line stroke="red" x1="2" y1="14" x2="1" y2="15"/>
  <line stroke="blue" x1="2" y1="14" x2="2" y2="16"/>
  <line stroke="red" x1="14" y1="2" x2="15" y2="1"/>
  <line stroke="blue" x1="14" y1="2" x2="16" y2="2"/>
  <line stroke="red" x1="8" y1="12" x2="9" y2="12"/>
  <line stroke="red" x1="8" y1="12" x2="8" y2="16"/>
  <line stroke="blue" x1="9" y1="12" x2="10" y2="12"/>
  <line stroke="red" x1="9" y1="12" x2="9" y2="16"/>
  <line stroke="red" x1="0" y1="15" x2="1" y2="15"/>
  <line stroke="black" x1="0" y1="15" x2="0" y2="16"/>
  <line stroke="red" x1="15" y1="0" x2="15" y2="1"/>
  <line stroke="black" x1="15" y1="0" x2="16" y2="0"/>
  <line stroke="blue" x1="1" y1="15" x2="0" y2="16"/>
  <line stroke="red" x1="1" y1="15" x2="1" y2="16"/>
  <line stroke="blue" x1="15" y1="1" x2="16" y2="0"/>
  <line stroke="red" x1="15" y1="1" x2="16" y2="1"/>
  <line stroke="red" x1="14" y1="6" x2="15" y2="7"/>
  <line stroke="blue" x1="14" y1="6" x2="16" y2="6"/>
  <line stroke="blue" x1="14" y1="6" x2="14" y2="10"/>
  <line stroke="red" x1="10" y1="12" x2="11" y2="12"/>
  <line stroke="blue" x1="10" y1="12" x2="10" y2="16"/>
  <line stroke="black" x1="0" y1="16" x2="1" y2="16"/>
  <line stroke="black" x1="16" y1="0" x2="16" y2="1"/>
  <line stroke="black" x1="1" y1="16" x2="2" y2="16"/>
  <line stroke="black" x1="16" y1="1" x2="16" y2="2"/>
  <line stroke="black" x1="2" y1="16" x2="3" y2="16"/>
  <line stroke="black" x1="16" y1="2" x2="16" y2="3"/>
  <line stroke="black" x1="3" y1="16" x2="4" y2="16"/>
  <line stroke="black" x1="16" y1="3" x2="16" y2="4"/>
  <line stroke="blue" x1="11" y1="12" x2="12" y2="12"/>
  <line stroke="red" x1="11" y1="12" x2="11" y2="16"/>
  <line stroke="black" x1="4" y1="16" x2="5" y2="16"/>
  <line stroke="black" x1="16" y1="4" x2="16" y2="5"/>
  <line stroke="red" x1="15" y1="7" x2="16" y2="7"/>
  <line stroke="red" x1="15" y1="7" x2="15" y2="9"/>
  <line stroke="blue" x1="15" y1="7" x2="16" y2="8"/>
  <line stroke="black" x1="5" y1="16" x2="6" y2="16"/>
  <line stroke="black" x1="16" y1="5" x2="16" y2="6"/>
  <line stroke="red" x1="12" y1="12" x2="13" y2="11"/>
  <line stroke="red" x1="12" y1="12" x2="13" y2="13"/>
  <line stroke="blue" x1="12" y1="12" x2="12" y2="16"/>
  <line stroke="blue" x1="12" y1="12" x2="16" y2="12"/>
  <line stroke="blue" x1="13" y1="11" x2="14" y2="10"/>
  <line stroke="red" x1="13" y1="11" x2="16" y2="11"/>
  <line stroke="black" x1="6" y1="16" x2="7" y2="16"/>
  <line stroke="black" x1="16" y1="6" x2="16" y2="7"/>
  <line stroke="red" x1="14" y1="10" x2="15" y2="9"/>
  <line stroke="blue" x1="14" y1="10" x2="16" y2="10"/>
  <line stroke="black" x1="7" y1="16" x2="8" y2="16"/>
  <line stroke="black" x1="16" y1="7" x2="16" y2="8"/>
  <line stroke="blue" x1="15" y1="9" x2="16" y2="8"/>
  <line stroke="red" x1="15" y1="9" x2="16" y2="9"/>
  <line stroke="black" x1="8" y1="16" x2="9" y2="16"/>
  <line stroke="black" x1="16" y1="8" x2="16" y2="9"/>
  <line stroke="black" x1="9" y1="16" x2="10" y2="16"/>
  <line stroke="black" x1="16" y1="9" x2="16" y2="10"/>
  <line stroke="blue" x1="13" y1="13" x2="14" y2="14"/>
  <line stroke="red" x1="13" y1="13" x2="13" y2="16"/>
  <line stroke="red" x1="13" y1="13" x2="16" y2="13"/>
  <line stroke="black" x1="10" y1="16" x2="11" y2="16"/>
  <line stroke="black" x1="16" y1="10" x2="16" y2="11"/>
  <line stroke="black" x1="11" y1="16" x2="12" y2="16"/>
  <line stroke="black" x1="16" y1="11" x2="16" y2="12"/>
  <line stroke="red" x1="14" y1="14" x2="15" y2="15"/>
  <line stroke="blue" x1="14" y1="14" x2="14" y2="16"/>
  <line stroke="blue" x1="14" y1="14" x2="16" y2="14"/>
  <line stroke="black" x1="12" y1="16" x2="13" y2="16"/>
  <line stroke="black" x1="16" y1="12" x2="16" y2="13"/>
  <line stroke="black" x1="13" y1="16" x2="14" y2="16"/>
  <line stroke="black" x1="16" y1="13" x2="16" y2="14"/>
  <line stroke="red" x1="15" y1="15" x2="15" y2="16"/>
  <line stroke="red" x1="15" y1="15" x2="16" y2="15"/>
  <line stroke="blue" x1="15" y1="15" x2="16" y2="16"/>
  <line stroke="black" x1="14" y1="16" x2="15" y2="16"/>
  <line stroke="black" x1="16" y1="14" x2="16" y2="15"/>
  <line stroke="black" x1="15" y1="16" x2="16" y2="16"/>
  <line stroke="black" x1="16" y1="15" x2="16" y2="16"/>
</svg>""",
)

SIMPLE_RIVER = BoxPleatingCreasePatternExample(  # pylint: disable=invalid-name
    name="simple_river",
    grid_size=4,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="0" y2="250"/>
  <line stroke="black" x1="0" y1="0" x2="1000" y2="0"/>
  <line stroke="black" x1="0" y1="250" x2="0" y2="750"/>
  <line stroke="green" x1="0" y1="250" x2="1000" y2="250"/>
  <line stroke="black" x1="0" y1="750" x2="0" y2="1000"/>
  <line stroke="green" x1="0" y1="750" x2="1000" y2="750"/>
  <line stroke="black" x1="0" y1="1000" x2="1000" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="250"/>
  <line stroke="black" x1="1000" y1="250" x2="1000" y2="750"/>
  <line stroke="black" x1="1000" y1="750" x2="1000" y2="1000"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="250" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="1000"/>
  <line stroke="black" x1="250" y1="0" x2="500" y2="0"/>
  <line stroke="red" x1="250" y1="0" x2="250" y2="1000"/>
  <line stroke="black" x1="500" y1="0" x2="750" y2="0"/>
  <line stroke="blue" x1="500" y1="0" x2="500" y2="1000"/>
  <line stroke="black" x1="750" y1="0" x2="1000" y2="0"/>
  <line stroke="red" x1="750" y1="0" x2="750" y2="1000"/>
  <line stroke="black" x1="0" y1="1000" x2="250" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="1000"/>
  <line stroke="black" x1="250" y1="1000" x2="500" y2="1000"/>
  <line stroke="black" x1="500" y1="1000" x2="750" y2="1000"/>
  <line stroke="black" x1="750" y1="1000" x2="1000" y2="1000"/>
</svg>""",
)

ONE_KAWASAKI_VIOLATION = BoxPleatingCreasePatternExample(
    name="one_kawasaki_violation",
    packing_svg="",
    grid_size=4,
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4 4">
  <line stroke="black" x1="0" y1="0" x2="0" y2="2"/>
  <line stroke="black" x1="0" y1="0" x2="4" y2="0"/>
  <line stroke="red" x1="0" y1="2" x2="2" y2="2"/>
  <line stroke="black" x1="0" y1="2" x2="0" y2="4"/>
  <line stroke="blue" x1="2" y1="2" x2="4" y2="0"/>
  <line stroke="red" x1="2" y1="2" x2="2" y2="4"/>
  <line stroke="red" x1="2" y1="2" x2="4" y2="2"/>
  <line stroke="black" x1="0" y1="4" x2="2" y2="4"/>
  <line stroke="black" x1="4" y1="0" x2="4" y2="2"/>
  <line stroke="black" x1="2" y1="4" x2="4" y2="4"/>
  <line stroke="black" x1="4" y1="2" x2="4" y2="4"/>
</svg>""",
)

FOUR_KAWASAKI_VIOLATIONS = BoxPleatingCreasePatternExample(
    name="four_kawasaki_violations",
    packing_svg="",
    grid_size=8,
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="0" y2="250"/>
  <line stroke="black" x1="0" y1="0" x2="250" y2="0"/>
  <line stroke="red" x1="0" y1="250" x2="250" y2="250"/>
  <line stroke="black" x1="0" y1="250" x2="0" y2="500"/>
  <line stroke="blue" x1="250" y1="0" x2="250" y2="250"/>
  <line stroke="black" x1="250" y1="0" x2="750" y2="0"/>
  <line stroke="red" x1="250" y1="250" x2="250" y2="625"/>
  <line stroke="red" x1="250" y1="250" x2="750" y2="250"/>
  <line stroke="blue" x1="0" y1="500" x2="250" y2="625"/>
  <line stroke="black" x1="0" y1="500" x2="0" y2="750"/>
  <line stroke="blue" x1="250" y1="625" x2="625" y2="625"/>
  <line stroke="blue" x1="250" y1="625" x2="250" y2="875"/>
  <line stroke="red" x1="0" y1="750" x2="250" y2="875"/>
  <line stroke="black" x1="0" y1="750" x2="0" y2="1000"/>
  <line stroke="blue" x1="750" y1="0" x2="750" y2="250"/>
  <line stroke="black" x1="750" y1="0" x2="1000" y2="0"/>
  <line stroke="red" x1="750" y1="250" x2="625" y2="625"/>
  <line stroke="red" x1="750" y1="250" x2="1000" y2="250"/>
  <line stroke="blue" x1="625" y1="625" x2="1000" y2="500"/>
  <line stroke="blue" x1="625" y1="625" x2="750" y2="875"/>
  <line stroke="red" x1="250" y1="875" x2="250" y2="1000"/>
  <line stroke="red" x1="250" y1="875" x2="750" y2="875"/>
  <line stroke="black" x1="0" y1="1000" x2="250" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="250"/>
  <line stroke="black" x1="250" y1="1000" x2="750" y2="1000"/>
  <line stroke="black" x1="1000" y1="250" x2="1000" y2="500"/>
  <line stroke="black" x1="1000" y1="500" x2="1000" y2="750"/>
  <line stroke="red" x1="750" y1="875" x2="750" y2="1000"/>
  <line stroke="red" x1="750" y1="875" x2="1000" y2="750"/>
  <line stroke="black" x1="750" y1="1000" x2="1000" y2="1000"/>
  <line stroke="black" x1="1000" y1="750" x2="1000" y2="1000"/>
</svg>""",
)

VALUTED_CANOPY = BoxPleatingCreasePatternExample(
    name="vaulted_canopy",
    grid_size=16,
    stick_figure=stick_figure_utils.StickFigure.from_dict({
        "name": "Vaulted Canopy",
        "category": "architecture and buildings",
        "complexity": 2,
        "root": "central_apex_post",
        "children": [
            {
                "name": "central_apex_post",
                "start": "ground_center",
                "end": "apex_point",
                "azimuth_angle": 0,
                "elevation_angle": 90,
                "length": 3,
                "width": 2,
                "shaping_flap": False,
            },
            {
                "name": "vault_rib_front_right_pillar_front_right",
                "start": "apex_point",
                "end": "ground_front_right_base",
                "azimuth_angle": 44.99999999999999,
                "elevation_angle": -57.805499962050625,
                "length": 5,
                "width": 1,
                "shaping_flap": False,
            },
            {
                "name": "vault_rib_front_left_pillar_front_left",
                "start": "apex_point",
                "end": "ground_front_left_base",
                "azimuth_angle": 135.0,
                "elevation_angle": -57.80549996205064,
                "length": 5,
                "width": 1,
                "shaping_flap": False,
            },
            {
                "name": "vault_rib_rear_left_pillar_rear_left",
                "start": "apex_point",
                "end": "ground_rear_left_base",
                "azimuth_angle": -135.0,
                "elevation_angle": -57.80549996205064,
                "length": 5,
                "width": 1,
                "shaping_flap": False,
            },
            {
                "name": "vault_rib_rear_right_pillar_rear_right",
                "start": "apex_point",
                "end": "ground_rear_right_base",
                "azimuth_angle": -44.99999999999999,
                "elevation_angle": -57.805499962050625,
                "length": 5,
                "width": 1,
                "shaping_flap": False,
            },
        ],
        "shaping_flaps_limit": 0,
    }),
    unmerged_stick_figure=stick_figure_utils.StickFigure.from_dict({
        "name": "Vaulted Canopy",
        "category": "architecture and buildings",
        "complexity": 2,
        "root": "central_apex_post",
        "children": [
            {
                "name": "central_apex_post",
                "start": "ground_center",
                "end": "apex_point",
                "azimuth_angle": 0,
                "elevation_angle": 90,
                "length": 3,
                "width": 2,
                "shaping_flap": False,
            },
            {
                "name": "vault_rib_front_right",
                "start": "apex_point",
                "end": "pillar_front_right_top",
                "azimuth_angle": 45,
                "elevation_angle": -37,
                "length": 3,
                "width": 1,
                "shaping_flap": False,
            },
            {
                "name": "vault_rib_front_left",
                "start": "apex_point",
                "end": "pillar_front_left_top",
                "azimuth_angle": 135,
                "elevation_angle": -37,
                "length": 3,
                "width": 1,
                "shaping_flap": False,
            },
            {
                "name": "vault_rib_rear_left",
                "start": "apex_point",
                "end": "pillar_rear_left_top",
                "azimuth_angle": 225,
                "elevation_angle": -37,
                "length": 3,
                "width": 1,
                "shaping_flap": False,
            },
            {
                "name": "vault_rib_rear_right",
                "start": "apex_point",
                "end": "pillar_rear_right_top",
                "azimuth_angle": 315,
                "elevation_angle": -37,
                "length": 3,
                "width": 1,
                "shaping_flap": False,
            },
            {
                "name": "pillar_front_right",
                "start": "pillar_front_right_top",
                "end": "ground_front_right_base",
                "azimuth_angle": 0,
                "elevation_angle": -90,
                "length": 2,
                "width": 1,
                "shaping_flap": False,
            },
            {
                "name": "pillar_front_left",
                "start": "pillar_front_left_top",
                "end": "ground_front_left_base",
                "azimuth_angle": 0,
                "elevation_angle": -90,
                "length": 2,
                "width": 1,
                "shaping_flap": False,
            },
            {
                "name": "pillar_rear_left",
                "start": "pillar_rear_left_top",
                "end": "ground_rear_left_base",
                "azimuth_angle": 0,
                "elevation_angle": -90,
                "length": 2,
                "width": 1,
                "shaping_flap": False,
            },
            {
                "name": "pillar_rear_right",
                "start": "pillar_rear_right_top",
                "end": "ground_rear_right_base",
                "azimuth_angle": 0,
                "elevation_angle": -90,
                "length": 2,
                "width": 1,
                "shaping_flap": False,
            },
        ],
        "shaping_flaps_limit": 0,
    }),
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
<line stroke="black" x1="0" y1="0" x2="312" y2="0"/>
<line stroke="black" x1="0" y1="0" x2="0" y2="375"/>
<line stroke="black" x1="312" y1="0" x2="500" y2="0"/>
<line stroke="green" x1="312" y1="0" x2="312" y2="688"/>
<line stroke="black" x1="0" y1="375" x2="0" y2="688"/>
<line stroke="red" x1="0" y1="375" x2="312" y2="688"/>
<line stroke="black" x1="500" y1="0" x2="688" y2="0"/>
<line stroke="red" x1="500" y1="0" x2="500" y2="1000"/>
<line stroke="green" x1="0" y1="688" x2="312" y2="688"/>
<line stroke="black" x1="0" y1="688" x2="0" y2="1000"/>
<line stroke="green" x1="688" y1="0" x2="688" y2="688"/>
<line stroke="black" x1="688" y1="0" x2="1000" y2="0"/>
<line stroke="red" x1="312" y1="688" x2="0" y2="1000"/>
<line stroke="green" x1="312" y1="688" x2="312" y2="1000"/>
<line stroke="red" x1="688" y1="688" x2="1000" y2="375"/>
<line stroke="green" x1="688" y1="688" x2="688" y2="1000"/>
<line stroke="green" x1="688" y1="688" x2="1000" y2="688"/>
<line stroke="red" x1="688" y1="688" x2="1000" y2="1000"/>
<line stroke="black" x1="0" y1="1000" x2="312" y2="1000"/>
<line stroke="black" x1="1000" y1="0" x2="1000" y2="375"/>
<line stroke="black" x1="312" y1="1000" x2="500" y2="1000"/>
<line stroke="black" x1="1000" y1="375" x2="1000" y2="688"/>
<line stroke="black" x1="500" y1="1000" x2="688" y2="1000"/>
<line stroke="black" x1="688" y1="1000" x2="1000" y2="1000"/>
<line stroke="black" x1="1000" y1="688" x2="1000" y2="1000"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
<line stroke="black" x1="0" y1="0" x2="0" y2="62"/>
<line stroke="black" x1="0" y1="0" x2="500" y2="0"/>
<line stroke="black" x1="0" y1="62" x2="0" y2="125"/>
<line stroke="red" x1="0" y1="62" x2="500" y2="62"/>
<line stroke="black" x1="0" y1="125" x2="0" y2="188"/>
<line stroke="blue" x1="0" y1="125" x2="500" y2="125"/>
<line stroke="black" x1="0" y1="188" x2="0" y2="250"/>
<line stroke="red" x1="0" y1="188" x2="500" y2="188"/>
<line stroke="black" x1="0" y1="250" x2="0" y2="312"/>
<line stroke="blue" x1="0" y1="250" x2="500" y2="250"/>
<line stroke="black" x1="0" y1="312" x2="0" y2="375"/>
<line stroke="red" x1="0" y1="312" x2="500" y2="312"/>
<line stroke="red" x1="0" y1="375" x2="62" y2="438"/>
<line stroke="blue" x1="0" y1="375" x2="500" y2="375"/>
<line stroke="black" x1="0" y1="375" x2="0" y2="688"/>
<line stroke="blue" x1="62" y1="438" x2="125" y2="500"/>
<line stroke="red" x1="62" y1="438" x2="500" y2="438"/>
<line stroke="red" x1="62" y1="438" x2="62" y2="688"/>
<line stroke="blue" x1="500" y1="0" x2="500" y2="62"/>
<line stroke="black" x1="500" y1="0" x2="1000" y2="0"/>
<line stroke="red" x1="500" y1="62" x2="500" y2="125"/>
<line stroke="red" x1="500" y1="62" x2="1000" y2="62"/>
<line stroke="red" x1="125" y1="500" x2="188" y2="562"/>
<line stroke="blue" x1="125" y1="500" x2="125" y2="688"/>
<line stroke="blue" x1="125" y1="500" x2="500" y2="500"/>
<line stroke="blue" x1="500" y1="125" x2="500" y2="188"/>
<line stroke="blue" x1="500" y1="125" x2="1000" y2="125"/>
<line stroke="red" x1="500" y1="188" x2="500" y2="250"/>
<line stroke="red" x1="500" y1="188" x2="1000" y2="188"/>
<line stroke="blue" x1="500" y1="250" x2="500" y2="312"/>
<line stroke="blue" x1="500" y1="250" x2="1000" y2="250"/>
<line stroke="red" x1="500" y1="312" x2="500" y2="375"/>
<line stroke="red" x1="500" y1="312" x2="1000" y2="312"/>
<line stroke="blue" x1="188" y1="562" x2="250" y2="625"/>
<line stroke="red" x1="188" y1="562" x2="188" y2="688"/>
<line stroke="red" x1="188" y1="562" x2="500" y2="562"/>
<line stroke="blue" x1="500" y1="375" x2="500" y2="438"/>
<line stroke="blue" x1="500" y1="375" x2="1000" y2="375"/>
<line stroke="red" x1="500" y1="438" x2="500" y2="500"/>
<line stroke="red" x1="500" y1="438" x2="938" y2="438"/>
<line stroke="blue" x1="250" y1="625" x2="250" y2="688"/>
<line stroke="red" x1="250" y1="625" x2="312" y2="688"/>
<line stroke="blue" x1="250" y1="625" x2="500" y2="625"/>
<line stroke="blue" x1="0" y1="688" x2="62" y2="688"/>
<line stroke="black" x1="0" y1="688" x2="0" y2="1000"/>
<line stroke="red" x1="62" y1="688" x2="125" y2="688"/>
<line stroke="red" x1="62" y1="688" x2="62" y2="938"/>
<line stroke="blue" x1="125" y1="688" x2="188" y2="688"/>
<line stroke="blue" x1="125" y1="688" x2="125" y2="875"/>
<line stroke="blue" x1="500" y1="500" x2="500" y2="562"/>
<line stroke="blue" x1="500" y1="500" x2="875" y2="500"/>
<line stroke="red" x1="188" y1="688" x2="250" y2="688"/>
<line stroke="red" x1="188" y1="688" x2="188" y2="812"/>
<line stroke="blue" x1="250" y1="688" x2="312" y2="688"/>
<line stroke="blue" x1="250" y1="688" x2="250" y2="750"/>
<line stroke="red" x1="500" y1="562" x2="500" y2="625"/>
<line stroke="red" x1="500" y1="562" x2="812" y2="562"/>
<line stroke="red" x1="312" y1="688" x2="250" y2="750"/>
<line stroke="red" x1="312" y1="688" x2="500" y2="688"/>
<line stroke="blue" x1="250" y1="750" x2="188" y2="812"/>
<line stroke="blue" x1="250" y1="750" x2="500" y2="750"/>
<line stroke="blue" x1="500" y1="625" x2="500" y2="688"/>
<line stroke="blue" x1="500" y1="625" x2="750" y2="625"/>
<line stroke="red" x1="188" y1="812" x2="125" y2="875"/>
<line stroke="red" x1="188" y1="812" x2="500" y2="812"/>
<line stroke="red" x1="500" y1="688" x2="500" y2="750"/>
<line stroke="red" x1="500" y1="688" x2="688" y2="688"/>
<line stroke="blue" x1="125" y1="875" x2="62" y2="938"/>
<line stroke="blue" x1="125" y1="875" x2="500" y2="875"/>
<line stroke="blue" x1="500" y1="750" x2="500" y2="812"/>
<line stroke="blue" x1="500" y1="750" x2="750" y2="750"/>
<line stroke="red" x1="62" y1="938" x2="0" y2="1000"/>
<line stroke="red" x1="62" y1="938" x2="500" y2="938"/>
<line stroke="red" x1="500" y1="812" x2="500" y2="875"/>
<line stroke="red" x1="500" y1="812" x2="812" y2="812"/>
<line stroke="red" x1="688" y1="688" x2="750" y2="625"/>
<line stroke="blue" x1="688" y1="688" x2="750" y2="688"/>
<line stroke="red" x1="688" y1="688" x2="750" y2="750"/>
<line stroke="blue" x1="750" y1="625" x2="812" y2="562"/>
<line stroke="blue" x1="750" y1="625" x2="750" y2="688"/>
<line stroke="red" x1="812" y1="562" x2="875" y2="500"/>
<line stroke="red" x1="812" y1="562" x2="812" y2="688"/>
<line stroke="black" x1="0" y1="1000" x2="500" y2="1000"/>
<line stroke="black" x1="1000" y1="0" x2="1000" y2="62"/>
<line stroke="black" x1="1000" y1="62" x2="1000" y2="125"/>
<line stroke="blue" x1="500" y1="875" x2="500" y2="938"/>
<line stroke="blue" x1="500" y1="875" x2="875" y2="875"/>
<line stroke="blue" x1="875" y1="500" x2="938" y2="438"/>
<line stroke="blue" x1="875" y1="500" x2="875" y2="688"/>
<line stroke="black" x1="1000" y1="125" x2="1000" y2="188"/>
<line stroke="blue" x1="750" y1="688" x2="750" y2="750"/>
<line stroke="red" x1="750" y1="688" x2="812" y2="688"/>
<line stroke="black" x1="1000" y1="188" x2="1000" y2="250"/>
<line stroke="black" x1="1000" y1="250" x2="1000" y2="312"/>
<line stroke="red" x1="938" y1="438" x2="1000" y2="375"/>
<line stroke="red" x1="938" y1="438" x2="938" y2="688"/>
<line stroke="black" x1="1000" y1="312" x2="1000" y2="375"/>
<line stroke="blue" x1="750" y1="750" x2="812" y2="812"/>
<line stroke="red" x1="500" y1="938" x2="500" y2="1000"/>
<line stroke="red" x1="500" y1="938" x2="938" y2="938"/>
<line stroke="blue" x1="812" y1="688" x2="875" y2="688"/>
<line stroke="red" x1="812" y1="688" x2="812" y2="812"/>
<line stroke="black" x1="1000" y1="375" x2="1000" y2="688"/>
<line stroke="red" x1="875" y1="688" x2="938" y2="688"/>
<line stroke="blue" x1="875" y1="688" x2="875" y2="875"/>
<line stroke="black" x1="500" y1="1000" x2="1000" y2="1000"/>
<line stroke="red" x1="812" y1="812" x2="875" y2="875"/>
<line stroke="blue" x1="938" y1="688" x2="1000" y2="688"/>
<line stroke="red" x1="938" y1="688" x2="938" y2="938"/>
<line stroke="black" x1="1000" y1="688" x2="1000" y2="1000"/>
<line stroke="blue" x1="875" y1="875" x2="938" y2="938"/>
<line stroke="red" x1="938" y1="938" x2="1000" y2="1000"/>
</svg>""",
)

DOVE = BoxPleatingCreasePatternExample(
    name="dove",
    grid_size=8,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8">
  <rect stroke="black" x="0" y="0" width="8" height="8"/>
  <line stroke="red" x1="0" y1="2" x2="2" y2="4"/>
  <line stroke="green" x1="2" y1="0" x2="2" y2="4"/>
  <line stroke="green" x1="0" y1="4" x2="2" y2="4"/>
  <line stroke="red" x1="4" y1="0" x2="4" y2="2"/>
  <line stroke="red" x1="2" y1="4" x2="4" y2="2"/>
  <line stroke="green" x1="2" y1="4" x2="6" y2="4"/>
  <line stroke="red" x1="4" y1="2" x2="6" y2="4"/>
  <line stroke="green" x1="0" y1="6" x2="2" y2="6"/>
  <line stroke="green" x1="6" y1="0" x2="6" y2="4"/>
  <line stroke="red" x1="2" y1="6" x2="0" y2="8"/>
  <line stroke="green" x1="2" y1="6" x2="2" y2="8"/>
  <line stroke="green" x1="2" y1="6" x2="6" y2="6"/>
  <line stroke="red" x1="2" y1="6" x2="4" y2="8"/>
  <line stroke="red" x1="6" y1="4" x2="8" y2="2"/>
  <line stroke="green" x1="6" y1="4" x2="8" y2="4"/>
  <line stroke="red" x1="6" y1="6" x2="4" y2="8"/>
  <line stroke="green" x1="6" y1="6" x2="6" y2="8"/>
  <line stroke="green" x1="6" y1="6" x2="8" y2="6"/>
  <line stroke="red" x1="6" y1="6" x2="8" y2="8"/>
</svg>""",
    central_crease_removed=False,
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8">
  <rect stroke="black" x="0" y="0" width="8" height="8"/>
  <line stroke="blue" x1="0" y1="1" x2="2" y2="1"/>
  <line stroke="red" x1="0" y1="2" x2="2" y2="2"/>
  <line stroke="blue" x1="0" y1="2" x2="1" y2="3"/>
  <line stroke="red" x1="2" y1="0" x2="2" y2="1"/>
  <line stroke="blue" x1="2" y1="1" x2="2" y2="2"/>
  <line stroke="blue" x1="2" y1="1" x2="4" y2="1"/>
  <line stroke="red" x1="2" y1="2" x2="2" y2="3"/>
  <line stroke="red" x1="2" y1="2" x2="4" y2="2"/>
  <line stroke="blue" x1="1" y1="3" x2="2" y2="3"/>
  <line stroke="red" x1="1" y1="3" x2="2" y2="4"/>
  <line stroke="blue" x1="1" y1="3" x2="1" y2="7"/>
  <line stroke="blue" x1="2" y1="3" x2="3" y2="3"/>
  <line stroke="blue" x1="2" y1="3" x2="2" y2="4"/>
  <line stroke="blue" x1="4" y1="0" x2="4" y2="1"/>
  <line stroke="red" x1="4" y1="1" x2="4" y2="2"/>
  <line stroke="blue" x1="4" y1="1" x2="6" y2="1"/>
  <line stroke="red" x1="3" y1="3" x2="2" y2="4"/>
  <line stroke="blue" x1="3" y1="3" x2="4" y2="2"/>
  <line stroke="blue" x1="3" y1="3" x2="3" y2="7"/>
  <line stroke="red" x1="2" y1="4" x2="2" y2="6"/>
  <line stroke="blue" x1="4" y1="2" x2="5" y2="3"/>
  <line stroke="red" x1="4" y1="2" x2="6" y2="2"/>
  <line stroke="red" x1="4" y1="2" x2="4" y2="8"/>
  <line stroke="blue" x1="5" y1="3" x2="6" y2="3"/>
  <line stroke="red" x1="5" y1="3" x2="6" y2="4"/>
  <line stroke="blue" x1="5" y1="3" x2="5" y2="7"/>
  <line stroke="red" x1="6" y1="0" x2="6" y2="1"/>
  <line stroke="blue" x1="6" y1="1" x2="6" y2="2"/>
  <line stroke="blue" x1="6" y1="1" x2="8" y2="1"/>
  <line stroke="red" x1="2" y1="6" x2="1" y2="7"/>
  <line stroke="blue" x1="2" y1="6" x2="2" y2="7"/>
  <line stroke="red" x1="2" y1="6" x2="3" y2="7"/>
  <line stroke="red" x1="6" y1="2" x2="6" y2="3"/>
  <line stroke="red" x1="6" y1="2" x2="8" y2="2"/>
  <line stroke="blue" x1="6" y1="3" x2="6" y2="4"/>
  <line stroke="blue" x1="6" y1="3" x2="7" y2="3"/>
  <line stroke="blue" x1="1" y1="7" x2="2" y2="7"/>
  <line stroke="blue" x1="1" y1="7" x2="0" y2="8"/>
  <line stroke="red" x1="6" y1="4" x2="7" y2="3"/>
  <line stroke="red" x1="6" y1="4" x2="6" y2="6"/>
  <line stroke="blue" x1="2" y1="7" x2="3" y2="7"/>
  <line stroke="red" x1="2" y1="7" x2="2" y2="8"/>
  <line stroke="blue" x1="3" y1="7" x2="4" y2="8"/>
  <line stroke="blue" x1="7" y1="3" x2="8" y2="2"/>
  <line stroke="blue" x1="7" y1="3" x2="7" y2="7"/>
  <line stroke="red" x1="6" y1="6" x2="5" y2="7"/>
  <line stroke="blue" x1="6" y1="6" x2="6" y2="7"/>
  <line stroke="red" x1="6" y1="6" x2="7" y2="7"/>
  <line stroke="blue" x1="5" y1="7" x2="4" y2="8"/>
  <line stroke="blue" x1="5" y1="7" x2="6" y2="7"/>
  <line stroke="blue" x1="6" y1="7" x2="7" y2="7"/>
  <line stroke="red" x1="6" y1="7" x2="6" y2="8"/>
  <line stroke="blue" x1="7" y1="7" x2="8" y2="8"/>
</svg>""",
)

BASIC_NARROW_45_ZIGZAG_BASE = BoxPleatingCreasePatternExample(
    name="basic_narrow_45_zigzag",
    packing_svg="",
    grid_size=4,
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="250" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="500"/>
  <line stroke="red" x1="250" y1="0" x2="250" y2="250"/>
  <line stroke="black" x1="250" y1="0" x2="500" y2="0"/>
  <line stroke="red" x1="250" y1="250" x2="0" y2="500"/>
  <line stroke="blue" x1="250" y1="250" x2="500" y2="500"/>
  <line stroke="red" x1="250" y1="250" x2="250" y2="1000"/>
  <line stroke="black" x1="0" y1="500" x2="0" y2="1000"/>
  <line stroke="blue" x1="500" y1="0" x2="500" y2="500"/>
  <line stroke="black" x1="500" y1="0" x2="750" y2="0"/>
  <line stroke="red" x1="500" y1="500" x2="750" y2="250"/>
  <line stroke="blue" x1="500" y1="500" x2="500" y2="1000"/>
  <line stroke="red" x1="750" y1="0" x2="750" y2="250"/>
  <line stroke="black" x1="750" y1="0" x2="1000" y2="0"/>
  <line stroke="blue" x1="750" y1="250" x2="1000" y2="500"/>
  <line stroke="red" x1="750" y1="250" x2="750" y2="1000"/>
  <line stroke="black" x1="0" y1="1000" x2="250" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="500"/>
  <line stroke="black" x1="250" y1="1000" x2="500" y2="1000"/>
  <line stroke="black" x1="500" y1="1000" x2="750" y2="1000"/>
  <line stroke="black" x1="1000" y1="500" x2="1000" y2="1000"/>
  <line stroke="black" x1="750" y1="1000" x2="1000" y2="1000"/>
</svg>""",
)

BASIC_NARROW_22P5_ZIGZAG_BASE = BoxPleatingCreasePatternExample(
    name="basic_narrow_22p5_zigzag",
    packing_svg="",
    grid_size=4,
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="250" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="500"/>
  <line stroke="red" x1="250" y1="0" x2="250" y2="375"/>
  <line stroke="black" x1="250" y1="0" x2="500" y2="0"/>
  <line stroke="red" x1="250" y1="375" x2="0" y2="500"/>
  <line stroke="blue" x1="250" y1="375" x2="500" y2="500"/>
  <line stroke="red" x1="250" y1="375" x2="250" y2="1000"/>
  <line stroke="black" x1="0" y1="500" x2="0" y2="1000"/>
  <line stroke="blue" x1="500" y1="0" x2="500" y2="500"/>
  <line stroke="black" x1="500" y1="0" x2="750" y2="0"/>
  <line stroke="red" x1="500" y1="500" x2="750" y2="375"/>
  <line stroke="blue" x1="500" y1="500" x2="500" y2="1000"/>
  <line stroke="red" x1="750" y1="0" x2="750" y2="375"/>
  <line stroke="black" x1="750" y1="0" x2="1000" y2="0"/>
  <line stroke="blue" x1="750" y1="375" x2="1000" y2="500"/>
  <line stroke="red" x1="750" y1="375" x2="750" y2="1000"/>
  <line stroke="black" x1="0" y1="1000" x2="250" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="500"/>
  <line stroke="black" x1="250" y1="1000" x2="500" y2="1000"/>
  <line stroke="black" x1="500" y1="1000" x2="750" y2="1000"/>
  <line stroke="black" x1="1000" y1="500" x2="1000" y2="1000"/>
  <line stroke="black" x1="750" y1="1000" x2="1000" y2="1000"/>
</svg>""",
)

BASIC_NARROW_56P31_ZIGZAG_BASE = BoxPleatingCreasePatternExample(
    name="basic_narrow_22p5_zigzag",
    packing_svg="",
    grid_size=4,
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">
  <line stroke="black" x1="0" y1="0" x2="250" y2="0"/>
  <line stroke="black" x1="0" y1="0" x2="0" y2="500"/>
  <line stroke="red" x1="250" y1="0" x2="250" y2="125"/>
  <line stroke="black" x1="250" y1="0" x2="500" y2="0"/>
  <line stroke="red" x1="250" y1="125" x2="0" y2="500"/>
  <line stroke="blue" x1="250" y1="125" x2="500" y2="500"/>
  <line stroke="red" x1="250" y1="125" x2="250" y2="1000"/>
  <line stroke="black" x1="0" y1="500" x2="0" y2="1000"/>
  <line stroke="blue" x1="500" y1="0" x2="500" y2="500"/>
  <line stroke="black" x1="500" y1="0" x2="750" y2="0"/>
  <line stroke="red" x1="500" y1="500" x2="750" y2="125"/>
  <line stroke="blue" x1="500" y1="500" x2="500" y2="1000"/>
  <line stroke="red" x1="750" y1="0" x2="750" y2="125"/>
  <line stroke="black" x1="750" y1="0" x2="1000" y2="0"/>
  <line stroke="blue" x1="750" y1="125" x2="1000" y2="500"/>
  <line stroke="red" x1="750" y1="125" x2="750" y2="1000"/>
  <line stroke="black" x1="0" y1="1000" x2="250" y2="1000"/>
  <line stroke="black" x1="1000" y1="0" x2="1000" y2="500"/>
  <line stroke="black" x1="250" y1="1000" x2="500" y2="1000"/>
  <line stroke="black" x1="500" y1="1000" x2="750" y2="1000"/>
  <line stroke="black" x1="1000" y1="500" x2="1000" y2="1000"/>
  <line stroke="black" x1="750" y1="1000" x2="1000" y2="1000"/>
</svg>""",
)

PAYLOAD_BAY = BoxPleatingCreasePatternExample(
    name="payload_bay",
    grid_size=14,
    central_crease_removed=True,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14">
  <rect stroke="black" x="0" y="0" width="14" height="14"/>
  <line stroke="green" x1="0" y1="3" x2="7" y2="3"/>
  <line stroke="red" x1="4" y1="0" x2="7" y2="3"/>
  <line stroke="green" x1="7" y1="0" x2="7" y2="3"/>
  <line stroke="red" x1="7" y1="3" x2="10" y2="0"/>
  <line stroke="green" x1="7" y1="3" x2="14" y2="3"/>
  <line stroke="green" x1="0" y1="11" x2="7" y2="11"/>
  <line stroke="red" x1="7" y1="11" x2="4" y2="14"/>
  <line stroke="green" x1="7" y1="11" x2="7" y2="14"/>
  <line stroke="red" x1="7" y1="11" x2="10" y2="14"/>
  <line stroke="green" x1="7" y1="11" x2="14" y2="11"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14">
  <rect stroke="black" x="0" y="0" width="14" height="14"/>
  <line stroke="red" x1="1" y1="0" x2="1" y2="14" elevation="1"/>
  <line stroke="blue" x1="2" y1="0" x2="2" y2="14" elevation="0"/>
  <line stroke="red" x1="3" y1="0" x2="3" y2="14" elevation="1"/>
  <line stroke="red" x1="4" y1="0" x2="5" y2="1"/>
  <line stroke="blue" x1="4" y1="0" x2="4" y2="14" elevation="0"/>
  <line stroke="blue" x1="5" y1="1" x2="6" y2="2"/>
  <line stroke="red" x1="5" y1="1" x2="7" y2="1" elevation="1"/>
  <line stroke="red" x1="5" y1="1" x2="5" y2="13" elevation="1"/>
  <line stroke="blue" x1="6" y1="0" x2="7" y2="1"/>
  <line stroke="red" x1="6" y1="2" x2="7" y2="1"/>
  <line stroke="blue" x1="6" y1="2" x2="8" y2="2" elevation="0"/>
  <line stroke="blue" x1="6" y1="2" x2="6" y2="12" elevation="0"/>
  <line stroke="blue" x1="7" y1="1" x2="8" y2="0"/>
  <line stroke="red" x1="7" y1="1" x2="8" y2="2"/>
  <line stroke="red" x1="7" y1="1" x2="9" y2="1" elevation="1"/>
  <line stroke="blue" x1="8" y1="2" x2="9" y2="1"/>
  <line stroke="blue" x1="8" y1="2" x2="8" y2="12" elevation="0"/>
  <line stroke="red" x1="9" y1="1" x2="10" y2="0"/>
  <line stroke="red" x1="9" y1="1" x2="9" y2="13" elevation="1"/>
  <line stroke="blue" x1="10" y1="0" x2="10" y2="14" elevation="0"/>
  <line stroke="red" x1="11" y1="0" x2="11" y2="14" elevation="1"/>
  <line stroke="blue" x1="12" y1="0" x2="12" y2="14" elevation="0"/>
  <line stroke="red" x1="13" y1="0" x2="13" y2="14" elevation="1"/>
  <line stroke="blue" x1="6" y1="12" x2="5" y2="13"/>
  <line stroke="blue" x1="6" y1="12" x2="8" y2="12" elevation="0"/>
  <line stroke="red" x1="6" y1="12" x2="7" y2="13"/>
  <line stroke="red" x1="5" y1="13" x2="4" y2="14"/>
  <line stroke="red" x1="5" y1="13" x2="7" y2="13" elevation="1"/>
  <line stroke="red" x1="8" y1="12" x2="7" y2="13"/>
  <line stroke="blue" x1="8" y1="12" x2="9" y2="13"/>
  <line stroke="blue" x1="7" y1="13" x2="6" y2="14"/>
  <line stroke="red" x1="7" y1="13" x2="9" y2="13" elevation="1"/>
  <line stroke="blue" x1="7" y1="13" x2="8" y2="14"/>
  <line stroke="red" x1="9" y1="13" x2="10" y2="14"/>
</svg>""",
)

RIVER_STAIRCASE = BoxPleatingCreasePatternExample(
    name="river_staircase",
    grid_size=16,
    central_crease_removed=False,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <rect stroke="black" x="0" y="0" width="16" height="16"/>
  <line stroke="red" x1="0" y1="0" x2="2" y2="2"/>
  <line stroke="green" x1="0" y1="2" x2="2" y2="2"/>
  <line stroke="green" x1="2" y1="0" x2="2" y2="2"/>
  <line stroke="red" x1="2" y1="2" x2="4" y2="0"/>
  <line stroke="green" x1="2" y1="2" x2="16" y2="2"/>
  <line stroke="green" x1="0" y1="14" x2="2" y2="14"/>
  <line stroke="red" x1="2" y1="14" x2="0" y2="16"/>
  <line stroke="green" x1="2" y1="14" x2="2" y2="16"/>
  <line stroke="red" x1="2" y1="14" x2="4" y2="16"/>
  <line stroke="green" x1="2" y1="14" x2="16" y2="14"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <rect stroke="black" x="0" y="0" width="16" height="16"/>
  <line stroke="red" x1="0" y1="0" x2="1" y2="1"/>
  <line stroke="red" x1="1" y1="1" x2="1" y2="2" elevation="1"/>
  <line stroke="blue" x1="1" y1="1" x2="2" y2="2"/>
  <line stroke="red" x1="1" y1="1" x2="3" y2="1" elevation="1"/>
  <line stroke="blue" x1="0" y1="2" x2="1" y2="2"/>
  <line stroke="red" x1="1" y1="2" x2="2" y2="2"/>
  <line stroke="red" x1="1" y1="2" x2="1" y2="14" elevation="1"/>
  <line stroke="blue" x1="2" y1="2" x2="3" y2="1"/>
  <line stroke="blue" x1="2" y1="2" x2="2" y2="14" elevation="0"/>
  <line stroke="red" x1="3" y1="1" x2="4" y2="0"/>
  <line stroke="red" x1="3" y1="1" x2="3" y2="15" elevation="1"/>
  <line stroke="blue" x1="4" y1="0" x2="4" y2="16" elevation="0"/>
  <line stroke="red" x1="5" y1="0" x2="5" y2="16" elevation="1"/>
  <line stroke="blue" x1="6" y1="0" x2="6" y2="16" elevation="0"/>
  <line stroke="red" x1="7" y1="0" x2="7" y2="16" elevation="1"/>
  <line stroke="blue" x1="8" y1="0" x2="8" y2="16" elevation="0"/>
  <line stroke="red" x1="9" y1="0" x2="9" y2="16" elevation="1"/>
  <line stroke="blue" x1="10" y1="0" x2="10" y2="16" elevation="0"/>
  <line stroke="red" x1="11" y1="0" x2="11" y2="16" elevation="1"/>
  <line stroke="blue" x1="12" y1="0" x2="12" y2="16" elevation="0"/>
  <line stroke="red" x1="13" y1="0" x2="13" y2="16" elevation="1"/>
  <line stroke="blue" x1="0" y1="14" x2="1" y2="14"/>
  <line stroke="blue" x1="14" y1="0" x2="14" y2="16" elevation="0"/>
  <line stroke="red" x1="1" y1="14" x2="2" y2="14"/>
  <line stroke="red" x1="1" y1="14" x2="1" y2="15" elevation="1"/>
  <line stroke="blue" x1="2" y1="14" x2="1" y2="15"/>
  <line stroke="blue" x1="2" y1="14" x2="3" y2="15"/>
  <line stroke="red" x1="15" y1="0" x2="15" y2="16" elevation="1"/>
  <line stroke="red" x1="1" y1="15" x2="3" y2="15" elevation="1"/>
  <line stroke="red" x1="1" y1="15" x2="0" y2="16"/>
  <line stroke="red" x1="3" y1="15" x2="4" y2="16"/>
</svg>""",
)

GECKO = BoxPleatingCreasePatternExample(
    name="gecko",
    grid_size=36,
    central_crease_removed=False,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 18 18">
  <rect stroke="black" x="0" y="0" width="18" height="18"/>
  <line stroke="red" x1="0" y1="1" x2="1" y2="2"/>
  <line stroke="green" x1="1" y1="0" x2="1" y2="2"/>
  <line stroke="green" x1="0" y1="2" x2="1" y2="2"/>
  <line stroke="green" x1="2" y1="0" x2="2" y2="7"/>
  <line stroke="red" x1="1" y1="2" x2="0" y2="3"/>
  <line stroke="green" x1="1" y1="2" x2="1" y2="4"/>
  <line stroke="red" x1="0" y1="3" x2="1" y2="4"/>
  <line stroke="green" x1="3" y1="0" x2="3" y2="8"/>
  <line stroke="green" x1="0" y1="4" x2="1" y2="4"/>
  <line stroke="red" x1="1" y1="4" x2="0" y2="5"/>
  <line stroke="green" x1="1" y1="4" x2="1" y2="6"/>
  <line stroke="red" x1="0" y1="5" x2="1" y2="6"/>
  <line stroke="green" x1="0" y1="6" x2="1" y2="6"/>
  <line stroke="red" x1="1" y1="6" x2="2" y2="7"/>
  <line stroke="green" x1="0" y1="7" x2="2" y2="7"/>
  <line stroke="red" x1="2" y1="7" x2="3" y2="8"/>
  <line stroke="green" x1="0" y1="8" x2="3" y2="8"/>
  <line stroke="red" x1="3" y1="8" x2="9" y2="2"/>
  <line stroke="green" x1="3" y1="8" x2="15" y2="8"/>
  <line stroke="red" x1="9" y1="0" x2="9" y2="2"/>
  <line stroke="red" x1="9" y1="2" x2="15" y2="8"/>
  <line stroke="green" x1="0" y1="12" x2="7" y2="12"/>
  <line stroke="green" x1="0" y1="13" x2="6" y2="13"/>
  <line stroke="red" x1="7" y1="12" x2="6" y2="13"/>
  <line stroke="green" x1="7" y1="12" x2="11" y2="12"/>
  <line stroke="red" x1="7" y1="12" x2="9" y2="14"/>
  <line stroke="green" x1="7" y1="12" x2="7" y2="18"/>
  <line stroke="green" x1="0" y1="14" x2="1" y2="14"/>
  <line stroke="green" x1="1" y1="14" x2="3" y2="14"/>
  <line stroke="red" x1="1" y1="14" x2="0" y2="15"/>
  <line stroke="red" x1="1" y1="14" x2="2" y2="15"/>
  <line stroke="green" x1="1" y1="14" x2="1" y2="18"/>
  <line stroke="green" x1="3" y1="14" x2="5" y2="14"/>
  <line stroke="red" x1="3" y1="14" x2="2" y2="15"/>
  <line stroke="red" x1="3" y1="14" x2="4" y2="15"/>
  <line stroke="green" x1="3" y1="14" x2="3" y2="18"/>
  <line stroke="red" x1="6" y1="13" x2="5" y2="14"/>
  <line stroke="green" x1="6" y1="13" x2="6" y2="18"/>
  <line stroke="red" x1="5" y1="14" x2="4" y2="15"/>
  <line stroke="green" x1="5" y1="14" x2="5" y2="18"/>
  <line stroke="green" x1="15" y1="0" x2="15" y2="8"/>
  <line stroke="red" x1="2" y1="15" x2="2" y2="18"/>
  <line stroke="red" x1="4" y1="15" x2="4" y2="18"/>
  <line stroke="green" x1="16" y1="0" x2="16" y2="7"/>
  <line stroke="red" x1="11" y1="12" x2="9" y2="14"/>
  <line stroke="red" x1="11" y1="12" x2="12" y2="13"/>
  <line stroke="green" x1="11" y1="12" x2="11" y2="18"/>
  <line stroke="green" x1="11" y1="12" x2="18" y2="12"/>
  <line stroke="red" x1="9" y1="14" x2="9" y2="18"/>
  <line stroke="green" x1="17" y1="0" x2="17" y2="2"/>
  <line stroke="red" x1="15" y1="8" x2="16" y2="7"/>
  <line stroke="green" x1="15" y1="8" x2="18" y2="8"/>
  <line stroke="green" x1="17" y1="2" x2="17" y2="4"/>
  <line stroke="red" x1="17" y1="2" x2="18" y2="1"/>
  <line stroke="green" x1="17" y1="2" x2="18" y2="2"/>
  <line stroke="red" x1="17" y1="2" x2="18" y2="3"/>
  <line stroke="red" x1="16" y1="7" x2="17" y2="6"/>
  <line stroke="green" x1="16" y1="7" x2="18" y2="7"/>
  <line stroke="green" x1="17" y1="4" x2="17" y2="6"/>
  <line stroke="red" x1="17" y1="4" x2="18" y2="3"/>
  <line stroke="green" x1="17" y1="4" x2="18" y2="4"/>
  <line stroke="red" x1="17" y1="4" x2="18" y2="5"/>
  <line stroke="red" x1="12" y1="13" x2="13" y2="14"/>
  <line stroke="green" x1="12" y1="13" x2="12" y2="18"/>
  <line stroke="green" x1="12" y1="13" x2="18" y2="13"/>
  <line stroke="red" x1="17" y1="6" x2="18" y2="5"/>
  <line stroke="green" x1="17" y1="6" x2="18" y2="6"/>
  <line stroke="red" x1="13" y1="14" x2="14" y2="15"/>
  <line stroke="green" x1="13" y1="14" x2="15" y2="14"/>
  <line stroke="green" x1="13" y1="14" x2="13" y2="18"/>
  <line stroke="red" x1="14" y1="15" x2="15" y2="14"/>
  <line stroke="red" x1="14" y1="15" x2="14" y2="18"/>
  <line stroke="red" x1="15" y1="14" x2="16" y2="15"/>
  <line stroke="green" x1="15" y1="14" x2="17" y2="14"/>
  <line stroke="green" x1="15" y1="14" x2="15" y2="18"/>
  <line stroke="red" x1="16" y1="15" x2="17" y2="14"/>
  <line stroke="red" x1="16" y1="15" x2="16" y2="18"/>
  <line stroke="green" x1="17" y1="14" x2="18" y2="14"/>
  <line stroke="red" x1="17" y1="14" x2="18" y2="15"/>
  <line stroke="green" x1="17" y1="14" x2="17" y2="18"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36">
  <rect stroke="black" x="0" y="0" width="36" height="36"/>
  <line stroke="red" x1="0" y1="1" x2="18" y2="1" elevation="1"/>
  <line stroke="red" x1="0" y1="2" x2="1" y2="3"/>
  <line stroke="blue" x1="0" y1="2" x2="18" y2="2" elevation="0"/>
  <line stroke="blue" x1="1" y1="3" x2="2" y2="4"/>
  <line stroke="red" x1="1" y1="3" x2="1" y2="5" elevation="1"/>
  <line stroke="red" x1="1" y1="3" x2="18" y2="3" elevation="1"/>
  <line stroke="blue" x1="2" y1="4" x2="1" y2="5"/>
  <line stroke="red" x1="2" y1="4" x2="2" y2="5"/>
  <line stroke="blue" x1="2" y1="4" x2="18" y2="4" elevation="0"/>
  <line stroke="red" x1="1" y1="5" x2="2" y2="5" elevation="1"/>
  <line stroke="red" x1="1" y1="5" x2="0" y2="6"/>
  <line stroke="blue" x1="2" y1="5" x2="2" y2="6"/>
  <line stroke="red" x1="2" y1="5" x2="17" y2="5" elevation="1"/>
  <line stroke="red" x1="0" y1="6" x2="2" y2="6" elevation="0"/>
  <line stroke="red" x1="0" y1="6" x2="1" y2="7"/>
  <line stroke="blue" x1="2" y1="6" x2="2" y2="7"/>
  <line stroke="blue" x1="2" y1="6" x2="16" y2="6" elevation="0"/>
  <line stroke="red" x1="1" y1="7" x2="2" y2="7" elevation="1"/>
  <line stroke="blue" x1="1" y1="7" x2="2" y2="8"/>
  <line stroke="red" x1="1" y1="7" x2="1" y2="9" elevation="1"/>
  <line stroke="red" x1="2" y1="7" x2="2" y2="8"/>
  <line stroke="red" x1="2" y1="7" x2="15" y2="7" elevation="1"/>
  <line stroke="blue" x1="2" y1="8" x2="1" y2="9"/>
  <line stroke="blue" x1="2" y1="8" x2="14" y2="8" elevation="0"/>
  <line stroke="red" x1="1" y1="9" x2="0" y2="10"/>
  <line stroke="red" x1="1" y1="9" x2="13" y2="9" elevation="1"/>
  <line stroke="red" x1="0" y1="10" x2="1" y2="11"/>
  <line stroke="blue" x1="0" y1="10" x2="12" y2="10" elevation="0"/>
  <line stroke="blue" x1="1" y1="11" x2="2" y2="12"/>
  <line stroke="red" x1="1" y1="11" x2="11" y2="11" elevation="1"/>
  <line stroke="red" x1="1" y1="11" x2="1" y2="16" elevation="1"/>
  <line stroke="red" x1="2" y1="12" x2="3" y2="13"/>
  <line stroke="blue" x1="2" y1="12" x2="10" y2="12" elevation="0"/>
  <line stroke="blue" x1="2" y1="12" x2="2" y2="16" elevation="0"/>
  <line stroke="blue" x1="3" y1="13" x2="4" y2="14"/>
  <line stroke="red" x1="3" y1="13" x2="9" y2="13" elevation="1"/>
  <line stroke="red" x1="3" y1="13" x2="3" y2="16" elevation="1"/>
  <line stroke="red" x1="4" y1="14" x2="5" y2="15"/>
  <line stroke="blue" x1="4" y1="14" x2="8" y2="14" elevation="0"/>
  <line stroke="blue" x1="4" y1="14" x2="4" y2="16" elevation="0"/>
  <line stroke="blue" x1="11" y1="11" x2="10" y2="12"/>
  <line stroke="red" x1="11" y1="11" x2="12" y2="10"/>
  <line stroke="red" x1="11" y1="11" x2="11" y2="27" elevation="1"/>
  <line stroke="red" x1="10" y1="12" x2="9" y2="13"/>
  <line stroke="blue" x1="10" y1="12" x2="10" y2="28" elevation="0"/>
  <line stroke="blue" x1="12" y1="10" x2="13" y2="9"/>
  <line stroke="blue" x1="12" y1="10" x2="12" y2="26" elevation="0"/>
  <line stroke="blue" x1="9" y1="13" x2="8" y2="14"/>
  <line stroke="red" x1="9" y1="13" x2="9" y2="28" elevation="1"/>
  <line stroke="red" x1="13" y1="9" x2="14" y2="8"/>
  <line stroke="red" x1="13" y1="9" x2="13" y2="25" elevation="1"/>
  <line stroke="red" x1="5" y1="15" x2="7" y2="15" elevation="1"/>
  <line stroke="red" x1="5" y1="15" x2="5" y2="16" elevation="1"/>
  <line stroke="blue" x1="5" y1="15" x2="6" y2="16"/>
  <line stroke="blue" x1="0" y1="16" x2="1" y2="16"/>
  <line stroke="red" x1="1" y1="16" x2="2" y2="16"/>
  <line stroke="red" x1="1" y1="16" x2="1" y2="29" elevation="1"/>
  <line stroke="blue" x1="2" y1="16" x2="3" y2="16"/>
  <line stroke="blue" x1="2" y1="16" x2="2" y2="28" elevation="0"/>
  <line stroke="red" x1="8" y1="14" x2="7" y2="15"/>
  <line stroke="blue" x1="8" y1="14" x2="8" y2="28" elevation="0"/>
  <line stroke="blue" x1="14" y1="8" x2="15" y2="7"/>
  <line stroke="blue" x1="14" y1="8" x2="14" y2="24" elevation="0"/>
  <line stroke="red" x1="3" y1="16" x2="4" y2="16"/>
  <line stroke="red" x1="3" y1="16" x2="3" y2="28" elevation="1"/>
  <line stroke="blue" x1="4" y1="16" x2="5" y2="16"/>
  <line stroke="blue" x1="4" y1="16" x2="4" y2="28" elevation="0"/>
  <line stroke="blue" x1="7" y1="15" x2="6" y2="16"/>
  <line stroke="red" x1="7" y1="15" x2="7" y2="28" elevation="1"/>
  <line stroke="red" x1="15" y1="7" x2="16" y2="6"/>
  <line stroke="red" x1="15" y1="7" x2="15" y2="24" elevation="1"/>
  <line stroke="red" x1="5" y1="16" x2="6" y2="16"/>
  <line stroke="red" x1="5" y1="16" x2="5" y2="28" elevation="1"/>
  <line stroke="blue" x1="6" y1="16" x2="6" y2="28" elevation="0"/>
  <line stroke="blue" x1="16" y1="6" x2="17" y2="5"/>
  <line stroke="blue" x1="16" y1="6" x2="16" y2="24" elevation="0"/>
  <line stroke="red" x1="17" y1="5" x2="18" y2="4"/>
  <line stroke="red" x1="17" y1="5" x2="17" y2="24" elevation="1"/>
  <line stroke="red" x1="18" y1="0" x2="18" y2="1"/>
  <line stroke="blue" x1="18" y1="1" x2="18" y2="2"/>
  <line stroke="red" x1="18" y1="1" x2="36" y2="1" elevation="1"/>
  <line stroke="red" x1="18" y1="2" x2="18" y2="3"/>
  <line stroke="blue" x1="18" y1="2" x2="36" y2="2" elevation="0"/>
  <line stroke="blue" x1="18" y1="3" x2="18" y2="4"/>
  <line stroke="red" x1="18" y1="3" x2="35" y2="3" elevation="1"/>
  <line stroke="red" x1="18" y1="4" x2="19" y2="5"/>
  <line stroke="blue" x1="18" y1="4" x2="18" y2="24" elevation="0"/>
  <line stroke="blue" x1="18" y1="4" x2="34" y2="4" elevation="0"/>
  <line stroke="blue" x1="19" y1="5" x2="20" y2="6"/>
  <line stroke="red" x1="19" y1="5" x2="19" y2="24" elevation="1"/>
  <line stroke="red" x1="19" y1="5" x2="34" y2="5" elevation="1"/>
  <line stroke="red" x1="20" y1="6" x2="21" y2="7"/>
  <line stroke="blue" x1="20" y1="6" x2="20" y2="24" elevation="0"/>
  <line stroke="blue" x1="20" y1="6" x2="34" y2="6" elevation="0"/>
  <line stroke="blue" x1="21" y1="7" x2="22" y2="8"/>
  <line stroke="red" x1="21" y1="7" x2="21" y2="24" elevation="1"/>
  <line stroke="red" x1="21" y1="7" x2="34" y2="7" elevation="1"/>
  <line stroke="red" x1="22" y1="8" x2="23" y2="9"/>
  <line stroke="blue" x1="22" y1="8" x2="22" y2="24" elevation="0"/>
  <line stroke="blue" x1="22" y1="8" x2="34" y2="8" elevation="0"/>
  <line stroke="blue" x1="23" y1="9" x2="24" y2="10"/>
  <line stroke="red" x1="23" y1="9" x2="23" y2="24" elevation="1"/>
  <line stroke="red" x1="23" y1="9" x2="35" y2="9" elevation="1"/>
  <line stroke="red" x1="24" y1="10" x2="25" y2="11"/>
  <line stroke="blue" x1="24" y1="10" x2="24" y2="24" elevation="0"/>
  <line stroke="blue" x1="24" y1="10" x2="36" y2="10" elevation="0"/>
  <line stroke="blue" x1="25" y1="11" x2="26" y2="12"/>
  <line stroke="red" x1="25" y1="11" x2="25" y2="24" elevation="1"/>
  <line stroke="red" x1="25" y1="11" x2="35" y2="11" elevation="1"/>
  <line stroke="blue" x1="14" y1="24" x2="13" y2="25"/>
  <line stroke="red" x1="14" y1="24" x2="15" y2="24"/>
  <line stroke="blue" x1="14" y1="24" x2="15" y2="25"/>
  <line stroke="red" x1="2" y1="28" x2="3" y2="28"/>
  <line stroke="blue" x1="2" y1="28" x2="1" y2="29"/>
  <line stroke="blue" x1="2" y1="28" x2="3" y2="29"/>
  <line stroke="blue" x1="3" y1="28" x2="4" y2="28"/>
  <line stroke="red" x1="3" y1="28" x2="3" y2="29" elevation="1"/>
  <line stroke="red" x1="13" y1="25" x2="12" y2="26"/>
  <line stroke="red" x1="13" y1="25" x2="15" y2="25" elevation="1"/>
  <line stroke="red" x1="4" y1="28" x2="5" y2="28"/>
  <line stroke="blue" x1="4" y1="28" x2="4" y2="30" elevation="0"/>
  <line stroke="blue" x1="15" y1="24" x2="16" y2="24"/>
  <line stroke="red" x1="15" y1="24" x2="15" y2="25" elevation="1"/>
  <line stroke="blue" x1="5" y1="28" x2="6" y2="28"/>
  <line stroke="red" x1="5" y1="28" x2="5" y2="29" elevation="1"/>
  <line stroke="red" x1="6" y1="28" x2="7" y2="28"/>
  <line stroke="blue" x1="6" y1="28" x2="5" y2="29"/>
  <line stroke="red" x1="6" y1="28" x2="6" y2="29"/>
  <line stroke="blue" x1="6" y1="28" x2="7" y2="29"/>
  <line stroke="blue" x1="12" y1="26" x2="11" y2="27"/>
  <line stroke="blue" x1="12" y1="26" x2="16" y2="26" elevation="0"/>
  <line stroke="red" x1="26" y1="12" x2="27" y2="13"/>
  <line stroke="blue" x1="26" y1="12" x2="26" y2="24" elevation="0"/>
  <line stroke="blue" x1="26" y1="12" x2="34" y2="12" elevation="0"/>
  <line stroke="red" x1="16" y1="24" x2="17" y2="24"/>
  <line stroke="blue" x1="16" y1="24" x2="16" y2="26" elevation="0"/>
  <line stroke="blue" x1="7" y1="28" x2="8" y2="28"/>
  <line stroke="red" x1="7" y1="28" x2="7" y2="29" elevation="1"/>
  <line stroke="red" x1="1" y1="29" x2="3" y2="29" elevation="1"/>
  <line stroke="red" x1="1" y1="29" x2="0" y2="30"/>
  <line stroke="red" x1="8" y1="28" x2="9" y2="28"/>
  <line stroke="blue" x1="8" y1="28" x2="8" y2="30" elevation="0"/>
  <line stroke="red" x1="3" y1="29" x2="4" y2="30"/>
  <line stroke="red" x1="11" y1="27" x2="10" y2="28"/>
  <line stroke="red" x1="11" y1="27" x2="17" y2="27" elevation="1"/>
  <line stroke="red" x1="15" y1="25" x2="16" y2="26"/>
  <line stroke="blue" x1="9" y1="28" x2="10" y2="28"/>
  <line stroke="red" x1="9" y1="28" x2="9" y2="29" elevation="1"/>
  <line stroke="blue" x1="17" y1="24" x2="18" y2="24"/>
  <line stroke="red" x1="17" y1="24" x2="17" y2="27" elevation="1"/>
  <line stroke="red" x1="5" y1="29" x2="6" y2="29" elevation="1"/>
  <line stroke="red" x1="5" y1="29" x2="4" y2="30"/>
  <line stroke="red" x1="6" y1="29" x2="7" y2="29" elevation="1"/>
  <line stroke="blue" x1="6" y1="29" x2="6" y2="30"/>
  <line stroke="blue" x1="10" y1="28" x2="9" y2="29"/>
  <line stroke="red" x1="10" y1="28" x2="10" y2="29"/>
  <line stroke="blue" x1="10" y1="28" x2="18" y2="28" elevation="0"/>
  <line stroke="red" x1="7" y1="29" x2="8" y2="30"/>
  <line stroke="blue" x1="27" y1="13" x2="28" y2="14"/>
  <line stroke="red" x1="27" y1="13" x2="33" y2="13" elevation="1"/>
  <line stroke="red" x1="27" y1="13" x2="27" y2="24" elevation="1"/>
  <line stroke="blue" x1="0" y1="30" x2="4" y2="30" elevation="0"/>
  <line stroke="red" x1="18" y1="24" x2="19" y2="24"/>
  <line stroke="blue" x1="18" y1="24" x2="18" y2="28" elevation="0"/>
  <line stroke="blue" x1="4" y1="30" x2="6" y2="30" elevation="0"/>
  <line stroke="blue" x1="4" y1="30" x2="4" y2="31"/>
  <line stroke="red" x1="9" y1="29" x2="10" y2="29" elevation="1"/>
  <line stroke="red" x1="9" y1="29" x2="8" y2="30"/>
  <line stroke="blue" x1="16" y1="26" x2="17" y2="27"/>
  <line stroke="blue" x1="6" y1="30" x2="8" y2="30" elevation="0"/>
  <line stroke="red" x1="6" y1="30" x2="6" y2="31"/>
  <line stroke="blue" x1="19" y1="24" x2="20" y2="24"/>
  <line stroke="red" x1="19" y1="24" x2="19" y2="27" elevation="1"/>
  <line stroke="blue" x1="10" y1="29" x2="10" y2="30"/>
  <line stroke="red" x1="10" y1="29" x2="18" y2="29" elevation="1"/>
  <line stroke="red" x1="0" y1="31" x2="4" y2="31" elevation="1"/>
  <line stroke="blue" x1="8" y1="30" x2="10" y2="30" elevation="0"/>
  <line stroke="blue" x1="8" y1="30" x2="8" y2="31"/>
  <line stroke="red" x1="20" y1="24" x2="21" y2="24"/>
  <line stroke="blue" x1="20" y1="24" x2="20" y2="26" elevation="0"/>
  <line stroke="red" x1="4" y1="31" x2="6" y2="31" elevation="1"/>
  <line stroke="red" x1="4" y1="31" x2="4" y2="32"/>
  <line stroke="red" x1="28" y1="14" x2="29" y2="15"/>
  <line stroke="blue" x1="28" y1="14" x2="32" y2="14" elevation="0"/>
  <line stroke="blue" x1="28" y1="14" x2="28" y2="24" elevation="0"/>
  <line stroke="red" x1="6" y1="31" x2="8" y2="31" elevation="1"/>
  <line stroke="blue" x1="6" y1="31" x2="6" y2="32"/>
  <line stroke="red" x1="10" y1="30" x2="10" y2="31"/>
  <line stroke="blue" x1="10" y1="30" x2="18" y2="30" elevation="0"/>
  <line stroke="blue" x1="21" y1="24" x2="22" y2="24"/>
  <line stroke="red" x1="21" y1="24" x2="21" y2="25" elevation="1"/>
  <line stroke="red" x1="17" y1="27" x2="18" y2="28"/>
  <line stroke="blue" x1="0" y1="32" x2="4" y2="32" elevation="0"/>
  <line stroke="red" x1="8" y1="31" x2="10" y2="31" elevation="1"/>
  <line stroke="red" x1="8" y1="31" x2="8" y2="32"/>
  <line stroke="blue" x1="4" y1="32" x2="6" y2="32" elevation="0"/>
  <line stroke="blue" x1="4" y1="32" x2="4" y2="33"/>
  <line stroke="blue" x1="6" y1="32" x2="8" y2="32" elevation="0"/>
  <line stroke="red" x1="6" y1="32" x2="6" y2="33"/>
  <line stroke="blue" x1="22" y1="24" x2="21" y2="25"/>
  <line stroke="red" x1="22" y1="24" x2="23" y2="24"/>
  <line stroke="red" x1="22" y1="24" x2="22" y2="25"/>
  <line stroke="blue" x1="22" y1="24" x2="23" y2="25"/>
  <line stroke="blue" x1="10" y1="31" x2="10" y2="32"/>
  <line stroke="red" x1="10" y1="31" x2="18" y2="31" elevation="1"/>
  <line stroke="red" x1="21" y1="25" x2="20" y2="26"/>
  <line stroke="red" x1="21" y1="25" x2="22" y2="25" elevation="1"/>
  <line stroke="blue" x1="29" y1="15" x2="30" y2="16"/>
  <line stroke="red" x1="29" y1="15" x2="31" y2="15" elevation="1"/>
  <line stroke="red" x1="29" y1="15" x2="29" y2="24" elevation="1"/>
  <line stroke="blue" x1="20" y1="26" x2="19" y2="27"/>
  <line stroke="blue" x1="20" y1="26" x2="22" y2="26" elevation="0"/>
  <line stroke="blue" x1="8" y1="32" x2="10" y2="32" elevation="0"/>
  <line stroke="blue" x1="8" y1="32" x2="8" y2="33"/>
  <line stroke="red" x1="0" y1="33" x2="4" y2="33" elevation="1"/>
  <line stroke="red" x1="19" y1="27" x2="18" y2="28"/>
  <line stroke="red" x1="19" y1="27" x2="22" y2="27" elevation="1"/>
  <line stroke="red" x1="4" y1="33" x2="6" y2="33" elevation="1"/>
  <line stroke="red" x1="4" y1="33" x2="4" y2="34"/>
  <line stroke="blue" x1="23" y1="24" x2="24" y2="24"/>
  <line stroke="red" x1="23" y1="24" x2="23" y2="25" elevation="1"/>
  <line stroke="blue" x1="18" y1="28" x2="18" y2="29"/>
  <line stroke="blue" x1="18" y1="28" x2="22" y2="28" elevation="0"/>
  <line stroke="red" x1="22" y1="25" x2="23" y2="25" elevation="1"/>
  <line stroke="blue" x1="22" y1="25" x2="22" y2="26"/>
  <line stroke="red" x1="10" y1="32" x2="10" y2="33"/>
  <line stroke="blue" x1="10" y1="32" x2="18" y2="32" elevation="0"/>
  <line stroke="red" x1="6" y1="33" x2="8" y2="33" elevation="1"/>
  <line stroke="blue" x1="6" y1="33" x2="6" y2="34"/>
  <line stroke="red" x1="24" y1="24" x2="25" y2="24"/>
  <line stroke="blue" x1="24" y1="24" x2="24" y2="26" elevation="0"/>
  <line stroke="red" x1="8" y1="33" x2="10" y2="33" elevation="1"/>
  <line stroke="red" x1="8" y1="33" x2="8" y2="34"/>
  <line stroke="red" x1="23" y1="25" x2="24" y2="26"/>
  <line stroke="blue" x1="0" y1="34" x2="4" y2="34" elevation="0"/>
  <line stroke="blue" x1="30" y1="16" x2="31" y2="15"/>
  <line stroke="red" x1="30" y1="16" x2="31" y2="16"/>
  <line stroke="blue" x1="30" y1="16" x2="30" y2="24" elevation="0"/>
  <line stroke="red" x1="22" y1="26" x2="22" y2="27"/>
  <line stroke="blue" x1="22" y1="26" x2="24" y2="26" elevation="0"/>
  <line stroke="red" x1="18" y1="29" x2="18" y2="30"/>
  <line stroke="red" x1="18" y1="29" x2="22" y2="29" elevation="1"/>
  <line stroke="blue" x1="4" y1="34" x2="6" y2="34" elevation="0"/>
  <line stroke="blue" x1="4" y1="34" x2="4" y2="35"/>
  <line stroke="red" x1="34" y1="4" x2="34" y2="5"/>
  <line stroke="blue" x1="34" y1="4" x2="35" y2="3"/>
  <line stroke="blue" x1="34" y1="4" x2="35" y2="5"/>
  <line stroke="blue" x1="34" y1="5" x2="34" y2="6"/>
  <line stroke="red" x1="34" y1="5" x2="35" y2="5" elevation="1"/>
  <line stroke="red" x1="31" y1="15" x2="31" y2="16" elevation="1"/>
  <line stroke="red" x1="31" y1="15" x2="32" y2="14"/>
  <line stroke="blue" x1="10" y1="33" x2="10" y2="34"/>
  <line stroke="red" x1="10" y1="33" x2="18" y2="33" elevation="1"/>
  <line stroke="blue" x1="6" y1="34" x2="8" y2="34" elevation="0"/>
  <line stroke="red" x1="6" y1="34" x2="6" y2="35"/>
  <line stroke="blue" x1="34" y1="6" x2="34" y2="7"/>
  <line stroke="red" x1="34" y1="6" x2="36" y2="6" elevation="0"/>
  <line stroke="blue" x1="25" y1="24" x2="26" y2="24"/>
  <line stroke="red" x1="25" y1="24" x2="25" y2="27" elevation="1"/>
  <line stroke="red" x1="34" y1="7" x2="34" y2="8"/>
  <line stroke="red" x1="34" y1="7" x2="35" y2="7" elevation="1"/>
  <line stroke="blue" x1="22" y1="27" x2="22" y2="28"/>
  <line stroke="red" x1="22" y1="27" x2="25" y2="27" elevation="1"/>
  <line stroke="blue" x1="31" y1="16" x2="32" y2="16"/>
  <line stroke="red" x1="31" y1="16" x2="31" y2="24" elevation="1"/>
  <line stroke="blue" x1="8" y1="34" x2="10" y2="34" elevation="0"/>
  <line stroke="blue" x1="8" y1="34" x2="8" y2="35"/>
  <line stroke="blue" x1="32" y1="14" x2="33" y2="13"/>
  <line stroke="blue" x1="32" y1="14" x2="32" y2="16" elevation="0"/>
  <line stroke="blue" x1="34" y1="8" x2="35" y2="7"/>
  <line stroke="blue" x1="34" y1="8" x2="35" y2="9"/>
  <line stroke="blue" x1="18" y1="30" x2="18" y2="31"/>
  <line stroke="blue" x1="18" y1="30" x2="22" y2="30" elevation="0"/>
  <line stroke="red" x1="0" y1="35" x2="4" y2="35" elevation="1"/>
  <line stroke="red" x1="35" y1="3" x2="35" y2="5" elevation="1"/>
  <line stroke="red" x1="35" y1="3" x2="36" y2="2"/>
  <line stroke="red" x1="4" y1="35" x2="6" y2="35" elevation="1"/>
  <line stroke="red" x1="4" y1="35" x2="4" y2="36"/>
  <line stroke="red" x1="35" y1="5" x2="36" y2="6"/>
  <line stroke="blue" x1="24" y1="26" x2="25" y2="27"/>
  <line stroke="red" x1="26" y1="24" x2="27" y2="24"/>
  <line stroke="blue" x1="26" y1="24" x2="26" y2="28" elevation="0"/>
  <line stroke="red" x1="10" y1="34" x2="10" y2="35"/>
  <line stroke="blue" x1="10" y1="34" x2="18" y2="34" elevation="0"/>
  <line stroke="red" x1="33" y1="13" x2="34" y2="12"/>
  <line stroke="red" x1="33" y1="13" x2="33" y2="16" elevation="1"/>
  <line stroke="red" x1="6" y1="35" x2="8" y2="35" elevation="1"/>
  <line stroke="blue" x1="6" y1="35" x2="6" y2="36"/>
  <line stroke="red" x1="22" y1="28" x2="22" y2="29"/>
  <line stroke="blue" x1="22" y1="28" x2="26" y2="28" elevation="0"/>
  <line stroke="red" x1="35" y1="7" x2="35" y2="9" elevation="1"/>
  <line stroke="red" x1="35" y1="7" x2="36" y2="6"/>
  <line stroke="red" x1="32" y1="16" x2="33" y2="16"/>
  <line stroke="blue" x1="32" y1="16" x2="32" y2="24" elevation="0"/>
  <line stroke="red" x1="18" y1="31" x2="18" y2="32"/>
  <line stroke="red" x1="18" y1="31" x2="22" y2="31" elevation="1"/>
  <line stroke="red" x1="8" y1="35" x2="10" y2="35" elevation="1"/>
  <line stroke="red" x1="8" y1="35" x2="8" y2="36"/>
  <line stroke="blue" x1="34" y1="12" x2="35" y2="11"/>
  <line stroke="blue" x1="34" y1="12" x2="34" y2="16" elevation="0"/>
  <line stroke="blue" x1="27" y1="24" x2="28" y2="24"/>
  <line stroke="red" x1="27" y1="24" x2="27" y2="28" elevation="1"/>
  <line stroke="red" x1="35" y1="9" x2="36" y2="10"/>
  <line stroke="blue" x1="10" y1="35" x2="10" y2="36"/>
  <line stroke="red" x1="10" y1="35" x2="18" y2="35" elevation="1"/>
  <line stroke="blue" x1="22" y1="29" x2="22" y2="30"/>
  <line stroke="red" x1="22" y1="29" x2="26" y2="29" elevation="1"/>
  <line stroke="blue" x1="33" y1="16" x2="34" y2="16"/>
  <line stroke="red" x1="33" y1="16" x2="33" y2="24" elevation="1"/>
  <line stroke="red" x1="35" y1="11" x2="36" y2="10"/>
  <line stroke="red" x1="35" y1="11" x2="35" y2="16" elevation="1"/>
  <line stroke="blue" x1="18" y1="32" x2="18" y2="33"/>
  <line stroke="blue" x1="18" y1="32" x2="22" y2="32" elevation="0"/>
  <line stroke="red" x1="25" y1="27" x2="26" y2="28"/>
  <line stroke="red" x1="28" y1="24" x2="29" y2="24"/>
  <line stroke="blue" x1="28" y1="24" x2="28" y2="28" elevation="0"/>
  <line stroke="red" x1="22" y1="30" x2="22" y2="31"/>
  <line stroke="blue" x1="22" y1="30" x2="26" y2="30" elevation="0"/>
  <line stroke="red" x1="34" y1="16" x2="35" y2="16"/>
  <line stroke="blue" x1="34" y1="16" x2="34" y2="24" elevation="0"/>
  <line stroke="red" x1="18" y1="33" x2="18" y2="34"/>
  <line stroke="red" x1="18" y1="33" x2="22" y2="33" elevation="1"/>
  <line stroke="blue" x1="29" y1="24" x2="30" y2="24"/>
  <line stroke="red" x1="29" y1="24" x2="29" y2="28" elevation="1"/>
  <line stroke="blue" x1="22" y1="31" x2="22" y2="32"/>
  <line stroke="red" x1="22" y1="31" x2="26" y2="31" elevation="1"/>
  <line stroke="blue" x1="26" y1="28" x2="27" y2="28"/>
  <line stroke="red" x1="26" y1="28" x2="26" y2="29"/>
  <line stroke="blue" x1="26" y1="28" x2="27" y2="29"/>
  <line stroke="red" x1="30" y1="24" x2="31" y2="24"/>
  <line stroke="blue" x1="30" y1="24" x2="30" y2="28" elevation="0"/>
  <line stroke="blue" x1="18" y1="34" x2="18" y2="35"/>
  <line stroke="blue" x1="18" y1="34" x2="22" y2="34" elevation="0"/>
  <line stroke="blue" x1="35" y1="16" x2="36" y2="16"/>
  <line stroke="red" x1="35" y1="16" x2="35" y2="24" elevation="1"/>
  <line stroke="red" x1="22" y1="32" x2="22" y2="33"/>
  <line stroke="blue" x1="22" y1="32" x2="26" y2="32" elevation="0"/>
  <line stroke="red" x1="27" y1="28" x2="28" y2="28"/>
  <line stroke="red" x1="27" y1="28" x2="27" y2="29" elevation="1"/>
  <line stroke="red" x1="26" y1="29" x2="27" y2="29" elevation="1"/>
  <line stroke="blue" x1="26" y1="29" x2="26" y2="30"/>
  <line stroke="blue" x1="31" y1="24" x2="32" y2="24"/>
  <line stroke="red" x1="31" y1="24" x2="31" y2="28" elevation="1"/>
  <line stroke="red" x1="18" y1="35" x2="18" y2="36"/>
  <line stroke="red" x1="18" y1="35" x2="22" y2="35" elevation="1"/>
  <line stroke="blue" x1="28" y1="28" x2="29" y2="28"/>
  <line stroke="blue" x1="28" y1="28" x2="28" y2="30" elevation="0"/>
  <line stroke="red" x1="27" y1="29" x2="28" y2="30"/>
  <line stroke="blue" x1="22" y1="33" x2="22" y2="34"/>
  <line stroke="red" x1="22" y1="33" x2="26" y2="33" elevation="1"/>
  <line stroke="red" x1="26" y1="30" x2="26" y2="31"/>
  <line stroke="blue" x1="26" y1="30" x2="28" y2="30" elevation="0"/>
  <line stroke="red" x1="32" y1="24" x2="33" y2="24"/>
  <line stroke="blue" x1="32" y1="24" x2="32" y2="28" elevation="0"/>
  <line stroke="red" x1="29" y1="28" x2="29" y2="29" elevation="1"/>
  <line stroke="red" x1="29" y1="28" x2="30" y2="28"/>
  <line stroke="blue" x1="26" y1="31" x2="26" y2="32"/>
  <line stroke="red" x1="26" y1="31" x2="28" y2="31" elevation="1"/>
  <line stroke="red" x1="22" y1="34" x2="22" y2="35"/>
  <line stroke="blue" x1="22" y1="34" x2="26" y2="34" elevation="0"/>
  <line stroke="blue" x1="33" y1="24" x2="34" y2="24"/>
  <line stroke="red" x1="33" y1="24" x2="33" y2="28" elevation="1"/>
  <line stroke="red" x1="29" y1="29" x2="28" y2="30"/>
  <line stroke="blue" x1="29" y1="29" x2="30" y2="28"/>
  <line stroke="red" x1="29" y1="29" x2="30" y2="29" elevation="1"/>
  <line stroke="blue" x1="28" y1="30" x2="28" y2="31"/>
  <line stroke="blue" x1="28" y1="30" x2="30" y2="30" elevation="0"/>
  <line stroke="red" x1="30" y1="28" x2="30" y2="29"/>
  <line stroke="blue" x1="30" y1="28" x2="31" y2="28"/>
  <line stroke="blue" x1="30" y1="28" x2="31" y2="29"/>
  <line stroke="red" x1="26" y1="32" x2="26" y2="33"/>
  <line stroke="blue" x1="26" y1="32" x2="28" y2="32" elevation="0"/>
  <line stroke="blue" x1="22" y1="35" x2="22" y2="36"/>
  <line stroke="red" x1="22" y1="35" x2="26" y2="35" elevation="1"/>
  <line stroke="red" x1="34" y1="24" x2="35" y2="24"/>
  <line stroke="blue" x1="34" y1="24" x2="34" y2="28" elevation="0"/>
  <line stroke="blue" x1="30" y1="29" x2="30" y2="30"/>
  <line stroke="red" x1="30" y1="29" x2="31" y2="29" elevation="1"/>
  <line stroke="red" x1="28" y1="31" x2="28" y2="32"/>
  <line stroke="red" x1="28" y1="31" x2="30" y2="31" elevation="1"/>
  <line stroke="red" x1="31" y1="28" x2="31" y2="29" elevation="1"/>
  <line stroke="red" x1="31" y1="28" x2="32" y2="28"/>
  <line stroke="blue" x1="26" y1="33" x2="26" y2="34"/>
  <line stroke="red" x1="26" y1="33" x2="28" y2="33" elevation="1"/>
  <line stroke="red" x1="30" y1="30" x2="30" y2="31"/>
  <line stroke="blue" x1="30" y1="30" x2="32" y2="30" elevation="0"/>
  <line stroke="blue" x1="35" y1="24" x2="36" y2="24"/>
  <line stroke="red" x1="35" y1="24" x2="35" y2="29" elevation="1"/>
  <line stroke="red" x1="31" y1="29" x2="32" y2="30"/>
  <line stroke="blue" x1="28" y1="32" x2="28" y2="33"/>
  <line stroke="blue" x1="28" y1="32" x2="30" y2="32" elevation="0"/>
  <line stroke="blue" x1="32" y1="28" x2="33" y2="28"/>
  <line stroke="blue" x1="32" y1="28" x2="32" y2="30" elevation="0"/>
  <line stroke="red" x1="26" y1="34" x2="26" y2="35"/>
  <line stroke="blue" x1="26" y1="34" x2="28" y2="34" elevation="0"/>
  <line stroke="blue" x1="30" y1="31" x2="30" y2="32"/>
  <line stroke="red" x1="30" y1="31" x2="32" y2="31" elevation="1"/>
  <line stroke="red" x1="28" y1="33" x2="28" y2="34"/>
  <line stroke="red" x1="28" y1="33" x2="30" y2="33" elevation="1"/>
  <line stroke="red" x1="33" y1="28" x2="33" y2="29" elevation="1"/>
  <line stroke="red" x1="33" y1="28" x2="34" y2="28"/>
  <line stroke="blue" x1="26" y1="35" x2="26" y2="36"/>
  <line stroke="red" x1="26" y1="35" x2="28" y2="35" elevation="1"/>
  <line stroke="red" x1="30" y1="32" x2="30" y2="33"/>
  <line stroke="blue" x1="30" y1="32" x2="32" y2="32" elevation="0"/>
  <line stroke="red" x1="32" y1="30" x2="33" y2="29"/>
  <line stroke="blue" x1="32" y1="30" x2="32" y2="31"/>
  <line stroke="blue" x1="32" y1="30" x2="36" y2="30" elevation="0"/>
  <line stroke="blue" x1="33" y1="29" x2="34" y2="28"/>
  <line stroke="red" x1="33" y1="29" x2="35" y2="29" elevation="1"/>
  <line stroke="blue" x1="28" y1="34" x2="28" y2="35"/>
  <line stroke="blue" x1="28" y1="34" x2="30" y2="34" elevation="0"/>
  <line stroke="blue" x1="34" y1="28" x2="35" y2="29"/>
  <line stroke="red" x1="32" y1="31" x2="32" y2="32"/>
  <line stroke="red" x1="32" y1="31" x2="36" y2="31" elevation="1"/>
  <line stroke="blue" x1="30" y1="33" x2="30" y2="34"/>
  <line stroke="red" x1="30" y1="33" x2="32" y2="33" elevation="1"/>
  <line stroke="red" x1="28" y1="35" x2="28" y2="36"/>
  <line stroke="red" x1="28" y1="35" x2="30" y2="35" elevation="1"/>
  <line stroke="blue" x1="32" y1="32" x2="32" y2="33"/>
  <line stroke="blue" x1="32" y1="32" x2="36" y2="32" elevation="0"/>
  <line stroke="red" x1="30" y1="34" x2="30" y2="35"/>
  <line stroke="blue" x1="30" y1="34" x2="32" y2="34" elevation="0"/>
  <line stroke="red" x1="35" y1="29" x2="36" y2="30"/>
  <line stroke="red" x1="32" y1="33" x2="32" y2="34"/>
  <line stroke="red" x1="32" y1="33" x2="36" y2="33" elevation="1"/>
  <line stroke="blue" x1="30" y1="35" x2="30" y2="36"/>
  <line stroke="red" x1="30" y1="35" x2="32" y2="35" elevation="1"/>
  <line stroke="blue" x1="32" y1="34" x2="32" y2="35"/>
  <line stroke="blue" x1="32" y1="34" x2="36" y2="34" elevation="0"/>
  <line stroke="red" x1="32" y1="35" x2="32" y2="36"/>
  <line stroke="red" x1="32" y1="35" x2="36" y2="35" elevation="1"/>
</svg>""",
)

GROSBEAK = BoxPleatingCreasePatternExample(
    name="grosbeak",
    grid_size=8,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14">
  <rect stroke="black" x="0" y="0" width="14" height="14"/>
  <line stroke="red" x1="0" y1="0" x2="3.5" y2="3.5"/>
  <line stroke="green" x1="0" y1="3.5" x2="3.5" y2="3.5"/>
  <line stroke="green" x1="3.5" y1="0" x2="3.5" y2="3.5"/>
  <line stroke="red" x1="3.5" y1="3.5" x2="7" y2="0"/>
  <line stroke="green" x1="3.5" y1="3.5" x2="14" y2="3.5"/>
  <line stroke="green" x1="0" y1="8.8" x2="3.5" y2="8.8"/>
  <line stroke="green" x1="3.5" y1="8.8" x2="7" y2="8.8"/>
  <line stroke="red" x1="3.5" y1="8.8" x2="5.2" y2="10.5"/>
  <line stroke="red" x1="3.5" y1="8.8" x2="0" y2="12.2"/>
  <line stroke="green" x1="3.5" y1="8.8" x2="3.5" y2="14"/>
  <line stroke="red" x1="7" y1="8.8" x2="5.2" y2="10.5"/>
  <line stroke="green" x1="7" y1="8.8" x2="7" y2="14"/>
  <line stroke="green" x1="7" y1="8.8" x2="14" y2="8.8"/>
  <line stroke="red" x1="7" y1="8.8" x2="12.2" y2="14"/>
  <line stroke="red" x1="5.2" y1="10.5" x2="5.2" y2="14"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8">
  <rect stroke="black" x="0" y="0" width="8" height="8"/>
  <line stroke="red" x1="0" y1="0" x2="1" y2="1"/>
  <line stroke="red" x1="1" y1="1" x2="1" y2="2" elevation="1"/>
  <line stroke="blue" x1="1" y1="1" x2="2" y2="2"/>
  <line stroke="red" x1="1" y1="1" x2="3" y2="1" elevation="1"/>
  <line stroke="blue" x1="0" y1="2" x2="1" y2="2"/>
  <line stroke="red" x1="1" y1="2" x2="2" y2="2"/>
  <line stroke="red" x1="1" y1="2" x2="1" y2="5" elevation="1"/>
  <line stroke="blue" x1="2" y1="2" x2="3" y2="1"/>
  <line stroke="blue" x1="2" y1="2" x2="2" y2="5" elevation="0"/>
  <line stroke="red" x1="3" y1="1" x2="4" y2="0"/>
  <line stroke="red" x1="3" y1="1" x2="3" y2="6" elevation="1"/>
  <line stroke="blue" x1="4" y1="0" x2="4" y2="5" elevation="0"/>
  <line stroke="blue" x1="0" y1="5" x2="1" y2="5"/>
  <line stroke="red" x1="5" y1="0" x2="5" y2="6" elevation="1"/>
  <line stroke="red" x1="1" y1="5" x2="2" y2="5"/>
  <line stroke="red" x1="1" y1="5" x2="1" y2="6" elevation="1"/>
  <line stroke="blue" x1="2" y1="5" x2="1" y2="6"/>
  <line stroke="blue" x1="2" y1="5" x2="3" y2="6"/>
  <line stroke="blue" x1="6" y1="0" x2="6" y2="7" elevation="0"/>
  <line stroke="red" x1="1" y1="6" x2="3" y2="6" elevation="1"/>
  <line stroke="red" x1="1" y1="6" x2="0" y2="7"/>
  <line stroke="blue" x1="4" y1="5" x2="3" y2="6"/>
  <line stroke="red" x1="4" y1="5" x2="4" y2="6"/>
  <line stroke="blue" x1="4" y1="5" x2="5" y2="6"/>
  <line stroke="red" x1="3" y1="6" x2="4" y2="6" elevation="1"/>
  <line stroke="red" x1="3" y1="6" x2="3" y2="7"/>
  <line stroke="blue" x1="0" y1="7" x2="3" y2="7" elevation="0"/>
  <line stroke="red" x1="7" y1="0" x2="7" y2="8" elevation="1"/>
  <line stroke="red" x1="4" y1="6" x2="5" y2="6" elevation="1"/>
  <line stroke="blue" x1="4" y1="6" x2="4" y2="7"/>
  <line stroke="blue" x1="3" y1="7" x2="4" y2="7" elevation="0"/>
  <line stroke="blue" x1="3" y1="7" x2="3" y2="8"/>
  <line stroke="red" x1="5" y1="6" x2="6" y2="7"/>
  <line stroke="red" x1="4" y1="7" x2="4" y2="8"/>
  <line stroke="blue" x1="4" y1="7" x2="6" y2="7" elevation="0"/>
  <line stroke="blue" x1="6" y1="7" x2="7" y2="8"/>
</svg>""",
)

BUTTERFLY = BoxPleatingCreasePatternExample(
    name="butterfly",
    grid_size=32,
    stick_figure=stick_figure_examples.BUTTERFLY,
    central_crease_removed=False,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <line stroke="black" x1="0" y1="0" x2="0" y2="3"/>
  <line stroke="black" x1="0" y1="0" x2="13" y2="0"/>
  <line stroke="black" x1="0" y1="3" x2="0" y2="4"/>
  <line stroke="green" x1="0" y1="3" x2="16" y2="3"/>
  <line stroke="green" x1="0" y1="4" x2="12" y2="4"/>
  <line stroke="black" x1="0" y1="4" x2="0" y2="13"/>
  <line stroke="red" x1="12" y1="4" x2="3" y2="13"/>
  <line stroke="red" x1="12" y1="4" x2="16" y2="8"/>
  <line stroke="green" x1="12" y1="4" x2="20" y2="4"/>
  <line stroke="green" x1="12" y1="4" x2="12" y2="22"/>
  <line stroke="red" x1="0" y1="13" x2="3" y2="13"/>
  <line stroke="black" x1="0" y1="13" x2="0" y2="22"/>
  <line stroke="black" x1="13" y1="0" x2="16" y2="0"/>
  <line stroke="red" x1="13" y1="0" x2="16" y2="3"/>
  <line stroke="red" x1="3" y1="13" x2="12" y2="22"/>
  <line stroke="green" x1="16" y1="0" x2="16" y2="3"/>
  <line stroke="black" x1="16" y1="0" x2="19" y2="0"/>
  <line stroke="red" x1="16" y1="3" x2="19" y2="0"/>
  <line stroke="green" x1="16" y1="3" x2="32" y2="3"/>
  <line stroke="red" x1="16" y1="8" x2="20" y2="4"/>
  <line stroke="red" x1="16" y1="8" x2="16" y2="32"/>
  <line stroke="black" x1="19" y1="0" x2="32" y2="0"/>
  <line stroke="green" x1="20" y1="4" x2="20" y2="22"/>
  <line stroke="red" x1="20" y1="4" x2="29" y2="13"/>
  <line stroke="green" x1="20" y1="4" x2="32" y2="4"/>
  <line stroke="green" x1="0" y1="22" x2="12" y2="22"/>
  <line stroke="black" x1="0" y1="22" x2="0" y2="31"/>
  <line stroke="red" x1="12" y1="22" x2="3" y2="31"/>
  <line stroke="green" x1="12" y1="22" x2="12" y2="32"/>
  <line stroke="red" x1="20" y1="22" x2="29" y2="13"/>
  <line stroke="green" x1="20" y1="22" x2="20" y2="32"/>
  <line stroke="green" x1="20" y1="22" x2="32" y2="22"/>
  <line stroke="red" x1="20" y1="22" x2="29" y2="31"/>
  <line stroke="red" x1="0" y1="31" x2="3" y2="31"/>
  <line stroke="black" x1="0" y1="31" x2="0" y2="32"/>
  <line stroke="red" x1="3" y1="31" x2="4" y2="32"/>
  <line stroke="red" x1="29" y1="13" x2="32" y2="13"/>
  <line stroke="black" x1="0" y1="32" x2="4" y2="32"/>
  <line stroke="black" x1="32" y1="0" x2="32" y2="3"/>
  <line stroke="black" x1="32" y1="3" x2="32" y2="4"/>
  <line stroke="black" x1="4" y1="32" x2="12" y2="32"/>
  <line stroke="black" x1="32" y1="4" x2="32" y2="13"/>
  <line stroke="black" x1="12" y1="32" x2="16" y2="32"/>
  <line stroke="black" x1="32" y1="13" x2="32" y2="22"/>
  <line stroke="black" x1="16" y1="32" x2="20" y2="32"/>
  <line stroke="black" x1="20" y1="32" x2="28" y2="32"/>
  <line stroke="black" x1="32" y1="22" x2="32" y2="31"/>
  <line stroke="red" x1="29" y1="31" x2="28" y2="32"/>
  <line stroke="red" x1="29" y1="31" x2="32" y2="31"/>
  <line stroke="black" x1="28" y1="32" x2="32" y2="32"/>
  <line stroke="black" x1="32" y1="31" x2="32" y2="32"/>
</svg>""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect stroke="black" x="0" y="0" width="32" height="32"/>
  <line stroke="blue" x1="1" y1="0" x2="1" y2="4" elevation="0"/>
  <line stroke="red" x1="2" y1="0" x2="2" y2="4" elevation="1"/>
  <line stroke="blue" x1="3" y1="0" x2="3" y2="4" elevation="0"/>
  <line stroke="red" x1="0" y1="4" x2="1" y2="4"/>
  <line stroke="red" x1="4" y1="0" x2="4" y2="4" elevation="1"/>
  <line stroke="blue" x1="1" y1="4" x2="2" y2="4"/>
  <line stroke="blue" x1="1" y1="4" x2="1" y2="13" elevation="0"/>
  <line stroke="red" x1="2" y1="4" x2="3" y2="4"/>
  <line stroke="red" x1="2" y1="4" x2="2" y2="13" elevation="1"/>
  <line stroke="blue" x1="3" y1="4" x2="4" y2="4"/>
  <line stroke="blue" x1="3" y1="4" x2="3" y2="13" elevation="0"/>
  <line stroke="blue" x1="5" y1="0" x2="5" y2="4" elevation="0"/>
  <line stroke="red" x1="4" y1="4" x2="5" y2="4"/>
  <line stroke="red" x1="4" y1="4" x2="4" y2="12" elevation="1"/>
  <line stroke="red" x1="6" y1="0" x2="6" y2="4" elevation="1"/>
  <line stroke="blue" x1="5" y1="4" x2="6" y2="4"/>
  <line stroke="blue" x1="5" y1="4" x2="5" y2="11" elevation="0"/>
  <line stroke="blue" x1="7" y1="0" x2="7" y2="4" elevation="0"/>
  <line stroke="red" x1="6" y1="4" x2="7" y2="4"/>
  <line stroke="red" x1="6" y1="4" x2="6" y2="10" elevation="1"/>
  <line stroke="red" x1="8" y1="0" x2="8" y2="4" elevation="1"/>
  <line stroke="blue" x1="7" y1="4" x2="8" y2="4"/>
  <line stroke="blue" x1="7" y1="4" x2="7" y2="9" elevation="0"/>
  <line stroke="red" x1="8" y1="4" x2="9" y2="4"/>
  <line stroke="red" x1="8" y1="4" x2="8" y2="8" elevation="1"/>
  <line stroke="blue" x1="9" y1="0" x2="9" y2="4" elevation="0"/>
  <line stroke="blue" x1="9" y1="4" x2="10" y2="4"/>
  <line stroke="blue" x1="9" y1="4" x2="9" y2="7" elevation="0"/>
  <line stroke="red" x1="10" y1="0" x2="10" y2="4" elevation="1"/>
  <line stroke="red" x1="10" y1="4" x2="10" y2="6" elevation="1"/>
  <line stroke="red" x1="10" y1="4" x2="11" y2="4"/>
  <line stroke="blue" x1="11" y1="0" x2="11" y2="4" elevation="0"/>
  <line stroke="red" x1="8" y1="8" x2="7" y2="9"/>
  <line stroke="blue" x1="8" y1="8" x2="9" y2="7"/>
  <line stroke="red" x1="8" y1="8" x2="16" y2="8" elevation="1"/>
  <line stroke="blue" x1="7" y1="9" x2="6" y2="10"/>
  <line stroke="blue" x1="7" y1="9" x2="16" y2="9" elevation="0"/>
  <line stroke="red" x1="9" y1="7" x2="10" y2="6"/>
  <line stroke="blue" x1="9" y1="7" x2="15" y2="7" elevation="0"/>
  <line stroke="red" x1="6" y1="10" x2="5" y2="11"/>
  <line stroke="red" x1="6" y1="10" x2="16" y2="10" elevation="1"/>
  <line stroke="blue" x1="10" y1="6" x2="11" y2="5"/>
  <line stroke="red" x1="10" y1="6" x2="14" y2="6" elevation="1"/>
  <line stroke="blue" x1="11" y1="4" x2="11" y2="5" elevation="0"/>
  <line stroke="blue" x1="11" y1="4" x2="12" y2="4"/>
  <line stroke="red" x1="12" y1="0" x2="12" y2="4" elevation="1"/>
  <line stroke="blue" x1="5" y1="11" x2="4" y2="12"/>
  <line stroke="blue" x1="5" y1="11" x2="16" y2="11" elevation="0"/>
  <line stroke="red" x1="11" y1="5" x2="12" y2="4"/>
  <line stroke="blue" x1="11" y1="5" x2="13" y2="5" elevation="0"/>
  <line stroke="red" x1="4" y1="12" x2="3" y2="13"/>
  <line stroke="red" x1="4" y1="12" x2="16" y2="12" elevation="1"/>
  <line stroke="red" x1="12" y1="4" x2="13" y2="5"/>
  <line stroke="blue" x1="0" y1="13" x2="1" y2="13"/>
  <line stroke="blue" x1="13" y1="0" x2="13" y2="5" elevation="0"/>
  <line stroke="red" x1="13" y1="0" x2="14" y2="1"/>
  <line stroke="red" x1="1" y1="13" x2="2" y2="13"/>
  <line stroke="blue" x1="1" y1="13" x2="1" y2="22" elevation="0"/>
  <line stroke="blue" x1="2" y1="13" x2="3" y2="13"/>
  <line stroke="red" x1="2" y1="13" x2="2" y2="22" elevation="1"/>
  <line stroke="red" x1="3" y1="13" x2="4" y2="14"/>
  <line stroke="blue" x1="3" y1="13" x2="16" y2="13" elevation="0"/>
  <line stroke="blue" x1="3" y1="13" x2="3" y2="22" elevation="0"/>
  <line stroke="blue" x1="13" y1="5" x2="14" y2="6"/>
  <line stroke="blue" x1="14" y1="1" x2="15" y2="2"/>
  <line stroke="red" x1="14" y1="1" x2="14" y2="6" elevation="1"/>
  <line stroke="red" x1="14" y1="1" x2="16" y2="1" elevation="1"/>
  <line stroke="blue" x1="4" y1="14" x2="5" y2="15"/>
  <line stroke="red" x1="4" y1="14" x2="16" y2="14" elevation="1"/>
  <line stroke="red" x1="4" y1="14" x2="4" y2="22" elevation="1"/>
  <line stroke="blue" x1="15" y1="2" x2="16" y2="2" elevation="0"/>
  <line stroke="red" x1="15" y1="2" x2="16" y2="3"/>
  <line stroke="blue" x1="15" y1="2" x2="15" y2="7" elevation="0"/>
  <line stroke="red" x1="14" y1="6" x2="15" y2="7"/>
  <line stroke="red" x1="5" y1="15" x2="6" y2="16"/>
  <line stroke="blue" x1="5" y1="15" x2="16" y2="15" elevation="0"/>
  <line stroke="blue" x1="5" y1="15" x2="5" y2="22" elevation="0"/>
  <line stroke="blue" x1="16" y1="0" x2="16" y2="1"/>
  <line stroke="red" x1="16" y1="1" x2="16" y2="2"/>
  <line stroke="red" x1="16" y1="1" x2="18" y2="1" elevation="1"/>
  <line stroke="blue" x1="16" y1="2" x2="16" y2="3"/>
  <line stroke="blue" x1="16" y1="2" x2="17" y2="2" elevation="0"/>
  <line stroke="red" x1="16" y1="3" x2="17" y2="2"/>
  <line stroke="red" x1="16" y1="3" x2="16" y2="8" elevation="1"/>
  <line stroke="blue" x1="15" y1="7" x2="16" y2="8"/>
  <line stroke="blue" x1="6" y1="16" x2="7" y2="17"/>
  <line stroke="red" x1="6" y1="16" x2="16" y2="16" elevation="1"/>
  <line stroke="red" x1="6" y1="16" x2="6" y2="22" elevation="1"/>
  <line stroke="blue" x1="17" y1="2" x2="18" y2="1"/>
  <line stroke="blue" x1="17" y1="2" x2="17" y2="7" elevation="0"/>
  <line stroke="red" x1="16" y1="8" x2="16" y2="9"/>
  <line stroke="blue" x1="16" y1="8" x2="17" y2="7"/>
  <line stroke="red" x1="16" y1="8" x2="24" y2="8" elevation="1"/>
  <line stroke="red" x1="18" y1="1" x2="18" y2="6" elevation="1"/>
  <line stroke="red" x1="18" y1="1" x2="19" y2="0"/>
  <line stroke="blue" x1="16" y1="9" x2="16" y2="10"/>
  <line stroke="blue" x1="16" y1="9" x2="25" y2="9" elevation="0"/>
  <line stroke="red" x1="7" y1="17" x2="8" y2="18"/>
  <line stroke="blue" x1="7" y1="17" x2="7" y2="22" elevation="0"/>
  <line stroke="blue" x1="7" y1="17" x2="16" y2="17" elevation="0"/>
  <line stroke="red" x1="17" y1="7" x2="18" y2="6"/>
  <line stroke="blue" x1="17" y1="7" x2="23" y2="7" elevation="0"/>
  <line stroke="red" x1="16" y1="10" x2="16" y2="11"/>
  <line stroke="red" x1="16" y1="10" x2="26" y2="10" elevation="1"/>
  <line stroke="blue" x1="18" y1="6" x2="19" y2="5"/>
  <line stroke="red" x1="18" y1="6" x2="22" y2="6" elevation="1"/>
  <line stroke="blue" x1="19" y1="0" x2="19" y2="5" elevation="0"/>
  <line stroke="blue" x1="16" y1="11" x2="16" y2="12"/>
  <line stroke="blue" x1="16" y1="11" x2="27" y2="11" elevation="0"/>
  <line stroke="red" x1="19" y1="5" x2="20" y2="4"/>
  <line stroke="blue" x1="19" y1="5" x2="21" y2="5" elevation="0"/>
  <line stroke="blue" x1="8" y1="18" x2="9" y2="19"/>
  <line stroke="red" x1="8" y1="18" x2="8" y2="22" elevation="1"/>
  <line stroke="red" x1="8" y1="18" x2="16" y2="18" elevation="1"/>
  <line stroke="red" x1="16" y1="12" x2="16" y2="13"/>
  <line stroke="red" x1="16" y1="12" x2="28" y2="12" elevation="1"/>
  <line stroke="red" x1="20" y1="0" x2="20" y2="4" elevation="1"/>
  <line stroke="blue" x1="20" y1="4" x2="21" y2="4"/>
  <line stroke="red" x1="20" y1="4" x2="21" y2="5"/>
  <line stroke="blue" x1="16" y1="13" x2="16" y2="14"/>
  <line stroke="blue" x1="16" y1="13" x2="29" y2="13" elevation="0"/>
  <line stroke="blue" x1="21" y1="0" x2="21" y2="4" elevation="0"/>
  <line stroke="red" x1="9" y1="19" x2="10" y2="20"/>
  <line stroke="blue" x1="9" y1="19" x2="9" y2="22" elevation="0"/>
  <line stroke="blue" x1="9" y1="19" x2="16" y2="19" elevation="0"/>
  <line stroke="red" x1="16" y1="14" x2="16" y2="15"/>
  <line stroke="red" x1="16" y1="14" x2="28" y2="14" elevation="1"/>
  <line stroke="blue" x1="21" y1="4" x2="21" y2="5" elevation="0"/>
  <line stroke="red" x1="21" y1="4" x2="22" y2="4"/>
  <line stroke="blue" x1="21" y1="5" x2="22" y2="6"/>
  <line stroke="blue" x1="16" y1="15" x2="16" y2="16"/>
  <line stroke="blue" x1="16" y1="15" x2="27" y2="15" elevation="0"/>
  <line stroke="red" x1="0" y1="22" x2="1" y2="22"/>
  <line stroke="red" x1="22" y1="0" x2="22" y2="4" elevation="1"/>
  <line stroke="blue" x1="1" y1="22" x2="2" y2="22"/>
  <line stroke="blue" x1="1" y1="22" x2="1" y2="31" elevation="0"/>
  <line stroke="red" x1="2" y1="22" x2="3" y2="22"/>
  <line stroke="red" x1="2" y1="22" x2="2" y2="31" elevation="1"/>
  <line stroke="blue" x1="3" y1="22" x2="4" y2="22"/>
  <line stroke="blue" x1="3" y1="22" x2="3" y2="31" elevation="0"/>
  <line stroke="red" x1="4" y1="22" x2="5" y2="22"/>
  <line stroke="red" x1="4" y1="22" x2="4" y2="30" elevation="1"/>
  <line stroke="blue" x1="10" y1="20" x2="11" y2="21"/>
  <line stroke="red" x1="10" y1="20" x2="10" y2="22" elevation="1"/>
  <line stroke="red" x1="10" y1="20" x2="16" y2="20" elevation="1"/>
  <line stroke="red" x1="22" y1="4" x2="22" y2="6" elevation="1"/>
  <line stroke="blue" x1="22" y1="4" x2="23" y2="4"/>
  <line stroke="blue" x1="5" y1="22" x2="6" y2="22"/>
  <line stroke="blue" x1="5" y1="22" x2="5" y2="29" elevation="0"/>
  <line stroke="red" x1="16" y1="16" x2="16" y2="17"/>
  <line stroke="red" x1="16" y1="16" x2="26" y2="16" elevation="1"/>
  <line stroke="red" x1="6" y1="22" x2="7" y2="22"/>
  <line stroke="red" x1="6" y1="22" x2="6" y2="28" elevation="1"/>
  <line stroke="red" x1="22" y1="6" x2="23" y2="7"/>
  <line stroke="blue" x1="23" y1="0" x2="23" y2="4" elevation="0"/>
  <line stroke="blue" x1="7" y1="22" x2="8" y2="22"/>
  <line stroke="blue" x1="7" y1="22" x2="7" y2="27" elevation="0"/>
  <line stroke="blue" x1="16" y1="17" x2="16" y2="18"/>
  <line stroke="blue" x1="16" y1="17" x2="25" y2="17" elevation="0"/>
  <line stroke="blue" x1="23" y1="4" x2="23" y2="7" elevation="0"/>
  <line stroke="red" x1="23" y1="4" x2="24" y2="4"/>
  <line stroke="red" x1="8" y1="22" x2="9" y2="22"/>
  <line stroke="red" x1="8" y1="22" x2="8" y2="26" elevation="1"/>
  <line stroke="blue" x1="11" y1="21" x2="11" y2="22" elevation="0"/>
  <line stroke="red" x1="11" y1="21" x2="12" y2="22"/>
  <line stroke="blue" x1="11" y1="21" x2="16" y2="21" elevation="0"/>
  <line stroke="blue" x1="9" y1="22" x2="10" y2="22"/>
  <line stroke="blue" x1="9" y1="22" x2="9" y2="25" elevation="0"/>
  <line stroke="red" x1="24" y1="0" x2="24" y2="4" elevation="1"/>
  <line stroke="blue" x1="23" y1="7" x2="24" y2="8"/>
  <line stroke="red" x1="16" y1="18" x2="16" y2="19"/>
  <line stroke="red" x1="16" y1="18" x2="24" y2="18" elevation="1"/>
  <line stroke="red" x1="10" y1="22" x2="11" y2="22"/>
  <line stroke="red" x1="10" y1="22" x2="10" y2="24" elevation="1"/>
  <line stroke="red" x1="24" y1="4" x2="24" y2="8" elevation="1"/>
  <line stroke="blue" x1="24" y1="4" x2="25" y2="4"/>
  <line stroke="blue" x1="11" y1="22" x2="12" y2="22"/>
  <line stroke="blue" x1="11" y1="22" x2="11" y2="23" elevation="0"/>
  <line stroke="blue" x1="16" y1="19" x2="16" y2="20"/>
  <line stroke="blue" x1="16" y1="19" x2="23" y2="19" elevation="0"/>
  <line stroke="blue" x1="25" y1="0" x2="25" y2="4" elevation="0"/>
  <line stroke="red" x1="12" y1="22" x2="11" y2="23"/>
  <line stroke="red" x1="12" y1="22" x2="16" y2="22" elevation="1"/>
  <line stroke="red" x1="24" y1="8" x2="25" y2="9"/>
  <line stroke="red" x1="25" y1="4" x2="26" y2="4"/>
  <line stroke="blue" x1="25" y1="4" x2="25" y2="9" elevation="0"/>
  <line stroke="blue" x1="11" y1="23" x2="10" y2="24"/>
  <line stroke="blue" x1="11" y1="23" x2="16" y2="23" elevation="0"/>
  <line stroke="red" x1="16" y1="20" x2="16" y2="21"/>
  <line stroke="red" x1="16" y1="20" x2="22" y2="20" elevation="1"/>
  <line stroke="red" x1="10" y1="24" x2="9" y2="25"/>
  <line stroke="red" x1="10" y1="24" x2="16" y2="24" elevation="1"/>
  <line stroke="red" x1="26" y1="0" x2="26" y2="4" elevation="1"/>
  <line stroke="blue" x1="26" y1="4" x2="27" y2="4"/>
  <line stroke="red" x1="26" y1="4" x2="26" y2="10" elevation="1"/>
  <line stroke="blue" x1="16" y1="21" x2="16" y2="22"/>
  <line stroke="blue" x1="16" y1="21" x2="21" y2="21" elevation="0"/>
  <line stroke="blue" x1="9" y1="25" x2="8" y2="26"/>
  <line stroke="blue" x1="9" y1="25" x2="16" y2="25" elevation="0"/>
  <line stroke="blue" x1="25" y1="9" x2="26" y2="10"/>
  <line stroke="blue" x1="27" y1="0" x2="27" y2="4" elevation="0"/>
  <line stroke="red" x1="8" y1="26" x2="7" y2="27"/>
  <line stroke="red" x1="8" y1="26" x2="16" y2="26" elevation="1"/>
  <line stroke="red" x1="16" y1="22" x2="16" y2="23"/>
  <line stroke="red" x1="16" y1="22" x2="20" y2="22" elevation="1"/>
  <line stroke="red" x1="27" y1="4" x2="28" y2="4"/>
  <line stroke="blue" x1="27" y1="4" x2="27" y2="11" elevation="0"/>
  <line stroke="red" x1="26" y1="10" x2="27" y2="11"/>
  <line stroke="blue" x1="7" y1="27" x2="6" y2="28"/>
  <line stroke="blue" x1="7" y1="27" x2="16" y2="27" elevation="0"/>
  <line stroke="red" x1="28" y1="0" x2="28" y2="4" elevation="1"/>
  <line stroke="blue" x1="16" y1="23" x2="16" y2="24"/>
  <line stroke="blue" x1="16" y1="23" x2="21" y2="23" elevation="0"/>
  <line stroke="blue" x1="28" y1="4" x2="29" y2="4"/>
  <line stroke="red" x1="28" y1="4" x2="28" y2="12" elevation="1"/>
  <line stroke="red" x1="6" y1="28" x2="5" y2="29"/>
  <line stroke="red" x1="6" y1="28" x2="16" y2="28" elevation="1"/>
  <line stroke="red" x1="16" y1="24" x2="16" y2="25"/>
  <line stroke="red" x1="16" y1="24" x2="22" y2="24" elevation="1"/>
  <line stroke="blue" x1="29" y1="0" x2="29" y2="4" elevation="0"/>
  <line stroke="blue" x1="27" y1="11" x2="28" y2="12"/>
  <line stroke="red" x1="29" y1="4" x2="30" y2="4"/>
  <line stroke="blue" x1="29" y1="4" x2="29" y2="13" elevation="0"/>
  <line stroke="blue" x1="5" y1="29" x2="4" y2="30"/>
  <line stroke="blue" x1="5" y1="29" x2="16" y2="29" elevation="0"/>
  <line stroke="blue" x1="16" y1="25" x2="16" y2="26"/>
  <line stroke="blue" x1="16" y1="25" x2="23" y2="25" elevation="0"/>
  <line stroke="red" x1="21" y1="21" x2="20" y2="22"/>
  <line stroke="blue" x1="21" y1="21" x2="22" y2="20"/>
  <line stroke="blue" x1="21" y1="21" x2="21" y2="22" elevation="0"/>
  <line stroke="blue" x1="20" y1="22" x2="21" y2="22"/>
  <line stroke="red" x1="20" y1="22" x2="21" y2="23"/>
  <line stroke="red" x1="22" y1="20" x2="23" y2="19"/>
  <line stroke="red" x1="22" y1="20" x2="22" y2="22" elevation="1"/>
  <line stroke="blue" x1="23" y1="19" x2="24" y2="18"/>
  <line stroke="blue" x1="23" y1="19" x2="23" y2="22" elevation="0"/>
  <line stroke="red" x1="24" y1="18" x2="25" y2="17"/>
  <line stroke="red" x1="24" y1="18" x2="24" y2="22" elevation="1"/>
  <line stroke="red" x1="30" y1="0" x2="30" y2="4" elevation="1"/>
  <line stroke="blue" x1="25" y1="17" x2="26" y2="16"/>
  <line stroke="blue" x1="25" y1="17" x2="25" y2="22" elevation="0"/>
  <line stroke="red" x1="4" y1="30" x2="3" y2="31"/>
  <line stroke="red" x1="4" y1="30" x2="16" y2="30" elevation="1"/>
  <line stroke="blue" x1="30" y1="4" x2="31" y2="4"/>
  <line stroke="red" x1="30" y1="4" x2="30" y2="13" elevation="1"/>
  <line stroke="red" x1="21" y1="22" x2="22" y2="22"/>
  <line stroke="blue" x1="21" y1="22" x2="21" y2="23" elevation="0"/>
  <line stroke="red" x1="28" y1="12" x2="29" y2="13"/>
  <line stroke="red" x1="16" y1="26" x2="16" y2="27"/>
  <line stroke="red" x1="16" y1="26" x2="24" y2="26" elevation="1"/>
  <line stroke="red" x1="26" y1="16" x2="27" y2="15"/>
  <line stroke="red" x1="26" y1="16" x2="26" y2="22" elevation="1"/>
  <line stroke="blue" x1="27" y1="15" x2="28" y2="14"/>
  <line stroke="blue" x1="27" y1="15" x2="27" y2="22" elevation="0"/>
  <line stroke="blue" x1="0" y1="31" x2="1" y2="31"/>
  <line stroke="blue" x1="31" y1="0" x2="31" y2="4" elevation="0"/>
  <line stroke="red" x1="1" y1="31" x2="2" y2="31"/>
  <line stroke="blue" x1="1" y1="31" x2="1" y2="32" elevation="0"/>
  <line stroke="blue" x1="2" y1="31" x2="3" y2="31"/>
  <line stroke="red" x1="2" y1="31" x2="2" y2="32" elevation="1"/>
  <line stroke="blue" x1="22" y1="22" x2="23" y2="22"/>
  <line stroke="red" x1="22" y1="22" x2="22" y2="24" elevation="1"/>
  <line stroke="blue" x1="3" y1="31" x2="3" y2="32" elevation="0"/>
  <line stroke="red" x1="3" y1="31" x2="4" y2="32"/>
  <line stroke="blue" x1="3" y1="31" x2="16" y2="31" elevation="0"/>
  <line stroke="blue" x1="21" y1="23" x2="22" y2="24"/>
  <line stroke="red" x1="31" y1="4" x2="32" y2="4"/>
  <line stroke="blue" x1="31" y1="4" x2="31" y2="13" elevation="0"/>
  <line stroke="red" x1="28" y1="14" x2="29" y2="13"/>
  <line stroke="red" x1="28" y1="14" x2="28" y2="22" elevation="1"/>
  <line stroke="blue" x1="16" y1="27" x2="16" y2="28"/>
  <line stroke="blue" x1="16" y1="27" x2="25" y2="27" elevation="0"/>
  <line stroke="blue" x1="29" y1="13" x2="30" y2="13"/>
  <line stroke="blue" x1="29" y1="13" x2="29" y2="22" elevation="0"/>
  <line stroke="red" x1="23" y1="22" x2="24" y2="22"/>
  <line stroke="blue" x1="23" y1="22" x2="23" y2="25" elevation="0"/>
  <line stroke="red" x1="16" y1="28" x2="16" y2="29"/>
  <line stroke="red" x1="16" y1="28" x2="26" y2="28" elevation="1"/>
  <line stroke="red" x1="22" y1="24" x2="23" y2="25"/>
  <line stroke="blue" x1="24" y1="22" x2="25" y2="22"/>
  <line stroke="red" x1="24" y1="22" x2="24" y2="26" elevation="1"/>
  <line stroke="red" x1="30" y1="13" x2="31" y2="13"/>
  <line stroke="red" x1="30" y1="13" x2="30" y2="22" elevation="1"/>
  <line stroke="blue" x1="16" y1="29" x2="16" y2="30"/>
  <line stroke="blue" x1="16" y1="29" x2="27" y2="29" elevation="0"/>
  <line stroke="red" x1="25" y1="22" x2="26" y2="22"/>
  <line stroke="blue" x1="25" y1="22" x2="25" y2="27" elevation="0"/>
  <line stroke="blue" x1="31" y1="13" x2="32" y2="13"/>
  <line stroke="blue" x1="31" y1="13" x2="31" y2="22" elevation="0"/>
  <line stroke="blue" x1="23" y1="25" x2="24" y2="26"/>
  <line stroke="red" x1="16" y1="30" x2="16" y2="31"/>
  <line stroke="red" x1="16" y1="30" x2="28" y2="30" elevation="1"/>
  <line stroke="blue" x1="26" y1="22" x2="27" y2="22"/>
  <line stroke="red" x1="26" y1="22" x2="26" y2="28" elevation="1"/>
  <line stroke="red" x1="27" y1="22" x2="28" y2="22"/>
  <line stroke="blue" x1="27" y1="22" x2="27" y2="29" elevation="0"/>
  <line stroke="blue" x1="16" y1="31" x2="16" y2="32"/>
  <line stroke="blue" x1="16" y1="31" x2="29" y2="31" elevation="0"/>
  <line stroke="red" x1="24" y1="26" x2="25" y2="27"/>
  <line stroke="blue" x1="28" y1="22" x2="29" y2="22"/>
  <line stroke="red" x1="28" y1="22" x2="28" y2="30" elevation="1"/>
  <line stroke="red" x1="29" y1="22" x2="30" y2="22"/>
  <line stroke="blue" x1="29" y1="22" x2="29" y2="31" elevation="0"/>
  <line stroke="blue" x1="25" y1="27" x2="26" y2="28"/>
  <line stroke="blue" x1="30" y1="22" x2="31" y2="22"/>
  <line stroke="red" x1="30" y1="22" x2="30" y2="31" elevation="1"/>
  <line stroke="red" x1="31" y1="22" x2="32" y2="22"/>
  <line stroke="blue" x1="31" y1="22" x2="31" y2="31" elevation="0"/>
  <line stroke="red" x1="26" y1="28" x2="27" y2="29"/>
  <line stroke="blue" x1="27" y1="29" x2="28" y2="30"/>
  <line stroke="red" x1="28" y1="30" x2="29" y2="31"/>
  <line stroke="red" x1="29" y1="31" x2="28" y2="32"/>
  <line stroke="blue" x1="29" y1="31" x2="30" y2="31"/>
  <line stroke="blue" x1="29" y1="31" x2="29" y2="32" elevation="0"/>
  <line stroke="red" x1="30" y1="31" x2="31" y2="31"/>
  <line stroke="red" x1="30" y1="31" x2="30" y2="32" elevation="1"/>
  <line stroke="blue" x1="31" y1="31" x2="31" y2="32" elevation="0"/>
  <line stroke="blue" x1="31" y1="31" x2="32" y2="31"/>
</svg>""",
)

SCORPION_LARGE_PINCERS = BoxPleatingCreasePatternExample(
    name="scorpion_large_pincers",
    grid_size=50,
    packing_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50">
  <rect stroke="black" x="0" y="0" width="50" height="50"/>
  <line stroke="green" x1="0" y1="3" x2="50" y2="3"/>
  <line stroke="red" x1="0" y1="14" x2="50" y2="14"/>
  <line stroke="red" x1="22" y1="0" x2="25" y2="3"/>
  <line stroke="green" x1="0" y1="25" x2="50" y2="25"/>
  <line stroke="green" x1="25" y1="0" x2="25" y2="3"/>
  <line stroke="red" x1="25" y1="3" x2="28" y2="0"/>
  <line stroke="green" x1="0" y1="27" x2="50" y2="27"/>
  <line stroke="red" x1="0" y1="30" x2="22" y2="30"/>
  <line stroke="green" x1="0" y1="33" x2="50" y2="33"/>
  <line stroke="green" x1="0" y1="34" x2="50" y2="34"/>
  <line stroke="green" x1="0" y1="35" x2="50" y2="35"/>
  <line stroke="red" x1="3" y1="35" x2="0" y2="38"/>
  <line stroke="green" x1="3" y1="35" x2="3" y2="41"/>
  <line stroke="red" x1="3" y1="35" x2="12" y2="44"/>
  <line stroke="green" x1="4" y1="36" x2="4" y2="42"/>
  <line stroke="green" x1="4" y1="36" x2="46" y2="36"/>
  <line stroke="red" x1="25" y1="27" x2="22" y2="30"/>
  <line stroke="red" x1="25" y1="27" x2="28" y2="30"/>
  <line stroke="green" x1="25" y1="27" x2="25" y2="33"/>
  <line stroke="red" x1="22" y1="30" x2="25" y2="33"/>
  <line stroke="green" x1="5" y1="37" x2="5" y2="43"/>
  <line stroke="green" x1="5" y1="37" x2="45" y2="37"/>
  <line stroke="red" x1="0" y1="38" x2="9" y2="47"/>
  <line stroke="green" x1="6" y1="38" x2="18" y2="38"/>
  <line stroke="green" x1="6" y1="38" x2="6" y2="44"/>
  <line stroke="green" x1="7" y1="39" x2="17" y2="39"/>
  <line stroke="green" x1="7" y1="39" x2="7" y2="45"/>
  <line stroke="green" x1="8" y1="40" x2="16" y2="40"/>
  <line stroke="green" x1="8" y1="40" x2="8" y2="46"/>
  <line stroke="green" x1="0" y1="41" x2="3" y2="41"/>
  <line stroke="red" x1="28" y1="30" x2="25" y2="33"/>
  <line stroke="red" x1="28" y1="30" x2="50" y2="30"/>
  <line stroke="red" x1="19" y1="37" x2="12" y2="44"/>
  <line stroke="red" x1="19" y1="37" x2="22" y2="40"/>
  <line stroke="green" x1="19" y1="37" x2="19" y2="50"/>
  <line stroke="green" x1="9" y1="41" x2="15" y2="41"/>
  <line stroke="green" x1="9" y1="41" x2="9" y2="50"/>
  <line stroke="green" x1="0" y1="42" x2="4" y2="42"/>
  <line stroke="green" x1="18" y1="38" x2="18" y2="50"/>
  <line stroke="green" x1="17" y1="39" x2="17" y2="50"/>
  <line stroke="green" x1="0" y1="43" x2="5" y2="43"/>
  <line stroke="green" x1="16" y1="40" x2="16" y2="50"/>
  <line stroke="green" x1="15" y1="41" x2="15" y2="50"/>
  <line stroke="green" x1="0" y1="44" x2="6" y2="44"/>
  <line stroke="red" x1="25" y1="37" x2="22" y2="40"/>
  <line stroke="red" x1="25" y1="37" x2="28" y2="40"/>
  <line stroke="green" x1="25" y1="37" x2="25" y2="50"/>
  <line stroke="green" x1="0" y1="45" x2="7" y2="45"/>
  <line stroke="red" x1="12" y1="44" x2="12" y2="50"/>
  <line stroke="red" x1="22" y1="40" x2="22" y2="50"/>
  <line stroke="green" x1="0" y1="46" x2="8" y2="46"/>
  <line stroke="green" x1="0" y1="47" x2="9" y2="47"/>
  <line stroke="red" x1="9" y1="47" x2="6" y2="50"/>
  <line stroke="red" x1="31" y1="37" x2="28" y2="40"/>
  <line stroke="red" x1="31" y1="37" x2="38" y2="44"/>
  <line stroke="green" x1="31" y1="37" x2="31" y2="50"/>
  <line stroke="red" x1="28" y1="40" x2="28" y2="50"/>
  <line stroke="green" x1="32" y1="38" x2="44" y2="38"/>
  <line stroke="green" x1="32" y1="38" x2="32" y2="50"/>
  <line stroke="green" x1="33" y1="39" x2="43" y2="39"/>
  <line stroke="green" x1="33" y1="39" x2="33" y2="50"/>
  <line stroke="green" x1="34" y1="40" x2="42" y2="40"/>
  <line stroke="green" x1="34" y1="40" x2="34" y2="50"/>
  <line stroke="green" x1="35" y1="41" x2="41" y2="41"/>
  <line stroke="green" x1="35" y1="41" x2="35" y2="50"/>
  <line stroke="green" x1="41" y1="41" x2="41" y2="50"/>
  <line stroke="green" x1="42" y1="40" x2="42" y2="46"/>
  <line stroke="green" x1="43" y1="39" x2="43" y2="45"/>
  <line stroke="red" x1="38" y1="44" x2="47" y2="35"/>
  <line stroke="red" x1="38" y1="44" x2="38" y2="50"/>
  <line stroke="green" x1="44" y1="38" x2="44" y2="44"/>
  <line stroke="green" x1="45" y1="37" x2="45" y2="43"/>
  <line stroke="green" x1="46" y1="36" x2="46" y2="42"/>
  <line stroke="green" x1="47" y1="35" x2="47" y2="41"/>
  <line stroke="red" x1="47" y1="35" x2="50" y2="38"/>
  <line stroke="green" x1="44" y1="44" x2="50" y2="44"/>
  <line stroke="green" x1="43" y1="45" x2="50" y2="45"/>
  <line stroke="green" x1="45" y1="43" x2="50" y2="43"/>
  <line stroke="green" x1="42" y1="46" x2="50" y2="46"/>
  <line stroke="green" x1="46" y1="42" x2="50" y2="42"/>
  <line stroke="red" x1="41" y1="47" x2="50" y2="38"/>
  <line stroke="red" x1="41" y1="47" x2="44" y2="50"/>
  <line stroke="green" x1="41" y1="47" x2="50" y2="47"/>
  <line stroke="green" x1="47" y1="41" x2="50" y2="41"/>
</svg>
""",
    base_svg="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50">
  <rect stroke="black" x="0" y="0" width="50" height="50"/>
  <line stroke="red" x1="1" y1="0" x2="1" y2="37" elevation="1"/>
  <line stroke="blue" x1="2" y1="0" x2="2" y2="36" elevation="0"/>
  <line stroke="blue" x1="0" y1="3" x2="1" y2="3"/>
  <line stroke="red" x1="3" y1="0" x2="3" y2="35" elevation="1"/>
  <line stroke="red" x1="1" y1="3" x2="2" y2="3"/>
  <line stroke="blue" x1="2" y1="3" x2="3" y2="3"/>
  <line stroke="blue" x1="4" y1="0" x2="4" y2="36" elevation="0"/>
  <line stroke="red" x1="3" y1="3" x2="4" y2="3"/>
  <line stroke="blue" x1="4" y1="3" x2="5" y2="3"/>
  <line stroke="red" x1="5" y1="0" x2="5" y2="37" elevation="1"/>
  <line stroke="red" x1="5" y1="3" x2="6" y2="3"/>
  <line stroke="blue" x1="6" y1="0" x2="6" y2="38" elevation="0"/>
  <line stroke="blue" x1="6" y1="3" x2="7" y2="3"/>
  <line stroke="red" x1="7" y1="0" x2="7" y2="39" elevation="1"/>
  <line stroke="red" x1="7" y1="3" x2="8" y2="3"/>
  <line stroke="blue" x1="8" y1="0" x2="8" y2="40" elevation="0"/>
  <line stroke="blue" x1="8" y1="3" x2="9" y2="3"/>
  <line stroke="red" x1="9" y1="0" x2="9" y2="41" elevation="1"/>
  <line stroke="red" x1="9" y1="3" x2="10" y2="3"/>
  <line stroke="blue" x1="10" y1="0" x2="10" y2="42" elevation="0"/>
  <line stroke="blue" x1="10" y1="3" x2="11" y2="3"/>
  <line stroke="red" x1="11" y1="0" x2="11" y2="43" elevation="1"/>
  <line stroke="red" x1="11" y1="3" x2="12" y2="3"/>
  <line stroke="blue" x1="12" y1="0" x2="12" y2="45" elevation="0"/>
  <line stroke="blue" x1="12" y1="3" x2="13" y2="3"/>
  <line stroke="red" x1="13" y1="0" x2="13" y2="43" elevation="1"/>
  <line stroke="red" x1="13" y1="3" x2="14" y2="3"/>
  <line stroke="red" x1="0" y1="14" x2="1" y2="14"/>
  <line stroke="blue" x1="14" y1="0" x2="14" y2="42" elevation="0"/>
  <line stroke="blue" x1="1" y1="14" x2="2" y2="14"/>
  <line stroke="red" x1="2" y1="14" x2="3" y2="14"/>
  <line stroke="blue" x1="3" y1="14" x2="4" y2="14"/>
  <line stroke="blue" x1="14" y1="3" x2="15" y2="3"/>
  <line stroke="red" x1="4" y1="14" x2="5" y2="14"/>
  <line stroke="blue" x1="5" y1="14" x2="6" y2="14"/>
  <line stroke="red" x1="15" y1="0" x2="15" y2="41" elevation="1"/>
  <line stroke="red" x1="6" y1="14" x2="7" y2="14"/>
  <line stroke="red" x1="15" y1="3" x2="16" y2="3"/>
  <line stroke="blue" x1="7" y1="14" x2="8" y2="14"/>
  <line stroke="blue" x1="16" y1="0" x2="16" y2="40" elevation="0"/>
  <line stroke="red" x1="8" y1="14" x2="9" y2="14"/>
  <line stroke="blue" x1="16" y1="3" x2="17" y2="3"/>
  <line stroke="blue" x1="9" y1="14" x2="10" y2="14"/>
  <line stroke="red" x1="17" y1="0" x2="17" y2="39" elevation="1"/>
  <line stroke="red" x1="10" y1="14" x2="11" y2="14"/>
  <line stroke="red" x1="17" y1="3" x2="18" y2="3"/>
  <line stroke="blue" x1="11" y1="14" x2="12" y2="14"/>
  <line stroke="blue" x1="18" y1="0" x2="18" y2="38" elevation="0"/>
  <line stroke="blue" x1="18" y1="3" x2="19" y2="3"/>
  <line stroke="red" x1="12" y1="14" x2="13" y2="14"/>
  <line stroke="red" x1="19" y1="0" x2="19" y2="37" elevation="1"/>
  <line stroke="blue" x1="13" y1="14" x2="14" y2="14"/>
  <line stroke="red" x1="19" y1="3" x2="20" y2="3"/>
  <line stroke="red" x1="14" y1="14" x2="15" y2="14"/>
  <line stroke="blue" x1="20" y1="0" x2="20" y2="38" elevation="0"/>
  <line stroke="blue" x1="20" y1="3" x2="21" y2="3"/>
  <line stroke="blue" x1="15" y1="14" x2="16" y2="14"/>
  <line stroke="red" x1="21" y1="0" x2="21" y2="39" elevation="1"/>
  <line stroke="red" x1="21" y1="3" x2="22" y2="3"/>
  <line stroke="red" x1="16" y1="14" x2="17" y2="14"/>
  <line stroke="red" x1="22" y1="0" x2="23" y2="1"/>
  <line stroke="blue" x1="22" y1="0" x2="22" y2="41" elevation="0"/>
  <line stroke="blue" x1="17" y1="14" x2="18" y2="14"/>
  <line stroke="blue" x1="22" y1="3" x2="23" y2="3"/>
  <line stroke="red" x1="18" y1="14" x2="19" y2="14"/>
  <line stroke="blue" x1="23" y1="1" x2="24" y2="2"/>
  <line stroke="red" x1="23" y1="1" x2="27" y2="1" elevation="1"/>
  <line stroke="red" x1="23" y1="1" x2="23" y2="29" elevation="1"/>
  <line stroke="red" x1="23" y1="3" x2="24" y2="3"/>
  <line stroke="blue" x1="19" y1="14" x2="20" y2="14"/>
  <line stroke="blue" x1="24" y1="0" x2="25" y2="1"/>
  <line stroke="red" x1="24" y1="2" x2="25" y2="1"/>
  <line stroke="blue" x1="24" y1="2" x2="26" y2="2" elevation="0"/>
  <line stroke="blue" x1="24" y1="2" x2="24" y2="28" elevation="0"/>
  <line stroke="blue" x1="24" y1="3" x2="26" y2="3"/>
  <line stroke="red" x1="20" y1="14" x2="21" y2="14"/>
  <line stroke="red" x1="0" y1="25" x2="1" y2="25"/>
  <line stroke="blue" x1="1" y1="25" x2="2" y2="25"/>
  <line stroke="blue" x1="25" y1="1" x2="26" y2="0"/>
  <line stroke="red" x1="25" y1="1" x2="26" y2="2"/>
  <line stroke="red" x1="2" y1="25" x2="3" y2="25"/>
  <line stroke="blue" x1="3" y1="25" x2="4" y2="25"/>
  <line stroke="blue" x1="21" y1="14" x2="22" y2="14"/>
  <line stroke="red" x1="4" y1="25" x2="5" y2="25"/>
  <line stroke="blue" x1="5" y1="25" x2="6" y2="25"/>
  <line stroke="red" x1="6" y1="25" x2="7" y2="25"/>
  <line stroke="blue" x1="7" y1="25" x2="8" y2="25"/>
  <line stroke="red" x1="22" y1="14" x2="23" y2="14"/>
  <line stroke="blue" x1="26" y1="2" x2="27" y2="1"/>
  <line stroke="blue" x1="26" y1="2" x2="26" y2="28" elevation="0"/>
  <line stroke="red" x1="26" y1="3" x2="27" y2="3"/>
  <line stroke="red" x1="8" y1="25" x2="9" y2="25"/>
  <line stroke="blue" x1="9" y1="25" x2="10" y2="25"/>
  <line stroke="red" x1="10" y1="25" x2="11" y2="25"/>
  <line stroke="blue" x1="23" y1="14" x2="24" y2="14"/>
  <line stroke="blue" x1="0" y1="27" x2="1" y2="27"/>
  <line stroke="red" x1="1" y1="27" x2="2" y2="27"/>
  <line stroke="red" x1="27" y1="1" x2="28" y2="0"/>
  <line stroke="red" x1="27" y1="1" x2="27" y2="29" elevation="1"/>
  <line stroke="blue" x1="2" y1="27" x2="3" y2="27"/>
  <line stroke="red" x1="3" y1="27" x2="4" y2="27"/>
  <line stroke="blue" x1="27" y1="3" x2="28" y2="3"/>
  <line stroke="blue" x1="4" y1="27" x2="5" y2="27"/>
  <line stroke="blue" x1="11" y1="25" x2="12" y2="25"/>
  <line stroke="red" x1="5" y1="27" x2="6" y2="27"/>
  <line stroke="blue" x1="6" y1="27" x2="7" y2="27"/>
  <line stroke="red" x1="12" y1="25" x2="13" y2="25"/>
  <line stroke="red" x1="24" y1="14" x2="26" y2="14"/>
  <line stroke="red" x1="7" y1="27" x2="8" y2="27"/>
  <line stroke="blue" x1="28" y1="0" x2="28" y2="41" elevation="0"/>
  <line stroke="blue" x1="8" y1="27" x2="9" y2="27"/>
  <line stroke="red" x1="28" y1="3" x2="29" y2="3"/>
  <line stroke="blue" x1="13" y1="25" x2="14" y2="25"/>
  <line stroke="red" x1="9" y1="27" x2="10" y2="27"/>
  <line stroke="red" x1="14" y1="25" x2="15" y2="25"/>
  <line stroke="blue" x1="10" y1="27" x2="11" y2="27"/>
  <line stroke="red" x1="29" y1="0" x2="29" y2="39" elevation="1"/>
  <line stroke="blue" x1="15" y1="25" x2="16" y2="25"/>
  <line stroke="blue" x1="29" y1="3" x2="30" y2="3"/>
  <line stroke="red" x1="11" y1="27" x2="12" y2="27"/>
  <line stroke="blue" x1="26" y1="14" x2="27" y2="14"/>
  <line stroke="blue" x1="12" y1="27" x2="13" y2="27"/>
  <line stroke="red" x1="16" y1="25" x2="17" y2="25"/>
  <line stroke="red" x1="13" y1="27" x2="14" y2="27"/>
  <line stroke="red" x1="0" y1="30" x2="1" y2="30"/>
  <line stroke="blue" x1="30" y1="0" x2="30" y2="38" elevation="0"/>
  <line stroke="blue" x1="1" y1="30" x2="2" y2="30"/>
  <line stroke="red" x1="2" y1="30" x2="3" y2="30"/>
  <line stroke="blue" x1="3" y1="30" x2="4" y2="30"/>
  <line stroke="red" x1="30" y1="3" x2="31" y2="3"/>
  <line stroke="blue" x1="17" y1="25" x2="18" y2="25"/>
  <line stroke="red" x1="4" y1="30" x2="5" y2="30"/>
  <line stroke="blue" x1="5" y1="30" x2="6" y2="30"/>
  <line stroke="blue" x1="14" y1="27" x2="15" y2="27"/>
  <line stroke="red" x1="27" y1="14" x2="28" y2="14"/>
  <line stroke="red" x1="6" y1="30" x2="7" y2="30"/>
  <line stroke="blue" x1="7" y1="30" x2="8" y2="30"/>
  <line stroke="red" x1="18" y1="25" x2="19" y2="25"/>
  <line stroke="red" x1="15" y1="27" x2="16" y2="27"/>
  <line stroke="red" x1="31" y1="0" x2="31" y2="37" elevation="1"/>
  <line stroke="red" x1="8" y1="30" x2="9" y2="30"/>
  <line stroke="blue" x1="31" y1="3" x2="32" y2="3"/>
  <line stroke="blue" x1="28" y1="14" x2="29" y2="14"/>
  <line stroke="blue" x1="9" y1="30" x2="10" y2="30"/>
  <line stroke="blue" x1="16" y1="27" x2="17" y2="27"/>
  <line stroke="blue" x1="19" y1="25" x2="20" y2="25"/>
  <line stroke="red" x1="10" y1="30" x2="11" y2="30"/>
  <line stroke="red" x1="17" y1="27" x2="18" y2="27"/>
  <line stroke="blue" x1="11" y1="30" x2="12" y2="30"/>
  <line stroke="blue" x1="32" y1="0" x2="32" y2="38" elevation="0"/>
  <line stroke="red" x1="20" y1="25" x2="21" y2="25"/>
  <line stroke="red" x1="32" y1="3" x2="33" y2="3"/>
  <line stroke="red" x1="29" y1="14" x2="30" y2="14"/>
  <line stroke="red" x1="12" y1="30" x2="13" y2="30"/>
  <line stroke="blue" x1="18" y1="27" x2="19" y2="27"/>
  <line stroke="blue" x1="21" y1="25" x2="22" y2="25"/>
  <line stroke="blue" x1="13" y1="30" x2="14" y2="30"/>
  <line stroke="red" x1="33" y1="0" x2="33" y2="39" elevation="1"/>
  <line stroke="red" x1="19" y1="27" x2="20" y2="27"/>
  <line stroke="red" x1="14" y1="30" x2="15" y2="30"/>
  <line stroke="blue" x1="30" y1="14" x2="31" y2="14"/>
  <line stroke="blue" x1="33" y1="3" x2="34" y2="3"/>
  <line stroke="red" x1="22" y1="25" x2="23" y2="25"/>
  <line stroke="blue" x1="15" y1="30" x2="16" y2="30"/>
  <line stroke="blue" x1="20" y1="27" x2="21" y2="27"/>
  <line stroke="blue" x1="23" y1="25" x2="24" y2="25"/>
  <line stroke="red" x1="16" y1="30" x2="17" y2="30"/>
  <line stroke="blue" x1="34" y1="0" x2="34" y2="40" elevation="0"/>
  <line stroke="red" x1="31" y1="14" x2="32" y2="14"/>
  <line stroke="red" x1="34" y1="3" x2="35" y2="3"/>
  <line stroke="red" x1="21" y1="27" x2="22" y2="27"/>
  <line stroke="blue" x1="17" y1="30" x2="18" y2="30"/>
  <line stroke="red" x1="24" y1="25" x2="26" y2="25"/>
  <line stroke="blue" x1="22" y1="27" x2="23" y2="27"/>
  <line stroke="blue" x1="32" y1="14" x2="33" y2="14"/>
  <line stroke="red" x1="18" y1="30" x2="19" y2="30"/>
  <line stroke="blue" x1="0" y1="35" x2="1" y2="35"/>
  <line stroke="red" x1="35" y1="0" x2="35" y2="41" elevation="1"/>
  <line stroke="red" x1="1" y1="35" x2="2" y2="35"/>
  <line stroke="blue" x1="2" y1="35" x2="3" y2="35"/>
  <line stroke="red" x1="3" y1="35" x2="2" y2="36"/>
  <line stroke="red" x1="3" y1="35" x2="4" y2="36"/>
  <line stroke="blue" x1="35" y1="3" x2="36" y2="3"/>
  <line stroke="red" x1="23" y1="27" x2="24" y2="27"/>
  <line stroke="blue" x1="19" y1="30" x2="20" y2="30"/>
  <line stroke="red" x1="33" y1="14" x2="34" y2="14"/>
  <line stroke="blue" x1="36" y1="0" x2="36" y2="42" elevation="0"/>
  <line stroke="blue" x1="2" y1="36" x2="4" y2="36" elevation="0"/>
  <line stroke="blue" x1="2" y1="36" x2="1" y2="37"/>
  <line stroke="red" x1="20" y1="30" x2="21" y2="30"/>
  <line stroke="blue" x1="26" y1="25" x2="27" y2="25"/>
  <line stroke="blue" x1="24" y1="27" x2="26" y2="27"/>
  <line stroke="red" x1="36" y1="3" x2="37" y2="3"/>
  <line stroke="blue" x1="4" y1="36" x2="5" y2="37"/>
  <line stroke="blue" x1="21" y1="30" x2="29" y2="30"/>
  <line stroke="blue" x1="34" y1="14" x2="35" y2="14"/>
  <line stroke="red" x1="27" y1="25" x2="28" y2="25"/>
  <line stroke="blue" x1="24" y1="28" x2="23" y2="29"/>
  <line stroke="red" x1="24" y1="28" x2="26" y2="28" elevation="0"/>
  <line stroke="blue" x1="24" y1="28" x2="25" y2="29"/>
  <line stroke="red" x1="37" y1="0" x2="37" y2="43" elevation="1"/>
  <line stroke="red" x1="1" y1="37" x2="5" y2="37" elevation="1"/>
  <line stroke="red" x1="1" y1="37" x2="0" y2="38"/>
  <line stroke="red" x1="23" y1="29" x2="22" y2="30"/>
  <line stroke="red" x1="23" y1="29" x2="27" y2="29" elevation="1"/>
  <line stroke="blue" x1="37" y1="3" x2="38" y2="3"/>
  <line stroke="red" x1="22" y1="30" x2="23" y2="31"/>
  <line stroke="red" x1="5" y1="37" x2="6" y2="38"/>
  <line stroke="red" x1="26" y1="27" x2="27" y2="27"/>
  <line stroke="blue" x1="28" y1="25" x2="29" y2="25"/>
  <line stroke="red" x1="35" y1="14" x2="36" y2="14"/>
  <line stroke="blue" x1="0" y1="38" x2="6" y2="38" elevation="0"/>
  <line stroke="red" x1="0" y1="38" x2="1" y2="39"/>
  <line stroke="blue" x1="38" y1="0" x2="38" y2="45" elevation="0"/>
  <line stroke="red" x1="38" y1="3" x2="39" y2="3"/>
  <line stroke="blue" x1="27" y1="27" x2="28" y2="27"/>
  <line stroke="blue" x1="26" y1="28" x2="25" y2="29"/>
  <line stroke="blue" x1="26" y1="28" x2="27" y2="29"/>
  <line stroke="red" x1="25" y1="29" x2="24" y2="30"/>
  <line stroke="red" x1="25" y1="29" x2="26" y2="30"/>
  <line stroke="red" x1="29" y1="25" x2="30" y2="25"/>
  <line stroke="blue" x1="24" y1="30" x2="25" y2="31"/>
  <line stroke="blue" x1="6" y1="38" x2="7" y2="39"/>
  <line stroke="blue" x1="23" y1="31" x2="24" y2="32"/>
  <line stroke="red" x1="23" y1="31" x2="27" y2="31" elevation="1"/>
  <line stroke="red" x1="23" y1="31" x2="23" y2="39" elevation="1"/>
  <line stroke="blue" x1="36" y1="14" x2="37" y2="14"/>
  <line stroke="red" x1="28" y1="27" x2="29" y2="27"/>
  <line stroke="red" x1="39" y1="0" x2="39" y2="43" elevation="1"/>
  <line stroke="red" x1="1" y1="39" x2="7" y2="39" elevation="1"/>
  <line stroke="blue" x1="1" y1="39" x2="2" y2="40"/>
  <line stroke="red" x1="1" y1="39" x2="1" y2="50" elevation="1"/>
  <line stroke="blue" x1="30" y1="25" x2="31" y2="25"/>
  <line stroke="blue" x1="39" y1="3" x2="40" y2="3"/>
  <line stroke="red" x1="37" y1="14" x2="38" y2="14"/>
  <line stroke="red" x1="7" y1="39" x2="8" y2="40"/>
  <line stroke="red" x1="27" y1="29" x2="28" y2="30"/>
  <line stroke="blue" x1="29" y1="27" x2="30" y2="27"/>
  <line stroke="blue" x1="26" y1="30" x2="25" y2="31"/>
  <line stroke="red" x1="25" y1="31" x2="24" y2="32"/>
  <line stroke="red" x1="25" y1="31" x2="26" y2="32"/>
  <line stroke="red" x1="31" y1="25" x2="32" y2="25"/>
  <line stroke="blue" x1="24" y1="32" x2="26" y2="32" elevation="0"/>
  <line stroke="blue" x1="24" y1="32" x2="24" y2="38" elevation="0"/>
  <line stroke="blue" x1="40" y1="0" x2="40" y2="42" elevation="0"/>
  <line stroke="blue" x1="2" y1="40" x2="8" y2="40" elevation="0"/>
  <line stroke="red" x1="2" y1="40" x2="3" y2="41"/>
  <line stroke="blue" x1="2" y1="40" x2="2" y2="50" elevation="0"/>
  <line stroke="red" x1="40" y1="3" x2="41" y2="3"/>
  <line stroke="red" x1="30" y1="27" x2="31" y2="27"/>
  <line stroke="blue" x1="38" y1="14" x2="39" y2="14"/>
  <line stroke="blue" x1="32" y1="25" x2="33" y2="25"/>
  <line stroke="blue" x1="8" y1="40" x2="9" y2="41"/>
  <line stroke="red" x1="41" y1="0" x2="41" y2="41" elevation="1"/>
  <line stroke="red" x1="28" y1="30" x2="27" y2="31"/>
  <line stroke="red" x1="3" y1="41" x2="9" y2="41" elevation="1"/>
  <line stroke="blue" x1="3" y1="41" x2="4" y2="42"/>
  <line stroke="red" x1="3" y1="41" x2="3" y2="50" elevation="1"/>
  <line stroke="blue" x1="41" y1="3" x2="42" y2="3"/>
  <line stroke="blue" x1="27" y1="31" x2="26" y2="32"/>
  <line stroke="red" x1="27" y1="31" x2="27" y2="39" elevation="1"/>
  <line stroke="blue" x1="31" y1="27" x2="32" y2="27"/>
  <line stroke="blue" x1="26" y1="32" x2="26" y2="38" elevation="0"/>
  <line stroke="red" x1="33" y1="25" x2="34" y2="25"/>
  <line stroke="red" x1="39" y1="14" x2="40" y2="14"/>
  <line stroke="red" x1="19" y1="37" x2="18" y2="38"/>
  <line stroke="blue" x1="19" y1="37" x2="19" y2="38"/>
  <line stroke="red" x1="19" y1="37" x2="20" y2="38"/>
  <line stroke="red" x1="29" y1="30" x2="30" y2="30"/>
  <line stroke="red" x1="32" y1="27" x2="33" y2="27"/>
  <line stroke="red" x1="9" y1="41" x2="10" y2="42"/>
  <line stroke="blue" x1="42" y1="0" x2="42" y2="40" elevation="0"/>
  <line stroke="blue" x1="18" y1="38" x2="17" y2="39"/>
  <line stroke="blue" x1="18" y1="38" x2="20" y2="38" elevation="0"/>
  <line stroke="red" x1="42" y1="3" x2="43" y2="3"/>
  <line stroke="blue" x1="4" y1="42" x2="10" y2="42" elevation="0"/>
  <line stroke="red" x1="4" y1="42" x2="5" y2="43"/>
  <line stroke="blue" x1="4" y1="42" x2="4" y2="50" elevation="0"/>
  <line stroke="blue" x1="34" y1="25" x2="35" y2="25"/>
  <line stroke="blue" x1="40" y1="14" x2="41" y2="14"/>
  <line stroke="blue" x1="30" y1="30" x2="31" y2="30"/>
  <line stroke="red" x1="19" y1="38" x2="19" y2="39"/>
  <line stroke="red" x1="17" y1="39" x2="16" y2="40"/>
  <line stroke="red" x1="17" y1="39" x2="21" y2="39" elevation="1"/>
  <line stroke="blue" x1="33" y1="27" x2="34" y2="27"/>
  <line stroke="blue" x1="20" y1="38" x2="21" y2="39"/>
  <line stroke="red" x1="43" y1="0" x2="43" y2="39" elevation="1"/>
  <line stroke="red" x1="35" y1="25" x2="36" y2="25"/>
  <line stroke="blue" x1="16" y1="40" x2="15" y2="41"/>
  <line stroke="blue" x1="16" y1="40" x2="34" y2="40" elevation="0"/>
  <line stroke="blue" x1="43" y1="3" x2="44" y2="3"/>
  <line stroke="red" x1="31" y1="30" x2="32" y2="30"/>
  <line stroke="blue" x1="10" y1="42" x2="11" y2="43"/>
  <line stroke="red" x1="5" y1="43" x2="11" y2="43" elevation="1"/>
  <line stroke="blue" x1="5" y1="43" x2="6" y2="44"/>
  <line stroke="red" x1="5" y1="43" x2="5" y2="50" elevation="1"/>
  <line stroke="red" x1="41" y1="14" x2="42" y2="14"/>
  <line stroke="blue" x1="19" y1="39" x2="19" y2="40"/>
  <line stroke="red" x1="34" y1="27" x2="35" y2="27"/>
  <line stroke="red" x1="15" y1="41" x2="14" y2="42"/>
  <line stroke="red" x1="15" y1="41" x2="35" y2="41" elevation="1"/>
  <line stroke="blue" x1="36" y1="25" x2="37" y2="25"/>
  <line stroke="blue" x1="32" y1="30" x2="33" y2="30"/>
  <line stroke="blue" x1="44" y1="0" x2="44" y2="38" elevation="0"/>
  <line stroke="red" x1="44" y1="3" x2="45" y2="3"/>
  <line stroke="blue" x1="35" y1="27" x2="36" y2="27"/>
  <line stroke="blue" x1="14" y1="42" x2="13" y2="43"/>
  <line stroke="blue" x1="14" y1="42" x2="36" y2="42" elevation="0"/>
  <line stroke="blue" x1="42" y1="14" x2="43" y2="14"/>
  <line stroke="red" x1="19" y1="40" x2="19" y2="41"/>
  <line stroke="red" x1="21" y1="39" x2="22" y2="40"/>
  <line stroke="red" x1="11" y1="43" x2="12" y2="44"/>
  <line stroke="red" x1="6" y1="44" x2="7" y2="45"/>
  <line stroke="blue" x1="6" y1="44" x2="6" y2="50" elevation="0"/>
  <line stroke="blue" x1="6" y1="44" x2="44" y2="44" elevation="0"/>
  <line stroke="red" x1="33" y1="30" x2="34" y2="30"/>
  <line stroke="red" x1="37" y1="25" x2="38" y2="25"/>
  <line stroke="red" x1="13" y1="43" x2="12" y2="44"/>
  <line stroke="red" x1="13" y1="43" x2="37" y2="43" elevation="1"/>
  <line stroke="blue" x1="24" y1="38" x2="23" y2="39"/>
  <line stroke="blue" x1="24" y1="38" x2="26" y2="38" elevation="0"/>
  <line stroke="red" x1="24" y1="38" x2="25" y2="39"/>
  <line stroke="red" x1="36" y1="27" x2="37" y2="27"/>
  <line stroke="red" x1="45" y1="0" x2="45" y2="37" elevation="1"/>
  <line stroke="blue" x1="45" y1="3" x2="46" y2="3"/>
  <line stroke="blue" x1="19" y1="41" x2="19" y2="42"/>
  <line stroke="red" x1="43" y1="14" x2="44" y2="14"/>
  <line stroke="red" x1="23" y1="39" x2="22" y2="40"/>
  <line stroke="red" x1="23" y1="39" x2="27" y2="39" elevation="1"/>
  <line stroke="blue" x1="34" y1="30" x2="35" y2="30"/>
  <line stroke="blue" x1="38" y1="25" x2="39" y2="25"/>
  <line stroke="blue" x1="7" y1="45" x2="8" y2="46"/>
  <line stroke="red" x1="7" y1="45" x2="7" y2="49" elevation="1"/>
  <line stroke="red" x1="7" y1="45" x2="43" y2="45" elevation="1"/>
  <line stroke="blue" x1="37" y1="27" x2="38" y2="27"/>
  <line stroke="blue" x1="46" y1="0" x2="46" y2="36" elevation="0"/>
  <line stroke="red" x1="26" y1="38" x2="25" y2="39"/>
  <line stroke="blue" x1="26" y1="38" x2="27" y2="39"/>
  <line stroke="red" x1="19" y1="42" x2="19" y2="43"/>
  <line stroke="red" x1="35" y1="30" x2="36" y2="30"/>
  <line stroke="red" x1="46" y1="3" x2="47" y2="3"/>
  <line stroke="blue" x1="44" y1="14" x2="45" y2="14"/>
  <line stroke="blue" x1="25" y1="39" x2="24" y2="40"/>
  <line stroke="blue" x1="25" y1="39" x2="26" y2="40"/>
  <line stroke="red" x1="39" y1="25" x2="40" y2="25"/>
  <line stroke="red" x1="22" y1="41" x2="22" y2="42"/>
  <line stroke="red" x1="12" y1="45" x2="12" y2="46"/>
  <line stroke="red" x1="38" y1="27" x2="39" y2="27"/>
  <line stroke="red" x1="24" y1="40" x2="25" y2="41"/>
  <line stroke="red" x1="8" y1="46" x2="9" y2="47"/>
  <line stroke="blue" x1="8" y1="46" x2="8" y2="48" elevation="0"/>
  <line stroke="blue" x1="8" y1="46" x2="42" y2="46" elevation="0"/>
  <line stroke="blue" x1="36" y1="30" x2="37" y2="30"/>
  <line stroke="red" x1="47" y1="0" x2="47" y2="35" elevation="1"/>
  <line stroke="blue" x1="19" y1="43" x2="19" y2="44"/>
  <line stroke="blue" x1="47" y1="3" x2="48" y2="3"/>
  <line stroke="red" x1="45" y1="14" x2="46" y2="14"/>
  <line stroke="blue" x1="40" y1="25" x2="41" y2="25"/>
  <line stroke="blue" x1="22" y1="42" x2="22" y2="43"/>
  <line stroke="red" x1="27" y1="39" x2="28" y2="40"/>
  <line stroke="blue" x1="39" y1="27" x2="40" y2="27"/>
  <line stroke="blue" x1="12" y1="46" x2="12" y2="47"/>
  <line stroke="red" x1="37" y1="30" x2="38" y2="30"/>
  <line stroke="red" x1="26" y1="40" x2="25" y2="41"/>
  <line stroke="red" x1="9" y1="47" x2="8" y2="48"/>
  <line stroke="blue" x1="9" y1="47" x2="9" y2="48"/>
  <line stroke="red" x1="9" y1="47" x2="41" y2="47" elevation="1"/>
  <line stroke="red" x1="19" y1="44" x2="19" y2="45"/>
  <line stroke="blue" x1="48" y1="0" x2="48" y2="36" elevation="0"/>
  <line stroke="blue" x1="25" y1="41" x2="24" y2="42"/>
  <line stroke="blue" x1="25" y1="41" x2="26" y2="42"/>
  <line stroke="red" x1="41" y1="25" x2="42" y2="25"/>
  <line stroke="blue" x1="46" y1="14" x2="47" y2="14"/>
  <line stroke="red" x1="48" y1="3" x2="49" y2="3"/>
  <line stroke="red" x1="40" y1="27" x2="41" y2="27"/>
  <line stroke="red" x1="31" y1="37" x2="30" y2="38"/>
  <line stroke="blue" x1="31" y1="37" x2="31" y2="38"/>
  <line stroke="red" x1="31" y1="37" x2="32" y2="38"/>
  <line stroke="red" x1="22" y1="43" x2="22" y2="44"/>
  <line stroke="red" x1="24" y1="42" x2="25" y2="43"/>
  <line stroke="blue" x1="30" y1="38" x2="29" y2="39"/>
  <line stroke="blue" x1="30" y1="38" x2="32" y2="38" elevation="0"/>
  <line stroke="blue" x1="38" y1="30" x2="39" y2="30"/>
  <line stroke="red" x1="12" y1="47" x2="12" y2="48"/>
  <line stroke="red" x1="29" y1="39" x2="28" y2="40"/>
  <line stroke="red" x1="29" y1="39" x2="33" y2="39" elevation="1"/>
  <line stroke="blue" x1="8" y1="48" x2="7" y2="49"/>
  <line stroke="blue" x1="8" y1="48" x2="42" y2="48" elevation="0"/>
  <line stroke="red" x1="9" y1="48" x2="9" y2="49"/>
  <line stroke="blue" x1="19" y1="45" x2="19" y2="46"/>
  <line stroke="blue" x1="42" y1="25" x2="43" y2="25"/>
  <line stroke="red" x1="49" y1="0" x2="49" y2="37" elevation="1"/>
  <line stroke="red" x1="31" y1="38" x2="31" y2="39"/>
  <line stroke="red" x1="47" y1="14" x2="48" y2="14"/>
  <line stroke="blue" x1="41" y1="27" x2="42" y2="27"/>
  <line stroke="blue" x1="49" y1="3" x2="50" y2="3"/>
  <line stroke="blue" x1="22" y1="44" x2="22" y2="45"/>
  <line stroke="red" x1="39" y1="30" x2="40" y2="30"/>
  <line stroke="red" x1="26" y1="42" x2="25" y2="43"/>
  <line stroke="blue" x1="12" y1="48" x2="12" y2="49"/>
  <line stroke="red" x1="7" y1="49" x2="6" y2="50"/>
  <line stroke="red" x1="7" y1="49" x2="43" y2="49" elevation="1"/>
  <line stroke="red" x1="28" y1="41" x2="28" y2="42"/>
  <line stroke="blue" x1="32" y1="38" x2="33" y2="39"/>
  <line stroke="blue" x1="25" y1="43" x2="24" y2="44"/>
  <line stroke="blue" x1="25" y1="43" x2="26" y2="44"/>
  <line stroke="red" x1="43" y1="25" x2="44" y2="25"/>
  <line stroke="red" x1="19" y1="46" x2="19" y2="47"/>
  <line stroke="blue" x1="9" y1="49" x2="9" y2="50"/>
  <line stroke="blue" x1="31" y1="39" x2="31" y2="40"/>
  <line stroke="red" x1="42" y1="27" x2="43" y2="27"/>
  <line stroke="blue" x1="40" y1="30" x2="41" y2="30"/>
  <line stroke="blue" x1="48" y1="14" x2="49" y2="14"/>
  <line stroke="red" x1="22" y1="45" x2="22" y2="46"/>
  <line stroke="red" x1="24" y1="44" x2="25" y2="45"/>
  <line stroke="red" x1="12" y1="49" x2="12" y2="50"/>
  <line stroke="blue" x1="28" y1="42" x2="28" y2="43"/>
  <line stroke="red" x1="31" y1="40" x2="31" y2="41"/>
  <line stroke="blue" x1="44" y1="25" x2="45" y2="25"/>
  <line stroke="blue" x1="19" y1="47" x2="19" y2="48"/>
  <line stroke="blue" x1="43" y1="27" x2="44" y2="27"/>
  <line stroke="red" x1="41" y1="30" x2="42" y2="30"/>
  <line stroke="red" x1="49" y1="14" x2="50" y2="14"/>
  <line stroke="blue" x1="22" y1="46" x2="22" y2="47"/>
  <line stroke="red" x1="33" y1="39" x2="34" y2="40"/>
  <line stroke="red" x1="26" y1="44" x2="25" y2="45"/>
  <line stroke="red" x1="28" y1="43" x2="28" y2="44"/>
  <line stroke="blue" x1="31" y1="41" x2="31" y2="42"/>
  <line stroke="blue" x1="25" y1="45" x2="24" y2="46"/>
  <line stroke="blue" x1="25" y1="45" x2="26" y2="46"/>
  <line stroke="red" x1="45" y1="25" x2="46" y2="25"/>
  <line stroke="blue" x1="42" y1="30" x2="43" y2="30"/>
  <line stroke="red" x1="19" y1="48" x2="19" y2="49"/>
  <line stroke="red" x1="44" y1="27" x2="45" y2="27"/>
  <line stroke="red" x1="24" y1="46" x2="25" y2="47"/>
  <line stroke="red" x1="22" y1="47" x2="22" y2="48"/>
  <line stroke="blue" x1="28" y1="44" x2="28" y2="45"/>
  <line stroke="red" x1="31" y1="42" x2="31" y2="43"/>
  <line stroke="blue" x1="46" y1="25" x2="47" y2="25"/>
  <line stroke="red" x1="43" y1="30" x2="44" y2="30"/>
  <line stroke="blue" x1="45" y1="27" x2="46" y2="27"/>
  <line stroke="blue" x1="34" y1="40" x2="35" y2="41"/>
  <line stroke="blue" x1="19" y1="49" x2="19" y2="50"/>
  <line stroke="blue" x1="22" y1="48" x2="22" y2="49"/>
  <line stroke="red" x1="26" y1="46" x2="25" y2="47"/>
  <line stroke="red" x1="28" y1="45" x2="28" y2="46"/>
  <line stroke="blue" x1="31" y1="43" x2="31" y2="44"/>
  <line stroke="blue" x1="25" y1="47" x2="24" y2="48"/>
  <line stroke="blue" x1="25" y1="47" x2="26" y2="48"/>
  <line stroke="red" x1="47" y1="25" x2="48" y2="25"/>
  <line stroke="blue" x1="44" y1="30" x2="45" y2="30"/>
  <line stroke="red" x1="46" y1="27" x2="47" y2="27"/>
  <line stroke="red" x1="24" y1="48" x2="25" y2="49"/>
  <line stroke="red" x1="22" y1="49" x2="22" y2="50"/>
  <line stroke="red" x1="31" y1="44" x2="31" y2="45"/>
  <line stroke="blue" x1="28" y1="46" x2="28" y2="47"/>
  <line stroke="red" x1="35" y1="41" x2="36" y2="42"/>
  <line stroke="red" x1="45" y1="30" x2="46" y2="30"/>
  <line stroke="blue" x1="48" y1="25" x2="49" y2="25"/>
  <line stroke="blue" x1="47" y1="27" x2="48" y2="27"/>
  <line stroke="red" x1="26" y1="48" x2="25" y2="49"/>
  <line stroke="blue" x1="31" y1="45" x2="31" y2="46"/>
  <line stroke="red" x1="28" y1="47" x2="28" y2="48"/>
  <line stroke="blue" x1="46" y1="30" x2="47" y2="30"/>
  <line stroke="blue" x1="25" y1="49" x2="24" y2="50"/>
  <line stroke="blue" x1="25" y1="49" x2="26" y2="50"/>
  <line stroke="red" x1="49" y1="25" x2="50" y2="25"/>
  <line stroke="red" x1="48" y1="27" x2="49" y2="27"/>
  <line stroke="blue" x1="36" y1="42" x2="37" y2="43"/>
  <line stroke="red" x1="31" y1="46" x2="31" y2="47"/>
  <line stroke="blue" x1="28" y1="48" x2="28" y2="49"/>
  <line stroke="red" x1="47" y1="30" x2="48" y2="30"/>
  <line stroke="blue" x1="49" y1="27" x2="50" y2="27"/>
  <line stroke="blue" x1="31" y1="47" x2="31" y2="48"/>
  <line stroke="red" x1="28" y1="49" x2="28" y2="50"/>
  <line stroke="blue" x1="48" y1="30" x2="49" y2="30"/>
  <line stroke="red" x1="37" y1="43" x2="38" y2="44"/>
  <line stroke="red" x1="31" y1="48" x2="31" y2="49"/>
  <line stroke="red" x1="49" y1="30" x2="50" y2="30"/>
  <line stroke="blue" x1="31" y1="49" x2="31" y2="50"/>
  <line stroke="red" x1="41" y1="41" x2="40" y2="42"/>
  <line stroke="blue" x1="41" y1="41" x2="42" y2="40"/>
  <line stroke="red" x1="41" y1="41" x2="47" y2="41" elevation="1"/>
  <line stroke="blue" x1="40" y1="42" x2="39" y2="43"/>
  <line stroke="blue" x1="40" y1="42" x2="46" y2="42" elevation="0"/>
  <line stroke="red" x1="42" y1="40" x2="43" y2="39"/>
  <line stroke="blue" x1="42" y1="40" x2="48" y2="40" elevation="0"/>
  <line stroke="red" x1="39" y1="43" x2="38" y2="44"/>
  <line stroke="red" x1="39" y1="43" x2="45" y2="43" elevation="1"/>
  <line stroke="blue" x1="43" y1="39" x2="44" y2="38"/>
  <line stroke="red" x1="43" y1="39" x2="49" y2="39" elevation="1"/>
  <line stroke="red" x1="44" y1="38" x2="45" y2="37"/>
  <line stroke="blue" x1="44" y1="38" x2="50" y2="38" elevation="0"/>
  <line stroke="blue" x1="45" y1="37" x2="46" y2="36"/>
  <line stroke="red" x1="45" y1="37" x2="49" y2="37" elevation="1"/>
  <line stroke="red" x1="46" y1="36" x2="47" y2="35"/>
  <line stroke="blue" x1="46" y1="36" x2="48" y2="36" elevation="0"/>
  <line stroke="blue" x1="47" y1="35" x2="48" y2="35"/>
  <line stroke="red" x1="47" y1="35" x2="48" y2="36"/>
  <line stroke="red" x1="38" y1="45" x2="38" y2="46"/>
  <line stroke="red" x1="48" y1="35" x2="49" y2="35"/>
  <line stroke="blue" x1="38" y1="46" x2="38" y2="47"/>
  <line stroke="blue" x1="48" y1="36" x2="49" y2="37"/>
  <line stroke="blue" x1="49" y1="35" x2="50" y2="35"/>
  <line stroke="red" x1="38" y1="47" x2="38" y2="48"/>
  <line stroke="blue" x1="38" y1="48" x2="38" y2="49"/>
  <line stroke="red" x1="49" y1="37" x2="50" y2="38"/>
  <line stroke="red" x1="38" y1="49" x2="38" y2="50"/>
  <line stroke="red" x1="44" y1="44" x2="43" y2="45"/>
  <line stroke="blue" x1="44" y1="44" x2="45" y2="43"/>
  <line stroke="blue" x1="44" y1="44" x2="44" y2="50" elevation="0"/>
  <line stroke="blue" x1="43" y1="45" x2="42" y2="46"/>
  <line stroke="red" x1="43" y1="45" x2="43" y2="49" elevation="1"/>
  <line stroke="red" x1="45" y1="43" x2="46" y2="42"/>
  <line stroke="red" x1="45" y1="43" x2="45" y2="50" elevation="1"/>
  <line stroke="red" x1="42" y1="46" x2="41" y2="47"/>
  <line stroke="blue" x1="42" y1="46" x2="42" y2="48" elevation="0"/>
  <line stroke="blue" x1="46" y1="42" x2="47" y2="41"/>
  <line stroke="blue" x1="46" y1="42" x2="46" y2="50" elevation="0"/>
  <line stroke="blue" x1="41" y1="47" x2="41" y2="48"/>
  <line stroke="red" x1="41" y1="47" x2="42" y2="48"/>
  <line stroke="red" x1="47" y1="41" x2="48" y2="40"/>
  <line stroke="red" x1="47" y1="41" x2="47" y2="50" elevation="1"/>
  <line stroke="blue" x1="48" y1="40" x2="49" y2="39"/>
  <line stroke="blue" x1="48" y1="40" x2="48" y2="50" elevation="0"/>
  <line stroke="red" x1="49" y1="39" x2="50" y2="38"/>
  <line stroke="red" x1="49" y1="39" x2="49" y2="50" elevation="1"/>
  <line stroke="red" x1="41" y1="48" x2="41" y2="49"/>
  <line stroke="blue" x1="42" y1="48" x2="43" y2="49"/>
  <line stroke="blue" x1="41" y1="49" x2="41" y2="50"/>
  <line stroke="red" x1="43" y1="49" x2="44" y2="50"/>
</svg>
""",
)

SCORPION_WIDE_STANCE = BoxPleatingCreasePatternExample(
    name="scorpion_wide_stance",
    grid_size=48,
    packing_svg="""\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <line stroke="black" x1="0" y1="0" x2="0" y2="3"/>
  <line stroke="black" x1="0" y1="0" x2="14" y2="0"/>
  <line stroke="black" x1="0" y1="3" x2="0" y2="8"/>
  <line stroke="red" x1="0" y1="3" x2="11" y2="3"/>
  <line stroke="black" x1="0" y1="8" x2="0" y2="10"/>
  <line stroke="green" x1="0" y1="8" x2="16" y2="8"/>
  <line stroke="black" x1="0" y1="10" x2="0" y2="15"/>
  <line stroke="green" x1="0" y1="10" x2="24" y2="10"/>
  <line stroke="red" x1="11" y1="3" x2="14" y2="0"/>
  <line stroke="red" x1="11" y1="3" x2="16" y2="8"/>
  <line stroke="black" x1="14" y1="0" x2="16" y2="0"/>
  <line stroke="black" x1="0" y1="15" x2="0" y2="20"/>
  <line stroke="red" x1="0" y1="15" x2="19" y2="15"/>
  <line stroke="green" x1="16" y1="0" x2="16" y2="8"/>
  <line stroke="black" x1="16" y1="0" x2="24" y2="0"/>
  <line stroke="red" x1="16" y1="8" x2="24" y2="0"/>
  <line stroke="green" x1="16" y1="8" x2="32" y2="8"/>
  <line stroke="black" x1="0" y1="20" x2="0" y2="21"/>
  <line stroke="green" x1="0" y1="20" x2="24" y2="20"/>
  <line stroke="black" x1="0" y1="21" x2="0" y2="22"/>
  <line stroke="green" x1="0" y1="21" x2="48" y2="21"/>
  <line stroke="black" x1="0" y1="22" x2="0" y2="27"/>
  <line stroke="green" x1="0" y1="22" x2="24" y2="22"/>
  <line stroke="black" x1="24" y1="0" x2="32" y2="0"/>
  <line stroke="red" x1="24" y1="0" x2="32" y2="8"/>
  <line stroke="red" x1="19" y1="15" x2="24" y2="10"/>
  <line stroke="red" x1="19" y1="15" x2="24" y2="20"/>
  <line stroke="green" x1="24" y1="10" x2="24" y2="20"/>
  <line stroke="red" x1="24" y1="10" x2="29" y2="15"/>
  <line stroke="green" x1="24" y1="10" x2="48" y2="10"/>
  <line stroke="black" x1="0" y1="27" x2="0" y2="32"/>
  <line stroke="red" x1="0" y1="27" x2="19" y2="27"/>
  <line stroke="red" x1="24" y1="20" x2="29" y2="15"/>
  <line stroke="green" x1="24" y1="20" x2="48" y2="20"/>
  <line stroke="black" x1="0" y1="32" x2="0" y2="33"/>
  <line stroke="green" x1="0" y1="32" x2="24" y2="32"/>
  <line stroke="green" x1="32" y1="0" x2="32" y2="8"/>
  <line stroke="black" x1="32" y1="0" x2="34" y2="0"/>
  <line stroke="red" x1="24" y1="22" x2="19" y2="27"/>
  <line stroke="red" x1="24" y1="22" x2="29" y2="27"/>
  <line stroke="green" x1="24" y1="22" x2="24" y2="32"/>
  <line stroke="green" x1="24" y1="22" x2="48" y2="22"/>
  <line stroke="red" x1="29" y1="15" x2="48" y2="15"/>
  <line stroke="red" x1="32" y1="8" x2="37" y2="3"/>
  <line stroke="green" x1="32" y1="8" x2="48" y2="8"/>
  <line stroke="black" x1="0" y1="33" x2="0" y2="34"/>
  <line stroke="green" x1="0" y1="33" x2="48" y2="33"/>
  <line stroke="red" x1="19" y1="27" x2="24" y2="32"/>
  <line stroke="black" x1="0" y1="34" x2="0" y2="35"/>
  <line stroke="green" x1="0" y1="34" x2="14" y2="34"/>
  <line stroke="red" x1="34" y1="0" x2="37" y2="3"/>
  <line stroke="black" x1="34" y1="0" x2="48" y2="0"/>
  <line stroke="black" x1="0" y1="35" x2="0" y2="36"/>
  <line stroke="green" x1="0" y1="35" x2="13" y2="35"/>
  <line stroke="black" x1="0" y1="36" x2="0" y2="37"/>
  <line stroke="green" x1="0" y1="36" x2="12" y2="36"/>
  <line stroke="red" x1="14" y1="34" x2="13" y2="35"/>
  <line stroke="green" x1="14" y1="34" x2="24" y2="34"/>
  <line stroke="red" x1="14" y1="34" x2="19" y2="39"/>
  <line stroke="green" x1="14" y1="34" x2="14" y2="48"/>
  <line stroke="black" x1="0" y1="37" x2="0" y2="38"/>
  <line stroke="green" x1="0" y1="37" x2="11" y2="37"/>
  <line stroke="red" x1="37" y1="3" x2="48" y2="3"/>
  <line stroke="red" x1="13" y1="35" x2="12" y2="36"/>
  <line stroke="green" x1="13" y1="35" x2="13" y2="48"/>
  <line stroke="red" x1="12" y1="36" x2="11" y2="37"/>
  <line stroke="green" x1="12" y1="36" x2="12" y2="48"/>
  <line stroke="black" x1="0" y1="38" x2="0" y2="39"/>
  <line stroke="green" x1="0" y1="38" x2="10" y2="38"/>
  <line stroke="red" x1="11" y1="37" x2="10" y2="38"/>
  <line stroke="green" x1="11" y1="37" x2="11" y2="48"/>
  <line stroke="green" x1="0" y1="39" x2="9" y2="39"/>
  <line stroke="black" x1="0" y1="39" x2="0" y2="42"/>
  <line stroke="red" x1="10" y1="38" x2="9" y2="39"/>
  <line stroke="green" x1="10" y1="38" x2="10" y2="48"/>
  <line stroke="red" x1="29" y1="27" x2="24" y2="32"/>
  <line stroke="red" x1="29" y1="27" x2="48" y2="27"/>
  <line stroke="green" x1="24" y1="32" x2="48" y2="32"/>
  <line stroke="red" x1="9" y1="39" x2="6" y2="42"/>
  <line stroke="green" x1="9" y1="39" x2="9" y2="45"/>
  <line stroke="red" x1="24" y1="34" x2="19" y2="39"/>
  <line stroke="green" x1="24" y1="34" x2="34" y2="34"/>
  <line stroke="red" x1="24" y1="34" x2="29" y2="39"/>
  <line stroke="green" x1="24" y1="34" x2="24" y2="48"/>
  <line stroke="red" x1="0" y1="42" x2="6" y2="42"/>
  <line stroke="black" x1="0" y1="42" x2="0" y2="45"/>
  <line stroke="red" x1="6" y1="42" x2="9" y2="45"/>
  <line stroke="red" x1="19" y1="39" x2="19" y2="48"/>
  <line stroke="green" x1="0" y1="45" x2="9" y2="45"/>
  <line stroke="black" x1="0" y1="45" x2="0" y2="48"/>
  <line stroke="red" x1="9" y1="45" x2="6" y2="48"/>
  <line stroke="green" x1="9" y1="45" x2="9" y2="48"/>
  <line stroke="black" x1="0" y1="48" x2="6" y2="48"/>
  <line stroke="black" x1="48" y1="0" x2="48" y2="3"/>
  <line stroke="red" x1="34" y1="34" x2="29" y2="39"/>
  <line stroke="red" x1="34" y1="34" x2="35" y2="35"/>
  <line stroke="green" x1="34" y1="34" x2="34" y2="48"/>
  <line stroke="green" x1="34" y1="34" x2="48" y2="34"/>
  <line stroke="black" x1="48" y1="3" x2="48" y2="8"/>
  <line stroke="black" x1="6" y1="48" x2="9" y2="48"/>
  <line stroke="red" x1="29" y1="39" x2="29" y2="48"/>
  <line stroke="black" x1="48" y1="8" x2="48" y2="10"/>
  <line stroke="black" x1="9" y1="48" x2="10" y2="48"/>
  <line stroke="black" x1="10" y1="48" x2="11" y2="48"/>
  <line stroke="black" x1="48" y1="10" x2="48" y2="15"/>
  <line stroke="black" x1="11" y1="48" x2="12" y2="48"/>
  <line stroke="black" x1="12" y1="48" x2="13" y2="48"/>
  <line stroke="red" x1="35" y1="35" x2="36" y2="36"/>
  <line stroke="green" x1="35" y1="35" x2="35" y2="48"/>
  <line stroke="green" x1="35" y1="35" x2="48" y2="35"/>
  <line stroke="black" x1="13" y1="48" x2="14" y2="48"/>
  <line stroke="black" x1="14" y1="48" x2="19" y2="48"/>
  <line stroke="black" x1="48" y1="15" x2="48" y2="20"/>
  <line stroke="red" x1="36" y1="36" x2="37" y2="37"/>
  <line stroke="green" x1="36" y1="36" x2="36" y2="48"/>
  <line stroke="green" x1="36" y1="36" x2="48" y2="36"/>
  <line stroke="black" x1="19" y1="48" x2="24" y2="48"/>
  <line stroke="black" x1="48" y1="20" x2="48" y2="21"/>
  <line stroke="red" x1="37" y1="37" x2="38" y2="38"/>
  <line stroke="green" x1="37" y1="37" x2="37" y2="48"/>
  <line stroke="green" x1="37" y1="37" x2="48" y2="37"/>
  <line stroke="black" x1="48" y1="21" x2="48" y2="22"/>
  <line stroke="black" x1="48" y1="22" x2="48" y2="27"/>
  <line stroke="black" x1="24" y1="48" x2="29" y2="48"/>
  <line stroke="red" x1="38" y1="38" x2="39" y2="39"/>
  <line stroke="green" x1="38" y1="38" x2="38" y2="48"/>
  <line stroke="green" x1="38" y1="38" x2="48" y2="38"/>
  <line stroke="black" x1="48" y1="27" x2="48" y2="32"/>
  <line stroke="red" x1="39" y1="39" x2="42" y2="42"/>
  <line stroke="green" x1="39" y1="39" x2="39" y2="45"/>
  <line stroke="green" x1="39" y1="39" x2="48" y2="39"/>
  <line stroke="black" x1="29" y1="48" x2="34" y2="48"/>
  <line stroke="black" x1="48" y1="32" x2="48" y2="33"/>
  <line stroke="black" x1="48" y1="33" x2="48" y2="34"/>
  <line stroke="black" x1="34" y1="48" x2="35" y2="48"/>
  <line stroke="black" x1="48" y1="34" x2="48" y2="35"/>
  <line stroke="red" x1="42" y1="42" x2="39" y2="45"/>
  <line stroke="red" x1="42" y1="42" x2="48" y2="42"/>
  <line stroke="black" x1="35" y1="48" x2="36" y2="48"/>
  <line stroke="black" x1="48" y1="35" x2="48" y2="36"/>
  <line stroke="green" x1="39" y1="45" x2="39" y2="48"/>
  <line stroke="red" x1="39" y1="45" x2="42" y2="48"/>
  <line stroke="green" x1="39" y1="45" x2="48" y2="45"/>
  <line stroke="black" x1="36" y1="48" x2="37" y2="48"/>
  <line stroke="black" x1="48" y1="36" x2="48" y2="37"/>
  <line stroke="black" x1="37" y1="48" x2="38" y2="48"/>
  <line stroke="black" x1="48" y1="37" x2="48" y2="38"/>
  <line stroke="black" x1="38" y1="48" x2="39" y2="48"/>
  <line stroke="black" x1="48" y1="38" x2="48" y2="39"/>
  <line stroke="black" x1="39" y1="48" x2="42" y2="48"/>
  <line stroke="black" x1="48" y1="39" x2="48" y2="42"/>
  <line stroke="black" x1="42" y1="48" x2="48" y2="48"/>
  <line stroke="black" x1="48" y1="42" x2="48" y2="45"/>
  <line stroke="black" x1="48" y1="45" x2="48" y2="48"/>
</svg>
""",
    base_svg="""\
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
    <line stroke="black" x1="0" y1="0" x2="1" y2="0"/>
    <line stroke="black" x1="0" y1="0" x2="0" y2="3"/>
    <line stroke="black" x1="1" y1="0" x2="2" y2="0"/>
    <line stroke="red" x1="1" y1="0" x2="1" y2="3" elevation="1"/>
    <line stroke="black" x1="2" y1="0" x2="3" y2="0"/>
    <line stroke="blue" x1="2" y1="0" x2="2" y2="3" elevation="0"/>
    <line stroke="red" x1="0" y1="3" x2="1" y2="3"/>
    <line stroke="black" x1="0" y1="3" x2="0" y2="10"/>
    <line stroke="black" x1="3" y1="0" x2="4" y2="0"/>
    <line stroke="red" x1="3" y1="0" x2="3" y2="3" elevation="1"/>
    <line stroke="blue" x1="1" y1="3" x2="2" y2="3"/>
    <line stroke="red" x1="1" y1="3" x2="1" y2="10" elevation="1"/>
    <line stroke="red" x1="2" y1="3" x2="3" y2="3"/>
    <line stroke="blue" x1="2" y1="3" x2="2" y2="10" elevation="0"/>
    <line stroke="blue" x1="4" y1="0" x2="4" y2="3" elevation="0"/>
    <line stroke="black" x1="4" y1="0" x2="5" y2="0"/>
    <line stroke="blue" x1="3" y1="3" x2="4" y2="3"/>
    <line stroke="red" x1="3" y1="3" x2="3" y2="10" elevation="1"/>
    <line stroke="red" x1="4" y1="3" x2="5" y2="3"/>
    <line stroke="blue" x1="4" y1="3" x2="4" y2="10" elevation="0"/>
    <line stroke="red" x1="5" y1="0" x2="5" y2="3" elevation="1"/>
    <line stroke="black" x1="5" y1="0" x2="6" y2="0"/>
    <line stroke="blue" x1="5" y1="3" x2="6" y2="3"/>
    <line stroke="red" x1="5" y1="3" x2="5" y2="10" elevation="1"/>
    <line stroke="blue" x1="6" y1="0" x2="6" y2="3" elevation="0"/>
    <line stroke="black" x1="6" y1="0" x2="7" y2="0"/>
    <line stroke="red" x1="6" y1="3" x2="7" y2="3"/>
    <line stroke="blue" x1="6" y1="3" x2="6" y2="10" elevation="0"/>
    <line stroke="red" x1="7" y1="0" x2="7" y2="3" elevation="1"/>
    <line stroke="black" x1="7" y1="0" x2="8" y2="0"/>
    <line stroke="blue" x1="7" y1="3" x2="8" y2="3"/>
    <line stroke="red" x1="7" y1="3" x2="7" y2="10" elevation="1"/>
    <line stroke="blue" x1="8" y1="0" x2="8" y2="3" elevation="0"/>
    <line stroke="black" x1="8" y1="0" x2="9" y2="0"/>
    <line stroke="red" x1="8" y1="3" x2="9" y2="3"/>
    <line stroke="blue" x1="8" y1="3" x2="8" y2="10" elevation="0"/>
    <line stroke="red" x1="9" y1="0" x2="9" y2="3" elevation="1"/>
    <line stroke="black" x1="9" y1="0" x2="10" y2="0"/>
    <line stroke="blue" x1="9" y1="3" x2="10" y2="3"/>
    <line stroke="red" x1="9" y1="3" x2="9" y2="10" elevation="1"/>
    <line stroke="blue" x1="0" y1="10" x2="1" y2="10"/>
    <line stroke="black" x1="0" y1="10" x2="0" y2="15"/>
    <line stroke="blue" x1="10" y1="0" x2="10" y2="3" elevation="0"/>
    <line stroke="black" x1="10" y1="0" x2="11" y2="0"/>
    <line stroke="red" x1="1" y1="10" x2="2" y2="10"/>
    <line stroke="red" x1="1" y1="10" x2="1" y2="15" elevation="1"/>
    <line stroke="blue" x1="2" y1="10" x2="3" y2="10"/>
    <line stroke="blue" x1="2" y1="10" x2="2" y2="15" elevation="0"/>
    <line stroke="red" x1="3" y1="10" x2="4" y2="10"/>
    <line stroke="red" x1="3" y1="10" x2="3" y2="15" elevation="1"/>
    <line stroke="red" x1="10" y1="3" x2="11" y2="3"/>
    <line stroke="blue" x1="10" y1="3" x2="10" y2="10" elevation="0"/>
    <line stroke="blue" x1="4" y1="10" x2="5" y2="10"/>
    <line stroke="blue" x1="4" y1="10" x2="4" y2="15" elevation="0"/>
    <line stroke="red" x1="11" y1="0" x2="11" y2="3" elevation="1"/>
    <line stroke="black" x1="11" y1="0" x2="12" y2="0"/>
    <line stroke="red" x1="5" y1="10" x2="6" y2="10"/>
    <line stroke="red" x1="5" y1="10" x2="5" y2="15" elevation="1"/>
    <line stroke="blue" x1="11" y1="3" x2="12" y2="2"/>
    <line stroke="blue" x1="11" y1="3" x2="12" y2="4"/>
    <line stroke="red" x1="11" y1="3" x2="11" y2="10" elevation="1"/>
    <line stroke="red" x1="11" y1="3" x2="21" y2="3"/>
    <line stroke="blue" x1="6" y1="10" x2="7" y2="10"/>
    <line stroke="blue" x1="6" y1="10" x2="6" y2="15" elevation="0"/>
    <line stroke="blue" x1="12" y1="0" x2="12" y2="2" elevation="0"/>
    <line stroke="black" x1="12" y1="0" x2="13" y2="0"/>
    <line stroke="red" x1="12" y1="2" x2="13" y2="1"/>
    <line stroke="blue" x1="12" y1="2" x2="22" y2="2" elevation="0"/>
    <line stroke="red" x1="7" y1="10" x2="8" y2="10"/>
    <line stroke="red" x1="7" y1="10" x2="7" y2="15" elevation="1"/>
    <line stroke="red" x1="12" y1="4" x2="13" y2="5"/>
    <line stroke="blue" x1="12" y1="4" x2="12" y2="10" elevation="0"/>
    <line stroke="blue" x1="12" y1="4" x2="20" y2="4" elevation="0"/>
    <line stroke="blue" x1="8" y1="10" x2="9" y2="10"/>
    <line stroke="blue" x1="8" y1="10" x2="8" y2="15" elevation="0"/>
    <line stroke="red" x1="13" y1="0" x2="13" y2="1" elevation="1"/>
    <line stroke="black" x1="13" y1="0" x2="14" y2="0"/>
    <line stroke="blue" x1="13" y1="1" x2="14" y2="0"/>
    <line stroke="red" x1="13" y1="1" x2="23" y2="1" elevation="1"/>
    <line stroke="red" x1="9" y1="10" x2="10" y2="10"/>
    <line stroke="red" x1="9" y1="10" x2="9" y2="15" elevation="1"/>
    <line stroke="blue" x1="13" y1="5" x2="14" y2="6"/>
    <line stroke="red" x1="13" y1="5" x2="13" y2="10" elevation="1"/>
    <line stroke="red" x1="13" y1="5" x2="19" y2="5" elevation="1"/>
    <line stroke="black" x1="14" y1="0" x2="24" y2="0"/>
    <line stroke="blue" x1="10" y1="10" x2="11" y2="10"/>
    <line stroke="blue" x1="10" y1="10" x2="10" y2="15" elevation="0"/>
    <line stroke="red" x1="11" y1="10" x2="12" y2="10"/>
    <line stroke="red" x1="11" y1="10" x2="11" y2="15" elevation="1"/>
    <line stroke="red" x1="0" y1="15" x2="1" y2="15"/>
    <line stroke="black" x1="0" y1="15" x2="0" y2="22"/>
    <line stroke="blue" x1="1" y1="15" x2="2" y2="15"/>
    <line stroke="red" x1="1" y1="15" x2="1" y2="22" elevation="1"/>
    <line stroke="red" x1="2" y1="15" x2="3" y2="15"/>
    <line stroke="blue" x1="2" y1="15" x2="2" y2="22" elevation="0"/>
    <line stroke="red" x1="14" y1="6" x2="15" y2="7"/>
    <line stroke="blue" x1="14" y1="6" x2="14" y2="10" elevation="0"/>
    <line stroke="blue" x1="14" y1="6" x2="18" y2="6" elevation="0"/>
    <line stroke="blue" x1="3" y1="15" x2="4" y2="15"/>
    <line stroke="red" x1="3" y1="15" x2="3" y2="22" elevation="1"/>
    <line stroke="red" x1="4" y1="15" x2="5" y2="15"/>
    <line stroke="blue" x1="4" y1="15" x2="4" y2="22" elevation="0"/>
    <line stroke="blue" x1="12" y1="10" x2="13" y2="10"/>
    <line stroke="blue" x1="12" y1="10" x2="12" y2="15" elevation="0"/>
    <line stroke="blue" x1="5" y1="15" x2="6" y2="15"/>
    <line stroke="red" x1="5" y1="15" x2="5" y2="22" elevation="1"/>
    <line stroke="red" x1="6" y1="15" x2="7" y2="15"/>
    <line stroke="blue" x1="6" y1="15" x2="6" y2="22" elevation="0"/>
    <line stroke="red" x1="13" y1="10" x2="14" y2="10"/>
    <line stroke="red" x1="13" y1="10" x2="13" y2="15" elevation="1"/>
    <line stroke="blue" x1="7" y1="15" x2="8" y2="15"/>
    <line stroke="red" x1="7" y1="15" x2="7" y2="22" elevation="1"/>
    <line stroke="blue" x1="15" y1="7" x2="16" y2="8"/>
    <line stroke="red" x1="15" y1="7" x2="15" y2="10" elevation="1"/>
    <line stroke="red" x1="15" y1="7" x2="17" y2="7" elevation="1"/>
    <line stroke="red" x1="8" y1="15" x2="9" y2="15"/>
    <line stroke="blue" x1="8" y1="15" x2="8" y2="22" elevation="0"/>
    <line stroke="blue" x1="14" y1="10" x2="15" y2="10"/>
    <line stroke="blue" x1="14" y1="10" x2="14" y2="15" elevation="0"/>
    <line stroke="blue" x1="9" y1="15" x2="10" y2="15"/>
    <line stroke="red" x1="9" y1="15" x2="9" y2="22" elevation="1"/>
    <line stroke="blue" x1="16" y1="8" x2="17" y2="7"/>
    <line stroke="red" x1="16" y1="8" x2="17" y2="8"/>
    <line stroke="blue" x1="16" y1="8" x2="16" y2="10" elevation="0"/>
    <line stroke="red" x1="10" y1="15" x2="11" y2="15"/>
    <line stroke="blue" x1="10" y1="15" x2="10" y2="22" elevation="0"/>
    <line stroke="red" x1="15" y1="10" x2="16" y2="10"/>
    <line stroke="red" x1="15" y1="10" x2="15" y2="15" elevation="1"/>
    <line stroke="red" x1="17" y1="7" x2="17" y2="8" elevation="1"/>
    <line stroke="red" x1="17" y1="7" x2="18" y2="6"/>
    <line stroke="blue" x1="11" y1="15" x2="12" y2="15"/>
    <line stroke="red" x1="11" y1="15" x2="11" y2="22" elevation="1"/>
    <line stroke="blue" x1="17" y1="8" x2="18" y2="8"/>
    <line stroke="red" x1="17" y1="8" x2="17" y2="10" elevation="1"/>
    <line stroke="blue" x1="16" y1="10" x2="17" y2="10"/>
    <line stroke="blue" x1="16" y1="10" x2="16" y2="15" elevation="0"/>
    <line stroke="blue" x1="18" y1="6" x2="19" y2="5"/>
    <line stroke="blue" x1="18" y1="6" x2="18" y2="8" elevation="0"/>
    <line stroke="red" x1="12" y1="15" x2="13" y2="15"/>
    <line stroke="blue" x1="12" y1="15" x2="12" y2="22" elevation="0"/>
    <line stroke="red" x1="19" y1="5" x2="20" y2="4"/>
    <line stroke="red" x1="19" y1="5" x2="19" y2="8" elevation="1"/>
    <line stroke="blue" x1="18" y1="8" x2="18" y2="10" elevation="0"/>
    <line stroke="red" x1="18" y1="8" x2="19" y2="8"/>
    <line stroke="red" x1="17" y1="10" x2="18" y2="10"/>
    <line stroke="red" x1="17" y1="10" x2="17" y2="15" elevation="1"/>
    <line stroke="blue" x1="13" y1="15" x2="14" y2="15"/>
    <line stroke="red" x1="13" y1="15" x2="13" y2="22" elevation="1"/>
    <line stroke="blue" x1="20" y1="4" x2="21" y2="3"/>
    <line stroke="blue" x1="20" y1="4" x2="20" y2="8" elevation="0"/>
    <line stroke="red" x1="14" y1="15" x2="15" y2="15"/>
    <line stroke="blue" x1="14" y1="15" x2="14" y2="22" elevation="0"/>
    <line stroke="blue" x1="18" y1="10" x2="19" y2="10"/>
    <line stroke="blue" x1="18" y1="10" x2="18" y2="15" elevation="0"/>
    <line stroke="red" x1="19" y1="8" x2="19" y2="10" elevation="1"/>
    <line stroke="blue" x1="19" y1="8" x2="20" y2="8"/>
    <line stroke="blue" x1="15" y1="15" x2="16" y2="15"/>
    <line stroke="red" x1="15" y1="15" x2="15" y2="22" elevation="1"/>
    <line stroke="red" x1="21" y1="3" x2="22" y2="2"/>
    <line stroke="red" x1="21" y1="3" x2="21" y2="8" elevation="1"/>
    <line stroke="red" x1="19" y1="10" x2="20" y2="10"/>
    <line stroke="red" x1="19" y1="10" x2="19" y2="15" elevation="1"/>
    <line stroke="blue" x1="20" y1="8" x2="20" y2="10" elevation="0"/>
    <line stroke="red" x1="20" y1="8" x2="21" y2="8"/>
    <line stroke="red" x1="16" y1="15" x2="17" y2="15"/>
    <line stroke="blue" x1="16" y1="15" x2="16" y2="22" elevation="0"/>
    <line stroke="blue" x1="0" y1="22" x2="1" y2="22"/>
    <line stroke="black" x1="0" y1="22" x2="0" y2="27"/>
    <line stroke="red" x1="1" y1="22" x2="2" y2="22"/>
    <line stroke="red" x1="1" y1="22" x2="1" y2="27" elevation="1"/>
    <line stroke="blue" x1="2" y1="22" x2="3" y2="22"/>
    <line stroke="blue" x1="2" y1="22" x2="2" y2="27" elevation="0"/>
    <line stroke="blue" x1="22" y1="2" x2="23" y2="1"/>
    <line stroke="blue" x1="22" y1="2" x2="22" y2="8" elevation="0"/>
    <line stroke="red" x1="3" y1="22" x2="4" y2="22"/>
    <line stroke="red" x1="3" y1="22" x2="3" y2="27" elevation="1"/>
    <line stroke="blue" x1="4" y1="22" x2="5" y2="22"/>
    <line stroke="blue" x1="4" y1="22" x2="4" y2="27" elevation="0"/>
    <line stroke="blue" x1="20" y1="10" x2="21" y2="10"/>
    <line stroke="blue" x1="20" y1="10" x2="20" y2="14" elevation="0"/>
    <line stroke="red" x1="21" y1="8" x2="21" y2="10" elevation="1"/>
    <line stroke="blue" x1="21" y1="8" x2="22" y2="8"/>
    <line stroke="red" x1="5" y1="22" x2="6" y2="22"/>
    <line stroke="red" x1="5" y1="22" x2="5" y2="27" elevation="1"/>
    <line stroke="blue" x1="17" y1="15" x2="18" y2="15"/>
    <line stroke="red" x1="17" y1="15" x2="17" y2="22" elevation="1"/>
    <line stroke="blue" x1="6" y1="22" x2="7" y2="22"/>
    <line stroke="blue" x1="6" y1="22" x2="6" y2="27" elevation="0"/>
    <line stroke="red" x1="23" y1="1" x2="24" y2="0"/>
    <line stroke="red" x1="23" y1="1" x2="23" y2="8" elevation="1"/>
    <line stroke="red" x1="7" y1="22" x2="8" y2="22"/>
    <line stroke="red" x1="7" y1="22" x2="7" y2="27" elevation="1"/>
    <line stroke="red" x1="21" y1="10" x2="22" y2="10"/>
    <line stroke="red" x1="21" y1="10" x2="21" y2="13" elevation="1"/>
    <line stroke="blue" x1="8" y1="22" x2="9" y2="22"/>
    <line stroke="blue" x1="8" y1="22" x2="8" y2="27" elevation="0"/>
    <line stroke="blue" x1="22" y1="8" x2="22" y2="10" elevation="0"/>
    <line stroke="red" x1="22" y1="8" x2="23" y2="8"/>
    <line stroke="red" x1="18" y1="15" x2="19" y2="15"/>
    <line stroke="blue" x1="18" y1="15" x2="18" y2="22" elevation="0"/>
    <line stroke="red" x1="9" y1="22" x2="10" y2="22"/>
    <line stroke="red" x1="9" y1="22" x2="9" y2="27" elevation="1"/>
    <line stroke="red" x1="24" y1="0" x2="25" y2="1"/>
    <line stroke="black" x1="24" y1="0" x2="34" y2="0"/>
    <line stroke="blue" x1="10" y1="22" x2="11" y2="22"/>
    <line stroke="blue" x1="10" y1="22" x2="10" y2="27" elevation="0"/>
    <line stroke="blue" x1="22" y1="10" x2="22" y2="12" elevation="0"/>
    <line stroke="blue" x1="22" y1="10" x2="23" y2="10"/>
    <line stroke="blue" x1="19" y1="15" x2="20" y2="14"/>
    <line stroke="blue" x1="19" y1="15" x2="20" y2="16"/>
    <line stroke="red" x1="19" y1="15" x2="23" y2="15"/>
    <line stroke="red" x1="19" y1="15" x2="19" y2="22" elevation="1"/>
    <line stroke="red" x1="23" y1="8" x2="23" y2="10" elevation="1"/>
    <line stroke="blue" x1="23" y1="8" x2="25" y2="8"/>
    <line stroke="red" x1="20" y1="14" x2="21" y2="13"/>
    <line stroke="blue" x1="20" y1="14" x2="24" y2="14" elevation="0"/>
    <line stroke="red" x1="11" y1="22" x2="12" y2="22"/>
    <line stroke="red" x1="11" y1="22" x2="11" y2="27" elevation="1"/>
    <line stroke="blue" x1="21" y1="13" x2="22" y2="12"/>
    <line stroke="red" x1="21" y1="13" x2="23" y2="13" elevation="1"/>
    <line stroke="blue" x1="25" y1="1" x2="26" y2="2"/>
    <line stroke="red" x1="25" y1="1" x2="25" y2="8" elevation="1"/>
    <line stroke="red" x1="25" y1="1" x2="35" y2="1" elevation="1"/>
    <line stroke="blue" x1="12" y1="22" x2="13" y2="22"/>
    <line stroke="blue" x1="12" y1="22" x2="12" y2="27" elevation="0"/>
    <line stroke="red" x1="22" y1="12" x2="23" y2="11"/>
    <line stroke="blue" x1="22" y1="12" x2="24" y2="12" elevation="0"/>
    <line stroke="red" x1="23" y1="10" x2="23" y2="11" elevation="1"/>
    <line stroke="red" x1="23" y1="10" x2="25" y2="10"/>
    <line stroke="red" x1="23" y1="11" x2="24" y2="12"/>
    <line stroke="blue" x1="23" y1="11" x2="25" y2="11" elevation="1"/>
    <line stroke="red" x1="13" y1="22" x2="14" y2="22"/>
    <line stroke="red" x1="13" y1="22" x2="13" y2="27" elevation="1"/>
    <line stroke="red" x1="20" y1="16" x2="21" y2="17"/>
    <line stroke="blue" x1="20" y1="16" x2="24" y2="16" elevation="0"/>
    <line stroke="blue" x1="20" y1="16" x2="20" y2="22" elevation="0"/>
    <line stroke="red" x1="26" y1="2" x2="27" y2="3"/>
    <line stroke="blue" x1="26" y1="2" x2="26" y2="8" elevation="0"/>
    <line stroke="blue" x1="26" y1="2" x2="36" y2="2" elevation="0"/>
    <line stroke="blue" x1="14" y1="22" x2="15" y2="22"/>
    <line stroke="blue" x1="14" y1="22" x2="14" y2="27" elevation="0"/>
    <line stroke="red" x1="25" y1="8" x2="25" y2="10" elevation="1"/>
    <line stroke="red" x1="25" y1="8" x2="26" y2="8"/>
    <line stroke="blue" x1="23" y1="13" x2="24" y2="12"/>
    <line stroke="red" x1="23" y1="13" x2="24" y2="14"/>
    <line stroke="red" x1="23" y1="13" x2="25" y2="13" elevation="1"/>
    <line stroke="red" x1="15" y1="22" x2="16" y2="22"/>
    <line stroke="red" x1="15" y1="22" x2="15" y2="27" elevation="1"/>
    <line stroke="red" x1="24" y1="12" x2="25" y2="11"/>
    <line stroke="blue" x1="24" y1="12" x2="25" y2="13"/>
    <line stroke="blue" x1="24" y1="12" x2="26" y2="12" elevation="0"/>
    <line stroke="red" x1="25" y1="10" x2="25" y2="11" elevation="1"/>
    <line stroke="blue" x1="25" y1="10" x2="26" y2="10"/>
    <line stroke="red" x1="0" y1="27" x2="1" y2="27"/>
    <line stroke="black" x1="0" y1="27" x2="0" y2="34"/>
    <line stroke="blue" x1="1" y1="27" x2="2" y2="27"/>
    <line stroke="red" x1="1" y1="27" x2="1" y2="34" elevation="1"/>
    <line stroke="blue" x1="21" y1="17" x2="22" y2="18"/>
    <line stroke="red" x1="21" y1="17" x2="23" y2="17" elevation="1"/>
    <line stroke="red" x1="21" y1="17" x2="21" y2="22" elevation="1"/>
    <line stroke="red" x1="2" y1="27" x2="3" y2="27"/>
    <line stroke="blue" x1="2" y1="27" x2="2" y2="34" elevation="0"/>
    <line stroke="blue" x1="3" y1="27" x2="4" y2="27"/>
    <line stroke="red" x1="3" y1="27" x2="3" y2="34" elevation="1"/>
    <line stroke="red" x1="27" y1="3" x2="27" y2="8" elevation="1"/>
    <line stroke="blue" x1="27" y1="3" x2="28" y2="4"/>
    <line stroke="red" x1="27" y1="3" x2="37" y2="3" elevation="1"/>
    <line stroke="blue" x1="16" y1="22" x2="17" y2="22"/>
    <line stroke="blue" x1="16" y1="22" x2="16" y2="27" elevation="0"/>
    <line stroke="blue" x1="26" y1="8" x2="26" y2="10" elevation="0"/>
    <line stroke="blue" x1="26" y1="8" x2="27" y2="8"/>
    <line stroke="red" x1="4" y1="27" x2="5" y2="27"/>
    <line stroke="blue" x1="4" y1="27" x2="4" y2="34" elevation="0"/>
    <line stroke="red" x1="25" y1="11" x2="26" y2="12"/>
    <line stroke="blue" x1="5" y1="27" x2="6" y2="27"/>
    <line stroke="red" x1="5" y1="27" x2="5" y2="34" elevation="1"/>
    <line stroke="blue" x1="23" y1="15" x2="24" y2="14"/>
    <line stroke="red" x1="23" y1="15" x2="24" y2="16"/>
    <line stroke="red" x1="23" y1="15" x2="25" y2="15"/>
    <line stroke="red" x1="6" y1="27" x2="7" y2="27"/>
    <line stroke="blue" x1="6" y1="27" x2="6" y2="34" elevation="0"/>
    <line stroke="red" x1="24" y1="14" x2="25" y2="13"/>
    <line stroke="blue" x1="24" y1="14" x2="25" y2="15"/>
    <line stroke="blue" x1="24" y1="14" x2="28" y2="14" elevation="0"/>
    <line stroke="red" x1="17" y1="22" x2="18" y2="22"/>
    <line stroke="red" x1="17" y1="22" x2="17" y2="27" elevation="1"/>
    <line stroke="blue" x1="26" y1="10" x2="26" y2="12" elevation="0"/>
    <line stroke="red" x1="26" y1="10" x2="27" y2="10"/>
    <line stroke="blue" x1="7" y1="27" x2="8" y2="27"/>
    <line stroke="red" x1="7" y1="27" x2="7" y2="34" elevation="1"/>
    <line stroke="red" x1="8" y1="27" x2="9" y2="27"/>
    <line stroke="blue" x1="8" y1="27" x2="8" y2="34" elevation="0"/>
    <line stroke="red" x1="27" y1="8" x2="27" y2="10" elevation="1"/>
    <line stroke="red" x1="27" y1="8" x2="28" y2="8"/>
    <line stroke="red" x1="25" y1="13" x2="27" y2="13" elevation="1"/>
    <line stroke="blue" x1="28" y1="4" x2="28" y2="8" elevation="0"/>
    <line stroke="red" x1="28" y1="4" x2="29" y2="5"/>
    <line stroke="blue" x1="28" y1="4" x2="36" y2="4" elevation="0"/>
    <line stroke="blue" x1="18" y1="22" x2="19" y2="22"/>
    <line stroke="blue" x1="18" y1="22" x2="18" y2="27" elevation="0"/>
    <line stroke="red" x1="22" y1="18" x2="23" y2="19"/>
    <line stroke="blue" x1="22" y1="18" x2="24" y2="18" elevation="0"/>
    <line stroke="blue" x1="22" y1="18" x2="22" y2="22" elevation="0"/>
    <line stroke="blue" x1="9" y1="27" x2="10" y2="27"/>
    <line stroke="red" x1="9" y1="27" x2="9" y2="34" elevation="1"/>
    <line stroke="blue" x1="23" y1="17" x2="24" y2="16"/>
    <line stroke="red" x1="23" y1="17" x2="24" y2="18"/>
    <line stroke="red" x1="23" y1="17" x2="25" y2="17" elevation="1"/>
    <line stroke="blue" x1="26" y1="12" x2="27" y2="13"/>
    <line stroke="red" x1="10" y1="27" x2="11" y2="27"/>
    <line stroke="blue" x1="10" y1="27" x2="10" y2="34" elevation="0"/>
    <line stroke="blue" x1="27" y1="10" x2="28" y2="10"/>
    <line stroke="red" x1="27" y1="10" x2="27" y2="13" elevation="1"/>
    <line stroke="red" x1="24" y1="16" x2="25" y2="15"/>
    <line stroke="blue" x1="24" y1="16" x2="25" y2="17"/>
    <line stroke="blue" x1="24" y1="16" x2="28" y2="16" elevation="0"/>
    <line stroke="red" x1="19" y1="22" x2="20" y2="22"/>
    <line stroke="red" x1="19" y1="22" x2="19" y2="27" elevation="1"/>
    <line stroke="blue" x1="28" y1="8" x2="28" y2="10" elevation="0"/>
    <line stroke="blue" x1="28" y1="8" x2="29" y2="8"/>
    <line stroke="blue" x1="11" y1="27" x2="12" y2="27"/>
    <line stroke="red" x1="11" y1="27" x2="11" y2="34" elevation="1"/>
    <line stroke="red" x1="25" y1="15" x2="29" y2="15"/>
    <line stroke="red" x1="29" y1="5" x2="29" y2="8" elevation="1"/>
    <line stroke="blue" x1="29" y1="5" x2="30" y2="6"/>
    <line stroke="red" x1="29" y1="5" x2="35" y2="5" elevation="1"/>
    <line stroke="red" x1="12" y1="27" x2="13" y2="27"/>
    <line stroke="blue" x1="12" y1="27" x2="12" y2="34" elevation="0"/>
    <line stroke="blue" x1="20" y1="22" x2="21" y2="22"/>
    <line stroke="blue" x1="20" y1="22" x2="20" y2="26" elevation="0"/>
    <line stroke="red" x1="28" y1="10" x2="29" y2="10"/>
    <line stroke="blue" x1="28" y1="10" x2="28" y2="14" elevation="0"/>
    <line stroke="blue" x1="23" y1="19" x2="24" y2="18"/>
    <line stroke="red" x1="23" y1="19" x2="25" y2="19" elevation="1"/>
    <line stroke="red" x1="23" y1="19" x2="23" y2="22" elevation="1"/>
    <line stroke="blue" x1="13" y1="27" x2="14" y2="27"/>
    <line stroke="red" x1="13" y1="27" x2="13" y2="34" elevation="1"/>
    <line stroke="red" x1="27" y1="13" x2="28" y2="14"/>
    <line stroke="red" x1="24" y1="18" x2="25" y2="17"/>
    <line stroke="blue" x1="24" y1="18" x2="25" y2="19"/>
    <line stroke="blue" x1="24" y1="18" x2="26" y2="18" elevation="0"/>
    <line stroke="red" x1="29" y1="8" x2="29" y2="10" elevation="1"/>
    <line stroke="red" x1="29" y1="8" x2="30" y2="8"/>
    <line stroke="red" x1="25" y1="17" x2="27" y2="17" elevation="1"/>
    <line stroke="red" x1="21" y1="22" x2="22" y2="22"/>
    <line stroke="red" x1="21" y1="22" x2="21" y2="25" elevation="1"/>
    <line stroke="red" x1="14" y1="27" x2="15" y2="27"/>
    <line stroke="blue" x1="14" y1="27" x2="14" y2="34" elevation="0"/>
    <line stroke="blue" x1="30" y1="6" x2="30" y2="8" elevation="0"/>
    <line stroke="red" x1="30" y1="6" x2="31" y2="7"/>
    <line stroke="blue" x1="30" y1="6" x2="34" y2="6" elevation="0"/>
    <line stroke="blue" x1="29" y1="10" x2="30" y2="10"/>
    <line stroke="red" x1="29" y1="10" x2="29" y2="15" elevation="1"/>
    <line stroke="blue" x1="15" y1="27" x2="16" y2="27"/>
    <line stroke="red" x1="15" y1="27" x2="15" y2="35" elevation="1"/>
    <line stroke="blue" x1="30" y1="8" x2="30" y2="10" elevation="0"/>
    <line stroke="blue" x1="30" y1="8" x2="31" y2="8"/>
    <line stroke="blue" x1="22" y1="22" x2="23" y2="22"/>
    <line stroke="blue" x1="22" y1="22" x2="22" y2="24" elevation="0"/>
    <line stroke="blue" x1="28" y1="14" x2="29" y2="15"/>
    <line stroke="red" x1="16" y1="27" x2="17" y2="27"/>
    <line stroke="blue" x1="16" y1="27" x2="16" y2="36" elevation="0"/>
    <line stroke="red" x1="25" y1="19" x2="26" y2="18"/>
    <line stroke="red" x1="25" y1="19" x2="25" y2="22" elevation="1"/>
    <line stroke="blue" x1="26" y1="18" x2="27" y2="17"/>
    <line stroke="blue" x1="26" y1="18" x2="26" y2="22" elevation="0"/>
    <line stroke="red" x1="30" y1="10" x2="31" y2="10"/>
    <line stroke="blue" x1="30" y1="10" x2="30" y2="15" elevation="0"/>
    <line stroke="red" x1="31" y1="7" x2="31" y2="8" elevation="1"/>
    <line stroke="blue" x1="31" y1="7" x2="32" y2="8"/>
    <line stroke="red" x1="31" y1="7" x2="33" y2="7" elevation="1"/>
    <line stroke="red" x1="23" y1="22" x2="23" y2="23" elevation="1"/>
    <line stroke="red" x1="23" y1="22" x2="25" y2="22"/>
    <line stroke="blue" x1="17" y1="27" x2="18" y2="27"/>
    <line stroke="red" x1="17" y1="27" x2="17" y2="37" elevation="1"/>
    <line stroke="red" x1="27" y1="17" x2="28" y2="16"/>
    <line stroke="red" x1="27" y1="17" x2="27" y2="22" elevation="1"/>
    <line stroke="red" x1="31" y1="8" x2="31" y2="10" elevation="1"/>
    <line stroke="red" x1="31" y1="8" x2="32" y2="8"/>
    <line stroke="blue" x1="28" y1="16" x2="29" y2="15"/>
    <line stroke="blue" x1="28" y1="16" x2="28" y2="22" elevation="0"/>
    <line stroke="red" x1="18" y1="27" x2="19" y2="27"/>
    <line stroke="blue" x1="18" y1="27" x2="18" y2="38" elevation="0"/>
    <line stroke="red" x1="23" y1="23" x2="22" y2="24"/>
    <line stroke="red" x1="23" y1="23" x2="24" y2="24"/>
    <line stroke="blue" x1="23" y1="23" x2="25" y2="23" elevation="1"/>
    <line stroke="blue" x1="22" y1="24" x2="21" y2="25"/>
    <line stroke="blue" x1="22" y1="24" x2="24" y2="24" elevation="0"/>
    <line stroke="blue" x1="31" y1="10" x2="32" y2="10"/>
    <line stroke="red" x1="31" y1="10" x2="31" y2="15" elevation="1"/>
    <line stroke="red" x1="29" y1="15" x2="30" y2="15"/>
    <line stroke="red" x1="29" y1="15" x2="29" y2="22" elevation="1"/>
    <line stroke="red" x1="21" y1="25" x2="20" y2="26"/>
    <line stroke="red" x1="21" y1="25" x2="23" y2="25" elevation="1"/>
    <line stroke="blue" x1="20" y1="26" x2="19" y2="27"/>
    <line stroke="blue" x1="20" y1="26" x2="24" y2="26" elevation="0"/>
    <line stroke="blue" x1="32" y1="8" x2="32" y2="10" elevation="0"/>
    <line stroke="blue" x1="32" y1="8" x2="33" y2="7"/>
    <line stroke="blue" x1="19" y1="27" x2="20" y2="28"/>
    <line stroke="red" x1="19" y1="27" x2="23" y2="27"/>
    <line stroke="red" x1="19" y1="27" x2="19" y2="39" elevation="1"/>
    <line stroke="red" x1="25" y1="22" x2="25" y2="23" elevation="1"/>
    <line stroke="blue" x1="25" y1="22" x2="26" y2="22"/>
    <line stroke="red" x1="32" y1="10" x2="33" y2="10"/>
    <line stroke="blue" x1="32" y1="10" x2="32" y2="15" elevation="0"/>
    <line stroke="blue" x1="30" y1="15" x2="31" y2="15"/>
    <line stroke="blue" x1="30" y1="15" x2="30" y2="22" elevation="0"/>
    <line stroke="red" x1="33" y1="7" x2="33" y2="10" elevation="1"/>
    <line stroke="red" x1="33" y1="7" x2="34" y2="6"/>
    <line stroke="blue" x1="24" y1="24" x2="23" y2="25"/>
    <line stroke="red" x1="24" y1="24" x2="25" y2="23"/>
    <line stroke="blue" x1="24" y1="24" x2="25" y2="25"/>
    <line stroke="blue" x1="24" y1="24" x2="26" y2="24" elevation="0"/>
    <line stroke="red" x1="23" y1="25" x2="25" y2="25" elevation="1"/>
    <line stroke="red" x1="23" y1="25" x2="24" y2="26"/>
    <line stroke="red" x1="25" y1="23" x2="26" y2="24"/>
    <line stroke="blue" x1="0" y1="34" x2="1" y2="34"/>
    <line stroke="black" x1="0" y1="34" x2="0" y2="42"/>
    <line stroke="black" x1="34" y1="0" x2="35" y2="0"/>
    <line stroke="blue" x1="34" y1="0" x2="35" y2="1"/>
    <line stroke="red" x1="1" y1="34" x2="2" y2="34"/>
    <line stroke="red" x1="1" y1="34" x2="1" y2="42" elevation="1"/>
    <line stroke="red" x1="26" y1="22" x2="27" y2="22"/>
    <line stroke="blue" x1="26" y1="22" x2="26" y2="24" elevation="0"/>
    <line stroke="blue" x1="2" y1="34" x2="3" y2="34"/>
    <line stroke="blue" x1="2" y1="34" x2="2" y2="42" elevation="0"/>
    <line stroke="red" x1="3" y1="34" x2="4" y2="34"/>
    <line stroke="red" x1="3" y1="34" x2="3" y2="42" elevation="1"/>
    <line stroke="blue" x1="4" y1="34" x2="5" y2="34"/>
    <line stroke="blue" x1="4" y1="34" x2="4" y2="42" elevation="0"/>
    <line stroke="red" x1="5" y1="34" x2="6" y2="34"/>
    <line stroke="red" x1="5" y1="34" x2="5" y2="42" elevation="1"/>
    <line stroke="red" x1="20" y1="28" x2="21" y2="29"/>
    <line stroke="blue" x1="20" y1="28" x2="24" y2="28" elevation="0"/>
    <line stroke="blue" x1="20" y1="28" x2="20" y2="38" elevation="0"/>
    <line stroke="red" x1="31" y1="15" x2="32" y2="15"/>
    <line stroke="red" x1="31" y1="15" x2="31" y2="22" elevation="1"/>
    <line stroke="blue" x1="33" y1="10" x2="34" y2="10"/>
    <line stroke="red" x1="33" y1="10" x2="33" y2="15" elevation="1"/>
    <line stroke="blue" x1="6" y1="34" x2="7" y2="34"/>
    <line stroke="blue" x1="6" y1="34" x2="6" y2="42" elevation="0"/>
    <line stroke="blue" x1="34" y1="6" x2="35" y2="5"/>
    <line stroke="blue" x1="34" y1="6" x2="34" y2="10" elevation="0"/>
    <line stroke="red" x1="7" y1="34" x2="8" y2="34"/>
    <line stroke="red" x1="7" y1="34" x2="7" y2="41" elevation="1"/>
    <line stroke="blue" x1="27" y1="22" x2="28" y2="22"/>
    <line stroke="red" x1="27" y1="22" x2="27" y2="25" elevation="1"/>
    <line stroke="blue" x1="8" y1="34" x2="9" y2="34"/>
    <line stroke="blue" x1="8" y1="34" x2="8" y2="40" elevation="0"/>
    <line stroke="red" x1="35" y1="0" x2="35" y2="1" elevation="1"/>
    <line stroke="black" x1="35" y1="0" x2="36" y2="0"/>
    <line stroke="red" x1="35" y1="1" x2="36" y2="2"/>
    <line stroke="red" x1="9" y1="34" x2="10" y2="34"/>
    <line stroke="red" x1="9" y1="34" x2="9" y2="39" elevation="1"/>
    <line stroke="blue" x1="32" y1="15" x2="33" y2="15"/>
    <line stroke="blue" x1="32" y1="15" x2="32" y2="22" elevation="0"/>
    <line stroke="red" x1="35" y1="5" x2="36" y2="4"/>
    <line stroke="red" x1="35" y1="5" x2="35" y2="10" elevation="1"/>
    <line stroke="red" x1="25" y1="25" x2="24" y2="26"/>
    <line stroke="red" x1="25" y1="25" x2="27" y2="25" elevation="1"/>
    <line stroke="blue" x1="24" y1="26" x2="23" y2="27"/>
    <line stroke="blue" x1="24" y1="26" x2="25" y2="27"/>
    <line stroke="blue" x1="24" y1="26" x2="28" y2="26" elevation="0"/>
    <line stroke="blue" x1="26" y1="24" x2="27" y2="25"/>
    <line stroke="blue" x1="10" y1="34" x2="11" y2="34"/>
    <line stroke="blue" x1="10" y1="34" x2="10" y2="38" elevation="0"/>
    <line stroke="red" x1="34" y1="10" x2="35" y2="10"/>
    <line stroke="blue" x1="34" y1="10" x2="34" y2="15" elevation="0"/>
    <line stroke="red" x1="23" y1="27" x2="25" y2="27"/>
    <line stroke="red" x1="23" y1="27" x2="24" y2="28"/>
    <line stroke="red" x1="28" y1="22" x2="29" y2="22"/>
    <line stroke="blue" x1="28" y1="22" x2="28" y2="26" elevation="0"/>
    <line stroke="red" x1="11" y1="34" x2="12" y2="34"/>
    <line stroke="red" x1="11" y1="34" x2="11" y2="37" elevation="1"/>
    <line stroke="red" x1="21" y1="29" x2="23" y2="29" elevation="1"/>
    <line stroke="blue" x1="21" y1="29" x2="22" y2="30"/>
    <line stroke="red" x1="21" y1="29" x2="21" y2="37" elevation="1"/>
    <line stroke="blue" x1="36" y1="0" x2="36" y2="2" elevation="0"/>
    <line stroke="black" x1="36" y1="0" x2="37" y2="0"/>
    <line stroke="blue" x1="12" y1="34" x2="13" y2="34"/>
    <line stroke="blue" x1="12" y1="34" x2="12" y2="36" elevation="0"/>
    <line stroke="blue" x1="36" y1="2" x2="37" y2="3"/>
    <line stroke="blue" x1="36" y1="4" x2="37" y2="3"/>
    <line stroke="blue" x1="36" y1="4" x2="36" y2="10" elevation="0"/>
    <line stroke="red" x1="33" y1="15" x2="34" y2="15"/>
    <line stroke="red" x1="33" y1="15" x2="33" y2="22" elevation="1"/>
    <line stroke="blue" x1="29" y1="22" x2="30" y2="22"/>
    <line stroke="red" x1="29" y1="22" x2="29" y2="27" elevation="1"/>
    <line stroke="blue" x1="35" y1="10" x2="36" y2="10"/>
    <line stroke="red" x1="35" y1="10" x2="35" y2="15" elevation="1"/>
    <line stroke="red" x1="13" y1="34" x2="14" y2="34"/>
    <line stroke="red" x1="13" y1="34" x2="13" y2="35" elevation="1"/>
    <line stroke="blue" x1="14" y1="34" x2="13" y2="35"/>
    <line stroke="blue" x1="14" y1="34" x2="15" y2="35"/>
    <line stroke="red" x1="25" y1="27" x2="24" y2="28"/>
    <line stroke="red" x1="25" y1="27" x2="29" y2="27"/>
    <line stroke="red" x1="27" y1="25" x2="28" y2="26"/>
    <line stroke="blue" x1="24" y1="28" x2="23" y2="29"/>
    <line stroke="blue" x1="24" y1="28" x2="25" y2="29"/>
    <line stroke="blue" x1="24" y1="28" x2="28" y2="28" elevation="0"/>
    <line stroke="red" x1="37" y1="0" x2="37" y2="3" elevation="1"/>
    <line stroke="black" x1="37" y1="0" x2="38" y2="0"/>
    <line stroke="red" x1="23" y1="29" x2="25" y2="29" elevation="1"/>
    <line stroke="red" x1="23" y1="29" x2="24" y2="30"/>
    <line stroke="red" x1="37" y1="3" x2="38" y2="3" elevation="1"/>
    <line stroke="red" x1="37" y1="3" x2="37" y2="10" elevation="1"/>
    <line stroke="blue" x1="34" y1="15" x2="35" y2="15"/>
    <line stroke="blue" x1="34" y1="15" x2="34" y2="22" elevation="0"/>
    <line stroke="blue" x1="22" y1="30" x2="24" y2="30" elevation="0"/>
    <line stroke="red" x1="22" y1="30" x2="23" y2="31"/>
    <line stroke="blue" x1="22" y1="30" x2="22" y2="36" elevation="0"/>
    <line stroke="red" x1="30" y1="22" x2="31" y2="22"/>
    <line stroke="blue" x1="30" y1="22" x2="30" y2="27" elevation="0"/>
    <line stroke="red" x1="13" y1="35" x2="12" y2="36"/>
    <line stroke="red" x1="13" y1="35" x2="15" y2="35" elevation="1"/>
    <line stroke="red" x1="36" y1="10" x2="37" y2="10"/>
    <line stroke="blue" x1="36" y1="10" x2="36" y2="15" elevation="0"/>
    <line stroke="blue" x1="12" y1="36" x2="11" y2="37"/>
    <line stroke="blue" x1="12" y1="36" x2="16" y2="36" elevation="0"/>
    <line stroke="blue" x1="38" y1="0" x2="38" y2="3" elevation="0"/>
    <line stroke="black" x1="38" y1="0" x2="39" y2="0"/>
    <line stroke="blue" x1="31" y1="22" x2="32" y2="22"/>
    <line stroke="red" x1="31" y1="22" x2="31" y2="27" elevation="1"/>
    <line stroke="red" x1="15" y1="35" x2="16" y2="36"/>
    <line stroke="red" x1="35" y1="15" x2="36" y2="15"/>
    <line stroke="red" x1="35" y1="15" x2="35" y2="22" elevation="1"/>
    <line stroke="blue" x1="38" y1="3" x2="39" y2="3"/>
    <line stroke="blue" x1="38" y1="3" x2="38" y2="10" elevation="0"/>
    <line stroke="blue" x1="28" y1="26" x2="29" y2="27"/>
    <line stroke="red" x1="25" y1="29" x2="24" y2="30"/>
    <line stroke="red" x1="25" y1="29" x2="27" y2="29" elevation="1"/>
    <line stroke="blue" x1="37" y1="10" x2="38" y2="10"/>
    <line stroke="red" x1="37" y1="10" x2="37" y2="15" elevation="1"/>
    <line stroke="blue" x1="24" y1="30" x2="23" y2="31"/>
    <line stroke="blue" x1="24" y1="30" x2="26" y2="30" elevation="0"/>
    <line stroke="blue" x1="24" y1="30" x2="25" y2="31"/>
    <line stroke="red" x1="11" y1="37" x2="10" y2="38"/>
    <line stroke="red" x1="11" y1="37" x2="17" y2="37" elevation="1"/>
    <line stroke="red" x1="23" y1="31" x2="25" y2="31" elevation="1"/>
    <line stroke="red" x1="23" y1="31" x2="23" y2="35" elevation="1"/>
    <line stroke="red" x1="32" y1="22" x2="33" y2="22"/>
    <line stroke="blue" x1="32" y1="22" x2="32" y2="27" elevation="0"/>
    <line stroke="blue" x1="36" y1="15" x2="37" y2="15"/>
    <line stroke="blue" x1="36" y1="15" x2="36" y2="22" elevation="0"/>
    <line stroke="red" x1="39" y1="0" x2="39" y2="3" elevation="1"/>
    <line stroke="black" x1="39" y1="0" x2="40" y2="0"/>
    <line stroke="red" x1="39" y1="3" x2="40" y2="3"/>
    <line stroke="red" x1="39" y1="3" x2="39" y2="10" elevation="1"/>
    <line stroke="blue" x1="10" y1="38" x2="9" y2="39"/>
    <line stroke="blue" x1="10" y1="38" x2="18" y2="38" elevation="0"/>
    <line stroke="red" x1="38" y1="10" x2="39" y2="10"/>
    <line stroke="blue" x1="38" y1="10" x2="38" y2="15" elevation="0"/>
    <line stroke="blue" x1="16" y1="36" x2="17" y2="37"/>
    <line stroke="red" x1="28" y1="28" x2="27" y2="29"/>
    <line stroke="blue" x1="28" y1="28" x2="29" y2="27"/>
    <line stroke="blue" x1="28" y1="28" x2="28" y2="38" elevation="0"/>
    <line stroke="blue" x1="27" y1="29" x2="26" y2="30"/>
    <line stroke="red" x1="27" y1="29" x2="27" y2="37" elevation="1"/>
    <line stroke="red" x1="29" y1="27" x2="30" y2="27"/>
    <line stroke="red" x1="29" y1="27" x2="29" y2="39" elevation="1"/>
    <line stroke="blue" x1="33" y1="22" x2="34" y2="22"/>
    <line stroke="red" x1="33" y1="22" x2="33" y2="27" elevation="1"/>
    <line stroke="red" x1="26" y1="30" x2="25" y2="31"/>
    <line stroke="blue" x1="26" y1="30" x2="26" y2="36" elevation="0"/>
    <line stroke="red" x1="25" y1="31" x2="25" y2="35" elevation="1"/>
    <line stroke="red" x1="37" y1="15" x2="38" y2="15"/>
    <line stroke="red" x1="37" y1="15" x2="37" y2="22" elevation="1"/>
    <line stroke="blue" x1="40" y1="0" x2="40" y2="3" elevation="0"/>
    <line stroke="black" x1="40" y1="0" x2="41" y2="0"/>
    <line stroke="red" x1="9" y1="39" x2="8" y2="40"/>
    <line stroke="red" x1="9" y1="39" x2="19" y2="39" elevation="1"/>
    <line stroke="blue" x1="40" y1="3" x2="41" y2="3"/>
    <line stroke="blue" x1="40" y1="3" x2="40" y2="10" elevation="0"/>
    <line stroke="blue" x1="39" y1="10" x2="40" y2="10"/>
    <line stroke="red" x1="39" y1="10" x2="39" y2="15" elevation="1"/>
    <line stroke="blue" x1="30" y1="27" x2="31" y2="27"/>
    <line stroke="blue" x1="30" y1="27" x2="30" y2="38" elevation="0"/>
    <line stroke="red" x1="34" y1="22" x2="35" y2="22"/>
    <line stroke="blue" x1="34" y1="22" x2="34" y2="27" elevation="0"/>
    <line stroke="red" x1="17" y1="37" x2="18" y2="38"/>
    <line stroke="blue" x1="8" y1="40" x2="7" y2="41"/>
    <line stroke="blue" x1="8" y1="40" x2="19" y2="40" elevation="0"/>
    <line stroke="blue" x1="38" y1="15" x2="39" y2="15"/>
    <line stroke="blue" x1="38" y1="15" x2="38" y2="22" elevation="0"/>
    <line stroke="red" x1="41" y1="0" x2="41" y2="3" elevation="1"/>
    <line stroke="black" x1="41" y1="0" x2="42" y2="0"/>
    <line stroke="red" x1="31" y1="27" x2="32" y2="27"/>
    <line stroke="red" x1="31" y1="27" x2="31" y2="37" elevation="1"/>
    <line stroke="red" x1="41" y1="3" x2="42" y2="3"/>
    <line stroke="red" x1="41" y1="3" x2="41" y2="10" elevation="1"/>
    <line stroke="red" x1="40" y1="10" x2="41" y2="10"/>
    <line stroke="blue" x1="40" y1="10" x2="40" y2="15" elevation="0"/>
    <line stroke="blue" x1="35" y1="22" x2="36" y2="22"/>
    <line stroke="red" x1="35" y1="22" x2="35" y2="27" elevation="1"/>
    <line stroke="red" x1="7" y1="41" x2="6" y2="42"/>
    <line stroke="red" x1="7" y1="41" x2="19" y2="41" elevation="1"/>
    <line stroke="red" x1="39" y1="15" x2="40" y2="15"/>
    <line stroke="red" x1="39" y1="15" x2="39" y2="22" elevation="1"/>
    <line stroke="blue" x1="32" y1="27" x2="33" y2="27"/>
    <line stroke="blue" x1="32" y1="27" x2="32" y2="36" elevation="0"/>
    <line stroke="red" x1="23" y1="35" x2="22" y2="36"/>
    <line stroke="red" x1="23" y1="35" x2="25" y2="35" elevation="1"/>
    <line stroke="blue" x1="23" y1="35" x2="24" y2="36"/>
    <line stroke="red" x1="0" y1="42" x2="1" y2="42"/>
    <line stroke="black" x1="0" y1="42" x2="0" y2="48"/>
    <line stroke="blue" x1="42" y1="0" x2="42" y2="3" elevation="0"/>
    <line stroke="black" x1="42" y1="0" x2="43" y2="0"/>
    <line stroke="blue" x1="1" y1="42" x2="2" y2="42"/>
    <line stroke="red" x1="1" y1="42" x2="1" y2="48" elevation="1"/>
    <line stroke="blue" x1="18" y1="38" x2="19" y2="39"/>
    <line stroke="red" x1="2" y1="42" x2="3" y2="42"/>
    <line stroke="blue" x1="2" y1="42" x2="2" y2="48" elevation="0"/>
    <line stroke="blue" x1="3" y1="42" x2="4" y2="42"/>
    <line stroke="red" x1="3" y1="42" x2="3" y2="48" elevation="1"/>
    <line stroke="blue" x1="42" y1="3" x2="43" y2="3"/>
    <line stroke="blue" x1="42" y1="3" x2="42" y2="10" elevation="0"/>
    <line stroke="red" x1="4" y1="42" x2="5" y2="42"/>
    <line stroke="blue" x1="4" y1="42" x2="4" y2="48" elevation="0"/>
    <line stroke="blue" x1="22" y1="36" x2="21" y2="37"/>
    <line stroke="blue" x1="22" y1="36" x2="24" y2="36" elevation="0"/>
    <line stroke="red" x1="36" y1="22" x2="37" y2="22"/>
    <line stroke="blue" x1="36" y1="22" x2="36" y2="27" elevation="0"/>
    <line stroke="blue" x1="41" y1="10" x2="42" y2="10"/>
    <line stroke="red" x1="41" y1="10" x2="41" y2="15" elevation="1"/>
    <line stroke="blue" x1="5" y1="42" x2="6" y2="42"/>
    <line stroke="red" x1="5" y1="42" x2="5" y2="48" elevation="1"/>
    <line stroke="red" x1="6" y1="42" x2="7" y2="43"/>
    <line stroke="blue" x1="6" y1="42" x2="19" y2="42"/>
    <line stroke="blue" x1="6" y1="42" x2="6" y2="48" elevation="0"/>
    <line stroke="red" x1="21" y1="37" x2="20" y2="38"/>
    <line stroke="red" x1="21" y1="37" x2="23" y2="37" elevation="1"/>
    <line stroke="red" x1="33" y1="27" x2="34" y2="27"/>
    <line stroke="red" x1="33" y1="27" x2="33" y2="35" elevation="1"/>
    <line stroke="blue" x1="40" y1="15" x2="41" y2="15"/>
    <line stroke="blue" x1="40" y1="15" x2="40" y2="22" elevation="0"/>
    <line stroke="blue" x1="20" y1="38" x2="19" y2="39"/>
    <line stroke="blue" x1="20" y1="38" x2="24" y2="38" elevation="0"/>
    <line stroke="red" x1="43" y1="0" x2="43" y2="3" elevation="1"/>
    <line stroke="black" x1="43" y1="0" x2="44" y2="0"/>
    <line stroke="blue" x1="25" y1="35" x2="24" y2="36"/>
    <line stroke="red" x1="25" y1="35" x2="26" y2="36"/>
    <line stroke="blue" x1="37" y1="22" x2="38" y2="22"/>
    <line stroke="red" x1="37" y1="22" x2="37" y2="27" elevation="1"/>
    <line stroke="red" x1="43" y1="3" x2="44" y2="3"/>
    <line stroke="red" x1="43" y1="3" x2="43" y2="10" elevation="1"/>
    <line stroke="red" x1="42" y1="10" x2="43" y2="10"/>
    <line stroke="blue" x1="42" y1="10" x2="42" y2="15" elevation="0"/>
    <line stroke="red" x1="24" y1="36" x2="23" y2="37"/>
    <line stroke="blue" x1="24" y1="36" x2="26" y2="36" elevation="0"/>
    <line stroke="red" x1="24" y1="36" x2="25" y2="37"/>
    <line stroke="red" x1="19" y1="39" x2="19" y2="40" elevation="1"/>
    <line stroke="red" x1="19" y1="39" x2="23" y2="39" elevation="1"/>
    <line stroke="blue" x1="34" y1="27" x2="35" y2="27"/>
    <line stroke="blue" x1="34" y1="27" x2="34" y2="34" elevation="0"/>
    <line stroke="blue" x1="7" y1="43" x2="8" y2="44"/>
    <line stroke="red" x1="7" y1="43" x2="19" y2="43" elevation="1"/>
    <line stroke="red" x1="7" y1="43" x2="7" y2="47" elevation="1"/>
    <line stroke="red" x1="23" y1="37" x2="25" y2="37" elevation="1"/>
    <line stroke="blue" x1="23" y1="37" x2="24" y2="38"/>
    <line stroke="red" x1="41" y1="15" x2="42" y2="15"/>
    <line stroke="red" x1="41" y1="15" x2="41" y2="22" elevation="1"/>
    <line stroke="red" x1="38" y1="22" x2="39" y2="22"/>
    <line stroke="blue" x1="38" y1="22" x2="38" y2="27" elevation="0"/>
    <line stroke="blue" x1="44" y1="0" x2="44" y2="3" elevation="0"/>
    <line stroke="black" x1="44" y1="0" x2="45" y2="0"/>
    <line stroke="blue" x1="44" y1="3" x2="45" y2="3"/>
    <line stroke="blue" x1="44" y1="3" x2="44" y2="10" elevation="0"/>
    <line stroke="blue" x1="43" y1="10" x2="44" y2="10"/>
    <line stroke="red" x1="43" y1="10" x2="43" y2="15" elevation="1"/>
    <line stroke="red" x1="35" y1="27" x2="36" y2="27"/>
    <line stroke="red" x1="35" y1="27" x2="35" y2="35" elevation="1"/>
    <line stroke="blue" x1="19" y1="40" x2="19" y2="41"/>
    <line stroke="blue" x1="19" y1="40" x2="24" y2="40" elevation="0"/>
    <line stroke="blue" x1="26" y1="36" x2="27" y2="37"/>
    <line stroke="blue" x1="42" y1="15" x2="43" y2="15"/>
    <line stroke="blue" x1="42" y1="15" x2="42" y2="22" elevation="0"/>
    <line stroke="blue" x1="25" y1="37" x2="24" y2="38"/>
    <line stroke="red" x1="25" y1="37" x2="27" y2="37" elevation="1"/>
    <line stroke="red" x1="8" y1="44" x2="9" y2="45"/>
    <line stroke="blue" x1="8" y1="44" x2="8" y2="46" elevation="0"/>
    <line stroke="blue" x1="8" y1="44" x2="19" y2="44" elevation="0"/>
    <line stroke="blue" x1="39" y1="22" x2="40" y2="22"/>
    <line stroke="red" x1="39" y1="22" x2="39" y2="27" elevation="1"/>
    <line stroke="red" x1="24" y1="38" x2="23" y2="39"/>
    <line stroke="red" x1="24" y1="38" x2="25" y2="39"/>
    <line stroke="blue" x1="24" y1="38" x2="28" y2="38" elevation="0"/>
    <line stroke="blue" x1="36" y1="27" x2="37" y2="27"/>
    <line stroke="blue" x1="36" y1="27" x2="36" y2="36" elevation="0"/>
    <line stroke="red" x1="45" y1="0" x2="45" y2="3" elevation="1"/>
    <line stroke="black" x1="45" y1="0" x2="46" y2="0"/>
    <line stroke="red" x1="45" y1="3" x2="45" y2="10" elevation="1"/>
    <line stroke="red" x1="45" y1="3" x2="46" y2="3"/>
    <line stroke="red" x1="44" y1="10" x2="45" y2="10"/>
    <line stroke="blue" x1="44" y1="10" x2="44" y2="15" elevation="0"/>
    <line stroke="red" x1="19" y1="41" x2="19" y2="42"/>
    <line stroke="red" x1="19" y1="41" x2="23" y2="41" elevation="1"/>
    <line stroke="red" x1="23" y1="39" x2="25" y2="39" elevation="1"/>
    <line stroke="blue" x1="23" y1="39" x2="24" y2="40"/>
    <line stroke="red" x1="43" y1="15" x2="44" y2="15"/>
    <line stroke="red" x1="43" y1="15" x2="43" y2="22" elevation="1"/>
    <line stroke="red" x1="40" y1="22" x2="41" y2="22"/>
    <line stroke="blue" x1="40" y1="22" x2="40" y2="27" elevation="0"/>
    <line stroke="red" x1="27" y1="37" x2="28" y2="38"/>
    <line stroke="red" x1="37" y1="27" x2="38" y2="27"/>
    <line stroke="red" x1="37" y1="27" x2="37" y2="37" elevation="1"/>
    <line stroke="red" x1="9" y1="45" x2="8" y2="46"/>
    <line stroke="blue" x1="9" y1="45" x2="9" y2="46"/>
    <line stroke="red" x1="9" y1="45" x2="19" y2="45" elevation="1"/>
    <line stroke="blue" x1="46" y1="0" x2="46" y2="3" elevation="0"/>
    <line stroke="black" x1="46" y1="0" x2="47" y2="0"/>
    <line stroke="blue" x1="19" y1="42" x2="19" y2="43"/>
    <line stroke="blue" x1="19" y1="42" x2="24" y2="42"/>
    <line stroke="blue" x1="45" y1="10" x2="46" y2="10"/>
    <line stroke="red" x1="45" y1="10" x2="45" y2="15" elevation="1"/>
    <line stroke="blue" x1="46" y1="3" x2="46" y2="10" elevation="0"/>
    <line stroke="blue" x1="46" y1="3" x2="47" y2="3"/>
    <line stroke="blue" x1="25" y1="39" x2="24" y2="40"/>
    <line stroke="red" x1="25" y1="39" x2="29" y2="39" elevation="1"/>
    <line stroke="blue" x1="44" y1="15" x2="45" y2="15"/>
    <line stroke="blue" x1="44" y1="15" x2="44" y2="22" elevation="0"/>
    <line stroke="blue" x1="41" y1="22" x2="42" y2="22"/>
    <line stroke="red" x1="41" y1="22" x2="41" y2="27" elevation="1"/>
    <line stroke="blue" x1="38" y1="27" x2="39" y2="27"/>
    <line stroke="blue" x1="38" y1="27" x2="38" y2="38" elevation="0"/>
    <line stroke="red" x1="24" y1="40" x2="23" y2="41"/>
    <line stroke="red" x1="24" y1="40" x2="25" y2="41"/>
    <line stroke="blue" x1="24" y1="40" x2="29" y2="40" elevation="0"/>
    <line stroke="blue" x1="8" y1="46" x2="9" y2="46" elevation="0"/>
    <line stroke="blue" x1="8" y1="46" x2="7" y2="47"/>
    <line stroke="red" x1="9" y1="46" x2="9" y2="47"/>
    <line stroke="blue" x1="9" y1="46" x2="19" y2="46" elevation="0"/>
    <line stroke="red" x1="47" y1="0" x2="47" y2="3" elevation="1"/>
    <line stroke="black" x1="47" y1="0" x2="48" y2="0"/>
    <line stroke="red" x1="19" y1="43" x2="19" y2="44"/>
    <line stroke="red" x1="19" y1="43" x2="23" y2="43" elevation="1"/>
    <line stroke="red" x1="23" y1="41" x2="25" y2="41" elevation="1"/>
    <line stroke="blue" x1="23" y1="41" x2="24" y2="42"/>
    <line stroke="red" x1="46" y1="10" x2="47" y2="10"/>
    <line stroke="blue" x1="46" y1="10" x2="46" y2="15" elevation="0"/>
    <line stroke="red" x1="47" y1="3" x2="47" y2="10" elevation="1"/>
    <line stroke="red" x1="47" y1="3" x2="48" y2="3"/>
    <line stroke="blue" x1="28" y1="38" x2="29" y2="39"/>
    <line stroke="red" x1="42" y1="22" x2="43" y2="22"/>
    <line stroke="blue" x1="42" y1="22" x2="42" y2="27" elevation="0"/>
    <line stroke="red" x1="39" y1="27" x2="40" y2="27"/>
    <line stroke="red" x1="39" y1="27" x2="39" y2="39" elevation="1"/>
    <line stroke="red" x1="45" y1="15" x2="46" y2="15"/>
    <line stroke="red" x1="45" y1="15" x2="45" y2="22" elevation="1"/>
    <line stroke="red" x1="7" y1="47" x2="9" y2="47" elevation="1"/>
    <line stroke="red" x1="7" y1="47" x2="6" y2="48"/>
    <line stroke="blue" x1="9" y1="47" x2="9" y2="48"/>
    <line stroke="red" x1="9" y1="47" x2="19" y2="47" elevation="1"/>
    <line stroke="blue" x1="19" y1="44" x2="19" y2="45"/>
    <line stroke="blue" x1="19" y1="44" x2="24" y2="44" elevation="0"/>
    <line stroke="black" x1="0" y1="48" x2="1" y2="48"/>
    <line stroke="black" x1="48" y1="0" x2="48" y2="3"/>
    <line stroke="black" x1="1" y1="48" x2="2" y2="48"/>
    <line stroke="blue" x1="25" y1="41" x2="24" y2="42"/>
    <line stroke="red" x1="25" y1="41" x2="29" y2="41" elevation="1"/>
    <line stroke="black" x1="2" y1="48" x2="3" y2="48"/>
    <line stroke="blue" x1="47" y1="10" x2="48" y2="10"/>
    <line stroke="red" x1="47" y1="10" x2="47" y2="15" elevation="1"/>
    <line stroke="blue" x1="34" y1="34" x2="33" y2="35"/>
    <line stroke="red" x1="34" y1="34" x2="34" y2="35"/>
    <line stroke="blue" x1="34" y1="34" x2="35" y2="35"/>
    <line stroke="black" x1="3" y1="48" x2="4" y2="48"/>
    <line stroke="black" x1="48" y1="3" x2="48" y2="10"/>
    <line stroke="red" x1="33" y1="35" x2="32" y2="36"/>
    <line stroke="red" x1="33" y1="35" x2="34" y2="35" elevation="1"/>
    <line stroke="black" x1="4" y1="48" x2="5" y2="48"/>
    <line stroke="blue" x1="32" y1="36" x2="31" y2="37"/>
    <line stroke="blue" x1="32" y1="36" x2="34" y2="36" elevation="0"/>
    <line stroke="black" x1="5" y1="48" x2="6" y2="48"/>
    <line stroke="blue" x1="40" y1="27" x2="41" y2="27"/>
    <line stroke="blue" x1="40" y1="27" x2="40" y2="40" elevation="0"/>
    <line stroke="red" x1="31" y1="37" x2="30" y2="38"/>
    <line stroke="red" x1="31" y1="37" x2="34" y2="37" elevation="1"/>
    <line stroke="blue" x1="43" y1="22" x2="44" y2="22"/>
    <line stroke="red" x1="43" y1="22" x2="43" y2="27" elevation="1"/>
    <line stroke="black" x1="6" y1="48" x2="9" y2="48"/>
    <line stroke="red" x1="24" y1="42" x2="23" y2="43"/>
    <line stroke="red" x1="24" y1="42" x2="25" y2="43"/>
    <line stroke="blue" x1="24" y1="42" x2="29" y2="42"/>
    <line stroke="blue" x1="46" y1="15" x2="47" y2="15"/>
    <line stroke="blue" x1="46" y1="15" x2="46" y2="22" elevation="0"/>
    <line stroke="blue" x1="30" y1="38" x2="29" y2="39"/>
    <line stroke="blue" x1="30" y1="38" x2="34" y2="38" elevation="0"/>
    <line stroke="red" x1="29" y1="39" x2="29" y2="40" elevation="1"/>
    <line stroke="red" x1="29" y1="39" x2="34" y2="39" elevation="1"/>
    <line stroke="red" x1="23" y1="43" x2="25" y2="43" elevation="1"/>
    <line stroke="blue" x1="23" y1="43" x2="24" y2="44"/>
    <line stroke="red" x1="34" y1="35" x2="35" y2="35" elevation="1"/>
    <line stroke="blue" x1="34" y1="35" x2="34" y2="36"/>
    <line stroke="black" x1="9" y1="48" x2="19" y2="48"/>
    <line stroke="red" x1="19" y1="45" x2="19" y2="46"/>
    <line stroke="red" x1="19" y1="45" x2="23" y2="45" elevation="1"/>
    <line stroke="black" x1="48" y1="10" x2="48" y2="15"/>
    <line stroke="red" x1="41" y1="27" x2="42" y2="27"/>
    <line stroke="red" x1="41" y1="27" x2="41" y2="41" elevation="1"/>
    <line stroke="red" x1="44" y1="22" x2="45" y2="22"/>
    <line stroke="blue" x1="44" y1="22" x2="44" y2="27" elevation="0"/>
    <line stroke="red" x1="47" y1="15" x2="48" y2="15"/>
    <line stroke="red" x1="47" y1="15" x2="47" y2="22" elevation="1"/>
    <line stroke="blue" x1="29" y1="40" x2="29" y2="41"/>
    <line stroke="blue" x1="29" y1="40" x2="34" y2="40" elevation="0"/>
    <line stroke="red" x1="35" y1="35" x2="36" y2="36"/>
    <line stroke="red" x1="34" y1="36" x2="34" y2="37"/>
    <line stroke="blue" x1="34" y1="36" x2="36" y2="36" elevation="0"/>
    <line stroke="blue" x1="25" y1="43" x2="24" y2="44"/>
    <line stroke="red" x1="25" y1="43" x2="29" y2="43" elevation="1"/>
    <line stroke="blue" x1="19" y1="46" x2="19" y2="47"/>
    <line stroke="blue" x1="19" y1="46" x2="24" y2="46" elevation="0"/>
    <line stroke="blue" x1="42" y1="27" x2="43" y2="27"/>
    <line stroke="blue" x1="42" y1="27" x2="42" y2="42" elevation="0"/>
    <line stroke="blue" x1="45" y1="22" x2="46" y2="22"/>
    <line stroke="red" x1="45" y1="22" x2="45" y2="27" elevation="1"/>
    <line stroke="red" x1="24" y1="44" x2="23" y2="45"/>
    <line stroke="red" x1="24" y1="44" x2="25" y2="45"/>
    <line stroke="blue" x1="24" y1="44" x2="29" y2="44" elevation="0"/>
    <line stroke="red" x1="29" y1="41" x2="29" y2="42"/>
    <line stroke="red" x1="29" y1="41" x2="34" y2="41" elevation="1"/>
    <line stroke="blue" x1="34" y1="37" x2="34" y2="38"/>
    <line stroke="red" x1="34" y1="37" x2="37" y2="37" elevation="1"/>
    <line stroke="black" x1="48" y1="15" x2="48" y2="22"/>
    <line stroke="red" x1="23" y1="45" x2="25" y2="45" elevation="1"/>
    <line stroke="blue" x1="23" y1="45" x2="24" y2="46"/>
    <line stroke="red" x1="19" y1="47" x2="19" y2="48"/>
    <line stroke="red" x1="19" y1="47" x2="23" y2="47" elevation="1"/>
    <line stroke="red" x1="43" y1="27" x2="44" y2="27"/>
    <line stroke="red" x1="43" y1="27" x2="43" y2="42" elevation="1"/>
    <line stroke="blue" x1="36" y1="36" x2="37" y2="37"/>
    <line stroke="red" x1="34" y1="38" x2="34" y2="39"/>
    <line stroke="blue" x1="34" y1="38" x2="38" y2="38" elevation="0"/>
    <line stroke="red" x1="46" y1="22" x2="47" y2="22"/>
    <line stroke="blue" x1="46" y1="22" x2="46" y2="27" elevation="0"/>
    <line stroke="blue" x1="29" y1="42" x2="29" y2="43"/>
    <line stroke="blue" x1="29" y1="42" x2="34" y2="42"/>
    <line stroke="blue" x1="25" y1="45" x2="24" y2="46"/>
    <line stroke="red" x1="25" y1="45" x2="29" y2="45" elevation="1"/>
    <line stroke="black" x1="19" y1="48" x2="24" y2="48"/>
    <line stroke="blue" x1="44" y1="27" x2="45" y2="27"/>
    <line stroke="blue" x1="44" y1="27" x2="44" y2="42" elevation="0"/>
    <line stroke="blue" x1="34" y1="39" x2="34" y2="40"/>
    <line stroke="red" x1="34" y1="39" x2="39" y2="39" elevation="1"/>
    <line stroke="red" x1="29" y1="43" x2="29" y2="44"/>
    <line stroke="red" x1="29" y1="43" x2="34" y2="43" elevation="1"/>
    <line stroke="red" x1="24" y1="46" x2="23" y2="47"/>
    <line stroke="red" x1="24" y1="46" x2="25" y2="47"/>
    <line stroke="blue" x1="24" y1="46" x2="29" y2="46" elevation="0"/>
    <line stroke="blue" x1="47" y1="22" x2="48" y2="22"/>
    <line stroke="red" x1="47" y1="22" x2="47" y2="27" elevation="1"/>
    <line stroke="red" x1="23" y1="47" x2="25" y2="47" elevation="1"/>
    <line stroke="blue" x1="23" y1="47" x2="24" y2="48"/>
    <line stroke="red" x1="37" y1="37" x2="38" y2="38"/>
    <line stroke="red" x1="45" y1="27" x2="46" y2="27"/>
    <line stroke="red" x1="45" y1="27" x2="45" y2="42" elevation="1"/>
    <line stroke="red" x1="34" y1="40" x2="34" y2="41"/>
    <line stroke="blue" x1="34" y1="40" x2="40" y2="40" elevation="0"/>
    <line stroke="blue" x1="29" y1="44" x2="29" y2="45"/>
    <line stroke="blue" x1="29" y1="44" x2="34" y2="44" elevation="0"/>
    <line stroke="black" x1="48" y1="22" x2="48" y2="27"/>
    <line stroke="blue" x1="25" y1="47" x2="24" y2="48"/>
    <line stroke="red" x1="25" y1="47" x2="29" y2="47" elevation="1"/>
    <line stroke="blue" x1="34" y1="41" x2="34" y2="42"/>
    <line stroke="red" x1="34" y1="41" x2="41" y2="41" elevation="1"/>
    <line stroke="blue" x1="46" y1="27" x2="47" y2="27"/>
    <line stroke="blue" x1="46" y1="27" x2="46" y2="42" elevation="0"/>
    <line stroke="red" x1="29" y1="45" x2="29" y2="46"/>
    <line stroke="red" x1="29" y1="45" x2="34" y2="45" elevation="1"/>
    <line stroke="black" x1="24" y1="48" x2="29" y2="48"/>
    <line stroke="blue" x1="38" y1="38" x2="39" y2="39"/>
    <line stroke="red" x1="34" y1="42" x2="34" y2="43"/>
    <line stroke="blue" x1="34" y1="42" x2="42" y2="42"/>
    <line stroke="red" x1="47" y1="27" x2="48" y2="27"/>
    <line stroke="red" x1="47" y1="27" x2="47" y2="42" elevation="1"/>
    <line stroke="blue" x1="29" y1="46" x2="29" y2="47"/>
    <line stroke="blue" x1="29" y1="46" x2="34" y2="46" elevation="0"/>
    <line stroke="blue" x1="34" y1="43" x2="34" y2="44"/>
    <line stroke="red" x1="34" y1="43" x2="41" y2="43" elevation="1"/>
    <line stroke="black" x1="48" y1="27" x2="48" y2="42"/>
    <line stroke="red" x1="39" y1="39" x2="40" y2="40"/>
    <line stroke="red" x1="29" y1="47" x2="29" y2="48"/>
    <line stroke="red" x1="29" y1="47" x2="34" y2="47" elevation="1"/>
    <line stroke="red" x1="34" y1="44" x2="34" y2="45"/>
    <line stroke="blue" x1="34" y1="44" x2="40" y2="44" elevation="0"/>
    <line stroke="black" x1="29" y1="48" x2="34" y2="48"/>
    <line stroke="blue" x1="34" y1="45" x2="34" y2="46"/>
    <line stroke="red" x1="34" y1="45" x2="39" y2="45" elevation="1"/>
    <line stroke="blue" x1="40" y1="40" x2="41" y2="41"/>
    <line stroke="red" x1="34" y1="46" x2="34" y2="47"/>
    <line stroke="blue" x1="34" y1="46" x2="40" y2="46" elevation="0"/>
    <line stroke="red" x1="41" y1="41" x2="42" y2="42"/>
    <line stroke="blue" x1="34" y1="47" x2="34" y2="48"/>
    <line stroke="red" x1="34" y1="47" x2="41" y2="47" elevation="1"/>
    <line stroke="black" x1="34" y1="48" x2="42" y2="48"/>
    <line stroke="red" x1="42" y1="42" x2="41" y2="43"/>
    <line stroke="blue" x1="42" y1="42" x2="43" y2="42"/>
    <line stroke="blue" x1="42" y1="42" x2="42" y2="45" elevation="0"/>
    <line stroke="blue" x1="41" y1="43" x2="40" y2="44"/>
    <line stroke="red" x1="41" y1="43" x2="41" y2="45" elevation="1"/>
    <line stroke="red" x1="40" y1="44" x2="39" y2="45"/>
    <line stroke="blue" x1="40" y1="44" x2="40" y2="45" elevation="0"/>
    <line stroke="blue" x1="39" y1="45" x2="40" y2="45"/>
    <line stroke="red" x1="39" y1="45" x2="40" y2="46"/>
    <line stroke="red" x1="43" y1="42" x2="44" y2="42"/>
    <line stroke="red" x1="43" y1="42" x2="43" y2="45" elevation="1"/>
    <line stroke="red" x1="40" y1="45" x2="41" y2="45"/>
    <line stroke="blue" x1="40" y1="45" x2="40" y2="46" elevation="0"/>
    <line stroke="blue" x1="44" y1="42" x2="45" y2="42"/>
    <line stroke="blue" x1="44" y1="42" x2="44" y2="45" elevation="0"/>
    <line stroke="blue" x1="41" y1="45" x2="42" y2="45"/>
    <line stroke="red" x1="41" y1="45" x2="41" y2="47" elevation="1"/>
    <line stroke="blue" x1="40" y1="46" x2="41" y2="47"/>
    <line stroke="red" x1="42" y1="45" x2="43" y2="45"/>
    <line stroke="blue" x1="42" y1="45" x2="42" y2="48" elevation="0"/>
    <line stroke="red" x1="45" y1="42" x2="46" y2="42"/>
    <line stroke="red" x1="45" y1="42" x2="45" y2="45" elevation="1"/>
    <line stroke="blue" x1="43" y1="45" x2="44" y2="45"/>
    <line stroke="red" x1="43" y1="45" x2="43" y2="48" elevation="1"/>
    <line stroke="blue" x1="46" y1="42" x2="47" y2="42"/>
    <line stroke="blue" x1="46" y1="42" x2="46" y2="45" elevation="0"/>
    <line stroke="red" x1="41" y1="47" x2="42" y2="48"/>
    <line stroke="red" x1="44" y1="45" x2="45" y2="45"/>
    <line stroke="blue" x1="44" y1="45" x2="44" y2="48" elevation="0"/>
    <line stroke="red" x1="47" y1="42" x2="48" y2="42"/>
    <line stroke="red" x1="47" y1="42" x2="47" y2="45" elevation="1"/>
    <line stroke="blue" x1="45" y1="45" x2="46" y2="45"/>
    <line stroke="red" x1="45" y1="45" x2="45" y2="48" elevation="1"/>
    <line stroke="black" x1="42" y1="48" x2="43" y2="48"/>
    <line stroke="black" x1="48" y1="42" x2="48" y2="45"/>
    <line stroke="red" x1="46" y1="45" x2="47" y2="45"/>
    <line stroke="blue" x1="46" y1="45" x2="46" y2="48" elevation="0"/>
    <line stroke="black" x1="43" y1="48" x2="44" y2="48"/>
    <line stroke="blue" x1="47" y1="45" x2="48" y2="45"/>
    <line stroke="red" x1="47" y1="45" x2="47" y2="48" elevation="1"/>
    <line stroke="black" x1="44" y1="48" x2="45" y2="48"/>
    <line stroke="black" x1="45" y1="48" x2="46" y2="48"/>
    <line stroke="black" x1="48" y1="45" x2="48" y2="48"/>
    <line stroke="black" x1="46" y1="48" x2="47" y2="48"/>
    <line stroke="black" x1="47" y1="48" x2="48" y2="48"/>
  </svg>""",
)
