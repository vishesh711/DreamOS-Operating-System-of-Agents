#!/bin/bash
# DreamOS Setup Script

echo "📦 Setting up DreamOS - An Agentic AI Operating System"
echo "------------------------------------------------------"

# Check for Python
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo "❌ Python not found. Please install Python 3.8 or newer."
    exit 1
fi

# Check Python version
PY_VERSION=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Found Python $PY_VERSION"

# Create virtual environment (optional)
if [[ "$1" == "--venv" ]]; then
    echo "🔧 Creating virtual environment..."
    $PYTHON -m venv venv
    
    # Activate virtual environment
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    echo "✅ Virtual environment created and activated"
fi

# Install dependencies
echo "📥 Installing dependencies..."
$PYTHON -m pip install -r requirements.txt

# Set up environment
echo "🔧 Setting up environment..."

# Create .env.example file
echo "📝 Creating .env.example file..."
cat > .env.example << 'EOL'
# API Keys
GROQ_API_KEY=your_groq_api_key_here

# Configuration
VECTOR_DB_PATH=./dreamos/memory/vector_db
PSEUDO_FILES_PATH=./dreamos/memory/pseudo_files.json
LOG_DIR=./dreamos/logs

# LLM Configuration
LLM_MODEL=mixtral-8x7b-32768
# Alternative models: llama3-70b-8192, gemma-7b-it

# Runtime Settings
DEBUG_MODE=false
DEFAULT_MEMORY_K=5

# Logging Configuration
# Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
CONSOLE_LOG_LEVEL=INFO
FILE_LOG_LEVEL=DEBUG
ENABLE_FILE_LOGGING=true
EOL
echo "✅ Created .env.example file"

# Copy to .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "⚠️  Please edit .env file to add your Groq API key"
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p dreamos/logs
mkdir -p dreamos/memory/vector_db

echo "✅ Setup complete!"
echo ""
echo "🚀 To run DreamOS:"
echo "   $PYTHON run_dreamos.py"
echo ""
echo "📝 For more options:"
echo "   $PYTHON run_dreamos.py --help" 