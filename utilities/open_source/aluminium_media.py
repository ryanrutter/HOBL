# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

"""Read the playback state that Android apps publish through their media session.

Chrome and media apps report whether they are playing and the playback position to Android's media session
service.  The position is reported at the time of the last state change, so the current position is extrapolated
from the elapsed time since then, the same way Android's MediaController does.
"""

import re


STATE_NAMES = {
    "0": "NONE", "1": "STOPPED", "2": "PAUSED", "3": "PLAYING", "4": "FAST_FORWARDING", "5": "REWINDING",
    "6": "BUFFERING", "7": "ERROR", "8": "CONNECTING",
}

_STATE = re.compile(
    r"state=PlaybackState \{state=(?P<name>[A-Z_]*)\((?P<code>\d+)\), position=(?P<position>-?\d+), "
    r"buffered position=-?\d+, speed=(?P<speed>[\d.]+), updated=(?P<updated>\d+)"
)


def parse_sessions(dumpsys_output):
    '''Returns {package: (state name, position ms, speed, updated ms)} for the media sessions in "dumpsys media_session".
    When a package has several sessions, the active one is used.'''
    sessions = {}
    package = None
    active = False
    for line in dumpsys_output.splitlines():
        line = line.strip()
        if line.startswith("package="):
            package = line[len("package="):].strip()
            active = False
            continue
        if line.startswith("active="):
            active = line == "active=true"
            continue
        match = _STATE.search(line)
        if match and package and (package not in sessions or (active and not sessions[package][1])):
            sessions[package] = ((
                match.group("name") or STATE_NAMES.get(match.group("code"), match.group("code")),
                int(match.group("position")),
                float(match.group("speed")),
                int(match.group("updated")),
            ), active)
    return {name: value for name, (value, _) in sessions.items()}


def playback(scenario, package):
    '''Returns (state, current position in seconds) for package's media session, or (None, None) without one.'''
    output = scenario._call(["sh", "-c \"dumpsys media_session; cat /proc/uptime\""], log_output=False)
    sessions = parse_sessions(output)
    if package not in sessions:
        return None, None
    state, position, speed, updated = sessions[package]
    uptime_line = output.strip().splitlines()[-1]
    now_ms = float(uptime_line.split()[0]) * 1000
    if state == "PLAYING":
        position += (now_ms - updated) * speed
    return state, position / 1000.0
