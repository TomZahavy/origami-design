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

"""Self-contained HTML/SVG contact-sheet visualization for packed crease patterns."""

from collections.abc import Iterable, Mapping
import html
import math
from typing import Any

from bp_pipeline import bus
from bp_pipeline import codec
from bp_pipeline.stick_figures import stick_figure as stick_figure_lib
from bp_pipeline.stick_figures import traversal as tr

_FLAP_PALETTE = (
    ('#3b82f6', 'rgba(59, 130, 246, 0.20)'),
    ('#10b981', 'rgba(16, 185, 129, 0.20)'),
    ('#8b5cf6', 'rgba(139, 92, 246, 0.20)'),
    ('#ec4899', 'rgba(236, 72, 153, 0.20)'),
    ('#06b6d4', 'rgba(6, 182, 212, 0.20)'),
    ('#eab308', 'rgba(234, 179, 8, 0.20)'),
    ('#f97316', 'rgba(249, 115, 22, 0.20)'),
    ('#14b8a6', 'rgba(20, 184, 166, 0.20)'),
)


def stage_display_name(stage: bus.SolveStage | int | str) -> str:
  """Returns a human-readable display label for a SolveStage or stage index."""
  if isinstance(stage, bus.SolveStage):
    return stage.numbered_name
  if isinstance(stage, int):
    for s in bus.SolveStage:
      if s.stage_index == stage:
        return s.numbered_name
    return f'Stage {stage}'
  return str(stage)


def render_stick_figure_svg(tree: stick_figure_lib.StickFigure | None) -> str:
  """Renders a lightweight 2D isometric stick-figure projection as inline SVG."""
  if tree is None or not tree.children:
    return (
        '<div class="bp-empty-stage">No stick figure metadata available</div>'
    )

  root_stick = tree[tree.root]
  joint_locations: dict[str, tuple[float, float]] = {
      root_stick.start: (0.0, 0.0)
  }
  segments: list[tuple[float, float, float, float, str, int, bool, bool]] = []

  for stick in tr.breadth_first_traversal(tree):
    start_joint, end_joint = (
        (stick.start, stick.end)
        if stick.start in joint_locations
        else (stick.end, stick.start)
    )
    x0, y0 = joint_locations[start_joint]
    dx, dy, dz = stick.get_coords(start_joint)
    proj_x = (dx - dy) * math.sqrt(3.0) / 2.0
    proj_y = -(dz - (dx + dy) / 2.0)
    proj_len = math.hypot(proj_x, proj_y)
    if proj_len < 0.35:
      angle_rad = math.radians(stick.azimuth_angle)
      proj_x = 0.5 * math.cos(angle_rad)
      proj_y = -0.5 * math.sin(angle_rad)
    if end_joint not in joint_locations:
      joint_locations[end_joint] = (x0 + proj_x, y0 + proj_y)
    x1, y1 = joint_locations[end_joint]
    segments.append((
        x0,
        y0,
        x1,
        y1,
        stick.name,
        int(stick.length),
        bool(stick.is_river),
        bool(stick.is_on_symmetry_axis),
    ))

  xs = [pt[0] for pt in joint_locations.values()]
  ys = [pt[1] for pt in joint_locations.values()]
  min_x, max_x = min(xs, default=0.0), max(xs, default=1.0)
  min_y, max_y = min(ys, default=0.0), max(ys, default=1.0)
  span = max(max_x - min_x, max_y - min_y, 2.0)
  pad = span * 0.22
  vb_x = min_x - pad
  vb_y = min_y - pad
  vb_size = span + 2.0 * pad
  cx_shift = (vb_size - (max_x - min_x)) / 2.0 - pad
  cy_shift = (vb_size - (max_y - min_y)) / 2.0 - pad

  parts = [
      '<svg class="bp-stick-svg" xmlns="http://www.w3.org/2000/svg"'
      f' viewBox="{vb_x - cx_shift:.3f} {vb_y - cy_shift:.3f}'
      f' {vb_size:.3f} {vb_size:.3f}">'
  ]
  for x0, y0, x1, y1, name, length, is_river, on_axis in segments:
    stroke = '#d97706' if is_river else ('#2563eb' if on_axis else '#1e293b')
    dash = ' stroke-dasharray="4 2"' if is_river else ''
    parts.append(
        f'<line x1="{x0:.3f}" y1="{y0:.3f}" x2="{x1:.3f}" y2="{y1:.3f}"'
        f' stroke="{stroke}" stroke-width="2.2" stroke-linecap="round"{dash}'
        ' vector-effect="non-scaling-stroke"/>'
    )
    mx = (x0 + x1) / 2.0
    my = (y0 + y1) / 2.0
    esc_label = html.escape(f'{name}:{length}')
    parts.append(
        f'<text x="{mx:.3f}" y="{my:.3f}" class="bp-stick-label">'
        f'{esc_label}</text>'
    )
  for jx, jy in joint_locations.values():
    parts.append(
        f'<circle cx="{jx:.3f}" cy="{jy:.3f}" r="{vb_size * 0.014:.3f}"'
        ' fill="#0f172a"/>'
    )
  parts.append('</svg>')
  return ''.join(parts)


