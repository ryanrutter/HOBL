# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import utilities.open_source.aluminium_browser as browser

def run(scenario):
    logging.debug('Executing code block: code_1X8U3LP.py')
    # Chrome or Edge, selected with global:browser as on Windows.
    browser.check(scenario)
    if not browser.is_installed(scenario):
        scenario.fail(f"{browser.name()} ({browser.package()}) is not installed on the DUT.  Run al_app_install_prep.")

    browser.kill(scenario)
    browser.use_command_line(scenario)
    started = browser.device_time(scenario) - 5

    # -W waits until the launch completes, so later actions go to the browser window.
    launch_args = f"start -W -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n {browser.launcher(scenario)}"
    scenario._call(["am", launch_args])
    browser.check_not_crashed(scenario, started)

    # The browser restores prior tabs after force-stop; close them so each workload starts clean.
    for _ in range(20):
        scenario._send_text("\ue009w", typing_delay=50)

    scenario._call(["am", launch_args])
    scenario._sleep_to_now()
