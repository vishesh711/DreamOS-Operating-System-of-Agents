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

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/DreamOS-Operating-System-of-Agents.git
   cd DreamOS-Operating-System-of-Agents
   ```

2. Run the setup script to create a virtual environment and install dependencies:
   ```bash
   ./setup.sh
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Add your Groq API key to the `.env` file:
   ```bash
   echo "GROQ_API_KEY=your-key-here" >> .env
   ```

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

## 📝 Usage Examples

Here are some examples of how to interact with DreamOS:

### Basic Operations
```
> write "Meeting with Alex on Tuesday at 2pm" to notes.txt
> read notes.txt
> what time is my meeting with Alex?
```

### Voice Interface
```
> voice speak Hello, how can I help you today?
> voice listen
  [System listens for voice command]
> voice start
  [System begins continuous listening]
```

### Data Visualization
```
> viz create bar {"Categories": ["A", "B", "C"], "Values": [10, 20, 30]} --title=Sample Chart
> viz parse "A, 10; B, 20; C, 30"
```

### Database Querying
```
> db load data/employees.csv
> db query What is the average salary by department?
> db describe employees
```

### Web and Calculations
```
> search web for latest AI research papers
> calculate 25 * 4.5 + (10 / 2)
```

### Memory Operations
```
> remember John's birthday is on March 15th
> recall when is John's birthday?
```

## 🧩 Architecture

DreamOS follows a modular architecture with these key components:

1. **Agent System**: Specialized agents that handle different aspects of the system
2. **Tool Integration**: Pluggable tools that provide specific capabilities
3. **Memory Management**: Vector-based storage for long-term recall
4. **Command Router**: Intelligent routing of commands to appropriate handlers

## 🛠️ Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please follow the project's code style and include appropriate tests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔮 Future Roadmap

- **Image Generation**: Add text-to-image generation capabilities
- **Collaborative Workflows**: Support for multiple users working together
- **Advanced File System**: File versioning and collaborative editing
- **Additional Data Connectors**: Support for more database formats
- **Voice Customization**: Adjustable voice parameters and multilingual support

## 🙏 Acknowledgements

- [Groq](https://groq.com/) for the LLM API
- [FAISS](https://github.com/facebookresearch/faiss) for vector storage
- [SpeechRecognition](https://github.com/Uberi/speech_recognition) and [pyttsx3](https://github.com/nateshmbhat/pyttsx3) for voice interface
- [Matplotlib](https://matplotlib.org/) and [Pandas](https://pandas.pydata.org/) for data visualization
- [SQLAlchemy](https://www.sqlalchemy.org/) and [SQLite](https://www.sqlite.org/) for database functionality