# Decision Log: Local RAG Pipeline

## Machine
- **Hardware:** Intel Core i5-12450H (12th Gen), 15.7 GB RAM, NVIDIA GeForce RTX 2050 (4 GB dedicated memory) plus Intel UHD Graphics. Windows, Ollama 0.40.16 running natively.
- **`ollama ps` with my main model loaded:**
NAME              ID               SIZE      PROCESSOR          CONTEXT    RUNNER    UNTIL       

qwen3.5:4b-q4_K_M    d8b0f5e9760c    3.9 GB    52%/48% CPU/GPU    8192       llamacpp    4 minutes from now   

## Model Selection
- **Chosen LLM:** qwen3.5:4b-q4_K_M. 
- **Thinking:** OFF
- **Why:** I chose this model after comparing with qwen3.5:2b-q4_K_M. Even though both model performed nearly well in the categories: "factual", "reasoning","summarization" and "structured", the 2b model didnt perform well for "code" and "instruction following" category.Rating for 2b was 3 for both the category code and intruction following while the rating for 4b was 5 refer benchmark_results.json.  
- **What I considered but rejected:** I considered qwen3.5:2b-q4_K_M even though it produces response faster there were some mistakes in the responses so i rejected the model. For example in instruction_following category the instructions says "write 3 bullet points and each points should be under 10 words" the model response had more than 10 words for each bullet point, the model didnt followed the instruction correctly .

## Embedding Model
- **Chosen:** nomic-embed-text
- **Why:** It is small and fast.It was given in the brief and it also runs locally through ollama,so the documents stay on the machine.

## Parsing
- **Extractor:** Plain

## Chunking Strategy
- **Chunk size:** 512
- **Overlap:** 50
- **Why:** i choose  512/50 after comparing it with 1000/150 and the results were 14/16 for 512/50 and 12/16 for 1000/150. So i choose the baseline 512/50 .

## Retrieval Configuration
- **Top-K:** 8
- **Context window:** 8192
- **Why:** I chose this from the brief.I didnt test other context.It works as well because the largest prompt we had was below 1500

## Observations
- **What worked well:**  Questions with the answer in one clear passage were answered correctly (q01–q06, q08, q10, q12). The conflict questions q13 and q14 worked when both sources were retrieved. The unanswerable ones (q17, q18) were refused correctly. All 18 runs finished with `stop` and thinking off
- **What failed:** The right chunk was not always in the top 8, so the model never saw it: q11 (budget split), q15 (handbook says ~110 for Lisbon) and q09 (per-product prices, cut off in the chunk). The model answered faithfully from what it got, so these are retrieval failures.
- **Traps I hit:** The retrieval gives 8chunks even when the answer was unanswerable. also after rating almost 13 Question, I wanted to rerun `pipeline.py --all`, but rerunning overwrites `pipeline_outputs.json` and would erase all my ratings and notes, so I didn't.
- **Local vs cloud expectations:** My expectation is cloud will be more faster than local.And the quality on harder questions will better with larger cloud models. But privacy and high will be the trade off for Cloud model.

## If I Had More Time / Better Hardware
- 
If i had more time or better hardware I would try different model especially larger models. Try more chunk size other than ones i tried. Try different context size,other embedding models and extraction modes.