"""
Terminal Agent for DreamOS - Main interface for user commands
"""
from typing import Dict, List, Any, Optional, Tuple
import re
import json
import datetime
import threading
import os

from ..config import SYSTEM_PROMPTS, DEBUG_MODE
from ..utils.llm_utils import generate_agent_response
from ..utils.logging_utils import get_logger
from .file_agent import FileAgent
from .memory_agent import MemoryAgent
from .plugin_agent import PluginAgent
from ..tools.voice_interface import VoiceInterfaceTool
from ..tools.data_viz import DataVizTool
from ..tools.database_query import DatabaseQueryTool

# Initialize logger
logger = get_logger("terminal_agent")

class TerminalAgent:
    """
    Terminal Agent - Main interface for processing user commands.
    Routes commands to appropriate specialized agents.
    """
    
    def __init__(self, enable_voice: bool = False):
        """
        Initialize the Terminal Agent and its sub-agents.
        
        Args:
            enable_voice: Whether to enable voice interface
        """
        logger.info("Initializing Terminal Agent and sub-agents")
        
        # Initialize sub-agents
        logger.debug("Initializing File Agent")
        self.file_agent = FileAgent()
        
        logger.debug("Initializing Memory Agent")
        self.memory_agent = MemoryAgent()
        
        logger.debug("Initializing Plugin Agent")
        self.plugin_agent = PluginAgent()
        
        # Initialize voice interface if enabled
        self.voice_interface = None
        self.voice_enabled = enable_voice
        self.voice_listening = False
        self.voice_listening_thread = None
        
        if self.voice_enabled:
            try:
                logger.info("Initializing Voice Interface")
                self.voice_interface = VoiceInterfaceTool()
                logger.info("Voice Interface initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Voice Interface: {str(e)}", exc_info=True)
                self.voice_enabled = False
        
        # Initialize data visualization tool
        try:
            logger.debug("Initializing Data Visualization Tool")
            self.data_viz = DataVizTool()
            logger.debug("Data Visualization Tool initialized successfully")
            self.data_viz_enabled = True
        except Exception as e:
            logger.error(f"Failed to initialize Data Visualization Tool: {str(e)}", exc_info=True)
            self.data_viz_enabled = False
        
        # Initialize database query tool
        try:
            logger.debug("Initializing Database Query Tool")
            self.db_query = DatabaseQueryTool()
            logger.debug("Database Query Tool initialized successfully")
            self.db_query_enabled = True
        except Exception as e:
            logger.error(f"Failed to initialize Database Query Tool: {str(e)}", exc_info=True)
            self.db_query_enabled = False
        
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
        
        # Handle voice commands
        if command.startswith("voice ") and self.voice_enabled:
            return self._handle_voice_command(command[6:])
        
        # Handle data visualization commands
        if command.startswith("viz ") and self.data_viz_enabled:
            return self._handle_data_viz_command(command[4:])
        
        # Handle database query commands
        if command.startswith("db ") and self.db_query_enabled:
            return self._handle_db_query_command(command[3:])
        
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
        
        # Speak the response if voice is enabled
        if self.voice_enabled and self.voice_interface:
            try:
                # Speak a shortened version if too long
                speak_text = agent_response
                if len(speak_text) > 200:
                    speak_text = speak_text[:197] + "..."
                
                # Speak asynchronously to avoid blocking
                logger.debug("Speaking response via voice interface")
                threading.Thread(
                    target=self.voice_interface.speak,
                    args=(speak_text, True),
                    daemon=True
                ).start()
            except Exception as e:
                logger.error(f"Error speaking response: {str(e)}", exc_info=True)
        
        # Store the response in memory
        logger.debug("Storing response in memory")
        memory_id = self.memory_agent.add_memory(
            text=f"Response to '{command}':\n{agent_response}",
            metadata={"type": "response", "command": command, "timestamp": datetime.datetime.now().isoformat()}
        )
        logger.debug(f"Response stored in memory with ID: {memory_id}")
        
        return agent_response
    
    def _handle_voice_command(self, voice_cmd: str) -> str:
        """
        Handle voice interface commands.
        
        Args:
            voice_cmd: The voice command (without the 'voice ' prefix)
            
        Returns:
            Response message
        """
        logger.info(f"Handling voice command: '{voice_cmd}'")
        
        if not self.voice_enabled or not self.voice_interface:
            return "Voice interface is not enabled or failed to initialize."
        
        try:
            if voice_cmd.startswith("speak "):
                # Handle speak command
                text = voice_cmd[6:]
                logger.debug(f"Speaking text: '{text}'")
                self.voice_interface.speak(text)
                return f"Speaking: '{text}'"
            
            elif voice_cmd == "listen":
                # Handle listen command (one-time)
                logger.debug("Listening for voice input")
                text = self.voice_interface.listen(timeout=5)
                
                if text:
                    logger.info(f"Recognized: '{text}'")
                    # Process the recognized text as a command
                    response = self.process_command(text)
                    return f"Voice input: '{text}'\nResponse: {response}"
                else:
                    return "No speech detected or could not recognize speech."
            
            elif voice_cmd == "start":
                # Start continuous listening
                if self.voice_listening:
                    return "Voice interface is already listening."
                
                logger.info("Starting continuous voice listening")
                self.voice_listening = True
                
                def voice_callback(text):
                    logger.info(f"Voice command recognized: '{text}'")
                    # Process the recognized text as a command
                    self.process_command(text)
                
                # Start listening in a background thread
                self.voice_listening_thread = threading.Thread(
                    target=self._continuous_listening_thread,
                    args=(voice_callback,),
                    daemon=True
                )
                self.voice_listening_thread.start()
                
                return "Voice interface is now listening continuously. Say 'voice stop' to stop."
            
            elif voice_cmd == "stop":
                # Stop continuous listening
                if not self.voice_listening:
                    return "Voice interface is not currently listening."
                
                logger.info("Stopping continuous voice listening")
                self.voice_listening = False
                
                if self.voice_interface:
                    self.voice_interface.stop_continuous_listening()
                
                if self.voice_listening_thread:
                    self.voice_listening_thread.join(timeout=2)
                    self.voice_listening_thread = None
                
                return "Voice interface has stopped listening."
            
            elif voice_cmd == "status":
                # Check voice interface status
                status = "enabled" if self.voice_enabled else "disabled"
                listening = "listening" if self.voice_listening else "not listening"
                
                return f"Voice interface is {status} and currently {listening}."
            
            else:
                return f"Unknown voice command: '{voice_cmd}'. Available commands: speak, listen, start, stop, status."
        
        except Exception as e:
            logger.error(f"Error handling voice command: {str(e)}", exc_info=True)
            return f"Error handling voice command: {str(e)}"
    
    def _continuous_listening_thread(self, callback):
        """
        Background thread for continuous listening.
        
        Args:
            callback: Function to call with recognized text
        """
        logger.debug("Starting continuous listening thread")
        
        if self.voice_interface:
            self.voice_interface.start_continuous_listening(callback)
            
            # Keep the thread alive until voice_listening is set to False
            while self.voice_listening:
                import time
                time.sleep(0.1)
            
            # Stop listening when done
            self.voice_interface.stop_continuous_listening()
        
        logger.debug("Continuous listening thread ended")
    
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
        
        # Voice interface status
        voice_status = ""
        if self.voice_enabled:
            voice_status = f"Voice interface is {'listening' if self.voice_listening else 'not listening'}."
        
        # Combine context
        context = f"Recent memories:\n{recent_memory_text}\n\nTools used in this session: {tools_used_text}"
        if voice_status:
            context += f"\n\n{voice_status}"
        
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
        Generate help text for the user.
        
        Returns:
            Help text
        """
        logger.debug("Generating help text")
        
        help_text = """
