## Retrieval quality (source: eval_results_local.json)
- Contextual Relevancy 0.296 ± 0.109, Contextual Recall 0.704 ± 0.199, Contextual Precision 0.819 ± 0.117
- Lowest Contextual Recall (0.00): q07, q11, q15, q18
- Lowest Contextual Relevancy: q18 (0.00), q17 (0.04), q04 (0.08), q05 (0.10), q02 (0.11)
- Lowest Contextual Precision: q18 (0.00), q16 (0.61), q15 (0.62), q04 (0.64), q17 (0.67)

## Generation quality (source: eval_results_local.json)
- Faithfulness 0.771 ± 0.126, Answer Relevancy 0.838 ± 0.129
(each value is mean ± 2×SE, n = 18, SE = standard deviation / sqrt(n))

## Mean ± 2×SE per metric (n = 18)
| Metric | Local | Cloud |
|---|---|---|
| Faithfulness | 0.771 ± 0.126 | 0.827 ± 0.180 |
| Answer Relevancy | 0.838 ± 0.129 | 0.972 ± 0.056 |
| Contextual Relevancy | 0.296 ± 0.109 | 0.289 ± 0.102 |
| Contextual Recall | 0.704 ± 0.199 | 0.704 ± 0.199 |
| Contextual Precision | 0.819 ± 0.117 | 0.763 ± 0.120 |

## Pass counts
| Rule | Local | Cloud |
|---|---|---|
| Strict, all five metrics >= 0.7 | 0/18 | 0/18 |
| Faithfulness and Answer Relevancy >= 0.7 | 10/18 | 14/18 |
| My hand ratings | 15/18 | not rated |

## Unanswerable questions (string check)
- local: 2 of 2 refused correctly (q17, q18)
- cloud: 2 of 2 refused correctly (q17, q18)

## Judge vs my ratings (local, Faithfulness and Answer Relevancy >= 0.7)
- agree on 9 of 18
- q03: judge fail, I passed
- q08: judge fail, I passed
- q11: judge pass, I failed
- q12: judge fail, I passed
- q14: judge fail, I passed
- q15: judge pass, I failed
- q16: judge fail, I passed
- q17: judge fail, I passed
- q18: judge fail, I passed
