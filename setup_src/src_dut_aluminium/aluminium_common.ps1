# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Shared helpers for setting up Aluminium (Android desktop) DUTs from the HOBL host over ADB.
# Dot-source this file from dut_setup_aluminium.ps1 and launch_agent.ps1.

$AgentDir = "/data/local/tmp/hobl_bin/AluminiumAgent"
$AgentJar = "$AgentDir/AluminiumAgent.jar"
$DataDir = "/data/local/tmp/hobl_data"
$AgentProcessName = "hobl_agent"

function log {
    [CmdletBinding()] Param([Parameter(ValueFromPipeline)] $msg)
    process {
        if ($msg -Match " ERROR - ") {
            Write-Host $msg -ForegroundColor Red
        } elseif ($msg -Match " WARNING - ") {
            Write-Host $msg -ForegroundColor Yellow
        } else {
            Write-Host $msg
        }
    }
}

function fail($msg) {
    " ERROR - $msg" | log
    Exit 1
}

# Read an environment variable from a scope: Process, User or Machine.  User and Machine are the saved values,
# which a long running window (such as a test plan started before the Android SDK was set up) doesn't inherit.
function Get-ScopedEnvironmentVariable {
    param([string]$Name, [string]$Scope)
    return [Environment]::GetEnvironmentVariable($Name, $Scope)
}

# Find adb from PATH or the Android SDK environment variables.  Install location is never assumed.
function Get-AdbPath {
    $cmd = Get-Command adb -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    foreach ($scope in @("Process", "User", "Machine")) {
        foreach ($name in @("ANDROID_HOME", "ANDROID_SDK_ROOT")) {
            $sdk = Get-ScopedEnvironmentVariable -Name $name -Scope $scope
            if ($sdk) {
                $candidate = Join-Path $sdk "platform-tools\adb.exe"
                if (Test-Path $candidate) { return $candidate }
            }
        }
    }
    fail "adb not found.  Install Android SDK Platform-Tools and add its folder to PATH, or set ANDROID_HOME.  See docs\support\docs\HOBL_Setup.md, 'DUT Setup For Aluminium'."
}

# Run adb against one device and return its output, failing on a non-zero exit code.
function Invoke-Adb {
    param([string]$Adb, [string]$Serial, [string[]]$Arguments, [switch]$AllowFailure)
    $output = & $Adb -s $Serial @Arguments 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0 -and -not $AllowFailure) {
        fail "adb $($Arguments -join ' ') failed with exit code $($LASTEXITCODE): $($output.Trim())"
    }
    return $output.Trim()
}

# Pick the device to use: the specified serial, the device whose Wi-Fi address is DeviceIp, or the only
# connected device.  Android 17 wireless debugging serials (adb-<serial>-<id>._adb-tls-connect._tcp) don't
# contain the IP address, so DeviceIp is how the HOBL host finds its DUT when several Googlebooks are paired.
function Get-AluminiumDevice {
    param([string]$Adb, [string]$Serial, [string]$DeviceIp = "")
    if ($Serial -match ":\d+$") {
        # Wireless debugging device, e.g. 192.0.2.20:37123.  Connecting again is harmless.
        & $Adb connect $Serial | log
    }
    $devices = Get-AdbDevices -Adb $Adb
    if (-not $Serial -and $DeviceIp) {
        $Serial = Find-AdbDeviceByIp -Adb $Adb -Devices $devices -DeviceIp $DeviceIp
        if (-not $Serial -and (Connect-WirelessDebugging -Adb $Adb -DeviceIp $DeviceIp)) {
            $devices = Get-AdbDevices -Adb $Adb
            $Serial = Find-AdbDeviceByIp -Adb $Adb -Devices $devices -DeviceIp $DeviceIp
        }
        if (-not $Serial) {
            fail "No authorized adb device has IP address $DeviceIp.  Connected devices: $($devices.Keys -join ', ').  Make sure Wireless debugging is on, the DUT is on the same network, and this host is paired with it."
        }
    }
    if (-not $Serial) {
        if ($devices.Count -eq 0) { fail "No devices found by adb.  Connect the Googlebook with USB, or pair it with Wireless debugging, and enable USB debugging." }
        if ($devices.Count -gt 1) { fail "More than one device is connected: $($devices.Keys -join ', ').  Specify one with -Serial." }
        $Serial = @($devices.Keys)[0]
    }
    if (-not $devices.ContainsKey($Serial)) {
        fail "Device $Serial not found by adb.  Connected devices: $($devices.Keys -join ', ')"
    }
    switch ($devices[$Serial]) {
        "device" { }
        "unauthorized" { fail "Device $Serial is unauthorized.  Unlock the Googlebook and accept the 'Allow USB debugging' prompt (check 'Always allow')." }
        default { fail "Device $Serial is $($devices[$Serial])." }
    }
    return $Serial
}

