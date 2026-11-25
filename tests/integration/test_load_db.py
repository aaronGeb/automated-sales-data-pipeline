import pandas as pd
import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from pipeline.load.database import get_engine
from pipeline.load.loader import load_sales


@pytest.fixture
def engine():
    eng = get_engine()
    try:
        with eng.connect() as c:
            c.execute(text("SELECT 1"))
    except OperationalError:
        pytest.skip("Postgres not reachable (run `docker compose up -d`)")
    yield eng
    with eng.begin() as c:
        c.execute(text("DELETE FROM sales_transactions WHERE invoice_no LIKE 'TEST%'"))


def test_load_is_idempotent(engine):
    df = pd.DataFrame(
        {
            "invoice_no": ["TEST001", "TEST002"],
            "stock_code": ["85123A", "22423"],
            "description": ["X", None],
            "quantity": [1, 2],
            "invoice_date": pd.to_datetime(
                ["2010-12-01 08:26:00", "2010-12-01 09:00:00"]
            ),
            "unit_price": [2.55, 3.10],
            "customer_id": [17850, None],
            "country": ["UK", "EIRE"],
            "is_cancellation": [False, False],
            "is_non_product": [False, False],
            "source_file": ["t.xlsx", "t.xlsx"],
            "source_row": [2, 3],
        }
    ).astype({"quantity": "Int64", "customer_id": "Int64"})

    first = load_sales(df, engine)
    second = load_sales(df, engine)

    assert first.inserted == 2
    assert second.inserted == 0 and second.skipped == 2
