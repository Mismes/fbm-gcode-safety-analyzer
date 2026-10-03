# Public validation contract

The corpus in `examples/validation/cases.json` is authored for this MIT-licensed
project using synthetic inputs only. It contains no production programs,
private research, customer data, or imported research evidence. Expectations
are written explicitly in the manifest, not generated from analyzer output.

Each finding is `[rule, severity, source_line]`. Exact findings are compared
without relying on message wording or ordering. JSON status, SARIF version,
exit code and empty stderr are also checked. A missing, extra, relocated, or
changed-severity finding fails validation.

| Case | Contract being exercised |
| --- | --- |
| baseline | Modal spindle/feed inheritance in millimetres |
| inch | Inch-to-profile conversion for rapid Z |
| incremental | Relative positions after explicit initialization |
| lateral | Inherited low Z on lateral rapid motion |
| spindle | Feed does not replace spindle activation |
| feed | Spindle activation does not replace feed |
| duplicate | Duplicate axis words are rejected |
| unsupported | Default policy reports unsupported G10 |
| clearance | Rapid Z must be known |

Run `python tools/validate_examples.py` from a checkout with the package installed.
CI runs it after building and installing the wheel on Windows/Linux and Python
3.11-3.13. Source tests additionally validate SARIF against the vendored schema
and exercise parser, profile, malformed state, and batch behavior.

## Interpretation

54 passing checks demonstrate agreement with these nine authored contracts.
They are not 54 independent machining scenarios, accuracy percentages, evidence
of real adoption, false-negative rates, collision validation, or certification.
No CNC controller has been used to validate this corpus. Geometry, tooling,
stock, fixtures, offsets, and full controller semantics are outside its scope.

## Add a reproducible report

1. Start from a minimal synthetic `.nc` reproducer.
2. Include the profile, package/commit version, command, output, and expected result.
3. State the rule rationale and controller assumptions; identify unsupported words.
4. Discuss false positives and false negatives before changing expectations.
5. Add the reproducer and explicit expectations, then rerun tests and this corpus.

The maintainer must review changes to expected findings. Updating the manifest
solely to make a failing implementation pass defeats this contract.

## Before a public release

- Review supported behavior and release notes at the intended commit.
- Require green matrix CI, Action smoke tests, corpus validation and wheel installation.
- Check source distributions include profiles, corpus, runner, docs and licenses.
- Record immutable commit and CI URLs; distinguish local results from hosted results.
- Publish only after explicit maintainer authorization, then verify documented install paths.
- Collect genuine user feedback through issues and preserve linked fixes over time.

Public use, independent review, downloads and ecosystem impact must be evidenced
separately. The repository does not currently claim these from its synthetic tests.
