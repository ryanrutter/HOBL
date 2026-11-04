# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

"""Battery readings on Aluminium (Android desktop) DUTs, from "dumpsys battery"."""


def battery_values(dumpsys_output):
    '''Charge counter in uAh, voltage in mV, and whether a charger is connected.'''
    values = {}
    for line in dumpsys_output.splitlines():
        key, _, value = line.partition(":")
        values[key.strip()] = value.strip()
    powered = any(values.get(name) == "true" for name in ("AC powered", "USB powered", "Wireless powered", "Dock powered"))
    return int(values.get("Charge counter", "-1")), int(values.get("voltage", "-1")), powered


def average_power(start, end, seconds):
    '''Average current in mA and power in mW from two battery_values() readings taken seconds apart.'''
    (start_charge, start_mv, _), (end_charge, end_mv, _) = start, end
    hours = seconds / 3600.0
    current_ma = (start_charge - end_charge) / 1000.0 / hours
    power_mw = current_ma * (start_mv + end_mv) / 2.0 / 1000.0
    return current_ma, power_mw


def read(scenario):
    return battery_values(scenario._call(["dumpsys", "battery"], log_output=False, timeout=30))
