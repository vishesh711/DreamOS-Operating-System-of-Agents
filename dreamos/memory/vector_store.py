"""
Vector store implementation for DreamOS Memory Agent.
Uses FAISS for efficient similarity search.
"""
import os
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import datetime
import faiss
from tqdm import tqdm

from ..config import VECTOR_DB_PATH, DEBUG_MODE

class VectorStore:
    """
    Vector database for storing and retrieving memory embeddings.
    Uses FAISS for efficient vector similarity search.
    """
    
    def __init__(self, vector_db_path: Optional[str] = None):
        """
        Initialize the vector store.
        
        Args:
            vector_db_path: Path to store the vector database
        """
        self.vector_db_path = vector_db_path or VECTOR_DB_PATH
        self.index_path = os.path.join(self.vector_db_path, "memory_index.faiss")
        self.metadata_path = os.path.join(self.vector_db_path, "memory_metadata.json")
        
        # Embedding dimension - this should match your embedding model
        self.embedding_dim = 768  # for Groq embeddings
        
        # Initialize metadata and index to default values before loading
        self.metadata = []
        self.index = None
        
        # Initialize or load the vector index and metadata
        self.index, self.metadata = self._load_or_create_store()
    
    def _load_or_create_store(self) -> Tuple[faiss.Index, List[Dict[str, Any]]]:
        """
        Load existing vector store or create a new one.
        
        Returns:
            Tuple of (faiss_index, metadata_list)
        """
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                # Load the FAISS index
                index = faiss.read_index(self.index_path)
                
                # Load the metadata
                with open(self.metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                if DEBUG_MODE:
                    print(f"Loaded vector store with {index.ntotal} memories")
                
                return index, metadata
            except Exception as e:
                print(f"Error loading vector store: {e}")
                return self._create_store()
        else:
            return self._create_store()
    
    def _create_store(self) -> Tuple[faiss.Index, List[Dict[str, Any]]]:
        """
        Create a new vector store.
        
        Returns:
            Tuple of (faiss_index, metadata_list)
        """
        # Create directory if it doesn't exist
        os.makedirs(self.vector_db_path, exist_ok=True)
        
        # Create a new FAISS index
        index = faiss.IndexFlatL2(self.embedding_dim)
        
        # Create empty metadata list
        metadata = []
        
        # Save the empty store - passing explicit values to avoid using self attributes
        self._save_store(index=index, metadata=metadata)
        
        return index, metadata
    
    def _save_store(self, index: Optional[faiss.Index] = None, metadata: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Save the vector store to disk.
        
        Args:
            index: FAISS index to save (or use self.index)
            metadata: Metadata list to save (or use self.metadata)
        """
        # Use provided values if given, otherwise use instance attributes
        # But don't attempt to use self.index or self.metadata if they're None
        if index is None and hasattr(self, 'index') and self.index is not None:
            index = self.index
        
        if metadata is None and hasattr(self, 'metadata') and self.metadata is not None:
            metadata = self.metadata
            
        # Ensure we have valid values to save
        if index is None or metadata is None:
            raise ValueError("Cannot save store: missing index or metadata")
        
        # Create directory if it doesn't exist
        os.makedirs(self.vector_db_path, exist_ok=True)
        
        # Save the FAISS index
        faiss.write_index(index, self.index_path)
        
        # Save the metadata
        with open(self.metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def add_memory(self, text: str, embedding: np.ndarray, metadata: Dict[str, Any] = None) -> int:
        """
        Add a memory to the vector store.
        
        Args:
            text: Text content of the memory
            embedding: Vector embedding of the text
            metadata: Additional metadata for the memory
            
        Returns:
            ID of the added memory
        """
        if metadata is None:
            metadata = {}
        
        # Ensure embedding is the right shape and type
        embedding = np.array([embedding]).astype('float32')
        
        # Get the next ID
        memory_id = self.index.ntotal
        
        # Add the embedding to the index
        self.index.add(embedding)
        
        # Prepare the metadata entry
        memory_metadata = {
            "id": memory_id,
            "text": text,
            "timestamp": datetime.datetime.now().isoformat(),
            **metadata
        }
        
        # Add the metadata
        self.metadata.append(memory_metadata)
        
        # Save the updated store
        self._save_store()
        
        return memory_id
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar memories.
        
        Args:
            query_embedding: Vector embedding of the query
            k: Number of results to return
            
        Returns:
            List of memory metadata dictionaries
        """
        if self.index.ntotal == 0:
            return []
        
        # Ensure query embedding is the right shape and type
        query_embedding = np.array([query_embedding]).astype('float32')
        
        # Limit k to the number of items in the index
        k = min(k, self.index.ntotal)
        
        # Search the index
        distances, indices = self.index.search(query_embedding, k)
        
        # Get the metadata for the results
        results = []
        for i, idx in enumerate(indices[0]):
            if 0 <= idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result["distance"] = float(distances[0][i])
                results.append(result)
        
        return results
    
    def get_memory_by_id(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a memory by its ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Memory metadata dictionary, or None if not found
        """
        if 0 <= memory_id < len(self.metadata):
            return self.metadata[memory_id].copy()
        return None
    
    def get_all_memories(self) -> List[Dict[str, Any]]:
        """
        Get all memories in the store.
        
        Returns:
            List of all memory metadata dictionaries
        """
        return [m.copy() for m in self.metadata]
    
    def delete_memory(self, memory_id: int) -> bool:
        """
        Delete a memory from the store.
        Note: This is implemented by rebuilding the index without the deleted memory.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not (0 <= memory_id < len(self.metadata)):
            return False
        
        # FAISS doesn't support direct deletion, so we need to rebuild the index
        # Get all embeddings
        all_embeddings = []
        for i in range(self.index.ntotal):
            if i != memory_id:
                # Get the vector at index i
                vector = np.zeros((1, self.embedding_dim), dtype=np.float32)
                faiss.reconstruct(self.index, i, vector.reshape(-1))
                all_embeddings.append(vector)
        
        # Create new metadata list without the deleted memory
        new_metadata = []
        for i, meta in enumerate(self.metadata):
            if i != memory_id:
                # Update the ID to match the new index
                new_id = len(new_metadata)
                meta_copy = meta.copy()
                meta_copy["id"] = new_id
                new_metadata.append(meta_copy)
        
        # Create a new index
        new_index = faiss.IndexFlatL2(self.embedding_dim)
        
        # Add all embeddings to the new index
        if all_embeddings:
            all_embeddings_array = np.vstack(all_embeddings).astype('float32')
            new_index.add(all_embeddings_array)
        
        # Update the store
        self.index = new_index
        self.metadata = new_metadata
        
        # Save the updated store
        self._save_store()
        
        return True
    
    def clear_store(self) -> None:
        """
        Clear all memories from the store.
        """
        # Create a new index
        new_index = faiss.IndexFlatL2(self.embedding_dim)
        
        # Update the store
        self.index = new_index
        self.metadata = []
        
        # Save the updated store
        self._save_store()
    
    def count_memories(self) -> int:
        """
        Get the number of memories in the store.
        
        Returns:
            Number of memories
        """
        return self.index.ntotal 