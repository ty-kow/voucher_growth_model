"""Enrollment and cost forecast charts side by side on one 16:9 canvas under a single title.

Usage (from the repo root):
    uv run python -m voucher_growth_model.plots_report.plot_forecast_slide <report_data> <forecast_csv> <out_png>
"""

import sys
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

from voucher_growth_model.plots_report.plot_forecast_cost_table import ROWS, plot_forecast_cost_table
from voucher_growth_model.plots_report.plot_forecast_enrollment import SAVE_DPI, TITLE as ENROLLMENT_TITLE, plot_forecast_enrollment

CANVAS_SIZE = (16, 9)  # inches
# Panel sizes in inches; widths sum to the canvas width. Wraps are characters per line at that width.
TITLE_GAP = 0.95  # inches at the top of the canvas reserved for the two-line title; the panels fill the rest
PANEL_HEIGHT = CANVAS_SIZE[1] - TITLE_GAP
ENROLLMENT = dict(figsize=(9.5, PANEL_HEIGHT), subtitle_wrap=112, notes_wrap=145, reserve_note_lines=5)
COST = dict(figsize=(6.5, PANEL_HEIGHT), subtitle_wrap=68, notes_wrap=104)  # same height, so plot areas can line up
TITLE_FONTSIZE = 22  # the largest size that keeps each of the two title lines inside the canvas
PANEL = dict(show_title=False, subtitle_top=0.15, center_subtitle=True, show_source=False)  # one slide title, one sources line
PANEL_TITLES = ("Enrollment Forecasts", "Cost Forecasts")  # left, right
TITLED_SUBTITLE_TOP = 0.6  # inches, leaves room above the subtitles for the panel titles
TITLED_SUBTITLE_FONTSIZE = 12
# Subtitle wraps (characters per line) at that size: the left one stays within the line graph's plot area (about 9.8 in
# wide at 12 pt); the right one is centred on its tables
LEFT_TABLE_WRAP = dict(subtitle_wrap=84)
RIGHT_TABLE_WRAP = dict(subtitle_wrap=56)
SOURCE = ("Sources: Arizona Department of Education for ESA data, "
          "Arizona Office of Economic Opportunity for population data")
COST_TITLE =";\nCost Could Reach \\${lo:,.1f}B to \\${hi:,.1f}B"


def plot_forecast_slide(voucher_csv: Path, forecast_csv: Path, out_path: Path) -> None:
    """The standalone report panels come from plot_forecast_enrollment.py and plot_forecast_cost_table.py."""
    with tempfile.TemporaryDirectory() as tmp:
        left, right = Path(tmp) / "enrollment.png", Path(tmp) / "cost.png"
        # Each side has a title, so the subtitles start lower, level with each other
        panel = {**PANEL, "subtitle_top": TITLED_SUBTITLE_TOP, "subtitle_fontsize": TITLED_SUBTITLE_FONTSIZE}
        axes_y = plot_forecast_enrollment(voucher_csv, forecast_csv, left, **panel,
                                          **{**ENROLLMENT, "panel_title": PANEL_TITLES[0], **LEFT_TABLE_WRAP})
        plot_forecast_cost_table(forecast_csv, right, axes_y=axes_y, **panel,
                                 **{**COST, "panel_title": PANEL_TITLES[1], **RIGHT_TABLE_WRAP})  # level with the line graph
        images = [Image.open(p).convert("RGB") for p in (left, right)]
    gap = round(TITLE_GAP * SAVE_DPI)
    canvas = Image.new("RGB", (sum(im.width for im in images), max(im.height for im in images) + gap), "white")
    x = 0
    for im in images:
        canvas.paste(im, (x, gap))
        x += im.width

    f = pd.read_csv(forecast_csv)
    f46 = f[f["fy"] == "FY46"]
    enroll = f46["enroll"].drop_duplicates() / 1e3
    cost = [f46[(f46["takeup_scenario"] == k) & (f46["voucher_scenario"] == v)]["cost_real_fy26"].iloc[0] / 1e9
            for k, _ in ROWS for v in ("infl2", "hist")]  # every cell of the FY46 table
    title = (ENROLLMENT_TITLE.format(lo=enroll.min(), hi=enroll.max()).replace("\n", " ")
             + COST_TITLE.format(lo=min(cost), hi=max(cost)))

    fig = plt.figure(figsize=CANVAS_SIZE, dpi=SAVE_DPI)
    fig.figimage(np.asarray(canvas), 0, 0)  # pixel-exact, so the panels are not resampled
    fig.suptitle(title, fontsize=TITLE_FONTSIZE, fontweight="bold", y=1 - 0.09 / CANVAS_SIZE[1])
    fig.text(0.5, 0.012, SOURCE, ha="center", va="bottom", fontsize=8)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=SAVE_DPI)


if __name__ == "__main__":
    plot_forecast_slide(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
