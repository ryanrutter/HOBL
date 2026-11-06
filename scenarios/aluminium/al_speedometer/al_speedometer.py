# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import core.app_scenario
import os
import utilities.open_source.aluminium_browser as browser
from . import default_params


class AlSpeedometer(core.app_scenario.Scenario):
    '''
    Runs the Speedometer 3.1 browser benchmark in Chrome, the Aluminium version of the Windows speedometer scenario.  The score is written to speedometer_score.csv with the same metric name as Windows.
    '''
    default_params.run()

    def setUp(self):
        actions_json = os.path.join(os.path.dirname(__file__), "al_speedometer.json")
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
            browser.kill_all(self)
        except Exception:
            pass
