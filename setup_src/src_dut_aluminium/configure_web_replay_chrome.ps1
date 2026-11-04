# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Configures Chrome on an Aluminium DUT to trust only web_replay's published leaf SPKI hashes. This is the
# non-rooted Android alternative to installing a user CA. It enables Chrome's command-line file support once,
# writes the allowlist to /data/local/tmp, and restarts Chrome for the active Android user.
#
# Usage:
#   .\configure_web_replay_chrome.ps1 [-Serial <adb serial or ip:port>] [-DeviceIp <DUT Wi-Fi ip>] [-Remove]

param(
    [string]$Serial = "",
    [string]$DeviceIp = "",
    [int]$Port = 8000,
    [switch]$Remove
)

. "$PSScriptRoot\aluminium_common.ps1"

$adb = Get-AdbPath
"Using adb: $adb" | log
$Serial = Get-AluminiumDevice -Adb $adb -Serial $Serial -DeviceIp $DeviceIp
$currentUser = (Invoke-Adb $adb $Serial @("shell", "am get-current-user")).Trim()
if ($currentUser -notmatch "^\d+$") {
    fail "Could not determine the active Android user on $($Serial): $currentUser"
}

$chromePath = Invoke-Adb $adb $Serial @("shell", "pm path --user $currentUser com.android.chrome") -AllowFailure
if ($chromePath -notmatch "package:") {
    fail "Chrome is not installed for Android user $currentUser."
}

$trust = Invoke-Adb $adb $Serial @("shell", "dumpsys trust")
$lockedLine = $trust -split "`r?`n" | Where-Object { $_ -match "\(id=$currentUser,.*deviceLocked=" } | Select-Object -First 1
if (-not $lockedLine) {
    fail "Could not determine whether Android user $currentUser is unlocked. Unlock the DUT and retry."
}
if ($lockedLine -match "deviceLocked=1") {
    fail "Android user $currentUser is locked. Unlock the DUT before configuring Chrome; this script will not bypass the screen lock."
}

$dutIp = $DeviceIp
if (-not $dutIp) {
    $dutIp = Get-DeviceIp -Adb $adb -Serial $Serial
}
try {
    Invoke-AgentRpc -Ip $dutIp -Port $Port -Method "GetVersion" -Arguments @() | Out-Null
    Invoke-AgentRpc -Ip $dutIp -Port $Port -Method "PluginLoad" -Arguments @(
        "InputInject", "InputInject.Application", "/data/local/tmp/hobl_bin/AluminiumAgent/AluminiumAgent.jar"
    ) | Out-Null
} catch {
    fail "The Aluminium agent is not reachable on the DUT. Restart it with setup_src\src_dut_aluminium\launch_agent.ps1, then retry."
}

function Set-ChromeCommandLineFlag {
    param([ValidateSet("Enabled", "Default")][string]$Selection)

    Invoke-Adb $adb $Serial @("shell", "am start --user $currentUser -W -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n com.android.chrome/com.google.android.apps.chrome.Main") | Out-Null
    Start-Sleep -Seconds 2
    $ctrlL = [string][char]0xE009 + "l"
    Invoke-AgentRpc -Ip $dutIp -Port $Port -Method "PluginCallMethod" -Arguments @("InputInject", "Type", $ctrlL, 80) | Out-Null
    Invoke-AgentRpc -Ip $dutIp -Port $Port -Method "PluginCallMethod" -Arguments @(
        "InputInject", "Type", "chrome://flags/#enable-command-line-on-non-rooted-devices", 60
    ) | Out-Null
    Invoke-AgentRpc -Ip $dutIp -Port $Port -Method "PluginCallMethod" -Arguments @("InputInject", "Type", [string][char]0xE007, 80) | Out-Null
    Start-Sleep -Seconds 5

    $screenWidth = [double](Invoke-AgentRpc -Ip $dutIp -Port $Port -Method "PluginCallMethod" -Arguments @("InputInject", "GetScreenWidth"))
    $screenHeight = [double](Invoke-AgentRpc -Ip $dutIp -Port $Port -Method "PluginCallMethod" -Arguments @("InputInject", "GetScreenHeight"))
    if ($screenWidth -lt 1000 -or $screenHeight -lt 700) {
        throw "Unexpected display size ${screenWidth}x${screenHeight}; refusing coordinate-based Chrome flag setup."
    }

    # Chrome's internal flags page scrolls to the target flag. Select its dropdown and the requested entry.
    $x = [long][math]::Round($screenWidth * 0.667)
    $dropdownY = [long][math]::Round($screenHeight * 0.218)
    $selectionY = if ($Selection -eq "Enabled") {
        [long][math]::Round($screenHeight * 0.280)
    } else {
        [long][math]::Round($screenHeight * 0.245)
    }
    Invoke-AgentRpc -Ip $dutIp -Port $Port -Method "PluginCallMethod" -Arguments @("InputInject", "Tap", $x, $dropdownY, 150, $true, 0, $false) | Out-Null
    Start-Sleep -Milliseconds 500
    Invoke-AgentRpc -Ip $dutIp -Port $Port -Method "PluginCallMethod" -Arguments @("InputInject", "Tap", $x, $selectionY, 150, $true, 0, $false) | Out-Null
    Start-Sleep -Milliseconds 500
}

