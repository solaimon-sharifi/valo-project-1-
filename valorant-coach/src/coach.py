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

    # K/D-based advice (aggressive vs conservative play)
    if kd_ratio >= 1.8:
        tips.append(
            Advice(
                priority="low",
                message=(
                    "Strong impact: your fragging is high; keep creating space "
                    "but prioritize team trades when possible."
                ),
            )
        )
    elif kd_ratio < 0.9:
        tips.append(
            Advice(
                priority="high",
                message=(
                    "Low K/D: prioritize survival and trades; avoid solo wide peeks "
                    "without utility or support."
                ),
            )
        )

    # Agent- and weapon-specific advice
    agent_key = (stats.agent or "").lower()
    # concise role map (normalized keys)
    role_map = {
        "jett": "duelist",
        "raze": "duelist",
        "reyna": "duelist",
        "phoenix": "duelist",
        "yoru": "duelist",
        "sage": "sentinel",
        "killjoy": "sentinel",
        "cypher": "sentinel",
        "sova": "initiator",
        "skye": "initiator",
        "breach": "initiator",
        "kayo": "initiator",
        "kay/o": "initiator",
        "fade": "initiator",
        "omen": "controller",
        "brimstone": "controller",
        "viper": "controller",
        "astra": "controller",
    }
    role = role_map.get(agent_key)
    if role:
        if role == "duelist":
            tips.append(
                Advice(
                    priority="high",
                    message=(
                        "Duelist: focus on creating space, entry timing, and quick "
                        "trades; avoid isolated wide swings."
                    ),
                )
            )
        elif role == "sentinel":
            tips.append(
                Advice(
                    priority="medium",
                    message=(
                        "Sentinel: prioritize map control, crossfires, and utility "
                        "to deny enemy info; hold angles post-plant."
                    ),
                )
            )
        elif role == "initiator":
            tips.append(
                Advice(
                    priority="medium",
                    message=(
                        "Initiator: use recon and flashes to enable teammates; call "
                        "timings and chain utility with entries."
                    ),
                )
            )
        elif role == "controller":
            tips.append(
                Advice(
                    priority="medium",
                    message=(
                        "Controller: plan smoke timing to cut rotations and isolate "
                        "fights; don't waste long-duration utility early."
                    ),
                )
            )

    # Per-agent particular tips (short, deterministic)
    agent_tips = {
        "jett": (
            "As Jett: isolate short peeks, play off smokes, and use dash to create "
            "unpredictable angles.",
            "high",
        ),
        "raze": (
            "As Raze: use Boom Bot and grenades to clear common corners; exploit "
            "verticality with satchel.",
            "high",
        ),
        "sova": (
            "As Sova: prioritize recon darts on common plant spots and use ult to "
            "deny defuse attempts.",
            "medium",
        ),
        "sage": (
            "As Sage: hold crossfires and time slows to retake safely; prioritize "
            "healing highest-impact ally.",
            "medium",
        ),
        "killjoy": (
            "As Killjoy: set up gadgets to deny site entry routes and play off your "
            "turret for safe trades.",
            "medium",
        ),
        "omen": (
            "As Omen: use teleports to flank and smoke deep to cut rotations; "
            "coordinate dark cover with team pushes.",
            "medium",
        ),
    }
    if agent_key in agent_tips:
        msg, pr = agent_tips[agent_key]
        tips.append(Advice(priority=pr, message=msg))

    # Weapon-specific small guidance
    fav = (stats.favorite_weapon or "").lower()
    weapon_tips = {
        "shorty": (
            "Shorty: stick to tight corners and close-range holds; don't take open fights.",
            "high",
        ),
        "bucky": (
            "Bucky: use in eco rounds for aggressive close-range pushes and surprise holds.",
            "high",
        ),
        "judge": (
            "Judge: excel in post-plant scenarios and tight chokes; avoid long sightlines.",
            "high",
        ),
        "stinger": (
            "Stinger: effective in eco/force buys; spray controlled bursts at close range.",
            "medium",
        ),
        "spectre": (
            "Spectre: great for close-quarter patrolling and quick peeks; use "
            "mobility to trade.",
            "medium",
        ),
        "vandal": (
            "Vandal: high reward for headshots at range; practice single taps and "
            "recoil for mid-long fights.",
            "low",
        ),
        "phantom": (
            "Phantom: prefer suppressed engagements and spraying at medium ranges; "
            "control recoil for body bursts.",
            "low",
        ),
        "operator": (
            "Operator: hold long angles and pre-aim common lines; prioritize safe "
            "positioning and trade coverage.",
            "high",
        ),
    }
    for key, (wmsg, wpr) in weapon_tips.items():
        if key in fav:
            tips.append(Advice(priority=wpr, message=wmsg))
            break

    # Utility usage (kept after agent/weapon to avoid duplicate high-priority noise)
    if stats.abilities_used_pct < 60:
        tips.append(
            Advice(
                priority="high",
                message=(
                    "Utility underused: integrate flashes and smokes into entry "
                    "sequences and post-plant setups."
                ),
            )
        )

    # Entry discipline (derived from first duels + entry deaths)
    if first_duel_rate < 0.45 and stats.deaths_while_entrying >= 3:
        tips.append(
            Advice(
                priority="high",
                message=(
                    "Entry discipline: avoid solo wide swings — use trades or "
                    "request flashes before taking aggressive angles."
                ),
            )
        )

    # If no strong signals produced a tip, derive a single insight from the most deviating metric
    if len(tips) == 0:
        # choose metric with largest deviation from neutral
        candidates = []
        candidates.append(
            (
                abs(stats.abilities_used_pct - 65) / 100.0,
                f"Abilities: {stats.abilities_used_pct}%",
            )
        )
        candidates.append((abs(kd_ratio - 1.0), f"K/D ratio: {kd_ratio:.2f}"))
        candidates.append(
            (abs(first_duel_rate - 0.5), f"First duel rate: {first_duel_rate:.2f}")
        )
        candidates.sort(reverse=True, key=lambda x: x[0])
        insight = candidates[0][1]
        tips.append(
            Advice(
                priority="low",
                message=(
                    f"Insight: {insight} — use this to prioritize practice for the next few rounds."
                ),
            )
        )

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
        f"{stats.agent} on {stats.map_name}: KD {metrics.kd_ratio}, first duel win "
        f"{int(metrics.first_duel_rate*100)}%. Playstyle: {stats.personality}."
    )

    return summary, loadout_reco, toned, metrics
