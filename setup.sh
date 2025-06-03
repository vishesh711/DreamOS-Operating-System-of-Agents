#!/bin/bash
# Setup script for DreamOS

# Print colored messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BLUE='\033[0;34m'

print_header() {
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=========================================${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

# Check if Python 3.8+ is installed
print_header "Checking Python version"
if command -v python3 &>/dev/null; then
    python_version=$(python3 --version | cut -d' ' -f2)
    echo "Python version: $python_version"
    
    # Extract major and minor version
    major=$(echo $python_version | cut -d. -f1)
    minor=$(echo $python_version | cut -d. -f2)
    
    if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 8 ]); then
        print_error "Python 3.8 or higher is required. Please upgrade your Python installation."
        exit 1
    else
        print_success "Python version is compatible."
    fi
else
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create a virtual environment
print_header "Setting up virtual environment"
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Using existing environment."
else
    echo "Creating new virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment. Please make sure venv module is installed."
        exit 1
    fi
    print_success "Virtual environment created successfully."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment."
    exit 1
fi
print_success "Virtual environment activated."

# Install dependencies
print_header "Installing dependencies"
echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing required packages..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    print_error "Failed to install required packages."
    exit 1
fi

# Check for platform-specific dependencies for voice interface
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    print_header "Checking voice interface dependencies for macOS"
    if ! command -v brew &>/dev/null; then
        print_warning "Homebrew is not installed. Voice interface might not work properly."
        print_warning "Consider installing Homebrew and running: brew install portaudio"
    else
        echo "Checking for portaudio..."
        if brew list portaudio &>/dev/null; then
            print_success "portaudio is already installed."
        else
            echo "Installing portaudio using Homebrew..."
            brew install portaudio
            if [ $? -ne 0 ]; then
                print_warning "Failed to install portaudio. Voice interface might not work properly."
            else
                print_success "portaudio installed successfully."
            fi
        fi
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    print_header "Checking voice interface dependencies for Linux"
    echo "Checking for portaudio development libraries..."
    if ! dpkg -l | grep -q libportaudio2; then
        print_warning "portaudio development libraries not found. Voice interface might not work properly."
        print_warning "Consider installing them with: sudo apt-get install portaudio19-dev python3-pyaudio"
    else
        print_success "portaudio development libraries found."
    fi
fi

# Create .env.example file if it doesn't exist
print_header "Setting up configuration files"
if [ ! -f ".env.example" ]; then
    echo "Creating .env.example file..."
    cat > .env.example << EOF
# API Keys
GROQ_API_KEY=your_groq_api_key_here

# Paths
VECTOR_DB_PATH=dreamos/memory/vector_db
PSEUDO_FILES_PATH=dreamos/memory/pseudo_files.json
LOG_DIR=dreamos/logs

# LLM Configuration
LLM_MODEL=llama-3.1-70b-versatile

# Runtime Settings
DEBUG_MODE=false
CONSOLE_LOG_LEVEL=INFO
FILE_LOG_LEVEL=DEBUG
ENABLE_FILE_LOGGING=true
EOF
    print_success ".env.example file created."
else
    print_warning ".env.example file already exists. Skipping creation."
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    print_success ".env file created. Please edit it with your API keys and configuration."
else
    print_warning ".env file already exists. Skipping creation."
fi

# Create necessary directories
print_header "Creating necessary directories"
mkdir -p dreamos/logs
mkdir -p dreamos/memory
mkdir -p dreamos/memory/vector_db
mkdir -p dreamos/plugins
mkdir -p dreamos/memory/databases

# Make run_dreamos.py executable
print_header "Setting up executable"
chmod +x run_dreamos.py
print_success "Made run_dreamos.py executable."

# Make voice_test.py executable
chmod +x voice_test.py
print_success "Made voice_test.py executable."

# Make data_viz_test.py executable
chmod +x data_viz_test.py
print_success "Made data_viz_test.py executable."

# Make db_query_test.py executable
chmod +x db_query_test.py
print_success "Made db_query_test.py executable."

# Make run_web.py executable
echo -e "\n${YELLOW}Making run_web.py executable...${NC}"
chmod +x run_web.py
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to make run_web.py executable.${NC}"
    exit 1
fi
echo -e "${GREEN}run_web.py is now executable.${NC}"

# Finished
print_header "Setup Complete"
print_success "DreamOS has been set up successfully!"
echo ""
echo "To start DreamOS, run:"
echo "  source venv/bin/activate"
echo "  ./run_dreamos.py"
echo ""
echo "To use voice interface, run:"
echo "  ./run_dreamos.py --voice"
echo ""
echo "To use data visualization, run:"
echo "  ./run_dreamos.py --dataviz"
echo ""
echo "To test voice interface separately, run:"
echo "  ./voice_test.py --interactive"
echo ""
echo "To test data visualization separately, run:"
echo "  ./data_viz_test.py --sample"
echo ""
echo "To test database querying separately, run:"
echo "  ./db_query_test.py --sample"
echo ""
print_warning "Make sure to edit the .env file with your API keys before running DreamOS." 