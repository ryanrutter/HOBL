# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import core.app_scenario
import os
import utilities.open_source.aluminium_office as office
import utilities.open_source.aluminium_browser as browser
from . import default_params


class AlAblStandby(core.app_scenario.Scenario):
    '''
    The standby part of the Windows ABL (all-day battery life) workload on an Aluminium (Android desktop) DUT: the Microsoft 365 apps are opened and the twelve web sites are loaded in Chrome, then the DUT sleeps for standby_duration with the screen off and is woken, and the apps are closed.  Steps and timings follow the Windows abl_standby scenario.

    Power is measured only while the DUT is in standby.  Without a power measurement device, the average standby current and power are calculated from the battery charge counter and written to standby_power.csv, as in al_standby.
    '''
    default_params.run()

    prep_scenarios = ['al_web_prep', 'al_productivity_prep']

    def setUp(self):
        # The DUT locks when it sleeps; unlock it before the Setup actions use the apps.
        if self.training_mode != '1':
            self._aluminium_unlock()
        actions_json = os.path.join(os.path.dirname(__file__), "al_abl_standby.json")
        self.actions = self.load_action_json(actions_json)
        setup_action = self._find_next_type("Setup", json=self.actions)
        if setup_action:
            self.run_actions(setup_action["children"])
        core.app_scenario.Scenario.setUp(self, callback_test_begin='')

    def runTest(self):
        self.run_actions(self._find_next_type("Run Test", json=self.actions)["children"])

    def tearDown(self):
        core.app_scenario.Scenario.tearDown(self, callback_test_end='')
        teardown_action = self._find_next_type("Teardown", json=self.actions)
        if teardown_action:
            self.run_actions(teardown_action["children"])

    def kill(self):
        try:
            browser.kill_all(self)
        except Exception:
            pass
        try:
            self._web_replay_kill()
        except Exception:
            pass
        try:
            office.kill_all(self)
        except Exception:
            pass
