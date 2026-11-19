# Product roadmap, prioritized backlog and criteria of acceptance

**Product vision:** create a trusted corporate product context that departments can use without interpreting competing spreadsheets or maintaining duplicate labels.

**Primary user groups:** product owner, product managers, commercial catalogue users, procurement stewards, operations, finance, data engineers, data analysts and read-only consuming applications.

## Value-driven releases (illustrative)

| Sequence | Outcome | Demonstration evidence | Product owner decision |
|---|---|---|---|
| 0. Discovery | Understand departmental discrepancies | Case-study workshops, role matrix, decisions | Resolve semantics before architecture |
| 1. Taxonomy | Shared hierarchy and terminal validity | 192-node, three-level synthetic model | Prioritise accepted classification rules |
| 2. Master | Searchable product identity and specifications | 640 products, 25 typed definitions, source mappings | Deliver reusable master before analytical enrichment |
| 3. Governance | Controlled safe modifications | Request/approve/reject, version checks, audit | Protect ownership and downstream consumption |
| 4. Intelligence | Explainable decision-support layer | Read-only synthetic metrics, coverage and evidence gaps | Never conflate product context and observations |

## Prioritised epics

| Rank | Epic | Business value | Dependency | Definition of done |
|---|---|---|---|---|
| P0 | Shared taxonomy | Search and reporting consistency | Cross-functional semantic review | Stable IDs, correct ancestry, accepted leaves |
| P0 | Corporate product identity | Source reconciliation without duplicates | Identity contract | Unique reference, provenance and lookup API |
| P0 | Governed specifications | Reliable technical descriptions | Taxonomy | Controlled data type, unit, applicability, requiredness |
| P0 | Correction workflow | Trusted change history | Master and owners | Request, independent review, version and audit |
| P1 | Consumer contracts | Reusable data products | Master + governance | Documented versioned read endpoints |
| P1 | Data quality | Confidence and explainable exceptions | Attribute contracts | Completeness/quality rules and tests |
| P1 | ProductIntelligence | Better human interpretation of facts | Stable master + source observations | Explainable source-backed metrics with missing-data handling |
| P2 | Production enablement | Enterprise resilience | Access and deployment decisions | SSO, RBAC, backup/recovery, telemetry, operations acceptance |

## Stories and acceptance scenarios

### Story PM-01 — Terminal classification

*As a product data steward, I want to select only a valid terminal classification so that downstream users consume an unambiguous family, subfamily and optional type.*

**Acceptance:** family-level assignments are invalid; a subfamily with no type children is valid; a subfamily with children requires a valid type; repeated labels remain independent under separate parents; changes to an accepted product go through the approval queue.

### Story PM-02 — Governed technical attributes

*As a product manager, I want category-specific technical specifications with units and controlled values so that products can be compared without free-text ambiguity.*

**Acceptance:** inapplicable attribute is rejected; controlled option outside vocabulary is rejected; numeric values cannot be unrelated strings; accepted product has all required attributes; new required definitions cannot silently invalidate existing accepted data.

### Story PM-03 — Correction with business approval

*As a commercial user, I want to propose a correction with evidence and receive a documented decision so that I can resolve catalogue discrepancies without overwriting existing trusted records.*

**Acceptance:** submission does not change the product; requestor cannot decide; revalidation checks version and validity; approval changes the master exactly once; rejection preserves it; audit links old and new state.

### Story PI-01 — Explainable demand and service review

*As an analyst, I want to combine approved product context with source-owned demand and inventory evidence so that I can identify where human review may be useful.*

**Acceptance:** metrics are read-only, no editor exists for source facts; zero-demand coverage is undefined; missing inputs display gaps; margin requires compatible input; no automatic product or purchasing operation can result.

## Outcome indicators (no fictional impact claims)

- Percentage of accepted products with valid terminal assignments.
- Percentage of applicable required specifications populated.
- Lead time from change request to steward decision.
- Percentage of classified products with traceable source mapping.
- Count of consumers using the versioned product API, measured only in a real adoption environment.
- Analytical evidence coverage and exception categories, not invented savings.

`docs/backlog.csv` contains a small importable priority register for further backlog planning.
