import pandas as pd

from pipeline.transform.cleaning import clean_sales


def test_casts_and_flags_cancellations():
    raw = pd.DataFrame(
        {
            "invoiceno": [" c536379", "536365"],
            "stockcode": ["d", "85123A"],
            "description": ["Discount", ""],
            "quantity": ["-1", "6.5"],
            "invoicedate": ["2010-12-01 09:41:00", "not a date"],
            "unitprice": ["27.50", "2.55"],
            "customerid": ["14527", None],
            "country": [" United Kingdom ", "EIRE"],
        }
    )

    out = clean_sales(raw)

    assert out.loc[0, "invoice_no"] == "C536379"
    assert out["is_cancellation"].tolist() == [True, False]
    assert out.loc[0, "quantity"] == -1
    assert pd.isna(out.loc[1, "quantity"])  # fractional -> NA
    assert pd.isna(out.loc[1, "invoice_date"])  # bad date -> NaT
    assert pd.isna(out.loc[1, "description"])  # "" -> NA
    assert out.loc[1, "country"] == "EIRE"
