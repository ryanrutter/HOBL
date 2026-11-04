# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import time

from core.parameters import Params
import utilities.open_source.aluminium_ui as ui
from scenarios.aluminium.al_accounts_check import require_accounts


def run(scenario):
    # The same sign-in as the Windows netflix scenario: username, Tab, password, Enter.  The values come from the
    # [netflix] section of the device profile and are replaced with ******** in the HOBL log.
    require_accounts(scenario, "netflix")
    username = Params.get("netflix", "netflix_username", log=False)
    password = Params.get("netflix", "netflix_password", log=False)

    root, field = ui.wait_for(scenario, ["Email or mobile number", "Email or phone number", "Email", "Sign In", "Sign in"], timeout=30)
    if field is None:
        scenario.fail("The Netflix sign-in page did not load.")
    edit = next((node for node in root.iter("node") if node.get("class") == "android.widget.EditText"), None)
    if edit is None:
        scenario.fail("The Netflix sign-in page has no email field.")
    ui.tap(scenario, edit)
    scenario._send_text("\ue009a")
    scenario._send_text(username + "\ue004" + password + "\ue007")
    time.sleep(15)

    root = ui.read_ui(scenario)
    if ui.find_any(root, ["Incorrect password", "Sorry, we can't find an account with this email address."]) is not None:
        scenario.fail("Netflix sign-in failed.  Check netflix_username and netflix_password in the device profile.")
    logging.info("Signed in to Netflix.")
