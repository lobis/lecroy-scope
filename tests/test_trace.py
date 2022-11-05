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
