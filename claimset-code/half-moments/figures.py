"""Figures and long-form tables of the half-moments study, drawn from the deciding runs' outputs.

Reads the outputs of the runs that decided PL3 (robustness), PL4 (real data) and PL6 (sampling properties):
    python3 figures.py RN12_DIR RN10_DIR RN13_DIR
Writes to $CLAIMSET_RUN_DIR (or the current directory):
    fig-robustness.png   standardised shift against k, n = 1000, one panel per distribution
    fig-dax-window.png   excess kurtosis and Extremity of the DAX returns on the expanding window
    fig-sampling.png     bias and jackknife-interval coverage against n, one panel per distribution
    robustness.csv       every standardised shift with its Monte Carlo standard error, and the growth exponents
    realdata.csv         every measure on the rock samples and the four index return series
    dax-window-paths.csv every measure on every window length (the RN10 output, copied)
    sampling.csv         bias, spread, RMSE, coverage and their Monte Carlo standard errors
Nothing is computed afresh: every number is a result of the runs named above.
"""
import csv
import json
import os
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator  # noqa: E402

# reference categorical palette, fixed order (slot 1 first); surfaces and inks of the light theme
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
DISTS = ["normal(0,1)", "t(5)", "exponential(1)"]
DIST_TITLE = {"normal(0,1)": "Normal", "t(5)": "Student t, 5 d.f.", "exponential(1)": "Exponential"}

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 9, "axes.titlesize": 10, "axes.titlecolor": INK,
    "legend.frameon": False, "legend.labelcolor": INK2, "lines.linewidth": 2, "lines.markersize": 5,
})


def plain_ticks(ax, axis, ticks):
    """Log axis labelled with plain numbers at the given ticks."""
    a = ax.xaxis if axis == "x" else ax.yaxis
    a.set_major_locator(FixedLocator(ticks))
    a.set_minor_locator(NullLocator())
    a.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))


def load(run_dir):
    return json.load(open(Path(run_dir) / "results.json"))


def write_csv(path, header, rows):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def robustness(res, out):
    shift, se, growth = {}, {}, {}
    for r in res:
        c = r["conditions"]
        if r["variable"] == "growth exponent of the standardised shift":
            growth[(c["measure"], c["distribution"], c["n"])] = r["value"]
            continue
        key = (c["measure"], c["distribution"], c["n"], c["k"])
        (shift if r["variable"] == "standardised shift" else se)[key] = r["value"]
    rows = [[m, dist, n, k, shift[(m, dist, n, k)], se[(m, dist, n, k)], growth.get((m, dist, n), "")]
            for (m, dist, n, k) in sorted(shift, key=lambda t: (t[0], DISTS.index(t[1]), t[2], t[3]))]
    write_csv(out / "robustness.csv", ["measure", "distribution", "n", "k", "standardised shift",
                                        "Monte Carlo standard error of the standardised shift",
                                        "growth exponent of the standardised shift"], rows)
    shown = [("Asymmetry", "-"), ("Hypotailedness", "-"), ("Extremity", "-"), ("moment skewness", "--"),
             ("excess kurtosis", "--"), ("L-skewness", ":"), ("L-kurtosis", ":"), ("medcouple", "-.")]
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.8), sharey=True, constrained_layout=True)
    for ax, dist in zip(axes, DISTS):
        for (m, ls), col in zip(shown, SERIES):
            ks = sorted(k for (mm, d, n, k) in shift if mm == m and d == dist and n == 1000)
            ys = [abs(shift[(m, dist, 1000, k)]) for k in ks]
            ax.plot(ks, ys, ls, color=col, marker="o", label=m)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(DIST_TITLE[dist], loc="left")
        plain_ticks(ax, "x", [0.5, 1, 2, 5, 10, 20, 50, 100])
        plain_ticks(ax, "y", [1e-4, 1e-3, 0.01, 0.1, 1, 10, 100, 1000, 1e4])
    fig.supxlabel("k: the moved value is the mean plus k standard deviations", color=INK2, fontsize=9)
    axes[0].set_ylabel("|standardised shift|, n = 1000")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside right upper", ncol=1)
    fig.savefig(out / "fig-robustness.png", dpi=200)
    plt.close(fig)


def realdata(res, run_dir, out):
    rows = []
    for r in res:
        c = r["conditions"]
        if r["variable"] == "measure value":
            rows.append([c["data"], c.get("variable", c.get("index")), c["measure"], r["value"]])
    write_csv(out / "realdata.csv", ["data", "variable or index", "measure", "value"], rows)
    shutil.copy(Path(run_dir) / "window_paths.csv", out / "dax-window-paths.csv")
    with open(Path(run_dir) / "window_paths.csv", newline="") as fh:
        paths = list(csv.DictReader(fh))
    t = [int(p["window length"]) for p in paths]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 5), sharex=True, constrained_layout=True)
    a1.plot(t, [float(p["excess kurtosis"]) for p in paths], color=SERIES[0])
    a1.set_title("Excess kurtosis", loc="left")
    a2.plot(t, [float(p["Extremity"]) for p in paths], color=SERIES[1])
    a2.axhline(0, color=AXIS, linewidth=1)
    a2.set_title("Extremity coefficient", loc="left")
    a2.set_ylim(-1, 1)
    a2.set_xlabel("window length: the first t daily log returns of the DAX, 1991-1998")
    fig.savefig(out / "fig-dax-window.png", dpi=200)
    plt.close(fig)


def sampling(res, out):
    rows = []
    val = {}
    for r in res:
        c = r["conditions"]
        rows.append([r["variable"], c.get("coefficient"), c.get("distribution"), c.get("n", ""), c.get("interval", ""), r["value"]])
        val[(r["variable"], c.get("coefficient"), c.get("distribution"), c.get("n"), c.get("interval"))] = r["value"]
    write_csv(out / "sampling.csv", ["quantity", "coefficient", "distribution", "n", "interval", "value"], rows)
    coefs = ["Asymmetry", "Hypotailedness", "Extremity"]
    jk = "normal approximation, jackknife standard error"
    ns = sorted({k[3] for k in val if k[3] is not None})
    fig, axes = plt.subplots(2, 3, figsize=(10, 5.4), sharex=True, sharey="row", constrained_layout=True)
    for j, dist in enumerate(DISTS):
        for coef, col in zip(coefs, SERIES):
            axes[0, j].plot(ns, [val[("bias", coef, dist, n, None)] for n in ns], color=col, marker="o", label=coef)
            axes[1, j].plot(ns, [val[("coverage of the 95% interval", coef, dist, n, jk)] for n in ns], color=col,
                            marker="o", label=coef)
        axes[0, j].axhline(0, color=AXIS, linewidth=1)
        axes[1, j].axhline(0.95, color=AXIS, linewidth=1)
        axes[0, j].set_title(DIST_TITLE[dist], loc="left")
        axes[1, j].set_xscale("log")
        plain_ticks(axes[1, j], "x", ns)
        axes[1, j].set_xlabel("sample size n")
    axes[0, 0].set_ylabel("bias")
    axes[1, 0].set_ylabel("coverage of the 95% interval\n(jackknife standard error)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=3)
    fig.savefig(out / "fig-sampling.png", dpi=200)
    plt.close(fig)


def main():
    rn12, rn10, rn13 = sys.argv[1:4]
    out = Path(os.environ.get("CLAIMSET_RUN_DIR", "."))
    robustness(load(rn12), out)
    realdata(load(rn10), rn10, out)
    sampling(load(rn13), out)


if __name__ == "__main__":
    main()
