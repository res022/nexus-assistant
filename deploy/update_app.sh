#!/bin/bash
#
# Nexus Assistant - Update Script
# Run this to update the application after making changes
#
# Usage: bash update_app.sh
#

set -e  # Exit on error

echo "=========================================="
echo "  Nexus Assistant - Update Application"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

APP_DIR="$HOME/nexus-assistant"

cd "$APP_DIR"

echo -e "${GREEN}[1/5] Pulling latest changes from git...${NC}"
if [ -d ".git" ]; then
    git pull origin main
    echo -e "${GREEN}Git pull completed${NC}"
else
    echo -e "${YELLOW}Not a git repository, skipping...${NC}"
fi

echo ""
echo -e "${GREEN}[2/5] Activating virtual environment...${NC}"
source venv/bin/activate

echo ""
echo -e "${GREEN}[3/5] Updating Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt --upgrade

echo ""
echo -e "${GREEN}[4/5] Restarting application...${NC}"
sudo systemctl restart nexus-assistant

# Wait for service to restart
sleep 2

echo ""
echo -e "${GREEN}[5/5] Checking service status...${NC}"
sudo systemctl status nexus-assistant --no-pager -l | head -15

echo ""
echo "=========================================="
echo -e "${GREEN}Update completed successfully!${NC}"
echo "=========================================="
echo ""
echo "Check logs: sudo tail -f /var/log/nexus-assistant/error.log"
echo ""
