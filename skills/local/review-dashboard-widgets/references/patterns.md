# Common claim-vs-compute failure patterns

Shapes that a widget's gap between claim and compute tends to take. Check
every widget against every pattern below — most dashboards trip at least
three of these, and they recur across unrelated domains because they come
from how dashboards are built (dataset + fields + filters), not from any one
dashboard's subject matter.

**Unit mismatch.** A count sums something that is not additive across rows
(a sum of per-group distinct counts, not a distinct count over the whole
population — the two diverge exactly when groups overlap, which is when the
metric matters most), or it counts a narrower unit than its name claims (an
asset instead of an asset-and-category pair; a session instead of a person).
Compute the honest version alongside the dashboard's version and compare.

**Window mismatch.** A widget reads a fixed window (a `CURRENT_TIMESTAMP() -
INTERVAL n DAYS` baked into a view) while sitting beside — or under — a
date-range picker that visually appears to control it. Trace every filter
from the widget back to the dataset it actually binds; a filter on a
different dataset than the widget silently does nothing.

**Partial-period artifact.** Any time series ending on "today" or "this
period" plots a point built from partial data next to points built from
complete data. That last point reads as a drop (or a spike) that is really
just incompleteness, and it moves every chart sharing that grain at once. If
the dataset reads a materialized view, don't just check the fraction of the
period elapsed — re-derive the same number from the raw source table the MV
is built on; the gap between the two is usually the MV's own refresh lag,
concentrated entirely in the most recent period.

**Description/filter contradiction.** A widget's own description promises a
population ("active or clearing") that its underlying query filters down to a
narrower one ("active only"). Descriptions are typed once and drift from the
query as the query is tuned later — verify the description against the
query, never assume they agree because they sit next to each other.

**Encoding inconsistency across a "comparable" set.** A row of charts meant
to be read side by side (four rate charts, say) uses a different axis scale
or a different split on one of them (linear on three, log on the fourth;
unsplit on three, split by category on the fourth). The odd one out usually
exists because one metric has a long-tail outlier that the author fixed
locally instead of flagging — check whether that outlier is itself a finding
(see partial-period and small-denominator patterns).

**Category collapse.** Two distinct underlying event types get plotted under
one label because the nearest-sounding source column was chosen without
checking what values it actually holds (a "bounce" chart plotting connection
refusals because the source has no bounce event at all). List the distinct
values a column actually takes before trusting a widget's name for it.

**Unread dataset.** A dataset is loaded by the dashboard but referenced by no
widget on any page. Harmless to results, but worth flagging — it usually
means an earlier widget was removed without cleaning up its dataset, and it
is a maintenance signal about how the dashboard is edited.

**Global claim unmet.** Header or section text makes a page-level promise
("real-time," "per-<dimension>") that no individual widget's query actually
delivers (every widget reads a windowed, cacheable query; nothing splits by
that dimension). Check global claims separately from widget claims — they
are easy to skip because no single widget is "responsible" for them.

**Cached-load discrepancy.** The page can serve a cached result on open that
differs from a forced refresh. If a claim depends on a number seen on
load, reload with a forced refresh and compare before recording the number in
the review.
