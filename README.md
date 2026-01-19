# 🎯 Dechivo - AI-Powered Job Description Platform

**Version**: 1.0  
**Status**: ✅ Production Ready  
**Last Updated**: January 19, 2026

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [Knowledge Graph Integration](#knowledge-graph-integration)
5. [Authentication System](#authentication-system)
6. [Getting Started](#getting-started)
7. [API Documentation](#api-documentation)
8. [Deployment Guide](#deployment-guide)
9. [Directory Structure](#directory-structure)
10. [Troubleshooting](#troubleshooting)

---

## Overview

Dechivo is an AI-powered platform that helps create and enhance job descriptions using **5 global skill frameworks** and advanced LLM technology. It combines organizational context with international skill standards to generate professional, comprehensive job descriptions.

### Key Highlights

✅ **15,000+ Skills** from 5 international frameworks  
✅ **AI-Powered** creation and enhancement  
✅ **Smart Skills Autocomplete** with multi-source search  
✅ **Primary & Secondary Skills** separation  
✅ **Unified Knowledge Graph** with 1.73M triples  
✅ **Multi-framework Intelligence** (SFIA, ESCO, O*NET, Singapore, Oasis)

---

## Features

### 🎨 **Job Description Creation**
- Create JDs from organizational context
- AI-powered content generation
- Primary (must-have) and Secondary (good-to-have) skills
- Experience level specification
- Work environment customization

### 🚀 **JD Enhancement**
- Enhance existing JDs with global skill standards
- SFIA skill mapping with levels
- Cross-framework skill suggestions
- Industry-standard terminology

### 🔍 **Smart Skills Search**
- **15,000+ skills** from 3 sources:
  - Common Skills (curated)
  - Knowledge Graph (4 international frameworks)
  - SFIA (IT professional standards)
- Real-time autocomplete
- Source transparency
- Intelligent deduplication

### 🌍 **Knowledge Graph**
- **5 Global Frameworks**:
  - 🎓 SFIA (IT Skills)
  - 🇪🇺 ESCO (European Standards)
  - 🇺🇸 O*NET (US Occupational Network)
  - 🇸🇬 Singapore SkillsFuture
  - 🇨🇦 OASIS (Canada)
- **1.73 million triples** (deduplicated)
- **6,372 unique occupations**
- **14,598+ skills**

### 🔐 **Authentication**
- User registration with email verification
- JWT-based authentication
- Role-based access control
- Secure password hashing (bcrypt)

---

## Technology Stack

### Frontend
- **Framework**: React + Vite
- **Styling**: Vanilla CSS
- **Routing**: React Router
- **State Management**: React Context (Auth)

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLAlchemy + SQLite
- **Authentication**: Flask-JWT-Extended
- **LLM**: OpenAI GPT-4o-mini (primary), Ollama (fallback)

### Knowledge Graph
- **Store**: Apache Jena Fuseki
- **Format**: RDF/Turtle
- **Query**: SPARQL
- **Deployment**: Docker

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Email**: Brevo (transactional emails)
- **Analytics**: Mixpanel (optional)

---

## Knowledge Graph Integration

### Architecture

The unified knowledge graph combines data from 5 international skill frameworks into a single, deduplicated dataset:

```
Source Files (7,929 TTL files, 4 frameworks)
    ↓
Merge Script (merge_ttl.py)
    ↓
Unified Graph (1,792,228 triples)
    ↓
Deduplication (deduplicate_entities.py)
    ↓
Production KG (1,726,471 triples, 129 MB)
    ↓
Apache Jena Fuseki (unified dataset)
    ↓
REST API (/api/kg/* endpoints)
    ↓
Frontend (Skills autocomplete, JD enhancement)
```

### Key Statistics

| Metric | Value |
|--------|-------|
| **Total Triples** | 1,726,471 |
| **Unique Occupations** | 6,372 |
| **Total Skills** | 14,598+ |
| **Frameworks** | 5 (SFIA, ESCO, O*NET, Singapore, Oasis) |
| **File Size** | 128.97 MB |
| **Duplicates Removed** | 529 occupation groups |

### API Endpoints

All Knowledge Graph endpoints are available at `/api/kg/*`:

```bash
# Health check
GET /api/kg/health

# Search occupations
GET /api/kg/occupations/search?q=developer

# Get occupation skills
GET /api/kg/occupations/{label}/skills

# Get occupation profile
GET /api/kg/occupations/{label}/profile

# Find similar occupations
GET /api/kg/occupations/{label}/similar

# Search skills
GET /api/kg/skills/search?q=python

# Enrich job description
POST /api/kg/jd/enrich
{
  "job_title": "Software Developer",
  "existing_skills": ["Python", "AWS"]
}

# Career skill gap analysis
POST /api/kg/career/skill-gap
{
  "current_occupation": "Junior Developer",
  "target_occupation": "Senior Developer"
}
```

### Skills Search Integration

The skills autocomplete is powered by **3 sources**:

1. **Common Skills** (score: 100-40)
   - Hand-curated, general tech/soft skills
   - ~500 skills

2. **Knowledge Graph** (score: 70)
   - International standards from 4 frameworks
   - 14,598+ skills
   - Real-time SPARQL queries

3. **SFIA** (score: 50)
   - IT professional competencies
   - ~180 skills

**Smart Filtering**:
- Secondary skills automatically exclude Primary skills
- Case-insensitive deduplication
- Relevance-based ranking

---

## Authentication System

### Features
- ✅ User registration with email verification
- ✅ JWT access & refresh tokens
- ✅ Password hashing with bcrypt
- ✅ Protected routes
- ✅ Role-based access (user/admin)

### User Model
```python
User:
  - email (unique)
  - username (unique)
  - password_hash
  - full_name
  - organization
  - role (user/admin)
  - is_verified
  - verification_token
  - created_at, updated_at
```

### API Endpoints
```bash
# Register
POST /api/auth/register
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123",
  "full_name": "John Doe"
}

# Login
POST /api/auth/login
{
  "username": "johndoe",
  "password": "SecurePass123"
}

# Verify email
GET /api/auth/verify/{token}

# Get current user
GET /api/auth/me
Headers: Authorization: Bearer {access_token}

# Refresh token
POST /api/auth/refresh
Headers: Authorization: Bearer {refresh_token}

# Logout
POST /api/auth/logout
```

---

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker & Docker Compose
- OpenAI API Key (or Ollama locally)

### Installation

#### 1. Clone Repository
```bash
git clone <repository-url>
cd dechivo
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run backend
python3 app.py
```

#### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

#### 4. Knowledge Graph Setup
```bash
cd knowledge-graph

# Start Fuseki
docker-compose up -d

# Load unified knowledge graph (if you have the data)
python3 scripts/replace_fuseki_datasets.py
```

### Environment Variables

Create `backend/.env`:

```bash
# Flask
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# OpenAI (Required for JD creation)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini

# Fuseki
FUSEKI_URL=http://localhost:3030
FUSEKI_DATASET=unified
FUSEKI_USERNAME=admin
FUSEKI_PASSWORD=admin123

# Email (Brevo)
BREVO_API_KEY=your-brevo-api-key
BREVO_SENDER_EMAIL=your@email.com
BREVO_SENDER_NAME=Your Name

# Optional: Ollama (fallback LLM)
# OLLAMA_URL=http://localhost:11434
# OLLAMA_MODEL=llama3:latest
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Fuseki UI**: http://localhost:3030
- **API Docs**: See `/api/*` endpoints below

---

## API Documentation

### Core Endpoints

```bash
# Authentication
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
POST /api/auth/logout
GET  /api/auth/me
GET  /api/auth/verify/{token}

# Job Descriptions
POST /api/create-jd          # Create new JD
POST /api/enhance-jd         # Enhance existing JD
GET  /api/search-skills      # Skills autocomplete

# Knowledge Graph
GET  /api/kg/health
GET  /api/kg/occupations/search
GET  /api/kg/occupations/{label}/skills
GET  /api/kg/occupations/{label}/profile
GET  /api/kg/occupations/{label}/similar
GET  /api/kg/skills/search
POST /api/kg/jd/enrich
POST /api/kg/career/skill-gap
```

### Example: Create JD

```bash
curl -X POST http://localhost:5000/api/create-jd \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "org_context": {
      "company_name": "TechCorp",
      "company_description": "Leading tech company",
      "role_title": "Senior Software Engineer",
      "role_type": "Permanent",
      "role_grade": "Senior (L5)",
      "location": "Bangalore, India",
      "work_environment": "Hybrid",
      "reporting_to": "Engineering Manager",
      "role_context": "Python, AWS, Docker",
      "business_context": "5+ years experience"
    }
  }'
```

---

## Deployment Guide

### Production Deployment Checklist

#### Pre-Deployment
- [ ] Review all code changes
- [ ] Test locally (frontend + backend + KG)
- [ ] Update `.gitignore` (exclude `.ttl` files)
- [ ] Package knowledge graph data

#### Backend Deployment
```bash
# 1. Pull latest code
git pull origin main

# 2. Install dependencies
cd backend
pip install -r requirements.txt

# 3. Set environment variables
# Edit .env with production values

# 4. Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Frontend Deployment
```bash
# 1. Build production bundle
cd frontend
npm run build

# 2. Serve with nginx or similar
# dist/ contains the built files
```

#### Knowledge Graph Deployment
```bash
# 1. Start Fuseki
cd knowledge-graph
docker-compose up -d

# 2. Load unified KG
python3 scripts/replace_fuseki_datasets.py

# 3. Verify loading
curl -u admin:admin123 \
  "http://localhost:3030/$/datasets"
```

#### Verification
```bash
# Test API
curl https://your-domain.com/api/kg/health

# Test frontend
open https://your-domain.com
```

---

## Directory Structure

```
dechivo/
├── backend/
│   ├── app.py                    # Main Flask application
│   ├── models.py                 # Database models
│   ├── auth.py                   # Authentication utilities
│   ├── kg_routes.py              # Knowledge Graph API
│   ├── services/
│   │   ├── jd_services.py        # JD creation/enhancement
│   │   ├── sfia_km_service.py    # SFIA KG service
│   │   └── email_service.py      # Email service (Brevo)
│   ├── prompts/                  # LLM prompts
│   ├── requirements.txt          # Python dependencies
│   └── .env                      # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── CreateJDPage.jsx
│   │   │   ├── EnhancePage.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   └── RegisterPage.jsx
│   │   ├── AuthContext.js       # Authentication context
│   │   ├── analytics.js         # Mixpanel analytics
│   │   └── styles/              # CSS files
│   ├── package.json
│   └── vite.config.js
│
├── knowledge-graph/
│   ├── scripts/
│   │   ├── merge_ttl.py          # Merge all TTL files
│   │   ├── deduplicate_entities.py  # Remove duplicates
│   │   ├── replace_fuseki_datasets.py # Load to Fuseki
│   │   ├── kg_service.py         # Python KG service
│   │   └── sparql_queries.py     # SPARQL templates
│   ├── COMPLETE_DOCUMENTATION.md # Full KG docs
│   ├── docker-compose.yml        # Fuseki container
│   └── requirements.txt
│
├── data/
│   ├── unified-files/
│   │   ├── deduplicated_knowledge_graph.ttl  # Production KG
│   │   ├── merge_statistics.json
│   │   └── deduplication_statistics.json
│   ├── ca_turtle/               # Canada source files
│   ├── esco_turtle/             # ESCO source files
│   ├── onet_turtle/             # O*NET source files
│   └── sg_turtle/               # Singapore source files
│
├── .gitignore                   # Git exclusions (*.ttl, .env, etc.)
└── README.md                    # This file
```

---

## Troubleshooting

### Common Issues

#### 1. OpenAI API Not Working

**Error**: `❌ No LLM available`

**Solution**:
```bash
# Check .env file
cd backend
cat .env | grep OPENAI_API_KEY

# Make sure dotenv is installed
pip install python-dotenv

# Verify key is loaded
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Key:', os.getenv('OPENAI_API_KEY')[:10])"

# Restart backend
python3 app.py
```

#### 2. Knowledge Graph Not Loading

**Error**: `❌ Knowledge Graph not available`

**Solution**:
```bash
# Check Fuseki is running
docker ps | grep fuseki

# If not running
cd knowledge-graph
docker-compose up -d

# Check logs
docker logs fuseki

# Verify endpoint
curl -u admin:admin123 http://localhost:3030/$/server
```

#### 3. Skills Autocomplete Not Working

**Error**: Empty suggestions or errors

**Solution**:
```bash
# 1. Check backend logs
tail -f backend/app.log

# 2. Test endpoint directly
curl "http://localhost:5000/api/search-skills?query=python" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Verify KG is loaded
curl -X POST "http://localhost:3030/unified/query" \
  -u admin:admin123 \
  -H "Content-Type: application/sparql-query" \
  --data 'SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }'

# Should return 1,726,471 triples
```

#### 4. Frontend Build Fails

**Error**: Module not found

**Solution**:
```bash
cd frontend

# Clear cache
rm -rf node_modules package-lock.json

# Reinstall
npm install

# Try building
npm run build
```

#### 5. Authentication Issues

**Error**: Token invalid or expired

**Solution**:
```bash
# Check JWT secret is set
grep JWT_SECRET_KEY backend/.env

# Regenerate token
# Login again through the UI or API

# Check token expiration in app.py
# JWT_ACCESS_TOKEN_EXPIRES defaults to 1 hour
```

---

## Performance Tips

### Backend
- Use Redis for caching frequent KG queries
- Increase Fuseki memory: `-Xmx8g` in docker-compose.yml
- Use gunicorn with multiple workers in production

### Frontend
- Enable production build optimizations
- Use CDN for static assets
- Enable gzip compression

### Knowledge Graph
- Add SPARQL query timeouts
- Index frequently queried properties
- Use LIMIT in queries (already implemented)

---

## Contributing

### Development Workflow

1. Create feature branch
2. Make changes
3. Test locally
4. Commit with clear messages
5. Push and create PR

### Code Style

- **Python**: Follow PEP 8
- **JavaScript**: Use ES6+, consistent formatting
- **CSS**: BEM naming convention

---

## Security

### Best Practices

✅ Environment variables for all secrets  
✅ .gitignore excludes sensitive files  
✅ JWT token expiration (1 hour access, 30 days refresh)  
✅ Password hashing with bcrypt  
✅ CORS configuration  
✅ SQL injection prevention (SQLAlchemy ORM)  

### Production Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Enable HTTPS
- [ ] Set secure cookie flags
- [ ] Configure rate limiting
- [ ] Enable security headers
- [ ] Regular dependency updates

---

## License

[Add your license here]

---

## Contact & Support

- **Documentation**: See `knowledge-graph/COMPLETE_DOCUMENTATION.md`
- **Issues**: [GitHub Issues]
- **Email**: [Your contact email]

---

## Acknowledgments

### Data Sources

- **SFIA**: Skills Framework for the Information Age
- **ESCO**: European Skills, Competences, Qualifications and Occupations
- **O*NET**: Occupational Information Network (US Department of Labor)
- **Singapore SkillsFuture**: Singapore Skills Framework
- **OASIS**: Canadian occupation classification

### Technologies

- OpenAI GPT-4o-mini
- Apache Jena Fuseki
- Flask & React
- LangChain & LangGraph

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: January 19, 2026

🎉 **Ready to create amazing job descriptions powered by global skill standards!**
