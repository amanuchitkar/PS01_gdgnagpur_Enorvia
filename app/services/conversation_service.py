import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import (
    ConversationRepository,
    MessageRepository,
    WellnessPlanRepository,
    AIObservationRepository,
)
from app.models import Conversation
from app.services.bedrock_service import bedrock_service

logger = logging.getLogger(__name__)


class ConversationService:
    """Service layer orchestrating conversation logic.

    All database operations are delegated to repository classes.
    This service handles business logic and AI integration only.
    """

    def __init__(self):
        self.conversation_repo = ConversationRepository()
        self.message_repo = MessageRepository()
        self.wellness_repo = WellnessPlanRepository()
        self.observation_repo = AIObservationRepository()

    async def create_conversation(self, db: AsyncSession) -> Conversation:
        """Create a new conversation session."""
        return await self.conversation_repo.create(db)

    async def create_conversation_with_checkin(
        self,
        db: AsyncSession,
        score: int,
        max_score: int,
        category: str,
        concerns: list[str],
        emotional_summary: str,
        area_scores: dict,
    ) -> Conversation:
        """Create a conversation pre-seeded with emotional check-in context.

        Stores the check-in results as an initial system-level assistant message
        so the AI has context about the user's emotional state without needing to
        repeat introductory questions.
        """
        conversation = await self.conversation_repo.create(db)

        # Build a context message that provides the AI with check-in results
        context_content = (
            f"[Assessment Context] The user completed an emotional wellness check-in "
            f"before starting this conversation. Results: Score {score}/{max_score} "
            f"(Category: {category})."
        )
        if concerns:
            context_content += f" Areas of concern: {', '.join(concerns)}."
        context_content += (
            " Please acknowledge that they've already completed the check-in, "
            "reference their results gently, and explore their flagged areas "
            "with empathy. Do not ask generic introductory questions."
        )

        # Store as an assistant message so it becomes part of conversation history
        # that the AI will see as context
        checkin_greeting = self._build_checkin_greeting(category, concerns)
        await self.message_repo.create(
            db,
            conversation_id=conversation.id,
            role="assistant",
            content=checkin_greeting,
            emotional_summary=emotional_summary,
            detected_concerns=concerns if concerns else None,
        )

        # Store an initial observation about the check-in
        await self.observation_repo.create(
            db,
            conversation_id=conversation.id,
            observation_type="insight",
            content=f"Pre-conversation check-in completed. Category: {category}. "
            f"Score: {score}/{max_score}. Concerns: {', '.join(concerns) if concerns else 'None flagged'}.",
            severity="info" if category in ("Thriving", "Doing Well") else "warning",
            related_emotions=concerns[:5] if concerns else None,
        )

        await db.commit()
        return conversation

    def _build_checkin_greeting(self, category: str, concerns: list[str]) -> str:
        """Build a personalized greeting based on check-in results."""
        if category == "Thriving":
            greeting = (
                "Thank you for taking the time to check in with yourself. "
                "It sounds like you're in a strong place emotionally right now, "
                "which is wonderful. I'm here if you'd like to explore anything "
                "on your mind or simply reflect on what's going well."
            )
        elif category == "Doing Well":
            greeting = (
                "Thanks for completing the check-in. It looks like you're managing "
                "well overall, though there may be a few areas worth exploring together. "
                "I'm here to listen — what feels most present for you right now?"
            )
        elif category == "Needs Attention":
            greeting = (
                "Thank you for being honest in your check-in — that takes real courage. "
                "I can see some areas where things have been harder lately"
            )
            if concerns:
                greeting += f", particularly around {concerns[0]}"
                if len(concerns) > 1:
                    greeting += f" and {concerns[1]}"
            greeting += (
                ". I'm here to listen without judgment. "
                "Would you like to start by sharing more about what's been weighing on you?"
            )
        else:  # High Emotional Strain
            greeting = (
                "I really appreciate you reaching out and being open in your check-in. "
                "It sounds like things have been genuinely difficult recently"
            )
            if concerns:
                greeting += f", especially around {concerns[0]}"
            greeting += (
                ". Please know you don't have to carry this alone. "
                "I'm here to listen for as long as you need. "
                "What would feel most helpful to talk about right now?"
            )
        return greeting

    async def get_conversation(self, db: AsyncSession, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation with all messages."""
        return await self.conversation_repo.get_by_id(db, conversation_id)

    async def process_message(
        self, db: AsyncSession, conversation_id: str, user_message: str
    ) -> dict:
        """Process a user message: analyze with Bedrock and store results."""
        conversation = await self.conversation_repo.get_by_id(db, conversation_id)
        if not conversation:
            raise ValueError("Conversation not found")

        # Build conversation history for context
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation.messages
        ]

        # Extract check-in context if this conversation started from check-in.
        # The first assistant message will have emotional_summary set from the check-in.
        checkin_context = ""
        if conversation.messages:
            first_msg = conversation.messages[0]
            if first_msg.role == "assistant" and first_msg.emotional_summary:
                checkin_context = first_msg.emotional_summary
                if first_msg.detected_concerns:
                    concerns_str = ", ".join(first_msg.detected_concerns)
                    checkin_context += f" Detected concerns: {concerns_str}."

        # Analyze with Bedrock
        analysis = await bedrock_service.analyze_message(user_message, history, checkin_context)

        # Store user message with analysis via repository
        await self.message_repo.create(
            db,
            conversation_id=conversation_id,
            role="user",
            content=user_message,
            emotion=analysis.get("emotion"),
            sentiment=analysis.get("sentiment"),
            stress_score=analysis.get("stress_score"),
            confidence_score=analysis.get("confidence_score"),
            risk_level=analysis.get("risk_level"),
            emotional_summary=analysis.get("emotional_summary"),
            detected_concerns=analysis.get("detected_concerns"),
            suggested_next_action=analysis.get("suggested_next_action"),
        )

        # Store AI response as assistant message
        ai_response = analysis.get("ai_response", "I'm here to listen. Could you tell me more?")
        await self.message_repo.create(
            db,
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response,
        )

        # Record AI observation if concerns detected
        concerns = analysis.get("detected_concerns", [])
        if concerns:
            await self.observation_repo.create(
                db,
                conversation_id=conversation_id,
                observation_type="concern",
                content=f"Detected concerns: {', '.join(concerns)}",
                severity="warning" if analysis.get("risk_level") == "moderate" else "info",
                related_emotions=[analysis.get("emotion")] if analysis.get("emotion") else None,
            )

        # Update conversation running metadata
        await self._update_conversation_metadata(db, conversation_id)

        await db.commit()

        return {
            "ai_response": ai_response,
            "emotion": analysis.get("emotion"),
            "sentiment": analysis.get("sentiment"),
            "stress_score": analysis.get("stress_score"),
            "confidence_score": analysis.get("confidence_score"),
            "risk_level": analysis.get("risk_level"),
            "emotional_summary": analysis.get("emotional_summary"),
            "detected_concerns": concerns,
            "suggested_next_action": analysis.get("suggested_next_action"),
        }

    async def end_conversation(self, db: AsyncSession, conversation_id: str) -> dict:
        """End a conversation: generate summary and wellness plan."""
        conversation = await self.conversation_repo.get_by_id(db, conversation_id)
        if not conversation:
            raise ValueError("Conversation not found")

        # Gather analysis data from messages
        emotions = []
        stress_scores = []
        concerns = []
        summaries = []

        for msg in conversation.messages:
            if msg.role == "user" and msg.emotion:
                emotions.append(msg.emotion)
                if msg.stress_score is not None:
                    stress_scores.append(msg.stress_score)
                if msg.detected_concerns:
                    concerns.extend(msg.detected_concerns)
                if msg.emotional_summary:
                    summaries.append(msg.emotional_summary)

        avg_stress = sum(stress_scores) / len(stress_scores) if stress_scores else 50
        unique_concerns = list(set(concerns))
        summary_text = ". ".join(summaries) if summaries else "General wellness conversation"

        # Determine dominant emotion
        dominant_emotion = (
            max(set(emotions), key=emotions.count) if emotions else "neutral"
        )

        # Determine overall risk level
        risk_levels = [msg.risk_level for msg in conversation.messages if msg.risk_level]
        if "high" in risk_levels:
            overall_risk = "high"
        elif "moderate" in risk_levels:
            overall_risk = "moderate"
        else:
            overall_risk = "low"

        # Generate wellness plan via Bedrock
        plan_data = await bedrock_service.generate_wellness_plan(
            summary=summary_text,
            emotions=emotions,
            stress_score=avg_stress,
            concerns=unique_concerns,
        )

        # Store wellness plan via repository
        await self.wellness_repo.create(
            db, conversation_id=conversation_id, plan_data=plan_data
        )

        # Store final observation summarizing the session
        await self.observation_repo.create(
            db,
            conversation_id=conversation_id,
            observation_type="insight",
            content=f"Session complete. Dominant emotion: {dominant_emotion}. "
            f"Average stress: {avg_stress:.0f}/100. Risk: {overall_risk}.",
            severity="info",
            related_emotions=list(set(emotions)),
        )

        # Detect recurring patterns
        if len(set(emotions)) < len(emotions) and len(emotions) >= 3:
            recurring_emotion = max(set(emotions), key=emotions.count)
            await self.observation_repo.create(
                db,
                conversation_id=conversation_id,
                observation_type="pattern",
                content=f"Recurring emotional pattern detected: {recurring_emotion} appeared "
                f"{emotions.count(recurring_emotion)} times across the conversation.",
                severity="warning",
                related_emotions=[recurring_emotion],
                is_recurring=True,
            )

        # Mark conversation as completed
        await self.conversation_repo.mark_completed(
            db,
            conversation_id=conversation_id,
            summary=summary_text,
            dominant_emotion=dominant_emotion,
            average_stress=avg_stress,
            risk_level=overall_risk,
        )

        await db.commit()

        return {
            "conversation_id": conversation_id,
            "summary": summary_text,
            "dominant_emotion": dominant_emotion,
            "average_stress": avg_stress,
            "risk_level": overall_risk,
            "emotions": emotions,
            "concerns": unique_concerns,
            "wellness_plan": plan_data,
        }

    async def get_dashboard_data(self, db: AsyncSession, conversation_id: str) -> dict:
        """Get dashboard data for a completed conversation."""
        conversation = await self.conversation_repo.get_by_id(db, conversation_id)
        if not conversation:
            raise ValueError("Conversation not found")

        # Get wellness plan via repository
        wellness_plan = await self.wellness_repo.get_by_conversation(db, conversation_id)

        # Get observations via repository
        observations = await self.observation_repo.get_by_conversation(db, conversation_id)

        # Build timeline data
        timeline = []
        emotions = []
        stress_scores = []
        concerns = []

        for msg in conversation.messages:
            if msg.role == "user" and msg.emotion:
                timeline.append({
                    "time": msg.created_at.isoformat() if msg.created_at else "",
                    "emotion": msg.emotion,
                    "stress_score": msg.stress_score,
                    "content_preview": (
                        msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
                    ),
                })
                emotions.append(msg.emotion)
                if msg.stress_score is not None:
                    stress_scores.append(msg.stress_score)
                if msg.detected_concerns:
                    concerns.extend(msg.detected_concerns)

        # Emotion frequency
        emotion_freq = {}
        for e in emotions:
            emotion_freq[e] = emotion_freq.get(e, 0) + 1

        # Format observations
        formatted_observations = [
            {
                "type": obs.observation_type,
                "content": obs.content,
                "severity": obs.severity,
                "is_recurring": obs.is_recurring,
            }
            for obs in observations
        ]

        return {
            "conversation_id": conversation_id,
            "status": conversation.status,
            "created_at": conversation.created_at.isoformat() if conversation.created_at else "",
            "summary": conversation.summary or "Conversation in progress",
            "dominant_emotion": conversation.dominant_emotion or "neutral",
            "average_stress": conversation.average_stress or 0,
            "risk_level": conversation.risk_level or "low",
            "timeline": timeline,
            "emotion_frequency": emotion_freq,
            "stress_scores": stress_scores,
            "concerns": list(set(concerns)),
            "observations": formatted_observations,
            "message_count": len(conversation.messages),
            "wellness_plan": wellness_plan.plan_data if wellness_plan else None,
        }

    async def _update_conversation_metadata(self, db: AsyncSession, conversation_id: str):
        """Update running conversation metadata from analyzed messages."""
        messages = await self.message_repo.get_analyzed_messages(db, conversation_id)

        if messages:
            emotions = [m.emotion for m in messages if m.emotion]
            stress_scores = [m.stress_score for m in messages if m.stress_score is not None]

            dominant = max(set(emotions), key=emotions.count) if emotions else None
            avg_stress = sum(stress_scores) / len(stress_scores) if stress_scores else None

            await self.conversation_repo.update_metadata(
                db,
                conversation_id,
                dominant_emotion=dominant,
                average_stress=avg_stress,
            )


conversation_service = ConversationService()
