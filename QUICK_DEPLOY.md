# Quick Deploy Guide - 5 Minutes to Production

Get Nexus Assistant running on Google Cloud in 5 minutes.

---

## Before You Start

**You need:**
- Google Cloud account with $300 credit
- Gemini API key: `AIzaSyCGfeY_Q1emufh5xs0qp-DMOf4tX-khaKQ`

---

## Step 1: Create VM (2 minutes)

1. Go to: https://console.cloud.google.com/compute/instances
2. Click "CREATE INSTANCE"
3. Configure:
   - **Name:** `nexus-assistant-vm`
   - **Region:** `europe-west1` (or closest to users)
   - **Machine type:** `e2-small` (2 vCPU, 2 GB RAM)
   - **Boot disk:** Ubuntu 22.04 LTS, 20 GB
   - **Firewall:** ✅ Allow HTTP, ✅ Allow HTTPS
4. Click "CREATE"
5. Wait 30 seconds for VM to start

**Cost: ~$15/month** (your $300 credit lasts 20 months)

---

## Step 2: Upload Application (1 minute)

**Option A: Direct Upload (Easiest)**

From Windows PowerShell:

```powershell
cd "C:\Users\mrluk\Desktop"
gcloud compute scp --recurse "nexus assistant" nexus-assistant-vm:~/ --zone=europe-west1-b
```

**Option B: Using Git**

On your VM (click SSH button):

```bash
git clone https://github.com/YOUR_USERNAME/nexus-assistant.git
cd nexus-assistant
```

---

## Step 3: Run Setup (2 minutes)

Click "SSH" button next to your VM, then run:

```bash
cd ~/nexus-assistant/deploy

# Fix line endings and make executable
sed -i 's/\r$//' *.sh
chmod +x *.sh

# Run VM setup (installs packages, firewall, nginx)
bash setup_vm.sh
```

Wait for completion (~1-2 minutes).

---

## Step 4: Install Application (1 minute)

```bash
# Install application
bash install_app.sh
```

**IMPORTANT:** When prompted, edit `.env` file:

```bash
nano ~/nexus-assistant/.env
```

Add your Gemini API key:
```
GEMINI_API_KEY=AIzaSyCGfeY_Q1emufh5xs0qp-DMOf4tX-khaKQ
SECRET_KEY=nexus_assistant_secret_key_2025_production
DEBUG=False
```

Save: `Ctrl+X`, `Y`, `Enter`

Then continue the installation.

---

## Step 5: Access Your Site

Get your external IP:

```bash
curl ifconfig.me
```

Open in browser:
```
http://YOUR_EXTERNAL_IP
```

**Done!** Your application is live! 🎉

---

## Optional: Add Domain + HTTPS

If you have a domain (e.g., `nexus.example.com`):

1. **Set DNS A Record** (in your domain registrar):
   - Point to your VM's external IP
   - Wait 5-60 minutes for DNS propagation

2. **Run SSL Setup**:
   ```bash
   cd ~/nexus-assistant/deploy
   bash setup_ssl.sh nexus.example.com
   ```

Now accessible at: `https://nexus.example.com`

---

## Useful Commands

```bash
# Check if app is running
sudo systemctl status nexus-assistant

# View error logs
sudo tail -f /var/log/nexus-assistant/error.log

# Restart application
sudo systemctl restart nexus-assistant

# Update after code changes
cd ~/nexus-assistant/deploy
bash update_app.sh
```

---

## Troubleshooting

### "502 Bad Gateway"

Application not running. Check logs:
```bash
sudo journalctl -u nexus-assistant -n 50
```

Fix: Verify `.env` file has correct API key

### Georgian text shows "??????"

SSH into VM and run:
```bash
sudo locale-gen ka_GE.UTF-8
sudo systemctl restart nexus-assistant
```

### Can't access website

Check firewall:
```bash
sudo ufw status
```

Should show ports 80 and 443 as ALLOW.

---

## What Happens Behind the Scenes

**setup_vm.sh:**
- Installs Python, Nginx, Git
- Configures firewall
- Enables auto-security updates
- Sets up fail2ban (brute force protection)

**install_app.sh:**
- Creates Python virtual environment
- Installs dependencies (Flask, Gemini API)
- Creates systemd service (auto-start on boot)
- Configures Nginx as reverse proxy
- Starts application on port 8000
- Nginx forwards port 80 → 8000

**Application runs on:**
- Gunicorn: 3 workers, handles Python/Flask
- Nginx: Reverse proxy, serves static files
- Systemd: Auto-restart if crashes, start on boot

---

## VM Specifications

```
Type:        e2-small (2 vCPU, 2 GB RAM)
OS:          Ubuntu 22.04 LTS
Disk:        20 GB Standard Persistent
Region:      europe-west1 (or your choice)
Cost:        ~$15/month

Software:
- Python 3.11 + Flask
- Gunicorn (WSGI server)
- Nginx (reverse proxy)
- SQLite (1,012 quiz questions)
- Gemini API (cloud-based)

Performance:
- Handles 50-100 concurrent users
- Quiz questions pre-generated (no API calls)
- Chat uses Gemini API (~0.5s response)
```

---

## Monitoring & Maintenance

**Check resource usage:**
```bash
htop              # CPU/Memory (press 'q' to exit)
df -h             # Disk space
free -h           # Memory usage
```

**View access logs:**
```bash
sudo tail -f /var/log/nexus-assistant/access.log
```

**Monthly costs:**
```bash
# In Google Cloud Console:
# Hamburger menu → Billing → Reports
```

**Set budget alerts:**
```bash
# Billing → Budgets & alerts → CREATE BUDGET
# Recommended: Alert at $20/month
```

---

## Need More Help?

- **Detailed guide:** See `DEPLOYMENT_GUIDE.md`
- **Scripts info:** See `deploy/README.md`
- **Application docs:** See `README.md`

---

## Summary of Steps

1. ✅ Create e2-small VM on Google Cloud
2. ✅ Upload application via gcloud or git
3. ✅ Run `bash deploy/setup_vm.sh`
4. ✅ Run `bash deploy/install_app.sh`
5. ✅ Edit `.env` with your API key
6. ✅ Visit http://YOUR_EXTERNAL_IP
7. ✅ (Optional) Add domain with `bash deploy/setup_ssl.sh`

**Total time: 5 minutes**
**Total cost: ~$15/month**

---

Made with ❤️ for San Andreas Roleplay Server
