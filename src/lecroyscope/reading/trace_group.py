from __future__ import annotations

from os import PathLike

import numpy

from pathlib import Path
from glob import glob

from .trace import Trace


class TraceGroup:
    def __init__(self, *args: str | PathLike[str] | Trace | bytes) -> None:
        self._traces = dict()
        for arg in args:
            traces = []
            if isinstance(arg, Trace):
                traces = [arg]
            elif isinstance(arg, bytes):
                trace = Trace(arg)
                if trace.channel is None:
                    raise ValueError(
                        "Trace group cannot be constructed from bytes without channel number"
                    )
                traces.append(trace)
            else:
                # is pathlike string
                path = Path(arg)
                if "*" in str(path):
                    traces = [Trace(filename) for filename in glob(str(path))]
                else:
                    traces = [Trace(arg)]

            for trace in traces:
                if trace.channel is None:
                    raise ValueError("Trace must have a channel number")

                if trace.channel in self._traces:
                    raise ValueError(
                        f"Channel {trace.channel} already exists in trace group"
                    )

                self._traces[trace.channel] = trace

        if len(self._traces) == 0:
            raise ValueError("Trace group must contain at least one trace")
        # sort by channel number
        self._traces = dict(sorted(self._traces.items()))

    def __iter__(self):
        for trace in self._traces.values():
            yield trace

    def __next__(self):
        return next(iter(self._traces.values()))

    def __len__(self) -> int:
        return len(self._traces)

    def __getitem__(self, item: int) -> TraceGroup | Trace:
        if isinstance(item, slice):
            # when slicing, return do not use channel number as key
            return TraceGroup(*list(self._traces.values())[item])
        if item not in self._traces:
            raise KeyError(f"Trace group does not contain channel {item}")
        return self._traces[item]

    @property
    def channels(self) -> list[int]:
        return list(self._traces.keys())

    @property
    def time(self) -> numpy.ndarray | None:
        """
        Returns the time vector of the traces if they are all equal, otherwise return None
        """
        t = next(iter(self._traces.values())).time
        for trace in self[1:]:
            diff = numpy.abs(trace.time - t)
            if numpy.any(diff > 1e-12):
                return None
        return t

    @property
    def x(self) -> numpy.ndarray | None:
        return self.time
