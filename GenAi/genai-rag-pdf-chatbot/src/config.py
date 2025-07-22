"""
Configuration Module
===================

This module contains all configuration settings for the RAG PDF Chatbot system.
It includes settings for text processing, embedding models, and vector store.

Key Features:
- Centralized configuration management
"""

from dataclasses import dataclass

@dataclass
class AppConfig:
    """
    Main application configuration
    """
    chunk_size: int = 1000
    chunk_overlap: int = 100
    model_name: str = "all-MiniLM-L6-v2"
    vector_store_path: str = "vectorstore"
    debug_mode: bool = False

# Initialize the global config
config = AppConfig()

# Example usage
if __name__ == "__main__":
    """
    Example usage of configuration
    """
    print(f"Current settings:")
    print(f"Chunk size: {config.chunk_size}")
    print(f"Embedding model: {config.model_name}")
    print(f"Vector store path: {config.vector_store_path}")
    print(f"Chunk size: {config.text_processing.chunk_size}")
    print(f"Embedding model: {config.embedding.model_name}")
    print(f"Vector store path: {config.vector_store.index_path}")