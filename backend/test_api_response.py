#!/usr/bin/env python3
"""
Test script to verify API response structure
"""

import json
from main import app
from fastapi.testclient import TestClient

def test_api_response_structure():
    """Test that the API returns both dataset and insights"""
    
    # Create test client
    client = TestClient(app)
    
    # Test the health endpoint first
    response = client.get("/api/health")
    print(f"Health check: {response.status_code}")
    
    # Test getting recent queries
    response = client.get("/api/queries/recent?limit=5")
    print(f"Recent queries: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data.get('recent_queries', []))} recent queries")
        
        # If there are recent queries, test getting results for the first one
        if data.get('recent_queries'):
            first_query = data['recent_queries'][0]
            job_id = first_query['job_id']
            
            print(f"\nTesting results for job: {job_id}")
            response = client.get(f"/api/datasets/{job_id}/results")
            
            if response.status_code == 200:
                result_data = response.json()
                print(f"✅ Job results retrieved successfully")
                print(f"   Status: {result_data.get('status')}")
                print(f"   Query: {result_data.get('query')}")
                print(f"   Dataset records: {len(result_data.get('dataset', []))}")
                print(f"   Sources: {len(result_data.get('sources', []))}")
                print(f"   Insights: {len(result_data.get('insights', []))}")
                print(f"   Insight summary: {result_data.get('insight_summary', 'None')}")
                print(f"   Data highlights: {len(result_data.get('data_highlights', []))}")
                print(f"   User rating: {result_data.get('user_rating', 'None')}")
                
                # Verify both dataset and insights are present
                if result_data.get('dataset') and result_data.get('insights'):
                    print("✅ BOTH dataset and insights are present!")
                elif result_data.get('dataset'):
                    print("⚠️  Only dataset present, no insights")
                elif result_data.get('insights'):
                    print("⚠️  Only insights present, no dataset")
                else:
                    print("❌ Neither dataset nor insights present")
                    
            else:
                print(f"❌ Failed to get job results: {response.status_code}")
                print(f"   Error: {response.text}")
        else:
            print("No recent queries found to test")
    else:
        print(f"❌ Failed to get recent queries: {response.status_code}")

if __name__ == "__main__":
    test_api_response_structure() 