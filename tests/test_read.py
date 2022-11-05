import pytest

from numpy.testing import assert_array_equal
from pathlib import Path
import numpy as np

import lecroyscope

from .test_header import header_reference_dict

files_path = Path(__file__).parent / "files"


def test_read_header():
    (
        header_header_only,
        trigger_times_header_only,
        values_header_only,
    ) = lecroyscope.reading.read(files_path / "header.trc", header_only=True)

    assert header_header_only == header_reference_dict

    header, trigger_times, values = lecroyscope.reading.read(
        files_path / "header.trc", header_only=False
    )

    assert header == header_header_only
    assert_array_equal(trigger_times, trigger_times_header_only)
    assert_array_equal(values, values_header_only)

    assert trigger_times.shape[0] == 2

    assert values.dtype in (np.int8, np.int16)


def test_read_header_from_bytes():
    filename = files_path / "header.trc"
    (
        header_from_file,
        trigger_times_from_file,
        values_from_file,
    ) = lecroyscope.reading.read(files_path / "header.trc", header_only=True)

    (
        header_from_bytes,
        trigger_times_from_bytes,
        values_from_bytes,
    ) = lecroyscope.reading.read(filename.read_bytes(), header_only=True)

    assert_array_equal(values_from_file, values_from_bytes)
    assert_array_equal(trigger_times_from_file, trigger_times_from_bytes)
    assert header_from_file == header_from_bytes
