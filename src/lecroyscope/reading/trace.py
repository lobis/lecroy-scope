from os import PathLike

import numpy

from .file import read
from .header import Header


class Trace:
    def __init__(self, filename: str | PathLike[str], header_only: bool = False):
        self._filename = filename

        header, self._trigger_times, self._values = read(filename, header_only)

        if header_only:
            return

        # store values in voltage units
        self._values = self._values * header["vertical_gain"]
        self._values = self._values + header["vertical_offset"]

        # compute time values
        self._time = (
            numpy.arange(self._values.shape[-1]) * header["horiz_interval"]
            + header["horiz_offset"]
        )
        self._header = Header(header)

    @property
    def header(self):
        return self._header

    @property
    def header_only(self):
        return self._values is None

    @property
    def values(self):
        return self._values

    @property
    def trigger_times(self):
        return self._trigger_times

    @property
    def time(self):
        return self._time

    # Alternative names
    @property
    def x(self):
        return self.time

    @property
    def y(self):
        return self.values
