"""
Plugin Agent for DreamOS - Manages and executes tools
"""
from typing import Dict, List, Any, Optional, Union
import re
import json

from ..config import SYSTEM_PROMPTS, DEBUG_MODE
from ..utils.tool_loader import ToolLoader
from ..utils.llm_utils import generate_agent_response

class PluginAgent:
    """
    Agent for managing and executing tools/plugins.
    Loads appropriate tools based on user needs and executes them.
    """
    
    def __init__(self):
        """Initialize the Plugin Agent."""
        self.tool_loader = ToolLoader()
        self.system_prompt = SYSTEM_PROMPTS["plugin_agent"]
    
    def get_available_tools(self) -> List[str]:
        """
        Get a list of available tools.
        
        Returns:
            List of tool names
        """
        return self.tool_loader.get_available_tools()
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """
        Get information about a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary with tool information
        """
        return self.tool_loader.get_tool_info(tool_name)
    
    def execute_tool(self, tool_name: str, tool_input: str) -> Dict[str, Any]:
        """
        Execute a tool with the given input.
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input for the tool
            
        Returns:
            Tool execution result
        """
        if DEBUG_MODE:
            print(f"Executing tool: {tool_name} with input: {tool_input}")
        
        result = self.tool_loader.execute_tool(tool_name, tool_input)
        
        if DEBUG_MODE:
            print(f"Tool result: {result}")
        
        return result
    
    def parse_tool_command(self, command: str) -> Optional[Dict[str, str]]:
        """
        Parse a tool command from natural language.
        
        Args:
            command: Natural language command
            
        Returns:
            Dictionary with tool name and input, or None if parsing fails
        """
        # Try to extract tool name using regex patterns
        # First try direct tool name mention
        tool_patterns = [
            r"use (?:the )?([\w_]+)(?: tool)? (?:to|for|with) (.+)",
            r"(?:run|execute) (?:the )?([\w_]+)(?: tool)? (?:to|for|with) (.+)",
            r"(?:with|using) (?:the )?([\w_]+)(?: tool)?,? (.+)",
            r"([\w_]+) the following:? (.+)",
        ]
        
        for pattern in tool_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                tool_name = match.group(1).lower()
                tool_input = match.group(2).strip()
                
                if tool_name in self.get_available_tools():
                    return {
                        "tool_name": tool_name,
                        "tool_input": tool_input
                    }
        
        return None
    
    def process_command(self, command: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a plugin-related command.
        
        Args:
            command: The plugin operation command
            context: Additional context for the command
            
        Returns:
            Dictionary with command processing result
        """
        # First try direct parsing
        parsed_command = self.parse_tool_command(command)
        
        if parsed_command:
            # If we successfully parsed a tool command, execute it directly
            tool_name = parsed_command["tool_name"]
            tool_input = parsed_command["tool_input"]
            
            tool_result = self.execute_tool(tool_name, tool_input)
            
            return {
                "status": "success",
                "tool_used": tool_name,
                "input": tool_input,
                "result": tool_result,
                "response": self._format_tool_response(tool_name, tool_input, tool_result)
            }
        else:
            # Use LLM to determine the appropriate tool and input
            available_tools = self.get_available_tools()
            tools_context = "Available tools:\n" + "\n".join(
                [f"- {tool}: {self.get_tool_info(tool).get('description', 'No description')}" 
                 for tool in available_tools]
            )
            
            # Combine contexts
            full_context = tools_context
            if context:
                full_context = f"{full_context}\n\nAdditional context:\n{context}"
            
            # Generate response using LLM to determine tool and input
            llm_response = generate_agent_response(
                system_prompt=self.system_prompt,
                user_input=f"Determine which tool to use for this command: {command}",
                context=full_context
            )
            
            # Try to extract tool information from LLM response
            try:
                # Check if LLM response contains a structured tool usage
                tool_info_match = re.search(r"Tool: ([\w_]+)\nInput: (.+)", llm_response, re.DOTALL)
                
                if tool_info_match:
                    tool_name = tool_info_match.group(1).strip().lower()
                    tool_input = tool_info_match.group(2).strip()
                    
                    # Verify tool exists
                    if tool_name in available_tools:
                        # Execute the tool
                        tool_result = self.execute_tool(tool_name, tool_input)
                        
                        return {
                            "status": "success",
                            "tool_used": tool_name,
                            "input": tool_input,
                            "result": tool_result,
                            "response": self._format_tool_response(tool_name, tool_input, tool_result)
                        }
                    else:
                        return {
                            "status": "error",
                            "error": f"Tool '{tool_name}' not found",
                            "response": f"I couldn't find the tool '{tool_name}' to complete your request."
                        }
                else:
                    # Fallback to treating the LLM response as the final response
                    return {
                        "status": "no_tool_needed",
                        "response": llm_response
                    }
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "response": "I had trouble determining which tool to use for your request."
                }
    
    def _format_tool_response(self, tool_name: str, tool_input: str, tool_result: Dict[str, Any]) -> str:
        """
        Format a tool result into a natural language response.
        
        Args:
            tool_name: Name of the tool used
            tool_input: Input provided to the tool
            tool_result: Result from the tool execution
            
        Returns:
            Formatted response string
        """
        status = tool_result.get("status", "unknown")
        
        if status == "success":
            result = tool_result.get("result", "No result provided")
            
            if tool_name == "calculator":
                return f"The result of {tool_input} is {result}."
            elif tool_name == "web_browser":
                return f"I found this information from the web: {result}"
            else:
                # Generic success response
                return f"I used the {tool_name} tool with '{tool_input}' and got: {result}"
        else:
            error = tool_result.get("error", "Unknown error")
            return f"I tried to use the {tool_name} tool, but encountered an error: {error}" 