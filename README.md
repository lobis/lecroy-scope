# lecroyscope

[![PyPI version](https://badge.fury.io/py/lecroyscope.svg)](https://badge.fury.io/py/lecroyscope)
[![Build and Test](https://github.com/lobis/lecroy-scope/actions/workflows/build-test.yml/badge.svg)](https://github.com/lobis/lecroy-scope/actions/workflows/build-test.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/lecroyscope)

## 🤔 What is this?

This is an unofficial Python package to interface with Teledyne LeCroy oscilloscopes and read binary trace
files (`*.trc`).

The parsing of `trc` files is based on
the [lecroy-reader](https://github.com/neago/lecroy-reader/blob/49c42a85c449013c1c48d154ae70192f172e32ba)
project.

## ⚠️ Disclaimer

The features of this package are based on my needs at the time of writing.
I have done very limited testing, using a single oscilloscope and a few trace files.

If you use this package, it is very possible you find a bug or some oversight.
You are encouraged to make a [pull request](https://github.com/lobis/lecroy-scope/pulls) or to create
an [issue](https://github.com/lobis/lecroy-scope/issues) to report a bug, to request additional features or to suggest
improvements.

## ⚙️ Installation

Installation via `pip` is supported.
To install the latest [published version](https://github.com/lobis/lecroy-scope/releases), run:

```bash
pip install lecroyscope
```

To install the package from source, including test dependencies, clone the repository and run:

```bash
pip install .[test]
```

## 👨‍💻 Usage

### 📖 Reading binary trace files (`*.trc`)

```python
from lecroyscope import Trace

trace = Trace("path/to/trace.trc")
```

Trace file header information can be accessed via the `header` attribute:

```python
header = trace.header

# properties can be accessed directly
print("Instrument name: ", header.instrument_name)

# or as python dict
print("Instrument name: ", header["instrument_name"])

# header can also be converted into a python dict
header_dict = dict(header)
print("Header keys: ", list(header_dict.keys()))
```

The trace data can be accessed via the `time`(`x`) and `voltage`(`y`) attributes:

```python
# time values
time = trace.time  # trace.x is an alias for trace.time

# channel voltage values
voltage = trace.voltage  # trace.y is an alias for trace.voltage
```

### 📟 Acquisition with LeCroy oscilloscope

```python
import lecroyscope

scope = lecroyscope.Scope("192.168.1.10")  # IP address of the scope

# print some info
print(f"Scope ID: {scope.id}")

# change to "Sequence" mode with 200 segments
scope.sample_mode = "Sequence"
scope.num_segments = 200
print(f"Sample mode: '{scope.sample_mode}' with {scope.num_segments} segments")

# acquire data with a single trigger, timout (fail) after 60 seconds
scope.acquire(timeout=60)

# Read channel 2 and 3 traces
# The data in the scope won't change until next acquisition
trace_channel2: lecroyscope.Trace = scope.read(2)
trace_channel3: lecroyscope.Trace = scope.read(3)

# Alternatively, it is recommended to use the TraceGroup class for reading multiple channels from the same trigger
trace_group: lecroyscope.TraceGroup = scope.read(2, 3)
trace_channel2 = trace_group[2]
trace_channel3 = trace_group[3]
time = trace_group.time  # time values are the same for all traces
```
