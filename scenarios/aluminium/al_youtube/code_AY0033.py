# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import time

from core.parameters import Params
import utilities.open_source.aluminium_media as media


def run(scenario):
    # Android's media session reports Chrome's playback state and position, so playback is verified on the DUT
    # itself.  Allowed shortfall: 10% of the loop, at least 15 seconds, for buffering and seeking.
    start_time, start_position = scenario.al_youtube_loop_start
    state, position = media.playback(scenario, "com.android.chrome")
    elapsed = time.time() - start_time
    if state != "PLAYING" or position is None:
        scenario.fail(f"YouTube stopped playing (state {state}).")

    played = position - start_position
    allowed = max(15.0, elapsed * 0.1)
    logging.info(f"YouTube played {played:.1f}s of video in {elapsed:.1f}s")
    if played < elapsed - allowed:
        scenario.fail(f"YouTube played only {played:.1f}s of video in {elapsed:.1f}s; playback stalled.")

    total = float(Params.getCalculated("al_youtube_played") or 0) + played
    Params.setCalculated("al_youtube_played", str(total))
