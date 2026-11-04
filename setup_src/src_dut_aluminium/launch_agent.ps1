# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Starts (or restarts) the HOBL agent on an Aluminium (Android desktop) DUT.
# HOBL runs this automatically while waiting for a DUT that rebooted or shut down; it can also be run by hand.
#
# Usage:
#   .\launch_agent.ps1 [-Serial <adb serial or ip:port>] [-DeviceIp <DUT Wi-Fi ip>] [-HostIp <host ip>] [-Port 8000] [-AllowAny]

param(
    [string]$Serial = "",
    [string]$DeviceIp = "",
    [string]$HostIp = "",
    [int]$Port = 8000,
    [switch]$AllowAny
)

. "$PSScriptRoot\aluminium_common.ps1"

$adb = Get-AdbPath
"Using adb: $adb" | log
$Serial = Get-AluminiumDevice -Adb $adb -Serial $Serial -DeviceIp $DeviceIp

$deviceIp = Get-DeviceIp -Adb $adb -Serial $Serial
if (-not $HostIp) { $HostIp = Get-HostIp -DeviceIp $deviceIp }
"DUT $Serial has IP $deviceIp; host IP is $HostIp" | log

$existing = Invoke-Adb $adb $Serial @("shell", "ls $AgentJar") -AllowFailure
if ($existing -notmatch [regex]::Escape($AgentJar) -or $existing -match "No such file") {
    fail "Agent not found at $AgentJar on the DUT.  Run dut_setup_aluminium.ps1 first."
}

# Stop any running agent so the new one can listen on the port.  app_process sets the agent's command line, not
# its process name ("main"), so match the start of the command line.  The anchor keeps it from matching this shell.
$agentPattern = "'^$AgentProcessName'"
Invoke-Adb $adb $Serial @("shell", "pkill -f $agentPattern") -AllowFailure | Out-Null
$running = $null
for ($i = 0; $i -lt 10; $i++) {
    $running = Invoke-Adb $adb $Serial @("shell", "pgrep -f $agentPattern") -AllowFailure
    if (-not $running) { break }
    Start-Sleep -Milliseconds 500
}
if ($running) {
    fail "Unable to stop the agent already running on the DUT (process $($running -replace '\s+', ' ')).  Restart the DUT and run this script again."
}

$allow = if ($AllowAny) { "--allow-any" } else { "--allow $HostIp" }
# setsid and nohup detach the agent from the ADB session, so it keeps running after USB is unplugged.
$launch = "CLASSPATH=$AgentJar setsid nohup app_process / --nice-name=$AgentProcessName com.microsoft.hobl.agent.Server --port $Port $allow --log $AgentDir/agent.log > /dev/null 2>&1 < /dev/null &"
"Starting agent: $launch" | log
Invoke-Adb $adb $Serial @("shell", $launch) | Out-Null

# Confirm the agent responds over the network, the same way the HOBL host will reach it.
$version = $null
for ($i = 0; $i -lt 10 -and -not $version; $i++) {
    Start-Sleep -Seconds 1
    $version = Test-Agent -Ip $deviceIp -Port $Port
}
if (-not $version) {
    $running = Invoke-Adb $adb $Serial @("shell", "pgrep -f $agentPattern") -AllowFailure
    if (-not $running) {
        fail "The agent did not start.  See $AgentDir/agent.log on the DUT: adb shell cat $AgentDir/agent.log"
    }
    fail "The agent is running but not reachable at $($deviceIp):$Port.  Make sure the host and DUT are on the same subnet, and the network does not isolate clients."
}
"Agent $version is running.  Use dut_ip=$deviceIp and platform=Aluminium in the HOBL profile." | log
Exit 0
