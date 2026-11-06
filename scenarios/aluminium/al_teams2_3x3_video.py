# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from core.parameters import Params
Params.setParam("teams", "duration", "600")
Params.setParam("teams", "send_video", "1")
Params.setParam("teams", "send_audio", "1")
Params.setParam("teams", "send_screen", "0")
Params.setParam("teams", "number_of_bots", "9")
Params.setParam("teams", "bots_send_video", "1")
Params.setParam("teams", "bots_send_audio", "1")
Params.setParam("teams", "bots_share_screen", "0")
import scenarios.aluminium.al_teams


class Teams3x3Video(scenarios.aluminium.al_teams.AlTeams):
    pass
