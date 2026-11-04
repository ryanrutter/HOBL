# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from core.app_scenario import Scenario
import logging
import os
import time
import utilities.open_source.aluminium_battery as battery


class Tool(Scenario):
    '''
    Aluminium only.  Measures the battery charge used during the test from the battery's charge counter, and calculates the average current and power.  Results are written to <test name>_battery_energy.csv.  This is a coarse alternative to a power measurement device: run on battery, and prefer tests of 10 minutes or more, since the charge counter resolution is about 1 mAh.
    '''
    module = __module__.split('.')[-1]

    def initCallback(self, scenario):
        self.scenario = scenario
        self.start = None
        self.end = None

    def testBeginCallback(self):
        if self.platform.lower() != "aluminium":
            logging.warning("The battery_energy tool is only supported on Aluminium.")
            return
        self.start = battery.read(self.scenario)
        self.start_time = time.time()
        if self.start[2]:
            logging.warning("battery_energy: the DUT is on AC power, so the power can't be calculated from the battery.")

    def testEndCallback(self):
        if self.start is None:
            return
        try:
            self.end = battery.read(self.scenario)
            self.end_time = time.time()
        except Exception as e:
            # The DUT may have shut down at the end of a rundown.
            logging.warning(f"battery_energy: could not read the battery at the end of the test: {e}")

    def dataReadyCallback(self):
        if self.start is None or self.end is None:
            return
        seconds = self.end_time - self.start_time
        charge_mah = (self.start[0] - self.end[0]) / 1000.0
        rows = [("battery_measured_duration_s", f"{seconds:.0f}"), ("battery_charge_used_mah", f"{charge_mah:.0f}")]
        if self.start[2] or self.end[2]:
            logging.info("battery_energy: on AC power, average power not reported.")
        elif seconds > 0:
            current_ma, power_mw = battery.average_power(self.start, self.end, seconds)
            rows += [("battery_avg_current_ma", f"{current_ma:.1f}"), ("battery_avg_power_mw", f"{power_mw:.0f}")]
            logging.info(f"battery_energy: {charge_mah:.0f} mAh in {seconds:.0f}s, average {current_ma:.1f} mA, {power_mw:.0f} mW")
        with open(os.path.join(self.scenario.result_dir, self.scenario.testname + "_battery_energy.csv"), "w") as f:
            for key, value in rows:
                f.write(f"{key},{value}\n")
