from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, FastAPI, Form, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    UserInDB,
    authenticate_user,
    create_access_token,
    hash_password,
    require_active_user,
    save_user,
)
from .coach import generate_advice
from .schemas import CoachResponse, HeatMap, Metrics, RoundStats

ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"
TEMPLATES_DIR = ROOT / "templates"

app = FastAPI(title="Valorant Tactical Coach MVP")

# Allow everything for local development MVP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the Valorant UI assets
app.mount("/web", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

auth_router = APIRouter()


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


def _get_token_from_request(request: Request) -> str | None:
    token = request.cookies.get("access_token")
    if not token:
        return None
    prefix = "Bearer "
    return token[len(prefix) :] if token.startswith(prefix) else token


def _current_user_from_request(request: Request) -> UserInDB | None:
    token = _get_token_from_request(request)
    if not token:
        return None
    try:
        return require_active_user(token)
    except Exception:
        return None


def _cookie_response(url: str, token: str) -> RedirectResponse:
    response = RedirectResponse(url, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        "access_token",
        f"Bearer {token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )
    return response


def _template_context(request: Request) -> dict[str, Any]:
    return {
        "request": request,
        "user": _current_user_from_request(request),
    }


@auth_router.get("/login", name="login")
async def login_form(request: Request):
    context = _template_context(request)
    context["message"] = None
    return templates.TemplateResponse("login.html", context)


@auth_router.post("/login")
async def login_action(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    username = username.strip().lower()
    user = authenticate_user(username, password)
    if not user:
        context = _template_context(request)
        context["message"] = "Invalid username or password."
        return templates.TemplateResponse("login.html", context)
    token = create_access_token({"sub": user.username})
    return _cookie_response("/dashboard/app", token)


@auth_router.get("/register", name="register")
async def register_form(request: Request):
    context = _template_context(request)
    context["message"] = None
    return templates.TemplateResponse("register.html", context)


@auth_router.post("/register")
async def register_action(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    username = username.strip().lower()
    if not username or not password:
        context = _template_context(request)
        context["message"] = "Enter both username and password."
        return templates.TemplateResponse("register.html", context)
    if authenticate_user(username, password):
        context = _template_context(request)
        context["message"] = "Username already exists."
        return templates.TemplateResponse("register.html", context)
    user = UserInDB(username=username, hashed_password=hash_password(password))
    save_user(user)
    token = create_access_token({"sub": user.username})
    return _cookie_response("/dashboard/app", token)


@auth_router.get("/dashboard", name="dashboard", include_in_schema=False)
async def dashboard_redirect() -> RedirectResponse:
    return RedirectResponse("/dashboard/app", status_code=status.HTTP_302_FOUND)


def _require_user(request: Request) -> UserInDB | RedirectResponse:
    user = _current_user_from_request(request)
    if not user:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    return user


@auth_router.get("/dashboard/app", name="dashboard_app")
async def dashboard_app(request: Request):
    user = _require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    context = _template_context(request)
    context.update(
        {
            "title": "Dashboard",
            "hero_line": "Unlock the dashboards you just logged in for.",
        }
    )
    return templates.TemplateResponse("dashboard.html", context)


@auth_router.get("/valorant-dashboard", name="valorant_dashboard")
async def valorant_dashboard(request: Request):
    user = _require_user(request)
    if isinstance(user, RedirectResponse):
        return user
    context = _template_context(request)
    context.update({"title": "Valorant Dashboard"})
    return templates.TemplateResponse("valorant_dashboard.html", context)


@auth_router.get("/logout", name="logout")
async def logout(_: Request):
    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


app.include_router(auth_router)
