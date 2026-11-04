# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Check the Aluminium agent
#
# Setup instructions:
#   Run setup_src\src_dut_aluminium\dut_setup_aluminium.ps1 first.
##

import filecmp
import json
import logging
import os
import shutil
import core.app_scenario
from core.parameters import Params
import core.call_rpc as rpc


class AlAgentCheck(core.app_scenario.Scenario):
    '''
    Checks that the agent on an Aluminium (Android desktop) DUT supports everything HOBL uses.  Run this after comm_check when setting up a new DUT or agent version.

    Steps:

    1. SimpleRemote compatible calls: version, command output, exit codes, and background jobs
    2. File upload and download, including sub-folders and long file names
    3. InputInject screen info and screenshot
    4. InputInject input injection, using input that doesn't change the DUT state
    5. Report results
    '''

    module = __module__.split('.')[-1]

    Params.setOverride("global", "prep_tools", "")
    is_prep = True

    def runTest(self):
        self.failed = False

        self.check("Version", self.checkVersion)
        self.check("Command output", self.checkCommandOutput)
        self.check("Exit code", self.checkExitCode)
        self.check("File transfer", self.checkFileTransfer)
        self.check("Screen info", self.checkScreenInfo)
        self.check("Screenshot", self.checkScreenshot)
        self.check("Input injection", self.checkInput)

        if self.failed:
            self.fail("At least one agent check failed")

    def check(self, name, method):
        try:
            detail = method()
            logging.info(f"{name}:\tOK {detail or ''}")
        except Exception as e:
            logging.error(f"{name}:\tFAIL - {e}")
            self.failed = True

    def checkVersion(self):
        output = json.loads(rpc.call_rpc(self.dut_ip, self.rpc_port, "GetVersion", [], timeout=5))
        if "result" not in output:
            raise Exception(output.get("error", "No result"))
        return f"(version = {output['result']})"

    def checkCommandOutput(self):
        # Uses a background job with a callback to the host when async_comm is enabled.
        output = self._call(["sh", '-c "echo hobl_agent_check"'], timeout=30)
        if "hobl_agent_check" not in output:
            raise Exception("Unexpected output: " + output)

    def checkExitCode(self):
        output = json.loads(rpc.call_rpc(self.dut_ip, self.rpc_port, "RunWithResultAndExitCode", ["sh", '-c "exit 3"'], timeout=30))
        if output.get("result", [""])[0] != "3":
            raise Exception("Unexpected result: " + str(output))

    def checkFileTransfer(self):
        upload_dir = os.path.join(self.result_dir, "agent_check_upload")
        download_dir = os.path.join(self.result_dir, "agent_check_download")
        shutil.rmtree(upload_dir, ignore_errors=True)
        shutil.rmtree(download_dir, ignore_errors=True)

        # Long names need the GNU tar extension used by call_rpc.upload().
        long_name = "long_" + "n" * 120 + ".txt"
        os.makedirs(os.path.join(upload_dir, "sub"))
        with open(os.path.join(upload_dir, "data.csv"), "w") as f:
            f.write("a,b\n1,2\n")
        with open(os.path.join(upload_dir, "sub", long_name), "wb") as f:
            f.write(os.urandom(100000))

        remote_dir = self.dut_data_path.rstrip("/\\") + "/agent_check_upload"
        try:
            self._upload(upload_dir, self.dut_data_path)
            self._copy_data_from_remote(download_dir, source=remote_dir)

            comparison = filecmp.dircmp(upload_dir, download_dir)
            if comparison.left_only or comparison.right_only or comparison.diff_files:
                raise Exception(f"Differences: missing={comparison.left_only} extra={comparison.right_only} changed={comparison.diff_files}")
            if not filecmp.cmp(os.path.join(upload_dir, "sub", long_name), os.path.join(download_dir, "sub", long_name), shallow=False):
                raise Exception("Long file name content differs")
        finally:
            self._call(["rm", "-rf " + remote_dir], expected_exit_code="")

    def checkScreenInfo(self):
        self.load_plugins()
        screens = rpc.plugin_screen_info(self.dut_ip, self.rpc_port, "InputInject")
        width, height, scale = screens[0]
        if width <= 0 or height <= 0 or scale <= 0:
            raise Exception(f"Invalid screen info: {screens}")
        return f"({width} x {height} @ scale {scale})"

    def checkScreenshot(self):
        img = self._capture_screen()
        width, height = self._get_screen_size(self.current_screen)
        if img.shape[0] != height or img.shape[1] != width:
            raise Exception(f"Screenshot is {img.shape[1]} x {img.shape[0]}, expected {width} x {height}")
        self._screenshot(name="agent_check_screen.png")
        return "(saved agent_check_screen.png)"

    def checkInput(self):
        width, height = self._get_screen_size(self.current_screen)
        calls = [
            ["MoveTo", int(width / 2), int(height / 2), 0, False],
            # Zero distance scroll and a Shift press do not change anything on the DUT.
            ["Scroll", int(width / 2), int(height / 2), 0, "up", 0, False],
            ["Type", "\ue008", 0],
            ["EventTag", "al_agent_check"],
        ]
        for call in calls:
            output = rpc.plugin_call(self.dut_ip, self.rpc_port, "InputInject", *call)
            if "error" in json.loads(output):
                raise Exception(f"{call[0]} failed: {json.loads(output)['error']}")

    def kill(self):
        # Nothing is left running by this scenario.
        return 0
