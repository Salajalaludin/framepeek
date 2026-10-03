"""Resolve installed versions, with a source-checkout fallback on Python 3.10+."""

import re
from importlib import metadata
from pathlib import Path


def runtime_version() -> str:
    try:
        return metadata.version("framepeek")
    except metadata.PackageNotFoundError:
        source = Path(__file__).resolve().parents[2] / "pyproject.toml"
        project = (
            source.read_text(encoding="utf-8")
            .split("[project]", 1)[1]
            .split("\n[", 1)[0]
        )
        match = re.search(r'^version\s*=\s*"([^"]+)"', project, re.MULTILINE)
        if match is None:
            raise RuntimeError("Missing project version in pyproject.toml.") from None
        return match.group(1)
