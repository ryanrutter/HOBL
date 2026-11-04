# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging

def run(scenario):
    logging.debug('Executing code block: code_1X8U3MW.py')
    # Android apps don't have a quit command, so stop Chrome the way the system does.
    scenario._kill("com.android.chrome")
    scenario._sleep_to_now()
