# Benchmark methodology

CodeProof does not publish performance or accuracy claims until a reproducible labeled benchmark exists.

## Planned evaluation design

1. Collect small, permissively licensed or synthetic code changes with documented intended behavior.
2. Include defect-introducing and benign changes to measure false positives as well as detections.
3. Have at least two reviewers label each case and record disagreements.
4. Freeze the test set before tuning scanner rules.
5. Report precision, recall, false-positive rate, false-negative rate, runtime, and language/framework coverage.
6. Separate deterministic rule results from LLM-assisted findings and report model name, configuration, and evaluation date.
7. Repeat model-based evaluations with fixed prompts and publish the limitations of non-deterministic outputs.

## Current status

The repository includes a synthetic demonstration diff and a deliberately buggy example module. They are teaching fixtures, not a statistically meaningful benchmark. No accuracy, speed, or bug-prevention percentage is claimed.
