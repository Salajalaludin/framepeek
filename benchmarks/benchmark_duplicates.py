"""Duplicate-analysis runtime and peak-memory benchmarks.

The default run stops at 1M rows. Use ``--ci-max`` to include 10M rows and
``--manual-25m`` only on a machine with enough memory for a 25M x 10 frame.
"""

from argparse import ArgumentParser
from collections.abc import Callable
from functools import partial
from gc import collect
from time import perf_counter
from tracemalloc import get_traced_memory, start, stop

import numpy as np
import pandas as pd

from framepeek._values import _structural_duplicate_data, duplicate_data

CI_MAX_ROWS = 10_000_000
MANUAL_ROWS = 25_000_000


def measure(name: str, run: Callable[[], object]) -> None:
    collect()
    start()
    began = perf_counter()
    run()
    elapsed = perf_counter() - began
    _, peak = get_traced_memory()
    stop()
    print(f"{name}: {elapsed:.3f}s, peak={peak / 1024**2:.2f} MiB")


def numeric_frame(rows: int, columns: int = 10) -> pd.DataFrame:
    values = np.arange(rows, dtype=np.int64) % max(rows // 2, 1)
    return pd.DataFrame(
        {f"x{index}": values + index for index in range(columns)}
    )


def mixed_frame(rows: int) -> pd.DataFrame:
    values = np.arange(rows, dtype=np.int64) % max(rows // 2, 1)
    return pd.DataFrame(
        {
            "number": values,
            "text": pd.Series("value-" + values.astype(str), dtype="string"),
        }
    )


def nested_frame(rows: int, duplicated: bool) -> pd.DataFrame:
    modulus = max(rows // 2, 1) if duplicated else max(rows, 1)
    return pd.DataFrame({"value": [[index % modulus] for index in range(rows)]})


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "--ci-max",
        action="store_true",
        help="include the CI ceiling of 10M x 10 numeric values",
    )
    parser.add_argument(
        "--manual-25m",
        action="store_true",
        help="include the manual-only 25M x 10 numeric case",
    )
    args = parser.parse_args()

    sizes = [100_000, 1_000_000]
    if args.ci_max or args.manual_25m:
        sizes.append(CI_MAX_ROWS)
    if args.manual_25m:
        sizes.append(MANUAL_ROWS)

    for rows in sizes:
        frame = numeric_frame(rows)
        measure(
            f"numeric-fast-{rows:,}x10",
            partial(duplicate_data, frame),
        )
    del frame

    comparison = numeric_frame(100_000)
    columns = list(comparison.columns)
    measure(
        "numeric-structural-100,000x10",
        partial(_structural_duplicate_data, comparison, columns),
    )
    del comparison

    case_rows = 100_000
    mixed = mixed_frame(case_rows)
    measure("mixed-numeric-string", partial(duplicate_data, mixed))
    del mixed
    nested = nested_frame(case_rows, duplicated=False)
    measure("nested-object", partial(duplicate_data, nested))
    del nested
    repeated_nested = nested_frame(case_rows, duplicated=True)
    measure(
        "duplicated-nested-object",
        partial(duplicate_data, repeated_nested),
    )


if __name__ == "__main__":
    main()
