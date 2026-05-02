"""
KPI Analysis & Visualisation
Generates all charts saved to results/
Author: Revanth Reddy Chitti
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ── Style ────────────────────────────────────────────────────────────────────
DARK_BG   = "#0f1117"
CARD_BG   = "#1a1d2e"
ACCENT1   = "#4f8ef7"   # blue
ACCENT2   = "#f7694f"   # orange-red
ACCENT3   = "#4fca8e"   # green
ACCENT4   = "#f7c44f"   # yellow
GRID_COL  = "#2a2d3e"
TEXT_COL  = "#e0e4f0"

PALETTE   = [ACCENT1, ACCENT2, ACCENT3, ACCENT4, "#a64ff7", "#4ff7e8"]

def style_ax(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(CARD_BG)
    ax.tick_params(colors=TEXT_COL, labelsize=9)
    ax.xaxis.label.set_color(TEXT_COL)
    ax.yaxis.label.set_color(TEXT_COL)
    ax.title.set_color(TEXT_COL)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COL)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e3:.0f}K" if x >= 1000 else f"£{x:.0f}"))
    if title:  ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    if xlabel: ax.set_xlabel(xlabel, fontsize=9)
    if ylabel: ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(axis="y", color=GRID_COL, linewidth=0.5, alpha=0.6)

# ── Load Data ────────────────────────────────────────────────────────────────
df = pd.read_csv("data/superstore_sales.csv", parse_dates=["order_date", "ship_date"])
df["year"]       = df["order_date"].dt.year
df["month"]      = df["order_date"].dt.month
df["month_name"] = df["order_date"].dt.strftime("%b")
df["year_month"] = df["order_date"].dt.to_period("M")

print(f"Loaded {len(df):,} rows | {df['year'].min()}–{df['year'].max()}")

# ════════════════════════════════════════════════════════════════════════════
# CHART 1: Monthly Revenue & Profit Trend
# ════════════════════════════════════════════════════════════════════════════
monthly = df.groupby("year_month").agg(revenue=("sales","sum"), profit=("profit","sum")).reset_index()
monthly["year_month_str"] = monthly["year_month"].astype(str)

fig, ax = plt.subplots(figsize=(14, 5), facecolor=DARK_BG)
x = range(len(monthly))
ax.fill_between(x, monthly["revenue"], alpha=0.15, color=ACCENT1)
ax.plot(x, monthly["revenue"], color=ACCENT1, linewidth=2.5, label="Revenue", marker="o", markersize=3)
ax.fill_between(x, monthly["profit"], alpha=0.15, color=ACCENT3)
ax.plot(x, monthly["profit"],  color=ACCENT3, linewidth=2,   label="Profit",  marker="o", markersize=3)

# Mark max revenue month
peak_idx = monthly["revenue"].idxmax()
ax.annotate(f"Peak\n{monthly.loc[peak_idx,'year_month_str']}",
            xy=(peak_idx, monthly.loc[peak_idx,"revenue"]),
            xytext=(peak_idx-4, monthly.loc[peak_idx,"revenue"]*1.08),
            arrowprops=dict(arrowstyle="->", color=ACCENT4),
            color=ACCENT4, fontsize=8)

tick_step = max(1, len(monthly)//12)
ax.set_xticks(list(range(0, len(monthly), tick_step)))
ax.set_xticklabels([monthly.loc[i,"year_month_str"] for i in range(0, len(monthly), tick_step)], rotation=45, ha="right")
style_ax(ax, "Monthly Revenue & Profit Trend (2021–2024)", ylabel="Amount (£)")
ax.legend(facecolor=CARD_BG, edgecolor=GRID_COL, labelcolor=TEXT_COL)
plt.tight_layout()
plt.savefig("results/01_monthly_revenue_profit.png", dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 1 saved")

# ════════════════════════════════════════════════════════════════════════════
# CHART 2: Revenue by Region (Bar)
# ════════════════════════════════════════════════════════════════════════════
region = df.groupby("region").agg(revenue=("sales","sum"), profit=("profit","sum")).reset_index().sort_values("revenue", ascending=False)

fig, ax = plt.subplots(figsize=(8, 5), facecolor=DARK_BG)
bars = ax.bar(region["region"], region["revenue"], color=PALETTE[:4], width=0.5, edgecolor=DARK_BG, linewidth=1.5)
for bar, val in zip(bars, region["revenue"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5000,
            f"£{val/1e6:.2f}M", ha="center", va="bottom", color=TEXT_COL, fontsize=10, fontweight="bold")
style_ax(ax, "Revenue by Region", ylabel="Total Revenue (£)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e6:.1f}M"))
plt.tight_layout()
plt.savefig("results/02_revenue_by_region.png", dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 2 saved")

# ════════════════════════════════════════════════════════════════════════════
# CHART 3: Category Performance (Grouped Bar)
# ════════════════════════════════════════════════════════════════════════════
cat = df.groupby("category").agg(revenue=("sales","sum"), profit=("profit","sum")).reset_index()

fig, ax = plt.subplots(figsize=(9, 5), facecolor=DARK_BG)
x = np.arange(len(cat))
w = 0.35
b1 = ax.bar(x - w/2, cat["revenue"], w, label="Revenue", color=ACCENT1, edgecolor=DARK_BG)
b2 = ax.bar(x + w/2, cat["profit"],  w, label="Profit",  color=ACCENT3, edgecolor=DARK_BG)
ax.set_xticks(x)
ax.set_xticklabels(cat["category"], color=TEXT_COL, fontsize=10)
style_ax(ax, "Revenue & Profit by Category", ylabel="Amount (£)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e6:.1f}M"))
ax.legend(facecolor=CARD_BG, edgecolor=GRID_COL, labelcolor=TEXT_COL)
plt.tight_layout()
plt.savefig("results/03_category_performance.png", dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 3 saved")

# ════════════════════════════════════════════════════════════════════════════
# CHART 4: Profit Margin by Sub-Category (Horizontal)
# ════════════════════════════════════════════════════════════════════════════
sub = df.groupby("sub_category").agg(revenue=("sales","sum"), profit=("profit","sum")).reset_index()
sub["margin"] = (sub["profit"] / sub["revenue"] * 100).round(1)
sub = sub.sort_values("margin", ascending=True)

fig, ax = plt.subplots(figsize=(10, 7), facecolor=DARK_BG)
colors = [ACCENT2 if m < 0 else ACCENT3 for m in sub["margin"]]
bars = ax.barh(sub["sub_category"], sub["margin"], color=colors, edgecolor=DARK_BG)
ax.axvline(0, color=TEXT_COL, linewidth=0.8, alpha=0.4)
for bar, val in zip(bars, sub["margin"]):
    ax.text(val + (0.3 if val >= 0 else -0.3), bar.get_y() + bar.get_height()/2,
            f"{val:.1f}%", va="center", ha="left" if val >= 0 else "right",
            color=TEXT_COL, fontsize=8)
ax.set_facecolor(CARD_BG)
ax.tick_params(colors=TEXT_COL, labelsize=9)
for spine in ax.spines.values(): spine.set_edgecolor(GRID_COL)
ax.set_title("Profit Margin % by Sub-Category", color=TEXT_COL, fontsize=13, fontweight="bold", pad=12)
ax.set_xlabel("Profit Margin (%)", color=TEXT_COL, fontsize=9)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
ax.grid(axis="x", color=GRID_COL, linewidth=0.5, alpha=0.6)
plt.tight_layout()
plt.savefig("results/04_profit_margin_subcategory.png", dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 4 saved")

# ════════════════════════════════════════════════════════════════════════════
# CHART 5: Segment Share (Donut)
# ════════════════════════════════════════════════════════════════════════════
seg = df.groupby("segment")["sales"].sum().reset_index()

fig, ax = plt.subplots(figsize=(7, 6), facecolor=DARK_BG)
wedges, texts, autotexts = ax.pie(
    seg["sales"], labels=seg["segment"],
    autopct="%1.1f%%", startangle=90,
    colors=PALETTE[:3],
    wedgeprops=dict(width=0.55, edgecolor=DARK_BG, linewidth=2),
    pctdistance=0.75
)
for t in texts:    t.set_color(TEXT_COL)
for t in autotexts: t.set_color(DARK_BG); t.set_fontweight("bold")
ax.set_title("Revenue Share by Customer Segment", color=TEXT_COL, fontsize=13, fontweight="bold")
ax.set_facecolor(DARK_BG)
plt.tight_layout()
plt.savefig("results/05_segment_share.png", dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 5 saved")

# ════════════════════════════════════════════════════════════════════════════
# CHART 6: YoY Revenue Growth
# ════════════════════════════════════════════════════════════════════════════
yoy = df.groupby("year")["sales"].sum().reset_index()
yoy["growth_pct"] = yoy["sales"].pct_change() * 100

fig, ax1 = plt.subplots(figsize=(9, 5), facecolor=DARK_BG)
ax2 = ax1.twinx()
bars = ax1.bar(yoy["year"].astype(str), yoy["sales"], color=ACCENT1, alpha=0.8, width=0.5)
ax2.plot(yoy["year"].astype(str), yoy["growth_pct"], color=ACCENT4, marker="o", linewidth=2.5, markersize=8)
for i, (yr, gp) in enumerate(zip(yoy["year"], yoy["growth_pct"])):
    if not pd.isna(gp):
        ax2.text(i, gp + 0.8, f"{gp:+.1f}%", ha="center", color=ACCENT4, fontsize=10, fontweight="bold")

ax1.set_facecolor(CARD_BG)
ax2.set_facecolor(CARD_BG)
ax1.tick_params(colors=TEXT_COL); ax2.tick_params(colors=ACCENT4)
for spine in ax1.spines.values(): spine.set_edgecolor(GRID_COL)
for spine in ax2.spines.values(): spine.set_edgecolor(GRID_COL)
ax1.set_title("Year-over-Year Revenue Growth", color=TEXT_COL, fontsize=13, fontweight="bold", pad=12)
ax1.set_ylabel("Annual Revenue (£)", color=TEXT_COL, fontsize=9)
ax2.set_ylabel("YoY Growth %", color=ACCENT4, fontsize=9)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1e6:.1f}M"))
ax1.grid(axis="y", color=GRID_COL, linewidth=0.5, alpha=0.6)
plt.tight_layout()
plt.savefig("results/06_yoy_growth.png", dpi=150, bbox_inches="tight", facecolor=DARK_BG)
plt.close()
print("✓ Chart 6 saved")

# ════════════════════════════════════════════════════════════════════════════
# Print KPI Summary
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "="*55)
print("KPI SUMMARY")
print("="*55)
print(f"Total Revenue  : £{df['sales'].sum():>12,.0f}")
print(f"Total Profit   : £{df['profit'].sum():>12,.0f}")
print(f"Profit Margin  : {df['profit'].sum()/df['sales'].sum()*100:>11.1f}%")
print(f"Total Orders   : {df['order_id'].nunique():>12,}")
print(f"Avg Order Value: £{df.groupby('order_id')['sales'].sum().mean():>12,.0f}")
print(f"Unique Customers: {df['customer_id'].nunique():>11,}")
print(f"Top Region     : {df.groupby('region')['sales'].sum().idxmax():>12}")
print(f"Top Category   : {df.groupby('category')['sales'].sum().idxmax():>12}")
print("="*55)
print("All charts saved to results/")
