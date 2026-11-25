SELECT invoice_date::date AS day,
       count(DISTINCT invoice_no) FILTER (WHERE NOT is_cancellation)            AS orders,
       round(sum(quantity * unit_price) FILTER (WHERE NOT is_cancellation), 2)  AS gross_revenue,
       round(sum(quantity * unit_price) FILTER (WHERE is_cancellation), 2)      AS cancelled_revenue,
       round(sum(quantity * unit_price), 2)                                     AS net_revenue
FROM sales_transactions
GROUP BY 1
ORDER BY 1;