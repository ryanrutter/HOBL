# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import scenarios.windows.wr_record_start


class AlWrRecordStart(scenarios.windows.wr_record_start.WebReplayRecordStart):
    '''
    Starts a web_replay recording server on the Host and points the Aluminium (Android desktop) DUT's global proxy at it.

    Set global:web_replay_recording to the archive to record; use a new name so an existing archive isn't overwritten.  Run the workload with global:web_replay_action=bulk_record, then run al_wr_record_stop.
    '''
