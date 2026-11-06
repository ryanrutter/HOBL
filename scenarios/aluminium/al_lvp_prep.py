# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Put the Tears of Steel video in the Movies folder of the DUT's test user, for al_lvp
#
# Setup instructions:
#   None.  The video is downloaded to the host's downloads folder the first time.
##

import glob
import logging
import os
import re
import shutil
import subprocess
import zipfile
import core.app_scenario
from core.parameters import Params


VIDEO_URI = "content://media/external/video/media"


def find_ffmpeg():
    '''ffmpeg from PATH, or the copy host_setup downloads into downloads\\ffmpeg_*.'''
    found = shutil.which("ffmpeg")
    if found:
        return found
    for candidate in sorted(glob.glob(os.path.join("downloads", "ffmpeg*", "bin", "ffmpeg.exe"))):
        return os.path.abspath(candidate)
    return None


def find_video(query_output, name):
    '''Returns (id, size) of the MediaStore row named name in "content query" output, or (None, None).'''
    for line in query_output.splitlines():
        if f"_display_name={name}," in line or line.rstrip().endswith(f"_display_name={name}"):
            row_id = re.search(r"\b_id=(\d+)", line)
            size = re.search(r"\b_size=(\d+)", line)
            return (row_id.group(1) if row_id else None), (int(size.group(1)) if size else None)
    return None, None


class AlLvpPrep(core.app_scenario.Scenario):
    '''
    Copies the Tears of Steel video used by the Windows lvp scenario to the Movies folder of the active Android user on an Aluminium (Android desktop) DUT.  The video is stored in an MP4 container without re-encoding, so the video and audio streams are the same as on Windows.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'video_file', 'ToS-4k-1920.mp4', desc="Name of the video file in the host's downloads folder and on the DUT.")
    Params.setDefault(module, 'video_url', 'http://ftp.nluug.nl/pub/graphics/blender/demo/movies/ToS/ToS-4k-1920.mov.zip', desc="Where to download the video if it isn't in the downloads folder.  A .zip or .mov is converted to MP4 without re-encoding.")

    is_prep = True

    def runTest(self):
        video_file = Params.get(self.module, 'video_file')
        source = self.host_video(video_file, Params.get(self.module, 'video_url'))
        size = os.path.getsize(source)
        self.user = self._call(["am", "get-current-user"]).strip()

        row_id, stored_size = self.query(video_file)
        if row_id and stored_size == size:
            logging.info(f"{video_file} is already in the Movies folder of Android user {self.user}.")
            self.createPrepStatusControlFile()
            return
        if row_id:
            logging.info(f"Replacing {video_file}, which has a different size.")
            self._call(["content", f"delete --user {self.user} --uri {VIDEO_URI}/{row_id}"])

        # The shell can't write to the user's storage directly, so the video goes through Android's media store.
        staging_dir = self.dut_exec_path + "/al_lvp"
        staging = staging_dir + "/" + video_file
        logging.info(f"Uploading {video_file} ({size // (1024 * 1024)} MB) to the DUT.")
        self._upload(source, staging_dir)
        try:
            self._call(["content", f"insert --user {self.user} --uri {VIDEO_URI} --bind _display_name:s:{video_file} --bind relative_path:s:Movies/ --bind mime_type:s:video/mp4"])
            row_id, _ = self.query(video_file)
            if not row_id:
                self.fail(f"Could not add {video_file} to the media store of Android user {self.user}.")
            self._call(["sh", f"-c \"content write --user {self.user} --uri {VIDEO_URI}/{row_id} < {staging}\""], timeout=1800)
            # The media store updates the size when it rescans the file.
            self._call(["content", f"update --user {self.user} --uri {VIDEO_URI}/{row_id} --bind _size:l:{size}"], expected_exit_code="", fail_on_exception=False)
            row_id, stored_size = self.query(video_file)
            if stored_size != size:
                self.fail(f"{video_file} was not copied completely ({stored_size} of {size} bytes).")
        finally:
            self._call(["rm", f"-rf {staging_dir}"], expected_exit_code="")

        logging.info(f"Copied {video_file} to the Movies folder of Android user {self.user}.")
        self.createPrepStatusControlFile()

    def query(self, video_file):
        output = self._call(["content", f"query --user {self.user} --uri {VIDEO_URI} --projection _id:_display_name:_size"], expected_exit_code="", log_output=False)
        return find_video(output, video_file)

    def host_video(self, video_file, url):
        path = os.path.join("downloads", video_file)
        if os.path.exists(path):
            return path

        name = url.rsplit("/", 1)[-1]
        download = os.path.join("downloads", name)
        if not os.path.exists(download):
            logging.info(f"Downloading {url}")
            self._check_and_download(name, "downloads", url=url)
        if name.lower().endswith(".zip"):
            with zipfile.ZipFile(download) as archive:
                member = next((m for m in archive.namelist() if m.lower().endswith((".mov", ".mp4"))), None)
                if not member:
                    self.fail(f"{download} does not contain a video.")
                archive.extract(member, os.path.join("downloads", "lvp_extract"))
                download = os.path.join("downloads", "lvp_extract", member)

        if download.lower().endswith(".mp4"):
            # A direct .mp4 URL with the same name is downloaded to path itself.
            if os.path.abspath(download) != os.path.abspath(path):
                shutil.copyfile(download, path)
            return path
        ffmpeg = find_ffmpeg()
        if not ffmpeg:
            self.fail("ffmpeg was not found.  Run host_setup.exe, or put ffmpeg on PATH.")
        logging.info(f"Converting {download} to MP4 without re-encoding.")
        subprocess.run([ffmpeg, "-v", "error", "-y", "-i", download, "-c", "copy", "-movflags", "+faststart", path], check=True)
        return path

    def kill(self):
        return 0
