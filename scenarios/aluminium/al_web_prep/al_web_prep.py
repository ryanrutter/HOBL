# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import core.app_scenario
import os
import utilities.open_source.aluminium_browser as browser
from . import default_params


class AlWebPrep(core.app_scenario.Scenario):
    '''
    Prepares the web browser (global:browser, Chrome or Edge) for Aluminium web workloads.  It dismisses the
    browser's first-run, sign-in, sync, notification, and default browser prompts without accepting them, then clears
    cached files only, preserving cookies, browsing history, passwords, and the signed-in test account.  For Edge, it
    also turns on Edge's "Enable command line on non-rooted devices" flag, so Edge trusts web_replay's certificates
    the same way as Chrome.
    '''
    default_params.run()

    is_prep = True

    def setUp(self):
        actions_json = os.path.join(os.path.dirname(__file__), "al_web_prep.json")
        self.actions = self.load_action_json(actions_json)
        setup_action = self._find_next_type("Setup", json=self.actions)
        if setup_action:
            self.run_actions(setup_action["children"])
        core.app_scenario.Scenario.setUp(self)

    def runTest(self):
        self.run_actions(self._find_next_type("Run Test", json=self.actions)["children"])
        self.createPrepStatusControlFile()

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
