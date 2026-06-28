"""Email helpers — session link, hot lead alert, retry."""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.logger import log


def _smtp_send(to: str, subject: str, body_html: str):
    user = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_PASSWORD")
    if not user or not password:
        log("EMAIL_ERROR: GMAIL_USER or GMAIL_PASSWORD not set in .env", level="ERROR")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(user, password)
            server.sendmail(user, to, msg.as_string())
        log(f"Email sent → {to} | {subject}")
    except Exception as e:
        log(f"EMAIL_ERROR: {e}", level="ERROR")


def send_session_email(lead_id: str, email: str, name: str):
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    session_url = f"{base_url}/session/{lead_id}"
    subject = "Your ASE Qualification Session Link"
    body = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px;">
      <h2 style="color:#1a73e8;">Hi {name},</h2>
      <p>Thank you for your interest! We'd like to learn more about your requirements in a quick voice session.</p>
      <p>Please click the button below to begin your 5-minute session:</p>
      <p style="text-align:center;margin:30px 0;">
        <a href="{session_url}"
           style="background:#1a73e8;color:#fff;padding:14px 28px;border-radius:6px;
                  text-decoration:none;font-size:16px;font-weight:bold;">
          Start Session
        </a>
      </p>
      <p style="color:#666;font-size:13px;">Or copy this link: <code>{session_url}</code></p>
      <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
      <p style="color:#888;font-size:12px;">ASE Lead Qualification Pipeline</p>
    </div>
    """
    _smtp_send(email, subject, body)


def send_rep_email(lead_data: dict):
    rep_email = os.getenv("GMAIL_TO")
    if not rep_email:
        log("EMAIL_ERROR: GMAIL_TO not set — skipping rep alert", level="WARNING")
        return
    name = lead_data.get("full_name", "Unknown")
    company = lead_data.get("company_name", "Unknown")
    score = lead_data.get("lead_score", "N/A")
    subject = f"🔥 Hot Lead Alert — {name} from {company} (Score: {score})"
    body = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px;">
      <h2 style="color:#e53935;">🔥 Hot Lead — Immediate Follow-Up Required</h2>
      <table style="width:100%;border-collapse:collapse;">
        <tr><td style="padding:8px;font-weight:bold;width:40%;">Name</td><td style="padding:8px;">{name}</td></tr>
        <tr style="background:#f5f5f5;"><td style="padding:8px;font-weight:bold;">Email</td><td style="padding:8px;">{lead_data.get("email","")}</td></tr>
        <tr><td style="padding:8px;font-weight:bold;">Phone</td><td style="padding:8px;">{lead_data.get("phone","")}</td></tr>
        <tr style="background:#f5f5f5;"><td style="padding:8px;font-weight:bold;">Company</td><td style="padding:8px;">{company}</td></tr>
        <tr><td style="padding:8px;font-weight:bold;">Service Interest</td><td style="padding:8px;">{lead_data.get("service_interest","")}</td></tr>
        <tr style="background:#f5f5f5;"><td style="padding:8px;font-weight:bold;">Budget</td><td style="padding:8px;">{lead_data.get("budget_category","")}</td></tr>
        <tr><td style="padding:8px;font-weight:bold;">Timeline</td><td style="padding:8px;">{lead_data.get("q6_timeline","")}</td></tr>
        <tr style="background:#f5f5f5;"><td style="padding:8px;font-weight:bold;">Lead Score</td>
          <td style="padding:8px;color:#e53935;font-weight:bold;">{score}/100</td></tr>
        <tr><td style="padding:8px;font-weight:bold;">Key Insights</td><td style="padding:8px;">{lead_data.get("key_insights","")}</td></tr>
        <tr style="background:#f5f5f5;"><td style="padding:8px;font-weight:bold;">Next Action</td><td style="padding:8px;">{lead_data.get("next_action","")}</td></tr>
      </table>
      <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
      <p style="color:#888;font-size:12px;">ASE Lead Qualification Pipeline — Auto Alert</p>
    </div>
    """
    _smtp_send(rep_email, subject, body)


def send_retry_email(lead_id: str, email: str, name: str):
    """Re-send the session link with a follow-up message."""
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    session_url = f"{base_url}/session/{lead_id}"
    subject = "Following Up — Your ASE Session Link"
    body = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px;">
      <h2 style="color:#1a73e8;">Hi {name},</h2>
      <p>We noticed you haven't completed your qualification session yet. No worries — here's the link again:</p>
      <p style="text-align:center;margin:30px 0;">
        <a href="{session_url}"
           style="background:#1a73e8;color:#fff;padding:14px 28px;border-radius:6px;
                  text-decoration:none;font-size:16px;font-weight:bold;">
          Start Session Now
        </a>
      </p>
      <p style="color:#666;font-size:13px;">Link: <code>{session_url}</code></p>
      <p>The session takes about 5 minutes and helps us prepare the best solution for you.</p>
      <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
      <p style="color:#888;font-size:12px;">ASE Lead Qualification Pipeline</p>
    </div>
    """
    _smtp_send(email, subject, body)
