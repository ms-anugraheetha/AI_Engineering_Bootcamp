"""Prints the numbers used in evaluation_report.md, read from the saved result files.
Run: uv run python report_stats.py > report_stats_output.md
"""
import json
import math
import statistics as st

METRICS = ["Faithfulness", "Answer Relevancy", "Contextual Relevancy",
           "Contextual Recall", "Contextual Precision"]
REFUSAL = "cannot find this information"


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def mean_2se(values):
    n = len(values)
    return st.mean(values), (2 * st.stdev(values) / math.sqrt(n) if n > 1 else float("nan"))


def pass_counts(results):
    strict = sum(all(m["success"] for m in r["metrics"].values()) for r in results)
    two = sum(r["metrics"]["Faithfulness"]["score"] >= 0.7
              and r["metrics"]["Answer Relevancy"]["score"] >= 0.7 for r in results)
    return strict, two


local = load("eval_results_local.json")
cloud = load("eval_results_cloud.json")
out_local = load("pipeline_outputs_local.json")
out_cloud = load("pipeline_outputs_cloud.json")
hand = sum(1 for r in out_local if r["passed"] is True)

def line(results, names):
    parts = []
    for m in names:
        mu, se = mean_2se([r["metrics"][m]["score"] for r in results])
        parts.append(f"{m} {mu:.3f} ± {se:.3f}")
    return ", ".join(parts)


def lowest(results, metric, k, only_zero=False):
    scored = sorted((r["metrics"][metric]["score"], r["id"]) for r in results)
    if only_zero:
        return [f"{qid}" for sc, qid in scored if sc == 0]
    return [f"{qid} ({sc:.2f})" for sc, qid in scored[:k]]


print("## Retrieval quality (source: eval_results_local.json)")
print("- " + line(local, ["Contextual Relevancy", "Contextual Recall", "Contextual Precision"]))
print("- Lowest Contextual Recall (0.00): " + ", ".join(sorted(lowest(local, "Contextual Recall", 0, True))))
print("- Lowest Contextual Relevancy: " + ", ".join(lowest(local, "Contextual Relevancy", 5)))
print("- Lowest Contextual Precision: " + ", ".join(lowest(local, "Contextual Precision", 5)))

print("\n## Generation quality (source: eval_results_local.json)")
print("- " + line(local, ["Faithfulness", "Answer Relevancy"]))
print("(each value is mean ± 2×SE, n = %d, SE = standard deviation / sqrt(n))\n" % len(local))

print("## Mean ± 2×SE per metric (n = %d)" % len(local))
print("| Metric | Local | Cloud |")
print("|---|---|---|")
for m in METRICS:
    lm, ls = mean_2se([r["metrics"][m]["score"] for r in local])
    cm, cs = mean_2se([r["metrics"][m]["score"] for r in cloud])
    print(f"| {m} | {lm:.3f} ± {ls:.3f} | {cm:.3f} ± {cs:.3f} |")

print("\n## Pass counts")
print("| Rule | Local | Cloud |")
print("|---|---|---|")
ls_, l2 = pass_counts(local)
cs_, c2 = pass_counts(cloud)
print(f"| Strict, all five metrics >= 0.7 | {ls_}/{len(local)} | {cs_}/{len(cloud)} |")
print(f"| Faithfulness and Answer Relevancy >= 0.7 | {l2}/{len(local)} | {c2}/{len(cloud)} |")
print(f"| My hand ratings | {hand}/{len(out_local)} | not rated |")

print("\n## Unanswerable questions (string check)")
for tag, rows in (("local", out_local), ("cloud", out_cloud)):
    unans = [r for r in rows if "do not contain" in r["expected_answer"].lower()
             or "does not contain" in r["expected_answer"].lower()]
    ok = [r["id"] for r in unans if REFUSAL in r["actual_answer"].lower()]
    print(f"- {tag}: {len(ok)} of {len(unans)} refused correctly ({', '.join(ok)})")

print("\n## Judge vs my ratings (local, Faithfulness and Answer Relevancy >= 0.7)")
by_id = {r["id"]: r for r in local}
agree, disagree = 0, []
for r in out_local:
    m = by_id[r["id"]]["metrics"]
    judge = m["Faithfulness"]["score"] >= 0.7 and m["Answer Relevancy"]["score"] >= 0.7
    if judge == r["passed"]:
        agree += 1
    else:
        disagree.append((r["id"], "judge pass, I failed" if judge else "judge fail, I passed"))
print(f"- agree on {agree} of {len(out_local)}")
for qid, kind in sorted(disagree):
    print(f"- {qid}: {kind}")
