if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s al_process_idle_tasks global:run_type=Power global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_config_check
.\hobl.cmd -p $ARGS[0] -s charge_off global:run_type=Misc global:post_run_delay=900

.\hobl.cmd -p $ARGS[0] -s idle_desktop global:tools="+power_heavy" global:run_type=ETL pre_run_delay=60
.\hobl.cmd -p $ARGS[0] -s al_standby global:tools="+power_heavy powercfg" global:run_type=ETL
.\hobl.cmd -p $ARGS[0] -s al_abl_active global:tools="+power_heavy" global:run_type=ETL
.\hobl.cmd -p $ARGS[0] -s al_abl_standby global:tools="+power_heavy powercfg" global:run_type=ETL
.\hobl.cmd -p $ARGS[0] -s al_web global:tools="+power_heavy" global:run_type=ETL
.\hobl.cmd -p $ARGS[0] -s al_idle_apps global:tools="+power_heavy" global:run_type=ETL
.\hobl.cmd -p $ARGS[0] -s al_productivity global:tools="+power_heavy" global:run_type=ETL
.\hobl.cmd -p $ARGS[0] -s al_netflix global:tools="+power_heavy" global:run_type=ETL
.\hobl.cmd -p $ARGS[0] -s al_youtube global:tools="+power_heavy" global:run_type=ETL
.\hobl.cmd -p $ARGS[0] -s al_lvp global:tools="+power_heavy" global:run_type=ETL
.\hobl.cmd -p $ARGS[0] -s al_teams2_3x3_video global:tools="+power_heavy" global:run_type=ETL
.\hobl.cmd -p $ARGS[0] -s al_teams2_1on1_audio global:tools="+power_heavy" global:run_type=ETL
.\hobl.cmd -p $ARGS[0] -s al_teams2_idle global:tools="+power_heavy" global:run_type=ETL

.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s study_report global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s al_notify global:run_type=Misc notify:plan_run_type=etl
