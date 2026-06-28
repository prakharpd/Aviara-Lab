"""Discovery Agent — summarises industry, pain points, and current tooling."""
import json
import ollama
from utils.logger import log

MODEL = "gpt-oss:20b-cloud"

SYSTEM = """You are a discovery agent analysing a sales call transcript.
Extract and return ONLY a JSON object with these exact keys:
{
  "industry": "string — industry/sector of the prospect",
  "pain_points": "string — top 2-3 pain points mentioned",
  "current_tools": "string — tools/software they currently use",
  "summary": "string — 2-sentence business overview",
  "flags": "string — any red flags or concerns (or 'none')"
}
Return ONLY the JSON. No preamble. No markdown fences."""


def run_discovery(transcript: str) -> dict:
    log("Discovery Agent: running...")
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
        log(f"Discovery Agent: done — industry={result.get('industry','?')}")
        return result
    except Exception as e:
        log(f"LLM_ERROR (discovery): {e}", level="ERROR")
        return {
            "industry": "unknown",
            "pain_points": "parse error",
            "current_tools": "unknown",
            "summary": "Agent failed to parse transcript.",
            "flags": str(e),
        }
