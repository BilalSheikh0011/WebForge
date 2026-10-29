import io, base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(run_data: dict, project_name: str, tc_name: str) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    # Title & Metadata
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#0f172a'))
    story.append(Paragraph(f"WebForge Test Execution Report", title_style))
    story.append(Spacer(1, 8))

    meta_text = f"<b>Project:</b> {project_name} | <b>Test Case:</b> {tc_name} | <b>Verdict:</b> {run_data['status']} | <b>Duration:</b> {run_data['duration_ms']}ms"
    story.append(Paragraph(meta_text, styles['Normal']))
    story.append(Spacer(1, 14))

    # Step Results Table
    table_data = [["#", "Action", "Expected", "Actual", "Status", "Duration"]]
    for s in run_data.get("step_results", []):
        table_data.append([
            str(s.get("index")),
            s.get("action", ""),
            s.get("expected", "-") or "-",
            (s.get("error") or s.get("actual") or "-")[:35],
            s.get("status", ""),
            f"{s.get('ms', 0)}ms"
        ])

    t = Table(table_data, colWidths=[25, 80, 120, 160, 60, 55])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 16))

    # Embed Screenshots for Failures
    for s in run_data.get("step_results", []):
        if s.get("screenshot_b64"):
            story.append(Paragraph(f"<b>Evidence for Failed Step {s.get('index')} ({s.get('action')})</b>", styles['Heading3']))
            img_data = base64.b64decode(s["screenshot_b64"])
            img_stream = io.BytesIO(img_data)
            img = RLImage(img_stream, width=420, height=220)
            story.append(img)
            story.append(Spacer(1, 10))

    doc.build(story)
    buffer.seek(0)
    return buffer