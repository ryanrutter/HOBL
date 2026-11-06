# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import utilities.open_source.aluminium_office as office

def run(scenario):
    logging.debug('Executing code block: code_1XKH68P.py')
    office.open_document(scenario, "word", "test_long_doc.docx")
    office.check_document_open(scenario, "word", "test_long_doc.docx")
    scenario._sleep_to_now()
