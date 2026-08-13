"""Synthetic transaction generator for local development and Databricks jobs."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate_transactions(n_rows: int = 100_000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    customer_count = max(5_000, n_rows // 12)
    customer_id = rng.integers(1, customer_count + 1, size=n_rows)
    amount = np.round(rng.lognormal(mean=3.6, sigma=1.05, size=n_rows), 2)
    income = np.round(rng.lognormal(mean=10.8, sigma=0.65, size=n_rows), 2)
    age = rng.integers(21, 76, size=n_rows)
    channels = rng.choice(["card", "transfer", "cash", "mobile"], size=n_rows, p=[.52, .25, .08, .15])
    countries = rng.choice(["US", "GB", "DE", "IN", "SG"], size=n_rows, p=[.42, .18, .15, .18, .07])
    velocity_24h = rng.poisson(lam=4.2, size=n_rows)
    late_payments = rng.poisson(lam=.55, size=n_rows)
    balance_ratio = np.clip(rng.beta(2.2, 5.5, size=n_rows), 0, 1)
    fraud_flag = ((amount > np.quantile(amount, .97)) & (velocity_24h >= 10)).astype(int)
    default_label = ((balance_ratio > .66) & (late_payments >= 2) | (income < np.quantile(income, .15)) & (late_payments >= 3)).astype(int)
    return pd.DataFrame({
        "transaction_id": np.arange(1, n_rows + 1),
        "customer_id": customer_id,
        "amount": amount,
        "income": income,
        "age": age,
        "channel": channels,
        "country": countries,
        "velocity_24h": velocity_24h,
        "late_payments": late_payments,
        "balance_ratio": np.round(balance_ratio, 4),
        "fraud_flag": fraud_flag,
        "default_label": default_label,
        "event_ts": pd.Timestamp("2026-01-01") + pd.to_timedelta(rng.integers(0, 90 * 24 * 60, n_rows), unit="m"),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=100_000)
    parser.add_argument("--output", type=Path, default=Path("data/bronze/transactions.parquet"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    generate_transactions(args.rows).to_parquet(args.output, index=False)
    print(f"wrote {args.rows:,} rows to {args.output}")


if __name__ == "__main__":
    main()
