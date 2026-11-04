# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# al_recharge
#
# Aluminium version of the recharge scenario.  Uses the same parameters (recharge:resume_threshold,
# recharge:post_charge_delay, etc.) so test plans can be shared with Windows.
#
# Setup instructions:
#   Set up the charge_on_call and charge_off_call parameters in the device profile.
##

import scenarios.windows.recharge

class AlRecharge(scenarios.windows.recharge.Recharge):
    '''
    Turns on the device charger and waits until the battery reaches the recharge:resume_threshold level, then waits recharge:post_charge_delay seconds and turns off the charger.  Aluminium version of recharge.
    '''

    def getBattLevel(self):
        return self.getAluminiumBatt()

    def checkState(self):
        # Returns 1 for DC, 2 for AC.
        return self.getAluminiumPowerState()
