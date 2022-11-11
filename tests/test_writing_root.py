import pytest
from pathlib import Path
import lecroyscope
from numpy.testing import assert_array_equal, assert_array_almost_equal
import numpy as np

uproot = pytest.importorskip("uproot")

files_path = Path(__file__).parent / "files"


def test_writing_tree(tmp_path):
    for file, multiply in zip(
        [
            files_path / "pulse.trc",
            files_path / "pulse_sequence.trc",
            files_path / "pulse_sequence.trc",
        ],
        [False, False, True],
    ):
        if not multiply:
            trace_group = lecroyscope.TraceGroup(lecroyscope.Trace(file, channel=2))
        else:
            trace_group = lecroyscope.TraceGroup(
                *[lecroyscope.Trace(file, channel=i + 1) for i in range(4)]
            )

        branches = lecroyscope.writing.root.get_tree_branch_definitions(trace_group)
        if not multiply:
            # get_tree_branch_definitions supports Trace or TraceGroup
            assert branches == lecroyscope.writing.root.get_tree_branch_definitions(
                next(trace_group)
            )
        tree_name = "t"
        uproot_file = tmp_path / "pulse.root"
        with uproot.recreate(uproot_file) as f:
            tree = f.mktree(
                tree_name,
                branches,
                "Tree",
            )
            data = lecroyscope.writing.root.get_tree_data(trace_group)
            tree.extend(data)

        with uproot.open(uproot_file) as f:
            tree = f[tree_name]
            times = tree["time"].array()
            voltages = {
                channel: tree[f"CH{channel:d}"].array()
                for channel in trace_group.channels
            }

        # check all times are equal
        for time in times:
            assert_array_equal(time, times[0])

        # not exactly equal
        assert_array_almost_equal(times[0], trace_group.time)

        for channel in trace_group.channels:
            trace = trace_group[channel]
            assert_array_almost_equal(
                np.array(voltages[channel]), trace.voltage.reshape((len(trace), -1))
            )
