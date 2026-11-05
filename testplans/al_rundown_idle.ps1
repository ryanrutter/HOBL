if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s charge_on
.\hobl.cmd -p $ARGS[0] -s al_wait_for_dut
.\hobl.cmd -p $ARGS[0] -s al_process_idle_tasks al_process_idle_tasks:timeout=7200
.\hobl.cmd -p $ARGS[0] -s al_recharge post_charge_delay=1800
.\hobl.cmd -p $ARGS[0] -s idle_desktop idle_desktop:duration=172800 global:rundown_mode=1 global:stop_soc=0 global:crit_batt_level=3 screenshot:pause=3600 global:tools="+power_light auto_charge screenshot display"
.\hobl.cmd -p $ARGS[0] -s al_wait_for_dut
.\hobl.cmd -p $ARGS[0] -s charge_on
.\hobl.cmd -p $ARGS[0] -s study_report
