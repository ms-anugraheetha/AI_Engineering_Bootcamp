| Metric | n | Local mean ± 2SE | Cloud mean ± 2SE | Cloud − local, per question (mean ± 2SE) | Verdict |
|---|---|---|---|---|---|
| Faithfulness | 18 | 0.771 ± 0.126 | 0.827 ± 0.180 | +0.056 ± 0.120 | no clear difference |
| Answer Relevancy | 18 | 0.838 ± 0.129 | 0.972 ± 0.056 | +0.135 ± 0.118 | cloud higher |
| Contextual Relevancy | 18 | 0.296 ± 0.109 | 0.289 ± 0.102 | -0.007 ± 0.040 | no clear difference |
| Contextual Recall | 18 | 0.704 ± 0.199 | 0.704 ± 0.199 | +0.000 ± 0.000 | no clear difference |
| Contextual Precision | 18 | 0.819 ± 0.117 | 0.763 ± 0.120 | -0.056 ± 0.062 | no clear difference |

| Run | Model | Median generation time (ms) | Slowest (ms) | Avg completion tokens | Empty or failed answers |
|---|---|---|---|---|---|
| local | qwen3.5:4b-q4_K_M | 10862 | 23143 | 118.0 | 0 |
| cloud | gpt-5.6-luna | 1132 | 2186 | 42.4 | 0 |
