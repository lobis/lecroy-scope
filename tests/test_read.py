from numpy.testing import assert_array_equal
import pytest
from pathlib import Path

import lecroyscope

files_path = Path(__file__).parent / "files"

header_reference = {
    "descriptor_name": "WAVEDESC",
    "template_name": "LECROY_2_3",
    "comm_type": 1,
    "comm_order": 1,
    "wave_descriptor": 346,
    "user_text": 0,
    "res_desc1": 0,
    "trig_time_array": 3200,
    "ris_time_array": 0,
    "res_array1": 0,
    "wave_array1": 800800,
    "wave_array2": 0,
    "res_array2": 0,
    "res_array3": 0,
    "instrument_name": "LECROYWR64Xi-A",
    "instrument_number": 50699,
    "trace_label": "",
    "reserved1": 7184,
    "reserved2": 6,
    "wave_array_count": 400400,
    "points_per_screen": 400000,
    "first_valid_point": 0,
    "last_valid_point": 400399,
    "first_point": 0,
    "sparsing_factor": 1,
    "segment_index": 0,
    "subarray_count": 200,
    "sweeps_per_acq": 1,
    "points_per_pair": 0,
    "pair_offset": 0,
    "vertical_gain": 0.00012499500007834285,
    "vertical_offset": -0.949999988079071,
    "max_value": 31745.0,
    "min_value": -32001.0,
    "nominal_bits": 8,
    "nom_subarray_count": 200,
    "horiz_interval": 9.999999717180685e-10,
    "horiz_offset": -2.2824463729809135e-07,
    "pixel_offset": -2.2800000000000008e-07,
    "vert_unit": "V",
    "horiz_unit": "S",
    "horiz_uncertainty": 9.999999960041972e-13,
    "trigger_time": 38.475715120000004,
    "acq_duration": 0.0,
    "record_type": 0,
    "processing_done": 0,
    "reserved5": 0,
    "ris_sweeps": 1,
    "time_base": 16,
    "vert_coupling": 0,
    "probe_att": 1.0,
    "fixed_vert_gain": 18,
    "bandwidth_limit": 0,
    "vertical_vernier": 1.0,
    "acq_vert_offset": -0.949999988079071,
    "wave_source": 1,
}


def test_read_header():
    (
        header_header_only,
        trigger_times_header_only,
        values_header_only,
    ) = lecroyscope.reading.read(files_path / "header.trc", header_only=True)

    assert header_header_only == header_reference

    header, trigger_times, values = lecroyscope.reading.read(
        files_path / "header.trc", header_only=False
    )

    assert header == header_header_only
    assert_array_equal(trigger_times, trigger_times_header_only)
    assert_array_equal(values, values_header_only)


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
