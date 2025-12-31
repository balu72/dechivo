# Knowledge Graph Integration Plan for Dechivo

**Project:** Dechivo - SFIA Job Description Enhancement System  
**Created:** 2025-12-31  
**Status:** Planning Phase - DO NOT IMPLEMENT YET

---

## 📋 Executive Summary

This document outlines the comprehensive plan to integrate Apache Jena Fuseki-based SFIA Knowledge Graph with the Dechivo application to enable semantic JD enhancement, skill extraction, and intelligent competency mapping.

### Current State
- ✅ SFIA 9 TTL file available (`SFIA_9_2025-02-27.ttl`, 651KB)
- ✅ Docker-based Fuseki setup configured (`knowledge-graph/docker-compose.yml`)
- ✅ Backend service skeleton exists (`sfia_km_service.py`)
- ✅ LangGraph enhancement workflow implemented (`enhance_jd_service.py`)
- ⚠️ Knowledge Graph NOT running (Fuseki needs to be started)
- ⚠️ Integration NOT connected (hardcoded to `localhost:3030`)

### Goal
Enable full SPARQL-based SFIA knowledge graph queries to power AI-driven job description enhancement with real-time semantic skill mapping.

---

## 🎯 Integration Objectives

1. **Deploy Knowledge Graph Infrastructure**
   - Start and configure Apache Jena Fuseki
   - Load SFIA 9 ontology data
   - Verify data integrity and query performance

2. **Backend Service Integration**
   - Connect backend to Fuseki SPARQL endpoint
   - Implement robust error handling and fallbacks
   - Add connection health checks

3. **Enhanced AI Workflow**
   - Integrate KG queries into LangGraph workflow
   - Enable semantic skill extraction
   - Improve SFIA competency mapping accuracy

4. **Testing & Validation**
   - Verify SPARQL query performance
   - Test enhancement quality with real JDs
   - Benchmark against fallback methods

5. **Production Readiness**
   - Add monitoring and logging
   - Implement caching strategies
   - Document deployment procedures

---

## 🏗️ Architecture Overview

### Current Architecture
```
┌─────────────────┐
│   Frontend      │
│   (React)       │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│   Flask API     │
│   (Backend)     │
└────────┬────────┘
         │
         ├──► enhance_jd_service.py (LangGraph + OpenAI)
         │    └──► sfia_km_service.py (SPARQLWrapper)
         │         └──► ❌ NOT CONNECTED
         │
         └──► Fallback: Hardcoded SFIA data
```

### Target Architecture
```
┌─────────────────┐
│   Frontend      │
│   (React)       │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────────────────────────┐
│   Flask API (Backend)               │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  enhance_jd_service.py       │  │
│  │  (LangGraph Workflow)        │  │
│  │                              │  │
│  │  1. Extract Keywords (LLM)  │  │
│  │  2. Map to SFIA (KG)        │◄─┼──┐
│  │  3. Assign Levels (LLM+KG)  │  │  │
│  └──────────────────────────────┘  │  │
│                                     │  │
│  ┌──────────────────────────────┐  │  │
│  │  sfia_km_service.py          │  │  │
│  │  (SPARQL Queries)            │  │  │
│  │  - Search skills             │  │  │
│  │  - Get skill details         │  │  │
│  │  - Find related skills       │  │  │
│  │  - Get level descriptions    │  │  │
│  └──────────────┬───────────────┘  │  │
└─────────────────┼───────────────────┘  │
                  │ SPARQL/HTTP          │
                  ▼                      │
         ┌────────────────┐              │
         │  Apache Jena   │              │
         │    Fuseki      │              │
         │  (Port 3030)   │              │
         ├────────────────┤              │
         │  SFIA Dataset  │              │
         │  (TDB2 Store)  │              │
         │                │              │
         │ • Skills       │◄─────────────┘
         │ • Categories   │
         │ • Levels       │
         │ • Competencies │
         └────────────────┘
```

---

## 📊 Phase-by-Phase Implementation Plan

### **Phase 1: Infrastructure Setup** (Estimated: 2-4 hours)

#### 1.1 Start Fuseki Server
```bash
cd knowledge-graph
docker-compose up -d
```

**Verification:**
- [ ] Fuseki accessible at http://localhost:3030
- [ ] Web UI login works (admin/admin123)
- [ ] Container running: `docker ps | grep sfia-fuseki`

#### 1.2 Create SFIA Dataset
**Option A: Web UI (Recommended)**
1. Navigate to http://localhost:3030
2. Click "Manage datasets" → "Add new dataset"
3. Dataset name: `sfia`
4. Dataset type: `Persistent (TDB2)`
5. Click "Create dataset"

