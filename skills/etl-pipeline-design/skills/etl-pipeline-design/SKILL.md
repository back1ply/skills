---
name: etl-pipeline-design
description: This skill should be used when the user asks to "design an ETL pipeline", "build data ingestion", "set up data orchestration", "troubleshoot pipeline issues", "optimize data workflows", or mentions ELT, medallion architecture, batch vs streaming, or data transformation patterns.
---

# ETL Pipeline Design Skill

> **Source**: Distilled from *Understanding ETL (Updated Edition)* by Matt Palmer, O'Reilly Media, August 2025. ISBN: 979-8-341-66508-8

Applicable when designing data ingestion from APIs, databases, or streaming sources; building transformation pipelines (batch or streaming); selecting orchestration tools or patterns; troubleshooting pipeline failures or data quality issues; or optimizing pipelines for efficiency and scale.

---

## Core Concepts

### ETL vs ELT

- **ETL**: Transform data before loading (legacy, when storage was expensive)
- **ELT**: Load all data first, transform downstream (modern approach — "storage is cheap")
- Modern pipelines are typically ELT, but the term "ETL" persists

### Medallion Architecture

Stage data in three quality layers:

| Layer | Purpose | Example |
| ------- | --------- | --------- |
| **Bronze** | Raw, unfiltered data directly from sources | API responses, raw logs |
| **Silver** | Cleaned, filtered, enriched | Removed duplicates, renamed columns |
| **Gold** | Stakeholder-ready, often aggregated | Reporting tables, ML features |

---

## 1. Data Ingestion

### Source Evaluation Checklist

For every data source, answer:

| Question | Why It Matters |
| ---------- | ---------------- |
| Who will use this data? | Aligns incentives, prioritizes work |
| How will it be used? | Guides downstream decisions |
| Is it bounded or unbounded? | Determines batch vs. streaming |
| What's the minimum update frequency? | Sets hard limits on freshness |
| What's the expected volume? | Informs storage/compute choices |
| What's the format? (JSON, CSV, API, DB) | Dictates processing requirements |
| What's the quality? | Determines transformation needs |

### Destination Considerations

- **OLAP** (BigQuery, Redshift, Snowflake, Databricks SQL): For analytics, column-oriented
- **OLTP** (Postgres, MySQL): For transactional apps, row-oriented
- **Lakehouse** (Delta Lake, Iceberg, Hudi): Combines lake + warehouse benefits

### Batch vs. Streaming Decision

```text
Is the data bounded (finite)?
├── YES → Batch processing
└── NO (continuous/unbounded) →
    ├── Latency requirement < 1 second? → True streaming (Flink, Kafka Streams)
    └── Latency 100ms-minutes acceptable? → Micro-batch (Spark Structured Streaming)
```

**Streaming Methods**:

- **Fixed windows**: Data batched in fixed time intervals
- **Sliding windows**: Overlapping time intervals
- **Sessions**: Dynamic windows based on activity gaps

### Choosing Ingestion Solutions

| Type | Examples | Pros | Cons |
| ------ | ---------- | ------ | ------ |
| **Legacy declarative** | Talend, Pentaho | Robust connectors | Outdated, not MDS-aligned |
| **Modern declarative** | Fivetran, Airbyte, Stitch | Low maintenance, connectors | Vendor lock-in, cost |
| **Native/Platform** | Lakeflow Connect, Glue | Integrated, managed | Platform-specific |
| **Imperative** | Custom scripts, Singer taps | Full control | High build/maintain cost |
| **Hybrid** | Mix of above | Flexibility | Complexity |

**Recommendation**: Use declarative for common sources, imperative for edge cases.

---

## 2. Data Transformation

### Transformation Patterns

| Pattern | Description | Example |
| --------- | ------------- | --------- |
| **Enrichment** | Add data from other sources | Join order codes → readable names |
| **Joining** | Combine datasets on common keys | Sales + Users → add country |
| **Filtering** | Select only needed records | `WHERE date >= '2025-01-01'` |
| **Structuring** | Convert formats | JSON → tabular Parquet |
| **Conversion** | Change data types | String → datetime |
| **Aggregation** | Summarize data | Daily totals from hourly data |
| **Anonymization** | Mask PII | Hash emails |
| **Splitting** | Break columns apart | email → prefix + domain |
| **Deduplication** | Remove duplicates | Keep earliest by UUID |

### Update Patterns

| Pattern | When to Use | SQL Concept |
| --------- | ------------- | ------------- |
| **Overwrite** | Small datasets, simple refreshes | `TRUNCATE` + `INSERT` |
| **Insert** | Append-only data (logs, transactions) | `INSERT INTO` |
| **Upsert** | CDC, deduplication, SCD | `MERGE` |
| **Delete** | Soft (status='deleted') or hard (remove row) | `UPDATE` or `DELETE` |

### UPSERT Example (Databricks)

```sql
MERGE INTO people10m
USING people10mupdates
ON people10m.id = people10mupdates.id
WHEN MATCHED THEN UPDATE SET
  firstName = people10mupdates.firstName,
  lastName = people10mupdates.lastName
WHEN NOT MATCHED THEN INSERT (id, firstName, lastName)
VALUES (people10mupdates.id, people10mupdates.firstName, people10mupdates.lastName)
```

### Best Practices

- **Staging**: Always stage intermediate data for recoverability
- **Idempotency**: Running a pipeline twice should produce the same result
- **Incrementality**: Process only new/changed data when possible

---

## 3. Data Orchestration

### What Orchestrators Do

