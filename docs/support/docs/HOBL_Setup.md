# Setup

## Lab Setup
* The HOBL UI software allows controlling multiple DUTs from a single Host, so a lab will generally have a single HOBL host computer.  
* The HOBL UI is a web server that can be accessed by multiple users simultaneously, if needed.  For larger labs, it can also be executed with IIS.
* The Hosts and DUTs should be on a local network that has internet access.
* The host should be connected with ethernet, but the DUT should be on Wi-Fi, to be representative of a user operating a device on battery.  Ethernet dongles often prevent devices from getting to lower power states.
### Wi-Fi
* The Wi-Fi network should be set up to provide each device with **50 Mbps**, again for representativeness.  Significantly more or less BW has power consumption impact.  Not all AP's are good at controlling this, but we have found the HPE Aruba line of access points adept at it, but they now require a centralized controller.  RUCKUS AP's that support "RUCKUS Unleashed" have also been tested to work well and don't require a central controller.  50 Mbps is also the minimum bandwidth requirement for correct functionality.
* 5 GHz channels should be used for connecting to DUTs.
* Do not domain-join the DUTs.
* Corporate network traffic can be intense, so it is recommended to deploy a firewall between the lab LAN and corporate networks that will filter out corporate traffic but still allow access to the internet.  This will improve representativeness and reduce test variability.
### Charger Control
* HOBL supports automatic recharging of DUTs via a variety of mechanisms, as long as they can be controlled by a shell command.  The commands are specified in the charge_on and charge_off sections of the Device Profile.  The most common mechanisms are:
    1. Any SNMP controllable IP switchable power strip, such as Cyberpower, APC, Raritan PX-series, etc.
    1. <a href="https://dlidirect.com/products/new-pro-switch" target="_blank">Digital-Loggers Pro Switch</a>.
    1. An iBoot controlled by either ethernet or relay.
    1. Shelly Smart Plugs.
### Display Brightness
* A luminance meter should be used to determine the DUT brightness setting that corresponds to 150 nits.  Measure and average all 4 corners plus center of a pure white screen.  All tests are expected to run at this brightness except JEITA-related tests (which are at 200 nits).  A nits map should be specified in the profile to associate the appropriate slider positions to 150 and 200 nits respectively.  <TODO: Add section on profile setup and tools>
### Audio Volume
* Tests are run with audio volume set to the out-of-box default level.  To ensure consistency, once this value is determined, it should also be specified in the device profile.

## Account Setup
The following accounts need to be created for the DUT:

1. <a href="https://outlook.live.com/owa/" target="_blank">MSA (Microsoft Account)</a> for logging into Windows, Teams, OneDrive, Office, and the Store.  Each DUT needs its own account, otherwise files syncing across devices will not only cause variability but can break tests.  It is critical to set security for the account, otherwise it will require a phone number from you in about a week.  To secure the account, go to <a href="https://account.microsoft.com" target="_blank">https://account.microsoft.com</a> and sign in with the newly created MSA.  Then select the "Security" menu item at the top.  Then click "Get Started" on the "Advanced Security Options" card.  Select to add a verification email account (so that you don't have to use a phone number), then you will be prompted to send verification codes twice.  You can use the same verification account for all MSA's that you create.  Log into the verification account using a different web browser or computer (so you don't log out of your MSA), to retrieve the codes.  Be sure to NOT set 2FA (MFA) in order to get full automation.

1. Office - To run scenarios that involve Microsoft OFfice (i.e. productivity, abl_active) you will need to purchase a subscription to Microsoft 365 Personal or Family (not Business), otherwise you will only have a 5-day grace period for testing after install.  The subscription needs to be tied to the MSA.  There is a limit to how many devices can use a single m365 subscription, so you may need to release the subscription on devices no longer used.  This can be managed at
<a href="https://account.microsoft.com/services/office/install" target="_blank">https://account.microsoft.com/services/office/install</a>.  Click "Sign out of Office" on devices no longer being used.  You may also have to do this for prior OS images on an active DUT, since new OS images may be considered a different "device".