def render_packed_overlay_svg(packed: bus.PackedCreasePattern) -> str:
  """Builds an SVG overlay in grid coordinates from packed.flaps/rivers/hinges."""
  g = packed.grid_size
  parts = [
      '<svg class="bp-cp-overlay" xmlns="http://www.w3.org/2000/svg"'
      f' viewBox="0 0 {g} {g}">'
  ]

  parts.append('<g class="bp-layer-grid">')
  for i in range(1, g):
    parts.append(
        f'<line x1="{i}" y1="0" x2="{i}" y2="{g}" class="bp-grid-line"/>'
    )
    parts.append(
        f'<line x1="0" y1="{i}" x2="{g}" y2="{i}" class="bp-grid-line"/>'
    )
  if packed.design is not None and packed.design.is_symmetric:
    mid = g / 2.0
    parts.append(
        f'<line x1="{mid}" y1="0" x2="{mid}" y2="{g}" class="bp-sym-axis"/>'
    )
  parts.append('</g>')

  parts.append('<g class="bp-layer-rivers">')
  for river_id, river in packed.rivers.items():
    esc_river = html.escape(f'{river_id} (w={river.width})')
    for rect in river.rects:
      parts.append(
          f'<rect x="{rect.x}" y="{rect.y}" width="{rect.width}"'
          f' height="{rect.height}" class="bp-river-rect">'
          f'<title>River {esc_river}</title></rect>'
      )
  parts.append('</g>')

  parts.append('<g class="bp-layer-flaps">')
  for idx, (flap_id, flap) in enumerate(packed.flaps.items()):
    stroke_color, fill_color = _FLAP_PALETTE[idx % len(_FLAP_PALETTE)]
    r = flap.rect
    esc_id = html.escape(flap_id)
    parts.append(
        f'<rect x="{r.x}" y="{r.y}" width="{r.width}" height="{r.height}"'
        f' fill="{fill_color}" stroke="{stroke_color}" class="bp-flap-rect"'
        f' data-flap-id="{esc_id}">'
        f'<title>Flap {esc_id} ({r.width}x{r.height},'
        f' {flap.flap_type.value})</title></rect>'
    )
  parts.append('</g>')

  parts.append('<g class="bp-layer-centers">')
  for idx, flap in enumerate(packed.flaps.values()):
    stroke_color, _ = _FLAP_PALETTE[idx % len(_FLAP_PALETTE)]
    for center in flap.circle_centers:
      parts.append(
          f'<circle cx="{center.x}" cy="{center.y}"'
          f' r="{max(0.18, g * 0.012):.3f}" fill="{stroke_color}"'
          ' class="bp-center-dot"/>'
      )
  parts.append('</g>')

  parts.append('<g class="bp-layer-hinges">')
  for hinge in packed.hinges:
    seg = hinge.segment
    elems = html.escape(','.join(hinge.elements))
    parts.append(
        f'<line x1="{seg.p1.x}" y1="{seg.p1.y}" x2="{seg.p2.x}"'
        f' y2="{seg.p2.y}" class="bp-hinge-line"'
        f' data-hinge-id="{hinge.id}" data-elements="{elems}">'
        f'<title>Hinge #{hinge.id}: {elems}</title></line>'
    )
  parts.append('</g>')

  parts.append('<g class="bp-layer-labels">')
  base_font = max(0.42, min(1.15, g * 0.036))
  for idx, (flap_id, flap) in enumerate(packed.flaps.items()):
    stroke_color, _ = _FLAP_PALETTE[idx % len(_FLAP_PALETTE)]
    r = flap.rect
    cx = r.x + r.width / 2.0
    cy = r.y + r.height / 2.0
    label_text = f'{flap_id} ({r.width}\u00d7{r.height})'
    fit_w = r.width / max(len(label_text) * 0.56, 1.0)
    fit_h = r.height * 0.42
    flap_font = max(0.28, min(base_font, fit_w, fit_h))
    esc_label = html.escape(label_text)
    parts.append(
        f'<text x="{cx:.2f}" y="{cy:.2f}" font-size="{flap_font:.2f}"'
        f' fill="{stroke_color}" class="bp-flap-label">{esc_label}</text>'
    )
  parts.append('</g>')

  parts.append('</svg>')
  return ''.join(parts)


