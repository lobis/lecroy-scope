from __future__ import annotations
from functools import cached_property

import vxi11
import ipaddress

from lecroyscope import Trace, TraceGroup


# The following manual can be references for additional commands and documentation:
# https://cdn.teledynelecroy.com/files/manuals/automation_command_ref_manual_wm-wp.pdf


def _parse_response(response: str) -> str:
    if response.startswith("VBS "):
        response = response[4:]
    return response.strip()


def _set_command(
    parameter: str, value: str | int | float, return_value: bool = False
) -> str:
    return_command = f"return = app.{parameter}" if return_value else ""
    return f"""VBS? \'app.{parameter} = "{value}"\n{return_command}\'"""


def _get_command(parameter: str) -> str:
    return f"VBS? 'return = app.{parameter}'"


def _capitalize_first_letter(string: str) -> str:
    if len(string) == 0:
        return string
    return string[0].upper() + string.lower()[1:]


class Scope:
    def __init__(self, ip_address: str):
        # validate ip address
        ip_address = str(ipaddress.ip_address(ip_address))

        self._instrument = vxi11.Instrument(ip_address)
        self.timeout = 30.0

    def __del__(self):
        self._instrument.close()

    @property
    def timeout(self) -> float:
        """ " Returns instrument timeout in seconds"""
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: float):
        """ " Sets instrument timeout in seconds"""
        if timeout <= 0.0:
            raise ValueError("Scope timeout must be a positive floating point number")
        self._timeout = timeout
        self._instrument.timeout = self._timeout

    def _ask(self, command: str):
        return _parse_response(self.instrument.ask(command))

    def get(self, parameter: str):
        return self._ask(_get_command(parameter))

    def set(self, parameter: str, value: str | int | float):
        return self._ask(_set_command(parameter, value, return_value=True))

    def acquire(self, force: bool = False) -> bool:
        response = self._ask(
            f"VBS? 'return = app.Acquisition.acquire({self.timeout}, {force})'"
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
            trace = Trace(self.instrument.read_raw())
            if trace.channel != channel:
                raise ValueError(f"Unexpected channel: {trace.channel}")
            traces.append(trace)
        return traces[0] if len(traces) == 1 else TraceGroup(*traces)

    @property
    def instrument(self):
        return self._instrument

    @cached_property
    def id(self):
        return self.instrument.ask("*IDN?")

    @cached_property
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
        if _capitalize_first_letter(value) not in trigger_modes:
            raise ValueError(
                f"Invalid trigger mode: {value}. Valid trigger modes are: {trigger_modes}"
            )
        self._ask(_set_command("Acquisition.TriggerMode", value))

    def channel(self, channel: int) -> Channel:
        return Channel(scope=self, channel=channel)


class Channel:
    def __init__(self, scope: Scope, channel: int):
        self._scope = scope
        self.channel = channel

    def __str__(self):
        return f"C{self._channel:d}"

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value: int):
        if f"C{value:d}" not in self._scope.name_all:
            valid_channels = [
                c for c in self._scope.name_all if c.startswith("C") and len(c) == 2
            ]
            raise ValueError(
                f"""Invalid channel: {value}. Valid channels are: {valid_channels}"""
            )
        self._channel = value

    @property
    def vertical_scale(self) -> float:
        return float(
            self._scope._ask(_get_command(f"Acquisition.{str(self)}.VerScale"))
        )

    @vertical_scale.setter
    def vertical_scale(self, value: float) -> None:
        self._scope._ask(_set_command(f"Acquisition.{str(self)}.VerScale", value))

    @property
    def vertical_offset(self) -> float:
        return float(
            self._scope._ask(_get_command(f"Acquisition.{str(self)}.VerOffset"))
        )

    @vertical_offset.setter
    def vertical_offset(self, value: float) -> None:
        self._scope._ask(_set_command(f"Acquisition.{str(self)}.VerOffset", value))

    # TODO: add setter
    @property
    def vertical_coupling(self) -> str:
        return self._scope._ask(_get_command(f"Acquisition.{str(self)}.Coupling"))

    def read(self) -> Trace:
        return self._scope.read(self.channel)
