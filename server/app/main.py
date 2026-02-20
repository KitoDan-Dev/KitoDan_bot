from __future__ import annotations

import logging
import sys
import uuid
from pathlib import Path
from time import perf_counter
from typing import Dict, List, Optional

import httpx
from fastapi import APIRouter, Cookie, FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.db import Database
from app.llm.ollama_client import OllamaClient
from app.mode_router import ChatMode, mode_instruction, resolve_mode
from app.settings import get_settings

settings = get_settings()

def resource_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]

profile_path = Path(settings.system_profile_path)
if not profile_path.is_absolute():
    profile_path = resource_root() / settings.system_profile_path
SYSTEM_PROMPT = profile_path.read_text(encoding="utf-8")

logging.basicConfig(
    filename=settings.log_path,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

app = FastAPI(title="KitoDan Local Server", version=settings.server_version)
api = APIRouter(prefix="/api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_origin, "http://127.0.0.1:5173", f"http://localhost:{settings.port}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database(settings.db_path)
ollama_client = OllamaClient(settings.ollama_base_url, settings.ollama_model)

OFFLINE_HINT = (
    "Ollama is offline. Start it with 'ollama serve' and ensure the model is available with "
    "'ollama pull llama3.1:8b' (or update OLLAMA_MODEL in %APPDATA%\\KitoDan\\server.env)."
)


class ChatRequest(BaseModel):
    message: str
    mode: ChatMode = "auto"
    reset: Optional[bool] = False


class ChatResponse(BaseModel):
    session_id: str
    model: str
    mode: str
    reply: str
    latency_ms: int


class ResetRequest(BaseModel):
    session_id: str


class SessionTitleRequest(BaseModel):
    session_id: str
    title: str


def resolve_session_id(header_id: Optional[str], cookie_id: Optional[str]) -> str:
    return header_id or cookie_id or str(uuid.uuid4())


@api.get("/health")
async def health() -> Dict[str, object]:
    started = perf_counter()
    status = await ollama_client.health()
    latency = int((perf_counter() - started) * 1000)

    if status["online"]:
        return {
            "status": "ok",
            "ollama_online": True,
            "model": settings.ollama_model,
            "latency_ms": latency,
            "server_version": settings.server_version,
            "port": settings.port,
        }

    return {
        "status": "degraded",
        "ollama_online": False,
        "model": settings.ollama_model,
        "latency_ms": latency,
        "server_version": settings.server_version,
        "port": settings.port,
        "message": OFFLINE_HINT,
    }


@api.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    response: Response,
    x_session_id: Optional[str] = Header(default=None),
    session_id_cookie: Optional[str] = Cookie(default=None, alias="session_id"),
) -> ChatResponse:
    session_id = resolve_session_id(x_session_id, session_id_cookie)
    db.ensure_session(session_id)

    if payload.reset:
        db.reset_session_messages(session_id)

    resolved_mode = resolve_mode(payload.mode, payload.message)
    context_messages = db.get_context_messages(session_id, settings.context_turns)
    messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(context_messages)
    messages.append({"role": "system", "content": mode_instruction(payload.mode, payload.message)})
    messages.append({"role": "user", "content": payload.message})

    started = perf_counter()
    try:
        reply = await ollama_client.chat(messages=messages, stream=False)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail=f"{OFFLINE_HINT} Technical detail: {exc}") from exc

    db.add_message(session_id, "user", payload.message)
    db.add_message(session_id, "assistant", reply)

    response.headers["X-Session-Id"] = session_id
    response.set_cookie(key="session_id", value=session_id, httponly=False, samesite="lax")

    logging.info("chat session=%s mode=%s", session_id, resolved_mode)

    return ChatResponse(
        session_id=session_id,
        model=settings.ollama_model,
        mode=resolved_mode,
        reply=reply,
        latency_ms=int((perf_counter() - started) * 1000),
    )


@api.get("/history")
async def history_sessions(sessions: int = 0):
    if sessions == 1:
        return {"sessions": db.list_sessions()}
    return {"sessions": []}


@api.get("/history/{session_id}")
async def history_messages(session_id: str):
    return {"session_id": session_id, "messages": db.get_messages(session_id)}


@api.post("/reset")
async def reset_chat(payload: ResetRequest):
    db.ensure_session(payload.session_id)
    db.reset_session_messages(payload.session_id)
    return {"ok": True, "session_id": payload.session_id}


@api.post("/session/title")
async def set_session_title(payload: SessionTitleRequest):
    db.ensure_session(payload.session_id)
    db.set_title(payload.session_id, payload.title)
    return {"ok": True, "session_id": payload.session_id, "title": payload.title}


app.include_router(api)

client_dist = resource_root() / "client" / "dist"
if client_dist.exists():
    app.mount("/assets", StaticFiles(directory=client_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        requested = client_dist / full_path
        if full_path and requested.exists() and requested.is_file():
            return FileResponse(requested)
        return FileResponse(client_dist / "index.html")
