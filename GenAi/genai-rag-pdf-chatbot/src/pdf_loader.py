"""
PDF Loader Module
================

This module provides functionality for loading and processing PDF documents.
It handles PDF reading, text extraction, and basic document analysis.

Key Features:
- Efficient PDF text extraction
- Page-level text processing
- Error handling and validation
- Support for multiple PDF formats
"""

from typing import List, Dict, Optional
import os
from pathlib import Path
import fitz  # PyMuPDF

class PDFLoader:
    """
    PDFLoader class for handling PDF document processing.
    
    This class provides methods to:
    - Load PDF documents
    - Extract text content
    - Process document metadata
    - Handle multiple PDF files
    """
    
    def __init__(self, pdf_path: str):
        """
        Initialize the PDFLoader with the PDF file path.
        
        Args:
            pdf_path: Path to the PDF file
        
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If file is not a PDF
        """
        self.pdf_path = Path(pdf_path)
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        if not self.pdf_path.suffix.lower() == ".pdf":
            raise ValueError(f"File is not a PDF: {pdf_path}")
            
        self.reader = None
        self.pages = None
        self.text = None

    def load_document(self) -> None:
        """
        Load the PDF document and extract basic information.
        
        Raises:
            RuntimeError: If document loading fails
        """
        try:
            self.reader = fitz.open(str(self.pdf_path))
            self.pages = [self.reader.load_page(i) for i in range(len(self.reader))]
            
            if not self.pages:
                raise RuntimeError("No pages found in PDF")
                
        except Exception as e:
            raise RuntimeError(f"Failed to load document: {str(e)}")

    def extract_text(self) -> str:
        """
        Extract text content from the PDF document using PyMuPDF.
        
        Returns:
            str: The extracted text content
        
        Raises:
            RuntimeError: If text extraction fails
        """
        try:
            doc = fitz.open(str(self.pdf_path))
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
            
            self.text = text.strip()
            return self.text
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract text: {str(e)}")
        finally:
            doc.close()

    def get_document_metadata(self) -> Dict[str, str]:
        """
        Get metadata information about the PDF document.
        
        Returns:
            dict: Dictionary containing document metadata
        """
        if not self.reader:
            self.load_document()
            
        metadata = {
            "title": self.reader.metadata.title or "Untitled",
            "author": self.reader.metadata.author or "Unknown",
            "creator": self.reader.metadata.creator or "Unknown",
            "producer": self.reader.metadata.producer or "Unknown",
            "number_of_pages": str(len(self.pages))
        }
        
        return metadata

    def get_text_by_page(self) -> List[str]:
        """
        Get text content organized by page.
        
        Returns:
            list: List of strings, one per page
        """
        if not self.pages:
            self.load_document()
            
        page_texts = []
        for page in self.pages:
            text = page.extract_text()
            if text:
                page_texts.append(text.strip())
        
        return page_texts

# Example usage
if __name__ == "__main__":
    """
    Example usage of PDFLoader class
    """
    try:
        # Create PDF loader instance
        pdf_loader = PDFLoader("example.pdf")
        
        # Load document and extract text
        pdf_loader.load_document()
        text = pdf_loader.extract_text()
        print(f"Extracted text length: {len(text)} characters")
        
        # Get document metadata
        metadata = pdf_loader.get_document_metadata()
        print("\nDocument Metadata:")
        for key, value in metadata.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")


"""
PDF Loader Module:
Created a PDFLoader class
Added metadata extraction
Implemented proper error handling
Added page-level text extraction
Added file validation
"""