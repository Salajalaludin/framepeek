# Data-quality warning audit for 0.2.0

This audit compares the proposed Data Quality Intelligence work with the actual
MVP implementation and tests. It defines scope only; no 0.2.0 behavior is
implemented here.

## Gap matrix

| Capability | Status | Current evidence | 0.2.0 decision |
| --- | --- | --- | --- |
| Constant columns | Existing | `warnings()` emits `constant`; covered by `test_warnings_detect_actionable_quality_issues`. | Keep behavior. Add content assertions only when severity calibration changes. |
| Near-constant columns | Needs refinement | `near_constant_ratio` is configurable and detection is tested. | Calibrate false positives before changing the `0.95` default. |
| High-cardinality categoricals | Needs refinement | Ratio is configurable and detection is tested; the `unique > 20` floor is fixed. | Retain the warning; evaluate the absolute floor and identifier overlap with representative data. |
| Numeric values stored as text | Needs refinement | `numeric_as_string` exists and is tested; its `0.9` parse ratio is fixed. | Measure mixed-format false positives before exposing or changing the threshold. |
| Datetimes stored as text | Needs refinement | `datetime_as_string` exists and is tested; delimiter and parse ratios are fixed. | Test compact dates, identifiers containing separators, and mixed formats before changing the heuristic. |
| Duplicate rows | Existing | `duplicate_rows` exists and is tested. | Keep behavior. |
| Duplicate column names | Needs refinement | `validate()` rejects them before `warnings()` can run; rejection is tested. | Improve the validation error to list duplicated labels and counts. Do not add an unsafe warning path. |
| All-missing columns | Existing | `all_missing` exists and is tested. | Keep behavior. |
| High missingness | Existing | `missing_threshold` is configurable and detection is tested. | Keep behavior and current severity split unless evidence supports a change. |
| Potential outliers | Needs refinement | IQR warning and percentage threshold exist and are tested. | Align warning configuration with the outlier section so one profile cannot use conflicting multipliers. |
| Target imbalance | Existing | `imbalance_ratio` is configurable and detection is tested. | Keep behavior. |
| Possible identifiers | Existing | `possible_identifier` exists and is tested. | Keep it distinct from high cardinality; calibrate overlap rather than adding another identifier warning. |
| Severity, recommendation, metric | Needs refinement | Every warning row has these fields, but tests mostly assert codes. | Add contract tests when wording or severity rules change; avoid a new class or schema. |
| Rare-category counts | Existing | `categorical()` reports rare and singleton category counts. | Reuse these calculations. |
| Rare-category concentration warning | Missing | No warning measures how much of a column is covered collectively by rare values. | This is the only new warning candidate. |

## Threshold and false-positive notes

| Signal | Current default | Tradeoff |
| --- | --- | --- |
| Near constant | Leading value ratio `>= 0.95` | Lower values flag ordinary skew; higher values miss small but meaningful anomalies. |
| High cardinality | Over 20 values and unique ratio `>= 0.5` | Small datasets and identifier-like text can trigger both cardinality and identifier warnings. |
| Numeric as text | Parse ratio `>= 0.9` | Mixed identifiers may look numeric; dirty numeric columns below the boundary are missed. |
| Datetime as text | Separator ratio and parse ratio `>= 0.9` | Separator-like identifiers can trigger; compact dates without separators are missed. |
| Potential outliers | IQR percentage `> 5` | Small samples and naturally heavy-tailed data can over-trigger. |
| Class imbalance | Majority/minority ratio `>= 3` | Domain cost matters more than one universal ratio. |
| Proposed rare concentration | No default yet | A row-share threshold catches widespread sparse levels; a category-count threshold alone overreacts to large datasets. |

Defaults should not change from anecdotal examples. A change needs labeled,
reproducible fixtures representing identifiers, skewed but valid categories,
dirty numeric/date text, small samples, and heavy-tailed numeric data.

## Acceptance criteria for 0.2.0

### Rare-category concentration

- Reuse categorical value counts; add no dependency or parallel profiling pass.
- Apply only to categorical columns and exclude missing values from the
  denominator.
- Define rare values with a configurable maximum count and trigger on a
  configurable collective row-share ratio.
- Emit one `rare_category_concentration` row per affected column with `medium`
  severity, the observed ratio as `metric`, and a recommendation to review or
  group categories in domain context.
- Cover below-boundary, exact-boundary, missing-value, and no-categorical-column
  cases without mutating the input.
- Expose matching configuration through `warnings()` and `profile()`.

### Duplicate column diagnostics

- Keep strict rejection because downstream column selection is ambiguous.
- Include each duplicated label and occurrence count in the `ValueError`.
- Cover string and non-string duplicate labels.
- Do not emit partial analysis results or introduce another public function.

### Refinement safeguards

- Ensure the outlier warning uses the same IQR multiplier selected for the
  profile's outlier section.
- Assert warning code, severity, recommendation, and metric for behavior that is
  changed.
- Add boundary tests for every threshold that becomes configurable.
- Preserve existing warning codes and defaults unless labeled fixtures show a
  concrete false-positive or false-negative improvement.
- Keep pandas as the only runtime dependency.

## Recommended implementation order

1. Refine duplicate-column error details.
2. Align outlier warning/profile configuration.
3. Add rare-category concentration only after its proposed defaults are
   reviewed against representative fixtures.
4. Revisit other heuristic defaults only from reported false positives or
   false negatives.
