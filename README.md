# Kindered – AI-Powered Mental Health Early Detection Agent

> **Helping people recognize emotional changes early through AI-powered conversations, personalized insights, and wellness recommendations.**

**🌐 Live Demo:** https://kindered.enorviaglobal.com

---

# Overview

**Kindered** is an AI-powered emotional wellness platform designed to help individuals identify gradual emotional changes before they become more serious.

Unlike traditional chatbots, Kindered functions as an **AI Mental Health Early Detection Agent**. It listens, understands context, analyzes emotional patterns throughout a conversation, and provides supportive, personalized wellness guidance.

The goal is **early awareness**, **self-reflection**, and **timely intervention**—not diagnosis.

---

# Problem Statement

Mental health challenges such as stress, anxiety, burnout, loneliness, and emotional exhaustion rarely appear overnight. They often develop gradually through everyday experiences, making them difficult for individuals to recognize until they begin affecting work, studies, relationships, or overall quality of life.

Unfortunately, most mental health support systems are reactive. Many people seek professional help only after symptoms become severe. Others avoid discussing their emotions because of stigma, limited access to professionals, financial barriers, or simply because they do not realize their emotional wellbeing is declining.

Existing AI chatbots generally provide conversational support but lack the ability to continuously understand emotional patterns, detect changes over time, and transform conversations into meaningful wellbeing insights.

There is a growing need for an intelligent, accessible, and privacy-focused solution that encourages users to regularly reflect on their emotional wellbeing, recognize early warning signs, and seek appropriate support before emotional difficulties escalate.

---

# Our Solution

Kindered addresses this challenge through an AI-powered emotional wellness companion built using **Python**, **FastAPI**, and **AWS Bedrock**.

Rather than simply responding to messages, Kindered continuously analyzes conversations to understand how a user is feeling.

The AI Agent can:

- Understand emotional context
- Detect stress and emotional patterns
- Ask intelligent follow-up questions
- Identify recurring concerns
- Generate personalized wellness recommendations
- Create structured emotional wellbeing reports
- Encourage professional support when emotional risk increases

Kindered **does not diagnose mental illnesses** or replace licensed mental health professionals.

Instead, it helps users better understand themselves through regular emotional check-ins and AI-powered reflection.

---

# Key Features

## 🤖 AI Emotional Conversation

An intelligent AI companion that conducts natural, supportive conversations.

The AI:

- Maintains conversation context
- Responds empathetically
- Asks meaningful follow-up questions
- Detects emotional changes during the conversation

---

## 📊 Emotional Analysis

Every message is analyzed using AWS Bedrock.

The AI identifies:

- Primary emotion
- Sentiment
- Stress score (0–100)
- Confidence score
- Emotional concerns
- Risk level

---

## 📈 Real-Time Emotional Tracking

As conversations progress, Kindered continuously updates emotional indicators and stress levels, allowing users to observe changes throughout the session.

---

## 📉 Emotional Insights Dashboard

After completing the conversation, Kindered generates a personalized dashboard containing:

- Emotional timeline
- Stress trend
- Emotion distribution
- AI observations
- Conversation insights
- Wellness summary

---

## 🌱 Personalized 7-Day Wellness Plan

Based on the conversation, the AI creates a practical improvement plan including recommendations such as:

- Better sleep habits
- Mindfulness
- Breathing exercises
- Physical activity
- Hydration
- Digital wellbeing
- Journaling
- Social connection

Every recommendation includes an explanation describing why it was suggested.

---

## 📄 Professional PDF Report

Generate a downloadable report containing:

- Conversation summary
- Emotional assessment
- Stress analysis
- Wellness observations
- Personalized recommendations
- Seven-day wellness plan

The report can be saved for personal reflection or shared with a licensed mental health professional if the user chooses.

---

# How Kindered Works

```text
User Conversation
        │
        ▼
AWS Bedrock AI Agent
        │
        ▼
Emotion Analysis
        │
        ▼
Stress & Risk Detection
        │
        ▼
Conversation Insights
        │
        ▼
Wellness Dashboard
        │
        ▼
7-Day Wellness Plan
        │
        ▼
Professional PDF Report
```

