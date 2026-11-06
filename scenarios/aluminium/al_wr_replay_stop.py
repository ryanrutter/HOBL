# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import scenarios.windows.wr_replay_stop


class AlWrReplayStop(scenarios.windows.wr_replay_stop.WebReplayReplayStop):
    '''Stops the web_replay replay server started by al_wr_replay_start and clears the Aluminium (Android desktop) DUT's global proxy.'''
