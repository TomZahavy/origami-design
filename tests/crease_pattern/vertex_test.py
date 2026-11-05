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

"""Tests for Vertex object."""

import dataclasses
import functools

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.crease_pattern import crease
from bp_pipeline.crease_pattern import point
from bp_pipeline.crease_pattern import vertex


@dataclasses.dataclass(frozen=True)
class VertexTestExample:
  """Contains a single variant of a problem."""

  creases: list[crease.Crease]


_VALID_VERTEX_EXAMPLES = [
    VertexTestExample(
        creases=[
            crease.Crease(
                point.Point(x=0, y=0),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=1, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
        ],
    ),
    VertexTestExample(
        creases=[
            crease.Crease(
                point.Point(x=0, y=0),
                point.Point(x=0.5, y=0),
                fold=crease.Fold.BORDER,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0),
                point.Point(x=1, y=0),
                fold=crease.Fold.BORDER,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
        ],
    ),
    VertexTestExample(  # colinear creases with different fold types
        creases=[
            crease.Crease(
                point.Point(x=0, y=0),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
            crease.Crease(
                point.Point(x=1, y=1),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.VALLEY,
            ),
        ],
    ),
    VertexTestExample(  # Modfied Tom's case to be flat foldable
        creases=[
            crease.Crease(
                point.Point(x=0, y=0),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.VALLEY,
            ),
            crease.Crease(
                point.Point(x=0, y=0.5),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.VALLEY,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.0),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=1.0, y=0.0),
                fold=crease.Fold.VALLEY,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=0.5, y=1.0),
                fold=crease.Fold.VALLEY,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=1.0, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
        ],
    ),
    VertexTestExample(
        creases=[
            crease.Crease(
                point.Point(x=0, y=0),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.VALLEY,
            ),
            crease.Crease(
                point.Point(x=0, y=1.0),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.VALLEY,
            ),
            crease.Crease(
                point.Point(x=1.0, y=1.0),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=1.0, y=0.0),
                fold=crease.Fold.VALLEY,
            ),
        ],
    ),
]

_INVALID_VERTEX_EXAMPLES = [
    VertexTestExample(  # 1 borders
        creases=[
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=0.5, y=0),
                fold=crease.Fold.BORDER,
            ),
            crease.Crease(
                point.Point(x=0, y=0),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
        ],
    ),
    VertexTestExample(  # colinear creases
        creases=[
            crease.Crease(
                point.Point(x=0, y=0),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
            crease.Crease(
                point.Point(x=1, y=1),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
        ],
    ),
]

_INVALID_VERTEX_ANGLES = [
    VertexTestExample(  # case Tom raised
        creases=[
            crease.Crease(
                point.Point(x=0, y=0),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.VALLEY,
            ),
            crease.Crease(
                point.Point(x=0, y=0.5),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.VALLEY,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.0),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=1.0, y=0.0),
                fold=crease.Fold.VALLEY,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=0.5, y=1.0),
                fold=crease.Fold.MOUNTAIN,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=1.0, y=0.5),
                fold=crease.Fold.VALLEY,
            ),
        ],
    ),
    VertexTestExample(
        creases=[
            crease.Crease(
                point.Point(x=0, y=0),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=1, y=0),
                fold=crease.Fold.VALLEY,
            ),
        ]
    ),
    VertexTestExample(
        creases=[
            crease.Crease(
                point.Point(x=0, y=0),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.MOUNTAIN,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=1, y=0),
                fold=crease.Fold.VALLEY,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=0.5, y=0),
                fold=crease.Fold.MOUNTAIN,
            ),
        ]
    ),
]

