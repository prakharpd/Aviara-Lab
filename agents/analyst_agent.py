"""Analyst Agent — final lead score, status recommendation, and next action."""
import json
import ollama
from utils.logger import log

MODEL = "gpt-oss:20b-cloud"

SYSTEM = """You are a senior sales analyst. Given discovery, budget, and sentiment data
from a prospect call, compute a final lead score and action plan.

Return ONLY a JSON object with these exact keys:
{
  "lead_score": integer 0-100,
  "recommended_status": "hot | warm | cold | disqualified",
  "key_insights": "string — top 2-3 bullet points as a single comma-separated string",
  "next_action": "string — one specific next step for the sales rep",
  "assigned_to": "string — 'SDR Team' | 'Senior AE' | 'No action'"
}

Scoring guide:
- Budget above_20k AND sentiment_score >= 70 AND buying_intent high  → 85-100 (hot)
- Budget 5k_to_20k AND sentiment positive/very_positive              → 60-84  (warm)
- Budget under_5k OR sentiment negative OR buying_intent low         → 30-59  (cold)
- No budget, very negative, or disqualifying flags                   → 0-29   (disqualified)

Return ONLY the JSON. No preamble. No markdown fences."""


def run_analyst(discovery: dict, budget: dict, sentiment: dict) -> dict:
    log("Analyst Agent: running...")
    context = json.dumps(
        {"discovery": discovery, "budget": budget, "sentiment": sentiment}, indent=2
    )
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"Agent outputs:\n{context}"},
            ],
        )
        raw = response["message"]["content"].strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        log(f"Analyst Agent: done — score={result.get('lead_score','?')} status={result.get('recommended_status','?')}")
        return result
    except Exception as e:
        log(f"LLM_ERROR (analyst): {e}", level="ERROR")
        return {
            "lead_score": 0,
            "recommended_status": "cold",
            "key_insights": "Agent error",
            "next_action": "Manual review required",
            "assigned_to": "SDR Team",
        }
