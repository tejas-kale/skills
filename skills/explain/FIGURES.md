# Figures

Every figure is inline SVG inside a `<figure>` with a caption that states the one thing the reader should see. Two routes; pick by where the numbers come from.

## By hand: diagrams, concept figures, fewer than about 30 points

Write the `<svg>` yourself with a `viewBox` and no fixed width.

- Colour through the template's classes (`axis`, `grid`, `ink`, `box`, `s1`..`s3`, `f1`..`f3`) or `var(--series-N)`, so the figure follows light and dark.
- A diagram of code or a pipeline: boxes and arrows, the hot path in `--accent`, each box labelled with the real name (`middleware/ratelimit.ts`), at most about 12 boxes. Past that, draw two diagrams.
- A live figure (a simulation, a distribution that reacts to a slider): put `<input type="range">` in `.controls`, keep the numbers in a script, and redraw the SVG on `input`. Show the current value in an `<output>`. Seed any random draw so the first view is the same on every load, and give a "resample" button when the point is variation.
- Label axes with the unit. Label series at the line end in place of a legend when there are three or fewer.

## From data: a Python script beside the page

For a chart of real data, write `<page name>.py` next to `<page name>.html` and keep it there: a change to the chart reruns it.

```python
"""Charts for 2026-11-16-checkout-readout.html.
Run: PYTHONPATH=<explain skill directory>/scripts python3 2026-11-16-checkout-readout.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from chart_svg import COLORS, put_chart, use_page_style

use_page_style()
rows = ...  # the query, or the file the data is read from

fig, ax = plt.subplots(figsize=(7, 3.2))
ax.plot(weeks, lift, color=COLORS["series-1"])
ax.fill_between(weeks, low, high, color=COLORS["series-1"], alpha=0.15)
ax.axhline(0, color=COLORS["border"], linewidth=1)
ax.set_ylabel("lift in conversion, percentage points")
put_chart("2026-11-16-checkout-readout.html", "lift", fig, label="Lift in conversion by week")
```

- The page holds one slot per chart inside its `<figure>`: `<!-- chart:lift --><!-- /chart:lift -->`. `put_chart` fills the slot and replaces it on a rerun.
- Draw only in `COLORS[...]` (text, muted, border, good, warn, bad, accent, series-1 to series-5). They become the page's tokens. A colormap (heatmap, continuous scale) keeps its own colours: choose one that reads on white and on near-black, such as `viridis`.
- plotnine: build the plot with the same `COLORS` in its scales and theme, then pass `plot.draw()` as the figure.
- Run it with the project's Python (`uv run python ...` in a uv project). matplotlib is the only requirement. Without it, draw by hand from the aggregated numbers.
- The script holds the query or the data path, so a reader can trace every chart to its numbers. List the script under sources in the provenance footer.

## What a data figure must show

- The unit, the period and the population, in the axis labels or the caption.
- Uncertainty wherever the number is an estimate: an interval band or error bars, with the level (95%) named in the caption.
- A zero baseline for bars; for lines, a caption that says so when the axis does not start at zero.
- The comparison the reader needs (control, baseline, last period) in the same figure, on the same axis.
