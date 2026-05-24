#!/bin/bash
# AgentShield — Splunk setup script
# Imports SPL detection rules and exposes Splunk Web externally
# Usage: bash setup_splunk.sh

set -e
SPLUNK=/opt/splunk/bin/splunk
AUTH="ajith:ajith123"

echo "==> Importing AgentShield SPL detection rules..."
sudo cp ~/agentshield-splunk/splunk/detections/saved_searches.conf \
    /opt/splunk/etc/apps/search/local/saved_searches.conf

echo "==> Exposing Splunk Web on port 8060 (all interfaces)..."
sudo bash -c 'cat > /opt/splunk/etc/system/local/web.conf << EOF
[settings]
httpport = 8060
enableSplunkWebSSL = false
startwebserver = 1
EOF'

echo "==> Restarting Splunk..."
sudo $SPLUNK stop --run-as-root 2>/dev/null || true
sudo $SPLUNK start --run-as-root

echo ""
echo "==> Waiting for Splunk to start..."
sleep 20

echo "==> Verifying SPL rules loaded..."
sudo $SPLUNK list saved-search --run-as-root -auth $AUTH 2>/dev/null | grep "AgentShield" || echo "Rules loading — check Splunk Web"

echo ""
echo "==> Done!"
echo "    Splunk Web:  http://192.168.86.178:8060  (user: ajith, pass: ajith123)"
echo "    AgentShield: http://192.168.86.178:8501"
echo "    Backend API: http://192.168.86.178:8000/docs"
