# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import utilities.open_source.aluminium_office as office

def run(scenario):
    logging.debug('Executing code block: code_1XKH6ER.py')
    office.tap_label(scenario, "outlook", ["Subject"], resource_suffix="compose_subject_field", settle=0)
