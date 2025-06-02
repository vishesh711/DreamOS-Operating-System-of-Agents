"""
Utilities for interacting with Groq LLM API
"""
import os
import json
import time
from typing import List, Dict, Any, Optional
from groq import Groq

from ..config import GROQ_API_KEY, LLM_MODEL, DEBUG_MODE, CONSOLE_LOG_LEVEL, FILE_LOG_LEVEL, ENABLE_FILE_LOGGING
from .logging_utils import get_logger

# Initialize logger
logger = get_logger("llm")

# Initialize Groq client
if not GROQ_API_KEY:
    error_msg = "GROQ_API_KEY not found in environment variables. Please set it."
    logger.error(error_msg)
    raise ValueError(error_msg)

groq_client = Groq(api_key=GROQ_API_KEY)
logger.info(f"Initialized Groq client with model: {LLM_MODEL}")

def call_llm(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> str:
    """
    Call the Groq LLM API with the given messages.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        model: Optional model override
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        Generated text response
    """
    model_name = model or LLM_MODEL
    logger.debug(f"Calling LLM with model: {model_name}, temperature: {temperature}, max_tokens: {max_tokens}")
    
    # Log messages in a readable format
    for i, msg in enumerate(messages):
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        logger.debug(f"Message {i+1} ({role}): {content[:100]}{'...' if len(content) > 100 else ''}")
    
    # Only log full messages at trace level
    if logger.isEnabledFor(5):  # TRACE level (lower than DEBUG)
        logger.log(5, f"Full messages: {json.dumps(messages, indent=2)}")
    
    try:
        start_time = time.time()
        logger.info(f"Sending request to Groq API...")
        
        response = groq_client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        elapsed_time = time.time() - start_time
        response_text = response.choices[0].message.content
        
        logger.info(f"Received response from Groq API in {elapsed_time:.2f}s")
        logger.debug(f"Response: {response_text[:100]}{'...' if len(response_text) > 100 else ''}")
        
        # Log full response at trace level
        if logger.isEnabledFor(5):  # TRACE level
            logger.log(5, f"Full response: {response_text}")
        
        # Log usage information if available
        if hasattr(response, 'usage'):
            usage = response.usage
            logger.debug(f"Token usage - Prompt: {usage.prompt_tokens}, Completion: {usage.completion_tokens}, Total: {usage.total_tokens}")
        
        return response_text
    except Exception as e:
        logger.error(f"Error calling Groq API: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"

def generate_agent_response(
    system_prompt: str,
    user_input: str,
    context: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.2,
) -> str:
    """
    Generate a response from an agent using the LLM.
    
    Args:
        system_prompt: The system prompt for the agent
        user_input: The user's input
        context: Optional additional context
        model: Optional model override
        temperature: Sampling temperature
        
    Returns:
        Generated response from the agent
    """
    logger.info(f"Generating agent response for user input: {user_input[:50]}{'...' if len(user_input) > 50 else ''}")
    
    messages = [{"role": "system", "content": system_prompt}]
    
    if context:
        logger.debug(f"Adding context: {context[:50]}{'...' if len(context) > 50 else ''}")
        messages.append({"role": "system", "content": f"Additional context: {context}"})
    
    messages.append({"role": "user", "content": user_input})
    
    return call_llm(
        messages=messages,
        model=model,
        temperature=temperature,
    ) 