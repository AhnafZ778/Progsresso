"""
PDF report generation service
"""

from io import BytesIO
from datetime import date, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from services.progress_service import ProgressService
from services.task_service import TaskService


class PDFService:
    @staticmethod
    def generate_report(start_date=None, end_date=None, weeks=4):
        """Generate AI-ready PDF progress report"""
        summary = ProgressService.get_summary(weeks)

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch
        )
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=20,
            spaceAfter=12,
            textColor=colors.HexColor("#1f2937"),
        )

        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=14,
            spaceBefore=16,
            spaceAfter=8,
            textColor=colors.HexColor("#374151"),
        )

        body_style = ParagraphStyle(
            "CustomBody",
            parent=styles["Normal"],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.HexColor("#4b5563"),
        )

        story = []
        today = date.today()

        # Title
        story.append(Paragraph("📊 Habit Progress Report", title_style))
        story.append(
            Paragraph(
                f"Generated: {today.strftime('%B %d, %Y')} | Period: {summary['period_start']} to {summary['period_end']}",
                body_style,
            )
        )
        story.append(Spacer(1, 12))

        # User Context
        story.append(Paragraph("User Context", heading_style))
        story.append(
            Paragraph(
                f"I am tracking <b>{summary['total_tasks']}</b> habits/tasks using a weekly habit tracker. "
                f"This report covers <b>{weeks}</b> week(s) of data.",
                body_style,
            )
        )
        story.append(Spacer(1, 12))

        # Current Habit Overview Table
        story.append(Paragraph("Current Habit Overview", heading_style))

        table_data = [["Habit", "Metric", "Target", "This Week", "Avg Value", "Health"]]

        for task in summary["tasks"]:
            this_week_completed = (
                task["weekly_data"][0]["completed_days"] if task["weekly_data"] else 0
            )
            avg_value = task["average_value"]
            avg_str = f"{avg_value:.1f}" if avg_value else "N/A"
            health_pct = f"{task['health_score'] * 100:.0f}%"

            target_str = (
                f"{task['target_value']} {task['metric_unit'] or ''}"
                if task["target_value"]
                else "None"
            )
            metric_str = f"{task['metric_type']}: {task['metric_unit'] or 'Yes/No'}"

            table_data.append(
                [
                    task["name"][:25],
                    metric_str,
                    target_str,
                    f"{this_week_completed} days",
                    avg_str,
                    health_pct,
                ]
            )

        if len(table_data) > 1:
            table = Table(
                table_data,
                colWidths=[
                    1.5 * inch,
                    1.2 * inch,
                    0.9 * inch,
                    0.8 * inch,
                    0.7 * inch,
                    0.6 * inch,
                ],
            )
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 9),
                        ("FONTSIZE", (0, 1), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f9fafb")),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor("#f3f4f6")],
                        ),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                    ]
                )
            )
            story.append(table)

        story.append(Spacer(1, 16))

        # Performance Summary
        story.append(Paragraph("Performance Summary", heading_style))

        excelling = [t for t in summary["tasks"] if t["health_score"] >= 0.8]
        needs_attention = [t for t in summary["tasks"] if t["health_score"] < 0.5]

        if excelling:
            story.append(
                Paragraph("<b>🌟 Excelling (&gt;80% completion rate):</b>", body_style)
            )
            for task in excelling:
                story.append(
                    Paragraph(
                        f"• {task['name']}: {task['health_score'] * 100:.0f}% - Streak: {task['current_streak']} days",
                        body_style,
                    )
                )

        if needs_attention:
            story.append(
                Paragraph(
                    "<b>⚠️ Needs Attention (&lt;50% completion rate):</b>", body_style
                )
            )
            for task in needs_attention:
                story.append(
                    Paragraph(
                        f"• {task['name']}: {task['health_score'] * 100:.0f}%",
                        body_style,
                    )
                )

        if not excelling and not needs_attention:
            story.append(
                Paragraph(
                    "All habits are performing moderately (50-80% completion).",
                    body_style,
                )
            )

        story.append(Spacer(1, 16))

        # Patterns
        story.append(Paragraph("Patterns Identified", heading_style))

        if summary["tasks"]:
            best_streak = max(summary["tasks"], key=lambda t: t["current_streak"])
            story.append(
                Paragraph(
                    f"• Longest active streak: <b>{best_streak['name']}</b> - {best_streak['current_streak']} days",
                    body_style,
                )
            )

            if needs_attention:
                at_risk = ", ".join([t["name"] for t in needs_attention[:3]])
                story.append(
                    Paragraph(f"• Current at-risk habits: {at_risk}", body_style)
                )

        story.append(Spacer(1, 16))

        # AI Request
        story.append(Paragraph("Request for AI Guidance", heading_style))
        story.append(
            Paragraph(
                "Based on the above data, I am looking for:<br/>"
                "1. Strategies to improve consistency with my struggling habits<br/>"
                "2. Insights into why certain patterns might be occurring<br/>"
                "3. Suggestions for adjusting my targets if they seem unrealistic<br/>"
                "4. Motivational support and actionable next steps<br/><br/>"
                "<b>Please analyze my progress and provide personalized recommendations.</b>",
                body_style,
            )
        )

        doc.build(story)
        buffer.seek(0)
        return buffer
