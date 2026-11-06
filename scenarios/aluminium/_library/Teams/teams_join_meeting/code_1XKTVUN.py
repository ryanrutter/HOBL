# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import utilities.open_source.aluminium_teams as teams
from core.parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_1XKTVUN.py')
    if Params.get('teams', 'bots_send_video') == '1':
        teams.check_bot_video(scenario)
    scenario._sleep_to_now()
