#!/bin/bash
# ==============================================================================
# AWS EC2 Automated User Data Script for Jnana Agent (neatHack 2026)
# Target OS: Ubuntu 24.04 LTS / 22.04 LTS
# Team: Vincci001 (Lead: Ibochi Vincent)
# Features:
#   1. Automatic git clone & venv setup
#   2. Docker installation for ephemeral execution sandboxing (/api/reproduce-test)
#   3. Caddy reverse proxy installation for automated TLS (HTTPS) on ports 80 & 443
#   4. systemd 24/7 background service management with auto-restart
# ==============================================================================

set -euxo pipefail

echo "==> Updating package indices and installing prerequisites..."
apt-get update -y
apt-get install -y git python3 python3-pip python3-venv curl ufw ca-certificates gnupg debian-keyring debian-archive-keyring apt-transport-https

echo "==> Installing Docker Engine for ephemeral sandbox execution..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
fi

echo "==> Installing Caddy Server for automated TLS reverse proxy..."
if ! command -v caddy &> /dev/null; then
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg --yes
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
    apt-get update -y
    apt-get install -y caddy
fi

echo "==> Cloning Jnana Agent repository from GitHub..."
mkdir -p /opt
cd /opt
rm -rf /opt/jnanaagent
git clone https://github.com/ibochivincent-lang/jnanaagent.git /opt/jnanaagent
cd /opt/jnanaagent

echo "==> Setting up Python virtual environment..."
python3 -m venv /opt/jnanaagent/venv
/opt/jnanaagent/venv/bin/pip install --upgrade pip setuptools wheel
/opt/jnanaagent/venv/bin/pip install -e .

echo "==> Configuring environment variables..."
cat << 'EOF' > /opt/jnanaagent/.env
# neatHack 2026 Credentials for Team Vincci001
LITELLM_API_KEY=sk-G2CdcbfSft_q8UoLOs13xQ
LITELLM_BASE_URL=https://litellm.vision.aivar.app/v1
RESEARCH_AGENT_MODEL=claude-haiku
NEATLOGS_API_KEY=g0mx_xH8a6btCYnVOH0wGk4mkzaqz1jS
CRUSTDATA_API_KEY=cd_a6070a6b539f8eb3f46c1e9acdf19ab78ef6
EOF

chmod 600 /opt/jnanaagent/.env

echo "==> Configuring Caddy Reverse Proxy..."
cp /opt/jnanaagent/deploy/Caddyfile /etc/caddy/Caddyfile
systemctl daemon-reload
systemctl enable caddy
systemctl restart caddy

echo "==> Creating systemd service for 24/7 background operation..."
cat << 'EOF' > /etc/systemd/system/jnanaagent.service
[Unit]
Description=Jnana Agent Web Console & Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/jnanaagent
EnvironmentFile=/opt/jnanaagent/.env
ExecStartPre=-/usr/bin/git -C /opt/jnanaagent pull origin master
ExecStart=/opt/jnanaagent/venv/bin/python -m research_agent.server --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "==> Starting Jnana Agent service..."
systemctl daemon-reload
systemctl enable jnanaagent.service
systemctl restart jnanaagent.service

echo "==> Verifying service status..."
systemctl is-active jnanaagent.service
systemctl is-active caddy

echo "=========================================================="
echo "Jnana Agent is LIVE with Caddy Proxy on http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo "=========================================================="
