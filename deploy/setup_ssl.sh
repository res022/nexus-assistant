#!/bin/bash
#
# Nexus Assistant - SSL Certificate Setup
# Run this after setting up your domain name
#
# Usage: bash setup_ssl.sh yourdomain.com
#

set -e  # Exit on error

echo "=========================================="
echo "  Nexus Assistant - SSL Setup"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if domain provided
if [ -z "$1" ]; then
    echo -e "${RED}ERROR: Domain name required${NC}"
    echo "Usage: bash setup_ssl.sh yourdomain.com"
    exit 1
fi

DOMAIN=$1

echo -e "${YELLOW}Domain: $DOMAIN${NC}"
echo ""

# Verify domain is pointing to this server
echo -e "${GREEN}[1/5] Verifying DNS...${NC}"
EXTERNAL_IP=$(curl -s ifconfig.me)
DOMAIN_IP=$(dig +short $DOMAIN | tail -1)

echo "  Server IP:  $EXTERNAL_IP"
echo "  Domain IP:  $DOMAIN_IP"

if [ "$EXTERNAL_IP" != "$DOMAIN_IP" ]; then
    echo -e "${YELLOW}WARNING: Domain IP doesn't match server IP${NC}"
    echo "Make sure your domain's DNS A record points to $EXTERNAL_IP"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}[2/5] Installing Certbot...${NC}"
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

echo ""
echo -e "${GREEN}[3/5] Updating Nginx configuration for domain...${NC}"
sudo sed -i "s/server_name .*/server_name $DOMAIN;/" /etc/nginx/sites-available/nexus-assistant
sudo nginx -t
sudo systemctl reload nginx

echo ""
echo -e "${GREEN}[4/5] Obtaining SSL certificate...${NC}"
echo -e "${YELLOW}You will be asked for:${NC}"
echo "  1. Email address (for renewal notifications)"
echo "  2. Agreement to Terms of Service"
echo "  3. Whether to redirect HTTP to HTTPS (choose YES)"
echo ""
read -p "Press Enter to continue..."
echo ""

sudo certbot --nginx -d $DOMAIN

echo ""
echo -e "${GREEN}[5/5] Testing auto-renewal...${NC}"
sudo certbot renew --dry-run

echo ""
echo "=========================================="
echo -e "${GREEN}SSL Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Your site is now available at:"
echo "  https://$DOMAIN"
echo ""
echo "Certificate will auto-renew every 90 days"
echo ""
echo "To manually renew:"
echo "  sudo certbot renew"
echo ""