# Devices known to adb, as a table of serial to state ("device", "unauthorized", "offline").
function Get-AdbDevices {
    param([string]$Adb)
    $devices = @{}
    foreach ($line in (& $Adb devices | Select-Object -Skip 1 | Where-Object { $_.Trim() -ne "" })) {
        $parts = $line -split "\s+"
        $devices[$parts[0]] = $parts[1]
    }
    return $devices
}

# The serial of the authorized device whose network address is DeviceIp, or $null.
function Find-AdbDeviceByIp {
    param([string]$Adb, [hashtable]$Devices, [string]$DeviceIp, [switch]$WirelessOnly)
    foreach ($candidate in @($Devices.Keys)) {
        if ($Devices[$candidate] -ne "device") { continue }
        if ($WirelessOnly -and -not (Test-WirelessSerial $candidate)) { continue }
        $addresses = & $Adb -s $candidate shell "ip -4 -o addr show" 2>$null | Out-String
        if ($addresses -match "inet $([regex]::Escape($DeviceIp))/") { return $candidate }
    }
    return $null
}

# Connect to a paired DUT's Wireless debugging port.  Wireless debugging picks a new port each time it starts,
# and adb doesn't always reconnect by itself after the DUT shuts down, so find the port with mDNS.
function Connect-WirelessDebugging {
    param([string]$Adb, [string]$DeviceIp)
    $services = & $Adb mdns services 2>$null | Out-String
    $pattern = "_adb-tls-connect\._tcp\.?\s+$([regex]::Escape($DeviceIp)):(\d+)"
    foreach ($line in ($services -split "`n")) {
        if ($line -match $pattern) {
            $endpoint = "$($DeviceIp):$($Matches[1])"
            $output = & $Adb connect $endpoint 2>&1 | Out-String
            "Wireless debugging: $($output.Trim())" | log
            if ($LASTEXITCODE -eq 0 -and $output -match "connected to") { return $true }
        }
    }
    return $false
}

