# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import core.app_scenario
import os
from . import default_params


class WebClearCache(core.app_scenario.Scenario):
    default_params.run()

    def setUp(self):
        actions_json = os.path.join(os.path.dirname(__file__), "web_clear_cache.json")
        self.actions = self.load_action_json(actions_json)
        setup_action = self._find_next_type("Setup", json=self.actions)
        if setup_action:
            self.run_actions(setup_action["children"])
        core.app_scenario.Scenario.setUp(self)

    def runTest(self):
        runtest_action = self._find_next_type("Run Test", json=self.actions)
        if runtest_action:
            self.run_actions(runtest_action["children"])
            return

        setup_action = self._find_next_type("Setup", json=self.actions)
        teardown_action = self._find_next_type("Teardown", json=self.actions)
        if not setup_action and not teardown_action:
            self.run_actions(self.actions)

    def tearDown(self):
        core.app_scenario.Scenario.tearDown(self)
        teardown_action = self._find_next_type("Teardown", json=self.actions)
        if teardown_action:
            self.run_actions(teardown_action["children"])

    def kill(self):
        pass
