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

"""Module entry point (`python -m bp_pipeline`) for the `bp-pipeline` CLI."""

# pylint: disable=invalid-name,g-import-not-at-top

import importlib.util
import pathlib
import sys

if importlib.util.find_spec('bp_pipeline') is None:
  sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from bp_pipeline import cli

if __name__ == '__main__':
  cli.main()
