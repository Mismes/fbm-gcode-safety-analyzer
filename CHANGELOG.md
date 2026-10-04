# Changelog

All notable changes are documented here. The project follows Semantic Versioning after its first release.

## [Unreleased]

## [0.1.0] - 2026-10-05

### Added

- Public synthetic corpus with explicit expected findings and CLI exit codes,
  reproduced through JSON/SARIF at all three failure thresholds after wheel installation.
- Quickstart walkthrough and maintainer feedback/release review guidance.

- Conservative invalidation of state after unsupported/malformed input.
- Finite-number and duplicate-word validation, lateral rapid clearance checks,
  and UTF-8 BOM support.
- Single-document batch JSON/SARIF, offline SARIF schema validation, coverage
  reporting, and installed-wheel tests in CI.

- Installable Python package and `fbm-gcode-check` command.
- Exact comment-aware word tokenizer and bounded modal-state engine.
- Version 1 TOML machine profiles.
- GSA001 through GSA006 structured diagnostics.
- Console, JSON, and SARIF 2.1.0 reporters.
- Synthetic examples, cross-platform CI, and a composite GitHub Action.

## [0.0.0] - 2026-09-20

- Initial proof-of-concept script.
