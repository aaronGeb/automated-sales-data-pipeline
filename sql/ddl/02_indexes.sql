CREATE INDEX IF NOT EXISTS idx_sales_invoice_date ON sales_transactions (invoice_date);
CREATE INDEX IF NOT EXISTS idx_sales_customer_id  ON sales_transactions (customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_stock_code   ON sales_transactions (stock_code);
CREATE INDEX IF NOT EXISTS idx_sales_country      ON sales_transactions (country);