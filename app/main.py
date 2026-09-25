from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .agent import run_agent
from .config import settings
from .models import AgentRequest, AgentResponse
from .workspace import snapshot_workspace


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Autonomous coding agent built with FastAPI, LangGraph and OpenAI.",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
def home():
    return (BASE_DIR / "templates" / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": settings.gemini_model,
        "workspace": str(settings.workspace_dir),
    }


@app.get("/api/workspace")
def workspace():
    return {"snapshot": snapshot_workspace()}


@app.post("/api/agent/run", response_model=AgentResponse)
def execute_agent(payload: AgentRequest):
    try:
        return run_agent(payload.task)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
