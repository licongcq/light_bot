#!/usr/bin/env bash
set -euo pipefail

echo "=== Stopping and disabling service ==="
sudo systemctl stop light-bot || true
sudo systemctl disable light-bot || true

echo "=== Removing systemd service file ==="
sudo rm -f /etc/systemd/system/light-bot.service
sudo systemctl daemon-reload

echo ""
echo "=== Done ==="
echo "You can now delete the project folder manually."
