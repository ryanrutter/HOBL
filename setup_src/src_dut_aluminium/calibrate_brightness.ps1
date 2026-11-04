# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Finds the display brightness that gives the HOBL target luminance (150 nits by default) on an Aluminium DUT,
# and optionally writes the result to the device profile as display:nits_map.
#
# The DUT shows a full-screen white page in Chrome, served by the DUT itself on its loopback address.  For each brightness the script tries, measure the
# luminance with a luminance meter (average of the center and the four corners) and type the reading.  Labs with
# a scriptable meter can pass -MeterCommand, a host command that prints the measured nits, to run unattended.
# Brightness percentages map to Android's 0-255 brightness setting the same way as HOBL's display tool.
#
# Usage:
#   .\calibrate_brightness.ps1 -DeviceIp <dut ip> [-Serial <adb serial>] [-TargetNits 150[,200]] [-Tolerance 3]
#                              [-ProfilePath <device profile .ini>] [-MeterCommand "<command that prints nits>"]

param(
    [string]$Serial = "",
    [string]$DeviceIp = "",
    [int]$Port = 8000,
    [int[]]$TargetNits = @(150),
    [double]$Tolerance = 3,
    [int]$MaxSteps = 10,
    [string]$ProfilePath = "",
    [string]$MeterCommand = ""
)

. "$PSScriptRoot\aluminium_common.ps1"

if ($ProfilePath -and -not (Test-Path -LiteralPath $ProfilePath)) {
    fail "Device profile not found: $ProfilePath"
}

$adb = Get-AdbPath
$Serial = Get-AluminiumDevice -Adb $adb -Serial $Serial -DeviceIp $DeviceIp
if (-not $DeviceIp) { $DeviceIp = Get-DeviceIp -Adb $adb -Serial $Serial }
$currentUser = (Invoke-Adb $adb $Serial @("shell", "am get-current-user")).Trim()

try {
    Invoke-AgentRpc -Ip $DeviceIp -Port $Port -Method "PluginLoad" -Arguments @(
        "InputInject", "InputInject.Application", $AgentJar
    ) | Out-Null
} catch {
    fail "The Aluminium agent is not reachable on the DUT.  Restart it with setup_src\src_dut_aluminium\launch_agent.ps1, then retry."
}

function Send-Keys {
    param([string]$Text, [int]$Delay = 60)
    Invoke-AgentRpc -Ip $DeviceIp -Port $Port -Method "PluginCallMethod" -Arguments @("InputInject", "Type", $Text, $Delay) | Out-Null
}

function Set-Brightness {
    param([int]$Percent)
    $value = [int][math]::Round($Percent * 255 / 100)
    Invoke-Adb $adb $Serial @("shell", "settings put system screen_brightness $value") | Out-Null
}

function Read-Luminance {
    param([int]$Percent)
    if ($MeterCommand) {
        $output = (& cmd.exe /c $MeterCommand 2>&1 | Out-String).Trim()
        if ($LASTEXITCODE -ne 0 -or $output -notmatch '(\d+(\.\d+)?)\s*$') {
            fail "The meter command failed or didn't print a number: $output"
        }
        return [double]$Matches[1]
    }
    while ($true) {
        $answer = Read-Host "Brightness $Percent%: enter the measured nits (average of the center and the four corners)"
        $value = 0.0
        if ([double]::TryParse($answer, [ref]$value) -and $value -ge 0) { return $value }
        "Enter a number, for example 148.5" | log
    }
}

$savedBrightness = (Invoke-Adb $adb $Serial @("shell", "settings get system screen_brightness")).Trim()
$savedMode = (Invoke-Adb $adb $Serial @("shell", "settings get system screen_brightness_mode")).Trim()
$savedImmersive = (Invoke-Adb $adb $Serial @("shell", "settings get secure immersive_mode_confirmations")).Trim()

# Chrome on Android doesn't open typed data: URLs, so the DUT serves the white page itself, on its loopback
# address only, with toybox nc.
$pagePort = 18123
$pageHandler = "/data/local/tmp/hobl_white_page.sh"
$handler = @'
while read -r line; do case "$line" in $(printf '\r')|'') break;; esac; done
printf 'HTTP/1.0 200 OK\r\nContent-Type: text/html\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n'
printf '<!DOCTYPE html><html><head><meta name="color-scheme" content="light"><title>HOBL calibration</title></head><body style="margin:0;background:#fff;height:100vh" onclick="document.documentElement.requestFullscreen()"></body></html>'
'@
$localHandler = Join-Path $env:TEMP ("hobl_white_page_" + [guid]::NewGuid().ToString("N") + ".sh")
[System.IO.File]::WriteAllText($localHandler, $handler.Replace("`r`n", "`n"), [System.Text.UTF8Encoding]::new($false))
# Matches only the listener; a pattern containing the handler name would also match the shell running pkill.
$stopServer = "pkill -f '[n]c -L -s 127.0.0.1 -p $pagePort '"

