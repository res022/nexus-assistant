#!/bin/bash
#
# Nexus Assistant - Automated VM Setup Script
# Run this script on your Google Cloud VM after initial connection
#
# Usage: bash setup_vm.sh
#

set -e  # Exit on error

echo "=========================================="
echo "  Nexus Assistant - VM Setup Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}ERROR: Do not run this script as root!${NC}"
    echo "Run as your regular user (the script will ask for sudo when needed)"
    exit 1
fi

echo -e "${GREEN}[1/8] Updating system packages...${NC}"
sudo apt update
sudo apt upgrade -y

echo ""
echo -e "${GREEN}[2/8] Installing Python 3.11 and dependencies...${NC}"
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    nginx \
    ufw \
    curl \
    htop \
    unattended-upgrades \
    fail2ban

echo ""
echo -e "${GREEN}[3/8] Configuring firewall...${NC}"
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw --force enable
echo -e "${YELLOW}Firewall status:${NC}"
sudo ufw status

echo ""
echo -e "${GREEN}[4/8] Enabling automatic security updates...${NC}"
sudo dpkg-reconfigure -plow unattended-upgrades

echo ""
echo -e "${GREEN}[5/8] Configuring fail2ban (brute force protection)...${NC}"
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

echo ""
echo -e "${GREEN}[6/8] Setting up log directories...${NC}"
sudo mkdir -p /var/log/nexus-assistant
sudo chown $USER:www-data /var/log/nexus-assistant
sudo chmod 755 /var/log/nexus-assistant

echo ""
echo -e "${GREEN}[7/8] Configuring Nginx...${NC}"
sudo systemctl enable nginx
sudo systemctl start nginx

echo ""
echo -e "${GREEN}[8/8] System setup complete!${NC}"
echo ""
echo "=========================================="
echo "  Next Steps:"
echo "=========================================="
echo "1. Upload your application to ~/nexus-assistant"
echo "2. Run: bash ~/nexus-assistant/deploy/install_app.sh"
echo ""
echo -e "${YELLOW}System Information:${NC}"
echo "  OS: $(lsb_release -d | cut -f2)"
echo "  Python: $(python3 --version)"
echo "  Nginx: $(nginx -v 2>&1)"
echo "  Memory: $(free -h | grep Mem | awk '{print $2}')"
echo "  Disk: $(df -h / | tail -1 | awk '{print $2}')"
echo ""
echo -e "${GREEN}VM setup completed successfully!${NC}"
