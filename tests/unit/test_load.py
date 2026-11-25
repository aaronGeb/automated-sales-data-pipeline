import pandas as pd

from pipeline.load.loader import add_row_hash


def _df(**kw):
    base = {
        "invoice_no": ["536365"],
        "stock_code": ["85123A"],
        "description": ["X"],
        "quantity": [1],
        "invoice_date": [pd.Timestamp("2010-12-01 08:26:00")],
        "unit_price": [2.55],
        "customer_id": [17850],
        "country": ["United Kingdom"],
    }
    base.update(kw)
    return pd.DataFrame(base).astype({"quantity": "Int64", "customer_id": "Int64"})


def test_row_hash_is_deterministic():
    assert add_row_hash(_df())["row_hash"][0] == add_row_hash(_df())["row_hash"][0]


def test_row_hash_changes_when_a_business_value_changes():
    assert (
        add_row_hash(_df())["row_hash"][0]
        != add_row_hash(_df(quantity=[2]))["row_hash"][0]
    )


def test_row_hash_handles_missing_customer_and_description():
    df = _df(description=[None], customer_id=[None]).astype({"customer_id": "Int64"})
    assert len(add_row_hash(df)["row_hash"][0]) == 64
