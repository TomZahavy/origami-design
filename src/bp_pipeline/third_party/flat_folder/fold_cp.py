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

"""A script to analyze and visualize flat-foldable origami crease patterns."""

import dataclasses
import json
from typing import Any, Self, TypedDict

from absl import logging as absl_logging

from . import constraints
from . import face_constraints
from . import folded_state
from . import graph_creation
from . import graph_topology
from . import io_utils
from . import logging
from . import math_utils
from . import solver
from . import svg

Point = math_utils.Point


class _State(TypedDict):
  region_polygons: list[list[int]]
  region_faces: list[int | bool | None]
  folded_vertices: list[Point]
  segment_points: list[list[int]]
  segment_display: list[str]


class _Report(TypedDict):
  folded_states: list[_State]


@dataclasses.dataclass(frozen=True, kw_only=True)
class FlatFolderFOLD:
  """Flat Folder result, parsed from the JSON output."""

  file: str | None
  flat_foldable: bool | None
  states: int | None
  folded_state_fold: dict[str, Any] | None
  folded_state_svg: str | None
  folded_state_svg_back: str | None
  conflict_reason: str | None
  conflict_faces: list[int] = dataclasses.field(default_factory=list)
  local_violations: list[str] = dataclasses.field(default_factory=list)
  computation_log: list[str] = dataclasses.field(default_factory=list)

  @classmethod
  def from_bytes(cls, raw_bytes: bytes) -> Self:
    """Creates a FlatFolderFOLD instance from raw JSON bytes."""
    parsed_json = json.loads(raw_bytes.decode())
    return cls.from_report_dict(parsed_json)

  @classmethod
  def from_report_dict(cls, report: dict[str, Any]) -> Self:
    """Creates a FlatFolderFOLD from a report dictionary."""
    return cls(
        file=report.get("file"),
        flat_foldable=report.get("flat_foldable"),
        states=report.get("states"),
        folded_state_fold=report.get("folded_state_fold"),
        folded_state_svg=report.get("folded_state_svg"),
        folded_state_svg_back=report.get("folded_state_svg_back"),
        conflict_reason=report.get("conflict_reason"),
        conflict_faces=report.get("conflict_faces") or [],
        local_violations=report.get("local_violations") or [],
        computation_log=report.get("computation_log") or [],
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class FlatFolderOutput:
  flat_folder_fold: FlatFolderFOLD


GUI_COLORS = {
    "background": "lightgray",
    "edge": {"F": "#CCC", "B": "#000"},
    "face": {"top": "#AAA", "bottom": "#FFF"},
}


def _create_svg_data(
    cell_face_indices: list[int | None],
    segment_cells: list[list[int]],
    segment_edges: list[list[int]],
    edge_faces: list[list[int]],
    face_orientations: list[bool | None],
    cell_vertices: list[list[int]],
    points: list[Point],
    segment_points: list[list[int]],
    invert_colors: bool,
    mirror_display: bool = False,
) -> str:
  """Computes SVG visualization for one view of the folded state."""
  segment_display = folded_state.compute_segment_display_properties(
      cell_face_indices,
      segment_cells,
      segment_edges,
      edge_faces,  # pyrefly: ignore[bad-argument-type]
      face_orientations,  # pyrefly: ignore[bad-argument-type]
  )
  region_polygons, region_faces = folded_state.compute_folded_regions(
      cell_face_indices,
      cell_vertices,
      segment_cells,
      segment_display,
      face_orientations,  # pyrefly: ignore[bad-argument-type]
      points,
  )
  visualization_report = {
      "folded_states": [{
          "region_polygons": region_polygons,
          "region_faces": region_faces,
          "folded_vertices": points,
          "segment_points": segment_points,
          "segment_display": segment_display,
      }]
  }
  return visualize_folded_state(
      visualization_report,  # pyrefly: ignore[bad-argument-type]
      invert_colors=invert_colors,
      face_frames=face_orientations,
      mirror_display=mirror_display,
  )


def get_absolute_face_orders_from_edges(
    edges: list[tuple[int, int]], num_faces: int
) -> list[int]:
  """Computes the absolute face orders from a list of face pairs.

  Face order 0 corresponds to the bottom-most face.

  Args:
    edges: A list of face pairs (top, bottom).
    num_faces: The total number of faces.

  Returns:
    A list of face orders, where each index corresponds to a face and the
    value is its stacking order.
  """
  adjacency_list = [[] for _ in range(num_faces)]
  in_degree = [0] * num_faces

  for edge_key in edges:
    top_face, bottom_face = math_utils.tuple_to_list(edge_key)
    if top_face < num_faces and bottom_face < num_faces:
      adjacency_list[bottom_face].append(top_face)
      in_degree[top_face] += 1

  face_orders = [0] * num_faces
  queue = [i for i in range(num_faces) if in_degree[i] == 0]

  head = 0
  while head < len(queue):
    bottom_face = queue[head]
    head += 1
    for top_face in adjacency_list[bottom_face]:
      face_orders[top_face] = max(
          face_orders[top_face], face_orders[bottom_face] + 1
      )
      in_degree[top_face] -= 1
      if in_degree[top_face] == 0:
        queue.append(top_face)
  return face_orders


def visualize_folded_state(
    report: _Report,
    invert_colors: bool = False,
    face_frames: list[bool | None] | None = None,
    mirror_display: bool = False,
) -> str:
  """Generates an SVG visualization of a folded state.

  Args:
    report: A dictionary containing folded state data.
    invert_colors: If True, inverts colors for back view.
    face_frames: A list of face orientations or reflection matrices.
    mirror_display: If True, mirrors the display horizontally.

  Returns:
    An SVG string representing the folded state.
  """
  folded_states = report["folded_states"]
  if not folded_states:
    return f'<svg xmlns="{svg.NAMESPACE}"/>'

  state_data = folded_states[0]
  region_polygons = state_data["region_polygons"]
  region_faces = state_data["region_faces"]
  folded_vertices = state_data["folded_vertices"]
  segment_points = state_data["segment_points"]
  segment_display = state_data["segment_display"]

  if not folded_vertices:
    return f'<svg xmlns="{svg.NAMESPACE}"/>'

  normalized_points = math_utils.normalize_points(folded_vertices)
  regions = [
      math_utils.expand(poly, normalized_points) for poly in region_polygons
  ]

  colors = []
  for face_or_orientation in region_faces:
    if face_or_orientation is None:
      colors.append(None)
    else:
      is_up = True

      # 1. Boolean (Direct mapping: True=Up, False=Down)
      # Note: In Python, isinstance(True, int) is True, so check bool first.
      if isinstance(face_or_orientation, bool):
        is_up = face_or_orientation

      # 2. Integer (Face Index -> Calculate from Matrix)
      elif isinstance(face_or_orientation, int) and face_frames is not None:
        face_index = face_or_orientation
        if 0 <= face_index < len(face_frames):
          frame = face_frames[face_index]
          # Matrix [a, b, c, d]
          if isinstance(frame, (list, tuple)) and len(frame) >= 4:
            determinant = frame[0] * frame[3] - frame[1] * frame[2]
            is_up = determinant > 0
          # Boolean Frame
          elif isinstance(frame, bool):
            is_up = frame
        else:
          # Fallback (assumes Face 0 is Up)
          is_up = face_index == 0

      # 3. Apply Inversion for Back View
      # If invert_colors is True, we flip the boolean.
      # (e.g. Face Up (True) -> Back View sees back (False/White))
      final_orientation = (not is_up) if invert_colors else is_up

      colors.append(
          GUI_COLORS["face"]["top"]
          if final_orientation
          else GUI_COLORS["face"]["bottom"]
      )

  lines = [
      math_utils.expand(points, normalized_points) for points in segment_points
  ]

  content = []

  # 1. Polygons (Faces)
  content.append(
      svg.draw_polygons(
          regions,
          {
              "fill": colors,
              "stroke": GUI_COLORS["edge"]["B"],
              "stroke-width": 0.5,
          },
      )
  )

  # 2. Creases
  content.append(
      svg.draw_segments(
          lines,  # pyrefly: ignore[bad-argument-type]
          {
              "stroke": GUI_COLORS["edge"]["F"],
              "filter": lambda i: segment_display[i] == "C",
          },
      )
  )

  # 3. Edges (Outline)
  content.append(
      svg.draw_segments(
          lines,  # pyrefly: ignore[bad-argument-type]
          {
              "stroke": GUI_COLORS["edge"]["B"],
              "filter": (
                  lambda i: segment_display[i]
                  and segment_display[i].startswith("B")
              ),
          },
      )
  )

  if mirror_display:
    g_attribs = f' transform="scale(-1, 1) translate(-{svg.SCALE}, 0)"'
    svg_content = f"<g{g_attribs}>{''.join(content)}</g>"
  else:
    svg_content = "".join(content)

  svg_str = f'{svg.header(f"0 0 {svg.SCALE} {svg.SCALE}")}{svg_content}</svg>'
  return svg_str


def analyze_fold_file(
    filename, doc_content, file_ext, generate_state_data, kawasaki_epsilon=5e-2
):
  """Analyzes a given origami file for flat-foldability.

  Args:
    filename: The name of the file being analyzed.
    doc_content: The content of the file.
    file_ext: The file extension (e.g., ".fold", ".cp", ".svg").
    generate_state_data: If True, generates folded state data including SVGs.
    kawasaki_epsilon: Tolerance for Kawasaki's theorem check.

  Returns:
    A FlatFolderOutput object containing the analysis report.
  """
  constraints.Constraints.build_implication_tables()
  type_ext = file_ext.replace(".", "").lower()
  processed_doc = doc_content

  if type_ext == "svg":
    lines = io_utils.svg_to_lines(doc_content)
    lines_str = []
    assignment_map = {"U": 5, "B": 1, "M": 2, "V": 3, "F": 4}
    for point1, point2, assignment in lines:
      lines_str.append(
          f"{assignment_map.get(assignment, 5)} {point1[0]} {point1[1]}"
          f" {point2[0]} {point2[1]}"
      )
    processed_doc = "\n".join(lines_str)
    type_ext = "cp"

  report = {
      "file": filename,
      "flat_foldable": False,
      "states": 0,
      "folded_state_fold": None,
      "folded_state_svg": None,
      "folded_state_svg_back": None,
      "conflict_reason": None,
      "conflict_faces": [],
      "local_violations": [],
      "computation_log": [],
  }

  parse_result = io_utils.parse_document(processed_doc, type_ext, True)
  if parse_result[0] is None:
    report["conflict_reason"] = "IO Parser failed"  # pyrefly: ignore[bad-assignment]
    return FlatFolderOutput(
        flat_folder_fold=FlatFolderFOLD.from_report_dict(report)
    )

  (
      vertex_coords,
      vertex_vertex_map,
      edge_vertex_map,
      edge_assignments,
      edge_faces,
      face_vertices,
      _,
  ) = parse_result

  vertex_foldability_results = folded_state.check_vertex_foldability(
      vertex_coords,  # pyrefly: ignore[bad-argument-type]
      vertex_vertex_map,  # pyrefly: ignore[bad-argument-type]
      edge_vertex_map,  # pyrefly: ignore[bad-argument-type]
      edge_assignments,  # pyrefly: ignore[bad-argument-type]
      report["computation_log"],
      kawasaki_epsilon,
  )

  for idx, result in enumerate(vertex_foldability_results):
    if result["type"] == "maekawa":
      report["local_violations"].append(
          f"v{idx} Maekawa Error |M-V|={result['deviation']}"
      )
    elif (
        result["type"] == "kawasaki" and result["deviation"] > kawasaki_epsilon  # pyrefly: ignore[unsupported-operation]
    ):
      report["local_violations"].append(
          f"v{idx} Kawasaki Error dev={result['deviation']:.2e}"
      )

  if report["local_violations"]:
    report["conflict_reason"] = "Local violations found"  # pyrefly: ignore[bad-assignment]
    return FlatFolderOutput(
        flat_folder_fold=FlatFolderFOLD.from_report_dict(report)
    )

  try:
    folded_vertices, face_orientations = folded_state.compute_folded_state(
        vertex_coords, face_vertices, edge_vertex_map, edge_assignments  # pyrefly: ignore[bad-argument-type]
    )
    lines_list = [
        math_utils.expand(p, folded_vertices) for p in edge_vertex_map  # pyrefly: ignore[bad-argument-type, not-iterable]
    ]
    lines = [tuple(l) for l in lines_list]
    points, segment_points, segment_edges, _ = (
        graph_creation.create_graph_from_lines(lines)  # pyrefly: ignore[bad-argument-type]
    )

    if not points:
      raise RuntimeError("Precision Error: unstable graph")

    _, cell_vertices = graph_topology.graph_to_adjacency_and_faces(
        points, segment_points
    )
    segment_cells, _ = graph_topology.build_edge_face_maps(
        segment_points, cell_vertices
    )
    cell_faces, face_cells = face_constraints.compute_cell_face_mappings(
        edge_faces,  # pyrefly: ignore[bad-argument-type]
        face_vertices,  # pyrefly: ignore[bad-argument-type]
        segment_points,
        segment_edges,
        cell_vertices,
        segment_cells,
    )
    face_pairs = face_constraints.compute_transitive_face_pairs(
        edge_faces, segment_points, segment_edges, cell_vertices, cell_faces  # pyrefly: ignore[bad-argument-type]
    )

    face_pair_to_index = {f: i for i, f in enumerate(face_pairs)}
    constraint_table = face_constraints.build_face_pair_constraint_table(
        face_pairs,
        face_pair_to_index,
        edge_faces,  # pyrefly: ignore[bad-argument-type]
        segment_edges,
        cell_faces,
        segment_cells,
    )
    face_components = face_constraints.build_face_graph_components(
        face_cells, constraint_table
    )

    trans_count = {"all": 0, "reduced": 0}
    initial_assignments = solver.get_initial_assignments_from_creases(
        edge_faces,  # pyrefly: ignore[bad-argument-type]
        edge_assignments,  # pyrefly: ignore[bad-argument-type]
        face_orientations,  # pyrefly: ignore[bad-argument-type]
        face_pairs,
        face_pair_to_index,
    )

    propagation_result = solver.propagate_initial_assignments(
        initial_assignments,
        face_pairs,
        constraint_table,
        face_pair_to_index,
        face_cells,
        cell_faces,
        face_components,
        trans_count,
    )

    if (
        isinstance(propagation_result, list)
        and len(propagation_result) == 3
        and isinstance(propagation_result[2], list)
    ):
      type_id, _, conflict_faces = propagation_result
      report["conflict_reason"] = (
          f"{constraints.Constraints.names[type_id]} conflict"  # pyrefly: ignore[bad-assignment, bad-index]
      )
      report["conflict_faces"] = conflict_faces  # pyrefly: ignore[bad-assignment]
      return FlatFolderOutput(
          flat_folder_fold=FlatFolderFOLD.from_report_dict(report)
      )

    assignments = propagation_result
    assignment_components = solver.get_assignment_components(
        face_pair_to_index,
        face_pairs,
        constraint_table,
        assignments,  # pyrefly: ignore[bad-argument-type]
        face_cells,
        cell_faces,
        face_components,
        trans_count,
    )
    solved_components = solver.solve_all_components(
        face_pair_to_index,
        face_pairs,
        constraint_table,
        assignments,  # pyrefly: ignore[bad-argument-type]
        assignment_components,
        face_cells,
        cell_faces,
        face_components,
        1,
    )

    if isinstance(solved_components, int):
      raise RuntimeError(f"Solver failed on component {solved_components}")

    num_states = 1
    for component_solution in solved_components:
      num_states *= len(component_solution)
    report["states"] = num_states

    if num_states > 0:
      report["flat_foldable"] = True
      if generate_state_data:
        logging.NOTE.log("   - Generating folded state data...")
        group_indices = [0] * len(solved_components)
        edges = face_constraints.get_ordered_face_pairs_from_assignments(
            face_pairs, assignment_components, solved_components, group_indices
        )

        report["folded_state_fold"] = {  # pyrefly: ignore[bad-assignment]
            "vertices_coords": folded_vertices,
            "edges_vertices": edge_vertex_map,
            "faces_vertices": face_vertices,
            "faceOrders": [
                get_absolute_face_orders_from_edges(edges, len(face_vertices))  # pyrefly: ignore[bad-argument-type]
            ],
            "faceOrientations": face_orientations,
        }

        cell_faces_ordered = face_constraints.sort_faces_in_cells_by_order(
            cell_faces, edges
        )

        # Front view
        cell_top_face_front = [
            (s[-1] if s else None) for s in cell_faces_ordered
        ]
        report["folded_state_svg"] = _create_svg_data(  # pyrefly: ignore[bad-assignment]
            cell_top_face_front,
            segment_cells,
            segment_edges,
            edge_faces,  # pyrefly: ignore[bad-argument-type]
            face_orientations,
            cell_vertices,
            points,
            segment_points,
            invert_colors=False,
        )

        # Back view
        cell_top_face_back = [(s[0] if s else None) for s in cell_faces_ordered]
        report["folded_state_svg_back"] = _create_svg_data(  # pyrefly: ignore[bad-assignment]
            cell_top_face_back,
            segment_cells,
            segment_edges,
            edge_faces,  # pyrefly: ignore[bad-argument-type]
            face_orientations,
            cell_vertices,
            points,
            segment_points,
            invert_colors=True,
            mirror_display=True,
        )

  except (IndexError, KeyError, RuntimeError, TypeError, ValueError) as e:
    report["flat_foldable"] = False
    if not report["conflict_reason"]:
      report["conflict_reason"] = str(e)  # pyrefly: ignore[bad-assignment]
      absl_logging.debug(
          "Flat-folder analysis failed on %s: %s", filename, e, exc_info=True
      )

  return FlatFolderOutput(
      flat_folder_fold=FlatFolderFOLD.from_report_dict(report)
  )
