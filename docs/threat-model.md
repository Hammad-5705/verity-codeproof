# Threat model

VerityAgent CodeProof analyzes software changes. Its input may be incomplete, adversarial, or sensitive. This document describes the alpha release's intended trust boundaries.

## Assets to protect

- Source code and proprietary implementation details.
- API credentials and other secrets in diffs.
- Integrity of the developer's working tree.
- Accuracy and provenance of verification findings.
- CI credentials and repository write permissions.

## Trust boundaries

| Boundary | Default behavior | Remaining risk |
|---|---|---|
| Git diff to local scanner | Process locally, no network | Heuristics miss issues and can raise false alarms |
| Diff to AI provider | Disabled unless --ai is set | User may intentionally send confidential content; provider handling follows that provider's terms |
| Repository test runner | Disabled unless --run-tests is set | Test code can perform arbitrary operations; timeout is not isolation |
| Report rendering | HTML-escape source-derived values | Reports may still reveal paths or sensitive evidence to their reader |
| CI integration | Read-only repository permissions in workflow examples | Workflow permissions and third-party actions must be reviewed by project maintainers |

## Adversaries and failure modes

- A malicious patch hides prompt-injection text in comments or strings to influence AI review.
- A developer accidentally includes credentials in a diff.
- A repository contains tests that read files, access the network, or modify the environment.
- A heuristic labels benign code as risky or fails to detect a real vulnerability.
- An LLM invents a defect or overlooks a real behavior change.
- A report is treated as a guarantee rather than a decision-support artifact.

## Mitigations in this release

- No AI call occurs without explicit user opt-in.
- The AI prompt treats source as untrusted input and source submission is bounded.
- Git and pytest are invoked using argument vectors, not shell strings derived from repository content.
- Test execution uses a fixed pytest command and a timeout, but is explicitly documented as not sandboxed.
- Findings carry source, confidence, location, evidence, and recommendations.
- HTML output escapes repository-derived values.
- No automatic code modifications, commits, or merges occur.

## Non-goals

This release does not prove correctness, replace human review, provide a complete SAST scanner, isolate hostile code, enforce organizational policy, or guarantee that a passing test suite covers all relevant behavior.

## Recommended deployment posture

For untrusted projects, run CodeProof in a disposable VM or container with no production credentials and restricted network access. Review diffs before enabling AI mode. Use least-privilege CI tokens and never add repository write permissions solely to publish a report.
