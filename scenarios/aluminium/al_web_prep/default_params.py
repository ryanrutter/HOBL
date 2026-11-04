# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from core.parameters import Params
from utilities.open_source.modules import import_run_user_only


def run():
    Params.setCalculated('scenario_section', __package__.split('.')[-1])
    run_user_only()


def run_user_only():
    for name in ['web_close_browser', 'web_clear_cache', 'web_first_run', 'web_live_mode', 'web_setup']:
        import_run_user_only(f'scenarios\\aluminium\\_library\\web\\{name}')
