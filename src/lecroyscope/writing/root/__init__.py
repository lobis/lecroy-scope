from __future__ import annotations

import uproot
import awkward
import numpy
from lecroyscope import Trace, TraceGroup


def get_tree_branch_definitions(
    trace_or_group: Trace | TraceGroup, additional_branches: dict = None
) -> dict:
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
    }
    if additional_branches is not None:
        for key in additional_branches.keys():
            if not isinstance(key, str):
                raise ValueError(f"key '{key}' should be a 'str'")
        branches = {**branches, **additional_branches}
    return branches


def get_tree_data(trace_or_group: Trace | TraceGroup):
    if isinstance(trace_or_group, TraceGroup):
        trace_group = trace_or_group
    elif isinstance(trace_or_group, Trace):
        print("creating trace group")
        trace_group = TraceGroup(trace_or_group)
        print("finished trace group")
    else:
        raise ValueError(
            "Input argument should be either 'lecroyscope.Trace' or 'lecroyscope.TraceGroup'"
        )

    channels = {
        f"CH{trace.channel}": trace.voltage.reshape((trace_group.trace_length, -1))
        for trace in trace_group
    }
    return {
        "time": numpy.array(trace_group.trace_length * [trace_group.time]).reshape(
            (trace_group.trace_length, -1)
        ),
        **channels,
    }
