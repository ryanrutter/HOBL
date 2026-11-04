@echo off
REM Copyright (c) Microsoft. All rights reserved.
REM Licensed under the MIT license. See LICENSE file in the project root for full license information.

REM Build the HOBL agent for Aluminium (Android desktop) DUTs.
REM Requires JDK 17 (JAVA_HOME) and the Android SDK (ANDROID_HOME or ANDROID_SDK_ROOT).
REM See docs\support\docs\HOBL_Setup.md, "DUT Setup For Aluminium".

SetLocal
pushd %~dp0

if "%JAVA_HOME%"=="" (
    echo  ERROR - JAVA_HOME is not set. Install JDK 17 and set JAVA_HOME to its folder.
    goto ERROR
)
if not exist "%JAVA_HOME%\bin\java.exe" (
    echo  ERROR - java.exe not found under JAVA_HOME: %JAVA_HOME%
    goto ERROR
)
if "%ANDROID_HOME%"=="" if not "%ANDROID_SDK_ROOT%"=="" set ANDROID_HOME=%ANDROID_SDK_ROOT%
if "%ANDROID_HOME%"=="" (
    echo  ERROR - ANDROID_HOME is not set. Install the Android SDK command-line tools and set ANDROID_HOME.
    goto ERROR
)
echo Using JAVA_HOME=%JAVA_HOME%
echo Using ANDROID_HOME=%ANDROID_HOME%

REM Run unit tests and build the agent JAR and test-only CA installer APK.
call gradlew.bat --console=plain :agent:testReleaseUnitTest :agent:assembleRelease :certinstaller:testDebugUnitTest :certinstaller:assembleDebug
if %errorlevel% neq 0 (
    echo  ERROR - Agent or certificate installer build/tests failed.
    goto ERROR
)

REM The agent is launched with app_process from a class path, so it is published as a .jar.
if not exist Output mkdir Output
copy /y agent\build\outputs\apk\release\agent-release-unsigned.apk Output\AluminiumAgent.jar
if %errorlevel% neq 0 goto ERROR
echo Agent built: %~dp0Output\AluminiumAgent.jar
echo Certificate installer built: %~dp0certinstaller\build\outputs\apk\debug\certinstaller-debug.apk

popd
exit /b 0

:ERROR
popd
exit /b 1
