# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Play a local video
#
# Setup instructions:
#   al_lvp_prep copies the video to the DUT.  Run it first, or run the prep scenario with prep:scenarios_to_prep=al_lvp.
##

import logging
import re
import time
import core.app_scenario
from core.parameters import Params
from scenarios.aluminium.al_lvp_prep import VIDEO_URI, find_video


PHOTOS = "com.google.android.apps.photos"
PHOTOS_VIEWER = PHOTOS + "/.pager.HostPhotoPagerActivity"


def audio_playing(dumpsys_audio, uid):
    '''True if an audio player of uid is started in "dumpsys audio" output.'''
    for line in dumpsys_audio.splitlines():
        if "AudioPlaybackConfiguration" in line and f"u/pid:{uid}/" in line and "state:started" in line:
            return True
    return False


class AlLvp(core.app_scenario.Scenario):
    '''
    Plays the Tears of Steel video full screen with the Google Photos video player on an Aluminium (Android desktop) DUT, the Aluminium version of the Windows lvp scenario.  The video starts again when it ends, like Windows' repeat setting.  Playback is checked every 30 seconds with Android's audio playback state.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'video_file', 'ToS-4k-1920.mp4', desc="The file name of the video, copied to the Movies folder by al_lvp_prep.")
    Params.setDefault(module, 'duration', '300', desc="Time to play the video in seconds")
    Params.setDefault(module, 'airplane_mode', '0', desc="Not supported on Aluminium: airplane mode would disconnect the HOBL agent.", valOptions=["0"])

    prep_scenarios = ["al_lvp_prep"]
    check_interval = 30

    def setUp(self):
        self.duration = float(Params.get(self.module, 'duration'))
        if Params.get('global', 'training_mode') == "1":
            self.duration = 10
        if Params.get(self.module, 'airplane_mode') != "0":
            self.fail("al_lvp:airplane_mode is not supported on Aluminium, since airplane mode would disconnect the HOBL agent.")

        video_file = Params.get(self.module, 'video_file')
        self.user = self._call(["am", "get-current-user"]).strip()
        query = self._call(["content", f"query --user {self.user} --uri {VIDEO_URI} --projection _id:_display_name:_size"], expected_exit_code="", log_output=False)
        row_id, _ = find_video(query, video_file)
        if not row_id:
            self.fail(f"{video_file} is not in the Movies folder.  Run al_lvp_prep first.")
        self.video_uri = f"{VIDEO_URI}/{row_id}"
        uid_output = self._call(["cmd", f"package list packages -U --user {self.user} {PHOTOS}"], expected_exit_code="")
        uid = re.search(r"uid:(\d+)", uid_output)
        if not uid:
            self.fail("Google Photos, the Android video player, is not installed for the test user.")
        self.photos_uid = uid.group(1)

        # Android shows a one-time hint, which dims the screen, the first time an app goes full screen.
        self._call(["settings", "put secure immersive_mode_confirmations confirmed"])
        self.play()
        # Match the Windows lvp timing, which starts measuring 10 seconds after playback starts.
        time.sleep(10)
        core.app_scenario.Scenario.setUp(self)

    def play(self):
        logging.info("Starting the video")
        self._call(["am", f"force-stop --user {self.user} {PHOTOS}"])
        self._call(["am", f"start --user {self.user} -W --windowingMode 1 -a android.intent.action.VIEW -d {self.video_uri} -t video/mp4 -n {PHOTOS_VIEWER}"])
        deadline = time.time() + 20
        while time.time() < deadline:
            if self.is_playing():
                return
            time.sleep(2)
        self.fail("The video did not start playing in Google Photos.")

    def is_playing(self):
        return audio_playing(self._call(["dumpsys", "audio"], log_output=False), self.photos_uid)

    def runTest(self):
        logging.info(f"Duration: {self.duration:.0f} sec.")
        end = time.time() + self.duration
        stopped_checks = 0
        while time.time() < end:
            time.sleep(min(self.check_interval, max(0, end - time.time())))
            if time.time() >= end:
                break
            if self.is_playing():
                stopped_checks = 0
                continue
            stopped_checks += 1
            # The 12 minute video has ended, so it starts again, like Windows' repeat setting.
            if stopped_checks >= 2:
                self.fail("The video stopped and could not be restarted.")
            self.play()
        if not self.is_playing():
            self.fail("The video was not playing at the end of the test.")

    def tearDown(self):
        core.app_scenario.Scenario.tearDown(self)
        self._call(["am", f"force-stop --user {self.user} {PHOTOS}"], expected_exit_code="")

    def kill(self):
        try:
            self._call(["am", f"force-stop {PHOTOS}"], expected_exit_code="")
        except Exception:
            pass
        return 0