DreamOS Help
===========

Available Commands:
------------------
1. File Operations:
   - note [text] - Create a quick note
   - read [filename] - Read a file
   - write [filename] [content] - Write to a file
   - search [query] - Search through files
   - list files - List files in the current directory

2. Memory Operations:
   - remember [fact] - Store information in memory
   - recall [query] - Retrieve information from memory
   - forget [memory_id] - Remove a specific memory
   - memories - List recent memories

3. Tools & Plugins:
   - calculate [expression] - Perform calculations
   - web search [query] - Search the web
   - run [code] - Execute code

4. System Commands:
   - help - Show this help message
   - status - Display system status
   - clear - Clear the screen
   - exit - Exit DreamOS

5. Voice Interface:
   - voice speak [text] - Speak the provided text
   - voice listen - Listen for a voice command
   - voice start - Start continuous listening
   - voice stop - Stop continuous listening
   - voice status - Check voice interface status

6. Data Visualization:
   - viz create [type] [data] - Create a chart (bar, line, scatter, pie, histogram)
   - viz parse [text/file] - Parse data from text or file
   - viz help - Show detailed visualization help

7. Database Querying:
   - db load [file] - Load a CSV or JSON file as a dataset
   - db query [question] - Query a dataset using natural language
   - db list - List all loaded datasets
   - db describe [dataset] - Show dataset schema and details
   - db execute [sql] - Execute SQL directly on a dataset
   - db help - Show detailed database commands

