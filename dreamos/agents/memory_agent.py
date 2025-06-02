"""
Memory Agent for DreamOS - Manages the system's knowledge and context
"""
import os
import json
from typing import List, Dict, Any, Optional
import numpy as np
import datetime

from ..config import SYSTEM_PROMPTS, DEFAULT_MEMORY_K, DEBUG_MODE
from ..memory.vector_store import VectorStore
from ..utils.llm_utils import generate_agent_response
from ..utils.logging_utils import get_logger

# Initialize logger
logger = get_logger("memory_agent")

class MemoryAgent:
    """
    Agent for managing the system's knowledge and context.
    Stores and retrieves memories using a vector database.
    """
    
    def __init__(self):
        """Initialize the Memory Agent."""
        logger.info("Initializing Memory Agent")
        
        # Initialize vector store
        logger.debug("Initializing vector store")
        self.vector_store = VectorStore()
        self.system_prompt = SYSTEM_PROMPTS["memory_agent"]
        
        # For demonstration, we'll use random vectors as embeddings
        # In a production system, we would use a proper embedding model
        self._embedding_dim = 768
        
        # Log memory stats
        memory_count = self.vector_store.count_memories()
        logger.info(f"Memory Agent initialized with {memory_count} memories")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Get an embedding vector for the text.
        This is a placeholder - in production, use a real embedding model.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        logger.debug(f"Generating embedding for text: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        # This is a placeholder - normally you'd use a real embedding model
        # For demonstration, we'll use a deterministic random vector based on the text
        np.random.seed(hash(text) % 2**32)
        embedding = np.random.randn(self._embedding_dim).astype(np.float32)
        
        logger.debug(f"Embedding generated with shape: {embedding.shape}")
        return embedding
    
    def add_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Add a memory to the store.
        
        Args:
            text: Text content of the memory
            metadata: Additional metadata for the memory
            
        Returns:
            ID of the added memory
        """
        logger.info(f"Adding memory: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        if metadata is None:
            metadata = {}
        
        logger.debug(f"Memory metadata: {metadata}")
        
        # Generate embedding for the text
        embedding = self._get_embedding(text)
        
        # Add the memory to the vector store
        memory_id = self.vector_store.add_memory(text, embedding, metadata)
        
        logger.info(f"Memory added with ID: {memory_id}")
        return memory_id
    
    def search_memories(self, query: str, k: int = None) -> List[Dict[str, Any]]:
        """
        Search for memories similar to the query.
        
        Args:
            query: Search query
            k: Number of results to return (default: DEFAULT_MEMORY_K)
            
        Returns:
            List of memory dictionaries
        """
        logger.info(f"Searching memories with query: {query}")
        
        if k is None:
            k = DEFAULT_MEMORY_K
        
        logger.debug(f"Using k={k} for memory search")
        
        # Generate embedding for the query
        query_embedding = self._get_embedding(query)
        
        # Search the vector store
        results = self.vector_store.search(query_embedding, k)
        
        logger.info(f"Memory search returned {len(results)} results")
        
        # Log result details at debug level
        for i, result in enumerate(results):
            memory_id = result.get("id", "unknown")
            distance = result.get("distance", "unknown")
            text = result.get("text", "")
            logger.debug(f"Result {i+1}: ID={memory_id}, Distance={distance}, Text={text[:30]}...")
        
        return results
    
    def get_memory(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a memory by its ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Memory dictionary, or None if not found
        """
        logger.info(f"Getting memory with ID: {memory_id}")
        
        memory = self.vector_store.get_memory_by_id(memory_id)
        
        if memory:
            logger.debug(f"Memory found: {memory.get('text', '')[:50]}...")
            return memory
        else:
            logger.warning(f"Memory with ID {memory_id} not found")
            return None
    
    def delete_memory(self, memory_id: int) -> bool:
        """
        Delete a memory.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Deleting memory with ID: {memory_id}")
        
        success = self.vector_store.delete_memory(memory_id)
        
        if success:
            logger.info(f"Memory {memory_id} successfully deleted")
        else:
            logger.warning(f"Failed to delete memory {memory_id}")
        
        return success
    
    def get_all_memories(self) -> List[Dict[str, Any]]:
        """
        Get all memories.
        
        Returns:
            List of all memory dictionaries
        """
        logger.info("Getting all memories")
        
        memories = self.vector_store.get_all_memories()
        
        logger.debug(f"Retrieved {len(memories)} memories")
        return memories
    
    def clear_all_memories(self) -> None:
        """Clear all memories from the store."""
        logger.warning("Clearing all memories from store")
        
        self.vector_store.clear_store()
        
        logger.info("All memories cleared")
    
    def store_interaction(self, 
                          user_input: str, 
                          system_response: str, 
                          tools_used: Optional[List[str]] = None) -> int:
        """
        Store a user-system interaction as a memory.
        
        Args:
            user_input: User's input
            system_response: System's response
            tools_used: List of tools used in this interaction
            
        Returns:
            ID of the added memory
        """
        logger.info("Storing user-system interaction")
        logger.debug(f"User input: {user_input[:50]}...")
        logger.debug(f"System response: {system_response[:50]}...")
        
        if tools_used is None:
            tools_used = []
        
        if tools_used:
            logger.debug(f"Tools used: {', '.join(tools_used)}")
        
        # Format the memory text
        timestamp = datetime.datetime.now().isoformat()
        memory_text = f"User: {user_input}\nSystem: {system_response}"
        
        # Create metadata
        metadata = {
            "type": "interaction",
            "timestamp": timestamp,
            "tools_used": tools_used
        }
        
        # Store the memory
        memory_id = self.add_memory(memory_text, metadata)
        
        logger.info(f"Interaction stored with memory ID: {memory_id}")
        return memory_id
    
    def remember_fact(self, fact: str, source: Optional[str] = None) -> int:
        """
        Remember an important fact.
        
        Args:
            fact: The fact to remember
            source: Optional source of the fact
            
        Returns:
            ID of the added memory
        """
        logger.info(f"Remembering fact: {fact[:50]}{'...' if len(fact) > 50 else ''}")
        
        if source:
            logger.debug(f"Fact source: {source}")
        
        metadata = {
            "type": "fact",
            "timestamp": datetime.datetime.now().isoformat(),
            "source": source
        }
        
        memory_id = self.add_memory(fact, metadata)
        
        logger.info(f"Fact stored with memory ID: {memory_id}")
        return memory_id
    
    def get_recent_memories(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent memories.
        
        Args:
            limit: Maximum number of memories to return
            
        Returns:
            List of recent memory dictionaries
        """
        logger.info(f"Getting {limit} most recent memories")
        
        all_memories = self.get_all_memories()
        
        # Sort by timestamp (newest first)
        sorted_memories = sorted(
            all_memories, 
            key=lambda m: m.get("timestamp", ""), 
            reverse=True
        )
        
        recent_memories = sorted_memories[:limit]
        
        logger.debug(f"Retrieved {len(recent_memories)} recent memories")
        return recent_memories
    
    def process_command(self, command: str, context: Optional[str] = None) -> str:
        """
        Process a memory-related command using the Memory Agent's LLM.
        
        Args:
            command: The memory operation command
            context: Additional context for the command
            
        Returns:
            Response from the Memory Agent
        """
        logger.info(f"Processing command: {command}")
        
        # Get recent memories for context
        logger.debug("Getting recent memories for context")
        recent_memories = self.get_recent_memories(5)
        recent_memory_text = "\n".join([
            f"[{m.get('id')}] {m.get('text', '')[:100]}..." 
            for m in recent_memories
        ])
        
        memory_context = f"Recent memories:\n{recent_memory_text}\n\nTotal memories: {self.vector_store.count_memories()}"
        
        # Combine contexts
        full_context = memory_context
        if context:
            full_context = f"{full_context}\n\nAdditional context:\n{context}"
            logger.debug("Added additional context to command")
        
        # Generate response using LLM
        logger.debug("Sending command to LLM")
        response = generate_agent_response(
            system_prompt=self.system_prompt,
            user_input=command,
            context=full_context
        )
        
        logger.info(f"Command processed, response length: {len(response)} chars")
        return response 