# After a restart, Aluminium shows its login screen as the system user (0), and the test user stays locked until
# its PIN is entered.  Switching users stops Wireless debugging and ends every process started over ADB, including
# the agent, so the agent can't do the switch.  Instead, verify the PIN to unlock the test user's storage, then
# switch to it; Wireless debugging starts again once the test user is unlocked, and HOBL enters the PIN on the lock
# screen through the agent.  Returns the adb serial to use after the switch.
function Switch-AluminiumTestUser {
    param([string]$Adb, [string]$Serial, [string]$DeviceIp, [string]$Pin, [int]$TimeoutSeconds = 120)
    $current = (Invoke-Adb $Adb $Serial @("shell", "am get-current-user") -AllowFailure).Trim()
    if ($current -ne "0") { return $Serial }
    $users = Invoke-Adb $Adb $Serial @("shell", "pm list users") -AllowFailure
    $testUser = [regex]::Matches($users, "UserInfo\{(\d+):") | ForEach-Object { $_.Groups[1].Value } | Where-Object { $_ -ne "0" } | Select-Object -First 1
    if (-not $testUser) { return $Serial }
    if (-not $Pin) {
        " WARNING - The DUT is at the login screen.  Set dut_pin in the device profile so HOBL can sign in to user $testUser after a restart, or sign in by hand." | log
        return $Serial
    }
    "The DUT is at the login screen.  Unlocking and switching to user $testUser." | log
    # The PIN goes to the DUT's shell on standard input, so it isn't on a command line or in the DUT's adbd log.
    $commands = "am start-user $testUser`ncmd lock_settings verify --old $(ConvertTo-ShellLiteral $Pin) --user $testUser`nexit`n"
    $output = $commands | & $Adb -s $Serial shell 2>&1 | Out-String
    if ($output -notmatch "verified successfully") {
        # Exit code 3 tells HOBL not to retry, since repeated wrong PINs lock the user out for longer each time.
        " ERROR - dut_pin was not accepted for user $testUser.  Check dut_pin in the device profile." | log
        Exit 3
    }
    Invoke-Adb $Adb $Serial @("shell", "am switch-user $testUser") -AllowFailure | Out-Null
    if (Test-WirelessSerial $Serial) { & $Adb disconnect $Serial 2>&1 | Out-Null }
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 5
        $devices = Get-AdbDevices -Adb $Adb
        $newSerial = Find-AdbDeviceByIp -Adb $Adb -Devices $devices -DeviceIp $DeviceIp
        if (-not $newSerial -and (Connect-WirelessDebugging -Adb $Adb -DeviceIp $DeviceIp)) {
            $newSerial = Find-AdbDeviceByIp -Adb $Adb -Devices (Get-AdbDevices -Adb $Adb) -DeviceIp $DeviceIp
        }
        if ($newSerial -and (Invoke-Adb $Adb $newSerial @("shell", "am get-current-user") -AllowFailure).Trim() -eq $testUser) {
            "Switched to user $testUser." | log
            return $newSerial
        }
    }
    fail "Wireless debugging did not reconnect within $TimeoutSeconds seconds after switching to user $testUser."
}

# IPv4 address of the DUT's Wi-Fi or Ethernet interface.
function Get-DeviceIp {
    param([string]$Adb, [string]$Serial)
    $output = Invoke-Adb $Adb $Serial @("shell", "ip -4 -o addr show")
    $addresses = foreach ($line in ($output -split "`n")) {
        if ($line -match "^\d+:\s+(\S+)\s+inet\s+(\d+\.\d+\.\d+\.\d+)/" -and $Matches[1] -ne "lo") {
            [PSCustomObject]@{ Interface = $Matches[1]; Address = $Matches[2] }
        }
    }
    $preferred = $addresses | Where-Object { $_.Interface -match "^(wlan|eth)" } | Select-Object -First 1
    if (-not $preferred) { $preferred = $addresses | Select-Object -First 1 }
    if (-not $preferred) { fail "The DUT has no network address.  Connect it to the same network as the HOBL host." }
    return $preferred.Address
}

# IPv4 address this host uses to reach the DUT, which is what the agent sees connecting.
function Get-HostIp {
    param([string]$DeviceIp)
    try {
        $route = Find-NetRoute -RemoteIPAddress $DeviceIp -ErrorAction Stop | Where-Object { $_.IPAddress } | Select-Object -First 1
        if ($route) { return $route.IPAddress }
    } catch {
    }
    fail "Unable to determine the host IP address used to reach $DeviceIp.  Specify it with -HostIp."
}

# Send a GetVersion JSON-RPC request, the same as HOBL's comm_check.  Returns the version or $null.
function Test-Agent {
    param([string]$Ip, [int]$Port)
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        if (-not $client.ConnectAsync($Ip, $Port).Wait(5000)) { return $null }
        $stream = $client.GetStream()
        $stream.ReadTimeout = 5000
        $writer = New-Object System.IO.StreamWriter($stream)
        $writer.Write('{"method":"GetVersion","params":[],"jsonrpc":"2.0","id":"1"}' + "`r`n")
        $writer.Flush()
        $reader = New-Object System.IO.StreamReader($stream)
        return ($reader.ReadLine() | ConvertFrom-Json).result
    } catch {
        return $null
    } finally {
        $client.Close()
    }
}

