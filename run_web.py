#!/usr/bin/env python3
"""
DreamOS Web Interface Runner Script
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
    """Main entry point for running DreamOS Web Interface."""
    parser = argparse.ArgumentParser(description="DreamOS Web Interface")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    args = parser.parse_args()
    
    # Add the current directory to the Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Set environment variables for debug mode
    if args.debug:
        os.environ["DEBUG_MODE"] = "true"
        os.environ["FLASK_ENV"] = "development"
    
    # Import Flask app and socket.io
    from dreamos.web import app, socketio
    
    # Setup logging
    from dreamos.utils.logging_utils import setup_logger
    logger = setup_logger("web_runner")
    
    # Create necessary directories
    os.makedirs("dreamos/memory", exist_ok=True)
    os.makedirs("dreamos/plugins", exist_ok=True)
    os.makedirs("dreamos/memory/visualizations", exist_ok=True)
    os.makedirs("dreamos/memory/databases", exist_ok=True)
    os.makedirs("dreamos/logs", exist_ok=True)
    
    # Log startup information
    logger.info(f"Starting DreamOS Web Interface on {args.host}:{args.port}")
    logger.info(f"Debug mode: {args.debug}")
    
    # Print startup information
    print(f"Starting DreamOS Web Interface...")
    print(f"Visit http://{args.host}:{args.port} in your browser")
    
    # Run the app
    socketio.run(app, host=args.host, port=args.port, debug=args.debug, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    main() 