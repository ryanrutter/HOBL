# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Disengage charger at beginning of scenario and re-engage when complete

# 4 specified functions
# Can't block duration of test
# Parameters specified in callback, like result_dir, scenario name?

from builtins import *
from core.parameters import Params
from core.app_scenario import Scenario
import logging
import time
from utilities.open_source.widgets import Widgets

class Tool(Scenario):
    '''
    Turn off charger before scenario, turn it on after.  Aluminium uses the configured host charger callbacks, or
    prompts the operator and waits for the DUT's Android battery state when those callbacks are empty.
    '''
    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'delay', '5')
    Params.setDefault(module, 'mode', 'DC') # DC or AC
    conn_timeout = False
    charge_on_done = True

    # Get parameters
    charge_on_call = Params.get('global', 'charge_on_call')
    charge_off_call = Params.get('global', 'charge_off_call')

    delay = Params.get(module, 'delay')
    mode = Params.get(module, 'mode')

    def initCallback(self, scenario):
        self.scenario = scenario
        self.conn_timeout = False
        self.charge_on_done = False
        self.aluminium = (Params.get('global', 'platform') or "").lower() == "aluminium"
        if self.mode == "AC":
            return
        # Disengage charging
        logging.info("Attempting to turn off charger...")
        if self.charge_off_call != "" and self.charge_off_call != None:
            self._host_call(self.charge_off_call)
            logging.info("Charger turned off.")
        else:
            logging.warning("No charge_off_call specified.")
            if self._use_manual_prompt():
                if self.aluminium:
                    self._manual_aluminium_charger_change(1)
                else:
                    self._host_call('utilities\\MsgPrompt.exe -WaitForDC')
                logging.info("Charger unplugged.")
        time.sleep(int(self.delay))

    def testBeginCallback(self):
        pass

    def testEndCallback(self):
        pass

    def dataReadyCallback(self):
        if not self.conn_timeout and not self.charge_on_done and self.mode != "AC":
            self._turn_on_charger()

    def testTimeoutCallback(self):
        if self.mode != "AC":
            self._turn_on_charger()
        self.conn_timeout = True

    def _use_manual_prompt(self):
        return self.aluminium or Params.get('global', 'local_execution') == '1'

    def _manual_aluminium_charger_change(self, expected_state):
        labels = {
            1: ("Disconnect Charger", "Disconnect the Aluminium DUT charger."),
            2: ("Connect Charger", "Connect the Aluminium DUT charger."),
        }
        title, message = labels[expected_state]
        widgets = Widgets()
        if Params.get("global", "dashboard_url"):
            widgets.about(title, message, break_callback=lambda: self.scenario.getAluminiumPowerState() == expected_state)
            return

        widgets.about(title, message + " Press Enter after changing the connection.")
        while self.scenario.getAluminiumPowerState() != expected_state:
            time.sleep(2)

    def _turn_on_charger(self):
        logging.info("Attempting to turn on charger...")
        if self.charge_on_call != "" and self.charge_on_call != None:
            self._host_call(self.charge_on_call)
            logging.info("Charger turned on.")
        else:
            logging.warning("No charge_on_call specified.")
            if self._use_manual_prompt():
                if self.aluminium:
                    self._manual_aluminium_charger_change(2)
                else:
                    self._host_call('utilities\\MsgPrompt.exe -WaitForAC')
                logging.info("Charger plugged in.")
        self.charge_on_done = True
    
    def cleanup(self):
        logging.debug("Cleanup")
        self.dataReadyCallback()
