"""fallback/ パターン JSON の妥当性を検証するテスト。"""
import json
from pathlib import Path

from generate import SIGNS


def test_global_patterns_exists():
    """fallback/global_patterns.json が存在する。"""
    path = Path("fallback/global_patterns.json")
    assert path.exists(), "fallback/global_patterns.json が存在しません"


def test_global_patterns_structure():
    """global_patterns に patterns 配列があり、各要素に必須キー（summary, advice）がある。"""
    with open(Path("fallback/global_patterns.json"), encoding="utf-8") as f:
        data = json.load(f)
    arr = data.get("patterns", [])
    assert len(arr) >= 1, "patterns が1件以上必要です"
    for i, t in enumerate(arr):
        assert "summary" in t, f"global[{i}]: summary がありません"
        assert "advice" in t, f"global[{i}]: advice がありません"


def test_sign_patterns_exists():
    """fallback/sign_patterns.json が存在する。"""
    path = Path("fallback/sign_patterns.json")
    assert path.exists(), "fallback/sign_patterns.json が存在しません"


def test_sign_patterns_structure():
    """12星座キーが揃い、各星座の配列長が1以上、各パターンに必須キー（summary, advice）がある。"""
    with open(Path("fallback/sign_patterns.json"), encoding="utf-8") as f:
        data = json.load(f)
    assert set(data.keys()) == set(SIGNS), "12星座のキーが揃っていません"
    for sign in SIGNS:
        arr = data[sign]
        assert isinstance(arr, list), f"{sign}: 値が配列ではありません"
        assert len(arr) >= 1, f"{sign}: 配列長が1未満です"
        for i, t in enumerate(arr):
            assert "summary" in t, f"{sign}[{i}]: summary がありません"
            assert "advice" in t, f"{sign}[{i}]: advice がありません"
