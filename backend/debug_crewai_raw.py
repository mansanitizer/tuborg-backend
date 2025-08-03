#!/usr/bin/env python3
"""
Debug script to see raw CrewAI result
"""

import asyncio
from crewai_setup_working import create_dataset_async

async def debug_crewai_raw():
    """Debug the raw CrewAI result"""
    
    query = "10 movies featuring kevin spacey"
    print(f"🔍 Testing CrewAI with query: {query}")
    
    try:
        result = await create_dataset_async(query)
        print(f"\n📊 CrewAI Result Type: {type(result)}")
        
        if isinstance(result, dict):
            print(f"📊 CrewAI Result Keys: {list(result.keys())}")
            
            # Check the data field specifically
            data = result.get('data', [])
            print(f"📊 Data field type: {type(data)}")
            print(f"📊 Data field length: {len(data)}")
            
            if data and len(data) > 0:
                first_item = data[0]
                print(f"📊 First item type: {type(first_item)}")
                print(f"📊 First item: {first_item}")
                
                # Check if it has a 'result' field with JSON
                if isinstance(first_item, dict) and 'result' in first_item:
                    result_str = first_item['result']
                    print(f"📊 Result string starts with: {result_str[:100]}...")
                    
                    # Try to parse the JSON manually
                    import re
                    import json
                    
                    # Look for JSON in markdown code blocks
                    code_block_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', result_str, re.DOTALL)
                    if code_block_match:
                        json_content = code_block_match.group(1).strip()
                        print(f"✅ Found JSON in code block: {json_content[:100]}...")
                        
                        try:
                            parsed_json = json.loads(json_content)
                            print(f"✅ Successfully parsed JSON with keys: {list(parsed_json.keys())}")
                            print(f"✅ Data array length: {len(parsed_json.get('data', []))}")
                        except json.JSONDecodeError as e:
                            print(f"❌ JSON parsing failed: {e}")
                    else:
                        print("❌ No code block found")
        else:
            print(f"   Result: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_crewai_raw()) 