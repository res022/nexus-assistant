# Deployment Scripts

Automated scripts to deploy Nexus Assistant to Google Cloud VM.

## Quick Start

### 1. Upload Application to VM

From your local Windows machine:

```powershell
# Install Google Cloud SDK first if you haven't:
# https://cloud.google.com/sdk/docs/install

# Upload to VM
cd "C:\Users\mrluk\Desktop"
gcloud compute scp --recurse "nexus assistant" YOUR_VM_NAME:~/ --zone=YOUR_ZONE

# Or use git (recommended):
# 1. Push to GitHub
# 2. On VM: git clone https://github.com/YOUR_USERNAME/nexus-assistant.git
```

### 2. Run Setup Scripts on VM

SSH into your VM and run:

```bash
# Step 1: Setup VM (system packages, firewall, nginx)
cd ~/nexus-assistant/deploy

# Fix line endings (if scripts were created on Windows)
sed -i 's/\r$//' *.sh

# Make scripts executable
chmod +x *.sh

# Run setup
bash setup_vm.sh

# Step 2: Install application
bash install_app.sh

# Step 3 (Optional): Setup SSL if you have a domain
bash setup_ssl.sh yourdomain.com
```

Done! Your application is now live.

---

## Script Reference

### setup_vm.sh

**Purpose:** Initial VM configuration

**What it does:**
- Updates Ubuntu packages
- Installs Python 3.11, Nginx, Git
- Configures firewall (ports 22, 80, 443)
- Enables automatic security updates
- Sets up fail2ban for brute force protection
- Creates log directories

**Usage:**
```bash
bash setup_vm.sh
```

**Run once:** After creating new VM

---

### install_app.sh

**Purpose:** Install and configure Nexus Assistant

**What it does:**
- Creates Python virtual environment
- Installs Python dependencies
- Creates systemd service (auto-start on boot)
- Configures Nginx reverse proxy
- Starts application
- Shows service status

**Usage:**
```bash
bash install_app.sh
```

**Run once:** After setup_vm.sh

**Important:** Edit `.env` file with your actual Gemini API key before running!

---

### update_app.sh

**Purpose:** Update application after changes

**What it does:**
- Pulls latest code from git
- Updates Python dependencies
- Restarts application
- Shows service status

**Usage:**
```bash
bash update_app.sh
```

**Run:** Whenever you update code

---

### setup_ssl.sh

**Purpose:** Add HTTPS with free SSL certificate

**What it does:**
- Verifies DNS is pointing to server
- Installs Certbot
- Updates Nginx config with domain name
- Obtains SSL certificate from Let's Encrypt
- Sets up auto-renewal (every 90 days)

**Usage:**
```bash
bash setup_ssl.sh yourdomain.com
```

**Prerequisites:**
- Domain name purchased
- DNS A record pointing to VM's external IP
- Wait 5-60 minutes for DNS propagation

**Run once:** After domain DNS is configured

---

## Manual Deployment (No Scripts)

If you prefer manual setup, see: `../DEPLOYMENT_GUIDE.md`

---

## Troubleshooting

### Script fails with "permission denied"

Make scripts executable:
```bash
chmod +x deploy/*.sh
```

### Can't find deploy directory

Upload the entire `nexus assistant` folder, including `deploy/` subdirectory.

### .env file issues

Create `.env` manually:
```bash
cd ~/nexus-assistant
nano .env
```

Add:
```
GEMINI_API_KEY=your_actual_api_key_here
SECRET_KEY=random_secret_key_here
DEBUG=False
```

### Application not starting

Check logs:
```bash
sudo journalctl -u nexus-assistant -n 50
sudo tail -f /var/log/nexus-assistant/error.log
```

Common issues:
- Missing .env file → Create it
- Wrong API key → Update .env
- Port already in use → Check `sudo netstat -tulpn | grep :8000`

---

## File Structure

```
deploy/
├── README.md           # This file
├── setup_vm.sh        # Initial VM setup
├── install_app.sh     # Install application
├── update_app.sh      # Update application
└── setup_ssl.sh       # Add HTTPS
```

---

## Cost Estimates

**e2-small VM:** ~$12-15/month
**Network:** ~$2-5/month
**Gemini API:** ~$1-3/month

**Total: ~$15-23/month**

Your $300 Google Cloud credit will last 12-20 months.

---

## Support

For detailed manual instructions, see: `../DEPLOYMENT_GUIDE.md`
