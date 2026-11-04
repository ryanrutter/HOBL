# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging

def run(scenario):
    logging.debug('Executing code block: code_1X8U3LM.py')
    # Initiate Web Page Record or Replay
    logging.info("Web Replay Delay Disabled")
    scenario._web_replay_start(disable_delay=True)
    scenario._sleep_to_now()
