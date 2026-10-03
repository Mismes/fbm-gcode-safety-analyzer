"""Offline validation against the vendored SARIF 2.1.0 schema."""

import json
from pathlib import Path

from jsonschema import Draft7Validator

from fbm_gcode_safety import analyze_text
from fbm_gcode_safety.reporters import sarif


def test_sarif_schema_accepts_empty_warning_error_and_malformed_results():
    schema = json.loads(Path(__file__).with_name("sarif-2.1.0.schema.json").read_text())
    validator = Draft7Validator(schema, format_checker=Draft7Validator.FORMAT_CHECKER)
    for source in ("G21\nG90\nG0 Z5", "G21\nG90\nG0 Z1", "G1 X2", "Gbad"):
        payload = json.loads(sarif.render(analyze_text(source, source_name="examples/part.nc")))
        validator.validate(payload)
    payload["runs"].append(payload["runs"][0])
    validator.validate(payload)
