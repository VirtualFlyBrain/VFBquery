## What's Changed (v1.6.11)

### Fix: security middleware & aria deprecation warning

- `security_middleware` now blocks all non-API paths with an empty 404 (no stack traces).
- The scanner probe counter is initialized at startup so aiohttp no longer emits the "Changing state of started or joined application is deprecated" warning.

### Release status
- v1.6.10 exists but does not include the final aiohttp deprecation fix.
- This release (v1.6.11) includes the final patch and is the current main branch tip.
