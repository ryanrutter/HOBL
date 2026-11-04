# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Make sure the Googlebook is signed in to its Google test account
#
# Setup instructions:
#   Set google_account and google_password in the device profile.
##

import logging
import time
import core.app_scenario
from core.parameters import Params
import utilities.open_source.aluminium_ui as ui
from scenarios.aluminium.al_accounts_check import missing_keys


def google_accounts(dumpsys_output):
    '''The Google account names in "dumpsys account" output.'''
    names = []
    for line in dumpsys_output.splitlines():
        line = line.strip()
        if line.startswith("Account {name=") and "type=com.google}" in line:
            names.append(line[len("Account {name="):].split(",", 1)[0].strip())
    return names


class AlGoogleAccountPrep(core.app_scenario.Scenario):
    '''
    Makes sure the active Android user of an Aluminium (Android desktop) DUT is signed in to the Google test account in google_account, the equivalent of msa_prep on Windows.  If the account is missing, it signs in with google_account and google_password.  Google may ask for extra verification for a new sign-in; the scenario then fails with instructions, since that needs a person.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'signin_timeout', '120', desc="Seconds to wait for each Google sign-in screen.")

    is_prep = True

    def runTest(self):
        account = (Params.get('global', 'google_account', log=False) or "").strip()
        accounts = google_accounts(self._call(["dumpsys", "account"], log_output=False))

        if not account:
            if accounts:
                logging.info("google_account is not set; the DUT is signed in to a Google account, so it is kept.")
                self.createPrepStatusControlFile()
                return
            self.fail("The DUT isn't signed in to a Google account, and google_account isn't set in the device profile.  Set google_account and google_password, or sign in on the DUT.")

        if account.lower() in (name.lower() for name in accounts):
            logging.info("The DUT is signed in to the Google test account.")
            self.createPrepStatusControlFile()
            return

        if missing_keys("google"):
            self.fail("The Google test account isn't signed in on the DUT, and google_password isn't set in the device profile.")
        logging.info("Signing in to the Google test account.")
        self.sign_in(account, Params.get('global', 'google_password', log=False))

        accounts = google_accounts(self._call(["dumpsys", "account"], log_output=False))
        if account.lower() not in (name.lower() for name in accounts):
            self.fail("Google sign-in did not complete.  Sign in to the Google test account on the DUT, then run al_google_account_prep again.")
        logging.info("Signed in to the Google test account.")
        self.createPrepStatusControlFile()

    def sign_in(self, account, password):
        timeout = int(Params.get(self.module, 'signin_timeout'))
        self._call(["am", "start -a android.settings.ADD_ACCOUNT_SETTINGS --esa account_types com.google"])

        self.enter_field(["Email or phone"], account, timeout)
        self.enter_field(["Enter your password", "Show password"], password, timeout)

        # Terms of service, then optional Google services and backup settings, which are accepted as offered.
        deadline = time.time() + timeout
        while time.time() < deadline:
            root = ui.read_ui(self)
            if ui.find_any(root, ["Verify it's you", "2-Step Verification", "Confirm it's you", "Try another way"]) is not None:
                self.fail("Google asked for extra verification for this sign-in.  Sign in to the Google test account on the DUT once, then run al_google_account_prep again.")
            button = ui.find_any(root, ["I agree", "Accept", "More", "Agree", "Done"])
            if button is not None:
                ui.tap(self, button, settle=3)
                continue
            if google_accounts(self._call(["dumpsys", "account"], log_output=False)):
                return
            time.sleep(3)

    def enter_field(self, labels, value, timeout):
        root, field = ui.wait_for(self, labels, timeout=timeout)
        if field is None:
            self.fail("The Google sign-in screen did not appear as expected.  Sign in to the Google test account on the DUT, then run al_google_account_prep again.")
        edit = next((node for node in root.iter("node") if node.get("class") == "android.widget.EditText"), field)
        ui.tap(self, edit)
        self._send_text(value)
        root, button = ui.wait_for(self, ["Next"], timeout=10)
        if button is None:
            self.fail("The Google sign-in screen has no Next button.")
        ui.tap(self, button, settle=5)

    def kill(self):
        return 0
