# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
from core.parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_1X8U3N2.py')
    youtube_duration = int(Params.get("web_check", "youtube_duration"))
    # al_web checks YouTube playback only when its web_workload includes a YouTube site.
    if getattr(scenario, "_module", "") == "al_web" and "youtube" not in (Params.get("al_web", "web_workload") or ""):
        youtube_duration = 0
    scenario._web_replay_check_log(youtube_duration)
