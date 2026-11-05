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

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline import bus
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import crease_pattern
from bp_pipeline.crease_pattern import point
from bp_pipeline.solving import solvability
import cp_test_fixtures as examples


class SolvabilityTest(parameterized.TestCase):

  def test_valid_examples_are_solvable(self):
    for example in (examples.HUMAN, examples.SCORPION):
      res = solvability.check_solvability(example.packing_cp)
      self.assertTrue(res.is_solvable, msg=f'{example.name}: {res.reason}')
      self.assertFalse(solvability.is_provably_unsolvable(example.packing_cp))

  def test_negative_or_zero_grid_size_unsolvable(self):
    cp = crease_pattern.CreasePattern([], grid_size=0, is_empty=True)
    res = solvability.check_solvability(cp)
    self.assertFalse(res.is_solvable)
    self.assertTrue(solvability.is_provably_unsolvable(cp))

  def test_fixed_interior_vertex_odd_degree_unsolvable(self):
    # Mountain crease ending at interior point (0.5, 0.5) with no other creases.
    # Degree is 1 (odd) and there are no candidate hinges.
    c = crease.Crease(
        point.Point(x=0.0, y=0.5),
        point.Point(x=0.5, y=0.5),
        fold=crease.Fold.MOUNTAIN,
    )
    cp = crease_pattern.CreasePattern([c], grid_size=16)
    # Using PackedCreasePattern bus record with empty hinges.
    packed_bus = bus.PackedCreasePattern(
        design=None,
        packed_tree=None,
        grid_size=16,
        creases=cp,
        flaps={},
        rivers={},
        hinges=(),
        config=None,  # pyrefly: ignore[bad-argument-type]
        diagnostics=bus.PackingDiagnostics(grid_size=16),
    )
    res = solvability.check_solvability(packed_bus)
    self.assertFalse(res.is_solvable)
    self.assertIn('Kawasaki parity violation', res.reason or '')
    self.assertTrue(solvability.is_provably_unsolvable(packed_bus))

  def test_fixed_interior_vertex_maekawa_violation_unsolvable(self):
    # 4 creases meeting at (0.5, 0.5): 4 Mountains and 0 Valleys.
    # |M - V| = 4 != 2, with 0 candidate hinges and 0 unassigned pleats.
    c1 = crease.Crease(
        point.Point(x=0.5, y=0.0),
        point.Point(x=0.5, y=0.5),
        fold=crease.Fold.MOUNTAIN,
    )
    c2 = crease.Crease(
        point.Point(x=0.5, y=1.0),
        point.Point(x=0.5, y=0.5),
        fold=crease.Fold.MOUNTAIN,
    )
    c3 = crease.Crease(
        point.Point(x=0.0, y=0.5),
        point.Point(x=0.5, y=0.5),
        fold=crease.Fold.MOUNTAIN,
    )
    c4 = crease.Crease(
        point.Point(x=1.0, y=0.5),
        point.Point(x=0.5, y=0.5),
        fold=crease.Fold.MOUNTAIN,
    )
    cp = crease_pattern.CreasePattern([c1, c2, c3, c4], grid_size=16)
    packed_bus = bus.PackedCreasePattern(
        design=None,
        packed_tree=None,
        grid_size=16,
        creases=cp,
        flaps={},
        rivers={},
        hinges=(),
        config=None,  # pyrefly: ignore[bad-argument-type]
        diagnostics=bus.PackingDiagnostics(grid_size=16),
    )
    res = solvability.check_solvability(packed_bus)
    self.assertFalse(res.is_solvable)
    self.assertIn('Maekawa violation', res.reason or '')
    self.assertTrue(solvability.is_provably_unsolvable(packed_bus))

  def test_flap_bounds_exceeded_unsolvable(self):
    cp = examples.HUMAN.packing_cp
    # Flap placed outside sheet bounds [0, 32].
    bad_rect = bus.GridRect(x=-2, y=5, width=12, height=10)
    bad_flap = bus.Flap(
        id='leg',
        stick='leg',
        rect=bad_rect,
        circle_centers=(bus.GridPoint(x=5, y=10),),
        flap_type=bus.FlapType.INTERNAL,
    )
    packed_bus = bus.PackedCreasePattern(
        design=None,
        packed_tree=None,
        grid_size=32,
        creases=cp,
        flaps={'leg': bad_flap},
        rivers={},
        hinges=(),
        config=None,  # pyrefly: ignore[bad-argument-type]
        diagnostics=bus.PackingDiagnostics(grid_size=32),
    )
    res = solvability.check_solvability(packed_bus)
    self.assertFalse(res.is_solvable)
    self.assertIn('exceeds sheet bounds', res.reason or '')
    self.assertTrue(solvability.is_provably_unsolvable(packed_bus))


if __name__ == '__main__':
  absltest.main()
