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

"""Pure-Python 3D hinge-rotation mesh folder and Matplotlib shaded renderer."""

import collections
from collections.abc import Sequence
import dataclasses
import math
import pathlib
import typing
from typing import Any

from matplotlib import axes
from matplotlib import collections as mpl_collections
from matplotlib import patches
import matplotlib.pyplot as plt

from . import bus
from .crease_pattern import crease as crease_lib
from .crease_pattern import crease_pattern as cp_lib

_FOLD_PRECEDENCE = {'M': 3, 'V': 3, 'F': 2, 'B': 1, 'U': 0}
_DEFAULT_PAPER_RGB = (0.85, 0.745, 0.596)

_TURNAROUND_VIEWS: tuple[tuple[str, float, float, float], ...] = (
    ('1. 3D Isometric (3/4 View)', -0.62, 0.38, 0.0),
    ('2. Side Profile View', -1.32, 0.22, 0.0),
    ('3. Front-Oblique View', -0.22, 0.20, 0.0),
    ('4. Top-Down Dorsal View', -0.20, 1.22, 0.0),
)


@dataclasses.dataclass(frozen=True)
class FoldedMesh3D:
  """Planar crease-pattern topology and its 3D BFS hinge-folded geometry."""

  vertices_2d: list[tuple[float, float]]
  vertices_3d: list[tuple[float, float, float]]
  faces: list[list[int]]
  edges: list[tuple[int, int]]
  edges_assignment: list[str]
  edges_fold_angle: list[float]
  edge_key_angle: dict[tuple[int, int], float]

  def to_fold_dict(self, title: str = 'model') -> dict[str, Any]:
    """Serializes this 3D folded mesh to a FOLD v1.1 `foldedForm` dictionary."""
    return mesh_to_fold_dict(self, title)


def _get_vertex_index(
    x: float,
    y: float,
    vertices: list[tuple[float, float]],
    tol: float,
) -> int:
  """Finds an existing vertex within `tol` or appends a new vertex."""
  tol_sq = tol * tol
  for idx, (vx, vy) in enumerate(vertices):
    dx = vx - x
    dy = vy - y
    if dx * dx + dy * dy < tol_sq:
      return idx
  vertices.append((x, y))
  return len(vertices) - 1


def _crease_assignment_and_angle(
    fold: crease_lib.Fold,
    fold_percent: float,
) -> tuple[str, float]:
  """Maps a `Fold` enum and `fold_percent` to FOLD assignment and angle."""
  clamped_pct = max(0.0, min(1.0, float(fold_percent)))
  match fold:
    case crease_lib.Fold.MOUNTAIN | crease_lib.Fold.MOUNTAIN_ZEBRA:
      return ('M', -180.0 * clamped_pct)
    case crease_lib.Fold.VALLEY | crease_lib.Fold.VALLEY_ZEBRA:
      return ('V', 180.0 * clamped_pct)
    case crease_lib.Fold.BORDER:
      return ('B', 0.0)
    case crease_lib.Fold.HINGE | crease_lib.Fold.TRIANGLE:
      return ('F', 0.0)
    case _ as unreachable:
      typing.assert_never(unreachable)


def _split_collinear_edges(
    vertices: Sequence[tuple[float, float]],
    edges: Sequence[dict[str, Any]],
    tol: float,
) -> list[dict[str, Any]]:
  """Splits edges whenever another vertex lies strictly in their interior."""
  num_vertices = len(vertices)
  split_edges: list[dict[str, Any]] = []
  for edge in edges:
    v1 = edge['v1']
    v2 = edge['v2']
    ax_pt, ay_pt = vertices[v1]
    bx_pt, by_pt = vertices[v2]
    ab_x = bx_pt - ax_pt
    ab_y = by_pt - ay_pt
    len_sq = ab_x * ab_x + ab_y * ab_y
    if len_sq < 1e-10:
      continue
    length = math.sqrt(len_sq)
    dot_limit = tol * length
    min_x = min(ax_pt, bx_pt) - tol
    max_x = max(ax_pt, bx_pt) + tol
    min_y = min(ay_pt, by_pt) - tol
    max_y = max(ay_pt, by_pt) + tol

    splits: list[tuple[float, int]] = []
    for idx in range(num_vertices):
      if idx in (v1, v2):
        continue
      vx, vy = vertices[idx]
      if vx < min_x or vx > max_x or vy < min_y or vy > max_y:
        continue
      av_x = vx - ax_pt
      av_y = vy - ay_pt
      cross = abs(ab_x * av_y - ab_y * av_x)
      if cross / length < tol:
        dot = ab_x * av_x + ab_y * av_y
        if dot_limit < dot < len_sq - dot_limit:
          splits.append((dot, idx))

    if not splits:
      split_edges.append(edge)
      continue

    splits.sort(key=lambda item: item[0])
    chain = [v1] + [idx for _, idx in splits] + [v2]
    for k in range(len(chain) - 1):
      if chain[k] != chain[k + 1]:
        split_edges.append({
            'v1': chain[k],
            'v2': chain[k + 1],
            'assignment': edge['assignment'],
            'fold_angle': edge['fold_angle'],
        })
  return split_edges


