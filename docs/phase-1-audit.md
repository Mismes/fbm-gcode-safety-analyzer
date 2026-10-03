# Phase 1 repository audit and migration design

Audit baseline: public `main` commit `70ba378c386466b6a278d2d2373889f9203ec973`.

## Scope and isolation

This audit uses only the public repository and synthetic G-code created by the
tests. No private research source, dataset, machine-production G-code, thesis
artifact, or canonical evidence was read or copied.

## Repository state

- The default and only checked-out branch is `main`, tracking `origin/main`.
- History contains three commits: the MIT-licensed repository skeleton, a
  README expansion, and the initial `main.py` prototype.
- Tracked project files are `.gitignore`, `LICENSE`, `README.md`, and `main.py`.
- There is no package metadata, command-line argument parser, test suite,
  configuration contract, CI, structured output, release, or GitHub Action.
- The host `python` command is unavailable. Phase 1 verification used the
  Codex workspace Python 3.12 runtime without changing the host configuration.

The live repository matches the handoff description. The only operational
environment mismatch is that the README mentions Python 3.10 while the audit
runtime is Python 3.12; the project does not yet declare supported versions.

## Current behavior

`GCodeChecker.run_check()` reads a file and returns separate string lists for
errors and warnings. It uppercases lines, skips blank lines and comments only
when `(` is the first non-whitespace character, remembers whether any `S` or
`F` character has appeared, warns for an explicitly written rapid Z below
2.0, and reports missing `S` or `F` on strings containing cutting G-codes.

Running `python main.py` prints start/end banners but never calls
`run_check()`. The input is hard-coded as `test.nc`; users cannot select a
file, profile, or output format, and process exit status does not represent
analysis findings.

The characterization suite records this baseline, including these defects:

- substring matching classifies `G10` as `G1`;
- inline comment text can set spindle-speed and feed flags;
- `M3`, `M4`, and `M5` spindle state is not tracked;
- any `S` or `F` character counts, even without a valid numeric word;
- rapid clearance ignores modal motion, positioning mode, units, and prior Z;
- file decoding and I/O failures have no stable diagnostic or exit contract;
- accumulated findings are not cleared if one checker instance runs twice.

These are observations, not the target v0.1.0 behavior. Phase 2 replaces the
prototype contract and rewrites the tests around the documented analyzer API.

## Smallest v0.1.0 architecture

Use a `src/fbm_gcode_safety/` package with a thin CLI and four internal
boundaries:

1. `parser.py` removes comments, tokenizes exact words, and returns typed
   blocks plus structural diagnostics. It does not apply machine rules.
2. `modal_state.py` applies the bounded G/M-code subset and exposes the state
   before and after each block.
3. `rules/` evaluates blocks and state against a validated immutable profile.
4. `reporters/` renders the same structured diagnostics as console, JSON, or
   SARIF without changing analysis decisions.

`diagnostics.py` owns stable rule identifiers and severities. `config.py`
loads a versioned TOML profile. `analyzer.py` coordinates parsing, state, and
rules, allowing CLI tests to remain separate from rule tests.

Use only the Python standard library at runtime for v0.1.0. TOML loading can
use `tomllib`, so the initial supported Python floor should be 3.11. Use
`pytest`, `ruff`, and `build` as development dependencies. CI should cover
Python 3.11, 3.12, and 3.13 on Windows and Linux.

## Migration sequence

1. Add `pyproject.toml`, package skeleton, diagnostic model, and a real
   `fbm-gcode-check` entry point with documented exit codes.
2. Replace substring scanning with comment-aware exact tokenization and
   conservative malformed-input diagnostics.
3. Add modal state for motion, units, positioning, spindle, speed, feed, and
   coordinates; then implement GSA001 through GSA006 against that state.
4. Add and validate the versioned TOML profile, including unknown-code policy.
5. Add console and JSON reporters, expand behavior tests, and retain only
   useful prototype regressions as target-contract tests.
6. Add SARIF, packaging checks, cross-platform CI, maintenance documents,
   synthetic examples, and the reusable GitHub Action.

Each step should leave the local checkout testable. External pushes, pull
requests, tags, releases, PyPI publication, Action publication, and program
application submission remain separate maintainer-authorized operations.

## Phase 2 definition of done

Phase 2 is complete when the package installs locally, the CLI accepts a G-code
path and optional profile, GSA001-GSA006 operate on the bounded documented
subset, console and JSON output follow stable schemas, and meaningful parser,
state, rule, reporter, and CLI tests pass on the audit runtime. SARIF, public CI,
maintenance documents, and release work remain Phase 3 and Phase 4 tasks.
