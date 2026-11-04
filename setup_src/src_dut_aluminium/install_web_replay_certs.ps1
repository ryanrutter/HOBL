# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Installs or removes the web_replay CA certificates for the active Aluminium DUT user. The default automated
# flow uses a test-only profile-owner app; -Manual retains Android's Settings-based installation as a fallback.
#
# Usage:
#   .\install_web_replay_certs.ps1 [-Serial <adb serial or ip:port>] [-DeviceIp <DUT Wi-Fi ip>]
#       [-Version v1.5.0] [-WebReplayDir C:\web_replay] [-ApkPath <prebuilt APK>] [-Manual] [-Remove]

param(
    [string]$Serial = "",
    [string]$DeviceIp = "",
    [string]$Version = "v1.5.0",
    [string]$WebReplayDir = "C:\web_replay",
    [string]$ApkPath = "",
    [int]$Port = 8000,
    [string]$RequestId = "",
    [switch]$Manual,
    [switch]$Remove
)

. "$PSScriptRoot\aluminium_common.ps1"

$certDir = Join-Path $WebReplayDir "$Version\certs"
$certs = [ordered]@{
    "root_cert.pem" = "hobl_web_replay_root.crt"
    "int_cert.pem"  = "hobl_web_replay_int.crt"
}
foreach ($name in $certs.Keys) {
    if (-not (Test-Path (Join-Path $certDir $name))) {
        fail "$name not found in $certDir. Download web_replay.zip from the $Version release and extract it to $(Join-Path $WebReplayDir $Version)."
    }
}

$adb = Get-AdbPath
"Using adb: $adb" | log
$Serial = Get-AluminiumDevice -Adb $adb -Serial $Serial -DeviceIp $DeviceIp
$currentUser = (Invoke-Adb $adb $Serial @("shell", "am get-current-user")).Trim()
if ($currentUser -notmatch "^\d+$") {
    fail "Could not determine the active Android user on $($Serial): $currentUser"
}

if ($Manual) {
    if ($Remove) { fail "-Remove is not supported with -Manual." }
    if ($currentUser -ne "0") {
        $downloadUrl = "https://github.com/microsoft/web_replay/releases/download/$Version/web_replay.zip"
        "Android user $currentUser is active. Opening the release ZIP in Chrome for that user: $downloadUrl" | log
        Invoke-Adb $adb $Serial @("shell", "am start --user $currentUser -a android.intent.action.VIEW -d $downloadUrl -p com.android.chrome") | Out-Null
        "In Chrome Downloads, extract the ZIP, then install the root and intermediate certificates in Settings > Security & privacy > Encryption & credentials." | log
        Exit 0
    }
    foreach ($name in $certs.Keys) {
        $source = Join-Path $certDir $name
        $target = "/storage/emulated/0/Download/$($certs[$name])"
        "Copying $source to $target" | log
        Invoke-Adb $adb $Serial @("push", $source, $target) | Out-Null
        Invoke-Adb $adb $Serial @("shell", "am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://$target") | Out-Null
    }
    Invoke-Adb $adb $Serial @("shell", "am start --user $currentUser -a android.settings.SECURITY_SETTINGS") -AllowFailure | Out-Null
    "Install both certificates as CA certificates in Settings, then verify them under Trusted credentials > User." | log
    Exit 0
}

