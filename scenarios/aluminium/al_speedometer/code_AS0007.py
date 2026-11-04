# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import os
import time

from core.parameters import Params
import utilities.open_source.aluminium_ui as ui


def read_score(root):
    '''The Speedometer score from the results page, which Chrome exposes with the HTML element id.'''
    for node in root.iter("node"):
        if node.get("resource-id") == "result-number" and node.get("text"):
            try:
                return float(node.get("text"))
            except ValueError:
                return None
    return None


def run(scenario):
    timeout = int(Params.get("al_speedometer", "timeout"))
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(15)
        score = read_score(ui.read_ui(scenario))
        if score is not None:
            break
    else:
        scenario.fail(f"Speedometer did not finish within {timeout} seconds.")

    logging.info(f"Speedometer Score: {score}")
    # Same file and metric name as the Windows speedometer scenario.
    with open(os.path.join(scenario.result_dir, "speedometer_score.csv"), "w") as f:
        f.write(f"Speedometer Score,{score}")
