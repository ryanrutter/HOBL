# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Microsoft Teams helpers for Aluminium (Android desktop) scenarios.  The meeting and its bots are created and removed
# on the host with the Windows Teams library code (scenarios/windows/_library/Teams); these helpers drive the Teams
# app on the DUT through its accessibility tree.

import importlib.util
import json
import logging
import os
import re
import time
import requests
from core.parameters import Params
import utilities.open_source.aluminium_ui as ui

PACKAGE = "com.microsoft.teams"
LAUNCHER = f"{PACKAGE}/com.microsoft.skype.teams.Launcher"
# Teams needs the phone permissions to join a meeting, as it places calls through Android's telecom service.
PERMISSIONS = ["android.permission.CAMERA", "android.permission.RECORD_AUDIO", "android.permission.READ_PHONE_STATE",
               "android.permission.CALL_PHONE"]
DENIED_PERMISSIONS = ["android.permission.POST_NOTIFICATIONS", "android.permission.ACCESS_FINE_LOCATION",
                      "android.permission.ACCESS_COARSE_LOCATION", "android.permission.BLUETOOTH_CONNECT",
                      "android.permission.BLUETOOTH_SCAN", "android.permission.BLUETOOTH_ADVERTISE",
                      "android.permission.READ_CONTACTS",
                      "android.permission.WRITE_CONTACTS"]

# Labels of the Teams app's main page.
SIGNED_IN = ["Activity", "Chat", "Calendar", "Calls", "Communities", "Home"]
# Labels shown while the DUT is in a call.
IN_CALL = ["Leave", "Hang up", "End call", "Leave call"]


def current_user(scenario):
    return scenario._call(["am", "get-current-user"]).strip()


def credentials():
    '''The Teams account and password: teams_install:teams_msa_account and teams_msa_password if set, as on Windows,
    otherwise msa_account and dut_password.'''
    account = Params.get('teams_install', 'teams_msa_account', log=False) or ""
    password = Params.get('teams_install', 'teams_msa_password', log=False) or ""
    if account.strip():
        return account.strip(), password
    return (Params.get('global', 'msa_account', log=False) or "").strip(), Params.get('global', 'dut_password', log=False) or ""


def is_installed(scenario):
    user = current_user(scenario)
    return bool(scenario._call(["sh", f"-c \"pm path --user {user} {PACKAGE} >/dev/null 2>&1 && echo installed\""],
                               expected_exit_code="").strip())


def grant_permissions(scenario):
    '''Allows the camera and microphone, which Teams asks for when joining a call, and turns off its notifications,
    location and nearby devices (Bluetooth) requests, as a user would on first launch.'''
    user = current_user(scenario)
    for permission in PERMISSIONS:
        scenario._call(["pm", f"grant --user {user} {PACKAGE} {permission}"], expected_exit_code="")
    for permission in DENIED_PERMISSIONS:
        scenario._call(["pm", f"revoke --user {user} {PACKAGE} {permission}"], expected_exit_code="", fail_on_exception=False)
        scenario._call(["pm", f"set-permission-flags --user {user} {PACKAGE} {permission} user-set user-fixed"],
                       expected_exit_code="", fail_on_exception=False)


def launch(scenario):
    user = current_user(scenario)
    scenario._call(["am", f"start --user {user} --windowingMode 1 -n {LAUNCHER}"], expected_exit_code="")


def kill(scenario):
    user = current_user(scenario)
    scenario._call(["am", f"force-stop --user {user} {PACKAGE}"], expected_exit_code="", fail_on_exception=False)


def find(root, labels, clickable=None):
    '''Finds the first Teams node whose text or content description is exactly one of labels.'''
    nodes = [node for node in root.iter("node") if node.get("package") == PACKAGE and node.get("bounds")]
    for label in labels:
        for node in nodes:
            if label in (node.get("text"), node.get("content-desc")) and \
                    (clickable is None or (node.get("clickable") == "true") == clickable):
                return node
    return None


def is_signed_in(root):
    return sum(1 for label in SIGNED_IN if find(root, [label]) is not None) >= 2


def in_call(root):
    return find(root, IN_CALL) is not None


# In-call camera and microphone buttons, and the labels they show while the camera or microphone is on and off.
TOGGLES = {
    "camera": ("call_control_video", "Turn off camera", "Turn on camera"),
    "mic": ("call_control_mute", "Mute", "Unmute"),
}


def toggle(root, name):
    '''The in-call camera or microphone button (name is "camera" or "mic"), or None.'''
    rid = TOGGLES[name][0]
    return next((node for node in root.iter("node") if node.get("package") == PACKAGE and node.get("clickable") == "true"
                 and (node.get("resource-id") or "").endswith("/" + rid)), None)


