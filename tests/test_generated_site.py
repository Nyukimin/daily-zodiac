"""生成物（site/）のHTML構造を BeautifulSoup で検証するテスト。"""
import os
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

JST = timezone(timedelta(hours=9))
SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
]


def _get_jst_date_str() -> str:
    """generate.py と同じロジックで JST 日付を取得。"""
    return datetime.now(JST).strftime("%Y-%m-%d")


def _run_generate(base_path: str = "/daily-zodiac/") -> None:
    """generate.py を subprocess で実行。site/ を生成。"""
    root = Path(__file__).resolve().parent.parent
    site = root / "site"
    if site.exists():
        shutil.rmtree(site)
    env = {**os.environ, "BASE_PATH": base_path}
    subprocess.run(
        ["python", "generate.py"],
        cwd=root,
        env=env,
        check=True,
        capture_output=True,
    )


def test_generate_creates_12_sign_pages():
    """site/{sign}/index.html が 12 個存在する。"""
    _run_generate()
    root = Path(__file__).resolve().parent.parent
    for sign in SIGNS:
        p = root / "site" / sign / "index.html"
        assert p.exists(), f"site/{sign}/index.html が存在しません"


def test_index_has_12_links():
    """入口にリンク 12 個あり、href が星座に対応。"""
    _run_generate()
    root = Path(__file__).resolve().parent.parent
    html = (root / "site" / "index.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    links = soup.select("ul a[href]")
    assert len(links) >= 12, "入口にリンクが 12 個ありません"
    hrefs = [a["href"] for a in links]
    for sign in SIGNS:
        assert any(sign in h for h in hrefs), f"星座 {sign} へのリンクがありません"


def test_contains_today_jst_date():
    """aries 等に JST の YYYY-MM-DD が含まれる。"""
    _run_generate()
    root = Path(__file__).resolve().parent.parent
    html = (root / "site" / "aries" / "index.html").read_text(encoding="utf-8")
    expected = _get_jst_date_str()
    assert expected in html, f"JST 日付 {expected} が aries ページに含まれません"


def test_base_path_local_links():
    """BASE_PATH=/ でリンクが /aries/ 形式。"""
    _run_generate("/")
    root = Path(__file__).resolve().parent.parent
    html = (root / "site" / "index.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    links = soup.select("ul a[href]")
    hrefs = [a["href"] for a in links]
    assert any("/aries/" in h for h in hrefs), "BASE_PATH=/ で /aries/ 形式のリンクがありません"


def test_base_path_pages_links():
    """BASE_PATH=/daily-zodiac/ で /daily-zodiac/aries/ 形式。"""
    _run_generate("/daily-zodiac/")
    root = Path(__file__).resolve().parent.parent
    html = (root / "site" / "index.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    links = soup.select("ul a[href]")
    hrefs = [a["href"] for a in links]
    assert any("daily-zodiac" in h and "aries" in h for h in hrefs), \
        "BASE_PATH=/daily-zodiac/ で /daily-zodiac/aries/ 形式のリンクがありません"


def test_utf8_meta_and_japanese_present():
    """meta charset utf-8 があり、牡羊座等の日本語が含まれる。"""
    _run_generate()
    root = Path(__file__).resolve().parent.parent
    html = (root / "site" / "index.html").read_text(encoding="utf-8")
    assert "charset" in html and "utf-8" in html, "meta charset utf-8 がありません"
    assert "牡羊座" in html or "牡牛座" in html, "日本語星座名が含まれません"


def test_index_has_grid_css_hook():
    """入口HTMLに class="sign-grid" 等のフックが存在。"""
    _run_generate()
    root = Path(__file__).resolve().parent.parent
    html = (root / "site" / "index.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    grid = soup.find(class_="sign-grid")
    assert grid is not None, "class=sign-grid がありません"


def test_pages_have_ad_placeholder():
    """入口・結果に class="ad-slot" が存在。"""
    _run_generate()
    root = Path(__file__).resolve().parent.parent
    index_html = (root / "site" / "index.html").read_text(encoding="utf-8")
    result_html = (root / "site" / "aries" / "index.html").read_text(encoding="utf-8")
    assert "ad-slot" in index_html, "入口に ad-slot がありません"
    assert "ad-slot" in result_html, "結果ページに ad-slot がありません"


def test_result_has_other_signs_nav():
    """結果ページに他星座リンク群が存在。"""
    _run_generate()
    root = Path(__file__).resolve().parent.parent
    html = (root / "site" / "aries" / "index.html").read_text(encoding="utf-8")
    assert "他の星座" in html, "「他の星座」導線がありません"
    for sign in ["taurus", "gemini"]:
        assert sign in html, f"他星座 {sign} へのリンクがありません"
