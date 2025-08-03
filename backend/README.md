# Webhound Backend

A FastAPI-based backend for the Webhound AI-powered dataset builder, featuring CrewAI multi-agent workflows for research, data extraction, and validation.

## Features

- **CrewAI Multi-Agent Workflow**: Three specialized agents working together
  - Web Research Specialist: Searches and researches queries
  - Data Extraction Specialist: Extracts and structures data
  - Data Quality Assurance Specialist: Validates and quality-checks data
- **FastAPI REST API**: Clean, modern API with comprehensive endpoints
- **SQLite Database**: Lightweight, file-based database for job storage
- **Async Processing**: Background task processing for non-blocking operations
- **Query Preprocessing**: Security guardrails against misuse and inappropriate content
- **User Feedback System**: "Good dog" / "Bad dog" rating system
- **Comprehensive Error Handling**: Graceful handling of API quotas and processing errors

## Architecture

### Core Components

1. **CrewAI Setup** (`crewai_setup_working.py`)
   - Multi-agent workflow orchestration
   - Google Gemini 1.5 Flash integration
   - Sequential task processing

2. **FastAPI Application** (`main.py`)
   - REST API endpoints
   - Background task processing
   - Request validation and preprocessing

3. **Database Layer** (`database.py`)
   - SQLite database management
   - Job storage and retrieval
   - User feedback tracking

## API Endpoints

### Core Endpoints
- `POST /api/datasets/generate` - Submit a new dataset generation request
- `GET /api/datasets/{job_id}/results` - Get results for a specific job
- `GET /api/queries/recent` - Get recent queries with job IDs
- `GET /api/health` - Health check endpoint

### Feedback System
- `POST /api/jobs/{job_id}/rate` - Rate a job (good dog / bad dog)
- `GET /api/jobs/rating-stats` - Get overall rating statistics

### Admin Endpoints
- `GET /api/admin/preprocessing-stats` - Get preprocessing statistics
- `POST /api/admin/test-preprocessing` - Test preprocessing with sample queries

## Setup and Installation

### Prerequisites
- Python 3.8+
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mansanitizer/tuborg-backend.git
   cd tuborg-backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

4. **Initialize the database**
   ```bash
   python -c "from database import JobDatabase; JobDatabase().init_db()"
   ```

5. **Start the server**
   ```bash
   python main.py
   ```

The server will start on `http://localhost:8000`

## Usage

### Basic Dataset Generation

```bash
curl -X POST "http://localhost:8000/api/datasets/generate" \
     -H "Content-Type: application/json" \
     -d '{"query": "top 10 movies 2025"}'
```

### Check Job Status

```bash
curl "http://localhost:8000/api/datasets/{job_id}/results"
```

### Rate a Job

```bash
curl -X POST "http://localhost:8000/api/jobs/{job_id}/rate" \
     -H "Content-Type: application/json" \
     -d '{"rating": "good_dog"}'
```

## Data Flow

1. **Query Submission**: Frontend submits query via `/api/datasets/generate`
2. **Preprocessing**: Query is validated and cleaned for security
3. **Background Processing**: CrewAI workflow runs asynchronously
4. **Data Extraction**: Agents research, extract, and validate data
5. **JSON Parsing**: Markdown-wrapped JSON is parsed into structured data
6. **Database Storage**: Results are stored in SQLite database
7. **API Response**: Frontend receives structured dataset via `/api/datasets/{job_id}/results`

## Security Features

- **Query Preprocessing**: Blocks NSFW content, prompt injection, and oversized queries
- **Agent-Level Safety**: Backup safety checks within the Web Research Agent
- **Request Size Limits**: 10KB limit on incoming requests
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection

## Error Handling

- **API Quota Management**: Graceful handling of Google Gemini API quota limits
- **Processing Failures**: Comprehensive error logging and user-friendly error messages
- **Database Errors**: Robust error handling for database operations
- **Network Issues**: Retry logic for external API calls

## Development

### Testing

Run the test scripts to verify functionality:

```bash
python test_api_response.py
python test_new_query_simple.py
```

### Debugging

Use the debug scripts to inspect data:

```bash
python check_latest_job.py
python debug_crewai_raw.py
```

### Database Management

```bash
# Reset database
python -c "from database import JobDatabase; import os; os.remove('webhound.db') if os.path.exists('webhound.db') else None; JobDatabase().init_db()"
```

## Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Your Google Gemini API key
- `DATABASE_PATH`: Path to SQLite database (default: `webhound.db`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

### CrewAI Configuration

The CrewAI setup can be customized in `crewai_setup_working.py`:
- Model selection (currently using `gemini-1.5-flash`)
- Agent roles and goals
- Task descriptions and workflows
- Tool integrations

## Troubleshooting

### Common Issues

1. **API Quota Exceeded**: The system will retry with exponential backoff
2. **Database Errors**: Check file permissions and disk space
3. **Import Errors**: Ensure all dependencies are installed
4. **Parsing Issues**: Check the debug scripts for data structure analysis

### Logs

Check the console output for detailed error messages and processing logs.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 