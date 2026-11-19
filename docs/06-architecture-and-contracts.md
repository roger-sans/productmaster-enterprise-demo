# Architecture, contracts and engineering decisions

## Local executable architecture

- **Backend:** original Python / FastAPI, Pydantic models and typed validation.
- **Storage:** SQLite for a portable, persistent local demo; table boundaries for classification nodes, attribute metadata, products, source mappings, change requests, audit events and analytical observations.
- **Presentation:** independent HTML/CSS/JavaScript workspace; catalogue, taxonomy, attributes, governance, product strategy and intelligence views.
- **Fixtures:** deterministic fictional categories, 640 products and synthetic source observations. No network dependency.
- **Checks:** pytest and TestClient; GitHub Actions CI configuration included.

The underlying taxonomy model uses parent pointers, node IDs and stable technical codes, rather than a schema with three hard-coded family columns. The interface exposes three business-facing levels, but the storage relationship is a general tree.

## Representative resource contract

| API | Method | Meaning |
|---|---|---|
| `/api/v1/overview` | GET | Product, taxonomy and metadata KPIs |
| `/api/v1/products` | GET, POST | Paginated lookup / validated creation |
| `/api/v1/products/{sku}` | GET | Product context, technical values, provenance and audit |
| `/api/v1/taxonomy` | GET | Node IDs, parent links, paths, descendants and counts |
| `/api/v1/taxonomy/nodes` | POST | Safe demo-only taxonomy extension |
| `/api/v1/attributes` | GET | Metadata definitions and applicability |
| `/api/v1/attributes/definitions` | POST | Demo-only metadata creation |
| `/api/v1/requests` | GET, POST | Review queue / initiate governed change to classifications, attributes or commercial dimensions |
| `/api/v1/requests/{id}/decision` | POST | Approve or reject, with independent reviewer and version check |
| `/api/v1/audit` | GET | Attributable change history |
| `/api/v1/intelligence` | GET | Read-only, explainable synthetic metrics |
| `/api/v1/contracts` | GET | Source authority and consumer expectations |

Explore the generated Swagger UI at `/docs` after launching the project.

## Example request

```json
{
  "sku": "PRD000000001",
  "kind": "attributes",
  "actor": "sam.commercial",
  "department": "Commercial",
  "reason": "Update a specification after approved business review.",
  "payload": {
    "attributes": {"recyclable_packaging": true}
  }
}
```

Submitting this request produces **no immediate master change**. A second simulated user must approve it, the version must still match and the updated attributes must validate against applicable metadata.

## Decision records

| Decision | Rationale | Trade-off |
|---|---|---|
| ProductMaster before ProductIntelligence | Inconsistent identity and taxonomy would contaminate metrics | Delays some visual analytics until master rules work |
| Stable keys distinct from display labels | Labels are mutable and reused in separate branches | Needs hierarchy-aware UI and node references |
| Metadata-driven attributes | Different categories have different meaningful specs | Requires governance of definitions and applicability |
| Four-eyes approval | Prevent silent corrections and preserve responsibility | Adds review latency and change queue work |
| API-first consumers | Avoid consumer access to database internals | Versioning and compatibility become explicit backlog tasks |
| Read-only source-owned metrics | Prevent duplicate authority for sales, stock and finance | Consumers need observation contracts, cutoffs and lineage |
| Portable SQLite for demo | Reviewers can launch without services or secrets | Not a substitute for production persistence, authorization or operations |

## Nonfunctional acceptance

Identity uniqueness, referential integrity, stable versions, category-safe technical attributes, closed-form error responses, no cross-domain editable metrics and deterministic test data. Production nonfunctional gates would additionally require SSO/RBAC, secret management, encrypted transport, backups and restores, API rate limits, resilience and operational monitoring.
