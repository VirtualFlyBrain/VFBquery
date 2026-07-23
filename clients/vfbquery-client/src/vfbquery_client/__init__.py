"""vfbquery-client — lightweight HTTP client for the Virtual Fly Brain query API.

Talks to the cached VFB query service (v3-cached) over plain HTTP and returns
pandas DataFrames, so notebooks and scripts get the common `vfb_connect`-style
queries with a two-second install and no `navis` / `setuptools<58` friction.

    from vfbquery_client import VfbClient
    vfb = VfbClient()
    vfb.get_instances('adult antennal lobe projection neuron DA1 lPN')

See docs/vfbconnect-http-api-plan.md in the VFBquery repo for the design and the
endpoints this depends on (some — /search, /xref — are part of the same plan and
land server-side alongside this client).
"""
from .client import VfbClient, DEFAULT_BASE_URL

__all__ = ["VfbClient", "DEFAULT_BASE_URL"]
__version__ = "0.1.0.dev0"
