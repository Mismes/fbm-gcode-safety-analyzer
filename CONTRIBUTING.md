# Contributing

Thank you for improving the analyzer. Open an issue before a large behavioral change so the supported dialect and safety contract stay bounded.

## Development workflow

1. Use Python 3.11 or newer and install `.[dev]` in a virtual environment.
2. Add behavior-focused tests for every parser, state, or rule change.
3. Run `python -m pytest`, `python -m ruff check .`, and `python -m build`.
4. Update the supported-command matrix and diagnostic reference when behavior changes.

Fixtures must be synthetic or explicitly licensed for public redistribution. Do not submit customer, production-machine, private research, credential, or personally identifying data. Rule proposals should state the exact trigger, expected severity, false-positive risks, controller assumptions, and tests.

Keep claims narrow: passing analysis does not certify a program as safe.
