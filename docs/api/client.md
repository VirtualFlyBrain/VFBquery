# `vfbquery_client`

The lightweight HTTP client. See [the client guide](../python-client.md) for the behaviour that is
not visible from a signature — DataFrame conventions, `df.attrs`, warnings and errors.

The package exports five names — `VfbClient`, `VfbError`, `default_base_url`, and the two base-URL
constants — and each is documented below. There is deliberately no `automodule` block for the package
itself: every one of those names is re-exported from `vfbquery_client.client`, and autodoc registers a
re-export under both its public and its canonical path, so documenting the module *and* its members
individually would register each of them twice and the `-W` docs build would fail on the collision.
The explicit directives are the single registration.

## `VfbClient`

```{eval-rst}
.. autoclass:: vfbquery_client.VfbClient
   :members:
   :undoc-members:
   :member-order: bysource
```

## Errors

```{eval-rst}
.. autoclass:: vfbquery_client.VfbError
   :show-inheritance:
```

## Base URL

```{eval-rst}
.. autofunction:: vfbquery_client.default_base_url

.. autodata:: vfbquery_client.PUBLIC_BASE_URL
   :no-value:

.. autodata:: vfbquery_client.DEFAULT_BASE_URL
   :no-value:
```

`PUBLIC_BASE_URL` is the deployed service; `DEFAULT_BASE_URL` is what a bare `VfbClient()` uses.
`VFB_API_URL` in the environment overrides both, which is how a workshop points a room at a private
deployment without editing a notebook.
