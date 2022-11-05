# lecroy-scope

[![Build and Test](https://github.com/lobis/lecroy-scope/actions/workflows/build-test.yml/badge.svg)](https://github.com/lobis/lecroy-scope/actions/workflows/build-test.yml)

An unofficial Python package 🐍📦 to interface with Teledyne LeCroy oscilloscopes and read binary trace files (`*.trc`).

Currently only reading trace files is supported.

This package is based on
the [lecroy-reader](https://github.com/neago/lecroy-reader/blob/49c42a85c449013c1c48d154ae70192f172e32ba/lecroyreader)
project.

## Installation

Installation via `pip` is supported:

```bash
pip install .
```

## Usage

### Reading binary trace files (`*.trc`)

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
header_dict = dict(header)
print("Instrument name: ", header_dict["instrument_name"])
```

The trace data can be accessed via the `time` and `values` attributes:

```python
# time values
time = trace.time  # trace.x is an alias for trace.time

# channel voltage values
values = trace.values  # trace.y is an alias for trace.values
```
