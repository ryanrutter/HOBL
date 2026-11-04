# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
from core.parameters import Params


def run(scenario):
    archive = Params.get('web_switch_archive', 'archive_name')
    logging.info("Switching web_replay archive to %s", archive)
    scenario._web_replay_change_archive(archive)
    scenario._sleep_to_now()
