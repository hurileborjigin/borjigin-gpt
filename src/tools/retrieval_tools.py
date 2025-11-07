# src/tools/retrieval_tools.py
from langchain_core.tools import tool
from langchain_core.documents import Document
from typing import List, Dict, Any
from src.memory.long_term_memory import LongTermMemory
from src.memory.company_research_cache import CompanyResearchCache

class RetrievalTools:
    """Tools for retrieving information from memory"""
    
    def __init__(
        self,
        long_term_memory: LongTermMemory,
        research_cache: CompanyResearchCache
    ):
        self.ltm = long_term_memory
        self.research_cache = research_cache
    
    def create_cv_retrieval_tool(self):
        """Create CV retrieval tool"""
        ltm = self.ltm
        
        @tool
        def retrieve_cv_info(query: str) -> str:
            """
            Retrieve relevant information from CV based on the query.
            Use this when you need to find specific skills, experiences, or qualifications from the user's CV.
            
            Args:
                query: The search query (e.g., "python experience", "leadership skills")
            
            Returns:
                Relevant CV information as a formatted string
            """
            results = ltm.search(query, k=3, filter_type="cv")
            
            if not results:
                return "No relevant CV information found."
            
            formatted = []
            for i, doc in enumerate(results, 1):
                formatted.append(f"[CV Section {i}]\n{doc.page_content}\n")
            
            return "\n".join(formatted)
        
        return retrieve_cv_info
    
    def create_experience_retrieval_tool(self):
        """Create experience retrieval tool"""
        ltm = self.ltm
        
        @tool
        def retrieve_experiences(query: str) -> str:
            """
            Retrieve relevant past experiences and stories based on the query.
            Use this when you need specific examples, projects, or achievements.
            
            Args:
                query: The search query (e.g., "challenging project", "team leadership")
            
            Returns:
                Relevant experiences as a formatted string
            """
            results = ltm.search(query, k=3, filter_type="experience")
            
            if not results:
                return "No relevant experiences found."
            
            formatted = []
            for i, doc in enumerate(results, 1):
                metadata = doc.metadata
                tags = metadata.get("tags", [])
                tag_str = f" [Tags: {', '.join(tags)}]" if tags else ""
                
                formatted.append(f"[Experience {i}]{tag_str}\n{doc.page_content}\n")
            
            return "\n".join(formatted)
        
        return retrieve_experiences
    
    def create_personality_retrieval_tool(self):
        """Create personality retrieval tool"""
        ltm = self.ltm
        
        @tool
        def retrieve_personality() -> str:
            """
            Retrieve personality traits and characteristics.
            Use this to understand the user's communication style, values, and strengths.
            
            Returns:
                Personality profile as a formatted string
            """
            results = ltm.search("personality traits characteristics", k=2, filter_type="personality")
            
            if not results:
                return "No personality profile found."
            
            return "\n\n".join([doc.page_content for doc in results])
        
        return retrieve_personality
    
    def create_company_research_tool(self):
        """Create company research retrieval tool"""
        research_cache = self.research_cache
        
        @tool
        def retrieve_company_research(company_name: str) -> str:
            """
            Retrieve cached company research data.
            Use this to get company information, culture, and recent news.
            
            Args:
                company_name: Name of the company
            
            Returns:
                Company research data as a formatted string
            """
            research = research_cache.get_research(company_name)
            
            if not research:
                return f"No cached research found for {company_name}."
            
            formatted = []
            
            if "overview" in research:
                formatted.append(f"**Company Overview:**\n{research['overview']}\n")
            
            if "culture" in research:
                formatted.append(f"**Company Culture:**\n{research['culture']}\n")
            
            if "news" in research:
                formatted.append(f"**Recent News:**\n{research['news']}\n")
            
            if "position_analysis" in research:
                formatted.append(f"**Position Analysis:**\n{research['position_analysis']}\n")
            
            return "\n".join(formatted)
        
        return retrieve_company_research
    
    def get_all_tools(self) -> List:
        """Get all retrieval tools"""
        return [
            self.create_cv_retrieval_tool(),
            self.create_experience_retrieval_tool(),
            self.create_personality_retrieval_tool(),
            self.create_company_research_tool()
        ]