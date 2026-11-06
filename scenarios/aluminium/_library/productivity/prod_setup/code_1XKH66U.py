# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import utilities.open_source.aluminium_office as office

def run(scenario):
    logging.debug('Executing code block: code_1XKH66U.py')
    # Windows uploads abl_docs to OneDrive before each run; this restores the documents the apps edited.
    office.copy_docs(scenario)
