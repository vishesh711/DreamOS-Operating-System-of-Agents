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

DreamOS is a visionary project that simulates an operating system using intelligent AI agents, shared memory, and powerful tools. It combines the philosophy of Unix, the autonomy of AutoGPT, and the structure of LangGraph—all accessible via natural language commands and voice interaction.

## 🌟 Key Features

- **Natural Language Interface**: Communicate with DreamOS using everyday language
- **Voice Commands**: Interact with DreamOS through speech recognition and text-to-speech
- **Data Visualization**: Create charts and visualize data with simple commands
- **Natural Language Database Querying**: Query structured data using plain English
- **Multiple Specialized Agents**: Terminal, Memory, File, and Plugin agents working together
- **Vector Memory System**: Long-term recall of conversations and contexts
- **Extensible Tools**: Calculator, web search, code execution and more
- **Detailed Logging**: Comprehensive logging system with rotating log files

## 🤖 Core Agents

DreamOS is built around four specialized AI agents that work together seamlessly:

1. **Terminal Agent**: The primary interface that accepts natural language commands and routes them to appropriate agents
2. **Memory Agent**: Maintains a vector-based knowledge graph and enables context sharing between agents
3. **File Agent**: Simulates a filesystem and handles file read/write operations
4. **Plugin Agent**: Dynamically loads and manages tools like web browser, calculator, and code runner

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Groq API key (sign up at [groq.com](https://console.groq.com/))
- For voice interface: Working microphone and speakers
- For macOS users: Homebrew (for installing portaudio)
- For Linux users: portaudio19-dev and python3-pyaudio packages

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/DreamOS-Operating-System-of-Agents.git
   cd DreamOS-Operating-System-of-Agents
   ```

2. Make the setup script executable:
   ```bash
   chmod +x setup.sh
   ```

3. Run the setup script to create a virtual environment and install dependencies:
   ```bash
   ./setup.sh
   ```
   
   The setup script will:
   - Check for Python compatibility
   - Create and activate a virtual environment
   - Install all required dependencies
   - Check for platform-specific dependencies (like portaudio for voice interface)
   - Create necessary directories
   - Make executable scripts runnable
   - Generate example configuration files

4. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. Add your Groq API key to the `.env` file:
   ```bash
   echo "GROQ_API_KEY=your-key-here" >> .env
   ```
   
   Alternatively, you can edit the `.env` file manually:
   ```bash
   nano .env
   # Edit the file to add: GROQ_API_KEY=your-key-here
   ```

### Troubleshooting Setup

If you encounter issues during setup:

- **Voice Interface Dependencies**: 
  - On macOS: `brew install portaudio`
  - On Ubuntu/Debian: `sudo apt-get install portaudio19-dev python3-pyaudio`
  
- **Scientific Computing Dependencies (scipy/numpy)**:
  - On macOS: 
    ```bash
    brew install openblas pkg-config
    export OPENBLAS="$(brew --prefix openblas)"
    export PKG_CONFIG_PATH="$OPENBLAS/lib/pkgconfig"
    pip install numpy scipy --no-binary scipy
    ```
  - On Ubuntu/Debian: `sudo apt-get install libopenblas-dev python3-scipy python3-numpy`
  
- **Permission Issues**:
  - If setup.sh is not executable: `chmod +x setup.sh`
  - If run_dreamos.py is not executable: `chmod +x run_dreamos.py`
  
- **Virtual Environment Issues**:
  - If venv module is missing: `pip install virtualenv`
  - Manual creation: `python3 -m virtualenv venv && source venv/bin/activate`

- **Alternative Installation Method**:
  If you encounter persistent issues with `setup.sh`, you can try installing dependencies manually:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  # Install core dependencies first
  pip install python-dotenv langchain pydantic
  # Install the remaining dependencies one by one
  pip install -r requirements.txt --no-deps
  ```
  
- **Installation Logs**:
  - Check logs in the `dreamos/logs` directory

### Running DreamOS

Start the system with:
```bash
./run_dreamos.py
```

For voice commands and text-to-speech, use:
```bash
./run_dreamos.py --voice
```

For data visualization features, use:
```bash
./run_dreamos.py --dataviz
```

For database querying features, use:
```bash
./run_dreamos.py --dbquery
```

Enable multiple features at once:
```bash
./run_dreamos.py --voice --dataviz --dbquery
```

### Web Interface

DreamOS now includes a modern web interface that provides access to all features in a user-friendly dashboard:

```bash
# Start the web interface
./run_web.py

# Start with specific host and port
./run_web.py --host 0.0.0.0 --port 8080

# Start in debug mode
./run_web.py --debug
```

Visit `http://localhost:5000` in your browser to access the web interface.

#### Web Interface Features

- **Modern UI**: Clean, responsive design that works on desktop and mobile
- **Terminal Emulation**: Familiar terminal experience with command history
- **Real-time Updates**: Instant command responses using WebSockets
- **Voice Recognition**: Browser-based speech recognition for voice commands
- **Visualization Display**: View charts and data visualizations directly in the browser
- **Dashboard**: View system status, memory usage, and command statistics
- **Settings Panel**: Configure DreamOS options through a graphical interface
- **Database Access**: Query and view database results in structured format

#### Web Pages

- **Terminal**: Main interface with command input and response display
- **Dashboard**: System monitoring with charts and status information
- **Settings**: Configure DreamOS behavior, voice settings, and API keys

#### Using the Web Interface

1. Start the web interface with `./run_web.py`
2. Open your browser to `http://localhost:5000`
3. Initialize the system by selecting the features you want to enable
4. Use the terminal interface to enter commands, just like the CLI version
5. Use the microphone button for voice input (if enabled)
6. Navigate between different sections using the sidebar
7. View real-time updates in the dashboard
8. Customize settings in the settings page

### Testing Individual Features

Test the voice interface separately:
```bash
./voice_test.py --interactive
```

Test the data visualization separately:
```bash
./data_viz_test.py --sample
```

Test the database querying separately:
```bash
./db_query_test.py --sample
```

Other command line options:
```bash
./run_dreamos.py --help  # Show all command line options
./run_dreamos.py --debug  # Run in debug mode
```

## 🎤 Voice Interface

DreamOS features a voice interface for hands-free interaction:

- **Speech Recognition**: Speak commands naturally and have them processed
- **Text-to-Speech**: Hear responses from DreamOS through your speakers
- **Continuous Listening**: Let DreamOS listen and respond to commands without manual activation
- **Voice Commands**: 
  - `voice speak [text]` - Make DreamOS speak the text
  - `voice listen` - Listen for a one-time voice command
  - `voice start` - Start continuous listening mode
  - `voice stop` - Stop continuous listening mode
  - `voice status` - Check voice interface status

## 📊 Data Visualization

DreamOS includes powerful data visualization capabilities:

- **Chart Creation**: Generate bar, line, scatter, pie, and histogram charts
- **Data Parsing**: Parse data from text, JSON, CSV, or structured files
- **Interactive Viewing**: View and save visualizations for later reference
- **Visualization Commands**:
  - `viz create [chart_type] [data_json]` - Create a visualization
  - `viz parse [text/file]` - Parse data for visualization
  - `viz help` - Show detailed visualization help
- **Standalone Testing**: Use `data_viz_test.py` to test visualization features

## 📝 Database Querying

DreamOS offers natural language database querying capabilities:

- **Data Loading**: Load structured data from CSV and JSON files
- **Natural Language Querying**: Ask questions about your data in plain English
- **SQL Generation**: Automatic conversion of natural language to SQL
- **Schema Exploration**: Examine your data structure and sample records
- **Database Commands**:
  - `db load [file]` - Load a CSV or JSON file as a dataset
  - `db query [question]` - Query a dataset using natural language
  - `db list` - List all loaded datasets
  - `db describe [dataset]` - Show dataset schema and details
  - `db execute [sql]` - Execute SQL directly on a dataset
  - `db help` - Show detailed database commands
- **Standalone Testing**: Use `db_query_test.py` to test database features

## 💾 Memory System

DreamOS uses a vector database to store and retrieve memories:

- **Long-term Storage**: Persistent retention of conversations and commands
- **Semantic Search**: Find relevant past interactions using natural language
- **Context Awareness**: Maintain coherent conversations over time
- **Memory Commands**:
  - `remember [fact]` - Store information in memory
  - `recall [query]` - Retrieve information from memory
  - `forget [memory_id]` - Remove a specific memory
  - `memories` - List recent memories

## 🔧 Available Tools

- **Calculator**: Perform mathematical calculations ranging from simple arithmetic to complex equations
- **Web Browser**: Search the web for information, summarize articles, and extract data
- **Code Runner**: Execute Python code safely in a controlled environment
- **Voice Interface**: Speech recognition and text-to-speech for hands-free interaction
- **Data Visualization**: Create charts and visualize data for better understanding
- **Database Querying**: Query structured data using natural language queries

## 🗃️ File System

DreamOS maintains a virtual file system for notes and documents:

- **File Operations**: Create, read, update, and delete files
- **Search Capability**: Search file contents using keywords or semantic search
- **Organization**: Structure information in a persistent, organized manner
- **File Commands**:
  - `note [text]` - Create a quick note
  - `read [filename]` - Read a file
  - `write [filename] [content]` - Write to a file
  - `search [query]` - Search through files
  - `list files` - List files in the current directory
