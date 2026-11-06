# Scenarios

## cinebench

The Cinebench benchmark.


<u>Parameters:</u>

`duration` - Minimum run time in seconds **Default:** `60` 

`workload` - Workload type: single_core or multi_core **Default:** `multi_core`  **Options:** `single_core, multi_core`

`installer_path` - Path to Cinebench installer on host machine. This should be the directory for your device architecture, containing the extracted Cinebench files, including cinebench.exe **Default:** `` 

## collect_logs

Collect various system logs.

## copilot

Nonfunctional.  Needs to be updated for new architecture.

## iperf3

Runs iperf3 network throughput tests against a remote server while measuring power.

Supports four predefined test profiles (T1-T4) drawn from the iperf3 test matrix, plus
a 'custom' option that accepts any iperf3 argument string. Power/performance collection
is enabled so each run captures the power impact of the traffic pattern alongside the
raw throughput numbers.

The scenario blocks on iperf3's process exit (expected exit code 0). The duration
parameter feeds the -t flag in the command; it does not drive any internal timer.

Results written to the run directory:
    iperf3_output.txt  —  raw iperf3 console output (stdout + stderr)
    iperf3.csv         —  parsed key metrics (throughput, jitter, packet loss)


<u>Parameters:</u>

`server_ip` - IP address of the iperf3 server (required for T1-T4) **Default:** `` 

`test_type` - Test profile to run: T1, T2, T3, T4, or custom **Default:** `T1`  **Options:** `T1, T2, T3, T4, custom`

`custom_arguments` - Full iperf3 argument string when test_type='custom'. Include everything after 'iperf3', e.g. '-c 192.168.1.1 -u -b100M -t 60'. Ignored for T1-T4. **Default:** `` 

`duration` - Seconds passed to iperf3 via -t (T1-T4 only). Also used to size the call timeout safety net for custom tests. **Default:** `300` 

`wlan_logging` - Set to '1' to capture Wi-Fi layer telemetry alongside iperf3. Logs adapter error/discard counter deltas (Get-NetAdapterStatistics), a 5-second channel/RSSI/rate poll time series, and WLAN AutoConfig event log entries (connects, disconnects, roaming, channel switches). Adds wlan_*.txt / wlan_events.csv to the results directory and appends wlan_* metrics to iperf3.csv. **Default:** `0`  **Options:** `0, 1`

## lvp

Plays a video on full screen for a specified amount of time.  


<u>Parameters:</u>

`title` - The file name of the video **Default:** `ToS-4k-1920` 

`duration` - Time to play the video in seconds **Default:** `300` 

`airplane_mode` - Enable airplane mode during video playback **Default:** `0`  **Options:** `0, 1`

`radio_enable` - Enable or disable radio during video playback if airplane_mode parameter is set to 1 **Default:** `1`  **Options:** `0, 1`

## lvp_jeita

Plays a video in full screen mode in accordance with requirements set by the Japan Electronics and Information Technology Industries Association for battery operated electronic devices being released in Japan.

Please do not alter parameters as they have been set to meet the requirements of that governing body


<u>Parameters:</u>

`title` - The file name of the video **Default:** `ToS-4k-1920` 

`duration` - Time to play the video in seconds **Default:** `300` 

`airplane_mode` - Enable airplane mode during video playback **Default:** `0`  **Options:** `0, 1`

`radio_enable` - Enable or disable radio during video playback if airplane_mode parameter is set to 1 **Default:** `1`  **Options:** `0, 1`

## mincp_all

Microsoft Teams video call with 9 bot participants.
Local camera and mic are on, other 9 participants are bots sending video and audio.


<u>Parameters:</u>

`meeting_time` - Set the time in minutes that the meeting can last up to. Default is teams:duration + 30 min. **Default:** `0` 

`access_key` - The access key for the Teams Bots Server. Contact HOBL Support to inquire for a key. **Default:** `-1` 

`number_of_bots` - Sets the number of bots to have in the meeting. **Default:** `1`  **Options:** `1, 2, 4, 8, 9`

`bots_send_video` - Set to 1 if bots should have their cameras on. Set to 0 for audio only calls. **Default:** `1`  **Options:** `0, 1`

`bots_send_audio` - Set to 1 to have bots send audio. Set to 0 to have bots be muted. **Default:** `1`  **Options:** `0, 1`

`bots_share_screen` - Set to 1 to have the primary bot share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`bots_test_server` - For advanced use. Set to 1 to use the testing instance of the bots server. Not Recomended for general use. **Default:** `0`  **Options:** `0, 1`

`send_video` - Set to 1 to have the DUT turn on its camera. Set to 0 to have the DUT camera off. **Default:** `1`  **Options:** `0, 1`

`send_audio` - Set to 1 to have the DUT have its mic on. Set to 0 to have the DUT be muted. **Default:** `1`  **Options:** `0, 1`

`send_screen` - Set to 1 to have the DUT share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`presentation_video_path` - Sets the path to the video file to use as the presented screen when the DUT is screen sharing. **Default:** `\teams_resources\ppt.mp4` 

`show_desktop` - Set to 1 to have the DUT screen share their desktop when screen sharing. Set to 0 to share a video of a presentation instead. **Default:** `0`  **Options:** `0, 1`

`bots_force_subscribe_resolution` - Force the bots to subscribe to a specific video resolution **Default:** `0`  **Options:** `0, 1080, 720, 480, 360`

`duration` - The time in seconds to call for. Default is 600s or 5min. **Default:** `600`  **Options:** `60, 120, 300, 600`

`parse_MSTeams_Logs` - Set to 1 to parse Teams logs after collecting them. **Default:** `1`  **Options:** `0, 1`

`parser_location` - Sets the path to the parser to use to decode Teams logs. **Default:** `..\ScenarioAssets\Teamsdecode\bin\UnifiedLogging` 

`collect_call_health` - Set to 1 to have the call health data collected. **Default:** `1`  **Options:** `0, 1`

`collect_MSTeams_Logs` - Set to 1 to collect MS Teams logs of the meeting after exiting the meeting. **Default:** `1`  **Options:** `0, 1`

`web_workload` - Specific websites to run. **Default:** `amazongot amazonvacuum googleimagesapollo googleimageslondon googlesearchbelgium googlesearchsuperbowl instagram reddit theverge wikipedia youtubenasa youtubetos`  **Options:** `amazonbsg, amazongot, amazonvacuum, googleimagesapollo, googleimageslondon, googlesearchbelgium, googlesearchsuperbowl, instagram, reddit, theverge, wikipedia, youtubenasa, youtubetos`

`mincp_workloads` -  **Default:** `live_captions copilot_query semantic_search click_todo productivity studioeffect_blur`  **Options:** `live_captions, copilot_query, semantic_search, click_todo, studioeffect_blur, productivity`

`background_timers` -  **Default:** `1`  **Options:** `0, 1`

`background_teams` -  **Default:** `1`  **Options:** `0, 1`

`background_onedrive_copy` -  **Default:** `1`  **Options:** `0, 1`

`simple_office_launch` -  **Default:** `0`  **Options:** `1, 0`

`perf_run` -  **Default:** `0`  **Options:** `0, 1`

## net_prep_wifi

Set device routing table to prefer Wi-Fi connection between DUT and HOBL Host, to ensure that prep scenarios do not run over cellular.


<u>Parameters:</u>

`net_prep_enabled` -  **Default:** `1` 

`connection` -  **Default:** `Wi-Fi` 

## perf_stress

Install pyenv + Python + numpy/psutil on DUT for percentile_stress.py


<u>Parameters:</u>

`meeting_time` - Set the time in minutes that the meeting can last up to. Default is teams:duration + 30 min. **Default:** `0` 

`access_key` - The access key for the Teams Bots Server. Contact HOBL Support to inquire for a key. **Default:** `-1` 

`number_of_bots` - Sets the number of bots to have in the meeting. **Default:** `1`  **Options:** `1, 2, 4, 8, 9`

`bots_send_video` - Set to 1 if bots should have their cameras on. Set to 0 for audio only calls. **Default:** `1`  **Options:** `0, 1`

`bots_send_audio` - Set to 1 to have bots send audio. Set to 0 to have bots be muted. **Default:** `1`  **Options:** `0, 1`

`bots_share_screen` - Set to 1 to have the primary bot share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`bots_test_server` - For advanced use. Set to 1 to use the testing instance of the bots server. Not Recomended for general use. **Default:** `0`  **Options:** `0, 1`

`send_video` - Set to 1 to have the DUT turn on its camera. Set to 0 to have the DUT camera off. **Default:** `1`  **Options:** `0, 1`

