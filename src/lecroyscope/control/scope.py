from __future__ import annotations

import vxi11
import ipaddress

from lecroyscope import Trace, TraceGroup


def _parse_response(response: str):
    if response.startswith("VBS "):
        response = response[4:]
    return response.strip()


def _set_command(parameter: str, value: str | int | float, return_value: bool = False):
    return_command = f"return = app.{parameter}" if return_value else ""
    return f"""VBS? \'app.{parameter} = "{value}"\n{return_command}\'"""


def _get_command(parameter: str):
    return f"VBS? 'return = app.{parameter}'"


class Scope:
    def __init__(self, ip_address: str):
        # validate ip address
        ip_address = str(ipaddress.ip_address(ip_address))
        self._instrument = vxi11.Instrument(ip_address)

    def __del__(self):
        self._instrument.close()

    def _ask(self, command: str):
        return _parse_response(self.instrument.ask(command))

    def get(self, parameter: str):
        return self._ask(_get_command(parameter))

    def set(self, parameter: str, value: str | int | float):
        return self._ask(_set_command(parameter, value, return_value=True))

    def acquire(self, timeout: float = 15.0, force: bool = False) -> bool:
        response = self._ask(
            f"VBS? 'return = app.Acquisition.acquire({timeout}, {force})'"
        )
        if response not in ["0", "1"]:
            raise ValueError(f"Unexpected response from scope: {response}")
        return bool(int(response))

    def read(self, *channels: int) -> Trace | TraceGroup:
        if len(channels) == 0:
            raise ValueError("At least one channel must be specified")
        traces = []
        for channel in channels:
            self.instrument.write(f"C{channel}:WF?")
            if len(channels) == 1:
                trace = Trace(self.instrument.read_raw())
                if trace.channel != channel:
                    raise ValueError(f"Unexpected channel: {trace.channel}")
                return trace
            traces.append(Trace(self.instrument.read_raw()))
        traces = TraceGroup(*traces)
        return traces

    @property
    def instrument(self):
        return self._instrument

    @property
    def id(self):
        return self.instrument.ask("*IDN?")

    @property
    def name_all(self):
        name_all = self._ask(_get_command("ExecsNameAll"))
        return name_all.split(",")

    @property
    def sample_mode(self):
        return self._ask(_get_command("Acquisition.Horizontal.SampleMode"))

    @sample_mode.setter
    def sample_mode(self, value: str):
        self._ask(_set_command("Acquisition.Horizontal.SampleMode", value))

    @property
    def num_segments(self):
        return int(self._ask(_get_command("Acquisition.Horizontal.NumSegments")))

    @num_segments.setter
    def num_segments(self, value: int):
        self._ask(_set_command("Acquisition.Horizontal.NumSegments", value))

    @property
    def trigger_mode(self):
        return self._ask(_get_command("Acquisition.TriggerMode"))

    @trigger_mode.setter
    def trigger_mode(self, value: str):
        trigger_modes = ["Stopped", "Single", "Normal", "Auto"]
        if value not in trigger_modes:
            raise ValueError(
                f"Invalid trigger mode: {value}. Valid trigger modes are: {trigger_modes}"
            )
        self._ask(_set_command("Acquisition.TriggerMode", value))
