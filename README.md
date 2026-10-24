# Minghao Zhang · Margin Watch

**Author:** Minghao Zhang

A small Streamlit review for a **regional sales manager** deciding which product groups need a discount and cost review before the next promotion cycle.

> Design rationale draft: review these choices and adapt the wording to reflect your own reasoning before submitting. The assignment requires your own README. The byline “Minghao Zhang” is the author’s real name, not a claim about an existing team or a real client interview.

## Step 1 — Dataset and decision-maker

**Source:** [Superstore Dataset on Kaggle, uploaded by Vivek Chowdhury](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final). The downloaded `Sample - Superstore.csv` is included as `superstore.csv`; no rows were sampled or aggregated away. It is 2,287,806 bytes (about 2.18 MiB), comfortably below the 25 MB limit. One row is an **order line**, not a whole order: 9,994 rows cover 5,009 distinct orders and 21 columns. Order dates span **3 January 2014 to 30 December 2017**.

This is a realistic retail business example with products, regions, sales, discounts and profit. It is **fictitious/sample retail data**, not verified accounts from a real operating company. [Tableau’s sample-data page](https://public.tableau.com/app/learn/sample-data) describes Superstore as a fictitious company. The Kaggle metadata does not establish transaction authenticity or give a full generation method; this project does not claim that its historical dollar totals describe a real retailer. Kaggle lists the license as “Other (specified in description)”; no additional license is asserted here. See `SOURCE.md` for the download record.

The intended viewer is one role: a **regional sales manager** responsible for promotions and coordination with product managers. The region filter lets that person select their own area. This is not an executive overview or a warehouse inventory tool.

## Step 2 — Why a dashboard

The proposed operating workflow is a Monday morning margin review before the manager agrees to the next promotion cycle. These are design assumptions, not observations from an interview.

**Decision sentence:** If the regional sales manager sees the latest completed month’s reported profit margin below 10%, or a product group with negative profit, they will ask that product owner to examine discounting and cost entries before approving another promotion.

Without the app, a plausible workflow is downloading an order report, making separate monthly and product-group pivots, and checking whether their filters match. The cost is repeated reconciliation work and the chance of overlooking a loss behind a strong sales total. No measured hours or dollar savings are claimed because no business time study was conducted.

An email can flag a problem but cannot let the manager switch between their region’s years and inspect the same definitions consistently. A static annual report is useful for a one-off presentation but becomes inconvenient for recurring reviews. An alert is appropriate for a threshold breach; the dashboard supplies the context needed to decide what to investigate after the alert. The small scope is deliberate: two recurring questions are enough to support this role’s action.

## Step 3 — EDA, content choices and layout

`superstore-eda.ipynb` contains executed Pandas and Matplotlib analysis: shape, types, missingness, duplicates, distribution plots, monthly margins, product-group profit and discount relationships.

The snapshot has **no missing cells** and **no duplicated full rows or Row IDs**. Sales total **$2,297,200.86**, reported profit totals **$286,397.02**, and the ratio of those sums is **12.47%**. However, **1,871 order lines (18.72%)** have negative profit. Tables lose **$17,725.48**, Bookcases lose **$3,472.56**, and Supplies lose **$1,189.10** across the full file. A positive company-level number can therefore hide product losses. The median line’s sales are **$54.49**, while the largest is **$22,638.48**: large lines can influence totals and deserve investigation, not automatic deletion.

### Three headline numbers

| KPI | Definition | Why it is shown |
|---|---|---|
| Sales | Sum of source `Sales` for the selected region and year | Shows the scale of activity behind the profit result. |
| Reported profit | Sum of source `Profit` for the same rows | Shows the dollar outcome of the activity. |
| Profit margin | Sum of Profit / sum of Sales | Makes profitability readable relative to sales; never averages line margins. |

The KPI row uses `st.columns` and three `st.metric` calls. It deliberately has no year-over-year deltas: those would need a carefully aligned comparison window and more explanation than this first review needs.

### Two charts and two filters

1. **Monthly profit margin:** a line reveals when the region weakened and whether a poor year is driven by particular months. The dashed 10% line is a proposed investigation threshold, explicitly labeled as a design assumption, not a measured company target. Missing months are reindexed to missing values so they would appear as gaps rather than fabricated zeroes.
2. **Profit by product subcategory:** sorted horizontal bars reveal where to direct the cost/discount review. All 17 groups remain visible; selecting only a top five could hide losses. Negative bars use coral, positive bars teal, and a zero reference keeps the sign clear.

The filters are **region** and **order year**. The year defaults to the latest year in the file, 2017. There are no unrelated customer, shipping or postcode controls. Keeping category unfiltered preserves the ranking needed for the decision. The dashboard reports the selected order-line and distinct-order counts in a caption to prevent confusing them.

### Items intentionally cut

- **Customer segment pie chart:** an interesting revenue breakdown, but segment shares alone do not tell this manager which loss-making product group to review. It would compete with the actionable profit chart.
- **Postal-code sales map:** geographic detail looks attractive, but the manager acts on product promotions in a chosen region. A map adds visual effort without changing that action.
- **Transaction table and customer names:** these are not needed for the initial review. A future authorized drill-down could support an investigation, but displaying thousands of rows would bury the first decision.

### Misleading interpretations and how the app handles them

- This is a frozen 2014–2017 sample, not current performance. Its period and the intended production refresh schedule are visible under the title.
- `Profit` has no full cost-accounting definition in the accessible metadata. The label is **reported profit**, not complete company net income; unknown overhead, returns and marketing costs are acknowledged.
- The app treats dollars as USD for this US retail example and states this assumption. Currency is not a separate source field.
- High discounts and losses are associated in the file, but the analysis cannot prove discounts caused losses or estimate an optimal price. The app recommends checking costs and discounts, not automatically changing them.
- Aggregated margins are weighted by sales, not by the number of rows. Negative profit is retained. Large transactions are retained and disclosed because they may be legitimate in this sample.

### Page blueprint, top to bottom

```text
Team title + one-line role/decision caption
Historical data period + intended refresh schedule
Region / year controls in the sidebar
Selected region/year → Sales | Reported profit | Margin
Brief list of product groups to review
Monthly margin chart | Product-group profit chart
Collapsed explanation of definitions and limitations
```

The top answers “is anything wrong?” before the viewer scrolls. The middle explains when and where. The bottom holds interpretation notes; an unnecessary detail table is omitted. This is the written layout blueprint, not a claim that a paper sketch was completed in class.

## Step 4 — Refresh, review and action

In a real deployment, order data should refresh **nightly**, after the day’s sales and cost postings are reconciled. The manager reviews it **every Monday** before the promotion meeting. Refresh and review are different: a nightly load keeps the next review current, whereas minute-by-minute updates would add processing without changing a weekly promotion decision.

Track **monthly reported profit margin** over time. At the Monday review, investigate the latest **completed** month if it is below **10%**; do not compare an incomplete month with full previous months. The threshold is an initial business rule to validate with the manager, not an empirically optimized target. The negative-profit product groups provide the first investigation list. An investigation should confirm postings and price/cost changes before acting.

One-day-old reconciled data is consistent with this weekly workflow. A week-old view could allow one more promotion cycle to repeat a loss-making offer or conceal a cost change. The available data cannot quantify that avoidable cost. Production would also need a visible last-successful-load timestamp and a failed-load alert; the present CSV has no live feed, so the app does not invent one.

## Step 5 — Run and deploy

The project uses `uv`, with `.python-version` set to **3.14**, project dependencies in `pyproject.toml`, a reproducible `uv.lock`, and pinned app requirements in `requirements.txt`.

```bash
uv sync
uv run streamlit run app.py
```

The EDA notebook uses the development dependencies included in `uv sync`. It can be opened with a Jupyter-compatible notebook editor using the project environment. Its saved outputs were executed in order with Python 3.14.7; no credentials are needed.

Publish this directory to a public repository in **your own GitHub account**, then deploy `app.py` from that repository in **your own Streamlit Community Cloud account**. Set Python to **3.14** in Advanced settings. The app reads its CSV relative to `app.py`, so deployment does not depend on a local Windows path.

Before submission, verify both links open successfully, adapt this draft rationale to your own decisions, confirm the byline, and put the deployed app URL and repository URL in the first Markdown cell of `phone-trade-in.ipynb`.
