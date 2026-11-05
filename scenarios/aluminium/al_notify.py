# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import core.app_scenario
from core.parameters import Params
from utilities.open_source.email_notify import send_plan_complete_email


class AlNotify(core.app_scenario.Scenario):
    '''Send the plan-completion email from the Windows HOBL host without contacting the Aluminium DUT.'''

    module = "notify"
    is_prep = True
    Params.setDefault(module, "plan_run_type", "")

    def setUp(self):
        return

    def runTest(self):
        send_plan_complete_email(Params.get(self.module, "plan_run_type"))

    def tearDown(self):
        return

    def kill(self):
        return 0
