# Kindered – API Documentation

Base URL: `https://kindered.enorviaglobal.com`

## Endpoints

### Health Check

```
GET /health
```

**Response:**
```json
{"status": "healthy", "service": "Kindered"}
```

---

### Start Conversation

```
POST /api/conversation/start
```

Creates a new conversation session.

**Response:**
```json
{
    "conversation_id": "uuid-string",
    "status": "active"
}
```

---

### Send Message

```
POST /api/conversation/message
```

Sends a user message and returns AI analysis.

**Request Body:**
```json
{
    "conversation_id": "uuid-string",
    "message": "I've been feeling overwhelmed at work lately"
}
```

**Response:**
```json
{
    "ai_response": "I hear you — feeling overwhelmed at work can be draining. What aspects of work feel most challenging right now?",
    "emotion": "overwhelm",
    "sentiment": "negative",
    "stress_score": 65,
    "confidence_score": 0.85,
    "risk_level": "moderate",
    "emotional_summary": "User is experiencing work-related overwhelm and stress",
    "detected_concerns": ["work stress", "overwhelm"],
    "suggested_next_action": "explore specific work stressors"
}
```

---

### End Conversation

```
POST /api/conversation/end
```

Ends the conversation, generates wellness plan and summary.

**Request Body:**
```json
{
    "conversation_id": "uuid-string"
}
```

**Response:**
```json
{
    "conversation_id": "uuid-string",
    "summary": "User expressed work-related stress and sleep difficulties...",
    "dominant_emotion": "anxiety",
    "average_stress": 62.5,
    "risk_level": "moderate",
    "emotions": ["anxiety", "overwhelm", "frustration", "hope"],
    "concerns": ["work stress", "sleep issues", "perfectionism"],
    "wellness_plan": { ... }
}
```

---

### Get Dashboard Data

```
GET /api/dashboard/{conversation_id}
```

Returns full dashboard analytics for a conversation.

**Response:**
```json
{
    "conversation_id": "uuid-string",
    "status": "completed",
    "created_at": "2024-01-15T10:30:00",
    "summary": "...",
    "dominant_emotion": "anxiety",
    "average_stress": 62.5,
    "risk_level": "moderate",
    "timeline": [
        {
            "time": "2024-01-15T10:31:00",
            "emotion": "anxiety",
            "stress_score": 70,
            "content_preview": "I've been feeling overwhelmed..."
        }
    ],
    "emotion_frequency": {"anxiety": 3, "overwhelm": 2, "hope": 1},
    "stress_scores": [70, 65, 55, 60],
    "concerns": ["work stress", "sleep issues"],
    "observations": [
        {
            "type": "pattern",
            "content": "Recurring emotional pattern: anxiety appeared 3 times",
            "severity": "warning",
            "is_recurring": true
        }
    ],
    "message_count": 8,
    "wellness_plan": { ... }
}
```

---

### Download PDF Report

```
GET /api/report/{conversation_id}/pdf
```

Generates and downloads a professional PDF wellness report.

**Response:** Binary PDF file with headers:
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="kindered_wellness_report_20240115_103000.pdf"
```

---

## Pages

| URL | Description |
|-----|-------------|
| `/` | Main conversation page (opens directly) |
| `/dashboard/{conversation_id}` | Wellness dashboard with charts |

## Error Responses

All errors follow this format:
```json
{
    "detail": "Error description"
}
```

| Status | Meaning |
|--------|---------|
| 404 | Conversation not found |
| 500 | Internal server error (Bedrock/DB issue) |
