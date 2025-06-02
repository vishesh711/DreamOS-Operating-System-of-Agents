"""
Terminal Agent for DreamOS - Main interface for user commands
"""
from typing import Dict, List, Any, Optional, Tuple
import re
import json
import datetime

from ..config import SYSTEM_PROMPTS, DEBUG_MODE
from ..utils.llm_utils import generate_agent_response
from ..utils.logging_utils import get_logger
from .file_agent import FileAgent
from .memory_agent import MemoryAgent
from .plugin_agent import PluginAgent

# Initialize logger
logger = get_logger("terminal_agent")

class TerminalAgent:
    """
    Terminal Agent - Main interface for processing user commands.
    Routes commands to appropriate specialized agents.
    """
    
    def __init__(self):
        """Initialize the Terminal Agent and its sub-agents."""
        logger.info("Initializing Terminal Agent and sub-agents")
        
        # Initialize sub-agents
        logger.debug("Initializing File Agent")
        self.file_agent = FileAgent()
        
        logger.debug("Initializing Memory Agent")
        self.memory_agent = MemoryAgent()
        
        logger.debug("Initializing Plugin Agent")
        self.plugin_agent = PluginAgent()
        
        self.system_prompt = SYSTEM_PROMPTS["terminal_agent"]
        
        # Record of tools used in the current session
        self.session_tools_used = []
        
        logger.info("Terminal Agent initialization complete")
    
    def process_command(self, command: str) -> str:
        """
        Process a user command.
        Determines which agent should handle the command and routes accordingly.
        
        Args:
            command: The user's command
            
        Returns:
            Response to the user
        """
        logger.info(f"Processing command: '{command}'")
        
        # Store the command in memory
        logger.debug("Storing command in memory")
        memory_id = self.memory_agent.add_memory(
            text=f"User command: {command}",
            metadata={"type": "command", "timestamp": datetime.datetime.now().isoformat()}
        )
        logger.debug(f"Command stored in memory with ID: {memory_id}")
        
        # Check for special commands
        if command.lower() in ["help", "?", "commands"]:
            logger.debug("Help command detected, generating help message")
            return self._generate_help()
        
        # Route the command to the appropriate agent
        logger.debug("Routing command to appropriate agent")
        agent_type, agent_response = self._route_command(command)
        logger.info(f"Command handled by {agent_type}")
        
        # Store the response in memory
        logger.debug("Storing response in memory")
        response_memory_id = self.memory_agent.add_memory(
            text=f"System response: {agent_response}",
            metadata={"type": "response", "agent": agent_type, "timestamp": datetime.datetime.now().isoformat()}
        )
        logger.debug(f"Response stored in memory with ID: {response_memory_id}")
        
        return agent_response
    
    def _route_command(self, command: str) -> Tuple[str, str]:
        """
        Route a command to the appropriate agent.
        
        Args:
            command: The user's command
            
        Returns:
            Tuple of (agent_type, agent_response)
        """
        logger.debug("Getting memory context for routing")
        # Get recent context from memory
        memory_context = self._get_memory_context()
        
        # First, we'll ask the LLM which agent should handle this
        logger.debug("Asking LLM to decide which agent should handle command")
        routing_prompt = f"""
        You are the Terminal Agent in DreamOS. Decide which agent should handle this command:
        
        Command: {command}
        
        Choose one:
        1. file_agent - For anything related to files, notes, reading, writing, or searching file content
        2. memory_agent - For remembering facts, storing information, or retrieving past context
        3. plugin_agent - For using specific tools like calculator, web search, or code execution
        4. terminal_agent (yourself) - For system-level commands, help, or commands that don't fit the other categories
        
        Respond with just the agent name (e.g., "file_agent") and nothing else.
        """
        
        agent_decision = generate_agent_response(
            system_prompt=routing_prompt,
            user_input=command,
            context=memory_context
        ).strip().lower()
        
        logger.debug(f"LLM agent decision: '{agent_decision}'")
        
        # Extract just the agent name if there's extra text
        if "file_agent" in agent_decision:
            agent_type = "file_agent"
        elif "memory_agent" in agent_decision:
            agent_type = "memory_agent"
        elif "plugin_agent" in agent_decision:
            agent_type = "plugin_agent"
        else:
            agent_type = "terminal_agent"
        
        logger.info(f"Selected agent for handling: {agent_type}")
        
        # Route to the appropriate agent
        if agent_type == "file_agent":
            logger.debug("Delegating to File Agent")
            agent_response = self.file_agent.process_command(command, context=memory_context)
        elif agent_type == "memory_agent":
            logger.debug("Delegating to Memory Agent")
            agent_response = self.memory_agent.process_command(command, context=memory_context)
        elif agent_type == "plugin_agent":
            logger.debug("Delegating to Plugin Agent")
            result = self.plugin_agent.process_command(command, context=memory_context)
            agent_response = result["response"]
            
            # Record tool usage
            if "tool_used" in result:
                tool_name = result["tool_used"]
                self.session_tools_used.append(tool_name)
                logger.info(f"Tool used: {tool_name}")
        else:
            # Handle with the terminal agent itself
            logger.debug("Handling with Terminal Agent")
            agent_response = self._handle_terminal_command(command, context=memory_context)
        
        logger.debug(f"Agent response length: {len(agent_response)} chars")
        return agent_type, agent_response
    
    def _get_memory_context(self) -> str:
        """
        Get recent context from memory.
        
        Returns:
            String with recent memory context
        """
        logger.debug("Retrieving recent memories for context")
        # Get recent memories
        recent_memories = self.memory_agent.get_recent_memories(5)
        recent_memory_text = "\n".join([
            f"[{m.get('id')}] {m.get('text', '')[:100]}..." 
            for m in recent_memories
        ])
        
        # Get tools used in this session
        tools_used = set(self.session_tools_used)
        tools_used_text = ", ".join(tools_used) if tools_used else "None"
        logger.debug(f"Tools used in current session: {tools_used_text}")
        
        # Combine context
        context = f"Recent memories:\n{recent_memory_text}\n\nTools used in this session: {tools_used_text}"
        logger.debug(f"Memory context created, length: {len(context)} chars")
        return context
    
    def _handle_terminal_command(self, command: str, context: Optional[str] = None) -> str:
        """
        Handle commands meant for the terminal agent itself.
        
        Args:
            command: The command to handle
            context: Additional context
            
        Returns:
            Response string
        """
        logger.debug(f"Handling terminal command: '{command}'")
        
        # Check for system commands
        if command.lower() in ["exit", "quit"]:
            logger.info("Exit command received")
            return "Goodbye! DreamOS session ended."
        elif command.lower() in ["clear", "cls"]:
            logger.info("Clear screen command received")
            return "[Screen cleared]"
        elif command.lower() in ["status", "system status"]:
            logger.info("Status command received")
            return self._generate_status()
        elif command.lower().startswith("help"):
            logger.info("Help command received")
            return self._generate_help()
        
        # Use the LLM for other terminal commands
        logger.debug("Using LLM to process terminal command")
        full_context = context or ""
        
        response = generate_agent_response(
            system_prompt=self.system_prompt,
            user_input=command,
            context=full_context
        )
        
        logger.debug(f"LLM response length: {len(response)} chars")
        return response
    
    def _generate_help(self) -> str:
        """
        Generate a help message.
        
        Returns:
            Help text
        """
        logger.info("Generating help message")
        help_text = """
DreamOS Command Help:

File Commands:
- list files
- read [filename]
- write [content] to [filename]
- search files for [query]
- delete [filename]

Memory Commands:
- remember [fact]
- what do you know about [topic]
- forget [memory ID]
- recall recent memories

Tool Commands:
- calculate [expression]
- search web for [query]
- run code [code snippet]

System Commands:
- help - Show this help message
- status - Show system status
- clear - Clear the screen
- exit - End the session

You can phrase commands naturally, like:
"Read my todo list"
"Write 'Buy milk' to shopping.txt"
"Calculate 25 * 4.5"
"What do you remember about my project?"
        """
        
        logger.debug("Help message generated")
        return help_text.strip()
    
    def _generate_status(self) -> str:
        """
        Generate a system status message.
        
        Returns:
            Status text
        """
        logger.info("Generating system status")
        
        # Get file stats
        file_count = len(self.file_agent.list_files())
        logger.debug(f"File count: {file_count}")
        
        # Get memory stats
        memory_count = self.memory_agent.vector_store.count_memories()
        logger.debug(f"Memory count: {memory_count}")
        
        # Get tool stats
        available_tools = self.plugin_agent.get_available_tools()
        tools_used_count = len(set(self.session_tools_used))
        logger.debug(f"Available tools: {len(available_tools)}, Used tools: {tools_used_count}")
        
        status_text = f"""
DreamOS Status:

Files: {file_count} files in virtual filesystem
Memories: {memory_count} memories stored
Tools: {len(available_tools)} available, {tools_used_count} used this session

System started: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """
        
        logger.debug("Status message generated")
        return status_text.strip() 