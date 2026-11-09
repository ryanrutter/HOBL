# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

"""Shared steps for the Microsoft 365 apps on an Aluminium (Android desktop) DUT.

The Windows productivity documents are copied to the test user's Documents/abl_docs folder through Android's media
store, and each app opens its document from that folder by path.  Office can only read a file another app created
when it has all-files access, which al_productivity_prep grants once.
"""

import csv
import logging
import os
import re
import time

from core.parameters import Params
import utilities.open_source.aluminium_ui as ui


DOCS_SOURCE = os.path.join("scenarios", "windows", "_library", "productivity", "prod_setup", "abl_docs")
DOCS_FOLDER = "Documents/abl_docs/"
FILE_URI = "content://media/external/file"
DOCUMENTS_UI = "com.google.android.documentsui"

APPS = {
    "word": {"package": "com.microsoft.office.word", "name": "Word"},
    "excel": {"package": "com.microsoft.office.excel", "name": "Excel"},
    "powerpoint": {"package": "com.microsoft.office.powerpoint", "name": "PowerPoint"},
    "outlook": {"package": "com.microsoft.office.outlook", "name": "Outlook"},
    "onenote": {"package": "com.microsoft.office.onenote", "name": "OneNote"},
}

MIME_TYPES = {
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".png": "image/png",
    ".jpg": "image/jpeg",
}

# Excel for Android up to this version crashes (a null pointer crash in libxlnextandroid.so, an Office bug) as soon as a
# workbook opens on x86_64 Googlebooks.  Raise it if a newer Excel build still crashes.
EXCEL_X86_64_LAST_BAD = (16, 0, 20625)
# Library folders whose steps use Excel.  Their code blocks return at once when Excel is skipped, and
# skip_excel_actions() turns their other steps into idle time.
EXCEL_COMPONENTS = {"prod_excel_open", "prod_excel_run", "prod_excel_switchto", "prod_excel_close"}
# Action types that don't use the DUT, so they are kept when Excel is skipped.
_IDLE_SAFE_ACTIONS = {
    "Information", "Comment", "Setup", "Run Test", "Teardown", "Set Default", "Set User Default", "Loop", "End Loop",
    "If", "Else If", "Else", "End If", "Try", "Except", "End Try", "On Success", "End", "Set", "Set Params",
    "Delete Params", "Increment", "Decrement", "Delay", "Delay To", "Code",
}

Params.setDefault('global', 'excel_skip', 'auto', desc="Skip the Excel steps of the productivity scenarios on Aluminium DUTs and run them as idle time.  auto skips Excel on x86_64 DUTs with an Excel build known to crash (an Office bug), 1 always skips it, 0 never skips it.", valOptions=['auto', '1', '0'])


def current_user(scenario):
    return scenario._call(["am", "get-current-user"]).strip()


def package(app):
    return APPS[app]["package"]


def _version(text):
    return tuple(int(part) for part in re.findall(r"\d+", text or ""))


def _is_aluminium():
    return (Params.get('global', 'platform') or "").strip().lower() == "aluminium"


def excel_skip_reason(scenario):
    '''Returns why the Excel steps are skipped on this DUT, or "" if Excel runs.  The [global] excel_skip parameter
    decides: auto skips Excel on x86_64 DUTs whose Excel build is EXCEL_X86_64_LAST_BAD or older, 1 always skips it
    and 0 never does.  Excel is only ever skipped on Aluminium DUTs; on any other platform this returns "" whatever
    excel_skip is set to.  The result is kept for the rest of the scenario, and a warning is logged once.'''
    if hasattr(scenario, "_excel_skip_reason"):
        return scenario._excel_skip_reason
    if not _is_aluminium():
        scenario._excel_skip_reason = ""
        return ""
    setting = (Params.get('global', 'excel_skip') or "auto").strip().lower()
    reason = ""
    if setting == "1":
        reason = "excel_skip=1 is set in the device profile"
    elif setting != "0":
        abi = (scenario._call(["getprop", "ro.product.cpu.abi"], expected_exit_code="", fail_on_exception=False,
                              log_output=False) or "").strip()
        if abi == "x86_64":
            output = scenario._call(["sh", f"-c \"dumpsys package {package('excel')} | grep -m1 versionName\""],
                                    expected_exit_code="", fail_on_exception=False, log_output=False)
            match = re.search(r"versionName=([\d.]+)", output or "")
            if match and _version(match.group(1))[:len(EXCEL_X86_64_LAST_BAD)] <= EXCEL_X86_64_LAST_BAD:
                reason = (f"Microsoft Excel {match.group(1)} crashes on x86_64 Googlebooks as soon as a workbook opens "
                          "(a null pointer crash in libxlnextandroid.so; an Office bug)")
    scenario._excel_skip_reason = reason
    if reason:
        logging.warning(f"Excel skipped: {reason}.  The Excel steps run as idle time, so the results are not "
                        "like-for-like with Windows or arm64 Googlebooks.  Set excel_skip=0 in the [global] section of "
                        "the device profile to run Excel anyway.")
    return reason


