# Webhound Backend

A FastAPI-based backend for the Webhound dataset generation service with SQLite database integration.

## Quick Start

### Using Reset Scripts (Recommended)

**For regular development:**
```bash
./quick_reset.sh
```

**For complete reset/troubleshooting:**
```bash
./reset_backend.sh
```

### Manual Setup

1. **Activate virtual environment:**
```bash
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Start the server:**
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Features

- ✅ **SQLite Database**: Persistent job storage
- ✅ **CrewAI Integration**: AI-powered dataset generation
- ✅ **RESTful API**: FastAPI with automatic documentation
- ✅ **Background Processing**: Async job processing
- ✅ **Admin Endpoints**: Database management and statistics
- ✅ **CSV Export**: Download generated datasets
- ✅ **Rate Limiting**: Request throttling (temporarily disabled)

## API Endpoints

### Core Endpoints
- `POST /api/datasets/generate` - Create new dataset generation job
- `GET /api/datasets/{job_id}/results` - Get job results
- `GET /api/datasets/{job_id}/download` - Download CSV file
- `GET /api/health` - Health check

### Admin Endpoints
- `GET /api/admin/stats` - Database statistics
- `GET /api/admin/jobs` - List all jobs
- `DELETE /api/admin/jobs/{job_id}` - Delete specific job
- `POST /api/admin/cleanup` - Cleanup old jobs

## Database

The backend uses SQLite for persistent storage:

- **File**: `webhound.db` (created automatically)
- **Schema**: Jobs table with JSON serialization
- **Features**: ACID compliance, indexed queries, admin tools

## Environment Variables

Create a `.env` file with:
```env
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

## Development

### Reset Scripts

Use the provided reset scripts for clean restarts:

- **`quick_reset.sh`**: Fast development restarts
- **`reset_backend.sh`**: Complete environment reset

### Manual Reset
```bash
# Kill processes
pkill -f uvicorn
pkill -f "python.*main"

# Clean cache
rm -rf __pycache__

# Start server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Documentation

- **`SQLITE_INTEGRATION.md`**: Complete database integration guide
- **`BACKEND_SCRIPTS.md`**: Reset script documentation
- **`SQLITE_CHANGES_SUMMARY.md`**: Integration change summary

## Troubleshooting

### Server Won't Start
1. Use `./reset_backend.sh` for complete reset
2. Check if port 8000 is available: `lsof -i :8000`
3. Verify virtual environment is activated
4. Check dependencies: `pip check`

### Database Issues
1. Remove database: `rm webhound.db`
2. Run full reset: `./reset_backend.sh`

### API Errors
1. Check server logs for detailed error messages
2. Verify API keys in `.env` file
3. Test with health endpoint: `curl http://localhost:8000/api/health`

## Project Structure

```
backend/
├── main.py                 # FastAPI application
├── database.py            # SQLite database layer
├── crewai_setup_working.py # CrewAI integration
├── requirements.txt       # Python dependencies
├── reset_backend.sh       # Full reset script
├── quick_reset.sh         # Quick reset script
├── .env                   # Environment variables
└── webhound.db           # SQLite database (auto-created)
```

## API Documentation

Once the server is running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc
- **OpenAPI schema**: http://localhost:8000/openapi.json 