# Day 12: evaluating my local RAG pipeline

**Pipeline evaluated:** my own Day 11 pipeline (local RAG over five NovaTech PDFs: Ollama qwen3.5:4b-q4_K_M, nomic-embed-text, ChromaDB, chunks 512/50, top-K 8), compared with the cloud model gpt-5.6-luna. Judge: gpt-5.4-mini with DeepEval.

**AI assistant used:** Claude (Sonnet 5.5) in the Claude app. It helped me write `compare.py` and `report_stats.py`, add my two own attacks to `security_probe.py`, and draft the report from my own hand ratings and notes. The ratings, the security verdicts and the decisions are mine.

## Where to run it
The scripts import `retrieve.py`, `generate.py` and `config.py` and use `chroma_db/` from my Day 11 folder, so they run from there. This folder holds copies of the results and the report.

## Files
- `evaluation_report.md` - the report
- `eval_pipeline.py` - DeepEval run (`uv run python eval_pipeline.py local` or `cloud`)
- `security_probe.py` - security probes, including my two own attacks (hidden instruction, data exfiltration)
- `compare.py`, `compare_output.md` - local vs cloud comparison
- `report_stats.py`, `report_stats_output.md` - the numbers used in the report (means, pass counts, judge vs my ratings)
- `pipeline_outputs_local.json`, `pipeline_outputs_cloud.json` - answers (local file has my hand ratings)
- `eval_results_local.json`, `eval_results_cloud.json` - judge scores
- `security_results_local.json`, `security_results_cloud.json` - probe results with my verdicts
