# AI Codebase Explainer (Gemini-Powered)

An intelligent tool that analyzes GitHub repositories using Google Gemini AI to provide comprehensive codebase explanations, including architecture overview, folder structure, API flow, database models, auto-generated README files, and natural-language Q&A.

## Features

- 🏗️ **Architecture Explanation**: Get AI-generated overview of the codebase architecture and design patterns
- 📁 **Folder Structure Analysis**: Understand the organization and purpose of directories
- 🔌 **API Flow Documentation**: Automatically identify and explain API endpoints, routes, and authentication
- 💾 **Database/Models Analysis**: Discover database schemas, ORM usage, and entity relationships
- 📝 **Auto README Generation**: Generate professional README.md files automatically
- 💬 **Natural-Language Q&A**: Ask questions about the codebase in plain English

## Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **Frontend**: React + Vite
- **AI**: Google Gemini API
- **Repository Access**: Git clone (supports public GitHub repos)

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Git
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## Project Structure

```
ai-codebase-explainer/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # FastAPI app entry point
│   │   ├── config.py    # Configuration management
│   │   ├── api/         # API routes
│   │   ├── services/    # Business logic (repo, gemini)
│   │   └── models/      # Pydantic schemas
│   ├── requirements.txt
│   └── .env.example
├── frontend/            # React + Vite frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── api/        # API client
│   │   └── styles/     # CSS styles
│   ├── package.json
│   └── .env.example
├── .env.example         # Root environment variables
└── README.md
```

## Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd ai-codebase-explainer
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env if needed (default: http://localhost:8000)
# VITE_API_URL=http://localhost:8000
```

## Running the Application

### Start the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

The backend API will be available at `http://localhost:8000`

### Start the Frontend

```bash
cd frontend
npm run dev
```

The frontend will open at `http://localhost:5173` (or the port shown in terminal)

## Usage

1. **Open the frontend** in your browser (usually `http://localhost:5173`)
2. **Enter a GitHub repository URL** (e.g., `https://github.com/owner/repo`)
3. **Click "Analyze Repository"** to start the analysis
4. **View the results** in the tabs:
   - Architecture Overview
   - Folder Structure
   - API Flow
   - Database/Models
5. **Generate README**: Click "Generate README.md" to create a comprehensive README file
6. **Ask Questions**: Use the Q&A panel to ask natural language questions about the codebase

## Environment Variables

### Backend (.env)

- `GEMINI_API_KEY` (required): Your Google Gemini API key
- `GITHUB_TOKEN` (optional): GitHub token for private repositories
- `MAX_FILES` (optional, default: 200): Maximum number of files to analyze
- `MAX_FILE_SIZE_KB` (optional, default: 100): Maximum file size in KB
- `MAX_TOTAL_CHARS` (optional, default: 200000): Maximum total characters for analysis
- `CLONE_TIMEOUT` (optional, default: 60): Git clone timeout in seconds
- `BACKEND_PORT` (optional, default: 8000): Backend server port
- `CORS_ORIGINS` (optional): Comma-separated list of allowed CORS origins

### Frontend (.env)

- `VITE_API_URL` (optional, default: http://localhost:8000): Backend API URL

## API Endpoints

### POST `/api/analyze`

Analyze a GitHub repository.

**Request:**
```json
{
  "repo_url": "https://github.com/owner/repo",
  "branch": "main"  // optional
}
```

**Response:**
```json
{
  "architecture": "...",
  "folder_structure": "...",
  "api_flow": "...",
  "db_models": "...",
  "repo_url": "https://github.com/owner/repo",
  "total_files": 42,
  "total_chars": 12345
}
```

### POST `/api/generate-readme`

Generate a README.md file.

**Request:**
```json
{
  "repo_url": "https://github.com/owner/repo",  // or use cached analysis
  "analysis": { ... }  // optional, reuse previous analysis
}
```

### POST `/api/ask`

Ask a question about the codebase.

**Request:**
```json
{
  "question": "How does authentication work?",
  "repo_url": "https://github.com/owner/repo",  // or use cached analysis
  "analysis": { ... }  // optional
}
```

## Token and Safety Limits

The application includes several safety limits to manage token usage:

- **File limits**: Maximum number of files analyzed (default: 200)
- **File size limits**: Large files are truncated or skipped (default: 100KB)
- **Total character limit**: Caps total context sent to Gemini (default: 200k chars)
- **Clone timeout**: Prevents hanging on slow clones (default: 60s)
- **Binary file detection**: Automatically skips binary files
- **Gitignore support**: Respects `.gitignore` rules

## Error Handling

The application handles various error cases:

- Invalid GitHub URLs → 400 Bad Request
- Repository not found → 400 with clear message
- Private repositories → 400 (requires GITHUB_TOKEN)
- Clone failures → 502/503 with error details
- Missing API key → Startup validation error
- Gemini API errors → 503 with service unavailable message
- Empty repositories → 200 with "No code files found"

## Limitations

- Currently supports **public GitHub repositories only** (private repos require GITHUB_TOKEN)
- Analysis is limited by token constraints (see safety limits above)
- Very large repositories may be partially analyzed
- Requires internet connection for cloning and Gemini API calls

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

---

**Note**: Make sure you have a valid Gemini API key before running the application. Get your key at [Google AI Studio](https://makersuite.google.com/app/apikey).
