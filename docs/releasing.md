# Releasing FramePeek

This checklist prepares and verifies a release. Creating a tag or publishing to
an index is a separate, explicitly authorized step.

## Build and validate

Start from a clean checkout of the intended release commit:

```bash
python -m pip install -e ".[dev,release]"
python -m ruff check .
python -m mypy src/framepeek
python -m pytest --cov=framepeek --cov-report=term-missing --cov-fail-under=100
python -m build --outdir dist/0.2.0
python -m twine check --strict dist/0.2.0/*
```

For version `0.2.0`, the build produces:

```text
dist/0.2.0/framepeek-0.2.0.tar.gz
dist/0.2.0/framepeek-0.2.0-py3-none-any.whl
```

The version in `pyproject.toml` and `CHANGELOG.md` must match these filenames.

## Clean-install smoke test

Create and activate a disposable virtual environment outside the repository,
then run:

```bash
python -m pip install dist/0.2.0/framepeek-0.2.0-py3-none-any.whl
python -c "import pandas as pd; import framepeek as fp; report = fp.profile(pd.DataFrame({'value': [1, 2, None]})); assert len(report) == 11"
```

Run the install command from the repository root or replace the wheel path with
an absolute path. Confirm that package metadata reports version `0.2.0`:

```bash
python -c "from importlib.metadata import version; assert version('framepeek') == '0.2.0'"
```

## Authorized release step

Only after the checks above pass and release authorization is explicit:

1. Move `Unreleased` changes into a dated `0.2.0` changelog entry.
2. Merge that change through the normal pull-request workflow.
3. Tag the exact merge commit as `v0.2.0`.
4. Publish the verified files from `dist/0.2.0/`.

Do not rebuild distributions between verification and publishing.
