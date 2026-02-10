"""同日・同星座の決定性を検証するテスト。"""
from pathlib import Path

from generate import load_templates, select_template


def test_same_input_same_output():
    """同じ sign, date_str で select_template を呼ぶと、同じ結果が返る。"""
    templates = load_templates(Path("assets/templates.json"))

    r1 = select_template(templates, "aries", "2026-02-10")
    r2 = select_template(templates, "aries", "2026-02-10")

    assert r1 == r2


def test_different_date_may_differ():
    """別日（date_str 違い）では、同一星座でも別テンプレになり得る。"""
    templates = load_templates(Path("assets/templates.json"))
    sign = "aries"

    # 配列長が7以上なので、日付を変えれば別テンプレになる日がある
    results = [select_template(templates, sign, f"2026-02-{10+i:02d}") for i in range(7)]
    all_same = all(r == results[0] for r in results)
    assert not all_same, "日付が違えば別テンプレになり得る（配列長>1）"
