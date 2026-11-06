# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import time

import utilities.open_source.aluminium_media as media
import utilities.open_source.aluminium_browser as browser


def run(scenario):
    # Android's media session reports whether Chrome is playing the video, and its position.
    deadline = time.time() + 60
    state = None
    while time.time() < deadline:
        state, position = media.playback(scenario, browser.package())
        if state == "PLAYING":
            logging.info(f"Netflix is playing at {position:.0f}s")
            scenario.al_netflix_start = (time.time(), position)
            return
        time.sleep(3)
    scenario.fail(f"Netflix playback did not start (state {state}).  Check the Netflix page on the DUT.")
