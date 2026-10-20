# Examples

These files are demonstration fixtures, not production-ready application code.

## Synthetic diff

From the repository root, run:

    python -m pip install -e .
    verity-codeproof demo

The demo reads examples/demo.diff and emits findings for intentionally risky added lines. The credential-like value is fake sample text only; it is not a real API key.

## Seeded-bug sample

The module in buggy_project/ intentionally contains a faulty percentage calculation. It shows how a meaningful test catches a behavioral regression. It is kept outside the configured project test path so it does not make CodeProof's own test suite fail.

To try the sample manually, use a temporary environment and run pytest in the sample folder. The expected-behavior test should fail until the seeded bug is fixed. Do not copy this deliberately buggy implementation into a real project.
