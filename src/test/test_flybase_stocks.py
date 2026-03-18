"""Tests for flybase_stocks module — entity resolution and stock discovery."""
import pytest

from vfbquery.flybase_stocks import resolve_entity, find_stocks

# Known stable test entities
KNOWN_GENE_SYMBOL = "dpp"
KNOWN_GENE_ID = "FBgn0000490"
KNOWN_GENE_ID_2 = "FBgn0003996"  # white
KNOWN_SYNONYM = "CG9885"
KNOWN_SYNONYM_RESOLVES_TO = "dpp"
NONEXISTENT_ENTITY = "xyzzy_nonexistent_gene_99999"


# ---------------------------------------------------------------------------
# resolve_entity tests
# ---------------------------------------------------------------------------


class TestResolveEntityByID:
    @pytest.mark.integration
    def test_known_gene_id(self):
        result = resolve_entity(KNOWN_GENE_ID)
        assert result["match_type"] == "EXACT"
        assert len(result["results"]) > 0
        assert result["results"][0]["uniquename"] == KNOWN_GENE_ID
        assert result["results"][0]["type"] == "gene"

    @pytest.mark.integration
    def test_known_combo_id(self):
        result = resolve_entity("FBco0001000")
        assert result["match_type"] == "EXACT"
        assert result["results"][0]["uniquename"] == "FBco0001000"
        assert result["results"][0]["type"] == "split system combination"

    @pytest.mark.integration
    def test_nonexistent_id(self):
        result = resolve_entity("FBgn9999999999")
        assert result["match_type"] == "NOT_FOUND"
        assert result["results"] == []


class TestResolveEntityExactMatch:
    @pytest.mark.integration
    def test_exact_gene_name(self):
        result = resolve_entity(KNOWN_GENE_SYMBOL)
        assert result["match_type"] == "EXACT"
        assert any(r["uniquename"] == KNOWN_GENE_ID for r in result["results"])
        assert any(r["type"] == "gene" for r in result["results"])


class TestResolveEntitySynonym:
    @pytest.mark.integration
    def test_synonym_resolves(self):
        result = resolve_entity(KNOWN_SYNONYM)
        assert result["match_type"] == "SYNONYM"
        assert any(
            KNOWN_SYNONYM_RESOLVES_TO in r["name"] for r in result["results"]
        )

    @pytest.mark.integration
    def test_synonym_includes_matched_synonym(self):
        result = resolve_entity(KNOWN_SYNONYM)
        assert any(
            r["matched_synonym"] == KNOWN_SYNONYM for r in result["results"]
        )

    @pytest.mark.integration
    def test_combo_synonym_resolves(self):
        result = resolve_entity("MB002B")
        assert result["match_type"] == "SYNONYM"
        assert any("FBco" in r["uniquename"] for r in result["results"])


class TestResolveEntityBroadMatch:
    @pytest.mark.integration
    def test_broad_match_partial_name(self):
        result = resolve_entity("Scer\\GAL4")
        assert result["match_type"] in ("EXACT", "SYNONYM", "BROAD")
        assert len(result["results"]) > 0


class TestResolveEntityNotFound:
    @pytest.mark.integration
    def test_nonexistent_name(self):
        result = resolve_entity(NONEXISTENT_ENTITY)
        assert result["match_type"] == "NOT_FOUND"


# ---------------------------------------------------------------------------
# find_stocks tests
# ---------------------------------------------------------------------------


class TestFindStocksGene:
    @pytest.mark.integration
    def test_dpp_returns_stocks(self):
        stocks = find_stocks(KNOWN_GENE_ID)
        assert len(stocks) > 0
        assert all("stock_id" in s for s in stocks)

    @pytest.mark.integration
    def test_dpp_stocks_have_fbst(self):
        stocks = find_stocks(KNOWN_GENE_ID)
        assert any(s["stock_id"].startswith("FBst") for s in stocks)

    @pytest.mark.integration
    def test_white_returns_stocks(self):
        stocks = find_stocks(KNOWN_GENE_ID_2)
        assert len(stocks) > 0


class TestFindStocksCollectionFilter:
    @pytest.mark.integration
    def test_bloomington_filter(self):
        stocks = find_stocks(KNOWN_GENE_ID, collection_filter="Bloomington")
        assert len(stocks) > 0
        for s in stocks:
            if s.get("collection"):
                assert "Bloomington" in s["collection"]

    @pytest.mark.integration
    def test_filter_reduces_count(self):
        all_stocks = find_stocks(KNOWN_GENE_ID)
        filtered = find_stocks(KNOWN_GENE_ID, collection_filter="Bloomington")
        assert len(filtered) <= len(all_stocks)


class TestFindStocksAllele:
    @pytest.mark.integration
    def test_known_allele(self):
        # dpp[hr4] = FBal0000469
        stocks = find_stocks("FBal0000469")
        assert isinstance(stocks, list)


class TestFindStocksInsertion:
    @pytest.mark.integration
    def test_known_insertion(self):
        stocks = find_stocks("FBti0016417")
        assert len(stocks) > 0


class TestFindStocksStockDetail:
    @pytest.mark.integration
    def test_stock_lookup(self):
        stocks = find_stocks("FBst0007144")
        assert len(stocks) > 0
        assert any("7144" in str(s.get("stock_number", "")) for s in stocks)

    @pytest.mark.integration
    def test_stock_includes_collection(self):
        stocks = find_stocks("FBst0007144")
        assert any("Bloomington" in str(s.get("collection", "")) for s in stocks)


class TestFindStocksCombination:
    @pytest.mark.integration
    def test_known_combination(self):
        stocks = find_stocks("FBco0001000")
        assert len(stocks) > 0
        assert all("stock_id" in s for s in stocks)

    @pytest.mark.integration
    def test_combination_has_component(self):
        stocks = find_stocks("FBco0001000")
        assert any("component" in s for s in stocks)

    @pytest.mark.integration
    def test_nonexistent_combination(self):
        stocks = find_stocks("FBco9999999")
        assert stocks == []


class TestFindStocksEdgeCases:
    @pytest.mark.integration
    def test_nonexistent_gene_id(self):
        stocks = find_stocks("FBgn9999999999")
        assert stocks == []

    @pytest.mark.integration
    def test_nonexistent_stock_id(self):
        stocks = find_stocks("FBst9999999999")
        assert stocks == []

    def test_bad_id_prefix(self):
        with pytest.raises(ValueError, match="Unrecognised ID prefix"):
            find_stocks("INVALID0001")
