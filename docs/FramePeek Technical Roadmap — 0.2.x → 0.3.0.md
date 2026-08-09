# FramePeek Technical Roadmap — 0.2.x → 0.3.0

Roadmap ini menentukan distribusi pekerjaan teknis setelah `0.2.0`.

Prinsip utama:

- `0.2.x` hanya untuk bug fix, correctness, performance, testing, CI, packaging, dan refactor internal yang backwards-compatible.
- `0.3.0` untuk public API baru, perubahan kontrak report, perubahan schema, atau capability baru.
- Tidak semua issue harus dipaksakan masuk satu patch release.
- Setiap patch harus punya fokus yang jelas dan dapat dirilis secara independen.

---

# 0.2.1 — Correctness & Edge-Case Hotfix

## Fokus

Menutup bug correctness yang masih dapat menyebabkan crash atau hasil salah pada input yang seharusnya dapat dianalisis.

## Bugs

### Unhashable value fast-path masih dapat salah

`_values.value_counts()` menentukan fast-path berdasarkan `type.__hash__`, bukan hashability nilai aktual.

Contoh yang masih berisiko:

- tuple berisi list;
- tuple berisi dictionary;
- object dengan implementasi `__hash__` yang melempar exception;
- nested object yang secara tipe terlihat hashable tetapi secara nilai tidak.

### Required fix

- Fast-path harus berdasarkan keberhasilan operasi pada nilai aktual.
- Jika pandas hash-based operation gagal, gunakan structural fallback.
- Jangan menentukan hashability hanya dari tipe.

---

### Structural identity belum mencakup semua nested values

Structural identity sudah menangani:

- list;
- tuple;
- dictionary;
- set;
- frozenset.

Namun object unhashable lain seperti NumPy array masih dapat jatuh ke object identity.

Akibatnya dua nilai terpisah dengan isi identik dapat dianggap berbeda.

### Required fix

- Tentukan support policy untuk NumPy arrays dan nested array-like values.
- Jika didukung, gunakan structural value equality.
- Jika tidak didukung, hasil harus eksplisit ditandai unsupported dan tidak diam-diam dianggap unik.

---

### Unhashable regression coverage belum lengkap

Tambahkan regression test untuk:

- tuple berisi list;
- tuple berisi dictionary;
- nested structures;
- NumPy array;
- custom object dengan broken `__hash__`;
- repeated nested objects;
- full `profile()` terhadap seluruh kasus tersebut.

---

## Release criteria

`0.2.1` hanya boleh dirilis jika:

- tidak ada silent misclassification pada supported nested values;
- tidak ada crash untuk struktur nested yang dinyatakan supported;
- seluruh regression tests lulus;
- tidak ada perubahan public API.

---

# 0.2.2 — Duplicate Analysis Performance

## Fokus

Menghilangkan regression performa yang muncul setelah safe structural duplicate handling diperkenalkan.

## Bugs / performance issues

### Duplicate analysis dihitung tiga kali dalam `profile()`

Saat ini duplicate information digunakan oleh:

- `overview()`;
- `duplicates()`;
- `quality_warnings()`.

Ketiganya melakukan duplicate detection sendiri.

### Required fix

- Hitung duplicate analysis sekali per `profile()`.
- Reuse hasil yang sama untuk overview, duplicate report, dan warnings.
- Jangan mengubah standalone behaviour fungsi publik.

---

### Structural duplicate path terlalu mahal untuk data normal

Safe duplicate implementation sekarang melakukan Python-level row/cell traversal bahkan untuk DataFrame sederhana yang sebenarnya dapat ditangani langsung oleh pandas.

### Required fix

Gunakan dua jalur:

1. Fast-path menggunakan pandas untuk data hashable normal.
2. Structural fallback hanya jika fast-path tidak dapat digunakan.

Tujuannya:

- correctness tetap terjaga;
- performa data normal mendekati pandas native;
- structural processing hanya dibayar ketika memang diperlukan.

---

### Repeated row-key construction

Structural row keys tidak boleh dibuat berulang untuk analysis yang sama dalam satu profile run.

### Required fix

- Reuse precomputed row identity bila fallback diperlukan.
- Hindari membuat `_ValueKey` berulang untuk dataset yang sama.

---

## Testing & benchmark

