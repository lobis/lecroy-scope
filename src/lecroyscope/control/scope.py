from __future__ import annotations

import vxi11
import ipaddress


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

    @property
    def instrument(self):
        return self._instrument

    def id(self):
        return self._instrument.ask("*IDN?")

    def name_all(self):
        return self._instrument.ask("VBS? 'return = app.ExecsNameAll'")

    def get(self, parameter: str):
        return self._instrument.ask(_get_command(parameter))

    def set(self, parameter: str, value: str | int | float):
        return self._instrument.ask(_set_command(parameter, value))
