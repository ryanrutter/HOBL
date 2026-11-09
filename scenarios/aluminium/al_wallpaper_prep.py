# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Set the wallpaper of the DUT's test user
#
# Setup instructions:
#   None.
##

import logging
import os
import time
import cv2 as cv
import numpy as np
import core.app_scenario
from core.parameters import Params


IMAGES = os.path.join("utilities", "open_source", "DesktopImages")
TOOL_JAR = os.path.join("utilities", "open_source", "AluminiumAgent", "Output", "AluminiumAgent.jar")
TOOL_CLASS = "com.microsoft.hobl.agent.WallpaperTool"
# Scores of the screen against the wallpaper image, from match_score(), at or above which the wallpaper is shown.  On the
# HP Googlebook 14, the JEITA image scores 0.98 when shown and 0.46 when another wallpaper is shown.
MATCH = 0.8
# Image pixels per screen pixel to try: Android scales a wallpaper to fill an area at least the size of the display
# (on the HP Googlebook 14, the 3840x2400 JEITA image is shown about 1.2 times smaller) and crops it.
SCALES = np.arange(0.5, 2.51, 0.05)


def _gray(image, factor):
    return cv.resize(cv.cvtColor(image, cv.COLOR_BGR2GRAY), None, fx=factor, fy=factor,
                     interpolation=cv.INTER_AREA).astype(np.float32)


def match_score(screen, image):
    '''How closely the desktop in the screenshot (BGR) shows the wallpaper image (BGR), from 0 to 1.  The middle of
    the desktop, which the launcher's icons, widgets and taskbar don't cover, is searched for in the image at each
    scale in SCALES, so it doesn't matter how Android scales and crops the wallpaper.  A plain image, like
    black-background.jpg, is compared by brightness instead.'''
    h, w = screen.shape[:2]
    factor = 480.0 / w
    middle = _gray(screen[int(h * 0.3):int(h * 0.7), int(w * 0.3):int(w * 0.7)], factor)
    if _gray(image, 480.0 / image.shape[1]).std() < 8:
        return max(0.0, 1.0 - abs(float(middle.mean()) - float(_gray(image, 480.0 / image.shape[1]).mean())) / 40.0)
    if middle.std() < 1:
        return 0.0
    best = 0.0
    for scale in SCALES:
        scaled = _gray(image, factor / scale)
        if scaled.shape[0] < middle.shape[0] or scaled.shape[1] < middle.shape[1]:
            continue
        best = max(best, float(cv.matchTemplate(scaled, middle, cv.TM_CCOEFF_NORMED).max()))
    return best


class AlWallpaperPrep(core.app_scenario.Scenario):
    '''
    Sets the wallpaper of the active Android user on an Aluminium (Android desktop) DUT, the Aluminium version of the wallpaper setting of the Windows system_prep scenario.  al_rundown_jeita_prep.ps1 uses it to set the JEITA JB3_0 image for the JEITA plans, as Windows does.

    The image is set for the home and lock screens through Android's wallpaper service, with a helper in the HOBL agent JAR.  It then checks, from a screenshot of the desktop, that the wallpaper is shown: Googlebook builds before CL3B.260622.286 save a new wallpaper but don't show it until the DUT restarts, so the prep fails on them rather than letting a JEITA test run with the wrong wallpaper.  wallpaper=default restores Android's default wallpaper.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'wallpaper', 'default', desc="Image file in utilities\\open_source\\DesktopImages to use as the wallpaper, for example JB3_0-IMAGE.jpg for JEITA tests, or default for Android's default wallpaper.")
    Params.setDefault(module, 'timeout', '30', desc="Seconds to wait for the desktop to show the new wallpaper.")

    is_prep = True

    def runTest(self):
        wallpaper = Params.get(self.module, 'wallpaper').strip()
        image_path = None
        if wallpaper.lower() != "default":
            image_path = os.path.join(IMAGES, wallpaper)
            if not os.path.isfile(image_path):
                self.fail(f"{wallpaper} is not in {IMAGES}.")
        user = self._call(["am", "get-current-user"]).strip()
        tool_dir = self.dut_exec_path + "/al_wallpaper"
        self._call(["mkdir", f"-p {tool_dir}"], expected_exit_code="")
        try:
            self._upload(TOOL_JAR, tool_dir, check_modified=False)
            tool = f"CLASSPATH={tool_dir}/AluminiumAgent.jar app_process / {TOOL_CLASS}"
            if image_path is None:
                self._call(["sh", f"-c \"{tool} clear {user}\""])
                logging.info(f"Restored the default wallpaper of Android user {user}.")
                return
            self._upload(image_path, tool_dir, check_modified=False)
            self._call(["sh", f"-c \"{tool} set {tool_dir}/{wallpaper} {user}\""])
        finally:
            self._call(["rm", f"-rf {tool_dir}"], expected_exit_code="")
        self.check_shown(wallpaper, image_path)

    def check_shown(self, wallpaper, image_path):
        '''Shows the desktop and waits for the screenshot to match the wallpaper image.'''
        image = cv.imread(image_path, cv.IMREAD_COLOR)
        self._call(["input", "keyevent KEYCODE_HOME"])
        deadline = time.time() + float(Params.get(self.module, 'timeout'))
        score = 0.0
        while True:
            time.sleep(2)
            screen = self._capture_screen()
            score = match_score(screen, image)
            if score >= MATCH:
                logging.info(f"The desktop shows {wallpaper} (match {score:.2f}).")
                return
            if time.time() >= deadline:
                break
        self._save_screen("wallpaper_not_shown.png", screen)
        build = self._call(["getprop", "ro.build.id"], expected_exit_code="", fail_on_exception=False).strip()
        self.fail(f"{wallpaper} was set as the wallpaper, but the desktop doesn't show it (match {score:.2f}).  "
                  f"Googlebook builds before CL3B.260622.286 (this DUT has {build or 'an unknown build'}) only show a new "
                  "wallpaper after a restart.  Update the DUT's OS, or restart it, before running JEITA tests.")

    def kill(self):
        return 0
