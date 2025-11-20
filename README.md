# Astrological Insight Generator

An **async-first** FastAPI service that generates personalized daily astrological insights using Cohere LLM, FAISS vector store, in-memory caching, and multilingual support.

## 🚀 Quick Start

Get started in 3 simple steps:

```bash
# 1. Run automated setup
./setup.sh

# 2. Add your Cohere API key to .env
nano .env

# 3. Start the server
./start_server.sh
```

Then visit http://127.0.0.1:8000/docs to see the interactive API documentation!

## Features

- **Async Architecture**: Fully async service for high performance and scalability
- **Automated Setup**: One-command installation and server startup scripts
- **Zodiac Inference**: Data-driven algorithm determines zodiac sign from birth date using tropical zodiac
- **LLM-Powered Insights**: Generates personalized insights using Cohere command-r model (async)
- **User Profile Personalization**: Tracks user history and preferences to influence insight generation
- **Vector Store (FAISS)**: Uses Cohere embeddings with FAISS for fast similarity search
- **In-Memory Caching**: Fast, simple dictionary-based caching with async interface
- **Multilingual Support**: Real translation using Cohere (supports 11+ languages)
- **Extensible Architecture**: Ready for Panchang integration (ascendant, moon sign, Nakshatra, etc.)
- **REST API**: Comprehensive async JSON API with automatic documentation (Swagger UI)
- **No External Dependencies**: No Redis or external services required

## Installation

### Quick Setup (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd astro
   ```

2. Run the automated setup script:
   ```bash
   ./setup.sh
   ```
   
   This will automatically:
   - Create and activate virtual environment
   - Install all dependencies
   - Create `.env` configuration file
   - Verify project structure

3. Update your Cohere API key:
   ```bash
   nano .env
   # Update COHERE_API_KEY with your key from https://dashboard.cohere.com/api-keys
   ```

### Manual Setup (Alternative)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd astro
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp example.env .env
   # Then edit .env and add your Cohere API key
   ```

5. Get your Cohere API key:
   - Sign up at https://cohere.com
   - Get your API key from the dashboard
   - Add it to your `.env` file

## Usage

### Quick Start

1. Start the server:
   ```bash
   ./start_server.sh
   ```
   
   Or with custom options:
   ```bash
   ./start_server.sh --host 0.0.0.0 --port 8080 --no-reload
   ```

2. Access the API documentation:
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc
   - Health Check: http://127.0.0.1:8000/health

3. Make a prediction request:
   ```bash
   curl -X POST "http://127.0.0.1:8000/predict?language=en" \
        -H "Content-Type: application/json" \
        -d '{
          "name": "Ritika",
          "birth_date": "1995-08-20",
          "birth_time": "14:30",
          "birth_place": "Jaipur, India"
        }'
   ```

### Manual Server Start

If you prefer to start the server manually:
```bash
source venv/bin/activate  # Activate virtual environment
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Setup Scripts

### `setup.sh` - Automated Environment Setup

Handles complete project setup in one command:
- Verifies Python 3 installation
- Creates virtual environment
- Installs all dependencies
- Creates `.env` configuration file
- Validates project structure

```bash
./setup.sh
```

### `start_server.sh` - Server Management

Starts the FastAPI server with pre-flight checks:
- Validates environment setup
- Checks Cohere API key configuration
- Activates virtual environment
- Displays all relevant URLs and endpoints
- Supports custom host, port, and reload options

```bash
# Basic usage
./start_server.sh

