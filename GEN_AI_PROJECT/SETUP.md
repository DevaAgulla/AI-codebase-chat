# Quick Setup Guide

## Environment Files

### Backend `.env` file
Create `backend/.env` with:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

Optional variables:
```
GITHUB_TOKEN=your_github_token_here
MAX_FILES=200
MAX_FILE_SIZE_KB=100
MAX_TOTAL_CHARS=200000
CLONE_TIMEOUT=60
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend `.env` file
Create `frontend/.env` with:
```
VITE_API_URL=http://localhost:8000
```

## Quick Start

1. **Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   # Create .env file with GEMINI_API_KEY
   uvicorn app.main:app --reload
   ```

2. **Frontend:**
   ```bash
   cd frontend
   npm install
   # Create .env file (optional, defaults to http://localhost:8000)
   npm run dev
   ```

3. **Open browser:** http://localhost:5173

## Get Your Gemini API Key

Visit: https://makersuite.google.com/app/apikey
