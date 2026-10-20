# Contributing to VerityAgent CodeProof

Thanks for helping make code verification more useful, explainable, and safe.

## Principles

- Evidence before claims: findings should reference the changed file and line when possible.
- Conservative defaults: never send source to an AI provider unless the caller explicitly opts in.
- Deterministic checks first: an LLM suggestion must not be described as an executed test.
- Human control: do not add automatic edits, commits, or merges without a separately reviewed design.
- Reproducibility: every bug report should include the smallest diff or fixture that demonstrates it.

## Development setup

1. Use Python 3.10 or newer.
2. Create and activate a virtual environment.
3. Install dependencies with: python -m pip install -e ".[dev]".
4. Run python -m compileall -q src tests, ruff check src tests, and pytest.

## Pull requests

- Keep changes focused and include tests for behavior changes.
- Update the README and relevant docs when a command, safety boundary, or output format changes.
- Do not commit credentials, proprietary code, customer data, generated virtual environments, or private reports.
- For scanner rules, document the evidence pattern, severity rationale, false-positive risks, and recommended action.
- For provider-related work, include mocked tests so CI does not require network access or API keys.
- Do not weaken a test merely to make CI pass; explain the intended behavior and add a regression case.

## Reporting a bug

Include the OS, Python version, CodeProof version, command used, sanitized sample diff, actual output, and expected output. Remove secrets and sensitive source before opening an issue.

## Project identity

This is a VerityAgent open-source project. Contributions should preserve the project's focus on evidence-first verification and transparent limitations.
