# Contributing

FramePeek welcomes focused bug fixes, tests, documentation, and features that
fit the current product scope.

## Setup

FramePeek requires Python 3.10 or newer.

```bash
git clone https://github.com/Salajalaludin/framepeek.git
cd framepeek
python -m venv .venv
```

Activate it with `.venv\Scripts\Activate.ps1` in PowerShell or
`source .venv/bin/activate` in a POSIX shell, then install and verify the
checkout:

```bash
python -m pip install -e ".[dev]"
python -m pytest --cov=framepeek --cov-report=term-missing --cov-fail-under=100
```

## Workflow

1. Search the Issues and open one when the work is not already tracked.
2. Create a focused branch from the latest `main`, such as
   `fix/12-clear-description`.
3. Add tests for behavior changes and update user documentation when the public
   API changes.
4. Open a draft pull request that links the Issue and records the exact
   verification command.
5. Mark the pull request ready only after its checks pass.

Keep changes small, avoid unrelated refactors, and never commit credentials,
private datasets, virtual environments, or generated caches.

By participating, you agree to follow the
[Code of Conduct](CODE_OF_CONDUCT.md).
