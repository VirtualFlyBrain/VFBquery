## What's Changed (v1.6.13)

### Increased Solr cache write timeout

Solr cache writes are performed asynchronously after the query returns to the user.
We now default to a **30 second write timeout** (configurable via `VFBQUERY_SOLR_WRITE_TIMEOUT`).

This helps prevent large or slow cache writes from spamming errors while still allowing the cache to work when Solr is responsive.
