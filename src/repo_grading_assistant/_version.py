"""Derive package version from top-level VERSION.py."""

from __future__ import annotations

from importlib import metadata
from pathlib import Path
import re

_VERSION_PATTERN = re.compile(r"__version__\s*=\s*['\"]([^'\"]+)['\"]")


def _read_version_from_file(version_path: Path) -> str | None:
    if not version_path.exists():
        return None

    text = version_path.read_text(encoding="utf-8")
    match = _VERSION_PATTERN.search(text)
    return match.group(1) if match else None


_version_file = Path(__file__).resolve().parents[2] / "VERSION.py"
__version__ = _read_version_from_file(_version_file) or metadata.version("repo-grading-assistant")
