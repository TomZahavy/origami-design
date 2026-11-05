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

"""Heuristic utilities for subdividing and preparing 3D shaping elements."""

from collections.abc import Sequence
import logging
import math
from typing import TypedDict

from ..crease_pattern import crease as crease_utils
from ..packing import types as packing_types
from ..stick_figures import stick_figure as sf_utils
from ..stick_figures import traversal as tr
from . import heuristics
from . import shaping_elements
from . import types as shaping_types

MIN_ANGLE = math.radians(20)
# NOTE: 0.05 added to avoid numerical issues / duplicate creases.
LARGE_ANGLE = math.pi - MIN_ANGLE / 2 + 0.05


def apply_small_angle_flip(target_flap_angle: float) -> Sequence[float]:
  """Splits an acute positive flap angle into two large shallow-fold angles.

  Args:
    target_flap_angle: Positive target flap angle in radians.

  Returns:
    Either `[target_flap_angle]` when no split is needed (`>= pi/2` or `~0`),
    or `[LARGE_ANGLE, remainder]` decomposing the acute rotation into two
    shallow folds.
  """
  if target_flap_angle < -crease_utils.DEFAULT_TOLERANCE:
    raise ValueError(
        'Target flap angle must be non-negative to apply small angle flip,'
        f' got {target_flap_angle}.'
    )
  if target_flap_angle >= (
      math.pi / 2
  ) - crease_utils.DEFAULT_TOLERANCE or math.isclose(
      target_flap_angle,
      0.0,
      abs_tol=crease_utils.DEFAULT_TOLERANCE,
  ):
    return [target_flap_angle]

  small_angle = max(MIN_ANGLE, target_flap_angle)
  remainder = (2 * math.pi - small_angle) - LARGE_ANGLE
  return [LARGE_ANGLE, remainder]


def _get_shaping_elements_for_unmerged_flaps(
    flaps: list[shaping_elements.ShapingFlap],
    rivers: list[shaping_elements.ShapingRiver],
    outer_bank_indices: dict[str, shaping_types.BankIndex],
    unmerged_flap_info: dict[str, heuristics.Node],
    merged_stick_name_dict: dict[str, list[str]],
) -> tuple[
    list[shaping_elements.ShapingFlap], list[shaping_elements.ShapingRiver]
]:
  """Creates new shaping elements for unmerged flaps and rivers."""
  unmerged_flaps, unmerged_rivers = [], []

  # Step 1: create new shaping elements for unmerged sticks in a flap
  for flap in flaps:
    merged_name = flap.name
    unmerged_names = merged_stick_name_dict.get(merged_name, None)

    # If flap name not found in merge dict, the flap was never merged
    if unmerged_names is None:
      unmerged_flaps.append(flap)
      continue

    logging.debug(
        'Subdividing flap %s with grid radius %s',
        merged_name,
        flap.grid_unit_radius,
    )

    for ind, unmerged_name in enumerate(unmerged_names):
      stick_length = unmerged_flap_info[unmerged_name].length
      logging.debug(
          'Creating unmerged flap %s with length %s',
          unmerged_name,
          stick_length,
      )
      if math.isclose(flap.grid_unit_radius, stick_length):
        unmerged_flap = flap.rename_and_copy(unmerged_name)
        assert (
            ind == len(unmerged_names) - 1
        ), 'Unmerged sticks too long or element too short!'
        unmerged_flaps.append(unmerged_flap)
      else:
        unmerged_flap = flap.rename_and_copy(
            unmerged_name, max_shaping_depth=stick_length
        )
        flap = flap.shrink(stick_length)
        unmerged_flaps.append(unmerged_flap)

  # Step 2: get unmerged rivers
  for river in rivers:
    merged_name = river.name
    unmerged_names = merged_stick_name_dict.get(merged_name, None)

    if unmerged_names is None:
      unmerged_rivers.append(river)
      continue

    logging.debug(
        'Subdividing river %s with grid radius %s',
        merged_name,
        river.width,
    )

    for ind, unmerged_name in enumerate(unmerged_names):
      stick_length = unmerged_flap_info[unmerged_name].length

      logging.debug(
          'Creating unmerged river %s with length %s',
          unmerged_name,
          stick_length,
      )

      if river.width == stick_length:
        unmerged_river = river.rename_and_copy(unmerged_name)
        assert (
            ind == len(unmerged_names) - 1
        ), 'Unmerged sticks too long or element too short!'
      else:
        outer_bank_index = outer_bank_indices[merged_name]
        unmerged_river = river.get_circumbscribed_river(
            stick_length, unmerged_name, outer_bank_index
        )
        river = river.shrink_along_bank(outer_bank_index, stick_length)
      unmerged_rivers.append(unmerged_river)

  return unmerged_flaps, unmerged_rivers


