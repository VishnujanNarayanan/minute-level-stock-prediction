-- The base rate any model has to beat: how often does the next minute close up?
-- Computed in SQL with a window function so the answer does not depend on the
-- Python feature code being correct.
WITH stepped AS (
    SELECT
        symbol,
        c,
        LEAD(c) OVER (PARTITION BY symbol ORDER BY minute) AS next_c
    FROM minute_bars
)
SELECT
    symbol,
    COUNT(next_c)                                            AS labelled_bars,
    SUM(CASE WHEN next_c > c THEN 1 ELSE 0 END)              AS up_bars,
    ROUND(100.0 * SUM(CASE WHEN next_c > c THEN 1 ELSE 0 END)
          / COUNT(next_c), 2)                                AS up_rate_pct
FROM stepped
WHERE next_c IS NOT NULL
GROUP BY symbol
ORDER BY up_rate_pct DESC;
