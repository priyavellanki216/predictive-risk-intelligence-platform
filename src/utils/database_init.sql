-- Predictive Risk Intelligence Platform serving contract
CREATE TABLE IF NOT EXISTS customer_risk_scores (
  customer_id BIGINT PRIMARY KEY,
  transaction_count INTEGER NOT NULL,
  total_amount NUMERIC(18,2) NOT NULL,
  avg_amount NUMERIC(18,2) NOT NULL,
  avg_velocity_24h NUMERIC(10,4) NOT NULL,
  late_payment_count INTEGER NOT NULL,
  avg_balance_ratio NUMERIC(10,4) NOT NULL,
  fraud_rate NUMERIC(10,6) NOT NULL,
  income NUMERIC(18,2) NOT NULL,
  age NUMERIC(5,1) NOT NULL,
  risk_score NUMERIC(10,4) NOT NULL,
  segment_id INTEGER,
  model_version VARCHAR(64) NOT NULL,
  scored_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_customer_risk_scores_risk_score ON customer_risk_scores (risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_customer_risk_scores_segment ON customer_risk_scores (segment_id);
