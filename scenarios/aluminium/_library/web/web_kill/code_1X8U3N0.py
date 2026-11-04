# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import time

def run(scenario):
    logging.debug('Executing code block: code_1X8U3N0.py')
    try:
        scenario._kill("com.android.chrome")
    except:
        pass

    time.sleep(3)

    scenario._web_replay_kill()

    scenario._sleep_to_now()
