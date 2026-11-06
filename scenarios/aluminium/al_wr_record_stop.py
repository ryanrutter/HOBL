# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import scenarios.windows.wr_record_stop


class AlWrRecordStop(scenarios.windows.wr_record_stop.WebReplayRecordStop):
    '''Stops the web_replay recording server started by al_wr_record_start and clears the Aluminium (Android desktop) DUT's global proxy.'''