`send_audio` - Set to 1 to have the DUT have its mic on. Set to 0 to have the DUT be muted. **Default:** `1`  **Options:** `0, 1`

`send_screen` - Set to 1 to have the DUT share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`presentation_video_path` - Sets the path to the video file to use as the presented screen when the DUT is screen sharing. **Default:** `\teams_resources\ppt.mp4` 

`show_desktop` - Set to 1 to have the DUT screen share their desktop when screen sharing. Set to 0 to share a video of a presentation instead. **Default:** `0`  **Options:** `0, 1`

`bots_force_subscribe_resolution` - Force the bots to subscribe to a specific video resolution **Default:** `0`  **Options:** `0, 1080, 720, 480, 360`

`duration` - The time in seconds to call for. Default is 600s or 5min. **Default:** `600`  **Options:** `60, 120, 300, 600`

`parse_MSTeams_Logs` - Set to 1 to parse Teams logs after collecting them. **Default:** `1`  **Options:** `0, 1`

`parser_location` - Sets the path to the parser to use to decode Teams logs. **Default:** `..\ScenarioAssets\Teamsdecode\bin\UnifiedLogging` 

`collect_call_health` - Set to 1 to have the call health data collected. **Default:** `1`  **Options:** `0, 1`

`collect_MSTeams_Logs` - Set to 1 to collect MS Teams logs of the meeting after exiting the meeting. **Default:** `1`  **Options:** `0, 1`

`web_workload` - Specific websites to run during stress workload. reddit must be included (Tab 1 with new_tab=0). **Default:** `reddit amazongot googleimagesapollo youtubetos`  **Options:** `amazonbsg, amazongot, amazonvacuum, googleimagesapollo, googleimageslondon, googlesearchbelgium, googlesearchsuperbowl, instagram, reddit, theverge, wikipedia, youtubenasa, youtubetos`

`background_teams` -  **Default:** `1`  **Options:** `0, 1`

`stress_run` - For perf metrics **Default:** `1`  **Options:** `0, 1`

`stress_cpu_target` - Target CPU load percentage for stress mode. **Default:** `25`  **Options:** `0, 25, 50, 65, 75, 85`

`background_onedrive_copy` -  **Default:** `1`  **Options:** `0, 1`

`simple_office_launch` -  **Default:** `1`  **Options:** `1, 0`

`shell_probes` -  **Default:** `1`  **Options:** `0, 1`

`sleep_resume_midrun` - This will actually sleep the DUT (pressing the power button) **Default:** `0`  **Options:** `0, 1`

`edge_close_relaunch` - 1 = mid-run kill msedge and relaunch with 12 foreground sites. Side effect: destroys background Edge tabs (no automatic restore). Default 0 keeps bg tabs alive for the entire run. **Default:** `0`  **Options:** `0, 1`

`perftrack_app_launch` -  **Default:** `1`  **Options:** `0, 1`

`provider` - WPRP file to use for perf_utc tracing. **Default:** `perf_utc.wprp`  **Options:** `abl_perf.wprp, full_th.wprp, full_th_wpp.wprp, general_cpi_collector.wprp, GTPLight_CustomMemHardFaults.wprp, multimedia.wprp, perf_utc.wprp, pmu.wprp, power.wprp, power_heavy.wprp, power_light.wprp, power_memory.wprp, productivity_perf.wprp, stack_walk.wprp, thermal_power_light.wprp, web_perf.wprp`

`bg_heavy_capture` - 1 = launch collect_5min_traces.ps1 in the background on the DUT alongside the core trace. Uses a named WPR instance (perfStressHeavy). Saves rolling ETLs to C:\hobl_bin\perf_stress_heavy\<RunName>\WPR_<timestamp>.etl. WARNING: dual-session WPR perturbs metrics - debug use only. **Default:** `0`  **Options:** `0, 1`

`bg_heavy_capture_interval` - Rolling ETL segment length in minutes for bg_heavy_capture (default 5). A 15-20 min run at 5 min should produce ~3 segments; shorten if wpr -stop flush eats into the next interval. **Default:** `5`  **Options:** `3, 4, 5, 6`

`bg_edge_tabs` - 1 = open background Edge tabs to increase memory pressure and CPU stress. **Default:** `1`  **Options:** `0, 1`

`bg_edge_tab_loops` - Iterations of the web_bg_tabs site loop. Each iteration opens 5 background Edge tabs. Default 6 = 30 background tabs **Default:** `6`  **Options:** `1, 2, 3, 4, 5, 6, 8, 10`

## process_idle_tasks

Preforms various tasks that prepare a device for testing.  This includes queuing background maintenance tasks in Windows so they will not be running during tests.  To ensure consistent results, please run this scenario at least once per day on devices before starting tests.


<u>Parameters:</u>

`timeout` - Maximum time in seconds the automation will wait for tasks to complete **Default:** `1800` 

`loops` - Number of times the automation will attempt to perform tasks **Default:** `3` 

`run_idle_tasks` - Queues Windows idle tasks so they will not be running during tests **Default:** `1`  **Options:** `0, 1`

`final_reboot` - Sets if the device will reboot at the conclusion of process_idle_tasks **Default:** `1`  **Options:** `0, 1`

## standby

Puts the device into standby mode, still connected to the network.


<u>Parameters:</u>

`cs_duration` -  **Default:** `1200` 

`button_to_record_delay` -  **Default:** `900` 

`button_sleep_callback` -  **Default:** `` 

`button_wake_callback` -  **Default:** `` 

`local_button` -  **Default:** `1` 

`sleep_mode` -  **Default:** `` 

`connection` - Connected or Disconnected from the network during standby **Default:** `Connected`  **Options:** `Disconnected, Connected`

## system_prep

Performs various tasks that prepare a device for testing.


<u>Parameters:</u>

`hibernate_enabled` - Enables or disables hibernation on the device **Default:** `1`  **Options:** `0, 1`

`telemetry_enabled` - Enables or disables the gathering of optional diagnostic data in the OS **Default:** `0`  **Options:** `0, 1`

`theme` - Change the Windows theme **Default:** `current`  **Options:** `current, light, dark`

`wallpaper` - Sets the device's background image.  Uses image files stored in the %SYSTEMDRIVE%\hobl_bin\DesktopImages folder **Default:** `ColorChecker3000x2000.png` 

`final_reboot` - Sets if the device will reboot at the conclusion of daily_prep **Default:** `1`  **Options:** `0, 1`

`bpm_pcc_blm_disable` - Disable BPM, PCC, and BLM **Default:** `0`  **Options:** `0, 1`

## teams2_10p_aud_dtop

Microsoft Teams audio call with 9 bot participants.
Local camera is off and mic is on, other 9 participants are bots sending audio.
Local user is sharing desktop.


<u>Parameters:</u>

`meeting_time` - Set the time in minutes that the meeting can last up to. Default is teams:duration + 30 min. **Default:** `0` 

`access_key` - The access key for the Teams Bots Server. Contact HOBL Support to inquire for a key. **Default:** `-1` 

`number_of_bots` - Sets the number of bots to have in the meeting. **Default:** `9`  **Options:** `1, 2, 4, 8, 9`

`bots_send_video` - Set to 1 if bots should have their cameras on. Set to 0 for audio only calls. **Default:** `0`  **Options:** `0, 1`

`bots_send_audio` - Set to 1 to have bots send audio. Set to 0 to have bots be muted. **Default:** `1`  **Options:** `0, 1`

`bots_share_screen` - Set to 1 to have the primary bot share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`bots_test_server` - For advanced use. Set to 1 to use the testing instance of the bots server. Not Recomended for general use. **Default:** `0`  **Options:** `0, 1`

`send_video` - Set to 1 to have the DUT turn on its camera. Set to 0 to have the DUT camera off. **Default:** `0`  **Options:** `0, 1`

`send_audio` - Set to 1 to have the DUT have its mic on. Set to 0 to have the DUT be muted. **Default:** `1`  **Options:** `0, 1`

`send_screen` - Set to 1 to have the DUT share its screen in the meeting. **Default:** `1`  **Options:** `0, 1`

`presentation_video_path` - Sets the path to the video file to use as the presented screen when the DUT is screen sharing. **Default:** `\teams_resources\ppt.mp4` 

`show_desktop` - Set to 1 to have the DUT screen share their desktop when screen sharing. Set to 0 to share a video of a presentation instead. **Default:** `1`  **Options:** `0, 1`

`bots_force_subscribe_resolution` - Force the bots to subscribe to a specific video resolution **Default:** `0`  **Options:** `0, 1080, 720, 480, 360`

`duration` - The time in seconds to call for. Default is 600s or 5min. **Default:** `300`  **Options:** `60, 120, 300, 600`

