"""
pipeline.py - question in, answer out (retrieve -> generate).

One question:   uv run python pipeline.py "How many PTO days do I get?"
All questions:  uv run python pipeline.py --all     (writes pipeline_outputs.json)
"""
import json
import sys

import config
from generate import generate_answer
from retrieve import retrieve_chunks


def answer_question(query: str) -> dict:
    retrieval_result = retrieve_chunks(query)
    generation_result = generate_answer(query=query, chunks=retrieval_result["retrieved_chunks"])
    return {**generation_result, "retrieval": retrieval_result}


def run_all() -> None:
    with open(config.TEST_QUESTIONS_FILE, encoding="utf-8") as f:
        questions = json.load(f)

    rows = []
    for number, q in enumerate(questions, start=1):
        print(f"[{number}/{len(questions)}] {q['id']}: {q['question']}")
        result = answer_question(q["question"])
        chunks = result["retrieval"]["retrieved_chunks"]
        rows.append({
            "id": q["id"],
            "question": q["question"],
            "expected_answer": q["expected_answer"],
            "actual_answer": result["answer"],
            "retrieved_context": [c["content"] for c in chunks],
            "context_sources": [
                {"source": c["source"], "page": c["page"], "score": c["relevance_score"]} for c in chunks
            ],
            "model": result["model"],
            "thinking": result["thinking"],
            "finish_reason": result["finish_reason"],
            "embedding_model": result["retrieval"]["embedding_model"],
            "prompt_tokens": result["prompt_tokens"],
            "tokens_generated": result["tokens_generated"],
            "retrieval_time_ms": result["retrieval"]["retrieval_time_ms"],
            "generation_time_ms": result["generation_time_ms"],
            "passed": None,       # you fill these two in by hand after the final run
            "rating_note": "",
        })
        # Save after every question so a crash does not lose the whole run.
        with open(config.PIPELINE_OUTPUTS_FILE, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(rows)} rows to {config.PIPELINE_OUTPUTS_FILE}. Now rate them by hand.")


if __name__ == "__main__":
    if "--all" in sys.argv:
        run_all()
    else:
        question = " ".join(sys.argv[1:]) or "How many days of paid time off do full-time employees get?"
        out = answer_question(question)
        print(out["answer"])
        print(f"\n(finish_reason={out['finish_reason']}, prompt_tokens={out['prompt_tokens']}, "
              f"{out['generation_time_ms']} ms)")
        for c in out["retrieval"]["retrieved_chunks"]:
            print(f"  {c['relevance_score']:.3f}  {c['source']} p.{c['page']}")
