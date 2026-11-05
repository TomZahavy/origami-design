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

"""The output of the packing solver."""

import json
import typing
from typing import TypedDict

import numpy as np
import pydantic

from .. import rectangle as shaping_utils
from ..crease_pattern import crease_pattern
from ..stick_figures import stick_figure as sf
from . import config as config_lib
from . import river as river_lib
from . import types
from . import utils_packing_svg
from . import utils_tracker
from .debug import debug_types


class NumpyEncoder(json.JSONEncoder):
  """A JSON encoder that handles numpy types."""

  def default(self, o: typing.Any) -> typing.Any:
    if isinstance(o, np.integer):
      return int(o)
    if isinstance(o, np.floating):
      return float(o)
    if isinstance(o, np.ndarray):
      return o.tolist()
    return json.JSONEncoder.default(self, o)


class PackingOutputDict(TypedDict):
  """A dictionary representation of PackingOutput."""

  success: bool
  flap_rectangles: str | None
  packing_rivers: str
  hinges: str | None
  sacrificial_flaps: str | None
  error_message: str | None
  details: debug_types.TilingDetails | None
  config: config_lib.PackingConfigDict | None


class PackingValidationError(Exception):
  """Error raised when packing output validation fails."""


class PackingOutput(pydantic.BaseModel):
  """Output of packing step.

  Attributes:
    success: Whether a perfect tiling was found and crease pattern generated.
    packing_cp: packing crease pattern.
    flap_rectangles: The rectangles of the flaps.
    packing_rivers: A dict from river name to rivers in the packing crease
      pattern.
    stick_figure: The stick figure.
    unmerged_stick_figure: Optional unmerged stick figure before level-shifter
      merge.
    hinges: Information about hinges in packing.
    sacrificial_flaps: Information about sacrificial flaps in packing.
    tracker: The crease pattern tracker.
    error_message: A summary of the error, if not successful.
    details: A dictionary with more details about the process, like
      is_symmetric, grid_size, unused_area, num_delta_combinations, suggestions
      for parameters.
    config: Configuration object that holds solver parameters.
  """

  model_config = pydantic.ConfigDict(frozen=True, arbitrary_types_allowed=True)

  success: bool
  packing_cp: crease_pattern.CreasePattern | None = None
  stick_figure: sf.StickFigure | None = None
  unmerged_stick_figure: sf.StickFigure | None = None
  flap_rectangles: list[shaping_utils.Rectangle] | None = None
  packing_rivers: dict[str, river_lib.PackingRiver | typing.Any] = (
      pydantic.Field(default_factory=dict)
  )
  hinges: list[types.HingeInfo] | None = None
  sacrificial_flaps: list[types.SacrificialFlap] | None = None
  tracker: utils_tracker.CreasePatternTracker | None = None
  error_message: str | None = None
  details: debug_types.TilingDetails | None = None
  config: config_lib.PackingConfig | None = None

  def asdict(self) -> dict[str, typing.Any]:
    """Returns a lossless plain-JSON dictionary via bp_pipeline.codec."""
    from .. import codec  # pylint: disable=g-import-not-at-top

    return codec.pack_to_dict(self)

  @classmethod
  def from_error(
      cls,
      error_message: str,
      details: debug_types.TilingDetails,
      tracker: utils_tracker.CreasePatternTracker | None = None,
      config: config_lib.PackingConfig | None = None,
  ) -> 'PackingOutput':
    """Creates a PackingOutput from an error."""
    return cls(
        success=False,
        packing_cp=None,
        flap_rectangles=None,
        packing_rivers=dict(),
        stick_figure=None,
        error_message=error_message,
        details=details,
        hinges=None,
        sacrificial_flaps=None,
        tracker=tracker,
        config=config,
    )

  def validate(self) -> None:
    """Performs assertions on a successful PackingOutput before returning."""
    if not self.success:
      raise PackingValidationError('Validation failed: success is False.')
    if self.details is None:
      raise PackingValidationError('Validation failed: details is None.')
    if self.tracker is None:
      raise PackingValidationError('Validation failed: tracker is None.')
    if self.stick_figure is None:
      raise PackingValidationError('Validation failed: stick_figure is None.')

    details = self.details
    tracker = self.tracker
    tree = self.stick_figure

    if not self.config or not getattr(self.config, 'easy_mode', False):
      if not details.get('perfect_tiling_found'):
        raise PackingValidationError(
            'PackingOutput inconsistency: success=True but perfect_tiling_found'
            ' is not True.'
        )
      if details.get('unused_area') != 0:
        raise PackingValidationError(
            'PackingOutput inconsistency: success=True but unused_area is not'
            ' 0.'
        )

    packed_leaf_ids = set(tracker.packed_polygons.keys()) | set(
        tracker.packed_rivers.keys()
    )
    packed_stick_names = {
        name.replace(utils_packing_svg.PolygonIDSuffix.COPY.value, '')
        for name in packed_leaf_ids
    }
    for stick in tree.children:
      if stick.name not in packed_stick_names:
        raise PackingValidationError(
            f'Stick {stick.name} from stick figure not found in final packing.'
        )

    if self.packing_cp is None:
      raise PackingValidationError(
          'PackingOutput inconsistency: success=True but packing_cp is None.'
      )
    if self.hinges is None:
      raise PackingValidationError(
          'PackingOutput inconsistency: success=True but hinges is None.'
      )
