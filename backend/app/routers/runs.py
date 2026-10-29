import base64
import io
import time
from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import TestCase
from ..services.executor import execute_case

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import openpyxl

router = APIRouter(prefix="/runs", tags=["Test Runs"])

LATEST_RUNS = {}

class StepItem(BaseModel):
    order: Optional[int] = 1
    action: str
    selector_type: Optional[str] = ""
    selector: Optional[str] = ""
    value: Optional[str] = ""
    expected: Optional[str] = ""

class TestCasePayload(BaseModel):
    id: Optional[str] = "TC-001"
    name: Optional[str] = "Unnamed Test"
    precondition: Optional[str] = ""
    priority: Optional[str] = "Critical"
    test_type: Optional[str] = "Functional"
    feature: Optional[str] = ""
    steps: List[StepItem] = []

class FlexibleExecutePayload(BaseModel):
    test_case_id: Optional[int] = 1
    base_url: Optional[str] = "https://leatherlaneatelier.store"
    stop_on_fail: Optional[bool] = True
    steps: Optional[List[StepItem]] = None
    test_case: Optional[TestCasePayload] = None

@router.post("/execute")
def execute_test(payload: FlexibleExecutePayload, db: Session = Depends(get_db)):
    raw_steps = []
    if payload.test_case and payload.test_case.steps:
        raw_steps = payload.test_case.steps
    elif payload.steps:
        raw_steps = payload.steps
    else:
        raise HTTPException(status_code=400, detail="No steps provided for execution.")

    formatted_steps = [
        s.model_dump() if hasattr(s, "model_dump") else s.dict() 
        for s in raw_steps
    ]

    base_url = payload.base_url or "https://leatherlaneatelier.store"
    
    tc = db.query(TestCase).filter(TestCase.id == payload.test_case_id).first()
    baseline = getattr(tc, "baseline_screenshot_b64", None) if tc else None

    results, final_screenshot, console_logs, network_fails = execute_case(
        steps=formatted_steps,
        base_url=base_url,
        baseline_screenshot=baseline,
        stop_on_fail=payload.stop_on_fail if payload.stop_on_fail is not None else True
    )

    if final_screenshot and tc and hasattr(tc, "baseline_screenshot_b64") and not tc.baseline_screenshot_b64:
        tc.baseline_screenshot_b64 = final_screenshot
        db.commit()

    is_fail = any(r.get("status") == "FAIL" for r in results)
    is_flaky = any(r.get("status") == "FLAKY" for r in results)
    duration = sum(r.get("ms", 0) for r in results)
    run_id = int(time.time())

    overall_status = "FAIL" if is_fail else ("FLAKY" if is_flaky else "PASS")

    run_record = {
        "run_id": run_id,
        "status": overall_status,
        "overall_status": overall_status,
        "duration_ms": duration,
        "final_screenshot": final_screenshot,
        "step_results": results,
        "console_logs": console_logs,
        "network_failures": network_fails
    }
    LATEST_RUNS[run_id] = run_record

    return run_record

@router.get("/{run_id}")
def get_run_details(run_id: int):
    run = LATEST_RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run results not found")
    return run

