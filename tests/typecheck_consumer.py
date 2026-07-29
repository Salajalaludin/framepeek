import pandas as pd

import framepeek as fp

frame = pd.DataFrame({"x": [1, 2], "y": [2, 4]})
result: fp.CorrelationResult = fp.correlations(
    frame,
    method="spearman",
    overflow="error",
)
matrix: pd.DataFrame = result["matrix"]
