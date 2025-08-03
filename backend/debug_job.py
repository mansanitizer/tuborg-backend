#!/usr/bin/env python3
"""
Debug script to examine job data in database
"""

import json
from database import JobDatabase

def debug_job(job_id):
    """Debug a specific job to see what's stored"""
    
    db = JobDatabase()
    job = db.get_job(job_id)
    
    if not job:
        print(f"❌ Job {job_id} not found")
        return
    
    print(f"🔍 Debugging job: {job_id}")
    print(f"   Status: {job.get('status')}")
    print(f"   Query: {job.get('query')}")
    print(f"   Total records: {job.get('total_records', 0)}")
    print(f"   Dataset type: {type(job.get('dataset'))}")
    print(f"   Dataset length: {len(job.get('dataset', []))}")
    print(f"   Raw data type: {type(job.get('raw_data'))}")
    
    # Check dataset content
    dataset = job.get('dataset', [])
    if dataset:
        print(f"   Dataset first item: {dataset[0] if len(dataset) > 0 else 'Empty'}")
    else:
        print("   Dataset is empty")
    
    # Check raw_data content
    raw_data = job.get('raw_data')
    if raw_data:
        print(f"   Raw data keys: {list(raw_data.keys()) if isinstance(raw_data, dict) else 'Not a dict'}")
        if isinstance(raw_data, dict):
            print(f"   Raw data has 'data' key: {'data' in raw_data}")
            if 'data' in raw_data:
                print(f"   Raw data['data'] length: {len(raw_data['data']) if isinstance(raw_data['data'], list) else 'Not a list'}")
    else:
        print("   Raw data is empty")
    
    # Check insights
    insights = job.get('insights', [])
    insight_summary = job.get('insight_summary', '')
    data_highlights = job.get('data_highlights', [])
    
    print(f"   Insights: {insights}")
    print(f"   Insight summary: {insight_summary}")
    print(f"   Data highlights: {data_highlights}")

if __name__ == "__main__":
    # Use the job ID from the test
    job_id = "e6b2d116-982f-438f-afa3-a0d6f18eb161"
    debug_job(job_id) 