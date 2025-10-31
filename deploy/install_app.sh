#!/bin/bash
#
# Nexus Assistant - Application Installation Script
# Run this after setup_vm.sh to install and configure the application
#
# Usage: bash install_app.sh
#

set -e  # Exit on error

echo "=========================================="
echo "  Nexus Assistant - App Installation"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get current directory
APP_DIR="$HOME/nexus-assistant"
CURRENT_USER=$(whoami)

# Check if app directory exists
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}ERROR: Application directory not found at $APP_DIR${NC}"
    echo "Please upload your application first or clone from git"
    exit 1
fi

cd "$APP_DIR"

echo -e "${GREEN}[1/7] Creating Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

echo ""
echo -e "${GREEN}[2/7] Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo ""
echo -e "${GREEN}[3/7] Checking .env file...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    echo -e "${YELLOW}WARNING: .env file not found!${NC}"
    echo "Creating template .env file..."
    cat > "$APP_DIR/.env" << 'EOF'
GEMINI_API_KEY=your_api_key_here
SECRET_KEY=nexus_assistant_secret_key_2025_production
DEBUG=False
EOF
    echo -e "${RED}IMPORTANT: Edit $APP_DIR/.env and add your actual GEMINI_API_KEY${NC}"
    echo "Press Enter to continue after editing .env file..."
    read
else
    echo -e "${GREEN}.env file exists${NC}"
fi

echo ""
echo -e "${GREEN}[4/7] Setting file permissions...${NC}"
chmod 640 "$APP_DIR/.env"
chmod 640 "$APP_DIR/quiz_data.db"

echo ""
echo -e "${GREEN}[5/7] Creating systemd service...${NC}"
sudo tee /etc/systemd/system/nexus-assistant.service > /dev/null << EOF
[Unit]
Description=Nexus Assistant - Georgian Law Database
After=network.target

[Service]
Type=notify
User=$CURRENT_USER
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn \\
    --workers 3 \\
    --bind 127.0.0.1:8000 \\
    --timeout 120 \\
    --access-logfile /var/log/nexus-assistant/access.log \\
    --error-logfile /var/log/nexus-assistant/error.log \\
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo -e "${GREEN}[6/7] Configuring Nginx...${NC}"

# Get external IP
EXTERNAL_IP=$(curl -s ifconfig.me)

sudo tee /etc/nginx/sites-available/nexus-assistant > /dev/null << EOF
server {
    listen 80;
    server_name $EXTERNAL_IP;

    client_max_body_size 10M;

    access_log /var/log/nginx/nexus-assistant-access.log;
    error_log /var/log/nginx/nexus-assistant-error.log;

    location /static {
        alias $APP_DIR/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/nexus-assistant /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx config
echo -e "${YELLOW}Testing Nginx configuration...${NC}"
sudo nginx -t

echo ""
echo -e "${GREEN}[7/7] Starting services...${NC}"

# Reload systemd
sudo systemctl daemon-reload

# Enable and start application
sudo systemctl enable nexus-assistant
sudo systemctl start nexus-assistant

# Restart Nginx
sudo systemctl restart nginx

# Wait a moment for services to start
sleep 3

# Check status
echo ""
echo "=========================================="
echo "  Service Status"
echo "=========================================="
echo ""
echo -e "${YELLOW}Nexus Assistant:${NC}"
sudo systemctl status nexus-assistant --no-pager -l | head -15

echo ""
echo -e "${YELLOW}Nginx:${NC}"
sudo systemctl status nginx --no-pager -l | head -10

echo ""
echo "=========================================="
echo "  Installation Complete!"
echo "=========================================="
echo ""
echo -e "${GREEN}Your application is now running!${NC}"
echo ""
echo "  URL: http://$EXTERNAL_IP"
echo ""
echo "Useful commands:"
echo "  - Check app logs:     sudo tail -f /var/log/nexus-assistant/error.log"
echo "  - Check Nginx logs:   sudo tail -f /var/log/nginx/nexus-assistant-error.log"
echo "  - Restart app:        sudo systemctl restart nexus-assistant"
echo "  - Check app status:   sudo systemctl status nexus-assistant"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Visit http://$EXTERNAL_IP to test your application"
echo "2. (Optional) Set up a domain name and SSL certificate"
echo "3. Monitor logs for any errors"
echo ""
