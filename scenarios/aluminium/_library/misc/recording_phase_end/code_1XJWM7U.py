# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
from core.parameters import Params
import time

def run(scenario):
    logging.debug('Executing code block: code_1XJWM7U.py')
    duration = time.time() - scenario.phase_start_time
    category = Params.get(scenario.component, "phase_category")
    name = Params.get(scenario.component, "phase_name")
    scenario._record_phase_time(category + ": " + name, scenario.phase_start_time, duration)
