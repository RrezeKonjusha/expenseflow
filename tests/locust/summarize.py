"""Tables and charts for the test report from the four load scenarios (tests/locust/run-matrix.sh).

    python tests/locust/summarize.py results/load docs/test-results/load

Writes summary.md (per-endpoint p50, p95, failure rate, RPS; steady-state figures) and three PNG charts into the
output folder, and copies the scenario CSVs there. Steady state = from 60 s after all 1000 users run (the logins
are done) to the end of the 5-minute run.
"""

import csv
import shutil
import statistics
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SCENARIOS = {  # name: (label, color): categorical slots 1-4 in fixed order, validated; every bar carries its value
    "1api-cache-on": ("1 replica, cache on", "#2a78d6"),
    "1api-cache-off": ("1 replica, cache off", "#eb6834"),
    "3api-cache-on": ("3 replicas, cache on", "#1baf7a"),
    "3api-cache-off": ("3 replicas, cache off", "#eda100"),
}
ENDPOINTS = ["dashboard", "expenses list", "expenses search", "login"]
RUN_SECONDS = 300
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"


def rows(path):
    return list(csv.DictReader(open(path)))


def steady(name):
    hist = [
        r for r in rows(SRC / f"{name}_stats_history.csv") if r["Name"] == "Aggregated" and r["95%"] not in ("N/A", "")
    ]
    t0 = int(hist[0]["Timestamp"])
    full = next(int(r["Timestamp"]) for r in hist if int(r["User Count"]) >= 1000)
    window = [r for r in hist if full + 60 <= int(r["Timestamp"]) <= t0 + RUN_SECONDS]
    med = lambda c: statistics.median(float(r[c]) for r in window)  # noqa: E731
    return {"p50": med("50%"), "p95": med("95%"), "rps": med("Requests/s")}


def style(ax, title, ylabel):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", fontsize=13, color=INK, pad=14)
    ax.set_ylabel(ylabel, color=MUTED)
    ax.tick_params(colors=MUTED, length=0)
    ax.grid(axis="y", color=GRID, linewidth=1)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.set_axisbelow(True)


def grouped_bars(path, title, ylabel, groups, values, fmt):
    """values[scenario] = list aligned with groups"""
    fig, ax = plt.subplots(figsize=(10, 4.4), facecolor=SURFACE)
    width = 0.8 / len(SCENARIOS)
    for i, (name, (label, color)) in enumerate(SCENARIOS.items()):
        xs = [j + (i - (len(SCENARIOS) - 1) / 2) * width for j in range(len(groups))]
        ax.bar(xs, values[name], width=width - 0.02, color=color, label=label, edgecolor=SURFACE, linewidth=2)
        for x, v in zip(xs, values[name], strict=True):
            ax.text(x, v, fmt(v), ha="center", va="bottom", color=INK, fontsize=8)
    ax.set_xticks(range(len(groups)), groups, color=INK)
    style(ax, title, ylabel)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=4, labelcolor=INK)
    ax.set_ylim(0, max(max(v) for v in values.values()) * 1.15)
    fig.tight_layout()
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "results/load")
    OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "docs/test-results/load")
    OUT.mkdir(parents=True, exist_ok=True)
    for missing in [n for n in SCENARIOS if not (SRC / f"{n}_stats.csv").exists()]:
        print(f"skipping {missing}: no results in {SRC}")
        del SCENARIOS[missing]

    stats = {n: {r["Name"]: r for r in rows(SRC / f"{n}_stats.csv")} for n in SCENARIOS}
    stdy = {n: steady(n) for n in SCENARIOS}

    lines = [
        "| Scenario | Endpoint | Requests | Failures | p50 (ms) | p95 (ms) | Requests/s |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for n, (label, _) in SCENARIOS.items():
        for ep in ENDPOINTS + ["Aggregated"]:
            r = stats[n][ep]
            fail = 100 * int(r["Failure Count"]) / max(1, int(r["Request Count"]))
            lines.append(
                f"| {label} | {'all' if ep == 'Aggregated' else ep} | {int(r['Request Count']):,} | {fail:.2f}% | "
                f"{float(r['50%']):.0f} | {float(r['95%']):.0f} | {float(r['Requests/s']):.0f} |"
            )
    lines += [
        "",
        "| Scenario | Steady-state p50 (ms) | Steady-state p95 (ms) | Steady-state requests/s |",
        "| --- | --- | --- | --- |",
    ]
    for n, (label, _) in SCENARIOS.items():
        s = stdy[n]
        lines.append(f"| {label} | {s['p50']:.0f} | {s['p95']:.0f} | {s['rps']:.0f} |")
    (OUT / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))

    eps = ["dashboard", "expenses list", "expenses search"]
    grouped_bars(OUT / "p50-by-endpoint.png", "Median response time per endpoint, 1000 users", "ms", eps,
                 {n: [float(stats[n][e]["50%"]) for e in eps] for n in SCENARIOS}, lambda v: f"{v:.0f}")  # fmt: skip
    grouped_bars(OUT / "p95-by-endpoint.png", "95th percentile response time per endpoint, 1000 users", "ms", eps,
                 {n: [float(stats[n][e]["95%"]) for e in eps] for n in SCENARIOS}, lambda v: f"{v:.0f}")  # fmt: skip
    grouped_bars(OUT / "steady-state.png", "Steady state (after logins), all endpoints", "ms",
                 ["p50", "p95"], {n: [stdy[n]["p50"], stdy[n]["p95"]] for n in SCENARIOS}, lambda v: f"{v:.0f}")  # fmt: skip
    for n in SCENARIOS:
        for suffix in ("_stats.csv", "_stats_history.csv", "_failures.csv"):
            if (SRC / f"{n}{suffix}").exists():
                shutil.copy(SRC / f"{n}{suffix}", OUT / f"{n}{suffix}")
    print(f"charts and CSVs in {OUT}")
