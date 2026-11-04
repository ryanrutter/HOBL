# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import math
from core.parameters import Params


def run(scenario):
    duration = int(Params.get("al_youtube", "duration"))
    loop_duration = int(Params.get("al_youtube", "loop_duration"))
    if duration <= 0 or loop_duration <= 0:
        scenario.fail("al_youtube:duration and al_youtube:loop_duration must be positive.")

    loops = math.ceil(duration / loop_duration)
    logging.info(f"Looping set for {loops} iteration{'s' if loops != 1 else ''}")
    Params.setParam("al_youtube", "loops", str(loops))
