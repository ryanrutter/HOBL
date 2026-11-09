if ($ARGS[0] -eq $null) {return("Params .ini not supplied, please supply a params .ini parameter.")}
.\hobl.cmd -p $ARGS[0] -s charge_on global:run_type=Misc
.\hobl.cmd -p $ARGS[0] -s al_net_prep net_prep:connection=Wi-Fi global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_version_report global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_config_check global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_app_install_prep global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s reboot global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_lvp_jeita_prep global:run_type=Prep global:post_run_delay=0
.\hobl.cmd -p $ARGS[0] -s al_wallpaper_prep global:run_type=Prep global:post_run_delay=0 al_wallpaper_prep:wallpaper=JB3_0-IMAGE.jpg
.\hobl.cmd -p $ARGS[0] -s al_config_check global:attempts=2 global:post_run_delay=0
