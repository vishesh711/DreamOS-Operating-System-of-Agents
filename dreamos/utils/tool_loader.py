"""
Tool loader utility for DreamOS
"""
import os
import json
import importlib
from typing import Dict, List, Any, Optional, Type, Callable

from ..config import DEBUG_MODE

class ToolLoader:
    """Utility class for dynamically loading and managing tools."""
    
    def __init__(self, tools_dir: Optional[str] = None, plugins_config: Optional[str] = None):
        """
        Initialize the tool loader.
        
        Args:
            tools_dir: Directory containing tool modules
            plugins_config: Path to plugin configuration file
        """
        # Default paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.tools_dir = tools_dir or os.path.join(base_dir, "tools")
        self.plugins_config = plugins_config or os.path.join(base_dir, "plugins", "plugin_config.json")
        
        # Dictionary to store loaded tool instances
        self.loaded_tools: Dict[str, Any] = {}
        
        # Tool class name mapping (defaults)
        self.tool_class_mapping = {
            "calculator": "CalculatorTool",
            "web_browser": "WebBrowserTool",
            "runner": "CodeRunnerTool"
        }
        
        # Load plugin configuration if it exists
        self._load_plugin_config()
    
    def _load_plugin_config(self) -> None:
        """Load plugin configuration from JSON file if it exists."""
        if os.path.exists(self.plugins_config):
            try:
                with open(self.plugins_config, 'r') as f:
                    config = json.load(f)
                
                # Update tool class mapping from config
                if "tool_class_mapping" in config:
                    self.tool_class_mapping.update(config["tool_class_mapping"])
                
                if DEBUG_MODE:
                    print(f"Loaded plugin configuration from {self.plugins_config}")
            except Exception as e:
                print(f"Error loading plugin configuration: {e}")
    
    def get_available_tools(self) -> List[str]:
        """
        Get a list of available tools based on the tools directory.
        
        Returns:
            List of tool names
        """
        available_tools = []
        
        # Check python files in tools directory
        for filename in os.listdir(self.tools_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                tool_name = filename[:-3]  # Remove .py extension
                available_tools.append(tool_name)
        
        return available_tools
    
    def load_tool(self, tool_name: str) -> Optional[Any]:
        """
        Load a tool by name.
        
        Args:
            tool_name: Name of the tool to load
            
        Returns:
            Tool instance or None if not found
        """
        # Return already loaded tool if exists
        if tool_name in self.loaded_tools:
            return self.loaded_tools[tool_name]
        
        try:
            # Import the tool module
            module_path = f"..tools.{tool_name}"
            module = importlib.import_module(module_path, package=__package__)
            
            # Get the tool class name from mapping or use default
            class_name = self.tool_class_mapping.get(tool_name, f"{tool_name.capitalize()}Tool")
            
            # Get the tool class and instantiate it
            tool_class = getattr(module, class_name)
            tool_instance = tool_class()
            
            # Store the loaded tool
            self.loaded_tools[tool_name] = tool_instance
            
            if DEBUG_MODE:
                print(f"Loaded tool: {tool_name}")
            
            return tool_instance
        except Exception as e:
            print(f"Error loading tool '{tool_name}': {e}")
            return None
    
    def execute_tool(self, tool_name: str, *args, **kwargs) -> Any:
        """
        Execute a tool by name with the given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            *args: Positional arguments for the tool
            **kwargs: Keyword arguments for the tool
            
        Returns:
            Tool execution result or error message
        """
        # Load the tool if not already loaded
        tool = self.load_tool(tool_name)
        
        if tool is None:
            return {
                "status": "error",
                "error": f"Tool '{tool_name}' not found"
            }
        
        try:
            # Execute the tool
            if hasattr(tool, "execute"):
                return tool.execute(*args, **kwargs)
            else:
                return {
                    "status": "error",
                    "error": f"Tool '{tool_name}' does not have an execute method"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """
        Get information about a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary with tool information
        """
        tool = self.load_tool(tool_name)
        
        if tool is None:
            return {
                "name": tool_name,
                "status": "not_found"
            }
        
        if hasattr(tool, "get_info"):
            return tool.get_info()
        else:
            return {
                "name": tool_name,
                "description": getattr(tool, "description", "No description available"),
                "status": "loaded"
            } 