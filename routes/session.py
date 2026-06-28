"""Session router — GET /session/{lead_id} and WS /ws/{lead_id}."""
import pathlib
from fastapi import APIRouter, WebSocket
from fastapi.responses import HTMLResponse
from pipeline.voice_session import handle_websocket

router = APIRouter(tags=["Session"])


@router.get("/session/{lead_id}", summary="Serve voice session UI for a lead")
async def serve_session(lead_id: str):
    html = pathlib.Path("static/session.html").read_text(encoding="utf-8")
    html = html.replace("__SESSION_ID__", lead_id)
    return HTMLResponse(html)


@router.websocket("/ws/{lead_id}")
async def websocket_endpoint(websocket: WebSocket, lead_id: str):
    await handle_websocket(websocket, lead_id)
