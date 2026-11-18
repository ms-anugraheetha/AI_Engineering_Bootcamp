# Local RAG: document Q&A on local models

Answers questions about five internal PDFs (NovaTech Solutions) using Ollama and ChromaDB. Nothing leaves the machine.

**AI assistant used:** Claude (Sonnet 5.5) in the Claude app, to scaffold the code and draft the test questions. The model inside the pipeline is local.

## Setup
1. Install Ollama and pull the models:
   ```
   ollama pull qwen3.5:4b-q4_K_M
   ollama pull qwen3.5:2b-q4_K_M
   ollama pull nomic-embed-text
   ```
2. Set the Ollama context to 8192 (see `capstone_brief.md`), restart Ollama, and check that `ollama ps` shows CONTEXT 8192 with a model loaded.
3. `uv sync`

## Run
```
uv run python ingest.py            # rebuilds chroma_db/ from documents/
uv run python benchmark.py         # writes benchmark_results.json
uv run python retrieval_check.py   # writes retrieval_check.json
uv run python pipeline.py --all    # writes pipeline_outputs.json
```
One question: `uv run python pipeline.py "How many PTO days do I get?"`

## Files
- `config.py` - all settings (swap provider with environment variables only)
- `ingest.py`, `retrieve.py`, `generate.py`, `pipeline.py` - the pipeline
- `benchmark.py`, `retrieval_check.py` - measurement scripts
- `test_questions.json` - 18 questions (6 easy, 6 medium, 4 hard, 2 unanswerable)
- `decision_log.md` - my reasoning

## Results

**Test questions:** 
`test_questions.json`: 18 questions (6 easy, 6 medium, 4 hard, 2 unanswerable).

**Pipeline:** 
`pipeline_outputs.json`, qwen3.5:4b-q4_K_M, thinking off, top-K 8, context 8192:
- Passed: 15 of 18: failures are q09, q11 and q15.
- All 18 rows finished with `stop`. Largest prompt was 1312 tokens.

**Retrieval:** 
| Setting | Found | File |
|---|---|---|
| 512 / 50, top-K 5 | 12/16 | `retrieval_baseline_512_50_k5.json` |
| 512 / 50, top-K 8 | 14/16 | `retrieval_k8.json` |
| 1000 / 150, top-K 8 | 12/16 | `retrieval_1000_150_k8.json` |

**Model benchmark** (`benchmark_results.json`, 6 prompts each, thinking off):
| Model | Rating | Time per prompt | Tokens/s |
|---|---|---|---|
| qwen3.5:4b-q4_K_M | 5 on all six | 5.4 s to 23.4 s | 0.9 to 12.3 |
| qwen3.5:2b-q4_K_M | 5 on four; 3 on code and instruction_following | 2.9 s to 8.5 s | 13.7 to 44.6 |

Decisions and explanations are in `decision_log.md`.
