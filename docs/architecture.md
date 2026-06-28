# ASE Pipeline Architecture

## System Flow

```mermaid
flowchart TD
    A([Streamlit Intake Form\nlocalhost:8501]) -->|POST JSON| B[FastAPI\n/webhook/lead\nlocalhost:8000]
    B --> C{Validate\nemail + phone}
    C -- Invalid --> X1([Reject & Log])
    C -- Valid --> D{Duplicate\nCheck}
    D --> E[Write Phase 1\nleads.csv]
    E --> F[Send Session Email\nGmail SMTP]
    F --> G([Prospect opens\nhttp://localhost:8000/session/ID])
    G --> H[Serve session.html\nFastAPI GET]
    H --> I([Prospect clicks\nStart Session])
    I --> J[WebSocket /ws/ID\nFastAPI]
    J --> K[Whisper STT\nlocal small model]
    K --> L[gpt-oss:20b-cloud\nvia Ollama\nacknowledgement]
    L --> M[pyttsx3 TTS\nspeak question + ack]
    M -->|8 questions loop| K
    M --> N[Save transcript\ndata/transcripts/ID.json]
    N --> O[Phase 2 CSV update]
    O --> P1[Discovery Agent\ngpt-oss:20b-cloud]
    O --> P2[Budget Agent\ngpt-oss:20b-cloud]
    O --> P3[Sentiment Agent\ngpt-oss:20b-cloud]
    P1 & P2 & P3 --> P4[Analyst Agent\ngpt-oss:20b-cloud]
    P4 --> Q[Phase 3 CSV update\nlead_score, recommended_status]
    Q --> R{lead_score > 70?}
    R -- Yes --> S[Send Rep Alert\nGmail SMTP]
    R -- No --> T([Done])
    S --> T
    T --> U([Streamlit CRM\nRefresh → updated row])
```

## Component Map

| Component | Port | Description |
|---|---|---|
| Streamlit | 8501 | Intake form + CRM dashboard |
| FastAPI | 8000 | Webhook, session page, WebSocket |
| Ollama | 11434 | Local LLM server |
| Whisper | — | Local STT, model=small |
| pyttsx3 | — | Local TTS engine |
| Gmail SMTP | 465 | Session + rep emails |

## Data Flow

```
Intake → Phase 1 CSV → Voice Session → Phase 2 CSV → 4 Agents → Phase 3 CSV
```

## Models Used

| Task | Model | Where |
|---|---|---|
| Voice session (STT) | Whisper small | Local |
| Real-time acknowledgement | gpt-oss:20b-cloud | Ollama → cloud |
| Discovery, Budget, Sentiment, Analyst | gpt-oss:20b-cloud | Ollama → cloud |
