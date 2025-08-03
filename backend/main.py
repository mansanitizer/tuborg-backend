from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import httpx
import os
import json
import csv
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import pandas as pd
from io import StringIO
from database import JobDatabase

load_dotenv()

# API Keys
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Cloud Run environment variable

app = FastAPI(title="Webhound API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173",  # React dev servers
        "https://webpuppy.netlify.app"  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQLite database
db = JobDatabase()

# Rate limiting storage (keeping in-memory for performance)
rate_limit_store = {}  # IP -> {count: int, reset_time: datetime}

# Rate limiting: 10 requests per hour per IP
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_HOURS = 1

# Request/Response Models
class DatasetGenerateRequest(BaseModel):
    query: str

class DatasetGenerateResponse(BaseModel):
    job_id: str
    status: str

class DatasetResult(BaseModel):
    job_id: str
    status: str
    query: str
    dataset: List[Dict[str, Any]]
    sources: List[str]
    total_records: int
    validation_status: Optional[str] = None
    quality_score: Optional[str] = None
    validation_notes: Optional[str] = None
    user_rating: Optional[str] = None

class RecentQuery(BaseModel):
    job_id: str
    query: str
    created_at: str
    status: str
    user_rating: Optional[str] = None

class UniqueRecentQuery(BaseModel):
    query: str
    last_asked: str
    times_asked: int

class RecentQueriesResponse(BaseModel):
    recent_queries: List[RecentQuery]
    unique_queries: List[UniqueRecentQuery]

class ErrorResponse(BaseModel):
    error: Dict[str, str]

# Add new models for feedback
class JobRatingRequest(BaseModel):
    rating: str  # "good_dog" or "bad_dog"

class JobRatingResponse(BaseModel):
    job_id: str
    rating: str
    success: bool
    message: str

class RatingStats(BaseModel):
    total_rated: int
    good_dogs: int
    bad_dogs: int
    good_percentage: float
    bad_percentage: float

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # For now, skip rate limiting to avoid issues
    # TODO: Implement proper rate limiting with database storage
    response = await call_next(request)
    return response

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Recent queries endpoint
@app.get("/api/queries/recent", response_model=RecentQueriesResponse)
async def get_recent_queries(limit: int = 10):
    """Get recent queries asked by users"""
    try:
        recent_queries = db.get_recent_queries(limit)
        unique_queries = db.get_unique_recent_queries(limit)
        
        return RecentQueriesResponse(
            recent_queries=[
                RecentQuery(
                    job_id=q['job_id'],
                    query=q['query'],
                    created_at=q['created_at'],
                    status=q['status'],
                    user_rating=q.get('user_rating')
                ) for q in recent_queries
            ],
            unique_queries=[
                UniqueRecentQuery(
                    query=q['query'],
                    last_asked=q['last_asked'],
                    times_asked=q['times_asked']
                ) for q in unique_queries
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent queries: {str(e)}")

# Raw data endpoint
@app.get("/api/datasets/{job_id}/raw")
async def get_raw_data(job_id: str):
    """Get raw JSON data for a specific job ID"""
    try:
        job = db.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        raw_data = job.get('raw_data', {})
        if not raw_data:
            raise HTTPException(status_code=404, detail="Raw data not found for this job")
        
        return {
            "job_id": job_id,
            "query": job.get('query', ''),
            "status": job.get('status', ''),
            "raw_data": raw_data,
            "created_at": job.get('created_at', ''),
            "updated_at": job.get('updated_at', '')
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get raw data: {str(e)}")

# Dataset generation endpoint (Ask phase)
@app.post("/api/datasets/generate", response_model=DatasetGenerateResponse)
async def generate_dataset(request: DatasetGenerateRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    
    # Create job in database
    db.create_job(job_id, request.query)
    
    # Start background processing
    background_tasks.add_task(process_dataset, job_id, request.query)
    
    return DatasetGenerateResponse(job_id=job_id, status="processing")

# Dataset results endpoint (Answer phase)
@app.get("/api/datasets/{job_id}/results", response_model=DatasetResult)
async def get_dataset_results(job_id: str):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return DatasetResult(
        job_id=job_id,
        status=job["status"],
        query=job["query"],
        dataset=job["dataset"] or [],
        sources=job["sources"] or [],
        total_records=job["total_records"] or 0,
        validation_status=job.get("validation_status"),
        quality_score=job.get("quality_score"),
        validation_notes=job.get("validation_notes"),
        user_rating=job.get("user_rating")
    )

# CSV download endpoint
@app.get("/api/datasets/{job_id}/download")
async def download_dataset_csv(job_id: str):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Dataset not ready for download")
    
    # Create CSV file
    csv_filename = f"webhound_dataset_{job_id}.csv"
    csv_path = f"/tmp/{csv_filename}"
    
    if job["dataset"]:
        df = pd.DataFrame(job["dataset"])
        df.to_csv(csv_path, index=False)
        
        return FileResponse(
            path=csv_path,
            filename=csv_filename,
            media_type="text/csv"
        )
    else:
        raise HTTPException(status_code=400, detail="No data to download")

# Background task to process dataset
async def process_dataset(job_id: str, query: str):
    try:
        # Use CrewAI for dataset creation
        from crewai_setup_working import create_dataset_async
        
        # Step 1: Process with CrewAI
        dataset = await create_dataset_async(query)
        
        # Step 2: Save raw data first
        db.update_job(
            job_id,
            raw_data=dataset
        )
        
        # Step 3: Check for quota error in the result
        if isinstance(dataset, dict) and dataset.get("validation_status") == "quota_exceeded":
            # Handle quota exceeded error
            db.update_job(
                job_id,
                status="quota_exceeded",
                dataset=[],
                sources=[],
                total_records=0,
                validation_status="quota_exceeded",
                quality_score="unknown",
                validation_notes="API quota exceeded. Please try again later or upgrade your plan."
            )
            return
        
        # Step 3: Parse the result structure - handle markdown JSON
        if isinstance(dataset, dict):
            # Check if data contains markdown-wrapped JSON
            raw_data = dataset.get("data", [])
            if raw_data and len(raw_data) > 0:
                first_item = raw_data[0]
                if isinstance(first_item, dict) and 'result' in first_item:
                    result_str = first_item['result']
                    
                    # Try to extract JSON from markdown code blocks
                    import re
                    import json
                    
                    code_block_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', result_str, re.DOTALL)
                    if code_block_match:
                        json_content = code_block_match.group(1).strip()
                        try:
                            parsed_json = json.loads(json_content)
                            # Extract the actual data from the parsed JSON
                            parsed_data = parsed_json.get("data", [])
                            sources = parsed_json.get("sources", [])
                            validation_status = parsed_json.get("validation_status", "completed")
                            quality_score = parsed_json.get("quality_score", "unknown")
                            validation_notes = parsed_json.get("validation_notes", "")
                        except json.JSONDecodeError:
                            # Fallback to original structure
                            parsed_data = raw_data
                            sources = dataset.get("sources", [])
                            validation_status = dataset.get("validation_status", "completed")
                            quality_score = dataset.get("quality_score", "unknown")
                            validation_notes = dataset.get("validation_notes", "")
                    else:
                        # No code block found, use original structure
                        parsed_data = raw_data
                        sources = dataset.get("sources", [])
                        validation_status = dataset.get("validation_status", "completed")
                        quality_score = dataset.get("quality_score", "unknown")
                        validation_notes = dataset.get("validation_notes", "")
                else:
                    # No result field, use original structure
                    parsed_data = raw_data
                    sources = dataset.get("sources", [])
                    validation_status = dataset.get("validation_status", "completed")
                    quality_score = dataset.get("quality_score", "unknown")
                    validation_notes = dataset.get("validation_notes", "")
            else:
                # No data, use original structure
                parsed_data = raw_data
                sources = dataset.get("sources", [])
                validation_status = dataset.get("validation_status", "completed")
                quality_score = dataset.get("quality_score", "unknown")
                validation_notes = dataset.get("validation_notes", "")
        else:
            # Fallback: create a simple data structure
            parsed_data = [{"query": query, "result": str(dataset)}]
            sources = []
            validation_status = "completed"
            quality_score = "unknown"
            validation_notes = "Processing completed"
        
        # Step 4: Update job with results
        db.update_job(
            job_id,
            status="completed",
            dataset=parsed_data,
            sources=sources,
            total_records=len(parsed_data),
            validation_status=validation_status,
            quality_score=quality_score,
            validation_notes=validation_notes
        )
        
    except Exception as e:
        error_message = str(e)
        
        # Check for specific quota-related errors
        if any(keyword in error_message.lower() for keyword in [
            "quota", "429", "resourceexhausted", "rate limit", "exceeded"
        ]):
            # Handle quota exceeded error
            db.update_job(
                job_id,
                status="quota_exceeded",
                dataset=[],
                sources=[],
                total_records=0,
                validation_status="quota_exceeded",
                quality_score="unknown",
                validation_notes=f"API quota exceeded: {error_message}. Please try again later or upgrade your plan."
            )
        else:
            # Handle other errors
            db.update_job(
                job_id,
                status="failed",
                dataset=[],
                sources=[],
                total_records=0,
                validation_status="failed",
                quality_score="unknown",
                validation_notes=f"Error: {error_message}"
            )

# Feedback endpoints
@app.post("/api/jobs/{job_id}/rate", response_model=JobRatingResponse)
async def rate_job(job_id: str, request: JobRatingRequest):
    """Rate a job as good_dog or bad_dog"""
    if request.rating not in ['good_dog', 'bad_dog']:
        raise HTTPException(
            status_code=400, 
            detail="Rating must be 'good_dog' or 'bad_dog'"
        )
    
    # Check if job exists
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Update the rating
    success = db.rate_job(job_id, request.rating)
    
    if success:
        return JobRatingResponse(
            job_id=job_id,
            rating=request.rating,
            success=True,
            message=f"Job rated as {request.rating}"
        )
    else:
        raise HTTPException(
            status_code=500, 
            detail="Failed to update rating"
        )

@app.get("/api/jobs/rating-stats", response_model=RatingStats)
async def get_rating_stats():
    """Get overall rating statistics"""
    stats = db.get_job_rating_stats()
    return RatingStats(**stats)

# Database management endpoints
@app.get("/api/admin/stats")
async def get_database_stats():
    """Get database statistics (admin endpoint)"""
    return db.get_job_stats()

@app.get("/api/admin/jobs")
async def get_all_jobs(limit: int = 100):
    """Get all jobs (admin endpoint)"""
    return {"jobs": db.get_all_jobs(limit)}

@app.delete("/api/admin/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a specific job (admin endpoint)"""
    success = db.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}

@app.post("/api/admin/cleanup")
async def cleanup_old_jobs(days: int = 30):
    """Clean up old jobs (admin endpoint)"""
    deleted_count = db.cleanup_old_jobs(days)
    return {"message": f"Deleted {deleted_count} old jobs"}

# CrewAI is now handling all the web search and LLM processing
# The old Tavily and Gemini functions have been replaced with CrewAI workflow

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port) 