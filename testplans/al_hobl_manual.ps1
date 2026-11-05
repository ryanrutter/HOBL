if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s charge_off global:run_type=Misc global:post_run_delay=60
.\hobl.cmd -p $ARGS[0] -s al_manual global:run_type=Power global:post_run_delay=0 manual:duration=180 global:module_name="Enter_Name_Use_Underscore" global:iterations=1 global:attempts=1 global:tools="+power_light"
.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc global:post_run_delay=0