$results = @{}
try {
    Invoke-Adb $adb $Serial @("push", $localHandler, $pageHandler) | Out-Null
    Invoke-Adb $adb $Serial @("shell", $stopServer) -AllowFailure | Out-Null
    Invoke-Adb $adb $Serial @("shell", "setsid nohup toybox nc -L -s 127.0.0.1 -p $pagePort sh $pageHandler > /dev/null 2>&1 < /dev/null &") | Out-Null

    # Adaptive brightness would change the setting while measuring, and Android's one-time full screen hint
    # dims the display.
    Invoke-Adb $adb $Serial @("shell", "settings put system screen_brightness_mode 0") | Out-Null
    Invoke-Adb $adb $Serial @("shell", "settings put secure immersive_mode_confirmations confirmed") | Out-Null

    # Open the white page, then tap it to make it full screen, so no browser or system UI is visible.
    Invoke-Adb $adb $Serial @("shell", "am start --user $currentUser -W -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n com.android.chrome/com.google.android.apps.chrome.Main") | Out-Null
    Start-Sleep -Seconds 2
    Send-Keys ([string][char]0xE009 + "l") 80
    Send-Keys "http://127.0.0.1:$pagePort/"
    Send-Keys ([string][char]0xE007) 80
    Start-Sleep -Seconds 3
    $width = [long](Invoke-AgentRpc -Ip $DeviceIp -Port $Port -Method "PluginCallMethod" -Arguments @("InputInject", "GetScreenWidth"))
    $height = [long](Invoke-AgentRpc -Ip $DeviceIp -Port $Port -Method "PluginCallMethod" -Arguments @("InputInject", "GetScreenHeight"))
    Invoke-AgentRpc -Ip $DeviceIp -Port $Port -Method "PluginCallMethod" -Arguments @("InputInject", "Tap", [long]($width / 2), [long]($height / 2), 150, $true, 0, $false) | Out-Null
    Start-Sleep -Seconds 2
    Invoke-DutUiTap -Adb $adb -Serial $Serial -Labels @("Got it") | Out-Null
    # Chrome's "press Esc to exit full screen" message, and its command-line flags message when Chrome has just
    # started, fade within 20 seconds.
    Start-Sleep -Seconds 20

    foreach ($target in $TargetNits) {
        "Calibrating for $target nits" | log
        $low = 1
        $high = 100
        $percent = 50
        $best = $null
        for ($step = 0; $step -lt $MaxSteps -and $low -le $high; $step++) {
            Set-Brightness $percent
            Start-Sleep -Seconds 2
            $nits = Read-Luminance $percent
            "  $percent% = $nits nits" | log
            if (-not $best -or [math]::Abs($nits - $target) -lt [math]::Abs($best.Nits - $target)) {
                $best = [PSCustomObject]@{ Percent = $percent; Nits = $nits }
            }
            if ([math]::Abs($nits - $target) -le $Tolerance) { break }
            if ($nits -lt $target) { $low = $percent + 1 } else { $high = $percent - 1 }
            $percent = [int][math]::Floor(($low + $high) / 2)
        }
        if ([math]::Abs($best.Nits - $target) -gt $Tolerance) {
            " WARNING - The closest brightness for $target nits is $($best.Percent)% ($($best.Nits) nits), outside the $Tolerance nit tolerance." | log
        }
        $results[$target] = $best.Percent
    }
} finally {
    # Leave full screen and close the calibration tab.
    Send-Keys ([string][char]0xE00C) 80
    Start-Sleep -Seconds 1
    Send-Keys ([string][char]0xE009 + "w") 80
    Invoke-Adb $adb $Serial @("shell", $stopServer) -AllowFailure | Out-Null
    Invoke-Adb $adb $Serial @("shell", "rm -f $pageHandler") -AllowFailure | Out-Null
    Remove-Item -LiteralPath $localHandler -Force -ErrorAction SilentlyContinue
    if ($savedBrightness -match '^\d+$') {
        Invoke-Adb $adb $Serial @("shell", "settings put system screen_brightness $savedBrightness") -AllowFailure | Out-Null
    }
    if ($savedMode -match '^\d+$') {
        Invoke-Adb $adb $Serial @("shell", "settings put system screen_brightness_mode $savedMode") -AllowFailure | Out-Null
    }
    if ($savedImmersive -eq "null" -or -not $savedImmersive) {
        Invoke-Adb $adb $Serial @("shell", "settings delete secure immersive_mode_confirmations") -AllowFailure | Out-Null
    } else {
        Invoke-Adb $adb $Serial @("shell", "settings put secure immersive_mode_confirmations $(ConvertTo-ShellLiteral $savedImmersive)") -AllowFailure | Out-Null
    }
}

$nitsMap = ($TargetNits | ForEach-Object { "$($_)nits:$($results[$_])%" }) -join " "
"nits_map=$nitsMap" | log
if ($ProfilePath) {
    Copy-Item -LiteralPath $ProfilePath -Destination "$ProfilePath.bak_before_calibration" -Force
    Set-ProfileValue -ProfilePath $ProfilePath -Section "display" -Key "nits_map" -Value $nitsMap
    if (-not (Get-ProfileValue -ProfilePath $ProfilePath -Section "display" -Key "brightness")) {
        Set-ProfileValue -ProfilePath $ProfilePath -Section "display" -Key "brightness" -Value "$($TargetNits[0])nits"
    }
    "Updated display:nits_map in $ProfilePath (backup: $ProfilePath.bak_before_calibration)" | log
}
Exit 0
