# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import time
import xml.etree.ElementTree as ET

from core.parameters import Params
import utilities.open_source.aluminium_browser as browser


UI_TREE_PATH = "/data/local/tmp/hobl_web_prep.xml"


def _find_text(root, text):
    return next((node for node in root.iter("node") if node.get("text") == text), None)


def _node_center(scenario, node, description):
    bounds = node.get("bounds", "").replace("][", ",").strip("[]").split(",")
    if len(bounds) != 4:
        scenario.fail(f"Chrome accessibility node has invalid bounds for {description}.")
    try:
        x1, y1, x2, y2 = (int(value) for value in bounds)
    except ValueError:
        scenario.fail(f"Chrome accessibility node has invalid bounds for {description}.")
    return (x1 + x2) // 2, (y1 + y2) // 2


def _tap_node(scenario, node, description):
    x, y = _node_center(scenario, node, description)
    scenario._call(["input", f"tap {x} {y}"])
    time.sleep(0.5)


def _read_ui(scenario):
    output = ""
    try:
        for attempt in range(3):
            dump_output = scenario._call(
                ["uiautomator", f"dump {UI_TREE_PATH}"],
                expected_exit_code="",
                fail_on_exception=False,
                log_output=False,
            )
            if Params.getCalculated("last_call_exit_code") != "0":
                if "could not get idle state" in str(dump_output).lower() and attempt < 2:
                    time.sleep(1)
                    continue
                raise RuntimeError("Android UIAutomator could not dump the Chrome accessibility tree.")

            output = scenario._call(
                ["cat", UI_TREE_PATH],
                expected_exit_code="",
                fail_on_exception=False,
                log_output=False,
            )
            if Params.getCalculated("last_call_exit_code") != "0":
                if "no such file" in str(output).lower() and attempt < 2:
                    time.sleep(1)
                    continue
                raise RuntimeError("Could not read the Chrome accessibility tree.")
            if not isinstance(output, str):
                raise RuntimeError("Android UIAutomator returned an unexpected response.")

            try:
                return ET.fromstring(output)
            except ET.ParseError as exc:
                if attempt < 2:
                    time.sleep(1)
                    continue
                raise RuntimeError("Could not read the Chrome accessibility tree.") from exc

        raise RuntimeError("Android UIAutomator could not capture an idle Chrome screen.")
    finally:
        scenario._call(
            ["rm", f"-f {UI_TREE_PATH}"],
            expected_exit_code="",
            fail_on_exception=False,
            log_output=False,
        )


def _find_checkbox(root, label):
    parents = {
        child: parent
        for parent in root.iter("node")
        for child in parent
    }
    label_node = _find_text(root, label)
    if label_node is None:
        return None

    current = label_node
    while current in parents:
        current = parents[current]
        checkbox = next(
            (
                node for node in current.iter("node")
                if node.get("class") == "android.widget.CheckBox"
            ),
            None,
        )
        if checkbox is not None:
            return checkbox
    return None


def _checkboxes(root):
    return [
        node for node in root.iter("node")
        if node.get("class") == "android.widget.CheckBox"
    ]


def _time_range_value(root):
    spinner = next(
        (
            node for node in root.iter("node")
            if node.get("class") == "android.widget.Spinner"
        ),
        None,
    )
    if spinner is None:
        return None
    return next(
        (node.get("text") for node in spinner.iter("node") if node.get("text")),
        spinner.get("text"),
    )


def _clear_data_settings_loaded(root):
    return any(
        _find_text(root, label) is not None
        for label in ("Time range", "Privacy and security", "Delete browsing data")
    )


def _open_clear_data_settings(scenario):
    for navigation_attempt in range(2):
        scenario._send_text("\ue009l", typing_delay=50)
        scenario._send_text("chrome://settings/clearBrowserData")
        scenario._send_text("\ue007", typing_delay=50)
        time.sleep(2)

        for poll in range(4):
            root = _read_ui(scenario)
            if _clear_data_settings_loaded(root):
                return root
            if poll < 3:
                time.sleep(1)

        if navigation_attempt == 0:
            logging.info("Chrome clear-data settings are not ready; retrying navigation.")

    scenario.fail("Chrome settings did not load. Initialize the Chrome test profile and rerun al_web_prep.")


