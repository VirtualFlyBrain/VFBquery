"""Live tests for the vfb-scRNAseq Clustering, Sample and Dataset queries.

A Clustering lists its Clusters, Samples and Assays (its term info no longer
lists the Samples inline); a Sample lists the Clusterings that use it; an
scRNAseq Dataset lists its Clusterings, Samples and Assays.
"""

import unittest

import pandas as pd

from vfbquery import vfb_queries as vfb
from .scrnaseq_fixtures import clustering_with_samples, reused_sample, sample_source_with_clusters

CLUSTER = ["id", "name", "anatomy", "cluster_stage", "cell_count", "gene_count", "dataset", "tags"]
# clusters from several Clusterings also show the stages / tissues of their Samples
CLUSTER_ACROSS = ["id", "name", "anatomy", "cluster_stage", "sample_stages", "sample_tissues",
                  "cell_count", "gene_count", "dataset", "tags"]
CLUSTERING = ["id", "name", "clusters", "samples", "sample_stages", "sample_tissues", "dataset", "tags"]
SAMPLE = ["id", "name", "tissue", "stage", "sex", "dataset", "tags"]
ASSAY = ["id", "name", "method", "sample", "dataset"]

QUERIES = {
    "get_clusters_in_clustering": CLUSTER,
    "get_samples_in_clustering": SAMPLE,
    "get_assays_in_clustering": ASSAY,
}


class ClusteringQueriesTest(unittest.TestCase):

    # Aging Fly Cell Atlas head (Lu 2023): 72 clusters, 49 samples (some reused
    # from the Fly Cell Atlas), 49 assays.
    CLUSTERING_ID = "VFBseq_00001613"

    @classmethod
    def setUpClass(cls):
        cls.CLUSTERING_ID = clustering_with_samples(cls.CLUSTERING_ID)

    def test_formatted_results(self):
        for func, columns in QUERIES.items():
            with self.subTest(func=func):
                result = getattr(vfb, func)(self.CLUSTERING_ID, return_dataframe=False)
                self.assertEqual(list(result["headers"]), columns)
                self.assertTrue(result["rows"], f"{func} found nothing for {self.CLUSTERING_ID}")
                self.assertEqual(set(result["rows"][0]), set(columns))
                self.assertGreaterEqual(result["count"], len(result["rows"]))

    def test_limit_keeps_the_full_count(self):
        for func in QUERIES:
            with self.subTest(func=func):
                full = getattr(vfb, func)(self.CLUSTERING_ID, return_dataframe=False)
                preview = getattr(vfb, func)(self.CLUSTERING_ID, return_dataframe=False, limit=2)
                self.assertEqual(len(preview["rows"]), min(2, full["count"]))
                self.assertEqual(preview["count"], full["count"])

    def test_dataframe(self):
        for func, columns in QUERIES.items():
            with self.subTest(func=func):
                df = getattr(vfb, func)(self.CLUSTERING_ID, return_dataframe=True)
                self.assertIsInstance(df, pd.DataFrame)
                self.assertFalse(df.empty)
                self.assertTrue(set(columns) <= set(df.columns))

    def test_rows_link_their_terms(self):
        clusters = vfb.get_clusters_in_clustering(self.CLUSTERING_ID, return_dataframe=False)
        self.assertTrue(all(r["anatomy"].startswith("[") for r in clusters["rows"]))
        samples = vfb.get_samples_in_clustering(self.CLUSTERING_ID, return_dataframe=False)
        self.assertTrue(all(r["dataset"].startswith("[") for r in samples["rows"]))

    def test_unknown_clustering_is_empty(self):
        result = vfb.get_samples_in_clustering("VFBseq_does_not_exist", return_dataframe=False)
        self.assertEqual(result["rows"], [])
        self.assertEqual(result["count"], 0)

    def test_schemas(self):
        for to_schema, func in [
                (vfb.ClustersInClustering_to_schema, "get_clusters_in_clustering"),
                (vfb.SamplesInClustering_to_schema, "get_samples_in_clustering"),
                (vfb.AssaysInClustering_to_schema, "get_assays_in_clustering")]:
            with self.subTest(func=func):
                q = to_schema("X", {"short_form": self.CLUSTERING_ID})
                self.assertEqual(q.function, func)
                self.assertEqual(q.takes["short_form"], {"$and": ["Individual", "Clustering"]})
                self.assertEqual(q.preview, 5)