def _extract_planar_graph(
    cp: cp_lib.CreasePattern,
    tol: float = 0.001,
) -> tuple[
    list[tuple[float, float]],
    list[dict[str, Any]],
    dict[tuple[int, int], dict[str, Any]],
]:
  """Builds a split planar vertex-and-edge graph from a `CreasePattern`."""
  vertices: list[tuple[float, float]] = []
  raw_edges_map: dict[tuple[int, int], dict[str, Any]] = {}

  def add_segment(
      x1: float,
      y1: float,
      x2: float,
      y2: float,
      assignment: str,
      fold_angle: float,
  ) -> None:
    if math.hypot(x1 - x2, y1 - y2) < 1e-5:
      return
    v1 = _get_vertex_index(x1, y1, vertices, tol)
    v2 = _get_vertex_index(x2, y2, vertices, tol)
    if v1 == v2:
      return
    key = (min(v1, v2), max(v1, v2))
    existing = raw_edges_map.get(key)
    cur_prec = _FOLD_PRECEDENCE.get(assignment, 0)
    ex_prec = (
        _FOLD_PRECEDENCE.get(existing['assignment'], 0) if existing else -1
    )
    if cur_prec > ex_prec:
      raw_edges_map[key] = {
          'v1': v1,
          'v2': v2,
          'assignment': assignment,
          'fold_angle': fold_angle,
      }

  # Seed the four unit-square sheet borders so the boundary stays watertight.
  border_corners = [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]
  for i in range(4):
    c1 = border_corners[i]
    c2 = border_corners[(i + 1) % 4]
    add_segment(c1[0], c1[1], c2[0], c2[1], 'B', 0.0)

  for crease_line in cp.creases:
    assign, angle = _crease_assignment_and_angle(
        crease_line.fold,
        crease_line.fold_percent,
    )
    add_segment(
        crease_line.p1.x - 0.5,
        crease_line.p1.y - 0.5,
        crease_line.p2.x - 0.5,
        crease_line.p2.y - 0.5,
        assign,
        angle,
    )

  split_edges = _split_collinear_edges(
      vertices, list(raw_edges_map.values()), tol
  )
  unique_map: dict[tuple[int, int], dict[str, Any]] = {}
  for edge in split_edges:
    key = (min(edge['v1'], edge['v2']), max(edge['v1'], edge['v2']))
    existing = unique_map.get(key)
    cur_prec = _FOLD_PRECEDENCE.get(edge['assignment'], 0)
    ex_prec = (
        _FOLD_PRECEDENCE.get(existing['assignment'], 0) if existing else -1
    )
    if cur_prec > ex_prec:
      unique_map[key] = edge

  unique_edges = list(unique_map.values())
  final_map = {
      (min(e['v1'], e['v2']), max(e['v1'], e['v2'])): {
          'assignment': e['assignment'],
          'fold_angle': e['fold_angle'],
      }
      for e in unique_edges
  }
  return vertices, unique_edges, final_map


def _find_planar_faces(
    vertices: Sequence[tuple[float, float]],
    edges: Sequence[dict[str, Any]],
) -> list[list[int]]:
  """Extracts minimal bounded planar faces via angular half-edge walking."""
  num_vertices = len(vertices)
  adj: list[list[int]] = [[] for _ in range(num_vertices)]
  for edge in edges:
    adj[edge['v1']].append(edge['v2'])
    adj[edge['v2']].append(edge['v1'])

  for v_idx in range(num_vertices):
    if not adj[v_idx]:
      continue
    x0, y0 = vertices[v_idx]
    adj[v_idx].sort(
        key=lambda nb, cx=x0, cy=y0: math.atan2(
            vertices[nb][1] - cy, vertices[nb][0] - cx
        )
    )

  next_half_edge: dict[tuple[int, int], int] = {}
  for v_idx, neighbors in enumerate(adj):
    degree = len(neighbors)
    for i, u_idx in enumerate(neighbors):
      next_half_edge[(u_idx, v_idx)] = neighbors[(i - 1) % degree]

  faces: list[list[int]] = []
  visited: set[tuple[int, int]] = set()
  for start_edge in next_half_edge:
    if start_edge in visited:
      continue
    u_idx, v_idx = start_edge
    face = [u_idx, v_idx]
    visited.add((u_idx, v_idx))
    start_vertex = u_idx
    w_idx = next_half_edge.get((u_idx, v_idx))
    broken = False
    steps = 0
    while w_idx != start_vertex:
      if w_idx is None or steps > 1000:
        broken = True
        break
      face.append(w_idx)
      visited.add((v_idx, w_idx))
      u_idx, v_idx = v_idx, w_idx
      w_idx = next_half_edge.get((u_idx, v_idx))
      steps += 1
    if broken or len(face) < 3:
      continue
    visited.add((face[-1], face[0]))
    signed_area = 0.0
    face_len = len(face)
    for i in range(face_len):
      p1 = vertices[face[i]]
      p2 = vertices[face[(i + 1) % face_len]]
      signed_area += p1[0] * p2[1] - p2[0] * p1[1]
    if signed_area > 1e-9:
      faces.append(list(reversed(face)))
  return faces


def _mat4_identity() -> list[float]:
  return [
      1.0,
      0.0,
      0.0,
      0.0,
      0.0,
      1.0,
      0.0,
      0.0,
      0.0,
      0.0,
      1.0,
      0.0,
      0.0,
      0.0,
      0.0,
      1.0,
  ]


def _mat4_mul(mat_a: Sequence[float], mat_b: Sequence[float]) -> list[float]:
  out = [0.0] * 16
  for row in range(4):
    for col in range(4):
      out[row * 4 + col] = (
          mat_a[row * 4 + 0] * mat_b[col]
          + mat_a[row * 4 + 1] * mat_b[4 + col]
          + mat_a[row * 4 + 2] * mat_b[8 + col]
          + mat_a[row * 4 + 3] * mat_b[12 + col]
      )
  return out


