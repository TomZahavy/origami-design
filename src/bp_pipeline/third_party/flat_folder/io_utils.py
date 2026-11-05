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
#
# Ported from Flat-Folder (https://github.com/origamimagiro/flat-folder),
# Copyright (c) 2022 Jason S. Ku (origamimagiro), licensed under the MIT
# License; see LICENSE in this directory.
# ==============================================================================

"""Utilities for reading and parsing origami file formats."""

import json
import re
import xml.etree.ElementTree as ET

from . import graph_creation
from . import graph_topology
from . import math_utils

Point = math_utils.Point
LineData = tuple[Point, Point, str]
# Graph represents origami structure:
# vertex_coords, vertex_vertex_map, edge_vertex_map, edge_assignments,
# edge_face_map, face_vertex_map, face_edge_map
Graph = tuple[
    list[Point] | None,
    list[list[int]] | None,
    list[list[int]] | None,
    list[str] | None,
    list[list[int | None]] | None,
    list[list[int]] | None,
    list[list[int | None]] | None,
]


def _flip_mountain_valley(assignments: list[str]) -> list[str]:
  """Swaps 'M' and 'V' assignments in a list.

  Args:
    assignments: A list of edge assignments, e.g., ['M', 'V', 'B'].

  Returns:
    A new list with 'M' and 'V' assignments swapped.
  """
  mountain_valley_map = {"M": "V", "V": "M"}
  return [
      mountain_valley_map.get(assignment, assignment)
      for assignment in assignments
  ]


def _flip_y(vertex_coords: list[Point]) -> list[Point]:
  """Flips the y-coordinate of vertices: y = 1 - y.

  Args:
    vertex_coords: A list of vertex coordinates.

  Returns:
    A new list of vertex coordinates with y-coordinates flipped.
  """
  return [(x, -y + 1) for x, y in vertex_coords]


def _svg_style_to_assignment(style: str | None) -> str:
  """Converts SVG style string to crease assignment.

  Args:
    style: The style attribute string from an SVG element.

  Returns:
    The crease assignment ('M', 'V', 'B', 'F', or 'U').
  """
  assignment = "U"
  if not style:
    return assignment
  pairs = style.split(";")
  for pair in pairs:
    parts = pair.split(":")
    if len(parts) == 2:
      attribute = parts[0].strip()
      value = parts[1].strip().lower()
      if attribute == "stroke":
        if value in ["red", "#ff0000"]:
          assignment = "M"
        elif value in ["blue", "#0000ff"]:
          assignment = "V"
        elif value in ["gray", "#808080"]:
          assignment = "F"
        elif value in ["black", "#000000"]:
          assignment = "B"
        break
  return assignment


def _parse_svg_path(d_attribute: str, assignment: str) -> list[LineData]:
  """Parses SVG path 'd' attribute into lines.

  Args:
    d_attribute: The 'd' attribute string from an SVG path element.
    assignment: The crease assignment for this path.

  Returns:
    A list of lines parsed from the path data.
  """
  lines = []
  tokens = re.findall(r"[A-Za-z]|-?[\d\.]+(?:e-?[\d]+)?", d_attribute)
  current_point: Point = (0.0, 0.0)
  start_point: Point = (0.0, 0.0)
  i = 0
  while i < len(tokens):
    command = tokens[i]
    if not command[0].isalpha():
      i += 1
      continue
    if command.upper() == "M":
      x = float(tokens[i + 1])
      y = float(tokens[i + 2])
      current_point = (x, y)
      start_point = (x, y)
      i += 3
    elif command.upper() == "L":
      x = float(tokens[i + 1])
      y = float(tokens[i + 2])
      next_point: Point = (x, y)
      lines.append((current_point, next_point, assignment))
      current_point = next_point
      i += 3
    elif command.upper() == "Z":
      if current_point != start_point:
        lines.append((current_point, start_point, assignment))
      i += 1
    else:
      i += 1  # Skip unknown commands
  return lines


