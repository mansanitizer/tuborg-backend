"""
Working CrewAI Setup for Webhound - AI-Powered Dataset Builder
This version works without requiring valid API keys for search services
"""

import os
from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
import json
import asyncio
from datetime import datetime

class WebhoundCrewAI:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize LLM with configurable model (default to flash)
        self.model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        print(f"Using Gemini model: {self.model}")
        
        self.llm = ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=self.gemini_api_key,
            temperature=0.1
        )
        
        # Initialize search tool
        self.search_tool = self._create_search_tool()
        
        # Create agents
        self.web_researcher = self._create_web_researcher()
        self.data_extractor = self._create_data_extractor()
        self.data_validator = self._create_data_validator()
    
    def _create_search_tool(self):
        """Create a search tool using available APIs with fallbacks"""
        from langchain.tools import Tool
        
        def search_web(query: str) -> str:
            """Search the web using available APIs with fallbacks"""
            try:
                # Try Tavily first if available and valid
                tavily_api_key = os.getenv("TAVILY_API_KEY")
                if tavily_api_key and tavily_api_key != "your_tavily_api_key_here":
                    try:
                        from tavily import TavilyClient
                        client = TavilyClient(api_key=tavily_api_key)
                        response = client.search(
                            query=query,
                            search_depth="basic",
                            max_results=3
                        )
                        
                        results = []
                        for result in response.get('results', []):
                            results.append({
                                'title': result.get('title', ''),
                                'url': result.get('url', ''),
                                'content': result.get('content', '')[:200] + '...'
                            })
                        
                        return f"Search results for '{query}':\n" + "\n\n".join([
                            f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}"
                            for r in results
                        ])
                    except Exception as e:
                        print(f"Tavily search failed: {e}")
                
                # Fallback to DuckDuckGo if available
                try:
                    from duckduckgo_search import DDGS
                    with DDGS() as ddgs:
                        results = list(ddgs.text(query, max_results=3))
                    
                    formatted_results = []
                    for result in results:
                        formatted_results.append({
                            'title': result.get('title', ''),
                            'url': result.get('link', ''),
                            'content': result.get('body', '')[:200] + '...'
                        })
                    
                    return f"Search results for '{query}':\n" + "\n\n".join([
                        f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}"
                        for r in formatted_results
                    ])
                except Exception as e:
                    print(f"DuckDuckGo search failed: {e}")
                
                # Final fallback: return a helpful message
                return f"""No search API available. Query: {query}

Since I cannot perform web searches, I'll provide general knowledge about this topic based on my training data. For the most current information, please provide a valid search API key or use a different search method."""
                        
            except Exception as e:
                return f"Error searching: {str(e)}"
        
        return Tool(
            name="web_search",
            description="Search the web for current information. Falls back to general knowledge if no search API is available.",
            func=search_web
        )
    
    def _create_web_researcher(self) -> Agent:
        """Create the Web Research Agent"""
        return Agent(
            role="Web Research Specialist",
            goal="Find comprehensive and accurate information from available sources",
            backstory="""You are an expert researcher with years of experience in 
            finding reliable information. You can use web search when available, 
            but also have extensive knowledge to provide helpful information when 
            search is not available.""",
            tools=[self.search_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def _create_data_extractor(self) -> Agent:
        """Create the Data Extraction Agent"""
        return Agent(
            role="Data Extraction Specialist",
            goal="Extract and structure data from research results into organized datasets",
            backstory="""You are a data extraction expert who specializes in converting 
            unstructured content into structured, usable datasets. You have a keen 
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
        
        # Task 1: Research
        research_task = Task(
            description=f"""
            Research the following query: "{query}"
            
            Your task is to:
            1. Search for relevant information using the web search tool if available
            2. If web search is not available, use your knowledge to provide helpful information
            3. Identify key data points and sources
            4. Provide a comprehensive summary
            
            Focus on finding accurate, up-to-date information from reliable sources.
            """,
            agent=self.web_researcher,
            expected_output="A comprehensive research summary with key findings and data points"
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
                "sources": ["source1", "source2", ...],
                "extraction_notes": "Brief notes about the extraction process"
            }}
            """,
            agent=self.data_extractor,
            expected_output="A structured JSON dataset with extracted data and sources",
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
                "sources": ["source1", "source2", ...],
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
                    # Look for JSON in the result (handle markdown code blocks)
                    import re
                    
                    # First try to extract from markdown code blocks
                    code_block_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', str(result.raw), re.DOTALL)
                    if code_block_match:
                        json_content = code_block_match.group(1).strip()
                        parsed_result = json.loads(json_content)
                    else:
                        # Fallback: look for JSON without code blocks
                        json_match = re.search(r'\{.*\}', str(result.raw), re.DOTALL)
                        if json_match:
                            json_content = json_match.group()
                            parsed_result = json.loads(json_content)
                        else:
                            # If no JSON found, create a simple structure
                            return {
                                "data": [{"query": query, "result": str(result.raw)}],
                                "sources": [],
                                "validation_status": "completed",
                                "quality_score": "unknown",
                                "validation_notes": "No JSON found in result"
                            }
                    
                    # Ensure all required fields are present
                    if "data" not in parsed_result:
                        parsed_result["data"] = []
                    if "sources" not in parsed_result:
                        parsed_result["sources"] = []
                    if "validation_status" not in parsed_result:
                        parsed_result["validation_status"] = "completed"
                    if "quality_score" not in parsed_result:
                        parsed_result["quality_score"] = "unknown"
                    if "validation_notes" not in parsed_result:
                        parsed_result["validation_notes"] = ""
                    
                    return parsed_result
                except json.JSONDecodeError:
                    return {
                        "data": [{"query": query, "result": str(result.raw)}],
                        "sources": [],
                        "validation_status": "completed",
                        "quality_score": "unknown",
                        "validation_notes": "JSON parsing failed, but workflow completed"
                    }
            else:
                return {
                    "data": [{"query": query, "result": str(result)}],
                    "sources": [],
                    "validation_status": "completed",
                    "quality_score": "unknown",
                    "validation_notes": "Workflow completed successfully"
                }
                
        except Exception as e:
            error_message = str(e)
            
            # Check for quota-related errors
            if any(keyword in error_message.lower() for keyword in [
                "quota", "429", "resourceexhausted", "rate limit", "exceeded"
            ]):
                return {
                    "data": [],
                    "sources": [],
                    "validation_status": "quota_exceeded",
                    "quality_score": "unknown",
                    "validation_notes": f"API quota exceeded: {error_message}"
                }
            else:
                return {
                    "data": [],
                    "sources": [],
                    "validation_status": "failed",
                    "quality_score": "unknown",
                    "validation_notes": f"Error: {error_message}"
                }

# Async wrapper for CrewAI
async def create_dataset_async(query: str) -> Dict[str, Any]:
    """Async wrapper for CrewAI dataset creation"""
    loop = asyncio.get_event_loop()
    crew_ai = WebhoundCrewAI()
    
    # Run CrewAI in thread pool to avoid blocking
    result = await loop.run_in_executor(None, crew_ai.create_dataset, query)
    return result 