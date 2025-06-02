"""
DreamOS - An Agentic AI Operating System
"""

from .agents import TerminalAgent, MemoryAgent, FileAgent, PluginAgent
import dreamos.tools
import dreamos.utils
import dreamos.memory

__version__ = "0.1.0"

__all__ = [
    "TerminalAgent",
    "MemoryAgent", 
    "FileAgent",
    "PluginAgent",
    "tools",
    "utils",
    "memory"
] 