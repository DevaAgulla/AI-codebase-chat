# AI Codebase Explainer - Backend

FastAPI backend for analyzing GitHub repositories with Google Gemini AI.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and set your `GEMINI_API_KEY`:
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

3. Run the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `POST /api/analyze` - Analyze a GitHub repository
- `POST /api/generate-readme` - Generate README.md
- `POST /api/ask` - Ask questions about the codebase

See the main README.md for detailed usage.