You can ask natural language questions or give commands - DreamOS will try to understand
and route your request to the appropriate agent.
"""
        
        logger.debug("Help text generated")
        return help_text
    
    def _generate_status(self) -> str:
        """
        Generate a status message.
        
        Returns:
            Status text
        """
        logger.info("Generating status message")
        
        # Count memories
        memory_count = len(self.memory_agent.get_all_memories())
        
        # Count files
        files = self.file_agent.list_files()
        file_count = len(files)
        
        # Get tools used
        tools_used = set(self.session_tools_used)
        tools_used_text = ", ".join(tools_used) if tools_used else "None"
        
        # Voice status
        voice_status = "Disabled"
        if self.voice_enabled:
            voice_status = f"Enabled, {'Listening' if self.voice_listening else 'Not Listening'}"
        
        status_text = f"""
DreamOS Status:

Memory: {memory_count} memories stored
Files: {file_count} files in the virtual filesystem
Tools Used This Session: {tools_used_text}
Voice Interface: {voice_status}

System is running normally.
"""
        
        return status_text
    
    def _handle_data_viz_command(self, viz_cmd: str) -> str:
        """
        Handle data visualization commands.
        
        Args:
            viz_cmd: The visualization command (without the 'viz ' prefix)
            
        Returns:
            Response message
        """
        logger.info(f"Handling data visualization command: '{viz_cmd}'")
        
        if not self.data_viz_enabled:
            return "Data visualization is not enabled or failed to initialize."
        
        try:
            # Parse the command
            if viz_cmd.startswith("create "):
                # Format: viz create <chart_type> <data_json> [title] [xlabel] [ylabel] [filename]
                parts = viz_cmd[7:].split(" ", 2)  # Split into chart_type and the rest
                
                if len(parts) < 2:
                    return "Invalid create command. Format: viz create <chart_type> <data_json> [title] [xlabel] [ylabel] [filename]"
                
                chart_type = parts[0].lower()
                if chart_type not in ["bar", "line", "scatter", "pie", "histogram"]:
                    return f"Invalid chart type: {chart_type}. Available types: bar, line, scatter, pie, histogram"
                
                # Parse optional parameters
                data_str = parts[1]
                title = ""
                x_label = ""
                y_label = ""
                filename = ""
                
                # Check if data_str contains JSON
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    return f"Invalid JSON data: {data_str}"
                
                # Check if there are additional parameters
                if len(parts) > 2:
                    # Try to extract title, x_label, y_label, filename from the remaining text
                    param_text = parts[2]
                    param_parts = param_text.split(" --")
                    
                    for param in param_parts:
                        if param.startswith("title="):
                            title = param[6:].strip()
                        elif param.startswith("xlabel="):
                            x_label = param[7:].strip()
                        elif param.startswith("ylabel="):
                            y_label = param[7:].strip()
                        elif param.startswith("file="):
                            filename = param[5:].strip()
                
                # Create the chart
                result = self.data_viz.create_chart(
                    chart_type=chart_type,
                    data=data,
                    title=title,
                    x_label=x_label,
                    y_label=y_label,
                    save=True,
                    filename=filename
                )
                
                if result["status"] == "success":
                    return f"Chart created successfully: {result['filepath']}"
                else:
                    return f"Error creating chart: {result.get('error', 'Unknown error')}"
            
            elif viz_cmd.startswith("parse "):
                # Format: viz parse <text_or_file>
                text = viz_cmd[6:].strip()
                
                # Check if text is a file path
                if os.path.exists(text):
                    try:
                        with open(text, 'r') as f:
                            text = f.read()
                    except Exception as e:
                        return f"Error reading file: {str(e)}"
                
                # Parse the data
                result = self.data_viz.execute("parse_data", text=text)
                
                if result["status"] == "success":
                    data_format = result["format"]
                    data_str = json.dumps(result["data"], indent=2)
                    return f"Data parsed successfully as {data_format}:\n{data_str}"
                else:
                    return f"Error parsing data: {result.get('error', 'Unknown error')}"
            
            elif viz_cmd == "help":
                # Show help for data visualization commands
                return """
