# Changelog

Notable changes to FramePeek are recorded here.

## [Unreleased]

### Combined 0.2.3 maintenance release

The planned 0.2.3–0.2.8 milestones are consolidated into release 0.2.3, following
0.2.2 without skipping version numbers. Report schema remains 1.1 and
serialization schema remains 1.0. Publication and release date are pending.

### Performance

- Compute expensive column metadata on demand and cache it per analysis run;
  numeric summaries retain only the leading value instead of full Python
  frequency tables.
- Group missingness using packed masks in bounded chunks, preserving exact
  patterns, column labels, and first-occurrence ordering for ties.
- Add numeric, high-cardinality, wide, mixed, and missingness benchmarks that
  report runtime and peak traced memory, including opt-in million-row cases.

### Fixed

- Record warning sampling and actual parsed sample sizes from execution,
  including sparse categorical columns and reports without text parsing.
- Resolve the version from pyproject.toml when importing an uninstalled checkout.
- Return NaN coefficient of variation for nonpositive means and NaN outlier
  measurements when IQR analysis is not applicable.
- Require a majority of leading-zero values for that numeric-identifier
  heuristic, reducing false positives from isolated values.

### Maintenance

- Check Ruff, source typing, 100% branch coverage, wheel/sdist metadata and
  contents, isolated installs, report schemas, and consumer typing in normal CI.
- Test minimum Python/pandas alongside the latest supported Python/pandas pair.
- Complete package metadata and synchronize API, bounded formatting, statistical
  semantics, sampling, and release documentation.

## [0.2.2] - 2026-08-11

### Performance

- Reused one duplicate analysis across each profile run instead of computing it
  separately for the overview, duplicate report, and quality warnings.
- Added a pandas-native fast path for normal hashable data while retaining the
  structural fallback for nested, mixed-object, and unhashable values.
- Reused structural row identities when building duplicate groups.

## [0.2.1] - 2026-08-09

### Fixed

- Made frequency and duplicate analysis use actual-value hashability with a
  structural fallback for nested containers and NumPy arrays, plus safe scalar
  equality for unhashable custom objects.

## [0.2.0] - 2026-07-30

### Changed

- Added shared structural identity for duplicate and frequency analysis so
  lists, dictionaries, sets, nested values, and mixed object columns no longer
  require hashability or `repr()`-based equality.
- Replaced lossy string-key serialization with schema `1.0` envelopes that
  preserve mapping entries, DataFrame labels, tagged scalar types, and
  conversion fidelity.
- Renamed target-selection parameters to `target_column`.
- Reused correlation and outlier results throughout each `profile()` call.
- Exposed `framepeek.__version__` and marked the distribution as typed.
- Standardized finite numeric, integer, method, threshold, and DataFrame
  validation with clearer duplicate-column diagnostics.
- Replaced the monolithic `core` module with focused analysis, validation,
  warning, report, and public-type modules while preserving top-level imports.
- Reused per-column type, missingness, cardinality, and frequency metadata
  throughout each `profile()` call.
- Added public structured result types and explicit target interpretation
  through `target_type`.
- Added separate infinity statistics, explicit outlier limitations, and
  diagnostics for text normalization, mixed objects, numeric identifiers, and
  rare-category concentration.
- Added schema-versioned report metadata, explicit missing summaries, bounded
  text formatting, and JSON-compatible serialization.
- Added reproducible sampling for text-warning heuristics and recorded its use
  in report metadata.
- Added correlation column and row limits, subset, pair-only, top-pair, overflow,
  and Kendall safeguards.
- Added bounded runtime and peak-memory profiling benchmarks.
- Expanded edge-case tests to nullable and non-finite data, minimal frames,
  hashable column names, and non-mutation across the public analysis API.
- Enforced branch coverage and clean-wheel typing checks in CI.
- Added inter-column missingness patterns and optional shallow memory
  measurement.
- Added `quality_warnings` as the recommended compatibility-preserving name and
  advanced the report schema to 1.1.
- Added development-only Arrow dtype coverage and bounded property-based tests
  for numeric, missingness, correlation-schema, and non-mutation invariants.

## [0.1.1] - 2026-07-24

### Added

- Titled, untruncated console output through `print_report()`.

## [0.1.0] - 2026-07-24

### Added

- Functional profiling API for pandas DataFrames.
- Dataset, column, missing-value, duplicate, numeric, categorical, outlier,
  correlation, target, and warning analyses.
- Configurable analysis thresholds and non-mutating input handling.
- Tests with 100% statement coverage and automated CI on supported Python
  versions.
- Getting-started, API, contribution, and community documentation.
