# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Idle on the desktop for JEITA battery life testing
#
# Setup instructions:
#   None.
##

import logging
import time
import core.app_scenario
from core.parameters import Params


class AlIdleDesktopJeita(core.app_scenario.Scenario):
    '''
    Idles on the Android desktop with all windows minimized, for JEITA battery life testing, the Aluminium version of the Windows idle_desktop_jeita scenario.  Windows sets the JEITA JB3_0 desktop image in its prep; Aluminium keeps the default wallpaper, since the Googlebook builds used for bring-up show the default wallpaper for the test user whatever is set.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'duration', '300', desc="Time to idle in seconds")

    duration = Params.get(module, 'duration')

    prep_scenarios = []

    def setUp(self):
        # Minimize any windows, like the Windows scenario, by showing the home screen.
        self._call(["input", "keyevent KEYCODE_HOME"])
        core.app_scenario.Scenario.setUp(self)

    def runTest(self):
        logging.info("Sleeping for " + self.duration)
        time.sleep(float(self.duration))
        if self.enable_screenshot == '1':
            self._screenshot(name="end_screen.png")

    def kill(self):
        return 0