Data Visualization Commands:
---------------------------
viz create <chart_type> <data_json> [--title=...] [--xlabel=...] [--ylabel=...] [--file=...]
  - Creates a chart with the specified data
  - chart_type: bar, line, scatter, pie, histogram
  - data_json: JSON data for the chart
  - Optional parameters:
    - title: Chart title
    - xlabel: X-axis label
    - ylabel: Y-axis label
    - file: Output filename

viz parse <text_or_file>
  - Parses data from text or file content
  - Supports JSON, CSV, and space/tab-separated values

viz help
  - Shows this help message
"""
            else:
                return f"Unknown data visualization command: '{viz_cmd}'. Try 'viz help' for available commands."
        
        except Exception as e:
            logger.error(f"Error handling data visualization command: {str(e)}", exc_info=True)
            return f"Error handling data visualization command: {str(e)}"
    
    def _handle_db_query_command(self, db_cmd: str) -> str:
        """
        Handle database query commands.
        
        Args:
            db_cmd: The database query command (without the 'db ' prefix)
            
        Returns:
            Response message
        """
        logger.info(f"Handling database query command: '{db_cmd}'")
        
        if not self.db_query_enabled:
            return "Database query is not enabled or failed to initialize."
        
        try:
            # Parse the command
            if db_cmd.startswith("load "):
                # Format: db load <file_path> [dataset_name]
                parts = db_cmd[5:].split(" ", 1)
                
                if len(parts) < 1:
                    return "Invalid load command. Format: db load <file_path> [dataset_name]"
                
                file_path = parts[0].strip()
                dataset_name = parts[1].strip() if len(parts) > 1 else ""
                
                # Determine file type
                if file_path.lower().endswith(".csv"):
                    result = self.db_query.execute("load_csv", file_path=file_path, dataset_name=dataset_name)
                elif file_path.lower().endswith(".json"):
                    result = self.db_query.execute("load_json", file_path=file_path, dataset_name=dataset_name)
                else:
                    return f"Unsupported file type: {file_path}. Supported types: CSV, JSON"
                
                if result["status"] == "success":
                    return f"Loaded dataset '{result['dataset_name']}' with {result['row_count']} rows and {result['column_count']} columns."
                else:
                    return f"Error loading dataset: {result.get('error', 'Unknown error')}"
            
            elif db_cmd.startswith("query "):
                # Format: db query <natural_language_query> [dataset_name]
                parts = db_cmd[6:].split(" --dataset=", 1)
                
                query = parts[0].strip()
                dataset_name = parts[1].strip() if len(parts) > 1 else ""
                
                if not query:
                    return "Invalid query command. Format: db query <natural_language_query> [--dataset=dataset_name]"
                
                result = self.db_query.execute("query", query=query, dataset=dataset_name)
                
                if result["status"] == "success":
                    return f"Query: {result['query']}\nSQL: {result['sql_query']}\nResults ({result['result_count']} rows):\n{result['table_format']}"
                else:
                    return f"Error executing query: {result.get('error', 'Unknown error')}"
            
            elif db_cmd == "list" or db_cmd == "list datasets":
                result = self.db_query.execute("list_datasets")
                
                if result["status"] == "success":
                    if not result["datasets"]:
                        return "No datasets loaded. Use 'db load <file_path>' to load a dataset."
                    
                    datasets_info = []
                    for dataset in result["datasets"]:
                        datasets_info.append(f"- {dataset['name']}: {dataset['row_count']} rows, {dataset['column_count']} columns, type: {dataset['type']}")
                    
                    return f"Loaded Datasets ({result['datasets_count']}):\n" + "\n".join(datasets_info)
                else:
                    return f"Error listing datasets: {result.get('error', 'Unknown error')}"
            
            elif db_cmd.startswith("describe "):
                # Format: db describe <dataset_name>
                dataset_name = db_cmd[9:].strip()
                
                if not dataset_name:
                    return "Invalid describe command. Format: db describe <dataset_name>"
                
                result = self.db_query.execute("describe_dataset", dataset_name=dataset_name)
                
                if result["status"] == "success":
                    schema_info = []
                    for col in result["schema"]:
                        schema_info.append(f"- {col['name']} ({col['type']})")
                    
                    response = [
                        f"Dataset: {result['dataset_name']}",
                        f"Source: {result['source']}",
                        f"Type: {result['type']}",
                        f"Rows: {result['row_count']}, Columns: {result['column_count']}",
                        "",
                        "Schema:",
                        "\n".join(schema_info)
                    ]
                    
                    return "\n".join(response)
                else:
                    return f"Error describing dataset: {result.get('error', 'Unknown error')}"
            
            elif db_cmd.startswith("execute "):
                # Format: db execute <sql_query> --dataset=<dataset_name>
                parts = db_cmd[8:].split(" --dataset=", 1)
                
                if len(parts) < 2:
                    return "Invalid execute command. Format: db execute <sql_query> --dataset=<dataset_name>"
                
                sql = parts[0].strip()
                dataset_name = parts[1].strip()
                
                if not sql or not dataset_name:
                    return "Invalid execute command. Both SQL query and dataset name are required."
                
                # This is more complex since our API doesn't directly support executing SQL on datasets
                # We need to create a temporary connection first
                if dataset_name not in self.db_query.loaded_datasets:
                    return f"Dataset '{dataset_name}' not found. Use 'db list' to see available datasets."
                
                import sqlite3
                import pandas as pd
                
                dataset = self.db_query.loaded_datasets[dataset_name]
                df = dataset["dataframe"]
                
                # Create a temporary in-memory database
                conn = sqlite3.connect(":memory:")
                df.to_sql(dataset_name, conn, index=False, if_exists="replace")
                
                try:
                    # Execute the query
                    result_df = pd.read_sql_query(sql, conn)
                    
                    # Format the result
                    from tabulate import tabulate
                    table_format = tabulate(result_df, headers='keys', tablefmt='grid', showindex=False)
                    
                    return f"SQL: {sql}\nResults ({len(result_df)} rows):\n{table_format}"
                except Exception as e:
                    return f"Error executing SQL: {str(e)}"
                finally:
                    conn.close()
            
            elif db_cmd == "help":
                # Show help for database query commands
                return """
Database Query Commands:
----------------------
db load <file_path> [dataset_name]
  - Load a CSV or JSON file as a dataset
  - The dataset name is optional (defaults to filename without extension)

db query <natural_language_query> [--dataset=dataset_name]
  - Execute a natural language query on a dataset
  - The dataset name is optional if only one dataset is loaded

db list
  - List all loaded datasets

db describe <dataset_name>
  - Show detailed information about a dataset

db execute <sql_query> --dataset=<dataset_name>
  - Execute a SQL query directly on a dataset

db help
  - Show this help message
"""
            else:
                return f"Unknown database query command: '{db_cmd}'. Try 'db help' for available commands."
        
        except Exception as e:
            logger.error(f"Error handling database query command: {str(e)}", exc_info=True)
            return f"Error handling database query command: {str(e)}" 