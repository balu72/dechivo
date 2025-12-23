# SFIA Knowledge Graph - Jena Fuseki Setup

This directory contains the Apache Jena Fuseki setup for the SFIA knowledge graph.

## Quick Start

### 1. Start Fuseki
```bash
cd knowledge-graph
docker-compose up -d
```

### 2. Access Fuseki Web UI
- URL: http://localhost:3030
- Username: `admin`
- Password: `admin123`

### 3. Load SFIA Data

#### Option A: Using Web UI (Recommended)
1. Open http://localhost:3030
2. Click "Manage datasets"
3. Click "Add new dataset"
   - Dataset name: `sfia`
   - Dataset type: `Persistent (TDB2)`
4. Click "Create dataset"
5. Go to "Add data" tab
6. Select dataset: `sfia`
7. Upload file: `../data/SFIA_9_2025-02-27.ttl`
8. Click "Upload"

#### Option B: Using cURL
```bash
# Create dataset
curl -X POST http://localhost:3030/$/datasets \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u admin:admin123 \
  -d "dbName=sfia&dbType=tdb2"

# Load data
docker exec sfia-fuseki \
  curl -X POST http://localhost:3030/sfia/data \
  -H "Content-Type: text/turtle" \
  -u admin:admin123 \
  --data-binary @/staging/sfia.ttl
```

### 4. Test SPARQL Query
```bash
# Count all triples
curl -X POST http://localhost:3030/sfia/query \
  -H "Content-Type: application/sparql-query" \
  --data "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
```

## SPARQL Endpoint

Once the dataset is created and loaded:
- **Query endpoint**: http://localhost:3030/sfia/query
- **Update endpoint**: http://localhost:3030/sfia/update
- **Data endpoint**: http://localhost:3030/sfia/data

## Useful Commands

```bash
# Stop Fuseki
docker-compose down

# View logs
docker-compose logs -f fuseki

# Restart Fuseki
docker-compose restart

# Remove everything (including data)
docker-compose down -v
```

## Data Storage

- Persistent data is stored in: `./fuseki-data/`
- This directory is automatically created when Fuseki starts
- Backup this directory to preserve your knowledge graph

## Configuration

Edit `docker-compose.yml` to change:
- Port (default: 3030)
- Admin password (default: admin123)
- Memory allocation (default: 2GB)

## Troubleshooting

**Fuseki won't start:**
```bash
# Check if port 3030 is already in use
lsof -i :3030

# View container logs
docker-compose logs fuseki
```

**Data not loading:**
- Ensure the TTL file exists at `../data/SFIA_9_2025-02-27.ttl`
- Check file permissions
- Verify the dataset was created first

## Next Steps

Integrate with your Flask backend by installing SPARQLWrapper:
```bash
cd ../backend
pip install SPARQLWrapper
```

Then query Fuseki from Python:
```python
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://localhost:3030/sfia/query")
sparql.setQuery("""
    SELECT ?s ?p ?o
    WHERE { ?s ?p ?o }
    LIMIT 10
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
print(results)
```