1. Teams - The MSA account needs to be one-time associated with a Teams Organization set up for testing.  Also make sure it's only associated with one organization, otherwise the DUT will prompt for which Org to execute with, which will break the automation.  The Teams org can be shared across any number of MSA's, so generally only one Teams org needs to be set up per test house.  Once the org is set up, you associate the MSA by clicking the provided URL and entering the MSA email.
    * Creating a Teams Test Organization:

        1. Go to MS Teams Page:  <a href="https://www.microsoft.com/en-us/microsoft-365/microsoft-teams/group-chat-software" target="_blank">https://www.microsoft.com/en-us/microsoft-365/microsoft-teams/group-chat-software</a>
        2.	Click Sign up for Free:  <a href="https://go.microsoft.com/fwlink/p/?LinkID=2123761&clcid=0x409&culture=en-us&country=US&lm=deeplink&lmsrc=homePageWeb&cmpid=FreemiumSignUpHero" target="_blank">https://go.microsoft.com/fwlink/p/?LinkID=2123761&clcid=0x409&culture=en-us&country=US&lm=deeplink&lmsrc=homePageWeb&cmpid=FreemiumSignUpHero</a>
        3.	Enter Email info and continue with sign up.
        4.	Select “For work and organizations” or “Not a school organization” depending on which prompt you get.
        5.	Enter a Test Company Name (ex. “Test Company”, “Contoso”, “Teams Testing”, etc.).
        6.	Click Create Teams Org.
        7.	Continue to the Web Teams site.
        8.	Wait for Teams org to finish creation and the web Teams site to finish loading.
        9.	Once the page has loaded, click on the user account icon in the top right of the page.
        10.	Select “Manage Org” from the dropdown .
        11.	Click the Settings tab in the top middle of the page.
        12.	Expand the “Manage Link” Section.
        13.	Check the toggle to “Enable link”.
        14.	Check the toggle to “Enable auto-join”.
        15. The Link URL below the toggles can now be used by any test account to join the new test org. 

1. <a href="https://www.netflix.com/signup" target="_blank">Netflix Premium</a> for the Netflix scenario.  Up to 4 DUTs can be used with the same account.

## Host Setup
The host computer houses the HOBL test framework and UI.  Through this, users execute tests remotely on one or more DUTs, and view the results.

Host computer system requirements are:  Intel or AMD processor running Windows 11.  For large labs, factor approximately 1 host core per 10 devices, and 16 GB of RAM + (0.5 GB * number of DUTs).

1. Make sure Git is installed on your Host computer.
1. Clone the HOBL repo to your preferred location, but note that putting it at "c:\hobl" will simplify things.  You might want to do a shallow clone if your organization has download capacity limits.
1. Run the host_setup.exe in the root folder.  This will:
    1. Download various items into the /Downloads folder.  These include:
        - The appropriate dut_setup executables.
        - ffmpeg.
        - Windows runtime libraries.
        - Set git hooks to automatically update the HOBL version on pulls.
        - Disable the Windows error reporting UI (to prevent halting automation in case of an error).
    1. Install embedded python.
    1. Download and install the HOBL UI in c:\HOBLweb.
        - If you installed hobl in a folder other than "c:\hobl", then you need to hand-edit c:\hoblweb\appsettings.json and modify the "DocsPath" parameter accordingly.
        - Likewise, if you intend to have your results go to a different base folder than "c:\hobl_results", modify the "ResultsPath" parameter accordingly.  Make sure that the "results_dir" parameter in your profile includes this base path.

To get future updates to the HOBL source code, do a "git pull" in the hobl folder.  To get future updates to the HOBL UI, rerun host_setup.exe and just select "HOBL User Interface" item.

HOBLweb UI documentation can be found here: [HOBL UI](HOBL_UI.md)

Set up a Device Profile for each DUT in the HOBLweb UI, giving it a unique name (typically we name it the name of the DUT), and modifying the parameters as appropriate.  Use the Parameters documentation as a guide.

## DUT Setup For Windows
1. After running host_setup.exe, dut_setup.exe should be found in the /downloads/Setup folder.  Copy dut_setup_\<ver\>.exe from here to a USB stick.
1. Plug the USB stick into the DUT and execute dut_setup.exe. This will install SimpleRemote and configure the DUT for communication with the HOBL Host.  HOBL can't communicate without this, and you will see errors about failed remote directory creation and communication timeouts.
1. You will be prompted to change the name of the device if desired.  Click Next.
1. You will be prompted to enter Wi-Fi information.  This will be saved to the USB stick so that you can set up the device again in the future, or other devices in the lab, without having to re-enter the information.
    1. This will setup various registry settings and launch simple_remote to allow communication from the host.
    1. If you see an error when it tries to set the developer mode, this can safely be ignored.
4. Test network connection to the DUT:
    1. Host and DUT need to be on the same subnet (first 2 octets of the IP address).
    1. Run Cmd or Powershell on the Host, and make sure sure DUT responds to pings:  `ping <dut_ip>`
    1. Make sure DUT can ping host as well.
    1. Run the "comm_check" scenario to make sure that all communications needs are met.

