"""
retrieval_check.py - did the right text even reach the model?

For every test question that has evidence_phrases, this checks whether those phrases
appear in the top-K retrieved chunks. It does not call the LLM, so it is fast, and it
lets you compare chunk sizes / top-K with numbers from a file.

Run:  uv run python retrieval_check.py          (uses TOP_K from config)
      uv run python retrieval_check.py 8        (try a different K)
Output: retrieval_check.json (settings + per-question result + hit rate)

Re-ingest first (uv run python ingest.py) after changing CHUNK_SIZE / CHUNK_OVERLAP.
"""
import json
import re
import sys

import config
from retrieve import retrieve_chunks


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).lower()


def main() -> None:
    top_k = int(sys.argv[1]) if len(sys.argv) > 1 else config.TOP_K
    with open(config.TEST_QUESTIONS_FILE, encoding="utf-8") as f:
        questions = json.load(f)

    rows, full_hits, checked = [], 0, 0
    for q in questions:
        phrases = q.get("evidence_phrases") or []
        if not phrases:
            continue  # unanswerable questions have no evidence to find
        result = retrieve_chunks(q["question"], top_k=top_k)
        joined = norm(" ".join(c["content"] for c in result["retrieved_chunks"]))
        found = [p for p in phrases if norm(p) in joined]
        full = len(found) == len(phrases)
        checked += 1
        full_hits += full
        rows.append({
            "id": q["id"], "difficulty": q["difficulty"], "phrases_found": len(found),
            "phrases_total": len(phrases), "all_found": full,
            "missing": [p for p in phrases if p not in found],
            "top_score": result["retrieved_chunks"][0]["relevance_score"],
        })
        print(f"{q['id']}  {len(found)}/{len(phrases)}  {'OK' if full else 'MISSING ' + str([p for p in phrases if p not in found])}")

    summary = {
        "chunk_size_chars": config.CHUNK_SIZE, "chunk_overlap_chars": config.CHUNK_OVERLAP,
        "top_k": top_k, "embedding_model": config.EMBEDDING_MODEL,
        "extraction_mode": config.EXTRACTION_MODE,
        "questions_checked": checked, "questions_with_all_evidence": full_hits,
    }
    print(f"\n{full_hits}/{checked} questions had ALL evidence in the top {top_k} chunks  {summary}")
    with open("retrieval_check.json", "w", encoding="utf-8") as f:
        json.dump({"settings": summary, "results": rows}, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