---

# Important Disclaimer

> **Kindered is an emotional wellness support application.**

Kindered is **not** a medical device and **does not diagnose** depression, anxiety disorders, or any other mental health condition.

The application is **not a replacement for licensed psychologists, psychiatrists, therapists, counselors, or other healthcare professionals.**

If you are experiencing significant emotional distress, thoughts of self-harm, or believe you are in crisis, please contact your local emergency services, crisis helpline, or a licensed mental health professional immediately.

---

# Technology Stack

| Layer | Technology |
|--------|------------|
| Backend | Python 3.11 |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (Async) |
| Frontend | Jinja2 Templates |
| UI | HTML5, Tailwind CSS, Vanilla JavaScript |
| Charts | Chart.js |
| Database | SQLite (PostgreSQL-ready via Alembic) |
| AI | AWS Bedrock (Claude 3 Sonnet) |
| PDF | ReportLab |
| Deployment | Docker, Nginx, Let's Encrypt |

---

# Project Architecture

```text
                 User
                  │
                  ▼
        AI Conversation Page
                  │
                  ▼
        FastAPI Backend API
                  │
                  ▼
        AWS Bedrock (Claude)
                  │
        ┌─────────┼─────────┐
        │         │         │
        ▼         ▼         ▼
 Emotion Analysis  Stress Analysis  Risk Detection
        │
        ▼
 SQLite Database
        │
        ▼
 Dashboard Generator
        │
        ├───────────────┐
        ▼               ▼
 Wellness Plan      PDF Report
```

---

# Project Structure

```text
app/
├── main.py
├── config.py
├── database.py
├── models.py
├── routers/
│   ├── api.py
│   └── pages.py
├── repositories/
├── services/
│   ├── bedrock_service.py
│   ├── conversation_service.py
│   └── pdf_service.py
├── templates/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── reports/

alembic/
deploy/
docs/
Dockerfile
docker-compose.yml
requirements.txt
README.md
```

---

# API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/conversation/start` | Start a new conversation |
| POST | `/api/conversation/message` | Send a message and receive AI analysis |
| POST | `/api/conversation/end` | End conversation and generate insights |
| GET | `/api/dashboard/{id}` | Dashboard analytics |
| GET | `/api/report/{id}/pdf` | Download PDF report |

---

# Local Development

## Clone Repository

```bash
git clone <repository-url>
cd kindered
```

## Create Virtual Environment

```bash
python -m venv .venv
```

Linux/macOS

```bash
source .venv/bin/activate
```

Windows

```bash
.venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment

```bash
cp .env.example .env
```

Update the AWS Bedrock credentials inside `.env`.

---

## Run Database Migrations

```bash
alembic upgrade head
```

---

## Start Application

```bash
uvicorn app.main:app --reload --port 8000
```

Open:

```
http://localhost:8000
```

---

# Docker

```bash
cp .env.example .env
```

Configure AWS credentials.

Then run:

```bash
docker compose up --build
```

---

# Migration to PostgreSQL

Kindered currently uses SQLite for rapid development.

The project has been designed using SQLAlchemy and Alembic, allowing seamless migration to PostgreSQL.

Simply update:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/kindered
```

Install:

```bash
pip install asyncpg
```

Run:

```bash
alembic upgrade head
```

No application code changes are required.

---

# Future Roadmap

- Persistent AI memory across sessions
- Voice conversations
- Wearable integration
- Therapist dashboard
- Personalized CBT-inspired wellness exercises
- Multi-language support
- Mobile application
- PostgreSQL + pgvector for semantic AI memory
- Anonymous organizational wellness analytics

---

# Why Kindered?

Kindered demonstrates how modern AI can move beyond simple conversation and become an intelligent emotional wellness companion.

By combining conversational AI, emotional analysis, personalized recommendations, and actionable insights, Kindered empowers users to better understand their emotional wellbeing while encouraging early intervention and professional support when needed.

The project is designed to be ethical, privacy-focused, scalable, and suitable for real-world emotional wellness applications.