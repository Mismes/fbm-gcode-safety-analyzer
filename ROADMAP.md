# Roadmap

## v0.1.0 — bounded static analyzer

- Package, CLI, profile validation, GSA001-GSA006, JSON, SARIF, CI, and Action.
- Document the exact Fanuc-style subset and non-certification limits.

## After v0.1.0

- Collect public, synthetic false-positive and false-negative cases.
- Extend the public validation corpus from reproducible user reports; multi-file JSON/SARIF is already implemented.
- Evaluate controller dialect modules only when each dialect has public documentation, a precise boundary, and dedicated tests.
- Consider deeper arc validation and configurable travel limits as separately specified rules.

Release timing depends on review and evidence. Unsupported dialects or machine semantics will not be added merely to increase feature count.