**Option B: cURL**
```bash
curl -X POST http://localhost:3030/$/datasets \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u admin:admin123 \
  -d "dbName=sfia&dbType=tdb2"
```

**Verification:**
- [ ] Dataset `sfia` appears in Fuseki UI
- [ ] Dataset status: Active

#### 1.3 Load SFIA TTL Data
**Web UI Method:**
1. Go to "Add data" tab
2. Select dataset: `sfia`
3. Choose file: `../data/SFIA_9_2025-02-27.ttl`
4. Click "Upload"

**cURL Method:**
```bash
curl -X POST http://localhost:3030/sfia/data \
  -H "Content-Type: text/turtle" \
  -u admin:admin123 \
  --data-binary @../data/SFIA_9_2025-02-27.ttl
```

**Verification:**
```bash
# Test SPARQL query
curl -X POST http://localhost:3030/sfia/query \
  -H "Content-Type: application/sparql-query" \
  --data "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
```

Expected: `{ "count": <number> }` (should be thousands of triples)

#### 1.4 Test Sample Queries
```sparql
# Query 1: Get all skills
SELECT ?skill ?name ?code WHERE {
  ?skill a sfia:Skill ;
         sfia:name ?name ;
         sfia:code ?code .
} LIMIT 10

# Query 2: Get skill categories
SELECT DISTINCT ?category ?name WHERE {
  ?category a sfia:Category ;
            sfia:name ?name .
}

# Query 3: Get levels
SELECT ?level ?number ?name WHERE {
  ?level a sfia:Level ;
         sfia:levelNumber ?number ;
         sfia:name ?name .
} ORDER BY ?number
```

**Success Criteria:**
- [ ] All queries return data
- [ ] Query response time < 500ms
- [ ] No SPARQL syntax errors

---

### **Phase 2: Backend Service Configuration** (Estimated: 2-3 hours)

#### 2.1 Update Environment Configuration

**File: `backend/.env`**
```bash
# Existing variables
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
OPENAI_API_KEY=your-openai-key

# NEW: Knowledge Graph Configuration
FUSEKI_URL=http://localhost:3030
FUSEKI_DATASET=sfia
FUSEKI_USERNAME=admin
FUSEKI_PASSWORD=admin123
KG_ENABLED=true
KG_TIMEOUT=10
KG_CACHE_TTL=3600  # Cache queries for 1 hour
```

**File: `backend/.env.example`**
```bash
# Add same KG variables with placeholder values
FUSEKI_URL=http://localhost:3030
FUSEKI_DATASET=sfia
KG_ENABLED=true
```

#### 2.2 Update Service Initialization

**File: `backend/services/sfia_km_service.py`**

**Changes needed:**
1. Update `__init__` to read from environment variables
2. Add connection health check method
3. Add retry logic for failed queries
4. Implement query result caching
5. Add fallback to mock data if KG unavailable

**Pseudo-code:**
```python
import os
from functools import lru_cache

class SFIAKnowledgeService:
    def __init__(self):
        self.fuseki_url = os.getenv('FUSEKI_URL', 'http://localhost:3030')
        self.dataset = os.getenv('FUSEKI_DATASET', 'sfia')
        self.enabled = os.getenv('KG_ENABLED', 'true').lower() == 'true'
        self.timeout = int(os.getenv('KG_TIMEOUT', '10'))
        
        # Initialize connection
        if self.enabled:
            self._validate_connection()
    
    def _validate_connection(self):
        """Test connection to Fuseki"""
        try:
            result = self._execute_query("SELECT (1 as ?test) WHERE {}")
            logger.info("✅ Knowledge Graph connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ KG connection failed: {e}")
            self.enabled = False
            return False
    
    @lru_cache(maxsize=100)
    def get_skill_by_code(self, skill_code):
        """Cached skill lookup"""
        if not self.enabled:
            return self._fallback_skill_data(skill_code)
        # ... existing SPARQL query
```

#### 2.3 Update Enhancement Service

**File: `backend/services/enhance_jd_service.py`**

**Changes needed:**
1. Add KG availability check on initialization
2. Update `map_to_sfia_node` to use live KG queries
3. Enhance `set_skill_level_node` with KG level descriptions
4. Add graceful degradation if KG fails

