# Combined maintenance benchmarks

Run date: 2026-10-03. Windows, Python 3.12.10, pandas 3.0.5, NumPy 2.5.1: the same
environment for tag v0.2.2 and the combined 0.2.8 checkout. Run the same
`benchmarks/benchmark_profile.py --large` against each source tree. Synthetic
frames are created before measurement; each call uses `perf_counter` and
`tracemalloc`. These are single-run measurements, not statistical estimates or
total process RSS. Tracing adds overhead, especially for Python object creation.

| Case | 0.2.2 seconds | Combined seconds | 0.2.2 peak MiB | Combined peak MiB |
|---|---:|---:|---:|---:|
| Context, 1M unique numeric rows | 4.699 | 0.004 | 137.96 | 1.92 |
| Profile, 1M unique numeric rows | 27.761 | 0.401 | 179.97 | 57.93 |
| Profile, 100k unique strings | 3.572 | 1.179 | 24.47 | 24.44 |
| Context, 128 columns × 1k rows | 0.664 | 0.032 | 14.72 | 0.25 |
| Profile, 100k mixed rows | 5.547 | 0.181 | 18.12 | 5.86 |
| Missingness, 1M rows × 4 columns | 40.795 | 0.383 | 29.87 | 1.92 |
| Missingness, 2k rows × 128 columns | 0.896 | 0.234 | 1.25 | 1.55 |
| Mostly complete, 100k rows × 10 columns | 4.727 | 0.035 | 3.55 | 1.90 |
| Random missing, 100k rows × 10 columns | 3.522 | 0.180 | 3.09 | 1.90 |
| Many patterns, 10k rows × 64 columns | 1.273 | 1.210 | 6.62 | 7.38 |

Lazy context setup postpones work; the full-profile row shows the effect after
consumers actually request the metadata. Exact categorical distributions still
need memory proportional to cardinality. Exact missing-pattern output still
needs memory proportional to the number and width of returned patterns; packed
keys add some overhead in the many-pattern case. Public truncation/sampling
controls remain reserved for 0.3.0.
