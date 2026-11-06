# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import time

import utilities.open_source.aluminium_browser as browser
import utilities.open_source.aluminium_office as office
import utilities.open_source.aluminium_ui as ui

FLAG = "enable-command-line-on-non-rooted-devices"
CHOICES = ["Default", "Enabled", "Disabled"]


def flag_choice(root):
    '''The dropdown of the flag on its edge://flags page: the first clickable choice after the flag's name.'''
    nodes = list(root.iter("node"))
    index = next((i for i, node in enumerate(nodes) if node.get("text") == FLAG), None)
    if index is None:
        return None
    return next((node for node in nodes[index + 1:index + 6] if node.get("clickable") == "true" and node.get("text") in CHOICES), None)


def open_flag(scenario):
    user = browser.current_user(scenario)
    started = browser.device_time(scenario) - 5
    for attempt in range(3):
        # Type only into the browser: on a new install, first-run pages can leave another app in front.
        scenario._call(["am", f"start --user {user} --windowingMode 1 -n {browser.launcher(scenario)}"], expected_exit_code="")
        time.sleep(3)
        top = office.foreground_package(scenario)
        if top != browser.package():
            browser.check_not_crashed(scenario, started)
            logging.info(f"{browser.name()} is not in front ({top}); trying again")
            continue
        scenario._send_text("\ue009l", typing_delay=50)
        scenario._send_text(f"edge://flags/#{FLAG}", typing_delay=50)
        scenario._send_text("\ue007", typing_delay=50)
        time.sleep(3)
        root = ui.read_ui(scenario)
        choice = flag_choice(root)
        if choice is not None:
            return choice
    scenario.fail(f"{browser.name()}'s {FLAG} flag was not found on its edge://flags page.")


def run(scenario):
    # Edge, like Chrome, reads its command-line file (with the web_replay certificates) only with this flag on.
    # Chrome's flag is turned on by install_web_replay_certs.ps1.
    if not browser.is_edge():
        return
    logging.debug('Executing code block: code_AW0212.py')
    choice = open_flag(scenario)
    if choice.get("text") == "Enabled":
        logging.info(f"{browser.name()} already reads its command-line file.")
        return
    ui.tap(scenario, choice, settle=2)
    enabled = next((node for node in ui.read_ui(scenario).iter("node") if node.get("text") == "Enabled"
                    and (node.get("resource-id") or "").endswith("dropdown_label")), None)
    if enabled is None:
        scenario.fail(f"{browser.name()}'s flag dropdown did not open.")
    ui.tap(scenario, enabled, settle=2)
    choice = flag_choice(ui.read_ui(scenario))
    if choice is None or choice.get("text") != "Enabled":
        scenario.fail(f"Could not turn on {browser.name()}'s {FLAG} flag.")
    logging.info(f"Turned on {browser.name()}'s {FLAG} flag; it takes effect when the browser restarts.")
