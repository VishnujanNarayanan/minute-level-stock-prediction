
# Minute-Level Stock Price Movement Prediction

This project uses a Random Forest classifier to predict whether a stock’s price will go up in the next minute based on historical trade and quote data, including rolling averages and order book features.

---

## Objective

The main goal is to build a predictive model that identifies very short-term upward price movements with high precision, minimizing false buy signals. This can help traders make confident decisions, reduce unnecessary trades, and improve profitability in high-frequency or algorithmic trading environments.

---

## Methodology

1. **Data Preparation:**
   - Merged trade and quote aggregates for multiple companies at minute-level granularity.
   - Added features including OHLC prices (Open, High, Low, Close), spread metrics, bid/ask sizes, and weighted average prices.
   - Calculated multiple rolling averages and rolling standard deviations on price and volume using different window sizes (e.g., 3, 5, 10, 20 minutes) to capture recent trends and volatility—this helps the model understand short-term market momentum and fluctuations.

2. **Target Definition:**
   - Created a binary target variable indicating whether the price will increase in the next minute (`1`) or not (`0`).
   - Ensured that only past and current data were used for feature construction to avoid data leakage and maintain model integrity.

3. **Modeling:**
   - Used a Random Forest classifier for its robustness, ability to handle nonlinear relationships, and interpretability.
   - Trained the model on historical data grouped by company, reserving the last 100 minutes of data per company for testing to simulate out-of-sample prediction.
   - Applied a probability threshold (typically > 0.6) to predict positive classes only when the model’s confidence is high, thus reducing false positives and improving precision.
   - Compared different values of `n_estimators` (number of trees in the forest) to balance between model complexity, training time, and prediction performance.

4. **Backtesting Strategy:**
   - Simulated a simple trading strategy starting with a fixed capital (e.g., $3000).
   - For every predicted upward price movement (with probability above threshold), executed a trade with a fixed amount (e.g., $200).
   - Calculated profit/loss based on actual price changes to evaluate the effectiveness of the model in realistic trading conditions.
   - This strategy focuses on maximizing precision to minimize unnecessary trades and transaction costs.

| n_estimators | Threshold | Precision | Predicted 1 count | Actual 1 count | Confusion Matrix (TN, FP, FN, TP)         |
|--------------|-----------|-----------|-------------------|----------------|--------------------------------------------|
| 80           | 0.63      | 0.6044    | 91                | 1451           | [[1613, 36], [1396, 55]]                   |
| 100          | 0.63      | 0.6143    | 70                | 1451           | [[1622, 27], [1408, 43]]                   |

---

## Explanation of Results and Model Choice

- **Why different results at `n_estimators=80` vs `n_estimators=100`?**

  Increasing the number of trees (`n_estimators`) generally improves the model's stability and accuracy by reducing variance. Here, with 100 trees, the model achieved slightly higher precision (0.6143) but predicted fewer positive cases (70 vs 91). With 80 trees, the precision is slightly lower (0.6044) but it catches more predicted positives.Both are valid choises.

- **Choosing between the two:**

  You can select either model depending on your preference:

  - **More conservative model:** `n_estimators=100` predicts fewer buy signals but with slightly higher precision (fewer false positives).
  - **More sensitive model:** `n_estimators=80` predicts more buy signals with slightly lower precision but potentially more opportunities.

---

## Probability Threshold (0.63)

- The threshold for predicting "up" is set to **0.63**, meaning the model only predicts a price increase if the predicted probability exceeds 63%.
- Adjusting this threshold controls the trade-off between precision and recall:

  - Higher threshold → Higher precision but fewer buy signals (less recall).
  - Lower threshold → More buy signals but risk of more false positives.

- The threshold of 0.63 was chosen as an **ideal balance**, maximizing precision while still capturing a reasonable number of positive signals.

---

## Key Metrics

| Metric    | Value  |
|-----------|--------|
| Precision | ~0.61+ |
| Recall    | ~0.03  |
| F1 Score  | ~0.08  |

---

## Interpretation

- **High Precision:** The model is very confident when it predicts an upward price movement (label 1). This means most of the predicted "buy" signals are correct, significantly reducing false positives.
- **Low Recall:** The model identifies only a small fraction of all actual upward movements.

### Why High Precision is Preferred Here

In minute-level trading, **false positive buy signals can lead to unnecessary trades and transaction costs** that erode profits. By focusing on high precision:

- We minimize risky trades based on uncertain predictions.
- Each "buy" signal has a higher likelihood of success, improving the overall profitability of the strategy.
- It’s acceptable to miss some opportunities (low recall) because it avoids losses from false predictions.

This trade-off aligns well with conservative trading strategies where avoiding losses is more important than capturing every possible gain.

---

## Effectiveness

The backtesting simulation starting with $3000 and trading $200 per signal showed a modest profit increase, demonstrating the strategy's ability to generate low-risk positive returns. While not capturing all opportunities, the model’s precision-first approach helps maintain capital and reduce losses, making it practical for cautious intraday trading.

---

## How to Run

- Install dependencies:

```bash
pip install -r requirements.txt
```
