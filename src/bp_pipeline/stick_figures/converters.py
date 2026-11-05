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

"""Converters to convert stick figure data to different formats."""

import math
from typing import Any

import networkx as nx

from .. import bps_types
from . import stick as stick_lib
from . import stick_figure


class GraphValidationError(Exception):
  """Custom exception raised for errors during graph validation."""

  def __init__(self, message: str):
    self.message = message
    super().__init__(self.message)


def convert_stick_figure_to_networkx_graph(
    figure: stick_figure.StickFigure,
) -> nx.MultiGraph:
  """Converts a StickFigure object to a NetworkX graph.

  Nodes are joints and edges are sticks.

  Args:
    figure: The StickFigure object to convert.

  Returns:
    A NetworkX graph representation of the stick figure.
  """
  g = nx.MultiGraph()

  for stick in figure.children:
    g.add_edge(
        stick.start,
        stick.end,
        name=stick.name,
        length=stick.length,
        angle=stick.azimuth_angle,
    )
  return g


def fold_to_svg(
    json_data: dict[str, Any],
    keep_flat_creases: bool = False,
    flat_creases_black: bool = False,
    scale_factor: float = 1000.0,
    viewbox_size: float = 1000,
    render_size: float = 1000,
) -> str | None:
  """Converts a crease pattern in FOLD format to an SVG."""
  if not json_data:
    return None

  if not all(
      k in json_data
      for k in ["vertices_coords", "edges_vertices", "edges_assignment"]
  ):
    raise ValueError(
        "Missing one or more required keys (vertices_coords, edges_vertices,"
        " edges_assignment) in JSON data."
    )

  vertices_coords = json_data["vertices_coords"]
  edges_vertices = json_data["edges_vertices"]
  edges_assignment = json_data["edges_assignment"]

  svg_parts = []
  svg_parts.append(
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0'
      f' {viewbox_size} {viewbox_size}" width="{render_size}"'
      f' height="{render_size}">'
  )

  black_line_elements = []
  colored_line_elements = []

  if keep_flat_creases:
    color_map = {
        "M": "#f00",  # red
        "V": "#00f",  # blue
        "B": "#000",  # black
        "F": "#000" if flat_creases_black else "#ffff00",  # black or yellow
    }
  else:
    color_map = {
        "M": "#f00",  # red
        "V": "#00f",  # blue
        "B": "#000",  # black
    }

  for i, edge in enumerate(edges_vertices):
    if i >= len(edges_assignment):
      raise ValueError(
          "Edges assignment is shorter than edges vertices. Edges assignment:"
          f" {edges_assignment}, edges vertices: {edges_vertices}"
      )
    assignment = edges_assignment[i]

    if assignment not in color_map:
      continue

    if not (
        isinstance(edge, (list, tuple))
        and len(edge) == 2
        and isinstance(edge[0], int)
        and isinstance(edge[1], int)
        and 0 <= edge[0] < len(vertices_coords)
        and 0 <= edge[1] < len(vertices_coords)
    ):
      raise ValueError(
          f"Invalid or malformed edge entry at index {i}: {edge}. Expecting a"
          " list/tuple of two integers representing valid vertex indices (0 to"
          f" {len(vertices_coords) - 1})."
      )

    v1_coord_orig = vertices_coords[edge[0]]
    v2_coord_orig = vertices_coords[edge[1]]

    if not (
        isinstance(v1_coord_orig, (list, tuple))
        and len(v1_coord_orig) == 2
        and isinstance(v2_coord_orig, (list, tuple))
        and len(v2_coord_orig) == 2
    ):
      raise ValueError(
          f"Malformed coordinate data for edge {edge}. v1: {v1_coord_orig}, v2:"
          f" {v2_coord_orig}. Skipping edge."
      )

    try:
      v1_x = int(round(float(v1_coord_orig[0]) * scale_factor))
      v1_y = int(round(float(v1_coord_orig[1]) * scale_factor))
      v2_x = int(round(float(v2_coord_orig[0]) * scale_factor))
      v2_y = int(round(float(v2_coord_orig[1]) * scale_factor))
    except (ValueError, TypeError) as e:
      raise ValueError(
          f"Non-numeric coordinate data for edge {edge}. v1:"
          f" {v1_coord_orig}, v2: {v2_coord_orig}. Error: {e}. Skipping edge."
      ) from e

    color = color_map[assignment]
    line_element_str = (
        f'<line stroke="{color}" x1="{v1_x}" y1="{v1_y}" x2="{v2_x}"'
        f' y2="{v2_y}"/>'
    )

    if color == color_map["B"]:
      black_line_elements.append(line_element_str)
    else:
      colored_line_elements.append(line_element_str)

  svg_parts.extend(black_line_elements)
  svg_parts.extend(colored_line_elements)
  svg_parts.append("</svg>")

  return "".join(svg_parts)


def bps_to_stick_figure(
    bps: bps_types.BoxPleatingTreeData,
    shaping_flaps_limit: int = 0,
) -> stick_figure.StickFigure:
  """Converts a crease pattern in BPS format to a StickFigure."""
  del shaping_flaps_limit
  data = bps["design"]
  tree = data["tree"]
  nodes = {node["id"]: node for node in tree["nodes"]}

  children = []
  root_edge = tree["edges"][0]
  root_name = f"{nodes[root_edge['n1']]['id']}_{nodes[root_edge['n2']]['id']}"
  for edge in tree["edges"]:
    start = nodes[edge["n1"]]
    end = nodes[edge["n2"]]
    dy = end["y"] - start["y"]
    dx = end["x"] - start["x"]
    angle = (math.degrees(math.atan2(dy, dx)) - 90) % 360
    length = round(edge["length"] or 1)
    children.append(
        stick_lib.Stick(
            start=str(start["id"]),
            end=str(end["id"]),
            name=f"{start['id']}_{end['id']}",
            length=length,
            azimuth_angle=angle,
        )
    )

  return stick_figure.StickFigure(
      name=data["title"],
      category="",
      complexity=1,
      root=root_name,
      children=children,
  )
