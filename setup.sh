#!/bin/bash

# ==============================================
# Astrological Insight Generator Setup Script
# ==============================================
# This script sets up the entire server environment
# and prepares it for running.

set -e  # Exit on any error

echo "🌟 Starting Astrological Insight Generator Setup..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if Python 3 is installed
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_success "Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment if it doesn't exist
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Skipping creation."
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
print_success "Pip upgraded"
echo ""

# Install requirements
echo "Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    print_success "All dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi
echo ""

# Setup environment file
if [ -f ".env" ]; then
    print_warning ".env file already exists. Skipping creation."
    print_warning "If you need to update it, check example.env for reference."
else
    if [ -f "example.env" ]; then
        echo "Setting up environment configuration..."
        cp example.env .env
        print_success ".env file created from example.env"
        print_warning "IMPORTANT: Please update .env with your Cohere API key!"
        print_warning "Get your key from: https://dashboard.cohere.com/api-keys"
    else
        print_error "example.env not found!"
        exit 1
    fi
fi
echo ""

# Verify critical files exist
echo "Verifying project structure..."
REQUIRED_FILES=("app/main.py" "app/models.py" "app/config.py" "app/data/astrological_corpus.json")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Found $file"
    else
        print_error "Missing required file: $file"
        exit 1
    fi
done
echo ""

# Display setup completion
echo "=========================================="
print_success "Setup completed successfully! 🎉"
echo "=========================================="
echo ""

# Display next steps
echo "📝 Next Steps:"
echo ""
echo "1. Update your .env file with your Cohere API key:"
echo "   ${YELLOW}nano .env${NC}"
echo ""
echo "2. Start the server:"
echo "   ${GREEN}./start_server.sh${NC}"
echo "   Or manually:"
echo "   ${GREEN}source venv/bin/activate${NC}"
echo "   ${GREEN}uvicorn app.main:app --reload${NC}"
echo ""
echo "3. Access the API documentation:"
echo "   ${GREEN}http://127.0.0.1:8000/docs${NC} (Swagger UI)"
echo "   ${GREEN}http://127.0.0.1:8000/redoc${NC} (ReDoc)"
echo ""
echo "4. Run tests:"
echo "   ${GREEN}python test_cohere_integration.py${NC}"
echo "   ${GREEN}python test_api.py${NC}"
echo ""

# Check if Cohere API key is set
if grep -q "your_cohere_api_key_here" .env 2>/dev/null || grep -q "i0OrIBaeHu9TcImEox1VJoP8S3Cchf5RPtOxSGcU" .env 2>/dev/null; then
    print_warning "Remember to update your Cohere API key in .env before starting!"
fi

echo "Happy coding! 🚀"

