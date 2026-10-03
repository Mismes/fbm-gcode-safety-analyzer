# v0.1.0 local release-candidate report

Status: review candidate branch pushed for hosted CI; not merged, tagged, or released.

## Resulting behavior

The original hard-coded demonstration script has been replaced by an
installable Python package and `fbm-gcode-check` command. The analyzer now uses
exact comment-aware word tokenization, tracks the documented motion, unit,
positioning, spindle, speed, feed, and coordinate state, and reports GSA001
through GSA006 as structured diagnostics.

A version 1 TOML machine profile owns the rapid-Z threshold and rule policy.
Console, JSON, and SARIF 2.1.0 outputs share the same findings. Exit codes
separate analysis findings from invocation and configuration failures, while
`--fail-on` controls the CI threshold.

The repository also contains synthetic safe and unsafe programs, Windows/Linux
CI configuration, a reusable composite Action with path/profile/format/failure
inputs, an Action smoke workflow, and the maintenance documents required for a
small public project.

## Verification evidence

- 56 behavior-focused tests pass on Windows with Python 3.12.
- Ruff reports no lint errors.
- Source distribution and wheel build successfully.
- The installed CLI help, safe example, unsafe JSON output, and Action runner
  have been exercised locally.
- Hosted CI passed on Windows and Linux with Python 3.11, 3.12, and 3.13:
  <https://github.com/Mismes/fbm-gcode-safety-analyzer/actions/runs/35527312681>
- The hosted Action smoke workflow passed:
  <https://github.com/Mismes/fbm-gcode-safety-analyzer/actions/runs/35527312697>
- The mandatory comment, exact `G10`, and modal spindle/feed regressions are
  covered, including `G10` following an active `G1` mode.

## Acceptance checklist

- [x] Package builds and installs in an isolated local environment.
- [x] `fbm-gcode-check --help` works.
- [x] The bounded Fanuc-style subset is documented.
- [x] Comments and exact word boundaries are tested.
- [x] Modal spindle, feed, unit, positioning, and coordinate behavior is tested.
- [x] A validated machine profile replaces the hard-coded threshold.
- [x] GSA001-GSA006 and stable console/JSON contracts exist.
- [x] SARIF 2.1.0 required structure is tested.
- [x] Exit codes and failure thresholds are tested.
- [x] More than 30 meaningful tests pass.
- [x] Windows/Linux CI and an Action smoke workflow are configured and pass.
- [x] Synthetic safe/unsafe fixtures are included.
- [x] README, contributing, security, changelog, roadmap, conduct, issue, and
  pull-request files are present.
- [x] Limitations and the non-certification statement are prominent.
- [x] The checkout contains no private or production G-code or research artifact.
- [x] Hosted Windows/Linux CI has passed.
- [x] The GitHub Action has passed its hosted smoke workflow.

## Remaining review risks

SARIF has structural tests but has not yet been uploaded to GitHub code
scanning. The Action runner handles newline-separated paths and glob patterns;
machine-readable output is most useful with one path because each analyzed
file emits its own complete JSON or SARIF document.

The parser remains intentionally bounded. Arc geometry is not validated,
rapid-Z checking is not collision detection, and initial coordinates remain
unknown until established. Passing analysis is never evidence that a program
is safe to execute.

## Publication boundary

The `codex/v0.1.0-rc` branch and its commits were pushed with maintainer
authorization to run hosted checks. No pull request, merge, tag, release, PyPI
package, advertised Action release, or program application has been created.
Those operations remain separate maintainer-authorized actions.
