from app.services.oven_engine import (
    Interval,
    Occupancy,
    RecipeDurations,
    build_occupancies,
    find_conflicts,
    find_pairwise_overlaps,
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


def test_pairwise_overlap_between_batches():
    occs = build_occupancies(1, 1, 0, RecipeDurations(20, 30)) + build_occupancies(
        1, 2, 25, RecipeDurations(20, 30)
    )
    hits = find_pairwise_overlaps(occs)
    phases = {(a.phase, b.phase) for a, b in hits}
    assert ("bake", "ferment") in phases
    assert all(a.batch_id != b.batch_id for a, b in hits)


def test_pairwise_touching_endpoints_no_overlap():
    occs = build_occupancies(1, 1, 0, RecipeDurations(20, 30)) + build_occupancies(
        1, 2, 50, RecipeDurations(20, 30)
    )
    assert find_pairwise_overlaps(occs) == []


def test_pairwise_ignores_same_batch_and_other_ovens():
    same_batch = build_occupancies(1, 1, 0, RecipeDurations(20, 30))
    assert find_pairwise_overlaps(same_batch) == []
    other_oven = build_occupancies(1, 1, 0, RecipeDurations(20, 30)) + build_occupancies(
        2, 2, 10, RecipeDurations(20, 30)
    )
    assert find_pairwise_overlaps(other_oven) == []
