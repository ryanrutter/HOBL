# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import csv
import json
import os
import re

import core.app_scenario
import core.call_rpc as rpc
from core.parameters import Params, get_hobl_version


PACKAGES = {
    "Chrome": "com.android.chrome",
    "Android WebView": "com.google.android.webview",
    "Word": "com.microsoft.office.word",
    "Excel": "com.microsoft.office.excel",
    "PowerPoint": "com.microsoft.office.powerpoint",
    "Outlook": "com.microsoft.office.outlook",
    "OneNote": "com.microsoft.office.onenote",
    "Netflix": "com.netflix.mediaclient",
    "Google Photos": "com.google.android.apps.photos",
}


class AlVersionReport(core.app_scenario.Scenario):
    '''Write Aluminium OS, build, architecture, agent, browser, and installed workload versions to the results.'''

    module = __module__.split(".")[-1]
    for key in ("trace", "config_check", "callback_test_begin", "callback_test_end", "callback_data_ready", "tools", "prep_tools"):
        Params.setOverride("global", key, "0" if key in ("trace", "config_check") else "")

    is_prep = True

    def runTest(self):
        report = [
            ("HOBL Version", get_hobl_version().strip()),
            ("Model", self._call(["getprop", "ro.product.model"], log_output=False).strip()),
            ("Android Version", self._call(["getprop", "ro.build.version.release"], log_output=False).strip()),
            ("SDK Version", self._call(["getprop", "ro.build.version.sdk"], log_output=False).strip()),
            ("Build Fingerprint", self._call(["getprop", "ro.build.fingerprint"], log_output=False).strip()),
            ("ABI", self._call(["getprop", "ro.product.cpu.abi"], log_output=False).strip()),
            ("Agent Version", json.loads(rpc.call_rpc(self.dut_ip, self.rpc_port, "GetVersion", [], log=False))["result"]),
        ]
        for label, package in PACKAGES.items():
            output = self._call(["dumpsys", f"package {package}"], expected_exit_code="", log_output=False)
            version = re.search(r"(?m)^\s*versionName=([^\s]+)", output or "")
            report.append((label, version.group(1) if version else "not installed"))

        path = os.path.join(self.result_dir, "VersionInformation.csv")
        with open(path, "w", newline="", encoding="utf-8") as file:
            csv.writer(file, lineterminator="\n").writerows(report)
        self.createPrepStatusControlFile()

    def kill(self):
        return 0
