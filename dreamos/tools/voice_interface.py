"""
Voice Interface tool for DreamOS
Provides speech recognition and text-to-speech capabilities
"""
import os
import threading
import queue
import time
from typing import Dict, Any, Optional, List, Callable
import speech_recognition as sr
import pyttsx3

from ..utils.logging_utils import get_logger

# Initialize logger
logger = get_logger("voice_interface")

class VoiceInterfaceTool:
    """Tool for voice interaction using speech recognition and text-to-speech."""
    
    def __init__(self):
        """Initialize the voice interface tool."""
        self.name = "voice_interface"
        self.description = "Provides speech recognition and text-to-speech capabilities"
        
        # Initialize text-to-speech engine
        logger.debug("Initializing text-to-speech engine")
        self.tts_engine = pyttsx3.init()
        
        # Set properties for the voice
        voices = self.tts_engine.getProperty('voices')
        # Try to find a female voice for better assistant sound
        female_voice = None
        for voice in voices:
            if "female" in voice.name.lower():
                female_voice = voice
                break
        
        # Set the voice
        if female_voice:
            logger.debug(f"Setting female voice: {female_voice.name}")
            self.tts_engine.setProperty('voice', female_voice.id)
        else:
            logger.debug("No female voice found, using default voice")
        
        # Set default properties
        self.tts_engine.setProperty('rate', 180)  # Speed of speech
        self.tts_engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
        
        # Initialize speech recognition
        logger.debug("Initializing speech recognition")
        self.recognizer = sr.Recognizer()
        
        # Adjustable recognition settings
        self.energy_threshold = 300  # Minimum audio energy to consider for recording
        self.pause_threshold = 0.8   # Seconds of non-speaking audio before a phrase is considered complete
        self.dynamic_energy_threshold = True  # Automatically adjust for ambient noise
        self.recognizer.energy_threshold = self.energy_threshold
        self.recognizer.pause_threshold = self.pause_threshold
        self.recognizer.dynamic_energy_threshold = self.dynamic_energy_threshold
        
        # Recognition state
        self.is_listening = False
        self.speech_queue = queue.Queue()
        self.listening_thread = None
        
        logger.info("Voice interface initialized")
    
    def speak(self, text: str, wait: bool = True) -> None:
        """
        Speak the given text using text-to-speech.
        
        Args:
            text: The text to speak
            wait: Whether to wait for speech to complete before returning
        """
        logger.info(f"Speaking: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        if wait:
            # Speak and wait until done
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        else:
            # Speak in a separate thread
            threading.Thread(target=self._speak_async, args=(text,), daemon=True).start()
    
    def _speak_async(self, text: str) -> None:
        """
        Speak text asynchronously.
        
        Args:
            text: Text to speak
        """
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self, timeout: int = 5) -> Optional[str]:
        """
        Listen for speech and convert to text.
        
        Args:
            timeout: Maximum time to listen for in seconds
            
        Returns:
            Recognized text or None if nothing was recognized
        """
        logger.info("Listening for speech...")
        
        with sr.Microphone() as source:
            # Adjust for ambient noise if using dynamic threshold
            if self.dynamic_energy_threshold:
                logger.debug("Adjusting for ambient noise")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            try:
                # Listen for audio
                logger.debug(f"Listening with timeout: {timeout}s")
                audio = self.recognizer.listen(source, timeout=timeout)
                
                # Recognize speech using Google Speech Recognition
                logger.debug("Recognizing speech")
                text = self.recognizer.recognize_google(audio)
                logger.info(f"Recognized: '{text}'")
                return text
            except sr.WaitTimeoutError:
                logger.warning("Listening timed out, no speech detected")
                return None
            except sr.UnknownValueError:
                logger.warning("Speech recognition could not understand audio")
                return None
            except sr.RequestError as e:
                logger.error(f"Could not request results from speech recognition service: {str(e)}")
                return None
            except Exception as e:
                logger.error(f"Error during speech recognition: {str(e)}", exc_info=True)
                return None
    
    def start_continuous_listening(self, callback: Callable[[str], None]) -> bool:
        """
        Start listening continuously in the background.
        
        Args:
            callback: Function to call with recognized text
            
        Returns:
            True if started successfully, False otherwise
        """
        if self.is_listening:
            logger.warning("Already listening continuously")
            return False
        
        logger.info("Starting continuous listening")
        self.is_listening = True
        self.listening_thread = threading.Thread(
            target=self._continuous_listening_thread,
            args=(callback,),
            daemon=True
        )
        self.listening_thread.start()
        return True
    
    def stop_continuous_listening(self) -> bool:
        """
        Stop continuous listening.
        
        Returns:
            True if stopped successfully, False if wasn't listening
        """
        if not self.is_listening:
            logger.warning("Not currently listening continuously")
            return False
        
        logger.info("Stopping continuous listening")
        self.is_listening = False
        if self.listening_thread:
            # Let the thread exit naturally
            self.listening_thread.join(timeout=2)
            self.listening_thread = None
        return True
    
    def _continuous_listening_thread(self, callback: Callable[[str], None]) -> None:
        """
        Background thread for continuous listening.
        
        Args:
            callback: Function to call with recognized text
        """
        logger.debug("Continuous listening thread started")
        
        # Start microphone stream
        mic = sr.Microphone()
        with mic as source:
            # Adjust for ambient noise
            logger.debug("Adjusting for ambient noise")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Set up callback for when speech is detected
            def on_speech(recognizer, audio):
                if not self.is_listening:
                    return
                
                try:
                    # Recognize speech using Google Speech Recognition
                    text = recognizer.recognize_google(audio)
                    logger.info(f"Continuously recognized: '{text}'")
                    
                    # Call the callback function with the recognized text
                    callback(text)
                except sr.UnknownValueError:
                    logger.debug("Continuous speech recognition could not understand audio")
                except sr.RequestError as e:
                    logger.error(f"Could not request results from speech recognition service: {str(e)}")
                except Exception as e:
                    logger.error(f"Error during continuous speech recognition: {str(e)}", exc_info=True)
            
            # Start listening in the background
            stop_listening = self.recognizer.listen_in_background(source, on_speech)
            
            # Keep the thread running until stop_continuous_listening is called
            while self.is_listening:
                time.sleep(0.1)
            
            # Stop the background listener
            stop_listening(wait_for_stop=False)
            logger.debug("Continuous listening stopped")
    
    def set_voice_properties(self, rate: Optional[int] = None, volume: Optional[float] = None) -> None:
        """
        Set voice properties.
        
        Args:
            rate: Speech rate (words per minute)
            volume: Volume (0.0 to 1.0)
        """
        if rate is not None:
            logger.debug(f"Setting speech rate to {rate}")
            self.tts_engine.setProperty('rate', rate)
        
        if volume is not None:
            logger.debug(f"Setting speech volume to {volume}")
            self.tts_engine.setProperty('volume', volume)
    
    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a voice interface command.
        
        Args:
            command: The command to execute (speak, listen, etc.)
            **kwargs: Additional arguments for the command
            
        Returns:
            Dictionary with execution results
        """
        logger.info(f"Executing voice interface command: {command}")
        
        try:
            if command == "speak":
                text = kwargs.get("text", "")
                wait = kwargs.get("wait", True)
                
                if not text:
                    return {
                        "status": "error",
                        "error": "No text provided for speech"
                    }
                
                self.speak(text, wait=wait)
                return {
                    "status": "success",
                    "result": f"Spoke: {text[:50]}{'...' if len(text) > 50 else ''}"
                }
            
            elif command == "listen":
                timeout = kwargs.get("timeout", 5)
                text = self.listen(timeout=timeout)
                
                if text:
                    return {
                        "status": "success",
                        "result": text
                    }
                else:
                    return {
                        "status": "error",
                        "error": "No speech detected or could not recognize speech"
                    }
            
            else:
                logger.warning(f"Unknown voice interface command: {command}")
                return {
                    "status": "error",
                    "error": f"Unknown command: {command}"
                }
        
        except Exception as e:
            logger.error(f"Error executing voice interface command: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": f"Error: {str(e)}"
            }
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the voice interface tool.
        
        Returns:
            Dictionary with tool information
        """
        return {
            "name": self.name,
            "description": self.description,
            "usage": "voice_interface.execute('speak', text='Hello, world!')",
            "examples": [
                "voice_interface.execute('speak', text='Hello, how can I help you?')",
                "voice_interface.execute('listen', timeout=10)",
            ],
            "commands": ["speak", "listen"]
        } 