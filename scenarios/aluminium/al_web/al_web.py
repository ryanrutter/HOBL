# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import core.app_scenario
import os
from . import default_params


class AlWeb(core.app_scenario.Scenario):
    '''
    Runs the twelve default Windows web_replay sites in Chrome with the Windows web scenario's tab order, page timings, scrolling and searches.  Set web_workload to run a subset of the sites, the same as Windows.

    Scrolling uses Page Down and Page Up, which reach Chrome whatever its window size.  Steps Windows finds by image match (the Amazon search bar, the first Instagram reel and the YouTube quality menu) keep the same timing without the interaction.  YouTube's player pauses the recorded videos in Chrome on Aluminium, so the scenario only checks that archived video segments were delivered; use al_youtube for representative video playback.
    '''
    default_params.run()

    prep_scenarios = ["al_web_prep"]

    def setUp(self):
        actions_json = os.path.join(os.path.dirname(__file__), "al_web.json")
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