Tambahkan benchmark:

- 100k rows × 10 numeric columns;
- 1M rows × 10 columns;
- mixed numeric/string;
- nested object;
- duplicated nested object;
- pandas fast-path versus structural fallback.

Tambahkan regression test bahwa duplicate computation hanya dilakukan satu kali pada `profile()`.

---

# 0.2.3 — Analysis Context Efficiency

## Fokus

Mengurangi pekerjaan dan penggunaan memori yang tidak diperlukan selama profiling.

## Performance issues

### Full `value_counts()` dihitung untuk semua kolom

`AnalysisContext` saat ini membuat frequency counts untuk:

- numeric;
- datetime;
- categorical;
- boolean;
- object.

Untuk numeric high-cardinality, ini dapat sangat mahal.

### Required fix

- Gunakan lazy frequency metadata.
- Hanya materialize full counts ketika benar-benar dibutuhkan.
- Gunakan operasi yang lebih murah untuk unique/non-null metadata.
- Numeric columns tidak perlu menyimpan full frequency table secara default.

---

### Metadata context terlalu eager

Metadata yang mahal sebaiknya dihitung on-demand dan kemudian di-cache selama satu analysis run.

### Required fix

Pisahkan metadata menjadi:

- cheap/eager metadata;
- expensive/lazy metadata.

Cheap:

- dtype;
- inferred type;
- missing;
- non-null;
- unique count.

Expensive:

- full value counts;
- mode/frequency distributions;
- structural identities.

---

## Benchmark

Tambahkan kasus:

- 1M unique numeric values;
- high-cardinality strings;
- 100+ columns;
- mixed numeric/categorical dataset.

Target utama bukan hanya runtime tetapi peak memory.

---

# 0.2.4 — Missingness Performance & Safeguards

## Fokus

Mencegah missing-pattern analysis menjadi bottleneck pada dataset besar.

## Performance issues

### Missing-pattern analysis melakukan loop Python per row

Pattern missing dibangun dengan iterasi setiap row dan menyimpan tuple kolom missing.

Ini dapat mahal untuk:

- jutaan row;
- ratusan kolom;
- banyak unique missing patterns.

### Required fix

Tanpa mengubah public API yang sudah ada:

- optimalkan internal representation;
- hindari pembuatan object tuple berlebihan;
- gunakan vectorized representation bila memungkinkan;
- batasi intermediate allocations;
- pastikan hasil existing tetap sama.

---

### Missing-pattern result dapat membesar ekstrem

Jika hampir setiap row memiliki kombinasi missing berbeda, jumlah pattern dapat mendekati jumlah row.

Untuk `0.2.4`, fokus pada perlindungan internal yang backwards-compatible.

Public options seperti `top_n_patterns`, sampling, atau disable patterns tidak dimasukkan di patch ini karena akan menjadi public capability baru dan dialokasikan ke `0.3.0`.

---

## Testing

Tambahkan:

- tall missing dataset;
- wide missing dataset;
- mostly complete dataset;
- random missing dataset;
- worst-case many-pattern dataset.

---

# 0.2.5 — Metadata Accuracy & Reproducibility Fixes

## Fokus

Memperbaiki metadata yang sudah ada agar tidak memberikan informasi yang salah.

## Bugs

### `warnings_used` dapat salah

Metadata saat ini dapat menyatakan warning sampling digunakan berdasarkan ukuran DataFrame, meskipun jumlah nilai non-null categorical column sebenarnya di bawah sample limit.

### Required fix

- Nilai existing `warnings_used` harus berasal dari eksekusi aktual.
- Jangan menebak sampling berdasarkan `len(df)` saja.

Karena ini memperbaiki arti field yang sudah ada, perubahan ini masuk PATCH.

---

### `warning_sample_size` dapat menyesatkan

Metadata harus menggambarkan sample size aktual yang digunakan, bukan hanya konfigurasi maksimum.

### Required fix

- Perbaiki existing metadata agar merepresentasikan execution behaviour sebenarnya.
- Jangan menambah schema besar baru pada seri `0.2.x`.

Metadata execution baru yang lebih detail dialokasikan ke `0.3.0`.

---

### Runtime version fallback

`framepeek.__version__` saat ini bergantung pada installed distribution metadata.

