# FramePeek Release Workflow

This document defines how a version selected according to the
[versioning policy](FramePeek%20Versioning%20Policy.md) moves through:

1. git/GitHub;
2. TestPyPI;
3. PyPI.

The versioning policy decides **which version number to use**.

This document decides **how that version is published safely**.

---

# 1. Platform responsibilities

| Platform | Responsibility |
|---|---|
| Git/GitHub | Immutable source revision, tags, changelog, release notes |
| TestPyPI | Release-candidate packaging and installation validation |
| PyPI | Stable end-user package distribution |

The latest stable PyPI release and latest stable GitHub Release must always represent the same version.

TestPyPI may contain additional release candidates.

---

# 2. Stable synchronization rule

For stable version `X.Y.Z`, all of these must exist:

- `pyproject.toml` version `X.Y.Z`;
- git tag `vX.Y.Z`;
- GitHub Release `vX.Y.Z`;
- PyPI release `X.Y.Z`.

A release is not considered complete until all four agree.

Release-candidate tags do not count as stable GitHub releases.

---

# 3. Release-candidate format

Test releases use:

`X.Y.Zrc1`
`X.Y.Zrc2`
`X.Y.Zrc3`

Release candidates are published to TestPyPI only.

Do not intentionally publish RC packages to production PyPI.

Stable packages use:

`X.Y.Z`

and are published to production PyPI only.

---

# 4. Prepare the release

Determine the target version using the versioning policy. The consolidated
maintenance release follows 0.2.2 as 0.2.3; roadmap milestones do not consume
release numbers.

Before RC1:

- all intended implementation changes must be merged;
- relevant tests must exist;
- `CHANGELOG.md` must contain the intended release changes under `Unreleased`;
- local quality checks must pass.

Required checks:

- Ruff;
- mypy;
- pytest with required branch coverage;
- wheel and sdist build;
- strict package metadata validation;
- clean installation tests.

Run the same local checks as normal CI:

```bash
python -m pip install -e ".[dev,release]"
python -m ruff check .
python -m mypy src/framepeek
python -m pytest --cov=framepeek --cov-branch --cov-report=term-missing --cov-fail-under=100
python -m build --outdir dist/check
python -m twine check --strict dist/check/*
python scripts/verify_artifacts.py dist/check
```

