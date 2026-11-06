if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}

.\hobl.cmd -p $ARGS[0] -s al_wr_record_start  global:run_type=Misc global:web_replay_recording=al_web_recording
.\hobl.cmd -p $ARGS[0] -s al_web              global:training_mode=1 global:web_replay_action=bulk_record
.\hobl.cmd -p $ARGS[0] -s al_wr_record_stop   global:run_type=Misc
