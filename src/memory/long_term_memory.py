# src/memory/long_term_memory.py
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from src.config.settings import settings

class LongTermMemory:
    """Manages persistent user profile information in vector store"""
    
    def __init__(self):
        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=settings.azure_openai_embedding_deployment,
            openai_api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key
        )
        
        self.vectorstore = Chroma(
            collection_name=settings.long_term_collection_name,
            embedding_function=self.embeddings,
            persist_directory=settings.chroma_persist_directory
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def add_cv(self, cv_text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add CV to long-term memory with chunking"""
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "type": "cv",
            "timestamp": datetime.now().isoformat()
        })
        
        chunks = self.text_splitter.split_text(cv_text)
        documents = [
            Document(
                page_content=chunk,
                metadata={**metadata, "chunk_id": i}
            )
            for i, chunk in enumerate(chunks)
        ]
        
        self.vectorstore.add_documents(documents)
        print(f"✅ Added CV with {len(documents)} chunks to long-term memory")
    
    def add_personality(self, personality_data: Dict[str, Any]) -> None:
        """Add personality profile to long-term memory"""
        personality_text = self._format_personality(personality_data)
        
        doc = Document(
            page_content=personality_text,
            metadata={
                "type": "personality",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        self.vectorstore.add_documents([doc])
        print("✅ Added personality profile to long-term memory")
    
    def _format_personality(self, data: Dict[str, Any]) -> str:
        """Format personality data as readable text"""
        sections = []
        
        if "communication_style" in data:
            sections.append(f"Communication Style: {data['communication_style']}")
        
        if "work_values" in data:
            values = ", ".join(data['work_values']) if isinstance(data['work_values'], list) else data['work_values']
            sections.append(f"Work Values: {values}")
        
        if "strengths" in data:
            strengths = ", ".join(data['strengths']) if isinstance(data['strengths'], list) else data['strengths']
            sections.append(f"Strengths: {strengths}")
        
        if "weaknesses" in data:
            weaknesses = ", ".join(data['weaknesses']) if isinstance(data['weaknesses'], list) else data['weaknesses']
            sections.append(f"Areas for Improvement: {weaknesses}")
        
        if "career_goals" in data:
            sections.append(f"Career Goals: {data['career_goals']}")
        
        return "\n\n".join(sections)
    
    def add_experience(self, experience: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a single experience to long-term memory"""
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "type": "experience",
            "timestamp": datetime.now().isoformat()
        })
        
        doc = Document(page_content=experience, metadata=metadata)
        self.vectorstore.add_documents([doc])
        print("✅ Added experience to long-term memory")
    
    def add_experiences_batch(self, experiences: List[Dict[str, Any]]) -> None:
        """Add multiple experiences at once"""
        documents = []
        
        for exp in experiences:
            content = exp.get("content", "")
            metadata = exp.get("metadata", {})
            metadata.update({
                "type": "experience",
                "timestamp": datetime.now().isoformat()
            })
            
            doc = Document(page_content=content, metadata=metadata)
            documents.append(doc)
        
        self.vectorstore.add_documents(documents)
        print(f"✅ Added {len(documents)} experiences to long-term memory")
    
    def search(
        self, 
        query: str, 
        k: int = 5, 
        filter_type: Optional[str] = None
    ) -> List[Document]:
        """Search long-term memory with optional filtering"""
        search_kwargs = {"k": k}
        
        if filter_type:
            search_kwargs["filter"] = {"type": filter_type}
        
        results = self.vectorstore.similarity_search(query, **search_kwargs)
        return results
    
    def search_with_score(
        self,
        query: str,
        k: int = 5,
        filter_type: Optional[str] = None
    ) -> List[tuple[Document, float]]:
        """Search with relevance scores"""
        search_kwargs = {"k": k}
        
        if filter_type:
            search_kwargs["filter"] = {"type": filter_type}
        
        results = self.vectorstore.similarity_search_with_score(query, **search_kwargs)
        return results
    
    def get_all_experiences(self) -> List[Document]:
        """Retrieve all stored experiences"""
        # Note: This is a workaround as Chroma doesn't have a direct "get all" method
        return self.search("experience project work", k=100, filter_type="experience")
    
    def delete_by_type(self, memory_type: str) -> None:
        """Delete all memories of a specific type"""
        print(f"⚠️ Deleting all {memory_type} memories...")
        # This requires getting IDs first - simplified implementation
        # In production, you'd want to implement this more robustly
        pass
    
    def clear_all(self) -> None:
        """Clear all long-term memory"""
        try:
            self.vectorstore.delete_collection()
            self.vectorstore = Chroma(
                collection_name=settings.long_term_collection_name,
                embedding_function=self.embeddings,
                persist_directory=settings.chroma_persist_directory
            )
            print("✅ Cleared all long-term memory")
        except Exception as e:
            print(f"❌ Error clearing memory: {e}")