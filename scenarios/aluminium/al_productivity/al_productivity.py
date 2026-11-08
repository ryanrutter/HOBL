# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import core.app_scenario
import os
import utilities.open_source.aluminium_office as office
from . import default_params


class AlProductivity(core.app_scenario.Scenario):
    '''
    Runs the Windows productivity workload in the Microsoft 365 apps on an Aluminium (Android desktop) DUT: Outlook, Excel, Word, PowerPoint and OneNote are opened with the Windows documents, each app's task is run, and the apps are closed, with the same steps, typed text, timings and phases as Windows.

    Outlook attaches its picture and document instead of inserting them inline, and OneNote keeps the picture-insert time without inserting the picture, since OneNote for Android inserts pictures through its camera.  Windows image-matched clicks are taps on the apps' labelled controls.

    When Excel is skipped (the excel_skip parameter; by default on x86_64 DUTs with an Excel build that crashes when a workbook opens, an Office bug), each Excel step runs as idle time of the same length, a warning is logged, and excel_skipped is written to excel_skip.csv.  al_idle_apps, al_abl_active and al_abl_standby do the same.
    '''
    default_params.run()

    prep_scenarios = ['al_productivity_prep']

    def setUp(self):
        # The DUT locks when it sleeps; unlock it before the Setup actions use the apps.
        if self.training_mode != '1':
            self._aluminium_unlock()
        actions_json = os.path.join(os.path.dirname(__file__), "al_productivity.json")
        self.actions = self.load_action_json(actions_json)
        office.skip_excel_actions(self, self.actions)
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
            office.kill_all(self)
        except Exception:
            pass
