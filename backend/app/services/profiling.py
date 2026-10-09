import hashlib
import math
import os
from typing import Any

import pandas as pd


def _json_number(value: Any) -> float | None:
    """Convert numpy/pandas numbers into finite JSON-safe Python floats."""
    if pd.isna(value):
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def profile_dataset(file_path: str) -> dict[str, Any]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(file_path)
    elif ext in {".parquet", ".pq"}:
        df = pd.read_parquet(file_path)
    else:
        raise ValueError("Unsupported file format. Upload a CSV or Parquet file.")

    digest = hashlib.sha256()
    with open(file_path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)

    row_count = len(df)
    schema_snapshot = {str(col): str(df[col].dtype) for col in df.columns}
    missing_values = {str(col): int(df[col].isna().sum()) for col in df.columns}
    missing_percentage = {
        str(col): round((int(df[col].isna().sum()) / row_count) * 100, 2) if row_count else 0.0
        for col in df.columns
    }
    unique_counts = {str(col): int(df[col].nunique(dropna=True)) for col in df.columns}

    numeric_stats: dict[str, dict[str, float | None]] = {}
    for col in df.select_dtypes(include=["number"]).columns:
        numeric_stats[str(col)] = {
            "mean": _json_number(df[col].mean()),
            "std": _json_number(df[col].std()),
            "min": _json_number(df[col].min()),
            "max": _json_number(df[col].max()),
        }

    return {
        "content_hash": digest.hexdigest(),
        "record_count": int(row_count),
        "column_count": int(len(df.columns)),
        "schema_snapshot": schema_snapshot,
        "missing_values": missing_values,
        "missing_percentage": missing_percentage,
        "unique_counts": unique_counts,
        "numeric_stats": numeric_stats,
        "duplicate_rows": int(df.duplicated().sum()),
    }
