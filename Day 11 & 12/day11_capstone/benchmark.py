"""
benchmark.py - Exercise 1. Same prompts, several local models, compare speed and quality.

Run:  uv run python benchmark.py
Then open benchmark_results.json and fill in quality_rating (1-5) and rating_note BY HAND.
Re-running overwrites the file, so rate last.
"""
import json
import time

from openai import OpenAI

import config

MODELS = ["qwen3.5:4b-q4_K_M", "qwen3.5:2b-q4_K_M"]
# Thinking is set the same way for every model, otherwise the comparison is unfair.
REASONING_EFFORT = config.REASONING_EFFORT

PARAGRAPH = (
    "Retrieval-augmented generation (RAG) combines a search step with a language model. "
    "Documents are split into chunks and converted to vectors. When a question arrives, the "
    "system finds the chunks whose vectors are closest to the question and passes them to the "
    "model as context. This lets the model answer from private documents it was never trained "
    "on, and it makes answers easier to check because the source chunks can be shown."
)

PROMPTS = [
    {"category": "factual", "prompt": "What causes tides on Earth? Answer in 2-3 sentences."},
    {"category": "reasoning", "prompt": "If a train travels 120km in 1.5 hours, and then 80km in 1 hour, what is the average speed for the entire journey?"},
    {"category": "summarization", "prompt": f"Summarize the following paragraph in one sentence:\n\n{PARAGRAPH}"},
    {"category": "structured", "prompt": 'List 3 European capitals. Respond ONLY with valid JSON: [{"city": ..., "country": ...}]'},
    {"category": "code", "prompt": "Write a Python function is_palindrome(s) that ignores case and spaces. Return only the code."},
    {"category": "instruction_following", "prompt": "Write exactly 3 bullet points about why backups matter. Each bullet must start with a verb and be under 10 words. No introduction, no conclusion."},
]


def run_benchmark(model: str, prompt_item: dict) -> dict:
    client = OpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)
    start = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt_item["prompt"]}],
        temperature=0.7,
        reasoning_effort=REASONING_EFFORT,
        **{config.TOKEN_LIMIT_PARAM: 1024},
    )
    elapsed = time.time() - start
    choice = response.choices[0]
    usage = response.usage
    text = choice.message.content or ""

    if not text.strip():
        print(f"WARNING: empty response from {model} on '{prompt_item['category']}' "
              f"(finish_reason={choice.finish_reason})")

    return {
        "model": model,
        "category": prompt_item["category"],
        "prompt": prompt_item["prompt"],
        "response": text,
        "thinking": REASONING_EFFORT != "none",
        "finish_reason": choice.finish_reason,
        "time_seconds": round(elapsed, 2),
        "prompt_tokens": usage.prompt_tokens if usage else None,
        "completion_tokens": usage.completion_tokens if usage else None,
        "tokens_per_second": round(usage.completion_tokens / elapsed, 1) if usage and usage.completion_tokens else None,
        "quality_rating": None,
        "rating_note": "",
    }


def main() -> None:
    results = []
    for model in MODELS:
        # Warm-up call so model loading time is not counted in the first real prompt.
        try:
            OpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY).chat.completions.create(
                model=model, messages=[{"role": "user", "content": "Hi"}],
                reasoning_effort=REASONING_EFFORT, **{config.TOKEN_LIMIT_PARAM: 5})
        except Exception as exc:
            print(f"WARNING: warm-up for {model} failed: {exc}")
        for item in PROMPTS:
            print(f"{model} / {item['category']} ...")
            results.append(run_benchmark(model, item))
            with open("benchmark_results.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(results)} rows to benchmark_results.json. Rate them by hand.")


if __name__ == "__main__":
    main()