**Key Integration Points:**
```python
class JobDescriptionEnhancer:
    def __init__(self):
        # ... existing code ...
        
        # Initialize KG service
        self.kg_service = get_sfia_service()
        self.kg_available = self.kg_service.enabled
        
        if self.kg_available:
            logger.info("✅ Knowledge Graph integration enabled")
        else:
            logger.warning("⚠️ Using fallback mode (no KG)")
    
    def map_to_sfia_node(self, state: EnhancementState):
        """Enhanced with real KG queries"""
        keywords = state["extracted_keywords"]
        sfia_skills = []
        
        for keyword in keywords:
            if self.kg_available:
                # Use real KG search
                results = self.kg_service.search_skills(keyword, limit=5)
                sfia_skills.extend(results)
            else:
                # Fallback to mock data
                sfia_skills.extend(self._mock_skill_search(keyword))
        
        # ... rest of logic
```

#### 2.4 Add Health Check Endpoint

**File: `backend/app.py`**
```python
@app.route('/api/health/kg', methods=['GET'])
def kg_health_check():
    """Check Knowledge Graph connectivity"""
    from services.sfia_km_service import get_sfia_service
    
    kg_service = get_sfia_service()
    
    if kg_service.enabled:
        stats = kg_service.get_knowledge_graph_stats()
        return jsonify({
            "status": "healthy",
            "fuseki_url": kg_service.fuseki_url,
            "dataset": kg_service.dataset,
            "stats": stats
        }), 200
    else:
        return jsonify({
            "status": "unavailable",
            "message": "Knowledge Graph not connected",
            "fallback_mode": True
        }), 503
```

---

### **Phase 3: Testing & Validation** (Estimated: 3-4 hours)

#### 3.1 Unit Tests

**Create: `backend/tests/test_kg_service.py`**
```python
import unittest
from services.sfia_km_service import SFIAKnowledgeService

class TestKnowledgeGraphService(unittest.TestCase):
    def setUp(self):
        self.kg = SFIAKnowledgeService()
    
    def test_connection(self):
        """Test KG connection"""
        self.assertTrue(self.kg.enabled)
    
    def test_search_skills(self):
        """Test skill search"""
        results = self.kg.search_skills("programming")
        self.assertGreater(len(results), 0)
    
    def test_get_skill_by_code(self):
        """Test getting skill by code"""
        skill = self.kg.get_skill_by_code("PROG")
        self.assertIsNotNone(skill)
        self.assertEqual(skill['code'], 'PROG')
    
    # Add more tests...
```

#### 3.2 Integration Tests

**Test Scenarios:**
1. ✅ Full workflow with KG enabled
2. ✅ Workflow with KG disabled (fallback mode)
3. ✅ KG connection failure handling
4. ✅ Query timeout handling
5. ✅ Invalid skill code handling

**Sample Test Job Descriptions:**
```
Test JD 1 (Software Engineer):
"Senior Software Engineer with 5+ years Python experience.
Expert in Django, REST APIs, and PostgreSQL.
Leads technical design and mentors junior developers."

Expected SFIA Skills:
- PROG (Programming/software development) - Level 5
- DTAN (Data modelling and design) - Level 4
- TECH (Technology service management) - Level 5

Test JD 2 (Data Analyst):
"Junior Data Analyst position. Requires SQL, Excel, Power BI.
Creates reports and dashboards for business teams."

Expected SFIA Skills:
- DAAN (Data analysis) - Level 2-3
- VISL (Data visualisation) - Level 2
- BUAN (Business analysis) - Level 2
```

#### 3.3 Performance Testing

**Metrics to Measure:**
- SPARQL query response time (target: < 500ms)
- End-to-end enhancement time (target: < 10s)
- Cache hit rate (target: > 60%)
- Fallback activation rate (target: < 1%)

**Load Testing:**
```bash
# Test concurrent requests
ab -n 100 -c 10 -T 'application/json' \
   -p test_jd.json \
   http://localhost:5000/api/enhance-jd
```

#### 3.4 Quality Validation

**Manual Testing Checklist:**
- [ ] Enhanced JDs contain relevant SFIA skills
- [ ] Skill levels match job seniority
- [ ] Skill descriptions are accurate
- [ ] No duplicate skills
- [ ] Categories properly assigned
- [ ] Level descriptions included

---

### **Phase 4: Frontend Integration** (Estimated: 2-3 hours)

#### 4.1 Display KG Status

