#!/bin/bash
# ==============================================================================
# AWS EC2 Automated User Data Script for Jnana Agent (neatHack 2026)
# Target OS: Ubuntu 24.04 LTS / 22.04 LTS
# Team: Vincci001 (Lead: Ibochi Vincent)
# ==============================================================================

set -euxo pipefail

echo "==> Updating package indices and installing prerequisites..."
apt-get update -y
apt-get install -y git python3 python3-pip python3-venv curl ufw

echo "==> Cloning Jnana Agent repository from GitHub..."
mkdir -p /opt
cd /opt
rm -rf /opt/jnana-agent
git clone https://github.com/ibochivincent-lang/jnana-agent.git /opt/jnana-agent
cd /opt/jnana-agent

echo "==> Setting up Python virtual environment..."
python3 -m venv /opt/jnana-agent/venv
/opt/jnana-agent/venv/bin/pip install --upgrade pip setuptools wheel
/opt/jnana-agent/venv/bin/pip install -e .

echo "==> Configuring environment variables..."
cat << 'EOF' > /opt/jnana-agent/.env
# neatHack 2026 Credentials for Team Vincci001
LITELLM_API_KEY=sk-G2CdcbfSft_q8UoLOs13xQ
LITELLM_BASE_URL=https://litellm.vision.aivar.app/v1
RESEARCH_AGENT_MODEL=claude-haiku
NEATLOGS_API_KEY=g0mx_xH8a6btCYnVOH0wGk4mkzaqz1jS
CRUSTDATA_API_KEY=cd_a6070a6b539f8eb3f46c1e9acdf19ab78ef6
EOF

chmod 600 /opt/jnana-agent/.env

echo "==> Creating systemd service for 24/7 background operation..."
cat << 'EOF' > /etc/systemd/system/proofsearch.service
[Unit]
Description=Jnana Agent Web Console & Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/jnana-agent
EnvironmentFile=/opt/jnana-agent/.env
ExecStartPre=-/usr/bin/git -C /opt/jnana-agent pull origin master
ExecStart=/opt/jnana-agent/venv/bin/python -m research_agent.server --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "==> Starting Jnana Agent service..."
systemctl daemon-reload
systemctl enable proofsearch.service
systemctl restart proofsearch.service

echo "==> Verifying service status..."
systemctl is-active proofsearch.service

echo "=========================================================="
echo "Jnana Agent is LIVE on http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
echo "=========================================================="
