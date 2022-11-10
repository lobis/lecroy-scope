from __future__ import annotations

from os import PathLike
from pathlib import Path
import re
import numpy

from .file import read
from .header import Header


def _get_channel_trace_from_trc_filename(
    filename: str | PathLike[str],
) -> tuple[int, int] | None:
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

    channel = int(match.group(1))
    trace_number = int(match.group(2).lstrip("0"))
    return channel, trace_number


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
        else:
            if isinstance(filename_or_bytes, bytes):
                try:
                    channel_string = filename_or_bytes[0:5].decode("ascii")
                    regex = re.compile(r"C(\d):WF")
                    match = regex.match(channel_string)
                    if match:
                        self.channel = int(match.group(1))
                except UnicodeDecodeError:
                    pass
            else:
                # attempt to get channel number from filename
                channel_trace = _get_channel_trace_from_trc_filename(filename_or_bytes)
                if channel_trace is not None:
                    self.channel = channel_trace[0]

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
    def header(self) -> Header:
        return self._header

    @property
    def header_only(self) -> bool:
        return self._voltage.size == 0

    @property
    def sequence(self) -> bool:
        return self.header.sequence

    @property
    def channel(self) -> int:
        return self._channel

    @channel.setter
    def channel(self, value: int):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Channel number must be a positive integer (1, 2, 3, ...)")
        self._channel = value

    @property
    def voltage(self) -> numpy.ndarray:
        return self._voltage

    @property
    def trigger_times(self) -> numpy.ndarray:
        return self._trigger_times

    @property
    def time(self) -> numpy.ndarray:
        return self._time

    # Alternative names
    @property
    def x(self) -> numpy.ndarray:
        return self._time

    @property
    def y(self) -> numpy.ndarray:
        return self._voltage
