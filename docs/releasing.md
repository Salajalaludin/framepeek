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
python -m build
python -m twine check --strict dist/*
```

For version `0.1.0`, the build produces:

```text
dist/framepeek-0.1.0.tar.gz
dist/framepeek-0.1.0-py3-none-any.whl
```

The version in `pyproject.toml` and `CHANGELOG.md` must match these filenames.

## Clean-install smoke test

Create and activate a disposable virtual environment outside the repository,
then run:

```bash
python -m pip install dist/framepeek-0.1.0-py3-none-any.whl
python -c "import pandas as pd; import framepeek as fp; report = fp.profile(pd.DataFrame({'value': [1, 2, None]})); assert len(report) == 10"
```

Run the install command from the repository root or replace the wheel path with
an absolute path. Confirm that package metadata reports version `0.1.0`:

```bash
python -c "from importlib.metadata import version; assert version('framepeek') == '0.1.0'"
```

## Authorized release step

Only after the checks above pass and release authorization is explicit:

1. Replace `Unreleased` on the `0.1.0` changelog entry with the release date.
2. Merge that change through the normal pull-request workflow.
3. Tag the exact merge commit as `v0.1.0`.
4. Publish the verified files from `dist/`.

Do not rebuild distributions between verification and publishing.
