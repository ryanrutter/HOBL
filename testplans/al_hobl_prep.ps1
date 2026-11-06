if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s charge_on post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_net_prep attempts=2 net_prep:connection=Wi-Fi post_run_delay=0

.\hobl.cmd -p $ARGS[0] -s al_teams_prep post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s prep post_run_delay=0 prep:scenarios_to_prep="al_abl_active al_standby al_lvp al_teams"

.\hobl.cmd -p $ARGS[0] -s al_net_prep attempts=2 post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_version_report post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_notify post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_run_plans_if_preps_passed post_run_delay=0
