# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from core.parameters import Params
from utilities.open_source.modules import import_run_user_only


def run():
    Params.setCalculated('scenario_section', __package__.split('.')[-1])
    run_user_only()
    Params.setDefault('al_youtube', 'duration', '600', desc='Total scenario duration')
    Params.setDefault('al_youtube', 'loop_duration', '300', desc='YouTube video playback duration before looping (max 480s)')
    Params.setDefault('al_youtube', 'full_screen', '0', desc='Full Screen mode', valOptions=['0', '1'])
    Params.setDefault('al_youtube', 'page_load_time', '15', desc='Seconds to wait for the video page')
    Params.setDefault('al_youtube', 'web_replay', '0', desc='Play the web_replay recording (1) or the live site (0).  The recording does not currently play in Chrome on Aluminium.', valOptions=['0', '1'])
    Params.setParam(None, 'web_replay_run', Params.get('al_youtube', 'web_replay'))


def run_user_only():
    for name in ['web_check', 'web_clear_cache', 'web_close_browser', 'web_enter_address', 'web_kill', 'web_live_mode', 'web_setup', 'web_switch_archive']:
        import_run_user_only(f'scenarios\\aluminium\\_library\\web\\{name}')
