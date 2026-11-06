# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import core.app_scenario
import os
import utilities.open_source.aluminium_office as office
from . import default_params


class AlIdleApps(core.app_scenario.Scenario):
    '''
    Idles with the Microsoft 365 apps open and the twelve web sites loaded in Chrome, switching to each app in turn, the Aluminium version of the Windows idle_apps scenario.
    '''
    default_params.run()

    prep_scenarios = ['al_web_prep', 'al_productivity_prep']

    def setUp(self):
        # The DUT locks when it sleeps; unlock it before the Setup actions use the apps.
        if self.training_mode != '1':
            self._aluminium_unlock()
        actions_json = os.path.join(os.path.dirname(__file__), "al_idle_apps.json")
        self.actions = self.load_action_json(actions_json)
        setup_action = self._find_next_type("Setup", json=self.actions)
        if setup_action:
            self.run_actions(setup_action["children"])
        core.app_scenario.Scenario.setUp(self)

    def runTest(self):
        self.run_actions(self._find_next_type("Run Test", json=self.actions)["children"])

    def tearDown(self):
        core.app_scenario.Scenario.tearDown(self)
        teardown_action = self._find_next_type("Teardown", json=self.actions)
        if teardown_action:
            self.run_actions(teardown_action["children"])

    def kill(self):
        try:
            self._kill("com.android.chrome")
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
