from __future__ import annotations

import uproot
import awkward
import numpy
from lecroyscope import Trace, TraceGroup


def get_tree_branch_definitions(trace_or_group: Trace | TraceGroup, **kwargs) -> dict:
    if isinstance(trace_or_group, TraceGroup):
        trace_group = trace_or_group
    elif isinstance(trace_or_group, Trace):
        trace_group = TraceGroup(trace_or_group)
    else:
        raise ValueError(
            "Input argument should be either 'lecroyscope.Trace' or 'lecroyscope.TraceGroup'"
        )
    if trace_group.time is None:
        raise ValueError(
            "Trace Group does not have unified time information (probably do not come from the same trigger)"
        )
    channels = {
        f"CH{trace.channel}": ("f4", (len(trace_group.time),)) for trace in trace_group
    }
    branches = {
        "time": ("f4", (len(trace_group.time),)),
        **channels,
        **kwargs,
    }

    return branches


def get_tree_extend_data(trace_or_group: Trace | TraceGroup, **kwargs):
    """
    Returns a dict which can be used as argument for the uproot tree extend method.
    The resulting dict will have one "time" entry and one channel entry "CHx" per channel with corresponding data
    Optionally kwargs can be used to set "additional" data which must be specified if it was also specified in the
    "get_tree_branch_definitions" method.

    For example:
    If we call `get_tree_branch_definitions(trace, some_data=float)`,
    then to get tree extend data we must call `get_tree_extend_data(trace, some_data=1.25)`.
    The value will be the same for all sequences of the trace (if is sequence).
    If you want different data for each sequence, you can always extend the result of this method invoked without kwargs
    """
    if isinstance(trace_or_group, TraceGroup):
        trace_group = trace_or_group
    elif isinstance(trace_or_group, Trace):
        trace_group = TraceGroup(trace_or_group)
    else:
        raise ValueError(
            "Input argument should be either 'lecroyscope.Trace' or 'lecroyscope.TraceGroup'"
        )

    channels = {
        f"CH{trace.channel}": trace.voltage.reshape((trace_group.trace_length, -1))
        for trace in trace_group
    }

    kwargs = {
        key: numpy.array(trace_group.trace_length * [value])
        for key, value in kwargs.items()
    }

    return {
        "time": numpy.array(trace_group.trace_length * [trace_group.time]).reshape(
            (trace_group.trace_length, -1)
        ),
        **channels,
        **kwargs,
    }