def _render_bus_card(
    idx: int,
    packed: bus.PackedCreasePattern,
    solved: bus.SolvedCreasePattern | None,
) -> str:
  """Renders a single card for a PackedCreasePattern / SolvedCreasePattern."""
  tree = (
      packed.design.source if packed.design is not None else packed.packed_tree
  )
  name = (
      tree.name
      if tree is not None and tree.name
      else f'crease_pattern_{idx + 1}'
  )
  stick_count = len(tree.children) if tree is not None else 0
  flap_count = len(packed.flaps)
  river_count = len(packed.rivers)
  hinge_count = len(packed.hinges)
  is_sym = (
      packed.design is not None and packed.design.is_symmetric
  ) or packed.diagnostics.is_symmetric
  sym_badge = 'Symmetric' if is_sym else 'Asymmetric'

  badges = [
      (
          '<span class="bp-badge bp-badge-grid">Grid'
          f' {packed.grid_size}&times;{packed.grid_size}</span>'
      ),
      f'<span class="bp-badge">{sym_badge}</span>',
      f'<span class="bp-badge">{flap_count} flaps</span>',
      f'<span class="bp-badge">{river_count} rivers</span>',
      f'<span class="bp-badge">{hinge_count} hinges</span>',
  ]
  if stick_count:
    badges.append(f'<span class="bp-badge">{stick_count} sticks</span>')
  if solved is not None:
    ff_class = (
        'bp-badge-ok' if solved.is_globally_flat_foldable else 'bp-badge-warn'
    )
    ff_text = (
        'Flat-Foldable' if solved.is_globally_flat_foldable else 'Local-Only'
    )
    badges.append(f'<span class="bp-badge {ff_class}">{ff_text}</span>')
    if solved.stats.time_taken > 0:
      badges.append(
          f'<span class="bp-badge">Solve {solved.stats.time_taken:.2f}s</span>'
      )

  stick_svg = render_stick_figure_svg(tree)
  packed_base_svg = packed.to_svg(pretty=False)
  packed_overlay_svg = render_packed_overlay_svg(packed)
  status = 'ok' if solved is not None else 'packed'
  if solved is not None:
    solved_panel = (
        f'<div class="bp-stage-box">{solved.to_svg(pretty=False)}</div>'
    )
  else:
    solved_panel = (
        '<div class="bp-empty-stage">Not solved (PackedCreasePattern'
        ' only)</div>'
    )

  return (
      f'<article class="bp-card" data-name="{html.escape(name.lower())}"'
      f' data-status="{status}">'
      '<header class="bp-card-header">'
      f'<h3 class="bp-card-title">#{idx + 1} &middot; {html.escape(name)}</h3>'
      f'<div class="bp-badges">{"".join(badges)}</div>'
      '</header>'
      '<div class="bp-panels">'
      '<div class="bp-panel">'
      '<div class="bp-panel-label">1. Stick Figure (2D Isometric)</div>'
      f'<div class="bp-stage-box">{stick_svg}</div>'
      '</div>'
      '<div class="bp-panel">'
      '<div class="bp-panel-label">2. Packed Crease Pattern + Overlay</div>'
      '<div class="bp-stage-box bp-packed-stack">'
      f'<div class="bp-cp-base">{packed_base_svg}</div>'
      f'{packed_overlay_svg}'
      '</div>'
      '</div>'
      '<div class="bp-panel">'
      '<div class="bp-panel-label">3. Solved Flat-Foldable CP</div>'
      f'{solved_panel}'
      '</div>'
      '</div>'
      '</article>'
  )


