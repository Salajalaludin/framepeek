# FramePeek Versioning Policy

FramePeek follows PEP 440 for Python package version identifiers and uses a stricter pre-1.0 versioning policy inspired by Semantic Versioning.

The purpose of this document is to make every version bump deterministic.

Given the same set of changes, maintainers should always arrive at the same next version.

---

## 1. Version format

Stable FramePeek releases use:

`MAJOR.MINOR.PATCH`

Examples:

- `0.2.0`
- `0.2.1`
- `0.3.0`
- `1.0.0`

Release candidates use:

`MAJOR.MINOR.PATCHrcN`

Examples:

- `0.2.1rc1`
- `0.2.1rc2`
- `0.3.0rc1`

FramePeek does not currently use:

- alpha releases (`aN`)
- beta releases (`bN`)
- development releases (`devN`)
- post releases (`postN`)

They may only be introduced later through an explicit change to this policy.

---

# 2. Current stability phase

FramePeek is currently in the `0.x` development phase.

Semantic Versioning allows arbitrary changes during `0.y.z`, but FramePeek intentionally adopts stricter rules so releases remain predictable.

Before `1.0.0`:

- PATCH = backwards-compatible correction.
- MINOR = new public capability or public-contract change.
- MAJOR remains `0` until the public API is declared stable.

Breaking changes before `1.0.0` therefore increment MINOR, not MAJOR.

---

# 3. PATCH release

Increment PATCH:

`0.2.0 → 0.2.1`

when the release contains only backwards-compatible corrections.

Examples:

- bug fixes;
- incorrect statistical behaviour corrected to match documentation;
- crash fixes;
- serialization correctness fixes;
- performance improvements without public behaviour changes;
- internal refactoring;
- typing improvements that do not change runtime API;
- test improvements;
- CI fixes;
- packaging fixes;
- documentation corrections;
- metadata corrections.

A PATCH release must not intentionally:

- add a new public feature;
- add a new public function;
- remove or rename a public function;
- add required parameters;
- change existing parameter semantics;
- change documented defaults;
- break the report schema;
- remove or rename output fields;
- remove supported Python versions;
- introduce a new required dependency with meaningful user impact.

If any of those occur, use MINOR.

---

# 4. MINOR release

Increment MINOR and reset PATCH:

`0.2.x → 0.3.0`

when the release introduces a new public capability or changes the public contract.

Examples:

- new public analysis function;
- new public configuration option;
- new report section;
- new supported analysis method;
- new serialization capability;
- new output fields that form part of the public contract;
- meaningful new warning types;
- deprecation of public API;
- change to default behaviour;
- report-schema change;
- return-type structure change;
- renamed or removed public parameter;
- renamed or removed public function;
- dropping a supported Python or pandas version;
- any other backwards-incompatible public change before `1.0.0`.

Before `1.0.0`, both backwards-compatible features and breaking public changes use MINOR.

Breaking changes must additionally be marked clearly in the changelog with a migration note.

---

# 5. MAJOR release

The first MAJOR release will be:

`1.0.0`

FramePeek should reach `1.0.0` only when the maintainers consider its public contract stable.

At minimum:

- the primary public API is intentionally defined;
- report structures are documented;
- serialization contracts are documented;
- typing contracts are established;
- supported Python and pandas ranges are explicit;
- release automation is reliable;
- major known correctness issues are resolved;
- backwards compatibility is expected rather than incidental.

After `1.0.0`:

- PATCH = backwards-compatible bug fixes;
- MINOR = backwards-compatible public features;
- MAJOR = backwards-incompatible public changes.

---

# 6. What counts as public API

Versioning decisions must consider more than function names.

The FramePeek public contract includes:

- objects exported from `framepeek`;
- public function names;
- public function signatures;
- parameter meanings;
- default values;
- documented exceptions;
- result dictionary keys;
- DataFrame output columns;
- report schema;
- warning codes;
- serialization schema;
- supported Python versions;
- supported pandas versions;
- documented observable behaviour.

Private implementation details do not form part of the compatibility contract.

Examples of private implementation:

- modules beginning with `_`;
- private helper functions;
- caching implementation;
- internal dataclasses;
- internal algorithms when externally observable results remain compatible.

---

# 7. Bug fix versus breaking change

A correction to behaviour that was clearly a bug is normally PATCH, even if someone could technically have depended on the broken behaviour.

For example:

- preventing serialization data loss;
- making configuration propagation consistent;
- stopping unexpected crashes;
- correcting a documented calculation.

However, if the fix intentionally changes an established and documented public contract, treat it as MINOR before `1.0.0`.

---

# 8. Report and serialization schemas

Package version and schema version are separate concepts.

A package PATCH release may fix implementation bugs without changing the schema.

A schema version must change when consumers need to interpret the structure differently.

Examples:

Package:

`0.2.0 → 0.2.1`

Serialization schema:

`1.0 → 1.0`

if only a bug is fixed without structural changes.

If a report or serialization structure changes incompatibly, bump the relevant schema and the FramePeek MINOR version.

---

# 9. Release candidates

Release candidates do not consume a stable release number.

Example sequence:

`0.2.0`
→ `0.2.1rc1`
→ `0.2.1rc2`
→ `0.2.1`

The next stable version remains `0.2.1`.

If the planned release changes from PATCH scope to MINOR scope during RC testing:

`0.2.1rc1`

must not become:

`0.2.1`

with the additional feature.

Instead restart the release line as:

`0.3.0rc1`

---

# 10. RC freeze rule

Once an RC passes TestPyPI validation, the final stable release must contain no behavioural source-code changes relative to that successful RC.

Allowed final-promotion changes:

- removing the `rcN` suffix;
- final changelog date;
- release metadata directly related to the version.

Not allowed:

- bug fixes;
- implementation changes;
- dependency changes;
- test-affecting source changes;
- API changes.

If any functional code changes after `rcN`, create:

`rcN+1`

and test again.

Example:

`0.2.1rc1`
→ bug discovered
→ code fixed
→ `0.2.1rc2`
→ validated
→ `0.2.1`

Never silently modify code between the final tested RC and stable release.

---

# 11. Sequential-version rule

FramePeek does not intentionally skip stable version numbers.

If current stable is:

`0.2.0`

then:

Bugfix release:

`0.2.1`

Feature or public-contract release:

`0.3.0`

After:

`0.2.1`

another bugfix becomes:

`0.2.2`

while a feature release becomes:

`0.3.0`

Do not release `0.2.3` if `0.2.1` and `0.2.2` were never released merely to match commit count, issue count, or internal milestones.

Versions represent public releases, not development activity.

---

# 12. No release required

Not every merge requires a package release.

Changes such as:

- internal documentation;
- issue templates;
- CI-only maintenance;
- test-only additions;
- development documentation;

may remain under `Unreleased` until there is a meaningful reason to publish a package.

Do not increment versions merely because commits have accumulated.

---

# 13. Version decision table

| Change | Before 1.0 |
|---|---|
| Bug fix | PATCH |
| Crash fix | PATCH |
| Performance optimisation, same behaviour | PATCH |
| Internal refactor | PATCH |
| Packaging correction | PATCH |
| Documentation-only correction | PATCH or no release |
| New public function | MINOR |
| New public feature | MINOR |
| New meaningful public parameter | MINOR |
| New analysis method | MINOR |
| Public deprecation | MINOR |
| Change documented default | MINOR |
| Rename/remove public API | MINOR + breaking note |
| Incompatible report schema | MINOR + schema bump |
| Drop supported Python/pandas version | MINOR + breaking note |
| First declared stable API | `1.0.0` |

---

# 14. Examples from FramePeek

Assume current stable release:

`0.2.0`

Fix only:

- correlation configuration forwarding;
- safe handling of nested unhashable values;
- duplicate-performance regression;
- metadata sampling accuracy;
- CI corrections.

Next version:

`0.2.1`

If the same release also introduces:

- a new public correlation configuration API in `profile()`;
- a new public report section;
- a new user-facing analysis method;

next version becomes:

`0.3.0`

If a public parameter is renamed or a report field is removed before 1.0:

next version is also:

`0.3.0`

and the changelog must explicitly identify the breaking change.

---

# 15. Single source of truth

`pyproject.toml` is the canonical package-version source.

The following must derive from or be validated against it:

- package metadata;
- `framepeek.__version__`;
- git tag;
- GitHub Release;
- PyPI release;
- built artifact filenames.

Do not maintain an independent hard-coded runtime version constant.

For a stable release `X.Y.Z`:

- `pyproject.toml` = `X.Y.Z`
- git tag = `vX.Y.Z`
- GitHub Release = `vX.Y.Z`
- PyPI = `X.Y.Z`

Any mismatch means the release is incomplete.
