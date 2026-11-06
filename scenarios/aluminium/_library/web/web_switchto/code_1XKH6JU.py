# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging

def run(scenario):
    logging.debug('Executing code block: code_1XKH6JU.py')
    user = scenario._call(["am", "get-current-user"]).strip()
    scenario._call(["am", f"start --user {user} --windowingMode 1 -n com.android.chrome/com.google.android.apps.chrome.Main"], expected_exit_code="")
