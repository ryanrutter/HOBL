# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Play the JEITA battery life test video
#
# Setup instructions:
#   Run al_lvp_jeita_prep first.
##

from core.parameters import Params
Params.setOverride("al_lvp_jeita", "video_file", "JB3_0-MOVIE.mp4")
Params.setOverride("al_lvp_jeita", "airplane_mode", "0")
Params.setDefault("al_lvp_jeita", "duration", "300", desc="Time to play the video in seconds")
import scenarios.aluminium.al_lvp


class AlLvpJeita(scenarios.aluminium.al_lvp.AlLvp):
    """
    Plays a video in full screen mode in accordance with requirements set by the Japan Electronics and Information Technology Industries Association for battery operated electronic devices being released in Japan, the Aluminium version of the Windows lvp_jeita scenario.

    Please do not alter parameters as they have been set to meet the requirements of that governing body.
    """
    module = __module__.split('.')[-1]
    prep_scenarios = ["al_lvp_jeita_prep"]
