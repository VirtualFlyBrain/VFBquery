"""Live fixtures for the scRNAseq (transcriptomics) tests.

The scRNAseq data in VFB is moving from the old FlyBase/SCEA loads (Datasets,
Clusters, Samples and Assays with FlyBase ``FBlc...`` ids) to the
vfb-scRNAseq repo's loads (``VFBseq_...`` ids). The two never coexist for one
study, so a hard-coded ``FBlc`` fixture disappears when its study is switched.

Each helper keeps the preferred (known-good) id while the database still has
data for it, and otherwise picks the first term that has the data the test
needs, so the tests run unchanged before, during and after the switch.
"""

from vfbquery.vfb_queries import vc, get_dict_cursor

#: Id prefixes of scRNAseq Datasets / Clusters: old FlyBase loads, new VFBseq loads.
SCRNASEQ_ID_PREFIXES = ("FBlc", "VFBseq_")


def _first(query):
    rows = get_dict_cursor()(vc.nc.commit_list([query]))
    return rows[0]["id"] if rows else None


def _pick(preferred, has_data, any_with_data):
    """``preferred`` if ``has_data`` (a query on ``$id``) finds it, else the
    first id ``any_with_data`` returns, else ``preferred`` (so the test fails
    on its own empty-result assertion rather than here)."""
    found = _first(has_data.replace("$id", "'%s'" % preferred))
    return found or _first(any_with_data) or preferred


def cluster_with_expression(preferred):
    """A Cluster with expressed genes and a cell type."""
    match = ("MATCH (c:Individual:Cluster)-[:expresses]->(:Gene:Class) "
             "MATCH (c)-[:composed_primarily_of]->(:Anatomy) ")
    return _pick(
        preferred,
        match + "WHERE c.short_form = $id RETURN c.short_form AS id LIMIT 1",
        match + "RETURN DISTINCT c.short_form AS id ORDER BY id LIMIT 1")


def dataset_with_clusters(preferred):
    """An scRNAseq DataSet with Clusters that have a cell type."""
    match = ("MATCH (:Anatomy)<-[:composed_primarily_of]-(:Individual:Cluster)"
             "-[:has_source]->(ds:scRNAseq_DataSet) ")
    return _pick(
        preferred,
        match + "WHERE ds.short_form = $id RETURN ds.short_form AS id LIMIT 1",
        match + "RETURN DISTINCT ds.short_form AS id ORDER BY id LIMIT 1")


def gene_with_clusters(preferred):
    """A Gene expressed in Clusters that have a cell type."""
    match = ("MATCH (:Anatomy)<-[:composed_primarily_of]-(:Individual:Cluster)"
             "-[:expresses]->(g:Gene:Class) ")
    return _pick(
        preferred,
        match + "WHERE g.short_form = $id RETURN g.short_form AS id LIMIT 1",
        match + "RETURN g.short_form AS id LIMIT 1")


def anatomy_with_clusters(preferred):
    """A cell type that scRNAseq Clusters are composed primarily of."""
    match = ("MATCH (a:Class:Anatomy)<-[:composed_primarily_of]-(:Cluster)"
             "-[:has_source]->(:scRNAseq_DataSet) ")
    return _pick(
        preferred,
        match + "WHERE a.short_form = $id RETURN a.short_form AS id LIMIT 1",
        match + "RETURN a.short_form AS id LIMIT 1")
