# Dechivo C4 Architecture Document

## Overview

Dechivo is an AI-powered job description enhancement platform that uses the SFIA (Skills Framework for the Information Age) knowledge graph to map skills and competencies. The system leverages LLMs (OpenAI/Ollama) and a SPARQL-based knowledge graph to provide intelligent skill mapping for job descriptions.

---

## Level 1: System Context Diagram

```mermaid
C4Context
    title System Context Diagram - Dechivo

    Person(user, "HR Professional", "Creates and enhances job descriptions with SFIA skills")
    
    System(dechivo, "Dechivo Platform", "AI-powered SFIA skill mapping for job descriptions")
    
    System_Ext(openai, "OpenAI API", "GPT-4o-mini for skill extraction and JD regeneration")
    System_Ext(mixpanel, "Mixpanel EU", "Product analytics and session recording")
    
    Rel(user, dechivo, "Uses", "HTTPS")
    Rel(dechivo, openai, "Extracts skills, generates JDs", "HTTPS/REST")
    Rel(dechivo, mixpanel, "Sends analytics events", "HTTPS")
```

### Context Description

| Element | Type | Description |
|---------|------|-------------|
| HR Professional | User | End users who create and enhance job descriptions |
| Dechivo Platform | System | Main application providing SFIA skill mapping |
| OpenAI API | External System | LLM service for AI-powered text processing |
| Mixpanel EU | External System | Analytics platform for tracking user behavior |

---

## Level 2: Container Diagram

```mermaid
C4Container
    title Container Diagram - Dechivo Platform

    Person(user, "HR Professional", "Creates JDs with SFIA skills")
    
    Container_Boundary(dechivo, "Dechivo Platform") {
        Container(spa, "Web Application", "React + Vite", "Single-page application for JD enhancement")
        Container(api, "Backend API", "Flask + Gunicorn", "REST API for authentication and enhancement")
        Container(fuseki, "Knowledge Graph", "Apache Jena Fuseki", "SFIA ontology and skill database")
        ContainerDb(db, "Database", "SQLite", "User accounts and session data")
    }
    
    Container_Boundary(infra, "Infrastructure") {
        Container(nginx, "Reverse Proxy", "Nginx", "SSL termination, static file serving, API proxy")
    }
    
    System_Ext(openai, "OpenAI API", "LLM Service")
    System_Ext(mixpanel, "Mixpanel EU", "Analytics")
    
    Rel(user, nginx, "Uses", "HTTPS")
    Rel(nginx, spa, "Serves", "Static Files")
    Rel(nginx, api, "Proxies", "HTTP/5000")
    Rel(spa, api, "API calls", "REST/JSON")
    Rel(spa, mixpanel, "Frontend events", "HTTPS")
    Rel(api, fuseki, "SPARQL queries", "HTTP/3030")
    Rel(api, db, "Reads/Writes", "SQL")
    Rel(api, openai, "LLM requests", "HTTPS")
    Rel(api, mixpanel, "Backend events", "HTTPS")
```

### Container Descriptions

| Container | Technology | Purpose |
|-----------|------------|---------|
| **Web Application** | React 18 + Vite 7 | Interactive SPA for JD creation, org context input, and enhancement |
| **Backend API** | Flask 3.0 + Gunicorn | REST API handling auth, enhancement workflow, and business logic |
| **Knowledge Graph** | Apache Jena Fuseki | SFIA ontology storage and SPARQL query endpoint |
| **Database** | SQLite | User authentication, profiles, and session management |
| **Reverse Proxy** | Nginx | SSL termination, static hosting, API routing |

---

## Level 3: Component Diagram - Backend API

```mermaid
C4Component
    title Component Diagram - Backend API

    Container_Boundary(api, "Backend API (Flask)") {
        Component(auth, "Auth Module", "Flask-JWT-Extended", "User registration, login, token management")
        Component(enhance, "Enhancement Service", "LangGraph", "JD enhancement workflow orchestration")
        Component(sfia, "SFIA KM Service", "SPARQLWrapper", "Knowledge graph queries and skill mapping")
        Component(prompts, "Prompt Templates", "Python", "LLM prompt engineering for skill extraction")
        Component(analytics, "Analytics Module", "Mixpanel SDK", "Backend event tracking")
        Component(models, "Data Models", "SQLAlchemy", "User and session models")
    }
    
    Container(fuseki, "Fuseki", "Knowledge Graph")
    Container(db, "SQLite", "Database")
    System_Ext(openai, "OpenAI", "LLM")
    System_Ext(mixpanel, "Mixpanel", "Analytics")
    
    Rel(auth, models, "Uses")
    Rel(auth, db, "Queries")
    Rel(enhance, sfia, "Gets SFIA skills")
    Rel(enhance, prompts, "Uses prompts")
    Rel(enhance, openai, "LLM calls")
    Rel(enhance, analytics, "Tracks events")
    Rel(sfia, fuseki, "SPARQL queries")
    Rel(analytics, mixpanel, "Sends events")
```

