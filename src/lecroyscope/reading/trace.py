from __future__ import annotations

from os import PathLike
from pathlib import Path
import re
import numpy

from .file import read
from .header import Header


def _get_channel_from_trc_filename(filename: str | PathLike[str]) -> int | None:
    """
    Get channel number from trc filename.
    trc files follow the pattern 'C{n}Trace{NNNNNN}.trc' where n is the channel number and NNNNNN is the trace number.
    If the filename does not follow this pattern, None is returned.
    """

    # get filename from path
    filename = Path(filename).name

    regex = re.compile(r"C(\d)Trace(\d\d\d\d\d).trc")
    match = regex.match(filename)

    if match is None:
        return None

    return int(match.group(1))


class Trace:
    def __init__(
        self,
        filename_or_bytes: str | PathLike[str] | bytes,
        header_only: bool = False,
        channel: int | None = None,
    ):

        self._filename = (
            filename_or_bytes if not isinstance(filename_or_bytes, bytes) else ""
        )

        self._channel = None
        if channel:
            self.channel = channel
        elif not isinstance(filename_or_bytes, bytes):
            # attempt to get channel number from filename
            channel = _get_channel_from_trc_filename(filename_or_bytes)
            if channel is not None:
                self.channel = channel

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
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value: int):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Channel number must be a positive integer (1, 2, 3, ...)")
        self._channel = value

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
