# 🚀 Knowledge Graph Production Deployment Plan

**Date**: January 19, 2026  
**Version**: 1.0  
**Target**: Production Environment

---

## 📋 **Pre-Deployment Checklist**

### ✅ **1. Prerequisites**
- [ ] Production server access (SSH)
- [ ] Git access to repository
- [ ] Docker installed on production server
- [ ] Fuseki admin credentials
- [ ] Backend has .env with proper configuration
- [ ] Minimum 4 GB RAM available
- [ ] Minimum 500 MB disk space available

### ✅ **2. Data Verification**
```bash
# On local machine - verify production files exist
cd ~/Development/dechivo
ls -lh knowledge-graph/fuseki-data/

# Expected files:
# - deduplicated_knowledge_graph.ttl (129 MB)
# - SFIA_9_2025-02-27.ttl (636 KB)
```

### ✅ **3. Backup Current State**
- [ ] Backup current Fuseki datasets
- [ ] Backup current code
- [ ] Document rollback procedure

---

## 📦 **Phase 1: Prepare Deployment**

### **Step 1.1: Commit Production Files to Git**

```bash
# On local machine
cd ~/Development/dechivo

# Check git status
git status

# Add production TTL files
git add knowledge-graph/fuseki-data/*.ttl
git add knowledge-graph/README.md
git add .gitignore

# Commit
git commit -m "Add production KG data files for deployment

- deduplicated_knowledge_graph.ttl (unified KG, 1.73M triples)
- SFIA_9_2025-02-27.ttl (SFIA v9)
- Updated .gitignore to allow fuseki-data/*.ttl
- Updated README with deployment instructions"

# Push to repository
git push origin main
```

**Size Note**: The TTL files are large (129 MB + 636 KB). Git LFS is recommended but not required for initial deployment.

### **Step 1.2: Verify Git Push**

```bash
# Check that files are in repository
git log --stat -1

# Should show:
# knowledge-graph/fuseki-data/deduplicated_knowledge_graph.ttl
# knowledge-graph/fuseki-data/SFIA_9_2025-02-27.ttl
```

---

## 🔧 **Phase 2: Server Preparation**

### **Step 2.1: SSH into Production Server**

```bash
# SSH to production
ssh user@your-production-server.com

# Navigate to application directory
cd /var/www/dechivo  # or your app path
```

### **Step 2.2: Backup Current State**

```bash
# Backup current code
tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz \
  backend/ frontend/ knowledge-graph/

# Move backup to safe location
mv backup-*.tar.gz ~/backups/

# Backup Fuseki data (if already running)
docker exec fuseki tar -czf /fuseki/backup-datasets-$(date +%Y%m%d).tar.gz \
  /fuseki/databases/ 2>/dev/null || echo "No existing Fuseki data"
```

### **Step 2.3: Pull Latest Code**

```bash
# Stash any local changes
git stash

# Pull latest code
git pull origin main

# Verify code is up to date
git log -1
```

### **Step 2.4: Download Knowledge Graph Data Files**

⚠️ **Important**: The production TTL files are too large for GitHub (129 MB) and must be downloaded separately.

```bash
cd knowledge-graph/fuseki-data

# Option A: Download from Google Drive (RECOMMENDED)
# Download unified KG (129 MB - may take 2-3 minutes)
wget --no-check-certificate \
  'https://drive.google.com/uc?export=download&id=1oxStLcHUjqAmWbyXJW3IZXyvDVAQ4Xbg' \
  -O deduplicated_knowledge_graph.ttl

# Download SFIA (636 KB)
wget --no-check-certificate \
  'https://drive.google.com/uc?export=download&id=1pb-_QLdijI6N8LXhiXeceV5tQK1AMsty' \
  -O SFIA_9_2025-02-27.ttl

# Alternative: Using curl (if wget not available)
curl -L \
  'https://drive.google.com/uc?export=download&id=1oxStLcHUjqAmWbyXJW3IZXyvDVAQ4Xbg' \
  -o deduplicated_knowledge_graph.ttl

curl -L \
  'https://drive.google.com/uc?export=download&id=1pb-_QLdijI6N8LXhiXeceV5tQK1AMsty' \
  -o SFIA_9_2025-02-27.ttl

# Option B: Transfer from local machine via SCP
# From your local machine:
# scp knowledge-graph/fuseki-data/*.ttl user@server:/path/to/dechivo/knowledge-graph/fuseki-data/

# Option C: Download from secure file server
# curl -u user:pass "https://fileserver.com/kg-data.zip" -o kg-data.zip
# unzip kg-data.zip

# Verify files downloaded correctly
ls -lh *.ttl

# Expected output:
# -rw-r--r-- 1 user user 636K ... SFIA_9_2025-02-27.ttl
# -rw-r--r-- 1 user user 129M ... deduplicated_knowledge_graph.ttl

# Quick validation
head -10 deduplicated_knowledge_graph.ttl
# Should show RDF/Turtle syntax with @prefix declarations
```

