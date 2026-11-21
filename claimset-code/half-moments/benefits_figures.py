"""Figures of the real-data comparison (question Q6), drawn from the runs that decided PL12, PL13 and PL14.

    python3 benefits_figures.py RN20_DIR RN21_DIR RN22_DIR

Writes to $CLAIMSET_RUN_DIR (or the current directory):
    fig-shift-vs-discrimination.png  discrimination ratio against the shift on removing the 3 values farthest from the
                                     mean (median over the group's four data sets), skewness and tail measures, on the
                                     rock samples and the index returns
    fig-spike-vs-discrimination.png  discrimination ratio against the spike ratio (median over the four indices), on
                                     the index returns
    fig-benefits-by-metric.png       each metric in its own panel, the rock samples and the index returns side by side
    benefits-summary.csv             the values these figures plot
Nothing is computed afresh: every number is a result of the runs named above, or the median of some of them.
"""
import collections
import csv
import json
import os
import statistics
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
FAMILY = {"half-moment": "#2a78d6", "moment": "#eb6834", "L- and TL-moment": "#1baf7a", "quantile": "#e87ba4",
          "other": "#898781"}
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 9, "axes.titlesize": 10, "axes.titlecolor": INK,
    "legend.frameon": False, "legend.labelcolor": INK2,
})
# measure in the results: (label, family)
SKEW = {"Asymmetry": ("Asymmetry", "half-moment"), "moment skewness": ("moment skewness", "moment"),
        "L-skewness": ("L-skewness", "L- and TL-moment"), "TL-skewness": ("TL-skewness", "L- and TL-moment"),
        "quartile skewness": ("quartile skewness", "quantile"), "medcouple": ("medcouple", "quantile"),
        "mean-based skewness 2F(mean) - 1": ("mean-based skewness", "other")}
TAIL = {"Extremity": ("Extremity", "half-moment"), "excess kurtosis": ("excess kurtosis", "moment"),
        "L-kurtosis": ("L-kurtosis", "L- and TL-moment"), "TL-kurtosis": ("TL-kurtosis", "L- and TL-moment"),
        "octile kurtosis": ("octile kurtosis", "quantile"), "Geary ratio": ("Geary ratio", "other")}
GROUPS = {"petroleum rock samples": "rock samples", "European stock index returns": "index returns"}
K = 3
# label placements (offset in points, horizontal alignment) where the default one would overlap another label
PLACE = {
    ("shift", "Skewness", "petroleum rock samples", "TL-skewness"): ((-6, 6), "right"),
    ("shift", "Skewness", "petroleum rock samples", "medcouple"): ((-4, 8), "left"),
    ("shift", "Skewness", "petroleum rock samples", "quartile skewness"): ((4, -12), "left"),
    ("shift", "Skewness", "petroleum rock samples", "mean-based skewness 2F(mean) - 1"): ((6, 6), "left"),
    ("shift", "Tail weight", "European stock index returns", "Extremity"): ((-6, 6), "right"),
    ("shift", "Tail weight", "European stock index returns", "Geary ratio"): ((6, -12), "left"),
    ("spike", "Tail weight", "European stock index returns", "Extremity"): ((-6, 6), "right"),
    ("spike", "Tail weight", "European stock index returns", "Geary ratio"): ((6, -12), "left"),
}


def load(run_dir):
    return json.load(open(Path(run_dir) / "results.json"))


def summaries(rn20, rn21, rn22):
    """{(metric, measure, group): value}: medians over a group's data sets, and the discrimination ratios."""
    out, pool = {}, collections.defaultdict(list)
    for x in load(rn20):
        c = x["conditions"]
        if c["k"] == K:
            pool[("shift", c["measure"], c["data"])].append(abs(x["value"]))
    for x in load(rn22):
        if x["variable"] == "spike ratio":
            pool[("spike", x["conditions"]["measure"], "European stock index returns")].append(x["value"])
    for key, v in pool.items():
        out[key] = statistics.median(v)
    for x in load(rn21):
        if x["variable"] == "discrimination ratio":
            out[("discrimination", x["conditions"]["measure"], x["conditions"]["data"])] = x["value"]
    return out


