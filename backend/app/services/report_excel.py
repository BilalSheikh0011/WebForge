import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

def generate_excel_report(run_data: dict, project_name: str, tc_name: str) -> io.BytesIO:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Execution Log"

    # Header Meta
    ws.append(["WebForge Execution Summary"])
    ws.append(["Project", project_name, "Test Case", tc_name])
    ws.append(["Status", run_data["status"], "Duration", f"{run_data['duration_ms']}ms"])
    ws.append([])

    # Table Header
    headers = ["Step #", "Action", "Expected", "Actual", "Status", "Duration (ms)", "Error"]
    ws.append(headers)

    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=5, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font

    for s in run_data.get("step_results", []):
        ws.append([
            s.get("index"),
            s.get("action"),
            s.get("expected") or "",
            s.get("actual") or "",
            s.get("status"),
            s.get("ms"),
            s.get("error") or ""
        ])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer