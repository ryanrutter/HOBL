# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import time

import utilities.open_source.aluminium_ui as ui


DOWN = "\ue015"
UP = "\ue013"
ENTER = "\ue007"


def run(scenario):
    # The same steps as the Windows web_site_youtube_tos component: reload, restart, then open the player
    # settings and choose the quality the recording was made with, so the player requests the recorded streams.
    scenario._send_text("\ue009r")
    time.sleep(10)
    scenario._send_text("0")
    time.sleep(2)

    root, settings = ui.wait_for(scenario, ["Settings"], timeout=20)
    if settings is None:
        scenario.fail("The YouTube player Settings button was not found.")
    ui.tap(scenario, settings, settle=1)

    scenario._send_text(DOWN * 10 + ENTER, typing_delay=120)
    time.sleep(2)
    scenario._send_text(UP * 6 + ENTER, typing_delay=120)
    time.sleep(3)
    scenario._send_text("0", typing_delay=120)
    time.sleep(0.5)
    logging.info("Selected the recorded YouTube video quality.")
