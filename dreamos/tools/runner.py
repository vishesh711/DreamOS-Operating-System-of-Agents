"""
Code Runner tool for DreamOS
Executes Python code snippets in a controlled environment
"""
import os
import sys
import time
import re
import io
import ast
import traceback
from typing import Dict, Any, List, Set, Optional
import tempfile
import subprocess
import threading
from contextlib import redirect_stdout, redirect_stderr

from ..utils.logging_utils import get_logger

# Initialize logger
logger = get_logger("runner")

class CodeRunnerTool:
    """Tool for safely executing Python code snippets."""
    
    def __init__(self):
        """Initialize the code runner tool."""
        self.name = "runner"
        self.description = "Executes Python code snippets"
        
        # Default settings
        self.timeout = 10  # seconds
        self.max_output_length = 10000  # characters
        
        # Security settings
        self.allowed_imports = {
            "math", "datetime", "json", "re", "random", "statistics", 
            "collections", "itertools", "functools", "operator",
            "string", "time", "csv", "io", "os.path"
        }
        
        # Dangerous modules that should never be allowed
        self.forbidden_imports = {
            "os", "sys", "subprocess", "socket", "requests", 
            "http", "urllib", "ftplib", "telnetlib", 
            "smtplib", "poplib", "imaplib", "nntplib", 
            "pickle", "shelve", "marshal", "builtins",
            "_winreg", "winreg", "msvcrt", "pty", "popen2",
            "platform", "threading", "multiprocessing"
        }
    
    def _is_safe_code(self, code: str) -> bool:
        """
        Check if the code is safe to execute.
        
        Args:
            code: Python code to check
            
        Returns:
            True if the code is considered safe, False otherwise
        """
        logger.debug("Checking code safety")
        
        # Check for imports
        try:
            parsed = ast.parse(code)
            
            for node in ast.walk(parsed):
                # Check for import statements
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    for name in node.names:
                        module_name = name.name.split('.')[0]
                        
                        if module_name in self.forbidden_imports:
                            logger.warning(f"Forbidden import detected: {module_name}")
                            return False
                        
                        if module_name not in self.allowed_imports:
                            logger.warning(f"Unauthorized import detected: {module_name}")
                            return False
                
                # Check for exec or eval calls
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in ['exec', 'eval', '__import__']:
                        logger.warning(f"Dangerous function call detected: {node.func.id}")
                        return False
            
            return True
        except SyntaxError:
            logger.warning("Syntax error in code")
            return False
    
    def _run_code_in_subprocess(self, code: str) -> Dict[str, Any]:
        """
        Run code in a subprocess for better isolation.
        
        Args:
            code: Python code to run
            
        Returns:
            Dictionary with execution results
        """
        logger.debug("Running code in subprocess")
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as temp_file:
            temp_file_path = temp_file.name
            
            # Write the code to the file
            temp_file.write(code)
        
        try:
            # Run the code in a subprocess
            process = subprocess.Popen(
                [sys.executable, temp_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Set a timeout
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
                
                # Limit output length
                if len(stdout) > self.max_output_length:
                    stdout = stdout[:self.max_output_length] + "\n... [output truncated]"
                
                if len(stderr) > self.max_output_length:
                    stderr = stderr[:self.max_output_length] + "\n... [error output truncated]"
                
                result = {
                    "status": "success" if process.returncode == 0 else "error",
                    "stdout": stdout,
                    "stderr": stderr,
                    "returncode": process.returncode
                }
                
                logger.debug(f"Code execution complete. Return code: {process.returncode}")
                return result
            
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning(f"Code execution timed out after {self.timeout} seconds")
                return {
                    "status": "error",
                    "error": f"Execution timed out after {self.timeout} seconds"
                }
        
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def execute(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code.
        
        Args:
            code: Python code to execute
            
        Returns:
            Dictionary with execution results
        """
        logger.info("Executing Python code")
        logger.debug(f"Code length: {len(code)} characters")
        
        # First, check if the code is safe
        if not self._is_safe_code(code):
            logger.warning("Code safety check failed")
            return {
                "status": "error",
                "error": "The code contains imports or functions that are not allowed for security reasons."
            }
        
        try:
            # Run the code in a subprocess
            result = self._run_code_in_subprocess(code)
            
            # Format the result
            if result["status"] == "success":
                output = result["stdout"]
                if not output.strip():
                    output = "Code executed successfully (no output)"
                
                logger.info("Code executed successfully")
                return {
                    "status": "success",
                    "result": output
                }
            else:
                error_msg = result.get("stderr", "") or result.get("error", "Unknown error")
                logger.warning(f"Code execution failed: {error_msg}")
                return {
                    "status": "error",
                    "error": error_msg
                }
        
        except Exception as e:
            logger.error(f"Error executing code: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": f"Error executing code: {str(e)}"
            }
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the code runner tool.
        
        Returns:
            Dictionary with tool information
        """
        return {
            "name": self.name,
            "description": self.description,
            "usage": "runner.execute('print(\"Hello, world!\")')",
            "examples": [
                "runner.execute('print(2 + 2)')",
                "runner.execute('import math\\nprint(math.pi)')",
                "runner.execute('for i in range(5):\\n    print(i)')"
            ],
            "allowed_imports": sorted(list(self.allowed_imports))
        } 