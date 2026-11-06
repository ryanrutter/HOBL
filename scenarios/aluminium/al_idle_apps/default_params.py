# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from core.parameters import Params
from utilities.open_source.modules import import_run_user_only


def run():
    Params.setCalculated('scenario_section', __package__.split('.')[-1])
    run_user_only()
    Params.setDefault('al_idle_apps', 'idle_time', '111', desc='Idle time between each app switch, - 3s', valOptions=[])
    Params.setParam(None, 'web_replay_run', '1')


def run_user_only():
    import_run_user_only('scenarios\\aluminium\\_library\\productivity\\prod_close')
    import_run_user_only('scenarios\\aluminium\\_library\\productivity\\prod_idle')
    import_run_user_only('scenarios\\aluminium\\_library\\productivity\\prod_kill')
    import_run_user_only('scenarios\\aluminium\\_library\\productivity\\prod_open')
    import_run_user_only('scenarios\\aluminium\\_library\\productivity\\prod_setup')
    import_run_user_only('scenarios\\aluminium\\_library\\web\\web_close_browser')
    import_run_user_only('scenarios\\aluminium\\_library\\web\\web_close_tabs')
    import_run_user_only('scenarios\\aluminium\\_library\\web\\web_kill')
    import_run_user_only('scenarios\\aluminium\\_library\\web\\web_run')
    import_run_user_only('scenarios\\aluminium\\_library\\web\\web_setup')
    import_run_user_only('scenarios\\aluminium\\_library\\web\\web_switchto')
