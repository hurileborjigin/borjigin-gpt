# src/tools/web_search.py
from typing import List, Dict, Any, Optional
from tavily import TavilyClient
from src.config.settings import settings
import json

class WebSearchTool:
    """Web search using Tavily API"""
    
    def __init__(self):
        self.client = TavilyClient(api_key=settings.tavily_api_key)
    
    def search_company(
        self,
        company_name: str,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """Search for company information"""
        try:
            # Company overview search
            overview_query = f"{company_name} company overview mission values"
            overview_results = self.client.search(
                query=overview_query,
                max_results=max_results,
                search_depth="advanced"
            )
            
            # Company culture search
            culture_query = f"{company_name} company culture work environment employee reviews"
            culture_results = self.client.search(
                query=culture_query,
                max_results=max_results,
                search_depth="advanced"
            )
            
            # Recent news search
            news_query = f"{company_name} recent news updates 2024"
            news_results = self.client.search(
                query=news_query,
                max_results=max_results,
                search_depth="basic"
            )
            
            return {
                "overview": self._format_results(overview_results),
                "culture": self._format_results(culture_results),
                "news": self._format_results(news_results),
                "raw_data": {
                    "overview": overview_results,
                    "culture": culture_results,
                    "news": news_results
                }
            }
        except Exception as e:
            print(f"❌ Error searching for company: {e}")
            return {}
    
    def search_position(
        self,
        position: str,
        company_name: Optional[str] = None,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """Search for position/role information"""
        try:
            # Build query
            if company_name:
                query = f"{position} at {company_name} job requirements responsibilities"
            else:
                query = f"{position} job requirements responsibilities skills"
            
            results = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced"
            )
            
            # Search for similar positions
            similar_query = f"{position} job description requirements"
            similar_results = self.client.search(
                query=similar_query,
                max_results=max_results,
                search_depth="basic"
            )
            
            return {
                "position_info": self._format_results(results),
                "similar_positions": self._format_results(similar_results),
                "raw_data": {
                    "position": results,
                    "similar": similar_results
                }
            }
        except Exception as e:
            print(f"❌ Error searching for position: {e}")
            return {}
    
    def search_interview_questions(
        self,
        company_name: str,
        position: str,
        max_results: int = 5
    ) -> List[str]:
        """Search for common interview questions"""
        try:
            query = f"{company_name} {position} interview questions"
            results = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced"
            )
            
            return self._extract_questions(results)
        except Exception as e:
            print(f"❌ Error searching for interview questions: {e}")
            return []
    
    def _format_results(self, results: Dict[str, Any]) -> str:
        """Format Tavily results into readable text"""
        if not results or "results" not in results:
            return ""
        
        formatted = []
        for result in results["results"]:
            title = result.get("title", "")
            content = result.get("content", "")
            url = result.get("url", "")
            
            formatted.append(f"**{title}**\n{content}\nSource: {url}\n")
        
        return "\n".join(formatted)
    
    def _extract_questions(self, results: Dict[str, Any]) -> List[str]:
        """Extract interview questions from search results"""
        # This is a simplified extraction - in production you'd use NLP
        questions = []
        
        if not results or "results" not in results:
            return questions
        
        for result in results["results"]:
            content = result.get("content", "")
            # Simple heuristic: look for question marks
            sentences = content.split(".")
            for sentence in sentences:
                if "?" in sentence:
                    questions.append(sentence.strip())
        
        return questions[:10]  # Return top 10