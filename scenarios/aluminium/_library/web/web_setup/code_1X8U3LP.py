# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
from core.parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_1X8U3LP.py')
    # Chrome is the only browser supported on Aluminium.
    browser = Params.get("global", "browser")
    if browser != "Chrome":
        scenario.fail(f"Unsupported browser {browser} on Aluminium.  Set global:browser=Chrome in the profile.")

    output = scenario._call(["pm", "path com.android.chrome"], expected_exit_code="")
    if "package:" not in output:
        scenario.fail("Chrome (com.android.chrome) is not installed on the DUT.")

    scenario._kill("com.android.chrome")

    # -W waits until the launch completes, so later actions go to the Chrome window.
    launch_chrome_args = "start -W -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n com.android.chrome/com.google.android.apps.chrome.Main"
    scenario._call(["am", launch_chrome_args])

    # Chrome restores prior tabs after force-stop; close them so each workload starts clean.
    for _ in range(20):
        scenario._send_text("\ue009w", typing_delay=50)

    scenario._call(["am", launch_chrome_args])
    scenario._sleep_to_now()
