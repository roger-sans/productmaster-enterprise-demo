# ProductIntelligence · Explainable product analysis

ProductIntelligence is a **working read-only analytical demonstration** composed of synthetic product context and synthetic operational/finance observations. It illustrates a governed extension, not a production forecasting or automated recommendation engine.

## Separation of authority

| Responsibility | ProductMaster | Analytical observations |
|---|---|---|
| Stable product identity | Owns master key and taxonomy identity | References the existing key |
| Technical specs | Owns approved metadata and values | Consumes them as context |
| Sales and returns | Does not own or edit | Source-owned period facts |
| Current stock and incoming supply | Does not own or edit | Source-owned cutoff/schedule facts |
| Finance amounts | Does not own or edit | Source-owned controlled finance facts |
| Explainable assessment | Exposes context | Creates calculated read-only facets |

## Synthetic example inputs

Each value is an independent `metric_observation` with metric code, product SKU, unit, observation period, source name, source revision and `as_of` timestamp. They are **fictional**. Some observations are intentionally absent and some demand values are zero to test correct handling of incomplete evidence.

| Metric code | Grain / period | Owner in fictional operating model |
|---|---|---|
| `net_sales_qty_90d` | Product, preceding 90 days | Sales ledger |
| `net_sales_amount_90d` | Product, preceding 90 days, EUR | Finance analytics |
| `gross_margin_amount_90d` | Product, preceding 90 days, EUR | Finance analytics |
| `stock_available` | Product, observed stock cutoff | Inventory operations |
| `open_demand_30d` | Product, next 30 days | Commercial demand |
| `inbound_supply_30d` | Product, next 30 days | Procurement/operations |

## Transparent calculations

Illustrative daily demand rate, when positive historic quantity is available:

\[
\mathrm{dailyDemand} = \frac{\mathrm{netSalesQty90d}}{90}
\]

Coverage is defined only when available stock and a positive demand rate exist:

\[
\mathrm{coverageDays} = \frac{\mathrm{availableStock}}{\mathrm{dailyDemand}}
\]

A simplified scenario shortfall is:

\[
\mathrm{projectedShortfall} = \max(0,\ \mathrm{openDemand30d} - \mathrm{availableStock} - \mathrm{inboundSupply30d})
\]

Margin percentage is calculated when compatible financial evidence is present and net revenue is strictly positive:

\[
\mathrm{margin\%} = 100\cdot\frac{\mathrm{grossMarginAmount90d}}{\mathrm{netSalesAmount90d}}
\]

### Explicit caveats

- The scenario does **not** infer due-date shortages per order or automate allocation; an enterprise model needs time-bucketed firm demand and supply, agreed stock eligibility, cancellations/returns, equivalent units and complete source watermarks.
- Coverage below 30 days is a **demonstration marker**, not a signed-off service risk threshold.
- Zero demand is not infinite coverage; without positive demand the ratio is **undefined**.
- Missing input means **missing**, not zero.
- Margin is a guardrail and availability facet; no automatic pricing or product lifecycle action is permitted.
- Product version and input source revision are exposed as provenance. The demo does not implement retained immutable evaluation snapshots or a genuine upstream provider contract.

## Product Owner acceptance criteria

1. No metric observation can update a product technical attribute through the read API.
2. The analytical row uses the existing product business identity and declared context version.
3. Zero and missing inputs produce explicit undefined/partial output, never fabricated zero performance.
4. Sources and observation periods are documented.
5. View results produce only **human review candidates** and explanation facets; there is no automated purchasing or operational write.
