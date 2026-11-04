# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
from core.parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_1X8U3N2.py')
    scenario._web_replay_check_log(int(Params.get("web_check", "youtube_duration")))
