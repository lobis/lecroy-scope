import pytest

from numpy.testing import assert_array_equal
import numpy as np
from pathlib import Path

import lecroyscope

from .test_header import header_reference_dict

files_path = Path(__file__).parent / "files"


def test_trace_header():
    filename = files_path / "header.trc"
    trace = lecroyscope.Trace(filename, header_only=True)
    assert dict(trace.header) == header_reference_dict


def test_trace_iter():
    filename = files_path / "header.trc"
    trace = lecroyscope.Trace(filename)

    # this header file is from a sequence of size 200
    assert len(trace) == 200

    data = np.array([(time, single) for time, single in trace])
    assert len(data) == len(trace)
    times = data[:, 0]
    voltage = data[:, 1]
    assert len(times) == len(voltage) == len(trace)

    # check all times are equal
    for time in times:
        assert_array_equal(time, times[0])


def test_trace_channel():
    filename = files_path / "header.trc"

    trace = lecroyscope.Trace(filename)
    assert trace.channel is None

    trace.channel = 2
    assert trace.channel == 2

    with pytest.raises(ValueError):
        trace.channel = 0

    trace = lecroyscope.Trace(filename, channel=3)
    assert trace.channel == 3


def test_trace_channel_from_filename_helper():
    assert (
        lecroyscope.reading._get_channel_trace_from_trc_filename("invalid.trc") is None
    )
    assert lecroyscope.reading._get_channel_trace_from_trc_filename(
        "C2Trace00001.trc"
    ) == (2, 1)
    assert lecroyscope.reading._get_channel_trace_from_trc_filename(
        "C3Trace01021.trc"
    ) == (3, 1021)
    assert lecroyscope.reading._get_channel_trace_from_trc_filename(
        "/this/is/ignored/C2Trace00001.trc"
    ) == (2, 1)
    assert (
        lecroyscope.reading._get_channel_trace_from_trc_filename("C3Tra1ce01021.trc")
        is None
    )
    assert (
        lecroyscope.reading._get_channel_trace_from_trc_filename("C3Trace01.trc")
        is None
    )


def test_trace_channel_from_filename(tmp_path):
    for filename, channel in [
        ("C2Trace00001.trc", 2),
        ("C3Trace01021.trc", 3),
        ("C4Trace01241.trc", 4),
        ("none.trc", None),
    ]:
        tmp_file = tmp_path / filename
        tmp_file.write_bytes((files_path / "header.trc").read_bytes())

        trace = lecroyscope.Trace(tmp_file)
        assert trace.channel == channel
