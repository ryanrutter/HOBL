# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import core.app_scenario
from core.parameters import Params
from utilities.open_source.aluminium_plan_runner import run_plans


class AlRunAblIfPrepsPassed(core.app_scenario.Scenario):
    '''Launch the Aluminium ABL rundown after its workload preps have completed.'''

    module = "run_abl_if_preps_passed"
    Params.setDefault(
        module,
        "prep_list",
        "al_abl_active al_web_prep al_productivity_prep al_lvp_prep",
        desc="Aluminium ABL prep scenarios to check.",
        multiple=True,
    )
    Params.setDefault(
        module,
        "plans_to_launch",
        "al_rundown_abl_lvp_web.ps1",
        desc="Aluminium ABL rundown plan to launch.",
        multiple=True,
    )
    prep_list = Params.get(module, "prep_list").split()
    plans_to_launch = Params.get(module, "plans_to_launch").split()
    is_prep = True

    def setUp(self):
        return

    def runTest(self):
        run_plans(self, self.prep_list, self.plans_to_launch)

    def tearDown(self):
        return

    def kill(self):
        return 0
