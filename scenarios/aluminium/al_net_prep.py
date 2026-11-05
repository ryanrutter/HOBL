# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import re

import core.app_scenario
from core.parameters import Params


class AlNetPrep(core.app_scenario.Scenario):
    '''
    Validate the DUT's Wi-Fi connection against dut_wifi_name.  Changing networks over wireless ADB would disconnect
    the agent and can change dut_ip; join or switch networks over USB with dut_setup_aluminium.ps1 instead.
    '''

    module = "net_prep"
    Params.setDefault(module, "net_prep_enabled", "1")
    Params.setDefault(module, "connection", "Wi-Fi")
    Params.setOverride("global", "prep_tools", "")
    is_prep = True

    def runTest(self):
        if Params.get(self.module, "net_prep_enabled") != "1":
            logging.info("Aluminium network prep is disabled.")
            self.createPrepStatusControlFile()
            return
        connection = Params.get(self.module, "connection")
        if connection.lower() not in ("wi-fi", "wifi"):
            self.fail(f"Aluminium net_prep supports Wi-Fi only, not {connection}.")
        expected = Params.get("global", "dut_wifi_name")
        if not expected:
            logging.warning("dut_wifi_name is empty; skipping Wi-Fi name validation.")
            self.createPrepStatusControlFile()
            return

        status = self._call(["cmd", "wifi status"], expected_exit_code="", log_output=False)
        match = re.search(r'Wifi is connected to "([^"]+)"', status or "")
        actual = match.group(1) if match else ""
        if actual != expected:
            self.fail(
                f"The DUT is connected to {actual or 'no Wi-Fi network'}, not dut_wifi_name.  "
                "Changing Wi-Fi disconnects wireless ADB; connect the DUT by USB and run "
                "setup_src\\src_dut_aluminium\\dut_setup_aluminium.ps1 with the profile."
            )
        logging.info("Aluminium Wi-Fi is connected to the profile network.")
        self.createPrepStatusControlFile()