# Make one SimpleRemote-compatible JSON-RPC call to the Aluminium agent.
function Invoke-AgentRpc {
    param([string]$Ip, [int]$Port, [string]$Method, [object[]]$Arguments)
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        if (-not $client.ConnectAsync($Ip, $Port).Wait(5000)) {
            throw "Timed out connecting to the Aluminium agent at ${Ip}:$Port"
        }
        $stream = $client.GetStream()
        $stream.ReadTimeout = 10000
        $writer = New-Object System.IO.StreamWriter($stream, [System.Text.UTF8Encoding]::new($false))
        $payload = @{
            method = $Method
            params = @($Arguments)
            jsonrpc = "2.0"
            id = "1"
        } | ConvertTo-Json -Compress -Depth 10
        $writer.Write($payload + "`r`n")
        $writer.Flush()
        $reader = New-Object System.IO.StreamReader($stream)
        $line = $reader.ReadLine()
        if (-not $line) { throw "The Aluminium agent returned an empty response to $Method" }
        $response = $line | ConvertFrom-Json
        if ($response.error) { throw "The Aluminium agent rejected $Method`: $($response.error.message)" }
        return $response.result
    } finally {
        $client.Close()
    }
}

# Read Key from Section of an INI device profile.  Returns "" when it's absent.  Values are never logged.
function Get-ProfileValue {
    param([string]$ProfilePath, [string]$Section, [string]$Key)
    $current = ""
    foreach ($line in (Get-Content -LiteralPath $ProfilePath)) {
        $trimmed = $line.Trim()
        if ($trimmed -match '^\[(.+)\]$') {
            $current = $Matches[1].Trim()
        } elseif ($current -eq $Section -and $trimmed -match "^$([regex]::Escape($Key))\s*=(.*)$") {
            return $Matches[1].Trim().Trim('"')
        }
    }
    return ""
}

# Quote a value for the DUT's sh, so spaces and special characters are passed through unchanged.
function ConvertTo-ShellLiteral {
    param([string]$Value)
    return "'" + $Value.Replace("'", "'\''") + "'"
}

# True for a Wireless debugging device, which disconnects if the DUT changes network.
function Test-WirelessSerial {
    param([string]$Serial)
    return ($Serial -match "_adb-tls-connect" -or $Serial -match ":\d+$")
}

# Name of the Wi-Fi network the DUT is connected to, or "".
function Get-DutWifiName {
    param([string]$Adb, [string]$Serial)
    $status = & $Adb -s $Serial shell "cmd wifi status" 2>&1 | Out-String
    if ($status -match 'Wifi is connected to "([^"]*)"') { return $Matches[1] }
    return ""
}

# MAC address the DUT uses on its current Wi-Fi network, or "".
function Get-DutWifiMac {
    param([string]$Adb, [string]$Serial)
    $info = & $Adb -s $Serial shell "dumpsys wifi | grep -m1 'mWifiInfo SSID'" 2>&1 | Out-String
    if ($info -match 'MAC: ([0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5})') { return $Matches[1] }
    return ""
}

# IDs of the DUT's saved Wi-Fi networks named Name, for the current Android user and shared networks.
function Get-DutSavedNetworkIds {
    param([string]$Adb, [string]$Serial, [string]$Name)
    $list = & $Adb -s $Serial shell "cmd wifi list-networks" 2>&1 | Out-String
    $ids = foreach ($line in ($list -split "`n")) {
        if ($line -match "^\s*(\d+)\s+$([regex]::Escape($Name))\s{2,}") { $Matches[1] }
    }
    return @($ids | Select-Object -Unique)
}

# True for a random MAC address: random addresses are locally administered (bit 2 of the first byte is set).
function Test-RandomMac {
    param([string]$Mac)
    return ($Mac -and ([Convert]::ToInt32($Mac.Substring(0, 2), 16) -band 2))
}

