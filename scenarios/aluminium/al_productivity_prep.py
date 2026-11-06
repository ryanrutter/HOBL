# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Prepare the Microsoft 365 apps for the productivity scenarios
#
# Setup instructions:
#   Run al_app_install_prep and al_office_prep first.  Set msa_account and dut_password in the device profile.
##

import logging
import os
import time
import core.app_scenario
from core.parameters import Params
import utilities.open_source.aluminium_office as office
import utilities.open_source.aluminium_ui as ui
from scenarios.aluminium.al_accounts_check import require_accounts


# First-run pages and prompts, and the button that declines or dismisses each, in the order to try them.
DISMISS = [
    "Don\u2019t send optional data", "Don't send optional data", "Get Started", "Next",
    "Don\u2019t allow", "Don't allow", "No Thanks", "No thanks", "MAYBE LATER", "Maybe later", "Not now", "Skip",
    "Got it", "Close", "OK",
]
DOCUMENTS = {"word": "test_long_doc.docx", "excel": "FamilyBudget.xlsx", "powerpoint": "sample.pptx"}
VERIFY = ["Verify your identity", "Approve sign in request", "Enter code", "Help us protect your account"]


class AlProductivityPrep(core.app_scenario.Scenario):
    '''
    Prepares Word, Excel, PowerPoint, OneNote and Outlook on an Aluminium (Android desktop) DUT for the productivity scenarios, the Aluminium version of the Windows productivity_prep scenario.

    It copies the Windows productivity documents to the test user's Documents/abl_docs folder, gives the Office apps access to them, turns off the apps' notification prompts, and completes each app's first-run pages: Word, Excel and PowerPoint open their documents, OneNote opens a notebook page, and Outlook adds msa_account (offered by the Microsoft 365 sign-in, or signed in with dut_password).
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'timeout', '180', desc="Seconds to wait for each app's first-run pages.")

    is_prep = True

    def runTest(self):
        require_accounts(self, "microsoft")
        self.timeout = int(Params.get(self.module, 'timeout'))
        self.user = office.current_user(self)
        for app in office.APPS:
            office.grant_storage(self, app)
            office.deny_notifications(self, app)
            self._call(["am", f"force-stop --user {self.user} {office.package(app)}"], expected_exit_code="")
        office.copy_docs(self)

        try:
            for app, document in DOCUMENTS.items():
                logging.info(f"Opening {document} in {office.APPS[app]['name']}")
                office.open_document(self, app, document)
                self.complete_first_run(app, lambda root, app=app, document=document:
                                        (office.document_title(root, app) or "").startswith(os.path.splitext(document)[0]))
            logging.info("Opening OneNote")
            office.switch_to(self, "onenote")
            self.complete_first_run("onenote", lambda root: office.find_in(root, "onenote", ["Canvas", "Recent Pages"]) is not None)
            logging.info("Opening Outlook")
            office.switch_to(self, "outlook")
            self.complete_first_run("outlook", lambda root: office.find_in(root, "outlook", ["New mail"]) is not None,
                                    extra=["Add account", "Continue"])
        finally:
            office.kill_all(self)
        self.createPrepStatusControlFile()

    def complete_first_run(self, app, ready, extra=()):
        '''Dismisses first-run pages until ready(root) is true.'''
        name = office.APPS[app]["name"]
        account = Params.get('global', 'msa_account', log=False)
        typed = set()
        started = office.device_time(self) - 30
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            root = ui.read_ui(self)
            if office.dismiss_prompts(self, app, root):
                continue
            if ready(root):
                # The notification prompt and the "Add to Home screen" offer can appear a moment after the window.
                time.sleep(5)
                if office.dismiss_prompts(self, app):
                    continue
                logging.info(f"{name} is ready.")
                return
            if ui.find_any(root, VERIFY) is not None:
                self.fail("Microsoft asked for extra verification.  Turn off two-step verification for the test account.")
            if ui.find_any(root, ["Can't open file", "Can\u2019t open file"]) is not None:
                self.fail(f"{name} couldn't open its document.  Check that the Office apps were updated from the Play Store.")
            if office.app_crashed(self, app, started) or not self._call(
                    ["pidof", office.package(app)], expected_exit_code="", fail_on_exception=False, log_output=False).strip():
                self.fail(f"{name} closed while starting.  On x86_64 Googlebooks, Excel 16.0.20625 and earlier crash when opening any workbook; check logcat for a native crash in {office.package(app)}.")
            edit = next((node for node in root.iter("node") if node.get("class") == "android.widget.EditText"
                         and node.get("package") == office.package(app) and node.get("password") in ("true", "false")
                         and not (node.get("resource-id") or "").endswith("subject_field")), None)
            if app == "outlook" and edit is not None and ui.find_any(root, ["New message"]) is None:
                is_password = edit.get("password") == "true"
                value, field = (Params.get('global', 'dut_password', log=False), "password") if is_password else (account, "account")
                if field in typed:
                    self.fail("Microsoft did not accept msa_account and dut_password.  Check them in the device profile.")
                typed.add(field)
                ui.tap(self, edit)
                self._send_text("\ue009a\ue009")
                self._send_text(value + "\ue007")
                time.sleep(5)
                continue
            # Outlook offers the account the Microsoft 365 apps are signed in with.
            picker = next((node for node in root.iter("node") if (node.get("text") or "").lower() == account.lower()
                           and node.get("clickable") == "true" and node.get("checked") == "false"), None)
            if picker is not None:
                ui.tap(self, picker, settle=1)
                continue
            button = None
            for label in list(extra) + DISMISS:
                button = office.find_in(root, app, [label])
                if button is not None:
                    break
            if button is not None:
                # Office's "Add to Home screen" dialog has a "Don't ask me again" box to tick before "No Thanks".
                never = office.find_in(root, app, ["Dont ask me again", "Don't ask me again", "Don\u2019t ask me again"])
                if never is not None:
                    ui.tap(self, never, settle=1)
                ui.tap(self, button, settle=3)
                continue
            time.sleep(3)
        self.fail(f"{name} didn't finish its first-run pages within {self.timeout} seconds.  Open it on the DUT once, then run al_productivity_prep again.")

    def kill(self):
        try:
            office.kill_all(self)
        except Exception:
            pass
        return 0
