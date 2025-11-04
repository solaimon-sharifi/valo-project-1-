from __future__ import annotations

from typing import List
from enum import Enum

from pydantic import BaseModel, Field


class MapName(str, Enum):
    Ascent = "Ascent"
    Bind = "Bind"
    Breeze = "Breeze"
    Icebox = "Icebox"
    Split = "Split"
    Fracture = "Fracture"
    Pearl = "Pearl"
    Haven = "Haven"


class Agent(str, Enum):
    # Duelists
    Jett = "Jett"
    Raze = "Raze"
    Reyna = "Reyna"
    Phoenix = "Phoenix"
    Yoru = "Yoru"
    # Sentinels
    Sage = "Sage"
    Killjoy = "Killjoy"
    Cypher = "Cypher"
    # Initiators
    Sova = "Sova"
    Skye = "Skye"
    Breach = "Breach"
    KAY_O = "KAY/O"
    Fade = "Fade"
    # Controllers
    Omen = "Omen"
    Brimstone = "Brimstone"
    Viper = "Viper"
    Astra = "Astra"


class Weapon(str, Enum):
    # Pistols
    Classic = "Classic"
    Ghost = "Ghost"
    Sheriff = "Sheriff"
    # SMGs
    Stinger = "Stinger"
    Spectre = "Spectre"
    # Shotguns
    Shorty = "Shorty"
    Bucky = "Bucky"
    Judge = "Judge"
    # Rifles
    Vandal = "Vandal"
    Phantom = "Phantom"
    Guardian = "Guardian"
    Bulldog = "Bulldog"
    # Snipers
    Marshal = "Marshal"
    Operator = "Operator"
    # LMGs
    Ares = "Ares"
    Odin = "Odin"


class Econ(str, Enum):
    full = "full"
    force = "force"
    eco = "eco"


class RoundStats(BaseModel):
    map_name: MapName
    agent: Agent
    econ: Econ = Field(description="eco|force|full or similar label")
    kda: str = Field(description="Format 'k/d/a', e.g., '18/16/4'")
    first_duels_taken: int = 0
    first_duels_won: int = 0
    abilities_used_pct: float = 0.0
    avg_time_to_engage_ms: int = 0
    deaths_while_entrying: int = 0
    favorite_weapon: Weapon = Weapon.Vandal
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
    agent: Agent
    map_name: MapName
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