**File: `frontend/src/EnhancementPage.jsx`**
```javascript
// Add KG status indicator
const [kgStatus, setKgStatus] = useState(null);

useEffect(() => {
  // Check KG health on mount
  fetch('http://localhost:5000/api/health/kg')
    .then(res => res.json())
    .then(data => setKgStatus(data))
    .catch(err => console.error('KG health check failed:', err));
}, []);

// Display status badge
{kgStatus && (
  <div className="kg-status">
    {kgStatus.status === 'healthy' ? (
      <span className="badge badge-success">
        🔗 Knowledge Graph Connected
      </span>
    ) : (
      <span className="badge badge-warning">
        ⚠️ Fallback Mode (No KG)
      </span>
    )}
  </div>
)}
```

#### 4.2 Enhanced Skill Display

**Show rich SFIA data:**
- Skill code + name
- SFIA level (1-7) with description
- Category and subcategory
- Related skills (optional)

#### 4.3 Add KG Statistics Page (Optional)

**New page: `KnowledgeGraphStats.jsx`**
- Total skills in KG
- Categories breakdown
- Query performance metrics
- Recent searches

---

### **Phase 5: Production Deployment** (Estimated: 2-4 hours)

#### 5.1 Docker Compose Enhancement

**File: `docker-compose.yml` (root)**
```yaml
version: '3.8'

services:
  fuseki:
    image: stain/jena-fuseki:latest
    container_name: dechivo-fuseki
    ports:
      - "3030:3030"
    environment:
      - ADMIN_PASSWORD=${FUSEKI_PASSWORD:-admin123}
      - JVM_ARGS=-Xmx2g -Xms1g
    volumes:
      - ./knowledge-graph/fuseki-data:/fuseki-base/databases
      - ./data/SFIA_9_2025-02-27.ttl:/staging/sfia.ttl:ro
    restart: unless-stopped
    networks:
      - dechivo-network

  backend:
    build: ./backend
    container_name: dechivo-backend
    ports:
      - "5000:5000"
    environment:
      - FUSEKI_URL=http://fuseki:3030
      - FUSEKI_DATASET=sfia
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - fuseki
    networks:
      - dechivo-network

  frontend:
    build: ./frontend
    container_name: dechivo-frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
    networks:
      - dechivo-network

networks:
  dechivo-network:
    driver: bridge
```

#### 5.2 Monitoring & Logging

**Add to `backend/app.py`:**
```python
import time
from functools import wraps

def log_kg_query(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        
        logger.info(f"KG Query: {func.__name__} | Duration: {duration:.2f}s")
        return result
    return wrapper
```

#### 5.3 Caching Strategy

**Implement Redis caching (optional):**
```bash
# Add to requirements.txt
redis==5.0.1

# Add to docker-compose.yml
redis:
  image: redis:7-alpine
  container_name: dechivo-redis
  ports:
    - "6379:6379"
```

**Cache SPARQL results:**
```python
import redis
import json

class SFIAKnowledgeService:
    def __init__(self):
        # ... existing code ...
        self.cache = redis.Redis(host='localhost', port=6379, db=0)
        self.cache_ttl = int(os.getenv('KG_CACHE_TTL', '3600'))
    
    def get_skill_by_code(self, skill_code):
        # Check cache first
        cache_key = f"skill:{skill_code}"
        cached = self.cache.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        # Query KG
        result = self._query_kg(skill_code)
        
        # Cache result
        self.cache.setex(cache_key, self.cache_ttl, json.dumps(result))
        
        return result
```

---

## 📝 Implementation Checklist

### Pre-Integration
- [ ] Review current codebase
- [ ] Backup database
- [ ] Document current fallback behavior
- [ ] Create feature branch: `feature/kg-integration`

### Phase 1: Infrastructure
- [ ] Start Fuseki container
- [ ] Create `sfia` dataset
- [ ] Load SFIA TTL data
- [ ] Verify data loaded correctly
- [ ] Test sample SPARQL queries
- [ ] Document connection details

### Phase 2: Backend
- [ ] Update `.env` with KG config
- [ ] Modify `sfia_km_service.py`
- [ ] Update `enhance_jd_service.py`
- [ ] Add health check endpoint
- [ ] Add error handling
- [ ] Implement caching
- [ ] Test connection logic

### Phase 3: Testing
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Test with sample JDs
- [ ] Performance benchmarking
- [ ] Load testing
- [ ] Quality validation

### Phase 4: Frontend
- [ ] Add KG status indicator
- [ ] Update skill display
- [ ] Test user experience
- [ ] Add loading states
- [ ] Handle errors gracefully

### Phase 5: Production
- [ ] Update docker-compose
- [ ] Configure monitoring
- [ ] Set up logging
- [ ] Implement caching (if needed)
- [ ] Write deployment docs
- [ ] Create backup strategy