def excel_skipped(scenario):
    '''True if the Excel steps are skipped on this DUT; see excel_skip_reason().'''
    return bool(excel_skip_reason(scenario))


def skip_excel_actions(scenario, actions):
    '''Call after load_action_json() in scenarios that use the productivity library.  Writes excel_skip.csv
    (excel_skipped and excel_skip_reason, for the run report) and, when Excel is skipped, turns each step of the
    prod_excel_* library folders that would use the DUT into a delay of the same length, so the timeline of the other
    apps doesn't change.  Code blocks in those folders return at once when excel_skipped() is true.  Does nothing on
    platforms other than Aluminium.'''
    if not _is_aluminium():
        return 0
    reason = excel_skip_reason(scenario)
    with open(os.path.join(scenario.result_dir, "excel_skip.csv"), "w", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["excel_skipped", 1 if reason else 0])
        if reason:
            writer.writerow(["excel_skip_reason", reason])
    if not reason:
        return 0
    try:
        typing_delay = int(Params.get('global', 'typing_delay'))
    except (TypeError, ValueError):
        typing_delay = 0
    replaced = 0

    def walk(items):
        nonlocal replaced
        for index, action in enumerate(items):
            if action.get("children"):
                walk(action["children"])
            if action.get("component") not in EXCEL_COMPONENTS or action.get("type") in _IDLE_SAFE_ACTIONS:
                continue
            delay = action.get("delay") or "0"
            if action["type"] == "Type":
                try:
                    delay = str(max(float(delay), typing_delay / 1000.0 * len(action.get("text", ""))))
                except ValueError:
                    pass
            items[index] = {
                "type": "Delay", "id": action.get("id", "AUTO"), "enabled": True, "delay": delay,
                "description": f"Excel skipped: {action['type']} {action.get('description', '')}".rstrip(),
                "component": action.get("component"),
            }
            replaced += 1

    walk(actions)
    logging.info(f"Excel skipped: {replaced} Excel steps will run as idle time.")
    return replaced


def docs_path(user):
    return f"/storage/emulated/{user}/{DOCS_FOLDER.rstrip('/')}"


def _query_doc(scenario, user, name):
    stem, ext = os.path.splitext(name)
    # Also finds copies the media store renamed, like "name (1).ext", when a file existed without a media store row.
    output = scenario._call(
        ["content", f"query --user {user} --uri {FILE_URI} --projection _id:_display_name --where \"relative_path='{DOCS_FOLDER}' AND (_display_name='{name}' OR _display_name LIKE '{stem} (%){ext}')\""],
        expected_exit_code="", log_output=False,
    )
    rows = [(match.group(1), match.group(2)) for match in re.finditer(r"\b_id=(\d+), _display_name=([^\r\n]*?)\s*$", output or "", re.MULTILINE)]
    return [row_id for row_id, display in sorted(rows, key=lambda row: row[1] != name)]


