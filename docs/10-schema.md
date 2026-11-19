# Logical data model

The portfolio implementation is intentionally **relational and metadata-driven**. Sales, demand, stock and finance observations have separate authority from product master fields.

```mermaid
erDiagram
  CLASSIFICATION_NODE ||--o{ CLASSIFICATION_NODE : parent_of
  CLASSIFICATION_NODE ||--o{ PRODUCT : classifies
  CLASSIFICATION_NODE ||--o{ CLASSIFICATION_ATTRIBUTE : governs
  ATTRIBUTE_DEFINITION ||--o{ CLASSIFICATION_ATTRIBUTE : applies
  PRODUCT ||--o{ SOURCE_MAPPING : reconciles
  PRODUCT ||--o{ CHANGE_REQUEST : receives
  PRODUCT ||--o{ AUDIT_EVENT : logs
  PRODUCT ||--o{ METRIC_OBSERVATION : observed_by
  CHANGE_REQUEST ||--o{ AUDIT_EVENT : documents
  CLASSIFICATION_NODE { string id PK string parent_id FK string code string label int level }
  PRODUCT { string sku PK string classification_node_id FK string description json attributes int version }
  ATTRIBUTE_DEFINITION { string code PK string data_type string unit json options }
  CLASSIFICATION_ATTRIBUTE { string node_id FK string attribute_code FK bool required }
  SOURCE_MAPPING { string sku FK string source_system string external_reference }
  CHANGE_REQUEST { int id PK string sku FK string kind string actor string status int expected_version }
  AUDIT_EVENT { int id PK string sku string event_type string actor int change_request_id }
  METRIC_OBSERVATION { int id PK string sku FK string metric_code float value string period string source_revision }
```

**Data ownership:** the product record owns governed identity, classification and technical values; external observations are never editable through the product field API. The most-specific node determines path ancestry and inherited attributes.

**Physical demo:** SQLite stores `attributes` as validated JSON strings; a protected enterprise deployment could use a relational/JSONB implementation and migration framework, keeping the public contract stable.
