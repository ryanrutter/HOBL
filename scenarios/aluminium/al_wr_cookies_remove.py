# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import scenarios.windows.wr_cookies_remove


class AlWrCookiesRemove(scenarios.windows.wr_cookies_remove.WebReplayCookiesRemove):
    '''Removes cookies from the web_replay archive file named by global:web_replay_recording on the Host, for archives recorded from an Aluminium (Android desktop) DUT.'''