**Cloud Storage Options:**
- Google Drive (shareable link)
- AWS S3 bucket
- Dropbox shared folder
- Azure Blob Storage
- Company file server

See `knowledge-graph/fuseki-data/README.md` for detailed instructions.

---

## 🐋 **Phase 3: Fuseki Deployment**

### **Step 3.1: Start/Verify Fuseki Container**

```bash
cd knowledge-graph

# Check if Fuseki is running
docker ps | grep fuseki

# If not running, start it
docker-compose up -d

# Check logs
docker logs fuseki

# Wait for startup (look for "Server started")
sleep 10

# Verify Fuseki is accessible
curl -u admin:admin123 http://localhost:3030/$/server

# Expected: JSON response with server info
```

### **Step 3.2: Delete Old Datasets (if exist)**

```bash
# List existing datasets
curl -u admin:admin123 http://localhost:3030/$/datasets

# Delete old datasets (if they exist)
curl -X DELETE -u admin:admin123 \
  "http://localhost:3030/$/datasets/ca" 2>/dev/null || true

curl -X DELETE -u admin:admin123 \
  "http://localhost:3030/$/datasets/esco" 2>/dev/null || true

curl -X DELETE -u admin:admin123 \
  "http://localhost:3030/$/datasets/onet" 2>/dev/null || true

curl -X DELETE -u admin:admin123 \
  "http://localhost:3030/$/datasets/sg" 2>/dev/null || true

curl -X DELETE -u admin:admin123 \
  "http://localhost:3030/$/datasets/dechivo" 2>/dev/null || true

echo "Old datasets removed"
```

### **Step 3.3: Create New Datasets**

```bash
# Create 'unified' dataset
curl -X POST -u admin:admin123 \
  "http://localhost:3030/$/datasets" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "dbName=unified&dbType=tdb2"

# Create 'sfia' dataset
curl -X POST -u admin:admin123 \
  "http://localhost:3030/$/datasets" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "dbName=sfia&dbType=tdb2"

# Verify datasets created
curl -u admin:admin123 http://localhost:3030/$/datasets
```

### **Step 3.4: Load Knowledge Graph Data**

This is the most time-consuming step (~3-5 minutes).

```bash
# Load unified KG (1.73M triples - takes ~3 minutes)
echo "Loading unified knowledge graph (this may take 3-5 minutes)..."
curl -X POST \
  "http://localhost:3030/unified/data" \
  -H "Content-Type: text/turtle" \
  -u admin:admin123 \
  --data-binary @fuseki-data/deduplicated_knowledge_graph.ttl

# Load SFIA KG (~10,000 triples - takes ~5 seconds)
echo "Loading SFIA knowledge graph..."
curl -X POST \
  "http://localhost:3030/sfia/data" \
  -H "Content-Type: text/turtle" \
  -u admin:admin123 \
  --data-binary @fuseki-data/SFIA_9_2025-02-27.ttl

echo "✅ Data loading complete!"
```

### **Step 3.5: Verify Data Loaded**

```bash
# Count triples in unified dataset
echo "Verifying unified dataset..."
curl -X POST "http://localhost:3030/unified/query" \
  -u admin:admin123 \
  -H "Content-Type: application/sparql-query" \
  --data 'SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }'

# Expected: ~1,726,471 triples

# Count triples in SFIA dataset
echo "Verifying SFIA dataset..."
curl -X POST "http://localhost:3030/sfia/query" \
  -u admin:admin123 \
  -H "Content-Type: application/sparql-query" \
  --data 'SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }'

# Expected: ~10,000 triples

# Test sample query
echo "Testing sample query..."
curl -X POST "http://localhost:3030/unified/query" \
  -u admin:admin123 \
  -H "Content-Type: application/sparql-query" \
  --data 'SELECT DISTINCT ?framework WHERE { 
    ?s <http://dechivo.com/ontology/fromFramework> ?framework 
  } LIMIT 10'

# Expected: Should return framework names (ESCO, O*NET, Singapore, Canada)
```