@router.get("/{run_id}/report.pdf")
def export_pdf(run_id: int):
    run = LATEST_RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run results not found")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor("#0f172a"))
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor("#1e293b"))
    diag_title = ParagraphStyle('DiagTitle', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold', textColor=colors.HexColor("#b91c1c"))
    diag_body = ParagraphStyle('DiagBody', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor("#334155"), leading=11)
    sug_title = ParagraphStyle('SugTitle', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold', textColor=colors.HexColor("#047857"))
    sug_body = ParagraphStyle('SugBody', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor("#065f46"), leading=11)

    story.append(Paragraph("WebForge QA Test Execution Report", title_style))
    story.append(Spacer(1, 8))

    status_color = "#10b981" if run['status'] == "PASS" else ("#f59e0b" if run['status'] == "FLAKY" else "#ef4444")
    meta_text = (
        f"<b>Status:</b> <font color='{status_color}'><b>{run['status']}</b></font> &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Duration:</b> {run['duration_ms']}ms &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Run Reference:</b> #{run_id}"
    )
    story.append(Paragraph(meta_text, styles['Normal']))
    story.append(Spacer(1, 14))

    table_data = [["#", "Action", "Status", "Duration", "Healed / Flaky", "Output / Error Summary"]]
    for s in run["step_results"]:
        status_label = s["status"]
        healed_flaky_text = "Flaky (Retried)" if s.get("status") == "FLAKY" else ("YES" if s.get("healed") else "No")
        table_data.append([
            str(s["index"]),
            s["action"],
            status_label,
            f"{s.get('ms', 0)}ms",
            healed_flaky_text,
            (s.get("error") or s.get("actual") or "")[:40]
        ])

    t = Table(table_data, colWidths=[24, 75, 55, 55, 75, 256])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t)
    story.append(Spacer(1, 18))

    failed_steps = [s for s in run["step_results"] if s.get("status") == "FAIL"]
    if failed_steps:
        story.append(Paragraph("<b>Root Cause Diagnostics & Remediation Advice</b>", h2_style))
        story.append(Spacer(1, 8))

        for fs in failed_steps:
            diag_elements = [
                Paragraph(f"<b>Failed Step #{fs['index']} ({fs['action'].upper()})</b>", styles['Normal']),
                Spacer(1, 4),
                Paragraph("<b>Why the test failed (Root Cause):</b>", diag_title),
                Paragraph(fs.get("explanation") or "Element assertion or interaction failed.", diag_body),
                Spacer(1, 6),
                Paragraph("<b>How to make it better (Recommended Fix):</b>", sug_title),
                Paragraph(fs.get("suggestion") or "Review DOM selector and wait times.", sug_body),
                Spacer(1, 10)
            ]

            if fs.get("screenshot_b64"):
                diag_elements.append(Paragraph("<b>Failure Screenshot Proof:</b>", styles['Normal']))
                diag_elements.append(Spacer(1, 4))
                try:
                    img_data = base64.b64decode(fs["screenshot_b64"])
                    img = RLImage(io.BytesIO(img_data), width=380, height=220)
                    diag_elements.append(img)
                    diag_elements.append(Spacer(1, 12))
                except Exception:
                    pass

            story.append(KeepTogether(diag_elements))

    doc.build(story)
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=WebForge_Report_{run_id}.pdf"}
    )

@router.get("/{run_id}/report.xlsx")
def export_excel(run_id: int):
    run = LATEST_RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run results not found")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "QA Execution & Diagnostics"

    headers = [
        "Step #", "Action", "Status", "Duration (ms)", 
        "Self-Healed / Flaky", "Actual Output / Error", 
        "Why It Failed (Root Cause Analysis)", "How To Make It Better (Remediation Advice)"
    ]
    ws.append(headers)

    for col_num, cell in enumerate(ws[1], 1):
        cell.font = openpyxl.styles.Font(bold=True, color="FFFFFF")
        cell.fill = openpyxl.styles.PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")

    for s in run["step_results"]:
        status = s["status"]
        healed_flaky_text = "Flaky (Retried)" if status == "FLAKY" else ("Yes" if s.get("healed") else "No")
        ws.append([
            s["index"],
            s["action"],
            status,
            s.get("ms", 0),
            healed_flaky_text,
            s.get("error") or s.get("actual", ""),
            s.get("explanation") if status == "FAIL" else "N/A - Step Passed",
            s.get("suggestion") if status == "FAIL" else "N/A - Step Passed"
        ])

    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = min(max(max_len + 2, 12), 50)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    return Response(
        content=stream.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=WebForge_Report_{run_id}.xlsx"}
    )