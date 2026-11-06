# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Idle with Teams in the background
#
# Setup instructions:
#   Run al_teams_prep
##

import logging
import time
import core.app_scenario
from core.parameters import Params
import utilities.open_source.aluminium_teams as teams


class AlTeams2Idle(core.app_scenario.Scenario):
    '''
    Teams is launched and then minimized to run in the background for the duration of the test, the Aluminium version of the Windows teams2_idle scenario.  As on Windows, Teams waits 5.5 minutes to reach its idle state before the measurement starts, and is left running afterwards.

    minimize_all=1 shows the home screen, the equivalent of minimizing all windows on Windows; with 0, Teams stays in front.  The Windows minimize_teams_only option isn't available, since the Android desktop has no shortcut to minimize one window.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'duration', '300', desc="Seconds to measure Teams idling in the background.")
    Params.setDefault(module, 'minimize_all', '1', desc="1 to show the home screen, minimizing all windows; 0 to leave Teams in front.", valOptions=['0', '1'])
    Params.setDefault(module, 'idle_wait', '330', desc="Seconds to wait for Teams to reach its idle state before measuring.")

    duration = Params.get(module, 'duration')
    minimize_all = Params.get(module, 'minimize_all')
    idle_wait = Params.get(module, 'idle_wait')

    prep_scenarios = ["al_teams_prep"]

    def setUp(self):
        # Call tool early callbacks, particularly to get video recording of the setup
        self.toolCallBacks("testBeginEarlyCallback")
        if self.training_mode != '1':
            self._aluminium_unlock()

        logging.debug("Starting Teams")
        teams.launch(self)
        time.sleep(10)
        teams.dismiss_prompts(self, teams.ui.read_ui(self))
        if not teams.is_signed_in(teams.ui.read_ui(self)):
            self.fail("Teams is not signed in.  Run al_teams_prep.")

        if self.minimize_all == '1':
            # Show the home screen, which minimizes all windows.
            self._call(["input", "keyevent KEYCODE_HOME"])

        # Long sleep to enter teams idle power period (5min + 30s for extra)
        logging.info(f"Waiting {float(self.idle_wait) / 60:.1f} minutes for Teams idle state to be achieved")
        time.sleep(float(self.idle_wait))

        # Base Class Call
        core.app_scenario.Scenario.setUp(self)

    def runTest(self):
        logging.info("Measuring idle for " + str(self.duration) + " seconds")
        time.sleep(float(self.duration))

    def tearDown(self):
        logging.info("Performing teardown.")
        # Call the test end callback to stop power recording.
        self._callback(Params.get('global', 'callback_test_end'))
        # Call base tearDown(), except for the callback_test_end, since that was called above.
        core.app_scenario.Scenario.tearDown(self, callback_test_end="")

    def kill(self):
        logging.debug("Closing Teams")
        try:
            teams.kill(self)
        except Exception:
            pass
        return 0
