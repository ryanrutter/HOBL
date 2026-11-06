# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Put the DUT into standby with the screen off
#
# Setup instructions:
#   For the Disconnected mode, set cs_floor:button_wake_callback to a host command that presses the DUT's
#   power button, since the HOBL host can't reach the DUT while its Wi-Fi is off.
##

import logging
import os
import time
import core.app_scenario
from core.parameters import Params
import utilities.open_source.aluminium_standby as standby


DISCONNECTED_SCRIPT = """sleep 3
input keyevent KEYCODE_SLEEP
svc wifi disable
until dumpsys power | grep -q 'mWakefulness=Awake'; do sleep 5; done
svc wifi enable
"""


class AlStandby(core.app_scenario.Scenario):
    '''
    Puts an Aluminium (Android desktop) DUT into standby with the screen off, the Aluminium version of the Windows standby scenario.  It uses the same cs_floor parameters: cs_duration, button_to_record_delay, connection, and the button callbacks.

    Without a power measurement device, the average standby current and power are calculated from the battery charge counter, read just before standby and just after waking, and written to standby_power.csv.  Run it on battery; the charge counter resolution is 1 mAh, so longer durations are more accurate.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault('cs_floor', 'cs_duration', '1200')
    Params.setDefault('cs_floor', 'button_to_record_delay', '900')
    Params.setDefault('cs_floor', 'button_sleep_callback', '')
    Params.setDefault('cs_floor', 'button_wake_callback', '')
    Params.setDefault('cs_floor', 'connection', 'Connected', desc="Connected or Disconnected from the network during standby", valOptions=["Disconnected", "Connected"])
    Params.setDefault(module, 'wake_timeout', '300', desc="Seconds to keep trying to wake the DUT after standby.")

    def setUp(self):
        self.cs_duration = float(Params.get('cs_floor', 'cs_duration'))
        self.record_delay = float(Params.get('cs_floor', 'button_to_record_delay'))
        self.button_sleep = Params.get('cs_floor', 'button_sleep_callback')
        self.button_wake = Params.get('cs_floor', 'button_wake_callback')
        self.connection = Params.get('cs_floor', 'connection')
        self.wake_timeout = float(Params.get(self.module, 'wake_timeout'))
        if self.connection == "Disconnected" and not self.button_wake:
            self.fail("cs_floor:connection=Disconnected needs cs_floor:button_wake_callback, since the HOBL host can't reach the DUT while its Wi-Fi is off.")
        core.app_scenario.Scenario.setUp(self)

    def runTest(self):
        start = standby.read_battery(self)
        if start[2]:
            logging.warning("The DUT is on AC power, so the standby power can't be calculated from the battery.")
        start_time = time.time()

        total = self.record_delay + self.cs_duration
        logging.info(f"Device sleep now, for {total:.0f} seconds ({self.record_delay:.0f} before measuring).")
        if self.connection == "Disconnected":
            # The host can't reach the DUT while its Wi-Fi is off, so the DUT sleeps, turns Wi-Fi off, and turns
            # it back on when it is woken, by itself.
            script = os.path.join(self.result_dir, "al_standby_disconnected.sh")
            with open(script, "w", newline="\n") as f:
                f.write(DISCONNECTED_SCRIPT)
            remote_dir = self.dut_exec_path + "/al_standby"
            self._upload(script, remote_dir)
            self._call(["sh", f"-c \"setsid nohup sh {remote_dir}/al_standby_disconnected.sh > /dev/null 2>&1 < /dev/null &\""])
        elif self.button_sleep:
            self._host_call(self.button_sleep)
        else:
            self._call(["input", "keyevent KEYCODE_SLEEP"], blocking=False)
        time.sleep(self.record_delay)
        self._callback(Params.get('global', 'callback_test_begin'))
        logging.info(f"Starting standby measurement for {self.cs_duration:.0f} seconds")
        time.sleep(self.cs_duration)
        self._callback(Params.get('global', 'callback_test_end'))

        self.wake()
        end = standby.read_battery(self)
        seconds = time.time() - start_time
        standby.write_power(self.result_dir, start, end, seconds)

    def wake(self):
        standby.wake(self, self.button_wake, self.wake_timeout)

    def kill(self):
        try:
            self._call(["input", "keyevent KEYCODE_WAKEUP"], timeout=20)
        except Exception:
            pass
        return 0
