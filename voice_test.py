#!/usr/bin/env python3
"""
Voice Interface Test Script for DreamOS
"""
import os
import sys
import time
import argparse
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from dreamos.tools.voice_interface import VoiceInterfaceTool
from dreamos.utils.logging_utils import setup_logger

# Setup logging
logger = setup_logger("voice_test")

def main():
    """Main entry point for voice interface testing."""
    parser = argparse.ArgumentParser(description="DreamOS Voice Interface Test")
    parser.add_argument("--speak", type=str, help="Text to speak")
    parser.add_argument("--listen", action="store_true", help="Listen for speech")
    parser.add_argument("--continuous", action="store_true", help="Continuous listening mode")
    parser.add_argument("--interactive", action="store_true", help="Interactive conversation mode")
    parser.add_argument("--timeout", type=int, default=5, help="Listening timeout in seconds")
    args = parser.parse_args()
    
    try:
        # Initialize the voice interface
        print("Initializing voice interface...")
        voice_tool = VoiceInterfaceTool()
        print("Voice interface initialized successfully!")
        
        if args.speak:
            # Speak the provided text
            print(f"Speaking: '{args.speak}'")
            voice_tool.speak(args.speak)
        
        elif args.listen:
            # Listen once for speech
            print(f"Listening for speech (timeout: {args.timeout}s)...")
            text = voice_tool.listen(timeout=args.timeout)
            
            if text:
                print(f"Recognized: '{text}'")
                print("Speaking response...")
                voice_tool.speak(f"I heard you say: {text}")
            else:
                print("No speech detected or could not recognize speech.")
                voice_tool.speak("I couldn't understand what you said.")
        
        elif args.continuous:
            # Start continuous listening
            print("Starting continuous listening mode. Press Ctrl+C to exit.")
            
            def speech_callback(text):
                print(f"Recognized: '{text}'")
                response = f"I heard you say: {text}"
                print(f"Response: '{response}'")
                voice_tool.speak(response, wait=True)
            
            voice_tool.start_continuous_listening(speech_callback)
            
            try:
                # Keep the main thread alive
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\nStopping continuous listening...")
                voice_tool.stop_continuous_listening()
                print("Continuous listening stopped.")
        
        elif args.interactive:
            # Interactive conversation mode
            print("Starting interactive conversation mode. Say 'exit' or press Ctrl+C to quit.")
            voice_tool.speak("Hello, I'm DreamOS voice assistant. How can I help you today?")
            
            try:
                while True:
                    print("\nListening...")
                    text = voice_tool.listen(timeout=args.timeout)
                    
                    if text:
                        print(f"You said: '{text}'")
                        
                        # Check for exit command
                        if text.lower() in ["exit", "quit", "bye", "goodbye"]:
                            voice_tool.speak("Goodbye! Have a nice day.")
                            break
                        
                        # Simple responses based on what was said
                        if "hello" in text.lower() or "hi" in text.lower():
                            response = "Hello there! How can I help you?"
                        elif "how are you" in text.lower():
                            response = "I'm doing well, thank you for asking! How about you?"
                        elif "thank" in text.lower():
                            response = "You're welcome! Is there anything else I can help with?"
                        elif "time" in text.lower():
                            current_time = time.strftime("%I:%M %p")
                            response = f"The current time is {current_time}."
                        elif "name" in text.lower():
                            response = "My name is DreamOS Voice Assistant. I'm here to help you!"
                        else:
                            response = f"I heard you say: {text}. How can I assist you with that?"
                        
                        print(f"Assistant: '{response}'")
                        voice_tool.speak(response)
                    else:
                        print("I didn't catch that. Could you please repeat?")
                        voice_tool.speak("I didn't catch that. Could you please repeat?")
            
            except KeyboardInterrupt:
                print("\nExiting interactive mode...")
                voice_tool.speak("Goodbye! Have a nice day.")
        
        else:
            # Default behavior: show help
            parser.print_help()
            print("\nExample usage:")
            print("  python voice_test.py --speak 'Hello, world!'")
            print("  python voice_test.py --listen")
            print("  python voice_test.py --continuous")
            print("  python voice_test.py --interactive")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        logger.error(f"Error in voice test: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 