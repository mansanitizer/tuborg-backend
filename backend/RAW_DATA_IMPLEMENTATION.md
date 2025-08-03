# Raw Data Implementation

## 🎯 **Overview**

The Webhound backend now saves the complete raw JSON data returned by CrewAI against each job ID and provides an API endpoint to retrieve this raw data. This allows frontend applications to access the unprocessed, complete response from CrewAI.

## 🔧 **Implementation Details**

### **1. Database Schema Update**

Added a new `raw_data` column to the `jobs` table:

```sql
ALTER TABLE jobs ADD COLUMN raw_data TEXT;
```

**Database Migration:**
- Automatically adds the `raw_data` column to existing databases
- Handles cases where the column already exists
- Preserves all existing data

### **2. Data Storage Process**

**Step 1: Query Submission**
```python
# User submits query → Job created with status "processing"
db.create_job(job_id, query)
```

**Step 2: CrewAI Processing**
```python
# CrewAI processes the query and returns raw data
dataset = await create_dataset_async(query)
```

**Step 3: Raw Data Storage**
```python
# Raw data is immediately saved to database
db.update_job(job_id, raw_data=dataset)
```

**Step 4: Data Processing**
```python
# Processed data is saved separately for the main API
db.update_job(job_id, status="completed", dataset=parsed_data, ...)
```

### **3. API Endpoint**

**Endpoint:** `GET /api/datasets/{job_id}/raw`

**Purpose:** Retrieve the complete raw JSON data for a specific job

**Response Structure:**
```json
{
  "job_id": "c83dd5ff-19c7-47cb-a10e-9ab7a7f990a2",
  "query": "What are the top 3 programming languages in 2024?",
  "status": "completed",
  "raw_data": {
    "data": [
      {
        "query": "What are the top 3 programming languages in 2024?",
        "result": "```json\n{\n  \"data\": [\n    {\n      \"rank\": 1,\n      \"language\": \"Python\",\n      \"description\": \"Python consistently ranks high...\"\n    }\n  ],\n  \"sources\": [...],\n  \"validation_status\": \"validated\",\n  \"quality_score\": \"high\",\n  \"validation_notes\": \"...\"\n}\n```"
      }
    ],
    "sources": [],
    "validation_status": "completed",
    "quality_score": "unknown",
    "validation_notes": "Workflow completed successfully"
  },
  "created_at": "2025-08-03 19:02:24.040388",
  "updated_at": "2025-08-03 19:02:49.249925"
}
```

## 🧪 **Testing Results**

### **Test Results:**
- ✅ Database migration successful
- ✅ Raw data storage working
- ✅ API endpoint responding correctly
- ✅ Error handling for invalid job IDs
- ✅ Complete CrewAI response preserved

### **Sample Raw Data:**
The raw data contains the complete CrewAI workflow output, including:
- **Research results** from web search
- **Extracted data** in structured format
- **Validation results** with quality scores
- **Source information** and validation notes

## 📊 **Frontend Integration**

### **JavaScript Example:**
```javascript
const getRawData = async (jobId) => {
  try {
    const response = await fetch(`/api/datasets/${jobId}/raw`);
    
    if (response.status === 404) {
      console.log('Job not found or raw data not available');
      return null;
    }
    
    if (!response.ok) {
      throw new Error('Failed to fetch raw data');
    }
    
    const data = await response.json();
    return data.raw_data;
  } catch (error) {
    console.error('Error fetching raw data:', error);
    return null;
  }
};

// Usage
const rawData = await getRawData('c83dd5ff-19c7-47cb-a10e-9ab7a7f990a2');
if (rawData) {
  console.log('Raw CrewAI response:', rawData);
}
```

### **TypeScript Interface:**
```typescript
interface RawDataResponse {
  job_id: string;
  query: string;
  status: string;
  raw_data: any; // Complete CrewAI response
  created_at: string;
  updated_at: string;
}
```

## 🚀 **Usage Examples**

### **1. Get Raw Data by Job ID**
```bash
curl "http://localhost:8000/api/datasets/c83dd5ff-19c7-47cb-a10e-9ab7a7f990a2/raw"
```

### **2. Check if Raw Data Exists**
```bash
# Valid job ID with raw data
curl "http://localhost:8000/api/datasets/valid-job-id/raw"
# Returns: 200 OK with raw data

# Invalid job ID
curl "http://localhost:8000/api/datasets/invalid-job-id/raw"
# Returns: 404 Not Found
```

### **3. Frontend Integration**
```javascript
// Submit query and get job ID
const response = await fetch('/api/datasets/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: "What are the top programming languages?" })
});
const { job_id } = await response.json();

// Wait for processing, then get raw data
setTimeout(async () => {
  const rawData = await getRawData(job_id);
  if (rawData) {
    console.log('Complete CrewAI response:', rawData);
  }
}, 30000); // Wait 30 seconds for processing
```

## 📈 **Benefits**

### **1. Complete Data Access**
- Access to the full CrewAI workflow output
- Raw research results and intermediate data
- Validation details and quality assessments

### **2. Debugging and Analysis**
- Debug CrewAI responses
- Analyze data quality and sources
- Understand the complete processing pipeline

### **3. Frontend Flexibility**
- Choose between processed and raw data
- Custom data processing on frontend
- Access to intermediate workflow steps

### **4. Data Preservation**
- Complete audit trail of CrewAI responses
- Historical data for analysis
- Backup of original responses

## 🔄 **Data Flow**

1. **User submits query** → `/api/datasets/generate`
2. **Job created** → Status: "processing"
3. **CrewAI processes** → Returns complete response
4. **Raw data saved** → Stored in `raw_data` column
5. **Data processed** → Stored in `dataset` column
6. **Frontend requests** → `/api/datasets/{job_id}/raw`
7. **Raw data returned** → Complete CrewAI response

## ✅ **Error Handling**

### **404 Not Found:**
- Job ID doesn't exist
- Raw data not available (job still processing)

### **500 Internal Server Error:**
- Database connection issues
- Data serialization problems

### **Frontend Handling:**
```javascript
const handleRawDataRequest = async (jobId) => {
  try {
    const response = await fetch(`/api/datasets/${jobId}/raw`);
    
    if (response.status === 404) {
      // Job not found or still processing
      return { error: 'Job not found or still processing' };
    }
    
    if (!response.ok) {
      throw new Error('Server error');
    }
    
    return await response.json();
  } catch (error) {
    return { error: error.message };
  }
};
```

## 🔮 **Future Enhancements**

1. **Raw Data Compression**: Compress large raw data responses
2. **Data Retention Policy**: Automatically clean up old raw data
3. **Raw Data Analytics**: Track raw data patterns and quality
4. **Export Functionality**: Export raw data in various formats
5. **Raw Data Search**: Search through raw data content
6. **Raw Data Versioning**: Track changes in raw data over time 