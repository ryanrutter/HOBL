#!/system/bin/sh
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

# Aluminium (Android desktop) counterpart of config_check_linux.sh.  Produces the same CSV keys.
# Written for Android's POSIX shell (mksh), which has no bash features such as associative arrays.

export LC_ALL=C

PreRun=false
PostRun=false
LogFile="Config"
OverrideString=""
pre_run_file=""

for arg in "$@"; do
    case $arg in
        --prerun) PreRun=true ;;
        --postrun) PostRun=true ;;
        --logfile=*) LogFile="${arg#*=}" ;;
        --prerunfile=*) pre_run_file="${arg#*=}" ;;
        --override-string=*) OverrideString="${arg#*=}" ;;
        *)
            echo " ERROR - Unknown argument: $arg" >&2
            exit 1
            ;;
    esac
done

if $PreRun && $PostRun; then
    echo " ERROR - Specify only one of --prerun and --postrun." >&2
    exit 1
fi

# Table entries are kept as "key<TAB>value<TAB>kind" lines; overrides win over readings.
Table="${TMPDIR:-/data/local/tmp}/config_check_$$.tsv"
: > "$Table" || { echo " ERROR - Unable to create $Table" >&2; exit 1; }
trap 'rm -f "$Table"' EXIT

add_to_table() {
    printf '%s\t%s\treading\n' "$1" "$2" >> "$Table"
}

output_table() {
    output_file="${LogFile}.csv"
    awk -F '\t' '
        function csv(v) {
            if (v ~ /[,"\r\n]/) { gsub(/"/, "\"\"", v); return "\"" v "\"" }
            return v
        }
        {
            if (!($1 in seen)) { seen[$1] = 1; order[++n] = $1 }
            if ($3 == "override") { override[$1] = $2 } else { value[$1] = $2 }
        }
        END {
            for (i = 1; i <= n; i++) {
                k = order[i]
                print csv(k) "," csv((k in override) ? override[k] : value[k])
            }
        }' "$Table" > "$output_file" || { echo " ERROR - Unable to write $output_file" >&2; exit 1; }
    cat "$output_file"
    echo "Configuration table saved to $output_file"
}

