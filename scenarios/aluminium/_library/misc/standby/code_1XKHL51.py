# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import time
from core.parameters import Params
import utilities.open_source.aluminium_standby as standby

def run(scenario):
    logging.debug('Executing code block: code_1XKHL51.py')
    standby_duration = float(Params.get('standby', 'standby_duration'))
    start = standby.read_battery(scenario)
    if start[2]:
        logging.warning("The DUT is on AC power, so the standby power can't be calculated from the battery.")
    start_time = time.time()

    logging.info("Device sleep now.")
    scenario._call(["input", "keyevent KEYCODE_SLEEP"], blocking=False)
    time.sleep(3)
    logging.info(f"Starting standby for {standby_duration:.0f} seconds.")
    # Wait 1s to make sure the screen is off, then start recording power.
    time.sleep(1.0)
    callback_start_time = time.time()
    scenario._callback(Params.get('global', 'callback_test_begin'))
    test_begin_callback_delay = time.time() - callback_start_time
    time.sleep(max(0.0, standby_duration - 3.0 - test_begin_callback_delay))
    # Stop recording power 2s before waking.
    scenario._callback(Params.get('global', 'callback_test_end'))
    time.sleep(2.0)

    standby.wake(scenario)
    standby.write_power(scenario.result_dir, start, standby.read_battery(scenario), time.time() - start_time)
