## What's Changed

- Rewrite `resolve_entity` and `resolve_combination` HA API requests that receive FlyBase IDs to use the preferred VFB term name before querying Chado.
- Return `NOT_FOUND` instead of passing raw IDs to Chado when no preferred name/label can be derived from VFB term info.
- Add focused HA API validation tests covering query normalization, ID rewriting, and the no-fallback path.
