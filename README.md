# DreamOS: AI Operating System of Agents

DreamOS is a visionary project where AI agents simulate an operating system as a task-and-tool orchestration layer using intelligent agents, memory, and tools. It combines the philosophy of Unix, the autonomy of AutoGPT, and the structure of LangGraph—all accessible via natural language.

## Core Components and Agents

1. **Terminal Agent**: Accepts natural language commands and routes to the right agent
2. **Memory Agent**: Maintains a shared knowledge graph and enables context sharing
3. **File Agent**: Simulates a filesystem and handles read/write operations
4. **Plugin Agent**: Loads modular tools dynamically

## Usage Examples

```
> summarize my notes from yesterday
> search web for Elon Musk's last tweet and save it to file
> create a table of upcoming deadlines and share it via email
```

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables: `cp .env.example .env` and add your Groq API key
3. Run the system: `python run_dreamos.py`

## Command Line Options

DreamOS supports various command line options for controlling its behavior:

```
python run_dreamos.py [OPTIONS]

Options:
  --debug                    Enable debug mode with more verbose output
  --log-level LEVEL          Set console logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  --disable-file-logging     Disable logging to files
  --web                      Run in web interface mode (not yet implemented)
```

## Detailed Logging

DreamOS includes a comprehensive logging system that provides detailed information about what's happening at each step:

- **Console Logging**: Colored output with configurable detail level
- **File Logging**: Detailed logs stored in `dreamos/logs/` directory with timestamps
- **Component-specific Logs**: Each agent and component has its own log file

You can configure logging behavior through command line options or by editing the `.env` file.

## Project Structure

```
dreamos/
├── main.py                  # Entry point (CLI or web server)
├── agents/
│   ├── terminal_agent.py    # Command router and user interface
│   ├── memory_agent.py      # Knowledge storage and retrieval
│   ├── file_agent.py        # File system operations
│   └── plugin_agent.py      # Tool/plugin management
├── tools/
│   ├── web_browser.py       # Web search and scraping
│   ├── calculator.py        # Math evaluations
│   └── runner.py            # Code execution
├── memory/
│   ├── vector_store.py      # Vector storage (FAISS/ChromaDB)
│   └── pseudo_files.json    # Virtual file system
├── plugins/
│   └── plugin_config.json   # Plugin metadata
├── utils/
│   ├── tool_loader.py       # Dynamic tool loading
│   ├── logging_utils.py     # Logging utilities
│   └── llm_utils.py         # LLM interaction utilities
├── logs/                    # Log files directory
└── config.py                # System configuration
```

## Environment Variables

DreamOS uses environment variables for configuration. You can set these in the `.env` file:

```
# API Keys
GROQ_API_KEY=your_groq_api_key_here

# Configuration
VECTOR_DB_PATH=./dreamos/memory/vector_db
PSEUDO_FILES_PATH=./dreamos/memory/pseudo_files.json
LOG_DIR=./dreamos/logs

# LLM Configuration
LLM_MODEL=mixtral-8x7b-32768

# Logging Configuration
CONSOLE_LOG_LEVEL=INFO
FILE_LOG_LEVEL=DEBUG
ENABLE_FILE_LOGGING=true
```

## Features

- **Natural Language Interface**: Interact with the system using everyday language
- **Virtual File System**: Create, read, and manage files using natural commands
- **Memory and Context**: System remembers previous interactions and maintains context
- **Extensible Tools**: Use built-in tools or add your own
- **Detailed Logging**: Track every operation with comprehensive logging