### Post-Integration
- [ ] Update README.md
- [ ] Update API documentation
- [ ] Create user guide
- [ ] Monitor performance for 1 week
- [ ] Gather user feedback
- [ ] Optimize based on metrics

---

## 🚨 Risk Mitigation

### Risk 1: Fuseki Connection Failure
**Impact:** High  
**Mitigation:**
- Implement robust fallback to mock data
- Add health checks and auto-retry
- Monitor connection status
- Alert on prolonged unavailability

### Risk 2: Poor Query Performance
**Impact:** Medium  
**Mitigation:**
- Implement caching (Redis)
- Optimize SPARQL queries
- Add query timeout limits
- Use async queries where possible

### Risk 3: Data Quality Issues
**Impact:** Medium  
**Mitigation:**
- Validate TTL data before loading
- Test with diverse job descriptions
- Compare KG results with fallback
- Implement result validation

### Risk 4: OpenAI + KG Latency
**Impact:** Low  
**Mitigation:**
- Parallelize independent operations
- Cache frequent queries
- Show progressive loading states
- Set reasonable timeout limits

---

## 📊 Success Metrics

### Technical Metrics
- **KG Uptime:** > 99.5%
- **Query Response Time:** < 500ms (p95)
- **Enhancement Time:** < 10s end-to-end
- **Cache Hit Rate:** > 60%
- **Error Rate:** < 0.1%

### Quality Metrics
- **Skill Match Accuracy:** > 90%
- **Level Assignment Accuracy:** > 85%
- **User Satisfaction:** > 4.5/5
- **False Positive Rate:** < 5%

### Performance Benchmarks
| Metric | Without KG | With KG | Target |
|--------|-----------|---------|--------|
| Enhancement Time | 8s | 9s | < 10s |
| Skill Accuracy | 70% | 90% | > 85% |
| Skills per JD | 3-5 | 5-8 | 5-10 |
| Level Accuracy | 60% | 85% | > 80% |

---

## 📚 Resources & References

### Documentation
- Apache Jena Fuseki: https://jena.apache.org/documentation/fuseki2/
- SPARQL 1.1: https://www.w3.org/TR/sparql11-query/
- SPARQLWrapper: https://sparqlwrapper.readthedocs.io/
- SFIA Framework: https://sfia-online.org/

### Internal Documentation
- `knowledge-graph/README.md` - Fuseki setup guide
- `backend/services/sfia_km_service.py` - KG service code
- `backend/services/enhance_jd_service.py` - Enhancement workflow
- `AUTHENTICATION_SUMMARY.md` - Auth system docs

### Example SPARQL Queries
See: `knowledge-graph/example-queries.sparql` (to be created)

---

## 🔄 Rollback Plan

If integration fails or causes issues:

1. **Immediate Rollback**
   ```bash
   git checkout main
   git branch -D feature/kg-integration
   ```

2. **Disable KG**
   ```bash
   # In .env
   KG_ENABLED=false
   ```

3. **Stop Fuseki**
   ```bash
   cd knowledge-graph
   docker-compose down
   ```

4. **Verify Fallback Mode**
   - Test enhancement with KG disabled
   - Confirm fallback data works
   - Monitor error logs

---

## 🎯 Next Steps After Integration

1. **Data Enhancement**
   - Add custom SFIA competencies
   - Map industry-specific skills
   - Create skill synonyms/aliases

2. **Advanced Features**
   - Skill gap analysis
   - Job-to-candidate matching
   - Career path recommendations
   - Competency comparison

3. **Knowledge Graph Expansion**
   - Add company-specific competencies
   - Integrate with other frameworks (O*NET, ESCO)
   - Build skill relationship graph
   - Add learning resources

4. **Analytics**
   - Track most-requested skills
   - Identify skill trends
   - Generate insights dashboard
   - Export analytics data

---

## ✅ Completion Criteria

Integration is considered **complete** when:

- [x] Fuseki running and accessible
- [x] SFIA data loaded and queryable
- [x] Backend successfully connects to KG
- [x] All SPARQL queries working
- [x] Enhancement workflow uses live KG data
- [x] Fallback mode functional
- [x] All tests passing (unit + integration)
- [x] Frontend displays KG status
- [x] Performance targets met
- [x] Documentation updated
- [x] Deployed to production

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-31  
**Owner:** Development Team  
**Status:** ⚠️ PLANNING - DO NOT IMPLEMENT YET

---

*This plan should be reviewed and approved before beginning implementation.*
