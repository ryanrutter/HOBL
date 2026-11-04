# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import time

import utilities.open_source.aluminium_media as media


def run(scenario):
    start_time, start_position = scenario.al_netflix_start
    state, position = media.playback(scenario, "com.android.chrome")
    elapsed = time.time() - start_time
    if state != "PLAYING":
        scenario.fail(f"Netflix stopped playing (state {state}).")
    played = position - start_position
    logging.info(f"Netflix played {played:.0f}s of video in {elapsed:.0f}s")
    if played < elapsed - max(15.0, elapsed * 0.1):
        scenario.fail(f"Netflix played only {played:.0f}s of video in {elapsed:.0f}s; playback stalled.")
