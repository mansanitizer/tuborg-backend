# SQLite Database Integration for Webhound

## Overview

The Webhound backend has been upgraded from in-memory job storage to a persistent SQLite database. This provides data persistence, better scalability, and improved reliability for production use.

## Database Schema

### Jobs Table

```sql
CREATE TABLE jobs (
    job_id TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    status TEXT NOT NULL,
    dataset TEXT,                    -- JSON serialized dataset
    sources TEXT,                    -- JSON serialized sources list
    total_records INTEGER DEFAULT 0,
    validation_status TEXT,
    quality_score TEXT,
    validation_notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Indexes:**
- `idx_jobs_status` - For filtering by job status
- `idx_jobs_created_at` - For sorting by creation time

## Key Features

### 1. **Data Persistence**
- Jobs survive server restarts
- No data loss during deployments
- Automatic database initialization

### 2. **JSON Serialization**
- Complex data structures (datasets, sources) are stored as JSON
- Automatic serialization/deserialization
- Maintains data integrity

### 3. **Database Operations**
- Create, read, update, delete operations
- Bulk operations for admin tasks
- Automatic timestamp management

### 4. **Admin Endpoints**
- Database statistics
- Job listing and management
- Cleanup utilities

## API Changes

### Existing Endpoints (Unchanged Interface)

All existing endpoints maintain the same interface:

- `POST /api/datasets/generate` - Creates job in database
- `GET /api/datasets/{job_id}/results` - Retrieves job from database
- `GET /api/datasets/{job_id}/download` - Downloads CSV from database

### New Admin Endpoints

#### Database Statistics
```http
GET /api/admin/stats
```

**Response:**
```json
{
  "total_jobs": 150,
  "status_counts": {
    "processing": 5,
    "completed": 140,
    "failed": 5
  },
  "recent_jobs_24h": 12
}
```

#### List All Jobs
```http
GET /api/admin/jobs?limit=100
```

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "uuid-here",
      "query": "example query",
      "status": "completed",
      "dataset": [...],
      "sources": [...],
      "total_records": 10,
      "validation_status": "completed",
      "quality_score": "high",
      "validation_notes": "Data validated successfully",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:35:00"
    }
  ]
}
```

#### Delete Job
```http
DELETE /api/admin/jobs/{job_id}
```

#### Cleanup Old Jobs
```http
POST /api/admin/cleanup?days=30
```

## Database Class Methods

### Core Operations

```python
# Initialize database
db = JobDatabase('webhound.db')

# Create job
db.create_job(job_id, query)

# Update job
db.update_job(job_id, status="completed", dataset=data)

# Get job
job = db.get_job(job_id)

# Delete job
success = db.delete_job(job_id)
```

### Admin Operations

```python
# Get all jobs
jobs = db.get_all_jobs(limit=100)

# Get statistics
stats = db.get_job_stats()

# Cleanup old jobs
deleted_count = db.cleanup_old_jobs(days=30)
```

## Migration from In-Memory Storage

### What Changed

1. **Storage Layer**: `jobs = {}` → `db = JobDatabase()`
2. **Job Creation**: Direct dict assignment → `db.create_job()`
3. **Job Retrieval**: Dict lookup → `db.get_job()`
4. **Job Updates**: Dict assignment → `db.update_job()`

### Benefits

- ✅ **Persistence**: Data survives restarts
- ✅ **Scalability**: Can handle more jobs
- ✅ **Reliability**: ACID compliance
- ✅ **Admin Tools**: Built-in management endpoints
- ✅ **Performance**: Indexed queries

## Database File Management

### Location
- Default: `webhound.db` in the backend directory
- Configurable via `JobDatabase(db_path='custom/path.db')`

### Backup
```bash
# Simple backup
cp webhound.db webhound_backup_$(date +%Y%m%d).db

# Compressed backup
sqlite3 webhound.db ".backup backup.db"
gzip backup.db
```

### Maintenance
```bash
# Optimize database
sqlite3 webhound.db "VACUUM;"

# Check integrity
sqlite3 webhound.db "PRAGMA integrity_check;"
```

## Error Handling

### Database Errors
- Connection errors are handled gracefully
- JSON serialization errors are caught
- Invalid job IDs return 404

### Fallback Behavior
- If database is unavailable, endpoints return 500
- Rate limiting remains in-memory for performance
- No data corruption from concurrent access

## Performance Considerations

### Indexes
- Status and creation time are indexed
- Queries are optimized for common patterns

### Connection Management
- Connections are opened/closed per operation
- No connection pooling (SQLite handles this)

### Memory Usage
- JSON serialization adds some overhead
- Database file grows with job count
- Regular cleanup recommended

## Security Notes

### File Permissions
```bash
# Secure database file
chmod 600 webhound.db
```

### Admin Endpoints
- Admin endpoints are public (no authentication)
- Consider adding authentication for production
- Use reverse proxy for additional security

## Testing

### Database Testing
```python
# Test database operations
db = JobDatabase(':memory:')  # In-memory for testing
db.create_job('test-id', 'test query')
job = db.get_job('test-id')
assert job['query'] == 'test query'
```

### Integration Testing
```python
# Test API with database
response = client.post("/api/datasets/generate", json={"query": "test"})
job_id = response.json()["job_id"]
job = client.get(f"/api/datasets/{job_id}/results")
assert job.json()["status"] == "processing"
```

## Future Enhancements

### Potential Improvements
1. **Connection Pooling**: For high concurrency
2. **Database Migrations**: For schema changes
3. **Encryption**: For sensitive data
4. **Replication**: For high availability
5. **Monitoring**: Database performance metrics

### Alternative Databases
- **PostgreSQL**: For larger scale
- **Redis**: For caching layer
- **MongoDB**: For document storage

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   chmod 755 backend/
   chmod 644 webhound.db
   ```

2. **Database Locked**
   ```bash
   # Check for other processes
   lsof webhound.db
   ```

3. **Corrupted Database**
   ```bash
   sqlite3 webhound.db "PRAGMA integrity_check;"
   ```

4. **Large Database File**
   ```bash
   # Cleanup old jobs
   curl -X POST "http://localhost:8000/api/admin/cleanup?days=7"
   ```

### Logs
- Database errors are logged to application logs
- Check for SQLite-specific error messages
- Monitor database file size growth 