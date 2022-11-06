from __future__ import annotations

from os import PathLike

from .trace import Trace


class TraceGroup:
    def __init__(self, *args: str | PathLike[str] | Trace):
        self._traces = dict()

        for trace_or_init_argument in args:
            trace = trace_or_init_argument
            if not isinstance(trace_or_init_argument, Trace):
                trace = Trace(trace_or_init_argument)

            if trace.channel is None:
                raise ValueError("Trace must have a channel number")

            if trace.channel in self._traces:
                raise ValueError(
                    f"Channel {trace.channel} already exists in trace group"
                )

            self._traces[trace.channel] = trace

    def __iter__(self):
        for trace in self._traces.values():
            yield trace

    def __len__(self):
        return len(self._traces)

    def __getitem__(self, item: int) -> Trace:
        if item not in self._traces:
            raise KeyError(f"Trace group does not contain channel {item}")
        return self._traces[item]