def _mat4_translation(tx: float, ty: float, tz: float) -> list[float]:
  return [
      1.0,
      0.0,
      0.0,
      tx,
      0.0,
      1.0,
      0.0,
      ty,
      0.0,
      0.0,
      1.0,
      tz,
      0.0,
      0.0,
      0.0,
      1.0,
  ]


def _mat4_rotation_axis(
    ax_x: float, ax_y: float, ax_z: float, rad: float
) -> list[float]:
  cos_a = math.cos(rad)
  sin_a = math.sin(rad)
  one_minus_c = 1.0 - cos_a
  return [
      one_minus_c * ax_x * ax_x + cos_a,
      one_minus_c * ax_x * ax_y - sin_a * ax_z,
      one_minus_c * ax_x * ax_z + sin_a * ax_y,
      0.0,
      one_minus_c * ax_x * ax_y + sin_a * ax_z,
      one_minus_c * ax_y * ax_y + cos_a,
      one_minus_c * ax_y * ax_z - sin_a * ax_x,
      0.0,
      one_minus_c * ax_x * ax_z - sin_a * ax_y,
      one_minus_c * ax_y * ax_z + sin_a * ax_x,
      one_minus_c * ax_z * ax_z + cos_a,
      0.0,
      0.0,
      0.0,
      0.0,
      1.0,
  ]


def _apply_mat4(
    mat: Sequence[float], x: float, y: float, z: float
) -> tuple[float, float, float]:
  return (
      mat[0] * x + mat[1] * y + mat[2] * z + mat[3],
      mat[4] * x + mat[5] * y + mat[6] * z + mat[7],
      mat[8] * x + mat[9] * y + mat[10] * z + mat[11],
  )


def _cross3(
    vec_a: tuple[float, float, float],
    vec_b: tuple[float, float, float],
) -> tuple[float, float, float]:
  return (
      vec_a[1] * vec_b[2] - vec_a[2] * vec_b[1],
      vec_a[2] * vec_b[0] - vec_a[0] * vec_b[2],
      vec_a[0] * vec_b[1] - vec_a[1] * vec_b[0],
  )


def _dot3(
    vec_a: tuple[float, float, float],
    vec_b: tuple[float, float, float],
) -> float:
  return vec_a[0] * vec_b[0] + vec_a[1] * vec_b[1] + vec_a[2] * vec_b[2]


def _select_centroid_face(
    vertices_2d: Sequence[tuple[float, float]],
    faces: Sequence[Sequence[int]],
) -> int:
  """Selects the face whose 2D centroid lies closest to the vertex centroid."""
  center_x = sum(v[0] for v in vertices_2d) / len(vertices_2d)
  center_y = sum(v[1] for v in vertices_2d) / len(vertices_2d)
  start_face = 0
  best_dist_sq = float('inf')
  for f_idx, face in enumerate(faces):
    fx = sum(vertices_2d[v][0] for v in face) / len(face)
    fy = sum(vertices_2d[v][1] for v in face) / len(face)
    dist_sq = (fx - center_x) ** 2 + (fy - center_y) ** 2
    if dist_sq < best_dist_sq:
      best_dist_sq = dist_sq
      start_face = f_idx
  return start_face


def _candidate_root_rivers(
    packed: bus.PackedCreasePattern,
) -> list[bus.River]:
  """Returns packed rivers ordered by preference for the root trunk stick."""
  root_name: str | None = None
  if packed.design is not None:
    root_name = packed.design.source.root
  elif packed.packed_tree is not None:
    root_name = packed.packed_tree.root

  if root_name is not None:
    exact = [
        rv
        for rv in packed.rivers.values()
        if rv.stick == root_name and rv.rects
    ]
    if exact:
      return exact

  on_axis = [rv for rv in packed.rivers.values() if rv.is_on_axis and rv.rects]
  if on_axis:
    return on_axis
  return [rv for rv in packed.rivers.values() if rv.rects]


def _select_anchor_face(
    vertices_2d: Sequence[tuple[float, float]],
    faces: Sequence[Sequence[int]],
    packed: bus.PackedCreasePattern | None,
) -> int:
  """Selects a stationary anchor facet inside the root trunk river region."""
  if packed is None or packed.grid_size <= 0 or not packed.rivers:
    return _select_centroid_face(vertices_2d, faces)

  gs = float(packed.grid_size)
  rivers = _candidate_root_rivers(packed)
  if not rivers:
    return _select_centroid_face(vertices_2d, faces)

  min_area = 0.08 / (gs * gs)
  band_half = max(2.5 / gs, 0.08)
  candidates: list[tuple[bool, bool, bool, float, float, int]] = []
  for river in rivers:
    for rect in river.rects:
      if rect.width <= 0 or rect.height <= 0:
        continue
      rx0 = rect.x / gs - 0.5 - 1e-4
      ry0 = rect.y / gs - 0.5 - 1e-4
      rx1 = (rect.x + rect.width) / gs - 0.5 + 1e-4
      ry1 = (rect.y + rect.height) / gs - 0.5 + 1e-4
      mid_x = 0.5 * (rx0 + rx1)
      mid_y = 0.5 * (ry0 + ry1)
      horiz_band = rect.width >= rect.height
      for f_idx, face in enumerate(faces):
        face_len = len(face)
        fx = sum(vertices_2d[v][0] for v in face) / face_len
        fy = sum(vertices_2d[v][1] for v in face) / face_len
        if not (rx0 <= fx <= rx1 and ry0 <= fy <= ry1):
          continue
        area2 = 0.0
        vert_len = 0.0
        horiz_len = 0.0
        for i in range(face_len):
          x1, y1 = vertices_2d[face[i]]
          x2, y2 = vertices_2d[face[(i + 1) % face_len]]
          area2 += x1 * y2 - x2 * y1
          edx, edy = abs(x2 - x1), abs(y2 - y1)
          if edx < 1e-4:
            vert_len += edy
          elif edy < 1e-4:
            horiz_len += edx
        area = abs(area2) * 0.5
        if horiz_band:
          spine_dist = abs(fx - 0.5 / gs) + 0.25 * abs(fy - mid_y)
          parallel_len = vert_len
        else:
          spine_dist = abs(fy - 0.5 / gs) + 0.25 * abs(fx - mid_x)
          parallel_len = horiz_len
        candidates.append((
            area < min_area,
            spine_dist > band_half,
            parallel_len < 1e-4,
            round(spine_dist, 4),
            -area,
            f_idx,
        ))

  if not candidates:
    return _select_centroid_face(vertices_2d, faces)
  candidates.sort()
  return candidates[0][5]


