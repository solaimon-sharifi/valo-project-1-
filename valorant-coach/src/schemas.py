from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class RoundStats(BaseModel):
    map_name: str
    agent: str
    econ: str = Field(description="eco|force|full or similar label")
    kda: str = Field(description="Format 'k/d/a', e.g., '18/16/4'")
    first_duels_taken: int = 0
    first_duels_won: int = 0
    abilities_used_pct: float = 0.0
    plants: int = 0
    defuses: int = 0
    avg_time_to_engage_ms: int = 0
    deaths_while_entrying: int = 0
    favorite_weapon: str = "Vandal"
    rounds_played: int = 0
    personality: str = "analyst"


class Advice(BaseModel):
    priority: str = Field(description="high|medium|low")
    message: str


class Metrics(BaseModel):
    win_rate: float
    kd_ratio: float
    first_duel_rate: float
    rank: str


class CoachResponse(BaseModel):
    agent: str
    map_name: str
    personality: str
    summary: str
    loadout_reco: str
    tips: List[Advice]
    metrics: Metrics


class Hotspot(BaseModel):
    x: float
    y: float
    intensity: float


class HeatMap(BaseModel):
    map: str
    hotspots: List[Hotspot]
