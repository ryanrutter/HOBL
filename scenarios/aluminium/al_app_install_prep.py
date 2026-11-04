# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

##
# Install the Android apps that HOBL scenarios use from the Play Store
#
# Setup instructions:
#   The DUT must be signed in to a Google account, so the Play Store can install apps.
##

import logging
import time
import core.app_scenario
from core.parameters import Params
import utilities.open_source.aluminium_ui as ui


# Apps used by Aluminium scenarios, by the name used in the "apps" parameter.  Word, Excel, PowerPoint, Outlook,
# and OneNote are the apps the Windows productivity scenario uses.
APP_PACKAGES = {
    "netflix": "com.netflix.mediaclient",
    "word": "com.microsoft.office.word",
    "excel": "com.microsoft.office.excel",
    "powerpoint": "com.microsoft.office.powerpoint",
    "outlook": "com.microsoft.office.outlook",
    "onenote": "com.microsoft.office.onenote",
    "teams": "com.microsoft.teams",
    "onedrive": "com.microsoft.skydrive",
}

INSTALLED_LABELS = ["Open", "Uninstall", "Play"]
INSTALL_LABELS = ["Install", "Update"]


class AlAppInstallPrep(core.app_scenario.Scenario):
    '''
    Installs the Android apps used by HOBL scenarios from the Play Store on an Aluminium (Android desktop) DUT, for the active Android user.  Apps that are already installed are left unchanged.  The DUT must be signed in to a Google account.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'apps', " ".join(APP_PACKAGES), desc="Space-separated apps to install: " + ", ".join(APP_PACKAGES), multiple=True)
    Params.setDefault(module, 'install_timeout', '900', desc="Seconds to wait for each app to download and install.")

    is_prep = True

    def runTest(self):
        apps = Params.get(self.module, 'apps').split()
        unknown = [app for app in apps if app not in APP_PACKAGES]
        if unknown:
            self.fail("Unknown apps in al_app_install_prep:apps: " + ", ".join(unknown))
        self.timeout = int(Params.get(self.module, 'install_timeout'))
        self.user = self._call(["am", "get-current-user"]).strip()

        try:
            for app in apps:
                self.install(app, APP_PACKAGES[app])
        finally:
            self._call(["am", f"force-stop --user {self.user} com.android.vending"], expected_exit_code="")
            self._call(["input", "keyevent KEYCODE_HOME"], expected_exit_code="")

        self.createPrepStatusControlFile()

    def installed_version(self, package):
        output = self._call(["sh", f"-c \"pm path --user {self.user} {package} >/dev/null 2>&1 && dumpsys package {package} 2>/dev/null | grep -m1 versionName\""], expected_exit_code="", log_output=False)
        if Params.getCalculated("last_call_exit_code") != "0":
            return None
        line = next((line for line in output.splitlines() if "versionName=" in line), "")
        return line.split("=", 1)[-1].strip() or "unknown"

    def install(self, app, package):
        version = self.installed_version(package)
        if version:
            logging.info(f"{app}: {package} {version} is already installed")
            return

        logging.info(f"{app}: installing {package} from the Play Store")
        self._call(["am", f"start --user {self.user} -a android.intent.action.VIEW -d market://details?id={package} -p com.android.vending"])
        root, button = ui.wait_for(self, INSTALL_LABELS + INSTALLED_LABELS, timeout=60)
        if button is None:
            self.fail(f"The Play Store page for {package} has no Install button.  The app may not be available for this device or account; check the Play Store on the DUT.")
        if button.get("text") in INSTALL_LABELS or button.get("content-desc") in INSTALL_LABELS:
            ui.tap(self, button)

        deadline = time.time() + self.timeout
        while time.time() < deadline:
            version = self.installed_version(package)
            if version:
                logging.info(f"{app}: installed {package} {version}")
                return
            # The first install for a Google account asks to complete the account setup, offering an optional
            # payment method, which is skipped.
            root = ui.read_ui(self)
            if ui.find(root, "Complete account setup") is not None:
                prompt = ui.find(root, ["Skip", "Continue"])
                if prompt is not None:
                    logging.info(f"Play Store: {prompt.get('text')} in the account setup prompt")
                    ui.tap(self, prompt, settle=3)
                    continue
            time.sleep(10)
        self.fail(f"{package} was not installed within {self.timeout} seconds.")

    def kill(self):
        self._call(["am", "force-stop com.android.vending"], expected_exit_code="")
        return 0
