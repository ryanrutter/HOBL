if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s al_timer global:run_type=Power
.\hobl.cmd -p $ARGS[0] -s al_timer global:run_type=Power
.\hobl.cmd -p $ARGS[0] -s al_test_fail global:run_type=Power
.\hobl.cmd -p $ARGS[0] -s al_timer global:run_type=Power
.\hobl.cmd -p $ARGS[0] -s al_notify global:run_type=Misc
