#!/bin/sh
set -e

echo "--- Installing test-suite dependencies ---"

apk update

echo "1. Firmware & drivers..."
apk add linux-firmware-intel intel-ucode linux-firmware-amdgpu amd-ucode sof-firmware

echo "2. Git & SSH..."
apk add git openssh-client-default
git config --global user.email "prog@ecomsense.in"
git config --global user.name "b karthick"
git config --global url."git@github.com:".insteadOf "https://github.com/"

echo "3. Network..."
apk add linux-firmware-iwlwifi linux-firmware-rtlwifi linux-firmware-ath10k linux-firmware-ath11k
apk add networkmanager networkmanager-wifi wpa_supplicant wireless-tools

echo "4. Test tools..."
apk add smartmontools memtester stress-ng acpi pciutils nvme-cli kbd alsa-utils dmidecode

echo "5. Persist to USB..."
apk cache sync
touch /media/usb/.boot_repository
lbu commit -d

echo "--- Installation complete ---"