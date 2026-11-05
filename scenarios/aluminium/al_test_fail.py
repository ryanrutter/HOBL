# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import core.app_scenario


class AlTestFail(core.app_scenario.Scenario):
    '''Intentionally fail the scenario to validate failure reporting and plan continuation.'''

    def runTest(self):
        self.fail("Intentional Aluminium test failure.")

    def kill(self):
        return 0
