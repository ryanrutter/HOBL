# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import time

from core.parameters import Params
import utilities.open_source.aluminium_ui as ui
from scenarios.aluminium.al_accounts_check import require_accounts
import utilities.open_source.aluminium_browser as browser

PASSWORD_OPTIONS = ["use password", "sign in with password"]
CODE_PAGE = ["enter the code we sent", "enter a pin code", "send sign-in code"]


def current_url(root):
    node = next((n for n in root.iter("node") if n.get("resource-id") == f"{browser.package()}:id/url_bar"), None)
    return node.get("text", "") if node is not None else ""


def find_text(root, fragments, attribute="text"):
    '''Returns the first node whose text contains one of fragments, ignoring case.'''
    for node in root.iter("node"):
        value = (node.get(attribute) or "").lower()
        if any(fragment in value for fragment in fragments):
            return node
    return None


def edit_field(root, password):
    return next((n for n in root.iter("node") if n.get("class") == "android.widget.EditText" and (n.get("password") == "true") == password), None)


def run(scenario):
    # Netflix keeps the sign-in between runs (web_clear_cache keeps cookies), so this signs in only when the
    # netflix.com/login page stays on the sign-in form.  The account comes from the [netflix] section of the
    # device profile, the same setting as the Windows netflix scenario, and is replaced with ******** in the log.
    root, _ = ui.wait_for(scenario, ["Netflix"], timeout=30)
    if "/login" not in current_url(root):
        logging.info("Already signed in to Netflix.")
        return

    require_accounts(scenario, "netflix")
    username = Params.get("netflix", "netflix_username", log=False)
    password = Params.get("netflix", "netflix_password", log=False)
    email = edit_field(root, password=False)
    if email is None:
        scenario.fail("The Netflix sign-in page has no email field.")
    ui.tap(scenario, email)
    scenario._send_text("\ue009a")
    # Netflix asks for the email first, then the password on the next page.
    scenario._send_text(username + "\ue007")

    deadline = time.time() + 30
    while time.time() < deadline:
        time.sleep(3)
        root = ui.read_ui(scenario)
        field = edit_field(root, password=True)
        if field is not None:
            ui.tap(scenario, field)
            scenario._send_text(password + "\ue007")
            break
        option = find_text(root, PASSWORD_OPTIONS)
        if option is None:
            option = find_text(root, PASSWORD_OPTIONS, "content-desc")
        if option is not None:
            ui.tap(scenario, option)
            continue
        if find_text(root, CODE_PAGE) is not None:
            scenario.fail("Netflix sent a sign-in code to the account's email instead of asking for its password, so HOBL can't sign in.  "
                          f"Sign in to Netflix once by hand in {browser.name()} on the DUT; the sign-in is kept between runs.")
    else:
        scenario.fail("The Netflix password page did not load.")

    time.sleep(15)
    root = ui.read_ui(scenario)
    if find_text(root, ["incorrect password", "can't find an account"]) is not None or "/login" in current_url(root):
        scenario.fail("Netflix sign-in failed.  Check netflix_username and netflix_password in the device profile.")
    logging.info("Signed in to Netflix.")
