# Cross-functional delivery · Product Owner playbook

> The organisation, people, workshops and decisions on this page are simulated scenarios for an independent portfolio. They do not assert that these meetings happened at a named company.

## Product challenge

The PO must resolve **conflicting interpretations**, not merely merge columns. In the example, supplier item categories use manufacturing terminology while Commercial uses customer-facing groupings. Product Management sees technical features that cannot be lost. Finance needs analytical consistency but does not own the product taxonomy. Data & IT needs implementable rules and an unambiguous authoritative contract.

## Six functional workstreams

| Department | Needs and pressure | Governed responsibility | Acceptance contribution |
|---|---|---|---|
| Product Management | Correct technical meaning and classification | Taxonomy semantics; attribute definitions and applicability | Approve classifications and technical field rules |
| Commercial | Catalogue navigation and market positioning | Range, sector and commercial relevance, following approved policy | Review searchable groupings and cross-market usability |
| Procurement | Supplier identifiers, specifications and packs | Supplier mapping as evidence, not new corporate identity | Reconcile supplier references and exceptions |
| Operations | Operational identifiers and warehouse usability | Reconcile operational source facts and source history | Validate product matching and no invalid source writes |
| Finance | Comparable commercial metrics | Economic definitions and valuation authority | Validate metric semantics and analytical access restrictions |
| Data & IT | Reliable governed interfaces and delivery | Technical platform, schema, tests, API, traceability | Validate integration, privacy, deployment and supportability |

## Example decision cycle: a roller cover disagreement

**Business issue:** Procurement classifies a synthetic product by supplier packaging; Product Management classifies it by application material; Commercial needs buyers to find it under *Paint Rollers → Roller Covers*.

**Discovery:** Collect sample descriptions and source references. List possible taxonomy levels and identify whether packaging is product identity, a technical attribute or a sales offer. Capture trade-offs and impacted consumers.

**Decision:** Assign the accepted product to one terminal technical category. Keep pack units as a governed attribute and supplier packaging as source evidence. Do not embed two competing corporate classifications in the master record.

**Backlog impact:** Create criteria for terminal validity, `pack_units` applicability, source mapping consistency, and a governed correction request. Define consumer expectations for unchanged SKUs and updated classification versions.

**Demonstration:** Open a product in the UI, submit a reclassification request, approve as a different simulated actor, then verify product version and audit history.

## RACI (illustrative)

| Decision / output | Product Owner | Product Mgmt | Commercial | Procurement | Operations | Finance | Data & IT |
|---|---|---|---|---|---|---|---|
| Prioritised backlog | **A/R** | C | C | C | C | C | C |
| Taxonomy semantics | C | **A/R** | C | C | C | I | C |
| Technical attribute dictionary | R | **A** | C | C | C | I | R |
| Source identity mapping | C | C | I | **R** | **A** | I | R |
| Cross-functional product acceptance | **A** | R | R | C | C | C | R |
| Finance metric contract | C | I | C | I | C | **A/R** | R |
| API implementation and validation | C | C | I | C | C | I | **A/R** |
| Release communication and adoption | **A/R** | R | R | C | C | C | R |

*A = accountable; R = responsible; C = consulted; I = informed. A fictional governance arrangement for the demo.*

## PO prioritisation logic

1. **Reduce semantic risk first.** A dashboard is not useful if products or units are inconsistent.
2. **Deliver a bounded accepted product slice.** Taxonomy and representative attributes before full-scale cross-system ingestion.
3. **Make ownership explicit.** A definition is not accepted until a business owner and source authority are known.
4. **Protect consumers during change.** Classification corrections must preserve SKU, audit, versions and expected compatibility.
5. **Include nonfunctional requirements.** Data quality, access control, observability, traceability and supportability are backlog work, not unplanned cleanup.
6. **Sequence ProductIntelligence after the master.** Analytics can depend on governed context without gaining rights to edit it.

## Artefacts delivered in this portfolio

Stakeholder responsibilities, fictional decision scenario, RACI, product vision, functional taxonomy, attribute dictionary, governance workflow, API contracts, ProductIntelligence analytic boundary, tested backlog increments and a live local interface.
