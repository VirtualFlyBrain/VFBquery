"""Fallback image choice for ROI-tree classes that have no indexed painted domain."""
from vfbquery.vfb_queries import _pick_fallback_domains, _roi_side


def _c(i, label):
    return {'individual_id': i, 'individual_label': label}


def _ids(picked):
    return [p['individual_id'] for p in picked]


def test_side_detection():
    assert _roi_side('MaleCNS:MB(L) on JRC2018Unisex') == 'L'
    assert _roi_side('BANC:MB_CA_R on JRC2018Unisex') == 'R'
    assert _roi_side('BANC:MB on JRC2018Unisex') is None
    assert _roi_side('JRC2018Unisex') is None


def test_complete_image_beats_a_left_right_pair():
    picked = _pick_fallback_domains([
        _c('VFB_00108iq7', 'MaleCNS:MB(L) on JRC2018Unisex'),
        _c('VFB_00108iqa', 'MaleCNS:MB(R) on JRC2018Unisex'),
        _c('VFB_00108vzl', 'BANC:MB on JRC2018Unisex'),
    ])
    assert _ids(picked) == ['VFB_00108vzl']


def test_sided_image_only_when_no_complete_one_exists():
    picked = _pick_fallback_domains([
        _c('VFB_001091rv', 'BANC:MB_ML_R on JRC2018Unisex'),
        _c('VFB_001091ru', 'BANC:MB_ML_L on JRC2018Unisex'),
    ])
    assert _ids(picked) == ['VFB_001091ru']


def test_named_source_beats_unlabelled_legacy_within_a_tier():
    picked = _pick_fallback_domains([
        _c('VFB_00030867', 'adult mushroom body on adult brain template JFRC2'),
        _c('VFB_00108vzl', 'BANC:MB on JRC2018Unisex'),
    ])
    assert _ids(picked) == ['VFB_00108vzl']
    assert _pick_fallback_domains([]) == []


def test_left_is_chosen_before_right_even_when_right_has_the_lower_id():
    picked = _pick_fallback_domains([
        _c('VFB_001091z0', 'CATMAID_L1EM:A8_R on L1_larval_CNS'),
        _c('VFB_001091z1', 'CATMAID_L1EM:A8_L on L1_larval_CNS'),
    ])
    assert _ids(picked) == ['VFB_001091z1']
    only_right = _pick_fallback_domains([_c('VFB_001091z0', 'CATMAID_L1EM:A8_R on L1_larval_CNS')])
    assert _ids(only_right) == ['VFB_001091z0']
