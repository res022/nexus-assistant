# 🚀 START HERE - Nexus Assistant Deployment

Welcome! This guide will help you deploy Nexus Assistant to Google Cloud in just 5 minutes.

---

## 📚 Quick Navigation

### New to deployment? Start here:
1. **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** ← Read this first! (5-minute guide)
2. **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** ← Track your progress

### Want detailed instructions?
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete 30-minute manual guide
- **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** - Overview of everything

### For automation:
- **[deploy/](deploy/)** - Contains 5 automated scripts
- **[deploy/README.md](deploy/README.md)** - Scripts documentation

---

## ⚡ Super Quick Start (5 Minutes)

**You need:**
- Google Cloud account with $300 credit
- Gemini API key: `AIzaSyCGfeY_Q1emufh5xs0qp-DMOf4tX-khaKQ`

**Steps:**

### 1. Create VM (2 min)
Go to: https://console.cloud.google.com/compute/instances

Click "CREATE INSTANCE" and configure:
- **Name:** `nexus-assistant-vm`
- **Machine:** `e2-small` (2 vCPU, 2 GB RAM)
- **Disk:** Ubuntu 22.04 LTS, 20 GB
- **Firewall:** ✅ Allow HTTP, ✅ Allow HTTPS

Click "CREATE"

### 2. Upload App (1 min)
From Windows PowerShell:
```powershell
cd "C:\Users\mrluk\Desktop"
gcloud compute scp --recurse "nexus assistant" nexus-assistant-vm:~/ --zone=YOUR_ZONE
```

### 3. Run Setup (2 min)
SSH into VM (click "SSH" button), then:
```bash
cd ~/nexus-assistant/deploy
chmod +x *.sh
bash setup_vm.sh
bash install_app.sh
```

**When prompted, edit .env with your API key!**

### 4. Access Your Site
Get IP: `curl ifconfig.me`

Visit: `http://YOUR_EXTERNAL_IP`

**Done! 🎉**

---

## 💰 Costs

- **VM (e2-small):** ~$12-15/month
- **Network:** ~$2-5/month
- **Gemini API:** ~$1-3/month

**Total: $15-23/month**

Your $300 credit = **12-20 months free** 🎁

---

## 📖 Detailed Documentation

| Document | Purpose | Time | When to Use |
|----------|---------|------|-------------|
| **QUICK_DEPLOY.md** | Fast deployment | 5 min | First time, want it running ASAP |
| **DEPLOYMENT_GUIDE.md** | Detailed manual | 30 min | Want to understand each step |
| **DEPLOYMENT_CHECKLIST.md** | Track progress | N/A | During deployment |
| **DEPLOYMENT_SUMMARY.md** | Overview | 5 min read | Want to see what's included |
| **deploy/README.md** | Scripts guide | 5 min read | Using automated scripts |

---

## 🛠️ What's Included

### Documentation (5 files)
- ✅ Quick start guide (5 minutes)
- ✅ Detailed manual (30 minutes)
- ✅ Interactive checklist
- ✅ Complete summary
- ✅ This file (START_HERE.md)

### Automation Scripts (5 files)
- ✅ `setup_vm.sh` - Install system packages
- ✅ `install_app.sh` - Deploy application
- ✅ `update_app.sh` - Update after changes
- ✅ `setup_ssl.sh` - Add HTTPS
- ✅ Scripts README

### Configuration
- ✅ `.gitignore` - Prevent committing secrets
- ✅ `.env` - Environment variables (add your API key here)

---

## 🎯 VM Specifications

Perfect balance of cost and performance:

```
Type:      e2-small
CPU:       2 vCPU
RAM:       2 GB
Disk:      20 GB
OS:        Ubuntu 22.04 LTS
Cost:      ~$15/month

Handles:   50-100 concurrent users
Perfect for: Small to medium communities
```

---

## 🔐 Security Included

- ✅ Firewall configured (UFW)
- ✅ Fail2ban (brute force protection)
- ✅ Automatic security updates
- ✅ SSL/TLS ready (optional)
- ✅ Non-root user operation
- ✅ Secure file permissions

---

## ⚠️ Important Notes

### Before You Start:

1. **Get Gemini API Key** (you already have it):
   - `AIzaSyCGfeY_Q1emufh5xs0qp-DMOf4tX-khaKQ`

2. **Activate $300 Google Cloud Credit:**
   - Go to: https://console.cloud.google.com/billing
   - Follow activation steps

3. **Install Google Cloud SDK** (for gcloud commands):
   - Windows: https://cloud.google.com/sdk/docs/install

### During Deployment:

- **DON'T SKIP** editing the `.env` file with your API key
- **DO TEST** the application after deployment
- **DO MONITOR** logs for first hour of operation

### After Deployment:

- **Bookmark** your external IP or domain
- **Set up** billing alerts ($20-25/month threshold)
- **Check** logs regularly: `sudo tail -f /var/log/nexus-assistant/error.log`

---

## 🆘 Getting Help

### Something not working?

1. **Check logs:**
   ```bash
   sudo tail -f /var/log/nexus-assistant/error.log
   ```

2. **Check service status:**
   ```bash
   sudo systemctl status nexus-assistant
   ```

3. **Common fixes:**
   - 502 error → `sudo systemctl restart nexus-assistant`
   - Can't access → Check firewall: `sudo ufw status`
   - Georgian text ??? → `sudo locale-gen ka_GE.UTF-8`

### Still stuck?

See **Troubleshooting** section in:
- `DEPLOYMENT_GUIDE.md` (Part 10)
- `DEPLOYMENT_SUMMARY.md` (Quick Reference table)

---

## 📋 Recommended Path

**For first-time deployers:**

1. ✅ Read this file (START_HERE.md) ← You are here!
2. ✅ Open `DEPLOYMENT_CHECKLIST.md` to track progress
3. ✅ Follow `QUICK_DEPLOY.md` for fast deployment
4. ✅ Check boxes in checklist as you go
5. ✅ Test your deployment
6. ✅ Set up monitoring and alerts

**For experienced users:**

1. ✅ Scan `DEPLOYMENT_SUMMARY.md` for overview
2. ✅ Run `deploy/setup_vm.sh` and `deploy/install_app.sh`
3. ✅ Done!

---

## 🎓 What You'll Learn

By deploying this application, you'll gain experience with:

- ✅ Google Cloud Platform (VM creation, billing)
- ✅ Linux server administration (Ubuntu)
- ✅ Web server configuration (Nginx)
- ✅ Python web applications (Flask, Gunicorn)
- ✅ Firewall configuration (UFW)
- ✅ SSL/TLS certificates (Let's Encrypt)
- ✅ Systemd services (auto-start on boot)
- ✅ Production deployment best practices

---

## ✨ Features of Your Deployed App

Once deployed, users can:

- 🔍 **Browse 38 Georgian Laws** with English summaries
- 💬 **Chat with AI Assistant** about legal questions in Georgian
- 📝 **Take Quizzes** from 1,012 AI-generated questions
- 📊 **Track Progress** with statistics and performance metrics
- 📱 **Use on Any Device** (responsive design)

---

## 🎉 Ready to Deploy?

Choose your path:

### Option 1: Fast (Recommended)
👉 Open **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** and follow the 5-minute guide

### Option 2: Detailed
👉 Open **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** for step-by-step instructions

### Option 3: Checklist-Driven
👉 Open **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** and check off items as you go

---

## 📞 Support

**Documentation:**
- All guides included in this package
- Check `README.md` for application details
- See `CLAUDE.md` for development info

**Google Cloud:**
- Console: https://console.cloud.google.com
- Docs: https://cloud.google.com/docs

**Gemini API:**
- Console: https://aistudio.google.com/apikey
- Docs: https://ai.google.dev/docs

---

## 🏁 Success Checklist

You're done when:

- ✅ Application loads at http://YOUR_EXTERNAL_IP
- ✅ Home page shows 38 laws
- ✅ Georgian text displays correctly
- ✅ AI chat responds to questions
- ✅ Quiz has 1,012+ questions
- ✅ Services auto-start on reboot
- ✅ (Optional) HTTPS enabled with domain

---

**Let's get started! Open QUICK_DEPLOY.md now →**

Made with ❤️ for San Andreas Roleplay Server
