import pytest

import lecroyscope

header_reference_dict = {
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
    "trigger_time": "2022-10-13T16:29:38",
    "acq_duration": 0.0,
    "record_type": "single sweep",
    "processing_done": "no processing",
    "reserved5": 0,
    "ris_sweeps": 1,
    "time_base": "200 ns / div",
    "vert_coupling": "DC 50 Ohm",
    "probe_att": 1.0,
    "fixed_vert_gain": "1 V / div",
    "bandwidth_limit": 0,
    "vertical_vernier": 1.0,
    "acq_vert_offset": -0.949999988079071,
    "wave_source": 1,
}


def test_header_dict():
    header = lecroyscope.reading.Header(header_reference_dict)
    header_as_dict = dict(header)
    assert header_as_dict == header_reference_dict


def test_header_getitem():
    header = lecroyscope.reading.Header(header_reference_dict)
    assert header["horiz_interval"] == header_reference_dict["horiz_interval"]

    with pytest.raises(KeyError):
        header["does_not_exist"]


def test_header_string():
    header = lecroyscope.reading.Header(header_reference_dict)
    assert (
        str(header)
        == """Instrument name: LECROYWR64Xi-A
Trigger time: 2022-10-13T16:29:38
Vertical coupling: DC 50 Ohm
Time base: 200 ns / div
Horizontal interval: 9.999999717180685e-10
Horizontal offset: -2.2824463729809135e-07
Fixed vertical gain: 1 V / div
Vertical gain: 0.00012499500007834285
Vertical offset: -0.949999988079071
Wave array count: 400400
Subarray count: 200"""
    )
