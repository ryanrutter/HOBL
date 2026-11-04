# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import time

import utilities.open_source.aluminium_media as media


def run(scenario):
    # Playback position and time at the start of this loop, checked by code_AY0033.
    time.sleep(2)
    state, position = media.playback(scenario, "com.android.chrome")
    scenario.al_youtube_loop_start = (time.time(), position or 0.0)
