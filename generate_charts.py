"""Rebuilds the three README charts from data/Audible_Cleaned_Dashboard.xlsx.

Replaces the original Excel-pivot-table workflow (not reproducible - no
formulas or pivot definitions were ever committed) with a script anyone can
re-run against the same cleaned data.
"""

import pandas as pd
import matplotlib.pyplot as plt

BLUE = "#2a78d6"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
SURFACE = "#fcfcfb"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK_SECONDARY,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


def style_axes(ax):
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(BASELINE)
    ax.spines["bottom"].set_color(BASELINE)


df = pd.read_excel("data/Audible_Cleaned_Dashboard.xlsx")
df = df.rename(columns={"Unnamed: 11": "Price"})
df["Price"] = (
    df["Price"].astype(str).str.replace(r"[$,]", "", regex=True).astype(float)
)
english = df[df["language"] == "English"].copy()

# ---------------------------------------------------------------------------
# 1. Author market dominance: volume vs. average price, top 15 by volume
# ---------------------------------------------------------------------------
author_stats = english.groupby("Cleaned_author").agg(
    books=("name", "size"), avg_price=("Price", "mean")
)
top15 = author_stats.sort_values("books", ascending=False).head(15)

fig, ax = plt.subplots(figsize=(8, 5.5))
ax.scatter(top15["books"], top15["avg_price"], s=90, color=BLUE,
           edgecolors=SURFACE, linewidths=1.2, zorder=3)
to_label = top15.sort_values("books", ascending=False).head(6).sort_values("avg_price")
offsets = [(8, -12), (8, 10), (8, -12), (8, 10), (8, -12), (8, 10)]
for (author, row), offset in zip(to_label.iterrows(), offsets):
    label = author if len(author) <= 22 else author[:20] + "…"
    ax.annotate(label, (row["books"], row["avg_price"]),
                textcoords="offset points", xytext=offset, fontsize=8.5, color=INK_SECONDARY)
ax.set_xlabel("Titles published")
ax.set_ylabel("Average price ($)")
ax.set_title("Author Market Dominance vs. Pricing Power (Top 15 by volume)",
             loc="left", fontsize=12.5, fontweight="bold")
ax.grid(True, color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
style_axes(ax)
plt.tight_layout()
plt.savefig("images/author_dominance.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 2. Market growth: English titles released per year
# ---------------------------------------------------------------------------
by_year = english.set_index("release_date").resample("YS").size()
by_year = by_year[by_year.index.year >= 2000]

fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(by_year.index.year, by_year.values, color=BLUE, width=0.7)
ax.set_ylabel("Titles released")
ax.set_title("Audiobook Market Growth (English titles per year)",
             loc="left", fontsize=13, fontweight="bold")
ax.yaxis.grid(True, color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
style_axes(ax)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("images/market_growth.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 3. Price distribution
# ---------------------------------------------------------------------------
priced = english[(english["Price"] > 0) & (english["Price"] < english["Price"].quantile(0.99))]

fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(priced["Price"], bins=40, color=BLUE, edgecolor=SURFACE, linewidth=0.5)
ax.set_xlabel("Price ($)")
ax.set_ylabel("Number of titles")
ax.set_title("Overall Price Distribution (English catalog)", loc="left",
             fontsize=13, fontweight="bold")
ax.yaxis.grid(True, color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
style_axes(ax)
plt.tight_layout()
plt.savefig("images/price_distribution.png", dpi=150)
plt.close()

print("Charts written to images/")
