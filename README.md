# FBM G-code Safety Analyzer

A conservative static analyzer for a bounded Fanuc-style G-code subset. It tracks modal state, applies configurable checks, and emits stable console, JSON, or SARIF diagnostics for local use and CI.

> **Safety notice:** This tool cannot prove that G-code is safe and does not perform complete collision detection, controller emulation, or machine certification. Always use controller-specific verification, simulation, machine limits, a dry run, and qualified operator review before execution.

## Install and run

Python 3.11 or newer is required.

```bash
git clone https://github.com/Mismes/fbm-gcode-safety-analyzer.git
cd fbm-gcode-safety-analyzer
python -m pip install .
fbm-gcode-check part.nc
fbm-gcode-check part.nc --profile machine.toml
fbm-gcode-check part.nc --format json
fbm-gcode-check part.nc --format sarif > results.sarif
```

Try the included synthetic examples before supplying your own files:

```bash
fbm-gcode-check examples/safe.nc --fail-on warning
fbm-gcode-check examples/unsafe.nc --format json
python tools/validate_examples.py
```

The first command exits 0, the second exits 1 with deliberate findings, and the
last checks the public corpus against independently specified expected findings
and exit codes. See the [walkthrough](docs/quickstart.md) and
[validation contract](docs/public-validation.md).

The built-in profile uses millimetres and a 2.0 mm rapid-Z clearance. For real review work, create and version a profile appropriate to the machine and workflow; the example is at `examples/generic-3axis-mm.toml`.

This is an unreleased candidate. A PyPI installation command will be added
after publication. Checks supplement simulation and operator review.

Malformed blocks, unsupported words, and unsupported commands invalidate modal
state. Following motion must establish its modes, spindle, feed, and position
again. Unsupported reporting may be configured, but it does not make those
commands supported. Empty/comment-only files fail analysis. A unit change
invalidates the modal feed; set F again before cutting. Repeated numeric
addresses and multiple spindle commands in a block are rejected.

## Supported subset

| Area | Supported in v0.1.0 |
| --- | --- |
| Input | blank lines, `N` line numbers, uppercase/lowercase words |
| Comments | parenthesized comments and `;` to end of line |
| Numbers | signed integers and decimal values |
| Motion | `G0/G00`, `G1/G01`, `G2/G02`, `G3/G03` |
| Units | `G20` inch, `G21` millimetre |
| Positioning | `G90` absolute, `G91` incremental |
| Spindle | `M3/M03`, `M4/M04`, `M5/M05`, modal `S` |
| Feed | modal `F` |
| Geometry words | `X`, `Y`, `Z`, `I`, `J`, `K`, `R` |

Anything outside this table is unsupported. The profile decides whether an unsupported word is ignored, warned, or treated as an error. The analyzer does not claim support for controller macros, canned cycles, tool changes, offsets, compensation, coordinate systems, or controller-specific syntax.

## Diagnostics

| Code | Default severity | Meaning |
| --- | --- | --- |
| `GSA001` | warning | Rapid target Z is below the configured clearance. |
| `GSA002` | error | Cutting motion lacks an active spindle and positive speed. |
| `GSA003` | error | Cutting motion lacks a positive modal feed rate. |
| `GSA004` | error | Input is malformed or structurally contradictory. |
| `GSA005` | profile policy | A command or word is unsupported. |
| `GSA006` | warning/error | Unit or positioning state is unsafe or indeterminate. |

Console output has a stable shape:

```text
part.nc:18: GSA002 ERROR Cutting move encountered without an active spindle and positive speed
```

JSON contains `status`, `source`, and a `diagnostics` array. Every diagnostic contains `rule`, `severity`, `line`, and `message`, with `column` when known. SARIF output follows SARIF 2.1.0 and includes physical file locations.

Multiple paths can be supplied: `fbm-gcode-check first.nc second.nc --format json`.
Batch JSON contains an aggregate `status` and a `files` array of the single-file
objects. Batch SARIF is one document containing a run per file. Paths within
the current working directory use escaped relative URIs in SARIF. If any input
cannot be read, exit 2 is returned with no partial report.

## Exit codes and failure threshold

- `0`: analysis completed and did not reach the selected failure threshold;
- `1`: analysis completed and reached the selected finding threshold;
- `2`: invocation, profile, decoding, or file I/O prevented valid analysis.

`--fail-on error` is the default. `--fail-on warning` makes any finding fail, and `--fail-on never` reports findings without returning exit code 1.

For a stricter gate, use `--fail-on warning` with `unknown_code = "error"` in
the profile. Default warning policy permits warning-only unsupported input to
exit 0; ignoring unsupported commands can suppress those findings entirely.
Neither policy establishes that an unsupported program is safe.

## Machine profiles

Profiles use a versioned TOML contract:

```toml
[profile]
schema_version = 1
name = "generic-3axis-mm"
units = "mm"
safe_rapid_z = 2.0

[rules]
require_spindle_for_cutting = true
require_feed_for_cutting = true
unknown_code = "warning"
```

`units` accepts `mm` or `inch`. `unknown_code` accepts `ignore`, `warning`, or `error`. Missing, invalid, or unknown-version profile values stop analysis with exit code 2.

## GitHub Action

For the current unreleased snapshot, pin the reviewed main commit. Update this
pin after reviewing a later commit; a released tag will be documented after publication:

```yaml
- uses: Mismes/fbm-gcode-safety-analyzer@5a6b7aa3253bfd5e9fd482066ab7aae09132b454
  with:
    paths: path/to/part.nc
    profile: path/to/machine.toml
    format: console
    fail-on: error
```

The repository smoke-tests the local Action with the synthetic safe example. No published Action or release is claimed until the maintainer publishes one.

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest --cov=fbm_gcode_safety --cov-report=term-missing
python -m ruff check .
python -m build
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [ROADMAP.md](ROADMAP.md). All fixtures must be synthetic or otherwise clearly licensed for public use.

## Known limits

The parser implements only the table above and is not controller-equivalent. Arc geometry is tokenized but not geometrically validated. Rapid clearance is a configured Z-target check, not collision detection. Initial coordinates are unknown until established, and incremental motion from an unknown coordinate is rejected. The analyzer does not evaluate stock, fixtures, tools, kinematics, travel limits, acceleration, or macro execution.

Licensed under the MIT License.
