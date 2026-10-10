#!/bin/bash
# ==============================================================================
# AWS EC2 Automated User Data Script for Proof of Search AI (neatHack 2026)
# Target OS: Ubuntu 24.04 LTS / 22.04 LTS
# Team: Vincci001 (Lead: Ibochi Vincent)
# ==============================================================================

set -euxo pipefail

echo "==> Updating package indices and installing prerequisites..."
apt-get update -y
apt-get install -y git python3 python3-pip python3-venv curl ufw

echo "==> Cloning Proof of Search AI repository from GitHub..."
mkdir -p /opt
cd /opt
rm -rf proof-of-search-ai
git clone https://github.com/ibochivincent-lang/proof-of-search-ai.git /opt/proof-of-search-ai
cd /opt/proof-of-search-ai

echo "==> Setting up Python virtual environment..."
python3 -m venv /opt/proof-of-search-ai/venv
/opt/proof-of-search-ai/venv/bin/pip install --upgrade pip setuptools wheel
/opt/proof-of-search-ai/venv/bin/pip install -e .

echo "==> Configuring environment variables..."
cat << 'EOF' > /opt/proof-of-search-ai/.env
# neatHack 2026 Credentials for Team Vincci001
LITELLM_API_KEY=sk-G2CdcbfSft_q8UoLOs13xQ
LITELLM_BASE_URL=https://litellm.vision.aivar.app/v1
RESEARCH_AGENT_MODEL=claude-haiku
NEATLOGS_API_KEY=g0mx_xH8a6btCYnVOH0wGk4mkzaqz1jS
CRUSTDATA_API_KEY=cd_a6070a6b539f8eb3f46c1e9acdf19ab78ef6
EOF

chmod 600 /opt/proof-of-search-ai/.env

echo "==> Creating systemd service for 24/7 background operation..."
cat << 'EOF' > /etc/systemd/system/proofsearch.service
[Unit]
Description=Proof of Search AI Web Console & Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/proof-of-search-ai
EnvironmentFile=/opt/proof-of-search-ai/.env
ExecStart=/opt/proof-of-search-ai/venv/bin/python -m research_agent.server --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "==> Starting Proof of Search AI service..."
systemctl daemon-reload
systemctl enable proofsearch.service
systemctl restart proofsearch.service

echo "==> Verifying service status..."
systemctl is-active proofsearch.service

echo "=========================================================="
echo "Proof of Search AI is LIVE on http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
echo "=========================================================="