def copy_docs(scenario, source=DOCS_SOURCE):
    '''Copies the productivity documents to Documents/abl_docs of the active Android user, replacing any edited copies,
    the equivalent of uploading abl_docs to OneDrive on Windows.'''
    user = current_user(scenario)
    staging = scenario.dut_exec_path + "/abl_docs"
    scenario._call(["mkdir", f"-p {staging}"], expected_exit_code="")
    try:
        for name in sorted(os.listdir(source)):
            path = os.path.join(source, name)
            if not os.path.isfile(path):
                continue
            scenario._upload(path, staging)
            # When an Office app saves, it replaces the file without updating the media store, so rescan it first.
            scenario._call(["content", f"call --user {user} --uri {FILE_URI} --method scan_file --arg {docs_path(user)}/{name}"],
                           expected_exit_code="", log_output=False)
            # Deleting the media store row deletes the file, so a shorter document can't leave old bytes behind.
            for row_id in _query_doc(scenario, user, name):
                scenario._call(["content", f"delete --user {user} --uri {FILE_URI}/{row_id}"], expected_exit_code="")
            mime = MIME_TYPES.get(os.path.splitext(name)[1].lower(), "application/octet-stream")
            scenario._call(["content", f"insert --user {user} --uri {FILE_URI} --bind _display_name:s:{name} --bind relative_path:s:{DOCS_FOLDER} --bind mime_type:s:{mime}"])
            rows = _query_doc(scenario, user, name)
            if len(rows) != 1:
                scenario.fail(f"Could not add {name} to the Documents folder of Android user {user}.")
            scenario._call(["sh", f"-c \"content write --user {user} --uri {FILE_URI}/{rows[0]} < {staging}/{name}\""])
    finally:
        scenario._call(["rm", f"-rf {staging}"], expected_exit_code="")
    logging.info(f"Copied the productivity documents to {docs_path(user)}")


def grant_storage(scenario, app):
    '''Gives an Office app all-files access, so it can open documents the HOBL agent copied.  The app op must be set
    for the app's uid; setting it for the package isn't enough for the media provider.'''
    user = current_user(scenario)
    output = scenario._call(["pm", f"list packages -U --user {user} {package(app)}"], expected_exit_code="")
    match = re.search(rf"package:{re.escape(package(app))} uid:(\d+)", output or "")
    if not match:
        scenario.fail(f"{APPS[app]['name']} is not installed.  Run al_app_install_prep first.")
    scenario._call(["appops", f"set --uid {match.group(1)} MANAGE_EXTERNAL_STORAGE allow"])


def deny_notifications(scenario, app):
    '''Turns off the app's notifications and its "Allow notifications?" prompt, as a user would on first launch.'''
    user = current_user(scenario)
    permission = "android.permission.POST_NOTIFICATIONS"
    scenario._call(["pm", f"revoke --user {user} {package(app)} {permission}"], expected_exit_code="")
    scenario._call(["pm", f"set-permission-flags --user {user} {package(app)} {permission} user-set user-fixed"], expected_exit_code="")


def launcher_activity(scenario, app):
    user = current_user(scenario)
    output = scenario._call(["cmd", f"package resolve-activity --brief --user {user} -c android.intent.category.LAUNCHER {package(app)}"], expected_exit_code="")
    lines = [line.strip() for line in (output or "").splitlines() if "/" in line]
    if not lines:
        scenario.fail(f"{APPS[app]['name']} is not installed.  Run al_app_install_prep first.")
    return lines[-1]


def foreground_package(scenario):
    output = scenario._call(["sh", "-c \"dumpsys activity activities | grep -m1 topResumedActivity\""],
                            expected_exit_code="", fail_on_exception=False, log_output=False)
    match = re.search(r"\su\d+\s+([\w.]+)/", output or "")
    return match.group(1) if match else None


def device_time(scenario):
    '''Returns the DUT's clock in epoch seconds, for app_crashed().'''
    output = scenario._call(["date", "+%s"], expected_exit_code="", fail_on_exception=False, log_output=False)
    return int(output.strip()) if (output or "").strip().isdigit() else 0


def app_crashed(scenario, app, since):
    '''Returns True if the app has crashed since the DUT time "since".  A pinned Office app can be restarted in the
    background after a crash, so the crash log is checked as well as the process.'''
    output = scenario._call(["logcat", f"-b crash -d -t {since}.000"], expected_exit_code="", fail_on_exception=False,
                            log_output=False) or ""
    return f"Cmdline: {package(app)}" in output or f"Process: {package(app)}," in output


