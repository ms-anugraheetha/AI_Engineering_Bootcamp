"""Local vs cloud comparison: prints one markdown table, then a timing/tokens/failures table.

    uv run python compare.py

Reads eval_results_local.json, eval_results_cloud.json, pipeline_outputs_local.json and
pipeline_outputs_cloud.json. SE = sample standard deviation / sqrt(n); ranges are mean +/- 2 x SE.
"""
import json
import math
import statistics as st

METRICS = ["Faithfulness", "Answer Relevancy", "Contextual Relevancy",
           "Contextual Recall", "Contextual Precision"]


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def mean_2se(values):
    n = len(values)
    mean = st.mean(values)
    two_se = 2 * st.stdev(values) / math.sqrt(n) if n > 1 else float("nan")
    return mean, two_se


def scores_by_id(results, metric):
    out = {}
    for row in results:
        score = row["metrics"].get(metric, {}).get("score")
        if score is not None:
            out[row["id"]] = score
    return out


def main():
    eval_local, eval_cloud = load("eval_results_local.json"), load("eval_results_cloud.json")
    out_local, out_cloud = load("pipeline_outputs_local.json"), load("pipeline_outputs_cloud.json")

    print("| Metric | n | Local mean ± 2SE | Cloud mean ± 2SE | Cloud − local, per question (mean ± 2SE) | Verdict |")
    print("|---|---|---|---|---|---|")
    for metric in METRICS:
        a, b = scores_by_id(eval_local, metric), scores_by_id(eval_cloud, metric)
        ids = sorted(set(a) & set(b))
        if len(ids) < 2:
            print(f"| {metric} | {len(ids)} | n/a | n/a | n/a | not enough paired scores |")
            continue
        la, lb = [a[i] for i in ids], [b[i] for i in ids]
        diffs = [y - x for x, y in zip(la, lb)]
        ma, ea = mean_2se(la)
        mb, eb = mean_2se(lb)
        md, ed = mean_2se(diffs)
        if md - ed <= 0 <= md + ed:
            verdict = "no clear difference"
        else:
            verdict = "cloud higher" if md > 0 else "local higher"
        print(f"| {metric} | {len(ids)} | {ma:.3f} ± {ea:.3f} | {mb:.3f} ± {eb:.3f} "
              f"| {md:+.3f} ± {ed:.3f} | {verdict} |")

    print()
    print("| Run | Model | Median generation time (ms) | Slowest (ms) | Avg completion tokens | Empty or failed answers |")
    print("|---|---|---|---|---|---|")
    for name, rows in (("local", out_local), ("cloud", out_cloud)):
        times = [r["generation_time_ms"] for r in rows]
        tokens = [r["tokens_generated"] for r in rows if r.get("tokens_generated") is not None]
        bad = [r["id"] for r in rows if not r["actual_answer"].strip() or r["finish_reason"] != "stop"]
        model = ", ".join(sorted({r["model"] for r in rows}))
        avg_tokens = f"{st.mean(tokens):.1f}" if tokens else "n/a"
        print(f"| {name} | {model} | {st.median(times):.0f} | {max(times)} | {avg_tokens} "
              f"| {len(bad)}{' (' + ', '.join(bad) + ')' if bad else ''} |")


if __name__ == "__main__":
    main()
