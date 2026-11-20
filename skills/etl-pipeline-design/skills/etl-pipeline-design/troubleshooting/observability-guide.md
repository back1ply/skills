# Troubleshooting & Observability Guide

## Observability Metrics

### Freshness

| Metric              | Description                              | Target             |
|---------------------|------------------------------------------|--------------------|
| Last update lag     | Time since most recent record            | Based on SLA       |
| Source-to-target lag| Delay between source and destination     | Minimize           |
| Refresh rate        | How often data updates                   | Match requirements |

### Volume

| Metric       | Description        | Action              |
|--------------|--------------------|---------------------|
| Row count    | Total records      | Compare to expected |
| Daily delta  | New rows per day   | Detect anomalies    |
| Size (GB/TB) | Storage footprint  | Monitor growth      |

### Quality

| Metric       | Description        | Check                    |
|--------------|--------------------|--------------------------|
| Uniqueness   | Duplicate records? | Count distinct vs total  |
| Completeness | NULL values        | NULL rate per column     |
| Validity     | In expected range  | Value distribution       |

---

## Observability Methods

### 1. Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_batch(batch_id):
    logger.info(f"Processing batch {batch_id}")
    try:
        # Processing logic
        logger.info(f"Batch {batch_id}: {row_count} rows processed")
    except Exception as e:
        logger.error(f"Batch {batch_id} failed: {e}")
        raise
```

### 2. Lineage

Track data origin at column level:

```text
raw.orders.order_id → stg.orders.id → fct.sales.order_id
                                   ↓
                           dim.users (JOIN)
```

**Tools**: Unity Catalog, dbt, Monte Carlo, DataHub

### 3. Anomaly Detection

```sql
-- Statistical anomaly detection
WITH daily_stats AS (
  SELECT 
    date,
    COUNT(*) as row_count,
    AVG(COUNT(*)) OVER (ORDER BY date ROWS 30 PRECEDING) as avg_30d,
    STDDEV(COUNT(*)) OVER (ORDER BY date ROWS 30 PRECEDING) as std_30d
  FROM orders
  GROUP BY date
)
SELECT date, row_count
FROM daily_stats
WHERE ABS(row_count - avg_30d) > 2 * std_30d  -- 2 sigma outliers
```

### 4. Assertions

```sql
-- dbt test example
-- tests/assert_positive_prices.sql
SELECT *
FROM {{ ref('fct_orders') }}
WHERE price <= 0

-- Expected: 0 rows (failure = data quality issue)
```

**Common Assertions**:

- Unique keys: No duplicates on ID columns
- Not null: Required fields are populated
- Referential: Foreign keys exist in parent tables
- Range: Values within expected bounds

### 5. Data Diffs

```bash
# Compare before/after a code change
datafold diff \
  --before prod.orders \
  --after staging.orders_v2 \
  --primary-key order_id
```

---

## Error Handling Patterns

### Retry with Backoff

```python
import time
from functools import wraps

def retry_with_backoff(retries=3, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == retries - 1:
                        raise
                    wait = backoff_factor ** attempt
                    time.sleep(wait)
        return wrapper
    return decorator

@retry_with_backoff(retries=3)
def call_api():
    # API call that might fail
    pass
```

### Graceful Degradation

```python
def get_data():
    try:
        return fetch_from_api()
    except APIError:
        logger.warning("API unavailable, using cached data")
        return fetch_from_cache()
```

### Error Isolation

```text
DAG Structure for Isolation:
├── Ingestion DAG (isolated)
│   └── If fails → Alert, don't break downstream
├── Transform DAG (isolated)
│   └── If fails → Use yesterday's data
└── Report DAG (isolated)
    └── If fails → Only reports affected
```

---

## Incident Response

### Key Metrics

| Metric       | Formula                | Target      |
|--------------|------------------------|-------------|
| **N**        | Number of incidents    | Minimize    |
| **TTD**      | Time to detection      | < 15 min    |
| **TTR**      | Time to resolution     | < 1 hour    |
| **Downtime** | N × (TTD + TTR)        | Minimize    |

### Alerting Best Practices

| Do                            | Don't                       |
|-------------------------------|-----------------------------|
| Alert on actionable issues    | Alert on every warning      |
| Include context in alerts     | Send cryptic error codes    |
| Route to right team           | Broadcast to everyone       |
| Set severity levels           | Treat all alerts equally    |

### Postmortem Template

```markdown
## Incident: [Title]
**Date**: [Date]
**Duration**: [TTD + TTR]
**Severity**: [P1-P4]

### What Happened
[Description of the incident]

### Root Cause
[Why did it happen]

### Impact
[Who/what was affected]

### Resolution
[How was it fixed]

### Action Items
- [ ] [Preventive measure 1]
- [ ] [Preventive measure 2]
```

---

## Recovery Patterns

### Backfill

```bash
# Airflow backfill command
airflow dags backfill \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  daily_etl
```

### Time Travel (Delta Lake)

```sql
-- Restore to previous version
RESTORE TABLE orders TO VERSION AS OF 5

-- Query historical state
SELECT * FROM orders VERSION AS OF '2024-01-01'
```

### Staging Recovery

```text
Bronze (Raw) → Silver (Clean) → Gold (Final)
     ↑               ↑              ↑
   Preserved     Time Travel     Rebuild from Silver
```

---

## Data Contracts & SLAs

### Data Contract Example

```yaml
# contract.yaml
dataset: orders
owner: data-team@example.com
sla:
  freshness: 1 hour
  completeness: 99.9%
schema:
  - name: order_id
    type: string
    nullable: false
    unique: true
  - name: amount
    type: decimal
    nullable: false
    constraints:
      - "amount > 0"
```

### SLA Monitoring

```sql
-- Check freshness SLA
SELECT 
  MAX(updated_at) as last_update,
  TIMESTAMPDIFF(HOUR, MAX(updated_at), NOW()) as hours_stale,
  CASE 
    WHEN TIMESTAMPDIFF(HOUR, MAX(updated_at), NOW()) > 1 
    THEN 'SLA BREACH' 
    ELSE 'OK' 
  END as status
FROM orders
```
