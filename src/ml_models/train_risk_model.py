from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from src.ml_models.modeling import train_risk_model, save_metrics
import pandas as pd

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("gold_path")
    parser.add_argument("--metrics", default="artifacts/risk_metrics.json")
    args = parser.parse_args()
    metrics = train_risk_model(pd.read_parquet(args.gold_path))
    save_metrics(metrics, args.metrics)
    print(metrics)