def opx_to_lines(file_content: str) -> list[LineData]:
  """Parses an OPX file string into a list of lines.

  Args:
    file_content: The OPX file content as a string.

  Returns:
    A list of lines, each represented as ([x1,y1], [x2,y2], assignment).
  """
  try:
    root = ET.fromstring(file_content)
  except ET.ParseError:
    return []

  lines: list[LineData] = []
  coords = ["x0", "x1", "y0", "y1"]
  type_map = ["", "F", "M", "V", "U"]

  for opx_line in root.iter():
    if opx_line.tag.endswith("object"):
      line_data: dict[str, float] = {c: 0.0 for c in coords}
      type_index = 0
      valid_line = False

      for node in opx_line:
        prop = node.get("property")
        if prop and (prop in coords or prop == "type"):
          if node and node[0].text:
            val = float(node[0].text)
            if prop == "type":
              type_index = int(val)
            else:
              line_data[prop] = val
            valid_line = True

      if valid_line:
        assignment = type_map[type_index] if type_index < len(type_map) else "F"
        lines.append((
            (line_data["x0"], line_data["y0"]),
            (line_data["x1"], line_data["y1"]),
            assignment,
        ))
  return lines


def cp_to_lines(file_content: str) -> list[LineData]:
  """Parses a CP file string into a list of lines.

  Args:
    file_content: The CP file content as a string.

  Returns:
    A list of lines, each represented as ([x1,y1], [x2,y2], assignment).
  """
  type_map = ["U", "B", "M", "V", "F"]
  lines: list[LineData] = []
  for line in file_content.splitlines():
    line = line.strip()
    if not line:
      continue
    parts = line.split()
    if len(parts) < 5:
      continue
    try:
      assignment_index = int(parts[0])
      coords = [float(x) for x in parts[1:5]]
      assignment = (
          type_map[assignment_index]
          if assignment_index < len(type_map)
          else "U"
      )
      lines.append(((coords[0], coords[1]), (coords[2], coords[3]), assignment))
    except ValueError:
      continue
  return lines


def svg_to_lines(file_content: str) -> list[LineData]:
  """Parses an SVG file string into a list of lines.

  Args:
    file_content: The SVG file content as a string.

  Returns:
    A list of lines, each represented as ([x1,y1], [x2,y2], assignment).
  """
  if file_content.strip().startswith("<?xml"):
    try:
      _, file_content = file_content.split("?>", 1)
    except ValueError:
      pass

  try:
    root = ET.fromstring(file_content)
  except ET.ParseError:
    return []

  lines: list[LineData] = []

  for element in root.iter():
    tag = element.tag.split("}")[-1]
    style = element.get("style")
    assignment = _svg_style_to_assignment(style)

    if tag == "line":
      x1 = float(element.get("x1", 0))
      y1 = float(element.get("y1", 0))
      x2 = float(element.get("x2", 0))
      y2 = float(element.get("y2", 0))
      lines.append(((x1, y1), (x2, y2), assignment))

    elif tag == "polyline" or tag == "polygon":
      points_str = element.get("points", "").replace(",", " ")
      points_coords = [float(x) for x in points_str.split() if x.strip()]

      points: list[Point] = []
      for i in range(0, len(points_coords), 2):
        if i + 1 < len(points_coords):
          points.append((points_coords[i], points_coords[i + 1]))

      if tag == "polygon" and len(points) > 2:
        points.append(points[0])

      for i in range(1, len(points)):
        lines.append((points[i - 1], points[i], assignment))

    elif tag == "path":
      d_attribute = element.get("d", "")
      lines.extend(_parse_svg_path(d_attribute, assignment))
  return lines


def fold_to_graph(
    file_content: str,
) -> tuple[
    list[Point],
    list[list[int]],
    list[str],
    list[list[int]] | None,
    list[list[int]] | None,
]:
  """Parses a FOLD file string into graph structures.

  Args:
    file_content: The FOLD file content as a string.

  Returns:
    A tuple containing vertex_coords, edge_vertex_map, edge_assignments,
    vertex_vertex_map, and face_vertex_map.
  """
  try:
    data = json.loads(file_content)
  except Exception as exc:
    raise ValueError("Invalid JSON") from exc

  vertex_coords_raw = data.get("vertices_coords")
  if not vertex_coords_raw:
    raise ValueError("Missing vertices_coords")
  vertex_coords: list[Point] = [tuple(p) for p in vertex_coords_raw]

  edge_vertex_map_raw: list[list[int]] = data.get("edges_vertices")
  if not edge_vertex_map_raw:
    raise ValueError("Missing edges_vertices")
  edge_vertex_map: list[list[int]] = [
      [v1, v2] if v1 < v2 else [v2, v1] for v1, v2 in edge_vertex_map_raw
  ]

  edge_assignments: list[str] = data.get("edges_assignment")
  if not edge_assignments:
    edge_assignments = ["U"] * len(edge_vertex_map)

  face_vertex_map: list[list[int]] | None = data.get("faces_vertices")
  vertex_vertex_map: list[list[int]] | None = None

  if face_vertex_map:
    math_utils.sort_faces(face_vertex_map, vertex_coords)
    vertex_vertex_map = graph_topology.faces_to_adjacency(
        vertex_coords, face_vertex_map
    )
  else:
    lines_list = [math_utils.expand(e, vertex_coords) for e in edge_vertex_map]
    lines = [tuple(l) for l in lines_list]
    vertex_coords, edge_vertex_map, _, _ = (
        graph_creation.create_graph_from_lines(lines)  # pyrefly: ignore[bad-argument-type]
    )
    edge_assignments = ["F"] * len(edge_vertex_map)

  return (
      vertex_coords,
      edge_vertex_map,
      edge_assignments,
      vertex_vertex_map,
      face_vertex_map,
  )


