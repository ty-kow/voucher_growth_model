"""Enrollment and cost forecast charts side by side on one 16:9 canvas under a single title.

Usage (from the repo root):
    uv run python -m voucher_growth_model.plots_report.plot_forecast_slide <report_data> <forecast_csv> <out_png> [--table] [--panels]
"""

import sys
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

from voucher_growth_model.plots_report.plot_forecast_cost import SCENARIOS, plot_forecast_cost
from voucher_growth_model.plots_report.plot_forecast_cost_table import plot_forecast_cost_table
from voucher_growth_model.plots_report.plot_forecast_enrollment import SAVE_DPI, TITLE as ENROLLMENT_TITLE, plot_forecast_enrollment

CANVAS_SIZE = (16, 9)  # inches
# Panel sizes in inches; widths sum to the canvas width. Wraps are characters per line at that width.
TITLE_GAP = 0.95  # inches at the top of the canvas reserved for the two-line title; the panels fill the rest
PANEL_HEIGHT = CANVAS_SIZE[1] - TITLE_GAP
ENROLLMENT = dict(figsize=(9.5, PANEL_HEIGHT), subtitle_wrap=112, notes_wrap=145, reserve_note_lines=5)
COST = dict(figsize=(6.5, PANEL_HEIGHT), subtitle_wrap=68, notes_wrap=104)  # same height, so plot areas can line up
TITLE_FONTSIZE = 22  # the largest size that keeps each of the two title lines inside the canvas
PANEL = dict(show_title=False, subtitle_top=0.15, center_subtitle=True, show_source=False)  # one slide title, one sources line
PANEL_TITLES = ("Enrollment Forecasts", "Cost Forecasts")  # table variant only: left, right
TITLED_SUBTITLE_TOP = 0.6  # inches, leaves room above the subtitles for the panel titles
TITLED_SUBTITLE_FONTSIZE = 12
# Subtitle wraps (characters per line) at that size: the left one stays within the line graph's plot area (about 9.8 in
# wide at 12 pt); the right one is centred on its tables
LEFT_TABLE_WRAP = dict(subtitle_wrap=84)
RIGHT_TABLE_WRAP = dict(subtitle_wrap=56)
SOURCE = ("Sources: Arizona Department of Education for ESA data, "
          "Arizona Office of Economic Opportunity for population data")
# The cost subtitle has two lines to the enrollment subtitle's three; drop it half a line so their centres match
SUBTITLE_LINE_HEIGHT = 0.167  # inches at 10 pt
COST_SUBTITLE_TOP = PANEL["subtitle_top"] + (3 - 2) / 2 * SUBTITLE_LINE_HEIGHT
PANEL_FILES = ("forecast_enrollment_report.png", "forecast_cost_table.png")  # left, right
# Standalone report panels only; the slide keeps PANEL_TITLES and its wraps
REPORT_ENROLLMENT_TITLE, REPORT_COST_TITLE = "ESA Voucher Enrollment Forecasts", "ESA Voucher Cost Forecasts"
# None keeps SUBTITLE's hand-set breaks (line 2 starts at "after"); three lines that fit the figure width
REPORT_SUBTITLE_WRAP, REPORT_SUBTITLE_FONTSIZE = None, 11
COST_TITLE =";\nCost Could Reach \\${lo:,.1f}B to \\${hi:,.1f}B"


def plot_forecast_slide(voucher_csv: Path, forecast_csv: Path, out_path: Path, table: bool = False,
                        panels: bool = False) -> None:
    """table=True replaces the cost bar chart with a table of FY46 costs. panels=True also saves each panel on its own
    next to out_path (PANEL_FILES)."""
    cost_panel = plot_forecast_cost_table if table else plot_forecast_cost
    with tempfile.TemporaryDirectory() as tmp:
        left, right = Path(tmp) / "enrollment.png", Path(tmp) / "cost.png"
        # The table variant heads each side with a title, so its subtitles start lower, level with each other; the bar
        # variant centres the cost subtitle on the enrollment subtitle instead
        panel = {**PANEL, "subtitle_top": TITLED_SUBTITLE_TOP, "subtitle_fontsize": TITLED_SUBTITLE_FONTSIZE} if table else PANEL
        left_extra = dict(panel_title=PANEL_TITLES[0], **LEFT_TABLE_WRAP) if table else {}
        right_extra = dict(panel_title=PANEL_TITLES[1], **RIGHT_TABLE_WRAP) if table else {}
        axes_y = plot_forecast_enrollment(voucher_csv, forecast_csv, left, **panel, **{**ENROLLMENT, **left_extra})
        panel = panel if table else {**PANEL, "subtitle_top": COST_SUBTITLE_TOP}
        cost_panel(forecast_csv, right, axes_y=axes_y, **panel, **{**COST, **right_extra})  # panel level with the line graph
        images = [Image.open(p).convert("RGB") for p in (left, right)]
    if panels:  # standalone panels for the written report; the cost panel is redrawn centred and with sources
        plot_forecast_enrollment(voucher_csv, forecast_csv, out_path.parent / PANEL_FILES[0],
                                 **{**panel, "source_below_notes": True, "center_subtitle": False,
                                    "subtitle_fontsize": REPORT_SUBTITLE_FONTSIZE},
                                 **{**ENROLLMENT, **left_extra, "panel_title": REPORT_ENROLLMENT_TITLE,
                                    "subtitle_wrap": REPORT_SUBTITLE_WRAP})
        cost_panel(forecast_csv, out_path.parent / PANEL_FILES[1], axes_y=axes_y,
                   **{**panel, "center_subtitle": False, "show_source": True},
                   **{**COST, **right_extra, "panel_title": REPORT_COST_TITLE})
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
    plot_forecast_slide(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), table="--table" in sys.argv[4:],
                        panels="--panels" in sys.argv[4:])