def toggle_is_on(name, node):
    '''Whether the camera or microphone is on, from its button's label: "Turn off camera" or "Mute" while it's on.'''
    return (node.get("content-desc") or node.get("text") or "") == TOGGLES[name][1]


def set_toggle(scenario, name, on, timeout=15):
    '''Turns the camera or microphone on or off in the call and checks that it changed.'''
    deadline = time.time() + timeout
    while time.time() < deadline:
        node = toggle(ui.read_ui(scenario), name)
        if node is None:
            time.sleep(1)
            continue
        if toggle_is_on(name, node) == on:
            return True
        logging.info(f"Turning the {name} {'on' if on else 'off'}")
        ui.tap(scenario, node, settle=2)
    scenario.fail(f"Could not turn the Teams {name} {'on' if on else 'off'}.")


def join_meeting(scenario, meeting_url, send_video, send_audio, timeout=120):
    '''Opens the meeting link in the Teams app, joins from the pre-join page, and sets the camera and microphone: the
    equivalent of the Windows msteams: join and pre-join clicks.  The pre-join page's camera and microphone buttons
    don't respond to taps, so they're set in the call.'''
    user = current_user(scenario)
    # A running Teams opens the meeting in its existing window; started fresh, the meeting window is maximized.
    kill(scenario)
    scenario._call(["am", f"start --user {user} --windowingMode 1 -a android.intent.action.VIEW -d \"{meeting_url}\" -p {PACKAGE}"],
                   expected_exit_code="")
    deadline = time.time() + timeout
    while time.time() < deadline:
        root = ui.read_ui(scenario)
        if in_call(root):
            logging.info("The DUT joined the Teams meeting.")
            maximize_call_window(scenario)
            set_toggle(scenario, "camera", send_video)
            set_toggle(scenario, "mic", send_audio)
            return
        if dismiss_prompts(scenario, root):
            continue
        join = find(root, ["Join now"], clickable=True)
        if join is not None:
            logging.info("Joining the Teams meeting")
            ui.tap(scenario, join, settle=5)
            continue
        if find(root, ["Teams needs permission"]) is not None:
            scenario.fail("Teams can't join meetings without the phone permission.  Run al_teams_prep.")
        time.sleep(2)
    scenario.fail("The DUT did not join the Teams meeting.  Run al_teams_prep, and check that the Teams account can join meetings of the bots' organization.")


def call_window_bounds(scenario):
    '''The call window's (left, top, right, bottom), or None.'''
    output = scenario._call(["sh", "-c \"dumpsys window windows | grep -A30 InCallActivity | grep -m1 -o 'mBounds=Rect([^)]*)'\""],
                            expected_exit_code="", fail_on_exception=False, log_output=False) or ""
    match = re.search(r"Rect\((\d+), (\d+) - (\d+), (\d+)\)", output)
    return tuple(int(v) for v in match.groups()) if match else None


def maximize_call_window(scenario):
    '''Maximizes the call window, which Teams opens in its own window, as the Windows meeting window is.  Teams doesn't
    let the shell restart the call activity maximized, so this uses the desktop's Meta+= shortcut, which toggles.'''
    width = int(re.search(r"(\d+)x\d+", scenario._call(["wm", "size"], expected_exit_code="", log_output=False) or "0x0").group(1))
    for attempt in range(3):
        bounds = call_window_bounds(scenario)
        if bounds is None or bounds[0] <= 0 and bounds[2] >= width:
            return
        logging.info("Maximizing the Teams call window")
        scenario._call(["input", "keycombination 117 70"], expected_exit_code="")
        time.sleep(2)
    logging.warning("Could not maximize the Teams call window.")


def bot_video_on(root, bot="Main"):
    '''Whether the bot's video is showing in the call (Teams shows its profile picture when it has no video), or None
    if the bot isn't on screen.'''
    labels = [node.get("content-desc") or "" for node in root.iter("node") if node.get("package") == PACKAGE]
    if f"{bot} profile picture" in labels:
        return False
    if any(label.startswith(f"{bot}'s video") for label in labels):
        return True
    return None


def check_bot_video(scenario, attempts=10, wait=30):
    '''Makes sure the main bot sends video in a video call, re-adding it if not.  The Windows teams_join_meeting code
    does the same, since the bots service sometimes doesn't send video for a bot that also sends audio; it finds the
    bot's video by image, Aluminium by its accessibility label.'''
    windows = _windows_join_code()
    for name in ["bots_send_video", "bots_send_audio", "bots_share_screen", "server_url", "access_key", "bot_uris", "bot_names", "meeting_url"]:
        setattr(scenario, name, Params.get("teams", name, log=False))
    for attempt in range(1, attempts + 1):
        deadline = time.time() + wait
        state = None
        while time.time() < deadline:
            state = bot_video_on(ui.read_ui(scenario))
            if state:
                logging.info("The main bot is sending video.")
                return
            time.sleep(3)
        if state is None:
            logging.info("The main bot isn't on screen, so its video can't be checked.")
            return
        if attempt == attempts:
            scenario.fail(f"The main bot didn't send video after {attempts} attempts.")
        logging.info("The main bot isn't sending video; adding it to the meeting again.")
        windows.remove_bot(scenario)
        windows.add_bot(scenario)


def _windows_join_code():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                        "scenarios", "windows", "_library", "Teams", "teams_join_meeting", "code_YTX59E.py")
    spec = importlib.util.spec_from_file_location("windows_teams_join_meeting", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def leave_meeting(scenario, timeout=30):
    '''Leaves the call, the equivalent of the Windows Leave click.'''
    deadline = time.time() + timeout
    while time.time() < deadline:
        root = ui.read_ui(scenario)
        button = find(root, IN_CALL, clickable=True)
        if button is None:
            logging.info("The DUT left the Teams meeting.")
            return True
        ui.tap(scenario, button, settle=3)
    logging.warning("Could not leave the Teams meeting; closing Teams.")
    kill(scenario)
    return False


def stop_meeting(scenario):
    '''Removes the bots from the meeting, with the same request as the Windows teams_leave_meeting code.  Used when
    the scenario fails before its teardown would do it, so the bots don't stay in the meeting.'''
    bot_uris = Params.get("teams", "bot_uris")
    server_url = Params.get("teams", "server_url")
    if not bot_uris or not server_url:
        return
    data = json.dumps({"botUris": json.loads(bot_uris)}, sort_keys=True)
    try:
        r = requests.post(server_url + "/StopMeeting?code=" + Params.get("teams", "access_key", log=False), data=data)
        logging.info(f"Removed the bots from the meeting: {r.status_code}")
    except Exception as e:
        logging.error(f"Unable to Stop Meeting! {e}")

PROMPTS = ["Don\u2019t allow", "Don't allow", "Not now", "Maybe later", "Skip", "Got it", "Dismiss", "Close", "OK"]


def dismiss_prompts(scenario, root):
    '''Declines a prompt Teams shows over the meeting: Android's notification permission prompt, or Teams' tips and
    survey dialogs.  Returns True if a prompt was dismissed.'''
    for node in root.iter("node"):
        if "permissioncontroller" in (node.get("package") or "") and node.get("bounds") \
                and (node.get("text") or node.get("content-desc")) in ("Don\u2019t allow", "Don't allow"):
            ui.tap(scenario, node, settle=2)
            return True
    if find(root, IN_CALL) is not None:
        return False
    button = find(root, PROMPTS, clickable=True)
    if button is not None:
        logging.info(f"Dismissing a Teams prompt ({button.get('text') or button.get('content-desc')})")
        ui.tap(scenario, button, settle=2)
        return True
    return False


def force_subscribe(scenario):
    '''Asks the bots to subscribe to the DUT's video at the resolution Windows uses for the call size.  Windows also
    re-adds the main bot if its video isn't on screen; Aluminium relies on maintain_bots instead.'''
    resolution = Params.get("teams", "bots_force_subscribe_resolution") or "0"
    send_screen = Params.get("teams", "send_screen") or "0"
    bot_uris = json.loads(Params.get("teams", "bot_uris"))
    bot_names = json.loads(Params.get("teams", "bot_names") or "[]")
    count = len(bot_uris)
    if resolution == "0":
        if count > 16:
            resolution = "180"
        elif count > 4:
            resolution = "240"
        elif count > 1:
            resolution = "180" if send_screen == "1" else "360"
        else:
            resolution = "180" if send_screen == "1" else "720"
    url = Params.get("teams", "server_url") + "/ForceSubscription?code=" + Params.get("teams", "access_key", log=False) + "&resolution=" + resolution
    data = json.dumps({"botUris": bot_uris, "botNames": bot_names}, sort_keys=True)
    for attempt in range(10):
        r = requests.post(url, data=data)
        logging.debug(r.status_code)
        if r.status_code == 200:
            logging.info(f"The bots subscribed to the DUT's video at {resolution}p.")
            return True
        time.sleep(30)
    logging.error("Unable to Force Video Subscribe! Server Side Error, See Logs for Details")
    return False
