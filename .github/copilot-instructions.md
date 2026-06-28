# VS Code Agent Instructions — ASE Lead Pipeline

## Trigger Word
When the user types **"start"**, execute ALL steps below in order automatically.
Do not wait for further instructions between steps.

---

## STEP 1 — Create .env file
Ask the user to paste their credentials in this exact format, then write them to `.env`:
```
GMAIL_USER=
GMAIL_PASSWORD=
GMAIL_TO=
HF_TOKEN=
BASE_URL=http://localhost:8000
```
Create the `.env` file with the provided values.

---

## STEP 2 — Create Python virtual environment
Run in the terminal:
```bash
python -m venv .venv
```
Then activate it:
- Windows: `.venv\Scripts\activate`
- Mac/Linux: `source .venv/bin/activate`

---

## STEP 3 — Install dependencies
Run:
```bash
pip install -r requirements.txt
```
Wait for completion. If any package fails, retry with `--no-cache-dir`.

---

## STEP 4 — Verify Ollama is running
Run:
```bash
ollama list
```
If this fails, tell the user to start Ollama manually with `ollama serve` in a separate terminal.
Then verify the model exists:
```bash
ollama run gpt-oss:20b-cloud "ping"
```

---

## STEP 5 — Run verification checks
Run this Python snippet to verify all imports work:
```bash
python -c "import fastapi, uvicorn, whisper, pyttsx3, ollama, streamlit, pandas; print('All imports OK')"
```
If any import fails, pip install that specific package.

---

## STEP 6 — Start the FastAPI pipeline server
Run in a new terminal:
```bash
python main.py
```
Confirm you see:
```
ASE LEAD QUALIFICATION PIPELINE
FastAPI server : http://localhost:8000
```

---

## STEP 7 — Start the Streamlit dashboard
Run in another new terminal:
```bash
streamlit run dashboard.py
```
Confirm it opens at http://localhost:8501

---

## STEP 8 — Run self-test
Run:
```bash
python scripts/test_webhook.py
```
Confirm you see `Status: 200` and `"status": "received"`.
Check the `python main.py` terminal for pipeline log output.

---

## STEP 9 — Report status
Print a summary:
```
✅ ASE Pipeline is fully running!

FastAPI  → http://localhost:8000
Docs     → http://localhost:8000/docs  
Dashboard→ http://localhost:8501

Demo flow:
1. Open http://localhost:8501 → fill form → Submit Lead
2. Watch python main.py terminal for logs
3. Check Gmail for session link
4. Open session link → speak answers
5. Refresh dashboard → see lead score
```

---

## Error Handling
- If port 8000 is busy: `lsof -ti:8000 | xargs kill -9` then retry
- If port 8501 is busy: `streamlit run dashboard.py --server.port 8502`
- If Whisper download slow: it only downloads once (~244MB), wait patiently
- If pyttsx3 fails on Linux: `sudo apt-get install espeak`
- If gpt-oss:20b-cloud not found in Ollama: `ollama pull gpt-oss:20b-cloud`
