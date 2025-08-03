#!/usr/bin/env python3
"""
Test script to run a new query and see the parsing
"""

import asyncio
import requests
import time
from main import app
from fastapi.testclient import TestClient

async def test_new_query():
    """Test a new query to see the parsing"""
    
    client = TestClient(app)
    
    # Submit a new query
    query = "top 3 programming languages 2025"
    print(f"🔍 Submitting new query: {query}")
    
    response = client.post("/api/datasets/generate", json={"query": query})
    print(f"   Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        job_id = data.get('job_id')
        print(f"   Job ID: {job_id}")
        
        # Wait a bit for processing
        print("   Waiting for processing...")
        time.sleep(5)
        
        # Check the results
        response = client.get(f"/api/datasets/{job_id}/results")
        print(f"   Results status: {response.status_code}")
        
        if response.status_code == 200:
            result_data = response.json()
            print(f"   Status: {result_data.get('status')}")
            print(f"   Dataset records: {len(result_data.get('dataset', []))}")
            print(f"   Insights: {len(result_data.get('insights', []))}")
            print(f"   Insight summary: {result_data.get('insight_summary', 'None')}")
            print(f"   Data highlights: {len(result_data.get('data_highlights', []))}")
            
            # Check if both dataset and insights are present
            if result_data.get('dataset') and result_data.get('insights'):
                print("✅ BOTH dataset and insights are present!")
            elif result_data.get('dataset'):
                print("⚠️  Only dataset present, no insights")
            elif result_data.get('insights'):
                print("⚠️  Only insights present, no dataset")
            else:
                print("❌ Neither dataset nor insights present")
        else:
            print(f"   Error getting results: {response.text}")
    else:
        print(f"   Error submitting query: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_new_query()) 