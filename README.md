# Dechivo - SFIA-Based ICT Job Description Enhancement System

[![React](https://img.shields.io/badge/React-19.2.0-blue.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![Ollama](https://img.shields.io/badge/Ollama-llama3-purple.svg)](https://ollama.ai/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

A **full-stack AI-powered application** for enhancing ICT job descriptions using the **SFIA (Skills Framework for the Information Age)** framework with integrated knowledge graph technology and local LLM support via Ollama.

---

## 🌟 Features

### 🔐 **User Authentication & Authorization**
- JWT-based authentication with access & refresh tokens
- Automatic token refresh for seamless sessions
- Secure password hashing using bcrypt
- User registration and login system
- Protected routes (frontend & backend)
- User profile management with dropdown menu
- Token expiration (1 hour for access, 30 days for refresh)
- Persistent sessions with localStorage

### 🚀 **Job Description Enhancement**
- **4-step AI workflow** powered by LangGraph:
  1. **Extract Skills** - LLM identifies keywords from JD
  2. **Map to SFIA** - Knowledge Graph finds matching SFIA skills
  3. **Set Skill Levels** - Assigns appropriate SFIA levels (1-7)
  4. **Regenerate JD** - LLM rewrites JD incorporating SFIA skills
- Local LLM support via **Ollama (llama3:latest)**
- SFIA 9 Knowledge Graph integration via Apache Jena Fuseki
- Multi-format file upload support (.txt, .pdf, .docx)
- Professionally rewritten job descriptions
- Real-time enhancement feedback
- Download enhanced JD functionality

### 🧠 **Knowledge Graph Integration**
- **SFIA 9 ontology** with 147+ skills and 28 categories
- SPARQL queries to Apache Jena Fuseki
- Searches skill labels, descriptions, and notes
- Semantic skill matching and relationship mapping
- Real-time KG health monitoring

### 💻 **Modern Tech Stack**
- **Frontend**: React 19, Vite, React Router
- **Backend**: Flask 3, SQLAlchemy, Flask-JWT-Extended
- **AI/ML**: LangChain, LangGraph, **Ollama (local LLM)**
- **Database**: SQLite (easily replaceable with PostgreSQL)
- **Knowledge Graph**: Apache Jena Fuseki, SPARQL, SFIA 9 RDF

---

## 📁 Project Structure

```
dechivo/
├── frontend/                    # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx             # Main app component with routing
│   │   ├── AuthContext.jsx     # Authentication state management
│   │   ├── ProtectedRoute.jsx  # Route protection component
│   │   ├── LandingPage.jsx     # Landing page with hero section
│   │   ├── LoginPage.jsx       # User login interface
│   │   ├── RegisterPage.jsx    # User registration interface
│   │   ├── EnhancementPage.jsx # Job description enhancement page
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/                     # Flask backend API
│   ├── app.py                  # Main Flask application
│   ├── models.py               # SQLAlchemy User model
│   ├── auth.py                 # Authentication decorators
│   ├── services/
│   │   ├── enhance_jd_service.py    # LangGraph JD enhancement workflow
│   │   ├── sfia_km_service.py       # SFIA knowledge graph SPARQL service
│   │   └── __init__.py
│   ├── prompts/
│   │   ├── enhance_jd_prompts.py    # LLM prompts (centralized)
│   │   └── __init__.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── knowledge-graph/             # Apache Jena Fuseki setup
│   ├── docker-compose.yml      # Docker config for Fuseki
│   ├── sfia9.ttl               # SFIA 9 RDF data
│   └── README.md
│
├── AUTHENTICATION_SUMMARY.md    # Authentication implementation docs
└── README.md                    # This file
```

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.8+
- **Ollama** with llama3 model installed
- **Docker** (for Apache Jena Fuseki)

### Installation & Setup

#### 1️⃣ **Start Knowledge Graph (Fuseki)**

```bash
cd knowledge-graph

# Start Fuseki with Docker
docker-compose up -d

# Load SFIA data (first time only)
curl -X POST http://localhost:3030/sfia/data \
  -H "Content-Type: text/turtle" \
  --data-binary @sfia9.ttl
```

**Fuseki runs on:** http://localhost:3030

#### 2️⃣ **Start Ollama LLM**

```bash
# Ensure Ollama is running with llama3
ollama run llama3:latest
```

**Ollama runs on:** http://localhost:11434

#### 3️⃣ **Backend Setup**

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Run the backend
python app.py
```

**Backend runs on:** http://localhost:5000

#### 4️⃣ **Frontend Setup**

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

**Frontend runs on:** http://localhost:5173

---

## 🔄 Enhancement Workflow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ 1. Extract      │ →  │ 2. Map to SFIA   │ →  │ 3. Set Skill    │ →  │ 4. Regenerate   │
│    Skills       │    │                  │    │    Levels       │    │    JD           │
│   (Ollama LLM)  │    │ (Knowledge Graph)│    │   (Rules-based) │    │   (Ollama LLM)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘
```

### Example Output

**Input:** "Senior Software Engineer with Python experience"

**Output:**
- **Keywords Extracted:** Python, software development, data analysis, agile...
- **SFIA Skills Mapped:** PROG (Programming), ARCH (Solution Architecture), DEMG (Delivery Management)
- **Levels Assigned:** Level 5-6 based on "Senior" indicator
- **Regenerated JD:** Professional job description with SFIA competencies embedded

---

## 🔌 API Endpoints

### **Health Endpoints**

```bash
# General health check
GET /api/health

# Knowledge Graph health check
GET /api/health/kg
# Response: { "connected": true, "stats": { "total_skills": 147, "total_categories": 28 } }
```

### **Authentication Endpoints**

```bash
# Register
POST /api/auth/register
{ "email": "user@example.com", "username": "user", "password": "pass123", "full_name": "User Name" }

# Login
POST /api/auth/login
{ "email_or_username": "user@example.com", "password": "pass123" }

# Refresh Token
POST /api/auth/refresh
Authorization: Bearer <refresh_token>

# Get Current User
GET /api/auth/me
Authorization: Bearer <access_token>

# Logout
POST /api/auth/logout
Authorization: Bearer <access_token>
```

### **Enhancement Endpoints** (Protected)

```bash
# Enhance Job Description
POST /api/enhance-jd
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "job_description": "Senior Software Engineer role requiring Python, cloud architecture..."
}

# Response:
{
  "success": true,
  "enhanced_jd": "# Enhanced Job Description...",
  "regenerated_jd": "# Professionally Rewritten JD...",
  "skills": [
    { "code": "PROG", "name": "Programming", "level": 5, "level_name": "Ensure/Advise" }
  ],
  "extracted_keywords": ["Python", "cloud", "architecture"],
  "knowledge_graph_connected": true
}
```

---

## ⚙️ Configuration

### Backend Environment Variables (.env)

```bash
# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000

# Database Configuration
DATABASE_URL=sqlite:///dechivo.db

# Ollama LLM Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3:latest

# Fuseki Knowledge Graph Configuration
FUSEKI_URL=http://localhost:3030
FUSEKI_DATASET=sfia
KG_ENABLED=true
KG_TIMEOUT=10

# OpenAI Configuration (optional fallback)
# OPENAI_API_KEY=your-openai-api-key-here
```

---

## 🎯 Key Technologies

| Category | Technologies |
|----------|-------------|
| **Frontend** | React 19, Vite, React Router DOM, Mammoth.js, PDF.js |
| **Backend** | Flask 3, Flask-CORS, Flask-JWT-Extended, Flask-SQLAlchemy |
| **AI/ML** | LangChain, LangGraph, **Ollama (llama3:latest)** |
| **Database** | SQLite (SQLAlchemy ORM) |
| **Security** | JWT, bcrypt, Token-based authentication |
| **Knowledge Graph** | Apache Jena Fuseki, SPARQL, SFIA 9 RDF/TTL |
| **Dev Tools** | ESLint, Python virtual environment, Docker |

---

## 📋 TODO & Future Enhancements

### Completed ✅
- [x] User authentication system with JWT
- [x] Automatic token refresh
- [x] Protected routes (frontend & backend)
- [x] Database integration with SQLAlchemy
- [x] Password hashing with bcrypt
- [x] **SFIA 9 Knowledge Graph integration (Fuseki)**
- [x] **Ollama LLM integration (local, no API key needed)**
- [x] **4-step LangGraph workflow**
- [x] **JD regeneration with SFIA skills**
- [x] File upload support (.txt, .pdf, .docx)
- [x] **Prompts centralized in separate file**
- [x] User profile UI

### In Progress 🚧
- [ ] Improve SFIA skill matching accuracy
- [ ] Add comprehensive unit tests
- [ ] Add API documentation (Swagger/OpenAPI)

### Future Features 🔮
- [ ] Email verification for new users
- [ ] Password reset functionality
- [ ] Save enhanced JDs to user account
- [ ] Job description history and versioning
- [ ] Export to multiple formats (PDF, DOCX, HTML)
- [ ] Analytics dashboard
- [ ] Integration with job posting platforms

---

## 🐛 Troubleshooting

### Ollama Not Connecting
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Pull llama3 if not available
ollama pull llama3:latest
```

### Knowledge Graph Not Finding Skills
1. Check Fuseki is running: http://localhost:3030
2. Verify SFIA data is loaded (147 skills expected)
3. Check backend logs for SPARQL errors

### Port 5000 Already in Use (macOS)
```bash
# Disable AirPlay Receiver in System Settings
# OR change port in backend/app.py
```

### Token Expired Errors
- Frontend now auto-refreshes tokens
- If issues persist, clear localStorage and login again

---

## 📄 License

© 2024-2025 Dechivo. All rights reserved.

---

## 📞 Support

- Authentication docs: [AUTHENTICATION_SUMMARY.md](AUTHENTICATION_SUMMARY.md)
- Backend docs: [backend/README.md](backend/README.md)
- Knowledge Graph docs: [knowledge-graph/README.md](knowledge-graph/README.md)

---

**Built with ❤️ using React, Flask, Ollama, and SFIA Knowledge Graph**