_ERROR_VERTEX_EXAMPLES = [
    VertexTestExample(  # Invalid vertex because the creases do not intersect.
        creases=[
            crease.Crease(
                point.Point(x=0, y=0),
                point.Point(x=0.2, y=0.2),
                fold=crease.Fold.BORDER,
                fold_percent=1.0,
            ),
            crease.Crease(
                point.Point(x=0.5, y=0.5),
                point.Point(x=1, y=1),
                fold=crease.Fold.BORDER,
                fold_percent=1.0,
            ),
        ],
    ),
    VertexTestExample(  # Invalid vertex because the creases overlap.
        creases=[
            crease.Crease(
                point.Point(x=0, y=0),
                point.Point(x=0.2, y=0.2),
                fold=crease.Fold.BORDER,
                fold_percent=1.0,
            ),
            crease.Crease(
                point.Point(x=0.1, y=0.1),
                point.Point(x=0.3, y=0.3),
                fold=crease.Fold.BORDER,
                fold_percent=1.0,
            ),
        ],
    ),
    VertexTestExample(  # One crease at the vertex.
        creases=[
            crease.Crease(
                point.Point(x=0, y=0),
                point.Point(x=0.5, y=0.5),
                fold=crease.Fold.BORDER,
            ),
        ],
    ),
]


