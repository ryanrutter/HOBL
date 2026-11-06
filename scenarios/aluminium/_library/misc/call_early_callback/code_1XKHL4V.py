# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging

def run(scenario):
    logging.debug('Executing code block: code_1XKHL4V.py')
    # Call tool early callbacks, particularly to get video recording of the setup
    scenario.toolCallBacks("testBeginEarlyCallback")