`parse_MSTeams_Logs` - Set to 1 to parse Teams logs after collecting them. **Default:** `1`  **Options:** `0, 1`

`parser_location` - Sets the path to the parser to use to decode Teams logs. **Default:** `..\ScenarioAssets\Teamsdecode\bin\UnifiedLogging` 

`collect_call_health` - Set to 1 to have the call health data collected. **Default:** `1`  **Options:** `0, 1`

`collect_MSTeams_Logs` - Set to 1 to collect MS Teams logs of the meeting after exiting the meeting. **Default:** `1`  **Options:** `0, 1`

`maintain_bots` - Set to 1 to have the test periodically check that all bots are present in the call and add bots if needed. **Default:** `1`  **Options:** `0, 1`

## teams2_1on1_audio

Microsoft Teams audio call with 1 bot participant.
Local camera is off and mic is on, other participant is a bot sending audio.


<u>Parameters:</u>

`meeting_time` - Set the time in minutes that the meeting can last up to. Default is teams:duration + 30 min. **Default:** `0` 

`access_key` - The access key for the Teams Bots Server. Contact HOBL Support to inquire for a key. **Default:** `-1` 

`number_of_bots` - Sets the number of bots to have in the meeting. **Default:** `1`  **Options:** `1, 2, 4, 8, 9`

`bots_send_video` - Set to 1 if bots should have their cameras on. Set to 0 for audio only calls. **Default:** `0`  **Options:** `0, 1`

`bots_send_audio` - Set to 1 to have bots send audio. Set to 0 to have bots be muted. **Default:** `1`  **Options:** `0, 1`

`bots_share_screen` - Set to 1 to have the primary bot share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`bots_test_server` - For advanced use. Set to 1 to use the testing instance of the bots server. Not Recomended for general use. **Default:** `0`  **Options:** `0, 1`

`send_video` - Set to 1 to have the DUT turn on its camera. Set to 0 to have the DUT camera off. **Default:** `0`  **Options:** `0, 1`

`send_audio` - Set to 1 to have the DUT have its mic on. Set to 0 to have the DUT be muted. **Default:** `1`  **Options:** `0, 1`

`send_screen` - Set to 1 to have the DUT share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`presentation_video_path` - Sets the path to the video file to use as the presented screen when the DUT is screen sharing. **Default:** `\teams_resources\ppt.mp4` 

`show_desktop` - Set to 1 to have the DUT screen share their desktop when screen sharing. Set to 0 to share a video of a presentation instead. **Default:** `0`  **Options:** `0, 1`

`bots_force_subscribe_resolution` - Force the bots to subscribe to a specific video resolution **Default:** `0`  **Options:** `0, 1080, 720, 480, 360`

`duration` - The time in seconds to call for. Default is 600s or 5min. **Default:** `300`  **Options:** `60, 120, 300, 600`

`parse_MSTeams_Logs` - Set to 1 to parse Teams logs after collecting them. **Default:** `1`  **Options:** `0, 1`

`parser_location` - Sets the path to the parser to use to decode Teams logs. **Default:** `..\ScenarioAssets\Teamsdecode\bin\UnifiedLogging` 

`collect_call_health` - Set to 1 to have the call health data collected. **Default:** `1`  **Options:** `0, 1`

`collect_MSTeams_Logs` - Set to 1 to collect MS Teams logs of the meeting after exiting the meeting. **Default:** `1`  **Options:** `0, 1`

`maintain_bots` - Set to 1 to have the test periodically check that all bots are present in the call and add bots if needed. **Default:** `1`  **Options:** `0, 1`

## teams2_1on1_video

Microsoft Teams video call with 1 bot participant.
Local camera and mic are on, other participant is a bot sending video and audio.


<u>Parameters:</u>

`meeting_time` - Set the time in minutes that the meeting can last up to. Default is teams:duration + 30 min. **Default:** `0` 

`access_key` - The access key for the Teams Bots Server. Contact HOBL Support to inquire for a key. **Default:** `-1` 

`number_of_bots` - Sets the number of bots to have in the meeting. **Default:** `1`  **Options:** `1, 2, 4, 8, 9`

`bots_send_video` - Set to 1 if bots should have their cameras on. Set to 0 for audio only calls. **Default:** `1`  **Options:** `0, 1`

`bots_send_audio` - Set to 1 to have bots send audio. Set to 0 to have bots be muted. **Default:** `1`  **Options:** `0, 1`

`bots_share_screen` - Set to 1 to have the primary bot share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`bots_test_server` - For advanced use. Set to 1 to use the testing instance of the bots server. Not Recomended for general use. **Default:** `0`  **Options:** `0, 1`

`send_video` - Set to 1 to have the DUT turn on its camera. Set to 0 to have the DUT camera off. **Default:** `1`  **Options:** `0, 1`

`send_audio` - Set to 1 to have the DUT have its mic on. Set to 0 to have the DUT be muted. **Default:** `1`  **Options:** `0, 1`

`send_screen` - Set to 1 to have the DUT share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`presentation_video_path` - Sets the path to the video file to use as the presented screen when the DUT is screen sharing. **Default:** `\teams_resources\ppt.mp4` 

`show_desktop` - Set to 1 to have the DUT screen share their desktop when screen sharing. Set to 0 to share a video of a presentation instead. **Default:** `0`  **Options:** `0, 1`

`bots_force_subscribe_resolution` - Force the bots to subscribe to a specific video resolution **Default:** `0`  **Options:** `0, 1080, 720, 480, 360`

`duration` - The time in seconds to call for. Default is 600s or 5min. **Default:** `300`  **Options:** `60, 120, 300, 600`

`parse_MSTeams_Logs` - Set to 1 to parse Teams logs after collecting them. **Default:** `1`  **Options:** `0, 1`

`parser_location` - Sets the path to the parser to use to decode Teams logs. **Default:** `..\ScenarioAssets\Teamsdecode\bin\UnifiedLogging` 

`collect_call_health` - Set to 1 to have the call health data collected. **Default:** `1`  **Options:** `0, 1`

`collect_MSTeams_Logs` - Set to 1 to collect MS Teams logs of the meeting after exiting the meeting. **Default:** `1`  **Options:** `0, 1`

`maintain_bots` - Set to 1 to have the test periodically check that all bots are present in the call and add bots if needed. **Default:** `1`  **Options:** `0, 1`

## teams2_3x3_audio

Microsoft Teams audio call with 9 bot participants.
Local camera is off and mic is on, other 9 participants are bots sending audio.


<u>Parameters:</u>

`meeting_time` - Set the time in minutes that the meeting can last up to. Default is teams:duration + 30 min. **Default:** `0` 

`access_key` - The access key for the Teams Bots Server. Contact HOBL Support to inquire for a key. **Default:** `-1` 

`number_of_bots` - Sets the number of bots to have in the meeting. **Default:** `9`  **Options:** `1, 2, 4, 8, 9`

`bots_send_video` - Set to 1 if bots should have their cameras on. Set to 0 for audio only calls. **Default:** `0`  **Options:** `0, 1`

`bots_send_audio` - Set to 1 to have bots send audio. Set to 0 to have bots be muted. **Default:** `1`  **Options:** `0, 1`

`bots_share_screen` - Set to 1 to have the primary bot share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`bots_test_server` - For advanced use. Set to 1 to use the testing instance of the bots server. Not Recomended for general use. **Default:** `0`  **Options:** `0, 1`

`send_video` - Set to 1 to have the DUT turn on its camera. Set to 0 to have the DUT camera off. **Default:** `0`  **Options:** `0, 1`

`send_audio` - Set to 1 to have the DUT have its mic on. Set to 0 to have the DUT be muted. **Default:** `1`  **Options:** `0, 1`

`send_screen` - Set to 1 to have the DUT share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`presentation_video_path` - Sets the path to the video file to use as the presented screen when the DUT is screen sharing. **Default:** `\teams_resources\ppt.mp4` 

`show_desktop` - Set to 1 to have the DUT screen share their desktop when screen sharing. Set to 0 to share a video of a presentation instead. **Default:** `0`  **Options:** `0, 1`

`bots_force_subscribe_resolution` - Force the bots to subscribe to a specific video resolution **Default:** `0`  **Options:** `0, 1080, 720, 480, 360`

`duration` - The time in seconds to call for. Default is 600s or 5min. **Default:** `600`  **Options:** `60, 120, 300, 600`

`parse_MSTeams_Logs` - Set to 1 to parse Teams logs after collecting them. **Default:** `1`  **Options:** `0, 1`

`parser_location` - Sets the path to the parser to use to decode Teams logs. **Default:** `..\ScenarioAssets\Teamsdecode\bin\UnifiedLogging` 

