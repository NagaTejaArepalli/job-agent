import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from config.settings import settings
from backend.database.models import Job, JobMatch, Company

class ReportingService:
    """
    Generates structured reports (Excel / CSV) summarizing discovered jobs,
    match scores, skills breakdown, and application statuses.
    """
    
    @classmethod
    def generate_excel_report(cls, jobs_data: List[Dict[str, Any]], filename: str = None) -> str:
        if not filename:
            filename = f"Job_Discovery_Report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
        file_path = settings.REPORTS_DIR / filename
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Discovered & Matched Jobs"
        
        # Styles
        header_fill = PatternFill(start_color="1F2937", end_color="1F2937", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        border = Border(
            left=Side(style='thin', color="E5E7EB"),
            right=Side(style='thin', color="E5E7EB"),
            top=Side(style='thin', color="E5E7EB"),
            bottom=Side(style='thin', color="E5E7EB")
        )
        
        headers = [
            "Company", "Job Title", "Location", "ATS Provider", "Match Score", 
            "Tech Score", "Key Matched Skills", "Missing Skills", "Application URL", "Status"
        ]
        ws.append(headers)
        
        for col_num, _ in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            
        for item in jobs_data:
            row = [
                item.get("company_name", ""),
                item.get("title", ""),
                item.get("location", ""),
                item.get("ats_provider", ""),
                f"{item.get('match_score', 0)}%",
                f"{item.get('tech_score', 0)}%",
                ", ".join(item.get("key_matches", [])),
                ", ".join(item.get("missing_skills", [])),
                item.get("url", ""),
                item.get("status", "new")
            ]
            ws.append(row)
            
        # Adjust column widths
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 50)
            
        wb.save(str(file_path))
        return str(file_path)
        
    @classmethod
    def generate_csv_report(cls, jobs_data: List[Dict[str, Any]], filename: str = None) -> str:
        if not filename:
            filename = f"Job_Discovery_Report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            
        file_path = settings.REPORTS_DIR / filename
        headers = [
            "company_name", "title", "location", "ats_provider", "match_score",
            "tech_score", "key_matches", "missing_skills", "url", "status"
        ]
        
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for item in jobs_data:
                writer.writerow({
                    "company_name": item.get("company_name", ""),
                    "title": item.get("title", ""),
                    "location": item.get("location", ""),
                    "ats_provider": item.get("ats_provider", ""),
                    "match_score": item.get("match_score", 0),
                    "tech_score": item.get("tech_score", 0),
                    "key_matches": "; ".join(item.get("key_matches", [])),
                    "missing_skills": "; ".join(item.get("missing_skills", [])),
                    "url": item.get("url", ""),
                    "status": item.get("status", "new")
                })
                
        return str(file_path)