def switch_to(scenario, app, attempts=4):
    '''Brings the app's window to the front, launching it maximized if it isn't running: the equivalent of clicking its
    taskbar button on Windows.  An app that is still starting can cover it, so it is checked and retried.'''
    user = current_user(scenario)
    activity = launcher_activity(scenario, app)
    for attempt in range(attempts):
        scenario._call(["am", f"start --user {user} --windowingMode 1 -n {activity}"], expected_exit_code="")
        time.sleep(1)
        top = foreground_package(scenario)
        if top in (package(app), "com.google.android.permissioncontroller"):
            return
        logging.info(f"{APPS[app]['name']} is not in front ({top}); trying again")
        time.sleep(1)
    scenario.fail(f"Could not bring {APPS[app]['name']} to the front.")


def open_document(scenario, app, name):
    '''Opens a document from Documents/abl_docs in the app, maximized.'''
    user = current_user(scenario)
    mime = MIME_TYPES[os.path.splitext(name)[1].lower()]
    path = f"file://{docs_path(user)}/{name}"
    scenario._call(["am", f"start --user {user} --windowingMode 1 -a android.intent.action.VIEW -d {path} -t {mime} -p {package(app)}"])


def document_title(root, app):
    '''The document name the app shows in its title bar, or None.'''
    for node in root.iter("node"):
        if node.get("package") != package(app):
            continue
        rid = node.get("resource-id") or ""
        if rid.endswith("/DocTitle") or rid.endswith("/HintBarDocTitle"):
            return (node.get("text") or node.get("content-desc") or "").split(" - ")[0].strip()
    return None


def check_document_open(scenario, app, name, timeout=60):
    '''Fails unless the app shows the document within timeout seconds.'''
    stem = os.path.splitext(name)[0]
    deadline = time.time() + timeout
    while True:
        root = ui.read_ui(scenario)
        if dismiss_prompts(scenario, app, root):
            continue
        title = document_title(root, app)
        if title and title.startswith(stem):
            return root
        error = ui.find_any(root, ["Can't open file", "Can\u2019t open file"])
        if error is not None:
            scenario.fail(f"{APPS[app]['name']} couldn't open {name}.  Run al_productivity_prep to give Office access to the documents.")
        if time.time() >= deadline:
            scenario.fail(f"{APPS[app]['name']} didn't open {name} within {timeout} seconds.")
        time.sleep(2)


def find_in(root, app_or_package, labels, clickable=None, resource_suffix=None):
    '''Finds the first node of the app (or package name) whose text or content description is exactly one of labels.'''
    pkg = APPS[app_or_package]["package"] if app_or_package in APPS else app_or_package
    if isinstance(labels, str):
        labels = [labels]
    nodes = [node for node in root.iter("node") if node.get("package") == pkg and node.get("bounds")]
    for label in labels:
        for node in nodes:
            if label not in (node.get("text"), node.get("content-desc")):
                continue
            if clickable is not None and (node.get("clickable") == "true") != clickable:
                continue
            if resource_suffix and not (node.get("resource-id") or "").endswith(resource_suffix):
                continue
            return node
    return None


def tap_label(scenario, app, labels, timeout=20, settle=1, clickable=None, resource_suffix=None, required=True):
    '''Waits for a labelled control of the app and taps it: the equivalent of a Windows image-matched click.'''
    deadline = time.time() + timeout
    while True:
        root = ui.read_ui(scenario)
        node = find_in(root, app, labels, clickable=clickable, resource_suffix=resource_suffix)
        if node is not None:
            ui.tap(scenario, node, settle=settle)
            return True
        if app in APPS and dismiss_prompts(scenario, app, root):
            continue
        if time.time() >= deadline:
            if required:
                scenario.fail(f"{APPS.get(app, {}).get('name', app)}: '{labels if isinstance(labels, str) else labels[0]}' was not found.")
            return False
        time.sleep(1)


