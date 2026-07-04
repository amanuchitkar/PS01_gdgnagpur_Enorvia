"""Initial schema - conversations, messages, observations, wellness plans, PDF reports

Revision ID: 001_initial
Revises: None
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Conversations table
    op.create_table(
        "conversations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("dominant_emotion", sa.String(50), nullable=True),
        sa.Column("average_stress", sa.Float(), nullable=True),
        sa.Column("risk_level", sa.String(20), nullable=True),
    )

    # Messages table
    op.create_table(
        "messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.String(36),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("emotion", sa.String(50), nullable=True),
        sa.Column("sentiment", sa.String(20), nullable=True),
        sa.Column("stress_score", sa.Integer(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("risk_level", sa.String(20), nullable=True),
        sa.Column("emotional_summary", sa.Text(), nullable=True),
        sa.Column("detected_concerns", sa.JSON(), nullable=True),
        sa.Column("suggested_next_action", sa.String(255), nullable=True),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])

    # AI Observations table
    op.create_table(
        "ai_observations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.String(36),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("observation_type", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(20), nullable=True),
        sa.Column("related_emotions", sa.JSON(), nullable=True),
        sa.Column("is_recurring", sa.Boolean(), server_default="0"),
    )
    op.create_index("ix_observations_conversation_id", "ai_observations", ["conversation_id"])

    # Wellness Plans table
    op.create_table(
        "wellness_plans",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.String(36),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("plan_data", sa.JSON(), nullable=False),
    )

    # PDF Reports table
    op.create_table(
        "pdf_reports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.String(36),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(512), nullable=False),
        sa.Column("report_type", sa.String(50), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("include_wellness_plan", sa.Boolean(), server_default="1"),
        sa.Column("include_charts", sa.Boolean(), server_default="1"),
    )
    op.create_index("ix_pdf_reports_conversation_id", "pdf_reports", ["conversation_id"])


def downgrade() -> None:
    op.drop_table("pdf_reports")
    op.drop_table("wellness_plans")
    op.drop_table("ai_observations")
    op.drop_table("messages")
    op.drop_table("conversations")
