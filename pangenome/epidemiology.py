"""Epidemiology — the sense organ, and the only part that produces value on day one.

Nobody can currently answer, for the live agent ecosystem: which capabilities are
spreading, how fast, through which hosts, mutating at what rate, with what lag
between first appearance and general adoption. The data to answer it is public and
nobody is keeping it. Snapshots are cheap; a two-year longitudinal series is not
reproducible by anyone who did not start collecting two years ago.

So this module treats capability adoption as an outbreak and measures it with the
standard machinery:

  r       exponential growth rate, from log-linear regression on the growth phase
  R0      reproduction number, via the Wallinga–Lipsitch relation for an
          exponentially distributed generation interval:  R0 = 1 + r * Tg
  Tg      generation interval — for software, the lag between a host adopting a
          capability and that host causing the next adoption
  K       carrying capacity, from a 3-point logistic fit
  phase   where on the curve it currently sits

Caveats stated rather than hidden: the signal is an adoption *proxy* (stars,
dependents, listing presence), not infection; the susceptible population is
unobserved, so K is inferred not counted; and R0 estimated from a proxy inherits
that proxy's biases. The series is still the asset — the estimator can be
replaced later, the missing history cannot.
"""

from __future__ import annotations

import math

DAY = 86400.0
DEFAULT_GENERATION_INTERVAL = 7 * DAY   # one week, agent-ecosystem fork cadence


# --- basic fits -------------------------------------------------------------

