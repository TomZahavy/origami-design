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

import dataclasses

from absl.testing import absltest
from absl.testing import parameterized
from bp_pipeline.crease_pattern.parser import parser_utils


@dataclasses.dataclass(frozen=True)
class FormatTestCase:
  """Contains a single variant of a problem."""

  value: float
  scale: float
  ndigits: int
  expected: str | None = None


FORMAT_TEST_EXAMPLES = [
    (
        "Trailing zeros ndigits=1",
        FormatTestCase(value=1, scale=1000, ndigits=1, expected="1000"),
    ),
    (
        "Trailing zeros ndigits=2",
        FormatTestCase(value=1, scale=1000, ndigits=2, expected="1000"),
    ),
    (
        "Trailing zeros ndigits=3",
        FormatTestCase(value=1, scale=1000, ndigits=3, expected="1000"),
    ),
    (
        "Trailing zeros ndigits=4",
        FormatTestCase(value=1, scale=1000, ndigits=4, expected="1000"),
    ),
    (
        "Trailing zeros ndigits=5",
        FormatTestCase(value=1, scale=1000, ndigits=5, expected="1000"),
    ),
    (
        "Float test (value=1.0)",
        FormatTestCase(value=1.0, scale=1000, ndigits=3, expected="1000"),
    ),
    (
        "Float test (value=0.5)",
        FormatTestCase(value=0.5, scale=1000, ndigits=3, expected="500"),
    ),
    (
        "Float test (value=1/3)",
        FormatTestCase(value=1 / 3, scale=1000, ndigits=3, expected="333"),
    ),
    (
        "Float test (value=0.04)",
        FormatTestCase(value=0.04, scale=1000, ndigits=3, expected="40"),
    ),
    (
        "Edge of ndigits (value=0.500111)",
        FormatTestCase(value=0.500111, scale=1000, ndigits=3, expected="500"),
    ),
    (
        "Edge of ndigits (value=0.501111)",
        FormatTestCase(value=0.501111, scale=1000, ndigits=3, expected="501"),
    ),
    (
        "Edge of ndigits (value=0.1000111)",
        FormatTestCase(value=0.1000111, scale=1000, ndigits=3, expected="100"),
    ),
    (
        "Edge of ndigits (value=0.000111)",
        FormatTestCase(value=0.000111, scale=1000, ndigits=3, expected="0"),
    ),
    (
        "Zero is 0 (ndigits=3)",
        FormatTestCase(value=0, scale=1000, ndigits=3, expected="0"),
    ),
    (
        "Zero is 0 (ndigits=4)",
        FormatTestCase(value=0, scale=1000, ndigits=4, expected="0"),
    ),
    (
        "0.0 is 0",
        FormatTestCase(value=0.0, scale=1000, ndigits=4, expected="0"),
    ),
    (
        "Rounding down",
        FormatTestCase(value=0.44, scale=10, ndigits=1, expected="4"),
    ),
    (
        "Rounding up",
        FormatTestCase(value=0.45, scale=10, ndigits=1, expected="5"),
    ),
    (
        "Rounding down, scale=1",
        FormatTestCase(value=0.44, scale=1, ndigits=1, expected="0.4"),
    ),
    (
        "Rounding up, scale=1",
        FormatTestCase(value=0.45, scale=1, ndigits=1, expected="0.5"),
    ),
    (
        "Different scales (scale=0.1)",
        FormatTestCase(value=1, scale=0.1, ndigits=3, expected="0.1"),
    ),
    (
        "Different scales (scale=1)",
        FormatTestCase(value=1, scale=1, ndigits=3, expected="1"),
    ),
    (
        "Different scales (scale=5)",
        FormatTestCase(value=1, scale=5, ndigits=3, expected="5"),
    ),
    (
        "Different scales (scale=10)",
        FormatTestCase(value=1, scale=10, ndigits=3, expected="10"),
    ),
    (
        "Different scales (scale=50)",
        FormatTestCase(value=1, scale=50, ndigits=3, expected="50"),
    ),
    (
        "Different scales (scale=100)",
        FormatTestCase(value=1, scale=100, ndigits=3, expected="100"),
    ),
    (
        "Different scales (scale=1000)",
        FormatTestCase(value=1, scale=1000, ndigits=3, expected="1000"),
    ),
    (
        "Different scales (scale=10000)",
        FormatTestCase(value=1, scale=10000, ndigits=3, expected="10000"),
    ),
    (
        "Different ndigits (value=4/9, ndigits=1)",
        FormatTestCase(value=4 / 9, scale=1000, ndigits=1, expected="400"),
    ),
    (
        "Different ndigits (value=4/9, ndigits=2)",
        FormatTestCase(value=4 / 9, scale=1000, ndigits=2, expected="440"),
    ),
    (
        "Different ndigits (value=4/9, ndigits=3)",
        FormatTestCase(value=4 / 9, scale=1000, ndigits=3, expected="444"),
    ),
    (
        "Different ndigits (value=4/9, ndigits=4)",
        FormatTestCase(value=4 / 9, scale=1000, ndigits=4, expected="444.4"),
    ),
    (
        "Different ndigits (value=4/9, ndigits=5)",
        FormatTestCase(value=4 / 9, scale=1000, ndigits=5, expected="444.44"),
    ),
    (
        "Different ndigits (value=5/9, ndigits=1)",
        FormatTestCase(value=5 / 9, scale=100, ndigits=1, expected="60"),
    ),
    (
        "Different ndigits (value=5/9, ndigits=2)",
        FormatTestCase(value=5 / 9, scale=100, ndigits=2, expected="56"),
    ),
    (
        "Different ndigits (value=5/9, ndigits=3)",
        FormatTestCase(value=5 / 9, scale=100, ndigits=3, expected="55.6"),
    ),
    (
        "Different ndigits (value=5/9, ndigits=4)",
        FormatTestCase(value=5 / 9, scale=100, ndigits=4, expected="55.56"),
    ),
    (
        "Different ndigits (value=5/9, ndigits=5)",
        FormatTestCase(value=5 / 9, scale=100, ndigits=5, expected="55.556"),
    ),
    (
        "Close to 0",
        FormatTestCase(value=-1e-4, scale=100, ndigits=2, expected="0"),
    ),
    (
        "Close to 1",
        FormatTestCase(value=1.0001, scale=100, ndigits=2, expected="100"),
    ),
    (
        "High precision ndigits=20",
        FormatTestCase(
            value=0.1234567890123456789,
            scale=1000,
            ndigits=20,
            expected="123.45678901234568058953",
        ),
    ),
]

INVALID_FORMAT_TEST_EXAMPLES = [
    FormatTestCase(value=1.1, scale=1000, ndigits=3),
    FormatTestCase(value=-0.1, scale=1000, ndigits=3),
    FormatTestCase(value=1, scale=1000, ndigits=0),
    FormatTestCase(value=1, scale=1000, ndigits=-1),
]


class ParserUtilsTest(parameterized.TestCase):

  @parameterized.named_parameters(FORMAT_TEST_EXAMPLES)
  def test_point_format(self, case: FormatTestCase):
    point = parser_utils.point_format(case.value, case.scale, case.ndigits)
    self.assertEqual(point, case.expected)

  @parameterized.parameters(INVALID_FORMAT_TEST_EXAMPLES)
  def test_invalid_point_format(self, case: FormatTestCase):
    with self.assertRaises(ValueError):
      parser_utils.point_format(case.value, case.scale, case.ndigits)


if __name__ == "__main__":
  absltest.main()
