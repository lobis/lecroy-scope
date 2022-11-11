import pytest
from pathlib import Path
import lecroyscope
from numpy.testing import assert_array_equal, assert_array_almost_equal

uproot = pytest.importorskip("uproot")

files_path = Path(__file__).parent / "files"


def test_writing_tree(tmp_path):
    pulse_file = files_path / "pulse_sequence.trc"
    trace = lecroyscope.Trace(pulse_file)
    trace.channel = 2

    branches = lecroyscope.writing.root.get_tree_branch_definitions(trace)

    tree_name = "t"
    uproot_file = tmp_path / "pulse.root"
    with uproot.recreate(uproot_file) as f:
        tree = f.mktree(
            tree_name,
            branches,
            "Tree",
        )
        data = lecroyscope.writing.root.get_tree_data(trace)
        tree.extend(data)

    print(uproot_file)

    with uproot.open(uproot_file) as f:
        tree = f[tree_name]
        times = tree["time"].array()
        voltages = tree["CH2"].array()

    # check all times are equal
    for time in times:
        assert_array_equal(time, times[0])
    time = times[0]

    # not exactly equal
    assert_array_almost_equal(time, trace.time)
    for voltage_from_file, voltage in zip(voltages, trace.voltage):
        assert_array_almost_equal(voltage_from_file, voltage)
