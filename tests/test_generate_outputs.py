"""生成物の妥当性を検証するテスト。"""
import json
from pathlib import Path

from generate import SIGNS, generate_site


def test_generate_site_creates_files(tmp_path):
    """generate_site を実行すると、index.html と各星座の index.html/index.json が生成される。"""
    generate_site(date_str="2026-02-10", out_dir=tmp_path)

    assert (tmp_path / "index.html").exists()

    for sign in SIGNS:
        assert (tmp_path / sign / "index.html").exists()
        assert (tmp_path / sign / "index.json").exists()


def test_json_has_required_keys(tmp_path):
    """各 JSON に必須キー（date, sign, sign_ja, summary, choices, next_step）がある。"""
    generate_site(date_str="2026-02-10", out_dir=tmp_path)
    required = {"date", "sign", "sign_ja", "summary", "choices", "next_step"}

    for sign in SIGNS:
        p = tmp_path / sign / "index.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert required <= set(data.keys()), f"{sign}: 必須キーが不足"


def test_html_has_meta_and_base(tmp_path):
    """HTML に meta charset utf-8 と base href が含まれる。"""
    generate_site(date_str="2026-02-10", out_dir=tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "charset" in index_html and "utf-8" in index_html
    assert "<base" in index_html and "href" in index_html

    sign_html = (tmp_path / "aries" / "index.html").read_text(encoding="utf-8")
    assert "charset" in sign_html and "utf-8" in sign_html
    assert "<base" in sign_html and "href" in sign_html
