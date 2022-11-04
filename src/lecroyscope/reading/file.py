import mmap
from os import PathLike
import struct
import numpy
from io import BytesIO

# description from
# https://github.com/neago/lecroy-reader/blob/49c42a85c449013c1c48d154ae70192f172e32ba/lecroyreader/lecroy.py#L4
trc_description = (
    ("descriptor_name", "16s"),
    ("template_name", "16s"),
    ("comm_type", "h"),
    ("comm_order", "h"),
    ("wave_descriptor", "i"),
    ("user_text", "i"),
    ("res_desc1", "i"),
    ("trig_time_array", "i"),
    ("ris_time_array", "i"),
    ("res_array1", "i"),
    ("wave_array1", "i"),
    ("wave_array2", "i"),
    ("res_array2", "i"),
    ("res_array3", "i"),
    ("instrument_name", "16s"),
    ("instrument_number", "i"),
    ("trace_label", "16s"),
    ("reserved1", "h"),
    ("reserved2", "h"),
    ("wave_array_count", "i"),
    ("points_per_screen", "i"),
    ("first_valid_point", "i"),
    ("last_valid_point", "i"),
    ("first_point", "i"),
    ("sparsing_factor", "i"),
    ("segment_index", "i"),
    ("subarray_count", "i"),
    ("sweeps_per_acq", "i"),
    ("points_per_pair", "h"),
    ("pair_offset", "h"),
    ("vertical_gain", "f"),
    ("vertical_offset", "f"),
    ("max_value", "f"),
    ("min_value", "f"),
    ("nominal_bits", "h"),
    ("nom_subarray_count", "h"),
    ("horiz_interval", "f"),
    ("horiz_offset", "d"),
    ("pixel_offset", "d"),
    ("vert_unit", "48s"),
    ("horiz_unit", "48s"),
    ("horiz_uncertainty", "f"),
    ("trigger_time", "dbbbbhh"),
    ("acq_duration", "f"),
    ("record_type", "h"),
    ("processing_done", "h"),
    ("reserved5", "h"),
    ("ris_sweeps", "h"),
    ("time_base", "h"),
    ("vert_coupling", "h"),
    ("probe_att", "f"),
    ("fixed_vert_gain", "h"),
    ("bandwidth_limit", "h"),
    ("vertical_vernier", "f"),
    ("acq_vert_offset", "f"),
    ("wave_source", "h"),
)


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

        if header_only:
            return header, None, None

        if header["user_text"] != 0:
            # skip user text
            f.read(header["user_text"])

        trigger_times = numpy.frombuffer(
            f.read(int(header["trig_time_array"])), dtype=numpy.float64
        ).reshape((2, -1), order="F")

        values_type = numpy.int8 if header["comm_type"] == 0 else numpy.int16
        values = numpy.frombuffer(
            f.read(int(header["wave_array_count"])), dtype=values_type
        ).reshape((header["subarray_count"], -1), order="C")

        return header, trigger_times, values
