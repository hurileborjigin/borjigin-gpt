# src/utils/document_parser.py
from typing import Optional
import PyPDF2
import docx
from pathlib import Path

class DocumentParser:
    """Parse various document formats"""
    
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        except Exception as e:
            print(f"Error parsing PDF: {e}")
        return text
    
    @staticmethod
    def parse_docx(file_path: str) -> str:
        """Extract text from DOCX"""
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error parsing DOCX: {e}")
        return text
    
    @staticmethod
    def parse_txt(file_path: str) -> str:
        """Extract text from TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error parsing TXT: {e}")
            return ""
    
    @staticmethod
    def parse_document(file_path: str) -> str:
        """Auto-detect and parse document"""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.pdf':
            return DocumentParser.parse_pdf(file_path)
        elif extension in ['.docx', '.doc']:
            return DocumentParser.parse_docx(file_path)
        elif extension == '.txt':
            return DocumentParser.parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")