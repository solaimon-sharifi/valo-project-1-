from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .coach import generate_advice
from .schemas import CoachResponse, HeatMap, Metrics, RoundStats

ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"

app = FastAPI(title="Valorant Tactical Coach MVP")

# CORS: allow everything for local MVP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve assets under /web; index will be served from GET "/" depending on Accept header
app.mount("/web", StaticFiles(directory=str(WEB_DIR), html=True), name="web")


@app.get("/")
async def root(request: Request):
    """Return {ok:true} for JSON clients, otherwise serve the UI."""
    accept = (request.headers.get("accept") or "").lower()
    if "application/json" in accept:
        return {"ok": True}
    index = WEB_DIR / "index.html"
    return FileResponse(str(index))


@app.post("/coach", response_model=CoachResponse)
async def coach_endpoint(stats: RoundStats):
    summary, loadout, tips, metrics = generate_advice(stats)
    return CoachResponse(
        agent=stats.agent,
        map_name=stats.map_name,
        personality=stats.personality,
        summary=summary,
        loadout_reco=loadout,
        tips=tips,
        metrics=metrics,
    )


@app.get("/metrics/demo", response_model=Metrics)
async def metrics_demo():
    # Deterministic sample metrics for UI demo
    return Metrics(win_rate=0.56, kd_ratio=1.05, first_duel_rate=0.47, rank="Gold")


@app.get("/heatmap/demo", response_model=HeatMap)
async def heatmap_demo():
    # 4 hotspots in normalized [0..1] coordinates
    return HeatMap(
        map="Ascent",
        hotspots=[
            {"x": 0.62, "y": 0.48, "intensity": 0.90},
            {"x": 0.30, "y": 0.22, "intensity": 0.75},
            {"x": 0.78, "y": 0.70, "intensity": 0.60},
            {"x": 0.45, "y": 0.55, "intensity": 0.80},
        ],
    )
