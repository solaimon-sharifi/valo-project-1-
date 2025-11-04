from __future__ import annotations

from typing import List, Tuple

from .schemas import Advice, Metrics, RoundStats


def parse_kda(kda: str) -> Tuple[int, int, int, float]:
    """Parse 'k/d/a' to integers and kd ratio. Defensive and deterministic."""
    try:
        parts = kda.replace(" ", "").split("/")
        k = int(parts[0]) if len(parts) > 0 and parts[0] != "" else 0
        d = int(parts[1]) if len(parts) > 1 and parts[1] != "" else 0
        a = int(parts[2]) if len(parts) > 2 and parts[2] != "" else 0
    except Exception:
        k, d, a = 0, 0, 0
    kd_ratio = round(k / (d if d > 0 else 1), 2)
    return k, d, a, kd_ratio


def format_loadout_reco(econ: str, favorite_weapon: str) -> str:
    """Return a simple human-readable loadout recommendation based on econ label."""
    e = (econ or "").lower().strip()
    if e.startswith("eco"):
        return "Eco: Classic or Sheriff + Light Shield. Prioritize utility for trades."
    if e.startswith("force") or e.startswith("half"):
        return "Force: Spectre/Stinger + Light Shield. Keep a smoke/flash for executes."
    # default to full buy
    prim = favorite_weapon or "Vandal"
    return f"Full Buy: {prim} + Full Shield + full utility (prioritize entry utility)."


def rank_from_metrics(kd: float, fdr: float) -> str:
    """Small deterministic mapping from combined score to a human rank label."""
    score = 0.6 * kd + 0.4 * fdr
    if score >= 1.3:
        return "Diamond"
    if score >= 1.05:
        return "Platinum"
    if score >= 0.85:
        return "Gold"
    return "Silver"


