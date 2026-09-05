-- The intraday spread curve: costs are worst at the open and settle after it.
-- Grouped by clock hour so the shape survives having only one session of data.
SELECT
    SUBSTR(minute, 12, 2)                      AS hour,
    COUNT(*)                                   AS bars,
    ROUND(AVG(avg_spread), 4)                  AS mean_spread,
    ROUND(AVG(max_spread), 4)                  AS mean_worst_spread,
    SUM(total_volume)                          AS traded_volume
FROM minute_bars
GROUP BY hour
ORDER BY hour;