def _coerce_item(
    item: bus.PackedCreasePattern | bus.SolvedCreasePattern | Mapping[str, Any],
) -> tuple[bus.PackedCreasePattern, bus.SolvedCreasePattern | None]:
  """Coerces a bus object or codec/eval dict into (PackedCreasePattern, SolvedCreasePattern | None)."""
  if isinstance(item, bus.SolvedCreasePattern):
    return item.packed, item
  if isinstance(item, bus.PackedCreasePattern):
    return item, None
  if isinstance(item, Mapping):
    if 'schema_version' in item and 'type' in item:
      decoded = codec.from_dict(item)
      if isinstance(
          decoded, (bus.PackedCreasePattern, bus.SolvedCreasePattern)
      ):
        return _coerce_item(decoded)
      raise ValueError(
          'Expected PackedCreasePattern or SolvedCreasePattern codec dict, got'
          f' {type(decoded)!r}'
      )
    if isinstance(item.get('solved'), Mapping):
      return _coerce_item(item['solved'])
    if isinstance(item.get('packed'), Mapping):
      return _coerce_item(item['packed'])
    raise ValueError(
        'Mapping passed to render_packing_grid must be a v1 codec dict or'
        ' contain "packed"/"solved" codec dicts.'
    )
  raise TypeError(
      'render_packing_grid expected PackedCreasePattern, SolvedCreasePattern,'
      f' or codec dict; got {type(item)!r}'
  )


def render_packing_grid(
    items: Iterable[
        bus.PackedCreasePattern | bus.SolvedCreasePattern | Mapping[str, Any]
    ],
    *,
    title: str = 'Box-Pleating Packing & Solving Contact Sheet',
) -> str:
  """Renders bus records or codec dicts into a self-contained HTML contact sheet."""
  cards: list[str] = []
  total_count = 0
  packed_count = 0
  solved_count = 0

  for idx, raw_item in enumerate(items):
    packed, solved = _coerce_item(raw_item)
    total_count += 1
    packed_count += 1
    if solved is not None:
      solved_count += 1
    cards.append(_render_bus_card(idx, packed, solved))

  esc_title = html.escape(title)
  cards_html = (
      '\n'.join(cards)
      if cards
      else '<div class="bp-empty-stage">No packing records to display.</div>'
  )

  return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{esc_title}</title>
