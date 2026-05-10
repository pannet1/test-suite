#!/bin/sh

# connect.sh - Network connectivity menu

CONF_DIR="/etc/wpa_supplicant"
CONF_FILE="$CONF_DIR/wpa_supplicant.conf"

enable_nm() {
    echo "--- Enabling NetworkManager ---"
    rc-service wpa_supplicant stop 2>/dev/null || true
    rc-update add networkmanager default
    rc-service networkmanager start
    echo "Done."
}

connect_wifi() {
    echo "--- WiFi Provisioning ---"

    # Find interface
    IFACE=$(iw dev | awk '/Interface/ {print $2}' | head -n 1)
    if [ -z "$IFACE" ]; then
        echo "ERROR: No WiFi hardware detected."
        return 1
    fi
    echo "Using: $IFACE"

    # Unblock radio
    rfkill unblock wifi
    if rfkill list wifi | grep -q "Hard blocked: yes"; then
        echo "HARD BLOCK: Physical switch is OFF. Flip it and press Enter."
        read _
    fi

    # Try existing config
    if [ -s "$CONF_FILE" ]; then
        echo "Trying saved config..."
        killall wpa_supplicant 2>/dev/null
        wpa_supplicant -B -i "$IFACE" -c "$CONF_FILE"
        sleep 5
        udhcpc -n -i "$IFACE" -t 5
        if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
            echo "Connected using saved profile."
            return 0
        fi
        killall wpa_supplicant 2>/dev/null
    fi

    # Scan networks
    echo "Scanning..."
    ip link set "$IFACE" up
    SCAN_RESULTS=$(iw dev "$IFACE" scan | grep "SSID" | awk '{print $2}' | sort -u)

    if [ -z "$SCAN_RESULTS" ]; then
        echo "No networks found."
        return 1
    fi

    echo "Available networks:"
    i=1
    for ssid in $SCAN_RESULTS; do
        echo "  $i) $ssid"
        eval "SSID_$i=\$ssid"
        i=$((i + 1))
    done

    echo -n "Select number or type SSID: "
    read selection
    eval chosen_ssid=\$SSID_$selection
    [ -z "$chosen_ssid" ] && chosen_ssid=$selection

    echo -n "Password for [$chosen_ssid]: "
    read -s wifi_pass
    echo ""

    # Connect
    mkdir -p "$CONF_DIR"
    wpa_passphrase "$chosen_ssid" "$wifi_pass" >"$CONF_FILE"

    killall wpa_supplicant 2>/dev/null
    wpa_supplicant -B -i "$IFACE" -c "$CONF_FILE"
    sleep 5
    udhcpc -i "$IFACE"

    if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        echo "Connected!"
        lbu add "$CONF_FILE"
        return 0
    else
        echo "Connection failed."
        rm -f "$CONF_FILE"
        return 1
    fi
}

connect_usb() {
    echo "--- USB Tethering ---"
    modprobe rndis_host
    ip link set usb0 up
    udhcpc -i usb0 || udhcpc -i eth0
    ping -c 1 8.8.8.8 && echo "Connected!" || echo "Failed."
}

# Menu
echo "=== CONNECT ==="
echo "1) Enable NetworkManager"
echo "2) Connect WiFi"
echo "3) Connect USB"
echo ""
echo -n "Select (1-3) or Enter for all: "
read choice

case "$choice" in
    1|"") enable_nm ;;
esac

case "$choice" in
    2|"") connect_wifi ;;
esac

case "$choice" in
    3|"") connect_usb ;;
esac