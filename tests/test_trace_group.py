import pytest

from pathlib import Path

import lecroyscope

files_path = Path(__file__).parent / "files"


def test_trace_group_from_files(tmp_path):
    filenames = []
    channels = [1, 2, 3, 4]
    for channel in channels:
        filename = f"C{channel}Trace00001.trc"
        tmp_file = tmp_path / filename
        tmp_file.write_bytes((files_path / "header.trc").read_bytes())
        filenames.append(tmp_file)

    # check glob works
    for trace_group in [
        lecroyscope.TraceGroup(*filenames),
        lecroyscope.TraceGroup(tmp_path / "C*Trace00001.trc"),
    ]:

        for i, trace in enumerate(trace_group):
            assert isinstance(trace, lecroyscope.Trace)
            # this checks sorting too! (glob order is not the same across platforms)
            assert trace.channel == channels[i]

        assert len(trace_group) == len(channels)

        for channel in channels:
            assert channel == trace_group[channel].channel
