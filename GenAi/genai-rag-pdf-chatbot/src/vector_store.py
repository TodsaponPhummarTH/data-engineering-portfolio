from typing import List, Tuple
import numpy as np
import faiss
import pickle
from pathlib import Path
from src.embedder import Embedder

class VectorStore:
    """
    VectorStore class for managing FAISS-based vector storage.
    
    This class provides methods to:
    - Save vector embeddings and their associated metadata
    - Load existing vector stores
    - Perform similarity searches
    - Manage vector store persistence
    """
    
    def __init__(self, index_path: str = "vectorstore/index.faiss", metadata_path: str = "vectorstore/metadata.pkl"):
        """
        Initialize the VectorStore with default paths.
        
        Args:
            index_path: Path to store the FAISS index
            metadata_path: Path to store the metadata pickle file
        """
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        self.index = None
        self.chunks = None
        self.embedder = Embedder()  # For similarity search

    def save(self, embeddings: List[List[float]], chunks: List[str]) -> None:
        """
        Save embeddings and metadata to disk.
        
        Args:
            embeddings: List of vector embeddings
            chunks: List of text chunks corresponding to embeddings
        """
        # Convert embeddings to numpy array
        embeddings_array = np.array(embeddings).astype(np.float32)
        
        # Create FAISS index
        self.index = faiss.IndexFlatL2(embeddings_array.shape[1])
        self.index.add(embeddings_array)
        
        # Save index
        faiss.write_index(self.index, str(self.index_path))
        
        # Save metadata
        self.chunks = chunks
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(chunks, f)

    def load(self) -> Tuple[faiss.Index, List[str]]:
        """
        Load existing vector store from disk.
        
        Returns:
            Tuple containing (FAISS index, list of chunks)
        """
        if not self.index_path.exists() or not self.metadata_path.exists():
            raise FileNotFoundError("Vector store files not found")
            
        # Load index
        self.index = faiss.read_index(str(self.index_path))
        
        # Load metadata
        with open(self.metadata_path, 'rb') as f:
            self.chunks = pickle.load(f)
            
        return self.index, self.chunks

    def search_similar(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Perform similarity search on the vector store.
        
        Args:
            query: Search query text
            top_k: Number of top results to return
            
        Returns:
            List of tuples containing (chunk text, similarity score)
        """
        if not self.index or not self.chunks:
            self.index, self.chunks = self.load()
            
        if not self.index or not self.chunks:
            raise ValueError("Vector store not initialized")
            
        # Generate embedding for the query
        query_embedding = self.embedder.embed(query)[0]
        
        # Convert to numpy array
        query_array = np.array(query_embedding).astype(np.float32).reshape(1, -1)
        
        # Perform search
        D, I = self.index.search(query_array, top_k)
        
        # Get results
        results = []
        for i, score in zip(I[0], D[0]):
            results.append((self.chunks[i], float(score)))
            
        return results

    def get_context_for_query(self, query: str, top_k: int = 3) -> str:
        """
        Get relevant context for a query by performing similarity search.
        
        Args:
            query: Search query text
            top_k: Number of top results to consider
            
        Returns:
            Combined context from most relevant chunks
        """
        results = self.search_similar(query, top_k)
        context = "\n".join([chunk for chunk, _ in results])
        return context
