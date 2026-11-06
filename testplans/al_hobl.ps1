if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s al_process_idle_tasks global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_config_check
.\hobl.cmd -p $ARGS[0] -s charge_off global:run_type=Misc global:post_run_delay=900

.\hobl.cmd -p $ARGS[0] -s idle_desktop global:iterations=3 global:attempts=2 global:run_type=Power global:tools="+power_light" pre_run_delay=60
.\hobl.cmd -p $ARGS[0] -s al_standby global:iterations=2 global:attempts=2 global:run_type=Power global:tools="+powercfg power_light"
.\hobl.cmd -p $ARGS[0] -s al_abl_active global:iterations=3 global:attempts=2 global:run_type=Power global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_web global:iterations=3  global:run_type=Power global:tools="+power_light"
# .\hobl.cmd -p $ARGS[0] -s al_idle_apps global:iterations=3 global:run_type=Power global:tools="+power_light"
# .\hobl.cmd -p $ARGS[0] -s al_productivity global:iterations=3 global:run_type=Power global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_abl_standby global:iterations=3 global:attempts=2 global:run_type=Power global:tools="+powercfg power_light"
.\hobl.cmd -p $ARGS[0] -s al_netflix global:iterations=3 global:attempts=2 global:run_type=Power global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_youtube global:iterations=3 global:attempts=2 global:run_type=Power global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_lvp global:iterations=3 global:attempts=2 global:run_type=Power global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_teams2_3x3_video global:iterations=3 global:attempts=2 global:run_type=Power global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_teams2_1on1_audio global:iterations=3 global:attempts=2 global:run_type=Power global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_teams2_1on1_video global:iterations=3 global:attempts=2 global:run_type=Power global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_teams2_idle global:iterations=3 global:attempts=2 global:run_type=Power global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s idle_desktop global:iterations=1 global:run_type=Power global:tools="+power_light" pre_run_delay=60
.\hobl.cmd -p $ARGS[0] -s al_standby global:iterations=1 global:run_type=Power global:tools="+powercfg power_light"
.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s study_report global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s al_version_report global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_notify global:run_type=Misc
