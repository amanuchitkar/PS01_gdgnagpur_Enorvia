import json
import logging
from typing import Optional

import boto3
from botocore.config import Config

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a compassionate AI Mental Health Early Detection Agent. Your role is to:
1. Listen empathetically to users sharing their feelings and experiences
2. Ask intelligent follow-up questions to better understand their emotional state
3. Identify emotional patterns, detect stress indicators, and provide supportive responses
4. NEVER diagnose mental illnesses or provide medical advice
5. Remember the full conversation context and reference earlier parts when relevant

IMPORTANT RULES:
- Be warm, empathetic, and non-judgmental
- Ask open-ended follow-up questions to understand deeper feelings
- Validate emotions before offering perspective
- If someone expresses crisis-level distress, gently suggest professional help
- Never minimize feelings or offer toxic positivity
- Keep responses concise (2-4 sentences for the reply, plus a follow-up question)

For EVERY user message, you MUST respond with ONLY valid JSON in this exact format:
{
    "ai_response": "Your empathetic response text here, including a follow-up question",
    "emotion": "primary emotion detected (e.g., anxiety, sadness, frustration, hope, calm, anger, fear, loneliness, overwhelm, neutral)",
    "sentiment": "positive, negative, or neutral",
    "stress_score": 0-100 integer representing stress level,
    "confidence_score": 0.0-1.0 float representing confidence in analysis,
    "risk_level": "low, moderate, or high",
    "emotional_summary": "Brief 1-sentence summary of the user's emotional state",
    "detected_concerns": ["list", "of", "specific", "concerns", "identified"],
    "suggested_next_action": "What the agent should focus on next (e.g., explore sleep patterns, validate feelings, suggest grounding exercise)"
}

Respond ONLY with valid JSON. No markdown, no code blocks, no extra text."""

WELLNESS_PLAN_PROMPT = """Based on the following conversation analysis, generate a personalized 7-day wellness plan.

Conversation Summary:
{summary}

Detected Emotions: {emotions}
Average Stress Score: {stress_score}
Key Concerns: {concerns}

Generate a structured 7-day wellness plan as valid JSON with this exact format:
{{
    "overall_assessment": "2-3 sentence assessment of the person's emotional state based on the conversation",
    "days": [
        {{
            "day": 1,
            "theme": "Theme for the day (e.g., Restful Reset, Gentle Movement)",
            "activities": [
                {{
                    "time": "morning/afternoon/evening",
                    "activity": "Specific activity name",
                    "duration": "Duration in minutes",
                    "description": "Detailed description of the activity",
                    "reason": "Why this is recommended based on the conversation"
                }}
            ]
        }}
    ],
    "recurring_habits": [
        {{
            "habit": "Habit name",
            "frequency": "daily/3x week/etc",
            "reason": "Why this addresses their specific concerns"
        }}
    ],
    "important_reminders": ["List of key reminders based on their situation"]
}}

