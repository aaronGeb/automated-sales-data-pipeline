import pandas as pd

from pipeline.validate.rules import validate_sales


def _row(**kw):
    base = {
        "invoice_no": "536365",
        "stock_code": "85123A",
        "description": "X",
        "quantity": 1,
        "invoice_date": pd.Timestamp("2010-12-01"),
        "unit_price": 2.5,
        "customer_id": 17850,
        "country": "United Kingdom",
        "is_cancellation": False,
        "source_row": 2,
    }
    base.update(kw)
    return base


def test_rules_split_valid_and_rejected():
    df = pd.DataFrame(
        [
            _row(),  # valid
            _row(source_row=3),  # duplicate of first
            _row(invoice_no="A563185", unit_price=-5.0, source_row=4),  # adjustment
            _row(
                invoice_no="C536379", quantity=-2, is_cancellation=True, source_row=5
            ),  # valid cancellation
            _row(stock_code="85124", unit_price=0.0, source_row=6),  # zero price
        ]
    ).astype({"quantity": "Int64", "customer_id": "Int64"})

    res = validate_sales(df)

    assert res.valid["source_row"].tolist() == [2, 5]
    reasons = res.rejected.set_index("source_row")["reject_reason"]
    assert "duplicate_row" in reasons[3]
    assert "accounting_adjustment" in reasons[4]
    assert "non_positive_unit_price" in reasons[6]
