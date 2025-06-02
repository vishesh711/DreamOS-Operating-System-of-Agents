"""
DreamOS - Main entry point
"""
import os
import sys
import readline
from typing import Optional
import argparse
import datetime
import logging

from .agents.terminal_agent import TerminalAgent
from .config import DEBUG_MODE, LOG_DIR, CONSOLE_LOG_LEVEL, FILE_LOG_LEVEL, ENABLE_FILE_LOGGING
from .utils.logging_utils import setup_logger, get_logger

# Initialize main logger
logger = get_logger("main")

def setup_environment():
    """Set up the environment for DreamOS."""
    logger.info("Setting up DreamOS environment")
    
    # Create necessary directories
    os.makedirs("dreamos/memory", exist_ok=True)
    logger.debug("Created memory directory")
    
    os.makedirs("dreamos/plugins", exist_ok=True)
    logger.debug("Created plugins directory")
    
    # Create empty plugin config if it doesn't exist
    plugin_config_path = os.path.join("dreamos", "plugins", "plugin_config.json")
    if not os.path.exists(plugin_config_path):
        logger.info(f"Creating default plugin config at {plugin_config_path}")
        with open(plugin_config_path, "w") as f:
            f.write('{"tool_class_mapping": {}}')
    
    # Create logs directory
    os.makedirs(LOG_DIR, exist_ok=True)
    logger.debug(f"Created logs directory at {LOG_DIR}")
    
    logger.info("Environment setup complete")

def print_banner():
    """Print the DreamOS banner."""
    banner = r"""
    _____                           ____   _____ 
   |  __ \                         / __ \ / ____|
   | |  | |_ __ ___  __ _ _ __ ___| |  | | (___  
   | |  | | '__/ _ \/ _` | '_ ` _ \ |  | |\___ \ 
   | |__| | | |  __/ (_| | | | | | | |__| |____) |
   |_____/|_|  \___|\__,_|_| |_| |_|\____/|_____/ 
                                                  
    An Agentic AI Operating System
    Type 'help' for available commands.
    """
    print(banner)
    logger.info("DreamOS banner displayed")

def run_cli(terminal_agent: TerminalAgent):
    """
    Run DreamOS in command-line interface mode.
    
    Args:
        terminal_agent: The initialized terminal agent
    """
    logger.info("Starting DreamOS CLI")
    print_banner()
    
    # Set up command history
    history_file = os.path.expanduser("~/.dreamos_history")
    logger.debug(f"Using command history file: {history_file}")
    
    try:
        readline.read_history_file(history_file)
        logger.debug("Read command history from file")
    except FileNotFoundError:
        logger.debug("Command history file not found, will create on exit")
    
    try:
        logger.info("Entering command loop")
        while True:
            try:
                command = input("\n> ")
                logger.debug(f"User entered command: {command}")
                
                if command.lower() in ["exit", "quit"]:
                    logger.info("Exit command received, terminating")
                    print("Goodbye! DreamOS session ended.")
                    break
                
                response = terminal_agent.process_command(command)
                logger.debug(f"Response received: {response[:50]}{'...' if len(response) > 50 else ''}")
                print(f"\n{response}")
            except KeyboardInterrupt:
                logger.warning("KeyboardInterrupt detected")
                print("\nUse 'exit' to quit DreamOS.")
            except Exception as e:
                logger.error(f"Error processing command: {str(e)}", exc_info=True)
                if DEBUG_MODE:
                    print(f"Error: {e}")
                else:
                    print("An error occurred while processing your command.")
    finally:
        logger.info("Writing command history to file")
        readline.write_history_file(history_file)
        logger.info("DreamOS CLI terminated")

def main():
    """Main entry point for DreamOS."""
    parser = argparse.ArgumentParser(description="DreamOS - An Agentic AI Operating System")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--web", action="store_true", help="Run in web interface mode (not implemented yet)")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
                        help="Set the console logging level")
    args = parser.parse_args()
    
    # Set debug mode from args
    global DEBUG_MODE
    if args.debug:
        DEBUG_MODE = True
        logger.setLevel(logging.DEBUG)
        logger.info("Debug mode enabled")
    
    # Set console log level from args if provided
    if args.log_level:
        log_level = getattr(logging, args.log_level)
        logger.info(f"Setting console log level to {args.log_level}")
        
        # Update console handler level for all loggers
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(log_level)
    
    # Log system information
    logger.info(f"DreamOS starting - Python {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Console logging level: {logging.getLevelName(CONSOLE_LOG_LEVEL)}")
    logger.info(f"File logging {'enabled' if ENABLE_FILE_LOGGING else 'disabled'}")
    if ENABLE_FILE_LOGGING:
        logger.info(f"File logging level: {logging.getLevelName(FILE_LOG_LEVEL)}")
        logger.info(f"Log directory: {LOG_DIR}")
    
    # Set up the environment
    setup_environment()
    
    # Initialize the terminal agent
    logger.info("Initializing Terminal Agent")
    terminal_agent = TerminalAgent()
    
    if args.web:
        logger.warning("Web interface not implemented yet, falling back to CLI mode")
        print("Web interface not implemented yet. Falling back to CLI mode.")
        run_cli(terminal_agent)
    else:
        run_cli(terminal_agent)
    
    logger.info("DreamOS shutdown complete")

if __name__ == "__main__":
    main() 