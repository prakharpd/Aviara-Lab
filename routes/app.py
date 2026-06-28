"""FastAPI app — mounts all routers and static files."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes.webhook import router as webhook_router
from routes.session import router as session_router

app = FastAPI(
    title="ASE Lead Qualification Pipeline",
    description="AI-powered lead qualification: voice session + 4 agents + CRM",
    version="1.0.0",
)

app.include_router(webhook_router)
app.include_router(session_router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return {
        "status": "running",
        "docs": "http://localhost:8000/docs",
        "dashboard": "streamlit run dashboard.py → http://localhost:8501",
    }
