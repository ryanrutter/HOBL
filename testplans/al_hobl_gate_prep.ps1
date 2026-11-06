if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s al_teams_prep global:attempts=2 global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_google_account_prep global:attempts=2 global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_app_install_prep global:attempts=3 global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_web_prep global:attempts=2 global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_office_prep global:attempts=2 global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s reboot global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_productivity_prep global:attempts=2 global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_config_check global:attempts=2 global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_version_report global:attempts=2 global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_run_plans_if_preps_passed run_plans_if_preps_passed:plans_to_launch=al_hobl_gate.json run_plans_if_preps_passed:prep_list="al_abl_active al_teams" global:run_type=Misc
