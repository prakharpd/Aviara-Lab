"""Sentiment Agent — scores prospect tone and buying intent."""
import json
import ollama
from utils.logger import log

MODEL = "gpt-oss:20b-cloud"

SYSTEM = """You are a sentiment analysis agent reviewing a sales call transcript.
Return ONLY a JSON object with these exact keys:
{
  "sentiment_score": integer between 0 and 100,
  "sentiment_label": "very_positive | positive | neutral | negative | very_negative",
  "buying_intent": "high | medium | low",
  "notes": "string — one sentence justification"
}
Return ONLY the JSON. No preamble. No markdown fences."""


def run_sentiment(transcript: str) -> dict:
    log("Sentiment Agent: running...")
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
        log(f"Sentiment Agent: done — score={result.get('sentiment_score','?')}")
        return result
    except Exception as e:
        log(f"LLM_ERROR (sentiment): {e}", level="ERROR")
        return {
            "sentiment_score": 50,
            "sentiment_label": "neutral",
            "buying_intent": "low",
            "notes": str(e),
        }