$debugApp = (Invoke-Adb $adb $Serial @("shell", "settings get global debug_app")).Trim()
if ($debugApp -and $debugApp -ne "null" -and $debugApp -ne "com.android.chrome") {
    fail "A different debug app is configured ($debugApp); refusing to replace it."
}

if ($Remove) {
    try {
        Set-ChromeCommandLineFlag -Selection "Default"
        Invoke-Adb $adb $Serial @("shell", "rm -f /data/local/tmp/chrome-command-line") | Out-Null
        if ($debugApp -eq "com.android.chrome") {
            Invoke-Adb $adb $Serial @("shell", "am clear-debug-app") | Out-Null
        }
        Invoke-Adb $adb $Serial @("shell", "am force-stop --user $currentUser com.android.chrome") | Out-Null
        Invoke-Adb $adb $Serial @("shell", "am start --user $currentUser -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n com.android.chrome/com.google.android.apps.chrome.Main") | Out-Null
    } catch {
        fail "Unable to remove the Chrome web_replay command-line settings: $($_.Exception.Message)"
    }
    "Removed the HOBL Chrome command-line file, reset command-line support to Default, and cleared Chrome's persistent debug-app setting." | log
    Exit 0
}

# Chrome v1.5.0 web_replay leaf-certificate SPKI hashes, documented by the web_replay release.
$spkiHashes = "2FBkVuYq8NvFRbHkFRFnXLd/FJK5tu7m/b+V7s/TUL4=,P0/jlVD2vgAtt9UmEeZf7IrHAva3Fs8N+4V9glmvwkc="
$commandLine = "_ --ignore-certificate-errors-spki-list=$spkiHashes"
$localFile = Join-Path $env:TEMP ("hobl-chrome-command-line-" + [guid]::NewGuid().ToString("N"))
[System.IO.File]::WriteAllText($localFile, $commandLine, [System.Text.UTF8Encoding]::new($false))
try {
    Set-ChromeCommandLineFlag -Selection "Enabled"
    if ($debugApp -ne "com.android.chrome") {
        Invoke-Adb $adb $Serial @("shell", "am set-debug-app --persistent com.android.chrome") | Out-Null
    }
    Invoke-Adb $adb $Serial @("push", $localFile, "/data/local/tmp/chrome-command-line") | Out-Null

    # Force-stop/relaunch applies the Chrome flag change and the scoped SPKI allowlist in one restart.
    Invoke-Adb $adb $Serial @("shell", "am force-stop --user $currentUser com.android.chrome") | Out-Null
    Invoke-Adb $adb $Serial @("shell", "am start --user $currentUser -W -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n com.android.chrome/com.google.android.apps.chrome.Main") | Out-Null
    Start-Sleep -Seconds 3
    $ctrlL = [string][char]0xE009 + "l"
    Invoke-AgentRpc -Ip $dutIp -Port $Port -Method "PluginCallMethod" -Arguments @("InputInject", "Type", $ctrlL, 80) | Out-Null
    Invoke-AgentRpc -Ip $dutIp -Port $Port -Method "PluginCallMethod" -Arguments @("InputInject", "Type", "chrome://version", 60) | Out-Null
    Invoke-AgentRpc -Ip $dutIp -Port $Port -Method "PluginCallMethod" -Arguments @("InputInject", "Type", [string][char]0xE007, 80) | Out-Null
} catch {
    fail "Chrome command-line setup failed: $($_.Exception.Message)"
} finally {
    Remove-Item -LiteralPath $localFile -Force -ErrorAction SilentlyContinue
}

"Chrome is configured for Android user $currentUser with the web_replay SPKI allowlist." | log
"Chrome's About Version page is open for verification. The page should show --ignore-certificate-errors-spki-list in Command Line." | log
"This is a scoped certificate exception; it does not install or trust a general-purpose root CA." | log
Exit 0
