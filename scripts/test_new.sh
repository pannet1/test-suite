#!/bin/sh

# test_new.sh - Comprehensive diagnostic suite

LOG_FILE="data/diag_report.txt"
mkdir -p data
echo "--- DIAGNOSTIC REPORT: $(date) ---" >"$LOG_FILE"

EXIT_PENDING=0
trap 'echo -e "\n[!] Exit requested." | tee -a "$LOG_FILE"; EXIT_PENDING=1' INT

run_test() {
    TEST_NAME=$1
    CMD=$2

    echo -e "\n[$TEST_NAME]..." | tee -a "$LOG_FILE"
    eval "$CMD" 2>&1 | tee -a "$LOG_FILE"
    STATUS=$?

    if [ $STATUS -ne 0 ]; then
        echo -e "\e[31m[!] ODDITY DETECTED in $TEST_NAME\e[0m" | tee -a "$LOG_FILE"
        echo "--- Press [Enter] to continue ---"
        read _ </dev/tty
    fi

    [ "$EXIT_PENDING" -eq 1 ] && exit 0
}

clear
echo "================================================="
echo "    ULTIMATE CHIP-LEVEL DIAGNOSTIC SUITE v4.2    "
echo "================================================="

# 1. I2C KERNEL
check_i2c_kernel() {
    echo "Kernel modules:"
    lsmod | grep i2c || echo "No i2c modules loaded"
    echo ""
    echo "I2C devices:"
    ls -l /dev/i2c-* 2>/dev/null || echo "No I2C devices found"
}
run_test "I2C KERNEL" "check_i2c_kernel"

# 2. BATTERY SMBUS
check_battery_smbus() {
    if command -v i2cdetect >/dev/null 2>&1; then
        for bus in $(ls /dev/i2c-* 2>/dev/null | cut -d'-' -f2); do
            echo "Scanning bus $bus for battery at 0x0B..."
            i2cdetect -y $bus 0x0b 0x0b
        done
    else
        echo "i2cdetect not found. Install i2c-tools."
    fi
}
run_test "BATTERY SMBUS" "check_battery_smbus"

# 3. STORAGE
run_test "STORAGE HEALTH" "smartctl -H /dev/sda || smartctl -H /dev/nvme0n1"

# 4. BATTERY HEALTH
check_battery() {
    for bat in /sys/class/power_supply/BAT*; do
        [ -d "$bat" ] || return 1
        DESIGN=$(cat "$bat/energy_full_design" 2>/dev/null || cat "$bat/charge_full_design" 2>/dev/null)
        FULL=$(cat "$bat/energy_full" 2>/dev/null || cat "$bat/charge_full" 2>/dev/null)
        HEALTH=$((FULL * 100 / DESIGN))
        echo "$bat: Health ${HEALTH}%"
        [ "$HEALTH" -lt 40 ] && return 1
    done
    return 0
}
run_test "BATTERY REPORT" "check_battery"

# 5. THERMAL
check_thermal() {
    OVERHEAT=0
    for zone in /sys/class/thermal/thermal_zone*; do
        [ -d "$zone" ] || continue
        TEMP=$(($(cat "$zone/temp") / 1000))
        echo "$(cat "$zone/type"): ${TEMP}°C"
        [ "$TEMP" -gt 85 ] && OVERHEAT=1
    done
    [ "$OVERHEAT" -eq 1 ] && return 1
    return 0
}
run_test "THERMAL ZONES" "check_thermal"

# 6. WIFI
check_wifi() {
    WLAN_DEV=$(nmcli -t -f DEVICE,TYPE device | grep wifi | cut -d: -f1 | head -n 1)
    if [ -z "$WLAN_DEV" ]; then
        echo "Hardware missing." && return 1
    fi
    rfkill list wifi | grep -q "yes" && { echo "Radio blocked!"; return 1; }
    nmcli -f SSID,SIGNAL,BARS dev wifi | head -n 5
}
run_test "WIFI AUDIT" "check_wifi"

echo -e "\nReport saved to: $LOG_FILE"