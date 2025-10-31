# Nexus Assistant - Google Cloud Deployment Guide

Complete step-by-step guide to deploy Nexus Assistant on Google Cloud Platform.

---

## Part 1: Google Cloud VM Setup

### Step 1: Create a Google Cloud VM Instance

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Login with your Google account (the one with $300 credit)

2. **Navigate to Compute Engine**
   - Click hamburger menu (☰) → Compute Engine → VM instances
   - Click "Create Instance" button

3. **Configure VM Settings:**

   **Basic Settings:**
   - **Name:** `nexus-assistant-vm`
   - **Region:** Choose closest to your users (e.g., `europe-west1` for Europe, `us-east1` for US)
   - **Zone:** Any zone in selected region (e.g., `europe-west1-b`)

   **Machine Configuration:**
   - **Series:** E2 (cost-effective)
   - **Machine type:** `e2-small` (2 vCPU, 2 GB memory)
     - Cost: ~$12-15/month
     - Perfect for Flask + Gemini API (API does the heavy lifting)
     - Can handle 50-100 concurrent users

   **Boot Disk:**
   - Click "CHANGE" button
   - **Operating System:** Ubuntu
   - **Version:** Ubuntu 22.04 LTS (Long Term Support)
   - **Boot disk type:** Standard persistent disk
   - **Size:** 20 GB (enough for OS + app + logs)
   - Click "SELECT"

   **Firewall:**
   - ✅ Check "Allow HTTP traffic"
   - ✅ Check "Allow HTTPS traffic"

4. **Click "CREATE"** (wait 30-60 seconds for VM to start)

---

## Part 2: Initial Server Setup

### Step 2: Connect to Your VM

**Option A: Browser SSH (Easiest)**
1. In VM instances list, click "SSH" button next to your VM
2. A terminal window will open in your browser

**Option B: Local Terminal (Windows)**
1. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install
2. Run: `gcloud compute ssh nexus-assistant-vm --zone=YOUR_ZONE`

### Step 3: Update System and Install Dependencies

Once connected to your VM, run these commands:

```bash
# Update package list
sudo apt update

# Upgrade existing packages
sudo apt upgrade -y

# Install Python 3.11 and pip
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Nginx (web server)
sudo apt install nginx -y

# Install git (to clone/update code)
sudo apt install git -y

# Install UFW firewall
sudo apt install ufw -y
```

### Step 4: Configure Firewall

```bash
# Allow SSH (important - don't lock yourself out!)
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status
```

---

## Part 3: Deploy the Application

### Step 5: Upload Your Application

**Option A: Using SCP (from your Windows machine)**

Open PowerShell on your local machine:

```powershell
# Navigate to your project
cd "C:\Users\mrluk\Desktop"

# Upload to VM (replace YOUR_ZONE and EXTERNAL_IP)
gcloud compute scp --recurse "nexus assistant" nexus-assistant-vm:~/ --zone=YOUR_ZONE
```

**Option B: Using Git (Recommended for updates)**

First, create a GitHub repository:
1. Go to github.com and create new repository: `nexus-assistant`
2. Upload your code from Windows:

```bash
cd "C:\Users\mrluk\Desktop\nexus assistant"
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/nexus-assistant.git
git push -u origin main
```

Then on your VM:

```bash
# Clone repository
cd ~
git clone https://github.com/YOUR_USERNAME/nexus-assistant.git
cd nexus-assistant
```

### Step 6: Set Up Python Environment

```bash
# Navigate to app directory
cd ~/nexus-assistant

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Gunicorn (production WSGI server)
pip install gunicorn
```

### Step 7: Configure Environment Variables

```bash
# Create .env file
nano .env
```

Add this content (paste your actual Gemini API key):

```env
GEMINI_API_KEY=AIzaSyCGfeY_Q1emufh5xs0qp-DMOf4tX-khaKQ
SECRET_KEY=nexus_assistant_secret_key_2025_san_andreas_roleplay_production
DEBUG=False
```

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

### Step 8: Test the Application

```bash
# Make sure you're in the app directory with venv activated
cd ~/nexus-assistant
source venv/bin/activate

# Test with Gunicorn
gunicorn -w 2 -b 0.0.0.0:8000 app:app
```

**Test in browser:**
- Get your VM's external IP from Google Cloud Console
- Visit: `http://YOUR_EXTERNAL_IP:8000`
- If it works, press `Ctrl+C` to stop

---

## Part 4: Production Setup with Nginx

### Step 9: Create Systemd Service (Auto-Start on Boot)

