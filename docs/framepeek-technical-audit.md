# FramePeek Technical Audit

**Repository:** `Salajalaludin/framepeek`
**Audited commit:** `72c82e1`
**Audit date:** 29 July 2026
**Scope:** correctness, data integrity, API consistency, performance, typing, packaging, maintainability, testing, CI, and release readiness.

---

## Executive Summary

FramePeek has improved significantly from its initial implementation. The package now includes:

- separated analysis, validation, warning, report, serialization, and type modules;
- reusable per-profile analysis context;
- typed public results;
- `py.typed`;
- runtime version exposure;
- branch coverage;
- property-based tests;
- warning sampling;
- correlation safeguards;
- machine-readable serialization;
- missingness patterns;
- bounded report formatting.

The previously identified correlation-method inconsistency, outlier-configuration inconsistency, and duplicate computation of correlations/outliers have been fixed and covered by regression tests.

The remaining highest-risk issues are no longer basic architecture problems. They concern **silent data corruption**, **failure on valid pandas object data**, and **full-profile behaviour that cannot be configured consistently**.

The most urgent findings are:

1. Serialization can silently lose category data because dictionary keys are coerced to strings.
2. Unhashable values such as lists and dictionaries can crash `overview()`, `duplicates()`, `categorical()`, and therefore `profile()`.
3. `profile()` cannot expose correlation overflow and sampling controls, causing crashes on wide numeric data and large Kendall analysis.
4. Report metadata does not record all effective configuration and can incorrectly claim that sampling was used.
5. The release guide and release assertions are outdated relative to the current report schema.

These findings should block the next public release until corrected.

---

## Remediation Checklist

