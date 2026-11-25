SELECT country,
       count(DISTINCT invoice_no) FILTER (WHERE NOT is_cancellation) AS orders,
       count(DISTINCT customer_id)                                   AS customers,
       round(sum(quantity * unit_price), 2)                          AS net_revenue
FROM sales_transactions
GROUP BY country
ORDER BY net_revenue DESC;