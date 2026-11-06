# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from core.parameters import Params
from utilities.open_source.modules import import_run_user_only

def run():
    Params.setCalculated('scenario_section', __package__.split('.')[-1])
    run_user_only()
    return

def run_user_only():
    Params.setUserDefault('teams', 'send_video', '1', desc='Set to 1 to have the DUT turn on its camera. Set to 0 to have the DUT camera off.', valOptions=['0', '1'])
    Params.setUserDefault('teams', 'send_audio', '1', desc='Set to 1 to have the DUT have its mic on. Set to 0 to have the DUT be muted.', valOptions=['0', '1'])
    Params.setUserDefault('teams', 'send_screen', '0', desc='Screen sharing from the DUT is not supported on Aluminium. Must be 0.', valOptions=['0'])
    Params.setUserDefault('teams', 'access_key', '-1', desc='The access key for the Teams Bots Server. Contact HOBL Support to inquire for a key.', valOptions=[])
    Params.setUserDefault('teams', 'bots_test_server', '0', desc='For advanced use. Set to 1 to use the testing instance of the bots server. Not Recomended for general use.', valOptions=['0', '1'])
    Params.setUserDefault('teams', 'bots_force_subscribe_resolution', '0', desc='Force the bots to subscribe to a specific video resolution', valOptions=['0', '1080', '720', '480', '360'])
    return
