# Dechivo Backend API

Flask-based backend API for the Dechivo SFIA-based ICT Job Description Enhancement System.

## Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running the Application

### Development Mode
```bash
python app.py
```

The server will start on `http://localhost:5000`

### Production Mode
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

### Health Check
- **GET** `/api/health`
- Returns the health status of the API

### Enhance Job Description
- **POST** `/api/enhance-jd`
- Body: `{ "job_description": "your job description text" }`
- Enhances job description using SFIA framework

### Upload Job Description
- **POST** `/api/upload-jd`
- Content-Type: `multipart/form-data`
- Accepts file upload and returns content

## Testing

Test the API using curl:

```bash
# Health check
curl http://localhost:5000/api/health

# Enhance JD
curl -X POST http://localhost:5000/api/enhance-jd \
  -H "Content-Type: application/json" \
  -d '{"job_description": "Software Developer position..."}'
```

## Project Structure
```
backend/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## Environment Variables

- `SECRET_KEY`: Flask secret key for sessions
- `FLASK_ENV`: Environment mode (development/production)
- `FLASK_DEBUG`: Enable/disable debug mode
- `PORT`: Server port (default: 5000)

## CORS Configuration

CORS is enabled to allow frontend communication from different origins.

## TODO

- [ ] Implement actual SFIA framework integration
- [ ] Add database support
- [ ] Implement authentication
- [ ] Add rate limiting
- [ ] Add comprehensive error handling
- [ ] Add logging
- [ ] Add unit tests
- [ ] Add API documentation (Swagger/OpenAPI)
