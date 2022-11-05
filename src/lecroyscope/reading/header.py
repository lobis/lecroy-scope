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


class Header:
    def __init__(self, header: dict):
        for name, _ in trc_description:
            setattr(self, f"_{name}", header[name])


# add header fields as properties
for (_name, _) in trc_description:
    setattr(
        Header,
        _name,
        property(lambda self, name=_name: self.__getattribute__(f"_{name}")),
    )
del _name
