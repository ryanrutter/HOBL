# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import utilities.open_source.aluminium_browser as browser

def run(scenario):
    logging.debug('Executing code block: code_1X8U3MW.py')
    # Android apps don't have a quit command, so stop the browser the way the system does.
    browser.kill(scenario)
    scenario._sleep_to_now()
