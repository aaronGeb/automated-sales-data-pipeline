import sys
import time
from pathlib import Path

from pipeline.extract.excel_reader import read_sales_excel
from pipeline.load.database import get_engine
from pipeline.load.loader import load_sales
from pipeline.transform.cleaning import clean_sales
from pipeline.validate.quarantine import write_rejected
from pipeline.validate.rules import validate_sales

src = Path(sys.argv[1] if len(sys.argv) > 1 else "data/raw/Online Retail.xlsx")
res = validate_sales(clean_sales(read_sales_excel(src)))
print("valid:", len(res.valid), "rejected:", len(res.rejected))
print("rejected file:", write_rejected(res.rejected, Path("data/rejected"), src.name))

engine = get_engine()
for run in (1, 2):
    t = time.time()
    r = load_sales(res.valid, engine)
    print(f"run {run}: attempted={r.attempted} inserted={r.inserted} skipped={r.skipped} ({time.time() - t:.1f}s)")