---

## ⚙️ **Phase 4: Backend Configuration**

### **Step 4.1: Update Environment Variables**

```bash
cd backend

# Verify .env file has correct Fuseki configuration
cat .env | grep FUSEKI

# Should have:
# FUSEKI_URL=http://localhost:3030
# FUSEKI_DATASET=unified  # Default dataset
# FUSEKI_USERNAME=admin
# FUSEKI_PASSWORD=admin123
```

### **Step 4.2: Install/Update Dependencies**

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify langchain packages are up to date
pip list | grep langchain
```

### **Step 4.3: Test Backend Connection**

```bash
# Test Python KG service
cd knowledge-graph
python3 -c "
from scripts.kg_service import kg_service
print('Testing KG connection...')
results = kg_service.search_occupations('developer')
print(f'✅ Found {len(results)} occupations')
"

# Expected: Should find occupations

# Test SFIA service
cd ../backend
python3 -c "
from services.sfia_km_service import get_sfia_service
sfia = get_sfia_service()
print('Testing SFIA connection...')
print(f'✅ Connected: {sfia.is_connected()}')
"

# Expected: ✅ Connected: True
```

---

## 🌐 **Phase 5: Service Restart**

### **Step 5.1: Restart Backend**

```bash
cd backend

# If using systemd
sudo systemctl restart dechivo-backend

# If using supervisor
sudo supervisorctl restart dechivo-backend

# If using pm2
pm2 restart dechivo-backend

# If running manually (development)
# Ctrl+C to stop, then:
python3 app.py
```

### **Step 5.2: Restart Frontend (if needed)**

```bash
cd frontend

# Rebuild production bundle
npm run build

# If using nginx, restart it
sudo systemctl restart nginx

# If using pm2
pm2 restart dechivo-frontend
```

---

## ✅ **Phase 6: Testing & Verification**

### **Step 6.1: API Health Checks**

```bash
# Test KG health endpoint
curl "http://your-domain.com/api/kg/health"

# Expected: {"status": "healthy", ...}

# Test occupation search
curl "http://your-domain.com/api/kg/occupations/search?q=developer"

# Expected: JSON with occupations

# Test skills search (requires auth)
curl "http://your-domain.com/api/search-skills?query=python" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected: Skills from all 3 sources (common, kg, sfia)
```

### **Step 6.2: Frontend Testing**

```bash
# Open browser to production URL
# http://your-domain.com

# Manual tests:
1. Login to application
2. Go to Create JD page
3. Type "python" in Primary Skills
   - Should see autocomplete suggestions
   - Should see skills from multiple sources
4. Type same skill in Secondary Skills
   - Should NOT see the skill you selected in Primary
5. Create a test JD
   - Should succeed with skills from KG
```

### **Step 6.3: Performance Check**

```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s \
  "http://your-domain.com/api/kg/occupations/search?q=developer"

# Create curl-format.txt with:
# time_total: %{time_total}s

# Expected: < 1 second

# Check Fuseki memory usage
docker stats fuseki --no-stream

# Expected: < 2 GB RAM usage
```

---

## 🔄 **Phase 7: Monitoring**

### **Step 7.1: Check Logs**

```bash
# Backend logs
tail -f /var/log/dechivo/backend.log

# Fuseki logs
docker logs -f fuseki

# Nginx logs (if applicable)
tail -f /var/log/nginx/access.log
```

### **Step 7.2: Monitor Metrics**

```bash
# Check dataset sizes
curl -u admin:admin123 "http://localhost:3030/$/stats/unified"

# Check query performance
# Run several test queries and measure time

# Check system resources
htop
df -h
```

---

## 🚨 **Phase 8: Rollback Plan (if needed)**

If something goes wrong, follow this rollback procedure:

### **Step 8.1: Restore Code**

```bash
cd /var/www/dechivo

