# AGENTS.md

Rules for any AI assistant working on this project.

## Project
Local document Q&A (RAG) over the 5 PDFs in `documents/`. Everything in the pipeline runs on this machine through Ollama.

## Hard rules
- Local models only. Never use an Ollama tag with `cloud` in its name.
- Every number in `decision_log.md` or `README.md` must come from a file the code wrote
  (`benchmark_results.json`, `pipeline_outputs.json`, `retrieval_check.json`). Do not write numbers by hand or from memory.
- `decision_log.md` is written by the student, not the assistant.
- Do not read or edit `.env`.
- Every chat call passes `reasoning_effort=config.REASONING_EFFORT` and the token cap as `**{config.TOKEN_LIMIT_PARAM: config.MAX_TOKENS}`.
- All settings live in `config.py`. No hard-coded model names or URLs in other files.
- One step at a time (ingest, retrieve, generate, benchmark). Run it, check it, commit it.

## How to run (from this folder)
| Step | Command |
|---|---|
| Install | `uv sync` |
| Check Ollama is up | `curl http://localhost:11434/api/version` |
| Build the vector DB | `uv run python ingest.py` |
| Try retrieval alone | `uv run python retrieve.py "your question"` |
| Check retrieval on all test questions | `uv run python retrieval_check.py` |
| Ask one question end to end | `uv run python pipeline.py "your question"` |
| Run all test questions | `uv run python pipeline.py --all` |
| Benchmark models | `uv run python benchmark.py` |

## The check
After any change to chunking or retrieval: re-run `ingest.py`, then `retrieval_check.py`, and compare `questions_with_all_evidence` in `retrieval_check.json`.
After any change to generation: run `pipeline.py` on one question and confirm the answer is not empty and `finish_reason` is `stop`.
