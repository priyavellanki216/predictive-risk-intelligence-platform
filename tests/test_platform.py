import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from src.utils.generate_transactions import generate_transactions
from src.pipelines.medallion_pipeline import silver_clean, gold_aggregate
from src.ml_models.modeling import train_risk_model, segment_customers


def test_generator_scale_and_schema():
    frame = generate_transactions(1_000)
    assert len(frame) == 1_000
    assert {"transaction_id", "customer_id", "amount", "default_label"}.issubset(frame.columns)


def test_silver_removes_duplicate_and_derives_features():
    frame = generate_transactions(100)
    import pandas as pd
    frame = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
    silver = silver_clean(frame)
    assert silver["transaction_id"].is_unique
    assert "amount_to_income" in silver.columns
    assert silver["amount"].min() >= 0


def test_gold_has_customer_risk_score():
    gold = gold_aggregate(silver_clean(generate_transactions(2_000)))
    assert gold["customer_id"].is_unique
    assert gold["risk_score"].between(0, 100).all()


def test_ml_metrics_are_logged():
    gold = gold_aggregate(silver_clean(generate_transactions(4_000)))
    risk = train_risk_model(gold)
    _, segments = segment_customers(gold)
    assert 0 <= risk["precision"] <= 1
    assert 0 <= risk["recall"] <= 1
    assert 0 <= risk["auc_roc"] <= 1
    assert -1 <= segments["silhouette_score"] <= 1