```bash
# Create service file
sudo nano /etc/systemd/system/nexus-assistant.service
```

Add this content:

```ini
[Unit]
Description=Nexus Assistant - Georgian Law Database
After=network.target

[Service]
Type=notify
User=YOUR_USERNAME
Group=www-data
WorkingDirectory=/home/YOUR_USERNAME/nexus-assistant
Environment="PATH=/home/YOUR_USERNAME/nexus-assistant/venv/bin"
ExecStart=/home/YOUR_USERNAME/nexus-assistant/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile /var/log/nexus-assistant/access.log \
    --error-logfile /var/log/nexus-assistant/error.log \
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Replace `YOUR_USERNAME`** with your actual username (run `whoami` to check)

Save and exit: `Ctrl+X`, `Y`, `Enter`

```bash
# Create log directory
sudo mkdir -p /var/log/nexus-assistant
sudo chown YOUR_USERNAME:www-data /var/log/nexus-assistant

# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable nexus-assistant

# Start service
sudo systemctl start nexus-assistant

# Check status
sudo systemctl status nexus-assistant
```

### Step 10: Configure Nginx as Reverse Proxy

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/nexus-assistant
```

Add this content:

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    # Increase client body size for potential file uploads
    client_max_body_size 10M;

    # Access and error logs
    access_log /var/log/nginx/nexus-assistant-access.log;
    error_log /var/log/nginx/nexus-assistant-error.log;

    # Static files
    location /static {
        alias /home/YOUR_USERNAME/nexus-assistant/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout settings for AI requests
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

**Replace:**
- `YOUR_DOMAIN_OR_IP` → your VM's external IP (or domain if you have one)
- `YOUR_USERNAME` → your actual username

Save and exit: `Ctrl+X`, `Y`, `Enter`

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/nexus-assistant /etc/nginx/sites-enabled/

# Remove default Nginx page
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Enable Nginx on boot
sudo systemctl enable nginx
```

---

## Part 5: Get Your External IP and Test

### Step 11: Find Your Public IP

```bash
# Get external IP
curl ifconfig.me
```

Or check in Google Cloud Console:
- Compute Engine → VM instances → Look for "External IP" column

### Step 12: Access Your Application

Open browser and visit:
```
http://YOUR_EXTERNAL_IP
```

You should see the Nexus Assistant homepage!

---

## Part 6: Set Up Custom Domain (Optional)

### Step 13: Configure Domain Name

If you have a domain (e.g., `nexus.example.com`):

1. **Add DNS A Record:**
   - Go to your domain registrar (Namecheap, GoDaddy, etc.)
   - Add an A record pointing to your VM's external IP
   - Wait 5-60 minutes for DNS propagation

2. **Update Nginx Config:**

```bash
sudo nano /etc/nginx/sites-available/nexus-assistant
```

Change `server_name YOUR_DOMAIN_OR_IP;` to `server_name nexus.example.com;`

```bash
sudo nginx -t
sudo systemctl restart nginx
```

### Step 14: Add SSL Certificate (HTTPS)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d nexus.example.com

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose: Redirect HTTP to HTTPS (option 2)

# Auto-renewal is set up automatically
# Test renewal:
sudo certbot renew --dry-run
```

Now your site is accessible at: `https://nexus.example.com`

---

## Part 7: Maintenance and Monitoring

### Useful Commands

**Check Application Status:**
```bash
sudo systemctl status nexus-assistant
```

**View Application Logs:**
```bash
# Real-time logs
sudo tail -f /var/log/nexus-assistant/error.log

# Access logs
sudo tail -f /var/log/nexus-assistant/access.log
```

**Restart Application:**
```bash
sudo systemctl restart nexus-assistant
```

**Update Application:**
```bash
cd ~/nexus-assistant
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart nexus-assistant
```

**Check Nginx Status:**
```bash
sudo systemctl status nginx
```

**View Nginx Logs:**
```bash
sudo tail -f /var/log/nginx/nexus-assistant-error.log
```

**Check Disk Space:**
```bash
df -h
```

**Check Memory Usage:**
```bash
free -h
```

**Monitor Active Connections:**
```bash
sudo netstat -tuln | grep :80
```

---

## Part 8: Cost Optimization

### Expected Monthly Costs

**VM Instance (e2-small):**
- ~$12-15/month
- 730 hours/month × $0.0168/hour = ~$12.26

**Network Egress:**
- First 1 GB free
- Then ~$0.12/GB (North America)
- Estimate: ~$2-5/month for moderate traffic

**Gemini API:**
- Gemini 2.0 Flash: $0.075 per 1M input tokens
- With pre-generated quiz questions, cost is minimal
- Estimate: ~$1-3/month for chat features

**Total: ~$15-23/month**

### Money-Saving Tips

1. **Stop VM when not in use:**
   ```bash
   # From local machine
   gcloud compute instances stop nexus-assistant-vm --zone=YOUR_ZONE

   # Start again
   gcloud compute instances start nexus-assistant-vm --zone=YOUR_ZONE
   ```

2. **Use committed use discounts:**
   - Google Cloud Console → Compute Engine → Committed use discounts
   - Save up to 57% with 1-year or 3-year commitment

3. **Monitor costs:**
   - Google Cloud Console → Billing → Reports
   - Set up budget alerts

---

## Part 9: Security Checklist

### Essential Security Steps

**1. Create a non-root user (if not already):**
```bash
# Run as root/sudo user
sudo adduser appuser
sudo usermod -aG sudo appuser
```

**2. Disable root SSH login:**
```bash
sudo nano /etc/ssh/sshd_config
```
Change: `PermitRootLogin no`
```bash
sudo systemctl restart sshd
```

**3. Set up automatic security updates:**
```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

**4. Install fail2ban (protects against brute force):**
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

**5. Restrict database file permissions:**
```bash
cd ~/nexus-assistant
chmod 640 quiz_data.db
chmod 640 .env
```

---

## Part 10: Troubleshooting

### Problem: Application won't start

**Check logs:**
```bash
sudo journalctl -u nexus-assistant -n 50
```

**Common fixes:**
- Check .env file exists and has correct API key
- Verify Python dependencies: `pip list`
- Check file permissions: `ls -la ~/nexus-assistant`

### Problem: "502 Bad Gateway"

**Cause:** Gunicorn not running

**Fix:**
```bash
sudo systemctl restart nexus-assistant
sudo systemctl status nexus-assistant
```

### Problem: Georgian text shows as "??????"

**Cause:** Missing UTF-8 locale

**Fix:**
```bash
sudo locale-gen ka_GE.UTF-8
sudo update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
```

### Problem: High memory usage

**Check memory:**
```bash
free -h
htop  # Install with: sudo apt install htop
```

**Fix:** Reduce Gunicorn workers in service file:
```bash
sudo nano /etc/systemd/system/nexus-assistant.service
# Change: --workers 3  →  --workers 2
sudo systemctl daemon-reload
sudo systemctl restart nexus-assistant
```

---

## Quick Reference

### VM Specifications Summary
```
Machine Type:    e2-small (2 vCPU, 2 GB RAM)
OS:              Ubuntu 22.04 LTS
Disk:            20 GB Standard Persistent Disk
Region:          europe-west1 (or closest to users)
Cost:            ~$15/month

Software Stack:
- Python 3.11 + Flask
- Gunicorn (3 workers)
- Nginx (reverse proxy)
- SQLite database
- Google Gemini API
```

### Service Management
```bash
# Application
sudo systemctl start|stop|restart|status nexus-assistant

# Web Server
sudo systemctl start|stop|restart|status nginx

# View Logs
sudo tail -f /var/log/nexus-assistant/error.log
sudo tail -f /var/log/nginx/nexus-assistant-error.log
```

### File Locations
```
Application:     /home/YOUR_USERNAME/nexus-assistant
Logs:           /var/log/nexus-assistant/
Nginx Config:   /etc/nginx/sites-available/nexus-assistant
Service File:   /etc/systemd/system/nexus-assistant.service
```

---

## Success Checklist

- [ ] VM created with e2-small instance
- [ ] Ubuntu 22.04 LTS installed
- [ ] Firewall configured (ports 22, 80, 443)
- [ ] Application uploaded to VM
- [ ] Python dependencies installed
- [ ] .env file configured with API key
- [ ] Gunicorn service created and running
- [ ] Nginx configured and running
- [ ] Application accessible via external IP
- [ ] SSL certificate installed (if using domain)
- [ ] Automatic security updates enabled
- [ ] Logs accessible and monitoring set up

---

## Support

If you encounter issues:
1. Check logs: `sudo tail -f /var/log/nexus-assistant/error.log`
2. Verify service status: `sudo systemctl status nexus-assistant`
3. Test Nginx: `sudo nginx -t`
4. Check firewall: `sudo ufw status`

**Made with ❤️ for San Andreas Roleplay Server**
