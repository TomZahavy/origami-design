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

"""Cooperative timeout utilities for packing and solving."""

from collections.abc import Iterator
import contextlib
import contextvars
import dataclasses
import datetime


class StageTimeoutError(TimeoutError):
  """Raised when a pipeline stage exceeds its timeout."""


class SweepLevelTimeoutError(TimeoutError):
  """Raised when a single packing/solving sweep configuration times out."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class CooperativeTimeout:
  """Tracks a UTC cooperative timeout deadline."""

  start_time: datetime.datetime
  timeout: datetime.timedelta

  def __post_init__(self) -> None:
    if self.start_time.tzinfo != datetime.timezone.utc:
      raise ValueError(
          f'start_time must be in utc timezone, got {self.start_time.tzinfo}'
      )
    if self.timeout <= datetime.timedelta(0):
      raise ValueError(f'Timeout must be positive, got {self.timeout}')

  @classmethod
  def from_timedelta(cls, timeout: datetime.timedelta) -> 'CooperativeTimeout':
    return cls(
        start_time=datetime.datetime.now(datetime.timezone.utc),
        timeout=timeout,
    )

  @property
  def deadline(self) -> datetime.datetime:
    return self.start_time + self.timeout

  @property
  def expired(self) -> bool:
    return datetime.datetime.now(datetime.timezone.utc) > self.deadline

  @property
  def elapsed(self) -> datetime.timedelta:
    return datetime.datetime.now(datetime.timezone.utc) - self.start_time

  @property
  def remaining(self) -> datetime.timedelta:
    return self.deadline - datetime.datetime.now(datetime.timezone.utc)

  def prettyprint(self) -> str:
    return (
        f'Cooperative timeout expired after: {self.elapsed}, started at: '
        f'{self.start_time}, should have expired after {self.timeout}, at: '
        f'{self.deadline}'
    )


class CooperativeTimeoutError(TimeoutError):
  """Raised when a cooperative timeout deadline is exceeded."""

  def __init__(
      self,
      message: str = 'Deadline exceeded',
      expired_timeout: CooperativeTimeout | None = None,
  ) -> None:
    super().__init__(message)
    self.expired_timeout = expired_timeout


@dataclasses.dataclass(frozen=True, kw_only=True)
class DeadlineStatus:
  """Status returned by check_deadline()."""

  expired: bool
  remaining: datetime.timedelta | None


_cooperative_timeout_stack: contextvars.ContextVar[
    tuple[CooperativeTimeout, ...]
] = contextvars.ContextVar('cooperative_timeout_stack', default=())


@contextlib.contextmanager
def cooperative_timeout(
    timeout: datetime.timedelta | float | None,
) -> Iterator[CooperativeTimeout | None]:
  """Context manager for cooperative timeouts.

  When nested inside an existing active timeout, the effective deadline is
  clamped to the earlier of the parent and child deadlines so a nested scope
  can never extend or clear an outer deadline.

  Args:
    timeout: Duration in seconds or timedelta, or None for no additional limit.
  """
  stack = _cooperative_timeout_stack.get()
  parent = stack[-1] if stack else None
  if timeout is None:
    active = parent
  else:
    if isinstance(timeout, int | float):
      timeout = datetime.timedelta(seconds=float(timeout))
    child = CooperativeTimeout.from_timedelta(timeout)
    if parent is not None and parent.deadline < child.deadline:
      remaining = parent.deadline - child.start_time
      if remaining <= datetime.timedelta(0):
        child = parent
      else:
        child = CooperativeTimeout(
            start_time=child.start_time,
            timeout=remaining,
        )
    active = child

  if active is not None:
    new_stack = stack + (active,)
  else:
    new_stack = stack

  token = _cooperative_timeout_stack.set(new_stack)
  try:
    yield active
  finally:
    _cooperative_timeout_stack.reset(token)


timeout_context = cooperative_timeout


def get_timeout() -> CooperativeTimeout | None:
  """Returns the current cooperative timeout, or None if none is set."""
  stack = _cooperative_timeout_stack.get()
  return stack[-1] if stack else None


def check_deadline() -> DeadlineStatus:
  """Checks the active cooperative timeout deadline."""
  stack = _cooperative_timeout_stack.get()
  timeout = stack[-1] if stack else None
  if timeout is None:
    return DeadlineStatus(expired=False, remaining=None)
  return DeadlineStatus(expired=timeout.expired, remaining=timeout.remaining)


def maybe_timeout_cooperatively(outer_only: bool = False) -> None:
  """Raises CooperativeTimeoutError if the active timeout has expired."""
  stack = _cooperative_timeout_stack.get()
  if not stack:
    return
  timeout = stack[0] if outer_only else stack[-1]
  if timeout.expired:
    raise CooperativeTimeoutError(
        timeout.prettyprint(), expired_timeout=timeout
    )
