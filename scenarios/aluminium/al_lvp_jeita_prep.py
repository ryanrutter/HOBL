# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Put the JEITA battery life test video in the Movies folder of the DUT's test user, for al_lvp_jeita
#
# Setup instructions:
#   None.  The video is downloaded from JEITA to the host's downloads folder the first time.
##

from core.parameters import Params
Params.setOverride("al_lvp_jeita_prep", "video_file", "JB3_0-MOVIE.mp4")
Params.setOverride("al_lvp_jeita_prep", "video_url", "https://home.jeita.or.jp/page_file/JB3_0-MOVIE.mp4")
import scenarios.aluminium.al_lvp_prep


class AlLvpJeitaPrep(scenarios.aluminium.al_lvp_prep.AlLvpPrep):
    '''
    Copies the JEITA JB3_0 battery life test video to the Movies folder of the active Android user on an Aluminium (Android desktop) DUT, the Aluminium version of the Windows lvp_jeita_prep scenario.
    '''
    module = __module__.split('.')[-1]
    is_prep = True
