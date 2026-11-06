# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

"""Read and act on the screen of an Aluminium (Android desktop) DUT through its accessibility tree.

The tree is captured with UIAutomator through the HOBL agent.  It can contain account names, so it is never
logged, and the copy on the DUT is deleted after reading.
"""

import time
import xml.etree.ElementTree as ET

from core.parameters import Params


UI_TREE_PATH = "/data/local/tmp/hobl_ui.xml"
# UIAutomator waits for the screen to be idle; give up and try again if it waits this long.
DUMP_TIMEOUT = 30


def read_ui(scenario, path=UI_TREE_PATH, attempts=3):
    '''Returns the root of the DUT's current accessibility tree.'''
    try:
        for attempt in range(attempts):
            last = attempt == attempts - 1
            dump_output = scenario._call(
                ["timeout", f"{DUMP_TIMEOUT} uiautomator dump {path}"],
                expected_exit_code="", fail_on_exception=False, log_output=False,
            )
            exit_code = Params.getCalculated("last_call_exit_code")
            if exit_code != "0":
                # UIAutomator fails, or doesn't return (exit code 124 from timeout), while the screen is animating.
                if ("could not get idle state" in str(dump_output).lower() or exit_code == "124") and not last:
                    time.sleep(1)
                    continue
                raise RuntimeError("Android UIAutomator could not capture the screen's accessibility tree.")

            output = scenario._call(
                ["cat", path],
                expected_exit_code="", fail_on_exception=False, log_output=False,
            )
            if Params.getCalculated("last_call_exit_code") != "0" or not isinstance(output, str):
                if not last:
                    time.sleep(1)
                    continue
                raise RuntimeError("Could not read the screen's accessibility tree.")
            try:
                return ET.fromstring(output)
            except ET.ParseError as exc:
                if not last:
                    time.sleep(1)
                    continue
                raise RuntimeError("Could not read the screen's accessibility tree.") from exc
        raise RuntimeError("Android UIAutomator could not capture the screen's accessibility tree.")
    finally:
        scenario._call(["rm", f"-f {path}"], expected_exit_code="", fail_on_exception=False, log_output=False)


def find(root, labels, attribute="text"):
    '''Returns the first node whose text (or content-desc) exactly matches one of labels, in label order.'''
    if isinstance(labels, str):
        labels = [labels]
    nodes = list(root.iter("node"))
    for label in labels:
        for node in nodes:
            if node.get(attribute) == label and node.get("bounds"):
                return node
    return None


def find_any(root, labels):
    '''Like find(), checking both the text and the content description.'''
    node = find(root, labels)
    return node if node is not None else find(root, labels, attribute="content-desc")


def center(node):
    bounds = node.get("bounds", "").replace("][", ",").strip("[]").split(",")
    x1, y1, x2, y2 = (int(value) for value in bounds)
    return (x1 + x2) // 2, (y1 + y2) // 2


def tap(scenario, node, settle=0.5):
    x, y = center(node)
    scenario._call(["input", f"tap {x} {y}"])
    time.sleep(settle)


def wait_for(scenario, labels, timeout=30, poll=2):
    '''Waits until a node matching one of labels is on screen.  Returns (root, node), or (root, None) on timeout.'''
    deadline = time.time() + timeout
    while True:
        root = read_ui(scenario)
        node = find_any(root, labels)
        if node is not None or time.time() >= deadline:
            return root, node
        time.sleep(poll)
