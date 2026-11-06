# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import utilities.open_source.aluminium_browser as browser

def run(scenario):
    logging.debug('Executing code block: code_1XKH6JU.py')
    user = scenario._call(["am", "get-current-user"]).strip()
    scenario._call(["am", f"start --user {user} --windowingMode 1 -n {browser.launcher(scenario)}"], expected_exit_code="")
