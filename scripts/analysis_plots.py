# Script to generate some overview plots
from pathlib import Path

import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

from db.utils import create_db_session

BASE_DIR = Path(__file__).resolve().parents[1]
PLOTS_DIR = BASE_DIR / "plots"
PLOTS_DIR.mkdir(exist_ok=True)


Session = create_db_session()
with Session() as session:
    landslide_view = gpd.read_postgis(
        "SELECT * FROM landslides_view", session.bind, geom_col="geometry"
    )

# Plotting the landslide data
fig, ax = plt.subplots(figsize=(10, 10))
landslide_view.plot(
    ax=ax,
    column="classification_name",
    legend=True,
    alpha=0.75,
    markersize=1.5,
    cmap="tab10",
)
cx.add_basemap(
    ax,
    crs=landslide_view.crs,
    source=cx.providers.CartoDB.PositronNoLabels,
    attribution_size=6,
)
ax.set_axis_off()
fig.savefig(PLOTS_DIR / "classification-map.png", dpi=150, bbox_inches="tight")

# Plot the number of events by year
fig, ax = plt.subplots(figsize=(10, 6))
landslide_view["event_year"] = landslide_view["datetime"].dt.year

year_counts = landslide_view["event_year"].value_counts().sort_index()
year_counts = year_counts[year_counts.index >= 1900]
year_counts.plot(ax=ax, kind="line", color="#6F60A1", marker="o", markersize=3)

plt.ylabel("Number of events")
plt.xlabel(None)
fig.savefig(PLOTS_DIR / "years.svg", bbox_inches="tight")

# Pie chart of landslide classifications with percentage labels
classification_counts = landslide_view["classification_name"].value_counts()
total = classification_counts.sum()

# Explode small slices
explode = [0.1 if (val / total) < 0.01 else 0 for val in classification_counts]

fig, ax = plt.subplots(figsize=(10, 6))

# Pie chart
wedges, texts, autotexts = ax.pie(
    classification_counts,
    labels=None,
    autopct=lambda p: f"{p:.2f}%" if p >= 1 else "",
    startangle=-20,
    pctdistance=0.8,
    explode=explode,
    colors=plt.cm.tab10.colors,
)

# --- Annotation logic ---
for i, (wedge, count) in enumerate(
    zip(wedges, classification_counts, strict=True)
):
    percentage = count / total

    label_text = (
        f"{classification_counts.index[i]}\n"
        f"{percentage * 100:.2f}% (N={count})"
    )

    if percentage < 0.01:
        # Mid-angle of slice
        ang = (wedge.theta2 + wedge.theta1) / 2
        ang_rad = np.deg2rad(ang)

        center, r = wedge.center, wedge.r

        # Small angular offset to reduce overlap
        ang_offset = -8 if i % 2 == 0 else 8
        ang_rad_shifted = np.deg2rad(ang + ang_offset)

        # Leader line start and end
        x_start = center[0] + r * np.cos(ang_rad)
        y_start = center[1] + r * np.sin(ang_rad)

        x_end = center[0] + 1.3 * r * np.cos(ang_rad_shifted)
        y_end = center[1] + 1.3 * r * np.sin(ang_rad_shifted)

        ax.plot([x_start, x_end], [y_start, y_end], color="gray", lw=0.8)

        ax.text(
            x_end + (0.02 if np.cos(ang_rad_shifted) > 0 else -0.02),
            y_end,
            label_text,
            ha="left" if np.cos(ang_rad_shifted) > 0 else "right",
            va="center",
            fontsize=8,
        )

    else:
        # Label directly on slice
        texts[i].set_text(label_text)
        texts[i].set_fontsize(8)

# Style percentage text inside slices
for autotext in autotexts:
    autotext.set_fontsize(8)
    autotext.set_color("black")
    autotext.set_weight("bold")

ax.axis("equal")
plt.tight_layout()
fig.savefig(PLOTS_DIR / "classification-pie.svg", bbox_inches="tight")