def close_file_menu(scenario, app, attempts=3):
    '''Leaves the app's File page with its Back button, the equivalent of pressing Esc on Windows.  A tap while the
    page is still sliding in can be ignored, so the page is checked and Back is tapped again if it is still open.'''
    for attempt in range(attempts):
        tap_label(scenario, app, ["Back"], resource_suffix="backButton")
        for _ in range(3):
            if find_in(ui.read_ui(scenario), app, ["Back"], resource_suffix="backButton") is None:
                return
            time.sleep(1)
        logging.info(f"{APPS[app]['name']}'s File page is still open; tapping Back again")
    scenario.fail(f"{APPS[app]['name']}: the File page didn't close.")


def pick_file(scenario, name, timeout=30):
    '''Picks a document in Android's file picker by searching for its name: the equivalent of typing its path into the
    Windows file dialog.'''
    deadline = time.time() + timeout
    while True:
        root = ui.read_ui(scenario)
        search = find_in(root, DOCUMENTS_UI, ["Search"], resource_suffix="docked_search_text")
        if search is None:
            search = find_in(root, DOCUMENTS_UI, ["Search"], clickable=True)
        if search is not None:
            break
        device = find_in(root, APPS["outlook"]["package"], ["Device"])
        if device is not None:
            ui.tap(scenario, device, settle=2)
            continue
        if time.time() >= deadline:
            scenario.fail(f"Android's file picker didn't open to pick {name}.")
        time.sleep(1)
    ui.tap(scenario, search, settle=1)
    scenario._send_text(name + "\ue007")
    while True:
        time.sleep(2)
        root = ui.read_ui(scenario)
        result = find_in(root, DOCUMENTS_UI, [name], resource_suffix="/title")
        if result is not None:
            ui.tap(scenario, result, settle=2)
            return
        if time.time() >= deadline:
            scenario.fail(f"{name} was not found in Android's file picker.  Run al_productivity_prep to copy the documents.")


def kill_all(scenario):
    user = current_user(scenario)
    for app in APPS:
        scenario._call(["am", f"force-stop --user {user} {package(app)}"], expected_exit_code="", fail_on_exception=False)


def outlook_body(scenario, timeout=10):
    '''Puts the cursor at the start of the message body of the Outlook draft.'''
    deadline = time.time() + timeout
    while True:
        root = ui.read_ui(scenario)
        body = next((node for node in root.iter("node") if node.get("package") == package("outlook")
                     and "rooster" in (node.get("resource-id") or "")
                     and node.get("class") == "android.widget.EditText"), None)
        if body is None:
            body = next((node for node in root.iter("node") if node.get("package") == package("outlook")
                         and node.get("class") == "android.widget.EditText"
                         and not (node.get("resource-id") or "").endswith(("subject_field", "to_field"))
                         and ui.center(node)[1] > 300), None)
        if body is not None:
            x1, y1 = (int(v) for v in node_bounds(body)[:2])
            scenario._call(["input", f"tap {x1 + 20} {y1 + 20}"])
            time.sleep(0.5)
            scenario._send_text("\ue009\ue011")
            return
        if time.time() >= deadline:
            scenario.fail("Outlook's message body was not found.")
        time.sleep(1)


def node_bounds(node):
    return [int(v) for v in node.get("bounds", "").replace("][", ",").strip("[]").split(",")]


def wait_for_attachment(scenario, name, timeout=30):
    '''Waits until the Outlook draft lists the attachment.'''
    deadline = time.time() + timeout
    while True:
        root = ui.read_ui(scenario)
        if find_in(root, "outlook", [name], resource_suffix="attachment_item_filename") is not None:
            return
        if time.time() >= deadline:
            scenario.fail(f"Outlook didn't attach {name}.")
        time.sleep(1)


def outlook_discard_draft(scenario):
    '''Discards the message being composed.  Outlook for Android has no Discard command: closing the message saves it
    as a draft, so the draft is deleted from the Drafts folder, then Outlook goes back to the Inbox.'''
    tap_label(scenario, "outlook", ["Close"], clickable=True, settle=2)
    tap_label(scenario, "outlook", ["Drafts"], settle=2)
    deadline = time.time() + 20
    while True:
        root = ui.read_ui(scenario)
        rows = [node for node in root.iter("node") if node.get("package") == package("outlook")
                and node.get("long-clickable") == "true" and ui.center(node)[0] > 400]
        if rows:
            break
        if time.time() >= deadline:
            scenario.fail("Outlook's Drafts folder didn't show the closed message.")
        time.sleep(1)
    x, y = ui.center(rows[0])
    scenario._call(["input", f"swipe {x} {y} {x} {y} 1200"])
    time.sleep(1)
    tap_label(scenario, "outlook", ["Delete"], clickable=True, settle=2)
    tap_label(scenario, "outlook", ["Inbox"], settle=1)


