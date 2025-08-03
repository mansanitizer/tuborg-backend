#!/usr/bin/env python3
"""
Test new query with simple parsing
"""

import requests
import time
import json

def test_new_query():
    """Test a new query to see if parsing works"""
    
    # Submit a new query
    query = "top 3 programming languages 2025"
    print(f"🔍 Submitting new query: {query}")
    
    try:
        response = requests.post("http://localhost:8000/api/datasets/generate", json={"query": query})
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get('job_id')
            print(f"   Job ID: {job_id}")
            
            # Wait a bit for processing
            print("   Waiting for processing...")
            time.sleep(10)
            
            # Check the results
            response = requests.get(f"http://localhost:8000/api/datasets/{job_id}/results")
            print(f"   Results status: {response.status_code}")
            
            if response.status_code == 200:
                result_data = response.json()
                print(f"   Status: {result_data.get('status')}")
                print(f"   Dataset records: {len(result_data.get('dataset', []))}")
                print(f"   Sources: {result_data.get('sources', [])}")
                print(f"   Validation status: {result_data.get('validation_status')}")
                print(f"   Quality score: {result_data.get('quality_score')}")
                
                # Check if dataset has proper structure
                dataset = result_data.get('dataset', [])
                if dataset and len(dataset) > 0:
                    first_item = dataset[0]
                    print(f"   First item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}")
                    
                    # Check if it's properly parsed (should have title, year, etc.)
                    if isinstance(first_item, dict) and 'title' in first_item:
                        print("✅ Data is properly parsed!")
                    elif isinstance(first_item, dict) and 'result' in first_item:
                        print("❌ Data still contains raw string")
                    else:
                        print(f"⚠️  Unexpected data structure: {first_item}")
                else:
                    print("❌ No dataset records")
            else:
                print(f"   Error getting results: {response.text}")
        else:
            print(f"   Error submitting query: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_new_query() 