def get_outer_bank_indices(
    stick_figure: sf_utils.StickFigure,
    shaping_flaps: list[shaping_elements.ShapingFlap],
    shaping_rivers: list[shaping_elements.ShapingRiver],
) -> dict[str, shaping_types.BankIndex]:
  """Computes river outer bank indices."""
  outer_bank_indices: dict[str, shaping_types.BankIndex] = {}
  root_name = heuristics.get_first_stick_for_shaping(stick_figure).name
  for river in shaping_rivers:
    try:
      bank_index = river.get_outer_bank_index(
          stick_figure,
          root_name,
          shaping_flaps,
          shaping_rivers,
      )
    except ValueError as e:
      logging.warning(
          'Could not determine outer bank index for river %s: %s',
          river.name,
          e,
      )
      bank_index = river.longer_bank_index
    outer_bank_indices[river.name] = bank_index
  return outer_bank_indices


def _rename_shaping_elements_to_match_merge_converter(
    shaping_flaps: list[shaping_elements.ShapingFlap],
    shaping_rivers: list[shaping_elements.ShapingRiver],
    merge_converter: dict[str, str],
) -> tuple[
    list[shaping_elements.ShapingFlap], list[shaping_elements.ShapingRiver]
]:
  """Renames shaping elements to match `merge_converter`."""
  packing_name_to_tree_name = {v: k for k, v in merge_converter.items()}
  new_shaping_flaps = []
  new_shaping_rivers = []
  for packing_name, tree_name in packing_name_to_tree_name.items():
    shaping_element = shaping_elements.get_element_by_name(
        packing_name, shaping_flaps, shaping_rivers
    )
    if isinstance(shaping_element, shaping_elements.ShapingFlap):
      new_shaping_flaps.append(shaping_element.rename_and_copy(tree_name))
    elif isinstance(shaping_element, shaping_elements.ShapingRiver):
      new_shaping_rivers.append(shaping_element.rename_and_copy(tree_name))
    else:
      raise ValueError(
          f'Unsupported shaping element type: {type(shaping_element)}'
          f' for element {packing_name}.'
      )
  return new_shaping_flaps, new_shaping_rivers


def _order_stick_name_dict_values_by_root_proximity(
    unmerged_stick_figure: sf_utils.StickFigure,
    merged_stick_name_dict: dict[str, list[str]],
) -> dict[str, list[str]]:
  """Orders lists of unmerged sub-sticks by distance from the unmerged root."""
  unmerged_to_merged_dict = {}
  for merged_name, unmerged_names in merged_stick_name_dict.items():
    for unmerged_name in unmerged_names:
      unmerged_to_merged_dict[unmerged_name] = merged_name

  unmerged_root = heuristics.get_first_stick_for_shaping(unmerged_stick_figure)
  marked_merged_stick_names = set()
  for unmerged_stick in tr.breadth_first_traversal(
      unmerged_stick_figure, start_stick_name=unmerged_root.name
  ):
    if unmerged_stick.name in unmerged_to_merged_dict:
      merged_stick_name = unmerged_to_merged_dict[unmerged_stick.name]
      if merged_stick_name not in marked_merged_stick_names:
        unmerged_stick_names = merged_stick_name_dict[merged_stick_name]
        assert unmerged_stick.name == unmerged_stick_names[0] or (
            unmerged_stick.name == unmerged_stick_names[-1]
        ), (
            f'Unmerged stick {unmerged_stick.name} not at expected position'
            f' in unmerged_stick_names {unmerged_stick_names}!'
        )
        if unmerged_stick_names[-1] == unmerged_stick.name:
          merged_stick_name_dict[merged_stick_name] = unmerged_stick_names[::-1]

      marked_merged_stick_names.add(merged_stick_name)

  return merged_stick_name_dict


