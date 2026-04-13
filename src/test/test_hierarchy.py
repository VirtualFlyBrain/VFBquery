"""Tests for get_hierarchy function.

Tests the hierarchy tree builder for both part_of (brain region structure)
and subclass_of (cell type hierarchies), in both ancestor and descendant
directions.
"""

import pytest

from vfbquery.vfb_queries import get_hierarchy


# Known test terms
MUSHROOM_BODY = "FBbt_00005801"
KENYON_CELL = "FBbt_00003686"


class TestHierarchyValidation:
    def test_invalid_relationship_raises(self):
        with pytest.raises(ValueError, match="relationship"):
            get_hierarchy(KENYON_CELL, relationship="invalid")

    def test_invalid_direction_raises(self):
        with pytest.raises(ValueError, match="direction"):
            get_hierarchy(KENYON_CELL, direction="invalid")


class TestSubclassOfDescendants:
    @pytest.mark.integration
    def test_returns_descendants(self):
        result = get_hierarchy(KENYON_CELL, 'subclass_of', 'descendants', max_depth=1)
        assert result['id'] == KENYON_CELL
        assert result['label'] == 'Kenyon cell'
        assert result['relationship'] == 'subclass_of'
        assert 'descendants' in result
        assert len(result['descendants']) > 0

    @pytest.mark.integration
    def test_descendants_have_id_and_label(self):
        result = get_hierarchy(KENYON_CELL, 'subclass_of', 'descendants', max_depth=1)
        for child in result['descendants']:
            assert 'id' in child
            assert 'label' in child
            assert child['id'].startswith('FBbt_')
            assert child['label'] != child['id']  # label should be resolved

    @pytest.mark.integration
    def test_depth_1_has_no_grandchildren(self):
        result = get_hierarchy(KENYON_CELL, 'subclass_of', 'descendants', max_depth=1)
        for child in result['descendants']:
            assert 'descendants' not in child

    @pytest.mark.integration
    def test_depth_2_has_nested_children(self):
        result = get_hierarchy(KENYON_CELL, 'subclass_of', 'descendants', max_depth=2)
        has_grandchildren = any('descendants' in child for child in result['descendants'])
        assert has_grandchildren, "At least one direct subclass should have its own subclasses"


class TestSubclassOfAncestors:
    @pytest.mark.integration
    def test_returns_ancestors(self):
        result = get_hierarchy(KENYON_CELL, 'subclass_of', 'ancestors', max_depth=1)
        assert 'ancestors' in result
        assert len(result['ancestors']) > 0

    @pytest.mark.integration
    def test_ancestors_have_id_and_label(self):
        result = get_hierarchy(KENYON_CELL, 'subclass_of', 'ancestors', max_depth=1)
        for anc in result['ancestors']:
            assert 'id' in anc
            assert 'label' in anc

    @pytest.mark.integration
    def test_kenyon_cell_ancestor_is_mb_intrinsic_neuron(self):
        result = get_hierarchy(KENYON_CELL, 'subclass_of', 'ancestors', max_depth=1)
        ancestor_ids = [a['id'] for a in result['ancestors']]
        assert 'FBbt_00007484' in ancestor_ids  # mushroom body intrinsic neuron

    @pytest.mark.integration
    def test_depth_2_has_nested_ancestors(self):
        result = get_hierarchy(KENYON_CELL, 'subclass_of', 'ancestors', max_depth=2)
        has_grandparent = any('ancestors' in anc for anc in result['ancestors'])
        assert has_grandparent


class TestPartOfDescendants:
    @pytest.mark.integration
    def test_returns_parts(self):
        result = get_hierarchy(MUSHROOM_BODY, 'part_of', 'descendants', max_depth=1)
        assert result['id'] == MUSHROOM_BODY
        assert result['label'] == 'mushroom body'
        assert 'descendants' in result
        assert len(result['descendants']) > 0

    @pytest.mark.integration
    def test_parts_have_id_and_label(self):
        result = get_hierarchy(MUSHROOM_BODY, 'part_of', 'descendants', max_depth=1)
        for part in result['descendants']:
            assert 'id' in part
            assert 'label' in part
            assert part['id'].startswith('FBbt_')


class TestPartOfAncestors:
    @pytest.mark.integration
    def test_mushroom_body_part_of_protocerebrum(self):
        result = get_hierarchy(MUSHROOM_BODY, 'part_of', 'ancestors', max_depth=1)
        assert 'ancestors' in result
        ancestor_ids = [a['id'] for a in result['ancestors']]
        assert 'FBbt_00003627' in ancestor_ids  # protocerebrum


class TestDisplayOutput:
    @pytest.mark.integration
    def test_display_field_present(self):
        result = get_hierarchy(KENYON_CELL, 'subclass_of', 'both', max_depth=1)
        assert 'display' in result
        assert isinstance(result['display'], str)
        assert 'Kenyon cell' in result['display']

    @pytest.mark.integration
    def test_display_shows_ancestors(self):
        result = get_hierarchy(KENYON_CELL, 'subclass_of', 'both', max_depth=1)
        assert 'ancestors' in result['display'].lower()
        assert 'mushroom body intrinsic neuron' in result['display']

    @pytest.mark.integration
    def test_display_shows_tree_connectors(self):
        result = get_hierarchy(KENYON_CELL, 'subclass_of', 'descendants', max_depth=1)
        assert '├──' in result['display'] or '└──' in result['display']

    @pytest.mark.integration
    def test_html_field_present(self):
        result = get_hierarchy(KENYON_CELL, 'subclass_of', 'both', max_depth=1)
        assert 'html' in result
        assert '<!DOCTYPE html>' in result['html']
        assert 'Kenyon cell' in result['html']

    @pytest.mark.integration
    def test_html_contains_vfb_links(self):
        result = get_hierarchy(KENYON_CELL, 'subclass_of', 'descendants', max_depth=1)
        assert 'virtualflybrain.org' in result['html']
        assert KENYON_CELL in result['html']


class TestBothDirections:
    @pytest.mark.integration
    def test_both_returns_ancestors_and_descendants(self):
        result = get_hierarchy(KENYON_CELL, 'subclass_of', 'both', max_depth=1)
        assert 'ancestors' in result
        assert 'descendants' in result
        assert len(result['ancestors']) > 0
        assert len(result['descendants']) > 0

    @pytest.mark.integration
    def test_descendants_only_has_no_ancestors(self):
        result = get_hierarchy(KENYON_CELL, 'subclass_of', 'descendants', max_depth=1)
        assert 'descendants' in result
        assert 'ancestors' not in result

    @pytest.mark.integration
    def test_ancestors_only_has_no_descendants(self):
        result = get_hierarchy(KENYON_CELL, 'subclass_of', 'ancestors', max_depth=1)
        assert 'ancestors' in result
        assert 'descendants' not in result
