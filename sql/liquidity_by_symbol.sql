-- Which names actually traded, and how expensive they were to cross.
-- Answers "where would this strategy be cheap to run", which is the first
-- question a desk asks before it looks at any signal.
SELECT
    symbol,
    COUNT(*)                                   AS bars,
    SUM(total_volume)                          AS traded_volume,
    SUM(num_trades)                            AS trades,
    ROUND(AVG(avg_spread), 4)                  AS mean_spread,
    ROUND(AVG(avg_spread) / AVG(c) * 10000, 2) AS mean_spread_bps,
    ROUND(AVG(total_bid_size + total_ask_size), 1) AS mean_resting_size
FROM minute_bars
GROUP BY symbol
HAVING bars > 0
ORDER BY traded_volume DESC;
