"""Build docs/images/analytics-dashboard.png from the CSV reports."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

plt.switch_backend("Agg")  # render to file, no window

REPORTS = Path("reports")
OUT = Path("docs/images/analytics-dashboard.png")
COLOR = "#e8962e"

daily = pd.read_csv(REPORTS / "daily_sales.csv", parse_dates=["day"])
products = pd.read_csv(REPORTS / "top_products.csv")
regions = pd.read_csv(REPORTS / "regional_summary.csv")

thousands = FuncFormatter(lambda v, _: f"{v / 1000:,.0f}k")

fig, ax = plt.subplots(2, 2, figsize=(14, 8.5))
fig.suptitle("Sales Analysis", fontsize=18, fontweight="bold", x=0.02, ha="left")

# 1) Net revenue by month
monthly = daily.set_index("day")["net_revenue"].resample("MS").sum()
a = ax[0, 0]
a.bar(monthly.index.strftime("%b %y"), monthly.to_numpy(), color=COLOR)
a.set_title("Net revenue by month", loc="left")
a.yaxis.set_major_formatter(thousands)
a.tick_params(axis="x", rotation=45)

# 2) Top 10 products
top = products.sort_values("net_revenue").tail(10)
names = top["description"].fillna(top["stock_code"]).astype(str).str.slice(0, 30)
a = ax[0, 1]
a.barh(names, top["net_revenue"], color=COLOR)
a.set_title("Top 10 products by net revenue", loc="left")
a.xaxis.set_major_formatter(thousands)

# 3) Top countries excluding the United Kingdom
uk = regions.loc[regions["country"] == "United Kingdom", "net_revenue"].sum()
others = regions[regions["country"] != "United Kingdom"].nlargest(8, "net_revenue")
others = others.sort_values("net_revenue")
a = ax[1, 0]
a.barh(others["country"], others["net_revenue"], color=COLOR)
a.set_title(f"Top countries excluding UK (UK: {uk / 1e6:.2f}M)", loc="left")
a.xaxis.set_major_formatter(thousands)

# 4) Key figures
kpis = [
    ("Net revenue", f"{daily['net_revenue'].sum():,.0f}"),
    ("Gross revenue", f"{daily['gross_revenue'].sum():,.0f}"),
    ("Cancelled revenue", f"{daily['cancelled_revenue'].sum():,.0f}"),
    ("Orders", f"{int(daily['orders'].sum()):,}"),
    ("Trading days", f"{len(daily)}"),
    ("Countries", f"{len(regions)}"),
]
a = ax[1, 1]
a.axis("off")
a.set_title("Key figures", loc="left")
for i, (label, value) in enumerate(kpis):
    y = 0.88 - i * 0.15
    a.text(0.02, y, label, fontsize=12, color="#555555", transform=a.transAxes)
    a.text(0.60, y, value, fontsize=14, fontweight="bold", transform=a.transAxes)

fig.text(
    0.02,
    0.01,
    "Source: reports/*.csv generated from PostgreSQL by sales-pipeline. "
    "Currency is not stated in the source data.",
    fontsize=9,
    color="#777777",
)
fig.tight_layout(rect=(0, 0.03, 1, 0.95))
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=130)
print(f"Saved {OUT}")
