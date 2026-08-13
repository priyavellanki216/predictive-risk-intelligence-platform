from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from src.pipelines.medallion_pipeline import gold_aggregate
import pandas as pd

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path")
    parser.add_argument("output_path")
    args = parser.parse_args()
    gold_aggregate(pd.read_parquet(args.input_path)).to_parquet(args.output_path, index=False)
