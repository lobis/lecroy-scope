import pytest

from .test_read import header_reference

import lecroyscope


def test_header_dict():
    header = lecroyscope.reading.Header(header_reference)
    header_as_dict = dict(header)
    assert header_as_dict == header_reference


def test_header_getitem():
    header = lecroyscope.reading.Header(header_reference)
    assert header["horiz_interval"] == header_reference["horiz_interval"]

    with pytest.raises(KeyError):
        header["does_not_exist"]
