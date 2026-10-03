"""Bounded runtime and peak-memory benchmarks; --large includes 1M rows."""

from argparse import ArgumentParser
from collections.abc import Callable
from time import perf_counter
from tracemalloc import get_traced_memory, start, stop

import numpy as np
import pandas as pd

import framepeek as fp
from framepeek._context import AnalysisContext


def measure(name: str, df: pd.DataFrame, run: Callable = fp.profile) -> None:
    start()
    began = perf_counter()
    run(df)
    elapsed = perf_counter() - began
    _, peak = get_traced_memory()
    stop()
    print(f"{name}: {elapsed:.3f}s, peak={peak / 1024**2:.2f} MiB")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--large", action="store_true")
    args = parser.parse_args()
    rows = 1_000_000 if args.large else 100_000
    numeric = pd.DataFrame({"x": range(rows)})
    measure("numeric-context", numeric, AnalysisContext.from_frame)
    measure("unique-numeric-profile", numeric)
    del numeric
    measure(
        "high-cardinality-strings",
        pd.DataFrame(
            {"text": pd.Series([f"v{i}" for i in range(100_000)], dtype="string")}
        ),
    )
    measure(
        "wide-context-128",
        pd.DataFrame({f"x{i}": range(1000) for i in range(128)}),
        AnalysisContext.from_frame,
    )
    measure("wide", pd.DataFrame({f"x{i}": range(100) for i in range(40)}))
    measure(
        "categorical",
        pd.DataFrame(
            {f"c{i}": [f"value-{j % 100}" for j in range(10_000)] for i in range(10)}
        ),
    )
    measure("missing", pd.DataFrame({"x": [None, 1] * 50_000}))
    measure(
        "mixed", pd.DataFrame({"x": range(100_000), "category": ["a", "b"] * 50_000})
    )
    rng = np.random.default_rng(0)
    for name, shape, probability in (
        ("tall-missing", (rows, 4), 0.1),
        ("wide-missing", (2000, 128), 0.1),
        ("mostly-complete", (100_000, 10), 0.001),
        ("random-missing", (100_000, 10), 0.3),
        ("many-patterns", (10_000, 64), 0.5),
    ):
        frame = pd.DataFrame(np.where(rng.random(shape) < probability, np.nan, 1.0))
        measure(name, frame, fp.missing)
