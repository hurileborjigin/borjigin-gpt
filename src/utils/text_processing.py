# src/utils/text_processing.py
from typing import List, Dict
import re

class TextProcessor:
    """Text processing utilities"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
        return text.strip()
    
    @staticmethod
    def extract_sections(text: str, sections: List[str]) -> Dict[str, str]:
        """Extract sections from CV text"""
        result = {}
        text_lower = text.lower()
        
        for i, section in enumerate(sections):
            section_lower = section.lower()
            start_idx = text_lower.find(section_lower)
            
            if start_idx != -1:
                # Find the end (next section or end of text)
                end_idx = len(text)
                for next_section in sections[i+1:]:
                    next_idx = text_lower.find(next_section.lower(), start_idx + 1)
                    if next_idx != -1:
                        end_idx = next_idx
                        break
                
                result[section] = text[start_idx:end_idx].strip()
        
        return result
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += chunk_size - overlap
        
        return chunks