# Preserve the existing flat override format, including HOBL's single-quoted keys.
# Nested objects/arrays and commas within values are not supported.
json_to_override_table() {
    json_string="$1"
    [ -n "$json_string" ] || return 0
    json_string=$(printf '%s' "$json_string" | sed "s/[][{}'\"]//g")
    old_ifs=$IFS
    IFS=','
    for pair in $json_string; do
        IFS=$old_ifs
        case $pair in
            *:*) ;;
            *)
                echo " ERROR - Invalid override pair: $pair" >&2
                exit 1
                ;;
        esac
        key=$(printf '%s' "${pair%%:*}" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        value=$(printf '%s' "${pair#*:}" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        if [ -z "$key" ]; then
            echo " ERROR - Override keys cannot be empty." >&2
            exit 1
        fi
        printf '%s\t%s\toverride\n' "$key" "$value" >> "$Table"
    done
    IFS=$old_ifs
}

read_attribute() {
    if [ -r "$1" ]; then
        cat "$1" 2>/dev/null || printf 'N/A'
    else
        printf 'N/A'
    fi
}

is_number() {
    printf '%s' "$1" | grep -Eq '^[0-9]+([.][0-9]+)?$'
}

add_reading() {
    if [ -z "$2" ] || [ "$2" = "N/A" ]; then
        echo " WARNING - $1 unavailable on this system." >&2
        add_to_table "$1" "N/A"
    else
        add_to_table "$1" "$2"
    fi
}

# Value of a "key: value" line from dumpsys battery.
dumpsys_battery() {
    dumpsys battery 2>/dev/null | awk -F': ' -v key="$1" '{gsub(/^[ \t]+/, "", $1)} $1 == key {print $2; exit}'
}

read_battery() {
    battery_level="N/A"
    battery_status="N/A"
    battery_capacity_wh="N/A"
    # Android's charge counter (uAh) and battery voltage (mV), used when the fuel gauge isn't readable.
    charge_counter_mah="N/A"
    battery_voltage_mv="N/A"
    counter=$(dumpsys_battery "Charge counter")
    if is_number "$counter"; then
        charge_counter_mah=$(awk -v uah="$counter" 'BEGIN {printf "%.1f", uah / 1000}')
    fi
    voltage_mv=$(dumpsys_battery "voltage")
    if is_number "$voltage_mv"; then
        battery_voltage_mv="$voltage_mv"
    fi

    # Fuel gauge readings give two decimal places, when the kernel exposes them to the shell.
    for supply in /sys/class/power_supply/*; do
        [ "$(read_attribute "$supply/type")" = "Battery" ] || continue
        [ "$(read_attribute "$supply/present")" != "0" ] || continue
        current=$(read_attribute "$supply/charge_now")
        full=$(read_attribute "$supply/charge_full")
        if is_number "$current" && is_number "$full" && [ "$full" != "0" ]; then
            battery_level=$(awk -v now="$current" -v full="$full" 'BEGIN {printf "%.2f", now / full * 100}')
        fi
        voltage=$(read_attribute "$supply/voltage_min_design")
        if is_number "$full" && is_number "$voltage" && [ "$full" != "0" ] && [ "$voltage" != "0" ]; then
            battery_capacity_wh=$(awk -v full="$full" -v volts="$voltage" 'BEGIN {print full * volts / 1e12}')
        fi
        break
    done

    if ! is_number "$battery_level"; then
        level=$(dumpsys_battery "level")
        scale=$(dumpsys_battery "scale")
        if is_number "$level" && is_number "$scale" && [ "$scale" != "0" ]; then
            battery_level=$(awk -v level="$level" -v scale="$scale" 'BEGIN {printf "%.2f", level / scale * 100}')
        fi
    fi

    # BatteryManager status codes.
    case "$(dumpsys_battery "status")" in
        2) battery_status="charging" ;;
        3) battery_status="discharging" ;;
        4) battery_status="not charging" ;;
        5) battery_status="charged" ;;
    esac
}

read_brightness() {
    screen_brightness_pct="N/A"
    brightness=$(settings get system screen_brightness 2>/dev/null)
    if is_number "$brightness"; then
        screen_brightness_pct=$(awk -v now="$brightness" 'BEGIN {printf "%.0f", now / 255 * 100}')
    fi
}

read_volume() {
    audio_volume="N/A"
    # Example output: "volume is 7 in range [0..15]"
    output=$(cmd media_session volume --stream 3 --get 2>/dev/null)
    audio_volume=$(printf '%s' "$output" | awk 'match($0, /volume is [0-9]+ in range \[[0-9]+\.\.[0-9]+\]/) {
        split(substr($0, RSTART, RLENGTH), parts, /[^0-9]+/)
        if (parts[4] > 0) printf "%.0f", parts[2] / parts[4] * 100
        exit
    }')
}

# Numeric Android setting, e.g. "system screen_off_timeout", or N/A if it isn't set.
read_setting() {
    value=$(settings get $1 2>/dev/null)
    if is_number "$value"; then printf '%s' "$value"; else printf 'N/A'; fi
}

collect_run_readings() {
    phase="$1"
    read_battery
    read_brightness
    read_volume
    add_reading "Run $phase Battery State (%)" "$battery_level"
    add_reading "Run $phase Charge Counter (mAh)" "$charge_counter_mah"
    add_reading "Run $phase Battery Voltage (mV)" "$battery_voltage_mv"
    add_reading "Run $phase Charge State" "$battery_status"
    add_reading "Run $phase Screen Brightness (%)" "$screen_brightness_pct"
    add_reading "Run $phase Audio Volume (%)" "$audio_volume"
}

csv_value() {
    awk -F, -v key="$1" '$1 == key {sub(/\r$/, "", $2); print $2; exit}' "$2"
}

json_to_override_table "$OverrideString"

if $PreRun; then
    echo "Running pre-run checks..."
    add_to_table "Run Start Time" "$(date +'%Y-%m-%d %H:%M:%S')"
    collect_run_readings "Start"
    # dut_setup_aluminium.ps1 sets the maximum screen timeout so the display stays on for the whole run.
    add_reading "Screen Off Timeout (ms)" "$(read_setting 'system screen_off_timeout')"
    add_reading "Stay On While Plugged In" "$(read_setting 'global stay_on_while_plugged_in')"
elif $PostRun; then
    if [ ! -f "$pre_run_file" ]; then
        echo " ERROR - Pre-run file $pre_run_file not found." >&2
        exit 1
    fi
    run_start_time=$(csv_value "Run Start Time" "$pre_run_file")
    # toybox date takes the input format with -D.
    if [ -z "$run_start_time" ] || ! stime=$(date -D '%Y-%m-%d %H:%M:%S' -d "$run_start_time" +%s 2>/dev/null); then
        echo " ERROR - Missing or invalid Run Start Time in pre-run file." >&2
        exit 1
    fi
    echo "Running post-run checks..."
    run_stop_time=$(date +'%Y-%m-%d %H:%M:%S')
    etime=$(date -D '%Y-%m-%d %H:%M:%S' -d "$run_stop_time" +%s)
    run_duration_seconds=$((etime - stime))
    if [ "$run_duration_seconds" -lt 0 ]; then
        echo " ERROR - Run Stop Time precedes Run Start Time." >&2
        exit 1
    fi
    add_to_table "Run Stop Time" "$run_stop_time"
    collect_run_readings "Stop"
    add_to_table "Run Duration (min)" "$(awk -v seconds="$run_duration_seconds" 'BEGIN {printf "%.2f", seconds / 60}')"
    start_battery_level=$(csv_value "Run Start Battery State (%)" "$pre_run_file")
    battery_drain_percentage="N/A"
    battery_drain_wh="N/A"
    battery_drain_rate_mw="N/A"
    if is_number "$start_battery_level" && is_number "$battery_level"; then
        battery_drain_percentage=$(awk -v start="$start_battery_level" -v stop="$battery_level" 'BEGIN {drain = start - stop; printf "%.2f", (drain > 0 ? drain : 0)}')
        if is_number "$battery_capacity_wh"; then
            battery_drain_wh=$(awk -v capacity="$battery_capacity_wh" -v drain="$battery_drain_percentage" 'BEGIN {printf "%.2f", capacity * drain / 100}')
            if [ "$run_duration_seconds" -gt 0 ]; then
                battery_drain_rate_mw=$(awk -v capacity="$battery_capacity_wh" -v drain="$battery_drain_percentage" -v seconds="$run_duration_seconds" 'BEGIN {printf "%.0f", capacity * drain / 100 * 1000 * 3600 / seconds}')
            fi
        fi
    fi
    # Googlebook builds don't let the shell read the fuel gauge's capacity, so the energy comes from the charge
    # counter and the average battery voltage instead.
    start_counter=$(csv_value "Run Start Charge Counter (mAh)" "$pre_run_file")
    start_voltage=$(csv_value "Run Start Battery Voltage (mV)" "$pre_run_file")
    if [ "$battery_drain_wh" = "N/A" ] && is_number "$start_counter" && is_number "$charge_counter_mah" \
            && is_number "$start_voltage" && is_number "$battery_voltage_mv"; then
        battery_drain_wh=$(awk -v start="$start_counter" -v stop="$charge_counter_mah" -v v1="$start_voltage" -v v2="$battery_voltage_mv" \
            'BEGIN {used = start - stop; printf "%.2f", (used > 0 ? used : 0) * (v1 + v2) / 2 / 1e6}')
        if [ "$run_duration_seconds" -gt 0 ]; then
            battery_drain_rate_mw=$(awk -v wh="$battery_drain_wh" -v seconds="$run_duration_seconds" 'BEGIN {printf "%.0f", wh * 1000 * 3600 / seconds}')
        fi
    fi
    add_reading "Battery Drain (%)" "$battery_drain_percentage"
    add_reading "Battery Drain (Wh)" "$battery_drain_wh"
    add_reading "Run Drain Rate (mW)" "$battery_drain_rate_mw"
else
    processor_model=$(getprop ro.soc.model 2>/dev/null)
    if [ -n "$processor_model" ]; then
        processor_model="$(getprop ro.soc.manufacturer 2>/dev/null) $processor_model"
    else
        processor_model=$(awk -F: '/^(model name|Model|Hardware)[[:space:]]*:/ {sub(/^[[:space:]]+/, "", $2); print $2; exit}' /proc/cpuinfo 2>/dev/null)
    fi
    add_reading "CPU Name" "$processor_model"
    add_to_table "CPU Architecture" "$(uname -m)"
    add_reading "OS Version" "Android $(getprop ro.build.version.release 2>/dev/null)"
    add_reading "OS Build Version" "$(getprop ro.build.display.id 2>/dev/null)"
    add_reading "Serial Number" "$(getprop ro.serialno 2>/dev/null)"
    # Some models already start with the manufacturer, e.g. "HP Googlebook 14".
    manufacturer=$(getprop ro.product.manufacturer 2>/dev/null)
    model=$(getprop ro.product.model 2>/dev/null)
    case "$model" in
        "$manufacturer"*) ;;
        *) model="$manufacturer $model" ;;
    esac
    add_reading "Model Identifier" "$(printf '%s' "$model" | tr ',' '_')"
    add_reading "Memory Size (GB)" "$(awk '/^MemTotal:/ {printf "%d", $2 * 1024 / 1000000000; exit}' /proc/meminfo 2>/dev/null)"
    add_reading "Storage Size (GB)" "$(df -k /data 2>/dev/null | awk 'NR == 2 {printf "%.0f", $2 * 1024 / 1000000000}')"
fi

output_table
