from src.coach import (
    format_loadout_reco,
    generate_advice,
    parse_kda,
    rank_from_metrics,
)
from src.schemas import Agent, Econ, MapName, RoundStats, Weapon


def test_parse_kda_handles_invalid_input() -> None:
    assert parse_kda("invalid") == (0, 0, 0, 0.0)


def test_format_loadout_reco_variants() -> None:
    assert format_loadout_reco("eco", "Vandal").startswith("Eco")
    assert format_loadout_reco("force", "Spectre").startswith("Force")
    assert "Guardian" in format_loadout_reco("full", "Guardian")


def test_rank_from_metrics_covers_ranges() -> None:
    assert rank_from_metrics(2.0, 1.0) == "Diamond"
    assert rank_from_metrics(1.2, 0.9) == "Platinum"
    assert rank_from_metrics(1.0, 0.8) == "Gold"
    assert rank_from_metrics(0.5, 0.1) == "Silver"


def test_generate_advice_strict_duelist_loads_tips() -> None:
    stats = RoundStats(
        map_name=MapName.Ascent,
        agent=Agent.Jett,
        econ=Econ.eco,
        kda="8/10/4",
        first_duels_taken=10,
        first_duels_won=3,
        abilities_used_pct=50,
        deaths_while_entrying=4,
        favorite_weapon=Weapon.Operator,
        personality="strict",
    )
    summary, loadout, tips, metrics = generate_advice(stats)
    assert "Fix:" in summary or "Fix:" in " ".join(t.message for t in tips)
    assert loadout.startswith("Eco")
    assert any("As Jett" in tip.message for tip in tips)
    assert any("Operator" in tip.message for tip in tips)
    assert metrics.kd_ratio == 0.8


def test_generate_advice_chill_fallback_and_tone() -> None:
    stats = RoundStats(
        map_name=MapName.Bind,
        agent=Agent.Sage,
        econ=Econ.full,
        kda="6/5/1",
        first_duels_taken=5,
        first_duels_won=5,
        abilities_used_pct=70,
        deaths_while_entrying=1,
        favorite_weapon=Weapon.Guardian,
        personality="chill",
    )
    stats.agent = None
    summary, loadout, tips, metrics = generate_advice(stats)
    assert len(tips) == 1
    assert "Insight:" in tips[0].message
    assert "Keep it chill" in tips[0].message
    assert metrics.rank == rank_from_metrics(metrics.kd_ratio, metrics.first_duel_rate)


def test_generate_advice_sentinel_and_controller_roles() -> None:
    sentinel_stats = RoundStats(
        map_name=MapName.Bind,
        agent=Agent.Sage,
        econ=Econ.full,
        kda="5/4/2",
        first_duels_taken=6,
        first_duels_won=5,
        abilities_used_pct=65,
        deaths_while_entrying=2,
        favorite_weapon=Weapon.Shorty,
        personality="strict",
    )
    _, _, sentinel_tips, _ = generate_advice(sentinel_stats)
    assert any("Do prioritize map control" in tip.message for tip in sentinel_tips)

    controller_stats = RoundStats(
        map_name=MapName.Bind,
        agent=Agent.Astra,
        econ=Econ.full,
        kda="7/5/1",
        first_duels_taken=6,
        first_duels_won=6,
        abilities_used_pct=70,
        deaths_while_entrying=1,
        favorite_weapon=Weapon.Bucky,
        personality="analyst",
    )
    _, _, controller_tips, _ = generate_advice(controller_stats)
    assert any("Controller" in tip.message for tip in controller_tips)
