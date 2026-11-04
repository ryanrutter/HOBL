# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from builtins import *
import logging
import core.app_scenario
import time
from core.parameters import Params

# Just a simple test case for testing out infrastructure
# For collecting data and running tools, use the manual.py scenario

class AlTimer(core.app_scenario.Scenario):
    '''
    Delays for the specified duration on an Aluminium (Android desktop) DUT.  Useful for checking that the HOBL host and the Aluminium agent are set up correctly.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'duration', '1', desc="Seconds to delay.")

    def runTest(self):
        self.duration = Params.get(self.module, 'duration')
        logging.info("Delaying for " + self.duration + " seconds")
        time.sleep(float(self.duration))
