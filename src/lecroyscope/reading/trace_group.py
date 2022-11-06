from __future__ import annotations

from os import PathLike

from .trace import Trace

from pathlib import Path
from glob import glob


class TraceGroup:
    def __init__(self, *args: str | PathLike[str] | Trace):
        self._traces = dict()

        for trace_or_init_argument in args:
            traces = [trace_or_init_argument]
            if not isinstance(trace_or_init_argument, Trace):
                path = Path(trace_or_init_argument)
                if "*" in str(path):
                    traces = [Trace(filename) for filename in glob(str(path))]
                else:
                    traces = [Trace(trace_or_init_argument)]

            for trace in traces:
                if trace.channel is None:
                    raise ValueError("Trace must have a channel number")

                if trace.channel in self._traces:
                    raise ValueError(
                        f"Channel {trace.channel} already exists in trace group"
                    )

                self._traces[trace.channel] = trace

        # sort by channel number
        self._traces = dict(sorted(self._traces.items()))

    def __iter__(self):
        for trace in self._traces.values():
            yield trace

    def __len__(self):
        return len(self._traces)

    def __getitem__(self, item: int) -> Trace:
        if item not in self._traces:
            raise KeyError(f"Trace group does not contain channel {item}")
        return self._traces[item]
