import pandas as pd
import hashlib
import os
from typing import Dict, Any

def profile_dataset(file_path: str) -> Dict[str, Any]:
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.csv':
        df = pd.read_csv(file_path)
    elif ext in ['.parquet', '.pq']:
        df = pd.read_parquet(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    # Calculate hash
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    content_hash = sha256_hash.hexdigest()

    # Profiling stats
    record_count = len(df)
    column_count = len(df.columns)
    
    schema_snapshot = {col: str(df[col].dtype) for col in df.columns}
    
    missing_values = {col: int(df[col].isnull().sum()) for col in df.columns}
    missing_pct = {col: round((df[col].isnull().sum() / record_count) * 100, 2) if record_count > 0 else 0 for col in df.columns}
    
    unique_counts = {col: int(df[col].nunique()) for col in df.columns}
    
    numeric_stats = {}
    for col in df.select_dtypes(include=['number']).columns:
        numeric_stats[col] = {
            "mean": float(df[col].mean()),
            "std": float(df[col].std()),
            "min": float(df[col].min()),
            "max": float(df[col].max())
        }

    duplicate_rows = int(df.duplicated().sum())

    return {
        "content_hash": content_hash,
        "record_count": record_count,
        "column_count": column_count,
        "schema_snapshot": schema_snapshot,
        "missing_values": missing_values,
        "missing_percentage": missing_pct,
        "unique_counts": unique_counts,
        "numeric_stats": numeric_stats,
        "duplicate_rows": duplicate_rows
    }