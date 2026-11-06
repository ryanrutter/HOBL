if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}

.\hobl.cmd -p $ARGS[0] -s al_netflix  global:browser=Chrome global:module_name=al_netflix_chrome  global:training_mode=1
.\hobl.cmd -p $ARGS[0] -s al_netflix  global:browser=Edge   global:module_name=al_netflix_edge    global:training_mode=1
.\hobl.cmd -p $ARGS[0] -s al_youtube  global:browser=Chrome global:module_name=al_youtube_chrome  global:training_mode=1
.\hobl.cmd -p $ARGS[0] -s al_youtube  global:browser=Edge   global:module_name=al_youtube_edge    global:training_mode=1

.\hobl.cmd -p $ARGS[0] -s al_process_idle_tasks global:post_run_delay=600
.\hobl.cmd -p $ARGS[0] -s charge_off
# .\hobl.cmd -p $ARGS[0] -s al_config_check

.\hobl.cmd -p $ARGS[0] -s al_netflix  global:browser=Chrome global:module_name=al_netflix_chrome  global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_netflix  global:browser=Edge   global:module_name=al_netflix_edge    global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_netflix  global:browser=Chrome global:module_name=al_netflix_chrome  global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_netflix  global:browser=Edge   global:module_name=al_netflix_edge    global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_netflix  global:browser=Chrome global:module_name=al_netflix_chrome  global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_netflix  global:browser=Edge   global:module_name=al_netflix_edge    global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s al_youtube  global:browser=Chrome global:module_name=al_youtube_chrome  global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_youtube  global:browser=Edge   global:module_name=al_youtube_edge    global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_youtube  global:browser=Chrome global:module_name=al_youtube_chrome  global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_youtube  global:browser=Edge   global:module_name=al_youtube_edge    global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_youtube  global:browser=Chrome global:module_name=al_youtube_chrome  global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s al_youtube  global:browser=Edge   global:module_name=al_youtube_edge    global:tools="+power_light"

.\hobl.cmd -p $ARGS[0] -s al_netflix  global:browser=Edge   global:module_name=al_netflix_edge    global:run_type=Trace global:tools="+perfetto_trace"
.\hobl.cmd -p $ARGS[0] -s al_youtube  global:browser=Edge   global:module_name=al_youtube_edge    global:run_type=Trace global:tools="+perfetto_trace"

.\hobl.cmd -p $ARGS[0] -s charge_on
.\hobl.cmd -p $ARGS[0] -s study_report
