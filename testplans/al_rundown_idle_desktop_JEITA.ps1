if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}

.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type="Misc"
.\hobl.cmd -p $ARGS[0] -s al_wait_for_dut global:run_type="Misc"
.\hobl.cmd -p $ARGS[0] -s reboot global:run_type="Misc"
.\hobl.cmd -p $ARGS[0] -s al_process_idle_tasks global:post_run_delay="900" global:run_type="Misc"
# .\hobl.cmd -p $ARGS[0] -s al_config_check global:run_type="Misc"
.\hobl.cmd -p $ARGS[0] -s al_recharge global:run_type="Misc"
.\hobl.cmd -p $ARGS[0] -s al_idle_desktop_jeita global:run_type="Power" al_idle_desktop_jeita:duration="1000000" global:rundown_mode=1 global:stop_soc=0 global:crit_batt_level=3 display_brightness:brightness=200nits audio_volume:volume=1 global:tools="+power_light auto_charge"
.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type="Misc"
.\hobl.cmd -p $ARGS[0] -s study_report global:run_type="Misc"