# Join the DUT to a Wi-Fi network over USB, the equivalent of dut_wifi_name/dut_wifi_password in the Windows
# dut_setup.  The password is passed to the DUT only, never written to the console.
#
# The network is saved once, shared with all Android users, with the device's own MAC address.  Settings saves a
# network for the current user only, with a random MAC that changes daily and differs per user.  After a restart,
# the login screen then has no network or a different IP address, so HOBL can't reach the DUT to sign in, and
# dut_ip in the profile stops matching.
function Connect-DutWifi {
    param([string]$Adb, [string]$Serial, [string]$Name, [string]$Password, [string]$Authentication = "WPA2PSK", [int]$TimeoutSeconds = 60)
    $current = Get-DutWifiName -Adb $Adb -Serial $Serial
    $saved = Get-DutSavedNetworkIds -Adb $Adb -Serial $Serial -Name $Name
    $randomMac = ($current -eq $Name) -and (Test-RandomMac (Get-DutWifiMac -Adb $Adb -Serial $Serial))
    if ($current -eq $Name -and -not $randomMac -and $saved.Count -le 1) {
        "Wi-Fi: already connected to $Name" | log
        return
    }
    if (Test-WirelessSerial $Serial) {
        if ($current -eq $Name) {
            # Changing the saved network reconnects Wi-Fi, which would disconnect Wireless debugging.
            " WARNING - Wi-Fi network $Name was saved in Settings (a random MAC address, or saved more than once), so the DUT's IP address can change after a restart and HOBL can't reconnect to it.  Connect the DUT with USB and run this script again to save the network for lab use." | log
            return
        }
        fail "The DUT is on Wi-Fi network '$current', not '$Name'.  Changing networks would disconnect Wireless debugging, so connect the DUT with USB and run this script again."
    }
    foreach ($id in $saved) {
        Invoke-Adb $Adb $Serial @("shell", "cmd wifi forget-network $id") -AllowFailure | Out-Null
    }
    $security = if (-not $Password) { "open" } elseif ($Authentication -eq "WPA3SAE") { "wpa3" } else { "wpa2" }
    # cmd wifi saves the network shared with all users; -r none uses the device's MAC address.
    $command = "cmd wifi connect-network $(ConvertTo-ShellLiteral $Name) $security"
    if ($Password) { $command += " $(ConvertTo-ShellLiteral $Password)" }
    $command += " -r none"
    "Wi-Fi: joining $Name ($security, device MAC address, shared with all users)" | log
    $output = & $Adb -s $Serial shell $command 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        if ($Password) { $output = $output.Replace($Password, "********") }
        fail "Could not join Wi-Fi network $Name`: $($output.Trim())"
    }
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        # Wait for DHCP too, since the agent and Wireless debugging need the DUT's address.
        $addresses = & $Adb -s $Serial shell "ip -4 -o addr show" 2>&1 | Out-String
        if ((Get-DutWifiName -Adb $Adb -Serial $Serial) -eq $Name -and $addresses -match "(wlan|eth)\S*\s+inet ") {
            "Wi-Fi: connected to $Name" | log
            return
        }
        Start-Sleep -Seconds 2
    }
    fail "The DUT did not connect to Wi-Fi network $Name within $TimeoutSeconds seconds.  Check dut_wifi_name and dut_wifi_password in the device profile."
}

# Tap the button labeled one of $Labels in the DUT's current screen, using its accessibility tree.
# Returns $true if a button was tapped.
function Invoke-DutUiTap {
    param([string]$Adb, [string]$Serial, [string[]]$Labels)
    $dumpPath = "/data/local/tmp/hobl_setup_ui.xml"
    & $Adb -s $Serial shell "uiautomator dump $dumpPath" 2>&1 | Out-Null
    $xml = & $Adb -s $Serial shell "cat $dumpPath" 2>$null | Out-String
    & $Adb -s $Serial shell "rm -f $dumpPath" 2>&1 | Out-Null
    try { $tree = [xml]$xml } catch { return $false }
    if (-not $tree) { return $false }
    foreach ($label in $Labels) {
        $node = $tree.SelectNodes("//node") | Where-Object { $_.text -eq $label -and $_.bounds } | Select-Object -First 1
        if ($node -and $node.bounds -match '\[(\d+),(\d+)\]\[(\d+),(\d+)\]') {
            $x = [int](([int]$Matches[1] + [int]$Matches[3]) / 2)
            $y = [int](([int]$Matches[2] + [int]$Matches[4]) / 2)
            & $Adb -s $Serial shell "input tap $x $y" 2>&1 | Out-Null
            return $true
        }
    }
    return $false
}

