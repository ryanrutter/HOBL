# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Prep an Aluminium DUT before testing
##

import logging
import core.app_scenario
from core.parameters import Params

class AlProcessIdleTasks(core.app_scenario.Scenario):
    '''
    Runs pending background maintenance on an Aluminium (Android desktop) DUT so it will not be running during tests.  Android compiles installed apps in a background job after OS and app updates, similar to Windows idle tasks.  To ensure consistent results, please run this scenario at least once per day on devices before starting tests.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'timeout', '1800', desc="Maximum time in seconds the automation will wait for tasks to complete") # 30 minutes = 1800 sec, 2 hr = 7200 sec

    Params.setOverride("global", "prep_tools", "")
    is_prep = True
    hide_ui = False

    def runTest(self):
        timeout = int(Params.get(self.module, 'timeout'))
        logging.info("Running background app compilation, Timeout: " + str(timeout / 60) + " minutes")
        # Runs the background dexopt job immediately, instead of waiting for the device to be idle and charging.
        self._call(["cmd", "package bg-dexopt-job"], timeout=timeout)
        logging.info("al_process_idle_tasks complete")

    def tearDown(self):
        self.createPrepStatusControlFile()
        core.app_scenario.Scenario.tearDown(self)