## DUT Setup For macOS
1. Manually set up the Mac with an account and connect the device to the appropriate Wi-Fi network, on the same subnet as the Host.
2. If Global Secure Access app exists, disable it.  It prevents peer-to-peer communication.
3. Change settings to do auto-login:
    1. System Settings -> Users & Groups -> Automatically log in as: specify account and password
4. Copy hobl\downloads\setup\dut_setup_<ver>.sh to Mac using a FAT32 formatted USB stick, and execute from terminal window.  You will be prompted for password and access permissions multiple times.  Be sure to enable everything.  If you don't see dut_setup_\<ver>\.sh in the hobl\downloads\setup folder, then do [Host Setup](#host-setup).
5. Either disable firewall, or disable "Stealth Mode" in Firewall Options (to allow pings to go through)
6. Use light meter to adjust screen brightness to 150 nits, on DC with white background.  Then run /users/Shared/hobl_bin/brightness -l to report setting level.  Multiply that fraction by 100 to turn to percentage, to set display:brightness in profile.
7. Leave audio level at out-of-box setting.
8. The first time you run some tests or tools there may be various permissions popups.  Manually allow them all. Then subsequent runs should work without interference.
10. Set keyboard shortcut Shift-Cmd-H to Safari "Clear History…"
    1. Settings -> Keyboard -> Keyboard Shortcuts -> App Shortcuts
    1. Application: "Safari"
    1. Menu title: "Clear History…" (the three dots are critical)
    1. Keyboard shortcut: "Shift-Cmd-H"
11. Set Safari history clear to "All History"
12. Test network connection to the DUT:
    1. Host and DUT need to be on the same subnet (first 2 octets of the IP address).
    1. Run Cmd or Powershell on the Host, and make sure sure DUT responds to pings:  `ping <dut_ip>`
    1. Make sure DUT can ping host as well.
    1. Run the "comm_check" scenario to make sure that all communications needs are met.

One thing to be aware of on Mac is that as icon count in the dock increases, macos reduces their size so that they all fit.  However, in our automation we need them to stay constant size for proper image matching.  So the solution is remove unneeded icons to make sure there is plenty of space on the left and right of the dock.  So you might need to remove a few unused ones, such as Calendar, Reminders, etc.  Make sure the dock is always visible.


Verify these settings have been set in  System Settings -> Privacy & Security:

- Files & Folders -> SimpleRemoteConsole:
    - Documents Folder
    - Downloads Folder
- Accessibility -> SimpleRemoteConsole
- Local Network -> SimpleRemoteConsole
- Screen & System Audio Recording -> SimpleRemoteConsole

## DUT Setup For Aluminium
Aluminium is the Android desktop operating system used by devices such as Googlebooks.  Instead of SimpleRemote, HOBL uses the Aluminium agent (utilities\open_source\AluminiumAgent), which provides the same functions.  The agent is started on the DUT over ADB (Android Debug Bridge) from the Host, so nothing is installed on the DUT itself.  Aluminium scenarios are in scenarios\aluminium and start with "al_".

Like SimpleRemote, the agent allows running programs and accessing files on the DUT with no authentication.  It only accepts connections from the HOBL Host's IP address, but should still only be used on dedicated test devices.

### Host Prerequisites
1. Install Android SDK Platform-Tools, which include adb, from <a href="https://developer.android.com/tools/releases/platform-tools" target="_blank">https://developer.android.com/tools/releases/platform-tools</a>.  Extract the zip file to a folder of your choice, then either add the platform-tools folder to the PATH environment variable, or set ANDROID_HOME to the folder containing platform-tools.
1. Open a new PowerShell window and run `adb version` to make sure adb is found.
1. The agent is prebuilt in utilities\open_source\AluminiumAgent\Output.  Rebuilding is only needed when changing the agent.  To rebuild, install JDK 17 and the Android SDK command-line tools, set JAVA_HOME and ANDROID_HOME, and run utilities\open_source\AluminiumAgent\build_aluminium.cmd.

