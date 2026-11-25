SELECT stock_code,
       mode() WITHIN GROUP (ORDER BY description) AS description,
       sum(quantity)                              AS units_sold,
       round(sum(quantity * unit_price), 2)       AS net_revenue
FROM sales_transactions
WHERE NOT is_non_product
GROUP BY stock_code
ORDER BY net_revenue DESC
LIMIT 20;