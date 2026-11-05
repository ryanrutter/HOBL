# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

"""Aluminium implementation of the Windows discharge scenario."""

import logging
import subprocess
import time

from core.parameters import Params
import core.app_scenario
import scenarios.windows.discharge


class AlDischarge(scenarios.windows.discharge.Discharge):
    '''
    Turns off the charger and waits for the battery to reach discharge:resume_threshold.
    Aluminium version of the Windows discharge scenario; optionally plays local video with al_lvp.  Configure
    global:charge_off_call or disconnect the charger manually; the scenario fails rather than waiting forever
    if the DUT is still on AC/USB power above the requested threshold.
    '''
    Params.setDefault(
        "discharge",
        "run_scenario",
        "",
        desc="Run al_lvp in the background while discharging.",
        valOptions=["lvp"],
    )

    def setUp(self):
        logging.info("Discharging...")
        if self.charge_off_call:
            self._host_call(self.charge_off_call)
        else:
            logging.warning("No charge_off_call is configured; disconnect the charger manually and keep it disconnected.")
        if not self.is_discharge_done() and self.getAluminiumPowerState() == 2:
            self.fail(
                "The DUT is still on AC/USB power.  Configure global:charge_off_call or disconnect the charger "
                "before running al_discharge."
            )
        core.app_scenario.Scenario.setUp(self)

    def getBattLevel(self):
        return self.getAluminiumBatt()

    def runTest(self):
        if self.is_discharge_done():
            return

        process = None
        workload = self.run_scenario.lower()
        if workload and workload != "lvp":
            self.fail(f"al_discharge supports only run_scenario=lvp on Aluminium, not {workload}.")
        if workload == "lvp":
            logging.info("Starting al_lvp while discharging.")
            process = subprocess.Popen(
                [
                    ".\\hobl.cmd",
                    "-p", self.params_file,
                    "-s", "al_lvp",
                    f"global:result_dir_complete={self.run_dir}",
                    "al_lvp:duration=14400",
                    "global:tools=",
                    "global:post_run_delay=0",
                ],
                stdin=subprocess.PIPE,
            )
            time.sleep(30)

        threshold = self.resume_threshold + self.taper_workload
        while not self.is_discharge_done(threshold):
            time.sleep(self.poll_period)

        if process:
            logging.info("Stopping al_lvp after reaching the discharge threshold.")
            if process.stdin is None:
                self.fail("Could not send teardown to the background al_lvp process.")
            process.stdin.write(b"teardown\n")
            process.stdin.flush()
            return_code = process.wait()
            if return_code != 0:
                self.fail(f"The background al_lvp process failed with exit code {return_code}.")

        if self.taper_workload > 0:
            logging.info("Workload tapered; continuing to discharge to resume_threshold.")
            while not self.is_discharge_done(self.resume_threshold):
                time.sleep(self.poll_period)

    def kill(self):
        if self.run_scenario.lower() == "lvp":
            subprocess.run([".\\hobl.cmd", "-p", self.params_file, "-k", "al_lvp"], check=False)
        return 0
