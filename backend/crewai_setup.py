"""
CrewAI Setup for Webhound - AI-Powered Dataset Builder
"""

import os
from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
# Tavily will be imported in the _create_tavily_tool method
import json
import asyncio
from datetime import datetime

class WebhoundCrewAI:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=self.gemini_api_key,
            temperature=0.1
        )
        
        # Initialize search tool - using Tavily instead of DuckDuckGo
        self.search_tool = self._create_tavily_tool()
        
        # Create agents
        self.web_researcher = self._create_web_researcher()
        self.data_extractor = self._create_data_extractor()
        self.data_validator = self._create_data_validator()
    
    def _create_tavily_tool(self):
        """Create a Tavily search tool"""
        from langchain.tools import Tool
        from tavily import TavilyClient
        
        if not self.tavily_api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        
        tavily_client = TavilyClient(api_key=self.tavily_api_key)
        
        def search_tavily(query: str) -> str:
            """Search the web using Tavily API"""
            try:
                response = tavily_client.search(
                    query=query,
                    search_depth="basic",
                    max_results=5
                )
                
                # Format the results
                results = []
                for result in response.get('results', []):
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'content': result.get('content', '')
                    })
                
                return f"Search results for '{query}':\n" + "\n\n".join([
                    f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}"
                    for r in results
                ])
            except Exception as e:
                return f"Error searching: {str(e)}"
        
        return Tool(
            name="tavily_search",
            description="Search the web for current information using Tavily API",
            func=search_tavily
        )
    
    def _create_web_researcher(self) -> Agent:
        """Create the Web Research Agent"""
        return Agent(
            role="Web Research Specialist",
            goal="Find comprehensive and accurate information from web sources",
            backstory="""You are an expert web researcher with years of experience in 
            finding reliable information from various online sources. You excel at 
            identifying authoritative websites and extracting relevant data.""",
            tools=[self.search_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def _create_data_extractor(self) -> Agent:
        """Create the Data Extraction Agent"""
        return Agent(
            role="Data Extraction Specialist",
            goal="Extract and structure data from web search results into organized datasets",
            backstory="""You are a data extraction expert who specializes in converting 
            unstructured web content into structured, usable datasets. You have a keen 
            eye for identifying patterns and organizing information logically.""",
            tools=[],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def _create_data_validator(self) -> Agent:
        """Create the Data Validation Agent"""
        return Agent(
            role="Data Quality Assurance Specialist",
            goal="Validate and ensure the quality and accuracy of extracted datasets",
            backstory="""You are a data quality expert who ensures that all extracted 
            data is accurate, complete, and properly formatted. You verify sources and 
            cross-reference information for reliability.""",
            tools=[],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def create_dataset(self, query: str) -> Dict[str, Any]:
        """Create a dataset using the CrewAI workflow"""
        
        # Task 1: Web Research
        research_task = Task(
            description=f"""
            Research the following query thoroughly: "{query}"
            
            Your task is to:
            1. Search for relevant information using multiple search queries
            2. Identify authoritative sources
            3. Collect comprehensive data points
            4. Document all sources used
            
            Focus on finding accurate, up-to-date information from reliable sources.
            """,
            agent=self.web_researcher,
            expected_output="A comprehensive research report with multiple data points and source URLs"
        )
        
        # Task 2: Data Extraction
        extraction_task = Task(
            description=f"""
            Based on the research results, extract and structure data for the query: "{query}"
            
            Your task is to:
            1. Analyze the research findings
            2. Identify the key data points
            3. Structure the data in a consistent format
            4. Create a JSON dataset with proper fields
            
            Return the data in this format:
            {{
                "data": [
                    {{"field1": "value1", "field2": "value2"}},
                    ...
                ],
                "sources": ["url1", "url2", ...],
                "extraction_notes": "Brief notes about the extraction process"
            }}
            """,
            agent=self.data_extractor,
            expected_output="A structured JSON dataset with extracted data and source URLs",
            context=[research_task]
        )
        
        # Task 3: Data Validation
        validation_task = Task(
            description=f"""
            Validate the extracted dataset for the query: "{query}"
            
            Your task is to:
            1. Verify the accuracy of extracted data
            2. Check for completeness and consistency
            3. Validate source reliability
            4. Ensure proper data formatting
            5. Provide quality assessment
            
            Return the final validated dataset in this format:
            {{
                "data": [
                    {{"field1": "value1", "field2": "value2"}},
                    ...
                ],
                "sources": ["url1", "url2", ...],
                "validation_status": "validated",
                "quality_score": "high/medium/low",
                "validation_notes": "Notes about validation process"
            }}
            """,
            agent=self.data_validator,
            expected_output="A validated dataset with quality assessment",
            context=[extraction_task]
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[self.web_researcher, self.data_extractor, self.data_validator],
            tasks=[research_task, extraction_task, validation_task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            # Execute the crew workflow
            result = crew.kickoff()
            
            # Parse the result
            if hasattr(result, 'raw') and result.raw:
                # Try to extract JSON from the result
                try:
                    # Look for JSON in the result
                    import re
                    json_match = re.search(r'\{.*\}', str(result.raw), re.DOTALL)
                    if json_match:
                        parsed_result = json.loads(json_match.group())
                        return parsed_result
                    else:
                        # Fallback: create basic structure
                        return {
                            "data": [],
                            "sources": [],
                            "validation_status": "completed",
                            "quality_score": "unknown",
                            "validation_notes": "Result parsing failed, but workflow completed"
                        }
                except json.JSONDecodeError:
                    return {
                        "data": [],
                        "sources": [],
                        "validation_status": "completed",
                        "quality_score": "unknown",
                        "validation_notes": "JSON parsing failed"
                    }
            else:
                return {
                    "data": [],
                    "sources": [],
                    "validation_status": "completed",
                    "quality_score": "unknown",
                    "validation_notes": "No result data available"
                }
                
        except Exception as e:
            return {
                "data": [],
                "sources": [],
                "validation_status": "failed",
                "quality_score": "unknown",
                "validation_notes": f"Error: {str(e)}"
            }

# Async wrapper for CrewAI
async def create_dataset_async(query: str) -> Dict[str, Any]:
    """Async wrapper for CrewAI dataset creation"""
    loop = asyncio.get_event_loop()
    crew_ai = WebhoundCrewAI()
    
    # Run CrewAI in thread pool to avoid blocking
    result = await loop.run_in_executor(None, crew_ai.create_dataset, query)
    return result 