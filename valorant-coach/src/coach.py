from __future__ import annotations

from typing import List, Tuple

from .schemas import Advice, Metrics, RoundStats


def parse_kda(kda: str) -> Tuple[int, int, int, float]:
    """Parse a k/d/a string and return (k, d, a, kd_ratio).

    Falls back safely if malformed; avoids division by zero.
    """
    try:
        parts = kda.replace(" ", "").split("/")
        k = int(parts[0]) if len(parts) > 0 else 0
        d = int(parts[1]) if len(parts) > 1 else 0
        a = int(parts[2]) if len(parts) > 2 else 0
    except Exception:
        k, d, a = 0, 0, 0
    kd_ratio = round(k / (d if d > 0 else 1), 2)
    return k, d, a, kd_ratio


def format_loadout_reco(econ: str, favorite_weapon: str) -> str:
    e = econ.lower().strip()
    if e.startswith("eco"):
        return "Eco: Classic or Sheriff + Light Shield, prioritize utility and trade setups"
    if e.startswith("force"):
        return "Force: Spectre/Stinger + Light Shield, keep utility for executes"
    # default to full buy
    prim = favorite_weapon or "Vandal"
    return f"Full Buy: {prim} + Full Shield + full utility (prioritize entry or anchor util)"


def rank_from_metrics(kd: float, fdr: float) -> str:
    score = 0.5 * kd + 0.5 * fdr  # naive aggregation
    if score >= 1.2:
        return "Diamond"
    if score >= 1.0:
        return "Platinum"
    if score >= 0.8:
        return "Gold"
    return "Silver"


def generate_advice(stats: RoundStats):
    """Rule-based advice engine. Deterministic and readable rules.

    High-level rules:
    - Abilities usage <60% => high priority utility tip
    - Poor first duel winrate + many entry deaths => high priority entry discipline
    - Econ determines loadout recommendation
    - KD < 1 => trade-frag positioning tip
    """

    _, _, _, kd_ratio = parse_kda(stats.kda)
    first_duel_rate = (
        (stats.first_duels_won / stats.first_duels_taken)
        if stats.first_duels_taken > 0
        else 0.0
    )

    tips: List[Advice] = []

    if stats.abilities_used_pct < 60:
        tips.append(
            Advice(
                priority="high",
                message=(
                    "Utility underused (<60%). Plan set plays: pair flashes/smokes with entries, "
                    "pre-commit util to take map control. Aim for >70% usage."
                ),
            )
        )

    if first_duel_rate < 0.45 and stats.deaths_while_entrying >= 4:
        tips.append(
            Advice(
                priority="high",
                message=(
                    "Entry discipline: reduce wide swings. Let a duelist take first contact or "
                    "swing with trade-ready teammate. Ask for a flash/smoke before peeking."
                ),
            )
        )

    if kd_ratio < 1.0:
        tips.append(
            Advice(
                priority="medium",
                message=(
                    "Value trades: position for instant refrags, avoid solo lurks, and fall back "
                    "when utility is down."
                ),
            )
        )

    if stats.avg_time_to_engage_ms > 20000:
        tips.append(
            Advice(
                priority="low",
                message=(
                    "Tempo: you're slow to first contact. Consider faster defaults or early map "
                    "pressure to draw rotations."
                ),
            )
        )

    loadout_reco = format_loadout_reco(stats.econ, stats.favorite_weapon)

    # Simple, bounded win-rate estimate for demo purposes
    win_rate = 0.5 + 0.15 * (kd_ratio - 1.0) + 0.15 * (first_duel_rate - 0.5)
    win_rate = max(0.0, min(1.0, win_rate))

    metrics = Metrics(
        win_rate=round(win_rate, 2),
        kd_ratio=round(kd_ratio, 2),
        first_duel_rate=round(first_duel_rate, 2),
        rank=rank_from_metrics(kd_ratio, first_duel_rate),
    )

    summary = (
        f"{stats.agent} on {stats.map_name}: KD {metrics.kd_ratio}, first duel win {int(metrics.first_duel_rate*100)}%. "
        f"Playstyle: {stats.personality}. Focus on utility discipline and trading to lift round conversion."
    )

    return summary, loadout_reco, tips, metrics
