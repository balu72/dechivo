# 📚 Dechivo Knowledge Graph Documentation

Welcome to the Dechivo Knowledge Graph documentation!

---

## 📖 **Main Documentation**

**All KG documentation has been consolidated into one comprehensive guide:**

### **[📘 COMPLETE_DOCUMENTATION.md](./COMPLETE_DOCUMENTATION.md)**

This 23 KB guide contains everything you need:

✅ Quick Start Guide  
✅ Complete API Reference  
✅ Usage Examples (Python & JavaScript)  
✅ SPARQL Query Templates  
✅ Architecture Overview  
✅ Data Sources & Statistics  
✅ Troubleshooting Guide  
✅ Scripts Reference  
✅ Changelog  

---

## 📦 **Production Data Files**

### **[fuseki-data/](./fuseki-data/)**

Production-ready TTL files for deployment (checked into git):

- **`deduplicated_knowledge_graph.ttl`** (129 MB)
  - Unified KG from 4 frameworks (ESCO, O*NET, Singapore, Canada)
  - 1,726,471 triples
  - 6,372 unique occupations
  - 14,598+ skills

- **`SFIA_9_2025-02-27.ttl`** (636 KB)
  - SFIA v9 IT professional competencies
  - ~10,000 triples
  - 180 skills with 7 levels each

**Usage**: Load these files into Fuseki to set up the knowledge graph.

---

## 📂 **Additional Resources**

### **[INTEGRATION_PLAN.md](./INTEGRATION_PLAN.md)**
- 8-phase implementation roadmap
- Technical architecture
- Risk management
- Timeline estimates

### **[UNIFIED_TTL_FEASIBILITY.md](./UNIFIED_TTL_FEASIBILITY.md)**
- Feasibility analysis for unified approach
- Performance comparisons
- Implementation strategy

### **[../data/unified-files/MERGE_DEDUP_SUMMARY.md](../data/unified-files/MERGE_DEDUP_SUMMARY.md)**
- Detailed merge & deduplication statistics
- Sample data structures
- Processing results

---

## 🚀 **Quick Start**

```bash
# 1. Access Fuseki
open http://localhost:3030
# Login: admin / admin123

# 2. Test API
curl http://localhost:5000/api/kg/health

# 3. Search occupations
curl "http://localhost:5000/api/kg/occupations/search?q=developer"
```

---

## 📊 **Current Status**

| Metric | Value |
|--------|-------|
| **Status** | ✅ Production Ready |
| **Dataset** | unified |
| **Triples** | 1,726,471 |
| **Occupations** | 6,372 unique |
| **Skills** | 14,598+ |
| **Frameworks** | 4 (CA, ESCO, O*NET, SG) |

---

## 🛠️ **Scripts**

All utility scripts are in `scripts/`:

- `merge_ttl.py` - Merge all TTL files  
- `deduplicate_entities.py` - Remove duplicates  
- `replace_fuseki_datasets.py` - Deploy to Fuseki  
- `kg_service.py` - Python API service  
- `sparql_queries.py` - Query templates  
- `cleanup_intermediary_files.py` - Cleanup tools  

---

## 📞 **Support**

- **Full Documentation**: [COMPLETE_DOCUMENTATION.md](./COMPLETE_DOCUMENTATION.md)
- **API Guide**: See COMPLETE_DOCUMENTATION.md § API Reference
- **Troubleshooting**: See COMPLETE_DOCUMENTATION.md § Troubleshooting

---

**Start Reading**: [**COMPLETE_DOCUMENTATION.md**](./COMPLETE_DOCUMENTATION.md) 📖
