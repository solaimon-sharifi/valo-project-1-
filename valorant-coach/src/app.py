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

# Allow everything for local development MVP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files under /web for asset access. The root route serves index.html
app.mount("/web", StaticFiles(directory=str(WEB_DIR), html=True), name="web")


@app.get("/")
async def root(request: Request):
    """Return JSON for API clients (Accept: application/json), otherwise serve the UI index.html."""
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
async def heatmap_demo(map: str | None = None):
    """Return demo heatmap hotspots. Accepts optional query parameter `map` (e.g. /heatmap/demo?map=Ascent)

    Returns a small, deterministic hotspot list per-map for the UI demo.
    """
    # Preset hotspots per map (normalized coordinates)
    presets = {
        "ascent": [
            {"x": 0.20, "y": 0.18, "intensity": 0.85},
            {"x": 0.48, "y": 0.52, "intensity": 0.78},
            {"x": 0.68, "y": 0.45, "intensity": 0.82},
            {"x": 0.85, "y": 0.70, "intensity": 0.65},
        ],
        "bind": [
            {"x": 0.12, "y": 0.60, "intensity": 0.8},
            {"x": 0.55, "y": 0.30, "intensity": 0.9},
            {"x": 0.82, "y": 0.52, "intensity": 0.6},
        ],
        "icebox": [
            {"x": 0.35, "y": 0.25, "intensity": 0.9},
            {"x": 0.60, "y": 0.40, "intensity": 0.75},
            {"x": 0.45, "y": 0.72, "intensity": 0.7},
        ],
        "split": [
            {"x": 0.28, "y": 0.48, "intensity": 0.8},
            {"x": 0.52, "y": 0.32, "intensity": 0.85},
            {"x": 0.76, "y": 0.60, "intensity": 0.6},
            {"x": 0.42, "y": 0.78, "intensity": 0.55},
        ],
        "breeze": [
            {"x": 0.22, "y": 0.28, "intensity": 0.7},
            {"x": 0.50, "y": 0.50, "intensity": 0.9},
            {"x": 0.74, "y": 0.68, "intensity": 0.8},
        ],
    }

    m = (map or "Ascent").lower()
    hotspots = presets.get(m, presets["ascent"])
    return HeatMap(map=(map or "Ascent"), hotspots=hotspots)
