"""Figures for the grounded finance test: answers by approach and token budget, and seconds per question.

  python figures.py figures      # reads results/run1_first_pass.json and results/run1.json
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

here = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1] if len(sys.argv) > 1 else here
os.makedirs(out, exist_ok=True)
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold",
                     "axes.grid": True, "grid.color": "#E5E7EB", "axes.axisbelow": True})
GREEN, RED, GREY, BLUE, ORANGE = "#2E8B57", "#C0392B", "#B0B0B0", "#006699", "#E8871E"
first = json.load(open(os.path.join(here, "results", "run1_first_pass.json")))["results"]
final = json.load(open(os.path.join(here, "results", "run1.json")))["results"]


def tally(results, mode):
    right = sum(r[mode]["correct"] for r in results)
    empty = sum(not r[mode]["answer"].strip() for r in results)
    return right, len(results) - right - empty, empty


rows = [("Whole table in the prompt\n4,000-token budget", tally(first, "table_in_prompt")),
        ("Whole table in the prompt\n16,000 tokens where it ran out", tally(final, "table_in_prompt")),
        ("SQL only, numbers checked\n4,000-token budget", tally(final, "query_only"))]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.8, 3.8), gridspec_kw={"width_ratios": [1.25, 1]})
for i, (label, (ok, wrong, empty)) in enumerate(rows):
    a1.barh(i, ok, color=GREEN, label="right" if i == 0 else None)
    a1.barh(i, wrong, left=ok, color=RED, label="wrong number" if i == 0 else None)
    a1.barh(i, empty, left=ok + wrong, color=GREY, label="no answer" if i == 0 else None)
    a1.text(24.3, i, f"{ok}/24", va="center", fontsize=9)
a1.set_yticks(range(3), [r[0] for r in rows], fontsize=8.5); a1.invert_yaxis(); a1.set_xlim(0, 27)
a1.set_xlabel("Questions (of 24)"); a1.set_title("Answers about a synthetic income statement")
a1.legend(fontsize=7.5, frameon=False, loc="upper center", bbox_to_anchor=(0.45, -0.2), ncol=3)

table_s = [r["table_in_prompt"]["seconds"] + (r["table_in_prompt"].get("seconds_retry") or 0) for r in final]
query_s = [r["query_only"]["seconds"] for r in final]
a2.boxplot([table_s, query_s], vert=False, widths=0.5, showfliers=True,
           medianprops={"color": "black"}, boxprops={"color": BLUE}, whiskerprops={"color": BLUE})
a2.set_yticks([1, 2], [f"Table in prompt\n(total {sum(table_s) / 60:.0f} min)", f"SQL only\n(total {sum(query_s) / 60:.0f} min)"], fontsize=8.5)
a2.set_xlabel("Seconds per question, including retries"); a2.set_title("Time to answer")
fig.tight_layout(); fig.savefig(os.path.join(out, "fig1_answers_and_time.png"), dpi=200, facecolor="white", bbox_inches="tight"); plt.close(fig)
print("ok")
