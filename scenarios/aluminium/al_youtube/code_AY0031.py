# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import time

import utilities.open_source.aluminium_media as media
import utilities.open_source.aluminium_browser as browser


def run(scenario):
    # YouTube usually starts playing by itself.  If it doesn't, k starts it, the same key Windows uses to pause.
    deadline = time.time() + 30
    pressed = False
    while time.time() < deadline:
        state, position = media.playback(scenario, browser.package())
        if state == "PLAYING":
            logging.info(f"YouTube is playing at {position:.1f}s")
            return
        if not pressed and time.time() > deadline - 20:
            logging.info(f"YouTube playback state is {state}; pressing k to play")
            scenario._send_text("k")
            pressed = True
        time.sleep(2)
    scenario.fail("YouTube playback did not start.  Check the video page on the DUT.")
