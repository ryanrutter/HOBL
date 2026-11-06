# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import core.app_scenario
import os
import utilities.open_source.aluminium_browser as browser
from . import default_params


class AlYoutube(core.app_scenario.Scenario):
    '''
    Plays the Tears of Steel YouTube video in Chrome, the Aluminium version of the Windows youtube scenario.

    It uses the same parameters as Windows: duration, loop_duration (the video restarts after this many seconds), and full_screen.  Playback is verified on the DUT: after each loop, Android's media session must report that Chrome is playing and that the video advanced by the loop duration.

    By default the live site is used, because YouTube's player pauses the web_replay recording in Chrome on Aluminium.  Set web_replay=1 to use the recording, the same as Windows, once that is resolved.
    '''
    default_params.run()

    prep_scenarios = ["al_web_prep"]

    def setUp(self):
        actions_json = os.path.join(os.path.dirname(__file__), "al_youtube.json")
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
        try:
            self._web_replay_kill()
        except Exception:
            pass
