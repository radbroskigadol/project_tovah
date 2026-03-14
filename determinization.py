"""
TOVAH v14 core/determinization.py — Determinization and readout helpers.

CRITICAL RULE:
  Determinization is an INTERFACE/VIEW, not the core state.
  Never treat a determinized answer as the real stored state
  unless a specific rule explicitly authorizes that collapse.

These functions consume bilateral state and produce classical views.
They never mutate the bilateral state.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from tovah_v14.core.primitives import BilateralValue, coerce_bilateral_value
from tovah_v14.core.lanes import lane_project, lane_divergence
from tovah_v14.core.state import ShadowState


def determinize_value(v: BilateralValue) -> float:
    """Map bilateral value to [0, 1] classical confidence.
    determinize(v) = clamp(0.5 + 0.5 * delta)
    """
    return max(0.0, min(1.0, 0.5 + 0.5 * v.delta))


def determinize_beta(beta: Dict[str, BilateralValue]) -> Dict[str, float]:
    """Determinize entire beta map to classical confidence map."""
    return {k: determinize_value(v) for k, v in beta.items()}


def readout_state(s: ShadowState) -> Dict[str, Any]:
    """Produce a human-readable readout of current state.

    This is a VIEW. It does not modify the state.
    Returns a dict with:
    - cache_histogram: counts of T/F/B/G classifications
    - determinized_beta: classical confidence values
    - carrier: operational state
    - provenance: step/refresh counts
    - high_glut_keys: keys with glut > 0.3
    - high_gap_keys: keys with gap > 0.3
    """
    hist: Dict[str, int] = {"T": 0, "F": 0, "B": 0, "G": 0}
    for v in s.nu.values():
        hist[v] = hist.get(v, 0) + 1

    high_glut: List[str] = []
    high_gap: List[str] = []
    for k, v in s.beta.items():
        if v.glut > 0.3:
            high_glut.append(k)
        if v.gap > 0.3:
            high_gap.append(k)

    return {
        "cache_histogram": hist,
        "determinized_beta": determinize_beta(s.beta),
        "carrier": {
            "active_goal": s.c.active_goal,
            "cycle": s.c.cycle,
            "mode": s.c.mode,
            "paused": s.c.paused,
            "degraded": getattr(s.c, "degraded", False),
        },
        "provenance": {
            "step": s.pi.step,
            "refresh_count": s.pi.refresh_count,
        },
        "beta_key_count": len(s.beta),
        "high_glut_keys": high_glut[:20],
        "high_gap_keys": high_gap[:20],
    }


def lane_readout(v: BilateralValue) -> Dict[str, Tuple[float, float]]:
    """Project a single bilateral value through all four lanes.
    Returns {"A": (t_a, f_a), "B": (t_b, f_b), ...}
    """
    return {name: lane_project(v.t, v.f, name) for name in ("A", "B", "C", "D")}
