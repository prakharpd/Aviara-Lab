"""CSV helpers — init, read, write, update for the 35-column leads store."""
import csv
import os
import uuid
from datetime import datetime
from utils.logger import log

CSV_FILE = "data/leads.csv"

COLUMNS = [
    # Phase 1 — intake
    "lead_id", "full_name", "email", "phone", "company_name",
    "company_website", "service_interest", "brief_description",
    "submission_time", "is_duplicate", "call_status", "session_url",
    # Phase 2 — voice session
    "q1_industry", "q2_pain_points", "q3_current_tools",
    "q4_expected_outcome", "q5_budget_range", "q6_timeline",
    "q7_decision_maker", "q8_wants_callback",
    "session_start", "session_end", "transcript_path",
    # Phase 3 — agent analysis
    "discovery_summary", "discovery_flags",
    "budget_category", "budget_confidence",
    "sentiment_score", "sentiment_label",
    "lead_score", "recommended_status",
    "key_insights", "next_action",
    "assigned_to", "last_updated",
]


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def init_csv():
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/transcripts", exist_ok=True)
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
        log(f"CSV initialised: {CSV_FILE}")


def find_duplicate(email: str, phone: str) -> dict | None:
    if not os.path.exists(CSV_FILE):
        return None
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("email") == email or row.get("phone") == phone:
                return row
    return None


def write_phase1(payload: dict, is_duplicate: bool = False) -> str:
    lead_id = "LD-" + uuid.uuid4().hex[:8].upper()
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    row = {col: "" for col in COLUMNS}
    row.update({
        "lead_id": lead_id,
        "full_name": payload.get("full_name", ""),
        "email": payload.get("email", ""),
        "phone": payload.get("phone", ""),
        "company_name": payload.get("company_name", ""),
        "company_website": payload.get("company_website", ""),
        "service_interest": payload.get("service_interest", ""),
        "brief_description": payload.get("brief_description", ""),
        "submission_time": now(),
        "is_duplicate": str(is_duplicate),
        "call_status": "pending",
        "session_url": f"{base_url}/session/{lead_id}",
        "last_updated": now(),
    })
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writerow(row)
    log(f"Phase 1 written: {lead_id}")
    return lead_id


def update_row(lead_id: str, updates: dict):
    if not os.path.exists(CSV_FILE):
        log(f"CSV_ERROR: file not found when updating {lead_id}", level="ERROR")
        return
    rows = []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    updated = False
    for row in rows:
        if row["lead_id"] == lead_id:
            row.update(updates)
            row["last_updated"] = now()
            updated = True
            break

    if not updated:
        log(f"CSV_ERROR: lead_id {lead_id} not found for update", level="ERROR")
        return

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    log(f"Row updated: {lead_id} → {list(updates.keys())}")


def get_row(lead_id: str) -> dict | None:
    if not os.path.exists(CSV_FILE):
        return None
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["lead_id"] == lead_id:
                return row
    return None
