# Dechivo - SFIA-Based ICT Job Description Enhancement System

[![React](https://img.shields.io/badge/React-19.2.0-blue.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

A **full-stack AI-powered application** for enhancing ICT job descriptions using the **SFIA (Skills Framework for the Information Age)** framework with integrated knowledge graph technology and LangChain/OpenAI integration.

---

## 🌟 Features

### 🔐 **User Authentication & Authorization**
- JWT-based authentication with access & refresh tokens
- Secure password hashing using bcrypt
- User registration and login system
- Protected routes (frontend & backend)
- User profile management with dropdown menu
- Token expiration (1 hour for access, 30 days for refresh)
- Persistent sessions with localStorage

### 🚀 **Job Description Enhancement**
- AI-powered job description enhancement using LangChain & OpenAI
- SFIA framework integration via knowledge graph
- SPARQL queries to fetch competencies from knowledge graph
- Multi-format file upload support (.txt, .pdf, .docx)
- Real-time enhancement feedback
- Download enhanced JD functionality
- Beautiful, responsive UI with modern design

### 🧠 **Knowledge Graph Integration**
- SFIA competency mapping using knowledge graphs
- SPARQL wrapper for querying RDF data
- Intelligent skill extraction and enhancement
- Semantic relationship mapping

### 💻 **Modern Tech Stack**
- **Frontend**: React 19, Vite, React Router
- **Backend**: Flask 3, SQLAlchemy, Flask-JWT-Extended
- **AI/ML**: LangChain, LangGraph, OpenAI
- **Database**: SQLite (easily replaceable with PostgreSQL)
- **Knowledge Graph**: SPARQL, RDF

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
│   │   ├── LandingPage.css
│   │   ├── LoginPage.jsx       # User login interface
│   │   ├── LoginPage.css
│   │   ├── RegisterPage.jsx    # User registration interface
│   │   ├── RegisterPage.css
│   │   ├── EnhancementPage.jsx # Job description enhancement page
│   │   ├── EnhancementPage.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/                     # Flask backend API
│   ├── app.py                  # Main Flask application
│   ├── models.py               # SQLAlchemy User model
│   ├── auth.py                 # Authentication decorators
│   ├── services/
│   │   ├── enhance_jd_service.py    # JD enhancement logic
│   │   ├── sfia_km_service.py       # SFIA knowledge graph service
│   │   └── __init__.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── data/                        # Data files (CSV, RDF, etc.)
├── knowledge-graph/             # Knowledge graph resources
├── AUTHENTICATION_SUMMARY.md    # Authentication implementation docs
└── README.md                    # This file
```

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.8+
- **pip** (Python package manager)
- **OpenAI API Key** (for AI enhancement features)

### Installation & Setup

#### 1️⃣ **Backend Setup**

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env and add your OpenAI API key and other configurations

# Run the backend
python app.py
```

**Backend runs on:** http://localhost:5000 (or http://localhost:5001 if port 5000 is busy)

#### 2️⃣ **Frontend Setup**

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

**Frontend runs on:** http://localhost:5173

### 3️⃣ **Access the Application**
Open your browser and navigate to: **http://localhost:5173**

---

## 📖 User Guide

### First Time User Flow
1. Visit http://localhost:5173
2. Click **"Sign Up"** in the header
3. Fill in the registration form (email, username, password, full name, organization)
4. Automatically logged in and redirected to `/enhance`
5. Start enhancing job descriptions! 🎉

### Returning User Flow
1. Visit http://localhost:5173
2. Click **"Login"** in the header
3. Enter your email/username and password
4. Redirected to `/enhance`

### Using the Enhancement Feature
1. In the `/enhance` page, **upload a file** (.txt, .pdf, .docx) or **type/paste** a job description
2. Click **"Publish"** to enhance it
3. View the enhanced JD with SFIA competencies
4. Click **"Download"** to save the enhanced JD
5. Click the user menu (top right) to see your profile or logout

---

## 🔌 API Endpoints

### **Authentication Endpoints**

#### Register User
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "securepassword",
  "full_name": "John Doe",
  "organization": "Company Inc."
}
```

#### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email_or_username": "user@example.com",
  "password": "securepassword"
}

# Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": { ... }
}
```

#### Refresh Token
```bash
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

#### Get Current User
```bash
GET /api/auth/me
Authorization: Bearer <access_token>
```

#### Logout
```bash
POST /api/auth/logout
Authorization: Bearer <access_token>
```

### **Job Description Endpoints** (Protected)

#### Health Check
```bash
GET /api/health
```

#### Enhance Job Description
```bash
POST /api/enhance-jd
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "job_description": "Software Engineer role requiring Python, JavaScript..."
}
```

#### Upload File
```bash
POST /api/upload-jd
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <your-file.pdf|.txt|.docx>
```

---

## 🛠️ Development

### Frontend Development
- **React 19** with modern hooks and context API
- **Vite** for blazing-fast HMR (Hot Module Replacement)
- **React Router** for client-side routing
- **Modern ES6+** JavaScript with async/await
- **Responsive CSS** with animations and gradients

### Backend Development
- **Flask 3.0** with RESTful API architecture
- **SQLAlchemy ORM** for database operations
- **JWT authentication** with Flask-JWT-Extended
- **CORS** enabled for cross-origin requests
- **Service-oriented architecture** with separate service modules
- **LangChain & LangGraph** for AI workflow orchestration
- **SPARQL queries** for knowledge graph integration

### Database Schema

#### User Model
```python
class User(db.Model):
    id: int                    # Primary key
    email: str                 # Unique email
    username: str              # Unique username
    password_hash: str         # Bcrypt hashed password
    full_name: str             # Full name
    organization: str          # Organization name
    role: str                  # User role (default: 'user')
    is_active: bool            # Active status
    created_at: datetime       # Registration timestamp
    updated_at: datetime       # Last update timestamp
    last_login: datetime       # Last login timestamp