`collect_call_health` - Set to 1 to have the call health data collected. **Default:** `1`  **Options:** `0, 1`

`collect_MSTeams_Logs` - Set to 1 to collect MS Teams logs of the meeting after exiting the meeting. **Default:** `1`  **Options:** `0, 1`

`maintain_bots` - Set to 1 to have the test periodically check that all bots are present in the call and add bots if needed. **Default:** `1`  **Options:** `0, 1`

## teams2_3x3_present

Microsoft Teams video call with 9 bot participants.
Local camera and mic are on, other 9 participants are bots sending video and audio.
Local users is sharing screen.


<u>Parameters:</u>

`meeting_time` - Set the time in minutes that the meeting can last up to. Default is teams:duration + 30 min. **Default:** `0` 

`access_key` - The access key for the Teams Bots Server. Contact HOBL Support to inquire for a key. **Default:** `-1` 

`number_of_bots` - Sets the number of bots to have in the meeting. **Default:** `9`  **Options:** `1, 2, 4, 8, 9`

`bots_send_video` - Set to 1 if bots should have their cameras on. Set to 0 for audio only calls. **Default:** `1`  **Options:** `0, 1`

`bots_send_audio` - Set to 1 to have bots send audio. Set to 0 to have bots be muted. **Default:** `1`  **Options:** `0, 1`

`bots_share_screen` - Set to 1 to have the primary bot share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`bots_test_server` - For advanced use. Set to 1 to use the testing instance of the bots server. Not Recomended for general use. **Default:** `0`  **Options:** `0, 1`

`send_video` - Set to 1 to have the DUT turn on its camera. Set to 0 to have the DUT camera off. **Default:** `1`  **Options:** `0, 1`

`send_audio` - Set to 1 to have the DUT have its mic on. Set to 0 to have the DUT be muted. **Default:** `1`  **Options:** `0, 1`

`send_screen` - Set to 1 to have the DUT share its screen in the meeting. **Default:** `1`  **Options:** `0, 1`

`presentation_video_path` - Sets the path to the video file to use as the presented screen when the DUT is screen sharing. **Default:** `\teams_resources\ppt.mp4` 

`show_desktop` - Set to 1 to have the DUT screen share their desktop when screen sharing. Set to 0 to share a video of a presentation instead. **Default:** `0`  **Options:** `0, 1`

`bots_force_subscribe_resolution` - Force the bots to subscribe to a specific video resolution **Default:** `0`  **Options:** `0, 1080, 720, 480, 360`

`duration` - The time in seconds to call for. Default is 600s or 5min. **Default:** `600`  **Options:** `60, 120, 300, 600`

`parse_MSTeams_Logs` - Set to 1 to parse Teams logs after collecting them. **Default:** `1`  **Options:** `0, 1`

`parser_location` - Sets the path to the parser to use to decode Teams logs. **Default:** `..\ScenarioAssets\Teamsdecode\bin\UnifiedLogging` 

`collect_call_health` - Set to 1 to have the call health data collected. **Default:** `1`  **Options:** `0, 1`

`collect_MSTeams_Logs` - Set to 1 to collect MS Teams logs of the meeting after exiting the meeting. **Default:** `1`  **Options:** `0, 1`

`maintain_bots` - Set to 1 to have the test periodically check that all bots are present in the call and add bots if needed. **Default:** `1`  **Options:** `0, 1`

## teams2_3x3_video

Microsoft Teams video call with 9 bot participants.
Local camera and mic are on, other 9 participants are bots sending video and audio.


<u>Parameters:</u>

`meeting_time` - Set the time in minutes that the meeting can last up to. Default is teams:duration + 30 min. **Default:** `0` 

`access_key` - The access key for the Teams Bots Server. Contact HOBL Support to inquire for a key. **Default:** `-1` 

`number_of_bots` - Sets the number of bots to have in the meeting. **Default:** `9`  **Options:** `1, 2, 4, 8, 9`

`bots_send_video` - Set to 1 if bots should have their cameras on. Set to 0 for audio only calls. **Default:** `1`  **Options:** `0, 1`

`bots_send_audio` - Set to 1 to have bots send audio. Set to 0 to have bots be muted. **Default:** `1`  **Options:** `0, 1`

`bots_share_screen` - Set to 1 to have the primary bot share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`bots_test_server` - For advanced use. Set to 1 to use the testing instance of the bots server. Not Recomended for general use. **Default:** `0`  **Options:** `0, 1`

`send_video` - Set to 1 to have the DUT turn on its camera. Set to 0 to have the DUT camera off. **Default:** `1`  **Options:** `0, 1`

`send_audio` - Set to 1 to have the DUT have its mic on. Set to 0 to have the DUT be muted. **Default:** `1`  **Options:** `0, 1`

`send_screen` - Set to 1 to have the DUT share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`presentation_video_path` - Sets the path to the video file to use as the presented screen when the DUT is screen sharing. **Default:** `\teams_resources\ppt.mp4` 

`show_desktop` - Set to 1 to have the DUT screen share their desktop when screen sharing. Set to 0 to share a video of a presentation instead. **Default:** `0`  **Options:** `0, 1`

`bots_force_subscribe_resolution` - Force the bots to subscribe to a specific video resolution **Default:** `0`  **Options:** `0, 1080, 720, 480, 360`

`duration` - The time in seconds to call for. Default is 600s or 5min. **Default:** `600`  **Options:** `60, 120, 300, 600`

`parse_MSTeams_Logs` - Set to 1 to parse Teams logs after collecting them. **Default:** `1`  **Options:** `0, 1`

`parser_location` - Sets the path to the parser to use to decode Teams logs. **Default:** `..\ScenarioAssets\Teamsdecode\bin\UnifiedLogging` 

`collect_call_health` - Set to 1 to have the call health data collected. **Default:** `1`  **Options:** `0, 1`

`collect_MSTeams_Logs` - Set to 1 to collect MS Teams logs of the meeting after exiting the meeting. **Default:** `1`  **Options:** `0, 1`

`maintain_bots` - Set to 1 to have the test periodically check that all bots are present in the call and add bots if needed. **Default:** `1`  **Options:** `0, 1`

## teams2_3x3_vid_share

Microsoft Teams video call with 9 bot participants.
Local camera and mic are on, other 9 participants are bots sending video and audio.
One of the bots is sharing a video.


<u>Parameters:</u>

`meeting_time` - Set the time in minutes that the meeting can last up to. Default is teams:duration + 30 min. **Default:** `0` 

`access_key` - The access key for the Teams Bots Server. Contact HOBL Support to inquire for a key. **Default:** `-1` 

`number_of_bots` - Sets the number of bots to have in the meeting. **Default:** `9`  **Options:** `1, 2, 4, 8, 9`

`bots_send_video` - Set to 1 if bots should have their cameras on. Set to 0 for audio only calls. **Default:** `1`  **Options:** `0, 1`

`bots_send_audio` - Set to 1 to have bots send audio. Set to 0 to have bots be muted. **Default:** `1`  **Options:** `0, 1`

`bots_share_screen` - Set to 1 to have the primary bot share its screen in the meeting. **Default:** `1`  **Options:** `0, 1`

`bots_test_server` - For advanced use. Set to 1 to use the testing instance of the bots server. Not Recomended for general use. **Default:** `0`  **Options:** `0, 1`

`send_video` - Set to 1 to have the DUT turn on its camera. Set to 0 to have the DUT camera off. **Default:** `1`  **Options:** `0, 1`

`send_audio` - Set to 1 to have the DUT have its mic on. Set to 0 to have the DUT be muted. **Default:** `1`  **Options:** `0, 1`

`send_screen` - Set to 1 to have the DUT share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`presentation_video_path` - Sets the path to the video file to use as the presented screen when the DUT is screen sharing. **Default:** `\teams_resources\ppt.mp4` 

`show_desktop` - Set to 1 to have the DUT screen share their desktop when screen sharing. Set to 0 to share a video of a presentation instead. **Default:** `0`  **Options:** `0, 1`

`bots_force_subscribe_resolution` - Force the bots to subscribe to a specific video resolution **Default:** `0`  **Options:** `0, 1080, 720, 480, 360`

`duration` - The time in seconds to call for. Default is 600s or 5min. **Default:** `600`  **Options:** `60, 120, 300, 600`

`parse_MSTeams_Logs` - Set to 1 to parse Teams logs after collecting them. **Default:** `1`  **Options:** `0, 1`

`parser_location` - Sets the path to the parser to use to decode Teams logs. **Default:** `..\ScenarioAssets\Teamsdecode\bin\UnifiedLogging` 