class VertexTest(parameterized.TestCase):

  @parameterized.parameters(_VALID_VERTEX_EXAMPLES)
  def test_valid_vertex(self, example: VertexTestExample):
    v1 = vertex.Vertex(creases=example.creases)
    self.assertIsInstance(v1, vertex.Vertex)
    self.assertTrue(v1.is_valid)
    self.assertEqual(v1.angles, sorted(v1.angles))
    self.assertEqual(len(v1.creases), len(v1.angles))

  @parameterized.parameters(_INVALID_VERTEX_EXAMPLES)
  def test_invalid_vertex(self, example: VertexTestExample):
    v1 = vertex.Vertex(creases=example.creases)
    self.assertFalse(v1.is_valid)

  @parameterized.parameters(_ERROR_VERTEX_EXAMPLES)
  def test_error_vertex(self, example: VertexTestExample):
    with self.assertRaises(ValueError):
      vertex.Vertex(creases=example.creases)

  @parameterized.parameters([_VALID_VERTEX_EXAMPLES[0]])
  def test_add_crease(self, example: VertexTestExample):
    v = vertex.Vertex(creases=example.creases.copy())
    v.add_crease(
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0, y=1),
            fold=crease.Fold.BORDER,
        )
    )
    self.assertLen(v.creases, 3)
    with self.assertRaises(ValueError):
      v.add_crease(
          crease.Crease(
              point.Point(x=0.2, y=0.5),
              point.Point(x=0, y=1),
              fold=crease.Fold.BORDER,
          )
      )

  # Tests all cached properties of Vertex.
  @parameterized.parameters(*(
      f.attrname
      for f in vertex.Vertex.__dict__.values()
      if isinstance(f, functools.cached_property)
  ))
  def test_add_remove_crease_clears_properties(self, attribute_name: str):
    v = vertex.Vertex(creases=_VALID_VERTEX_EXAMPLES[0].creases.copy())
    # Access a cached property to populate the cache.
    getattr(v, attribute_name)
    self.assertIn(attribute_name, vars(v))

    with self.subTest("add_crease_clears_cache"):
      # Add a crease and check if the cache is cleared.
      new_crease = crease.Crease(
          point.Point(x=0.5, y=0.5),
          point.Point(x=0, y=1),
          fold=crease.Fold.BORDER,
      )
      v.add_crease(new_crease)
      self.assertNotIn(attribute_name, vars(v))

    with self.subTest("remove_crease_clears_cache"):
      # Re-populate cache.
      getattr(v, attribute_name)
      self.assertIn(attribute_name, vars(v))

      # Remove the crease and check if the cache is cleared.
      v.remove_crease(new_crease)
      self.assertNotIn(attribute_name, vars(v))
      getattr(v, attribute_name)

  @parameterized.parameters([_VALID_VERTEX_EXAMPLES[0]])
  def test_sector_angles(self, example: VertexTestExample):
    v = vertex.Vertex(creases=example.creases)
    sector_angles = v.sector_angles()
    self.assertLen(sector_angles, 2)

    a1, a2 = sector_angles
    self.assertEqual(a1, (225, crease.Fold.MOUNTAIN, crease.Fold.MOUNTAIN))
    self.assertEqual(a2, (135, crease.Fold.MOUNTAIN, crease.Fold.MOUNTAIN))

  @parameterized.parameters([_VALID_VERTEX_EXAMPLES[0]])
  def test_remove_crease(self, example: VertexTestExample):
    v = vertex.Vertex(creases=example.creases)
    self.assertLen(v.creases, 2)
    v.remove_crease(v.creases[0])
    self.assertLen(v.creases, 1)
    c = v.creases[0]
    new_crease = crease.Crease(
        c.p1,
        c.p2,
        fold=crease.Fold.BORDER,
    )
    with self.assertRaises(ValueError):
      v.remove_crease(new_crease)

  def test_foldability(self):
    creases = [
        crease.Crease(
            point.Point(x=0, y=0),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.VALLEY,
            fold_percent=0.5,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1, y=1),
            fold=crease.Fold.VALLEY,
            fold_percent=0.5,
        ),
        crease.Crease(
            point.Point(x=0, y=1),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.VALLEY,
            fold_percent=0.5,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1, y=0),
            fold=crease.Fold.VALLEY,
            fold_percent=1.0,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.MOUNTAIN,
            fold_percent=1.0,
        ),
    ]
    v = vertex.Vertex(creases=creases)
    self.assertTrue(v.is_foldable)
    self.assertFalse(v.flat_foldability())

  @parameterized.parameters(_INVALID_VERTEX_ANGLES)
  def test_fail_crimp_angles(self, example: VertexTestExample):
    v = vertex.Vertex(creases=example.creases)
    self.assertFalse(v.check_crimp_angles)
    self.assertTrue(v.check_blb)

  @parameterized.parameters(_VALID_VERTEX_EXAMPLES[3:])
  def test_pass_crimp_angles(self, example: VertexTestExample):
    v = vertex.Vertex(creases=example.creases)
    self.assertTrue(v.check_crimp_angles)

  def test_blb_fail_crimp_pass(self):
    creases = [
        crease.Crease(
            point.Point(x=0.0, y=0.5),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.MOUNTAIN,
            fold_percent=1.0,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.0),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.VALLEY,
            fold_percent=1.0,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1.0, y=0.5),
            fold=crease.Fold.VALLEY,
            fold_percent=1.0,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0.7, y=1.0),
            fold=crease.Fold.VALLEY,
            fold_percent=1.0,
        ),
    ]
    v = vertex.Vertex(creases=creases)
    self.assertFalse(v.check_blb)
    self.assertTrue(v.check_crimp_angles)

  def test_crimp_angles_smallest_angle_same_fold(self):
    # Test case where the smallest angle does not have one mountain and one
    # valley crease.
    creases = [
        crease.Crease(
            point.Point(x=0, y=0),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1, y=0),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0.6, y=0.4),
            fold=crease.Fold.VALLEY,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=0.5, y=0),
            fold=crease.Fold.VALLEY,
        ),
    ]
    v = vertex.Vertex(creases=creases)
    self.assertFalse(v.check_crimp_angles)

  def test_clone(self):
    creases = [
        crease.Crease(
            point.Point(x=0, y=0),
            point.Point(x=0.5, y=0.5),
            fold=crease.Fold.MOUNTAIN,
        ),
        crease.Crease(
            point.Point(x=0.5, y=0.5),
            point.Point(x=1, y=0.5),
            fold=crease.Fold.MOUNTAIN,
        ),
    ]
    v = vertex.Vertex(creases=creases)
    v_clone = v.clone()

    # Check that point is the same object
    self.assertIs(v.point, v_clone.point)

    # Check that creases and angles are equal but not the same object
    self.assertEqual(v.creases, v_clone.creases)
    self.assertIsNot(v.creases, v_clone.creases)
    self.assertEqual(v.angles, v_clone.angles)
    self.assertIsNot(v.angles, v_clone.angles)

    with self.subTest("modify_clone"):
      # Modify the clone and check that the original is not affected
      v_clone.add_crease(
          crease.Crease(
              point.Point(x=0.5, y=0.5),
              point.Point(x=0.5, y=1),
              fold=crease.Fold.VALLEY,
          )
      )
      self.assertLen(v.creases, 2)
      self.assertLen(v_clone.creases, 3)

      self.assertLen(v.angles, 2)
      self.assertLen(v_clone.angles, 3)


if __name__ == "__main__":
  absltest.main()
