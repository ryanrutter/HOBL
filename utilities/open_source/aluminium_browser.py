# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# The web browser used by Aluminium (Android desktop) web scenarios, selected with global:browser like on Windows:
# Chrome, or Edge and its preview channels.

import logging
from core.parameters import Params

# Android package and command-line file of each browser.  Chromium-based browsers on Android read their command-line
# file from /data/local/tmp when they are the debug app and their "Enable command line on non-rooted devices" flag is
# on; HOBL uses it to trust only web_replay's certificates (see setup_src\src_dut_aluminium).
BROWSERS = {
    "chrome": ("Chrome", "com.android.chrome", "chrome-command-line"),
    "edge": ("Edge", "com.microsoft.emmx", "edge-command-line"),
    "edgebeta": ("Edge Beta", "com.microsoft.emmx.beta", "edge-command-line"),
    "edgedev": ("Edge Dev", "com.microsoft.emmx.dev", "edge-command-line"),
    "edgecanary": ("Edge Canary", "com.microsoft.emmx.canary", "edge-command-line"),
}
COMMAND_LINE_DIR = "/data/local/tmp"
# The web_replay v1.5.0 leaf certificate SPKI hashes, the same as configure_web_replay_chrome.ps1.
WEB_REPLAY_SPKI = "2FBkVuYq8NvFRbHkFRFnXLd/FJK5tu7m/b+V7s/TUL4=,P0/jlVD2vgAtt9UmEeZf7IrHAva3Fs8N+4V9glmvwkc="


def key(browser=None):
    browser = browser if browser is not None else (Params.get("global", "browser") or "Chrome")
    return browser.lower().replace(" ", "")


def is_supported(browser=None):
    return key(browser) in BROWSERS


def check(scenario):
    '''Fails the scenario if global:browser isn't a browser Aluminium supports.'''
    if not is_supported():
        names = ", ".join(name.replace(" ", "") for name, _, _ in BROWSERS.values())
        scenario.fail(f"Unsupported browser {Params.get('global', 'browser')} on Aluminium.  Set global:browser to one of: {names}.")


def name(browser=None):
    return BROWSERS[key(browser)][0]


def package(browser=None):
    return BROWSERS[key(browser)][1]


def is_edge(browser=None):
    return key(browser).startswith("edge")


def all_packages():
    return [pkg for _, pkg, _ in BROWSERS.values()]


def current_user(scenario):
    return scenario._call(["am", "get-current-user"]).strip()


def is_installed(scenario):
    output = scenario._call(["pm", f"path --user {current_user(scenario)} {package()}"], expected_exit_code="")
    return "package:" in (output or "")


def launcher(scenario):
    '''The browser's launcher activity, as package/class.'''
    output = scenario._call(["cmd", f"package resolve-activity --brief --user {current_user(scenario)} -c android.intent.category.LAUNCHER {package()}"],
                            expected_exit_code="")
    lines = [line.strip() for line in (output or "").splitlines() if "/" in line]
    if not lines:
        scenario.fail(f"{name()} ({package()}) is not installed on the DUT.")
    return lines[-1]


def kill(scenario):
    scenario._kill(package())


def device_time(scenario):
    output = scenario._call(["date", "+%s"], expected_exit_code="", fail_on_exception=False, log_output=False)
    return int(output.strip()) if (output or "").strip().isdigit() else 0


def check_not_crashed(scenario, since):
    '''Fails the scenario if the browser crashed since the DUT time "since", with the reason when it is known.  The
    Play Store can deliver a browser build without code for the DUT's processor; it then crashes on every start.'''
    pkg = package()
    output = scenario._call(["logcat", f"-b crash -d -t {since}.000"], expected_exit_code="", fail_on_exception=False,
                            log_output=False) or ""
    if f"Cmdline: {pkg}" not in output and f"Process: {pkg}" not in output and f">>> {pkg}" not in output:
        return
    if "instead of EM_X86_64" in output:
        scenario.fail(f"{name()} ({pkg}) crashes on start: the Play Store installed a build without x86_64 code, so it can't run on "
                      "this x86_64 DUT.  Use an arm64 DUT, or install a build with x86_64 support.")
    scenario.fail(f"{name()} ({pkg}) crashed while starting.  Check logcat -b crash on the DUT.")


def kill_all(scenario):
    '''Stops every supported browser that is installed, for scenario kill() methods.'''
    for pkg in all_packages():
        try:
            scenario._kill(pkg)
        except Exception:
            pass


def use_command_line(scenario):
    '''Makes the browser read its command-line file, so it trusts web_replay's certificates.  Only one app can be the
    debug app, so this is set each time the browser starts.  Chrome's file is written by
    install_web_replay_certs.ps1; Edge's is written here with the same certificates.'''
    _, pkg, file_name = BROWSERS[key()]
    path = f"{COMMAND_LINE_DIR}/{file_name}"
    if is_edge():
        scenario._call(["sh", f"-c \"echo '_ --ignore-certificate-errors-spki-list={WEB_REPLAY_SPKI}' > {path}; chmod 666 {path}\""])
    elif not scenario._call(["sh", f"-c \"[ -f {path} ] && echo yes\""], expected_exit_code="").strip():
        # Without the file, Chrome uses the setting install_web_replay_certs.ps1 made instead.
        return
    debug_app = scenario._call(["settings", "get global debug_app"], expected_exit_code="").strip()
    if debug_app != pkg:
        logging.info(f"Making {name()} the debug app, so it reads {path}")
        scenario._call(["am", f"set-debug-app --persistent {pkg}"])
