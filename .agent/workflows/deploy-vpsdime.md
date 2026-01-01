---
description: Deploy Dechivo to VPSDime with Split Architecture (2 VPS servers)
---

# 🚀 Dechivo VPSDime Deployment Guide

## Architecture Overview

This deployment uses a **Single VPS + OpenAI API** for cost-effective hosting:

| Component | Location | Cost |
|-----------|----------|------|
| **Frontend (React)** | VPS 1 (Nginx) | ~$7/month |
| **Backend (Flask)** | VPS 1 (Gunicorn) | included |
| **Knowledge Graph (Fuseki)** | VPS 1 (Docker) | included |
| **LLM** | OpenAI API | ~$1-25/month |
| **Total** | | **~$8-32/month** |

---

## 📋 Prerequisites

Before starting:
- [ ] VPSDime account created
- [ ] OpenAI API key from [platform.openai.com](https://platform.openai.com)
- [ ] Domain name (optional but recommended)
- [ ] SSH key pair generated locally
- [ ] Git repository with Dechivo code pushed

---

## 🖥️ PART 1: Purchase VPS from VPSDime

1. Go to [vpsdime.com](https://vpsdime.com)
2. Select **Premium VPS** - 4GB RAM, 2 vCPU, 40GB SSD (~$7/month)
3. Choose **Ubuntu 22.04 LTS** as the OS
4. Select location closest to your users
5. Complete purchase and note the IP address

---

## 🔧 PART 2: Initial Server Setup

// turbo-all

### 2.1 SSH into your VPS

```bash
ssh root@YOUR_VPS_IP
```

### 2.2 Update System

```bash
apt update && apt upgrade -y
```

### 2.3 Create Non-Root User

```bash
# Create user
adduser dechivo
usermod -aG sudo dechivo

# Setup SSH key for new user
mkdir -p /home/dechivo/.ssh
cp ~/.ssh/authorized_keys /home/dechivo/.ssh/
chown -R dechivo:dechivo /home/dechivo/.ssh
chmod 700 /home/dechivo/.ssh
chmod 600 /home/dechivo/.ssh/authorized_keys
```

### 2.4 Exit and Re-login as dechivo

```bash
exit
ssh dechivo@YOUR_VPS_IP
```

---

## 📦 PART 3: Install Required Software

### 3.1 Install Docker

```bash
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker dechivo

# Re-login to apply docker group
exit
ssh dechivo@YOUR_VPS_IP
```

### 3.2 Install Nginx

```bash
sudo apt install -y nginx
sudo systemctl enable nginx
```

### 3.3 Install Certbot (SSL)

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 3.4 Install Node.js 20.x

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### 3.5 Install Python 3.11

```bash
sudo apt install -y python3.11 python3.11-venv python3-pip git
```

---

## 📂 PART 4: Deploy Application

### 4.1 Clone Repository

```bash
sudo mkdir -p /opt/dechivo
sudo chown dechivo:dechivo /opt/dechivo
cd /opt/dechivo

# Clone your repository
git clone YOUR_REPO_URL .
```

---

## 🗃️ PART 5: Deploy Fuseki (Knowledge Graph)

### 5.1 Start Fuseki Container

```bash
cd /opt/dechivo/knowledge-graph
docker-compose up -d
```

### 5.2 Wait for Fuseki to Start (~30 seconds)

```bash
sleep 30
```

### 5.3 Create SFIA Dataset

```bash
curl -X POST "http://localhost:3030/$/datasets" \
  -u admin:admin123 \
  -d "dbType=mem&dbName=sfia"
```

### 5.4 Load SFIA Data

```bash
curl -X POST "http://localhost:3030/sfia/data" \
  -H "Content-Type: text/turtle" \
  -u admin:admin123 \
  --data-binary @../data/SFIA_9_2025-02-27.ttl
```

### 5.5 Verify Data Loaded

```bash
curl "http://localhost:3030/sfia/query" \
  -u admin:admin123 \
  --data-urlencode "query=SELECT (COUNT(*) AS ?count) WHERE { ?s a <http://sfia-online.org/ontology#Skill> }"
```

Expected output should show ~147 skills.

---

## 🐍 PART 6: Deploy Backend (Flask + Gunicorn)

### 6.1 Create Virtual Environment

```bash
cd /opt/dechivo/backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

### 6.2 Create Production Environment File

```bash
cat > /opt/dechivo/backend/.env << 'EOF'
# Flask Configuration
SECRET_KEY=REPLACE_WITH_GENERATED_KEY
JWT_SECRET_KEY=REPLACE_WITH_GENERATED_JWT_KEY
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000

# OpenAI LLM (REQUIRED)
OPENAI_API_KEY=REPLACE_WITH_YOUR_OPENAI_API_KEY
OPENAI_MODEL=gpt-4o-mini

# Fuseki Knowledge Graph
FUSEKI_URL=http://localhost:3030
FUSEKI_DATASET=sfia
FUSEKI_USERNAME=admin
FUSEKI_PASSWORD=admin123
KG_ENABLED=true
KG_TIMEOUT=10
EOF
```

### 6.3 Generate Secret Keys

Run these commands and copy the output to your `.env` file:

```bash
python3 -c "import secrets; print('SECRET_KEY:', secrets.token_hex(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY:', secrets.token_hex(64))"
```

Then edit the `.env` file:
```bash
nano /opt/dechivo/backend/.env
```

### 6.4 Initialize Database

```bash
cd /opt/dechivo/backend
source venv/bin/activate
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
deactivate
```

### 6.5 Create Systemd Service

```bash
sudo tee /etc/systemd/system/dechivo-backend.service > /dev/null << 'EOF'
[Unit]
Description=Dechivo Backend API (Flask + Gunicorn)
After=network.target docker.service

[Service]
User=dechivo
Group=dechivo
WorkingDirectory=/opt/dechivo/backend
Environment="PATH=/opt/dechivo/backend/venv/bin"
EnvironmentFile=/opt/dechivo/backend/.env
ExecStart=/opt/dechivo/backend/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:5000 \
    --timeout 300 \
    --access-logfile /var/log/dechivo/access.log \
    --error-logfile /var/log/dechivo/error.log \
    app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

### 6.6 Create Log Directory and Start Service

```bash
sudo mkdir -p /var/log/dechivo
sudo chown dechivo:dechivo /var/log/dechivo

sudo systemctl daemon-reload
sudo systemctl enable dechivo-backend
sudo systemctl start dechivo-backend
```

### 6.7 Check Backend Status

```bash
sudo systemctl status dechivo-backend
curl http://localhost:5000/api/health
```

---

## ⚛️ PART 7: Deploy Frontend (React)

### 7.1 Build Frontend

```bash
cd /opt/dechivo/frontend
npm install
npm run build
```

### 7.2 Copy Build to Nginx Directory

```bash
sudo mkdir -p /var/www/dechivo
sudo cp -r dist/* /var/www/dechivo/
sudo chown -R www-data:www-data /var/www/dechivo
```

---

## 🌐 PART 8: Configure Nginx

### 8.1 Create Nginx Configuration

**Option A: With Domain**

```bash
sudo tee /etc/nginx/sites-available/dechivo > /dev/null << 'EOF'
server {
    listen 80;
    server_name YOUR_DOMAIN.com www.YOUR_DOMAIN.com;

    root /var/www/dechivo;
    index index.html;

    # React Router - serve index.html for all routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
EOF
```

**Option B: IP Only (no domain)**

```bash
sudo tee /etc/nginx/sites-available/dechivo > /dev/null << 'EOF'
server {
    listen 80 default_server;
    server_name _;

    root /var/www/dechivo;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
EOF
```

### 8.2 Enable Site

```bash
sudo ln -sf /etc/nginx/sites-available/dechivo /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔒 PART 9: Setup SSL (If Using Domain)

```bash
sudo certbot --nginx -d YOUR_DOMAIN.com -d www.YOUR_DOMAIN.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

---

## 🛡️ PART 10: Configure Firewall

```bash
sudo apt install -y ufw

sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

sudo ufw enable
sudo ufw status
```

---

## ✅ PART 11: Verification

### 11.1 Test All Components

```bash
# Test Fuseki
curl http://localhost:3030/sfia/query \
  -u admin:admin123 \
  --data-urlencode "query=SELECT * WHERE { ?s ?p ?o } LIMIT 1"

# Test Backend health
curl http://localhost:5000/api/health

# Test Knowledge Graph health
curl http://localhost:5000/api/health/kg

# Test via Nginx
curl http://YOUR_VPS_IP/api/health
```

### 11.2 Test Full Workflow

1. Open browser to `http://YOUR_VPS_IP` (or `https://YOUR_DOMAIN.com`)
2. Register a new user
3. Login
4. Paste a job description
5. Click "Enhance" and verify it completes

---

## 🔧 Maintenance Commands

### View Logs

```bash
# Backend logs
sudo journalctl -u dechivo-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Fuseki logs
docker logs -f sfia-fuseki
```

### Restart Services

```bash
sudo systemctl restart dechivo-backend
sudo systemctl restart nginx
cd /opt/dechivo/knowledge-graph && docker-compose restart
```

### Update Application

```bash
cd /opt/dechivo
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart dechivo-backend

# Rebuild frontend
cd ../frontend
npm install
npm run build
sudo cp -r dist/* /var/www/dechivo/
```

### Backup Database

```bash
mkdir -p /opt/dechivo/backups
cp /opt/dechivo/backend/dechivo.db /opt/dechivo/backups/dechivo-$(date +%Y%m%d).db
```

---

## 💡 Cost Summary

| Component | Monthly Cost |
|-----------|--------------|
| VPSDime VPS (4GB RAM) | ~$7.00 |
| OpenAI API (GPT-4o Mini, ~500 req) | ~$1.00 |
| OpenAI API (GPT-4o, ~500 req) | ~$12.50 |
| Domain (optional) | ~$1.00 |
| **Total (Budget)** | **~$8-9/month** |
| **Total (Quality)** | **~$20/month** |

---

## 🆘 Troubleshooting

### OpenAI API Issues

```bash
# Check if API key is set
grep OPENAI_API_KEY /opt/dechivo/backend/.env

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Backend Not Starting

```bash
sudo journalctl -u dechivo-backend --no-pager -n 100
```

### Fuseki Not Responding

```bash
docker ps
docker logs sfia-fuseki
docker-compose -f /opt/dechivo/knowledge-graph/docker-compose.yml restart
```

### Frontend Blank Page

```bash
ls -la /var/www/dechivo/
sudo tail -f /var/log/nginx/error.log
```