`collect_call_health` - Set to 1 to have the call health data collected. **Default:** `1`  **Options:** `0, 1`

`collect_MSTeams_Logs` - Set to 1 to collect MS Teams logs of the meeting after exiting the meeting. **Default:** `1`  **Options:** `0, 1`

`maintain_bots` - Set to 1 to have the test periodically check that all bots are present in the call and add bots if needed. **Default:** `1`  **Options:** `0, 1`

## teams2_5p_rpres

Microsoft Teams video call with 4 bot participants.
Local camera and mic are on, other 4 participants are bots sending video and audio.
One of the bots is sharing a video.


<u>Parameters:</u>

`meeting_time` - Set the time in minutes that the meeting can last up to. Default is teams:duration + 30 min. **Default:** `0` 

`access_key` - The access key for the Teams Bots Server. Contact HOBL Support to inquire for a key. **Default:** `-1` 

`number_of_bots` - Sets the number of bots to have in the meeting. **Default:** `4`  **Options:** `1, 2, 4, 8, 9`

`bots_send_video` - Set to 1 if bots should have their cameras on. Set to 0 for audio only calls. **Default:** `1`  **Options:** `0, 1`

`bots_send_audio` - Set to 1 to have bots send audio. Set to 0 to have bots be muted. **Default:** `1`  **Options:** `0, 1`

`bots_share_screen` - Set to 1 to have the primary bot share its screen in the meeting. **Default:** `1`  **Options:** `0, 1`

`bots_test_server` - For advanced use. Set to 1 to use the testing instance of the bots server. Not Recomended for general use. **Default:** `0`  **Options:** `0, 1`

`send_video` - Set to 1 to have the DUT turn on its camera. Set to 0 to have the DUT camera off. **Default:** `1`  **Options:** `0, 1`

`send_audio` - Set to 1 to have the DUT have its mic on. Set to 0 to have the DUT be muted. **Default:** `1`  **Options:** `0, 1`

`send_screen` - Set to 1 to have the DUT share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`presentation_video_path` - Sets the path to the video file to use as the presented screen when the DUT is screen sharing. **Default:** `\teams_resources\ppt.mp4` 

`show_desktop` - Set to 1 to have the DUT screen share their desktop when screen sharing. Set to 0 to share a video of a presentation instead. **Default:** `0`  **Options:** `0, 1`

`bots_force_subscribe_resolution` - Force the bots to subscribe to a specific video resolution **Default:** `0`  **Options:** `0, 1080, 720, 480, 360`

`duration` - The time in seconds to call for. Default is 600s or 5min. **Default:** `600`  **Options:** `60, 120, 300, 600`

`parse_MSTeams_Logs` - Set to 1 to parse Teams logs after collecting them. **Default:** `1`  **Options:** `0, 1`

`parser_location` - Sets the path to the parser to use to decode Teams logs. **Default:** `..\ScenarioAssets\Teamsdecode\bin\UnifiedLogging` 

`collect_call_health` - Set to 1 to have the call health data collected. **Default:** `1`  **Options:** `0, 1`

`collect_MSTeams_Logs` - Set to 1 to collect MS Teams logs of the meeting after exiting the meeting. **Default:** `1`  **Options:** `0, 1`

`maintain_bots` - Set to 1 to have the test periodically check that all bots are present in the call and add bots if needed. **Default:** `1`  **Options:** `0, 1`

## teams2_audio_desktop

Microsoft Teams audio call with 1 bot participant.
Local camera is off and mic is on, other participant is a bot sending audio.
Local user is sharing desktop.


<u>Parameters:</u>

`meeting_time` - Set the time in minutes that the meeting can last up to. Default is teams:duration + 30 min. **Default:** `0` 

`access_key` - The access key for the Teams Bots Server. Contact HOBL Support to inquire for a key. **Default:** `-1` 

`number_of_bots` - Sets the number of bots to have in the meeting. **Default:** `1`  **Options:** `1, 2, 4, 8, 9`

`bots_send_video` - Set to 1 if bots should have their cameras on. Set to 0 for audio only calls. **Default:** `0`  **Options:** `0, 1`

`bots_send_audio` - Set to 1 to have bots send audio. Set to 0 to have bots be muted. **Default:** `1`  **Options:** `0, 1`

`bots_share_screen` - Set to 1 to have the primary bot share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`bots_test_server` - For advanced use. Set to 1 to use the testing instance of the bots server. Not Recomended for general use. **Default:** `0`  **Options:** `0, 1`

`send_video` - Set to 1 to have the DUT turn on its camera. Set to 0 to have the DUT camera off. **Default:** `0`  **Options:** `0, 1`

`send_audio` - Set to 1 to have the DUT have its mic on. Set to 0 to have the DUT be muted. **Default:** `1`  **Options:** `0, 1`

`send_screen` - Set to 1 to have the DUT share its screen in the meeting. **Default:** `1`  **Options:** `0, 1`

`presentation_video_path` - Sets the path to the video file to use as the presented screen when the DUT is screen sharing. **Default:** `\teams_resources\ppt.mp4` 

`show_desktop` - Set to 1 to have the DUT screen share their desktop when screen sharing. Set to 0 to share a video of a presentation instead. **Default:** `1`  **Options:** `0, 1`

`bots_force_subscribe_resolution` - Force the bots to subscribe to a specific video resolution **Default:** `0`  **Options:** `0, 1080, 720, 480, 360`

`duration` - The time in seconds to call for. Default is 600s or 5min. **Default:** `300`  **Options:** `60, 120, 300, 600`

`parse_MSTeams_Logs` - Set to 1 to parse Teams logs after collecting them. **Default:** `1`  **Options:** `0, 1`

`parser_location` - Sets the path to the parser to use to decode Teams logs. **Default:** `..\ScenarioAssets\Teamsdecode\bin\UnifiedLogging` 

`collect_call_health` - Set to 1 to have the call health data collected. **Default:** `1`  **Options:** `0, 1`

`collect_MSTeams_Logs` - Set to 1 to collect MS Teams logs of the meeting after exiting the meeting. **Default:** `1`  **Options:** `0, 1`

`maintain_bots` - Set to 1 to have the test periodically check that all bots are present in the call and add bots if needed. **Default:** `1`  **Options:** `0, 1`

## teams2_idle

Teams is launched and then minimized to run in the background for the duration of the test.


<u>Parameters:</u>

`duration` -  **Default:** `300` 

`minimize_all` -  **Default:** `1` 

`minimize_teams_only` -  **Default:** `0` 

## upload

Uploads a file or folder to the DUT


<u>Parameters:</u>

`source_path` - Source path (file or folder) **Default:** `` 

`target_path` - Target folder (defaults to hobl_bin) **Default:** `` 

## youtube

Plays a YouTube video in a web browser in Default View mode.

Steps:

1. Navigate to Tears of Steel YouTube video URL: [youtu.be/41hv2tW5Lc4](https://youtu.be/41hv2tW5Lc4)
2. Change video quality to 1080p.
3. Let video play for specified duration and loops.
4. Close web browser.


<u>Parameters:</u>

`duration` - Total scenario duration **Default:** `600` 

`loop_duration` - YouTube video playback duration before looping (max 480s) **Default:** `300` 

`full_screen` - Full Screen mode **Default:** `0`  **Options:** `0, 1`

## brightness_study_report

Extract brightness value from a path containing a Brightness-XX folder.


<u>Parameters:</u>

`result_path` -  **Default:** `` 

`name` -  **Default:** `` 

`device_name` -  **Default:** `` 

`backlight_key` - Metric name for backlight power in brightness curve report. **Default:** `DisplayLight Power (W)` 

`analog_key` - Metric name for analog/panel power in brightness curve report. **Default:** `DisplayLogic Power (W)` 

## comm_check

Checks for valid communications between host and DUT.

Steps:

1. Ping DUT
2. SimpleRemote RPC call
3. SimpleRemote Async call
4. WinAppDriver launch and communication
5. Report results

## mac_cinebench

Scenario to run Cinebench on Mac, supporting singleCore and multiCore runs, collecting scores and battery rundown.


<u>Parameters:</u>

`duration` - Minimum run time in seconds **Default:** `60` 

`workload` - Workload type: single_core or multi_core **Default:** `multi_core`  **Options:** `single_core, multi_core`

## mac_teams2_10p_aud_dtop

Microsoft Teams audio call with 9 bot participants.
Local camera is off and mic is on, other 9 participants are bots sending audio.
Local user is sharing desktop.


<u>Parameters:</u>

`meeting_time` - Set the time in minutes that the meeting can last up to. Default is 120min. **Default:** `120` 

`access_key` - The access key for the Teams Bots Server. Contact HOBL Support to inquire for a key. **Default:** `-1` 

`number_of_bots` - Sets the number of bots to have in the meeting. **Default:** `8`  **Options:** `1, 2, 4, 8, 9`

`bots_send_video` - Set to 1 if bots should have their cameras on. Set to 0 for audio only calls. **Default:** `0`  **Options:** `0, 1`

`bots_send_audio` - Set to 1 to have bots send audio. Set to 0 to have bots be muted. **Default:** `1`  **Options:** `0, 1`

`bots_share_screen` - Set to 1 to have the primary bot share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`bots_test_server` - For advanced use. Set to 1 to use the testing instance of the bots server. Not Recomended for general use. **Default:** `0`  **Options:** `0, 1`

`duration` - Sets the time in seconds for the test to run. **Default:** `300`  **Options:** `60, 120, 240, 300, 600, 900`

`send_video` - Set to 1 to have the DUT turn on its camera. Set to 0 to have the DUT camera off. **Default:** `0`  **Options:** `0, 1`

`send_audio` - Set to 1 to have the DUT have its mic on. Set to 0 to have the DUT be muted. **Default:** `1`  **Options:** `0, 1`

`send_screen` - Set to 1 to have the DUT share its screen in the meeting. **Default:** `1`  **Options:** `0, 1`

`presentation_video_path` - Sets the path to the video file to use as the presented screen when the DUT is screen sharing. **Default:** `/teams_resources/ppt.mp4` 

`show_desktop` - Set to 1 to have the DUT screen share their desktop when screen sharing. Set to 0 to share a video of a presentation instead. **Default:** `1`  **Options:** `0, 1`

`bots_force_subscribe_resolution` - Force the bots to subscribe to a specific video resolution **Default:** `0`  **Options:** `0, 1080, 720, 480, 360`

`parse_MSTeams_Logs` - Set to 1 to parse Teams logs after collecting them. **Default:** `1`  **Options:** `0, 1`

`parser_location` - Sets the path to the parser to use to decode Teams logs. **Default:** `..\ScenarioAssets\Teamsdecode\bin\UnifiedLogging` 

`collect_call_health` - Set to 1 to have the call health data collected. **Default:** `1`  **Options:** `0, 1`

`collect_MSTeams_Logs` - Set to 1 to collect MS Teams logs of the meeting after exiting the meeting. **Default:** `1`  **Options:** `0, 1`

`maintain_bots` - Set to 1 to have the test periodically check that all bots are present in the call and add bots if needed. **Default:** `0`  **Options:** `0, 1`

## al_abl_active

The active part of the Windows ABL (all-day battery life) workload on an Aluminium (Android desktop) DUT: the Microsoft 365 apps are opened, the twelve web sites are browsed in Chrome, the apps are idled in turn, then each app's productivity task is run and the apps are closed.  Steps and timings follow the Windows abl_active scenario; see al_productivity and al_web for the Aluminium differences.


<u>Parameters:</u>

`web_workload` - Specific websites to run. **Default:** `amazonbsg amazonvacuum googleimagesapollo googleimageslondon googlesearchbelgium googlesearchsuperbowl instagram reddit theverge wikipedia youtubenasa youtubetos`  **Options:** `amazonbsg, amazonvacuum, googleimagesapollo, googleimageslondon, googlesearchbelgium, googlesearchsuperbowl, instagram, reddit, theverge, wikipedia, youtubenasa, youtubetos`

`idle_time` - Idle time between each app switch, - 3s **Default:** `111` 

## al_abl_standby

The standby part of the Windows ABL (all-day battery life) workload on an Aluminium (Android desktop) DUT: the Microsoft 365 apps are opened and the twelve web sites are loaded in Chrome, then the DUT sleeps for standby_duration with the screen off and is woken, and the apps are closed.  Steps and timings follow the Windows abl_standby scenario.

Power is measured only while the DUT is in standby.  Without a power measurement device, the average standby current and power are calculated from the battery charge counter and written to standby_power.csv, as in al_standby.


<u>Parameters:</u>

`web_workload` - Specific websites to run. **Default:** `amazonbsg amazonvacuum googleimagesapollo googleimageslondon googlesearchbelgium googlesearchsuperbowl instagram reddit theverge wikipedia youtubenasa youtubetos`  **Options:** `amazonbsg, amazonvacuum, googleimagesapollo, googleimageslondon, googlesearchbelgium, googlesearchsuperbowl, instagram, reddit, theverge, wikipedia, youtubenasa, youtubetos`

`standby_duration` - The time to be in standby, in seconds **Default:** `2348` 

## al_accounts_check

Reports which account settings are present in the device profile of an Aluminium (Android desktop) DUT, without showing their values.

Use it after filling in the profile, to see which account-dependent scenarios can run.  The scenario fails if a workload listed in "required" is missing a setting.


<u>Parameters:</u>

`required` - Space-separated workloads whose settings must be present: wifi, google, microsoft, netflix, teams **Default:** `` 

## al_agent_check

Checks that the agent on an Aluminium (Android desktop) DUT supports everything HOBL uses.  Run this after comm_check when setting up a new DUT or agent version.

Steps:

1. SimpleRemote compatible calls: version, command output, exit codes, and background jobs
2. File upload and download, including sub-folders and long file names
3. InputInject screen info and screenshot
4. InputInject input injection, using input that doesn't change the DUT state
5. Report results

## al_app_install_prep

Installs the Android apps used by HOBL scenarios from the Play Store on an Aluminium (Android desktop) DUT, for the active Android user.  Apps that are already installed are left unchanged.  The DUT must be signed in to a Google account.


<u>Parameters:</u>

`apps` - Space-separated apps to install: netflix, word, excel, powerpoint, outlook, onenote, teams, onedrive **Default:** `netflix word excel powerpoint outlook onenote teams onedrive` 

`install_timeout` - Seconds to wait for each app to download and install. **Default:** `900` 

## al_config_check

Run the Aluminium config-check script as a standalone prep and save Config.csv in the scenario results.
The normal scenario lifecycle already runs this check automatically for measured workloads.


<u>Parameters:</u>

`Study Type` -  **Default:** ``

`Comments` -  **Default:** ``

`Hardware Version` -  **Default:** ``

`Hardware Type` -  **Default:** ``

`Screen Size (in)` -  **Default:** ``

`Blade` -  **Default:** ``

`Accessories` -  **Default:** ``

`RTC Reserve (%)` -  **Default:** ``

`Raw Data Location` -  **Default:** ``

`Device Name` -  **Default:** ``

## al_discharge

Turns off the charger and waits for the battery to reach discharge:resume_threshold.
Aluminium version of the Windows discharge scenario; optionally plays local video with al_lvp.  Configure
global:charge_off_call or disconnect the charger manually; the scenario fails rather than waiting forever
if the DUT is still on AC/USB power above the requested threshold.


<u>Parameters:</u>

`resume_threshold` - Percent battery level to discharge to **Default:** `100`

`poll_period` - How often to check battery level (default 30s) **Default:** `30`

`run_scenario` - Run al_lvp in the background while discharging. **Default:** ``  **Options:** `lvp`

`leave_on_dc` - Leave on DC power after discharge scenario (default 1 - keep charger off) **Default:** `1`

`taper_workload` - Stop workload to cool down device. resume_threshold + taper_workload. (default 0) **Default:** `0`

## al_google_account_prep

The Google account names in "dumpsys account" output.


<u>Parameters:</u>

`required` - Space-separated workloads whose settings must be present: wifi, google, microsoft, netflix, teams **Default:** `` 

`signin_timeout` - Seconds to wait for each Google sign-in screen. **Default:** `120` 

## al_idle_apps

Idles with the Microsoft 365 apps open and the twelve web sites loaded in Chrome, switching to each app in turn, the Aluminium version of the Windows idle_apps scenario.


<u>Parameters:</u>

`web_workload` - Specific websites to run. **Default:** `amazonbsg amazonvacuum googleimagesapollo googleimageslondon googlesearchbelgium googlesearchsuperbowl instagram reddit theverge wikipedia youtubenasa youtubetos`  **Options:** `amazonbsg, amazonvacuum, googleimagesapollo, googleimageslondon, googlesearchbelgium, googlesearchsuperbowl, instagram, reddit, theverge, wikipedia, youtubenasa, youtubetos`

`idle_time` - Idle time between each app switch, - 3s **Default:** `111` 

## al_lvp

True if an audio player of uid is started in "dumpsys audio" output.


<u>Parameters:</u>

`video_file` - Name of the video file in the host's downloads folder and on the DUT. **Default:** `ToS-4k-1920.mp4` 

`video_url` - Where to download the video if it isn't in the downloads folder.  A .zip or .mov is converted to MP4 without re-encoding. **Default:** `http://ftp.nluug.nl/pub/graphics/blender/demo/movies/ToS/ToS-4k-1920.mov.zip` 

`video_file` - The file name of the video, copied to the Movies folder by al_lvp_prep. **Default:** `ToS-4k-1920.mp4` 

`duration` - Time to play the video in seconds **Default:** `300` 

`airplane_mode` - Not supported on Aluminium: airplane mode would disconnect the HOBL agent. **Default:** `0`  **Options:** `0`

## al_lvp_prep

ffmpeg from PATH, or the copy host_setup downloads into downloads\ffmpeg_*.


<u>Parameters:</u>

`video_file` - Name of the video file in the host's downloads folder and on the DUT. **Default:** `ToS-4k-1920.mp4` 

`video_url` - Where to download the video if it isn't in the downloads folder.  A .zip or .mov is converted to MP4 without re-encoding. **Default:** `http://ftp.nluug.nl/pub/graphics/blender/demo/movies/ToS/ToS-4k-1920.mov.zip` 

## al_manual

Aluminium platform alias for the host-driven Windows manual measurement scenario.


<u>Parameters:</u>

`duration` -  **Default:** ``

`delay` -  **Default:** ``

`start_prompt` -  **Default:** `1`

`setup_prompt` -  **Default:** `1`

`teardown_prompt` -  **Default:** `1`

## al_netflix

Watches a Netflix video in Chrome, the Aluminium version of the Windows netflix scenario: it signs in with netflix_username and netflix_password from the [netflix] section of the device profile if Chrome isn't signed in already, and plays the same title from the same position, full screen, for the specified duration.  Playback is verified with Android's media session at the start and end.  Unlike Windows, it doesn't sign out first:  Netflix may send a sign-in code to the account's email instead of asking for the password, which can't be automated.  If it does, sign in to Netflix once by hand in Chrome on the DUT.


<u>Parameters:</u>

`duration` - Seconds to play the video **Default:** `600` 

`page_load_time` - Seconds to wait for each Netflix page **Default:** `20` 

`netflix_username` - Netflix account, the same setting as the Windows netflix scenario **Default:** `` 

`netflix_password` - Netflix account password **Default:** `` 

## al_net_prep

Validate the DUT's Wi-Fi connection against dut_wifi_name.  Changing networks over wireless ADB would disconnect
the agent and can change dut_ip; join or switch networks over USB with dut_setup_aluminium.ps1 instead.


<u>Parameters:</u>

`net_prep_enabled` -  **Default:** `1`

`connection` -  **Default:** `Wi-Fi`

## al_notify

Send the plan-completion email from the Windows HOBL host without contacting the Aluminium DUT.


<u>Parameters:</u>

`plan_run_type` -  **Default:** ``

## al_office_prep

Signs in to the Microsoft 365 apps (Word, Excel, PowerPoint, Outlook, OneNote) on an Aluminium (Android desktop) DUT with msa_account and dut_password from the device profile, the equivalent of office_install activation on Windows.  The apps share the sign-in, so it is done once in Word.  Editing documents on Googlebook-sized screens needs a Microsoft 365 subscription on the account.


<u>Parameters:</u>

`required` - Space-separated workloads whose settings must be present: wifi, google, microsoft, netflix, teams **Default:** `` 

`timeout` - Seconds to wait for each sign-in step. **Default:** `180` 

## al_process_idle_tasks

Runs pending background maintenance on an Aluminium (Android desktop) DUT so it will not be running during tests.  Android compiles installed apps in a background job after OS and app updates, similar to Windows idle tasks.  To ensure consistent results, please run this scenario at least once per day on devices before starting tests.


<u>Parameters:</u>

`timeout` - Maximum time in seconds the automation will wait for tasks to complete **Default:** `1800` 

## al_productivity

Runs the Windows productivity workload in the Microsoft 365 apps on an Aluminium (Android desktop) DUT: Outlook, Excel, Word, PowerPoint and OneNote are opened with the Windows documents, each app's task is run, and the apps are closed, with the same steps, typed text, timings and phases as Windows.

Outlook attaches its picture and document instead of inserting them inline, and OneNote keeps the picture-insert time without inserting the picture, since OneNote for Android inserts pictures through its camera.  Windows image-matched clicks are taps on the apps' labelled controls.

## al_productivity_prep

Prepares Word, Excel, PowerPoint, OneNote and Outlook on an Aluminium (Android desktop) DUT for the productivity scenarios, the Aluminium version of the Windows productivity_prep scenario.

It copies the Windows productivity documents to the test user's Documents/abl_docs folder, gives the Office apps access to them, turns off the apps' notification prompts, and completes each app's first-run pages: Word, Excel and PowerPoint open their documents, OneNote opens a notebook page, and Outlook adds msa_account (offered by the Microsoft 365 sign-in, or signed in with dut_password).


<u>Parameters:</u>

`timeout` - Seconds to wait for each app's first-run pages. **Default:** `180` 

## al_read128kseq

Reads a 1 GB file sequentially in 128 KB blocks, bypassing the file cache, for the specified duration on an Aluminium (Android desktop) DUT.  The Aluminium version of read128kseq, using toybox dd with direct I/O instead of diskspd.  The throughput is written to disk_throughput.csv.


<u>Parameters:</u>

`block` - Block size in KB **Default:** `128` 

`duration` - Seconds **Default:** `300` 

## al_recharge

Turns on the device charger and waits until the battery reaches the recharge:resume_threshold level, then waits recharge:post_charge_delay seconds and turns off the charger.  Aluminium version of recharge.


<u>Parameters:</u>

`resume_threshold` -  **Default:** `100` 

`post_charge_delay` - How many seconds to wait after reaching the resume_threshold before disconnecting charger. **Default:** `0` 

`leave_on_ac` -  **Default:** `0`  **Options:** `0, 1`

`monitor_only` -  **Default:** `0`  **Options:** `0, 1`

`check_smart_charge` -  **Default:** `1`  **Options:** `0, 1`

## al_run_abl_if_preps_passed

Launch the Aluminium ABL rundown after its workload preps have completed.


<u>Parameters:</u>

`prep_list` - Aluminium ABL prep scenarios to check. **Default:** `al_abl_active al_web_prep al_productivity_prep al_lvp_prep`

`plans_to_launch` - Aluminium ABL rundown plan to launch. **Default:** `al_rundown_abl_lvp_web.ps1`

## al_run_plans_if_preps_passed

Launch Aluminium plans after the required preps have completed on the DUT.


<u>Parameters:</u>

`prep_list` - Aluminium prep scenarios to check before launching plans. **Default:** `al_app_install_prep al_google_account_prep al_web_prep al_lvp_prep`

`plans_to_launch` - Aluminium test plans to launch in order. **Default:** `al_hobl.ps1 al_hobl_smoke.ps1`

## al_speedometer

Runs the Speedometer 3.1 browser benchmark in Chrome, the Aluminium version of the Windows speedometer scenario.  The score is written to speedometer_score.csv with the same metric name as Windows.


<u>Parameters:</u>

`timeout` - Seconds to wait for the benchmark to finish **Default:** `900` 

## al_standby

Puts an Aluminium (Android desktop) DUT into standby with the screen off, the Aluminium version of the Windows standby scenario.  It uses the same cs_floor parameters: cs_duration, button_to_record_delay, connection, and the button callbacks.

Without a power measurement device, the average standby current and power are calculated from the battery charge counter, read just before standby and just after waking, and written to standby_power.csv.  Run it on battery; the charge counter resolution is 1 mAh, so longer durations are more accurate.


<u>Parameters:</u>

`cs_duration` -  **Default:** `1200` 

`button_to_record_delay` -  **Default:** `900` 

`button_sleep_callback` -  **Default:** `` 

`button_wake_callback` -  **Default:** `` 

`connection` - Connected or Disconnected from the network during standby **Default:** `Connected`  **Options:** `Disconnected, Connected`

`wake_timeout` - Seconds to keep trying to wake the DUT after standby. **Default:** `300` 

## al_teams

A Teams call with bots on an Aluminium (Android desktop) DUT, the Aluminium version of the Windows teams scenario used by the teams2_* scenarios.  The bots meeting is created, maintained and removed on the host with the Windows Teams library code and the teams parameters (access_key, number_of_bots, duration, bots_send_video, ...); the DUT joins it in the Teams app with its camera and microphone set by send_video and send_audio.

The Teams account (teams_install:teams_msa_account) is in one call at a time, so don't run Teams scenarios on two DUTs with the same account at once.  Sharing the DUT's screen (send_screen) and Teams call health and log collection are not available on Aluminium.


<u>Parameters:</u>

`meeting_time` - Set the time in minutes that the meeting can last up to. Default is 120min. **Default:** `120` 

`access_key` - The access key for the Teams Bots Server. Contact HOBL Support to inquire for a key. **Default:** `-1` 

`number_of_bots` - Sets the number of bots to have in the meeting. **Default:** `1`  **Options:** `1, 2, 4, 8, 9`

`bots_send_video` - Set to 1 if bots should have their cameras on. Set to 0 for audio only calls. **Default:** `1`  **Options:** `0, 1`

`bots_send_audio` - Set to 1 to have bots send audio. Set to 0 to have bots be muted. **Default:** `1`  **Options:** `0, 1`

`bots_share_screen` - Set to 1 to have the primary bot share its screen in the meeting. **Default:** `0`  **Options:** `0, 1`

`bots_test_server` - For advanced use. Set to 1 to use the testing instance of the bots server. Not Recomended for general use. **Default:** `0`  **Options:** `0, 1`

`send_video` - Set to 1 to have the DUT turn on its camera. Set to 0 to have the DUT camera off. **Default:** `1`  **Options:** `0, 1`

`send_audio` - Set to 1 to have the DUT have its mic on. Set to 0 to have the DUT be muted. **Default:** `1`  **Options:** `0, 1`

`send_screen` - Screen sharing from the DUT is not supported on Aluminium. Must be 0. **Default:** `0`  **Options:** `0`

`bots_force_subscribe_resolution` - Force the bots to subscribe to a specific video resolution **Default:** `0`  **Options:** `0, 1080, 720, 480, 360`

`duration` - The time in seconds to call for. Default is 600s or 5min. **Default:** `600`  **Options:** `60, 120, 300, 600`

`maintain_bots` - Set to 1 to have the test periodically check that all bots are present in the call and add bots if needed. **Default:** `1`  **Options:** `0, 1`

## al_teams2_idle

Teams is launched and then minimized to run in the background for the duration of the test, the Aluminium version of the Windows teams2_idle scenario.  As on Windows, Teams waits 5.5 minutes to reach its idle state before the measurement starts, and is left running afterwards.

minimize_all=1 shows the home screen, the equivalent of minimizing all windows on Windows; with 0, Teams stays in front.  The Windows minimize_teams_only option isn't available, since the Android desktop has no shortcut to minimize one window.


<u>Parameters:</u>

`duration` - Seconds to measure Teams idling in the background. **Default:** `300` 

`minimize_all` - 1 to show the home screen, minimizing all windows; 0 to leave Teams in front. **Default:** `1`  **Options:** `0, 1`

`idle_wait` - Seconds to wait for Teams to reach its idle state before measuring. **Default:** `330` 

## al_teams_prep

Signs in to the Teams app on an Aluminium (Android desktop) DUT, the Aluminium version of the Windows teams_install scenario.  It uses teams_install:teams_msa_account and teams_msa_password, or msa_account and dut_password if they aren't set, as on Windows.  The account must not need extra verification (two-step verification or the Authenticator app) to sign in.

It also allows Teams to use the camera, microphone, and phone (Teams can't join a meeting without the phone permission, since it places calls through Android's telecom service), and turns off its notifications and its location, nearby devices, and contacts requests.


<u>Parameters:</u>

`timeout` - Seconds to wait for the Teams sign-in. **Default:** `300` 

## al_test_fail

Intentionally fail the scenario to validate failure reporting and plan continuation.

## al_timer

Delays for the specified duration on an Aluminium (Android desktop) DUT.  Useful for checking that the HOBL host and the Aluminium agent are set up correctly.


<u>Parameters:</u>

`duration` - Seconds to delay. **Default:** `1` 

## al_version_report

Write Aluminium OS, build, architecture, agent, browser, and installed workload versions to the results.

## al_wait_for_dut

Waits until the Aluminium agent on the DUT responds.

## al_web

Runs the twelve default Windows web_replay sites in Chrome with the Windows web scenario's tab order, page timings, scrolling and searches.  Set web_workload to run a subset of the sites, the same as Windows.

Scrolling uses Page Down and Page Up, which reach Chrome whatever its window size.  Steps Windows finds by image match (the Amazon search bar, the first Instagram reel and the YouTube quality menu) keep the same timing without the interaction.  YouTube's player pauses the recorded videos in Chrome on Aluminium, so the scenario only checks that archived video segments were delivered; use al_youtube for representative video playback.


<u>Parameters:</u>

`web_workload` - Specific websites to run. **Default:** `amazonbsg amazonvacuum googleimagesapollo googleimageslondon googlesearchbelgium googlesearchsuperbowl instagram reddit theverge wikipedia youtubenasa youtubetos`  **Options:** `amazonbsg, amazonvacuum, googleimagesapollo, googleimageslondon, googlesearchbelgium, googlesearchsuperbowl, instagram, reddit, theverge, wikipedia, youtubenasa, youtubetos`

`loops` - Number of browser loops **Default:** `1` 

`youtube_duration` - Expected archived YouTube playback duration checked by web_check **Default:** `90` 

## al_webxprt

Runs the WebXPRT 4 browser benchmark in Chrome with its automation URL, the Aluminium version of the Windows webxprt scenario.  The overall score is written to webxprt_score.csv with the same metric name as Windows.


<u>Parameters:</u>

`timeout` - Seconds to wait for the benchmark to finish **Default:** `1800` 

## al_web_prep

Prepares Chrome for Aluminium web workloads.  It dismisses Chrome's first-run, sign-in, sync,
notification, and default browser prompts without accepting them, then clears cached files only,
preserving cookies, browsing history, passwords, and the signed-in test account.

## al_write128kseq

Writes a 1 GB file sequentially in 128 KB blocks, bypassing the file cache, for the specified duration on an Aluminium (Android desktop) DUT.  The Aluminium version of write128kseq, using toybox dd with direct I/O instead of diskspd.  The throughput is written to disk_throughput.csv.


<u>Parameters:</u>

`block` - Block size in KB **Default:** `128` 

`duration` - Seconds **Default:** `300` 

`block` - Block size in KB **Default:** `128` 

`duration` - Seconds **Default:** `300` 

## al_wr_cookies_remove

Removes cookies from the web_replay archive file named by global:web_replay_recording on the Host, for archives recorded from an Aluminium (Android desktop) DUT.

## al_wr_idle_timeout

Adds the server idle timeouts in the Host's web_replay recordings\idle_timeouts.json to the archive named by global:web_replay_recording.

On Windows, idle_timeouts.json comes from a Microsoft Edge netlog capture.  Chrome on Aluminium (Android desktop) can't be started with a netlog, so the file must come from a Windows recording of the same sites.

## al_wr_record_start

Starts a web_replay recording server on the Host and points the Aluminium (Android desktop) DUT's global proxy at it.

Set global:web_replay_recording to the archive to record; use a new name so an existing archive isn't overwritten.  Run the workload with global:web_replay_action=bulk_record, then run al_wr_record_stop.

## al_wr_record_stop

Stops the web_replay recording server started by al_wr_record_start and clears the Aluminium (Android desktop) DUT's global proxy.

## al_wr_replay_start

Starts a web_replay replay server on the Host for global:web_replay_recording and points the Aluminium (Android desktop) DUT's global proxy at it.

Run workloads with global:web_replay_action=bulk_replay while it is running, then run al_wr_replay_stop.

## al_wr_replay_stop

Stops the web_replay replay server started by al_wr_replay_start and clears the Aluminium (Android desktop) DUT's global proxy.

## al_youtube

Plays the Tears of Steel YouTube video in Chrome, the Aluminium version of the Windows youtube scenario.

It uses the same parameters as Windows: duration, loop_duration (the video restarts after this many seconds), and full_screen.  Playback is verified on the DUT: after each loop, Android's media session must report that Chrome is playing and that the video advanced by the loop duration.

By default the live site is used, because YouTube's player pauses the web_replay recording in Chrome on Aluminium.  Set web_replay=1 to use the recording, the same as Windows, once that is resolved.


<u>Parameters:</u>

`duration` - Total scenario duration **Default:** `600` 

`loop_duration` - YouTube video playback duration before looping (max 480s) **Default:** `300` 

`full_screen` - Full Screen mode **Default:** `0`  **Options:** `0, 1`

`page_load_time` - Seconds to wait for the video page **Default:** `15` 

`web_replay` - Play the web_replay recording (1) or the live site (0).  The recording does not currently play in Chrome on Aluminium. **Default:** `0`  **Options:** `0, 1`
