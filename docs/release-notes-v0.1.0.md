# v0.1.0 — first public release (prepared notes)

These notes are ready for maintainer review. This file does not establish that
a tag, GitHub Release, PyPI package or program application has been published.

## Purpose

FBM G-code Safety Analyzer provides lightweight static preflight checks for
CAM/FBM workflows and CI. It checks a bounded Fanuc-style subset and reports
problems before downstream simulation or controller verification.

## Included

- Python 3.11+ package and `fbm-gcode-check` CLI; no runtime dependencies.
- Exact comment-aware parsing and modal units, positioning, spindle and feed tracking.
- Configurable version 1 TOML profiles and GSA001-GSA006 diagnostics.
- Console, JSON and SARIF 2.1.0 output, including single-document batch output.
- Composite GitHub Action, Windows/Linux CI on Python 3.11-3.13.
- Synthetic examples and nine-case public corpus with 54 output/exit checks.

## Install and try

After the Release exists, download its wheel and install it:

```bash
python -m pip install ./fbm_gcode_safety_analyzer-0.1.0-py3-none-any.whl
fbm-gcode-check --help
fbm-gcode-check program.nc --profile machine.toml --fail-on warning
```

Alternatively, download and extract the source distribution:

```bash
python -m pip install ./fbm_gcode_safety_analyzer-0.1.0.tar.gz
```

The source distribution also contains `examples/`, `tools/`, `tests/` and `docs/`.
From its extracted directory, run `python tools/validate_examples.py` to reproduce
the nine-case corpus. The wheel installs the CLI/library; it does not install
the source examples into your working directory.

PyPI publication is separate. Do not use a registry installation command until
the maintainer announces and verifies that publication.

## Result interpretation

- Exit 0: configured finding threshold was not reached.
- Exit 1: analysis completed and reached that threshold.
- Exit 2: invocation, profile or input could not be analyzed.

Default unsupported-command policy is warning and default threshold is error;
warning-only input can exit 0. Choose `--fail-on warning` and an appropriate
profile for a stricter gate. `--fail-on never` is reporting-only.

## Limits and feedback

This Alpha release cannot certify machine safety, detect all collisions, emulate
a controller or validate full arc geometry. Macros, canned cycles, offsets,
compensation, tool changes and controller-specific dialects are unsupported.
Passing checks does not mean collision-free or production-qualified.

All included examples are synthetic and must not be run on a machine. Use
simulation, controller-specific verification and qualified operator review.

Please report issues with a minimal synthetic reproducer, profile, exact version,
command, observed output and expected behavior. Do not submit private research,
thesis, customer or production-machine files.

License: MIT.
