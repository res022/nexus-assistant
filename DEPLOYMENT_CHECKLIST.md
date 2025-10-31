# Deployment Checklist

Use this checklist to ensure you complete all steps for deployment.

---

## Pre-Deployment

- [ ] Google Cloud account created
- [ ] $300 credit activated
- [ ] Gemini API key obtained: `AIzaSyCGfeY_Q1emufh5xs0qp-DMOf4tX-khaKQ`
- [ ] Google Cloud SDK installed (for gcloud commands)
- [ ] Application tested locally on Windows

---

## Google Cloud VM Creation

- [ ] Logged into https://console.cloud.google.com
- [ ] Navigated to Compute Engine → VM instances
- [ ] Created new instance with settings:
  - [ ] Name: `nexus-assistant-vm`
  - [ ] Region: `europe-west1` (or your choice)
  - [ ] Machine type: `e2-small` (2 vCPU, 2 GB RAM)
  - [ ] Boot disk: Ubuntu 22.04 LTS, 20 GB
  - [ ] Firewall: HTTP and HTTPS allowed
- [ ] VM created successfully (green checkmark in list)
- [ ] External IP noted: `____________________`

---

## Application Upload

**Choose one method:**

### Option A: Direct Upload via gcloud
- [ ] Opened PowerShell on Windows
- [ ] Ran: `gcloud compute scp --recurse "C:\Users\mrluk\Desktop\nexus assistant" nexus-assistant-vm:~/ --zone=YOUR_ZONE`
- [ ] Upload completed successfully

### Option B: Git Upload (Recommended)
- [ ] Created GitHub repository
- [ ] Pushed code to GitHub
- [ ] SSH'd into VM
- [ ] Cloned repository: `git clone https://github.com/YOUR_USERNAME/nexus-assistant.git`

---

## VM Initial Setup

- [ ] SSH'd into VM (clicked SSH button in Console)
- [ ] Navigated to: `cd ~/nexus-assistant/deploy`
- [ ] Made scripts executable: `chmod +x *.sh`
- [ ] Ran setup script: `bash setup_vm.sh`
- [ ] Setup completed without errors
- [ ] Firewall configured (ports 22, 80, 443 open)
- [ ] Nginx installed and running

---

## Application Installation

- [ ] Ran: `bash install_app.sh`
- [ ] When prompted, edited `.env` file with API key
- [ ] Confirmed .env contains:
  ```
  GEMINI_API_KEY=AIzaSyCGfeY_Q1emufh5xs0qp-DMOf4tX-khaKQ
  SECRET_KEY=nexus_assistant_secret_key_2025_production
  DEBUG=False
  ```
- [ ] Installation completed successfully
- [ ] Service status shows "active (running)"
- [ ] Nginx status shows "active (running)"

---

## Testing

- [ ] Visited http://YOUR_EXTERNAL_IP in browser
- [ ] Homepage loads correctly
- [ ] Georgian text displays properly (not "??????")
- [ ] Tested Browse page (lists all 38 laws)
- [ ] Tested Chat page:
  - [ ] Can send Georgian question
  - [ ] AI responds in Georgian
  - [ ] Law citations shown
- [ ] Tested Quiz page:
  - [ ] Can start quiz
  - [ ] Questions load
  - [ ] Can answer questions
  - [ ] Stats update correctly

---

## Optional: Domain Setup

If using a custom domain:

- [ ] Domain purchased (e.g., nexus.example.com)
- [ ] DNS A record added pointing to VM external IP
- [ ] Waited 5-60 minutes for DNS propagation
- [ ] Verified DNS: `dig +short yourdomain.com` shows VM IP
- [ ] Ran SSL setup: `bash deploy/setup_ssl.sh yourdomain.com`
- [ ] Entered email for renewal notifications
- [ ] Agreed to Let's Encrypt Terms of Service
- [ ] Chose to redirect HTTP to HTTPS
- [ ] Certificate obtained successfully
- [ ] Visited https://yourdomain.com - shows padlock icon
- [ ] Tested auto-renewal: `sudo certbot renew --dry-run`

---

## Security Hardening

- [ ] Changed default SSH port (optional):
  - [ ] Edited: `sudo nano /etc/ssh/sshd_config`
  - [ ] Changed: `Port 2222` (or your choice)
  - [ ] Added firewall rule: `sudo ufw allow 2222/tcp`
  - [ ] Restarted SSH: `sudo systemctl restart sshd`
