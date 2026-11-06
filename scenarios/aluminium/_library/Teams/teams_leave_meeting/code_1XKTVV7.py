# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import utilities.open_source.aluminium_teams as teams

def run(scenario):
    logging.debug('Executing code block: code_1XKTVV7.py')
    teams.leave_meeting(scenario)
    scenario._sleep_to_now()