### Component Descriptions

| Component | Responsibility |
|-----------|----------------|
| **Auth Module** | JWT-based authentication, user registration, login/logout, token refresh |
| **Enhancement Service** | LangGraph workflow: Extract Keywords → Map to SFIA → Set Levels → Regenerate JD |
| **SFIA KM Service** | SPARQL queries to Fuseki, skill search by keyword, category, and description |
| **Prompt Templates** | Skill extraction and JD regeneration prompts with org context integration |
| **Analytics Module** | Mixpanel integration for tracking success rates, processing times, errors |
| **Data Models** | SQLAlchemy ORM for User entity with bcrypt password hashing |

---

## Level 3: Component Diagram - Frontend

```mermaid
C4Component
    title Component Diagram - Frontend (React)

    Container_Boundary(spa, "Web Application (React)") {
        Component(landing, "Landing Page", "React Component", "Hero, file upload, user onboarding")
        Component(enhance, "Enhancement Page", "React Component", "JD editor, org context form, enhancement")
        Component(auth_ctx, "Auth Context", "React Context", "Authentication state, token management")
        Component(analytics, "Analytics Module", "JavaScript", "Mixpanel event tracking")
        Component(auth_pages, "Auth Pages", "React Components", "Login and Registration forms")
    }
    
    Container(api, "Backend API", "REST API")
    System_Ext(mixpanel, "Mixpanel", "Analytics")
    
    Rel(landing, enhance, "Navigates with file")
    Rel(enhance, auth_ctx, "Uses for API calls")
    Rel(enhance, analytics, "Tracks events")
    Rel(auth_ctx, api, "Auth API calls")
    Rel(auth_ctx, analytics, "Login/Logout events")
    Rel(auth_pages, auth_ctx, "Login/Register")
    Rel(analytics, mixpanel, "Sends events")
```

### Frontend Component Descriptions

| Component | File | Responsibility |
|-----------|------|----------------|
| **Landing Page** | `LandingPage.jsx` | Marketing hero, file upload, CTA |
| **Enhancement Page** | `EnhancementPage.jsx` | JD textarea, org context form, enhance/download actions |
| **Auth Context** | `AuthContext.jsx` | JWT token management, auto-refresh, authenticated fetch |
| **Analytics** | `analytics.js` | Mixpanel tracking utilities |
| **Auth Pages** | `LoginPage.jsx`, `RegisterPage.jsx` | User authentication forms |

---

## Level 4: Code - Enhancement Workflow

```mermaid
stateDiagram-v2
    [*] --> ExtractSkills: Job Description Input
    
    ExtractSkills --> MapToSFIA: Keywords extracted
    ExtractSkills: LLM extracts skill keywords
    ExtractSkills: from job description text
    
    MapToSFIA --> SetSkillLevel: SFIA skills matched
    MapToSFIA: Query Knowledge Graph
    MapToSFIA: Match keywords to SFIA skills
    
    SetSkillLevel --> RegenerateJD: Levels assigned
    SetSkillLevel: Detect seniority from JD
    SetSkillLevel: Assign SFIA levels 1-7
    
    RegenerateJD --> [*]: Enhanced JD
    RegenerateJD: LLM regenerates JD with
    RegenerateJD: SFIA skills + org context
```

### Enhancement Workflow Code Structure

```python
# enhance_jd_service.py - LangGraph Workflow

class EnhancementState(TypedDict):
    job_description: str
    org_context: Dict[str, Any]
    extracted_keywords: List[str]
    sfia_skills: List[Dict]
    enhanced_skills: List[Dict]
    regenerated_jd: str

class JobDescriptionEnhancer:
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(EnhancementState)
        workflow.add_node("extract_skills", self.extract_skills_node)
        workflow.add_node("map_to_sfia", self.map_to_sfia_node)
        workflow.add_node("set_skill_level", self.set_skill_level_node)
        workflow.add_node("regenerate_jd", self.regenerate_jd_node)
        
        workflow.set_entry_point("extract_skills")
        workflow.add_edge("extract_skills", "map_to_sfia")
        workflow.add_edge("map_to_sfia", "set_skill_level")
        workflow.add_edge("set_skill_level", "regenerate_jd")
        workflow.add_edge("regenerate_jd", END)
        
        return workflow.compile()
```

