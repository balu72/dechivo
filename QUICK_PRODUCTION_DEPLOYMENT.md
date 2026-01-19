# 🚀 Quick Production Deployment Guide - VPSDime

**Target**: VPSDime Split Architecture (2 VPS servers)  
**Time Required**: ~15 minutes  
**Downtime**: ~5 minutes

---

## 📋 **Pre-Deployment**

✅ Code is in GitHub with Google Drive links  
✅ Production TTL files uploaded to Google Drive  
✅ VPSDime servers accessible via SSH  

---

## 🎯 **Quick Deployment Steps**

### **1. Deploy Code to Both Servers**

Use your existing `/deploy-vpsdime` workflow:

```bash
# This will deploy to both VPS servers
# Follow the workflow prompts
```

### **2. Download Knowledge Graph Data (VPS1 - Backend Server)**

SSH to your backend server and download KG files:

```bash
# SSH to backend VPS
ssh user@backend-vps-ip

# Navigate to app directory
cd /path/to/dechivo/knowledge-graph/fuseki-data

# Download KG files from Google Drive (~2-3 minutes)
wget --no-check-certificate \
  'https://drive.google.com/uc?export=download&id=1oxStLcHUjqAmWbyXJW3IZXyvDVAQ4Xbg' \
  -O deduplicated_knowledge_graph.ttl

wget --no-check-certificate \
  'https://drive.google.com/uc?export=download&id=1pb-_QLdijI6N8LXhiXeceV5tQK1AMsty' \
  -O SFIA_9_2025-02-27.ttl

# Verify download
ls -lh *.ttl
# Should show:
# -rw-r--r-- 1 user user 636K ... SFIA_9_2025-02-27.ttl
# -rw-r--r-- 1 user user 129M ... deduplicated_knowledge_graph.ttl
```

### **3. Start Fuseki (if not running)**

```bash
cd /path/to/dechivo/knowledge-graph

# Start Fuseki container
docker-compose up -d

# Wait for startup (~10 seconds)
sleep 10

# Verify it's running
docker ps | grep fuseki

# Check logs
docker logs fuseki
# Should show "Server started"
```

### **4. Load Knowledge Graph Data**

```bash
cd /path/to/dechivo/knowledge-graph

# Create datasets
curl -X POST -u admin:admin123 \
  "http://localhost:3030/$/datasets" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "dbName=unified&dbType=tdb2"

curl -X POST -u admin:admin123 \
  "http://localhost:3030/$/datasets" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "dbName=sfia&dbType=tdb2"

# Load unified KG (~3 minutes for 1.73M triples)
echo "Loading unified KG (this takes ~3 minutes)..."
curl -X POST "http://localhost:3030/unified/data" \
  -H "Content-Type: text/turtle" \
  -u admin:admin123 \
  --data-binary @fuseki-data/deduplicated_knowledge_graph.ttl

# Load SFIA (~5 seconds)
echo "Loading SFIA..."
curl -X POST "http://localhost:3030/sfia/data" \
  -H "Content-Type: text/turtle" \
  -u admin:admin123 \
  --data-binary @fuseki-data/SFIA_9_2025-02-27.ttl

echo "✅ KG data loaded!"
```

### **5. Verify KG is Loaded**

```bash
# Count triples in unified dataset
curl -X POST "http://localhost:3030/unified/query" \
  -u admin:admin123 \
  -H "Content-Type: application/sparql-query" \
  --data 'SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }'

# Expected: ~1,726,471

# Test sample query
curl "http://localhost:5000/api/kg/health"
# Expected: {"status": "healthy", ...}
```

### **6. Restart Backend Application**

```bash
# Using systemd
sudo systemctl restart dechivo-backend

# OR using pm2
pm2 restart dechivo-backend

# Check logs
pm2 logs dechivo-backend
# Should show: "✅ OpenAI LLM initialized"
```

### **7. Test Frontend**

Open your production URL in browser:
```
https://your-domain.com
```

**Test checklist**:
- [ ] Login works
- [ ] Go to Create JD page
- [ ] Type "python" in Primary Skills → sees autocomplete
- [ ] Type "python" in Secondary Skills → NOT seeing selected primary skills
- [ ] Create a test JD → succeeds

---

## ⚡ **Quick Reference**

### **Check if Fuseki is Running**
```bash
docker ps | grep fuseki
curl -u admin:admin123 http://localhost:3030/$/server
```

### **Check Backend Status**
```bash
systemctl status dechivo-backend
# or
pm2 status
```

### **View Logs**
```bash
# Backend
pm2 logs dechivo-backend

# Fuseki
docker logs fuseki

# Nginx (if applicable)
tail -f /var/log/nginx/access.log
```

### **Test API Endpoints**
```bash
# KG Health
curl https://your-domain.com/api/kg/health

# Search skills
curl "https://your-domain.com/api/search-skills?query=python" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Should return skills from 3 sources (common, kg, sfia)
```

---

## 🔧 **Troubleshooting**

### **Issue**: Can't download files from Google Drive

**Solution**: Files too large, use alternative:
```bash
# From your local machine, transfer via SCP
scp knowledge-graph/fuseki-data/*.ttl \
  user@backend-vps:/path/to/dechivo/knowledge-graph/fuseki-data/
```

### **Issue**: Fuseki port 3030 not accessible

**Solution**: Update firewall
```bash
# Allow internal access only
sudo ufw allow from backend-ip to any port 3030
```

### **Issue**: Backend can't connect to Fuseki

**Solution**: Check .env configuration
```bash
cd backend
cat .env | grep FUSEKI

# Should have:
# FUSEKI_URL=http://localhost:3030
# FUSEKI_DATASET=unified
# FUSEKI_USERNAME=admin
# FUSEKI_PASSWORD=admin123
```

### **Issue**: Skills autocomplete not working

**Solution**: Verify KG endpoints
```bash
# Test unified endpoint
curl -X POST "http://localhost:3030/unified/query" \
  -u admin:admin123 \
  -H "Content-Type: application/sparql-query" \
  --data 'SELECT * WHERE { ?s ?p ?o } LIMIT 1'

# Should return RDF data
```

---

## 📊 **Expected Results**

After successful deployment:

✅ **Fuseki**: Running on port 3030  
✅ **Datasets**: 2 (unified, sfia)  
✅ **Triples**: 1.73M in unified, 10K in sfia  
✅ **API**: All `/api/kg/*` endpoints returning 200  
✅ **Frontend**: Skills autocomplete showing 15,000+ skills  
✅ **Performance**: Query responses < 500ms  

---

## 📝 **Deployment Checklist**

- [ ] Code deployed via `/deploy-vpsdime`
- [ ] KG files downloaded to backend server
- [ ] Fuseki running
- [ ] Datasets created (unified, sfia)
- [ ] Data loaded successfully
- [ ] Triple counts verified
- [ ] Backend restarted
- [ ] API health check passes
- [ ] Frontend skills autocomplete works
- [ ] Test JD creation succeeds

---

## 🎉 **Success!**

Your Knowledge Graph is now live in production with:
- 🌍 **15,000+ skills** from 5 global frameworks
- 📊 **1.73M triples** of occupational data
- 🚀 **Real-time autocomplete** with smart filtering
- 🎯 **Primary/Secondary skills** separation

---

**For detailed troubleshooting**: See `KNOWLEDGE_GRAPH_DEPLOYMENT_PLAN.md`  
**For workflow details**: Use `/deploy-vpsdime` command

**Production is ready!** 🚀
