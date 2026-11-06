if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}

.\hobl.cmd -p $ARGS[0] -s al_app_install_prep al_app_install_prep:apps="edge edgebeta edgecanary" global:run_type=Prep global:post_run_delay=0 global:attempts=2
.\hobl.cmd -p $ARGS[0] -s al_web_prep global:run_type=Prep global:post_run_delay=0 global:attempts=2 global:browser=Edge
.\hobl.cmd -p $ARGS[0] -s al_web_prep global:run_type=Prep global:post_run_delay=0 global:attempts=2 global:browser=EdgeBeta
.\hobl.cmd -p $ARGS[0] -s al_web_prep global:run_type=Prep global:post_run_delay=0 global:attempts=2 global:browser=EdgeCanary

# .\hobl.cmd -p $ARGS[0] -s al_config_check global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_version_report global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s charge_off global:run_type=Misc global:post_run_delay=900

.\hobl.cmd -p $ARGS[0] -s idle_desktop global:iterations=3 idle_desktop:duration=1200 global:run_type=Power global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=Power global:browser=Edge global:module_name=al_web_edge global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=Power global:browser=EdgeBeta global:module_name=al_web_edgebeta global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=Power global:browser=EdgeCanary global:module_name=al_web_edgecanary global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=Power global:browser=Edge global:module_name=al_web_edge global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=Power global:browser=EdgeBeta global:module_name=al_web_edgebeta global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=Power global:browser=EdgeCanary global:module_name=al_web_edgecanary global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=Power global:browser=Edge global:module_name=al_web_edge global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=Power global:browser=EdgeBeta global:module_name=al_web_edgebeta global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=Power global:browser=EdgeCanary global:module_name=al_web_edgecanary global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=Power global:browser=Edge global:module_name=al_web_edge global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=Power global:browser=EdgeBeta global:module_name=al_web_edgebeta global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=Power global:browser=EdgeCanary global:module_name=al_web_edgecanary global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=Power global:browser=Edge global:module_name=al_web_edge global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=Power global:browser=EdgeBeta global:module_name=al_web_edgebeta global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=Power global:browser=EdgeCanary global:module_name=al_web_edgecanary global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=ETL global:browser=Edge global:module_name=al_web_edge global:tools="+power_heavy"
.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=ETL global:browser=EdgeBeta global:module_name=al_web_edgebeta global:tools="+power_heavy"
.\hobl.cmd -p $ARGS[0] -s al_web global:run_type=ETL global:browser=EdgeCanary global:module_name=al_web_edgecanary global:tools="+power_heavy"

.\hobl.cmd -p $ARGS[0] -s idle_desktop global:iterations=3 idle_desktop:duration=1200 global:run_type=ETL global:tools="+power_heavy"

.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s study_report global:run_type=Misc global:post_run_delay=0

.\hobl.cmd -p $ARGS[0] -s al_notify global:run_type=Misc global:post_run_delay=0
