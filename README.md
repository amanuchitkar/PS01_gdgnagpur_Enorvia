# Kindered – AI Mental Health Early Detection Agent

An AI-powered emotional wellness support application that detects stress, identifies emotional patterns, provides empathetic support, and generates personalized wellness recommendations.

**Live:** https://kindered.enorviaglobal.com

## Features

- **AI Conversation Agent**: Context-aware AI that remembers the conversation, asks intelligent follow-up questions, and detects emotional patterns
- **Structured Analysis**: Every message analyzed for emotion, sentiment, stress score (0–100), confidence, risk level, and concerns
- **Real-time Tracking**: Live stress and emotion indicators during conversation
- **Wellness Dashboard**: Interactive charts (emotional timeline, emotion distribution), AI observations, and conversation insights
- **7-Day Wellness Plan**: Personalized daily recommendations with specific habits and reasoning
- **PDF Reports**: Downloadable professional report suitable for sharing with mental health professionals
- **AWS Bedrock (Claude)**: Production AI integration for intelligent, empathetic responses

## Important Disclaimer

This application supports emotional wellness and is **not a replacement for licensed mental health professionals**. It does not diagnose mental illnesses or provide medical advice.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0 (async) |
| Frontend | Jinja2, Tailwind CSS, Chart.js, Vanilla JS |
| Database | SQLite (PostgreSQL-ready via Alembic) |
| AI | AWS Bedrock (Claude 3 Sonnet) |
| PDF | ReportLab |
| Deployment | Docker, Nginx, Let's Encrypt |

## Quick Start

### Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your AWS credentials

# Run database migrations
alembic upgrade head

# Start the application
uvicorn app.main:app --reload --port 8000
```

### Docker

```bash
cp .env.example .env
# Edit .env with your AWS credentials

docker compose up --build
```

Open http://localhost:8000 — the app opens directly to the conversation page.

## Project Structure

```
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Environment configuration
│   ├── database.py             # Async SQLAlchemy setup
│   ├── models.py               # 5 ORM models
│   ├── routers/
│   │   ├── api.py              # REST API + PDF endpoint
│   │   └── pages.py            # HTML routes
│   ├── services/
│   │   ├── bedrock_service.py  # AWS Bedrock integration
│   │   ├── conversation_service.py  # Business logic
│   │   └── pdf_service.py      # PDF report generation
│   ├── repositories/           # Data access layer (5 repos)
│   ├── templates/              # Jinja2 HTML templates
│   ├── static/js/              # Frontend JavaScript
│   └── reports/                # Generated PDF files
├── alembic/                    # Database migrations
├── deploy/
│   ├── nginx/                  # Nginx server block
│   ├── deploy.sh               # Automated deployment
│   └── rollback.sh             # Rollback script
├── docs/
│   ├── ARCHITECTURE.md         # System architecture
│   ├── API.md                  # API documentation
│   └── DEPLOYMENT.md           # Deployment guide
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/conversation/start` | Start new session |
| POST | `/api/conversation/message` | Send message, get AI analysis |
| POST | `/api/conversation/end` | End session, generate plan |
| GET | `/api/dashboard/{id}` | Dashboard analytics data |
| GET | `/api/report/{id}/pdf` | Download PDF report |

## How It Works

1. User opens the app → lands on the conversation page
2. AI engages with empathetic questions and detects emotional patterns
3. Each message is analyzed: emotion, stress, sentiment, risk, concerns
4. Real-time emotion bar shows current state
5. "End & View Insights" generates the wellness plan
6. Dashboard shows charts, observations, and the 7-day plan
7. PDF report can be downloaded for personal records or sharing with professionals

## Database Migration to PostgreSQL

```bash
# 1. Install asyncpg
pip install asyncpg

# 2. Update .env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/kindered

# 3. Run migrations
alembic upgrade head
```

No code changes required.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) – System design and data flow
- [API Reference](docs/API.md) – Endpoint documentation
- [Deployment Guide](docs/DEPLOYMENT.md) – VPS deployment with isolation guarantees
