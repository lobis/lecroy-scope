# lecroyscope

[![Build and Test](https://github.com/lobis/lecroy-scope/actions/workflows/build-test.yml/badge.svg)](https://github.com/lobis/lecroy-scope/actions/workflows/build-test.yml)

## 🤔 What is this?

This is an unofficial Python package to interface with Teledyne LeCroy oscilloscopes and read binary trace
files (`*.trc`).

Currently only reading trace files is supported.

This package is based on
the [lecroy-reader](https://github.com/neago/lecroy-reader/blob/49c42a85c449013c1c48d154ae70192f172e32ba)
project.

## 🐞 Disclaimer

The features of this package are based on my needs at the time of writing.
I have done very limited testing, using a single oscilloscope and a few trace files.

If you use this package, it is very possible you find a bug or some oversight.
You are encouraged to make a [pull request](https://github.com/lobis/lecroy-scope/pulls) or to create
an [issue](https://github.com/lobis/lecroy-scope/issues) to report a bug, to request additional features or to suggest
improvements.

## 📦 Installation

Installation via `pip` is supported:

```bash
pip install .
```

## 👨‍💻 Usage

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
