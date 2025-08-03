#!/usr/bin/env python3
"""
Debug script to examine raw data structure
"""

import json
from database import JobDatabase

def debug_raw_data(job_id):
    """Debug the raw data structure"""
    
    db = JobDatabase()
    job = db.get_job(job_id)
    
    if not job:
        print(f"❌ Job {job_id} not found")
        return
    
    raw_data = job.get('raw_data')
    if not raw_data:
        print("❌ No raw data found")
        return
    
    print(f"🔍 Raw data structure for job: {job_id}")
    print(f"   Raw data type: {type(raw_data)}")
    print(f"   Raw data keys: {list(raw_data.keys()) if isinstance(raw_data, dict) else 'Not a dict'}")
    
    if isinstance(raw_data, dict):
        for key, value in raw_data.items():
            print(f"   {key}: {type(value)} = {value}")
            
        # Examine the data field more closely
        if 'data' in raw_data:
            data = raw_data['data']
            print(f"\n📊 Data field analysis:")
            print(f"   Data type: {type(data)}")
            print(f"   Data length: {len(data) if isinstance(data, list) else 'Not a list'}")
            
            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                print(f"   First item type: {type(first_item)}")
                print(f"   First item: {first_item}")
                
                # Check if it has a 'result' field
                if isinstance(first_item, dict) and 'result' in first_item:
                    result = first_item['result']
                    print(f"   Result type: {type(result)}")
                    print(f"   Result: {result[:200]}..." if isinstance(result, str) and len(result) > 200 else f"   Result: {result}")

if __name__ == "__main__":
    job_id = "e6b2d116-982f-438f-afa3-a0d6f18eb161"
    debug_raw_data(job_id) 