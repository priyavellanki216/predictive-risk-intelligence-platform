"""Local ML reference implementation; the same feature contract can be promoted to PySpark MLlib."""
from __future__ import annotations

from pathlib import Path
import json
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, roc_auc_score, silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

FEATURES = ["transaction_count", "total_amount", "avg_amount", "avg_velocity_24h", "late_payment_count", "avg_balance_ratio", "fraud_rate", "income", "age"]


def train_risk_model(gold: pd.DataFrame, model_path: str | Path | None = None) -> dict:
    x = gold[FEATURES].fillna(0)
    y = gold["default_label"].astype(int)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.25, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=120, max_depth=9, random_state=42, class_weight="balanced")
    model.fit(x_train, y_train)
    probabilities = model.predict_proba(x_test)[:, 1]
    predictions = (probabilities >= .5).astype(int)
    metrics = {
        "precision": round(float(precision_score(y_test, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, predictions, zero_division=0)), 4),
        "auc_roc": round(float(roc_auc_score(y_test, probabilities)), 4),
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
    }
    if model_path:
        import joblib
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)
    return metrics


def segment_customers(gold: pd.DataFrame, n_clusters: int = 4, model_path: str | Path | None = None) -> tuple[pd.DataFrame, dict]:
    x = gold[FEATURES].fillna(0)
    scaled = StandardScaler().fit_transform(x)
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = model.fit_predict(scaled)
    scored = gold.copy()
    scored["segment_id"] = labels
    metrics = {"clusters": n_clusters, "silhouette_score": round(float(silhouette_score(scaled, labels)), 4)}
    if model_path:
        import joblib
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)
    return scored, metrics


def save_metrics(metrics: dict, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
