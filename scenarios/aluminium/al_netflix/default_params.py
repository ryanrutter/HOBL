# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from core.parameters import Params
from utilities.open_source.modules import import_run_user_only


def run():
    Params.setCalculated('scenario_section', __package__.split('.')[-1])
    run_user_only()
    Params.setDefault('al_netflix', 'duration', '600', desc='Seconds to play the video')
    Params.setDefault('al_netflix', 'page_load_time', '20', desc='Seconds to wait for each Netflix page')
    Params.setDefault('netflix', 'netflix_username', '', desc='Netflix account, the same setting as the Windows netflix scenario')
    Params.setDefault('netflix', 'netflix_password', '', desc='Netflix account password')
    Params.setParam(None, 'web_replay_run', '0')


def run_user_only():
    for name in ['web_clear_cache', 'web_close_browser', 'web_enter_address', 'web_kill', 'web_live_mode', 'web_setup']:
        import_run_user_only(f'scenarios\\aluminium\\_library\\web\\{name}')