<style>
  :root {{
    color-scheme: dark;
    --bg: #0b0f19;
    --card-bg: #111827;
    --panel-bg: #1f2937;
    --border: #374151;
    --text: #f3f4f6;
    --muted: #9ca3af;
    --accent: #3b82f6;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 20px 24px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
  }}
  .bp-topbar {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    margin-bottom: 20px;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--border);
  }}
  .bp-title-block h1 {{
    margin: 0;
    font-size: 20px;
    font-weight: 600;
  }}
  .bp-summary {{
    margin-top: 4px;
    font-size: 13px;
    color: var(--muted);
  }}
  .bp-controls {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
    font-size: 13px;
  }}
  .bp-controls label {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    cursor: pointer;
    user-select: none;
  }}
  .bp-search {{
    padding: 6px 10px;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: var(--card-bg);
    color: var(--text);
    font-size: 13px;
  }}
  .bp-grid {{
    display: flex;
    flex-direction: column;
    gap: 18px;
  }}
  .bp-card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
  }}
  .bp-card-header {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-bottom: 12px;
  }}
  .bp-card-title {{
    margin: 0;
    font-size: 15px;
    font-weight: 600;
  }}
  .bp-badges {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }}
  .bp-badge {{
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 12px;
    background: var(--panel-bg);
    border: 1px solid var(--border);
    color: var(--text);
  }}
  .bp-badge-grid {{
    background: rgba(59, 130, 246, 0.18);
    border-color: #3b82f6;
    color: #93c5fd;
    font-weight: 600;
  }}
  .bp-badge-ok {{
    background: rgba(16, 185, 129, 0.18);
    border-color: #10b981;
    color: #6ee7b7;
  }}
  .bp-badge-warn {{
    background: rgba(245, 158, 11, 0.18);
    border-color: #f59e0b;
    color: #fcd34d;
  }}
  .bp-badge-fail {{
    background: rgba(239, 68, 68, 0.18);
    border-color: #ef4444;
    color: #fca5a5;
  }}
  .bp-panels {{
    display: grid;
    grid-template-columns: repeat(3, minmax(220px, 1fr));
    gap: 14px;
  }}
  .bp-panels-two {{
    grid-template-columns: repeat(2, minmax(260px, 1fr));
  }}
  @media (max-width: 960px) {{
    .bp-panels, .bp-panels-two {{
      grid-template-columns: 1fr;
    }}
  }}
  .bp-panel {{
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}
  .bp-panel-label {{
    font-size: 12px;
    font-weight: 500;
    color: var(--muted);
  }}
  .bp-stage-box {{
    position: relative;
    width: 100%;
    aspect-ratio: 1 / 1;
    background: #ffffff;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--border);
  }}
  .bp-stage-box svg {{
    width: 100%;
    height: 100%;
    display: block;
  }}
  .bp-cp-base {{
    position: absolute;
    inset: 0;
  }}
  .bp-cp-base svg line,
  .bp-stage-box > svg line,
  .bp-cp-base svg rect,
  .bp-stage-box > svg rect {{
    vector-effect: non-scaling-stroke;
    stroke-width: 1.4px;
    fill: none;
  }}
  .bp-cp-overlay {{
    position: absolute;
    inset: 0;
    pointer-events: all;
  }}
  .bp-grid-line {{
    stroke: rgba(148, 163, 184, 0.28);
    stroke-width: 0.7px;
    vector-effect: non-scaling-stroke;
  }}
  .bp-sym-axis {{
    stroke: rgba(37, 99, 235, 0.55);
    stroke-width: 1.2px;
    stroke-dasharray: 4 3;
    vector-effect: non-scaling-stroke;
  }}
  .bp-river-rect {{
    fill: rgba(245, 158, 11, 0.22);
    stroke: #d97706;
    stroke-width: 1.4px;
    stroke-dasharray: 3 2;
    vector-effect: non-scaling-stroke;
  }}
  .bp-flap-rect {{
    stroke-width: 1.5px;
    vector-effect: non-scaling-stroke;
  }}
  .bp-hinge-line {{
    stroke: #059669;
    stroke-width: 2.6px;
    stroke-linecap: round;
    vector-effect: non-scaling-stroke;
  }}
  .bp-flap-label {{
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-weight: 700;
    text-anchor: middle;
    dominant-baseline: central;
    paint-order: stroke;
    stroke: rgba(255, 255, 255, 0.92);
    stroke-width: 0.22px;
    pointer-events: none;
  }}
  .bp-stick-label {{
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 0.55px;
    fill: #0f172a;
    text-anchor: middle;
    dominant-baseline: central;
    paint-order: stroke;
    stroke: rgba(255, 255, 255, 0.9);
    stroke-width: 0.14px;
  }}
  .bp-empty-stage {{
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 180px;
    padding: 16px;
    background: var(--panel-bg);
    border-radius: 8px;
    color: var(--muted);
    font-size: 12px;
    text-align: center;
    white-space: pre-wrap;
  }}
  body.hide-flaps .bp-layer-flaps {{ display: none; }}
  body.hide-rivers .bp-layer-rivers {{ display: none; }}
  body.hide-hinges .bp-layer-hinges {{ display: none; }}
  body.hide-labels .bp-layer-labels {{ display: none; }}
  body.hide-centers .bp-layer-centers {{ display: none; }}
  body.hide-grid .bp-layer-grid {{ display: none; }}
</style>
</head>
<body>
  <div class="bp-topbar">
    <div class="bp-title-block">
      <h1>{esc_title}</h1>
      <div class="bp-summary">
        Showing {total_count} items &middot; {packed_count} packed &middot; {solved_count} solved
      </div>
    </div>
    <div class="bp-controls">
      <input type="search" id="bp-filter" class="bp-search" placeholder="Filter by stick figure name..."/>
      <label><input type="checkbox" data-toggle="hide-flaps" checked/> Flaps</label>
      <label><input type="checkbox" data-toggle="hide-rivers" checked/> Rivers</label>
      <label><input type="checkbox" data-toggle="hide-hinges" checked/> Hinges</label>
      <label><input type="checkbox" data-toggle="hide-labels" checked/> Labels</label>
      <label><input type="checkbox" data-toggle="hide-centers" checked/> Centers</label>
      <label><input type="checkbox" data-toggle="hide-grid" checked/> Grid</label>
    </div>
  </div>
  <main class="bp-grid" id="bp-grid">
    {cards_html}
  </main>
  <script>
    document.querySelectorAll('[data-toggle]').forEach((cb) => {{
      cb.addEventListener('change', () => {{
        document.body.classList.toggle(cb.dataset.toggle, !cb.checked);
      }});
    }});
    const filterInput = document.getElementById('bp-filter');
    if (filterInput) {{
      filterInput.addEventListener('input', () => {{
        const q = filterInput.value.trim().toLowerCase();
        document.querySelectorAll('.bp-card').forEach((card) => {{
          const match = !q || (card.dataset.name || '').includes(q);
          card.style.display = match ? '' : 'none';
        }});
      }});
    }}
  </script>
</body>
</html>
"""
