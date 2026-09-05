-- Minutes where the book was more than three times its symbol's usual width.
-- These are the minutes a signal should be distrusted: the quoted price is
-- there, but nobody would have filled at it.
--
-- The baseline is leave-one-out on purpose. Comparing a minute against an
-- average that includes that same minute lets a big enough outlier drag the
-- baseline up with it and hide itself -- which it demonstrably did on a small
-- group before this was fixed.
WITH totals AS (
    SELECT symbol,
           SUM(avg_spread) AS sum_spread,
           COUNT(*)        AS n
    FROM minute_bars
    WHERE avg_spread IS NOT NULL
    GROUP BY symbol
)
SELECT
    b.symbol,
    b.minute,
    ROUND(b.avg_spread, 4)                                            AS spread,
    ROUND((t.sum_spread - b.avg_spread) / (t.n - 1), 4)               AS usual_spread,
    ROUND(b.avg_spread / ((t.sum_spread - b.avg_spread) / (t.n - 1)), 2) AS times_usual,
    b.total_volume
FROM minute_bars b
JOIN totals t ON t.symbol = b.symbol
WHERE t.n > 1
  AND (t.sum_spread - b.avg_spread) > 0
  AND b.avg_spread > 3 * ((t.sum_spread - b.avg_spread) / (t.n - 1))
ORDER BY times_usual DESC
LIMIT 50;
