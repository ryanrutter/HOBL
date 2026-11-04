# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Sets up an Aluminium (Android desktop) DUT for HOBL.  Runs on the HOBL host and configures the DUT
# over ADB; nothing needs to be installed on the DUT itself.  Re-running is safe.
#
# Prerequisites (see docs\support\docs\HOBL_Setup.md, "DUT Setup For Aluminium"):
#   - Android SDK Platform-Tools (adb) on the host.
#   - Developer options and USB debugging (or Wireless debugging) enabled on the DUT.
#
# Usage:
#   .\dut_setup_aluminium.ps1 [-Serial <adb serial or ip:port>] [-HostIp <host ip>] [-Port 8000] [-AllowAny] [-AgentPath <path to AluminiumAgent.jar>]
#                             [-ProfilePath <device profile .ini>] [-SkipWirelessDebugging]
#
# With -ProfilePath, the DUT joins the Wi-Fi network in the profile's dut_wifi_name and dut_wifi_password, and
# the script checks that the profile's dut_ip matches the DUT.  Over USB, Wireless debugging is turned on and
# connected, so the USB cable can be removed afterwards; use -SkipWirelessDebugging to leave it unchanged.

param(
    [string]$Serial = "",
    [string]$HostIp = "",
    [int]$Port = 8000,
    [switch]$AllowAny,
    [string]$AgentPath = "",
    [string]$ProfilePath = "",
    [switch]$SkipWirelessDebugging
)

. "$PSScriptRoot\aluminium_common.ps1"

if (-not $AgentPath) {
    $AgentPath = Join-Path $PSScriptRoot "..\..\utilities\open_source\AluminiumAgent\Output\AluminiumAgent.jar"
}
if (-not (Test-Path $AgentPath)) {
    fail "Agent not found at $AgentPath.  Build it with utilities\open_source\AluminiumAgent\build_aluminium.cmd."
}
$AgentPath = (Resolve-Path $AgentPath).Path
if ($ProfilePath -and -not (Test-Path -LiteralPath $ProfilePath)) {
    fail "Device profile not found: $ProfilePath"
}

$adb = Get-AdbPath
"Using adb: $adb" | log
$Serial = Get-AluminiumDevice -Adb $adb -Serial $Serial

# Describe the DUT
$release = Invoke-Adb $adb $Serial @("shell", "getprop ro.build.version.release")
if (-not $release) { fail "Device $Serial does not look like an Android device." }
$model = Invoke-Adb $adb $Serial @("shell", "getprop ro.product.model")
$abi = Invoke-Adb $adb $Serial @("shell", "getprop ro.product.cpu.abi")
$build = Invoke-Adb $adb $Serial @("shell", "getprop ro.build.display.id")
"DUT: $model, Android $release, $abi, build $build" | log

if ($ProfilePath) {
    $wifiName = Get-ProfileValue -ProfilePath $ProfilePath -Section "global" -Key "dut_wifi_name"
    if ($wifiName) {
        $wifiPassword = Get-ProfileValue -ProfilePath $ProfilePath -Section "global" -Key "dut_wifi_password"
        $wifiAuthentication = Get-ProfileValue -ProfilePath $ProfilePath -Section "global" -Key "dut_wifi_authentication"
        Connect-DutWifi -Adb $adb -Serial $Serial -Name $wifiName -Password $wifiPassword -Authentication $wifiAuthentication
    } else {
        "Wi-Fi: dut_wifi_name is not set in the profile, so the current network is kept" | log
    }
    $profileIp = Get-ProfileValue -ProfilePath $ProfilePath -Section "global" -Key "dut_ip"
    $deviceIp = Get-DeviceIp -Adb $adb -Serial $Serial
    if ($profileIp -and $profileIp -ne $deviceIp) {
        " WARNING - The DUT's address is $deviceIp, but dut_ip in the profile is $profileIp.  Update the profile, or reserve the address in the router's DHCP settings." | log
    }
}

# Install the agent.  It is a single architecture independent file.
"Installing agent to $AgentDir" | log
Invoke-Adb $adb $Serial @("shell", "mkdir -p $AgentDir $DataDir") | Out-Null
Invoke-Adb $adb $Serial @("push", $AgentPath, $AgentJar) | log

# Equivalent of the power settings applied by the Windows dut_setup: the display never turns off and
# the lock screen is disabled, so automation is not interrupted.  Adaptive brightness is turned off
# so the display tool can set a fixed brightness.
"Applying test settings" | log
Invoke-Adb $adb $Serial @("shell", "settings put system screen_off_timeout 2147483647") | Out-Null
Invoke-Adb $adb $Serial @("shell", "settings put system screen_brightness_mode 0") | Out-Null
$lock = Invoke-Adb $adb $Serial @("shell", "locksettings set-disabled true") -AllowFailure
if ($LASTEXITCODE -ne 0) {
    " WARNING - Could not disable the lock screen ($lock).  Remove the screen lock PIN or password in Settings > Security, then run this script again." | log
}

# Start the agent
& "$PSScriptRoot\launch_agent.ps1" -Serial $Serial -HostIp $HostIp -Port $Port -AllowAny:$AllowAny
if ($LASTEXITCODE -ne 0) { Exit $LASTEXITCODE }

# Over USB, also set up Wireless debugging, which HOBL uses to relaunch the agent after the DUT restarts.
if (-not $SkipWirelessDebugging -and -not (Test-WirelessSerial $Serial)) {
    $wirelessSerial = Enable-WirelessDebugging -Adb $adb -Serial $Serial -DeviceIp (Get-DeviceIp -Adb $adb -Serial $Serial)
    "Wireless debugging is ready ($wirelessSerial).  The USB cable can now be removed." | log
}

"DUT setup complete.  If USB was used, unplug it before measuring, since it charges the DUT." | log
"Next, run the comm_check and al_agent_check scenarios." | log
Exit 0
