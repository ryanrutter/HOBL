# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import core.app_scenario
import os
from . import default_params


class WebLiveMode(core.app_scenario.Scenario):
    default_params.run()

    def setUp(self):
        actions_json = os.path.join(os.path.dirname(__file__), "web_live_mode.json")
        self.actions = self.load_action_json(actions_json)
        core.app_scenario.Scenario.setUp(self)

    def runTest(self):
        self.run_actions(self.actions)

    def kill(self):
        return