class SampleAndDatasetQueriesTest(unittest.TestCase):

    # A Fly Cell Atlas head sample (Li 2022) that the Aging Fly Cell Atlas head
    # clustering (Lu 2023) reuses, so it has Clusterings in two Datasets.
    SAMPLE_ID = "VFBseq_00000730"
    # Lu 2023: its own Samples plus the reused FCA ones.
    DATASET_ID = "VFBseq_00001468"

    @classmethod
    def setUpClass(cls):
        cls.SAMPLE_ID, cls.DATASET_ID = reused_sample(cls.SAMPLE_ID, cls.DATASET_ID)

    def _check(self, func, short_form, columns):
        result = getattr(vfb, func)(short_form, return_dataframe=False)
        self.assertEqual(list(result["headers"]), columns)
        self.assertTrue(result["rows"], f"{func} found nothing for {short_form}")
        self.assertEqual(result["count"], len(result["rows"]))
        return result

    def test_clusterings_with_sample_cross_datasets(self):
        """The reusing Dataset's Clustering is listed, though the Sample was
        curated under another Dataset."""
        result = self._check("get_clusterings_with_sample", self.SAMPLE_ID, CLUSTERING)
        self.assertTrue(any(f"({self.DATASET_ID})" in r["dataset"] for r in result["rows"]))
        self.assertTrue(all(r["clusters"] > 0 for r in result["rows"]))

    def test_dataset_queries(self):
        self._check("get_clusterings_in_dataset", self.DATASET_ID, CLUSTERING)
        samples = self._check("get_samples_in_dataset", self.DATASET_ID, SAMPLE)
        assays = self._check("get_assays_in_dataset", self.DATASET_ID, ASSAY)
        # reused Samples come with their own Dataset
        self.assertGreaterEqual(len({r["dataset"] for r in samples["rows"]}), 2)
        self.assertGreaterEqual(len(assays["rows"]), len(samples["rows"]))

    def test_schemas(self):
        for to_schema, func, takes in [
                (vfb.ClusteringsWithSample_to_schema, "get_clusterings_with_sample", ["Individual", "Sample"]),
                (vfb.ClusteringsInDataset_to_schema, "get_clusterings_in_dataset", ["DataSet", "hasScRNAseq"]),
                (vfb.SamplesInDataset_to_schema, "get_samples_in_dataset", ["DataSet", "hasScRNAseq"]),
                (vfb.AssaysInDataset_to_schema, "get_assays_in_dataset", ["DataSet", "hasScRNAseq"])]:
            with self.subTest(func=func):
                q = to_schema("X", {"short_form": "VFBseq_1"})
                self.assertEqual(q.function, func)
                self.assertEqual(q.takes["short_form"], {"$and": takes})


class SampleSourceQueriesTest(unittest.TestCase):

    # Hörmann 2020's split-GAL4 combination (T4/T5 driver): 10 Samples, 40 Clusters.
    ENTITY_ID = "FBco0000215"

    @classmethod
    def setUpClass(cls):
        cls.ENTITY_ID = sample_source_with_clusters(cls.ENTITY_ID)

    def test_samples_from(self):
        result = vfb.get_scrnaseq_samples_from(self.ENTITY_ID, return_dataframe=False)
        self.assertEqual(list(result["headers"]), SAMPLE)
        self.assertTrue(result["rows"])
        self.assertEqual(result["count"], len(result["rows"]))

    def test_clusters_from(self):
        result = vfb.get_scrnaseq_clusters_from(self.ENTITY_ID, return_dataframe=False)
        self.assertEqual(list(result["headers"]), CLUSTER_ACROSS)
        self.assertTrue(result["rows"])
        self.assertTrue(all(r["dataset"].startswith("[") for r in result["rows"]))

    def test_unrelated_entity_is_empty(self):
        # a gene: no Sample links it
        result = vfb.get_scrnaseq_samples_from("FBgn0000490", return_dataframe=False)
        self.assertEqual((result["rows"], result["count"]), ([], 0))

    def test_schemas(self):
        for to_schema, func in [
                (vfb.ScRNAseqSamplesFrom_to_schema, "get_scrnaseq_samples_from"),
                (vfb.ScRNAseqClustersFrom_to_schema, "get_scrnaseq_clusters_from")]:
            with self.subTest(func=func):
                q = to_schema("X", {"short_form": self.ENTITY_ID})
                self.assertEqual(q.function, func)
                self.assertEqual(q.takes["short_form"], {"$and": ["hasScRNAseqSample"]})


if __name__ == "__main__":
    unittest.main()
