from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from src.ml_models.modeling import segment_customers, save_metrics
import pandas as pd

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("gold_path")
    parser.add_argument("--clusters", type=int, default=4)
    parser.add_argument("--metrics", default="artifacts/segmentation_metrics.json")
    args = parser.parse_args()
    scored, metrics = segment_customers(pd.read_parquet(args.gold_path), args.clusters)
    save_metrics(metrics, args.metrics)
    print(metrics)
