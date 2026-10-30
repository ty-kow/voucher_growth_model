"""Enrollment and cost forecast charts side by side on one 16:9 canvas under a single title.

Usage (from the repo root):
    uv run python -m voucher_growth_model.plots.plot_forecast_slide <final_data> <forecast_csv> <out_png> [--table]
"""

import sys
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

from voucher_growth_model.plots.plot_forecast_cost import SCENARIOS, plot_forecast_cost
from voucher_growth_model.plots.plot_forecast_cost_table import plot_forecast_cost_table
from voucher_growth_model.plots.plot_forecast_enrollment import SAVE_DPI, TITLE as ENROLLMENT_TITLE, plot_forecast_enrollment

CANVAS_SIZE = (16, 9)  # inches
# Panel sizes in inches; widths sum to the canvas width. Wraps are characters per line at that width.
ENROLLMENT = dict(figsize=(9.5, 9), subtitle_wrap=112, notes_wrap=145, reserve_note_lines=5)
COST = dict(figsize=(6.5, 9), subtitle_wrap=68, notes_wrap=104)  # same height, so plot areas can line up
TITLE_FONTSIZE = 17  # the largest size that keeps the title on one line
PANEL = dict(show_title=False, subtitle_top=0.57, center_subtitle=True, show_source=False)  # one slide title, one sources line
SOURCE = ("Sources: Arizona Department of Education for ESA data, "
          "Arizona Office of Economic Opportunity for population data")
# The cost subtitle has two lines to the enrollment subtitle's three; drop it half a line so their centres match
SUBTITLE_LINE_HEIGHT = 0.167  # inches at 10 pt
COST_SUBTITLE_TOP = PANEL["subtitle_top"] + (3 - 2) / 2 * SUBTITLE_LINE_HEIGHT
COST_TITLE = "; Cost Could Reach \\${lo:,.1f}B to \\${hi:,.1f}B"


def plot_forecast_slide(voucher_csv: Path, forecast_csv: Path, out_path: Path, table: bool = False) -> None:
    """table=True replaces the cost bar chart with a table of FY46 costs."""
    cost_panel = plot_forecast_cost_table if table else plot_forecast_cost
    with tempfile.TemporaryDirectory() as tmp:
        left, right = Path(tmp) / "enrollment.png", Path(tmp) / "cost.png"
        axes_y = plot_forecast_enrollment(voucher_csv, forecast_csv, left, **PANEL, **ENROLLMENT)
        cost_panel(forecast_csv, right, axes_y=axes_y, **{**PANEL, "subtitle_top": COST_SUBTITLE_TOP}, **COST)  # panel level with the line graph
        images = [Image.open(p).convert("RGB") for p in (left, right)]
    canvas = Image.new("RGB", (sum(im.width for im in images), max(im.height for im in images)), "white")
    x = 0
    for im in images:
        canvas.paste(im, (x, 0))
        x += im.width

    f = pd.read_csv(forecast_csv)
    f46 = f[f["fy"] == "FY46"]
    enroll = f46["enroll"].drop_duplicates() / 1e3
    cost = [f46[(f46["takeup_scenario"] == k) & (f46["voucher_scenario"] == v)]["cost_real_fy26"].iloc[0] / 1e9
            for k, v, _, _ in SCENARIOS]
    title = (ENROLLMENT_TITLE.format(lo=enroll.min(), hi=enroll.max()).replace("\n", " ")
             + COST_TITLE.format(lo=min(cost), hi=max(cost)))

    fig = plt.figure(figsize=CANVAS_SIZE, dpi=SAVE_DPI)
    fig.figimage(np.asarray(canvas), 0, 0)  # pixel-exact, so the panels are not resampled
    fig.suptitle(title, fontsize=TITLE_FONTSIZE, fontweight="bold", y=1 - 0.09 / CANVAS_SIZE[1])
    fig.text(0.5, 0.012, SOURCE, ha="center", va="bottom", fontsize=8)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=SAVE_DPI)


if __name__ == "__main__":
    plot_forecast_slide(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), table="--table" in sys.argv[4:])
