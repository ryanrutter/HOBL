# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Standby helpers for Aluminium (Android desktop) scenarios: wake the DUT and report the standby power calculated
# from the battery charge counter.

import logging
import os
import time
from utilities.open_source.aluminium_battery import average_power, battery_values


def read_battery(scenario):
    '''Returns the battery_values() tuple, read just before standby or just after waking.'''
    return battery_values(scenario._call(["dumpsys", "battery"], log_output=False))


def wake(scenario, button_wake="", timeout=300):
    '''Wakes the DUT and unlocks it.  A network request wakes the DUT in connected standby; the wake key turns the
    screen on.  button_wake is an optional host command that presses the DUT's power button.'''
    if button_wake:
        scenario._host_call(button_wake)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            scenario._call(["input", "keyevent KEYCODE_WAKEUP"], timeout=20)
            state = scenario._call(["sh", "-c \"dumpsys power | grep -m1 mWakefulness=\""], timeout=20)
            if "Awake" in state:
                logging.info("The DUT is awake.")
                # With a screen lock PIN, the DUT wakes to the lock screen.
                scenario._aluminium_unlock()
                return
        except Exception as e:
            logging.debug(f"DUT not reachable yet: {e}")
        time.sleep(10)
    scenario.fail(f"The DUT did not wake up within {timeout:.0f} seconds after standby.")


def write_power(result_dir, start, end, seconds):
    '''Writes standby_power.csv with the charge used and, on battery, the average current and power.'''
    current_ma, power_mw = average_power(start, end, seconds)
    logging.info(f"Standby: {seconds:.0f}s, {(start[0] - end[0]) / 1000.0:.0f} mAh, average {current_ma:.1f} mA, {power_mw:.0f} mW")
    with open(os.path.join(result_dir, "standby_power.csv"), "w") as f:
        f.write(f"standby_duration_s,{seconds:.0f}\n")
        f.write(f"standby_charge_used_mah,{(start[0] - end[0]) / 1000.0:.0f}\n")
        if not start[2] and not end[2]:
            f.write(f"standby_avg_current_ma,{current_ma:.2f}\n")
            f.write(f"standby_avg_power_mw,{power_mw:.1f}\n")
