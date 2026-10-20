# Security Policy

VerityAgent CodeProof is an alpha developer tool. Its heuristics are incomplete and must not be treated as a security certification.

## Reporting a vulnerability

Please do not publish exploitable details, credentials, or sensitive sample code in a public issue. Contact the project maintainers through the private contact channel listed on the VerityAgent profile/site, and include a safe reproduction, affected version, impact, and mitigation if known. Do not include live credentials in any report.

## Scope and current limits

- The built-in scanner is a small heuristic ruleset, not a comprehensive vulnerability database.
- The optional AI reviewer may receive diff contents. It is disabled by default and requires the explicit --ai flag.
- Repository tests are arbitrary project code. The --run-tests option is not a sandbox.
- CodeProof does not automatically patch, commit, or merge code.
- HTML reports escape repository-derived text, but users should still treat reports as sensitive project artifacts.
- Secret detection is heuristic. Revoke or rotate any real credential exposed in a repository; deleting a line alone does not invalidate a key.

## Safe operation

Inspect unfamiliar repositories before running tests. Use a disposable container or VM for untrusted code. Do not use AI mode with confidential changes unless the configured provider and your organization's policy permit it. Keep API keys in environment variables or a secret manager.
