"""
Test script — simulate a lead POST without touching the Streamlit form.
Run: python scripts/test_webhook.py
Ensure python main.py is running first.
"""
import requests
import json

PAYLOAD = {
    "full_name":         "Priya Sharma",
    "email":             "studysaint17@gmail.com",
    "phone":             "+919876543210",
    "company_name":      "Acme Logistics",
    "company_website":   "https://acmelogistics.in",
    "service_interest":  "AI Automation",
    "brief_description": "We need to automate dispatch tracking and customer notifications.",
}

print("Sending test lead to http://localhost:8000/webhook/lead ...")
print("Payload:", json.dumps(PAYLOAD, indent=2))

try:
    r = requests.post("http://localhost:8000/webhook/lead", json=PAYLOAD, timeout=5)
    print(f"\nStatus: {r.status_code}")
    print("Response:", r.json())
    print("\n✅ Lead accepted. Watch the python main.py terminal for pipeline logs.")
    print("Check your Gmail inbox for the session email.")
except requests.exceptions.ConnectionError:
    print("\n❌ Cannot connect to localhost:8000.")
    print("   Make sure  python main.py  is running first.")
