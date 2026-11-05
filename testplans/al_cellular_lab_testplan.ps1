if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s al_manual al_manual:duration=5 global:module_name=daq_check global:run_type=Power al_manual:delay=0 al_manual:start_prompt=0 al_manual:setup_prompt=0 al_manual:teardown_prompt=0 global:config_check=0