```

---

## 🧪 Testing

### Test API with cURL

#### Register
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User",
    "organization": "Test Corp"
  }'
```

#### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_username": "testuser",
    "password": "password123"
  }'
```

#### Enhance JD (with authentication)
```bash
curl -X POST http://localhost:5000/api/enhance-jd \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "job_description": "Software Engineer position requiring Python experience..."
  }'
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

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# CORS Configuration (optional)
ALLOWED_ORIGINS=http://localhost:5173
```

---

## 🎯 Key Technologies

| Category | Technologies |
|----------|-------------|
| **Frontend** | React 19, Vite, React Router DOM, Mammoth.js, PDF.js |
| **Backend** | Flask 3, Flask-CORS, Flask-JWT-Extended, Flask-SQLAlchemy |
| **AI/ML** | LangChain, LangGraph, OpenAI GPT, LangChain-OpenAI |
| **Database** | SQLite (SQLAlchemy ORM) |
| **Security** | JWT, bcrypt, Token-based authentication |
| **Knowledge Graph** | SPARQL, SPARQLWrapper, RDF |
| **Dev Tools** | ESLint, Python virtual environment, Gunicorn |

---

## 📋 TODO & Future Enhancements

### Completed ✅
- [x] User authentication system
- [x] JWT-based token management
- [x] Protected routes (frontend & backend)
- [x] Database integration with SQLAlchemy
- [x] Password hashing with bcrypt
- [x] SFIA knowledge graph integration
- [x] LangChain/OpenAI integration
- [x] File upload support (.txt, .pdf, .docx)
- [x] User profile UI
- [x] Modern, responsive design

### In Progress 🚧
- [ ] Replace mock SFIA data with complete knowledge graph
- [ ] Add comprehensive unit tests
- [ ] Add API documentation (Swagger/OpenAPI)

### Future Features 🔮
- [ ] Email verification for new users
- [ ] Password reset functionality
- [ ] User profile editing page
- [ ] Role-based access control (admin features)
- [ ] Save enhanced JDs to user account
- [ ] Job description history and versioning
- [ ] Team collaboration features
- [ ] Export to multiple formats (PDF, DOCX, HTML)
- [ ] Job description comparison feature
- [ ] Batch processing for multiple JDs
- [ ] Analytics dashboard
- [ ] Integration with job posting platforms

---

## 🐛 Troubleshooting

### Port 5000 Already in Use (macOS)
**Issue:** AirPlay Receiver uses port 5000 by default on macOS 12+

**Solution:**
1. Go to **System Settings** → **General** → **AirDrop & Handoff**
2. Disable **AirPlay Receiver**

**Alternative:** Change the port in `backend/app.py`:
```python
port = int(os.getenv('PORT', 5001))  # Change to 5001
```

### Authentication Not Working
1. Ensure backend is running on http://localhost:5000
2. Clear browser localStorage: `localStorage.clear()`
3. Check browser console for errors (F12)
4. Verify JWT tokens are being sent in headers

### Database Errors
1. Delete `backend/instance/dechivo.db`
2. Restart the backend server
3. Database tables will be recreated automatically

### OpenAI API Errors
1. Verify your OpenAI API key in `.env`
2. Check your OpenAI account has available credits
3. Review the backend logs for specific error messages

---

## 📄 License

© 2024-2025 Dechivo. All rights reserved.

---

## 👨‍💻 Contributing

This is a private project. For inquiries, please contact the maintainers.

---

## 📞 Support

For detailed authentication implementation information, see [AUTHENTICATION_SUMMARY.md](AUTHENTICATION_SUMMARY.md)

For backend-specific documentation, see [backend/README.md](backend/README.md)

---

**Built with ❤️ using React, Flask, and AI**
