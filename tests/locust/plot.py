"""Charts for the test report from Locust's CSV output (cache on vs cache off).

    python tests/locust/plot.py docs/test-results/load

Reads <dir>/cache-on_stats_history.csv and <dir>/cache-off_stats_history.csv and writes two PNGs into <dir>.
"""

import csv
import statistics
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RUNS = {"cache-on": ("Redis cache on", "#2a78d6"), "cache-off": ("Cache off", "#eb6834")}
ENDPOINTS = ["dashboard", "expenses list", "expenses search"]
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"


def load(path: Path) -> list[dict]:
    return list(csv.DictReader(path.open()))


def steady_start(rows: list[dict]) -> int:
    agg = [r for r in rows if r["Name"] == "Aggregated"]
    return int(next(r for r in agg if int(r["User Count"]) >= 1000)["Timestamp"]) + 60


def style(ax, title: str, ylabel: str) -> None:
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", fontsize=13, color=INK, pad=14)
    ax.set_ylabel(ylabel, color=MUTED)
    ax.tick_params(colors=MUTED, length=0)
    ax.grid(axis="y", color=GRID, linewidth=1)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.set_axisbelow(True)


def median_over_time(out: Path, data: dict) -> None:
    run_length, y_cap = 300, 1000  # the 5-minute run; the ramp-up spike is labelled instead of plotted to scale
    fig, ax = plt.subplots(figsize=(10, 4.6), facecolor=SURFACE)
    peaks = {}
    for run, (label, color) in RUNS.items():
        agg = [r for r in data[run] if r["Name"] == "Aggregated" and r["50%"] not in ("N/A", "")]
        t0 = int(agg[0]["Timestamp"])
        agg = [r for r in agg if int(r["Timestamp"]) - t0 <= run_length]  # drop the shutdown tail
        xs = [int(r["Timestamp"]) - t0 for r in agg]
        ys = [float(r["50%"]) for r in agg]
        smooth = [statistics.median(ys[max(0, i - 4) : i + 5]) for i in range(len(ys))]  # 9-second rolling median
        peaks[label] = max(smooth)
        ax.plot(xs, [min(v, y_cap) for v in smooth], color=color, linewidth=2, label=label)
        ax.annotate(f"{label}: {smooth[-1]:.0f} ms", (xs[-1], smooth[-1]), xytext=(8, 0),
                    textcoords="offset points", va="center", color=INK, fontsize=10)  # fmt: skip
    ax.axvspan(0, 21, color=GRID, alpha=0.6, linewidth=0)
    peak_text = ", ".join(f"{k.lower()} {v / 1000:.1f} s" for k, v in peaks.items())
    ax.text(130, y_cap * 0.97, f"logins during ramp-up (shaded, 50 users/s) push the median off scale:\npeak {peak_text}",
            color=MUTED, fontsize=9, va="top")  # fmt: skip
    style(ax, "Median response time, 1000 users (all endpoints, 9-second rolling median)", "ms")
    ax.set_xlabel("seconds since start", color=MUTED)
    ax.legend(frameon=False, loc="center right", labelcolor=INK)
    ax.set_ylim(0, y_cap)
    ax.set_xlim(0, run_length * 1.3)
    fig.tight_layout()
    fig.savefig(out / "median-over-time.png", dpi=150, facecolor=SURFACE)


def median_by_endpoint(out: Path) -> dict:
    """Whole-run median per endpoint (Locust keeps per-endpoint history only with --csv-full-history)."""
    result = {}
    for run in RUNS:
        rows = {r["Name"]: r for r in load(out / f"{run}_stats.csv")}
        for ep in ENDPOINTS:
            result[(run, ep)] = float(rows[ep]["50%"])
    fig, ax = plt.subplots(figsize=(10, 4.2), facecolor=SURFACE)
    width = 0.36
    for i, (run, (label, color)) in enumerate(RUNS.items()):
        xs = [j + (i - 0.5) * (width + 0.02) for j in range(len(ENDPOINTS))]
        vals = [result[(run, ep)] for ep in ENDPOINTS]
        ax.bar(xs, vals, width=width, color=color, label=label, edgecolor=SURFACE, linewidth=2)
        for x, v in zip(xs, vals, strict=True):
            ax.text(x, v + 4, f"{v:.0f} ms", ha="center", va="bottom", color=INK, fontsize=10)
    ax.set_xticks(range(len(ENDPOINTS)), ENDPOINTS, color=INK)
    style(ax, "Median response time per endpoint over the whole run, 1000 users", "ms")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2, labelcolor=INK)
    ax.set_ylim(0, max(result.values()) * 1.15)
    fig.tight_layout()
    fig.savefig(out / "median-by-endpoint.png", dpi=150, facecolor=SURFACE)
    return result


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/test-results/load")
    data = {run: load(out / f"{run}_stats_history.csv") for run in RUNS}
    median_over_time(out, data)
    for (run, ep), v in median_by_endpoint(out).items():
        print(f"{run:10} {ep:16} median {v:6.0f} ms")
