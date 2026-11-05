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

"""SVG rendering utilities."""

from collections.abc import Sequence
from typing import Callable

from . import math_utils

Point = math_utils.Point
SCALE = 1000
NAMESPACE = "http://www.w3.org/2000/svg"


def header(view_box: str) -> str:
  """Creates an SVG header.

  Args:
    view_box: The view box string (e.g., "0 0 1000 1000").

  Returns:
    The SVG header string.
  """
  return (
      f'<svg xmlns="{NAMESPACE}" viewBox="{view_box}"'
      ' style="background:lightgray">'
  )


def _append(tag: str, attributes: dict[str, str], content: str = "") -> str:
  """Creates an SVG element string.

  Args:
    tag: The SVG tag name (e.g., "polygon", "line").
    attributes: A dictionary of element attributes.
    content: Optional content for the element.

  Returns:
    The SVG element string.
  """
  attributes_string = " ".join([f'{k}="{v}"' for k, v in attributes.items()])
  return f"<{tag} {attributes_string}>{content}</{tag}>"


def draw_polygons(
    polygons: list[list[Point]], options: dict[str, object]
) -> str:
  """Draws a list of polygons as SVG polygon elements.

  Args:
    polygons: A list of polygons, where each polygon is a list of points.
    options: A dictionary of drawing options, including "fill", "stroke", and
      "stroke-width".

  Returns:
    An SVG string containing polygon elements.
  """
  output_parts = []
  fill_colors_val = options.get("fill", [])
  fill_colors: list[str | None]
  if isinstance(fill_colors_val, list):
    fill_colors = fill_colors_val
  else:
    fill_colors = []
  stroke_val = options.get("stroke")
  stroke: str | None
  if isinstance(stroke_val, str) or stroke_val is None:
    stroke = stroke_val
  else:
    stroke = None
  stroke_width_val = options.get("stroke-width", 1)
  stroke_width: int | float
  if isinstance(stroke_width_val, (int, float)):
    stroke_width = stroke_width_val
  else:
    stroke_width = 1

  for i, polygon in enumerate(polygons):
    color = fill_colors[i] if i < len(fill_colors) else "black"
    if color is None:
      continue

    scaled_polygon = [math_utils.multiply(p, SCALE) for p in polygon]
    points_string = " ".join([f"{p[0]},{p[1]}" for p in scaled_polygon])

    attributes = {"points": points_string, "fill": color}

    if stroke:
      attributes["stroke"] = stroke
      attributes["stroke-width"] = str(stroke_width)
      attributes["stroke-linejoin"] = "round"

    output_parts.append(_append("polygon", attributes))
  return "".join(output_parts)


def draw_segments(
    segments: list[Sequence[Point]],
    options: dict[str, object],
) -> str:
  """Draws a list of segments as SVG line elements.

  Args:
    segments: A list of segments, where each segment is a tuple of two points.
    options: A dictionary of drawing options, including "stroke",
      "stroke-width", and "filter".

  Returns:
    An SVG string containing line elements.
  """
  output_parts = []
  stroke_val = options.get("stroke", "black")
  stroke: str
  if isinstance(stroke_val, str):
    stroke = stroke_val
  else:
    stroke = "black"
  stroke_width_val = options.get("stroke-width", 1)
  stroke_width: int | float
  if isinstance(stroke_width_val, (int, float)):
    stroke_width = stroke_width_val
  else:
    stroke_width = 1
  filter_func_val = options.get("filter")
  filter_func: Callable[[int], bool] | None
  if callable(filter_func_val):
    filter_func = filter_func_val  # pyrefly: ignore[bad-assignment]
  else:
    filter_func = None

  for i, segment in enumerate(segments):
    if filter_func and not filter_func(i):
      continue

    p1 = math_utils.multiply(segment[0], SCALE)
    p2 = math_utils.multiply(segment[1], SCALE)

    attributes = {
        "x1": str(p1[0]),
        "y1": str(p1[1]),
        "x2": str(p2[0]),
        "y2": str(p2[1]),
        "stroke": stroke,
        "stroke-width": str(stroke_width),
        "stroke-linecap": "round",
    }
    output_parts.append(_append("line", attributes))
  return "".join(output_parts)
