"""Tests for flybase_stocks module — entity resolution and stock discovery."""
import pytest

from vfbquery.flybase_stocks import resolve_entity, find_stocks
from vfbquery.vfb_queries import (
    _flybase_report_url,
    _md_link,
    _stock_number_url,
    get_flybase_stocks,
)


def assert_single_selection_id(result):
    """A result table must declare exactly one `selection_id` identity column,
    hidden at order -1. Without it the website consumes the first visible data
    column as the row identity and drops it from the table (regression: the
    Stock ID / FBrf columns went missing on the site)."""
    headers = result["headers"]
    sel = [c for c, m in headers.items() if m.get("type") == "selection_id"]
    assert len(sel) == 1, f"expected exactly one selection_id column, got {sel}"
    assert headers[sel[0]]["order"] == -1, "selection_id column must be hidden (order -1)"

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
        # bcd[25] = FBal0034227, held in stocks (dpp[hr4]/FBal0000469 has none,
        # so the old fixture made this test pass without checking anything).
        stocks = find_stocks("FBal0034227")
        assert isinstance(stocks, list)
        assert len(stocks) > 0, "bcd[25] (FBal0034227) should be held in at least one stock"


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


class TestFindStocksConstruct:
    # FBtp0000352 = P{GawB} — a widely-used construct carried by many insertions.
    KNOWN_CONSTRUCT_ID = "FBtp0000352"

    @pytest.mark.integration
    def test_known_construct_returns_stocks(self):
        # A construct is not held in stocks directly; stocks are propagated from
        # the FBti insertions producedby it.
        stocks = find_stocks(self.KNOWN_CONSTRUCT_ID)
        assert len(stocks) > 0
        assert all("stock_id" in s for s in stocks)

    @pytest.mark.integration
    def test_construct_stocks_have_fbst(self):
        stocks = find_stocks(self.KNOWN_CONSTRUCT_ID)
        assert any(s["stock_id"].startswith("FBst") for s in stocks)

    @pytest.mark.integration
    def test_construct_collection_filter(self):
        all_stocks = find_stocks(self.KNOWN_CONSTRUCT_ID)
        filtered = find_stocks(self.KNOWN_CONSTRUCT_ID, collection_filter="Bloomington")
        assert 0 < len(filtered) <= len(all_stocks)
        for s in filtered:
            if s.get("collection"):
                assert "Bloomington" in s["collection"]

    @pytest.mark.integration
    def test_construct_stocks_via_allele_path(self):
        # FBtp0000162 = P{CaSpeR-3}: has stocks ONLY through alleles made from it
        # (zero via the producedby-insertion route). Regression guard for the
        # multi-path UNION — a single insertion-only query returns 0 here.
        stocks = find_stocks("FBtp0000162")
        assert len(stocks) > 0
        assert all(s["stock_id"].startswith("FBst") for s in stocks)

    @pytest.mark.integration
    def test_nonexistent_construct(self):
        stocks = find_stocks("FBtp9999999999")
        assert stocks == []


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


class TestFindStocksTableSchema:
    CONSTRUCT_WITH_STOCKS = "FBtp0000352"  # P{GawB}

    @pytest.mark.integration
    def test_single_selection_id_column(self):
        result = get_flybase_stocks(self.CONSTRUCT_WITH_STOCKS, return_dataframe=False, limit=3)
        assert_single_selection_id(result)

    @pytest.mark.integration
    def test_stock_id_is_a_visible_column(self):
        # stock_id must be a normal displayed column, not the (hidden) identity.
        result = get_flybase_stocks(self.CONSTRUCT_WITH_STOCKS, return_dataframe=False, limit=3)
        stock_id = result["headers"]["stock_id"]
        assert stock_id["type"] == "markdown"
        assert stock_id["order"] >= 0
        # the hidden identity stays the bare FBst; the visible column links it
        row = result["rows"][0]
        assert row["stock_id"] == f"[{row['id']}](https://flybase.org/reports/{row['id']})"

    @pytest.mark.integration
    def test_linked_columns_are_declared_markdown(self):
        result = get_flybase_stocks(self.CONSTRUCT_WITH_STOCKS, return_dataframe=False, limit=3)
        for col in ("stock_id", "stock_number", "collection"):
            assert result["headers"][col]["type"] == "markdown", col
        # genotype carries FlyBase bracket notation (w[1118]) and must stay text
        assert result["headers"]["genotype"]["type"] == "text"

    @pytest.mark.integration
    def test_collection_links_to_the_centre_homepage(self):
        result = get_flybase_stocks(self.CONSTRUCT_WITH_STOCKS, return_dataframe=False, limit=3)
        assert any(row["collection"].startswith("[") and "](" in row["collection"]
                   for row in result["rows"])


class TestStockLinkouts:
    """Unit tests for the linkout helpers — no database access."""

    def test_flybase_report_url_accepts_any_fb_id(self):
        assert _flybase_report_url("FBst0006565") == "https://flybase.org/reports/FBst0006565"
        assert _flybase_report_url("FBrf0239740") == "https://flybase.org/reports/FBrf0239740"

    def test_flybase_report_url_rejects_non_ids(self):
        assert _flybase_report_url("6565") is None
        assert _flybase_report_url("") is None
        assert _flybase_report_url(None) is None

    def test_md_link_without_url_is_plain_text(self):
        assert _md_link("6565", None) == "6565"
        assert _md_link("", "https://example.org/") == ""

    def test_md_link_escapes_parentheses_in_the_url(self):
        # MarkdownLinkComponent's link target excludes ()[] so the label may
        # contain brackets; a DOI with parentheses must not end the match early.
        assert _md_link("10.1002/(SICI)1096", "https://doi.org/10.1002/(SICI)1096") == \
            "[10.1002/(SICI)1096](https://doi.org/10.1002/%28SICI%291096)"

    def test_bloomington_stock_number_deep_links(self):
        assert _stock_number_url("Bloomington Drosophila Stock Center", "6565") == \
            "https://bdsc.indiana.edu/stocks/6565"

    def test_unknown_collection_has_no_stock_number_link(self, monkeypatch):
        import vfbquery.flybase_stocks as fbs
        monkeypatch.setattr(fbs, "collection_links",
                            lambda: {"Kyoto Stock Center": {
                                "order_url": "https://kyotofly.kit.jp/cgi-bin/stocks/index.cgi"}})
        assert _stock_number_url("Kyoto Stock Center", "103972") is None

    def test_order_url_ending_in_equals_takes_the_stock_number(self, monkeypatch):
        import vfbquery.flybase_stocks as fbs
        monkeypatch.setattr(fbs, "collection_links",
                            lambda: {"FlyORF": {
                                "order_url": "https://www.flyorf.ch/imlskonakart/SelectProd.do?flylineId="}})
        assert _stock_number_url("FlyORF", "F000748") == \
            "https://www.flyorf.ch/imlskonakart/SelectProd.do?flylineId=F000748"


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
