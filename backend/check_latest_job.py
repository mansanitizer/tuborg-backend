#!/usr/bin/env python3
"""
Check the latest job's data structure
"""

import json
from database import JobDatabase

def check_latest_job():
    """Check the latest job's data structure"""
    
    db = JobDatabase()
    
    # Get recent queries to find the latest job
    recent_queries = db.get_recent_queries(1)
    if not recent_queries:
        print("❌ No recent queries found")
        return
    
    job_id = recent_queries[0]['job_id']
    job = db.get_job(job_id)
    
    if not job:
        print(f"❌ Job {job_id} not found")
        return
    
    print(f"🔍 Latest job: {job_id}")
    print(f"   Query: {job.get('query')}")
    print(f"   Status: {job.get('status')}")
    
    # Check dataset content
    dataset = job.get('dataset', [])
    print(f"   Dataset length: {len(dataset)}")
    
    if dataset:
        first_item = dataset[0]
        print(f"   First item type: {type(first_item)}")
        
        if isinstance(first_item, dict):
            print(f"   First item keys: {list(first_item.keys())}")
            
            # Check if it has a 'result' field
            if 'result' in first_item:
                result_str = first_item['result']
                print(f"   Result string starts with: {result_str[:200]}...")
                
                # Try to parse the JSON manually
                import re
                
                # Look for JSON in markdown code blocks
                code_block_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', result_str, re.DOTALL)
                if code_block_match:
                    json_content = code_block_match.group(1).strip()
                    print(f"✅ Found JSON in code block")
                    
                    try:
                        parsed_json = json.loads(json_content)
                        print(f"✅ Successfully parsed JSON with keys: {list(parsed_json.keys())}")
                        
                        data = parsed_json.get('data', [])
                        print(f"✅ Data array length: {len(data)}")
                        
                        if data and len(data) > 0:
                            print(f"✅ First data item: {data[0]}")
                        
                        sources = parsed_json.get('sources', [])
                        print(f"✅ Sources: {sources}")
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON parsing failed: {e}")
                else:
                    print("❌ No code block found")
    
    # Check raw_data
    raw_data = job.get('raw_data')
    if raw_data:
        print(f"\n📊 Raw data structure:")
        print(f"   Raw data type: {type(raw_data)}")
        if isinstance(raw_data, dict):
            print(f"   Raw data keys: {list(raw_data.keys())}")

if __name__ == "__main__":
    check_latest_job() 