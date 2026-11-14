import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

def generate_html_email_report(candidate_name: str, jobs: List[Dict[str, Any]], date_str: str) -> str:
    """Generates a mobile-friendly, beautiful HTML email summary of daily matched jobs."""
    jobs_rows_html = ""
    for j in jobs[:10]: # Top 10 matches
        score = round(float(j.get("match_score", 0)))
        score_color = "#10b981" if score >= 80 else "#3b82f6"
        matched_skills_pills = "".join([
            f'<span style="display:inline-block;background-color:#064e3b;color:#a7f3d0;font-size:10px;padding:2px 8px;border-radius:12px;margin:2px;font-family:monospace;">✓ {sk}</span>'
            for sk in j.get("key_matches", [])[:5]
        ])
        
        jobs_rows_html += f"""
        <div style="background-color:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:16px;margin-bottom:14px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span style="color:#60a5fa;font-size:12px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;">{j.get('company_name', 'Company')}</span>
                <span style="background-color:#1e293b;color:{score_color};font-size:13px;font-weight:bold;padding:3px 10px;border-radius:8px;border:1px solid #334155;">{score}% Match</span>
            </div>
            <h3 style="color:#f8fafc;font-size:15px;margin:0 0 6px 0;font-family:sans-serif;">{j.get('title', 'SDET Opening')}</h3>
            <p style="color:#94a3b8;font-size:12px;margin:0 0 10px 0;">📍 {j.get('location', 'Bangalore, India')} • Source: {j.get('ats_provider', 'Official Career Portal')}</p>
            <div style="margin-bottom:12px;">{matched_skills_pills}</div>
            <div style="text-align:right;">
                <a href="{j.get('url', '#')}" target="_blank" style="display:inline-block;background-color:#2563eb;color:#ffffff;text-decoration:none;font-size:12px;font-weight:bold;padding:8px 16px;border-radius:8px;">View & Apply on Career Site →</a>
            </div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily Job Discovery Report</title>
    </head>
    <body style="background-color:#020617;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;margin:0;padding:20px;color:#f8fafc;">
        <div style="max-width:600px;margin:0 auto;background-color:#0b0f19;border:1px solid #1e293b;border-radius:16px;overflow:hidden;box-shadow:0 10px 25px rgba(0,0,0,0.5);">
            
            <!-- Header -->
            <div style="background:linear-gradient(135deg,#1e3a8a,#312e81);padding:24px;text-align:left;">
                <span style="background-color:rgba(255,255,255,0.1);color:#93c5fd;font-size:11px;font-weight:bold;padding:4px 10px;border-radius:12px;text-transform:uppercase;letter-spacing:1px;">Automated Cloud Discovery</span>
                <h1 style="color:#ffffff;font-size:20px;margin:10px 0 4px 0;">Everyday Job Discovery Report</h1>
                <p style="color:#bfdbfe;font-size:12px;margin:0;">Profile: <strong>{candidate_name}</strong> • Location: <strong>India Only</strong></p>
                <p style="color:#94a3b8;font-size:11px;margin-top:4px;">Date: {date_str} • 148 Target Career Sites Scanned</p>
            </div>

            <!-- Content -->
            <div style="padding:20px;">
                <p style="color:#cbd5e1;font-size:13px;line-height:1.5;margin-bottom:18px;">
                    Here are your top-matched SDET and Test Automation opportunities discovered across your official target company career sites in India.
                </p>

                {jobs_rows_html}

                <!-- Footer Summary -->
                <div style="background-color:#0f172a;border-radius:10px;padding:14px;margin-top:20px;border:1px dashed #334155;text-align:center;">
                    <p style="color:#94a3b8;font-size:11px;margin:0;">
                        Attached is your complete <strong>Job_Discovery_Report.xlsx</strong>.<br>
                        Infor & Accenture are strictly excluded from applications.
                    </p>
                </div>
            </div>

            <div style="background-color:#020617;padding:14px;text-align:center;font-size:10px;color:#64748b;border-top:1px solid #1e293b;">
                AI Job Search & Application Agent • Automated GitHub Actions Cloud Pipeline
            </div>
        </div>
    </body>
    </html>
    """
    return html

def send_email_alert(
    candidate_name: str,
    recipient_email: str,
    jobs_data: List[Dict[str, Any]],
    excel_attachment_path: Optional[str] = None
) -> bool:
    """
    Sends an email with the HTML summary and attached Excel report.
    Uses SMTP credentials from environment variables:
    SMTP_HOST (default: smtp.gmail.com)
    SMTP_PORT (default: 587)
    SMTP_USER
    SMTP_PASS
    """
    smtp_user = (os.getenv("SMTP_USER") or "").strip()
    smtp_pass = (os.getenv("SMTP_PASS") or "").strip()
    smtp_host = (os.getenv("SMTP_HOST") or "smtp.gmail.com").strip()
    smtp_port_raw = os.getenv("SMTP_PORT") or "587"
    smtp_port = int(smtp_port_raw) if smtp_port_raw.isdigit() else 587
    recipient_email = (recipient_email or os.getenv("ALERT_EMAIL_TO") or "naga.teja.are@gmail.com").strip()
    
    if not smtp_user or not smtp_pass:
        print("[EmailService] SMTP credentials not configured (SMTP_USER or SMTP_PASS missing). Skipping email.")
        return False
        
    date_str = datetime.now().strftime("%d %b %Y")
    subject = f"🎯 Daily SDET Job Matches ({len(jobs_data)} Openings) - {date_str}"
    
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = f"AI Job Agent <{smtp_user}>"
    msg["To"] = recipient_email
    
    # HTML body
    html_content = generate_html_email_report(candidate_name, jobs_data, date_str)
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    
    # Attach Excel file if present
    if excel_attachment_path and os.path.exists(excel_attachment_path):
        part = MIMEBase("application", "octet-stream")
        with open(excel_attachment_path, "rb") as f:
            part.set_payload(f.read())
        encoders.encode_base64(part)
        filename = Path(excel_attachment_path).name
        part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
        msg.attach(part)
        
    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, [recipient_email], msg.as_string())
        server.quit()
        print(f"[EmailService] Successfully sent daily report email to {recipient_email}!")
        return True
    except Exception as e:
        print(f"[EmailService] Failed to send email alert: {e}")
        return False
