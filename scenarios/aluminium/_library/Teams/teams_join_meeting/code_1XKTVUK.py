# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import utilities.open_source.aluminium_teams as teams
from core.parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_1XKTVUK.py')
    if Params.get('teams', 'send_screen') == '1':
        scenario.fail("Sharing the DUT's screen in Teams is not supported on Aluminium.  Set teams:send_screen=0.")
    teams.join_meeting(scenario, Params.get('teams', 'meeting_url'), Params.get('teams', 'send_video') == '1',
                       Params.get('teams', 'send_audio') == '1')
    scenario._sleep_to_now()
