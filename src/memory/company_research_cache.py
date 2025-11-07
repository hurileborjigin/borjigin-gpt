# src/memory/company_research_cache.py
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from src.config.settings import settings

class CompanyResearchCache:
    """Manages cached company research data"""
    
    def __init__(self):
        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=settings.azure_openai_embedding_deployment,
            openai_api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key
        )
        
        self.vectorstore = Chroma(
            collection_name=settings.company_research_collection_name,
            embedding_function=self.embeddings,
            persist_directory=settings.chroma_persist_directory
        )
    
    def add_research(
        self,
        company_name: str,
        research_data: Dict[str, Any]
    ) -> None:
        """Cache company research data"""
        timestamp = datetime.now()
        
        # Store different aspects of research
        documents = []
        
        # Company overview
        if "overview" in research_data:
            doc = Document(
                page_content=research_data["overview"],
                metadata={
                    "company": company_name,
                    "type": "overview",
                    "timestamp": timestamp.isoformat(),
                    "expires_at": (timestamp + timedelta(days=settings.research_cache_days)).isoformat()
                }
            )
            documents.append(doc)
        
        # Company culture
        if "culture" in research_data:
            doc = Document(
                page_content=research_data["culture"],
                metadata={
                    "company": company_name,
                    "type": "culture",
                    "timestamp": timestamp.isoformat(),
                    "expires_at": (timestamp + timedelta(days=settings.research_cache_days)).isoformat()
                }
            )
            documents.append(doc)
        
        # Recent news
        if "news" in research_data:
            news_text = "\n\n".join(research_data["news"]) if isinstance(research_data["news"], list) else research_data["news"]
            doc = Document(
                page_content=news_text,
                metadata={
                    "company": company_name,
                    "type": "news",
                    "timestamp": timestamp.isoformat(),
                    "expires_at": (timestamp + timedelta(days=settings.research_cache_days)).isoformat()
                }
            )
            documents.append(doc)
        
        # Position analysis
        if "position_analysis" in research_data:
            doc = Document(
                page_content=json.dumps(research_data["position_analysis"], indent=2),
                metadata={
                    "company": company_name,
                    "type": "position_analysis",
                    "position": research_data.get("position", ""),
                    "timestamp": timestamp.isoformat(),
                    "expires_at": (timestamp + timedelta(days=settings.research_cache_days)).isoformat()
                }
            )
            documents.append(doc)
        
        if documents:
            self.vectorstore.add_documents(documents)
            print(f"✅ Cached research for {company_name} ({len(documents)} documents)")
    
    def get_research(
        self,
        company_name: str,
        force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Retrieve cached research if not expired"""
        if force_refresh:
            return None
        
        # Search for company research
        results = self.vectorstore.similarity_search(
            company_name,
            k=10,
            filter={"company": company_name}
        )
        
        if not results:
            return None
        
        # Check if expired
        now = datetime.now()
        research_data = {}
        
        for doc in results:
            expires_at = doc.metadata.get("expires_at")
            if expires_at:
                expire_date = datetime.fromisoformat(expires_at)
                if expire_date < now:
                    continue  # Skip expired
            
            doc_type = doc.metadata.get("type")
            if doc_type:
                research_data[doc_type] = doc.page_content
        
        return research_data if research_data else None
    
    def clear_company_research(self, company_name: str) -> None:
        """Clear research for a specific company"""
        print(f"🗑️ Clearing research cache for {company_name}")
        # Note: Simplified - would need proper implementation
        pass
    
    def clear_expired(self) -> None:
        """Clear all expired research"""
        print("🗑️ Clearing expired research cache")
        # Note: Simplified - would need proper implementation
        pass