---

## Data Flow Diagram

```mermaid
flowchart LR
    subgraph User
        A[HR Professional]
    end
    
    subgraph Frontend
        B[React SPA]
        C[Auth Context]
        D[Analytics.js]
    end
    
    subgraph Backend
        E[Flask API]
        F[Enhancement Service]
        G[SFIA KM Service]
        H[Analytics.py]
    end
    
    subgraph External
        I[(Fuseki KG)]
        J[OpenAI API]
        K[Mixpanel EU]
    end
    
    A -->|Upload JD + Org Context| B
    B -->|JWT Auth| C
    C -->|API Request| E
    E -->|Start Workflow| F
    F -->|Extract Keywords| J
    F -->|Query Skills| G
    G -->|SPARQL| I
    F -->|Regenerate JD| J
    F -->|Track Success| H
    H -->|Events| K
    B -->|Track UI Events| D
    D -->|Events| K
    E -->|Enhanced JD| B
    B -->|Display Result| A
```

---

## Deployment Architecture

```mermaid
flowchart TB
    subgraph Internet
        U[User Browser]
    end
    
    subgraph VPS["VPSDime Server (185.7.81.154)"]
        subgraph Docker["Docker Compose"]
            N[Nginx :443/:80]
            F[Fuseki :3030]
        end
        
        subgraph Systemd["Systemd Services"]
            G[Gunicorn :5000]
        end
        
        subgraph Files["File System"]
            S[/var/www/dechivo]
            D[/opt/dechivo]
            DB[(SQLite DB)]
        end
    end
    
    subgraph External["External Services"]
        O[OpenAI API]
        M[Mixpanel EU]
        GH[GitHub]
    end
    
    U -->|HTTPS| N
    N -->|Static Files| S
    N -->|/api/*| G
    G -->|SPARQL| F
    G -->|LLM| O
    G -->|Analytics| M
    G -->|SQLite| DB
    GH -->|CI/CD Deploy| D
```

---

## Technology Stack Summary

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.x | UI Framework |
| Vite | 7.x | Build Tool |
| React Router | 6.x | Client-side Routing |
| Mammoth.js | - | DOCX Parsing |
| PDF.js | - | PDF Parsing |
| Mixpanel Browser | - | Analytics |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Flask | 3.0.0 | Web Framework |
| Gunicorn | 21.2.0 | WSGI Server |
| LangGraph | 0.2.x | Workflow Orchestration |
| LangChain | 0.3.x | LLM Integration |
| SPARQLWrapper | 2.0.0 | Knowledge Graph Client |
| Flask-JWT-Extended | 4.6.0 | Authentication |
| SQLAlchemy | 3.1.1 | ORM |
| Mixpanel | 4.10.0 | Analytics |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| Nginx | Reverse Proxy, SSL |
| Apache Jena Fuseki | SFIA Knowledge Graph |
| Docker Compose | Container Orchestration |
| Systemd | Service Management |
| Let's Encrypt | SSL Certificates |
| GitHub Actions | CI/CD |

### External Services
| Service | Purpose |
|---------|---------|
| OpenAI API (gpt-4o-mini) | LLM for skill extraction and JD generation |
| Mixpanel EU | Product analytics and session recording |
| GitHub | Source control and CI/CD |

---

## Security Considerations

1. **Authentication**: JWT-based with access/refresh token pattern
2. **Password Storage**: bcrypt hashing
3. **SSL/TLS**: All traffic encrypted via Let's Encrypt certificates
4. **API Security**: Protected endpoints require valid JWT
5. **CORS**: Configured for production domain only
6. **Environment Variables**: Sensitive config stored in `.env` files

---

## Scalability Path

1. **Database**: Migrate SQLite → PostgreSQL for multi-user scaling
2. **Caching**: Add Redis for session and SPARQL query caching
3. **LLM**: Switch to Azure OpenAI for enterprise SLAs
4. **Knowledge Graph**: Cluster Fuseki or migrate to Neptune/Stardog
5. **Deployment**: Kubernetes for horizontal scaling

---

*Document Version: 1.0*
*Last Updated: 2026-01-04*
*Author: Dechivo Team*
