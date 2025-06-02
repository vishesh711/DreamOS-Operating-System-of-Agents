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