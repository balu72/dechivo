# 📦 Production Knowledge Graph Data

## ⚠️ Large Files Not in Git

The production TTL files are **too large for GitHub** (129 MB exceeds 100 MB limit).

### **Required Files**

1. **`deduplicated_knowledge_graph.ttl`** (128.97 MB)
   - Unified KG from 4 frameworks (ESCO, O*NET, Singapore, Canada)
   - 1,726,471 triples
   - 6,372 unique occupations
   - 14,598+ skills

2. **`SFIA_9_2025-02-27.ttl`** (636 KB)
   - SFIA v9 IT professional competencies
   - ~10,000 triples
   - 180 skills with 7 levels each

---

## 📥 **How to Get the Files**

### **For Local Development**

If you already have the source data:

```bash
# From project root
cd knowledge-graph

# Run merge + deduplication
python3 scripts/merge_ttl.py
python3 scripts/deduplicate_entities.py

# Copy to fuseki-data
cp ../data/unified-files/deduplicated_knowledge_graph.ttl fuseki-data/
cp ../data/sfia_turtle/SFIA_9_2025-02-27.ttl fuseki-data/
```

### **For Production Deployment**

**Option A: Download from Cloud Storage**

```bash
# Upload files to your preferred storage:
# - Google Drive
# - Dropbox
# - AWS S3
# - Azure Blob Storage
# - Company file server

# During deployment, download:
cd knowledge-graph/fuseki-data/

# Example with wget (replace with your URL)
wget "YOUR_CLOUD_STORAGE_URL/deduplicated_knowledge_graph.ttl"
wget "YOUR_CLOUD_STORAGE_URL/SFIA_9_2025-02-27.ttl"
```

**Option B: Direct Transfer (SCP/RSYNC)**

```bash
# From local machine to production server
scp deduplicated_knowledge_graph.ttl user@server:/path/to/dechivo/knowledge-graph/fuseki-data/
scp SFIA_9_2025-02-27.ttl user@server:/path/to/dechivo/knowledge-graph/fuseki-data/
```

**Option C: Build on Production Server**

```bash
# Transfer source TTL files (7,929 files, ~500 MB)
# Then run merge/deduplication on the server
# (Requires more time and resources)
```

---

## ✅ **Verification**

After downloading, verify files:

```bash
cd knowledge-graph/fuseki-data/

# Check files exist
ls -lh *.ttl

# Expected output:
# -rw-r--r-- 1 user user 636K ... SFIA_9_2025-02-27.ttl
# -rw-r--r-- 1 user user 129M ... deduplicated_knowledge_graph.ttl

# Quick validation (optional)
head -20 deduplicated_knowledge_graph.ttl
# Should show RDF/Turtle syntax with prefixes
```

---

## 🚀 **Next Steps**

Once you have the files, proceed with Fuseki loading:

```bash
# Load into Fuseki
curl -X POST "http://localhost:3030/unified/data" \
  -H "Content-Type: text/turtle" \
  -u admin:admin123 \
  --data-binary @deduplicated_knowledge_graph.ttl

curl -X POST "http://localhost:3030/sfia/data" \
  -H "Content-Type: text/turtle" \
  -u admin:admin123 \
  --data-binary @SFIA_9_2025-02-27.ttl
```

See `../../KNOWLEDGE_GRAPH_DEPLOYMENT_PLAN.md` for complete deployment instructions.

---

## 📝 **File Locations**

- **Local development**: Generate from source using scripts
- **Production**: Download from cloud storage or transfer directly
- **Backup**: Keep copies in secure storage

---

**Note**: These files are excluded from git via `.gitignore` due to size limits.
Contact your team lead for access to the cloud storage location.
