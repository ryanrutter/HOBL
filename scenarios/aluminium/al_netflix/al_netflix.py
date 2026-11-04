# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import core.app_scenario
import os
from . import default_params


class AlNetflix(core.app_scenario.Scenario):
    '''
    Watches a Netflix video in Chrome, the Aluminium version of the Windows netflix scenario: it signs in with netflix_username and netflix_password from the [netflix] section of the device profile if Chrome isn't signed in already, and plays the same title from the same position, full screen, for the specified duration.  Playback is verified with Android's media session at the start and end.  Unlike Windows, it doesn't sign out first:  Netflix may send a sign-in code to the account's email instead of asking for the password, which can't be automated.  If it does, sign in to Netflix once by hand in Chrome on the DUT.
    '''
    default_params.run()

    prep_scenarios = ["al_web_prep"]

    def setUp(self):
        actions_json = os.path.join(os.path.dirname(__file__), "al_netflix.json")
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