def _compute_stick_figure_joints(
    source_tree: Any,
) -> tuple[
    Any,
    dict[str, tuple[float, float, float]],
    set[str],
    set[str],
]:
  """Computes 3D joint positions and root start/end joint partitions."""
  root_stick = next(
      s for s in source_tree.children if s.name == source_tree.root
  )
  adj: dict[str, list[tuple[str, tuple[float, float, float]]]] = (
      collections.defaultdict(list)
  )
  for stick in source_tree.children:
    phi = math.radians(stick.azimuth_angle)
    psi = math.radians(stick.elevation_angle)
    length = float(stick.length)
    delta = (
        -length * math.cos(psi) * math.sin(phi),
        length * math.cos(psi) * math.cos(phi),
        length * math.sin(psi),
    )
    adj[stick.start].append((stick.end, delta))
    adj[stick.end].append((stick.start, (-delta[0], -delta[1], -delta[2])))

  coords: dict[str, tuple[float, float, float]] = {
      root_stick.start: (0.0, 0.0, 0.0)
  }
  queue = collections.deque([root_stick.start])
  while queue:
    curr = queue.popleft()
    cx, cy, cz = coords[curr]
    for nxt, (dx, dy, dz) in adj[curr]:
      if nxt not in coords:
        coords[nxt] = (cx + dx, cy + dy, cz + dz)
        queue.append(nxt)

  def _reachable(seed: str, blocked: str) -> set[str]:
    seen = {seed}
    walk = collections.deque([seed])
    while walk:
      node = walk.popleft()
      for nb, _ in adj[node]:
        if nb != blocked and nb not in seen:
          seen.add(nb)
          walk.append(nb)
    return seen

  return (
      root_stick,
      coords,
      _reachable(root_stick.start, root_stick.end),
      _reachable(root_stick.end, root_stick.start),
  )


