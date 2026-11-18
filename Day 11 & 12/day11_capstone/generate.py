"""
generate.py - give the LLM the question plus the retrieved chunks, get an answer.
"""
import time

from openai import OpenAI

import config

_client = OpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)


def build_context(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        parts.append(f"[{i}] ({chunk['source']}, page {chunk['page']})\n{chunk['content']}")
    return "\n\n".join(parts)


def generate_answer(query: str, chunks: list[dict]) -> dict:
    context = build_context(chunks)
    started = time.time()
    response = _client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": config.SYSTEM_PROMPT.format(context=context)},
            {"role": "user", "content": query},
        ],
        temperature=config.TEMPERATURE,
        reasoning_effort=config.REASONING_EFFORT,
        **{config.TOKEN_LIMIT_PARAM: config.MAX_TOKENS},
    )
    elapsed_ms = round((time.time() - started) * 1000)

    choice = response.choices[0]
    answer = (choice.message.content or "").strip()
    usage = response.usage

    if not answer:
        print(f"WARNING: empty answer (finish_reason={choice.finish_reason}) for: {query}")
    elif "</think>" in answer:
        print(f"WARNING: reasoning text leaked into the answer for: {query}")
    if choice.finish_reason == "length":
        print(f"WARNING: answer was cut off by the token cap for: {query}")

    return {
        "query": query,
        "answer": answer,
        "context_used": context,
        "model": config.LLM_MODEL,
        "thinking": config.REASONING_EFFORT != "none",
        "finish_reason": choice.finish_reason,
        "generation_time_ms": elapsed_ms,
        "prompt_tokens": usage.prompt_tokens if usage else None,
        "tokens_generated": usage.completion_tokens if usage else None,
    }
