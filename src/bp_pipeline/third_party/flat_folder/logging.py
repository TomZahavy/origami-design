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
#
# Ported from Flat-Folder (https://github.com/origamimagiro/flat-folder),
# Copyright (c) 2022 Jason S. Ku (origamimagiro), licensed under the MIT
# License; see LICENSE in this directory.
# ==============================================================================

"""Utility classes for logging and progress tracking."""

import time

from absl import logging


class NOTE:
  """A simple utility class for logging and progress tracking."""

  show: bool = True
  lines: list[str] = []
  check_interval: int = 5000
  check_label: str = ""

  main_start: float = 0
  main_lap: float = 0
  est_start: float = 0
  est_lap: float = 0
  est_lim: int | None = 0

  @classmethod
  def start(cls, label: str | None = None) -> None:
    """Starts the main timer and optionally logs a starting message.

    Args:
        label: An optional label to log with timestamp indicating start.
    """
    cls.main_start = time.time() * 1000
    cls.main_lap = cls.main_start
    if label:
      cls.time(label)

  @classmethod
  def time(cls, label: str) -> None:
    """Logs a message with the current timestamp.

    Args:
        label: The message to log.
    """
    now = time.localtime()
    time_str = time.strftime("%H:%M:%S", now)
    cls.log(f"{time_str} | {label}")

  @classmethod
  def log(cls, message: str) -> None:
    """Logs a message to stdout and stores it if cls.show is True.

    Args:
        message: The message to log.
    """
    if cls.show:
      logging.info(message)
      cls.lines.append(message)

  @classmethod
  def start_check(
      cls,
      label: str,
      items: list[object] | set[object] | int | None = None,
      interval: int = 5000,
  ) -> None:
    """Initializes progress checking for a loop or iterative process.

    Args:
        label: A label for the process being tracked (e.g., 'profiles').
        items: A collection (list or set) or an integer representing total items
          to process. If provided, used for estimating time remaining.
        interval: The logging interval in milliseconds.
    """
    limit = len(items) if isinstance(items, (list, set)) else items
    cls.est_start = time.time() * 1000
    cls.est_lap = cls.est_start
    cls.est_lim = limit
    cls.check_interval = interval
    cls.check_label = label

  @classmethod
  def check(cls, current_step: int) -> None:
    """Checks progress and logs estimated time remaining if interval is met.

    Args:
        current_step: The current step or item index in the process.
    """
    now = time.time() * 1000
    if (now - cls.est_lap) > cls.check_interval:
      if cls.est_lim:
        elapsed = now - cls.est_start
        if current_step > 0:
          remaining_time = elapsed * (cls.est_lim / current_step - 1)
          remaining_time_str = cls._format_time(remaining_time)
          cls.log(
              f"    On {cls.check_label} {current_step} out of"
              f" {cls.est_lim}, est time left: {remaining_time_str}"
          )
      else:
        cls.log(f"    On {cls.check_label} {current_step} of unknown")
      cls.est_lap = now

  @classmethod
  def count(cls, items: list[object] | int, label: str) -> int:
    """Counts items in a list or nested list and logs the count.

    Args:
        items: An integer count, a list of items, or a list of lists.
        label: A label for the items being counted (e.g., 'assignments').

    Returns:
        The total count of items.
    """
    if isinstance(items, list):
      if items and isinstance(items[0], list):
        item_count = sum(len(sub) for sub in items)  # pyrefly: ignore[bad-argument-type]
      else:
        item_count = len(items)
    else:
      item_count = items
    cls.log(f"   - Found {item_count} {label}")
    return item_count

  @classmethod
  def _format_time(cls, milliseconds: float) -> str:
    """Formats milliseconds into a human-readable string.

    Args:
        milliseconds: A duration in milliseconds.

    Returns:
        A formatted string (e.g., '1 mins 5 secs', '500 millisecs').
    """
    if milliseconds < 1000:
      return f"{int(milliseconds)} millisecs"
    if milliseconds < 60000:
      return f"{int(milliseconds/1000)} secs"
    minutes = int(milliseconds / 60000)
    seconds = int((milliseconds - minutes * 60000) / 1000)
    return f"{minutes} mins {seconds} secs"
