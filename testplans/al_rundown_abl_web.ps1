if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s al_wait_for_dut global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s al_config_check global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s al_web global:tools="+power_light screen_record" global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s al_recharge global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s al_web al_web:loops=100 global:rundown_mode=1 global:stop_soc=0 global:crit_batt_level=3 display_brightness:brightness=150nits screenshot:pause=3600 global:tools="+power_light auto_charge screenshot" global:run_type=Power
.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s study_report global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s al_wait_for_dut global:run_type=Misc
