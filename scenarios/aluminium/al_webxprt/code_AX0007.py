# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import os
import time

from core.parameters import Params
import utilities.open_source.aluminium_ui as ui


def read_score(root):
    '''The overall score from the WebXPRT results table: the number after the "Overall Score" label.'''
    texts = [node.get("text").strip() for node in root.iter("node") if node.get("text") and node.get("text").strip()]
    for index, text in enumerate(texts[:-1]):
        if text == "Overall Score" and texts[index + 1].isdigit():
            return int(texts[index + 1])
    return None


def run(scenario):
    timeout = int(Params.get("al_webxprt", "timeout"))
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(30)
        score = read_score(ui.read_ui(scenario))
        if score is not None:
            break
    else:
        scenario.fail(f"WebXPRT did not finish within {timeout} seconds.")

    logging.info(f"WebXPRT Score: {score}")
    # Same file and metric name as the Windows webxprt scenario.
    with open(os.path.join(scenario.result_dir, "webxprt_score.csv"), "w") as f:
        f.write(f"WebXPRT Score,{score}")
