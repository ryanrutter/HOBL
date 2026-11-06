# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import scenarios.windows.wr_replay_start


class AlWrReplayStart(scenarios.windows.wr_replay_start.WebReplayReplayStart):
    '''
    Starts a web_replay replay server on the Host for global:web_replay_recording and points the Aluminium (Android desktop) DUT's global proxy at it.

    Run workloads with global:web_replay_action=bulk_replay while it is running, then run al_wr_replay_stop.
    '''