def _align_points_to_camera_frame(
    raw_pts_3d: Sequence[tuple[float, float, float]],
    vertices_2d: Sequence[tuple[float, float]],
    anchor_face: Sequence[int],
    packed: bus.PackedCreasePattern | None,
) -> list[tuple[float, float, float]]:
  """Rotates folded 3D points via SO(3) into canonical `(X, Y=Up, Z=Front)`."""
  if (
      packed is None
      or packed.design is None
      or packed.grid_size <= 0
      or not packed.flaps
  ):
    return list(raw_pts_3d)

  design = packed.design
  source = design.source
  try:
    root_stick, sf_coords, start_joints, end_joints = (
        _compute_stick_figure_joints(source)
    )
  except StopIteration:
    return list(raw_pts_3d)

  stick_by_name = {s.name: s for s in source.children}
  gs = float(packed.grid_size)
  flap_samples: list[
      tuple[tuple[float, float, float], tuple[float, float, float]]
  ] = []
  start_xy: list[tuple[float, float]] = []
  end_xy: list[tuple[float, float]] = []

  for flap in packed.flaps.values():
    if flap.id != flap.stick:
      continue
    chain = design.merged_from.get(flap.stick, (flap.stick,))
    leaf_joint: str | None = None
    for s_name in chain:
      stick_obj = stick_by_name.get(s_name)
      if stick_obj is None:
        continue
      for j_name in (stick_obj.end, stick_obj.start):
        joint_obj = source.joints.get(j_name)
        if joint_obj is not None and joint_obj.degree == 1:
          leaf_joint = j_name
          break
      if leaf_joint is not None:
        break
    if leaf_joint is None or leaf_joint not in sf_coords:
      continue

    if flap.circle_centers:
      tx = flap.circle_centers[0].x / gs - 0.5
      ty = flap.circle_centers[0].y / gs - 0.5
    else:
      tx = (flap.rect.x + 0.5 * flap.rect.width) / gs - 0.5
      ty = (flap.rect.y + 0.5 * flap.rect.height) / gs - 0.5

    nearest_v = min(
        range(len(vertices_2d)),
        key=lambda idx, cx=tx, cy=ty: (
            (vertices_2d[idx][0] - cx) ** 2 + (vertices_2d[idx][1] - cy) ** 2
        ),
    )
    flap_samples.append((sf_coords[leaf_joint], raw_pts_3d[nearest_v]))
    if leaf_joint in start_joints:
      start_xy.append((tx, -ty))
    elif leaf_joint in end_joints:
      end_xy.append((tx, -ty))

  if not flap_samples or not start_xy or not end_xy:
    return list(raw_pts_3d)

  dv_x = sum(p[0] for p in end_xy) / len(end_xy) - (
      sum(p[0] for p in start_xy) / len(start_xy)
  )
  dv_y = sum(p[1] for p in end_xy) / len(end_xy) - (
      sum(p[1] for p in start_xy) / len(start_xy)
  )
  if abs(dv_y) >= abs(dv_x):
    e_along_m = (0.0, 1.0 if dv_y >= 0.0 else -1.0, 0.0)
    u_perp = (1.0, 0.0, 0.0)
  else:
    e_along_m = (1.0 if dv_x >= 0.0 else -1.0, 0.0, 0.0)
    u_perp = (0.0, 1.0, 0.0)

  phi = math.radians(root_stick.azimuth_angle)
  psi = math.radians(root_stick.elevation_angle)
  e_along_sf = (
      -math.cos(psi) * math.sin(phi),
      math.cos(psi) * math.cos(phi),
      math.sin(psi),
  )
  e_left_sf = (-math.cos(phi), -math.sin(phi), 0.0)
  e_norm_sf = _cross3(e_along_sf, e_left_sf)

  root_s = sf_coords[root_stick.start]
  root_e = sf_coords[root_stick.end]
  root_mid = (
      0.5 * (root_s[0] + root_e[0]),
      0.5 * (root_s[1] + root_e[1]),
      0.5 * (root_s[2] + root_e[2]),
  )
  anchor_3d = (
      sum(raw_pts_3d[v][0] for v in anchor_face) / len(anchor_face),
      sum(raw_pts_3d[v][1] for v in anchor_face) / len(anchor_face),
      sum(raw_pts_3d[v][2] for v in anchor_face) / len(anchor_face),
  )

  roll_candidates = (
      (0.0, 0.0, 1.0),
      (0.0, 0.0, -1.0),
      u_perp,
      (-u_perp[0], -u_perp[1], 0.0),
  )
  best_score = float('-inf')
  best_norm_m = roll_candidates[0]
  best_left_m = _cross3(best_norm_m, e_along_m)
  for e_norm_m in roll_candidates:
    e_left_m = _cross3(e_norm_m, e_along_m)
    norm_corr = 0.0
    left_corr = 0.0
    for p_sf, p_m in flap_samples:
      rel_sf = (
          p_sf[0] - root_mid[0],
          p_sf[1] - root_mid[1],
          p_sf[2] - root_mid[2],
      )
      rel_m = (
          p_m[0] - anchor_3d[0],
          p_m[1] - anchor_3d[1],
          p_m[2] - anchor_3d[2],
      )
      norm_corr += _dot3(rel_m, e_norm_m) * _dot3(rel_sf, e_norm_sf)
      left_corr += _dot3(rel_m, e_left_m) * _dot3(rel_sf, e_left_sf)
    score = 2.0 * norm_corr + left_corr
    if score > best_score + 1e-9:
      best_score = score
      best_norm_m = e_norm_m
      best_left_m = e_left_m

  aligned: list[tuple[float, float, float]] = []
  for pt_m in raw_pts_3d:
    c_a = _dot3(pt_m, e_along_m)
    c_l = _dot3(pt_m, best_left_m)
    c_n = _dot3(pt_m, best_norm_m)
    x_sf = c_a * e_along_sf[0] + c_l * e_left_sf[0] + c_n * e_norm_sf[0]
    y_sf = c_a * e_along_sf[1] + c_l * e_left_sf[1] + c_n * e_norm_sf[1]
    z_sf = c_a * e_along_sf[2] + c_l * e_left_sf[2] + c_n * e_norm_sf[2]
    # Right-handed SO(3) mapping to camera frame: +Y is dorsal up, +Z is front.
    aligned.append((-x_sf, z_sf, y_sf))
  return aligned


MeshTarget = (
    cp_lib.CreasePattern
    | bus.ShapedCreasePattern
    | bus.SolvedCreasePattern
    | bus.PipelineResult
)


def _unwrap_mesh_target(
    target: MeshTarget,
    packed: bus.PackedCreasePattern | None,
) -> tuple[cp_lib.CreasePattern, bus.PackedCreasePattern | None]:
  """Extracts `(CreasePattern, PackedCreasePattern | None)` from `target`."""
  if isinstance(target, bus.PipelineResult):
    return target.solved.creases, (packed or target.packed)
  if isinstance(target, (bus.ShapedCreasePattern, bus.SolvedCreasePattern)):
    return target.creases, (packed or target.packed)
  if isinstance(target, cp_lib.CreasePattern):
    return target, packed
  raise TypeError(
      'Expected CreasePattern, SolvedCreasePattern, ShapedCreasePattern, or'
      f' PipelineResult; got {type(target)!r}'
  )


