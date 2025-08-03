# API Quota Error Handling Implementation

## 🎯 **Overview**

The Webhound backend now includes comprehensive error handling for API quota limits. When quota limits are exceeded, jobs are properly terminated with a `quota_exceeded` status instead of failing with generic errors.

## 🔧 **Implementation Details**

### **1. Job Status Updates**

Added new job status: `quota_exceeded`

**Status Values:**
- `processing`: Job is being processed
- `completed`: Job completed successfully  
- `failed`: Job failed due to general error
- `quota_exceeded`: Job failed due to API quota limits

### **2. Error Detection**

The system detects quota errors by checking for specific keywords in error messages:

```python
quota_keywords = [
    "quota", "429", "resourceexhausted", "rate limit", "exceeded"
]
```

### **3. Error Handling Layers**

#### **Layer 1: CrewAI Setup (`crewai_setup_working.py`)**
- Catches exceptions during CrewAI workflow execution
- Identifies quota-related errors
- Returns structured error response with `validation_status: "quota_exceeded"`

#### **Layer 2: Main API (`main.py`)**
- Processes CrewAI results
- Checks for quota error status in response
- Updates job with appropriate status and error message
- Handles exceptions at the API level

### **4. Error Response Structure**

When quota is exceeded, the API returns:

```json
{
  "job_id": "uuid",
  "status": "quota_exceeded",
  "query": "original query",
  "dataset": [],
  "sources": [],
  "total_records": 0,
  "validation_status": "quota_exceeded",
  "quality_score": "unknown",
  "validation_notes": "API quota exceeded. Please try again later or upgrade your plan."
}
```

## 🧪 **Testing**

### **Test Script: `test_quota_handling.py`**

The test script verifies:
1. API configuration loading
2. Quota error detection
3. Model switching capabilities
4. Error handling flow

**Run Test:**
```bash
cd backend
source venv/bin/activate
python test_quota_handling.py
```

### **Manual Testing**

**1. Submit Query:**
```bash
curl -X POST "http://localhost:8000/api/datasets/generate" \
     -H "Content-Type: application/json" \
     -d '{"query": "test query"}'
```

**2. Check Results:**
```bash
curl "http://localhost:8000/api/datasets/{job_id}/results"
```

**Expected Response (Quota Exceeded):**
```json
{
  "status": "quota_exceeded",
  "validation_notes": "API quota exceeded. Please try again later or upgrade your plan."
}
```

## 📊 **Frontend Integration**

### **Updated TypeScript Interface**

```typescript
interface DatasetResult {
  job_id: string;
  status: 'processing' | 'completed' | 'failed' | 'quota_exceeded';
  query: string;
  dataset: any[];
  sources: string[];
  total_records: number;
  validation_status: string;
  quality_score: string;
  validation_notes: string;
}
```

### **Frontend Error Handling**

```typescript
const pollForResults = async (id: string) => {
  const pollInterval = setInterval(async () => {
    const response = await fetch(`/api/datasets/${id}/results`);
    const data: DatasetResult = await response.json();
    
    if (data.status === 'quota_exceeded') {
      setError('API quota exceeded. Please try again later.');
      setLoading(false);
      clearInterval(pollInterval);
    } else if (data.status === 'completed') {
      setResult(data);
      setLoading(false);
      clearInterval(pollInterval);
    }
  }, 2000);
};
```

## 🔄 **Recovery Strategies**

### **1. Wait for Quota Reset**
- **Daily Reset**: Midnight UTC
- **Check Status**: Visit [Google AI Studio](https://aistudio.google.com/app/apikey)

### **2. Switch Models**
```bash
# Add to .env
GEMINI_MODEL=gemini-1.0-pro  # Different quota pool
```

### **3. Upgrade to Paid Plan**
- **Cost**: ~$0.50 per 1M input tokens
- **Benefits**: Higher limits, faster processing

## 📈 **Monitoring**

### **Database Queries**

Check quota-exceeded jobs:
```sql
SELECT * FROM jobs WHERE status = 'quota_exceeded' ORDER BY created_at DESC;
```

### **Admin Endpoints**

```bash
# Get job statistics
curl "http://localhost:8000/api/admin/stats"

# Get all jobs
curl "http://localhost:8000/api/admin/jobs"
```

## 🚀 **Usage Examples**

### **1. Handle Quota Errors Gracefully**

```javascript
const handleQuery = async (query) => {
  try {
    const response = await fetch('/api/datasets/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    
    const { job_id } = await response.json();
    
    // Poll for results
    const result = await pollForResults(job_id);
    
    if (result.status === 'quota_exceeded') {
      showQuotaError(result.validation_notes);
    } else if (result.status === 'completed') {
      showResults(result.dataset);
    }
  } catch (error) {
    console.error('Query failed:', error);
  }
};
```

### **2. Retry with Different Model**

```javascript
const retryWithDifferentModel = async (originalQuery) => {
  // Switch to different model
  await fetch('/api/admin/switch-model', {
    method: 'POST',
    body: JSON.stringify({ model: 'gemini-1.0-pro' })
  });
  
  // Retry the query
  return handleQuery(originalQuery);
};
```

## ✅ **Benefits**

1. **Clear Error Messages**: Users know exactly what went wrong
2. **Graceful Degradation**: System doesn't crash on quota errors
3. **Recovery Options**: Multiple strategies for handling quota limits
4. **Monitoring**: Easy to track quota usage and errors
5. **Frontend Integration**: Type-safe error handling in React/TypeScript

## 🔮 **Future Enhancements**

1. **Automatic Model Switching**: Automatically try different models when quota is hit
2. **Caching**: Cache results to reduce API calls
3. **Rate Limiting**: Implement client-side rate limiting
4. **Multiple API Keys**: Rotate between multiple API keys
5. **Usage Analytics**: Track quota usage patterns 