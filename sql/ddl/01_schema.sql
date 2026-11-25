CREATE TABLE IF NOT EXISTS sales_transactions (
    row_hash        CHAR(64)       PRIMARY KEY,   -- sha256 of business columns
    invoice_no      TEXT           NOT NULL,
    stock_code      TEXT           NOT NULL,
    description     TEXT,
    quantity        INTEGER        NOT NULL,
    invoice_date    TIMESTAMP      NOT NULL,
    unit_price      NUMERIC(12, 4) NOT NULL CHECK (unit_price > 0),
    customer_id     INTEGER,
    country         TEXT           NOT NULL,
    is_cancellation BOOLEAN        NOT NULL,
    is_non_product  BOOLEAN        NOT NULL,
    source_file     TEXT           NOT NULL,
    source_row      INTEGER        NOT NULL,
    loaded_at       TIMESTAMPTZ    NOT NULL DEFAULT now()
);