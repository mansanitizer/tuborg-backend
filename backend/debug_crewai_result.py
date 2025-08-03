#!/usr/bin/env python3
"""
Debug script to see CrewAI result structure
"""

import asyncio
from crewai_setup_working import create_dataset_async

async def debug_crewai_result():
    """Debug what CrewAI actually returns"""
    
    query = "best fitness podcast 2025"
    print(f"🔍 Testing CrewAI with query: {query}")
    
    try:
        result = await create_dataset_async(query)
        print(f"\n📊 CrewAI Result Type: {type(result)}")
        print(f"📊 CrewAI Result Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"   {key}: {type(value)} = {value}")
        else:
            print(f"   Result: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_crewai_result()) 