- Manage dependencies between tasks (DAGs)
- Schedule and trigger pipelines
- Handle retries, errors, and alerts
- Provide monitoring and lineage

### Orchestrator Selection Criteria

| Criterion | Questions to Ask |
| ----------- | ------------------ |
| **Scalability** | Can it handle 10x DAGs/tasks? |
| **Reusability** | Can I create reusable components? |
| **Connections** | Native integrations with my stack? |
| **Support** | Active community or paid support? |
| **Observability** | Can I see failures, lineage, logs? |

### Orchestrator Options

| Tool | Type | Best For |
| ------ | ------ | ---------- |
| **Airflow** | Open source | Mature, widely adopted, many connectors |
| **Dagster** | Open source | Modern, asset-based, good DX |
| **Prefect** | Open source | Python-native, flexible |
| **Lakeflow Jobs** | Platform | Databricks-native, integrated |
| **dbt** | SQL orchestrator | Warehouse transformations |

### Design Patterns

| Pattern | Description |
| --------- | ------------- |
| **Backfills** | Build pipelines that can recreate historical data |
| **Event-driven** | Trigger on data arrival, not just schedules |
| **Conditional logic** | Branch based on conditions (if/else) |
| **Concurrency** | Fan out parallel tasks for performance |
| **Parameterized** | Accept variables for flexibility |
| **Decomposition** | Break into micro-DAGs for isolation |

---

## 4. Troubleshooting & Observability

### Key Metrics

| Metric | What It Measures |
| -------- | ------------------ |
| **Freshness** | Time since last update |
| **Volume** | Row counts, data sizes |
| **Quality** | Uniqueness, completeness, validity |

### Observability Methods

| Method | Purpose |
| -------- | --------- |
| **Logging** | Capture execution details |
| **Lineage** | Track data flow (column-level ideal) |
| **Anomaly detection** | Catch unexpected data patterns |
| **Data diffs** | See what code changes affect data |
| **Assertions** | Validate constraints (`price > 0`) |

### Error Handling

| Technique | Description |
| ----------- | ------------- |
| **Retry logic** | Automatic retries with backoff |
| **Conditional handling** | Different paths for different errors |
| **Pipeline decomposition** | Isolate failures |
| **Graceful degradation** | Partial functionality on failure |
| **Alerting** | Notify team (avoid alert fatigue) |

### Incident Metrics

- **N**: Number of incidents
- **TTD**: Time to detection
- **TTR**: Time to resolution
- **Downtime**: N × (TTD + TTR)

---

## 5. Efficiency & Scalability

### Resource Allocation

| Concept | Description |
| --------- | ------------- |
| **Spot instances** | Cheaper but interruptible |
| **On-demand** | Reliable but costly |
| **Pooling** | Pre-warm clusters for faster starts |
| **Autoscaling** | Adjust resources to workload |
| **Serverless** | Pay per use (BigQuery, Databricks SQL) |

### Optimization Techniques

| Technique | Benefit |
| ----------- | --------- |
| **Incremental processing** | Only process new/changed data |
| **Columnar storage** | Faster analytics (Parquet, Delta) |
| **Partitioning** | Reduce data scanned |
| **Materialization** | Tables vs. views trade-offs |

### Scaling Formula

```text
Horizontal scaling = More machines/nodes
Vertical scaling = Bigger machines/nodes
```

### Developer Experience (DevEx)

Efficiency also covers the team building the pipelines. The book uses the three "core dimensions" of DevEx from Noda et al. (2022):

| Dimension | What it means | Questions to ask |
| --------- | ------------- | ---------------- |
| **Feedback loops** | Speed and quality of responses to your actions | Can you develop a DAG locally? Do you see a change's effect on the system and the data right away? Aim for a "frontend DevEx": edit in one window, see results live, deploy in a few commands. |
| **Cognitive load** | Mental effort a task requires | How hard is it to set up a local environment, create a new dbt model, or understand existing tables and metadata? Are you switching between seven tools? Simplify config and builds. |
| **Flow state** | Focused, immersed, enjoyable work | Follows from meaningful work, short feedback loops and low cognitive load. Tune systems for fast, low-stress development. |

---

## Decision Framework

When designing a pipeline:

1. **Understand the source** → Use source evaluation checklist
2. **Determine frequency** → Batch vs. streaming based on bounds + requirements
3. **Choose ingestion** → Declarative for common, imperative for custom
4. **Design transformations** → Apply appropriate patterns
5. **Plan updates** → Overwrite, insert, or upsert based on use case
6. **Orchestrate** → Select tool, apply design patterns
7. **Observe** → Implement logging, lineage, assertions
8. **Optimize** → Incrementality, partitioning, right-sizing resources

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad |
| -------------- | -------------- |
| Mixing orchestration with transformation | Orchestrator should trigger, not execute |
| No staging layer | Hard to recover from failures |
| Non-idempotent pipelines | Reruns cause duplicates or errors |
| Ignoring lineage | Impossible to debug data issues |
| Alert fatigue | Too many alerts = ignored alerts |
| GUI-only tooling | No version control, hard to collaborate |

---

## Reference Files

For detailed patterns and extended guidance, consult:

- **`patterns/transformation-patterns.md`** — Detailed transformation pattern catalog with examples
- **`patterns/orchestration-patterns.md`** — Advanced orchestration design patterns and DAG strategies
- **`troubleshooting/observability-guide.md`** — Comprehensive observability setup, monitoring, and incident response
- **`checklists/evaluation-checklists.md`** — Pipeline evaluation checklists for design reviews and production readiness
