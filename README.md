# Madeena Core - Ultra-Enterprise Middleware System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![Code style: strict](https://img.shields.io/badge/code%20style-strict-red.svg)](https://github.com/psf/black)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)

Mission-critical middleware system orchestrating asynchronous communication between Messaging Channels (WhatsApp/WeChat) and Task Management Systems (Trello), utilizing Chinese Large Language Models (DeepSeek) for cognitive processing.

## 🎯 Features

- **AI-Powered Task Parsing**: Utilizes DeepSeek LLM for intelligent message analysis
- **Multi-Platform Support**: WhatsApp, WeChat integration ready
- **Trello Integration**: Automated card creation with rich formatting
- **Enterprise Security**: OWASP Top 10 compliant with rate limiting and input validation
- **Circuit Breaker Pattern**: Resilient external API calls with automatic retries
- **Distributed Tracing**: Correlation IDs across all services
- **Strict Type Safety**: mypy strict mode compliance
- **Production Ready**: Docker, Gunicorn, health checks included

## 🏗️ Architecture

```
madeena_core/
├── app/
│   ├── main.py                  # FastAPI application entry
│   ├── core/                    # Core functionality
│   │   ├── config.py           # Pydantic settings
│   │   ├── constants.py        # System prompts & constants
│   │   ├── exceptions.py       # Custom exceptions
│   │   ├── logger.py           # Loguru configuration
│   │   └── security.py         # Authentication logic
│   ├── middlewares/            # Request middlewares
│   │   ├── base.py
│   │   └── timing.py           # Processing time tracker
│   ├── schemas/                # Pydantic models
│   │   ├── ai_response.py      # DeepSeek response schema
│   │   ├── payload.py          # Webhook input schema
│   │   └── trello_api.py       # Trello API schemas
│   ├── services/               # Business logic
│   │   ├── deepseek_engine.py  # AI service with circuit breaker
│   │   └── trello_manager.py   # Trello service
│   └── api/v1/                 # API endpoints
│       ├── endpoints/
│       │   ├── health.py       # Health check
│       │   └── webhooks.py     # Main webhook handler
│       └── router.py
└── tests/                      # Test suite
    ├── unit/                   # Unit tests
    └── integration/            # Integration tests
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Virtual environment (recommended)
- DeepSeek API key
- Trello API credentials

### Installation

```bash
# Clone the repository
git clone https://github.com/Madeena-software/madeena-workspace-ai.git
cd madeena-workspace-ai

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### Configuration

Required environment variables in `.env`:

```bash
# Application
ENV=development
DEBUG=true
APP_TIMEZONE=Asia/Jakarta

# Security
MADEENA_WEBHOOK_SECRET=your-webhook-secret-here

# DeepSeek AI
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# Trello
TRELLO_API_KEY=your-trello-api-key
TRELLO_TOKEN=your-trello-token
TRELLO_BOARD_ID=your-board-id
TRELLO_LIST_ID_INBOX=your-inbox-list-id
```

### Running the Application

#### Development Mode

```bash
# Using make
make run

# Or directly with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir madeena_core
```

#### Production Mode

```bash
# Using Gunicorn
gunicorn -c gunicorn_conf.py app.main:app --chdir madeena_core

# Using Docker
make docker-build
make docker-run

# Or with docker-compose
docker-compose up -d
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Webhook Endpoint

**POST** `/api/v1/webhook`

Process incoming messages from messaging platforms.

**Headers:**
- `X-Madeena-Secret`: Your webhook secret (required)
- `Content-Type`: application/json

**Request Body:**
```json
{
  "platform": "whatsapp",
  "message_text": "TOLONG CEPAT! Fix bug production besok jam 10 pagi",
  "sender_id": "6281234567890",
  "sender_name": "John Doe",
  "timestamp": "2026-02-19T10:30:00Z"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Webhook processed successfully",
  "card_url": "https://trello.com/c/abc123/1-fix-bug-production",
  "card_id": "abc123def456",
  "processing_time": "0.45s",
  "ai_data": {
    "title": "Fix Bug Production",
    "priority": "High",
    "due_date": "2026-02-20",
    "requires_meeting": false
  }
}
```

### Health Check

**GET** `/health`

Returns service health status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "Madeena Core",
  "version": "1.0.0",
  "environment": "development"
}
```

## 🧪 Testing

```bash
# Run all tests
make test

# Or with pytest directly
pytest madeena_core/tests/ -v

# With coverage
pytest madeena_core/tests/ --cov=madeena_core/app --cov-report=html
```

## 🔒 Security

### Security Features

- **API Key Authentication**: X-Madeena-Secret header validation
- **Rate Limiting**: 10 requests/minute per IP (configurable)
- **Input Validation**: Pydantic V2 strict validation
- **Type Safety**: mypy strict mode compliance
- **Security Headers**: CORS, HTTPS enforcement ready
- **Secrets Management**: Environment-based configuration

### Security Scanning

```bash
# Run security checks
make lint

# Manual bandit scan
bandit -r madeena_core/app -ll

# Type checking
mypy madeena_core/app --strict --ignore-missing-imports
```

## 🔧 Development

### Code Quality

```bash
# Type checking
make lint

# Run tests
make test

# Format code (if using black)
black madeena_core/

# Security scan
bandit -r madeena_core/app -ll
```

### Project Standards

- **Type Hints**: All functions must have complete type hints
- **Docstrings**: Google-style docstrings required
- **Testing**: Minimum 80% code coverage
- **Security**: Pass bandit security scans
- **Style**: Follow PEP 8, enforced by mypy strict

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t madeena-core:latest .
```

### Run Container

```bash
docker run -d \
  --name madeena-core \
  -p 8000:8000 \
  --env-file .env \
  madeena-core:latest
```

### Docker Compose

```bash
docker-compose up -d
```

## 📊 Observability

### Logging

All logs include correlation IDs for distributed tracing:

```json
{
  "time": "2026-02-19 12:00:00.123",
  "level": "INFO",
  "correlation_id": "abc-123-def-456",
  "message": "Webhook processed successfully",
  "module": "webhooks",
  "function": "process_webhook",
  "line": 95
}
```

### Monitoring

- **Health Endpoint**: `/health` - For load balancer health checks
- **Process Time**: `X-Process-Time` header on all responses
- **Correlation IDs**: `X-Correlation-ID` for request tracing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework
- **DeepSeek** - AI language model
- **Trello** - Task management platform
- **Loguru** - Beautiful logging

## 📧 Support

For support, email support@madeena.software or open an issue on GitHub.

---

**Built with ❤️ by the Madeena Team**