### Required fix

- Tambahkan source-tree-safe fallback.
- Tetap pertahankan `pyproject.toml` sebagai canonical version source.

---

# 0.2.6 — Statistical Correctness

## Fokus

Merapikan hasil statistik yang secara teknis dapat menyesatkan.

## Bugs / semantic issues

### Coefficient of variation pada mean negatif

CV saat ini dapat menghasilkan nilai negatif.

### Required fix

Tentukan definisi yang konsisten dan dokumentasikan behaviour untuk:

- mean positif;
- mean nol;
- mean negatif.

Jangan mengembalikan angka yang terlihat valid jika statistik tersebut tidak meaningful.

---

### Zero-IQR menyatakan `outlier_count = 0`

Ketika:

- `applicable = False`;
- `limitation = "zero_iqr"`,

hasil tetap dapat terlihat seolah-olah terbukti tidak ada outlier.

### Required fix

Gunakan nilai non-applicable/nullable secara konsisten agar:

`not applicable`

tidak sama dengan:

`zero outliers`.

---

### Numeric identifier heuristic terlalu sensitif

Satu sampled value dengan leading zero dapat memengaruhi classification seluruh kolom.

### Required fix

- Gunakan ratio/proportion.
- Kurangi false positive.
- Pertahankan warning code dan schema existing.

---

## Testing

Tambahkan boundary tests untuk:

- negative mean;
- zero mean;
- zero IQR;
- near-zero IQR;
- leading-zero minority;
- leading-zero majority;
- numeric strings biasa.

---

# 0.2.7 — CI & Packaging Reliability

## Fokus

Membuat green CI berarti package benar-benar mendekati release-ready.

## CI gaps

Tambahkan ke normal CI:

- Ruff;
- mypy terhadap `src/framepeek`;
- pytest branch coverage;
- wheel build;
- sdist build;
- strict metadata validation;
- clean wheel install;
- clean sdist install;
- public consumer type-check.

---

### Supported dependency testing

Tambahkan matrix:

- Python minimum + pandas minimum;
- Python terbaru + pandas terbaru.

Scheduled workflow dapat menguji:

- pandas prerelease.

---

### Packaging tests

Pastikan:

- `py.typed` masuk wheel;
- `py.typed` masuk sdist;
- README/license ikut artifact;
- version metadata benar;
- artifact dapat diinstall tanpa editable source tree.

---

# 0.2.8 — Documentation & Release Hardening

## Fokus

Menutup technical debt release sebelum memulai `0.3.0`.

## Required corrections

- Sinkronkan README dengan behaviour aktual.
- Sinkronkan API reference dengan output aktual.
- Hapus stale wording.
- Pastikan release smoke test memvalidasi schema, bukan hanya jumlah key.
- Kurangi hard-coded version di release documentation.
- Pastikan TestPyPI → PyPI → GitHub workflow mengikuti `VERSIONING.md`.
- Backfill/mastikan seluruh stable version memiliki GitHub Release.

---

## Packaging metadata

Lengkapi metadata yang tidak memengaruhi API:

- project URLs;
- repository URL;
- issues URL;
- changelog URL;
- keywords;
- classifiers;
- development status;
- intended audience;
- typing classifier;
- maintainer.

---

# 0.2.x — Reserved Patch Line

Setelah `0.2.8`, seri `0.2.x` tetap terbuka.

Tidak ada keharusan bahwa versi berikutnya langsung `0.3.0`.

Contoh:

- `0.2.9`
- `0.2.10`
- `0.2.11`

boleh dibuat jika ditemukan bug tambahan yang memenuhi kriteria PATCH.

Nomor patch tidak memiliki batas satu digit.

`0.2.10` adalah versi valid dan lebih baru dari `0.2.9`.

Patch line `0.2.x` ditutup hanya ketika development aktif berpindah ke public capability yang memang membutuhkan `0.3.0`.

---

# 0.3.0 — Public API & Scalability Release

## Fokus

Setelah fondasi `0.2.x` stabil, `0.3.0` digunakan untuk perubahan yang memperluas atau mengubah public contract.

---

## 1. Correlation controls pada `profile()`

Tambahkan konfigurasi publik untuk:

