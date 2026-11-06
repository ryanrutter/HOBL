# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import utilities.open_source.aluminium_office as office

def run(scenario):
    logging.debug('Executing code block: code_1XKH6EY.py')
    office.tap_label(scenario, "outlook", ["Attachments"])
    office.tap_label(scenario, "outlook", ["Choose from files"])
    office.pick_file(scenario, "Manarola2.png")
    office.wait_for_attachment(scenario, "Manarola2.png")
    scenario._sleep_to_now()
