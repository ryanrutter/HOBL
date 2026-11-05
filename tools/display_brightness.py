# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

"""Deprecated compatibility tool for setting display brightness."""

import logging
import re

from core.parameters import Params
from tools.display import Tool as DisplayTool


class Tool(DisplayTool):
    '''
    Deprecated compatibility tool.  Maps the display brightness slider percentage to the nits value specified by
    a scenario; on Aluminium it uses the display tool's calibrated display:nits_map and restores the original
    brightness when display_brightness:display_restore=1.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'brightness', '150nits')
    Params.setDefault(module, 'nits_map', '100nits:50% 150nits:65%')

    def initCallback(self, scenario):
        logging.warning("display_brightness is deprecated. Use the display tool instead.")
        self.scenario = scenario
        self.platform = Params.get('global', 'platform')
        self.brightness = Params.get(self.module, 'brightness')
        self.nits_map = Params.get(self.module, 'nits_map')

        if self.platform.lower() == "aluminium":
            # Aluminium's calibrated mapping lives in the shared display section.
            display_nits_map = Params.get("display", "nits_map")
            if display_nits_map and display_nits_map != "Unknown":
                self.nits_map = display_nits_map
            # Reuse display's saved-state, nits mapping, Android scaling, and restore logic.
            self._init_brightness(self.brightness, self.nits_map)
            return

        brightness_val = re.findall(r'\d+', self.brightness)[0]
        if "nits" in self.brightness:
            nits_table = {}
            for item in self.nits_map.split():
                nits, slider = item.split(":")
                nits_table[re.findall(r'\d+', nits)[0]] = re.findall(r'\d+', slider)[0]
            if brightness_val not in nits_table:
                raise ValueError(f"No slider mapping for {self.brightness}.")
            brightness_val = nits_table[brightness_val]
        logging.info("Display brightness set to: %s", brightness_val)

        if self.platform.lower() == "android":
            self._host_call(
                "adb -s " + self.dut_ip + ":5555 shell settings put system screen_brightness " + brightness_val,
                expected_exit_code="",
            )
        elif self.platform.lower() == "macos":
            self._call([self.dut_exec_path + "/brightness", str(int(brightness_val) / 100.0)])
        else:
            self._call(["cmd.exe", "/c Powercfg.exe -SETDCVALUEINDEX scheme_balanced SUB_VIDEO aded5e82-b909-4619-9949-f5d71dac0bcb " + brightness_val])
            self._call(["cmd.exe", "/c Powercfg.exe -SETACVALUEINDEX scheme_balanced SUB_VIDEO aded5e82-b909-4619-9949-f5d71dac0bcb " + brightness_val])
            self._call(["cmd.exe", "/c Powercfg.exe -SETACTIVE scheme_balanced"])

    def testBeginCallback(self):
        return

    def testEndCallback(self):
        if self.platform.lower() == "aluminium" and Params.get("display", "display_restore") == "1":
            self._restore_brightness()

    def dataReadyCallback(self):
        return
