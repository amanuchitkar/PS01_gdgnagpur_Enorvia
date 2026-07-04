"""PDF Report Generation Service.

Generates professional, shareable wellness reports using ReportLab.
"""
import io
import os
import logging
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    HRFlowable,
    ListFlowable,
    ListItem,
)
from reportlab.graphics.shapes import Drawing, Rect, String, Circle
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgets.markers import makeMarker

logger = logging.getLogger(__name__)

# Color palette
BRAND_GREEN = colors.HexColor("#22c55e")
BRAND_BLUE = colors.HexColor("#0ea5e9")
BRAND_ORANGE = colors.HexColor("#f97316")
BRAND_DARK = colors.HexColor("#1f2937")
BRAND_GRAY = colors.HexColor("#6b7280")
BRAND_LIGHT = colors.HexColor("#f9fafb")
RISK_COLORS = {
    "low": colors.HexColor("#22c55e"),
    "moderate": colors.HexColor("#f59e0b"),
    "high": colors.HexColor("#ef4444"),
}

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def _get_styles():
    """Create custom paragraph styles for the report."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=24,
        textColor=BRAND_DARK,
        spaceAfter=6,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=BRAND_GRAY,
        spaceAfter=20,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=BRAND_DARK,
        spaceBefore=16,
        spaceAfter=8,
        borderPadding=(0, 0, 4, 0),
    ))
    styles.add(ParagraphStyle(
        "KBodyText",
        parent=styles["Normal"],
        fontSize=10,
        textColor=BRAND_DARK,
        leading=14,
        alignment=TA_JUSTIFY,
    ))
    styles.add(ParagraphStyle(
        "SmallText",
        parent=styles["Normal"],
        fontSize=8,
        textColor=BRAND_GRAY,
        leading=11,
    ))
    styles.add(ParagraphStyle(
        "MetricValue",
        parent=styles["Normal"],
        fontSize=18,
        textColor=BRAND_DARK,
        alignment=TA_CENTER,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        "MetricLabel",
        parent=styles["Normal"],
        fontSize=8,
        textColor=BRAND_GRAY,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "PlanDay",
        parent=styles["Heading3"],
        fontSize=11,
        textColor=BRAND_GREEN,
        spaceBefore=10,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        "ActivityText",
        parent=styles["Normal"],
        fontSize=9,
        textColor=BRAND_DARK,
        leading=12,
        leftIndent=12,
    ))
    styles.add(ParagraphStyle(
        "ReasonText",
        parent=styles["Normal"],
        fontSize=8,
        textColor=BRAND_BLUE,
        leading=11,
        leftIndent=12,
        fontName="Helvetica-Oblique",
    ))
    return styles


class PDFReportService:
    """Generates professional PDF wellness reports."""

    def generate_report(self, dashboard_data: dict) -> tuple[bytes, str]:
        """Generate a PDF report and return (pdf_bytes, filename)."""
        buffer = io.BytesIO()
        styles = _get_styles()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        elements = []

        # Title page
        elements.extend(self._build_title_section(dashboard_data, styles))
        elements.append(Spacer(1, 12))

        # Key Metrics
        elements.extend(self._build_metrics_section(dashboard_data, styles))
        elements.append(Spacer(1, 12))

        # Conversation Summary
        elements.extend(self._build_summary_section(dashboard_data, styles))

        # Emotional Analysis
        elements.extend(self._build_emotion_section(dashboard_data, styles))

        # Stress Timeline
        elements.extend(self._build_stress_section(dashboard_data, styles))

        # AI Observations
        elements.extend(self._build_observations_section(dashboard_data, styles))

        # Detected Concerns
        elements.extend(self._build_concerns_section(dashboard_data, styles))

        # Wellness Plan
        if dashboard_data.get("wellness_plan"):
            elements.append(PageBreak())
            elements.extend(self._build_wellness_plan_section(dashboard_data, styles))

        # Disclaimer
        elements.append(Spacer(1, 24))
        elements.extend(self._build_disclaimer(styles))

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"kindered_wellness_report_{timestamp}.pdf"

        return pdf_bytes, filename

    def save_report(self, pdf_bytes: bytes, filename: str) -> str:
        """Save PDF to disk and return file path."""
        file_path = os.path.join(REPORTS_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)
        return file_path

    def _build_title_section(self, data: dict, styles) -> list:
        """Build the report header."""
        elements = []
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Kindered", styles["ReportTitle"]))
        elements.append(Paragraph("Emotional Wellness Report", styles["ReportSubtitle"]))

        date_str = ""
        if data.get("created_at"):
            try:
                dt = datetime.fromisoformat(data["created_at"])
                date_str = dt.strftime("%B %d, %Y at %I:%M %p")
            except (ValueError, TypeError):
                date_str = data["created_at"]
        elements.append(Paragraph(f"Generated: {date_str or 'Today'}", styles["SmallText"]))
        elements.append(Spacer(1, 8))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb")))
        return elements

    def _build_metrics_section(self, data: dict, styles) -> list:
        """Build the key metrics overview."""
        elements = []
        elements.append(Paragraph("Session Overview", styles["SectionHeader"]))

        stress = data.get("average_stress", 0)
        risk = data.get("risk_level", "low")
        emotion = data.get("dominant_emotion", "neutral")
        messages = data.get("message_count", 0)

        # Calculate wellness score (inverse of stress + risk modifier)
        risk_modifier = {"low": 0, "moderate": -10, "high": -25}.get(risk, 0)
        wellness_score = max(0, min(100, 100 - int(stress) + risk_modifier))

        table_data = [[
            Paragraph(f"<b>{emotion.capitalize()}</b>", styles["MetricValue"]),
            Paragraph(f"<b>{int(stress)}/100</b>", styles["MetricValue"]),
            Paragraph(f"<b>{risk.capitalize()}</b>", styles["MetricValue"]),
            Paragraph(f"<b>{wellness_score}/100</b>", styles["MetricValue"]),
            Paragraph(f"<b>{messages}</b>", styles["MetricValue"]),
        ], [
            Paragraph("Dominant Emotion", styles["MetricLabel"]),
            Paragraph("Avg Stress", styles["MetricLabel"]),
            Paragraph("Risk Level", styles["MetricLabel"]),
            Paragraph("Wellness Score", styles["MetricLabel"]),
            Paragraph("Messages", styles["MetricLabel"]),
        ]]

        col_width = (A4[0] - 40 * mm) / 5
        table = Table(table_data, colWidths=[col_width] * 5)
        table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND", (0, 0), (-1, -1), BRAND_LIGHT),
            ("ROUNDEDCORNERS", [6, 6, 6, 6]),
            ("TOPPADDING", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, -1), (-1, -1), 12),
        ]))
        elements.append(table)
        return elements

    def _build_summary_section(self, data: dict, styles) -> list:
        """Build the conversation summary section."""
        elements = []
        elements.append(Paragraph("Conversation Summary", styles["SectionHeader"]))
        summary = data.get("summary", "No summary available.")
        elements.append(Paragraph(summary, styles["KBodyText"]))
        return elements

    def _build_emotion_section(self, data: dict, styles) -> list:
        """Build the emotional analysis with pie chart."""
        elements = []
        elements.append(Paragraph("Emotional Analysis", styles["SectionHeader"]))

        emotion_freq = data.get("emotion_frequency", {})
        if not emotion_freq:
            elements.append(Paragraph("No emotional data recorded.", styles["KBodyText"]))
            return elements

        # Emotion frequency table
        table_data = [["Emotion", "Frequency", "Percentage"]]
        total = sum(emotion_freq.values())
        for emotion, count in sorted(emotion_freq.items(), key=lambda x: -x[1]):
            pct = (count / total * 100) if total > 0 else 0
            table_data.append([emotion.capitalize(), str(count), f"{pct:.0f}%"])

        table = Table(table_data, colWidths=[80 * mm, 40 * mm, 40 * mm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_GREEN),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)
        return elements

    def _build_stress_section(self, data: dict, styles) -> list:
        """Build stress timeline section."""
        elements = []
        elements.append(Paragraph("Stress Trend", styles["SectionHeader"]))

        stress_scores = data.get("stress_scores", [])
        timeline = data.get("timeline", [])

        if not stress_scores:
            elements.append(Paragraph("No stress data recorded.", styles["KBodyText"]))
            return elements

        # Stress statistics
        avg = sum(stress_scores) / len(stress_scores)
        peak = max(stress_scores)
        low = min(stress_scores)

        stats_text = (
            f"Average: <b>{avg:.0f}/100</b> | "
            f"Peak: <b>{peak}/100</b> | "
            f"Lowest: <b>{low}/100</b> | "
            f"Data Points: <b>{len(stress_scores)}</b>"
        )
        elements.append(Paragraph(stats_text, styles["KBodyText"]))
        elements.append(Spacer(1, 6))

        # Stress values per message table
        if timeline:
            table_data = [["Message #", "Emotion", "Stress Score"]]
            for i, entry in enumerate(timeline, 1):
                table_data.append([
                    str(i),
                    entry.get("emotion", "—").capitalize(),
                    str(entry.get("stress_score", "—")),
                ])

            table = Table(table_data, colWidths=[30 * mm, 60 * mm, 40 * mm])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), BRAND_BLUE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (2, 0), (2, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            elements.append(table)

        return elements

    def _build_observations_section(self, data: dict, styles) -> list:
        """Build AI observations section."""
        elements = []
        observations = data.get("observations", [])
        if not observations:
            return elements

        elements.append(Paragraph("AI Observations", styles["SectionHeader"]))

        for obs in observations:
            severity_icon = {"info": "\u2139\ufe0f", "warning": "\u26a0\ufe0f", "critical": "\u274c"}.get(
                obs.get("severity", "info"), "\u2022"
            )
            obs_type = obs.get("type", "observation").capitalize()
            content = obs.get("content", "")
            recurring = " (Recurring Pattern)" if obs.get("is_recurring") else ""

            elements.append(Paragraph(
                f"<b>{obs_type}{recurring}:</b> {content}",
                styles["KBodyText"],
            ))
            elements.append(Spacer(1, 4))

        return elements

    def _build_concerns_section(self, data: dict, styles) -> list:
        """Build detected concerns section."""
        elements = []
        concerns = data.get("concerns", [])
        if not concerns:
            return elements

        elements.append(Paragraph("Recurring Concerns", styles["SectionHeader"]))
        items = [ListItem(Paragraph(c.capitalize(), styles["KBodyText"])) for c in concerns]
        elements.append(ListFlowable(items, bulletType="bullet", start=""))
        return elements

    def _build_wellness_plan_section(self, data: dict, styles) -> list:
        """Build the 7-day wellness plan section."""
        elements = []
        plan = data.get("wellness_plan", {})
        if not plan:
            return elements

        elements.append(Paragraph("Personalized 7-Day Wellness Plan", styles["SectionHeader"]))

        # Overall assessment
        assessment = plan.get("overall_assessment", "")
        if assessment:
            elements.append(Paragraph(assessment, styles["KBodyText"]))
            elements.append(Spacer(1, 10))

        # Days
        days = plan.get("days", [])
        for day in days:
            day_num = day.get("day", "?")
            theme = day.get("theme", "")
            elements.append(Paragraph(f"Day {day_num}: {theme}", styles["PlanDay"]))

            activities = day.get("activities", [])
            for act in activities:
                time_slot = act.get("time", "").capitalize()
                activity_name = act.get("activity", "")
                duration = act.get("duration", "")
                description = act.get("description", "")
                reason = act.get("reason", "")

                elements.append(Paragraph(
                    f"<b>{time_slot}</b> — {activity_name} ({duration})",
                    styles["ActivityText"],
                ))
                if description:
                    elements.append(Paragraph(description, styles["ActivityText"]))
                if reason:
                    elements.append(Paragraph(f"Why: {reason}", styles["ReasonText"]))
                elements.append(Spacer(1, 3))

        # Recurring habits
        habits = plan.get("recurring_habits", [])
        if habits:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("Recommended Recurring Habits", styles["SectionHeader"]))
            for habit in habits:
                name = habit.get("habit", "")
                freq = habit.get("frequency", "")
                reason = habit.get("reason", "")
                elements.append(Paragraph(
                    f"<b>{name}</b> ({freq})", styles["KBodyText"]
                ))
                if reason:
                    elements.append(Paragraph(f"Why: {reason}", styles["ReasonText"]))
                elements.append(Spacer(1, 4))

        # Important reminders
        reminders = plan.get("important_reminders", [])
        if reminders:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("Important Reminders", styles["SectionHeader"]))
            items = [ListItem(Paragraph(r, styles["KBodyText"])) for r in reminders]
            elements.append(ListFlowable(items, bulletType="bullet", start=""))

        return elements

    def _build_disclaimer(self, styles) -> list:
        """Build the professional disclaimer section."""
        elements = []
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb")))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(
            "<b>Disclaimer:</b> This report is generated by Kindered, an AI-powered emotional wellness "
            "support tool. It is intended to support self-awareness and is <b>not a substitute for "
            "professional mental health diagnosis, treatment, or advice</b>. If you choose to share "
            "this report with a licensed mental health professional, it can serve as supplementary "
            "information about your self-reported emotional patterns. Always consult a qualified "
            "healthcare provider for medical or mental health concerns.",
            styles["SmallText"],
        ))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(
            f"Report generated on {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')} by Kindered v1.0",
            styles["SmallText"],
        ))
        return elements


pdf_service = PDFReportService()
