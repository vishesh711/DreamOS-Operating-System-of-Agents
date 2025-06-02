# DreamOS: An Agentic AI Operating System

```
    _____                           ____   _____ 
   |  __ \                         / __ \ / ____|
   | |  | |_ __ ___  __ _ _ __ ___| |  | | (___  
   | |  | | '__/ _ \/ _` | '_ ` _ \ |  | |\___ \ 
   | |__| | | |  __/ (_| | | | | | | |__| |____) |
   |_____/|_|  \___|\__,_|_| |_| |_|\____/|_____/ 
                                                  
    An Agentic AI Operating System
    Type 'help' for available commands.
```

DreamOS is a visionary project that simulates an operating system using intelligent AI agents, shared memory, and powerful tools. It combines the philosophy of Unix, the autonomy of AutoGPT, and the structure of LangGraph—all accessible via natural language commands.

## 🌟 Key Features

- **Natural Language Interface**: Interact with the system using everyday language
- **Agent Orchestration**: Specialized agents work together to accomplish complex tasks
- **Memory and Context**: System remembers previous interactions and maintains context
- **Virtual File System**: Create, read, and manage virtual files using natural commands
- **Extensible Tools**: Use built-in tools like web search, calculator, and code runner
- **Detailed Logging**: Track every operation with comprehensive, color-coded logging

## 🤖 Core Agents

DreamOS is built around four specialized AI agents that work together seamlessly:

1. **Terminal Agent**: The primary interface that accepts natural language commands and routes them to appropriate agents
2. **Memory Agent**: Maintains a vector-based knowledge graph and enables context sharing between agents
3. **File Agent**: Simulates a filesystem and handles file read/write operations
4. **Plugin Agent**: Dynamically loads and manages tools like web browser, calculator, and code runner

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- [Groq API key](https://console.groq.com/keys) for LLM functionality

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/DreamOS-Operating-System-of-Agents.git
   cd DreamOS-Operating-System-of-Agents
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your Groq API key.

5. Run the setup script:
   ```bash
   bash setup.sh
   ```

### Running DreamOS

Start the system with:
```bash
python run_dreamos.py
```

## 💬 Usage Examples

```
> summarize my notes from yesterday
> search web for latest AI research papers and save to file
> create a table of upcoming deadlines
> calculate the compound interest on $1000 at 5% for 10 years
> run python code to analyze my data.csv file
> remind me to call mom tomorrow at 6pm
```

## ⚙️ Command Line Options

DreamOS supports various command line options for controlling its behavior:

```
python run_dreamos.py [OPTIONS]

Options:
  --debug                    Enable debug mode with more verbose output
  --log-level LEVEL          Set console logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  --disable-file-logging     Disable logging to files
  --web                      Run in web interface mode (not yet implemented)
```

## 📊 Logging System

DreamOS includes a comprehensive logging system that provides detailed information about what's happening at each step:

- **Color-Coded Console Output**: Easy-to-read, colored logs with configurable detail level
- **Automatic Log Rotation**: Only the latest log file for each component is kept to save disk space
- **Component-specific Logs**: Each agent and component has its own detailed log file
- **Configurable Log Levels**: Set different verbosity for console and file logging

You can configure logging behavior through command line options or by editing the `.env` file.

## 📁 Project Structure

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
│   ├── vector_store.py      # Vector storage (FAISS)
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

## 🔧 Configuration

DreamOS uses environment variables for configuration. You can set these in the `.env` file:

```
# API Keys
GROQ_API_KEY=your_groq_api_key_here

# Configuration
VECTOR_DB_PATH=./dreamos/memory/vector_db
PSEUDO_FILES_PATH=./dreamos/memory/pseudo_files.json
LOG_DIR=./dreamos/logs

# LLM Configuration
LLM_MODEL=llama-3.1-70b-versatile

# Logging Configuration
CONSOLE_LOG_LEVEL=INFO
FILE_LOG_LEVEL=DEBUG
ENABLE_FILE_LOGGING=true
```

## 🔄 Memory System

DreamOS uses a vector-based memory system for storing and retrieving information:

- **Vector Embeddings**: Uses FAISS for efficient similarity search
- **Persistent Storage**: Memory is saved between sessions
- **Semantic Search**: Find related information based on meaning, not just keywords
- **Context Management**: Automatically provides relevant context to agents

## 🛠️ Available Tools

DreamOS comes with several built-in tools:

1. **Web Browser Tool**: Search the web and extract information
2. **Calculator Tool**: Perform mathematical calculations
3. **Code Runner Tool**: Safely execute Python code snippets

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Groq](https://groq.com/) for their powerful LLM API
- [FAISS](https://github.com/facebookresearch/faiss) for efficient vector similarity search
- [Playwright](https://playwright.dev/) for web browsing capabilities