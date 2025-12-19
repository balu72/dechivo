# Dechivo - SFIA-Based ICT Job Description Enhancement System

A full-stack application for enhancing ICT job descriptions using the SFIA (Skills Framework for the Information Age) framework.

## Project Structure

```
dechivo/
├── frontend/          # React + Vite frontend
│   ├── src/
│   │   ├── LandingPage.jsx
│   │   ├── EnhancementPage.jsx
│   │   └── App.jsx
│   └── package.json
└── backend/           # Flask backend API
    ├── app.py
    ├── requirements.txt
    └── README.md
```

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- pip (Python package manager)

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Backend runs on: http://localhost:5000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on: http://localhost:5173

### Access the Application
Open your browser and navigate to: http://localhost:5173

## Features

### Frontend
- ✅ Modern React UI with responsive design
- ✅ Landing page with hero section
- ✅ Job description enhancement page
- ✅ Real-time backend communication
- ✅ File upload support
- ✅ Backend message display
- ✅ Download enhanced JD

### Backend
- ✅ Flask REST API
- ✅ CORS enabled for frontend communication
- ✅ Job description enhancement endpoint
- ✅ File upload endpoint
- ✅ Health check endpoint

## API Endpoints

### Health Check
```bash
GET http://localhost:5000/api/health
```

### Enhance Job Description
```bash
POST http://localhost:5000/api/enhance-jd
Content-Type: application/json

{
  "job_description": "Your job description text here"
}
```

### Upload File
```bash
POST http://localhost:5000/api/upload-jd
Content-Type: multipart/form-data

file: [your file]
```

## Development

### Frontend Development
- Uses Vite for fast HMR (Hot Module Replacement)
- React Router for navigation
- Modern ES6+ JavaScript

### Backend Development
- Flask with CORS support
- RESTful API architecture
- JSON responses

## Testing the Integration

1. Start both frontend and backend servers
2. Navigate to http://localhost:5173
3. Click "Enhance JD" button
4. Enter or type a job description in the textarea
5. Click the "Publish" button
6. Watch the backend message area for status updates
7. See the enhanced job description appear

## Environment Variables

### Backend (.env)
```
SECRET_KEY=your-secret-key
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

## TODO

- [ ] Implement actual SFIA framework integration
- [ ] Add user authentication
- [ ] Add database support
- [ ] Implement job description templates
- [ ] Add export to multiple formats (PDF, DOCX)
- [ ] Add job description comparison feature
- [ ] Implement role-based access control

## License

© 2024 Dechivo. All rights reserved.