- [x] 1. Prevent serialization collisions and silent data loss ([#43](https://github.com/Salajalaludin/framepeek/issues/43), [#44](https://github.com/Salajalaludin/framepeek/pull/44)).
- [x] 2. Handle unhashable DataFrame values safely ([#45](https://github.com/Salajalaludin/framepeek/issues/45)).
- [ ] 3. Expose correlation safeguards through `profile()`.
- [ ] 4. Make report metadata complete and accurate.
- [ ] 5. Update release documentation, assertions, and version.
- [ ] 6. Reuse duplicate analysis throughout a profile.
- [ ] 7. Make analysis-context frequency tables lazy.
- [ ] 8. Add safeguards for missing-pattern analysis.
- [ ] 9. Clarify correlation output versus computation options.
- [ ] 10. Avoid repeated validation inside full profiles.
- [ ] 11. Remove internal parameters from public signatures.
- [ ] 12. Split `analysis.py` by moderate analytical domains.
- [ ] 13. Remove warning-module dependencies on private analysis helpers.
- [ ] 14. Define unambiguous column-selection semantics.
- [ ] 15. Align standalone and full-profile configuration.
- [ ] 16. Return explicit correlation execution status.
- [ ] 17. Add performance regression benchmarks.
- [ ] 18. Strengthen metadata typing.
- [ ] 19. Export all missing-result types.
- [ ] 20. Run the full quality contract in CI.
- [ ] 21. Test minimum and latest supported pandas.
- [ ] 22. Complete distribution metadata.
- [ ] 23. Add a source-tree runtime-version fallback.
- [ ] 24. Correct coefficient-of-variation semantics.
- [ ] 25. Use nullable non-applicable outlier results.
- [ ] 26. Improve numeric-identifier detection.
- [ ] 27. Refine automatic target inference.

---

# Severity Classification

| Priority | Meaning |
|---|---|
| **P0** | Release blocker: data loss, incorrect output, or reproducible crash in normal supported usage |
| **P1** | High priority: major maintainability, performance, API, typing, CI, or reproducibility weakness |
| **P2** | Important refinement: statistical semantics, ergonomics, diagnostics, and future scalability |

---

# P0 — Release-Blocking Findings

## 1. Serialization Can Silently Lose Data

### Problem

`to_serializable()` converts dictionary keys to strings.

Values that are different in Python can therefore become the same serialized key. For example:

- integer `1`
- string `"1"`

Both become `"1"`.

This can overwrite one category entry without raising an exception. The serialized report remains apparently valid but contains incorrect data.

This is more severe than a crash because users may trust a report that is silently wrong.

### Affected areas

- categorical frequency dictionaries;
- any report dictionary using non-string keys;
- integer, boolean, tuple, datetime, or mixed-type category values;
- serialized objects containing nested mappings;
- downstream JSON exports.

### Required corrections

- Do not use raw category values as dictionary keys in machine-readable output.
- Represent frequency data as records containing explicit `value` and `count` fields.
- Preserve DataFrame index, columns, and data explicitly during serialization.
- Add a versioned serialization schema.
- Detect key collisions before conversion.
- Define how non-standard Python values are represented.
- Distinguish exact and lossy conversions.

### Required tests

- integer `1` and string `"1"` in the same category column;
- boolean `True` and integer `1`;
- tuple labels;
- datetime labels;
- nullable categories;
- mixed category types;
- correlation matrix row and column labels;
- serialization round-trip expectations;
- explicit collision detection.

### Recommended issue title

**Prevent serialization key collisions and silent report data loss**

---

## 2. Unhashable Data Values Crash Multiple Public Functions

### Problem

Valid pandas object columns may contain:

- lists;
- dictionaries;
- sets;
- nested objects;
- mixed scalar and nested values.

FramePeek currently performs hash-dependent operations without one shared fallback. As a result, unhashable values can crash:

- `overview()`;
- `duplicates()`;
- `categorical()`;
- `profile()`.

The warnings implementation already contains a limited fallback for duplicate counting, which proves that the package intends to inspect this type of data. However, the safeguard is not shared across the rest of the package.

### Root causes

- direct `df.duplicated()` calls;
- direct `value_counts()` calls;
- direct `groupby()` over unhashable values;
- conversion of category counts to dictionaries;
- inconsistent use of `repr()` fallbacks.

### Required corrections

Create a shared internal value-handling layer that supports:

- safe duplicate detection;
- safe frequency counting;
- safe grouping;
- stable analysis identity;
- separate display representation;
- separate serialization representation;
- collision detection;
- indication that original values were unhashable or transformed.

Do not patch each public function independently.

Using only `repr()` is insufficient because two different objects can produce the same representation. Identity keys and display values must be treated separately.

### Required tests

- repeated lists;
- repeated dictionaries;
- nested lists and dictionaries;
- sets;
- mixed scalar and nested objects;
- two different objects with identical `repr()`;
- individual public functions;
- full `profile()`;
- non-mutation of the original DataFrame.

### Recommended issue title

**Add shared safe handling for unhashable DataFrame values**

---

## 3. `profile()` Does Not Expose Correlation Safeguards

### Problem

The standalone correlation function supports:

- numeric-column limits;
- overflow behaviour;
- row sampling;
- column subsets;
- matrix exclusion;
- top-pair limits;
- minimum periods.

The full `profile()` function does not expose these controls.

Consequences:

- 51 or more numeric columns can cause `profile()` to raise `ValueError`;
- Kendall correlation on more than 10,000 rows cannot be used through `profile()`;
- users cannot select correlation columns from the full-report API;
- users cannot choose to skip, sample, or reduce correlation output.

### Required corrections

Expose correlation controls through `profile()`:

- selected columns;
- maximum numeric columns;
- overflow behaviour;
- sampled rows;
- include matrix;
- top pairs;
- minimum periods;
- correlation random state, if separated from warning sampling.

A full convenience report should not unexpectedly fail on a wide dataset without providing a configuration path.

### Recommended behaviour

When correlation is skipped, return explicit execution status instead of indistinguishable empty DataFrames.

Record:

- whether correlation was computed;
- whether it was skipped;
- why it was skipped;
- selected columns;
- input row count;
- analysed row count;
- whether sampling was applied;
- method used.

### Required tests

- exactly 50 numeric columns;
- 51 numeric columns;
- hundreds of numeric columns;
- `overflow="skip"` through `profile()`;
- selected correlation columns through `profile()`;
- Kendall with 10,001+ rows;
- sampled Kendall through `profile()`;
- target correlation consistency after sampling or skipping.

### Recommended issue title

**Expose correlation limits and sampling through `profile()`**

---

## 4. Report Metadata Is Incomplete and Sometimes Incorrect

### Problem A: incomplete configuration

The report records only part of the public configuration.

Configuration currently omitted includes parameters such as:

- top categorical values;
- missing thresholds;
- warning missing threshold;
- high-cardinality ratio;
- imbalance ratio;
- minimum outlier sample size;
- rare-category settings;
- future correlation controls.

A report cannot be reproduced reliably without all parameters that influenced it.

### Problem B: inaccurate warning-sampling metadata

Sampling metadata is inferred from:

- total DataFrame row count;
- existence of any categorical column.

Actual warning sampling is based on the number of non-missing values in each individual categorical column.

A large DataFrame with a sparse categorical column can therefore claim sampling was used when no column was sampled.

### Required corrections

- Record every effective public configuration parameter.
- Generate execution metadata from actual analysis execution, not pre-analysis assumptions.
- Record sampling per analysis and preferably per column.
- Record population size, sample size, random state, exact/sampled status, and skipped status.
- Separate user configuration from execution outcome.
- Add typed metadata structures.

### Required tests

- all public `profile()` parameters appear in metadata;
- sparse categorical columns;
- multiple categorical columns where only some are sampled;
- no categorical columns;
- sampled correlation;
- skipped correlation;
- exact versus sampled execution.

### Recommended issue title

**Make report configuration and execution metadata complete and truthful**

---

## 5. Release Documentation and Release Assertions Are Outdated

### Problem

The release guide still assumes an older package state.

Outdated items include:

- hard-coded release version `0.1.1`;
- hard-coded artifact paths;
- release instructions that move unreleased changes into `0.1.1`;
- smoke test expecting ten report keys;
- current report now containing eleven top-level keys because of metadata;
- report schema now at version 1.1;
- changed return structure for missingness analysis.

Following the current release guide can fail even when the package itself is working.

### Required corrections

- Remove hard-coded release versions.
- Read the version from package metadata or a release variable.
- Validate expected report keys rather than only report length.
- Build and test both wheel and source distribution.
- Run strict metadata validation.
- Clearly identify breaking, fixed, changed, and added sections in the changelog.
- Choose a new package version appropriate to the API and schema changes.

### Versioning note

The current unreleased changes are larger than a patch-only fix. They include:

- renamed parameters;
- changed report schema;
- changed missing-result structure;
- new public result types;
- new warnings;
- new metadata;
- new serialization behaviour.

These changes should not be published again as `0.1.1`.

### Recommended issue title

**Update release contract for the current report schema and package version**

---

# P1 — High-Priority Findings

## 6. Duplicate Analysis Is Still Recomputed

Within one `profile()` execution, duplicate information is calculated in multiple places:

- dataset overview;
- duplicate analysis;
- data-quality warnings.

Correlation and outlier reuse have been implemented successfully, but duplicate reuse has not.

### Required corrections

- Compute the duplicate mask once.
- Reuse duplicate totals in overview and warnings.
- Reuse repeated rows and grouped duplicates where appropriate.
- Store the precomputed duplicate result in the per-run context.
- Add a function-call regression test.

---

## 7. Analysis Context Computes Full Frequency Tables for Every Column

The analysis context calculates `value_counts()` for all columns, including numeric columns with potentially millions of unique values.

This can create substantial memory and CPU overhead before the analysis requiring those counts begins.

### Required corrections

- Compute full frequency tables lazily.
- Restrict full counts to categorical and boolean columns by default.
- Use `nunique()` or specialised operations for numeric columns.
- Cache only values actually reused.
- Add high-cardinality numeric benchmarks.

---

## 8. Missing-Pattern Analysis Can Become a Major Bottleneck

Missingness patterns are currently assembled by iterating row by row in Python and constructing tuples of missing column names.

Potential problems:

- cost grows with rows × columns;
- every unique pattern is retained;
- high-width datasets can create large tuple objects;
- no sampling or limit is available;
- full `profile()` always computes patterns.

### Required corrections

- Add an option to disable missing-pattern analysis.
- Add a maximum number of returned patterns.
- Add column and row safeguards.
- Consider row sampling.
- Use vectorised or bitmask-based representation where practical.
- Record exact versus sampled pattern analysis in metadata.

---

## 9. Correlation Output Options Do Not Reduce Core Computation

`include_matrix=False` and `top_pairs` currently reduce returned output but do not prevent calculation of the full correlation matrix.

### Required corrections

- Document that these options currently reduce output size only.
- Avoid presenting them as computational optimisations.
- Consider block-based or selected-pair calculations for future performance work.
- Benchmark output-only versus actual computational savings.

---

## 10. Public Functions Repeat Validation During Full Profiles

The full report validates the DataFrame, creates a context that validates again, and calls public analysis functions that validate again.

### Required corrections

- Preserve strict validation on public entry points.
- Introduce validated internal implementations.
- Avoid repeated validation when a trusted per-run context is provided.
- Keep internal execution paths separate from public wrappers.

---

## 11. Internal Parameters Leak Into Public Signatures

Public functions expose internal parameters such as:

- `_context`;
- `_correlation_result`;
- `_outlier_result`.

These appear in:

- autocomplete;
- API introspection;
- generated documentation;
- static type information.

### Required corrections

- Keep public signatures limited to supported user configuration.
- Move dependency injection into private implementation functions.
- Use internal orchestration helpers for precomputed results.

---

## 12. `analysis.py` Is Becoming a New Monolith

The former monolithic core module has been split, but `analysis.py` now contains most major analytical domains.

### Suggested structure

A moderate split is preferable:

- dataset-level analysis;
- column-level analysis;
- statistical analysis;
- target analysis;
- shared utilities.

Avoid creating one file per tiny function.

---

## 13. Warning Module Depends on Private Analysis Helpers

The warning module relies on private analysis helpers for percentage calculation and type inference.

### Required corrections

- Use metadata already present in the analysis context.
- Move generic helpers to a shared internal utility module.
- Avoid coupling one feature module to another module’s private API.

---

## 14. Column Selection API Is Ambiguous

Selection parameters use a generic sequence of hashable column names.

Potential ambiguities:

- a plain string can be interpreted as a sequence of characters;
- a tuple column label can be interpreted as multiple labels;
- duplicate selected columns are not clearly rejected;
- non-numeric requested correlation columns can be silently omitted.

### Required corrections

- Define single-label versus multi-label input clearly.
- Reject ambiguous bare strings when a collection is required.
- Support tuple labels explicitly.
- Reject duplicate selections.
- Report requested non-numeric columns rather than silently dropping them.
- Add selection-specific tests.

---

## 15. Standalone APIs Are Less Configurable Than `profile()`

Standalone numeric target analysis cannot configure its correlation method, sampling, column selection, or overflow behaviour.

Standalone quality warnings do not expose the same target interpretation override as the full report.

### Required corrections

- Align relevant standalone parameters with `profile()`.
- Or simplify target analysis and separate feature-target relationships into a dedicated function.
- Ensure equivalent operations do not behave differently depending on entry point.

---

## 16. Skipped Correlations Are Indistinguishable From Empty Correlations

When correlation overflow is skipped, the function returns empty DataFrames.

This looks the same as:

- no numeric columns;
- no valid pairs;
- all undefined correlations;
- intentionally skipped analysis.

### Required corrections

Return execution status containing:

- computed;
- skipped;
- reason;
- selected columns;
- method;
- input rows;
- analysed rows;
- sampled.

---

## 17. Benchmarking Is Only a Smoke Test

The current benchmark script prints elapsed time and Python allocation peak. It does not provide regression thresholds or historical comparison.

### Required additions

- 49, 50, 51, 100, and 500 numeric-column cases;
- high-cardinality numeric data;
- nested object data;
- missing-pattern stress cases;
- repeated duplicates;
- serialisation stress cases;
- stored baselines;
- scheduled performance runs;
- process-level memory measurement beyond Python-only allocation tracking.

---

# P1 — Typing and Packaging

## 18. Metadata Typing Is Too Weak

`ProfileResult` currently types metadata as a generic dictionary.

### Required corrections

Add nested typed structures for:

- report metadata;
- configuration;
- sampling metadata;
- execution status;
- correlation execution;
- serialisation schema.

---

## 19. Missing Result Types Are Not Fully Exported

`MissingResult` and `MissingRowsResult` exist but are not exposed consistently through the top-level package API.

### Required corrections

- Export all public result types.
- Add them to `__all__`.
- Add consumer typing tests.
- Document their stability contract.

---

## 20. CI Does Not Run the Full Declared Quality Contract

Current CI covers tests, wheel creation, `py.typed`, wheel installation, and a limited consumer typing test.

It does not run all checks described in project documentation.

### Required additions

- Ruff;
- mypy against package source;
- branch coverage;
- wheel build;
- source distribution build;
- strict package metadata check;
- clean wheel install;
- clean source distribution install;
- consumer typing from installed artifact;
- minimum pandas compatibility;
- latest pandas compatibility;
- optional scheduled pandas prerelease compatibility.

---

## 21. Minimum Supported Pandas Is Not Explicitly Tested

The package declares support for pandas 2.0 and newer, but ordinary dependency installation will usually test only a recent pandas version.

### Required additions

Use a dependency matrix including:

- Python 3.10 with pandas 2.0.x;
- latest supported Python with latest pandas;
- optional scheduled pandas prerelease build.

---

## 22. Distribution Metadata Is Incomplete

Recommended additions:

- project URLs;
- issue tracker;
- documentation URL;
- changelog URL;
- keywords;
- classifiers;
- development status;
- intended audience;
- typing classifier;
- maintainer metadata.

---

## 23. Runtime Version Lookup Has No Source-Tree Fallback

Runtime version exposure relies directly on installed distribution metadata.

### Required correction

Provide a safe fallback for source-tree execution or use a generated internal version module.

---

# P2 — Statistical and Behavioural Refinements

## 24. Coefficient of Variation Can Be Misleading for Non-Positive Means

Current calculation can return a negative coefficient of variation when the mean is negative.

### Required correction

Either:

- use absolute mean;
- mark CV not applicable for non-positive means;
- or attach an applicability/limitation field.

---

## 25. Zero-IQR Results Report Zero Outliers While Marked Not Applicable

Returning `outlier_count=0` can be interpreted as a valid finding even though the analysis declares that the method is not applicable.

### Required correction

Use nullable values for count and percentage when the method is not applicable.

---

## 26. Numeric-Identifier Detection Is Too Sensitive

A single sampled value with a leading zero can influence the classification of the entire column.

### Required correction

- use a proportion threshold;
- expose confidence;
- add false-positive tests;
- distinguish postal codes, phone numbers, IDs, and dirty numeric fields.

---

## 27. Automatic Target Inference Uses a Fixed Unique-Value Threshold

Numeric targets with at most 20 unique values are automatically treated as categorical.

### Required refinement

- make the threshold configurable;
- handle all-missing targets explicitly;
- clarify ordinal and count target behaviour;
- retain `target_type` as an explicit override.

---

# Testing Gaps

The following tests should be added before the next release:

1. Serialization collision between integer and string category labels.
2. Serialization collision between boolean and integer labels.
3. Correlation matrix index preservation.
4. Full profile with repeated list values.
5. Full profile with repeated dictionaries.
6. Nested mixed-object profile.
7. 51-column numeric profile.
8. Hundreds-column numeric profile.
9. Kendall profile above 10,000 rows.
10. Sparse categorical warning sampling metadata.
11. All public configuration fields in metadata.
12. Duplicate analysis called only once per profile.
13. Bare string selection behaviour.
14. Tuple column selection behaviour.
15. Duplicate selected column behaviour.
16. Nonnumeric requested correlation columns.
17. All-missing target.
18. Negative-mean coefficient of variation.
19. Zero-IQR nullable result semantics.
20. Wheel and source distribution content.
21. Minimum pandas compatibility.
22. Full source mypy check.
23. Ruff in CI.
24. Installed-artifact typing for all public result types.

---

# Documentation Corrections

The following documentation should be updated:

- README should mention report metadata.
- README should describe bounded output accurately.
- Documentation should not claim that formatter ellipses never occur when output limits are enabled.
- API reference should list all `profile()` parameters.
- API reference should document correlation execution status.
- API reference should explain exact versus sampled results.
- Release guide should use dynamic versions.
- Release guide should validate the current schema.
- Changelog should clearly identify breaking API and schema changes.

---

# Recommended Implementation Order

## Release-blocking phase

1. Prevent serialization collisions and silent data loss.
2. Add shared safe handling for unhashable values.
3. Expose correlation safeguards through `profile()`.
4. Make metadata complete and execution-derived.
5. Update versioning, release guide, README, and API reference.
6. Add regression tests for all P0 findings.

## Correctness and scalability phase

7. Reuse duplicate analysis.
8. Make frequency metadata lazy.
9. Add missing-pattern limits and sampling.
10. Add explicit correlation execution status.
11. Remove internal parameters from public signatures.

## Maintainability and quality phase

12. Split `analysis.py` by domain.
13. Remove private cross-module dependencies.
14. Strengthen public typing.
15. Complete CI and compatibility matrices.
16. Convert benchmarks into regression tracking.

## Statistical refinement phase

17. Correct coefficient-of-variation semantics.
18. Use nullable values for non-applicable outlier results.
19. Improve numeric-identifier confidence logic.
20. Refine automatic target inference.

---

# Proposed GitHub Issues

1. **Prevent serialization key collisions and silent report data loss**
2. **Add shared safe handling for unhashable DataFrame values**
3. **Expose correlation limits and sampling through `profile()`**
4. **Make report configuration and execution metadata complete and truthful**
5. **Update release contract for the current report schema**
6. **Reuse duplicate analysis across profile sections**
7. **Make analysis-context frequency counts lazy**
8. **Add safeguards and limits for missingness-pattern analysis**
9. **Return explicit correlation execution status**
10. **Remove internal dependency parameters from public API signatures**
11. **Export and strengthen all public result types**
12. **Align CI with the documented release contract**
13. **Test minimum and latest pandas compatibility**
14. **Correct non-applicable statistical result semantics**

---

# Release Recommendation

**Do not publish the current unreleased state until all P0 findings are resolved.**

The package foundations are strong, and the earlier consistency bugs have been corrected. The next step should prioritise report integrity and predictable behaviour rather than adding new analytical features.

The most critical rule for the next release is:

> A FramePeek report must either produce correct, explicitly qualified output or fail transparently. It must never silently discard or merge user data.
