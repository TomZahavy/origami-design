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

"""A utility to check for global flat-foldability of a CreasePattern."""

from typing import Any
from absl import logging
from bp_pipeline.crease_pattern import crease_pattern
from bp_pipeline.crease_pattern.parser import cp_format
from bp_pipeline.third_party.flat_folder import fold_cp


def _log_result(result: Any, implementation: str):
  """Logs flat-foldability result.

  Args:
    result: The FlatFolderFOLD object containing the result.
    implementation: The name of the flat folder implementation used.
  """
  is_foldable = result.flat_foldable
  logging.info('Flat Folder %s result: %s', implementation, result)
  if not is_foldable:
    logging.info(
        'Flat Folder %s conflict reason: %s',
        implementation,
        result.conflict_reason,
    )
    logging.info(
        'Flat Folder %s conflict faces: %s',
        implementation,
        result.conflict_faces,
    )
    logging.info(
        'Flat Folder %s local violations: %s',
        implementation,
        result.local_violations,
    )


def is_globally_flat_foldable(
    cp: crease_pattern.CreasePattern,
    verbose: bool = False,
    scale: int = 1000,
    ndigits: int = 3,
    grid: int = -1,
) -> bool:
  """Checks if a CreasePattern object is globally flat-foldable.

  Args:
    cp: The CreasePattern object to check.
    verbose: Whether to log information.
    scale: The scale factor to use for the CreasePattern.
    ndigits: The number of digits to use for the CreasePattern.
    grid: The grid size to use for the CreasePattern.

  Returns:
    True if the CreasePattern is globally flat-foldable, False otherwise.
  """
  cp_string = cp_format.to_cp(cp, scale=scale, ndigits=ndigits, grid=grid)
  result = fold_cp.analyze_fold_file(
      filename='pattern.cp',
      doc_content=cp_string,
      file_ext='.cp',
      generate_state_data=False,
  )
  fold_result = result.flat_folder_fold
  if verbose:
    _log_result(fold_result, 'Python')
  is_foldable = fold_result.flat_foldable
  return is_foldable if is_foldable is not None else False