# Custom configuration
./start_server.sh --host 0.0.0.0 --port 8080 --no-reload
```

## API Endpoints

### POST /predict
Generate personalized astrological insight.

**Query Parameters:**
- `language` (optional): Language code - `en` (default) or `hi` , `te` , `ta`

**Request Body:**
```json
{
  "name": "string",
  "birth_date": "YYYY-MM-DD",
  "birth_time": "HH:MM",
  "birth_place": "string",
  "latitude": 0.0,  // optional, for Panchang calculations
  "longitude": 0.0, // optional, for Panchang calculations
  "user_id": "string" // optional, for personalization
}
```

**Response:**
```json
{
  "zodiac": "Leo",
  "insight": "Your innate leadership and warmth will shine today...",
  "language": "en",
  "cache_hit": false,
  "user_score": 1.0
}
```

### GET /health
Health check endpoint.

### GET /cache/stats
Get cache statistics (hits, misses, sizes).

### DELETE /cache
Clear all caches.

## Architecture

### Services (All Async)

- **`zodiac.py`**: Data-driven zodiac calculation with stubs for Panchang integration
- **`llm_service.py`**: Async Cohere integration for insight generation with fallback templates
- **`vector_store.py`**: Async FAISS + Cohere embeddings for similarity search (1024 dimensions)
- **`cache.py`**: Simple in-memory dictionary cache (daily insights + user profiles)
- **`translation.py`**: Real translation using Cohere (supports 11+ languages)
- **`insight.py`**: Async orchestration of all services

### Async Data Flow

1. Request received with birth details
2. Zodiac sign calculated from birth date using data-driven algorithm
3. **[Async]** User profile retrieved from in-memory cache (if user_id provided)
4. **[Async]** Cache checked for daily insight (per zodiac)
5. If cache miss:
   - **[Async]** Vector store searched using Cohere embeddings + FAISS (personalized based on user profile)
   - **[Async]** Cohere LLM generates personalized insight using:
     - User's name and zodiac
     - Context from vector store
     - User profile data (past insights, preferences, history)
   - **[Async]** Insight cached in memory
6. Translation applied via Cohere if language != "en"
7. **[Async]** User interaction recorded in cache for personalization (score updated, history tracked)

## Configuration

Environment variables (see `app/config.py`):

**Cohere:**
- `COHERE_API_KEY`: Your Cohere API key (required for LLM and embeddings)
- `COHERE_MODEL`: Model to use (default: `command-r`)
- `COHERE_TEMPERATURE`: Creativity level 0-1 (default: `0.7`)
- `COHERE_MAX_TOKENS`: Maximum tokens in response (default: `200`)
- `COHERE_EMBEDDING_MODEL`: Embedding model (default: `embed-english-v3.0`)

**Vector Store:**
- `VECTOR_STORE_ENABLED`: Enable/disable vector store (default: `true`)
- `TOP_K_RESULTS`: Number of similar insights to retrieve (default: `3`)

**Translation:**
- `TRANSLATION_ENABLED`: Enable/disable translation (default: `true`)

**Application:**
- `DEBUG`: Enable debug mode (default: `false`)

## Testing

**Note:** Activate the virtual environment first if not already active:
```bash
source venv/bin/activate
```

Run comprehensive integration tests:
```bash
python test_cohere_integration.py
```

Test zodiac algorithm:
```bash
python test_zodiac.py
```

Test API (when server is running):
```bash
python example_usage.py
```

Or use the existing test file:
```bash
python test_api.py
```

**Tip:** If you used `./start_server.sh`, it automatically activates the virtual environment.

## Extensibility

### Adding Panchang Integration

The `zodiac.py` service includes stubs for:
- `get_ascendant()`: Calculate ascendant (Lagna)
- `get_moon_sign()`: Calculate moon sign (Rashi)
- `get_panchang_data()`: Get comprehensive Panchang data

To integrate, replace stubs with libraries like:
- `swisseph` (Swiss Ephemeris)
- `jyotisha` (Python astrological library)
- `pyephem` (Astronomical calculations)

### Changing LLM Provider

The `llm_service.py` can be modified to support other providers:
- OpenAI (just swap Cohere client)
- Anthropic Claude
- HuggingFace models
- Local models via Ollama

Simply modify the client initialization and API calls.

### Vector Store Alternatives

Replace `vector_store.py` with:
- Pinecone (cloud vector database)
- Weaviate (self-hosted vector database)
- Chroma (lightweight vector store)
- Qdrant (high-performance vector search)

### Cache Persistence

The current in-memory cache can be upgraded to:
- Redis (distributed caching)
- Memcached (fast caching)
- SQLite (persistent local cache)
- PostgreSQL (full database)

## Project Structure

```
astro/
├── setup.sh                    # 🆕 Automated setup script
├── start_server.sh             # 🆕 Server startup script
├── SETUP_GUIDE.md              # 🆕 Comprehensive setup documentation
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── example.env                 # Example configuration
├── .env                        # Configuration (created by setup.sh)
│
├── app/
│   ├── main.py                # FastAPI application
│   ├── models.py              # Pydantic models
│   ├── config.py              # Configuration management
│   ├── services/
│   │   ├── zodiac.py          # Zodiac calculation + Panchang stubs
│   │   ├── insight.py         # Main orchestration service
│   │   ├── llm_service.py     # Cohere LLM integration
│   │   ├── vector_store.py    # FAISS vector similarity search
│   │   ├── cache.py           # In-memory caching system
│   │   └── translation.py     # Multilingual translation service
│   └── data/
│       └── astrological_corpus.json  # Astrological knowledge corpus
│
├── test_cohere_integration.py # Integration tests
├── test_zodiac.py             # Zodiac algorithm tests
├── test_api.py                # API endpoint tests
├── example_usage.py           # Usage examples
│
└── venv/                      # Virtual environment (created by setup.sh)
```

## Troubleshooting

### Common Issues

**"Permission denied" when running scripts:**
```bash
chmod +x setup.sh start_server.sh
```

**"Python 3 not found":**
Install Python 3.8 or higher from [python.org](https://python.org)

**"Virtual environment not found":**
```bash
./setup.sh
```

**"Cohere API key error":**
1. Get a new key from https://dashboard.cohere.com/api-keys
2. Update `.env` file
3. Restart the server

**"Port 8000 already in use":**
```bash
./start_server.sh --port 8080
```

For more detailed troubleshooting, see [SETUP_GUIDE.md](SETUP_GUIDE.md).

## Documentation

- **[README.md](README.md)** - Main project documentation (you are here)
- **API Docs** - Available at http://127.0.0.1:8000/docs when server is running

## License

See LICENSE file for details.
