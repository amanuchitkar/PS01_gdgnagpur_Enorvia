# Kindered – Architecture Document

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                              CLIENT                                    │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────┐  │
│  │  Chat Page      │  │  Dashboard     │  │  PDF Download           │  │
│  │  (Jinja2+JS)    │  │  (Chart.js)    │  │  (Browser fetch)        │  │
│  └───────┬─────────┘  └───────┬────────┘  └──────────┬─────────────┘  │
└──────────┼─────────────────────┼──────────────────────┼────────────────┘
           │ POST /api/message    │ GET /api/dashboard    │ GET /api/report
           ▼                     ▼                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                          FASTAPI APPLICATION                          │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                        ROUTERS                                    │  │
│  │   pages.py (HTML)    api.py (REST JSON + PDF binary)              │  │
│  └────────────────────────────┬──────────────────────────────────────┘  │
│                               │                                        │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                      SERVICE LAYER                                │  │
│  │  conversation_service.py    bedrock_service.py    pdf_service.py   │  │
│  │  (Business logic)          (AI integration)      (Report gen)     │  │
│  └────────────────┬───────────────────┬──────────────────────────────┘  │
│                   │                   │                                  │
│  ┌────────────────▼───────────────────▼─────────────────────────────┐  │
│  │                    REPOSITORY LAYER                                │  │
│  │  conversation_repo  message_repo  observation_repo                │  │
│  │  wellness_repo      pdf_report_repo                               │  │
│  └────────────────────────────┬──────────────────────────────────────┘  │
│                               │                                        │
│  ┌────────────────────────────▼──────────────────────────────────────┐  │
│  │                      DATABASE (SQLAlchemy)                         │  │
│  │  conversations │ messages │ ai_observations │ wellness_plans │ pdf │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   AWS Bedrock          │
                    │   (Claude 3 Sonnet)    │
                    │   - Message analysis   │
                    │   - Wellness plan gen  │
                    └───────────────────────┘
```

## Layer Responsibilities

### Routers (`app/routers/`)
- HTTP request/response handling
- Input validation via Pydantic models
- Error translation to HTTP status codes
- No business logic

### Services (`app/services/`)
- **conversation_service.py**: Orchestrates conversation flow, calls AI and repos
- **bedrock_service.py**: AWS Bedrock API calls, prompt engineering, JSON parsing
- **pdf_service.py**: PDF generation with ReportLab

### Repositories (`app/repositories/`)
- Pure data access (CRUD operations)
- SQLAlchemy queries
- No business logic or external API calls
- Easy to swap underlying database

### Models (`app/models.py`)
- SQLAlchemy ORM definitions
- 5 tables with proper foreign keys and cascades
- Alembic-managed migrations

## Data Flow: Send Message

```
User types message
    → POST /api/conversation/message
        → ConversationService.process_message()
            → ConversationRepository.get_by_id()     [load history]
            → BedrockService.analyze_message()        [AI call]
            → MessageRepository.create() × 2          [user + assistant]
            → AIObservationRepository.create()        [if concerns found]
            → ConversationRepository.update_metadata() [running stats]
        → Return JSON response
    → Frontend updates chat + emotion bar
```

## Data Flow: End Conversation

```
User clicks "End & View Insights"
    → POST /api/conversation/end
        → ConversationService.end_conversation()
            → Aggregate emotion/stress/concerns from messages
            → BedrockService.generate_wellness_plan()
            → WellnessPlanRepository.create()
            → AIObservationRepository.create() (patterns)
            → ConversationRepository.mark_completed()
        → Return summary + plan
    → Redirect to /dashboard/{id}
        → GET /api/dashboard/{id}
            → ConversationService.get_dashboard_data()
            → Return full analytics payload
        → Chart.js renders charts
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Jinja2 + Tailwind CSS + Chart.js | UI rendering + charts |
| API | FastAPI | Async REST API |
| AI | AWS Bedrock (Claude 3) | Emotional analysis + plans |
| ORM | SQLAlchemy 2.0 (async) | Database abstraction |
| Database | SQLite (swappable to PostgreSQL) | Persistence |
| Migrations | Alembic | Schema versioning |
| PDF | ReportLab | Report generation |
| Container | Docker | Isolation & deployment |
| Proxy | Nginx | SSL termination + routing |

## Database Schema

```sql
conversations (id, created_at, updated_at, status, summary,
               dominant_emotion, average_stress, risk_level)

messages (id, conversation_id FK, role, content, created_at,
          emotion, sentiment, stress_score, confidence_score,
          risk_level, emotional_summary, detected_concerns,
          suggested_next_action)

ai_observations (id, conversation_id FK, created_at,
                 observation_type, content, severity,
                 related_emotions, is_recurring)

wellness_plans (id, conversation_id FK, created_at, plan_data)

pdf_reports (id, conversation_id FK, created_at, filename,
             file_path, report_type, file_size_bytes,
             include_wellness_plan, include_charts)
```

## Security

- HTTPS enforced via Nginx redirect
- Security headers (X-Frame-Options, HSTS, etc.)
- No authentication (hackathon MVP requirement)
- AWS credentials via environment variables (never in code)
- Input sanitization via Pydantic
- SQL injection prevented by SQLAlchemy ORM
- XSS prevention via `escapeHtml()` in all frontend rendering
