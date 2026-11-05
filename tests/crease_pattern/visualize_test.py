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

"""Test crease pattern visualization."""

import io

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.crease_pattern import visualize
from bp_pipeline.crease_pattern.parser import svg
from matplotlib import axes
from matplotlib import pyplot as plt
from PIL import Image

SQUARE_BASE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1">
  <rect x='0' y='0' width='1' height='1' stroke='black' />
  <line stroke="#f00" x1="0.5" y1="1" x2="0.5" y2="0.5" />
  <line stroke="#f00" x1="0.5" y1="0.5" x2="0.5" y2="0" />
  <line stroke="#f00" x1="1" y1="0.5" x2="0.5" y2="0.5" />
  <line stroke="#00f" x1="0.5" y1="0.5" x2="0" y2="0.5" />
</svg>"""


class VisualizeTest(parameterized.TestCase):

  def test_visualize_cp(self):
    cp = svg.parse_svg(SQUARE_BASE_SVG)
    figure, axis = visualize.draw_cp(
        cp, show_vertices=True, show_only_not_flat_foldable_vertices=False
    )
    self.assertIsInstance(figure, plt.Figure)
    self.assertIsInstance(axis, axes.Axes)
    n_creases = len(cp.creases)
    n_vertices = len(cp.vertices)
    self.assertLen(axis.lines, n_creases + n_vertices)
    plt.close(figure)

  def test_visualize_cp_custom_lw_and_vertex_size(self):
    cp = svg.parse_svg(SQUARE_BASE_SVG)
    figure, axis = visualize.draw_cp(
        cp,
        show_vertices=True,
        show_only_not_flat_foldable_vertices=False,
        lw=0.65,
        vertex_size=5.0,
    )
    self.assertIsInstance(figure, plt.Figure)
    self.assertIsInstance(axis, axes.Axes)
    # Crease lines should have lw=0.65
    for line in axis.lines[: len(cp.creases)]:
      self.assertEqual(line.get_linewidth(), 0.65)
    plt.close(figure)

  def test_visualize_cp_only_internal(self):
    cp = svg.parse_svg(SQUARE_BASE_SVG)
    _, axis = visualize.draw_cp(
        cp,
        only_internal=True,
        show_vertices=True,
        show_only_not_flat_foldable_vertices=False,
    )
    n_creases = len(cp.creases)
    n_internal_vertices = sum(v.internal for v in cp.vertices)
    self.assertLen(axis.lines, n_creases + n_internal_vertices)

  @parameterized.parameters("JPEG", "PNG")
  def test_figure_to_bytes(self, file_format: str):
    cp = svg.parse_svg(SQUARE_BASE_SVG)
    figure, _ = visualize.draw_cp(cp)

    bytes_image = visualize.figure_to_image(figure, file_format)
    pil_img = Image.open(io.BytesIO(bytes_image))
    self.assertEqual(pil_img.format, file_format)

    figure_width, figure_height = figure.get_size_inches()
    pil_width, pil_height = pil_img.size
    self.assertAlmostEqual(pil_width / pil_height, figure_width / figure_height)

  def test_folding_grid(self):
    cp = svg.parse_svg(SQUARE_BASE_SVG)
    _, axs = visualize.folding_grid(cp, cols=1)
    self.assertEqual(axs.shape, (1, 1))

  def test_render_cps_to_png_bytes(self):
    cp = svg.parse_svg(SQUARE_BASE_SVG)
    png_bytes = visualize.render_cps_to_png_bytes([cp])
    self.assertNotEmpty(png_bytes)
    pil_img = Image.open(io.BytesIO(png_bytes))
    self.assertEqual(pil_img.format, "PNG")


if __name__ == "__main__":
  absltest.main()