def scatter(ax, v, xmetric, kind, measures, group, xlabel):
    for m, (label, fam) in measures.items():
        x, y = v[(xmetric, m, group)], v[("discrimination", m, group)]
        own = fam == "half-moment"
        ax.scatter(x, y, s=70 if own else 40, color=FAMILY[fam], zorder=3, edgecolors=SURFACE, linewidths=1.5)
        offset, ha = PLACE.get((xmetric, kind, group, m), ((6, 4), "left"))
        ax.annotate(label, (x, y), textcoords="offset points", xytext=offset, ha=ha, fontsize=8,
                    color=INK if own else INK2, fontweight="bold" if own else "normal")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("discrimination ratio (higher is better)")
    ax.set_title(f"{kind}, {GROUPS[group]}", loc="left")


def family_legend(fig):
    fig.legend(handles=[plt.Line2D([], [], marker="o", ls="", color=c, label=f) for f, c in FAMILY.items()],
               loc="outside lower center", ncol=5)


def main():
    v = summaries(*sys.argv[1:4])
    out = Path(os.environ.get("CLAIMSET_RUN_DIR", "."))
    shift_label = f"shift on removing the {K} values farthest from the mean\n(in standard errors; lower is better)"

    fig, axes = plt.subplots(2, 2, figsize=(11, 8.4), constrained_layout=True)
    for i, (kind, measures) in enumerate((("Skewness", SKEW), ("Tail weight", TAIL))):
        for j, group in enumerate(GROUPS):
            scatter(axes[i, j], v, "shift", kind, measures, group, shift_label)
    family_legend(fig)
    fig.savefig(out / "fig-shift-vs-discrimination.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), constrained_layout=True)
    for ax, (kind, measures) in zip(axes, (("Skewness", SKEW), ("Tail weight", TAIL))):
        scatter(ax, v, "spike", kind, measures, "European stock index returns",
                "spike ratio: the largest change between consecutive windows,\nin standard deviations over all windows (lower is better)")
    family_legend(fig)
    fig.savefig(out / "fig-spike-vs-discrimination.png", dpi=150)
    plt.close(fig)

    metrics = [("shift", f"shift on removing {K} values\n(standard errors; lower is better)"),
               ("discrimination", "discrimination ratio\n(higher is better)"),
               ("spike", "spike ratio, index returns\n(lower is better)")]
    marker = {"petroleum rock samples": ("o", True), "European stock index returns": ("s", False)}
    fig, axes = plt.subplots(2, 3, figsize=(12, 7.2), constrained_layout=True)
    for i, measures in enumerate((SKEW, TAIL)):
        for j, (metric, title) in enumerate(metrics):
            ax = axes[i, j]
            groups = [g for g in GROUPS if (metric, next(iter(measures)), g) in v]
            ms = sorted(measures, key=lambda m: statistics.mean(v[(metric, m, g)] for g in groups))
            for r, m in enumerate(ms):
                vals = [v[(metric, m, g)] for g in groups]
                ax.hlines(r, min(vals + [0]), max(vals), color=GRID, linewidth=2, zorder=1)
                for g in groups:
                    shape, filled = marker[g]
                    colour = FAMILY[measures[m][1]]
                    ax.scatter(v[(metric, m, g)], r, marker=shape, s=48, zorder=3, linewidths=1.5,
                               color=colour if filled else SURFACE, edgecolors=colour)
            ax.set_yticks(range(len(ms)), [measures[m][0] for m in ms])
            for t, m in zip(ax.get_yticklabels(), ms):
                if measures[m][1] == "half-moment":
                    t.set_fontweight("bold")
                    t.set_color(INK)
            if i == 0:
                ax.set_title(title, loc="left", fontsize=9)
            ax.grid(axis="y", visible=False)
    fig.legend(handles=[plt.Line2D([], [], marker="o", ls="", color=MUTED, label="rock samples"),
                        plt.Line2D([], [], marker="s", ls="", color=MUTED, markerfacecolor=SURFACE,
                                   label="index returns")],
               loc="outside lower center", ncol=2)
    fig.savefig(out / "fig-benefits-by-metric.png", dpi=150)
    plt.close(fig)

    with open(out / "benefits-summary.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["measure", "data", f"median shift on removing {K} values (standard errors)",
                    "discrimination ratio", "median spike ratio"])
        for m in list(SKEW) + list(TAIL):
            for g in GROUPS:
                w.writerow([m, g] + [f"{v[(k, m, g)]:.6g}" if (k, m, g) in v else ""
                                     for k in ("shift", "discrimination", "spike")])


if __name__ == "__main__":
    main()
