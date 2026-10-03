"""FBM G-code Safety Analyzer public API."""

from .analyzer import AnalysisResult, analyze_file, analyze_text
from .config import MachineProfile, ProfileError, default_profile, load_profile

__all__ = [
    "AnalysisResult",
    "MachineProfile",
    "ProfileError",
    "analyze_file",
    "analyze_text",
    "default_profile",
    "load_profile",
]

__version__ = "0.1.0"