def generate_advice(stats: RoundStats):
    """Rule-based advice engine.

    Deterministic rules (easy to read):
    - abilities_used_pct < 60 => high priority utility tip
    - low first duel winrate + many entry deaths => high priority entry tip
    - kd < 1 => medium priority trade/positioning tip

    Returns: (summary, loadout_reco, tips:list[Advice], metrics:Metrics)
    """

    _, _, _, kd_ratio = parse_kda(stats.kda)
    first_duel_rate = (
        (stats.first_duels_won / stats.first_duels_taken)
        if stats.first_duels_taken > 0
        else 0.0
    )

    tips: List[Advice] = []

    # Utility usage
    if stats.abilities_used_pct < 60:
        tips.append(
            Advice(
                priority="high",
                message=(
                    "Utility underused (<60%). Coordinate flashes/smokes with entries and aim to use utility for map control."
                ),
            )
        )

    # Entry discipline
    if first_duel_rate < 0.45 and stats.deaths_while_entrying >= 4:
        tips.append(
            Advice(
                priority="high",
                message=(
                    "Entry discipline: avoid solo wide swings. Let duelists take first contact and ensure trade setups or request a flash."
                ),
            )
        )

    # KD based
    if kd_ratio < 1.0:
        tips.append(
            Advice(
                priority="medium",
                message=(
                    "Value trades and team positioning: play for instant refrags and avoid isolated fights without utility."
                ),
            )
        )

    # Tempo / engagement speed removed per config — not using avg time to engage

    loadout_reco = format_loadout_reco(stats.econ, stats.favorite_weapon)

    # Deterministic win-rate estimate for demo
    win_rate = 0.5 + 0.15 * (kd_ratio - 1.0) + 0.15 * (first_duel_rate - 0.5)
    win_rate = max(0.0, min(1.0, win_rate))

    metrics = Metrics(
        win_rate=round(win_rate, 2),
        kd_ratio=round(kd_ratio, 2),
        first_duel_rate=round(first_duel_rate, 2),
        rank=rank_from_metrics(kd_ratio, first_duel_rate),
    )

    # Agent-specific advice (role-based heuristics)
    agent = (stats.agent or "").lower()
    role_map = {
        # Duelists
        "jett": "duelist",
        "raze": "duelist",
        "reyna": "duelist",
        "jakal": "duelist",
        # Sentinels
        "sage": "sentinel",
        "killjoy": "sentinel",
        "cypher": "sentinel",
        # Initiators
        "sova": "initiator",
        "skye": "initiator",
        "breach": "initiator",
        # Controllers
        "omen": "controller",
        "brimstone": "controller",
        "viper": "controller",
    }
    role = role_map.get(agent)
    if role == "duelist":
        tips.append(Advice(priority="high", message=("Duelist role: create space and trade efficiently; avoid overextending alone.")))
    elif role == "sentinel":
        tips.append(Advice(priority="medium", message=("Sentinel: focus on post-plant positions, anchor sites, and use utility to deny info.")))
    elif role == "initiator":
        tips.append(Advice(priority="medium", message=("Initiator: use recon and flashes to enable entries; coordinate timings with duelists.")))
    elif role == "controller":
        tips.append(Advice(priority="medium", message=("Controller: plan smoke timing to cut rotations and support executes; hold angles after smoke.")))

    # Weapon-based advice
    fav = (stats.favorite_weapon or "").lower()
    if any(s in fav for s in ("shorty", "bucky", "judge")):
        tips.append(Advice(priority="high", message=("Shotgun note: favor close angles and tight corners; avoid long sightlines.")))
    elif any(s in fav for s in ("stinger", "spectre")):
        tips.append(Advice(priority="medium", message=("SMG economy: play aggressively in close ranges and use utility to isolate fights.")))
    elif any(s in fav for s in ("vandal", "phantom", "guardian")):
        # already had a generic weapon note earlier; add tiered advice
        tips.append(Advice(priority="low", message=("Rifle play: prefer medium-long angles and controlled bursts; practice recoil discipline.")))

    # K/D-based advice (aggressive vs conservative play)
    if kd_ratio >= 1.8:
        tips.append(Advice(priority="low", message=("Strong impact: your fragging is high; keep creating space but prioritize team trades when possible.")))
    elif kd_ratio < 0.9:
        tips.append(Advice(priority="high", message=("Low K/D: prioritize survival and trades; avoid solo wide peeks without utility or support.")))

    # Role/agent advice (derived from agent string)
    agent = (stats.agent or "").lower()
    role_map = {
        "jett": "duelist",
        "raze": "duelist",
        "reyna": "duelist",
        "sage": "sentinel",
        "killjoy": "sentinel",
        "cypher": "sentinel",
        "sova": "initiator",
        "skye": "initiator",
        "breach": "initiator",
        "omen": "controller",
        "brimstone": "controller",
        "viper": "controller",
    }
    role = role_map.get(agent)
    if role == "duelist":
        tips.append(Advice(priority="high", message=("Duelist focus: create space, trade efficiently, and avoid isolated peaks without support.")))
    elif role == "sentinel":
        tips.append(Advice(priority="medium", message=("Sentinel focus: hold strong post-plant positions and use utility to deny information to enemies.")))
    elif role == "initiator":
        tips.append(Advice(priority="medium", message=("Initiator focus: use recon and flashes to enable entries; coordinate timings with duelists.")))
    elif role == "controller":
        tips.append(Advice(priority="medium", message=("Controller focus: plan and time smokes to cut rotations and support executes; avoid wasting utility early.")))

    # Utility usage
    if stats.abilities_used_pct < 60:
        tips.append(Advice(priority="high", message=("Utility underused: integrate flashes and smokes into entry sequences and post-plant setups.")))

    # Entry discipline (derived from first duels + entry deaths)
    if first_duel_rate < 0.45 and stats.deaths_while_entrying >= 3:
        tips.append(Advice(priority="high", message=("Entry discipline: avoid solo wide swings — use trades or request flashes before taking aggressive angles.")))

    # Tempo / engagement speed removed — not used per user request

    # Weapon-based advice (if favorite provided)
    fav = (stats.favorite_weapon or "").lower()
    if fav:
        if any(s in fav for s in ("shorty", "bucky", "judge")):
            tips.append(Advice(priority="high", message=("Shotgun note: favor close angles, pre-aim tight corners, and avoid long sightlines.")))
        elif any(s in fav for s in ("stinger", "spectre")):
            tips.append(Advice(priority="medium", message=("SMG play: use close-range advantages and isolate fights — use utility to force short engagements.")))
        elif any(s in fav for s in ("vandal", "phantom", "guardian")):
            tips.append(Advice(priority="low", message=("Rifle play: focus on controlled bursts at medium range and good crosshair placement for headshots.")))

    # If no strong signals produced a tip, derive a single insight from the most deviating metric
    if len(tips) == 0:
        # choose metric with largest deviation from neutral
        candidates = []
        candidates.append((abs(stats.abilities_used_pct - 65) / 100.0, f"Abilities: {stats.abilities_used_pct}%"))
        candidates.append((abs(kd_ratio - 1.0), f"K/D ratio: {kd_ratio:.2f}"))
        candidates.append((abs(first_duel_rate - 0.5), f"First duel rate: {first_duel_rate:.2f}"))
        candidates.sort(reverse=True, key=lambda x: x[0])
        insight = candidates[0][1]
        tips.append(Advice(priority="low", message=(f"Insight: {insight} — use this to prioritize practice for the next few rounds.")))

    # Apply personality tone to messages (no generic/pre-set tips)
    p = (stats.personality or "analyst").lower()
    def tone(msg: str, personality: str) -> str:
        if personality == "strict":
            # concise, imperative
            if not msg.lower().startswith("fix") and not msg.lower().startswith("do"):
                return "Fix: " + msg
            return msg
        if personality == "chill":
            # friendly, encouraging
            return "Hey — " + msg + " Keep it chill and practice at your pace."
        # analyst / default: explanatory
        return "Analysis: " + msg

    toned: List[Advice] = []
    for t in tips:
        toned.append(Advice(priority=t.priority, message=tone(t.message, p)))

    summary = (
        f"{stats.agent} on {stats.map_name}: KD {metrics.kd_ratio}, first duel win {int(metrics.first_duel_rate*100)}%. Playstyle: {stats.personality}."
    )

    return summary, loadout_reco, toned, metrics
