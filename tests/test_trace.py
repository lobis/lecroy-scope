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


def test_read_trace_from_file():
    for filename, shape, length, sequence in zip(
        [
            files_path / "pulse.trc",
            files_path / "pulse_sequence.trc",
            files_path / "issue_1.trc",
        ],
        [(502,), (20, 502), (100002,)],
        [1, 20, 1],
        [False, True, False],
    ):
        trace = lecroyscope.Trace(filename)
        assert len(trace) == length
        assert trace.header_only is False
        assert trace.sequence == sequence
        assert trace.voltage.shape == shape
        assert trace.time.shape == shape[-1:]
        assert (trace.voltage.shape[-1],) == trace.time.shape

        if filename == files_path / "pulse.trc":
            # check voltage and time scaling is done properly
            # test against signal which consists of ~ 0V baseline + sharp pulse at trigger time
            # first bins should be ~ 0V since we are on the region before pulse
            assert pytest.approx(np.mean(trace.voltage[0:100])) == 0.0057997689768671985
            # time of max voltage value should be very close to trigger time (0 seconds)
            assert (
                pytest.approx(trace.time[np.argmax(trace.y)]) == 4.254989846811945e-09
            )


def test_trace_adc_values():
    filename = files_path / "pulse.trc"
    trace = lecroyscope.Trace(filename)

    adc_from_trace = trace.adc_values

    (
        _,
        _,
        adc_from_file,
    ) = lecroyscope.reading.read(filename)

    assert_array_equal(adc_from_file, adc_from_trace)
