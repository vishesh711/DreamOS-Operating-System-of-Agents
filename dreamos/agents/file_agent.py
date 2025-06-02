"""
File Agent for DreamOS - Manages the virtual file system
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import datetime

from ..config import PSEUDO_FILES_PATH, SYSTEM_PROMPTS, DEBUG_MODE
from ..utils.llm_utils import generate_agent_response
from ..utils.logging_utils import get_logger

# Initialize logger
logger = get_logger("file_agent")

class FileAgent:
    """
    Agent for managing virtual files in the DreamOS filesystem.
    Supports reading, writing, listing, and searching files.
    """
    
    def __init__(self, pseudo_files_path: Optional[str] = None):
        """
        Initialize the File Agent.
        
        Args:
            pseudo_files_path: Path to the JSON file storing the virtual filesystem
        """
        logger.info("Initializing File Agent")
        self.pseudo_files_path = pseudo_files_path or PSEUDO_FILES_PATH
        logger.debug(f"Using pseudo files path: {self.pseudo_files_path}")
        
        self.fs_data = self._load_fs()
        self.system_prompt = SYSTEM_PROMPTS["file_agent"]
        
        # Log filesystem stats
        file_count = len(self.fs_data.get("files", {}))
        logger.info(f"Loaded virtual filesystem with {file_count} files")
    
    def _load_fs(self) -> Dict:
        """Load the virtual filesystem data from JSON"""
        logger.debug(f"Loading filesystem from {self.pseudo_files_path}")
        if os.path.exists(self.pseudo_files_path):
            try:
                with open(self.pseudo_files_path, 'r') as f:
                    fs_data = json.load(f)
                    logger.debug(f"Successfully loaded filesystem with {len(fs_data.get('files', {}))} files")
                    return fs_data
            except json.JSONDecodeError as e:
                logger.error(f"Error loading filesystem from {self.pseudo_files_path}: {str(e)}")
                logger.info("Creating new filesystem")
                return self._create_default_fs()
        else:
            logger.info(f"Filesystem file not found at {self.pseudo_files_path}. Creating new one.")
            return self._create_default_fs()
    
    def _save_fs(self) -> None:
        """Save the virtual filesystem data to JSON"""
        # Ensure directory exists
        logger.debug(f"Saving filesystem to {self.pseudo_files_path}")
        os.makedirs(os.path.dirname(self.pseudo_files_path), exist_ok=True)
        
        try:
            with open(self.pseudo_files_path, 'w') as f:
                json.dump(self.fs_data, f, indent=2)
            logger.debug(f"Successfully saved filesystem with {len(self.fs_data.get('files', {}))} files")
        except Exception as e:
            logger.error(f"Error saving filesystem to {self.pseudo_files_path}: {str(e)}")
    
    def _create_default_fs(self) -> Dict:
        """Create a default filesystem structure"""
        logger.info("Creating default filesystem")
        timestamp = datetime.datetime.now().isoformat()
        
        fs_data = {
            "metadata": {
                "created_at": timestamp,
                "updated_at": timestamp
            },
            "files": {
                "/home/user/welcome.md": {
                    "content": "# Welcome to DreamOS\n\nThis is your virtual file system. You can create, read, and edit files using natural language commands.\n\nTry these commands:\n- list files\n- create a note about my project ideas\n- read welcome.md",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "mime_type": "text/markdown"
                },
                "/home/user/todo.txt": {
                    "content": "1. Try out DreamOS commands\n2. Create some notes\n3. Explore available tools",
                    "created_at": timestamp,
                    "updated_at": timestamp,
                    "mime_type": "text/plain"
                }
            }
        }
        
        logger.debug(f"Created default filesystem with {len(fs_data['files'])} files")
        return fs_data
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize a file path to use standard format with leading slash.
        
        Args:
            path: File path to normalize
            
        Returns:
            Normalized path string
        """
        # If path doesn't start with /, add /home/user/ prefix
        if not path.startswith('/'):
            path = f"/home/user/{path}"
        
        # Clean up any double slashes, etc.
        normalized_path = os.path.normpath(path)
        logger.debug(f"Normalized path '{path}' to '{normalized_path}'")
        return normalized_path
    
    def list_files(self, directory: Optional[str] = None) -> List[str]:
        """
        List all files in the specified directory.
        
        Args:
            directory: Directory path to list files from (defaults to root)
            
        Returns:
            List of file paths
        """
        if directory:
            directory = self._normalize_path(directory)
            logger.info(f"Listing files in directory: {directory}")
            # Filter files that are in the specified directory
            file_list = [
                path for path in self.fs_data["files"].keys() 
                if os.path.dirname(path) == directory
            ]
        else:
            logger.info("Listing all files")
            file_list = list(self.fs_data["files"].keys())
        
        logger.debug(f"Found {len(file_list)} files")
        return file_list
    
    def read_file(self, path: str) -> Optional[str]:
        """
        Read the contents of a file.
        
        Args:
            path: Path to the file to read
            
        Returns:
            File contents as string, or None if file doesn't exist
        """
        path = self._normalize_path(path)
        logger.info(f"Reading file: {path}")
        
        if path in self.fs_data["files"]:
            content = self.fs_data["files"][path]["content"]
            content_len = len(content)
            logger.debug(f"Successfully read file ({content_len} chars): {path}")
            return content
        else:
            logger.warning(f"File not found: {path}")
            return None
    
    def write_file(self, path: str, content: str, mime_type: Optional[str] = None) -> bool:
        """
        Write content to a file.
        
        Args:
            path: Path to the file to write
            content: Content to write to the file
            mime_type: MIME type of the file
            
        Returns:
            True if successful, False otherwise
        """
        path = self._normalize_path(path)
        timestamp = datetime.datetime.now().isoformat()
        content_len = len(content)
        logger.info(f"Writing to file: {path} ({content_len} chars)")
        
        # Determine MIME type based on file extension if not provided
        if not mime_type:
            ext = os.path.splitext(path)[1].lower()
            mime_map = {
                '.txt': 'text/plain',
                '.md': 'text/markdown',
                '.json': 'application/json',
                '.csv': 'text/csv',
                '.py': 'text/x-python',
                '.js': 'text/javascript',
                '.html': 'text/html',
                '.css': 'text/css',
            }
            mime_type = mime_map.get(ext, 'text/plain')
            logger.debug(f"Determined MIME type: {mime_type}")
        
        # Check if file exists
        if path in self.fs_data["files"]:
            logger.debug(f"Updating existing file: {path}")
            # Update existing file
            self.fs_data["files"][path].update({
                "content": content,
                "updated_at": timestamp,
                "mime_type": mime_type
            })
        else:
            logger.debug(f"Creating new file: {path}")
            # Create new file
            # Ensure directory exists in our virtual structure
            dir_path = os.path.dirname(path)
            
            # Create the file
            self.fs_data["files"][path] = {
                "content": content,
                "created_at": timestamp,
                "updated_at": timestamp,
                "mime_type": mime_type
            }
        
        # Update the filesystem metadata
        self.fs_data["metadata"]["updated_at"] = timestamp
        
        # Save changes
        self._save_fs()
        logger.info(f"Successfully wrote to file: {path}")
        return True
    
    def delete_file(self, path: str) -> bool:
        """
        Delete a file.
        
        Args:
            path: Path to the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        path = self._normalize_path(path)
        logger.info(f"Deleting file: {path}")
        
        if path in self.fs_data["files"]:
            del self.fs_data["files"][path]
            
            # Update the filesystem metadata
            self.fs_data["metadata"]["updated_at"] = datetime.datetime.now().isoformat()
            
            # Save changes
            self._save_fs()
            logger.info(f"Successfully deleted file: {path}")
            return True
        else:
            logger.warning(f"Cannot delete: File not found: {path}")
            return False
    
    def search_files(self, query: str) -> Dict[str, str]:
        """
        Search for files containing the query string.
        
        Args:
            query: Search query string
            
        Returns:
            Dictionary mapping file paths to matching content snippets
        """
        logger.info(f"Searching files for query: {query}")
        results = {}
        
        for path, file_data in self.fs_data["files"].items():
            content = file_data["content"]
            if query.lower() in content.lower():
                # Extract a snippet around the match
                index = content.lower().find(query.lower())
                start = max(0, index - 50)
                end = min(len(content), index + len(query) + 50)
                snippet = content[start:end]
                
                # Add ellipses if we truncated
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."
                
                results[path] = snippet
                logger.debug(f"Match found in file: {path}")
        
        logger.info(f"Search found {len(results)} matching files")
        return results
    
    def get_file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata about a file.
        
        Args:
            path: Path to the file
            
        Returns:
            Dictionary with file metadata, or None if file doesn't exist
        """
        path = self._normalize_path(path)
        logger.info(f"Getting file info: {path}")
        
        if path in self.fs_data["files"]:
            file_data = self.fs_data["files"][path].copy()
            file_data["size"] = len(file_data["content"])
            logger.debug(f"File info retrieved: {path}, size: {file_data['size']} chars")
            return file_data
        else:
            logger.warning(f"File not found: {path}")
            return None
    
    def process_command(self, command: str, context: Optional[str] = None) -> str:
        """
        Process a file-related command using the File Agent's LLM.
        
        Args:
            command: The file operation command
            context: Additional context for the command
            
        Returns:
            Response from the File Agent
        """
        logger.info(f"Processing command: {command}")
        
        # Prepare file system context
        file_list = "\n".join(self.list_files())
        fs_context = f"Current files in system:\n{file_list}"
        
        # Combine contexts
        full_context = fs_context
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