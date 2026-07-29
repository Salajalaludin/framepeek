"""Bounded runtime and peak-memory smoke benchmarks."""

from time import perf_counter
from tracemalloc import get_traced_memory, start, stop

import pandas as pd

import framepeek as fp


def measure(name: str, df: pd.DataFrame) -> None:
    start()
    began = perf_counter()
    fp.profile(df)
    elapsed = perf_counter() - began
    _, peak = get_traced_memory()
    stop()
    print(f"{name}: {elapsed:.3f}s, peak={peak / 1024**2:.2f} MiB")


if __name__ == "__main__":
    measure("tall", pd.DataFrame({"x": range(100_000)}))
    measure("wide", pd.DataFrame({f"x{i}": range(100) for i in range(40)}))
    measure(
        "categorical",
        pd.DataFrame({f"c{i}": [f"value-{j % 100}" for j in range(10_000)] for i in range(10)}),
    )
    measure("missing", pd.DataFrame({"x": [None, 1] * 50_000}))
