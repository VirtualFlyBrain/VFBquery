# Parked GitHub Actions workflows

The two YAML files in this directory are **not running**. They are complete, valid workflow
definitions sitting one `git mv` away from being active:

```bash
git mv docs/ci/search-gates.yml .github/workflows/search-gates.yml
git mv docs/ci/docs.yml         .github/workflows/docs.yml
```

They are parked rather than committed in place because the credential this branch was pushed with has
no `workflow` scope, and GitHub rejects a push touching `.github/workflows/` **wholesale** — not just
that file. Parking them keeps the definitions under review with the code they gate, instead of
existing only as a paragraph in a pull request description saying what CI ought to do.

Move them from a checkout with a workflow-scoped credential. Nothing else needs to change: neither
file refers to this directory, and both use paths relative to the repository root.

## `search-gates.yml`

The five gates from `scripts/check_gates.sh`, split into three jobs:

- **client** — the client's request-shaping tests on 3.8 (ubuntu-22.04) and 3.11 (ubuntu-latest),
  because the client claims `requires-python = ">=3.8"` and a claim nothing tests is a wish.
- **server** — everything under `tests/`, offline.
- **live** — schedule-only (`0 3 * * 1`), because it needs the live Solr index and a server started
  from the checkout.

## `docs.yml`

Builds the Sphinx site with `-W`, so a broken cross-reference fails the pull request rather than
appearing as a red badge on Read the Docs after the merge. A weekly `linkcheck` job runs separately;
see the comments at the top of the file for why it is not part of the gate.
