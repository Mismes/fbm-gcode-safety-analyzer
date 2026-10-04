# v0.1.0 release readiness

Preparation snapshot: 2026-10-05, before publication. Public operations were
separately authorized by the maintainer. See the Releases page for publication status.

This report supersedes the earlier 56-test candidate snapshot. The implementation
and public corpus were merged through PR #1 and PR #2. The release preparation
updates documentation only; package version remains 0.1.0 (Alpha).

## Behavior

The installable Python package provides bounded Fanuc-style static checks,
version 1 TOML profiles, GSA001-GSA006, console/JSON/SARIF output, batch CLI,
and a composite GitHub Action. Unsupported or malformed input invalidates modal
state. Warning policy and exit thresholds are configurable; analysis success
never establishes machine safety.

## Verified public baseline

Baseline: `965e6e4d428c523a1e1cbcc918b81e435f85ce87`.

- [Merged PR #1](https://github.com/Mismes/fbm-gcode-safety-analyzer/pull/1)
- [Merged PR #2](https://github.com/Mismes/fbm-gcode-safety-analyzer/pull/2)
- [Baseline CI](https://github.com/Mismes/fbm-gcode-safety-analyzer/actions/runs/37126578188): Windows/Linux, Python 3.11-3.13, success.
- [Baseline Action smoke](https://github.com/Mismes/fbm-gcode-safety-analyzer/actions/runs/37126578163): success.
- Existing test suite: 76 tests; baseline line coverage 96%.
- Public synthetic corpus: 9 cases, 54 JSON/SARIF and exit-policy checks.

These hosted results apply to the baseline commit, not to subsequent preparation
commits. A new release commit must pass its own hosted checks before tagging.
Detailed local preparation logs, distribution hashes and environment information
are retained in the maintainer's separate OSS output directory.

## Release gates

1. Review [release notes](release-notes-v0.1.0.md), supported subset and limitations.
2. Build wheel and sdist, and inspect contents for version, license and public-only files.
3. Install the actual artifacts in isolated environments, then check CLI examples,
   all tests, public corpus, and dependency consistency.
4. Obtain authorization to push the documentation branch, create a PR and merge
   after green hosted CI and Action smoke checks.
5. Tag the verified merged commit, publish Release notes and attach tested artifacts
   only with explicit authorization. Record the final tag/commit mapping and hashes.
6. Keep PyPI publication and any OSS program application separately authorized.

## Limits

SARIF is schema-validated but GitHub code-scanning upload is not claimed as tested.
Arc geometry, collision detection, tools, stock, fixtures, travel limits and
controller emulation are outside the supported contract. No CNC machine has
validated the synthetic corpus. Public adoption is not established by these tests.

No private research or thesis files are required for any release gate.
