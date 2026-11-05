# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

"""Power measurements and Perfetto traces for Aluminium DUTs."""

import base64
import csv
import os
import re
import time

from utilities.open_source import aluminium_battery


TRACE_DIR = "/data/misc/perfetto-traces"
TRACE_DURATION_MS = 86_400_000
ATRACE_CATEGORIES = {"am", "binder_driver", "freq", "gfx", "idle", "power", "sched", "view", "wm"}


def read_battery_sample(scenario):
    sample = aluminium_battery.read(scenario)
    if sample[0] <= 0 or sample[1] <= 0:
        raise RuntimeError("The DUT did not report a valid battery charge counter and voltage.")
    return sample


def battery_summary(start, end, started_at, ended_at):
    duration = ended_at - started_at
    charge_used = (start[0] - end[0]) / 1000.0
    rows = [
        ("battery_measured_duration_s", f"{duration:.0f}"),
        ("battery_charge_used_mah", f"{charge_used:.1f}"),
    ]
    if duration > 0 and not start[2] and not end[2] and charge_used > 0:
        current_ma, power_mw = aluminium_battery.average_power(start, end, duration)
        rows.extend([
            ("battery_avg_current_ma", f"{current_ma:.1f}"),
            ("battery_avg_power_mw", f"{power_mw:.0f}"),
        ])
    elif duration > 0 and not start[2] and not end[2]:
        status = "insufficient_charge_counter_resolution" if charge_used == 0 else "charge_counter_increased"
        rows.append(("battery_power_measurement_status", status))
    return rows


def write_rows(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output, lineterminator="\n")
        writer.writerows(rows)


def available_power_channels(scenario):
    output = scenario._call(["dumpsys", "powerstats"], expected_exit_code="", log_output=False)
    return [
        match.group(1)
        for match in re.finditer(r"^\s*ChannelId:\s*\d+,\s*ChannelName:\s*([^,\r\n]+)", output or "", re.MULTILINE)
    ]


def start_perfetto(scenario, name, buffer_size="64mb", categories=()):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
        raise ValueError(f"Invalid Perfetto trace name: {name!r}")
    if categories:
        invalid = set(categories) - ATRACE_CATEGORIES
        if invalid:
            raise ValueError(f"Unsupported Perfetto categories: {', '.join(sorted(invalid))}")
    match = re.fullmatch(r"(\d+)(kb|mb)", buffer_size.lower())
    if not match:
        raise ValueError(f"Invalid Perfetto buffer size: {buffer_size!r}")
    size_kb = int(match.group(1)) * (1024 if match.group(2) == "mb" else 1)

    trace_path = f"{TRACE_DIR}/{name}.pftrace"
    config_path = None
    config = [
        f"buffers {{ size_kb: {size_kb} fill_policy: RING_BUFFER }}",
        'data_sources { config { name: "android.power" } }',
    ]
    if categories:
        atrace = " ".join(f'atrace_categories: "{category}"' for category in sorted(set(categories)))
        config.append(f'data_sources {{ config {{ name: "linux.ftrace" ftrace_config {{ {atrace} }} }} }}')
    config.append(f"duration_ms: {TRACE_DURATION_MS}")
    encoded_config = base64.b64encode("\n".join(config).encode("utf-8")).decode("ascii")
    command = (
        f"mkdir -p {TRACE_DIR} && rm -f {trace_path} && "
        f"echo {encoded_config} | base64 -d | perfetto --background-wait --txt -c - -o {trace_path}"
    )
    output = scenario._call(["sh", f'-c "{command}"'], timeout=60)
    pid_match = re.search(r"(?m)^\s*(\d+)\s*$", output or "")
    if not pid_match:
        raise RuntimeError(f"Perfetto did not return a tracing process ID: {(output or '').strip()}")
    return pid_match.group(1), trace_path, config_path


def stop_perfetto(scenario, pid, trace_path, config_path):
    scenario._call(["kill", f"-INT {pid}"], expected_exit_code="", timeout=30)
    for _ in range(30):
        running = scenario._call(
            ["sh", f'-c "kill -0 {pid} 2>/dev/null && echo running"'],
            expected_exit_code="",
            log_output=False,
        )
        if (running or "").strip() != "running":
            break
        time.sleep(1)
    else:
        raise RuntimeError(f"Perfetto process {pid} did not stop after SIGINT.")

    data_dir = scenario.dut_data_path.replace("\\", "/").rstrip("/")
    destination = f"{data_dir}/{os.path.basename(trace_path)}"
    cleanup = f"rm -f {trace_path}" if not config_path else f"rm -f {trace_path} {config_path}"
    scenario._call(["sh", f'-c "cp {trace_path} {destination} && {cleanup}"'], timeout=60)
    return destination
