"""同日・同星座の決定性を検証するテスト。"""
from generate import build_sign_fallback, pick_index, stable_hash_to_int


def test_stable_hash_deterministic():
    """stable_hash_to_int は同じ入力で常に同じ値を返す。"""
    r1 = stable_hash_to_int("2026-02-10:sign:aries")
    r2 = stable_hash_to_int("2026-02-10:sign:aries")
    assert r1 == r2


def test_pick_index_deterministic():
    """pick_index は同じ date_key, key で常に同じインデックスを返す。"""
    r1 = pick_index("2026-02-10", "sign:aries", 7)
    r2 = pick_index("2026-02-10", "sign:aries", 7)
    assert r1 == r2
    assert 0 <= r1 < 7


def test_build_sign_fallback_same_date_same_output():
    """同じ date_key, sign で build_sign_fallback を呼ぶと、同じ結果が返る。"""
    r1 = build_sign_fallback("2026-02-10", "aries")
    r2 = build_sign_fallback("2026-02-10", "aries")
    assert r1 == r2


def test_build_sign_fallback_different_date_may_differ():
    """別日では、同一星座でも別パターンになり得る。"""
    results = [build_sign_fallback(f"2026-02-{10+i:02d}", "aries") for i in range(9)]
    all_same = all(r == results[0] for r in results)
    assert not all_same, "日付が違えば別パターンになり得る（配列長>1）"
