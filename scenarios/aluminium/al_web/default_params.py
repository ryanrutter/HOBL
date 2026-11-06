# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from core.parameters import Params
from utilities.open_source.modules import import_run_user_only


def run():
    Params.setCalculated('scenario_section', __package__.split('.')[-1])
    run_user_only()
    Params.setDefault('al_web', 'loops', '1', desc='Number of browser loops')
    Params.setDefault('al_web', 'youtube_duration', '90', desc='Expected archived YouTube playback duration checked by web_check')
    Params.setParam(None, 'web_replay_run', '1')
    Params.setParam(None, 'phase_reporting', '1')


def run_user_only():
    for name in ['web_check', 'web_close_browser', 'web_close_tabs', 'web_kill', 'web_run', 'web_setup']:
        import_run_user_only(f'scenarios\\aluminium\\_library\\web\\{name}')
