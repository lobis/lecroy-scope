import mmap
from os import PathLike
import struct
import numpy
from io import BytesIO

from .header import trc_description


def read(
    filename_or_bytes: str | PathLike[str] | bytes, header_only: bool = False
) -> tuple[dict[str, str | int | float], numpy.ndarray | None, numpy.ndarray | None]:
    with open(filename_or_bytes, "r+b") if not isinstance(
        filename_or_bytes, bytes
    ) else BytesIO(filename_or_bytes) as f:

        wavedesc_bytes = b"WAVEDESC"
        # find "WAVEDESC" and skip those bytes
        if isinstance(filename_or_bytes, bytes):
            f.read(filename_or_bytes.find(wavedesc_bytes))
        else:
            # https://docs.python.org/3/library/mmap.html
            mm = mmap.mmap(f.fileno(), 0)
            f.read(mm.find(wavedesc_bytes))

        header = {
            name: f.read(struct.Struct(fmt).size) for (name, fmt) in trc_description
        }

        endianness = ">" if struct.unpack("h", header["comm_order"])[0] == 0 else "<"

        header = {
            name: struct.unpack(f"{endianness}{fmt}", header[name])[0]
            for (name, fmt) in trc_description
        }

        # format strings
        for name in header:
            if isinstance(header[name], bytes):
                header[name] = header[name].decode("ascii").strip("\x00")

        if not header_only:
            if header["user_text"] != 0:
                # skip user text
                f.read(header["user_text"])

            trigger_times = numpy.frombuffer(
                f.read(int(header["trig_time_array"])), dtype=numpy.float64
            )

            values_type = numpy.int8 if header["comm_type"] == 0 else numpy.int16
            values = numpy.frombuffer(
                f.read(int(header["wave_array_count"])), dtype=values_type
            )
        else:
            trigger_times = numpy.array([], dtype=numpy.float64)
            values = numpy.array([], dtype=numpy.float64)

        trigger_times = trigger_times.reshape((2, -1), order="F")
        if subarray_count := header["subarray_count"]:
            values = values.reshape((subarray_count, -1), order="C")

        return header, trigger_times, values
