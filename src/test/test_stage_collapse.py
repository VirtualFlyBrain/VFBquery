"""Collapsing a Clustering's Sample stages: the narrowest FBdv stage covering each
developmental period's stages, never above embryonic / larval / prepupal / pupal /
pharate adult / adult stage.
Offline: ancestor maps as `_stage_ancestors` returns them ({stage: {ancestor: (label, steps)}})."""
from vfbquery.vfb_queries import _collapse_stages

ADULT, P_STAGE, PUPAL, EMB = "FBdv_00005369", "FBdv_00007001", "FBdv_00005349", "FBdv_00005289"
PHARATE = "FBdv_00006011"
ANC = {
    "D5": {"D5": ("day 5 of adulthood", 0), ADULT: ("adult stage", 1)},
    "D30": {"D30": ("day 30 of adulthood", 0), ADULT: ("adult stage", 1)},
    "P6": {"P6": ("pupal stage P6", 0), PUPAL: ("pupal stage", 1), P_STAGE: ("P-stage", 2)},
    "P7": {"P7": ("pupal stage P7", 0), PUPAL: ("pupal stage", 1), P_STAGE: ("P-stage", 2)},
    "P8": {"P8": ("pharate adult stage P8", 0), PHARATE: ("pharate adult stage", 1), P_STAGE: ("P-stage", 2)},
    "P9": {"P9": ("pharate adult stage P9", 0), PHARATE: ("pharate adult stage", 1), P_STAGE: ("P-stage", 2)},
    "E16": {"E16": ("embryonic stage 16", 0), "LATE": ("late embryonic stage", 1), EMB: ("embryonic stage", 2)},
    "E17": {"E17": ("embryonic stage 17", 0), "LATE": ("late embryonic stage", 1), EMB: ("embryonic stage", 2)},
    "MAT": {"MAT": ("mature adult stage", 0)},           # no substage_of edge in FBdv
}


def collapse(*ids):
    return _collapse_stages([{"short_form": i, "label": ANC[i][i][0]} for i in ids], ANC)


def test_single_stage_kept():
    assert collapse("D5") == [("D5", "day 5 of adulthood")]


def test_same_period_collapses_to_narrowest_common_stage():
    assert collapse("D5", "D30") == [(ADULT, "adult stage")]
    assert collapse("P6", "P7") == [(PUPAL, "pupal stage")]
    assert collapse("E16", "E17") == [("LATE", "late embryonic stage")]


def test_pupal_and_pharate_adult_stages_kept_apart():
    # never collapsed to P-stage: pupal and pharate adult are separate periods
    assert collapse("P6", "P7", "P8", "P9") == [(PUPAL, "pupal stage"), (PHARATE, "pharate adult stage")]
    assert collapse("P6", "P8") == [("P6", "pupal stage P6"), ("P8", "pharate adult stage P8")]


def test_several_periods_shown_in_developmental_order():
    assert collapse("D30", "P6", "E16", "P7") == [
        ("E16", "embryonic stage 16"), (PUPAL, "pupal stage"), ("D30", "day 30 of adulthood")]


def test_stage_under_no_ceiling_stays():
    assert collapse("D5", "MAT") == [("D5", "day 5 of adulthood"), ("MAT", "mature adult stage")]
