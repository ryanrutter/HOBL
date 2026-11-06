# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from core.parameters import Params
import core.app_scenario
from utilities.open_source.aluminium_plan_runner import run_plans


class AlRunPlansIfPrepsPassed(core.app_scenario.Scenario):
    '''Launch Aluminium plans after the required preps have completed on the DUT.'''

    module = "run_plans_if_preps_passed"
    Params.setDefault(
        module,
        "prep_list",
        "al_abl_active al_standby al_lvp al_teams",
        desc="Aluminium scenarios whose prep scenarios must have completed before launching plans.",
        multiple=True,
    )
    Params.setDefault(
        module,
        "plans_to_launch",
        "al_hobl.ps1 al_hobl_etl.ps1",
        desc="Aluminium test plans to launch in order.",
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
