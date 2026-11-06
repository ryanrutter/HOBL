# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import core.app_scenario
import os
import utilities.open_source.aluminium_teams as teams
from . import default_params


class AlTeams(core.app_scenario.Scenario):
    '''
    A Teams call with bots on an Aluminium (Android desktop) DUT, the Aluminium version of the Windows teams scenario used by the teams2_* scenarios.  The bots meeting is created, maintained and removed on the host with the Windows Teams library code and the teams parameters (access_key, number_of_bots, duration, bots_send_video, ...); the DUT joins it in the Teams app with its camera and microphone set by send_video and send_audio.

    The Teams account (teams_install:teams_msa_account) is in one call at a time, so don't run Teams scenarios on two DUTs with the same account at once.  Sharing the DUT's screen (send_screen) and Teams call health and log collection are not available on Aluminium.
    '''
    default_params.run()

    prep_scenarios = ["al_teams_prep"]

    def setUp(self):
        # The DUT locks when it sleeps; unlock it before the Setup actions use the apps.
        if self.training_mode != '1':
            self._aluminium_unlock()
        actions_json = os.path.join(os.path.dirname(__file__), "al_teams.json")
        self.actions = self.load_action_json(actions_json)
        setup_action = self._find_next_type("Setup", json=self.actions)
        if setup_action:
            try:
                self.run_actions(setup_action["children"])
            except Exception:
                # The teardown that removes the bots doesn't run when setUp fails.
                teams.stop_meeting(self)
                raise
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
            teams.kill(self)
        except Exception:
            pass
        return 0
