if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
# .\hobl.cmd -p $ARGS[0] -s al_process_idle_tasks global:run_type=Power
# .\hobl.cmd -p $ARGS[0] -s al_config_check
# .\hobl.cmd -p $ARGS[0] -s charge_off global:run_type=Misc

.\hobl.cmd -p $ARGS[0] -s idle_desktop global:run_type=Power global:tools="+power_light" duration=5
.\hobl.cmd -p $ARGS[0] -s al_standby global:run_type=Power global:tools="+powercfg power_light" cs_floor:button_to_record_delay=5 cs_floor:cs_duration=10
.\hobl.cmd -p $ARGS[0] -s al_abl_active global:run_type=Power global:tools="+power_light" idle_time=5
.\hobl.cmd -p $ARGS[0] -s al_abl_standby global:run_type=Power global:tools="+powercfg power_light" standby_duration=5
.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=Power global:tools="+power_light" duration=5
.\hobl.cmd -p $ARGS[0] -s al_productivity global:run_type=Power global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_idle_apps global:run_type=Power global:tools="+power_light" idle_time=5
.\hobl.cmd -p $ARGS[0] -s al_netflix global:run_type=Power global:tools="+power_light" duration=5
.\hobl.cmd -p $ARGS[0] -s al_youtube global:run_type=Power global:tools="+power_light" duration=5
.\hobl.cmd -p $ARGS[0] -s al_lvp global:run_type=Power global:tools="+power_light" duration=5
.\hobl.cmd -p $ARGS[0] -s al_teams2_3x3_video global:run_type=Power global:tools="+power_light" duration=5
.\hobl.cmd -p $ARGS[0] -s al_teams2_1on1_audio global:run_type=Power global:tools="+power_light" duration=5
.\hobl.cmd -p $ARGS[0] -s al_teams2_idle global:run_type=Power global:tools="+power_light" duration=5

.\hobl.cmd -p $ARGS[0] -s idle_desktop global:run_type=ETL global:tools="+power_heavy" duration=120

# .\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s study_report global:run_type=Misc
