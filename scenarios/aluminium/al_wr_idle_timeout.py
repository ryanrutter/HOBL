# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import scenarios.windows.wr_idle_timeout


class AlWrIdleTimeout(scenarios.windows.wr_idle_timeout.WebReplayIdleTimeout):
    '''
    Adds the server idle timeouts in the Host's web_replay recordings\\idle_timeouts.json to the archive named by global:web_replay_recording.

    On Windows, idle_timeouts.json comes from a Microsoft Edge netlog capture.  Chrome on Aluminium (Android desktop) can't be started with a netlog, so the file must come from a Windows recording of the same sites.
    '''
