# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Sign in to the Microsoft 365 apps with the test Microsoft account
#
# Setup instructions:
#   Set msa_account and dut_password in the device profile.  Run al_app_install_prep first.
##

import logging
import time
import core.app_scenario
from core.parameters import Params
import utilities.open_source.aluminium_ui as ui
from scenarios.aluminium.al_accounts_check import require_accounts


WORD = "com.microsoft.office.word"

# Prompts the Office apps show on first launch, and the button that declines or dismisses each.
DISMISS = ["Don\u2019t allow", "Don't allow", "No, deny", "Not now", "Skip", "Maybe later", "Close", "Got it"]
SIGNED_IN = ["Blank document", "New", "Recent", "Home"]
VERIFY = ["Verify your identity", "Approve sign in request", "Enter code", "Help us protect your account"]


class AlOfficePrep(core.app_scenario.Scenario):
    '''
    Signs in to the Microsoft 365 apps (Word, Excel, PowerPoint, Outlook, OneNote) on an Aluminium (Android desktop) DUT with msa_account and dut_password from the device profile, the equivalent of office_install activation on Windows.  The apps share the sign-in, so it is done once in Word.  Editing documents on Googlebook-sized screens needs a Microsoft 365 subscription on the account.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'timeout', '180', desc="Seconds to wait for each sign-in step.")

    is_prep = True

    def runTest(self):
        require_accounts(self, "microsoft")
        account = Params.get('global', 'msa_account', log=False)
        password = Params.get('global', 'dut_password', log=False)
        timeout = int(Params.get(self.module, 'timeout'))
        user = self._call(["am", "get-current-user"]).strip()
        if not self._call(["sh", f"-c \"pm path --user {user} {WORD} >/dev/null 2>&1 && echo installed\""], expected_exit_code="").strip():
            self.fail("Word is not installed.  Run al_app_install_prep first.")

        self._call(["am", f"start --user {user} -n {WORD}/com.microsoft.office.apphost.LaunchActivity"], expected_exit_code="")
        try:
            if self.signed_in(timeout):
                logging.info("The Microsoft 365 apps are signed in.")
            else:
                self.sign_in(account, password, timeout)
        finally:
            self._call(["am", f"force-stop --user {user} {WORD}"], expected_exit_code="")
        self.createPrepStatusControlFile()

    def signed_in(self, timeout):
        '''Dismisses first-run prompts until Word shows its home page (True) or its Sign in button (False).'''
        deadline = time.time() + timeout
        while time.time() < deadline:
            root = ui.read_ui(self)
            if ui.find_any(root, SIGNED_IN) is not None:
                return True
            sign_in = ui.find(root, "Sign in")
            if sign_in is not None:
                return False
            prompt = ui.find_any(root, DISMISS)
            if prompt is not None:
                ui.tap(self, prompt, settle=2)
                continue
            time.sleep(3)
        self.fail("Word did not show its home page or a Sign in button.")

    def sign_in(self, account, password, timeout):
        logging.info("Signing in to the Microsoft 365 apps.")
        root, button = ui.wait_for(self, ["Sign in"], timeout=10)
        ui.tap(self, button, settle=3)
        for value, labels in ((account, ["Next"]), (password, ["Sign in", "Next"])):
            root, field = ui.wait_for(self, ["Email, phone, or Skype", "Email or phone", "Enter password", "Password"], timeout=timeout)
            edit = next((node for node in root.iter("node") if node.get("class") == "android.widget.EditText"), None)
            if edit is None:
                self.fail("The Microsoft sign-in page has no text field.  Sign in to Word on the DUT once, then run al_office_prep again.")
            ui.tap(self, edit)
            self._send_text(value)
            root, button = ui.wait_for(self, labels, timeout=15)
            if button is None:
                self.fail("The Microsoft sign-in page has no Next button.")
            ui.tap(self, button, settle=5)

        deadline = time.time() + timeout
        while time.time() < deadline:
            root = ui.read_ui(self)
            if ui.find_any(root, VERIFY) is not None:
                self.fail("Microsoft asked for extra verification.  Turn off two-step verification for the test account, or sign in on the DUT once, then run al_office_prep again.")
            if ui.find_any(root, SIGNED_IN) is not None:
                logging.info("Signed in to the Microsoft 365 apps.")
                return
            # "Stay signed in?" and first-run prompts.
            button = ui.find_any(root, ["Yes", "Continue", "Accept"] + DISMISS)
            if button is not None:
                ui.tap(self, button, settle=3)
                continue
            time.sleep(3)
        self.fail("Microsoft 365 sign-in did not complete.  Sign in to Word on the DUT once, then run al_office_prep again.")

    def kill(self):
        self._call(["am", f"force-stop {WORD}"], expected_exit_code="")
        return 0
