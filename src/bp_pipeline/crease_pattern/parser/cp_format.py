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

"""Parser for .cp origami files.

Each line in a .cp file is a single crease and its fold type separated by
spaces:

```
(linetype: 1: Contour, 2: Mountain, 3: Valley) (start x) (start y) (end x) (end
y)
```

Read more: https://mitani.cs.tsukuba.ac.jp/oripa/

Since .cp files don't specify a viewbox, including a complete border around
creases is recommended to avoid unexpected crease resizing.
"""

from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import crease_pattern
from bp_pipeline.crease_pattern import point
from bp_pipeline.crease_pattern.parser import parser_utils


def get_fold(linetype: str) -> crease.Fold:
  match linetype.strip():
    case '1':
      return crease.Fold.BORDER
    case '2':
      return crease.Fold.MOUNTAIN
    case '3':
      return crease.Fold.VALLEY
    case '4':
      return crease.Fold.TRIANGLE
    case '5':
      return crease.Fold.MOUNTAIN_ZEBRA
    case '6':
      return crease.Fold.VALLEY_ZEBRA
    case _:
      raise ValueError(f'Linetype {linetype} is not in the allowed list.')


def parse_cp(cp_file: str) -> crease_pattern.CreasePattern:
  """Parses a .cp file into a CreasePattern object."""
  raw_creases = []
  min_x = min_y = float('inf')
  max_x = max_y = float('-inf')
  for i, line in enumerate(cp_file.split('\n')):
    if not line.strip():
      continue

    values = line.split()
    if len(values) != 5:
      raise ValueError(f'Invalid line {i}: {line}')

    linetype, x1_s, y1_s, x2_s, y2_s = values
    fold = get_fold(linetype)
    x1, y1, x2, y2 = map(float, (x1_s, y1_s, x2_s, y2_s))
    raw_creases.append((fold, x1, y1, x2, y2))

    min_x = min(min_x, x1, x2)
    max_x = max(max_x, x1, x2)

    min_y = min(min_y, y1, y2)
    max_y = max(max_y, y1, y2)

  viewbox = (min_x, min_y, max_x - min_x, max_y - min_y)
  creases = [
      crease.Crease(
          point.Point.from_viewbox(x=x1, y=y1, viewbox=viewbox),
          point.Point.from_viewbox(x=x2, y=y2, viewbox=viewbox),
          fold=fold,
      )
      for fold, x1, y1, x2, y2 in raw_creases
  ]

  return crease_pattern.CreasePattern(creases)


def to_cp(
    pattern: crease_pattern.CreasePattern,
    scale: float = 1000,
    ndigits: int = 3,
    grid: int = -1,
) -> str:
  """Parses a CreasePattern object into a .cp file string."""
  lines = []
  for line in pattern.creases:
    if line.fold in (
        crease.Fold.MOUNTAIN,
        crease.Fold.VALLEY,
        crease.Fold.BORDER,
        crease.Fold.TRIANGLE,
        crease.Fold.VALLEY_ZEBRA,
        crease.Fold.MOUNTAIN_ZEBRA,
    ):
      linetype = line.fold.linetype()
      x1 = parser_utils.point_format(
          line.p1.x, scale=scale, ndigits=ndigits, grid=grid
      )
      y1 = parser_utils.point_format(
          line.p1.y, scale=scale, ndigits=ndigits, grid=grid
      )
      x2 = parser_utils.point_format(
          line.p2.x, scale=scale, ndigits=ndigits, grid=grid
      )
      y2 = parser_utils.point_format(
          line.p2.y, scale=scale, ndigits=ndigits, grid=grid
      )
      lines.append(f'{linetype} {x1} {y1} {x2} {y2}')

  return '\n'.join(lines)