def _label(node):
    return (node.get("content-desc") or node.get("text") or "").strip()


def _onenote_nodes(root, prefix):
    return [node for node in root.iter("node") if node.get("package") == package("onenote") and node.get("bounds")
            and _label(node).startswith(prefix)]


def onenote_set_default_section(scenario, timeout=20):
    '''Answers OneNote's "Default section unavailable" prompt, which it shows instead of adding a page when it has no
    default section: picks Quick Notes (or the first section) of the notebook OneNote offers as the default section.'''
    tap_label(scenario, "onenote", ["OK"], clickable=True, settle=2)
    deadline = time.time() + timeout
    while time.time() < deadline:
        root = ui.read_ui(scenario)
        sections = _onenote_nodes(root, "Section:")
        if sections:
            section = next((node for node in sections if _label(node).startswith("Section: Quick Notes")), sections[0])
            notebook = next((_label(node).split(". ", 1)[-1] for node in _onenote_nodes(root, "Navigate Up")), "the notebook")
            name = _label(section).split(". ")[0][len("Section: "):]
            logging.warning(f"OneNote had no default section, so it couldn't add a page; setting {name} in {notebook} as "
                            "its default section.")
            ui.tap(scenario, section, settle=1)
            tap_label(scenario, "onenote", ["OK"], clickable=True, settle=2)
            return
        # The picker can open on the list of notebooks: open the first one.
        header = next(iter(_onenote_nodes(root, "Notebooks")), None)
        if header is not None:
            top = ui.center(header)[1]
            notebook = next((node for node in root.iter("node") if node.get("package") == package("onenote")
                             and node.get("bounds") and _label(node) and not _label(node).startswith("\ufffd")
                             and _label(node) not in ("Notebooks", "CANCEL", "OK", "Set as default")
                             and ui.center(node)[1] > top), None)
            if notebook is not None:
                ui.tap(scenario, notebook, settle=2)
                continue
        time.sleep(1)
    scenario.fail("OneNote has no default section and its default section picker didn't show a section.  "
                  "Open OneNote on the DUT, add a page, and choose a default section when asked.")


def onenote_new_page(scenario):
    '''Adds a page to the default notebook: the equivalent of Windows OneNote's Add page button.'''
    root = ui.read_ui(scenario)
    if find_in(root, "onenote", ["New Page"]) is None:
        tap_label(scenario, "onenote", ["Back"], clickable=True, settle=2)
    tap_label(scenario, "onenote", ["New Page"], clickable=True, settle=2)
    if _onenote_nodes(ui.read_ui(scenario), "Default section unavailable"):
        onenote_set_default_section(scenario)
        tap_label(scenario, "onenote", ["New Page"], clickable=True, settle=2)


def onenote_delete_page(scenario, timeout=10):
    '''Deletes the page being edited: the equivalent of selecting the page and pressing Delete on Windows.  OneNote's
    page menu ignores taps while a note is being edited, so the page is selected in the page list and deleted with
    the selection toolbar.  The test account's notebook is shared by every DUT that uses it, so the list can also show
    pages synced from other DUTs; the page being edited is the one marked Active.'''
    scenario._send_text("\ue00c")
    time.sleep(1)
    root = ui.read_ui(scenario)
    if find_in(root, "onenote", ["New Page"]) is None:
        tap_label(scenario, "onenote", ["Back"], clickable=True, settle=2)
    deadline = time.time() + timeout
    while True:
        pages = _onenote_nodes(ui.read_ui(scenario), "Page:")
        entry = next((node for node in pages if ". Active." in _label(node)), pages[0] if pages else None)
        if entry is not None:
            break
        if time.time() >= deadline:
            scenario.fail("OneNote's page list didn't show the page to delete.")
        time.sleep(1)
    x, y = ui.center(entry)
    scenario._call(["input", f"swipe {x} {y} {x} {y} 1200"])
    time.sleep(1)
    tap_label(scenario, "onenote", ["Delete page"], clickable=True, resource_suffix="selection_delete", settle=1)
    tap_label(scenario, "onenote", ["DELETE", "Delete"], clickable=True, settle=1)


