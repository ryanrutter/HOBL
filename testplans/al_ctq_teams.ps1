if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}

.\hobl.cmd -p $ARGS[0] -s al_config_check

# NEW Teams Power AC 
.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc global:post_run_delay=300
.\hobl.cmd -p $ARGS[0] -s idle_desktop global:iterations=5 global:run_type=Power global:tools="+power_light" idle_desktop:duration=1200 global:module_name=idle_desktop_t21_AC
.\hobl.cmd -p $ARGS[0] -s al_teams2_3x3_video global:iterations=5 global:run_type=Power global:tools="+power_light" global:module_name=t21_3x3_V_AC
# .\hobl.cmd -p $ARGS[0] -s al_teams2_1on1_video global:iterations=5 global:run_type=Power global:tools="+power_light" global:module_name=t21_1x1_V_AC

.\hobl.cmd -p $ARGS[0] -s al_teams2_1on1_audio global:iterations=5 global:run_type=Power global:tools="+power_light" global:module_name=t21_1x1_A_AC

# NEW Teams ETL AC
.\hobl.cmd -p $ARGS[0] -s idle_desktop global:run_type=ETL global:tools="+power_heavy" idle_desktop:duration=1200 global:module_name=idle_desktop_t21_AC
.\hobl.cmd -p $ARGS[0] -s al_teams2_3x3_video global:run_type=ETL global:tools="+power_heavy" global:module_name=t21_3x3_V_AC
# .\hobl.cmd -p $ARGS[0] -s al_teams2_1on1_video global:run_type=ETL global:tools="+power_heavy" global:module_name=t21_1x1_V_AC
.\hobl.cmd -p $ARGS[0] -s al_teams2_1on1_audio global:run_type=ETL global:tools="+power_heavy" global:module_name=t21_1x1_A_AC

# NEW Teams Power DC 
.\hobl.cmd -p $ARGS[0] -s charge_off global:run_type=Misc global:post_run_delay=300
.\hobl.cmd -p $ARGS[0] -s idle_desktop global:iterations=5 global:run_type=Power global:tools="+power_light" idle_desktop:duration=1200 global:module_name=idle_desktop_t21_DC
.\hobl.cmd -p $ARGS[0] -s al_teams2_3x3_video global:iterations=5 global:run_type=Power global:tools="+power_light" global:module_name=t21_3x3_V_DC
# .\hobl.cmd -p $ARGS[0] -s al_teams2_1on1_video global:iterations=5 global:run_type=Power global:tools="+power_light" global:module_name=t21_1x1_V_DC
.\hobl.cmd -p $ARGS[0] -s al_teams2_1on1_audio global:iterations=5 global:run_type=Power global:tools="+power_light" global:module_name=t21_1x1_A_DC

# NEW Teams ETL DC
.\hobl.cmd -p $ARGS[0] -s idle_desktop global:run_type=ETL global:tools="+power_heavy" idle_desktop:duration=1200 global:module_name=idle_desktop_t21_DC
.\hobl.cmd -p $ARGS[0] -s al_teams2_3x3_video global:run_type=ETL global:tools="+power_heavy" global:module_name=t21_3x3_V_DC
# .\hobl.cmd -p $ARGS[0] -s al_teams2_1on1_video global:run_type=ETL global:tools="+power_heavy" global:module_name=t21_1x1_V_DC
.\hobl.cmd -p $ARGS[0] -s al_teams2_1on1_audio global:run_type=ETL global:tools="+power_heavy" global:module_name=t21_1x1_A_DC

.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s study_report global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s al_version_report global:run_type=Prep global:post_run_delay=0
