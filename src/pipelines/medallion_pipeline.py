"""Medallion transformations; callable from Databricks or local pandas tests."""
from __future__ import annotations

from pathlib import Path
import pandas as pd


def bronze_ingest(input_path: str | Path) -> pd.DataFrame:
    return pd.read_parquet(input_path)


def silver_clean(bronze: pd.DataFrame) -> pd.DataFrame:
    frame = bronze.copy()
    frame["event_ts"] = pd.to_datetime(frame["event_ts"], errors="coerce", utc=True)
    frame = frame.drop_duplicates(subset=["transaction_id"]).dropna(subset=["customer_id", "amount"])
    frame["amount"] = frame["amount"].clip(lower=0)
    frame["velocity_24h"] = frame["velocity_24h"].clip(lower=0)
    frame["amount_to_income"] = (frame["amount"] / frame["income"].clip(lower=1)).clip(upper=10)
    frame["risk_velocity_interaction"] = frame["velocity_24h"] * (1 + frame["balance_ratio"])
    return frame.reset_index(drop=True)


def gold_aggregate(silver: pd.DataFrame) -> pd.DataFrame:
    grouped = silver.groupby("customer_id", as_index=False).agg(
        transaction_count=("transaction_id", "count"),
        total_amount=("amount", "sum"),
        avg_amount=("amount", "mean"),
        avg_velocity_24h=("velocity_24h", "mean"),
        late_payment_count=("late_payments", "sum"),
        avg_balance_ratio=("balance_ratio", "mean"),
        fraud_rate=("fraud_flag", "mean"),
        default_label=("default_label", "max"),
        income=("income", "median"),
        age=("age", "median"),
    )
    grouped["risk_score"] = (
        100 * (0.34 * grouped["avg_balance_ratio"] + 0.28 * grouped["fraud_rate"] +
               0.22 * (grouped["late_payment_count"] / grouped["transaction_count"].clip(lower=1)).clip(upper=1) +
               0.16 * (grouped["avg_velocity_24h"] / 20).clip(upper=1))
    ).round(2)
    return grouped


def run_local_pipeline(input_path: str | Path, output_dir: str | Path) -> dict[str, str]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    bronze = bronze_ingest(input_path)
    silver = silver_clean(bronze)
    gold = gold_aggregate(silver)
    paths = {}
    for name, frame in [("bronze", bronze), ("silver", silver), ("gold", gold)]:
        path = output / f"{name}.parquet"
        frame.to_parquet(path, index=False)
        paths[name] = str(path)
    return paths