def permission_prompt(root):
    '''The "Don't allow" button of an Android permission prompt on screen, or None.'''
    for node in root.iter("node"):
        if "permissioncontroller" in (node.get("package") or "") and node.get("bounds") \
                and (node.get("text") or node.get("content-desc")) in ("Don\u2019t allow", "Don't allow"):
            return node
    return None


def dismiss_permission_prompt(scenario, root=None):
    '''Declines an Android permission prompt if one is showing.  The Office apps can ask for notifications on launch
    even after al_productivity_prep denied them.  Returns True if a prompt was dismissed.'''
    root = root if root is not None else ui.read_ui(scenario)
    button = permission_prompt(root)
    if button is None:
        return False
    logging.info("Declining an Android permission prompt")
    ui.tap(scenario, button, settle=2)
    return True


def dismiss_prompts(scenario, app, root=None):
    '''Declines a prompt the app shows over its document: Android's notification permission prompt, Office's feedback
    survey and feature announcements, or its "Add to Home screen" offer (ticking "Don't ask me again").  Returns True
    if a prompt was dismissed.'''
    root = root if root is not None else ui.read_ui(scenario)
    if dismiss_permission_prompt(scenario, root):
        return True
    # Office asks for feedback at random; decline it.
    survey = find_in(root, app, ["NOT NOW", "Not now"], clickable=True)
    if survey is not None and find_in(root, app, ["We'd love your feedback!", "We\u2019d love your feedback!"]) is not None:
        logging.info(f"Declining {APPS[app]['name']}'s feedback survey")
        ui.tap(scenario, survey, settle=2)
        return True
    # Office asks for an app rating at random ("Enjoying OneNote?"), and can follow a "Not really" with a request for
    # feedback; decline both.  The prompts are matched by their exact text wherever they are drawn.
    name = APPS[app]['name']
    if ui.find_any(root, [f"Enjoying {name}?", "Enjoying the app?"]) is not None:
        button = ui.find_any(root, ["Not really", "NOT REALLY"])
        if button is not None:
            logging.info(f"Declining {name}'s rating prompt")
            ui.tap(scenario, button, settle=2)
            return True
    if ui.find_any(root, ["Would you mind giving us some feedback?", "Would you like to give feedback?"]) is not None:
        button = ui.find_any(root, ["No, thanks", "No thanks", "NO THANKS", "Not now", "NOT NOW"])
        if button is not None:
            logging.info(f"Declining {name}'s feedback request")
            ui.tap(scenario, button, settle=2)
            return True
    # Outlook points out a new feature once with a tooltip that holds focus, hiding the rest of the window; tap it away.
    tip = next((node for node in root.iter("node") if node.get("package") == package("outlook")
                and (node.get("text") or "").startswith("Now your folders on mobile match")), None)
    if tip is not None:
        logging.info("Closing Outlook's new-feature tip")
        ui.tap(scenario, tip, settle=2)
        return True
    # Microsoft 365 announces new features with a one-time sheet.
    got_it = find_in(root, app, ["Got It", "Got it", "GOT IT"], clickable=True)
    if got_it is not None:
        logging.info(f"Closing {APPS[app]['name']}'s feature announcement")
        ui.tap(scenario, got_it, settle=2)
        return True
    if find_in(root, app, ["Add to Home screen"]) is None:
        return False
    never = find_in(root, app, ["Dont ask me again", "Don't ask me again", "Don\u2019t ask me again"])
    if never is not None:
        ui.tap(scenario, never, settle=1)
    no = find_in(root, app, ["No Thanks", "No thanks"])
    if no is None:
        return False
    logging.info(f"Declining {APPS[app]['name']}'s offer to add the document to the home screen")
    ui.tap(scenario, no, settle=2)
    return True
