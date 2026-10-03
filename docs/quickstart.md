# Reproduce a first review

Use Python 3.11+ and install from the repository as described in the README.
All commands below run from the repository root. These are synthetic text
examples and must not be sent to a machine.

## A program with no configured findings

```bash
fbm-gcode-check examples/safe.nc --profile examples/generic-3axis-mm.toml --fail-on warning
```

Expected: exit 0 and no console findings. The program explicitly establishes
units and absolute positioning, retracts to Z5, activates the spindle, and
establishes feed before cutting. Later blocks inherit spindle and feed.
No findings means only that these bounded checks did not flag this input.

## A program with deliberate findings

```bash
fbm-gcode-check examples/unsafe.nc --profile examples/generic-3axis-mm.toml --format json
```

Expected: exit 1, JSON status `failed`, and these findings:

| Line | Rule | Severity | Reason |
| --- | --- | --- | --- |
| 4 | GSA001 | warning | Rapid Z1 is below configured Z2 clearance. |
| 5 | GSA002 | error | Cutting has no active spindle and positive speed. |
| 5 | GSA003 | error | Cutting has no positive modal feed. |
| 6 | GSA005 | warning | G10 is outside the supported subset. |

In PowerShell inspect `$LASTEXITCODE`; in Bash inspect `$?` immediately after
the command. Deliberate exit 1 is expected here, not an installation error.

## Warnings and failure policy

```bash
fbm-gcode-check examples/validation/lateral-low-z.nc --fail-on error
fbm-gcode-check examples/validation/lateral-low-z.nc --fail-on warning
```

Both report GSA001 at lines 3 and 4. The first exits 0; the second exits 1.
`--fail-on never` returns 0 even for error findings; it is intended for reporting,
not as a gate. JSON status describes error findings independently of exit policy.
For example, warning-only input can have status `passed` and exit 1 under the
warning threshold. Input/profile errors still exit 2 under every threshold.

## Reproduce the corpus

```bash
python tools/validate_examples.py
```

Expected: 9 cases, 54 checks, 54 passed, empty failures, exit 0. The runner uses
the installed package, does not execute G-code, and needs no machine or network.
Each input is checked in JSON and SARIF under error, warning, and never policies.
The [validation contract](public-validation.md) explains what these checks establish.