def build_folded_mesh_3d(
    cp: MeshTarget,
    tol: float = 0.001,
    *,
    packed: bus.PackedCreasePattern | None = None,
) -> FoldedMesh3D:
  """Folds a shaped `CreasePattern` in 3D via BFS dihedral hinge rotations.

  Args:
    cp: Solved or shaped `CreasePattern` (or `ShapedCreasePattern`,
      `SolvedCreasePattern`, or `PipelineResult`) with `fold_percent` encoding
      target dihedral fold angles (`fold_percent * +-180` degrees).
    tol: Planar vertex snapping tolerance in unit-square coordinates.
    packed: Optional `PackedCreasePattern` used to anchor the stationary root
      facet inside the trunk river region and align the folded mesh into the
      canonical turnaround camera frame (`+Y` dorsal up, `+Z` anterior front).
      Automatically inferred when `cp` is a bus stage record.

  Returns:
    A `FoldedMesh3D` containing planar faces and centered 3D folded vertices.

  Raises:
    ValueError: If no bounded planar faces can be extracted from `cp`.
  """
  cp_obj, resolved_packed = _unwrap_mesh_target(cp, packed)
  raw_verts, raw_edges, raw_edges_map = _extract_planar_graph(cp_obj, tol=tol)
  raw_faces = _find_planar_faces(raw_verts, raw_edges)
  if not raw_faces:
    raise ValueError('No bounded planar faces found in crease pattern.')

  active_set: set[int] = set()
  for face in raw_faces:
    active_set.update(face)
  active_vertices = sorted(active_set)
  old_to_new = {old_i: new_i for new_i, old_i in enumerate(active_vertices)}
  vertices_2d = [raw_verts[i] for i in active_vertices]
  faces: list[list[int]] = []
  for face in raw_faces:
    faces.append([old_to_new[v] for v in face])

  edge_map: dict[tuple[int, int], tuple[int, int, tuple[int, int]]] = {}
  for face in faces:
    face_len = len(face)
    for i in range(face_len):
      u_idx, v_idx = face[i], face[(i + 1) % face_len]
      key = (min(u_idx, v_idx), max(u_idx, v_idx))
      if key not in edge_map:
        orig_u = active_vertices[u_idx]
        orig_v = active_vertices[v_idx]
        edge_map[key] = (
            u_idx,
            v_idx,
            (min(orig_u, orig_v), max(orig_u, orig_v)),
        )

  edges: list[tuple[int, int]] = []
  edges_assignment: list[str] = []
  edges_fold_angle: list[float] = []
  edge_key_angle: dict[tuple[int, int], float] = {}
  for u_idx, v_idx, orig_key in edge_map.values():
    edges.append((u_idx, v_idx))
    info = raw_edges_map.get(orig_key)
    assign = info['assignment'] if info else 'B'
    angle = float(info['fold_angle']) if info else 0.0
    edges_assignment.append(assign)
    edges_fold_angle.append(angle)
    edge_key_angle[(min(u_idx, v_idx), max(u_idx, v_idx))] = angle

  start_face = _select_anchor_face(vertices_2d, faces, resolved_packed)

  edge_to_faces: dict[tuple[int, int], list[int]] = {}
  for f_idx, face in enumerate(faces):
    face_len = len(face)
    for i in range(face_len):
      u_idx, v_idx = face[i], face[(i + 1) % face_len]
      key = (min(u_idx, v_idx), max(u_idx, v_idx))
      edge_to_faces.setdefault(key, []).append(f_idx)

  face_mats: list[list[float] | None] = [None] * len(faces)
  face_mats[start_face] = _mat4_identity()
  visited_faces = {start_face}
  queue = collections.deque([start_face])

  while queue:
    curr_f = queue.popleft()
    curr_mat = face_mats[curr_f]
    assert curr_mat is not None
    curr_verts = faces[curr_f]
    face_len = len(curr_verts)
    for i in range(face_len):
      v1, v2 = curr_verts[i], curr_verts[(i + 1) % face_len]
      key = (min(v1, v2), max(v1, v2))
      for next_f in edge_to_faces.get(key, ()):
        if next_f == curr_f or next_f in visited_faces:
          continue
        angle_deg = edge_key_angle.get(key, 0.0)
        p1 = _apply_mat4(curr_mat, vertices_2d[v1][0], vertices_2d[v1][1], 0.0)
        p2 = _apply_mat4(curr_mat, vertices_2d[v2][0], vertices_2d[v2][1], 0.0)
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dz = p2[2] - p1[2]
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        if length > 1e-9 and abs(angle_deg) > 1e-6:
          rad = math.radians(angle_deg)
          piv = _mat4_translation(p1[0], p1[1], p1[2])
          piv_inv = _mat4_translation(-p1[0], -p1[1], -p1[2])
          rot = _mat4_rotation_axis(dx / length, dy / length, dz / length, rad)
          transform = _mat4_mul(
              piv, _mat4_mul(rot, _mat4_mul(piv_inv, curr_mat))
          )
        else:
          transform = list(curr_mat)
        face_mats[next_f] = transform
        visited_faces.add(next_f)
        queue.append(next_f)

  num_v = len(vertices_2d)
  sum_xyz = [[0.0, 0.0, 0.0] for _ in range(num_v)]
  counts = [0] * num_v
  for f_idx, face in enumerate(faces):
    mat = face_mats[f_idx]
    if mat is None:
      continue
    for v_idx in face:
      px, py, pz = _apply_mat4(
          mat, vertices_2d[v_idx][0], vertices_2d[v_idx][1], 0.0
      )
      sum_xyz[v_idx][0] += px
      sum_xyz[v_idx][1] += py
      sum_xyz[v_idx][2] += pz
      counts[v_idx] += 1

  raw_pts_3d: list[tuple[float, float, float]] = []
  for idx in range(num_v):
    if counts[idx] > 0:
      raw_pts_3d.append((
          sum_xyz[idx][0] / counts[idx],
          -sum_xyz[idx][1] / counts[idx],
          sum_xyz[idx][2] / counts[idx],
      ))
    else:
      raw_pts_3d.append((vertices_2d[idx][0], -vertices_2d[idx][1], 0.0))

  aligned_pts_3d = _align_points_to_camera_frame(
      raw_pts_3d,
      vertices_2d,
      faces[start_face],
      resolved_packed,
  )
  cx = sum(p[0] for p in aligned_pts_3d) / num_v
  cy = sum(p[1] for p in aligned_pts_3d) / num_v
  cz = sum(p[2] for p in aligned_pts_3d) / num_v
  vertices_3d = [(p[0] - cx, p[1] - cy, p[2] - cz) for p in aligned_pts_3d]

  return FoldedMesh3D(
      vertices_2d=vertices_2d,
      vertices_3d=vertices_3d,
      faces=faces,
      edges=edges,
      edges_assignment=edges_assignment,
      edges_fold_angle=edges_fold_angle,
      edge_key_angle=edge_key_angle,
  )


