# Combined AoI-Fidelity Statistical Results

Each combination uses 100 paired synthetic network scenarios. Confidence intervals are paired percentile bootstrap intervals with 10,000 resamples. Raw p-values are exact two-sided McNemar tests; Holm step-down correction controls familywise alpha at 0.05.

| Maximum AoI | Minimum Fidelity | Scenarios | Baseline Feasibility (%) | Temporal Feasibility (%) | Difference (pp) | Paired Bootstrap 95% CI (pp) | McNemar Raw p | Holm-Adjusted p | Significant After Holm (0.05) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2.0 | 0.5 | 100 | 7.0 | 8.0 | 1.0 | [0.00, 3.00] | 1 | 1 | No |
| 2.0 | 0.6 | 100 | 7.0 | 8.0 | 1.0 | [0.00, 3.00] | 1 | 1 | No |
| 2.0 | 0.7 | 100 | 7.0 | 7.0 | 0.0 | [0.00, 0.00] | 1 | 1 | No |
| 2.0 | 0.8 | 100 | 7.0 | 7.0 | 0.0 | [0.00, 0.00] | 1 | 1 | No |
| 4.0 | 0.5 | 100 | 15.0 | 33.0 | 18.0 | [11.00, 26.00] | 7.6293945e-06 | 9.1552734e-05 | Yes |
| 4.0 | 0.6 | 100 | 15.0 | 33.0 | 18.0 | [11.00, 26.00] | 7.6293945e-06 | 9.1552734e-05 | Yes |
| 4.0 | 0.7 | 100 | 15.0 | 27.0 | 12.0 | [6.00, 18.00] | 0.00048828125 | 0.00390625 | Yes |
| 4.0 | 0.8 | 100 | 12.0 | 13.0 | 1.0 | [0.00, 3.00] | 1 | 1 | No |
| 6.0 | 0.5 | 100 | 35.0 | 67.0 | 32.0 | [23.00, 41.00] | 4.6566129e-10 | 7.4505806e-09 | Yes |
| 6.0 | 0.6 | 100 | 35.0 | 64.0 | 29.0 | [20.00, 38.00] | 3.7252903e-09 | 5.5879354e-08 | Yes |
| 6.0 | 0.7 | 100 | 33.0 | 51.0 | 18.0 | [11.00, 26.00] | 7.6293945e-06 | 9.1552734e-05 | Yes |
| 6.0 | 0.8 | 100 | 25.0 | 27.0 | 2.0 | [0.00, 5.00] | 0.5 | 1 | No |
| 8.0 | 0.5 | 100 | 64.0 | 89.0 | 25.0 | [17.00, 34.00] | 5.9604645e-08 | 8.3446503e-07 | Yes |
| 8.0 | 0.6 | 100 | 64.0 | 87.0 | 23.0 | [15.00, 31.00] | 2.3841858e-07 | 3.0994415e-06 | Yes |
| 8.0 | 0.7 | 100 | 58.0 | 74.0 | 16.0 | [9.00, 24.00] | 3.0517578e-05 | 0.0002746582 | Yes |
| 8.0 | 0.8 | 100 | 36.0 | 37.0 | 1.0 | [0.00, 3.00] | 1 | 1 | No |
