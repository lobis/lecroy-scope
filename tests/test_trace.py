import pytest
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
    trace = lecroyscope.Trace(filename, header_only=True)

    # this header file is from a sequence of size 200
    assert len(trace) == 200

    data = np.array([(time, single) for time, single in trace])
    assert len(data) == len(trace)
    times = data[:, 0]
    values = data[:, 1]
    assert len(times) == len(values) == len(trace)