"""生成物の妥当性を検証するテスト。"""
import json
from pathlib import Path

from generate import SIGNS, generate_site


def test_generate_site_creates_files(tmp_path):
    """generate_site を実行すると、index.html、各星座の index.html、data/{date}.json が生成される。"""
    generate_site(date_str="2026-02-10", out_dir=tmp_path)

    assert (tmp_path / "index.html").exists()
    assert (tmp_path / "data" / "2026-02-10.json").exists()

    for sign in SIGNS:
        assert (tmp_path / sign / "index.html").exists()


def test_json_has_required_keys(tmp_path):
    """data/{date}.json に global と signs の必須キー（summary, advice）がある。"""
    generate_site(date_str="2026-02-10", out_dir=tmp_path)
    p = tmp_path / "data" / "2026-02-10.json"
    payload = json.loads(p.read_text(encoding="utf-8"))
    assert "date" in payload and payload["date"] == "2026-02-10"
    assert "global" in payload
    assert {"summary", "advice"} <= set(payload["global"].keys())
    assert "signs" in payload
    for sign in SIGNS:
        assert sign in payload["signs"], f"signs に {sign} がありません"
        s = payload["signs"][sign]
        assert {"summary", "advice"} <= set(s.keys()), f"{sign}: 必須キーが不足"


def test_html_has_meta_and_base(tmp_path):
    """HTML に meta charset utf-8 と base href が含まれる。"""
    generate_site(date_str="2026-02-10", out_dir=tmp_path)

    index_html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "charset" in index_html and "utf-8" in index_html
    assert "<base" in index_html and "href" in index_html

    sign_html = (tmp_path / "aries" / "index.html").read_text(encoding="utf-8")
    assert "charset" in sign_html and "utf-8" in sign_html
    assert "<base" in sign_html and "href" in sign_html
