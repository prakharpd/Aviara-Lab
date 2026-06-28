"""Budget Agent — categorises budget range and confidence."""
import json
import ollama
from utils.logger import log

MODEL = "gpt-oss:20b-cloud"

SYSTEM = """You are a budget classification agent analysing a sales call transcript.
Return ONLY a JSON object with these exact keys:
{
  "budget_category": "under_5k | 5k_to_20k | above_20k | unknown",
  "confidence": "high | medium | low",
  "notes": "string — any caveats or reasoning in one sentence"
}
Return ONLY the JSON. No preamble. No markdown fences."""


def run_budget(transcript: str) -> dict:
    log("Budget Agent: running...")
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"Transcript:\n{transcript}"},
            ],
        )
        raw = response["message"]["content"].strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        log(f"Budget Agent: done — category={result.get('budget_category','?')}")
        return result
    except Exception as e:
        log(f"LLM_ERROR (budget): {e}", level="ERROR")
        return {"budget_category": "unknown", "confidence": "low", "notes": str(e)}
