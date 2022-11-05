import mmap
from os import PathLike
import struct
import numpy
from io import BytesIO
from datetime import datetime

from .header import trc_description


def read(
    filename_or_bytes: str | PathLike[str] | bytes, header_only: bool = False
) -> tuple[dict[str, str | int | float], numpy.ndarray, numpy.ndarray]:
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
            name: struct.unpack(f"{endianness}{fmt}", header[name])
            for (name, fmt) in trc_description
        }

        for name in header:
            if name != "trigger_time":
                header[name] = header[name][0]
            else:
                trigger_time = reversed(header["trigger_time"][:-1])
                # convert seconds to integer (lose milliseconds)
                trigger_time = [int(t) for t in trigger_time]
                header[name] = datetime(*trigger_time).isoformat()

        # format strings
        for name in header:
            if isinstance(header[name], bytes):
                header[name] = header[name].decode("ascii").strip("\x00")

        # format some attributes in a more human-readable way
        # https://github.com/neago/lecroy-reader/blob/49c42a85c449013c1c48d154ae70192f172e32ba/lecroyreader/lecroy.py
        record_types = [
            "single sweep",
            "interleaved",
            "histogram",
            "graph",
            "filter coefficient",
            "complex",
            "extrema",
            "sequence obsolete",
            "centered RIS",
            "peak detect",
        ]
        header["record_type"] = record_types[header["record_type"]]

        processing_types = [
            "no processing",
            "fir filter",
            "interpolated",
            "sparsed",
            "autoscaled",
            "no result",
            "rolling",
            "cumulative",
        ]
        header["processing_done"] = processing_types[header["processing_done"]]

        vertical_couplings = [
            "DC 50 Ohm",
            "ground",
            "DC 1 MOhm",
            "ground",
            "AC 1 MOhm",
        ]
        header["vert_coupling"] = vertical_couplings[header["vert_coupling"]]
        time_base = header["time_base"]
        if time_base == 100:
            header["time_base"] = "external"
        else:
            value = [1, 2, 5, 10, 20, 50, 100, 200, 500][time_base % 9]
            prefix = ["p", "n", "μ", "m", "", "k"][time_base // 9]
            header["time_base"] = f"{value} {prefix}s / div"

        fixed_vert_gain = header["fixed_vert_gain"]
        value = [1, 2, 5, 10, 20, 50, 100, 200, 500][fixed_vert_gain % 9]
        prefix = ["μ", "m", "", "k"][fixed_vert_gain // 9]
        header["fixed_vert_gain"] = f"{value} {prefix}V / div"

        # if header only return empty arrays
        values_type = numpy.int8 if header["comm_type"] == 0 else numpy.int16
        if not header_only:
            if header["user_text"] != 0:
                # skip user text
                f.read(header["user_text"])

            trigger_times = numpy.frombuffer(
                f.read(int(header["trig_time_array"])), dtype=numpy.float64
            )

            values = numpy.frombuffer(
                f.read(int(header["wave_array_count"])), dtype=values_type
            )
        else:
            trigger_times = numpy.array([], dtype=numpy.float64)
            values = numpy.array([], dtype=values_type)

        trigger_times = trigger_times.reshape((2, -1), order="F")
        if (subarray_count := header["subarray_count"]) > 1:
            values = values.reshape((subarray_count, -1), order="C")

        return header, trigger_times, values
