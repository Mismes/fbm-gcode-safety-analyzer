"""Versioned machine-profile loading and validation."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


class ProfileError(ValueError):
    """Raised when a machine profile cannot be used safely."""


@dataclass(frozen=True, slots=True)
class MachineProfile:
    schema_version: int
    name: str
    units: str
    safe_rapid_z: float
    require_spindle_for_cutting: bool
    require_feed_for_cutting: bool
    unknown_code: str


def default_profile() -> MachineProfile:
    return MachineProfile(
        schema_version=1,
        name="generic-3axis-mm",
        units="mm",
        safe_rapid_z=2.0,
        require_spindle_for_cutting=True,
        require_feed_for_cutting=True,
        unknown_code="warning",
    )


def _require(table: dict[str, object], key: str, expected: type | tuple[type, ...]) -> object:
    if key not in table:
        raise ProfileError(f"missing required profile value: {key}")
    value = table[key]
    invalid_boolean = isinstance(value, bool) and expected is not bool
    if invalid_boolean or not isinstance(value, expected):
        names = (
            ", ".join(item.__name__ for item in expected)
            if isinstance(expected, tuple)
            else expected.__name__
        )
        raise ProfileError(f"profile value {key} must be {names}")
    return value


def load_profile(path: str | Path) -> MachineProfile:
    profile_path = Path(path)
    try:
        data = tomllib.loads(profile_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ProfileError(f"cannot load profile {profile_path}: {exc}") from exc

    profile = data.get("profile")
    rules = data.get("rules")
    if not isinstance(profile, dict) or not isinstance(rules, dict):
        raise ProfileError("profile must contain [profile] and [rules] tables")

    schema_version = _require(profile, "schema_version", int)
    name = _require(profile, "name", str)
    units = _require(profile, "units", str)
    safe_rapid_z = _require(profile, "safe_rapid_z", (int, float))
    require_spindle = _require(rules, "require_spindle_for_cutting", bool)
    require_feed = _require(rules, "require_feed_for_cutting", bool)
    unknown_code = _require(rules, "unknown_code", str)

    if schema_version != 1:
        raise ProfileError(f"unsupported profile schema_version: {schema_version}")
    if not name.strip():
        raise ProfileError("profile name must not be empty")
    if units not in {"mm", "inch"}:
        raise ProfileError("profile units must be 'mm' or 'inch'")
    if not float("-inf") < float(safe_rapid_z) < float("inf"):
        raise ProfileError("safe_rapid_z must be finite")
    if unknown_code not in {"ignore", "warning", "error"}:
        raise ProfileError("unknown_code must be 'ignore', 'warning', or 'error'")

    return MachineProfile(
        schema_version=schema_version,
        name=name,
        units=units,
        safe_rapid_z=float(safe_rapid_z),
        require_spindle_for_cutting=require_spindle,
        require_feed_for_cutting=require_feed,
        unknown_code=unknown_code,
    )
