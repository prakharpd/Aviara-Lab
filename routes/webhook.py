"""Webhook router — POST /webhook/lead."""
from fastapi import APIRouter, BackgroundTasks
from pipeline.orchestrator import run_full_pipeline

router = APIRouter(tags=["Webhook"])


@router.post("/webhook/lead", summary="Receive a new lead from Streamlit form")
async def receive_lead(payload: dict, background_tasks: BackgroundTasks):
    """
    Accepts lead payload, immediately returns 200, runs pipeline in background.
    """
    background_tasks.add_task(run_full_pipeline, payload)
    return {"status": "received", "message": "Lead is being processed"}