def mesh_to_fold_dict(mesh: FoldedMesh3D, title: str) -> dict[str, Any]:
  """Serializes a `FoldedMesh3D` to a FOLD v1.1 `foldedForm` 3D JSON dict."""
  return {
      'file_spec': 1.1,
      'file_creator': 'bp_pipeline + render_3d',
      'file_title': f'{title} (3D Shaped Figure)',
      'file_classes': ['singleModel'],
      'frame_classes': ['foldedForm'],
      'frame_attributes': ['3D'],
      'vertices_coords': [
          [round(p[0], 6), round(p[1], 6), round(p[2], 6)]
          for p in mesh.vertices_3d
      ],
      'faces_vertices': mesh.faces,
      'edges_vertices': [list(e) for e in mesh.edges],
      'edges_assignment': mesh.edges_assignment,
      'edges_foldAngle': [round(a, 4) for a in mesh.edges_fold_angle],
  }


def _normalize_paper_rgb(
    color_top: Sequence[int] | None,
) -> tuple[float, float, float]:
  """Normalizes an optional RGB color into a legible lit paper tint."""
  if not color_top or len(color_top) != 3:
    return _DEFAULT_PAPER_RGB
  # Clamp extremes so crease lines and Lambertian facet shading stay clear.
  return (
      max(0.24, min(0.92, float(color_top[0]) / 255.0)),
      max(0.24, min(0.92, float(color_top[1]) / 255.0)),
      max(0.24, min(0.92, float(color_top[2]) / 255.0)),
  )


def draw_folded_mesh_on_ax(
    ax: axes.Axes,
    mesh: FoldedMesh3D,
    title: str,
    *,
    yaw: float = -0.62,
    pitch: float = 0.38,
    roll: float = 0.0,
    color_top: Sequence[int] | None = None,
) -> None:
  """Draws a Lambertian-shaded 3D folded origami mesh view onto `ax`."""
  ax.set_facecolor('#f8fafc')
  ax.set_aspect('equal', adjustable='box')
  ax.set_title(title, fontsize=11, fontweight='bold')
  ax.set_xticks([])
  ax.set_yticks([])
  for spine in ax.spines.values():
    spine.set_edgecolor('#cbd5e1')

  base_rgb = _normalize_paper_rgb(color_top)
  cos_y, sin_y = math.cos(yaw), math.sin(yaw)
  cos_p, sin_p = math.cos(pitch), math.sin(pitch)
  cos_r, sin_r = math.cos(roll), math.sin(roll)

  rotated_pts: list[tuple[float, float, float]] = []
  for px, py, pz in mesh.vertices_3d:
    x1 = px * cos_y + pz * sin_y
    z1 = -px * sin_y + pz * cos_y
    y2 = py * cos_p - z1 * sin_p
    z2 = py * sin_p + z1 * cos_p
    x3 = x1 * cos_r - y2 * sin_r
    y3 = x1 * sin_r + y2 * cos_r
    rotated_pts.append((x3, y3, z2))

  min_x = min(p[0] for p in rotated_pts)
  max_x = max(p[0] for p in rotated_pts)
  min_y = min(p[1] for p in rotated_pts)
  max_y = max(p[1] for p in rotated_pts)
  span_x = max(max_x - min_x, 0.05)
  span_y = max(max_y - min_y, 0.05)
  span = max(span_x, span_y)

  # Subtle ground shadow beneath the model.
  shadow = patches.Ellipse(
      ((min_x + max_x) * 0.5, min_y - span * 0.045),
      width=span_x * 0.85,
      height=span * 0.055,
      facecolor='#0f172a',
      edgecolor='none',
      alpha=0.12,
      zorder=0,
  )
  ax.add_patch(shadow)

  light_1 = (0.42, 0.62, 0.66)
  light_2 = (-0.52, -0.25, 0.81)
  face_items: list[
      tuple[
          float,
          float,
          float,
          list[tuple[float, float]],
          tuple[float, float, float],
          list[tuple[tuple[float, float], tuple[float, float]]],
      ]
  ] = []

  for face in mesh.faces:
    if len(face) < 3:
      continue
    p0, p1, p2 = (
        rotated_pts[face[0]],
        rotated_pts[face[1]],
        rotated_pts[face[2]],
    )
    ux, uy, uz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    vx, vy, vz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx
    norm_len = math.sqrt(nx * nx + ny * ny + nz * nz)
    if norm_len > 1e-9:
      nx, ny, nz = nx / norm_len, ny / norm_len, nz / norm_len
    else:
      nx, ny, nz = 0.0, 0.0, 1.0

    if nz < 0:
      nx, ny, nz = -nx, -ny, -nz
    dot_1 = max(0.0, nx * light_1[0] + ny * light_1[1] + nz * light_1[2])
    dot_2 = max(0.0, nx * light_2[0] + ny * light_2[1] + nz * light_2[2])
    shade = 0.56 + 0.35 * dot_1 + 0.14 * dot_2
    face_rgb = (
        min(1.0, base_rgb[0] * shade),
        min(1.0, base_rgb[1] * shade),
        min(1.0, base_rgb[2] * shade),
    )

    poly_2d = [(rotated_pts[v][0], rotated_pts[v][1]) for v in face]
    area_2d = 0.0
    face_len = len(poly_2d)
    for i in range(face_len):
      xa, ya = poly_2d[i]
      xb, yb = poly_2d[(i + 1) % face_len]
      area_2d += xa * yb - xb * ya
    area_2d = abs(area_2d) * 0.5

    z_avg = sum(rotated_pts[v][2] for v in face) / face_len
    z_bucket = round(z_avg / 0.002) * 0.002

    crease_segs: list[tuple[tuple[float, float], tuple[float, float]]] = []
    for i in range(face_len):
      u_idx, v_idx = face[i], face[(i + 1) % face_len]
      key = (min(u_idx, v_idx), max(u_idx, v_idx))
      ang = mesh.edge_key_angle.get(key, 0.0)
      if abs(ang) > 1.0 or key not in mesh.edge_key_angle:
        crease_segs.append((poly_2d[i], poly_2d[(i + 1) % face_len]))

    face_items.append((
        z_bucket,
        area_2d,
        z_avg,
        poly_2d,
        face_rgb,
        crease_segs,
    ))

  face_items.sort(key=lambda item: (item[0], item[1], item[2]))

  polys: list[list[tuple[float, float]]] = []
  face_colors: list[tuple[float, float, float]] = []
  edge_colors: list[tuple[float, float, float]] = []
  crease_lines: list[tuple[tuple[float, float], tuple[float, float]]] = []
  crease_line_colors: list[tuple[float, float, float, float]] = []

  for _, _, _, poly_2d, rgb, crease_segs in face_items:
    polys.append(poly_2d)
    face_colors.append(rgb)
    edge_colors.append((rgb[0] * 0.86, rgb[1] * 0.85, rgb[2] * 0.84))
    dark_rgba = (rgb[0] * 0.56, rgb[1] * 0.54, rgb[2] * 0.52, 0.88)
    for seg in crease_segs:
      crease_lines.append(seg)
      crease_line_colors.append(dark_rgba)

  poly_collection = mpl_collections.PolyCollection(
      polys,
      facecolors=face_colors,
      edgecolors=edge_colors,
      linewidths=0.45,
      zorder=2,
  )
  ax.add_collection(poly_collection)

  if crease_lines:
    line_collection = mpl_collections.LineCollection(
        crease_lines,
        colors=crease_line_colors,
        linewidths=0.75,
        capstyle='round',
        joinstyle='round',
        zorder=3,
    )
    ax.add_collection(line_collection)

  mid_x = (min_x + max_x) * 0.5
  mid_y = (min_y + max_y) * 0.5 - span * 0.02
  half = span * 0.58
  ax.set_xlim(mid_x - half, mid_x + half)
  ax.set_ylim(mid_y - half, mid_y + half)


