"""
Embedder Module
==============

This module provides functionality for generating text embeddings using various models.
It supports multiple embedding models and provides a unified interface for embedding generation.

Key Features:
- Support for multiple embedding models
- Batch processing for efficiency
- Type-safe operations
- Error handling and validation
"""

from typing import List, Optional, Union
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel

class Embedder:
    """
    Embedder class for generating text embeddings.
    
    This class provides methods to:
    - Initialize different embedding models
    - Generate embeddings for text
    - Process embeddings in batches
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the Embedder with a specific model.
        
        Args:
            model_name: Name of the pre-trained model to use
        """
        self.model = SentenceTransformer(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def embed(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """
        Generate embeddings for the given text(s).
        
        Args:
            texts: Single text string or list of text strings
        
        Returns:
            List of embeddings (one per input text)
        
        Raises:
            ValueError: If input is empty
            RuntimeError: If embedding generation fails
        """
        if not texts:
            raise ValueError("Input text cannot be empty")
            
        try:
            # Convert single string to list if necessary
            if isinstance(texts, str):
                texts = [texts]
                
            # Generate embeddings
            embeddings = self.model.encode(
                texts,
                batch_size=32,  # Optimal batch size for efficiency
                show_progress_bar=False,
                convert_to_tensor=True
            )
            
            # Convert to list of lists for consistency
            return embeddings.cpu().numpy().tolist()
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate embeddings: {str(e)}")

    def batch_embed(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for large text lists using batch processing.
        
        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process at once
        
        Returns:
            List of embeddings (one per input text)
        """
        if not texts:
            return []
            
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.embed(batch)
            all_embeddings.extend(embeddings)
            
        return all_embeddings

# Example usage
if __name__ == "__main__":
    """
    Example usage of Embedder class
    """
    # Create an embedder instance
    embedder = Embedder()
    
    # Example text
    example_text = "This is a test sentence."
    
    try:
        # Generate single embedding
        embedding = embedder.embed(example_text)
        print(f"Generated embedding of size: {len(embedding[0])}")
        
        # Generate embeddings for multiple texts
        texts = [example_text] * 100  # Create a list of 100 texts
        embeddings = embedder.batch_embed(texts)
        print(f"Generated {len(embeddings)} embeddings")
        
    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")



"""
Embedder Module:
Created a robust Embedder class
Added batch processing support
Implemented proper error handling
Added GPU support
Added example usage
"""