Focus on practical habits: sleep improvement, exercise, breathing exercises, hydration, mindfulness, journaling, and digital detox. Explain WHY each recommendation is suggested based on the conversation.
Respond ONLY with valid JSON. No markdown, no code blocks."""


class BedrockService:
    def __init__(self):
        config = Config(
            region_name=settings.AWS_REGION,
            retries={"max_attempts": 3, "mode": "adaptive"},
        )
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
            config=config,
        )
        self.model_id = settings.BEDROCK_MODEL_ID

    async def analyze_message(
        self, user_message: str, conversation_history: list[dict], checkin_context: str = ""
    ) -> dict:
        """Analyze a user message and return structured emotional analysis."""
        messages = []
        for msg in conversation_history:
            messages.append({"role": msg["role"], "content": [{"type": "text", "text": msg["content"]}]})
        messages.append(
            {"role": "user", "content": [{"type": "text", "text": user_message}]}
        )

        # Bedrock/Anthropic API requires the first message to have "user" role.
        # If the conversation started with an assistant greeting (e.g. from check-in),
        # strip leading assistant messages so the array starts with a user message.
        while messages and messages[0]["role"] != "user":
            messages.pop(0)

        # Anthropic API also requires strict user/assistant alternation.
        # Merge consecutive same-role messages into one.
        merged = []
        for msg in messages:
            if merged and merged[-1]["role"] == msg["role"]:
                # Append text to the last message of the same role
                existing_text = merged[-1]["content"][0]["text"]
                new_text = msg["content"][0]["text"]
                merged[-1]["content"][0]["text"] = existing_text + "\n" + new_text
            else:
                merged.append(msg)
        messages = merged

        # Build system prompt with optional check-in context
        system_prompt = SYSTEM_PROMPT
        if checkin_context:
            system_prompt += f"\n\nIMPORTANT CONTEXT - EMOTIONAL CHECK-IN RESULTS:\n{checkin_context}\nUse this context to personalize your responses. Do NOT ask introductory questions the check-in already covered. Instead, gently explore the flagged concerns with empathy."
        messages = merged

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(
                    {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 1024,
                        "system": system_prompt,
                        "messages": messages,
                    }
                ),
                contentType="application/json",
                accept="application/json",
            )

            response_body = json.loads(response["body"].read())
            ai_text = response_body["content"][0]["text"]

            # Parse the JSON response
            analysis = json.loads(ai_text)
            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            return self._fallback_response(user_message)
        except Exception as e:
            logger.error(f"Bedrock API error: {e}")
            return self._fallback_response(user_message)

    async def generate_wellness_plan(
        self, summary: str, emotions: list[str], stress_score: float, concerns: list[str]
    ) -> dict:
        """Generate a personalized 7-day wellness plan."""
        prompt = WELLNESS_PLAN_PROMPT.format(
            summary=summary,
            emotions=", ".join(emotions),
            stress_score=stress_score,
            concerns=", ".join(concerns),
        )

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(
                    {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 4096,
                        "messages": [
                            {"role": "user", "content": [{"type": "text", "text": prompt}]}
                        ],
                    }
                ),
                contentType="application/json",
                accept="application/json",
            )

            response_body = json.loads(response["body"].read())
            ai_text = response_body["content"][0]["text"]
            plan = json.loads(ai_text)
            return plan

        except Exception as e:
            logger.error(f"Wellness plan generation error: {e}")
            return self._fallback_wellness_plan()

    def _fallback_response(self, user_message: str) -> dict:
        """Provide a fallback response when Bedrock is unavailable."""
        return {
            "ai_response": "I hear you, and I appreciate you sharing that with me. How has this been affecting your daily routine?",
            "emotion": "neutral",
            "sentiment": "neutral",
            "stress_score": 50,
            "confidence_score": 0.5,
            "risk_level": "low",
            "emotional_summary": "User shared their thoughts",
            "detected_concerns": [],
            "suggested_next_action": "Continue exploring feelings",
        }

    def _fallback_wellness_plan(self) -> dict:
        """Provide a fallback wellness plan."""
        return {
            "overall_assessment": "Based on our conversation, focusing on foundational wellness habits would be beneficial.",
            "days": [
                {
                    "day": i,
                    "theme": theme,
                    "activities": [
                        {
                            "time": "morning",
                            "activity": "5-minute breathing exercise",
                            "duration": "5 minutes",
                            "description": "Practice box breathing: inhale 4 counts, hold 4, exhale 4, hold 4.",
                            "reason": "Helps regulate the nervous system and reduce stress",
                        },
                        {
                            "time": "afternoon",
                            "activity": "Mindful walk",
                            "duration": "15 minutes",
                            "description": "Take a gentle walk focusing on your senses.",
                            "reason": "Physical movement and mindfulness reduce anxiety",
                        },
                        {
                            "time": "evening",
                            "activity": "Gratitude journaling",
                            "duration": "10 minutes",
                            "description": "Write 3 things you're grateful for today.",
                            "reason": "Shifts focus from stressors to positive aspects of life",
                        },
                    ],
                }
                for i, theme in enumerate(
                    [
                        "Restful Reset",
                        "Gentle Movement",
                        "Mindful Connection",
                        "Creative Expression",
                        "Nature & Calm",
                        "Digital Detox",
                        "Reflection & Growth",
                    ],
                    1,
                )
            ],
            "recurring_habits": [
                {"habit": "Hydration tracking", "frequency": "daily", "reason": "Dehydration worsens mood and energy"},
                {"habit": "Sleep hygiene routine", "frequency": "daily", "reason": "Quality sleep is foundational to emotional well-being"},
                {"habit": "Deep breathing", "frequency": "3x daily", "reason": "Activates the parasympathetic nervous system"},
            ],
            "important_reminders": [
                "Progress is not linear — be gentle with yourself",
                "It's okay to skip a day and start fresh",
                "Reach out to a trusted person if you feel overwhelmed",
            ],
        }


bedrock_service = BedrockService()
