# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import utilities.open_source.aluminium_office as office

def run(scenario):
    logging.debug('Executing code block: code_1XKH68W.py')
    office.open_document(scenario, "powerpoint", "sample.pptx")
    office.check_document_open(scenario, "powerpoint", "sample.pptx")
    scenario._sleep_to_now()
