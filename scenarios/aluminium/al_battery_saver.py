# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Turn Android's Battery Saver on or off
#
# Setup instructions:
#   None.
##

import logging
import time
import core.app_scenario
from core.parameters import Params
from utilities.open_source.aluminium_battery import battery_values


class AlBatterySaver(core.app_scenario.Scenario):
    '''
    Turns Android's Battery Saver on (state=1) or off (state=0) on an Aluminium (Android desktop) DUT, the Aluminium version of the Windows energy_saver scenario.  No restart is needed on Android.

    Android doesn't run Battery Saver while the DUT is charging.  On AC power, state=1 sets Battery Saver to turn on when the charger is disconnected, and keeps it on after a full charge, so measurements on battery run with it.  The scenario checks the setting took effect, and fails if not.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'state', '0', desc="1 to turn Battery Saver on, 0 to turn it off.", valOptions=['0', '1'])
    Params.setOverride("global", "prep_tools", "")

    state = Params.get(module, 'state')
    is_prep = True

    def runTest(self):
        on_ac = battery_values(self._call(["dumpsys", "battery"], log_output=False))[2]
        if self.state == "1":
            # Android turns a sticky Battery Saver off after charging above 90% unless this is off.
            self._call(["settings", "put global low_power_sticky_auto_disable_enabled 0"])
            if on_ac:
                # Battery Saver can only be turned on while unplugged, so Android is told the charger is disconnected
                # for a moment.  It then stays set ("sticky") and turns on whenever the DUT is on battery.
                try:
                    self._call(["cmd", "battery unplug"])
                    self._call(["cmd", "power set-mode 1"])
                finally:
                    self._call(["cmd", "battery reset"])
                time.sleep(2)
                if self.setting("low_power_sticky") != "1":
                    self.fail("Battery Saver could not be set to turn on when the charger is disconnected.")
                logging.info("The DUT is charging; Battery Saver will turn on when the charger is disconnected.")
            else:
                self._call(["cmd", "power set-mode 1"])
                time.sleep(2)
                if self.setting("low_power") != "1":
                    self.fail("Battery Saver did not turn on.")
                logging.info("Battery Saver is on.")
        else:
            self._call(["cmd", "power set-mode 0"])
            self._call(["settings", "put global low_power_sticky 0"])
            self._call(["settings", "delete global low_power_sticky_auto_disable_enabled"], expected_exit_code="")
            time.sleep(2)
            if self.setting("low_power") != "0" or self.setting("low_power_sticky") == "1":
                self.fail("Battery Saver did not turn off.")
            logging.info("Battery Saver is off.")

    def setting(self, name):
        return self._call(["settings", f"get global {name}"], expected_exit_code="").strip()

    def kill(self):
        try:
            # Never leave Android thinking the charger is disconnected.
            self._call(["cmd", "battery reset"], expected_exit_code="")
        except Exception:
            pass
        return 0
