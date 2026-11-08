# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import logging
import os
from core.parameters import Params
import utilities.open_source.aluminium_office as office

def run(scenario):
    logging.debug('Executing code block: code_1XKH6C5.py')
    # When Excel is skipped, the typing time is kept as idle time.
    skipped = office.excel_skipped(scenario)
    module_folder = os.path.join('scenarios', 'windows', '_library', 'productivity', 'prod_excel_run')
    typing_delay = int(Params.get('global', 'typing_delay'))
    short = Params.get(None, 'short_typing') == '1'
    size = 10 if short else 21
    with open(os.path.join(module_folder, 'TestBookData.txt'), 'r') as myfile:
        data = myfile.read().split()
    index = 0
    for a in range(0, size):
        typing_str = data[index] + '\ue014'
        if a > 9 and a % 10 == 0:
            typing_str += '=AVERAGE(OFFSET(INDIRECT(ADDRESS(ROW(),COLUMN())),-10,0,10,1))'
        else:
            typing_str += data[index + 1]
        typing_str += '\n' + '\ue012'
        index += 2
        if not skipped:
            scenario._send_text(typing_str, typing_delay)
        typing_str_delay = round((len(typing_str) * typing_delay) / 1000 * 2) / 2
        scenario._sleep_by(typing_str_delay + 2)