def _linreg(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    """Least squares. Returns (slope, intercept, r2)."""
    n = len(xs)
    if n < 2:
        return 0.0, ys[0] if ys else 0.0, 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0:
        return 0.0, my, 0.0
    slope = sxy / sxx
    intercept = my - slope * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return slope, intercept, r2


# A fit needs history. These are the minimums below which no rate is reported.
MIN_DISTINCT_DAYS = 3
MIN_SPAN_DAYS = 2.0


def daily(series: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Collapse to one point per calendar day, keeping the last of each.

    Without this, several observations taken seconds apart inside one heartbeat
    look like explosive growth: the time denominator goes to ~0 and r goes to
    infinity. A snapshot is not a time series, and repeated snapshots inside one
    beat are still one snapshot.
    """
    by_day: dict[int, tuple[float, float]] = {}
    for t, v in series:
        if v is None or v <= 0:
            continue
        by_day[int(t // DAY)] = (t, v)
    return [by_day[k] for k in sorted(by_day)]


def growth_rate(series: list[tuple[float, float]]) -> tuple[float, float]:
    """Exponential growth rate r per day, and the fit's r-squared.

    Fitted on log(signal) — an outbreak is linear in log space while it is still
    exponential, and r2 says honestly whether it still is. Returns (0, 0) when
    there is not enough history to fit, rather than a number that looks like a
    measurement and is not one.
    """
    pts = daily(series)
    if len(pts) < MIN_DISTINCT_DAYS:
        return 0.0, 0.0
    span = (pts[-1][0] - pts[0][0]) / DAY
    if span < MIN_SPAN_DAYS:
        return 0.0, 0.0
    t0 = pts[0][0]
    xs = [(t - t0) / DAY for t, _ in pts]
    ys = [math.log(v) for _, v in pts]
    slope, _, r2 = _linreg(xs, ys)
    return slope, r2


def lifetime_rate(signal: float, created_at: float, now: float) -> float | None:
    """Mean growth since inception — log(signal) / age in days.

    Explicitly NOT an instantaneous rate and not comparable to `r`: it is the
    average over the whole life of the locus, which is all that is knowable
    before the organism has accumulated its own longitudinal series. It exists
    so the first weeks of operation are not blind, and it is reported under its
    own name so it is never mistaken for a fit.
    """
    if signal is None or signal <= 1 or not created_at:
        return None
    age_days = (now - created_at) / DAY
    if age_days < 7:
        return None
    return math.log(signal) / age_days


def reproduction_number(r_per_day: float,
                        generation_interval: float = DEFAULT_GENERATION_INTERVAL) -> float:
    """Wallinga–Lipsitch for an exponentially distributed generation interval.

    R0 = 1 + r * Tg. Chosen over R0 = exp(r*Tg) deliberately: the exponential
    kernel is the conservative assumption, and adoption intervals in software
    are long-tailed, which is exactly the case the exponential kernel handles
    without over-estimating.
    """
    return 1.0 + r_per_day * (generation_interval / DAY)


def logistic_fit(series: list[tuple[float, float]]) -> dict | None:
    """Three-point (Hotelling) estimate of the carrying capacity K.

    For y(t) = K / (1 + A e^{-rt}), the reciprocals u = 1/y satisfy
    (u - 1/K) ~ e^{-rt}. So at three *equally spaced* times the quantities
    (u_i - 1/K) are geometric, and solving

        (u2 - c)^2 = (u1 - c)(u3 - c),  c = 1/K

    gives  K = (2*u2 - u1 - u3) / (u2^2 - u1*u3).

    Equal spacing is not optional — it is what makes the sequence geometric.
    Indices 0, m, 2m give equal spacing in *index*; on a gappy series that is
    not equal spacing in *time*, and a fit run anyway fabricates a ceiling. So
    the actual timestamps are checked: if the two gaps differ by more than 25%,
    there is no valid three-point estimate and None is returned — the same
    honest-null this function already produces when the curve has not bent.
    """
    pts = [(t, v) for t, v in series if v and v > 0]
    if len(pts) < 7:
        return None
    m = (len(pts) - 1) // 2
    t1, t2, t3 = pts[0][0], pts[m][0], pts[2 * m][0]
    gap_a, gap_b = t2 - t1, t3 - t2
    mean_gap = (gap_a + gap_b) / 2
    if mean_gap <= 0 or abs(gap_a - gap_b) > 0.25 * mean_gap:
        return None                     # gappy series: no equal-spaced triple
    y1, y2, y3 = pts[0][1], pts[m][1], pts[2 * m][1]
    u1, u2, u3 = 1.0 / y1, 1.0 / y2, 1.0 / y3
    denom = u2 * u2 - u1 * u3
    if abs(denom) < 1e-18:
        return None                     # still purely exponential
    K = (2 * u2 - u1 - u3) / denom
    latest = pts[-1][1]
    if K <= max(y1, y2, y3, latest):
        return None                     # no ceiling visible yet
    return {"K": K, "saturation": round(latest / K, 4)}


# --- the read-out -----------------------------------------------------------

def phase_of(r: float, r2: float, saturation: float | None, fittable: bool) -> str:
    if not fittable:
        return "no-history"          # the organism has not watched it long enough
    if r2 < 0.3:
        return "noisy"
    if r <= 0.001:
        return "endemic" if saturation and saturation > 0.6 else "dormant"
    if saturation is not None and saturation > 0.85:
        return "saturated"
    if saturation is not None and saturation > 0.4:
        return "decelerating"
    return "outbreak"


def profile(series: list[tuple[float, float]], locus: str,
            generation_interval: float = DEFAULT_GENERATION_INTERVAL,
            created_at: float | None = None, now: float | None = None) -> dict:
    import time as _t
    now = now or _t.time()
    pts = daily(series)
    span = (pts[-1][0] - pts[0][0]) / DAY if len(pts) > 1 else 0.0
    fittable = len(pts) >= MIN_DISTINCT_DAYS and span >= MIN_SPAN_DAYS

    r, r2 = growth_rate(series)
    fit = logistic_fit(series) if fittable else None
    sat = fit["saturation"] if fit else None
    latest = pts[-1][1] if pts else None
    lr = lifetime_rate(latest, created_at, now) if created_at else None

    return {
        "locus": locus,
        "observations": len(series),
        "distinct_days": len(pts),
        "span_days": round(span, 2),
        # instantaneous fit — None until there is genuinely something to fit
        "r_per_day": round(r, 5) if fittable else None,
        "fit_r2": round(r2, 3) if fittable else None,
        "R0": round(reproduction_number(r, generation_interval), 3) if fittable else None,
        "doubling_days": round(math.log(2) / r, 2) if fittable and r > 0 else None,
        # since-inception mean — available immediately, not the same quantity
        "lifetime_r": round(lr, 5) if lr else None,
        "signal": latest,
        "K": round(fit["K"], 1) if fit else None,
        "saturation": sat,
        "phase": phase_of(r, r2, sat, fittable),
    }


def outbreak_table(store, source: str | None = None, min_obs: int = 1) -> list[dict]:
    """Every capability the organism is watching.

    Ranked by fitted R0 where it exists, and by since-inception growth where it
    does not — so the table is useful on day one and becomes trustworthy as the
    series accumulates. The `phase` column says which of the two you are looking
    at; `no-history` means the organism has not watched this long enough to have
    an opinion, and it says so rather than inventing one.

    The longitudinal series is the asset here. The estimator can be replaced
    later; the history cannot be back-filled by anyone who did not collect it.
    """
    import json
    rows = []
    for src, locus in store.loci(source):
        series = store.series(src, locus)
        if len(series) < min_obs:
            continue
        created = None
        last = store.q("SELECT payload FROM observations WHERE source=? AND locus=?"
                       " ORDER BY seen_at DESC LIMIT 1", (src, locus))
        if last:
            meta = json.loads(last[0]["payload"])
            created = _parse_ts(meta.get("created_at") or meta.get("published_at"))
        p = profile(series, locus, created_at=created)
        p["source"] = src
        rows.append(p)
    return sorted(rows, key=lambda p: (-(p["R0"] or 0), -(p["lifetime_r"] or 0),
                                       -(p["fit_r2"] or 0)))


def _parse_ts(s) -> float | None:
    if not s or not isinstance(s, str):
        return None
    import datetime
    try:
        return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None