- [ ] Disabled root login (should be done by default)
- [ ] Automatic security updates enabled
- [ ] Fail2ban running: `sudo systemctl status fail2ban`
- [ ] Database file permissions set: `chmod 640 quiz_data.db`
- [ ] .env file permissions set: `chmod 640 .env`

---

## Monitoring Setup

- [ ] Checked logs are being written:
  - [ ] `ls -la /var/log/nexus-assistant/`
  - [ ] error.log and access.log exist
- [ ] Can view real-time logs: `sudo tail -f /var/log/nexus-assistant/error.log`
- [ ] Set up billing alerts in Google Cloud Console
- [ ] Budget alert configured (e.g., $20/month)
- [ ] Email notifications enabled for budget alerts

---

## Post-Deployment

- [ ] Bookmarked VM external IP or domain
- [ ] Saved SSH connection details
- [ ] Documented all credentials securely
- [ ] Created backup of .env file (stored securely offline)
- [ ] Tested from multiple devices (mobile, desktop)
- [ ] Shared URL with team/community
- [ ] Monitored logs for first hour of operation

---

## Performance Check

After 24 hours of operation:

- [ ] Checked CPU usage: `htop`
- [ ] Checked memory usage: `free -h`
- [ ] Checked disk space: `df -h`
- [ ] Reviewed error logs for issues
- [ ] Confirmed no crashes or restarts
- [ ] Application responsive under load
- [ ] Gemini API working (no rate limit errors)

---

## Maintenance Schedule

Set reminders for:

- [ ] **Weekly:** Check error logs
- [ ] **Weekly:** Review resource usage (CPU, memory, disk)
- [ ] **Monthly:** Review billing (expected ~$15-20/month)
- [ ] **Monthly:** Check for application updates
- [ ] **Quarterly:** Review security updates
- [ ] **Quarterly:** Test backup/restore procedure

---

## Troubleshooting Reference

### If application won't start:

```bash
# Check service status
sudo systemctl status nexus-assistant

# View detailed logs
sudo journalctl -u nexus-assistant -n 100

# Check for errors in logs
sudo tail -f /var/log/nexus-assistant/error.log

# Verify .env file exists
cat ~/nexus-assistant/.env

# Restart service
sudo systemctl restart nexus-assistant
```

### If 502 Bad Gateway error:

```bash
# Check Gunicorn is running
ps aux | grep gunicorn

# Check port 8000 is listening
sudo netstat -tulpn | grep :8000

# Restart application
sudo systemctl restart nexus-assistant

# Restart Nginx
sudo systemctl restart nginx
```

### If high memory usage:

```bash
# Check memory
free -h

# Reduce Gunicorn workers
sudo nano /etc/systemd/system/nexus-assistant.service
# Change: --workers 3  →  --workers 2

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart nexus-assistant
```

---

## Success Criteria

Your deployment is successful when:

- ✅ Application accessible via external IP or domain
- ✅ All pages load without errors (home, browse, chat, quiz)
- ✅ Georgian text displays correctly
- ✅ AI chat responds to questions
- ✅ Quiz loads and records answers
- ✅ Services auto-start on VM reboot
- ✅ HTTPS enabled (if using domain)
- ✅ Logs are being written
- ✅ Monthly cost under $25
- ✅ No security vulnerabilities (firewall configured, updates enabled)

---

## Contact Information

**VM Details:**
- VM Name: `____________________`
- External IP: `____________________`
- Zone: `____________________`
- Domain (if any): `____________________`

**Access:**
- URL: `____________________`
- SSH: `gcloud compute ssh nexus-assistant-vm --zone=YOUR_ZONE`

**API Keys:**
- Gemini API Key: Stored in `.env` on server
- Location: `~/nexus-assistant/.env`

---

## Rollback Procedure

If something goes wrong:

1. **Stop the application:**
   ```bash
   sudo systemctl stop nexus-assistant
   sudo systemctl stop nginx
   ```

2. **Delete and recreate VM:**
   - Google Cloud Console → VM Instances
   - Select VM → DELETE
   - Start over from "Google Cloud VM Creation" section

3. **Restore from backup:**
   - If you backed up your application, re-upload to new VM
   - Run setup scripts again

---

## Completion

**Deployment completed on:** `____________________`

**Deployed by:** `____________________`

**Final URL:** `____________________`

**Notes:**
```
[Add any custom notes or changes you made]
```

---

Congratulations! Your Nexus Assistant is now live! 🎉
