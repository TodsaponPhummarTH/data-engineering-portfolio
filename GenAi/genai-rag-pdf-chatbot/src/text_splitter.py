"""
Text Splitter Module
===================

This module provides functionality for splitting text into manageable chunks.
It includes various splitting strategies and optimization techniques.

Key Features:
- Multiple splitting strategies (by character count, sentences, paragraphs)
- Overlapping chunks for better context
- Length optimization
- Type-safe operations
"""

from typing import List, Optional
import re

class TextSplitter:
    """
    TextSplitter class for splitting text into chunks.
    
    This class provides methods to:
    - Split text by character count
    - Split text by sentences
    - Split text by paragraphs
    - Create overlapping chunks
    """
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        """
        Initialize the TextSplitter with chunk parameters.
        
        Args:
            chunk_size: Maximum length of each chunk
            overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        
    def split_by_chars(self, text: str) -> List[str]:
        """
        Split text into chunks based on character count.
        
        Args:
            text: Input text to split
        
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunks.append(text[start:end])
            start = end - self.overlap
            
        return chunks

    def split_by_sentences(self, text: str) -> List[str]:
        """
        Split text into chunks based on sentence boundaries.
        
        Args:
            text: Input text to split
        
        Returns:
            List of text chunks
        """
        # Split text into sentences using regex
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
                current_chunk += (" " if current_chunk else "") + sentence
            else:
                chunks.append(current_chunk)
                current_chunk = sentence
                
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    def split_by_paragraphs(self, text: str) -> List[str]:
        """
        Split text into chunks based on paragraph boundaries.
        
        Args:
            text: Input text to split
        
        Returns:
            List of text chunks
        """
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= self.chunk_size:
                current_chunk += ("\n\n" if current_chunk else "") + paragraph
            else:
                chunks.append(current_chunk)
                current_chunk = paragraph
                
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    def optimize_chunks(self, chunks: List[str]) -> List[str]:
        """
        Optimize chunks by:
        - Removing empty chunks
        - Trimming whitespace
        - Ensuring minimum length
        
        Args:
            chunks: List of text chunks to optimize
        
        Returns:
            List of optimized chunks
        """
        optimized_chunks = []
        min_chunk_size = 50  # Minimum meaningful chunk size
        
        for chunk in chunks:
            chunk = chunk.strip()
            if chunk and len(chunk) >= min_chunk_size:
                optimized_chunks.append(chunk)
                
        return optimized_chunks

def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    Split text into chunks based on character count.
    
    Args:
        text: Input text to split
        chunk_size: Maximum length of each chunk
        chunk_overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    text = text.replace("\n", "\n\n").replace("\r", "\n\n").replace("\t", "\n\n")
    text = text.replace("\n\n\n\n", "\n\n")
    text = text.replace("   ", " ").replace("  ", " ")
    text = text.strip()
    text = text.replace("\n\n", "\n")

    splitter = TextSplitter(chunk_size=chunk_size, overlap=chunk_overlap)
    return splitter.split_by_chars(text)

# Example usage
if __name__ == "__main__":
    """
    Example usage of TextSplitter class
    """
    try:
        # Create text splitter instance
        splitter = TextSplitter(chunk_size=1000, overlap=100)
        
        # Example text
        example_text = """
        This is a sample text that we want to split into chunks. It contains multiple sentences and paragraphs.
        
        Here's another paragraph with more content. We'll use this to demonstrate different splitting strategies.
        """
        
        # Split by characters
        char_chunks = splitter.split_by_chars(example_text)
        print(f"\nCharacter-based chunks ({len(char_chunks)}):")
        for i, chunk in enumerate(char_chunks, 1):
            print(f"Chunk {i}: {len(chunk)} characters")
            
        # Split by sentences
        sentence_chunks = splitter.split_by_sentences(example_text)
        print(f"\nSentence-based chunks ({len(sentence_chunks)}):")
        for i, chunk in enumerate(sentence_chunks, 1):
            print(f"Chunk {i}: {len(chunk)} characters")
            
        # Split by paragraphs
        paragraph_chunks = splitter.split_by_paragraphs(example_text)
        print(f"\nParagraph-based chunks ({len(paragraph_chunks)}):")
        for i, chunk in enumerate(paragraph_chunks, 1):
            print(f"Chunk {i}: {len(chunk)} characters")
            
    except Exception as e:
        print(f"Error splitting text: {str(e)}")

"""
Text Splitter Module:
Created a TextSplitter class
Added multiple splitting strategies (character, sentence, paragraph)
Implemented chunk optimization
Added overlapping support
Added comprehensive documentation
"""