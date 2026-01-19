# Data Files - Download Instructions

This directory contains large data files that are **not included in Git** to keep the repository size manageable.

## 📁 Required Data Files

The following directories are needed but excluded from Git:

```
data/
├── ca_turtle/           (21 files, Canada OASIS)
├── esco_turtle/         (2,936 files, ESCO)
├── onet_turtle/         (915 files, O*NET)
├── sg_turtle/           (4,057 files, Singapore)
└── unified-files/       (Generated files)
    └── deduplicated_knowledge_graph.ttl  (129 MB - Production file)
```

**Total Source Files**: 7,929 TTL files (~500 MB)  
**Generated File**: 1 deduplicated TTL file (129 MB)

## 🚀 How to Set Up Data

### Option 1: Generate from Source (Recommended)

If you have the source TTL files:

```bash
# 1. Place source files in data/
data/
├── ca_turtle/
├── esco_turtle/
├── onet_turtle/
└── sg_turtle/

# 2. Run the merge script
cd knowledge-graph
python3 scripts/merge_ttl.py ../data

# 3. Run deduplication
python3 scripts/deduplicate_entities.py

# 4. Load into Fuseki
python3 scripts/replace_fuseki_datasets.py
```

**Time**: ~5 minutes

### Option 2: Download Pre-built (Fastest)

If available, download the pre-built deduplicated file:

```bash
# Download deduplicated_knowledge_graph.ttl to data/unified-files/
# (Contact your team for the file)

# Then load into Fuseki
cd knowledge-graph
python3 scripts/replace_fuseki_datasets.py
```

**Time**: ~2 minutes (just loading)

### Option 3: Request from Team

Contact the development team to get:
- Access to source TTL files
- Pre-built `deduplicated_knowledge_graph.ttl`
- Backup Fuseki database

## 📊 Data Statistics

| Source | Files | Triples | Size |
|--------|-------|---------|------|
| Canada | 21 | 657,418 | ~40 MB |
| ESCO | 2,936 | 210,347 | ~20 MB |
| O*NET | 915 | 38,167 | ~5 MB |
| Singapore | 4,057 | 886,234 | ~65 MB |
| **Total Source** | **7,929** | **1,792,228** | **~130 MB** |
| **Deduplicated** | **1** | **1,726,471** | **129 MB** |

## ✅ Verification

After setup, verify the data is loaded:

```bash
# Check Fuseki
curl -u admin:admin123 \
  "http://localhost:3030/$/datasets"

# Count triples
curl -X POST "http://localhost:3030/unified/query" \
  -u admin:admin123 \
  -H "Content-Type: application/sparql-query" \
  --data 'SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }'

# Expected: 1,726,471 triples
```

## 🔐 Important Notes

- **TTL files are in .gitignore** - They will never be committed to Git
- **Total excluded**: ~630 MB (source + generated + duplicates)
- **Source data**: Keep for regeneration if needed
- **Production file**: `deduplicated_knowledge_graph.ttl` is all you need for Fuseki

## 📚 Documentation

See `knowledge-graph/COMPLETE_DOCUMENTATION.md` for:
- Complete setup guide
- Processing pipeline details
- API usage examples
- Troubleshooting help

## 🆘 Get Help

1. Missing source files? Contact the team
2. Already have source files? Run the scripts (takes 5 minutes)
3. Just need production? Get `deduplicated_knowledge_graph.ttl` from team

---

**Remember**: Never commit TTL files to Git! They're automatically excluded by .gitignore.
