# API Quota Solutions

## 🚨 **Current Issue: Gemini API Quota Exceeded**

You're hitting the **free tier quota limit** for Gemini API. This is normal and expected.

### **Error Details:**
```
ResourceExhausted: 429 You exceeded your current quota
quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_requests"
quota_value: 50
```

## 📊 **Gemini API Free Tier Limits**

### **gemini-1.5-flash** (Current Model)
- **Daily Requests**: 50 requests per day
- **Rate Limit**: 15 requests per minute
- **Reset Time**: Daily at midnight UTC

### **gemini-1.5-pro** (Alternative)
- **Daily Requests**: 50 requests per day
- **Rate Limit**: 2 requests per minute
- **Reset Time**: Daily at midnight UTC

## 🔧 **Immediate Solutions**

### **1. Wait for Quota Reset**
- **When**: Daily at midnight UTC
- **Check**: Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
- **Status**: Monitor your usage in the dashboard

### **2. Use Alternative Models**
Update your `.env` file to use a different model:

```bash
# Option A: Use gemini-1.5-pro (slower but same quota)
GEMINI_API_KEY=AIzaSyBT0TNBjz-El0u0COuFShS_gJPpM_6jp6U
GEMINI_MODEL=gemini-1.5-pro

# Option B: Use gemini-1.0-pro (different quota pool)
GEMINI_API_KEY=AIzaSyBT0TNBjz-El0u0COuFShS_gJPpM_6jp6U
GEMINI_MODEL=gemini-1.0-pro
```

### **3. Upgrade to Paid Plan**
- **Cost**: ~$0.50 per 1M input tokens
- **Benefits**: Higher limits, faster processing
- **Setup**: Visit [Google AI Studio](https://aistudio.google.com/app/apikey)

## 🛠️ **Code Modifications**

### **Option 1: Add Model Configuration**
Update `crewai_setup_working.py`:

```python
# Add to __init__ method
self.model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

self.llm = ChatGoogleGenerativeAI(
    model=self.model,  # Use configurable model
    google_api_key=self.gemini_api_key,
    temperature=0.1
)
```

### **Option 2: Add Fallback LLM**
Create a fallback system:

```python
def _create_llm_with_fallback(self):
    """Create LLM with fallback options"""
    models = [
        "gemini-1.5-flash",
        "gemini-1.5-pro", 
        "gemini-1.0-pro"
    ]
    
    for model in models:
        try:
            llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=self.gemini_api_key,
                temperature=0.1
            )
            # Test the connection
            llm.invoke("test")
            return llm
        except Exception as e:
            print(f"Model {model} failed: {e}")
            continue
    
    raise Exception("No working Gemini model found")
```

### **Option 3: Add Rate Limiting**
Implement request throttling:

```python
import time
from functools import wraps

def rate_limit(max_requests=10, time_window=60):
    """Rate limiting decorator"""
    requests = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old requests
            requests[:] = [req for req in requests if now - req < time_window]
            
            if len(requests) >= max_requests:
                wait_time = time_window - (now - requests[0])
                if wait_time > 0:
                    time.sleep(wait_time)
            
            requests.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## 🎯 **Recommended Actions**

### **Immediate (Today)**
1. **Wait for quota reset** (midnight UTC)
2. **Test with different model** (gemini-1.5-pro)
3. **Monitor usage** in Google AI Studio

### **Short Term (This Week)**
1. **Implement fallback models**
2. **Add rate limiting**
3. **Consider paid plan** for development

### **Long Term (Next Month)**
1. **Upgrade to paid plan**
2. **Implement caching**
3. **Add multiple API keys**

## 📈 **Usage Monitoring**

### **Check Current Usage**
```bash
# Visit Google AI Studio
open https://aistudio.google.com/app/apikey
```

### **Monitor in Application**
Add logging to track usage:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_api_usage(model, tokens_used):
    logger.info(f"API Usage - Model: {model}, Tokens: {tokens_used}")
```

## 🔄 **Alternative Solutions**

### **1. Use Different LLM Provider**
- **OpenAI**: GPT-3.5-turbo (free tier available)
- **Anthropic**: Claude (free tier available)
- **Local Models**: Ollama, LM Studio

### **2. Implement Caching**
```python
import redis
import hashlib

def cache_llm_response(query, response, ttl=3600):
    """Cache LLM responses to reduce API calls"""
    cache_key = hashlib.md5(query.encode()).hexdigest()
    redis_client.setex(cache_key, ttl, response)
```

### **3. Batch Processing**
```python
def batch_queries(queries, batch_size=5):
    """Process multiple queries in batches"""
    for i in range(0, len(queries), batch_size):
        batch = queries[i:i+batch_size]
        # Process batch
        time.sleep(60)  # Rate limiting
```

## 🚀 **Quick Fix Commands**

### **Test Different Model**
```bash
# Add to .env
echo "GEMINI_MODEL=gemini-1.5-pro" >> .env

# Restart server
./start_server.sh
```

### **Check Quota Status**
```bash
# Visit in browser
open https://aistudio.google.com/app/apikey
```

### **Monitor Usage**
```bash
# Check server logs for API usage
tail -f server.log | grep "API Usage"
```

## 📞 **Support**

- **Google AI Studio**: https://aistudio.google.com/app/apikey
- **Gemini API Docs**: https://ai.google.dev/gemini-api/docs
- **Quota Limits**: https://ai.google.dev/gemini-api/docs/rate-limits 