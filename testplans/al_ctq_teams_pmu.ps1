if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}

# .\hobl.cmd -p $ARGS[0] -s al_config_check

# Windows records PMU counters with etl_trace:providers=pmu.wprp; Aluminium records a Perfetto CPU scheduling,
# frequency and idle trace with perfetto_trace.
#MS Teams AC On power runs
# .\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc global:post_run_delay=300
# .\hobl.cmd -p $ARGS[0] -s al_teams2_3x3_video global:iterations=1 global:run_type=PMU global:module_name=t21_3x3_V_AC global:tools="+perfetto_trace"
# .\hobl.cmd -p $ARGS[0] -s al_teams2_1on1_video global:iterations=1 global:run_type=PMU global:module_name=t21_1x1_V_AC global:tools="+perfetto_trace"
# .\hobl.cmd -p $ARGS[0] -s al_teams2_1on1_audio global:iterations=1 global:run_type=PMU global:module_name=t21_1x1_A_AC global:tools="+perfetto_trace"

#MS Teams DC power runs
.\hobl.cmd -p $ARGS[0] -s charge_off global:run_type=Misc global:post_run_delay=300
.\hobl.cmd -p $ARGS[0] -s al_teams2_3x3_video global:iterations=1 global:run_type=PMU global:module_name=t21_3x3_V_DC global:tools="+perfetto_trace"
# .\hobl.cmd -p $ARGS[0] -s al_teams2_1on1_video global:iterations=1 global:run_type=PMU global:module_name=t21_1x1_V_DC global:tools="+perfetto_trace"
# .\hobl.cmd -p $ARGS[0] -s al_teams2_1on1_audio global:iterations=1 global:run_type=PMU global:module_name=t21_1x1_A_DC global:tools="+perfetto_trace"

.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s study_report global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s al_version_report global:run_type=Prep global:post_run_delay=0
