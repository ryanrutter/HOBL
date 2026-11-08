# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import utilities.open_source.aluminium_office as office

def run(scenario):
    logging.debug('Executing code block: code_1XKH6C0.py')
    if office.excel_skipped(scenario):
        return
    office.tap_label(scenario, "excel", ["Monthly Expenses"])
