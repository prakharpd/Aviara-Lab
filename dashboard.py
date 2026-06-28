"""
ASE Lead Pipeline — Streamlit Dashboard
Tabs: New Lead intake form | Live CRM view
Run: streamlit run dashboard.py
"""
import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
CSV_FILE  = "data/leads.csv"

st.set_page_config(page_title="ASE Lead Pipeline", page_icon="🎯", layout="wide")
st.title(" Lead Qualification Pipeline")
st.caption("Powered by FastAPI · Whisper · Ollama · 4 AI Agents")

tab_form, tab_crm = st.tabs([" Submit a Lead", " Live CRM"])

# ── TAB 1: INTAKE FORM ──────────────────────────────────────────────────────
with tab_form:
    st.header("New Lead Intake")
    st.info(f"Leads are sent to `{BASE_URL}/webhook/lead`. Ensure `python main.py` is running.", icon="ℹ️")

    with st.form("lead_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        full_name        = col1.text_input("Full Name *")
        email            = col1.text_input("Email *")
        phone            = col1.text_input("Phone * (e.g. +919876543210)")
        company_name     = col2.text_input("Company Name *")
        company_website  = col2.text_input("Company Website")
        service_interest = col2.selectbox(
            "Service Interest",
            ["AI Automation", "Web Development", "Data Analytics",
             "Consulting", "Custom Software", "Other"],
        )
        brief_description = st.text_area("Brief Description of Requirements", height=100)
        submitted = st.form_submit_button("🚀 Submit Lead", type="primary")

    if submitted:
        missing = [f for f, v in [
            ("Full Name", full_name), ("Email", email),
            ("Phone", phone), ("Company Name", company_name)
        ] if not v.strip()]

        if missing:
            st.error(f"Please fill in required fields: {', '.join(missing)}")
        else:
            payload = {
                "full_name": full_name.strip(),
                "email": email.strip(),
                "phone": phone.strip(),
                "company_name": company_name.strip(),
                "company_website": company_website.strip(),
                "service_interest": service_interest,
                "brief_description": brief_description.strip(),
            }
            try:
                r = requests.post(f"{BASE_URL}/webhook/lead", json=payload, timeout=5)
                if r.status_code == 200:
                    st.success(
                        f"✅ Lead submitted! A session link is being emailed to **{email}**.\n\n"
                        f"Watch the `python main.py` terminal for pipeline logs."
                    )
                else:
                    st.error(f"Server returned {r.status_code}: {r.text}")
            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Cannot reach FastAPI server at `http://localhost:8000`.\n\n"
                    "**Start it with:** `python main.py`"
                )
            except Exception as ex:
                st.error(f"Unexpected error: {ex}")

# ── TAB 2: LIVE CRM DASHBOARD ───────────────────────────────────────────────
with tab_crm:
    st.header("Lead CRM")

    col_r, _ = st.columns([1, 9])
    with col_r:
        if st.button("🔄 Refresh"):
            st.rerun()

    try:
        df = pd.read_csv(CSV_FILE)
        df = df.dropna(how='all')
        df = df[df['lead_id'].notna()]
        df = df[df['lead_id'].str.startswith('LD-', na=False)]
        df = df.reset_index(drop=True)

        # Metrics row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Leads", len(df))
        m2.metric("🔥 Hot (score > 70)",
                  int((pd.to_numeric(df.get("lead_score", pd.Series()), errors="coerce") > 70).sum()))
        m3.metric("✅ Completed",
                  int((df.get("call_status", pd.Series()) == "completed").sum()))
        m4.metric("⏳ Pending",
                  int((df.get("call_status", pd.Series()) == "pending").sum()))

        # Summary table
        display_cols = [c for c in [
            "lead_id", "full_name", "email", "company_name",
            "service_interest", "call_status", "lead_score",
            "recommended_status", "assigned_to", "last_updated",
        ] if c in df.columns]

        # Colour-code score
        def colour_score(val):
            try:
                v = float(val)
                if v > 70: return "background-color: #d4edda; color: #155724"
                if v > 40: return "background-color: #fff3cd; color: #856404"
                return "background-color: #f8d7da; color: #721c24"
            except Exception:
                return ""

        styled = df[display_cols].sort_values("last_updated", ascending=False)
        if "lead_score" in styled.columns:
            st.dataframe(
                styled.style.map(colour_score, subset=["lead_score"]),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.dataframe(styled, use_container_width=True, hide_index=True)

        st.divider()
        with st.expander("🔍 View Full Lead Detail"):
            lead_ids = df["lead_id"].dropna().tolist()
            if lead_ids:
                selected = st.selectbox("Select Lead ID", lead_ids)
                matches = df[df["lead_id"] == selected]
                if not matches.empty:
                    st.json(matches.iloc[0].dropna().to_dict())
                else:
                    st.warning("Lead not found.")
            else:
                st.info("No valid leads found.")

    except FileNotFoundError:
        st.info("📭 No leads yet. Use the **Submit a Lead** tab to submit the first lead.")
    except Exception as e:
        st.error(f"Error loading CRM: {e}")
