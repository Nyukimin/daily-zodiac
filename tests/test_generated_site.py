"""生成物（site/）のHTML構造・JSON を BeautifulSoup で検証するテスト。"""
import json
import os
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

JST = timezone(timedelta(hours=9))
SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
]


def _get_jst_date_str() -> str:
    """generate.py と同じロジックで JST 日付を取得。"""
    return datetime.now(JST).strftime("%Y-%m-%d")


def _run_generate(base_path: str = "/daily-zodiac/") -> Path:
    """generate.py を subprocess で実行。site_test/ に出力（BASE_PATH を子プロセスで反映）。"""
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "site_test"
    if out_dir.exists():
        try:
            shutil.rmtree(out_dir)
        except OSError:
            pass
    env = {**os.environ, "BASE_PATH": base_path}
    out_dir_str = str(out_dir.resolve())
    script = (
        f"import os; os.environ['BASE_PATH']={base_path!r}; "
        f"import sys; sys.path.insert(0, {str(root)!r}); "
        f"from generate import generate_site; generate_site(out_dir={out_dir_str!r})"
    )
    result = subprocess.run(
        ["python", "-c", script],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"generate failed: {result.stderr}")
    return out_dir


def test_generate_creates_12_sign_pages():
    """site/{sign}/index.html が 12 個存在する。"""
    site = _run_generate()
    for sign in SIGNS:
        p = site / sign / "index.html"
        assert p.exists(), f"site/{sign}/index.html が存在しません"


def test_data_json_exists():
    """site/data/{date}.json が存在し、global と signs 構造を持つ。"""
    site = _run_generate()
    date_str = _get_jst_date_str()
    data_path = site / "data" / f"{date_str}.json"
    assert data_path.exists(), f"site/data/{date_str}.json が存在しません"
    payload = json.loads(data_path.read_text(encoding="utf-8"))
    assert "date" in payload and payload["date"] == date_str
    assert "generated_at_jst" in payload
    assert "global" in payload
    assert "summary" in payload["global"] and "advice" in payload["global"]
    assert "signs" in payload
    for sign in SIGNS:
        assert sign in payload["signs"], f"signs に {sign} がありません"
        s = payload["signs"][sign]
        assert "summary" in s and "advice" in s


def test_index_has_12_links():
    """入口に 12 星座への導線（リンク）がある。"""
    site = _run_generate()
    html = (site / "index.html").read_text(encoding="utf-8")
    for sign in SIGNS:
        assert f'href="' in html and sign in html, f"星座 {sign} への導線がありません"


def test_contains_today_jst_date():
    """aries 等に JST の YYYY-MM-DD が含まれる。"""
    site = _run_generate()
    html = (site / "aries" / "index.html").read_text(encoding="utf-8")
    expected = _get_jst_date_str()
    assert expected in html, f"JST 日付 {expected} が aries ページに含まれません"


def test_base_path_local_links():
    """BASE_PATH=/ で /aries/ 形式のリンクがある。"""
    site = _run_generate("/")
    html = (site / "index.html").read_text(encoding="utf-8")
    assert "/aries/" in html, "BASE_PATH=/ で /aries/ への導線がありません"


def test_base_path_pages_links():
    """BASE_PATH=/daily-zodiac/ で /daily-zodiac/aries/ 形式。"""
    site = _run_generate("/daily-zodiac/")
    html = (site / "index.html").read_text(encoding="utf-8")
    assert "daily-zodiac" in html and "aries" in html, \
        "BASE_PATH=/daily-zodiac/ で /daily-zodiac/aries/ 形式の導線がありません"


def test_utf8_meta_and_japanese_present():
    """meta charset utf-8 があり、牡羊座等の日本語が含まれる。"""
    site = _run_generate()
    html = (site / "index.html").read_text(encoding="utf-8")
    assert "charset" in html and "utf-8" in html, "meta charset utf-8 がありません"
    assert "牡羊座" in html or "牡牛座" in html, "日本語星座名が含まれません"


def test_index_has_grid_css_hook():
    """入口HTMLに結果セクション（今日の全体運）が存在。"""
    site = _run_generate()
    html = (site / "index.html").read_text(encoding="utf-8")
    assert "今日の全体運" in html, "結果セクションがありません"


def test_pages_have_ad_placeholder():
    """入口・結果に ad-slot（class または広告枠）が存在。"""
    site = _run_generate()
    index_html = (site / "index.html").read_text(encoding="utf-8")
    result_html = (site / "aries" / "index.html").read_text(encoding="utf-8")
    assert "ad-slot" in index_html or "Ad Slot" in index_html, "入口に広告枠がありません"
    assert "ad-slot" in result_html, "結果ページに ad-slot がありません"


def test_result_has_other_signs_nav():
    """結果ページに他星座リンク群が存在。"""
    site = _run_generate()
    html = (site / "aries" / "index.html").read_text(encoding="utf-8")
    assert "他の星座" in html, "「他の星座」導線がありません"
    for sign in ["taurus", "gemini"]:
        assert sign in html, f"他星座 {sign} へのリンクがありません"