$features = Invoke-Adb $adb $Serial @("shell", "pm list features")
if ($features -notmatch "feature:android\.software\.device_admin") {
    "This Android build does not provide android.software.device_admin; silent profile-owner CA installation is unavailable." | log
    "Configuring Chrome's documented web_replay SPKI allowlist instead." | log
    $chromeSetup = Join-Path $PSScriptRoot "configure_web_replay_chrome.ps1"
    & $chromeSetup -Serial $Serial -DeviceIp $DeviceIp -Port $Port -Remove:$Remove
    if ($LASTEXITCODE -ne 0) { Exit $LASTEXITCODE }
    Exit 0
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$projectRoot = Join-Path $repoRoot "utilities\open_source\AluminiumAgent"
$component = "com.microsoft.hobl.certinstaller/.HoblDeviceAdminReceiver"
$packageName = "com.microsoft.hobl.certinstaller"
$activity = "$packageName/.InstallCaActivity"
$assetDir = Join-Path $projectRoot "certinstaller\src\main\assets"
foreach ($name in @("root_cert.pem", "int_cert.pem")) {
    $assetName = if ($name -eq "root_cert.pem") { "web_replay_root.pem" } else { "web_replay_intermediate.pem" }
    $assetPath = Join-Path $assetDir $assetName
    if (-not (Test-Path $assetPath)) {
        fail "Bundled certificate asset is missing: $assetPath. Build the certificate installer from the repository."
    }
    $hostHash = (Get-FileHash (Join-Path $certDir $name) -Algorithm SHA256).Hash
    $assetHash = (Get-FileHash $assetPath -Algorithm SHA256).Hash
    if ($hostHash -ne $assetHash) {
        fail "The certificates in $certDir do not match the certificates bundled with the installer. Update the certificate assets and rebuild before installing."
    }
}

if (-not $ApkPath) {
    $javaHome = $null
    foreach ($scope in @("Process", "User", "Machine")) {
        $javaHome = Get-ScopedEnvironmentVariable -Name "JAVA_HOME" -Scope $scope
        if ($javaHome) { break }
    }
    if (-not $javaHome -or -not (Test-Path (Join-Path $javaHome "bin\java.exe"))) {
        fail "JDK 17 was not found from JAVA_HOME. Set JAVA_HOME to the installed JDK or pass -ApkPath."
    }
    $sdk = $null
    foreach ($scope in @("Process", "User", "Machine")) {
        foreach ($name in @("ANDROID_HOME", "ANDROID_SDK_ROOT")) {
            $sdk = Get-ScopedEnvironmentVariable -Name $name -Scope $scope
            if ($sdk -and (Test-Path (Join-Path $sdk "platform-tools\adb.exe"))) { break }
            $sdk = $null
        }
        if ($sdk) { break }
    }
    if (-not $sdk) {
        fail "Android SDK root was not found from ANDROID_HOME or ANDROID_SDK_ROOT."
    }
    $env:JAVA_HOME = $javaHome
    $env:ANDROID_HOME = $sdk
    Push-Location $projectRoot
    try {
        "Building the test-only certificate installer." | log
        & ".\gradlew.bat" --no-daemon --console=plain ":certinstaller:assembleDebug"
        if ($LASTEXITCODE -ne 0) { fail "Gradle failed to build the certificate installer (exit code $LASTEXITCODE)." }
    } finally {
        Pop-Location
    }
    $ApkPath = Join-Path $projectRoot "certinstaller\build\outputs\apk\debug\certinstaller-debug.apk"
}
if (-not (Test-Path $ApkPath)) {
    fail "Certificate installer APK not found: $ApkPath"
}

$owners = Invoke-Adb $adb $Serial @("shell", "dpm list-owners")
$ownerLine = ($owners -split "`r?`n" | Where-Object { $_ -match "User\s+$currentUser\b" } | Select-Object -First 1)
if ($ownerLine -and $ownerLine -notmatch [regex]::Escape($packageName)) {
    fail "Android user $currentUser already has a different profile/device owner: $ownerLine. Remove or review it before proceeding."
}

if ($Remove) {
    if (-not $ownerLine -or $ownerLine -notmatch [regex]::Escape($packageName)) {
        "The HOBL certificate installer is not the profile owner for Android user $currentUser; nothing to remove." | log
        Exit 0
    }
} else {
    "Installing the test-only certificate installer for Android user $currentUser." | log
    Invoke-Adb $adb $Serial @("install", "--user", $currentUser, "-r", "-t", $ApkPath) | log
    if (-not $ownerLine) {
        "Setting the test-only app as profile owner for Android user $currentUser." | log
        Invoke-Adb $adb $Serial @("shell", "dpm set-profile-owner --user $currentUser $component") | log
    }
}

$operation = if ($Remove) { "uninstall" } else { "install" }
if (-not $RequestId) { $RequestId = [guid]::NewGuid().ToString("N") }
$start = "am start --user $currentUser -W -n $activity --es com.microsoft.hobl.certinstaller.OPERATION $operation --es com.microsoft.hobl.certinstaller.REQUEST_ID $requestId"
Invoke-Adb $adb $Serial @("shell", $start) | Out-Null

$result = $null
for ($i = 0; $i -lt 20; $i++) {
    $log = Invoke-Adb $adb $Serial @("shell", "logcat -d -s HoblCertInstaller:I")
    $result = $log -split "`r?`n" | Where-Object { $_ -match "RESULT:${RequestId}:" } | Select-Object -Last 1
    if ($result) { break }
    Start-Sleep -Seconds 1
}
if (-not $result) {
    fail "The certificate app did not report a result. Check the DUT log with: adb -s $Serial logcat -d -s HoblCertInstaller"
}
if ($result -match "RESULT:${RequestId}:ERROR:(.*)$") {
    fail "Android certificate operation failed: $($Matches[1])"
}
if ($result -notmatch "RESULT:${RequestId}:OK:") {
    fail "Unexpected certificate app response: $result"
}

if ($Remove) {
    "Removing the test-only profile owner from Android user $currentUser." | log
    Invoke-Adb $adb $Serial @("shell", "dpm remove-active-admin --user $currentUser $component") | log
    Invoke-Adb $adb $Serial @("shell", "pm uninstall --user $currentUser $packageName") | log
    "The web_replay certificates and test-only profile owner were removed." | log
} else {
    "Both web_replay CA certificates are trusted for Android user $currentUser." | log
    "To remove them later, run this script with -Remove." | log
}
Exit 0