# Turn on Wireless debugging over USB and connect to it, so the DUT doesn't need the USB cable afterwards.
# A host that was allowed with "Always allow from this computer" over USB is trusted by Wireless debugging
# too, so no pairing code is needed.  Returns the Wireless debugging endpoint.
function Enable-WirelessDebugging {
    param([string]$Adb, [string]$Serial, [string]$DeviceIp, [int]$TimeoutSeconds = 60)
    $enabled = (& $Adb -s $Serial shell "settings get global adb_wifi_enabled" 2>&1 | Out-String).Trim()
    if ($enabled -ne "1") {
        "Wireless debugging: turning on" | log
        & $Adb -s $Serial shell "settings put global adb_wifi_enabled 1" 2>&1 | Out-Null
    }
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $promptHandled = $false
    while ((Get-Date) -lt $deadline) {
        $connected = Find-AdbDeviceByIp -Adb $Adb -Devices (Get-AdbDevices -Adb $Adb) -DeviceIp $DeviceIp -WirelessOnly
        if ($connected) {
            "Wireless debugging: connected as $connected" | log
            return $connected
        }
        if (Connect-WirelessDebugging -Adb $Adb -DeviceIp $DeviceIp) { continue }
        # Android asks once per network whether to allow Wireless debugging on it.
        if (-not $promptHandled -and (Invoke-DutUiTap -Adb $Adb -Serial $Serial -Labels @("Always allow on this network"))) {
            Invoke-DutUiTap -Adb $Adb -Serial $Serial -Labels @("Allow") | Out-Null
            "Wireless debugging: allowed on this network" | log
            $promptHandled = $true
            & $Adb -s $Serial shell "settings put global adb_wifi_enabled 1" 2>&1 | Out-Null
        }
        Start-Sleep -Seconds 3
    }
    fail "Could not connect to Wireless debugging on $DeviceIp.  On the DUT, open Settings > System > Developer options > Wireless debugging, make sure it is on and this network is allowed, then pair this host with 'adb pair' using 'Pair device with pairing code'."
}

# Set Key in Section of an INI device profile, keeping comments and other settings.  The key is added at the end
# of the section if it is missing, and the section is added if the profile doesn't have it.  The file is written
# without a byte order mark, which HOBL's profile reader doesn't expect.
function Set-ProfileValue {
    param([string]$ProfilePath, [string]$Section, [string]$Key, [string]$Value)
    $lines = [System.Collections.Generic.List[string]]::new([string[]][System.IO.File]::ReadAllLines($ProfilePath))
    $current = ""
    $headerIndex = -1
    $lastIndex = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $trimmed = $lines[$i].Trim()
        if ($trimmed -match '^\[(.+)\]$') {
            $current = $Matches[1].Trim()
            if ($current -eq $Section -and $headerIndex -lt 0) {
                $headerIndex = $i
                $lastIndex = $i
            }
            continue
        }
        if ($current -ne $Section) { continue }
        if ($trimmed -match "^$([regex]::Escape($Key))\s*=") {
            $lines[$i] = "$Key=$Value"
            [System.IO.File]::WriteAllLines($ProfilePath, $lines, [System.Text.UTF8Encoding]::new($false))
            return
        }
        if ($trimmed -and -not $trimmed.StartsWith(";")) { $lastIndex = $i }
    }
    if ($headerIndex -ge 0) {
        $lines.Insert($lastIndex + 1, "$Key=$Value")
    } else {
        $lines.Add("")
        $lines.Add("[$Section]")
        $lines.Add("$Key=$Value")
    }
    [System.IO.File]::WriteAllLines($ProfilePath, $lines, [System.Text.UTF8Encoding]::new($false))
}