# Restore from backup
tar -xzf ~/backups/backup-YYYYMMDD-HHMMSS.tar.gz
```

### **Step 8.2: Restore Fuseki Data**

```bash
# Stop Fuseki
docker-compose down

# Restore databases
docker run --rm -v fuseki-data:/data \
  -v ~/backups:/backup ubuntu \
  tar -xzf /backup/backup-datasets-YYYYMMDD.tar.gz -C /

# Restart Fuseki
docker-compose up -d
```

### **Step 8.3: Restart Services**

```bash
# Restart backend
sudo systemctl restart dechivo-backend

# Restart frontend
sudo systemctl restart nginx
```

---

## 📊 **Post-Deployment Checklist**

After successful deployment:

- [ ] ✅ Fuseki running with 2 datasets (unified, sfia)
- [ ] ✅ Unified dataset has 1.73M triples
- [ ] ✅ SFIA dataset has ~10K triples
- [ ] ✅ Backend can query both datasets
- [ ] ✅ API endpoints return correct data
- [ ] ✅ Frontend skills autocomplete works
- [ ] ✅ Primary/Secondary skills filtering works
- [ ] ✅ JD creation uses KG data
- [ ] ✅ Response times acceptable (< 1s)
- [ ] ✅ No errors in logs
- [ ] ✅ Backups created and stored safely

---

## 📝 **Documentation Updates**

After deployment, update:

1. **Deployment log**
   ```bash
   echo "$(date): Deployed KG v1.0 - 1.73M triples" >> DEPLOYMENT_LOG.md
   ```

2. **Version tracking**
   - Unified KG: v1.0 (Jan 19, 2026)
   - SFIA: v9 (Feb 27, 2025)
   - Frameworks: 4 (ESCO, O*NET, Singapore, Canada)

3. **Team notification**
   - Send email/slack about new KG deployment
   - Document any breaking changes
   - Share API endpoint updates

---

## ⏱️ **Estimated Timeline**

| Phase | Duration | Downtime? |
|-------|----------|-----------|
| 1. Prepare | 15 min | No |
| 2. Server prep | 10 min | No |
| 3. Fuseki setup | 5 min | Yes |
| 4. Backend config | 5 min | No |
| 5. Service restart | 2 min | Yes |
| 6. Testing | 15 min | No |
| 7. Monitoring | Ongoing | No |
| **Total** | **~50 min** | **~7 min** |

**Recommended**: Schedule during low-traffic period (e.g., 2-4 AM local time)

---

## 🎯 **Success Criteria**

Deployment is successful if:

✅ No errors during data loading  
✅ Correct triple counts verified  
✅ All API endpoints return 200 OK  
✅ Frontend autocomplete shows results from all sources  
✅ JD creation works end-to-end  
✅ Response times < 500ms for queries  
✅ System resources within normal ranges  
✅ Zero errors in logs after 1 hour  

---

## 📞 **Support**

### **Troubleshooting**

**Issue**: Fuseki won't start
```bash
# Check Docker logs
docker logs fuseki

# Check port availability
netstat -tulpn | grep 3030

# Restart Docker
sudo systemctl restart docker
docker-compose up -d
```

**Issue**: Data loading timeout
```bash
# Increase timeout in curl
curl --max-time 600 ...  # 10 minutes

# Or use chunked loading
split -l 100000 deduplicated_knowledge_graph.ttl chunk_
for file in chunk_*; do
  curl -X POST ... --data-binary @$file
done
```

**Issue**: Backend can't connect to Fuseki
```bash
# Check Fuseki is accessible
curl http://localhost:3030/$/server

# Check firewall
sudo ufw status

# Check .env file
cat backend/.env | grep FUSEKI
```

### **Emergency Contacts**

- DevOps: [contact]
- Backend Lead: [contact]
- Database Admin: [contact]

---

## 🔐 **Security Notes**

- ✅ Change default Fuseki password (`admin:admin123`)
- ✅ Use HTTPS for production API
- ✅ Enable Fuseki authentication
- ✅ Firewall Fuseki port (3030) - internal only
- ✅ Regular security updates for Docker/Python
- ✅ Monitor access logs for suspicious queries

---

**Prepared by**: Dechivo DevOps Team  
**Date**: January 19, 2026  
**Version**: 1.0  
**Status**: Ready for Production Deployment 🚀
