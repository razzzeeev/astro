#!/bin/bash

# ==============================================
# Astrological Insight Generator Server Starter
# ==============================================
# This script starts the FastAPI server

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

echo "🌟 Starting Astrological Insight Generator Server..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found!"
    echo "Please run setup.sh first:"
    echo "  ${GREEN}./setup.sh${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    echo "Please run setup.sh first:"
    echo "  ${GREEN}./setup.sh${NC}"
    exit 1
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"
echo ""

# Check if Cohere API key is configured
if grep -q "your_cohere_api_key_here" .env 2>/dev/null; then
    print_warning "Cohere API key not configured in .env!"
    print_warning "Please update your .env file with a valid API key."
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Display server info
echo "=========================================="
print_success "Server Configuration"
echo "=========================================="
echo "📍 Server URL: http://127.0.0.1:8000"
echo "📚 API Docs (Swagger): http://127.0.0.1:8000/docs"
echo "📖 API Docs (ReDoc): http://127.0.0.1:8000/redoc"
echo "🏥 Health Check: http://127.0.0.1:8000/health"
echo ""
echo "Press ${RED}Ctrl+C${NC} to stop the server"
echo "=========================================="
echo ""

# Start the server
print_info "Starting FastAPI server with uvicorn..."
echo ""

# Parse command line arguments
HOST="127.0.0.1"
PORT="8000"
RELOAD="--reload"

while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --no-reload)
            RELOAD=""
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Usage: $0 [--host HOST] [--port PORT] [--no-reload]"
            exit 1
            ;;
    esac
done

# Start uvicorn
uvicorn app.main:app --host "$HOST" --port "$PORT" $RELOAD

