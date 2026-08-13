"""Export Gold metrics to a SQLite file or PostgreSQL via SQLAlchemy."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd


def export_gold(gold: pd.DataFrame, connection_url: str, table_name: str = "customer_risk_scores") -> None:
    from sqlalchemy import create_engine
    engine = create_engine(connection_url)
    gold.to_sql(table_name, engine, if_exists="replace", index=False, method="multi")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("gold_path")
    parser.add_argument("--database", default="sqlite:///artifacts/risk_serving.db")
    args = parser.parse_args()
    export_gold(pd.read_parquet(args.gold_path), args.database)
    print(f"exported Gold scores to {args.database}")