def _select_all_time(scenario, root):
    if _time_range_value(root) == "All time":
        return root

    spinner = next(
        (
            node for node in root.iter("node")
            if node.get("class") == "android.widget.Spinner"
        ),
        None,
    )
    if spinner is None:
        scenario.fail("Chrome clear-data dialog has no time-range selector.")
    _tap_node(scenario, spinner, "time-range selector")

    root = _read_ui(scenario)
    all_time = _find_text(root, "All time")
    if all_time is None:
        scenario.fail("Chrome clear-data dialog does not offer an All time range.")
    _tap_node(scenario, all_time, "All time")

    root = _read_ui(scenario)
    if _time_range_value(root) != "All time":
        scenario.fail("Chrome did not select All time for cached-data cleanup.")
    return root


def _set_cache_only(scenario, root):
    cache_checkbox = _find_checkbox(root, "Cached images and files")
    checkboxes = _checkboxes(root)
    if cache_checkbox is None or not checkboxes:
        scenario.fail("Chrome clear-data categories are unavailable; refusing to delete browser data.")

    for checkbox in checkboxes:
        should_be_checked = checkbox is cache_checkbox
        is_checked = checkbox.get("checked") == "true"
        if is_checked != should_be_checked:
            _tap_node(scenario, checkbox, "browser-data category")

    root = _read_ui(scenario)
    cache_checkbox = _find_checkbox(root, "Cached images and files")
    checked = [node for node in _checkboxes(root) if node.get("checked") == "true"]
    if cache_checkbox is None or checked != [cache_checkbox]:
        scenario.fail("Chrome selections are not cache-only; refusing to delete browser data.")
    return root


def _confirm_site_data_dialog(scenario, root):
    if _find_text(root, "Also clear data from these sites?") is None:
        return root

    for checkbox in _checkboxes(root):
        if checkbox.get("checked") == "true":
            _tap_node(scenario, checkbox, "site-data confirmation")

    root = _read_ui(scenario)
    if any(node.get("checked") == "true" for node in _checkboxes(root)):
        scenario.fail("Chrome selected site data for deletion; refusing to remove cookies or sign-in data.")

    delete_button = next(
        (
            node for node in root.iter("node")
            if node.get("text") == "Delete"
            and node.get("class") == "android.widget.Button"
        ),
        None,
    )
    if delete_button is None:
        scenario.fail("Chrome site-data confirmation has no Delete button.")
    _tap_node(scenario, delete_button, "cache-only confirmation")

    time.sleep(2)
    return _read_ui(scenario)


def run(scenario):
    if browser.is_edge():
        # Edge for Android has no clear-data settings page (edge://settings/clearBrowserData is blank).
        logging.info(f"{browser.name()} cached files are kept: Edge for Android has no clear-data settings page.")
        return
    logging.info("Clearing Chrome cached files only; retaining cookies, history, and saved passwords.")

    root = _open_clear_data_settings(scenario)

    if _find_text(root, "Time range") is None:
        privacy = _find_text(root, "Privacy and security")
        if privacy is not None:
            _tap_node(scenario, privacy, "Privacy and security")
            root = _read_ui(scenario)

        delete_data = _find_text(root, "Delete browsing data")
        if delete_data is None:
            scenario.fail("Chrome privacy settings do not expose Delete browsing data.")
        _tap_node(scenario, delete_data, "Delete browsing data")
        root = _read_ui(scenario)

    if _find_text(root, "Time range") is None:
        scenario.fail("Chrome clear-data dialog did not open.")

    root = _select_all_time(scenario, root)
    root = _set_cache_only(scenario, root)
    delete_button = next(
        (
            node for node in root.iter("node")
            if node.get("text") == "Delete data"
            and node.get("class") == "android.widget.Button"
        ),
        None,
    )
    if delete_button is None:
        scenario.fail("Chrome clear-data dialog has no Delete data button.")

    _tap_node(scenario, delete_button, "Delete data")
    time.sleep(2)
    root = _confirm_site_data_dialog(scenario, _read_ui(scenario))
    if _find_text(root, "Time range") is not None:
        scenario.fail("Chrome did not close the clear-data dialog after cache cleanup.")
    logging.info("Chrome cached images and files were cleared.")
