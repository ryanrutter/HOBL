# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Tool wrapper for audio control

from builtins import str
from builtins import *
from core.parameters import Params
from core.app_scenario import Scenario
import logging
import sys
import os
import re
import decimal


class Tool(Scenario):
    '''
    Set specified audio volume.
    '''
    module = __module__.split('.')[-1]

    # Set default parameters
    Params.setDefault(module, 'volume', 'Unknown')
    #Params.setDefault(module, 'mute', "False")

    # Get parameters
    volume = Params.get(module, 'volume')
    #mute = Params.get(module, 'mute')

    def initCallback(self, scenario):

        self.scenario = scenario
        if self.volume == "Unknown":
            logging.error("Could not resolve specified volume parameter.")
            self.fail("Could not resolve specified volume parameter.")

        self.set_vol = (decimal.Decimal(self.volume) / 100)
        
        if self.platform.lower() == "macos":
            self._call(["zsh", f"-c \"osascript -e 'set volume output volume {self.volume}'\""])
            logging.info("Audio volume set to: " + str(self.volume))
            return
        
        elif self.platform.lower() == "windows":

            # exists = os.path.isfile(self.dut_exec_path)
            exists = os.path.isfile(self.dut_exec_path + "\\audio_volume.ps1")
            if exists:
                pass
            else:
                self._upload("utilities\\open_source\\audio_volume.ps1", self.dut_exec_path)
            
            self._call(["powershell.exe ", self.dut_exec_path + "\\audio_volume.ps1 " +  str(self.set_vol)])
            logging.info("Audio volume set to: " + str(self.set_vol))
            return

        elif self.platform.lower() == "aluminium":
            # Media volume uses device specific steps, reported as "volume is <n> in range [<min>..<max>]".
            output = self._call(["cmd", "media_session volume --stream 3 --get"])
            match = re.search(r"in range \[(\d+)\.\.(\d+)\]", output)
            if not match:
                self.fail("Could not read media volume range: " + output)
            steps = round(int(match.group(2)) * float(self.volume) / 100)
            self._call(["cmd", f"media_session volume --stream 3 --set {steps}"])
            logging.info("Audio volume set to: " + str(self.volume) + "% (" + str(steps) + " of " + match.group(2) + " steps)")
            return

    def testBeginCallback(self):
        pass

    def testEndCallback(self):
        pass

    def dataReadyCallback(self):
        pass



