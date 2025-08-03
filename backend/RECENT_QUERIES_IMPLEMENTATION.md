# Recent Queries Implementation

## 🎯 **Overview**

The Webhound backend now automatically saves all user queries to the SQLite database and provides an API endpoint to retrieve "recently asked questions" for the frontend.

## 🔧 **Implementation Details**

### **1. Database Storage**

All queries are automatically saved when submitted via the `/api/datasets/generate` endpoint:

```python
# In main.py - process_dataset function
db.create_job(job_id, request.query)  # Saves query to database
```

### **2. Database Methods**

Added two new methods to `JobDatabase` class:

#### **`get_recent_queries(limit: int = 10)`**
- Returns the most recent queries with timestamps and status
- Includes duplicates (shows every time a query was asked)
- Ordered by creation time (newest first)

#### **`get_unique_recent_queries(limit: int = 10)`**
- Returns unique queries (no duplicates)
- Shows how many times each query was asked
- Shows when it was last asked
- Ordered by last asked time (newest first)

### **3. API Endpoint**

**Endpoint:** `GET /api/queries/recent`

**Query Parameters:**
- `limit` (optional): Number of queries to return (default: 10)

**Response Structure:**
```json
{
  "recent_queries": [
    {
      "query": "What are the top programming languages in 2024?",
      "created_at": "2024-01-15T10:30:00",
      "status": "completed"
    }
  ],
  "unique_queries": [
    {
      "query": "What are the top programming languages in 2024?",
      "last_asked": "2024-01-15T10:30:00",
      "times_asked": 3
    }
  ]
}
```

## 🧪 **Testing Results**

### **Test Results:**
- ✅ Server health check passed
- ✅ Query submission working
- ✅ Recent queries endpoint responding
- ✅ Both recent and unique queries returned
- ✅ Limit parameter working correctly

### **Sample Data:**
```json
{
  "recent_queries": [
    {
      "query": "Weather forecast for tomorrow",
      "created_at": "2025-08-03 18:10:00",
      "status": "processing"
    },
    {
      "query": "Latest AI developments",
      "created_at": "2025-08-03 18:09:00",
      "status": "processing"
    }
  ],
  "unique_queries": [
    {
      "query": "Weather forecast for tomorrow",
      "last_asked": "2025-08-03 18:10:00",
      "times_asked": 1
    },
    {
      "query": "Latest AI developments",
      "last_asked": "2025-08-03 18:09:00",
      "times_asked": 1
    }
  ]
}
```

## 📊 **Frontend Integration**

### **TypeScript Interfaces:**
```typescript
interface RecentQuery {
  query: string;
  created_at: string;
  status: string;
}

interface UniqueRecentQuery {
  query: string;
  last_asked: string;
  times_asked: number;
}

interface RecentQueriesResponse {
  recent_queries: RecentQuery[];
  unique_queries: UniqueRecentQuery[];
}
```

### **React Component Example:**
```typescript
const RecentQueries: React.FC = () => {
  const [recentQueries, setRecentQueries] = useState<RecentQuery[]>([]);
  const [uniqueQueries, setUniqueQueries] = useState<UniqueRecentQuery[]>([]);

  const fetchRecentQueries = async () => {
    const response = await fetch('http://localhost:8000/api/queries/recent?limit=10');
    const data = await response.json();
    
    setRecentQueries(data.recent_queries);
    setUniqueQueries(data.unique_queries);
  };

  return (
    <div>
      <h3>Recently Asked Questions</h3>
      {recentQueries.map((query, index) => (
        <div key={index}>
          <span>{query.query}</span>
          <span>Status: {query.status}</span>
          <span>{new Date(query.created_at).toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
};
```

## 🚀 **Usage Examples**

### **1. Get Recent Queries**
```bash
curl "http://localhost:8000/api/queries/recent?limit=5"
```

### **2. JavaScript Fetch**
```javascript
const response = await fetch('/api/queries/recent?limit=10');
const data = await response.json();

console.log('Recent queries:', data.recent_queries);
console.log('Unique queries:', data.unique_queries);
```

### **3. Display in UI**
```javascript
// Show recent queries
data.recent_queries.forEach(query => {
  console.log(`Query: ${query.query} (Status: ${query.status})`);
});

// Show popular queries
data.unique_queries.forEach(query => {
  console.log(`Query: ${query.query} (Asked ${query.times_asked} times)`);
});
```

## 📈 **Features**

### **Recent Queries:**
- Shows every query submitted (including duplicates)
- Includes timestamp and job status
- Ordered by creation time (newest first)

### **Unique Queries:**
- Shows each unique query only once
- Counts how many times each query was asked
- Shows when it was last asked
- Useful for identifying popular questions

### **Status Tracking:**
- `processing`: Query is being processed
- `completed`: Query completed successfully
- `failed`: Query failed due to error
- `quota_exceeded`: Query failed due to API limits

## 🔄 **Data Flow**

1. **User submits query** → `/api/datasets/generate`
2. **Query saved to database** → `jobs` table
3. **Frontend requests recent queries** → `/api/queries/recent`
4. **Backend retrieves from database** → Recent and unique queries
5. **Frontend displays to user** → "Recently Asked Questions"

## ✅ **Benefits**

1. **User Experience**: Users can see what others are asking
2. **Popular Questions**: Identify trending topics
3. **Query History**: Track what has been asked
4. **Status Visibility**: See which queries succeeded/failed
5. **Analytics**: Understand user behavior and interests

## 🔮 **Future Enhancements**

1. **Query Categories**: Group queries by topic
2. **Search Functionality**: Search through recent queries
3. **User-specific History**: Track queries per user
4. **Query Suggestions**: Suggest similar queries
5. **Analytics Dashboard**: Visualize query patterns
6. **Export Functionality**: Export query history 