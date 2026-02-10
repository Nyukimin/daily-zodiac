"""assets/templates.json の妥当性を検証するテスト。"""
from pathlib import Path

from generate import SIGNS, load_templates


def test_templates_json_exists():
    """assets/templates.json が存在する。"""
    path = Path("assets/templates.json")
    assert path.exists(), "assets/templates.json が存在しません"


def test_templates_structure():
    """12星座キーが揃い、各星座の配列長が1以上、各テンプレに必須キーがある。"""
    templates = load_templates(Path("assets/templates.json"))

    assert set(templates.keys()) == set(SIGNS), "12星座のキーが揃っていません"

    for sign in SIGNS:
        arr = templates[sign]
        assert isinstance(arr, list), f"{sign}: 値が配列ではありません"
        assert len(arr) >= 1, f"{sign}: 配列長が1未満です"

        for i, t in enumerate(arr):
            assert "summary" in t, f"{sign}[{i}]: summary がありません"
            assert "choices" in t, f"{sign}[{i}]: choices がありません"
            assert "next_step" in t, f"{sign}[{i}]: next_step がありません"

            choices = t["choices"]
            assert 2 <= len(choices) <= 3, f"{sign}[{i}]: choices は2〜3個である必要があります"
