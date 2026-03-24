## What's Changed

- Relax HA API FlyBase ID rewriting so `resolve_entity` and `resolve_combination` fall back to the canonical FlyBase ID when VFB term info cannot provide a preferred symbol or label.
- Keep the preferred VFB term name rewrite path when term info is available.
- Update HA API validation tests to cover the canonical-ID fallback behavior.
