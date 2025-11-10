#!/bin/bash

# Setup Environment Script
# Initializes the complete development environment
# Usage: ./scripts/setup_environment.sh

set -e  # Exit on error

echo "================================"
echo "Job Application Agent - Setup"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_step() {
    echo -e "${BLUE}→ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check Python installation
print_step "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION found"

# Check if Python version >= 3.8
REQUIRED_PYTHON="3.8"
if ! python3 -c "import sys; exit(0 if sys.version_info >= tuple(map(int, '$REQUIRED_PYTHON'.split('.'))) else 1)"; then
    print_error "Python $REQUIRED_PYTHON or higher is required"
    exit 1
fi

# Create virtual environment
print_step "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_step "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip, setuptools, wheel
print_step "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
print_success "Package managers upgraded"

# Install requirements
print_step "Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_warning "requirements.txt not found"
fi

# Install development dependencies
print_step "Installing development dependencies..."
pip install pytest pytest-cov black flake8 mypy isort bandit safety > /dev/null 2>&1
print_success "Development dependencies installed"

# Create necessary directories
print_step "Creating necessary directories..."
mkdir -p logs
mkdir -p data
mkdir -p models
mkdir -p output
mkdir -p cache
print_success "Directories created"

# Create .env file if it doesn't exist
print_step "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Environment Configuration
ENVIRONMENT=development
DEBUG=true
PYTHONUNBUFFERED=1

# Model Settings
VOCAB_SIZE=5000
MODEL_HIDDEN_DIM=256

# Device
USE_GPU=true

# Logging
LOG_LEVEL=INFO

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=7860
EOF
    print_success ".env file created"
else
    print_warning ".env file already exists"
fi

# Create config/secrets.yaml if it doesn't exist
print_step "Setting up secrets configuration..."
if [ ! -f "config/secrets.yaml" ]; then
    if [ -f "config/secrets.example.yaml" ]; then
        cp config/secrets.example.yaml config/secrets.yaml
        print_success "Created config/secrets.yaml from template"
        print_warning "Please edit config/secrets.yaml with your actual secrets"
    else
        print_warning "config/secrets.example.yaml not found"
    fi
else
    print_warning "config/secrets.yaml already exists"
fi

# Initialize git hooks (if git is available)
if command -v git &> /dev/null; then
    print_step "Setting up git hooks..."
    if [ -d ".git" ]; then
        # Create pre-commit hook
        mkdir -p .git/hooks
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "Running pre-commit checks..."
source venv/bin/activate 2>/dev/null || true
black --check src tests > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Code formatting issues found. Run: black src tests"
    exit 1
fi
flake8 src tests > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Linting issues found. Run: flake8 src tests"
    exit 1
fi
EOF
        chmod +x .git/hooks/pre-commit
        print_success "Git hooks installed"
    fi
fi

# Print summary
echo ""
echo "================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Edit your secrets:"
echo "   nano config/secrets.yaml"
echo ""
echo "3. Run the application:"
echo "   python app.py"
echo ""
echo "4. Run tests:"
echo "   pytest tests/ -v"
echo ""
print_success "Environment is ready for development!"
