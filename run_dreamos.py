#!/usr/bin/env python3
"""
DreamOS Runner Script
"""
import os
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"Loaded environment variables from {dotenv_path}")
else:
    print("Warning: .env file not found. Using default or environment variables.")

def main():
    """Main entry point for running DreamOS."""
    parser = argparse.ArgumentParser(description="DreamOS - An Agentic AI Operating System")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--web", action="store_true", help="Run in web interface mode (not implemented yet)")
    parser.add_argument("--voice", action="store_true", help="Enable voice interface")
    parser.add_argument("--dataviz", action="store_true", help="Enable data visualization features")
    parser.add_argument("--dbquery", action="store_true", help="Enable database querying features")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], 
                        help="Set the console logging level")
    parser.add_argument("--disable-file-logging", action="store_true", 
                        help="Disable logging to files")
    args = parser.parse_args()
    
    # Add the current directory to the Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Set environment variables for logging if provided
    if args.log_level:
        os.environ["CONSOLE_LOG_LEVEL"] = args.log_level
    
    if args.disable_file_logging:
        os.environ["ENABLE_FILE_LOGGING"] = "false"
    
    if args.debug:
        os.environ["DEBUG_MODE"] = "true"
    
    if args.dataviz:
        os.environ["ENABLE_DATAVIZ"] = "true"
    
    if args.dbquery:
        os.environ["ENABLE_DBQUERY"] = "true"
    
    # Import DreamOS main module
    from dreamos.main import main as dreamos_main
    
    # Run DreamOS
    dreamos_main()

if __name__ == "__main__":
    main() 