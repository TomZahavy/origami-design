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
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import crease_pattern
from bp_pipeline.crease_pattern import point
from bp_pipeline.crease_pattern import symmetry

# An asymmetric pattern in the shape of an L.
ASYMMETRIC_CP = crease_pattern.CreasePattern(
    creases=[
        crease.Crease(
            point.Point(x=0.5, y=0.0),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0.0, y=1.0),
            fold=crease.Fold.MOUNTAIN,
        ),
    ]
)

# A symmetric pattern in the shape of a diamond.
SYMMETRIC_CP = crease_pattern.CreasePattern(
    creases=[
        crease.Crease(
            point.Point(x=0.5, y=0),
            point.Point(x=0, y=0.5),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0, y=0.5),
            point.Point(x=0.5, y=1.0),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=1.0),
            point.Point(x=1.0, y=0.5),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=1.0, y=0.5),
            point.Point(x=0.5, y=0),
            fold=crease.Fold.MOUNTAIN,
        ),
    ]
)


class SymmetryTest(parameterized.TestCase):

  def assertCreasesEqual(self, expected_creases, actual_creases):
    self.assertEqual(len(expected_creases), len(actual_creases))
    for expected in expected_creases:
      self.assertTrue(any(expected == actual for actual in actual_creases))

  def test_identity_transform(self):
    cp = symmetry.Transform.IDENTITY(ASYMMETRIC_CP)
    self.assertEqual(ASYMMETRIC_CP, cp)

  @parameterized.parameters(symmetry.FLIPS)
  def test_flip_cycle_test(self, flip: symmetry.Transform):
    cp = flip(flip(ASYMMETRIC_CP))
    self.assertCreasesEqual(ASYMMETRIC_CP.creases, cp.creases)

  def test_rotation_cycle_test(self):
    """Tests that four 90 degree rotations return the original CP."""
    r90 = symmetry.Transform.ROTATE_90
    cp_r90 = r90(ASYMMETRIC_CP)
    cp_r180 = r90(cp_r90)
    cp_r270 = r90(cp_r180)
    cp_final = r90(cp_r270)
    self.assertCreasesEqual(ASYMMETRIC_CP.creases, cp_final.creases)

  @parameterized.parameters(symmetry.Transform)
  def test_transform_cycle_test_symmetric(self, transform: symmetry.Transform):
    cp = transform(SYMMETRIC_CP)
    self.assertCreasesEqual(SYMMETRIC_CP.creases, cp.creases)
    self.assertEqual(symmetry.transform_symmetry(SYMMETRIC_CP, transform), 1.0)

  def test_symmetry_score_symmetric(self):
    self.assertEqual(symmetry.symmetry_score(SYMMETRIC_CP), 1.0)

  def test_symmetry_score_asymmetric(self):
    """Only 1 of 2 of the creases is symmetric."""
    self.assertEqual(symmetry.symmetry_score(ASYMMETRIC_CP), 0.5)

  def test_horizontal_flip(self):
    """Expected: (x, y) -> (x, 1-y)."""
    expected_creases = [
        crease.Crease(
            point.Point(x=0.5, y=1.0),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0.0, y=0.0),
            fold=crease.Fold.MOUNTAIN,
        ),
    ]
    transformed_cp = symmetry.Transform.HORIZONTAL_FLIP(ASYMMETRIC_CP)
    self.assertCreasesEqual(expected_creases, transformed_cp.creases)

  def test_vertical_flip(self):
    """Expected: (x, y) -> (1-x, y)."""
    expected_creases = [
        crease.Crease(
            point.Point(x=0.5, y=0.0),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1.0, y=1.0),
            fold=crease.Fold.MOUNTAIN,
        ),
    ]
    transformed_cp = symmetry.Transform.VERTICAL_FLIP(ASYMMETRIC_CP)
    self.assertCreasesEqual(expected_creases, transformed_cp.creases)

  def test_diagonal_flip(self):
    """Expected: (x, y) -> (y, x)."""
    expected_creases = [
        crease.Crease(
            point.Point(x=0.0, y=0.5),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1.0, y=0.0),
            fold=crease.Fold.MOUNTAIN,
        ),
    ]
    transformed_cp = symmetry.Transform.DIAGONAL_FLIP(ASYMMETRIC_CP)
    self.assertCreasesEqual(expected_creases, transformed_cp.creases)

  def test_anti_diagonal_flip(self):
    """Expected: (x, y) -> (1-y, 1-x)."""
    expected_creases = [
        crease.Crease(
            point.Point(x=1.0, y=0.5),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0.0, y=1.0),
            fold=crease.Fold.MOUNTAIN,
        ),
    ]
    transformed_cp = symmetry.Transform.ANTIDIAGONAL_FLIP(ASYMMETRIC_CP)
    self.assertCreasesEqual(expected_creases, transformed_cp.creases)

  def test_rotate_90(self):
    """Expected: (x, y) -> (1-y, x)."""
    expected_creases = [
        crease.Crease(
            point.Point(x=1.0, y=0.5),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0.0, y=0.0),
            fold=crease.Fold.MOUNTAIN,
        ),
    ]
    transformed_cp = symmetry.Transform.ROTATE_90(ASYMMETRIC_CP)
    self.assertCreasesEqual(expected_creases, transformed_cp.creases)

  def test_rotate_180(self):
    """Expected: (x, y) -> (1-x, 1-y)."""
    expected_creases = [
        crease.Crease(
            point.Point(x=0.5, y=1.0),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1.0, y=0.0),
            fold=crease.Fold.MOUNTAIN,
        ),
    ]
    transformed_cp = symmetry.Transform.ROTATE_180(ASYMMETRIC_CP)
    self.assertCreasesEqual(expected_creases, transformed_cp.creases)

  def test_rotate_270(self):
    """Expected: (x, y) -> (y, 1-x)."""
    expected_creases = [
        crease.Crease(
            point.Point(x=0.0, y=0.5),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1.0, y=1.0),
            fold=crease.Fold.MOUNTAIN,
        ),
    ]
    transformed_cp = symmetry.Transform.ROTATE_270(ASYMMETRIC_CP)
    self.assertCreasesEqual(expected_creases, transformed_cp.creases)

  def test_invert_folds_all_types(self):
    input_cp = crease_pattern.CreasePattern(
        creases=[
            crease.Crease(
                point.Point(x=0.0, y=0.1),
                point.Point(x=1.0, y=0.1),
                fold=crease.Fold.MOUNTAIN,
            ),
            crease.Crease(
                point.Point(x=0.0, y=0.3),
                point.Point(x=1.0, y=0.3),
                fold=crease.Fold.VALLEY,
            ),
            crease.Crease(
                point.Point(x=0.0, y=0.9),
                point.Point(x=1.0, y=0.9),
                fold=crease.Fold.BORDER,
            ),
        ]
    )

    expected_creases = [
        crease.Crease(
            point.Point(x=0.0, y=0.1),
            point.Point(x=1.0, y=0.1),
            fold=crease.Fold.VALLEY,
        ),
        crease.Crease(
            point.Point(x=0.0, y=0.3),
            point.Point(x=1.0, y=0.3),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.0, y=0.9),
            point.Point(x=1.0, y=0.9),
            fold=crease.Fold.BORDER,
        ),
    ]

    inverted_cp = symmetry.invert_crease_folds(input_cp)
    self.assertCreasesEqual(expected_creases, inverted_cp.creases)

  def test_invert_folds_zebra_fold(self):
    input_cp = crease_pattern.CreasePattern(
        creases=[
            crease.Crease(
                point.Point(x=0.0, y=0.5),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=1.0, y=0.5),
                fold=crease.Fold.VALLEY,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0),
                point.Point(x=0.5, y=1),
                fold=crease.Fold.MOUNTAIN,
            ),
        ]
    )

    expected_creases = [
        crease.Crease(
            point.Point(x=0.0, y=0.5),
            point.Point(x=1.0, y=0.5),
            fold=crease.Fold.VALLEY_ZEBRA,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0),
            point.Point(x=0.5, y=1),
            fold=crease.Fold.VALLEY,
        ),
    ]

    with self.subTest("invert then merge zebra"):
      inverted_cp = symmetry.invert_crease_folds(input_cp)
      inverted_cp.merge_creases(merge_zebra=True)
      self.assertCreasesEqual(expected_creases, inverted_cp.creases)

    with self.subTest("merge then invert"):
      input_cp.merge_creases(merge_zebra=True)
      inverted_cp = symmetry.invert_crease_folds(input_cp)
      inverted_cp.merge_creases(merge_zebra=True)
      self.assertCreasesEqual(expected_creases, inverted_cp.creases)

    with self.subTest("reconstruct original"):
      reconstructed_cp = symmetry.invert_crease_folds(inverted_cp)
      reconstructed_cp.merge_creases(merge_zebra=True)
      self.assertCreasesEqual(input_cp.creases, reconstructed_cp.creases)

  @parameterized.parameters(ASYMMETRIC_CP, SYMMETRIC_CP)
  def test_invert_folds_twice_is_identity(
      self, pattern: crease_pattern.CreasePattern
  ):
    reconstructed = symmetry.invert_crease_folds(
        symmetry.invert_crease_folds(pattern)
    )
    self.assertCreasesEqual(pattern.creases, reconstructed.creases)


if __name__ == "__main__":
  absltest.main()
