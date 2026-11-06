# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Check which account settings are present in the device profile
#
# Setup instructions:
#   Fill in the account keys in the device profile.  See profile_templates\aluminium.ini.
##

import logging
import core.app_scenario
from core.parameters import Params


# The profile keys each workload needs.  Key names match Windows where Windows has an equivalent.
ACCOUNT_REQUIREMENTS = {
    "wifi": [("global", "dut_wifi_name"), ("global", "dut_wifi_password")],
    "google": [("global", "google_account"), ("global", "google_password")],
    "microsoft": [("global", "msa_account"), ("global", "dut_password")],
    "netflix": [("netflix", "netflix_username"), ("netflix", "netflix_password")],
    "teams": [("global", "msa_account"), ("global", "dut_password"), ("teams", "access_key")],
}

# Teams uses teams_install:teams_msa_account and teams_msa_password instead of msa_account and dut_password when set.
TEAMS_ACCOUNT = [("teams_install", "teams_msa_account"), ("teams_install", "teams_msa_password")]

UNSET_VALUES = ("", "-1")


def _is_set(section, key):
    value = Params.get(section, key, log=False)
    return value is not None and str(value).strip() not in UNSET_VALUES


def missing_keys(workload):
    requirements = ACCOUNT_REQUIREMENTS[workload]
    if workload == "teams" and _is_set(*TEAMS_ACCOUNT[0]):
        requirements = TEAMS_ACCOUNT + [("teams", "access_key")]
    return [f"{section}:{key}" for section, key in requirements if not _is_set(section, key)]


def require_accounts(scenario, workload):
    missing = missing_keys(workload)
    if missing:
        scenario.fail(
            f"The device profile is missing {', '.join(missing)} for {workload}.  "
            "Add them to the profile; see profile_templates\\aluminium.ini."
        )


class AlAccountsCheck(core.app_scenario.Scenario):
    '''
    Reports which account settings are present in the device profile of an Aluminium (Android desktop) DUT, without showing their values.

    Use it after filling in the profile, to see which account-dependent scenarios can run.  The scenario fails if a workload listed in "required" is missing a setting.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'required', '', desc="Space-separated workloads whose settings must be present: " + ", ".join(ACCOUNT_REQUIREMENTS), multiple=True)

    is_prep = True

    def runTest(self):
        required = Params.get(self.module, 'required', log=False).split()
        unknown = [workload for workload in required if workload not in ACCOUNT_REQUIREMENTS]
        if unknown:
            self.fail("Unknown workloads in al_accounts_check:required: " + ", ".join(unknown))

        failed = []
        for workload in ACCOUNT_REQUIREMENTS:
            missing = missing_keys(workload)
            if missing:
                logging.info(f"{workload}:\tmissing {', '.join(missing)}")
                if workload in required:
                    failed.append(workload)
            else:
                logging.info(f"{workload}:\tset")

        if failed:
            self.fail("Required account settings are missing for: " + ", ".join(failed))

    def kill(self):
        return 0
