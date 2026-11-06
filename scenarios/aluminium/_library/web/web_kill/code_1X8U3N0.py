# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import time
import utilities.open_source.aluminium_browser as browser

def run(scenario):
    logging.debug('Executing code block: code_1X8U3N0.py')
    try:
        browser.kill(scenario)
    except:
        pass

    time.sleep(3)

    scenario._web_replay_kill()

    scenario._sleep_to_now()
