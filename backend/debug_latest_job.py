#!/usr/bin/env python3
"""
Debug script to examine the latest job
"""

import json
from database import JobDatabase

def debug_latest_job():
    """Debug the most recent job"""
    
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
    
    print(f"🔍 Debugging latest job: {job_id}")
    print(f"   Status: {job.get('status')}")
    print(f"   Query: {job.get('query')}")
    print(f"   Total records: {job.get('total_records', 0)}")
    
    # Check dataset content
    dataset = job.get('dataset', [])
    print(f"   Dataset length: {len(dataset)}")
    if dataset:
        print(f"   Dataset first item: {dataset[0]}")
    
    # Check raw_data content
    raw_data = job.get('raw_data')
    if raw_data:
        print(f"   Raw data keys: {list(raw_data.keys()) if isinstance(raw_data, dict) else 'Not a dict'}")
        if isinstance(raw_data, dict):
            for key, value in raw_data.items():
                print(f"   Raw data[{key}]: {type(value)} = {value}")
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
    debug_latest_job() 