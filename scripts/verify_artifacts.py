"""Validate both artifacts, then install and type-check each in a fresh venv."""

import argparse
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import venv
from email.parser import BytesParser
from pathlib import Path
from zipfile import ZipFile


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dist", type=Path)
    parser.add_argument("--constraints", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    project = (root / "pyproject.toml").read_text(encoding="utf-8")
    expected = re.search(r'^version\s*=\s*"([^"]+)"', project, re.MULTILINE).group(1)
    artifacts = sorted(args.dist.resolve().glob("framepeek-*"))
    assert len(artifacts) == 2, (
        "Use a fresh directory containing exactly one wheel and one sdist"
    )
    assert {p.suffix for p in artifacts} == {".whl", ".gz"}
    constraints = ["-c", str(args.constraints.resolve())] if args.constraints else []
    readme = (root / "README.md").read_text(encoding="utf-8").strip()
    for artifact in artifacts:
        if artifact.suffix == ".whl":
            with ZipFile(artifact) as archive:
                names = archive.namelist()
                assert "framepeek/py.typed" in names
                assert any(name.endswith("/licenses/LICENSE") for name in names)
                metadata = archive.read(
                    next(name for name in names if name.endswith(".dist-info/METADATA"))
                )
        else:
            with tarfile.open(artifact) as archive:
                names = archive.getnames()
                for suffix in (
                    "/src/framepeek/py.typed",
                    "/README.md",
                    "/LICENSE",
                    "/pyproject.toml",
                ):
                    assert any(name.endswith(suffix) for name in names), suffix
                metadata = archive.extractfile(f"framepeek-{expected}/PKG-INFO").read()
        parsed = BytesParser().parsebytes(metadata)
        assert parsed["Name"] == "framepeek" and parsed["Version"] == expected
        assert parsed["Requires-Python"] == ">=3.10"
        assert parsed["License-Expression"] == "Apache-2.0"
        assert "Typing :: Typed" in parsed.get_all("Classifier", [])
        assert len(parsed.get_all("Project-URL", [])) >= 4
        assert readme in parsed.get_payload().replace("\r\n", "\n")
        with tempfile.TemporaryDirectory(prefix="framepeek-install-") as temp:
            directory = Path(temp)
            venv.EnvBuilder(with_pip=True).create(directory / "venv")
            python = (
                directory
                / "venv"
                / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            )
            subprocess.run(
                [
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    "--no-cache-dir",
                    *constraints,
                    str(artifact),
                    "mypy>=1.10",
                    "pandas-stubs>=2.0",
                ],
                check=True,
                cwd=directory,
                timeout=300,
            )
            subprocess.run(
                [str(python), "-m", "pip", "check"],
                check=True,
                cwd=directory,
                timeout=60,
            )
            for name in ("release_smoke.py", "typecheck_consumer.py"):
                shutil.copyfile(root / "tests" / name, directory / name)
            subprocess.run(
                [str(python), "-I", "release_smoke.py", expected],
                check=True,
                cwd=directory,
                timeout=60,
            )
            subprocess.run(
                [
                    str(python),
                    "-m",
                    "mypy",
                    "--no-incremental",
                    "typecheck_consumer.py",
                ],
                check=True,
                cwd=directory,
                timeout=120,
            )
        print(f"Verified {artifact.name}", flush=True)


if __name__ == "__main__":
    main()
