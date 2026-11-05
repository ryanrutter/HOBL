# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import json

import core.app_scenario
from core.parameters import Params, get_hobl_version


class AlConfigCheck(core.app_scenario.Scenario):
    '''
    Run the Aluminium config-check script as a standalone prep and save Config.csv in the scenario results.
    The normal scenario lifecycle already runs this check automatically for measured workloads.
    '''

    module = "config_check"
    override_keys = [
        "Study Type", "Comments", "Hardware Version", "Hardware Type", "Screen Size (in)",
        "Blade", "Accessories", "RTC Reserve (%)", "Raw Data Location", "Device Name",
    ]
    for key in override_keys:
        Params.setDefault(module, key, "")

    Params.setOverride("global", "trace", "0")
    Params.setOverride("global", "config_check", "0")
    Params.setOverride("global", "callback_test_begin", "")
    Params.setOverride("global", "callback_test_end", "")
    Params.setOverride("global", "callback_data_ready", "")
    Params.setOverride("global", "tools", "")
    Params.setOverride("global", "prep_tools", "")

    is_prep = True

    def runTest(self):
        override = {key: Params.get(self.module, key) for key in self.override_keys}
        override["Hardware Version"] = override["Hardware Version"].upper()
        override["HOBL Version"] = get_hobl_version().strip()
        override["Study Type"] = Params.get("global", "study_type")
        override["Hardware Type"] = Params.get("global", "hardware_type")
        override["Screen Size (in)"] = Params.get("global", "screen_size")
        override["Device Name"] = Params.get("global", "dut_name")
        override_string = json.dumps(override).replace('"', "'")

        source = "utilities\\open_source\\config_check_aluminium.sh"
        self._upload(source, self.dut_exec_path, check_modified=True)
        destination = self.dut_exec_path + "/config_check_aluminium.sh"
        command = (
            f'-c "{destination} --prerun --logfile={self.dut_data_path}/Config '
            f'--override-string=\\\"{override_string}\\\""'
        )
        self._call(["sh", command])
        self.createPrepStatusControlFile()