Use a fresh output directory each time. [PyPA build](https://build.pypa.io/en/stable/)
produces an sdist and builds
the wheel from that sdist. `verify_artifacts.py` checks metadata,
README/license/typing contents, then installs each artifact in its own new
environment. Its smoke check asserts report keys, nested table columns, actual
values, and both schema versions; its public consumer is type-checked against
the installed package.

Set:

`version = "X.Y.Zrc1"`

in `pyproject.toml`.

Commit the RC version.

---

# 5. Traceability of release candidates

Every TestPyPI release candidate must correspond to one immutable git revision.

Recommended tag:

`vX.Y.ZrcN`

Example:

`vX.Y.Zrc1`

RC tags may exist on GitHub without creating a GitHub Release.

The stable synchronization requirement applies to stable GitHub Releases, not RC tags.

This makes every TestPyPI artifact traceable to exact source code.

---

# 6. Build an RC

Always use a fresh artifact directory; do not delete or mix older artifacts.

Build both:

- source distribution;
- wheel.

Validate both artifacts before upload.

Never reuse artifacts from another version.

Artifacts must contain the same version as `pyproject.toml`.

---

# 7. Publish the RC to TestPyPI

Upload the RC artifacts to TestPyPI.

A published version is immutable.

If an RC is broken, do not attempt to overwrite it.

Increment:

`rc1 → rc2 → rc3`

and repeat the complete process.

---

# 8. Test installation safely

TestPyPI is a separate package index and does not contain the complete dependency set available on PyPI.

For FramePeek, install runtime dependencies from production PyPI first.

Then install the exact FramePeek RC from TestPyPI without dependency resolution.

The clean environment must verify at minimum:

- package installation succeeds;
- `import framepeek` succeeds;
- `framepeek.__version__` equals the RC version;
- a minimal `profile()` call succeeds;
- wheel contents are correct;
- source-distribution installation succeeds.

Download both exact RC artifacts into a new directory and run the verifier
against them, with the checkout on that RC's revision/version. Dependencies
and type-check tools come from PyPI; the FramePeek artifact comes from TestPyPI.
Do not use a combined `--extra-index-url` for dependency resolution.

The tested package must be the downloaded TestPyPI artifact, not an editable local checkout.

---

# 9. RC failure rule

If any problem is found after publishing an RC:

1. fix the problem;
2. increment the RC number;
3. run all checks again;
4. create a new RC commit/tag;
5. build new artifacts;
6. upload the new RC to TestPyPI;
7. test the installed package again.

Example:

`X.Y.Zrc1`
→ packaging bug
→ `X.Y.Zrc2`

Never reuse `X.Y.Zrc1`.

---

# 10. RC freeze

Once an RC passes all validation, freeze its functional contents.

The final promotion may only change release metadata such as:

- `X.Y.ZrcN → X.Y.Z`;
- changelog release date.

Any functional source, dependency, API, or packaging change invalidates the tested RC and requires another RC.

---

# 11. Prepare the stable release

From the final successful RC:

1. remove the RC suffix;
2. finalize the changelog entry;
3. run the complete quality suite again;
4. commit the release;
5. create annotated tag `vX.Y.Z`.

The tag must point to the exact release commit.

Never move or recreate a published stable tag.

---

# 12. Stable build rule

Build stable artifacts only from the exact tagged release commit.

Use a fresh artifact directory for the tagged version.

Build once.

Run:

- artifact validation;
- wheel clean-install test;
- sdist clean-install test;
- version verification;
- smoke tests.

Do not rebuild artifacts after they have passed release validation.

The files that are validated are the files that must be published.

---

# 13. Publish to PyPI

Upload the verified stable artifacts to production PyPI.

After publishing, verify installation in a clean environment using the exact stable version.

Check:

- installed version;
- import;
- minimal profile execution;
- package metadata.

A PyPI version is immutable.

If the stable release contains a defect after publication, fix it in a new
version according to the versioning policy.

Never attempt to replace the existing release.

---

# 14. GitHub Release

Every stable PyPI release must have a corresponding GitHub Release.

For `X.Y.Z`:

- tag: `vX.Y.Z`;
- GitHub Release title: `vX.Y.Z`;
- release body: matching `CHANGELOG.md` section.

Built wheel and source-distribution files may be attached as GitHub Release assets for auditability.

No stable PyPI release is considered complete without its GitHub Release.

---

# 15. Historical release audit

Before publishing, compare all stable PyPI versions and stable git tags with
GitHub Releases. Exclude RC tags. Backfill missing GitHub Releases using the
existing immutable tag and matching changelog section; never recreate tags or
re-upload an existing PyPI version.

The 2026-10-03 audit confirmed published GitHub Releases for `v0.2.0`, `v0.2.1`,
and `v0.2.2`. The old instruction saying `v0.2.0` was missing is obsolete.
PyPI also contains `0.1.0` and `0.1.1`, and both immutable git tags exist, but
their GitHub Releases are missing. Backfill notes are prepared in
[historical release notes](historical-release-notes.md). Publishing those two
GitHub Releases remains a release-maintainer action; do not claim the historical
synchronization is complete before they are published.

---

# 16. Final synchronization checklist

A stable release is complete only when:

- [ ] `pyproject.toml` on `main` contains `X.Y.Z`
- [ ] git contains immutable tag `vX.Y.Z`
- [ ] the tag points to the intended release commit
- [ ] GitHub Releases contains `vX.Y.Z`
- [ ] PyPI contains `X.Y.Z`
- [ ] installed PyPI package reports `X.Y.Z`
- [ ] changelog contains the matching release section
- [ ] wheel passed clean-install verification
- [ ] sdist passed clean-install verification
- [ ] no RC version was published to production PyPI

---

# 17. Trusted Publishing target workflow

FramePeek should migrate from long-lived API tokens to PyPI Trusted Publishing.

Recommended automation model:

## RC

Push:

`vX.Y.ZrcN`

→ GitHub Actions  
→ build exact tagged revision  
→ test  
→ publish to TestPyPI.

## Stable

Publish GitHub Release:

`vX.Y.Z`

→ GitHub Actions  
→ build exact release tag  
→ run release validation  
→ publish through PyPI Trusted Publishing.

Using GitHub Release publication as the stable trigger has one useful property:

A production PyPI release cannot occur before the corresponding GitHub Release exists.

Use a dedicated release workflow and protected GitHub environment with manual approval for production publishing.

---

# 18. Release invariants

The following rules must never be violated.

### Immutable version

Once any version is published, never reuse it.

### Immutable stable tag

Never move a stable release tag.

### Tested artifacts are published artifacts

Never rebuild between final verification and upload.

### No hidden code after RC

Functional changes after a successful RC require a new RC.

### Stable GitHub and PyPI stay synchronized

Every PyPI stable release has exactly one matching GitHub stable release.

### Version follows change scope

Release workflow never chooses the version.

The versioning policy chooses the version before release preparation begins.
