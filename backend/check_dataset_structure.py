#!/usr/bin/env python3
"""
Check dataset structure of latest job
"""

import json
from database import JobDatabase

def check_dataset_structure():
    """Check the dataset structure of the latest job"""
    
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
    
    print(f"🔍 Checking dataset structure for job: {job_id}")
    print(f"   Query: {job.get('query')}")
    print(f"   Status: {job.get('status')}")
    
    # Check dataset content
    dataset = job.get('dataset', [])
    print(f"   Dataset length: {len(dataset)}")
    
    if dataset:
        first_item = dataset[0]
        print(f"   First item type: {type(first_item)}")
        print(f"   First item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}")
        
        if isinstance(first_item, dict):
            for key, value in first_item.items():
                print(f"   {key}: {type(value)} = {value}")
    
    # Check raw_data
    raw_data = job.get('raw_data')
    if raw_data:
        print(f"\n📊 Raw data structure:")
        print(f"   Raw data type: {type(raw_data)}")
        if isinstance(raw_data, dict):
            print(f"   Raw data keys: {list(raw_data.keys())}")
            for key, value in raw_data.items():
                print(f"   {key}: {type(value)} = {value}")

if __name__ == "__main__":
    check_dataset_structure() 