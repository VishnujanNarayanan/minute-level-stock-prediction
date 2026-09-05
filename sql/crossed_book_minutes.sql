-- Minutes where the best bid sat above the best ask.
--
-- This is not corrupt data. NSE runs a pre-open call auction from 09:00 to
-- 09:15, and during order collection the book is crossed by design while a
-- single opening price is discovered. Spread statistics from those minutes
-- describe an auction, not a continuous market, so they should be reported
-- separately rather than averaged in with the rest of the session.
SELECT
    CASE WHEN minute < '2024-04-01 09:15:00' THEN 'pre-open auction'
         ELSE 'continuous session' END          AS session,
    COUNT(*)                                    AS bars,
    SUM(CASE WHEN avg_spread < 0 THEN 1 ELSE 0 END) AS crossed_bars,
    ROUND(100.0 * SUM(CASE WHEN avg_spread < 0 THEN 1 ELSE 0 END)
          / COUNT(*), 2)                        AS crossed_pct,
    ROUND(AVG(avg_spread), 4)                   AS mean_spread
FROM minute_bars
GROUP BY session
ORDER BY session;
