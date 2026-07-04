import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Boolean,
)
from sqlalchemy.orm import relationship

from app.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Conversation(Base):
    """A conversation session between user and AI agent."""

    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    status = Column(String(20), default="active", nullable=False)  # active, completed
    summary = Column(Text, nullable=True)
    dominant_emotion = Column(String(50), nullable=True)
    average_stress = Column(Float, nullable=True)
    risk_level = Column(String(20), nullable=True)  # low, moderate, high

    # Relationships
    messages = relationship(
        "Message", back_populates="conversation", order_by="Message.created_at", cascade="all, delete-orphan"
    )
    observations = relationship(
        "AIObservation", back_populates="conversation", order_by="AIObservation.created_at", cascade="all, delete-orphan"
    )
    wellness_plan = relationship(
        "WellnessPlan", back_populates="conversation", uselist=False, cascade="all, delete-orphan"
    )
    pdf_reports = relationship(
        "PDFReport", back_populates="conversation", order_by="PDFReport.created_at", cascade="all, delete-orphan"
    )


class Message(Base):
    """Individual message in a conversation with AI analysis metadata."""

    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # AI emotion analysis (populated for user messages)
    emotion = Column(String(50), nullable=True)
    sentiment = Column(String(20), nullable=True)  # positive, negative, neutral
    stress_score = Column(Integer, nullable=True)  # 0-100
    confidence_score = Column(Float, nullable=True)  # 0.0-1.0
    risk_level = Column(String(20), nullable=True)  # low, moderate, high
    emotional_summary = Column(Text, nullable=True)
    detected_concerns = Column(JSON, nullable=True)
    suggested_next_action = Column(String(255), nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class AIObservation(Base):
    """AI-generated observations about patterns detected across conversation."""

    __tablename__ = "ai_observations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    observation_type = Column(String(50), nullable=False)  # pattern, concern, positive, insight
    content = Column(Text, nullable=False)
    severity = Column(String(20), nullable=True)  # info, warning, critical
    related_emotions = Column(JSON, nullable=True)
    is_recurring = Column(Boolean, default=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="observations")


class WellnessPlan(Base):
    """Generated 7-day personalized wellness plan."""

    __tablename__ = "wellness_plans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    plan_data = Column(JSON, nullable=False)  # Full structured plan

    # Relationships
    conversation = relationship("Conversation", back_populates="wellness_plan")


class PDFReport(Base):
    """Metadata for generated PDF reports."""

    __tablename__ = "pdf_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    report_type = Column(String(50), nullable=False)  # summary, full, wellness_plan
    file_size_bytes = Column(Integer, nullable=True)
    include_wellness_plan = Column(Boolean, default=True)
    include_charts = Column(Boolean, default=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="pdf_reports")
