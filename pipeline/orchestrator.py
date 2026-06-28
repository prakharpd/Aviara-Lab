"""Orchestrator — validates intake payload, writes Phase 1, sends session email."""
import os
from utils.validation import validate_email, validate_phone
from utils.csv_helpers import find_duplicate, write_phase1, update_row
from utils.email_sender import send_session_email
from utils.logger import log

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def run_full_pipeline(payload: dict):
    lead_id = None
    try:
        log(f"Pipeline started for: {payload.get('email','?')}")

        # Step 1 — Validate
        if not validate_email(payload.get("email", "")):
            log("VALIDATION_ERROR: bad email — lead rejected", level="ERROR")
            return
        if not validate_phone(payload.get("phone", "")):
            log("VALIDATION_ERROR: bad phone — lead rejected", level="ERROR")
            return

        # Step 2 — Duplicate check
        duplicate = find_duplicate(payload["email"], payload["phone"])
        if duplicate:
            log(f"Duplicate detected for {payload['email']} (existing: {duplicate.get('lead_id')})")

        # Step 3 — Write Phase 1 to CSV
        lead_id = write_phase1(payload, is_duplicate=bool(duplicate))
        log(f"Lead {lead_id} written to CSV")

        # Step 4 — Send session email
        send_session_email(lead_id, payload["email"], payload["full_name"])
        log(f"Session email sent to {payload['email']}")

    except Exception as e:
        log(f"PIPELINE_ERROR: {e}", level="ERROR")
        if lead_id:
            update_row(lead_id, {"call_status": "error"})
