# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import utilities.open_source.aluminium_office as office

def run(scenario):
    logging.debug('Executing code block: code_1XKH68H.py')
    if office.excel_skipped(scenario):
        return
    office.open_document(scenario, "excel", "FamilyBudget.xlsx")
    office.check_document_open(scenario, "excel", "FamilyBudget.xlsx")
    scenario._sleep_to_now()