### Google Account
1. Create a dedicated <a href="https://accounts.google.com/signup" target="_blank">Google account</a> for each DUT, for the same reasons as the MSA described in [Account Setup](#account-setup). Use recovery information you control. Google may require phone verification during account creation.
1. Add the dedicated account on the DUT through Settings -> Passwords & accounts -> Add account -> Google, or let the `al_google_account_prep` scenario add it (see [Accounts and Prep Scenarios](#accounts-and-prep-scenarios)).
1. Keep Chrome sync off unless the scenario being run explicitly requires it. Do not sync personal data to a test DUT.
1. Automated sign-in, like Windows' `msa_prep`, needs the account without 2-Step Verification.  If your lab requires 2-Step Verification, sign in on the DUT once by hand and leave `google_password` empty; `al_google_account_prep` then only checks that the account is signed in.

### Device Setup
1. Set up the Googlebook with the dedicated Google account, and connect it to the lab Wi-Fi network, on the same subnet as the Host.
1. Enable Developer mode:  Settings -> About device -> scroll down to "Build number" -> tap "Build number" 7 times.  When prompted, enter the device PIN.  After the confirmation that Developer mode is enabled, Developer options becomes available.
1. Enable USB debugging:  Settings -> System -> Developer options -> USB debugging.  Enable Wireless debugging in the same Developer options screen if using ADB over Wi-Fi.
1. Connect the DUT to the Host with a USB cable.  On the DUT, accept the "Allow USB debugging?" prompt and check "Always allow from this computer".
    1. On the HP Googlebook 14 used during initial bring-up, the left USB-C port enumerated over USB; the right port did not. Use the left port for initial ADB setup on this model, and verify ports separately on other models.
    1. Windows may show the device as a portable/MTP device before ADB is available. ADB requires USB debugging to be enabled and the Android debugging interface to enumerate.
1. On the Host, run `adb devices` and make sure the DUT is listed as `device`.  If it is listed as `unauthorized`, unlock the DUT and accept the prompt.
    1. Alternatively, ADB can be used over Wi-Fi without a cable:  Developer options -> Wireless debugging -> Pair device with pairing code.  On the Host, run `adb pair <ip>:<pairing port>` with the IP address and port shown, and enter the pairing code.  Android 17 with ADB 37 may reconnect automatically on a trusted network; otherwise run `adb connect <ip>:<port>` using the device's current Wireless debugging address and port.
1. Remove any screen lock:  Settings -> Security & privacy -> Device unlock -> Screen lock -> None.  Otherwise the lock screen will interrupt automation.
1. On the Host, run `setup_src\src_dut_aluminium\dut_setup_aluminium.ps1 -ProfilePath <device profile .ini>` in PowerShell.  If more than one device is connected, specify one with `-Serial <serial or ip:port>`.  This will:
    1. Join the Wi-Fi network in the profile's `dut_wifi_name` and `dut_wifi_password`, the same settings the Windows dut_setup uses, if they are set.  The password is passed to the DUT only and is never shown.  The network is saved once, shared with all Android users, and uses the device's own MAC address.  A network added in Settings is saved for the signed-in user only, with a random MAC address that changes daily, so after a restart the login screen has no network or a different IP address, and HOBL can't reach the DUT to sign in.  The network can only be changed over USB, since changing it would disconnect Wireless debugging; over Wireless debugging, setup warns if the network was saved in Settings.
    1. Warn if the DUT's IP address is different from the profile's `dut_ip`.
    1. Install the agent to /data/local/tmp/hobl_bin on the DUT.
    1. Apply test settings, the same as the Windows dut_setup:  the display never turns off, the lock screen is disabled, and adaptive brightness is turned off.
    1. Start the agent, allowing connections only from the Host.
    1. Over USB, turn on Wireless debugging and connect to it.  A Host that was allowed with "Always allow from this computer" over USB is also trusted over Wireless debugging, so no pairing code is needed, and Android's "Allow wireless debugging on this network?" prompt is accepted automatically.  Use `-SkipWirelessDebugging` to leave Wireless debugging unchanged.
    1. Report the DUT's IP address, to use as dut_ip in the device profile.
    1. Run this setup after the final test account is signed in.  If you add, remove, or switch the Android user/account later, rerun setup.  Measured scenarios check the screen timeout before they start, and fail with a message to rerun setup if the screen could turn off.
1. Disconnect the USB cable.  The agent keeps running, and the cable must not be connected during measurements since it charges the DUT.
1. Create a device profile from profile_templates\aluminium.ini.  Set dut_ip, and set dut_architecture to x64 if dut_setup_aluminium.ps1 reported x86_64, or arm64 for arm64-v8a.
1. Find the display brightness that gives 150 nits, as described in [Display Brightness](#display-brightness), with `setup_src\src_dut_aluminium\calibrate_brightness.ps1 -DeviceIp <dut_ip> -ProfilePath <device profile .ini>`.  The DUT shows a full-screen white page; for each brightness the script tries, measure the center and the four corners with a luminance meter and type the average.  It narrows down to the brightness within 3 nits of the target and writes `nits_map` to the `[display]` section of the profile (a backup is kept).  Use `-TargetNits 150,200` to also calibrate the 200 nits used by JEITA tests.  A lab with a scriptable meter can pass `-MeterCommand "<command that prints the nits>"` to calibrate without a person.
    1. On Aluminium, display:brightness is a percentage of Android's brightness setting (0-255), which is **not** the position of the brightness slider: the slider follows a perceptual curve, so 80% on the slider can be about 15% of the setting.  Don't calibrate with the slider.  On the Googlebooks used for bring-up, 150 nits was about 36% (HP Googlebook 14) and 13% (Acer Googlebook 14).
1. Leave the audio volume at the out-of-box level.
1. Test the network connection to the DUT:
    1. Host and DUT need to be on the same subnet (first 2 octets of the IP address).
    1. Run Cmd or Powershell on the Host, and make sure the DUT responds to pings:  `ping <dut_ip>`
    1. Run the "comm_check" scenario to make sure that all communications needs are met.
    1. Run the "al_agent_check" scenario to make sure that all agent functions work on this DUT.
1. For web scenarios, configure Chrome for web_replay.  Unlock the active Android user, connect ADB, and run `setup_src\src_dut_aluminium\install_web_replay_certs.ps1 -DeviceIp <dut_ip>` in PowerShell.
    1. On a build with the `android.software.device_admin` feature, the script installs a test-only profile-owner app for the active Android user and silently installs only the web_replay root and intermediate CA certificates. Remove them and the test app later with `install_web_replay_certs.ps1 -DeviceIp <dut_ip> -Remove`.
    1. The HP and Acer Android 17 builds do not advertise `android.software.device_admin`, so they cannot grant profile-owner rights to this app. On these devices, the script instead enables Chrome's "Enable command line on non-rooted devices" flag and configures a narrowly scoped SPKI allowlist for the two web_replay leaf keys. This is not a CA installation and does not disable certificate checks for other certificates. Chrome warns that the command-line feature is unsupported; this warning is expected on the test DUT.
    1. Chrome must be unlocked when the script runs. Verify in `chrome://version` that the Command Line includes `--ignore-certificate-errors-spki-list`. The `-Remove` option deletes the command-line file, resets this Chrome flag to Default, and clears Chrome's persistent debug-app setting.
    1. To retain the manual Android Settings flow instead, use `install_web_replay_certs.ps1 -DeviceIp <dut_ip> -Manual`. On Android user 0 it copies the CA files to Downloads; on a secondary user it opens the release ZIP in Chrome for that user.

### Accounts and Prep Scenarios
Accounts are stored the same way as on Windows: in the device profile, which is kept outside the repository (for example in c:\profiles, where the HOBL UI keeps profiles) and must never be committed.  Avoid folders that sync to the cloud.  HOBL replaces password, PIN, and access key values with `********` in its logs.  The Aluminium keys, with the same names as Windows where Windows has the setting, are in profile_templates\aluminium.ini:

| Profile setting | Used for |
|---|---|
| `[global] dut_wifi_name`, `dut_wifi_password` | Wi-Fi joined by dut_setup_aluminium.ps1 |
| `[global] google_account`, `google_password` | Google test account (`al_google_account_prep`) |
| `[global] msa_account`, `dut_password` | Microsoft account for Microsoft 365 (`al_office_prep`), and for Teams if the `[teams_install]` keys are empty |
| `[teams_install] teams_msa_account`, `teams_msa_password` | Teams test account (`al_teams_prep`), when it isn't msa_account, as on Windows |
| `[netflix] netflix_username`, `netflix_password` | `al_netflix` |
| `[teams] access_key` | Teams bots server; request a key from HOBLsupport@microsoft.com |

* Run the `al_accounts_check` scenario to see which accounts are set up.  It only reports "set" or "missing", never the values.  `al_accounts_check:required="netflix microsoft"` makes it fail if those are missing.
* The `prep` scenario works on Aluminium the same way as on Windows: `hobl.cmd -p <profile> -s prep prep:scenarios_to_prep="al_web al_lvp"` runs the prep scenarios those scenarios need, plus the Aluminium common preps in `prep:aluminium_common_preps`, skipping preps that have already run.  The prep scenarios are:
    * `al_google_account_prep`: makes sure the test user is signed in to `google_account`, signing in if needed.  Google may ask for extra verification for a new sign-in; the scenario then fails, and the account must be added on the DUT by hand once.
    * `al_app_install_prep`: installs Netflix, Word, Excel, PowerPoint, Outlook, OneNote, Teams, OneDrive, and Edge from the Play Store, skipping apps that are installed.  `al_app_install_prep:apps="edgebeta edgedev edgecanary"` installs the Edge preview channels, used by the browser study.  The first install for a Google account asks to complete the account setup with an optional payment method; this is skipped automatically.
    * `al_office_prep`: signs in to the Microsoft 365 apps with `msa_account`.  Word, Excel, and PowerPoint can't be used without signing in on Googlebook-sized screens, and editing needs a Microsoft 365 subscription.
    * `al_web_prep`: dismisses the browser's first-run, sign-in, sync, notification, and default browser prompts without accepting them, and clears Chrome's cached files.  Run it for each browser used, with `global:browser`.
        * The web scenarios (`al_web`, `al_youtube`, `al_netflix`, `al_speedometer`, `al_webxprt`, and the ABL scenarios) use the browser in `global:browser`, the same setting as Windows: `Chrome` (the Aluminium profile template's default), or `Edge`, `Edge Beta`, `Edge Dev` or `Edge Canary` (Edge for Android).
        * Edge trusts web_replay's certificates the same way as Chrome:  `al_web_prep` turns on Edge's "Enable command line on non-rooted devices" flag, and each web scenario writes the web_replay certificates to Edge's command-line file and makes the selected browser Android's debug app, since only one app at a time reads its command-line file.  Run `install_web_replay_certs.ps1` first for Chrome.
        * The Edge build the Play Store installs (156) contains only arm64 code, so Edge crashes on start on x86_64 Googlebooks, such as the Acer Googlebook 14; the web scenarios fail with a message about it.  Run the browser studies on arm64 Googlebooks until an x86_64 build is available.
        * Edge for Android has no page for clearing cached files, so `al_web_prep` keeps Edge's cache.  Edge keeps its own cookies, so sign in to Netflix in Edge once by hand if Netflix emails a sign-in code.
    * `al_lvp_prep`: copies the Tears of Steel video used by the Windows lvp scenario to the test user's Movies folder.  The video is downloaded to the Host's downloads folder the first time and stored as MP4 without re-encoding.
    * `al_lvp_jeita_prep`: copies the JEITA JB3_0 battery life test video (about 1.3 GB, downloaded from JEITA the first time) to the Movies folder, for `al_lvp_jeita`.  Windows also sets the JEITA JB3_0 desktop image for JEITA tests; the Googlebook builds used for bring-up show the default wallpaper for the test user whatever wallpaper is set, even from Settings, so the Aluminium JEITA plans keep the default wallpaper.
    * `al_productivity_prep`: prepares Outlook, Excel, Word, PowerPoint, and OneNote for `al_productivity`, `al_idle_apps`, `al_abl_active`, and `al_abl_standby`.  It copies the Windows productivity documents (scenarios\windows\_library\productivity\abl_docs) to the test user's Documents\abl_docs folder, lets the Office apps open them (Android's "All files access", granted with `appops`), turns off the apps' notifications, and opens each app once to clear its first-run pages, signing Outlook in to `msa_account`.  Run `al_office_prep` first.
        * Outlook attaches the picture and document from Documents\abl_docs instead of inserting them inline, and deletes its draft from the Drafts folder, since Outlook for Android has no Discard command.
        * OneNote for Android inserts pictures through its camera (Office Lens), so OneNote keeps the time Windows spends inserting the Hummingbird picture without inserting it.
        * Excel 16.0.20625 and earlier crash when opening any workbook on x86_64 Googlebooks, such as the Acer Googlebook 14; `al_productivity_prep` fails with a message about it.  Update Excel from the Play Store when a fixed version is available.  Word, PowerPoint, Outlook, and OneNote work.
    * `al_teams_prep`: signs in to the Teams app with the Teams account, the Aluminium version of Windows' teams_install.  It allows Teams the camera, microphone, and phone permissions (Teams can't join a meeting without the phone permission, since it places calls through Android's telecom service) and turns off its notifications, location, nearby devices, and contacts requests.  The account must sign in without extra verification.
        * The Teams scenarios (`al_teams2_1on1_audio`, `al_teams2_1on1_video`, `al_teams2_3x3_audio`, `al_teams2_3x3_video`, `al_teams2_3x3_vid_share`, `al_teams2_5p_rpres`, `al_teams2_idle`) use the same `teams` parameters and Teams bots service as Windows; set `[teams] access_key` in the profile.  The meeting and bots are created, checked, and removed on the Host with the Windows Teams code; the DUT joins the meeting in the Teams app, maximizes the call window, and sets its camera and microphone in the call.
        * A Teams account can only be in one call at a time.  If several DUTs share an account, don't run Teams scenarios on them at the same time.
        * Sharing the DUT's screen (`teams:send_screen=1`, used by Windows' teams2_3x3_present, teams2_audio_desktop and teams2_10p_aud_dtop), Teams call health, and Teams log collection aren't available on Aluminium.
* Charger control uses the same `charge_on_call` and `charge_off_call` host commands as Windows, for example a smart plug.  `al_recharge` waits for the DUT to report AC or battery power after each command.  If no command is configured, `charge_on`/`charge_off` and `auto_charge` prompt the Host operator to connect or disconnect the charger.

### Daily Operation
* The agent does not start automatically when the DUT boots.  While HOBL waits for an Aluminium DUT ("Waiting for DUT communication"), for example after a reboot or at the end of a rundown, it relaunches the agent every 30 seconds by running `setup_src\src_dut_aluminium\launch_agent.ps1 -DeviceIp <dut_ip>`.  This finds the DUT among the devices paired with Wireless debugging by its IP address, so several Googlebooks can be paired with the same Host.  Wireless debugging uses a new port each time the DUT starts; if ADB hasn't reconnected by itself, the script finds the port with `adb mdns services` and connects to it.  After a shutdown, connecting the charger and pressing the power button is normally all that's needed.
    * adb is found from PATH, or from ANDROID_HOME or ANDROID_SDK_ROOT, including values saved for the user or machine after the PowerShell window was opened.
    * To keep the DUT's IP address from changing, reserve it in the router's DHCP settings.  Signing in to Wi-Fi again, for example after changing the test account, can assign a new address.
    * If the DUT doesn't reconnect automatically, run `adb connect <ip>:<port>` with the address and port shown on its Wireless debugging screen.
    * The agent can also be restarted by hand with `launch_agent.ps1`.  To turn off automatic relaunch, set `aluminium_agent_relaunch=0` in the `[global]` section of the profile.
    * After a restart, Googlebooks show the login screen, and the test user stays locked until its PIN is entered.  Set `dut_pin` in the profile, and HOBL signs in by itself:  `launch_agent.ps1` verifies the PIN and switches to the test user over ADB (Wireless debugging stops while the user is switched, so the agent can't do this), then HOBL enters the PIN on the lock screen once the agent is running.  The PIN is sent to the DUT on standard input, never on a command line, and is not logged.  If the PIN is rejected, HOBL stops trying, since each wrong PIN locks the user out for longer.  Without `dut_pin`, sign in by hand.
* `testplans\al_rundown_idle.ps1` waits for the agent after the rundown.  If the Googlebook powered off, reconnect its charger and press the power button; the test plan continues once the agent responds.  The configuration data is copied to the Host when the run starts, since it can't be copied from a DUT that has shut down.
* Windows-format Aluminium plans are provided under `testplans\al_*.ps1`: hobl, hobl_smoke, hobl_etl, hobl_prep, hobl_prep_smoke, fundamentals, manual, cellular (manual-only; these DUTs have no WWAN), ctq_teams, ctq_teams_pmu, ctq_browser_study, ctq_browser_study_media, hobl_gate (al_hobl_gate.json, launched by al_hobl_gate_prep.ps1), the JEITA plans, and the web, LVP, and ABL rundown plans.  The browser studies compare Chrome and the Edge channels with `al_web`, `al_netflix` and `al_youtube`; Windows' third media arm uses scenarios that aren't in the repository.  `al_ctq_teams_pmu.ps1` records a Perfetto CPU scheduling, frequency, and idle trace (`perfetto_trace`) instead of the Windows PMU counters.  Plans with Teams steps must not run on two DUTs with the same Teams account at once.  The battery rundowns are long; run them from an interactive PowerShell window after the short workload checks.
* `al_battery_saver` turns Android's Battery Saver on or off, the Aluminium version of Windows' energy_saver, used by `al_hobl_gate.json`.  Android doesn't run Battery Saver while charging, so on AC power `state=1` sets it to turn on when the charger is disconnected and to stay on after a full charge.
* `testplans\al_rundown_web.ps1` runs the 100-loop Aluminium web workload and collects a study report.  Charger connection/disconnection is prompted unless the profile has host charger-control commands.
* `al_net_prep` validates that the DUT is on the profile's `dut_wifi_name`.  It does not switch networks over wireless ADB; use USB and `dut_setup_aluminium.ps1` to change the DUT's network.
* The agent log is on the DUT, and can be viewed with `adb shell cat /data/local/tmp/hobl_bin/AluminiumAgent/agent.log`.
* To collect Android logs for a problem, run `adb logcat -d > logcat.txt`, or `adb bugreport bugreport.zip` for a full report.
* ScenarioMaker works with Aluminium DUTs the same way as Windows and macOS DUTs.
* Run `testplans\al_rundown_idle.ps1 "<path to profile.ini>"` from the HOBL repository in an interactive PowerShell window; do not launch it as a background or non-interactive process.

Current limitations on Aluminium:
* `al_web` opens the twelve default Windows web_replay sites in seven browser tabs (Chrome by default), with the Windows web scenario's tab order, page timings, searches and scrolls, and clears cached files before each loop while preserving cookies and the signed-in test account.  `al_web:web_workload` selects a subset of sites, as on Windows.  Scrolling uses Page Down and Page Up instead of the mouse wheel so it reaches Chrome whatever its window size, and steps that Windows finds by image match (the Amazon search bar, the first Instagram reel and the YouTube quality menu) keep their timing without the interaction.  The recorded YouTube videos load but YouTube's player pauses them in Chrome on Aluminium (the recording's streaming requests don't match Android Chrome's), so the YouTube part of `al_web` is not representative video playback.
* To record a new web_replay archive from a Googlebook, run `testplans\al_ctq_web_replay_record.ps1 <profile>`: `al_wr_record_start` starts a recording server on the Host and points the DUT's proxy at it, `al_web` runs with `global:web_replay_action=bulk_record`, and `al_wr_record_stop` stops the server and clears the proxy.  It records into `C:\web_replay\<version>\recordings\al_web_recording`; replay it with `global:web_replay_recording=al_web_recording`.  `testplans\al_wr_record.json` records, replays and removes Instagram cookies, like Windows' `wr_record.json`; its idle-timeout step is disabled because Chrome on Android can't capture the netlog it needs.
* For that reason `al_youtube` plays the live site by default (`al_youtube:web_replay=0`).  A YouTube archive recorded from Chrome on a Googlebook with `al_ctq_web_replay_record.ps1` doesn't play either: the player stays black in replay.  It uses the same parameters as Windows (duration, loop_duration, full_screen) and verifies playback after each loop with Android's media session.  The media session reports pauses and stops, but not short buffering stalls.
* `al_netflix` mirrors the Windows browser flow and needs a Netflix account in the profile.  Netflix may email a sign-in code instead of asking for the password; if `al_netflix` reports that, sign in to Netflix once by hand in Chrome on the DUT.  The sign-in is kept between runs.  `al_office_prep` needs a Microsoft account; the Microsoft 365 productivity workload and the Teams scenarios are not yet ported.
* `al_lvp` plays the video with Google Photos, full screen, restarting it when it ends.  Airplane mode is not supported, since it would disconnect the agent.
* `al_standby` measures connected standby by default.  The disconnected mode turns Wi-Fi off on the DUT and needs `cs_floor:button_wake_callback` to wake it.
* `al_read128kseq` and `al_write128kseq` use toybox dd with direct I/O instead of diskspd; throughputs are indicative, since storage encryption may still cache data.  iperf3 and random 4 KB disk tests are not available, since Android has no iperf3 or diskspd equivalent.
* Without a power measurement device, `battery_energy`, `al_standby`, `power_light`, `power_heavy`, and `powercfg` use the battery charge counter to estimate total average power.  Its resolution is about 1 mAh; if it does not change during a short run, HOBL reports the measurement as below resolution instead of reporting 0 W.  Battery-derived power is not reported while the DUT is on AC/USB power.
* `power_light` records Android's `android.power` Perfetto source and a charge-counter summary; `power_heavy` adds detailed ftrace/atrace categories and has significant measurement overhead; `powercfg` saves Android battery check-in, power-state, and device-idle reports.  The Acer exposes PowerStats channels (SoC/package, CPU cores, GPU, DRAM, system), which are present in its Perfetto trace; the HP does not expose PowerStats channels.  HOBL currently reports charge-counter total power rather than separate per-component watts.
* Only the primary display is supported.
* `screen_record` uses Android's screenrecord, and `perfetto_trace` records a Perfetto trace (the equivalent of etl_trace), to open at https://ui.perfetto.dev.  The display tool supports brightness only.  The original brightness and adaptive-brightness setting are saved the first time the tool changes them and restored when `display:display_restore=1` is set; otherwise the brightness set by HOBL remains in effect after the scenario.