def parse_document(
    doc: str, file_extension: str, flip_to_top_face_up: bool
) -> Graph:
  """Parses a document string into a graph based on file extension.

  Args:
    doc: The file content as a string.
    file_extension: The file extension (e.g., "fold", "svg", "cp", "opx").
    flip_to_top_face_up: If True, flip geometry so top face is face-up.

  Returns:
    A tuple containing V, VV, EV, EA, EF, FV, FE.
  """
  vertex_vertex_map: list[list[int]] | None = None
  face_vertex_map: list[list[int]] | None = None

  if file_extension == "fold":
    try:
      (
          vertex_coords,
          edge_vertex_map,
          edge_assignments,
          vertex_vertex_map,
          face_vertex_map,
      ) = fold_to_graph(doc)
    except ValueError:
      return None, None, None, None, None, None, None
  else:
    if file_extension == "svg":
      lines = svg_to_lines(doc)
    elif file_extension == "cp":
      lines = cp_to_lines(doc)
    elif file_extension == "opx":
      lines = opx_to_lines(doc)
    else:
      return None, None, None, None, None, None, None

    vertex_coords, edge_vertex_map, edges_lines, _ = (
        graph_creation.create_graph_from_lines([(l[0], l[1]) for l in lines])
    )
    edge_assignments = []
    for edge_lines_indices in edges_lines:
      assignment = "F"
      for line_idx in edge_lines_indices:
        if line_idx < len(lines) and lines[line_idx][2] != "F":
          assignment = lines[line_idx][2]
          break
      edge_assignments.append(assignment)

  if face_vertex_map is None:
    if flip_to_top_face_up:
      edge_assignments = _flip_mountain_valley(edge_assignments)
    else:
      vertex_coords = _flip_y(vertex_coords)
    vertex_vertex_map, face_vertex_map = (
        graph_topology.graph_to_adjacency_and_faces(
            vertex_coords, edge_vertex_map
        )
    )
  else:
    if face_vertex_map and (
        math_utils.polygon_twice_signed_area(
            math_utils.expand(face_vertex_map[0], vertex_coords)
        )
        < 0
    ):
      edge_assignments = _flip_mountain_valley(edge_assignments)
      for face in face_vertex_map:
        face.reverse()
    if not flip_to_top_face_up:
      edge_assignments = _flip_mountain_valley(edge_assignments)
      for face in face_vertex_map:
        face.reverse()
      vertex_coords = _flip_y(vertex_coords)

  edge_face_map, face_edge_map = graph_topology.build_edge_face_maps(
      edge_vertex_map, face_vertex_map
  )

  if face_vertex_map and len(face_vertex_map) > 1:
    new_face_vertex_map = []
    for i, face in enumerate(face_vertex_map):
      all_boundary = True
      for edge_idx in face_edge_map[i]:
        if edge_assignments[edge_idx] != "B":  # pyrefly: ignore[bad-index]
          all_boundary = False
          break
      if not all_boundary:
        new_face_vertex_map.append(face)
    face_vertex_map = new_face_vertex_map
    if len(face_vertex_map) != len(face_edge_map):
      edge_face_map, face_edge_map = graph_topology.build_edge_face_maps(
          edge_vertex_map, face_vertex_map
      )

  for i, face_pair in enumerate(edge_face_map):
    if len(face_pair) == 1:
      edge_assignments[i] = "B"

  return (  # pyrefly: ignore[bad-return]
      vertex_coords,
      vertex_vertex_map,
      edge_vertex_map,
      edge_assignments,
      edge_face_map,
      face_vertex_map,
      face_edge_map,
  )
