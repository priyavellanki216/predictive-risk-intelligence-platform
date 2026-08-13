from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from src.pipelines.medallion_pipeline import bronze_ingest

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path")
    args = parser.parse_args()
    print(bronze_ingest(args.input_path).head())