- selected correlation columns;
- maximum numeric columns;
- overflow behaviour;
- sample rows;
- minimum periods;
- include matrix;
- top pairs;
- correlation-specific random state bila diperlukan.

Ini tidak dimasukkan ke `0.2.x` karena merupakan public API baru.

### Target behaviour

Full `profile()` harus dapat menangani:

- 51+ numeric columns;
- hundreds of numeric columns;
- Kendall >10k rows;

tanpa membuat pengguna keluar dari full-report API.

---

## 2. Correlation execution status

Perluas result contract agar dapat membedakan:

- computed;
- skipped;
- sampled;
- no numeric columns;
- no valid pairs;
- overflow.

Metadata yang dapat ditambahkan:

- `computed`;
- `skipped`;
- `reason`;
- `method`;
- `selected_columns`;
- `input_rows`;
- `analysis_rows`;
- `sampled`.

Karena mengubah public output schema, ini MINOR.

---

## 3. Complete report configuration metadata

Tambahkan seluruh konfigurasi publik ke report metadata:

- top category count;
- missing thresholds;
- warning thresholds;
- high-cardinality threshold;
- imbalance threshold;
- outlier minimum sample;
- rare-category configuration;
- correlation configuration;
- sampling configuration.

Tambahkan typed execution metadata.

Karena memperluas public report schema secara signifikan, ini `0.3.0`.

---

## 4. Missing-pattern controls

Tambahkan public options seperti:

- enable/disable patterns;
- maximum returned patterns;
- sample rows;
- minimum pattern frequency.

Tambahkan execution status:

- exact;
- sampled;
- truncated.

---

## 5. Public result typing expansion

Export:

- `MissingResult`;
- `MissingRowsResult`;
- metadata result types;
- execution metadata types;
- serialization result types.

Tambahkan nested TypedDict untuk report metadata.

---

## 6. Clean public signatures

Hilangkan parameter internal dari public function signatures:

- `_context`;
- `_correlation_result`;
- `_outlier_result`.

Gunakan internal implementation functions untuk orchestration.

Ini membuat public API lebih jelas sebelum menuju 1.0.

---

## 7. Standalone API consistency

Samakan konfigurasi antara:

- `profile()`;
- `target()`;
- `correlations()`;
- `quality_warnings()`.

Contoh:

- target correlation method;
- target type override;
- sampling;
- overflow behaviour.

---

## 8. Column selection contract

Definisikan public selection API dengan jelas untuk:

- string column labels;
- integer column labels;
- tuple column labels;
- multiple columns;
- duplicate selections;
- nonnumeric correlation selections.

Hilangkan ambiguity `Sequence[ColumnName]`.

---

## 9. Analysis module refactor

Setelah public contract `0.3.0` ditentukan, pecah `analysis.py` menjadi domain yang lebih maintainable.

Contoh:

- dataset analysis;
- column analysis;
- statistical analysis;
- target analysis.

Public imports tetap berasal dari `framepeek`.

---

# Version Map

| Version | Primary purpose |
|---|---|
| `0.2.0` | Current feature/refactor baseline |
| `0.2.1` | Nested/unhashable correctness |
| `0.2.2` | Duplicate performance |
| `0.2.3` | Analysis-context efficiency |
| `0.2.4` | Missingness scalability |
| `0.2.5` | Metadata correctness |
| `0.2.6` | Statistical correctness |
| `0.2.7` | CI and packaging reliability |
| `0.2.8` | Documentation and release hardening |
| `0.2.x` | Additional backwards-compatible fixes as needed |
| `0.3.0` | Public API and scalability expansion |

---

# Rule for Moving Issues Between Versions

An issue may move between patch releases when implementation complexity changes.

However:

- a PATCH issue must not silently become a public feature;
- if fixing an issue requires a new public API or incompatible output contract, move it to `0.3.0`;
- do not inflate a patch release simply to finish the entire audit;
- prefer several focused, releasable patches over one giant `0.2.1`.

The goal is:

`small scope → test → RC → release → continue`

rather than:

`accumulate everything → one oversized release`.

---

# Current Next Release

Current stable:

`0.2.0`

Next planned release:

`0.2.1`

Scope:

**Correctness fixes for structural/unhashable value handling only.**

Performance work follows in `0.2.2`.

Public correlation API changes remain reserved for `0.3.0`.