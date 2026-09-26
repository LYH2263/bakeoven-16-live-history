from app.services.oven_engine import (
    Interval,
    Occupancy,
    RecipeDurations,
    build_occupancies,
    find_conflicts,
    find_overlapping_pairs,
    next_free_window,
)


def test_half_open_no_touch_conflict():
    a = Occupancy(1, Interval(0, 30), "bake", 1)
    b = Occupancy(1, Interval(30, 60), "bake", 2)
    assert find_conflicts([a], [b]) == []


def test_overlap_detected():
    recipe = RecipeDurations(20, 30)
    cand = build_occupancies(1, 9, 10, recipe)
    existing = [Occupancy(1, Interval(25, 40), "bake", 1)]
    assert find_conflicts(existing, cand)


def test_next_free_window_after_busy():
    existing = [
        Occupancy(1, Interval(0, 40), "ferment", 1),
        Occupancy(1, Interval(40, 70), "bake", 1),
    ]
    w = next_free_window(existing, 1, duration=30, search_from=0)
    assert w == Interval(70, 100)


def test_next_free_in_gap():
    existing = [
        Occupancy(1, Interval(0, 20), "bake", 1),
        Occupancy(1, Interval(80, 100), "bake", 2),
    ]
    w = next_free_window(existing, 1, duration=30, search_from=0)
    assert w == Interval(20, 50)


def test_pairs_touching_endpoints_empty():
    # 端点相接（半开区间）不算重叠
    occs = build_occupancies(1, 1, 0, RecipeDurations(20, 20))
    occs += build_occupancies(1, 2, 40, RecipeDurations(20, 20))
    assert find_overlapping_pairs(occs) == []


def test_pairs_reported_once_with_phases():
    # b1: 发酵[0,30) 烘烤[30,60)；b2: 发酵[10,40) 烘烤[40,70)
    occs = build_occupancies(1, 1, 0, RecipeDurations(30, 30))
    occs += build_occupancies(1, 2, 10, RecipeDurations(30, 30))
    pairs = find_overlapping_pairs(occs)
    phase_pairs = sorted((a.phase, b.phase) for a, b in pairs)
    assert phase_pairs == [
        ("bake", "bake"),
        ("bake", "ferment"),
        ("ferment", "ferment"),
    ]
    assert all(a.batch_id != b.batch_id for a, b in pairs)


def test_pairs_ignore_other_ovens():
    occs = build_occupancies(1, 1, 0, RecipeDurations(30, 30))
    occs += build_occupancies(2, 2, 0, RecipeDurations(30, 30))
    assert find_overlapping_pairs(occs) == []


def test_pairs_zero_ferment_no_false_positive():
    # 零长发酵段（空区间）不与任何段重叠，烘烤段照常参与
    occs = build_occupancies(1, 1, 600, RecipeDurations(0, 30))
    occs += build_occupancies(1, 2, 610, RecipeDurations(0, 30))
    pairs = find_overlapping_pairs(occs)
    assert [(a.phase, b.phase) for a, b in pairs] == [("bake", "bake")]


def test_pairs_single_batch_never_self_pairs():
    occs = build_occupancies(1, 1, 0, RecipeDurations(30, 30))
    assert find_overlapping_pairs(occs) == []


def test_empty_interval_overlaps_nothing():
    empty = Interval(600, 600)
    assert not empty.overlaps(Interval(590, 620))
    assert not Interval(590, 620).overlaps(empty)
