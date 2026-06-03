from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional, Set

from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from analysis_contract import GymEyeAnalysis, normalize_analysis_payload

app = FastAPI(title="Gym Eye Bridge")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_connections: Set[WebSocket] = set()
_last_state: GymEyeAnalysis = normalize_analysis_payload(
    {
        "source": "demo",
        "exercise": None,
        "bodyVisible": "none",
        "activeSuggestion": "Backend is idle. Showing demo-ready fallback state.",
        "timestamp": time.time(),
    },
    fallback_source="demo",
)
_last_frame: Optional[bytes] = None
_last_analysis_at: Optional[float] = None


def _backend_status() -> Dict[str, Any]:
    now = time.time()
    last_seen_seconds = None if _last_analysis_at is None else max(0.0, now - _last_analysis_at)
    live_sources = {"backend", "raspberry_pi", "gazebo", "browser_ai"}
    current_source = _last_state.source

    return {
        "backendConnected": _last_analysis_at is not None,
        "raspberryPiConnected": current_source == "raspberry_pi",
        "currentSource": current_source,
        "lastAnalysisAt": _last_state.timestamp,
        "lastSeenSeconds": last_seen_seconds,
        "hasFrame": _last_frame is not None,
        "transport": {
            "websocketClients": len(_connections),
            "restAvailable": True,
        },
        "mode": current_source if current_source in live_sources else "demo",
    }


def _state_payload() -> Dict[str, Any]:
    return {
        "analysis": _last_state.model_dump(),
        "status": _backend_status(),
    }


async def _broadcast_state() -> None:
    payload = _state_payload()
    for ws in list(_connections):
        try:
            await ws.send_json(payload)
        except Exception:
            _connections.discard(ws)


async def _apply_update(raw: Dict[str, Any], fallback_source: str = "backend") -> Dict[str, Any]:
    global _last_analysis_at, _last_state

    _last_state = normalize_analysis_payload(raw, previous=_last_state, fallback_source=fallback_source)  # type: ignore[arg-type]
    _last_analysis_at = time.time()
    await _broadcast_state()
    return _state_payload()


@app.get("/health")
async def get_health() -> Dict[str, Any]:
    return {"ok": True, "service": "gym-eye-backend", "status": _backend_status()}


@app.get("/state")
async def get_state() -> Dict[str, Any]:
    return _state_payload()


@app.post("/analysis")
async def post_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    return await _apply_update(payload, fallback_source="backend")


@app.post("/update")
async def post_update(payload: Dict[str, Any]) -> Dict[str, Any]:
    return await _apply_update(payload, fallback_source="backend")


@app.post("/state")
async def post_state(payload: Dict[str, Any]) -> Dict[str, Any]:
    return await _apply_update(payload, fallback_source="backend")


@app.post("/frame")
async def post_frame(request: Request) -> Dict[str, bool]:
    global _last_frame
    _last_frame = await request.body()
    return {"ok": True}


@app.get("/frame")
async def get_frame() -> Response:
    if not _last_frame:
        return Response(status_code=404)
    return Response(content=_last_frame, media_type="image/jpeg")


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    _connections.add(ws)
    await ws.send_json(_state_payload())
    try:
        while True:
            raw = await ws.receive_text()
            try:
                data = json.loads(raw)
                if isinstance(data, dict):
                    await _apply_update(data, fallback_source="backend")
                else:
                    await ws.send_json({"error": "payload must be an object"})
            except Exception:
                await ws.send_json({"error": "invalid payload"})
    except WebSocketDisconnect:
        _connections.discard(ws)
