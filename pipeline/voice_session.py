"""Voice session — WebSocket handler: Whisper STT → LLM → pyttsx3 TTS → 8 questions."""
import asyncio
import json
import os
import tempfile
import threading
from datetime import datetime

import numpy as np
import pyttsx3
import whisper
import ollama
from fastapi import WebSocket, WebSocketDisconnect

from agents.discovery_agent import run_discovery
from agents.budget_agent import run_budget
from agents.sentiment_agent import run_sentiment
from agents.analyst_agent import run_analyst
from utils.csv_helpers import update_row, get_row
from utils.email_sender import send_rep_email
from utils.logger import log

VOICE_MODEL = "gpt-oss:20b-cloud"

QUESTIONS = [
    "Can you tell me what your business does and which industry you operate in?",
    "What are the main challenges or pain points you're currently facing?",
    "What tools or software are you currently using for these processes?",
    "What kind of solution are you looking for and what outcome do you expect?",
    "Regarding budget — would you say under 5,000 dollars, between 5 and 20 thousand, or above 20 thousand?",
    "What is your expected timeline — immediate, within 30 days, 1 to 3 months, or are you still exploring?",
    "Are you the decision maker for this project, or will others be involved?",
    "Would you like a specialist from our team to contact you?",
]

Q_KEYS = [
    "q1_industry", "q2_pain_points", "q3_current_tools",
    "q4_expected_outcome", "q5_budget_range", "q6_timeline",
    "q7_decision_maker", "q8_wants_callback",
]

# Load Whisper model once at module level
_whisper_model = None

def get_whisper():
    global _whisper_model
    if _whisper_model is None:
        log("Loading Whisper model (medium)...")
        _whisper_model = whisper.load_model("medium")
        log("Whisper model loaded.")
    return _whisper_model


def _tts_speak(text: str):
    """Run pyttsx3 in a thread (it blocks)."""
    def _speak():
        engine = pyttsx3.init()
        engine.setProperty("rate", 165)
        engine.setProperty("volume", 1.0)
        engine.say(text)
        engine.runAndWait()
    t = threading.Thread(target=_speak, daemon=True)
    t.start()
    t.join(timeout=20)


def _transcribe(audio_bytes: bytes) -> str:
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name
    try:
        model = get_whisper()
        result = model.transcribe(tmp_path, language="en", fp16=False, verbose=False)
        text = result["text"].strip()
        return text if text else "[no response detected]"
    except Exception as e:
        log(f"WHISPER_ERROR: {e}", level="ERROR")
        return "[no response detected]"
    finally:
        os.unlink(tmp_path)


def _llm_followup(question: str, answer: str) -> str:
    """Generate a short, natural acknowledgement from the LLM."""
    try:
        resp = ollama.chat(
            model=VOICE_MODEL,
            messages=[{
                "role": "user",
                "content": (
                    f"You asked: '{question}'\n"
                    f"Prospect replied: '{answer}'\n"
                    "Give a brief, warm 1-sentence acknowledgement (max 20 words). "
                    "Do not repeat the answer. Do not ask another question."
                ),
            }],
        )
        return resp["message"]["content"].strip()
    except Exception as e:
        log(f"LLM_ERROR (followup): {e}", level="ERROR")
        return "Thank you for sharing that."


async def handle_websocket(websocket: WebSocket, lead_id: str):
    await websocket.accept()
    log(f"WebSocket connected: {lead_id}")
    transcript_parts = []
    answers = {}

    try:
        update_row(lead_id, {"call_status": "in_progress", "session_start": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

        for i, question in enumerate(QUESTIONS):
            # Send question text to browser
            await websocket.send_json({"type": "question", "index": i, "text": question})
            log(f"Q{i+1}: {question}")

            # Speak the question via TTS in background
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _tts_speak, question)

            # Wait for audio bytes from browser
            await websocket.send_json({"type": "recording_start"})
            audio_data = await websocket.receive_bytes()

            # Transcribe (with timeout and robust error handling)
            answer = await loop.run_in_executor(None, _transcribe, audio_data)
            if not answer or answer == "[no response detected]":
                answer = "[no response detected]"
            log(f"A{i+1}: {answer}")

            answers[Q_KEYS[i]] = answer
            transcript_parts.append(f"Q{i+1}: {question}\nA{i+1}: {answer}")

            # LLM acknowledgement
            ack = await loop.run_in_executor(None, _llm_followup, question, answer)
            await websocket.send_json({"type": "ack", "text": ack})
            await loop.run_in_executor(None, _tts_speak, ack)

        # Session complete
        await websocket.send_json({"type": "session_complete", "text": "Thank you! Your session is complete. We'll be in touch soon."})
        await loop.run_in_executor(None, _tts_speak, "Thank you! Your session is complete. We will be in touch soon.")

        # Save transcript
        transcript_text = "\n\n".join(transcript_parts)
        transcript_path = f"data/transcripts/{lead_id}.json"
        os.makedirs("data/transcripts", exist_ok=True)
        with open(transcript_path, "w") as f:
            json.dump({"lead_id": lead_id, "answers": answers, "transcript": transcript_text}, f, indent=2)

        # Phase 2 CSV update
        phase2_updates = {
            "call_status": "completed",
            "session_end": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "transcript_path": transcript_path,
            **answers,
        }
        update_row(lead_id, phase2_updates)

        # Run 4 agents
        log(f"Running agents for {lead_id}...")
        discovery = await loop.run_in_executor(None, run_discovery, transcript_text)
        budget    = await loop.run_in_executor(None, run_budget, transcript_text)
        sentiment = await loop.run_in_executor(None, run_sentiment, transcript_text)
        analyst   = await loop.run_in_executor(None, run_analyst, discovery, budget, sentiment)

        # Phase 3 CSV update
        phase3_updates = {
            "discovery_summary": discovery.get("summary", ""),
            "discovery_flags": discovery.get("flags", ""),
            "budget_category": budget.get("budget_category", ""),
            "budget_confidence": budget.get("confidence", ""),
            "sentiment_score": str(sentiment.get("sentiment_score", "")),
            "sentiment_label": sentiment.get("sentiment_label", ""),
            "lead_score": str(analyst.get("lead_score", "")),
            "recommended_status": analyst.get("recommended_status", ""),
            "key_insights": analyst.get("key_insights", ""),
            "next_action": analyst.get("next_action", ""),
            "assigned_to": analyst.get("assigned_to", ""),
        }
        update_row(lead_id, phase3_updates)
        log(f"Agent analysis complete for {lead_id} — score={analyst.get('lead_score')}")

        # Hot lead alert
        score = int(analyst.get("lead_score", 0))
        if score > 70:
            row = get_row(lead_id) or {}
            row.update(phase3_updates)
            send_rep_email(row)
            log(f"Hot lead alert sent for {lead_id} (score={score})")

    except WebSocketDisconnect:
        log(f"WebSocket disconnected early: {lead_id}", level="WARNING")
        update_row(lead_id, {"call_status": "unanswered"})
    except Exception as e:
        log(f"VOICE_SESSION_ERROR: {e}", level="ERROR")
        update_row(lead_id, {"call_status": "error"})
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
