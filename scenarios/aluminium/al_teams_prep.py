# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Sign in to the Teams app with the Teams test account
#
# Setup instructions:
#   Set teams_install:teams_msa_account and teams_msa_password (or msa_account and dut_password), and
#   teams:access_key, in the device profile.  Run al_app_install_prep first.
##

import logging
import time
import core.app_scenario
from core.parameters import Params
import utilities.open_source.aluminium_ui as ui
import utilities.open_source.aluminium_teams as teams
import utilities.open_source.aluminium_office as office
from scenarios.aluminium.al_accounts_check import require_accounts


# First-run pages and the button that declines or continues past each.
DISMISS = ["Get started", "Don\u2019t allow", "Don't allow", "Not now", "Maybe later", "Skip", "Got it", "Close",
           "No, thanks", "No thanks", "Yes", "Continue", "Accept", "Next", "OK", "Done"]
VERIFY = ["Verify your identity", "Approve sign in request", "Enter code", "Help us protect your account",
          "More information required", "Approve sign-in request"]
# Teams' own email box is an AutoCompleteTextView; Microsoft's sign-in pages use EditText.
TEXT_FIELDS = ["android.widget.EditText", "android.widget.AutoCompleteTextView"]


class AlTeamsPrep(core.app_scenario.Scenario):
    '''
    Signs in to the Teams app on an Aluminium (Android desktop) DUT, the Aluminium version of the Windows teams_install scenario.  It uses teams_install:teams_msa_account and teams_msa_password, or msa_account and dut_password if they aren't set, as on Windows.  The account must not need extra verification (two-step verification or the Authenticator app) to sign in.

    It also allows Teams to use the camera, microphone, and phone (Teams can't join a meeting without the phone permission, since it places calls through Android's telecom service), and turns off its notifications and its location, nearby devices, and contacts requests.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'timeout', '300', desc="Seconds to wait for the Teams sign-in.")

    is_prep = True

    def runTest(self):
        require_accounts(self, "teams")
        if not teams.is_installed(self):
            self.fail("Teams is not installed.  Run al_app_install_prep first.")
        account, password = teams.credentials()
        timeout = int(Params.get(self.module, 'timeout'))
        teams.grant_permissions(self)
        teams.launch(self)
        try:
            self.sign_in(account, password, timeout)
        finally:
            teams.kill(self)
        self.createPrepStatusControlFile()

    def sign_in(self, account, password, timeout):
        '''Reacts to each first-run and sign-in page until Teams shows its main page.  If another Microsoft app on the
        DUT is signed in with the account, Microsoft offers it in an account picker instead of asking for it.'''
        typed = set()
        unrecognized = None
        deadline = time.time() + timeout
        while time.time() < deadline:
            root = ui.read_ui(self)
            if teams.is_signed_in(root):
                logging.info("Teams is signed in.")
                # Tips can appear a moment after the main page.
                time.sleep(5)
                teams.dismiss_prompts(self, ui.read_ui(self))
                return
            if ui.find_any(root, VERIFY) is not None:
                self.fail("Microsoft asked for extra verification.  Turn off two-step verification for the Teams account, or sign in to Teams on the DUT once, then run al_teams_prep again.")
            edit = next((node for node in root.iter("node") if node.get("class") in TEXT_FIELDS and node.get("bounds")), None)
            if edit is not None:
                is_password = edit.get("password") == "true"
                value, name = (password, "password") if is_password else (account, "account")
                if name in typed:
                    self.fail("Microsoft did not accept the Teams account and password.  Check teams_msa_account and teams_msa_password in the device profile.")
                typed.add(name)
                logging.info(f"Entering the Teams {name}")
                ui.tap(self, edit)
                self._send_text("\ue009a\ue009")
                self._send_text(value + "\ue007")
                time.sleep(5)
                continue
            picker = next((node for node in root.iter("node") if (node.get("text") or "").lower() == account.lower()
                           and node.get("clickable") == "true"), None)
            if picker is not None:
                ui.tap(self, picker, settle=3)
                continue
            # Teams explains why it wants nearby devices (Bluetooth) before asking; decline.
            if ui.find_any(root, ["Allow Nearby Devices Access"]) is not None:
                button = ui.find_any(root, ["Cancel"])
                if button is not None:
                    ui.tap(self, button, settle=3)
                    continue
            button = ui.find_any(root, DISMISS)
            if button is not None:
                logging.info(f"Tapping {button.get('text') or button.get('content-desc')}")
                ui.tap(self, button, settle=3)
                continue
            # Teams can drop to the background while signing in, for example after a permission prompt; bring it back.
            top = office.foreground_package(self)
            if top not in (teams.PACKAGE, "com.google.android.permissioncontroller"):
                logging.info(f"Teams is not in front ({top}); opening it again")
                teams.launch(self)
                time.sleep(5)
                continue
            labels = sorted({node.get("text") or node.get("content-desc") for node in root.iter("node")
                             if node.get("package") == teams.PACKAGE and (node.get("text") or node.get("content-desc"))
                             and "@" not in (node.get("text") or node.get("content-desc"))})[:15]
            if labels != unrecognized:
                logging.debug(f"Waiting on a Teams page with: {labels}")
                unrecognized = labels
            time.sleep(3)
        self.fail(f"Teams sign-in did not complete within {timeout} seconds.  Sign in to Teams on the DUT once, then run al_teams_prep again.")

    def kill(self):
        try:
            teams.kill(self)
        except Exception:
            pass
        return 0
