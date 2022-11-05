from os import PathLike

import numpy

from .file import read
from .header import Header


class Trace:
    def __init__(
        self, filename_or_bytes: str | PathLike[str] | bytes, header_only: bool = False
    ):

        self._filename = (
            filename_or_bytes if not isinstance(filename_or_bytes, bytes) else ""
        )

        header, self._trigger_times, self._voltage = read(
            filename_or_bytes, header_only
        )
        self._header = Header(header)

        # store values in voltage units
        self._voltage = self._voltage * self._header["vertical_gain"]
        self._voltage = self._voltage + self._header["vertical_offset"]

        # compute time values
        self._time = (
            numpy.arange(self._voltage.shape[-1]) * self._header["horiz_interval"]
            + self._header["horiz_offset"]
        )

    def __len__(self):
        if not self._header.sequence:
            return 1
        return len(self._voltage)

    def __iter__(self):
        if len(self) == 1:
            yield self._time, self._voltage
        else:
            for single in self._voltage:
                yield self._time, single

    @property
    def header(self):
        return self._header

    @property
    def header_only(self):
        return self._voltage.size == 0

    @property
    def voltage(self):
        return self._voltage

    @property
    def trigger_times(self):
        return self._trigger_times

    @property
    def time(self):
        return self._time

    # Alternative names
    @property
    def x(self):
        return self._time

    @property
    def y(self):
        return self._voltage