def render_shaped_3d_turnaround_png(
    out_path: str | pathlib.Path,
    *,
    name: str,
    mesh: FoldedMesh3D,
    color_top: Sequence[int] | None = None,
    dpi: int = 180,
) -> pathlib.Path:
  """Renders a 4-angle shaded 3D turnaround PNG (`Iso`, `Side`, `Front`, `Top`)."""
  target_path = pathlib.Path(out_path)
  target_path.parent.mkdir(parents=True, exist_ok=True)
  fig, axs = plt.subplots(1, 4, figsize=(20, 5.2))
  fig.suptitle(
      f'3D Shaped Origami Turnaround: {name} '
      f'({len(mesh.faces)} facets, {len(mesh.edges)} edges)',
      fontsize=13,
      fontweight='bold',
      y=1.02,
  )
  for ax, (view_title, yaw, pitch, roll) in zip(
      axs, _TURNAROUND_VIEWS, strict=True
  ):
    draw_folded_mesh_on_ax(
        ax,
        mesh,
        view_title,
        yaw=yaw,
        pitch=pitch,
        roll=roll,
        color_top=color_top,
    )
  fig.tight_layout()
  fig.savefig(target_path, dpi=dpi, bbox_inches='tight')
  plt.close(fig)
  return target_path


def save_3d_turnaround(
    target: FoldedMesh3D | MeshTarget,
    out_path: str | pathlib.Path,
    *,
    name: str | None = None,
    packed: bus.PackedCreasePattern | None = None,
    color_top: Sequence[int] | None = None,
    dpi: int = 180,
) -> FoldedMesh3D:
  """Folds `target` (if needed) and saves a 4-angle shaded 3D turnaround PNG."""
  resolved_packed = packed
  if isinstance(target, FoldedMesh3D):
    mesh = target
  else:
    _, resolved_packed = _unwrap_mesh_target(target, packed)
    mesh = build_folded_mesh_3d(target, packed=resolved_packed)

  source_tree = None
  if resolved_packed is not None:
    if resolved_packed.design is not None:
      source_tree = resolved_packed.design.source
    else:
      source_tree = resolved_packed.packed_tree

  resolved_name = name or (
      source_tree.name if source_tree is not None and source_tree.name else None
  ) or 'model'
  resolved_color = color_top
  if resolved_color is None and source_tree is not None:
    resolved_color = getattr(source_tree, 'color_top', None)

  render_shaped_3d_turnaround_png(
      out_path,
      name=resolved_name,
      mesh=mesh,
      color_top=resolved_color,
      dpi=dpi,
  )
  return mesh
