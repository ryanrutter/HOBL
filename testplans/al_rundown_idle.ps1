if ($ARGS[0] -eq $null) {
    Write-Host " ERROR - Params .ini not supplied.  Please supply a params .ini parameter." -ForegroundColor Red
    exit 1
}

function Invoke-HoblStep {
    param([string[]]$Arguments)

    & .\hobl.cmd @Arguments
    if ($LASTEXITCODE -ne 0) {
        $exitCode = $LASTEXITCODE
        Write-Host " ERROR - HOBL step failed with exit code $exitCode.  See the scenario log for details." -ForegroundColor Red
        exit $exitCode
    }
}

$profile = $ARGS[0]

Invoke-HoblStep @("-p", $profile, "-s", "charge_on")
Invoke-HoblStep @("-p", $profile, "-s", "al_wait_for_dut")
Invoke-HoblStep @("-p", $profile, "-s", "al_process_idle_tasks", "al_process_idle_tasks:timeout=7200")
Invoke-HoblStep @("-p", $profile, "-s", "al_recharge", "post_charge_delay=1800")
Invoke-HoblStep @("-p", $profile, "-s", "idle_desktop", "idle_desktop:duration=172800", "global:rundown_mode=1", "global:stop_soc=0", "global:crit_batt_level=3", "screenshot:pause=3600", "global:tools=+screenshot display")
Invoke-HoblStep @("-p", $profile, "-s", "al_wait_for_dut")
Invoke-HoblStep @("-p", $profile, "-s", "charge_on")
Invoke-HoblStep @("-p", $profile, "-s", "study_report")