class ShapingData(TypedDict):
  """Shaping data used for 3D heuristics."""

  shaping_flaps: list[shaping_elements.ShapingFlap]
  shaping_rivers: list[shaping_elements.ShapingRiver]
  flap_info: dict[str, heuristics.Node]
  outer_bank_indices: dict[str, shaping_types.BankIndex]


def get_heuristics_shaping_data(
    stick_figure: sf_utils.StickFigure,
    shaping_flaps: list[shaping_elements.ShapingFlap],
    shaping_rivers: list[shaping_elements.ShapingRiver],
    hinge_info_list: list[packing_types.HingeInfo],
    central_crease_removed: bool,
    *,
    shape_with_unmerged_tree: bool = False,
    merge_converter: dict[str, str] | None = None,
    sacrificial_flaps: Sequence[packing_types.SacrificialFlap] = (),
) -> ShapingData:
  """Computes data necessary for 3D shaping heuristics."""
  unmerged_stick_figure = stick_figure
  stick_figure, merged_stick_name_dict = stick_figure.merge_linear_chains()
  merged_stick_name_dict = _order_stick_name_dict_values_by_root_proximity(
      unmerged_stick_figure, merged_stick_name_dict
  )
  stick_figure = stick_figure.align_root_stick_to_target_azimuth_elevation()
  unmerged_stick_figure = (
      unmerged_stick_figure.align_root_stick_to_target_azimuth_elevation()
  )
  if merge_converter:
    if sacrificial_flaps:
      raise NotImplementedError(
          'Sacrificial flaps are not supported when renaming shaping elements'
          ' to match merge_converter.'
      )
    shaping_flaps, shaping_rivers = (
        _rename_shaping_elements_to_match_merge_converter(
            shaping_flaps, shaping_rivers, merge_converter
        )
    )
    inverted_merge_converter = {v: k for k, v in merge_converter.items()}
    for hinge_info in hinge_info_list:
      element_names = hinge_info.flap_names
      new_names = tuple(
          inverted_merge_converter.get(name, name) for name in element_names
      )
      hinge_info.flap_names = new_names  # pyrefly: ignore[bad-assignment]

  root_stick_direction = (
      heuristics.compute_root_stick_direction_follow_stick_figure_root(
          stick_figure, shaping_flaps, shaping_rivers
      )
  )
  logging.debug('root_stick_direction: %r', root_stick_direction)

  sac_flaps_mapping = heuristics.build_sacrificial_flaps_by_base_flap(
      sacrificial_flaps
  )
  flap_info = heuristics.get_flap_info_dict_with_hinge_info(
      stick_figure,
      hinge_info_list,
      root_stick_direction,
      sac_flaps_mapping,
  )
  unmerged_flap_info = heuristics.get_flap_info_dict_for_unmerged_stick_figure(
      unmerged_stick_figure=unmerged_stick_figure,
      merged_stick_name_dict=merged_stick_name_dict,
      hinge_info_list=hinge_info_list,
      root_direction_follow_stick_figure_root=root_stick_direction,
      node_dict=flap_info,
      sacrificial_flaps_by_base_flap=sac_flaps_mapping,
  )

  outer_bank_indices = get_outer_bank_indices(
      stick_figure, shaping_flaps, shaping_rivers
  )

  if shape_with_unmerged_tree:
    shaping_flaps, shaping_rivers = _get_shaping_elements_for_unmerged_flaps(
        flaps=shaping_flaps,
        rivers=shaping_rivers,
        outer_bank_indices=outer_bank_indices,
        unmerged_flap_info=unmerged_flap_info,
        merged_stick_name_dict=merged_stick_name_dict,
    )
    flap_info = unmerged_flap_info
    outer_bank_indices = get_outer_bank_indices(
        unmerged_stick_figure, shaping_flaps, shaping_rivers
    )

    logging.debug('New flaps: %r', shaping_flaps)
    logging.debug('New rivers: %r', shaping_rivers)

  shaping_flaps, shaping_rivers = (
      shaping_elements.adjust_shaping_elements_for_central_crease_removal(
          shaping_flaps,
          shaping_rivers,
          outer_bank_indices,
          central_crease_removed,
      )
  )

  return ShapingData(
      shaping_flaps=shaping_flaps,
      shaping_rivers=shaping_rivers,
      flap_info=flap_info,
      outer_bank_indices=outer_bank_indices,
  )
