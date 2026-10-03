# Historical GitHub release backfill

Audit date: 2026-10-03. PyPI contains five stable releases, 0.1.0 through 0.2.2.
GitHub Releases now contains all five versions. Releases v0.1.0 and v0.1.1
were backfilled on 2026-10-03 with the following changelog-derived notes.
The original tag targets were preserved, neither release was marked latest,
and no package was rebuilt or uploaded to PyPI.

## v0.1.0

### Added

- Functional profiling API for pandas DataFrames.
- Dataset, column, missing-value, duplicate, numeric, categorical, outlier,
  correlation, target, and warning analyses.
- Configurable analysis thresholds and non-mutating input handling.
- Tests with 100% statement coverage and automated CI on supported Python
  versions.
- Getting-started, API, contribution, and community documentation.

## v0.1.1

### Added

- Titled, untruncated console output through `print_report()`.

This describes the historical release. Current formatting is bounded; see
the API reference for the current behavior.
